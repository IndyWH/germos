; ============================================================================
; Stage 1 - Owning the processor.
;
; One UEFI application, hand-assembled as a PE32+ binary. No compiler, no C
; runtime, no linker: the headers below are written byte by byte like
; everything else in this project. OVMF loads it from a FAT image as
; EFI/BOOT/BOOTX64.EFI and calls it in 64-bit long mode with boot services live.
;
; Built with:  nasm -f bin stage1/stage1.asm -o stage1/out/BOOTX64.EFI
;
; NASM -f bin is literal - no sections, no relocation, no linker to fix
; anything up. Because FileAlignment and SectionAlignment are both 0x1000, a
; file offset IS its RVA, so the flat output NASM produces is already the image
; the loader expects.
;
; Relocations are stripped and every memory reference is RIP-relative
; ("default rel" below), so the code does not care where it is loaded.
; ============================================================================

bits 64
default rel
org 0                           ; file offsets == RVAs

%define IMAGE_BASE      0x0000000000400000

; COM1, the same port and the same 115200 8N1 setup as Stage 0's boot sector.
; OVMF has already been using this port for its own console; we take it over.
%define COM1            0x3F8
%define COM1_IER        COM1 + 1
%define COM1_FCR        COM1 + 2
%define COM1_LCR        COM1 + 3
%define COM1_MCR        COM1 + 4
%define COM1_LSR        COM1 + 5
%define SECT_ALIGN      0x1000
%define FILE_ALIGN      0x1000

; ---------------------------------------------------------------------------
; DOS header. Only two fields matter to a UEFI loader: the 'MZ' magic, and
; e_lfanew at 0x3C pointing at the PE header.
; ---------------------------------------------------------------------------
dos_header:
        db      'MZ'
        times   0x3C-($-$$) db 0
        dd      pe_header               ; e_lfanew

; ---------------------------------------------------------------------------
; PE signature and COFF header.
; ---------------------------------------------------------------------------
pe_header:
        db      'PE', 0, 0

coff_header:
        dw      0x8664                  ; Machine: x86-64
        dw      2                       ; NumberOfSections: .text and .data
        dd      0                       ; TimeDateStamp
        dd      0                       ; PointerToSymbolTable
        dd      0                       ; NumberOfSymbols
        dw      opt_header_end - opt_header      ; SizeOfOptionalHeader (0xF0)
        ; 0x0001 RELOCS_STRIPPED     - we are position independent, there is no
        ;                              .reloc section and none is needed
        ; 0x0002 EXECUTABLE_IMAGE
        ; 0x0004 LINE_NUMS_STRIPPED
        ; 0x0008 LOCAL_SYMS_STRIPPED
        ; 0x0020 LARGE_ADDRESS_AWARE
        ; 0x0200 DEBUG_STRIPPED
        dw      0x022F                  ; Characteristics

; ---------------------------------------------------------------------------
; Optional header, PE32+ flavour.
; ---------------------------------------------------------------------------
opt_header:
        dw      0x020B                  ; Magic: PE32+
        db      0                       ; MajorLinkerVersion
        db      0                       ; MinorLinkerVersion
        dd      text_size               ; SizeOfCode
        dd      data_raw_size           ; SizeOfInitializedData
        dd      bss_size                ; SizeOfUninitializedData
        dd      efi_main                ; AddressOfEntryPoint
        dd      text_start              ; BaseOfCode
        dq      IMAGE_BASE              ; ImageBase
        dd      SECT_ALIGN              ; SectionAlignment
        dd      FILE_ALIGN              ; FileAlignment
        dw      0, 0                    ; OperatingSystemVersion
        dw      0, 0                    ; ImageVersion
        dw      0, 0                    ; SubsystemVersion
        dd      0                       ; Win32VersionValue
        dd      image_size              ; SizeOfImage
        dd      headers_size            ; SizeOfHeaders
        dd      0                       ; CheckSum (unused by UEFI)
        dw      10                      ; Subsystem: EFI application
        dw      0                       ; DllCharacteristics: none. Deliberately
                                        ; not NX_COMPAT and not DYNAMIC_BASE.
        dq      0x10000                 ; SizeOfStackReserve
        dq      0x10000                 ; SizeOfStackCommit
        dq      0x10000                 ; SizeOfHeapReserve
        dq      0x10000                 ; SizeOfHeapCommit
        dd      0                       ; LoaderFlags
        dd      16                      ; NumberOfRvaAndSizes
        times   16 dq 0                 ; the sixteen data directories, all empty
