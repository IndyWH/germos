; ============================================================================
; The hog - stage6/hog.asm (Stage 6 ring 6a, plan item 2).
;
; A deliberately bad app the mock broker serves for the request "hog":
; init draws its name in its panel (so the rehearsal's "drew nothing"
; criterion is satisfied and the budget criterion is the one that fires),
; and every step spins on ticks_ms for 200 ms before returning - four
; times the 50 ms budget GLASS.md sets. The twin reads step_worst out of
; the obs page and must refuse it with "the app missed its budget".
;
; Frozen with its binary at item 8. Built with:
;   nasm -f bin stage6/hog.asm -o stage6/hog.bin
; ============================================================================

bits 64
default rel

%define SVC_DRAW_TEXT     8
%define SVC_TICKS_MS      24
%define HOG_MS            200

header:
        dd      init, step, key, exit

init:
        mov     [table], rdi
        mov     r12, rdi
        mov     edi, 1
        mov     esi, 2
        lea     rdx, [s_name]
        mov     ecx, s_name_len
        call    [r12 + SVC_DRAW_TEXT]
        ret

step:
        mov     r12, [table]
        call    [r12 + SVC_TICKS_MS]
        mov     r13, rax
.spin:
        call    [r12 + SVC_TICKS_MS]
        sub     rax, r13
        cmp     rax, HOG_MS
        jb      .spin
        ret

key:
        ret

exit:
        ret

s_name:         db      'hog'
s_name_len      equ     $ - s_name

        align   8
table:          dq      0
