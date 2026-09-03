; ============================================================================
; The liar - stage6/liar.asm (Stage 6 ring 6b, plan item 2).
;
; A deliberately wrong build of plans/liar.md - the same intent and the
; same five tests as plans/echo.md - which the mock broker serves for
; "! install liar". It is SAFE: it boots, draws its starting state,
; keeps its budget, stays in its panel, faults nothing, exits, and so
; passes every one of GLASS.md's nine criteria. It is WRONG: key draws
; the key PLUS ONE - "b" for "a" - so the plan's second test, expect "a",
; must fail, and the install must be refused with
;
;     rehearsal failed: expect "a"
;
; That refusal is what proves the plan's tests are judged, not only
; safety (spec, ring 6b, the mock table).
;
; Frozen with its binary at item 8. Built with:
;   nasm -f bin stage6/liar.asm -o stage6/liar.bin
; ============================================================================

bits 64
default rel

%define SVC_DRAW_TEXT     8

%define ROW               1
%define COL               1

header:
        dd      init, step, key, exit

init:
        push    rbx
        push    r12
        mov     [table], rdi
        mov     byte [cell], '-'
        call    draw
        pop     r12
        pop     rbx
        ret

step:
        ret

; key(byte) - RDI = the key. The lie: the printable one past it is drawn
; ('a' becomes 'b'; '~' wraps to '!', which no plan can press anyway).
key:
        push    rbx
        push    r12
        mov     eax, edi
        cmp     al, 0x20
        jb      .done
        cmp     al, 0x7E
        ja      .done
        inc     al
        cmp     al, 0x7E
        jbe     .lie
        mov     al, '!'
.lie:
        mov     [cell], al
        call    draw
.done:
        pop     r12
        pop     rbx
        ret

exit:
        ret

draw:
        mov     r12, [table]
        mov     edi, ROW
        mov     esi, COL
        lea     rdx, [cell]
        mov     ecx, 1
        call    [r12 + SVC_DRAW_TEXT]
        ret

        align   8
table:          dq      0
cell:           db      '-'