opt_header_end:

; ---------------------------------------------------------------------------
; Section table.
;
; Two sections, not one. A single read-write-execute section risks tripping
; OVMF's image-protection policy, which would fault on our first write to a
; variable; splitting code from data avoids the class entirely.
; ---------------------------------------------------------------------------
section_table:
        ; .text - code, execute, read
        db      '.text', 0, 0, 0
        dd      text_size               ; VirtualSize
        dd      text_start              ; VirtualAddress
        dd      text_size               ; SizeOfRawData
        dd      text_start              ; PointerToRawData (== RVA)
        dd      0                       ; PointerToRelocations
        dd      0                       ; PointerToLinenumbers
        dw      0                       ; NumberOfRelocations
        dw      0                       ; NumberOfLinenumbers
        dd      0x60000020              ; CODE | EXECUTE | READ

        ; .data - initialised data, read, write. VirtualSize covers the BSS,
        ; which the loader zero-fills for us, so none of it sits in the file.
        db      '.data', 0, 0, 0
        dd      data_virt_size          ; VirtualSize (initialised + BSS)
        dd      data_start              ; VirtualAddress
        dd      data_raw_size           ; SizeOfRawData (initialised only)
        dd      data_start              ; PointerToRawData (== RVA)
        dd      0                       ; PointerToRelocations
        dd      0                       ; PointerToLinenumbers
        dw      0                       ; NumberOfRelocations
        dw      0                       ; NumberOfLinenumbers
        dd      0xC0000040              ; INITIALIZED_DATA | READ | WRITE

        align   FILE_ALIGN, db 0
headers_size    equ     $ - $$

; ===========================================================================
; .text
; ===========================================================================
text_start:

; ---------------------------------------------------------------------------
; efi_main(EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable)
;
; Microsoft x64 calling convention: RCX = ImageHandle, RDX = SystemTable.
;
; Interrupts are deliberately left ENABLED here. Boot services are still live
; and the firmware's timer is still theirs; we take interrupts down at
; ExitBootServices, not before.
;
; RSP is aligned to 16 once, here. Every firmware call afterwards reserves 0x40
; below it - 32 bytes of shadow space the callee owns, plus room for a fifth and
; sixth stack argument - which keeps RSP 16-aligned at the call, as the ABI
; requires.
; ---------------------------------------------------------------------------
efi_main:
        cld                             ; lodsb/stosb below depend on it
        mov     [image_handle], rcx
        mov     [system_table], rdx
        mov     rax, [rdx + 0x60]       ; SystemTable->BootServices
        mov     [boot_services], rax

        and     rsp, -16                ; we never return, so the frame is ours
        sub     rsp, 0x40

        ; Step 1 of the spec: serial first, before anything else. A black screen
        ; with no serial means we died before this point; a black screen WITH
        ; serial means the fault is later. That distinction is the whole
        ; debugging strategy.
        call    serial_init
        lea     rsi, [msg_alive]
        call    serial_puts

halt_forever:
        cli
.hang:  hlt
        jmp     .hang

; ---------------------------------------------------------------------------
; Serial. Only the BSP ever calls any of this - one owner per device, the
; concurrency doctrine's first appearance. The application processors have no
; path to these routines at all.
; ---------------------------------------------------------------------------

; serial_init - COM1 at 115200 8N1, FIFO on. Preserves everything.
serial_init:
        push    rax
        push    rdx
        mov     dx, COM1_IER
        xor     al, al
        out     dx, al                  ; no interrupts from the UART
        mov     dx, COM1_LCR
        mov     al, 0x80
        out     dx, al                  ; DLAB on, so the next two are the divisor
        mov     dx, COM1
        mov     al, 0x01
        out     dx, al                  ; divisor low  = 1 -> 115200 baud
        mov     dx, COM1_IER
        xor     al, al
        out     dx, al                  ; divisor high = 0
        mov     dx, COM1_LCR
        mov     al, 0x03
        out     dx, al                  ; 8 bits, no parity, 1 stop; DLAB off
        mov     dx, COM1_FCR
        mov     al, 0xC7
        out     dx, al                  ; FIFO on and cleared
        mov     dx, COM1_MCR
        mov     al, 0x03
        out     dx, al                  ; DTR | RTS
        pop     rdx
        pop     rax
        ret

