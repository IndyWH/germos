; ============================================================================
; The echo app - stage6/echo.asm (Stage 6 ring 6b, plan item 2).
;
; The canned, committed, hand-written correct build of plans/echo.md, which
; the mock broker serves for "! install echo" (and, zero-padded to 4096
; bytes, for "! install echo, but big"). The plan's intent: shows a dash
; until a key is pressed, then the last key pressed, as a single character
; at the top left of the panel; nothing else is drawn. So:
;
;   init  draws "-" at panel row 1, column 1 - the starting state, which
;         the twin's screendump B must not find blank (plan amendment A1)
;   key   replaces that one cell with the key, for a printable
;   step  nothing
;   exit  nothing - the loader clears the panel
;
; The plan's tests (press a / expect "a" / press b / expect "b" / expect
; not "a") are what the twin runs against it; the app panel holds exactly
; one glyph at any time, so an expect proves the key and nothing else.
;
; Written to GLASS.md's callback contract: flat, bits 64, position
; independent, the 16-byte header of four u32 offsets first, RDI = the
; service table at init, RDI = the key at key, every callback returning
; with ret. The callee-saved registers are kept as found.
;
; This file and its assembled stage6/echo.bin are both frozen at item 8;
; the checker assembles this source to stage6/out/ and demands the
; committed binary byte for byte.
;
; Built with:  nasm -f bin stage6/echo.asm -o stage6/echo.bin
; ============================================================================

bits 64
default rel

%define SVC_DRAW_TEXT     8

%define ROW               1
%define COL               1

header:
        dd      init, step, key, exit

; init(services) - RDI = the service table. Keeps it, draws the dash.
init:
        push    rbx
        push    r12
        mov     [table], rdi
        mov     byte [cell], '-'
        call    draw
        pop     r12
        pop     rbx
        ret

; step() - nothing to do between keys.
step:
        ret

; key(byte) - RDI = the key. A printable becomes the one cell.
key:
        push    rbx
        push    r12
        mov     eax, edi
        cmp     al, 0x20
        jb      .done
        cmp     al, 0x7E
        ja      .done
        mov     [cell], al
        call    draw
.done:
        pop     r12
        pop     rbx
        ret

; exit() - the loader clears the panel.
exit:
        ret

; draw - the one cell at (ROW, COL) through draw_text. Clobbers the
; caller-saved registers only.
draw:
        mov     r12, [table]
        mov     edi, ROW
        mov     esi, COL
        lea     rdx, [cell]
        mov     ecx, 1
        call    [r12 + SVC_DRAW_TEXT]
        ret

        align   8
table:          dq      0               ; the service table, kept from init
cell:           db      '-'             ; what the panel shows
