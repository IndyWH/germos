; ============================================================================
; The test app - stage6/app.asm (Stage 6 ring 6a, plan item 2).
;
; The canned, committed, hand-written ABI 2 app the mock broker serves for
; the request "test app" (and, zero-padded to the 1 MB cap, for "big"). It
; exists so acceptance test 3 has a KNOWN picture to demand pixel by pixel,
; and so every one of the four callbacks and the four services in
; stage6/GLASS.md is exercised by something the gate can see. In its panel
; (rows and columns relative to the app panel):
;
;   row  1, col 2:  glass test app                 draw_text, from init
;   row  3, col 2:  panel <cols>x<rows>            panel_size, own itoa
;   row  5, col 2:  ticks ok  |  ticks stuck       ticks_ms advanced, from step
;   row  7, col 2:  key: -    ->  key: <ch>        key, each printable
;   row  9, col 2:  esc exits  tab prompt
;   row 11, col 2:  five foreground blocks         fill(11, 2, 1, 5, 1)
;
; It declares two choices (a alpha, b beta) - the broker's mock table says
; so; the blob itself only sees keys.
;
; Written to the callback contract: flat, bits 64, position-independent
; (default rel, no absolute address), the 16-byte header of four u32
; offsets first, RDI = the service table at init, RDI = the key at key,
; every callback returning with ret. The callee-saved registers are pushed
; and popped anyway - the contract lets a callback clobber them, but an app
; that leaves the core's registers as it found them is one less thing to
; wonder about when something else goes wrong.
;
; This file and its assembled stage6/app.bin are both frozen at item 8; the
; checker assembles this source to stage6/out/ and demands the committed
; binary byte for byte.
;
; Built with:  nasm -f bin stage6/app.asm -o stage6/app.bin
; ============================================================================

bits 64
default rel

%define SVC_DRAW_TEXT     8
%define SVC_PANEL_SIZE    16
%define SVC_TICKS_MS      24
%define SVC_FILL          32

%define STEP_TRIES        100           ; steps without the clock moving before "stuck"

; The header: four u32 offsets from the blob's first byte.
header:
        dd      init, step, key, exit

; init(services) - RDI = the service table. Draws everything but the
; ticks line, which step draws once the clock has visibly moved.
init:
        push    rbx
        push    rbp
        push    r12
        push    r13
        push    r14
        push    r15
        mov     [table], rdi
        mov     r12, rdi

        ; Row 1: the title.
        mov     edi, 1
        mov     esi, 2
        lea     rdx, [s_title]
        mov     ecx, s_title_len
        call    [r12 + SVC_DRAW_TEXT]

        ; Row 3: "panel <cols>x<rows>", the numbers from panel_size.
        call    [r12 + SVC_PANEL_SIZE]
        mov     r13, rax                ; cols in the low half, rows in the high
        lea     rdi, [line_buf]
        lea     rsi, [s_panel]
        mov     ecx, s_panel_len
        rep     movsb
        mov     eax, r13d               ; cols
        call    put_dec
        mov     byte [rdi], 'x'
        inc     rdi
        mov     rax, r13
        shr     rax, 32                 ; rows
        call    put_dec
        lea     rdx, [line_buf]
        mov     rcx, rdi
        sub     rcx, rdx                ; the length built
        mov     edi, 3
        mov     esi, 2
        call    [r12 + SVC_DRAW_TEXT]

        ; The clock's reading at init; step compares against it.
        call    [r12 + SVC_TICKS_MS]
        mov     [t_init], rax
        mov     dword [tick_state], 0
        mov     dword [tick_tries], 0

        ; Row 7: the last key, "-" until one arrives.
        call    draw_key

        ; Row 9: the way out.
        mov     edi, 9
        mov     esi, 2
        lea     rdx, [s_esc]
        mov     ecx, s_esc_len
        call    [r12 + SVC_DRAW_TEXT]

        ; Row 11: five foreground blocks, through fill.
        mov     edi, 11
        mov     esi, 2
        mov     edx, 1
        mov     ecx, 5
        mov     r8d, 1
        call    [r12 + SVC_FILL]

        pop     r15
        pop     r14
        pop     r13
        pop     r12
        pop     rbp
        pop     rbx
        ret

; step() - until the clock has moved since init, look; then draw "ticks
; ok" once and do nothing more. A clock that never moves within
; STEP_TRIES steps is reported as stuck, not waited on for ever.
step:
        push    rbx
        push    rbp
        push    r12
        push    r13
        push    r14
        push    r15
        cmp     dword [tick_state], 0
        jne     .done                   ; already drawn
        mov     r12, [table]
        call    [r12 + SVC_TICKS_MS]
        cmp     rax, [t_init]
        jne     .ok
        inc     dword [tick_tries]
        cmp     dword [tick_tries], STEP_TRIES
        jb      .done
        lea     rdx, [s_stuck]
        mov     ecx, s_stuck_len
        jmp     .draw
.ok:
        lea     rdx, [s_ticks]
        mov     ecx, s_ticks_len
.draw:
        mov     dword [tick_state], 1
        mov     edi, 5
        mov     esi, 2
        call    [r12 + SVC_DRAW_TEXT]
.done:
        pop     r15
        pop     r14
        pop     r13
        pop     r12
        pop     rbp
        pop     rbx
        ret

; key(byte) - RDI = the key. A printable redraws row 7; anything else is
; ignored.
key:
        push    rbx
        push    rbp
        push    r12
        push    r13
        push    r14
        push    r15
        mov     eax, edi
        cmp     al, 0x20
        jb      .done
        cmp     al, 0x7E
        ja      .done
        mov     [s_key + 5], al
        mov     r12, [table]
        call    draw_key
.done:
        pop     r15
        pop     r14
        pop     r13
        pop     r12
        pop     rbp
        pop     rbx
        ret

; exit() - nothing to undo: the loader clears the panel.
exit:
        ret

; draw_key - row 7, column 2: the six bytes of s_key. R12 = the table.
; Clobbers the caller-saved registers only.
draw_key:
        mov     edi, 7
        mov     esi, 2
        lea     rdx, [s_key]
        mov     ecx, s_key_len
        call    [r12 + SVC_DRAW_TEXT]
        ret

; put_dec - RAX = an unsigned value; its decimal digits are written at RDI,
; which advances past them. Clobbers RAX, RCX, RDX, R8.
put_dec:
        mov     r8d, 10
        xor     ecx, ecx                ; digits pushed
.split:
        xor     edx, edx
        div     r8
        push    rdx
        inc     ecx
        test    rax, rax
        jnz     .split
.emit:
        pop     rax
        add     al, '0'
        mov     [rdi], al
        inc     rdi
        dec     ecx
        jnz     .emit
        ret

; The strips. Lengths are assembly-time constants, so no scan for a NUL.
s_title:        db      'glass test app'
s_title_len     equ     $ - s_title
s_panel:        db      'panel '
s_panel_len     equ     $ - s_panel
s_ticks:        db      'ticks ok'
s_ticks_len     equ     $ - s_ticks
s_stuck:        db      'ticks stuck'
s_stuck_len     equ     $ - s_stuck
s_esc:          db      'esc exits  tab prompt'
s_esc_len       equ     $ - s_esc
s_key:          db      'key: -'
s_key_len       equ     $ - s_key

; Writable state inside the blob - the region is ordinary RAM.
        align   8
table:          dq      0               ; the service table, kept from init
t_init:         dq      0               ; ticks_ms at init
tick_state:     dd      0               ; 1 once the ticks line is drawn
tick_tries:     dd      0
line_buf:       times 32 db 0
