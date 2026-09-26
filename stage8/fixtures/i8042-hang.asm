; ============================================================================
; i8042-hang - stage8/fixtures/i8042-hang.asm (Stage 8 ring 8a, plan item 5).
;
; A FIXTURE PART for the i8042 slot (stage8/PARTS.md, "The fixtures"):
; i8042-good whose byte entry spins for ever on its 100th call after
; its own init.
;
; THE ONE CHANGE from i8042-good, marked FIXTURE CHANGE below:
; byte counts its calls once init has run, and the 100th spins for ever.
; In shadow init never runs, so it is never armed. Its name field is 'hang'.
;
; Everything else is i8042-good's, byte for byte in the source: init is
; mouse_init's work with the two part: lines, byte is the generic's decoder
; and packet assembly, health answers 0 unless init failed, and the state is
; valid as stored.
;
; Its fate (PARTS.md's fixture table): threshold 1 boot, 100 keyboard bytes, 100 mouse packets;
; in shadow it behaves as good (0 disagreements) and is taken; live, the
; machine hangs, the pets stop, the TCO resets it, and the next boot is
; "S8: recovery i8042 watchdog" with hang demoted.
;
; Frozen with its binary at item 13. Built with:
;   nasm -f bin stage8/fixtures/i8042-hang.asm -o stage8/fixtures/i8042-hang.bin
; The header's body hash below is the SHA-256 of the assembled body (the
; part's bytes from 96 on); test 1 re-assembles the part and checks it.
; ============================================================================
bits 64
default rel

%define SVC_PIT_WAIT       48
%define SVC_SERIAL_LINE    56
%define SVC_KEY_EVENT      64
%define SVC_MOUSE_PACKET   72

%define WAIT_TRIES         100          ; x 10 ms: the generic's I8042_WAIT_TRIES
%define IBF_SPINS          0x10000      ; the generic's bound on the input buffer

; LINE msg - one line through the service, "part: " prefixed by the seed.
%macro LINE 1
        lea     rdi, [%1]
        mov     esi, %1_len
        call    [rbx + SVC_SERIAL_LINE]
%endmacro

; ---------------------------------------------------------------- header --
part:
        db      'PART', 3, 0, 0, 0
slot:   db      'i8042'
        times   8 - ($ - slot) db 0
        dd      body_end - body
        dd      init - part, byte_entry - part, health - part
name:   db      'hang'
        times   16 - ($ - name) db 0
body_sha256:
        db      0x5d, 0xd9, 0xc1, 0xed, 0x05, 0x67, 0xc1, 0xbd
        db      0x4c, 0x37, 0x88, 0x9e, 0x23, 0xbf, 0xde, 0x88
        db      0x4c, 0x32, 0xa3, 0x30, 0x53, 0x07, 0xca, 0xc6
        db      0xff, 0xc0, 0x2d, 0x0d, 0x94, 0xe9, 0x23, 0x68
        times   96 - ($ - part) db 0

; ------------------------------------------------------------------ body --
body:

; init(svc) - RDI = the service table. The controller's cold init and the
; mouse's reset, as mouse_init does them. Clobbers everything but RSP.
init:
        mov     rbx, rdi                ; the services preserve RBX
        mov     al, 0xAD                ; the keyboard port off
        call    cmd
        mov     al, 0xA7                ; the auxiliary port off
        call    cmd
        call    drain
        mov     al, 0xAA                ; the controller's self-test
        call    cmd
        call    read
        jc      .self_test_failed
        cmp     al, 0x55
        jne     .self_test_failed
        mov     al, 0xAD                ; both ports off again, drained: the
        call    cmd                     ; self-test may have re-enabled them
        mov     al, 0xA7                ; (ring 7c item 15)
        call    cmd
        call    drain
        LINE    msg_self_ok
        mov     al, 0x20                ; the command byte, after the self-test
        call    cmd
        call    read
        jc      .no_cmd_byte
        or      al, 0x03                ; both interrupts on
        and     al, 0xCF                ; both ports enabled
        movzx   r12d, al                ; translation and the rest kept
        mov     al, 0x60                ; write it
        call    cmd
        mov     eax, r12d
        call    data
        mov     al, 0x20                ; read it back: a confirmation only
        call    cmd
        call    read
        mov     al, 0xA8                ; the auxiliary port enabled
        call    cmd

        mov     al, 0xFF                ; reset: FA, then AA, then the ID
        call    mouse_cmd
        jc      .no_mouse
        call    read_mouse
        jc      .no_mouse
        cmp     al, 0xAA
        jne     .no_mouse
        call    read_mouse              ; the ID
        jc      .no_mouse
        mov     al, 0xF6                ; defaults
        call    mouse_cmd
        jc      .no_mouse
        mov     al, 0xF4                ; enable reporting
        call    mouse_cmd
        jc      .no_mouse
        LINE    msg_mouse_ok
.done:
        call    drain
        mov     byte [inited], 1
        ret
.no_mouse:
        LINE    msg_mouse_none
        jmp     .done
.self_test_failed:
        mov     dword [failure], 1
        LINE    msg_self_failed
        jmp     .done
.no_cmd_byte:
        mov     dword [failure], 2
        LINE    msg_cmd_failed
        jmp     .done

; byte(status, data, stamp, svc) - RDI = the status byte, RSI = the data
; byte, RDX = its TSC stamp, RCX = the service table. The seed's stub has
; read the ports; nothing here touches them. Clobbers everything but RSP.
byte_entry:
        mov     rbx, rcx
        cmp     byte [inited], 0        ; FIXTURE CHANGE: once init has run,
        je      .unarmed                ; the 100th byte spins for ever
        inc     dword [calls]
        cmp     dword [calls], 100
        jne     .unarmed
.spin:  jmp     .spin
.unarmed:
        test    dil, 0x20               ; bit 5: the byte is the mouse's
        jnz     mouse_byte

; The keyboard: kbd_next's decode, one byte at a time.
        movzx   eax, sil
        cmp     byte [kbd_e0], 0        ; an E0 prefix swallows its successor
        je      .no_pending
        mov     byte [kbd_e0], 0
        ret
.no_pending:
        cmp     al, 0xE0
        jne     .not_e0
        mov     byte [kbd_e0], 1
        ret
.not_e0:
        cmp     al, 0x2A                ; LShift make
        je      .shift_down
        cmp     al, 0x36                ; RShift make
        je      .shift_down
        cmp     al, 0xAA                ; LShift break
        je      .shift_up
        cmp     al, 0xB6                ; RShift break
        je      .shift_up
        test    al, 0x80                ; other break codes: ignored
        jnz     .ret
        lea     rcx, [scan1_map]        ; set 1, US, unshifted ...
        cmp     byte [kbd_shift], 0
        je      .translate
        lea     rcx, [scan1_shift_map]  ; ... or shifted
.translate:
        movzx   edi, byte [rcx + rax]   ; lea first: [label + reg] is never RIP-relative
        test    edi, edi
        jz      .ret                    ; not a key this slot listens to
        mov     rsi, rdx                ; the stamp of the byte that completed it
        call    [rbx + SVC_KEY_EVENT]
.ret:
        ret
.shift_down:
        mov     byte [kbd_shift], 1
        ret
.shift_up:
        mov     byte [kbd_shift], 0
        ret

; The mouse: mouse_byte's three-byte packet machine.
mouse_byte:
        movzx   eax, sil
        mov     ecx, [mse_phase]
        test    ecx, ecx
        jnz     .later
        test    al, 0x08                ; byte 0 always has bit 3 set: without
        jnz     .first                  ; it the byte is dropped (a resync)
        ret
.first:
        mov     [mse_pkt], al
        mov     [mse_stamp0], rdx
        mov     dword [mse_phase], 1
        ret
.later:
        lea     rdx, [mse_pkt]
        mov     [rdx + rcx], al
        inc     ecx
        mov     [mse_phase], ecx
        cmp     ecx, 3
        jb      .ret
        mov     dword [mse_phase], 0
        movsx   rdi, byte [mse_pkt + 1] ; dx, signed
        movsx   rsi, byte [mse_pkt + 2] ; dy, signed, positive upwards
        movzx   edx, byte [mse_pkt]
        and     edx, 7                  ; the buttons
        mov     rcx, [mse_stamp0]       ; the packet's first byte's stamp
        call    [rbx + SVC_MOUSE_PACKET]
.ret:
        ret

; health(svc) - 0, or init's failure code.
health:
        mov     eax, [failure]
        ret

; ------------------------------------------------------ the controller --
; wait_ibf - spin until the input buffer is empty, bounded; a controller
; that never empties it is failure 3. Clobbers RAX, RCX.
wait_ibf:
        mov     ecx, IBF_SPINS
.w:     in      al, 0x64
        test    al, 2
        jz      .ok
        dec     ecx
        jnz     .w
        mov     dword [failure], 3
.ok:    ret

; cmd - AL = a controller command, to port 0x64.
cmd:
        push    rax
        call    wait_ibf
        pop     rax
        out     0x64, al
        ret

; data - AL = a byte for the controller or the device it addresses.
data:
        push    rax
        call    wait_ibf
        pop     rax
        out     0x60, al
        ret

; read - one byte from the output buffer, waited for up to WAIT_TRIES x
; 10 ms through the service: AL = the byte, AH = its status byte, CF clear;
; or CF set on a timeout.
read:
        mov     r13d, WAIT_TRIES
.poll:
        in      al, 0x64
        test    al, 1
        jnz     .got
        mov     edi, 10
        call    [rbx + SVC_PIT_WAIT]
        dec     r13d
        jnz     .poll
        stc
        ret
.got:
        mov     ah, al
        in      al, 0x60
        clc
        ret

; read_mouse - as read, but a keyboard byte meanwhile is dropped.
read_mouse:
        call    read
        jc      .out
        test    ah, 0x20
        jz      read_mouse
.out:
        ret

; drain - read and drop whatever the output buffer holds.
drain:
        in      al, 0x64
        test    al, 1
        jz      .done
        in      al, 0x60
        jmp     drain
.done:
        ret

; mouse_cmd - AL = a command for the mouse: D4, the byte, and its ACK (FA)
; awaited. CF set on a timeout or anything but an ACK.
mouse_cmd:
        push    rax
        mov     al, 0xD4
        call    cmd
        pop     rax
        call    data
        call    read_mouse
        jc      .out
        cmp     al, 0xFA
        je      .ack
        stc
        ret
.ack:
        clc
.out:
        ret

; ---------------------------------------------------------------- lines --
msg_self_ok:        db 'i8042 self-test ok'
msg_self_ok_len     equ $ - msg_self_ok
msg_mouse_ok:       db 'i8042 mouse reset ok'
msg_mouse_ok_len    equ $ - msg_mouse_ok
msg_mouse_none:     db 'i8042 mouse none'
msg_mouse_none_len  equ $ - msg_mouse_none
msg_self_failed:    db 'i8042 self-test failed'
msg_self_failed_len equ $ - msg_self_failed
msg_cmd_failed:     db 'i8042 command byte not answered'
msg_cmd_failed_len  equ $ - msg_cmd_failed

; ----------------------------------------------------------- the maps --
; Scancode set 1, US layout: the seed's scan1_map and scan1_shift_map,
; byte for byte.
        align   8
scan1_map:
        db      0, 0x1B                                 ; 00 -, 01 Esc
        db      '1','2','3','4','5','6','7','8','9','0' ; 02-0B
        db      '-','='                                 ; 0C, 0D
        db      8, 9                                    ; 0E Backspace, 0F Tab
        db      'q','w','e','r','t','y','u','i','o','p' ; 10-19
        db      '[',']'                                 ; 1A, 1B
        db      13, 0                                   ; 1C Enter, 1D LCtrl
        db      'a','s','d','f','g','h','j','k','l'     ; 1E-26
        db      ';', 0x27, '`'                          ; 27 ; 28 ' 29 `
        db      0, '\'                                  ; 2A LShift, 2B
        db      'z','x','c','v','b','n','m'             ; 2C-32
        db      ',','.','/'                             ; 33-35
        db      0, 0                                    ; 36 RShift, 37 kp*
        db      0, ' '                                  ; 38 LAlt, 39 Space
        times   128 - ($ - scan1_map) db 0              ; 3A-7F: nothing

scan1_shift_map:
        db      0, 0x1B                                 ; 00 -, 01 Esc
        db      '!','@','#','$','%','^','&','*','(',')' ; 02-0B
        db      '_','+'                                 ; 0C, 0D
        db      8, 9                                    ; 0E Backspace, 0F Tab
        db      'Q','W','E','R','T','Y','U','I','O','P' ; 10-19
        db      '{','}'                                 ; 1A, 1B
        db      13, 0                                   ; 1C Enter, 1D LCtrl
        db      'A','S','D','F','G','H','J','K','L'     ; 1E-26
        db      ':', '"', '~'                           ; 27 : 28 " 29 ~
        db      0, '|'                                  ; 2A LShift, 2B
        db      'Z','X','C','V','B','N','M'             ; 2C-32
        db      '<','>','?'                             ; 33-35
        db      0, 0                                    ; 36 RShift, 37 kp*
        db      0, ' '                                  ; 38 LAlt, 39 Space
        times   128 - ($ - scan1_shift_map) db 0        ; 3A-7F: nothing

; ----------------------------------------------------------- the state --
; Inside the part, zero as stored.
        align   8
mse_stamp0:     dq      0
mse_phase:      dd      0
failure:        dd      0
calls:          dd      0               ; bytes since init: hang's counter
mse_pkt:        db      0, 0, 0
kbd_e0:         db      0
kbd_shift:      db      0
inited:         db      0               ; set at init's end
        align   8
body_end:
