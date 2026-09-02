; ============================================================================
; The escapee - stage6/escapee.asm (Stage 6 ring 6a, plan item 2).
;
; A deliberately bad app the mock broker serves for the request "escapee":
; init draws its name in its own panel through the service (so the "drew
; nothing" criterion passes), then does what a grown app could do and must
; not - finds the framebuffer by itself and paints one cell outside its
; panel, in the conversation panel. It finds the framebuffer the way the
; core does: a PCI scan of bus 0 for a display-class device (class code
; 0x0300) and its BAR0, through ports 0xCF8/0xCFC; it takes the screen
; width as twice the app panel's columns times 16 pixels (on the standard
; VGA device the stride equals the width, and the two panels are equal
; halves of this machine's 90 columns), and paints a 16x16 foreground
; block at screen row 7, column 3. Once, at init: a pixel diff over time
; would never see it, which is why the twin compares the conversation
; panel against its surface instead.
;
; Frozen with its binary at item 8. Built with:
;   nasm -f bin stage6/escapee.asm -o stage6/escapee.bin
; ============================================================================

bits 64
default rel

%define SVC_DRAW_TEXT     8
%define SVC_PANEL_SIZE    16
%define FG_PIXEL          0x00E0E0E0    ; rgb(224,224,224), the same in both pixel orders
%define TARGET_ROW        7             ; a screen cell inside the conversation panel
%define TARGET_COL        3

header:
        dd      init, step, key, exit

init:
        mov     r12, rdi

        ; The honest part: its name, in its panel.
        mov     edi, 1
        mov     esi, 2
        lea     rdx, [s_name]
        mov     ecx, s_name_len
        call    [r12 + SVC_DRAW_TEXT]

        ; The width: twice the panel's columns, 16 pixels each, 4 bytes each.
        call    [r12 + SVC_PANEL_SIZE]
        mov     r13d, eax               ; the panel's columns
        shl     r13d, 7                 ; * 2 panels * 16 px * 4 bytes = the stride in bytes

        ; The framebuffer: the display-class device's BAR0.
        xor     esi, esi                ; device number
.dev:
        cmp     esi, 32
        jae     .done                   ; no display device: draw nothing more
        mov     ebx, esi
        shl     ebx, 11                 ; bus 0, function 0
        xor     ecx, ecx
        call    pci_read
        cmp     ax, 0xFFFF
        je      .next
        mov     ecx, 8
        call    pci_read
        shr     eax, 16
        cmp     ax, 0x0300
        jne     .next
        mov     ecx, 0x10               ; BAR0
        call    pci_read
        test    al, 1
        jnz     .next                   ; an I/O BAR
        and     eax, ~0xF
        mov     edi, eax                ; the framebuffer, below 4 GB

        ; Paint the block: 16 lines of 16 pixels.
        mov     eax, TARGET_ROW * 16
        imul    rax, r13
        add     rdi, rax
        add     rdi, TARGET_COL * 16 * 4
        mov     ebx, 16
.line:
        mov     rdx, rdi
        mov     ecx, 16
        mov     eax, FG_PIXEL
        rep     stosd
        mov     rdi, rdx
        add     rdi, r13
        dec     ebx
        jnz     .line
        jmp     .done
.next:
        inc     esi
        jmp     .dev
.done:
        ret

step:
        ret

key:
        ret

exit:
        ret

; pci_read - EBX = bus<<16 | device<<11 | function<<8, ECX = register.
; Returns EAX. Preserves everything else.
pci_read:
        push    rdx
        mov     eax, ecx
        and     eax, 0xFC
        or      eax, ebx
        or      eax, 0x80000000
        mov     dx, 0xCF8
        out     dx, eax
        mov     dx, 0xCFC
        in      eax, dx
        pop     rdx
        ret

s_name:         db      'escapee'
s_name_len      equ     $ - s_name
