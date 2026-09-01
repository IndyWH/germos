; ============================================================================
; The test component - stage5/component.asm (Stage 5, plan item 2).
;
; The canned, committed, hand-written component the mock broker serves for
; the request "test component" (and, zero-padded to the 1 MB cap, for
; "big"). It exists so acceptance test 3 has a KNOWN picture to demand
; pixel by pixel, and so every one of the four services in
; stage5/GERMLINE.md is exercised by something the gate can see:
;
;   row  2, col 4:  germline test component        draw_text
;   row  4, col 4:  console <cols>x<rows>          console_size, own itoa
;   row  6, col 4:  ticks ok  |  ticks stuck        ticks_ms advanced, or not
;   row  8, col 4:  key: -    ->  key: <ch>         poll_key, each printable
;   row 10, col 4:  esc returns to the prompt
;
; then it polls until poll_key returns Esc (0x1B) and returns.
;
; Written to the entry contract: flat, bits 64, position-independent
; (default rel, no absolute address), entry at the first byte, RDI = the
; service table, returns with ret. Services are called through the table
; with arguments in RDI, RSI, RDX, RCX and preserve RBX, RBP, R12-R15, so
; the state lives there. The callee-saved registers are pushed and popped
; anyway - the contract lets a component clobber them, but a component that
; leaves the core's registers as it found them is one less thing to wonder
; about when something else goes wrong.
;
; This file and its assembled stage5/component.bin are both frozen at item
; 8; the checker assembles this source to stage5/out/ and demands the
; committed binary byte for byte.
;
; Built with:  nasm -f bin stage5/component.asm -o stage5/component.bin
; ============================================================================

bits 64
default rel

%define SVC_DRAW_TEXT     8
%define SVC_CONSOLE_SIZE  16
%define SVC_POLL_KEY      24
%define SVC_TICKS_MS      32

%define TICK_TRIES        2000000       ; polls of ticks_ms before "stuck"

entry:
        push    rbx
        push    rbp
        push    r12
        push    r13
        push    r14
        push    r15
        mov     r12, rdi                ; the service table

        ; Row 2: the title.
        mov     edi, 2
        mov     esi, 4
        lea     rdx, [s_title]
        mov     ecx, s_title_len
        call    [r12 + SVC_DRAW_TEXT]

        ; Row 4: "console <cols>x<rows>", the numbers from console_size.
        call    [r12 + SVC_CONSOLE_SIZE]
        mov     r13, rax                ; cols in the low half, rows in the high
        lea     rdi, [line_buf]
        lea     rsi, [s_console]
        mov     ecx, s_console_len
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
        mov     edi, 4
        mov     esi, 4
        call    [r12 + SVC_DRAW_TEXT]

        ; Row 6: does ticks_ms advance? Read it, then poll until it differs,
        ; bounded - a stuck clock is reported, not waited on for ever.
        call    [r12 + SVC_TICKS_MS]
        mov     r14, rax
        mov     r15d, TICK_TRIES
.tick:
        call    [r12 + SVC_TICKS_MS]
        cmp     rax, r14
        jne     .tick_ok
        dec     r15d
        jnz     .tick
        lea     rdx, [s_stuck]
        mov     ecx, s_stuck_len
        jmp     .tick_draw
.tick_ok:
        lea     rdx, [s_ticks]
        mov     ecx, s_ticks_len
.tick_draw:
        mov     edi, 6
        mov     esi, 4
        call    [r12 + SVC_DRAW_TEXT]

        ; Row 8: the last key, "-" until one arrives.
        call    draw_key

        ; Row 10: the way out.
        mov     edi, 10
        mov     esi, 4
        lea     rdx, [s_esc]
        mov     ecx, s_esc_len
        call    [r12 + SVC_DRAW_TEXT]

        ; Poll until Esc. A printable key redraws row 8; anything else is
        ; ignored.
.poll:
        call    [r12 + SVC_POLL_KEY]
        test    eax, eax
        jz      .poll
        cmp     al, 0x1B
        je      .done
        cmp     al, 0x20
        jb      .poll
        cmp     al, 0x7E
        ja      .poll
        mov     [s_key + 5], al
        call    draw_key
        jmp     .poll

.done:
        pop     r15
        pop     r14
        pop     r13
        pop     r12
        pop     rbp
        pop     rbx
        ret

; draw_key - row 8, column 4: the six bytes of s_key. Clobbers the
; caller-saved registers only.
draw_key:
        mov     edi, 8
        mov     esi, 4
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
s_title:        db      'germline test component'
s_title_len     equ     $ - s_title
s_console:      db      'console '
s_console_len   equ     $ - s_console
s_ticks:        db      'ticks ok'
s_ticks_len     equ     $ - s_ticks
s_stuck:        db      'ticks stuck'
s_stuck_len     equ     $ - s_stuck
s_esc:          db      'esc returns to the prompt'
s_esc_len       equ     $ - s_esc
s_key:          db      'key: -'
s_key_len       equ     $ - s_key

; Writable scratch inside the blob - the region is ordinary RAM.
        align   8
line_buf:       times 32 db 0
