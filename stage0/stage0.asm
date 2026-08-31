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

; ------------------------------------------------------------ serial init ---
; COM1 at 0x3F8. Divisor 1 gives 115200 baud, 8N1, FIFO on.
;
; The serial channel comes up before anything touches video. That is the
; foundation's serial-log-from-byte-one rule, and it is the whole debugging
; strategy for bare metal: a black screen with NO serial means we died before
; running; a black screen WITH serial means video is the bug.

        mov     dx, 0x3F9               ; IER - no interrupts, we poll
        mov     al, 0x00
        out     dx, al
        mov     dx, 0x3FB               ; LCR - DLAB on, to reach the divisor
        mov     al, 0x80
        out     dx, al
        mov     dx, 0x3F8               ; divisor low  = 1  -> 115200 baud
        mov     al, 0x01
        out     dx, al
        mov     dx, 0x3F9               ; divisor high = 0
        mov     al, 0x00
        out     dx, al
        mov     dx, 0x3FB               ; LCR - 8 bits, no parity, 1 stop, DLAB off
        mov     al, 0x03
        out     dx, al
        mov     dx, 0x3FA               ; FCR - FIFO on and cleared
        mov     al, 0xC7
        out     dx, al
        mov     dx, 0x3FC               ; MCR - DTR and RTS asserted
        mov     al, 0x03
        out     dx, al

; -------------------------------------------------- serial line 1: alive ----
; The first observable act of the machine.

        mov     si, msg_alive
        call    serial_print

; ------------------------------------------------------------- halt loop ----
; Nothing left to do. Interrupts off, halt, and if anything ever wakes us,
; halt again.

halt_forever:
        cli
        hlt
        jmp     halt_forever

; ---------------------------------------------------------- serial_print ----
; SI -> NUL-terminated string. Writes it to COM1 a byte at a time, polling the
; line status register for "transmit holding register empty" before each byte.
; Clobbers AX, DX, SI.

serial_print:
.next:
        lodsb
        test    al, al
        jz      .done
.wait:
        push    ax
        mov     dx, 0x3FD               ; LSR
        in      al, dx
        test    al, 0x20                ; bit 5 - transmit holding reg empty
        pop     ax
        jz      .wait
        mov     dx, 0x3F8               ; THR
        out     dx, al
        jmp     .next
.done:
        ret

; ---------------------------------------------------------------- strings ---
; Exactly the bytes the spec names, each line CRLF terminated. Acceptance test
; 2 compares the whole serial stream against these, byte for byte.

msg_alive:      db "S0: alive", 13, 10, 0

; --------------------------------------------- padding and boot signature ---
; `times` fails the build loudly if the code above ever overruns 510 bytes.
; That error is a feature.

        times 510-($-$$) db 0
        dw 0xAA55
