; ============================================================================
; The point app - stage6/pointer.asm (Stage 6 ring 6c, plan item 2).
;
; The canned, committed, hand-written five-callback app the mock broker
; (broker/pointer.py --mock) serves for the request "point app". It exists
; so acceptance test 3 can prove that a click in the app panel reaches the
; fifth callback GLASS.md's ring 6c section defines, and that the app draws
; the cell it was given - a KNOWN picture the checker demands cell by cell.
; In its panel (rows and columns relative to the app panel):
;
;   row 0, col 0:      point app                     draw_text, from init
;   (row, col):        1, 2 or 3                     point, the button's digit
;                                                    at the cell of the press
;   key c:             the panel cleared, the title redrawn   fill, draw_text
;
; It declares one choice (c clear) - the broker's mock table says so; the
; blob itself only sees keys and presses. Every other key is ignored; step
; and exit do nothing. It draws its starting state at init (ring 6b's A1
; rule), so the twin's screendump B is never blank.
;
; Written to the callback contract: flat, bits 64, position independent
; (default rel, no absolute address), the 28-byte header first - the four
; u32 offsets of the 6a text, then the eight bytes POINTER2, then the u32
; offset of point - RDI = the service table at init, RDI = the key at key,
; RDI/RSI/RDX = row, column, button at point, every callback returning with
; ret. The callee-saved registers are kept as found.
;
; This file and its assembled stage6/pointer.bin are both frozen at item 8;
; the checker assembles this source to stage6/out/ and demands the
; committed binary byte for byte.
;
; Built with:  nasm -f bin stage6/pointer.asm -o stage6/pointer.bin
; ============================================================================

bits 64
default rel

%define SVC_DRAW_TEXT     8
%define SVC_PANEL_SIZE    16
%define SVC_FILL          32

; The header: four u32 offsets, the magic, the fifth offset.
header:
        dd      init, step, key, exit
        db      'POINTER2'
        dd      point

; init(services) - RDI = the service table. Keeps it, draws the title.
init:
        push    rbx
        push    r12
        mov     [table], rdi
        call    title
        pop     r12
        pop     rbx
        ret

; step() - nothing to do between events.
step:
        ret

; key(byte) - RDI = the key. 'c' clears the panel and redraws the title;
; anything else is ignored.
key:
        push    rbx
        push    r12
        cmp     edi, 'c'
        jne     .done
        mov     r12, [table]
        call    [r12 + SVC_PANEL_SIZE]  ; RAX = cols | rows << 32
        mov     rdx, rax
        shr     rdx, 32                 ; rows
        mov     ecx, eax                ; cols
        xor     edi, edi                ; row 0
        xor     esi, esi                ; column 0
        xor     r8d, r8d                ; the background
        call    [r12 + SVC_FILL]
        call    title
.done:
        pop     r12
        pop     rbx
        ret

; exit() - the loader clears the panel.
exit:
        ret

; point(row, col, button) - RDI = the row, RSI = the column, RDX = the
; button (1, 2, 3): the button's digit drawn at that cell.
point:
        push    rbx
        push    r12
        mov     r12, [table]
        add     edx, '0'
        mov     [digit], dl
        lea     rdx, [digit]
        mov     ecx, 1
        call    [r12 + SVC_DRAW_TEXT]
        pop     r12
        pop     rbx
        ret

; title - "point app" at row 0, column 0. Clobbers the caller-saved
; registers only.
title:
        mov     r12, [table]
        xor     edi, edi
        xor     esi, esi
        lea     rdx, [name]
        mov     ecx, name_len
        call    [r12 + SVC_DRAW_TEXT]
        ret

        align   8
table:          dq      0               ; the service table, kept from init
name:           db      'point app'
name_len        equ     $ - name
digit:          db      '0'             ; the last press's button, as a glyph
