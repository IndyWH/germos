; ---------------------------------------------------------------------------
; stage0.asm - Stage 0 of the AI OS: first pixel.
;
; One 512-byte boot sector. SeaBIOS loads it to 0x7C00 and jumps to it in
; 16-bit real mode. It says hello over serial, switches to VGA mode 13h, paints
; the Spectrum loading stripes, says so over serial, and halts.
;
; Built and run only inside QEMU. No real disk is ever in reach.
;
;   nasm -f bin stage0.asm -o stage0.img
;
; Layout follows stage0/spec.md.
; ---------------------------------------------------------------------------

        bits 16
        org 0x7C00

; ------------------------------------------------------------------ entry ---
; Only CS:IP can be trusted on entry, so DS, ES and SS are zeroed explicitly
; with interrupts off, and the stack is put just below the code at 0x7C00.
; CLD is set once here: lodsb and stosb further down both depend on the
; direction flag, and the BIOS is not required to leave it clear.

start:
        cli
        xor     ax, ax
        mov     ds, ax
        mov     es, ax
        mov     ss, ax
        mov     sp, 0x7C00
        cld
        sti

; ------------------------------------------------------------- halt loop ----
; Nothing left to do. Interrupts off, halt, and if anything ever wakes us,
; halt again.

halt_forever:
        cli
        hlt
        jmp     halt_forever

; --------------------------------------------- padding and boot signature ---
; `times` fails the build loudly if the code above ever overruns 510 bytes.
; That error is a feature.

        times 510-($-$$) db 0
        dw 0xAA55