; serial_putc - AL = the byte. Preserves everything.
serial_putc:
        push    rax
        push    rdx
        mov     ah, al
.wait:  mov     dx, COM1_LSR
        in      al, dx
        test    al, 0x20                ; transmit holding register empty?
        jz      .wait
        mov     al, ah
        mov     dx, COM1
        out     dx, al
        pop     rdx
        pop     rax
        ret

; serial_puts - RSI = NUL-terminated string. Preserves everything.
serial_puts:
        push    rax
        push    rsi
.next:  lodsb
        test    al, al
        jz      .done
        call    serial_putc
        jmp     .next
.done:  pop     rsi
        pop     rax
        ret

; serial_putdec - EAX = unsigned value, in decimal, no padding.
serial_putdec:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        xor     ecx, ecx                ; how many digits we pushed
        mov     ebx, 10
        test    eax, eax
        jnz     .split
        mov     al, '0'                 ; zero still has one digit
        call    serial_putc
        jmp     .done
.split: test    eax, eax
        jz      .emit
        xor     edx, edx
        div     ebx                     ; EAX = quotient, EDX = remainder
        add     dl, '0'
        push    rdx
        inc     ecx
        jmp     .split
.emit:  test    ecx, ecx
        jz      .done
        pop     rax                     ; digits come back most significant first
        call    serial_putc
        dec     ecx
        jmp     .emit
.done:  pop     rdx
        pop     rcx
        pop     rbx
        pop     rax
        ret

; serial_puthex64 - RAX = value, as exactly 16 lowercase hex digits.
; Fixed width on purpose: the acceptance test matches [0-9a-f]{16}, and a fixed
; width means no leading-zero suppression logic to get wrong.
serial_puthex64:
        push    rax
        push    rbx
        push    rcx
        mov     rbx, rax
        mov     ecx, 16
.next:  rol     rbx, 4                  ; top nibble down into bl
        mov     al, bl
        and     al, 0x0F
        cmp     al, 10
        jb      .dec
        add     al, 'a' - 10
        jmp     .out
.dec:   add     al, '0'
.out:   call    serial_putc
        dec     ecx
        jnz     .next
        pop     rcx
        pop     rbx
        pop     rax
        ret

; serial_err - RSI = message. Prints "ERR: <msg>" and stops the machine.
;
; The ERR: prefix is deliberate. It can never be mistaken for one of the seven
; S1: lines the acceptance tests count, so a failure path can say what went
; wrong without changing the shape of the log the tests match - and the tests
; print the whole capture on failure, so it is seen.
serial_err:
        push    rsi
        lea     rsi, [msg_err]
        call    serial_puts
        pop     rsi
        call    serial_puts
        lea     rsi, [msg_crlf]
        call    serial_puts
        jmp     halt_forever

        align   SECT_ALIGN, db 0
text_end:
text_size       equ     text_end - text_start

; ===========================================================================
; .data - initialised
; ===========================================================================
data_start:

image_handle:   dq      0               ; EFI_HANDLE we were loaded as
system_table:   dq      0               ; EFI_SYSTEM_TABLE *
boot_services:  dq      0               ; EFI_BOOT_SERVICES *

; The seven lines of the spec, and nothing else on this channel.
msg_alive:      db      'S1: alive', 13, 10, 0

msg_err:        db      'ERR: ', 0
msg_crlf:       db      13, 10, 0

        align   FILE_ALIGN, db 0
data_raw_end:
data_raw_size   equ     data_raw_end - data_start

; ===========================================================================
; .data - BSS. Reserved, never emitted: the loader zero-fills the difference
; between VirtualSize and SizeOfRawData, so none of this is in the file.
; ===========================================================================
bss_start:
        resb    0                       ; grows as the stage does
bss_end:

bss_size        equ     bss_end - bss_start
data_virt_size  equ     bss_end - data_start
image_size      equ     ((bss_end - $$) + SECT_ALIGN - 1) & ~(SECT_ALIGN - 1)
