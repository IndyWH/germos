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

; Where the application processors start life. A 4 KB-aligned page below 1 MB,
; because a processor coming out of INIT-SIPI-SIPI begins in real mode at
; CS = vector<<8, IP = 0. Claimed from the firmware before boot services go.
%define TRAMP_BASE      0x8000

; The memory map buffer is static, in our own BSS, rather than pool-allocated.
; Allocating changes the very map whose key we are about to hand to
; ExitBootServices, so a static buffer sidesteps the whole dance.
%define MAP_BUF_SIZE    0x4000
%define BSP_STACK_SIZE  0x4000

%define EFI_INVALID_PARAMETER   0x8000000000000002
%define EFI_BUFFER_TOO_SMALL    0x8000000000000005
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

        ; -------------------------------------------------------------------
        ; Step 2 of the spec: the Graphics Output Protocol, at the highest
        ; resolution it offers with a 32-bit linear framebuffer.
        ;
        ; Nothing here hard-codes a resolution. Whatever the firmware offers is
        ; measured, chosen, and then reported on serial - and the pixel test
        ; reads the answer back out of that same log rather than being told.
        ; -------------------------------------------------------------------
        mov     rax, [boot_services]
        lea     rcx, [gop_guid]
        xor     edx, edx                ; Registration = NULL
        lea     r8, [gop_ptr]
        call    [rax + 0x140]           ; BootServices->LocateProtocol
        test    rax, rax
        jz      .gop_found
        lea     rsi, [err_no_gop]
        call    serial_err
.gop_found:

        mov     rbx, [gop_ptr]          ; RBX, R12-R15 are callee-saved, so the
        mov     rax, [rbx + 0x18]       ; firmware gives them back untouched
        mov     r13d, [rax]             ; Mode->MaxMode
        xor     r12d, r12d              ; mode number under consideration
        mov     r14d, -1                ; best mode so far: none
        mov     dword [best_area], 0
        mov     dword [best_w], 0

.mode_loop:
        cmp     r12d, r13d
        jae     .mode_done

        mov     rax, [rbx]              ; gop->QueryMode
        mov     rcx, rbx
        mov     edx, r12d
        lea     r8, [info_size]
        lea     r9, [info_ptr]
        call    rax
        test    rax, rax
        jnz     .next_mode              ; a mode that will not describe itself

        mov     rdi, [info_ptr]
        mov     eax, [rdi + 0x0C]       ; PixelFormat
        cmp     eax, 1                  ; 0 = RGB reserved, 1 = BGR reserved.
        ja      .free_and_next          ; 2 is a bitmask, 3 is Blt-only: neither
                                        ; is a 32-bit framebuffer we can write
        mov     eax, [rdi + 4]          ; HorizontalResolution
        mov     ecx, [rdi + 8]          ; VerticalResolution
        test    eax, eax
        jz      .free_and_next
        test    ecx, ecx
        jz      .free_and_next
        mov     edx, eax
        imul    edx, ecx                ; area, the thing we maximise
        cmp     edx, [best_area]
        ja      .take
        jb      .free_and_next
        cmp     eax, [best_w]           ; equal area: prefer the wider mode
        jbe     .free_and_next
.take:
        mov     [best_area], edx
        mov     [best_w], eax
        mov     r14d, r12d

.free_and_next:
        mov     rax, [boot_services]
        mov     rcx, [info_ptr]
        call    [rax + 0x48]            ; BootServices->FreePool
.next_mode:
        inc     r12d
        jmp     .mode_loop

.mode_done:
        cmp     r14d, -1
        jne     .have_mode
        lea     rsi, [err_no_mode]
        call    serial_err
.have_mode:

        mov     rax, [rbx + 0x08]       ; gop->SetMode
        mov     rcx, rbx
        mov     edx, r14d
        call    rax
        test    rax, rax
        jz      .mode_set
        lea     rsi, [err_setmode]
        call    serial_err
.mode_set:

        ; Read the numbers back from the protocol rather than from our own
        ; candidate copy: after SetMode, gop->Mode is the authority.
        mov     rax, [rbx + 0x18]       ; gop->Mode
        mov     rdx, [rax + 0x18]       ; FrameBufferBase
        mov     [fb_base], rdx
        mov     rdx, [rax + 0x20]       ; FrameBufferSize
        mov     [fb_size], rdx
        mov     rax, [rax + 0x08]       ; Mode->Info
        mov     ecx, [rax + 4]
        mov     [fb_width], ecx
        mov     ecx, [rax + 8]
        mov     [fb_height], ecx
        mov     ecx, [rax + 0x0C]
        mov     [fb_format], ecx

        ; Stride is PixelsPerScanLine, NOT width. They are allowed to differ,
        ; and assuming otherwise skews every row down the screen.
        mov     ecx, [rax + 0x20]
        test    ecx, ecx
        jnz     .have_stride
        mov     ecx, [fb_width]         ; firmware that leaves it zero means "= width"
.have_stride:
        mov     [fb_pps], ecx

        ; Item 10 identity-maps the first 4 GB. A framebuffer beyond that would
        ; be unmapped the moment we load our own CR3, and the symptom would be a
        ; black screen with no clue. Say so now instead.
        mov     rax, [fb_base]
        add     rax, [fb_size]
        mov     rdx, 0x100000000
        cmp     rax, rdx
        jbe     .fb_reachable
        lea     rsi, [err_fb_high]
        call    serial_err
.fb_reachable:

        lea     rsi, [msg_gop]
        call    serial_puts
        mov     eax, [fb_width]
        call    serial_putdec
        mov     al, 'x'
        call    serial_putc
        mov     eax, [fb_height]
        call    serial_putdec
        lea     rsi, [msg_fb]
        call    serial_puts
        mov     rax, [fb_base]
        call    serial_puthex64
        lea     rsi, [msg_crlf]
        call    serial_puts

        ; -------------------------------------------------------------------
        ; Step 3 of the spec: the memory map, and then throw the ladder away.
        ;
        ; The trampoline page is claimed FIRST, while boot services still
        ; exist. Afterwards there is no allocator left to ask.
        ; -------------------------------------------------------------------
        call    get_memory_map          ; for the fallback scan below
        test    rax, rax
        jz      .map_ok
        mov     rdx, EFI_BUFFER_TOO_SMALL
        cmp     rax, rdx
        je      .map_too_small
        lea     rsi, [err_map]
        call    serial_err
.map_too_small:
        ; Name the number, so that fixing this is changing one constant.
        lea     rsi, [msg_err]
        call    serial_puts
        lea     rsi, [err_map_needs]
        call    serial_puts
        mov     eax, [map_size]
        call    serial_putdec
        lea     rsi, [err_map_have]
        call    serial_puts
        mov     eax, MAP_BUF_SIZE
        call    serial_putdec
        lea     rsi, [err_map_bytes]
        call    serial_puts
        lea     rsi, [msg_crlf]
        call    serial_puts
        jmp     halt_forever
.map_ok:

        mov     qword [tramp_addr], TRAMP_BASE
        call    alloc_tramp_page
        test    rax, rax
        jz      .tramp_ok

        ; The preferred address was refused. Walk the map for any free
        ; conventional page below 1 MB and take the first that will have us.
        lea     r12, [map_buf]
        mov     r13, r12
        add     r13, [map_size]
.scan:
        cmp     r12, r13
        jae     .no_tramp
        cmp     dword [r12], 7          ; EfiConventionalMemory
        jne     .scan_step
        mov     rdx, [r12 + 8]          ; PhysicalStart
        cmp     rdx, 0x1000             ; never the first page
        jb      .scan_step
        cmp     rdx, 0x100000           ; must be reachable in real mode
        jae     .scan_step
        mov     [tramp_addr], rdx
        call    alloc_tramp_page
        test    rax, rax
        jz      .tramp_ok
.scan_step:
        add     r12, [desc_size]        ; stride is desc_size, never sizeof
        jmp     .scan
.no_tramp:
        lea     rsi, [err_no_tramp]
        call    serial_err
.tramp_ok:

        ; ExitBootServices, with the retry the spec names. The map key goes
        ; stale if anything has allocated since the map was fetched - and the
        ; AllocatePages just above did exactly that - so the map is fetched
        ; fresh on every attempt.
        mov     r12d, 5
.ebs_try:
        call    get_memory_map
        test    rax, rax
        jnz     .ebs_map_failed
        mov     rax, [boot_services]
        mov     rcx, [image_handle]
        mov     rdx, [map_key]
        call    [rax + 0xE8]            ; BootServices->ExitBootServices
        test    rax, rax
        jz      .ebs_done
        mov     rdx, EFI_INVALID_PARAMETER
        cmp     rax, rdx
        jne     .ebs_hard
        dec     r12d
        jnz     .ebs_try
        lea     rsi, [err_ebs_stale]
        call    serial_err
.ebs_map_failed:
        lea     rsi, [err_map]
        call    serial_err
.ebs_hard:
        lea     rsi, [err_ebs]
        call    serial_err
.ebs_done:
        ; The firmware's timer would otherwise keep firing into code that no
        ; longer exists. From here there is no IDT either, so any CPU exception
        ; is a triple fault and a reboot - which shows up in a serial capture as
        ; the whole sequence repeating, not as a missing line.
        cli

        ; Stand on our own stack rather than the firmware's.
        lea     rsp, [bsp_stack_top]

        lea     rsi, [msg_exited]
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

; ---------------------------------------------------------------------------
; Firmware call helpers.
;
; Each one re-establishes a 16-byte-aligned frame with 0x40 of scratch below
; it: 32 bytes of shadow space the callee owns, plus room for a fifth and sixth
; stack argument. Returns EFI_STATUS in RAX.
; ---------------------------------------------------------------------------

; get_memory_map - fill map_buf and the four values that describe it.
get_memory_map:
        push    rbp
        mov     rbp, rsp
        and     rsp, -16
        sub     rsp, 0x40
        mov     qword [map_size], MAP_BUF_SIZE
        mov     rax, [boot_services]
        lea     rcx, [map_size]
        lea     rdx, [map_buf]
        lea     r8, [map_key]
        lea     r9, [desc_size]
        lea     r10, [desc_ver]
        mov     [rsp + 0x20], r10       ; DescriptorVersion, the fifth argument
        call    [rax + 0x38]            ; BootServices->GetMemoryMap
        mov     rsp, rbp
        pop     rbp
        ret

; alloc_tramp_page - claim the single page at [tramp_addr], exactly there.
alloc_tramp_page:
        push    rbp
        mov     rbp, rsp
        and     rsp, -16
        sub     rsp, 0x40
        mov     rax, [boot_services]
        mov     ecx, 2                  ; AllocateAddress
        mov     edx, 2                  ; EfiLoaderData
        mov     r8d, 1                  ; one 4 KB page
        lea     r9, [tramp_addr]
        call    [rax + 0x28]            ; BootServices->AllocatePages
        mov     rsp, rbp
        pop     rbp
        ret

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

msg_gop:        db      'S1: gop ', 0
msg_fb:         db      ' fb 0x', 0
msg_exited:     db      'S1: boot services exited', 13, 10, 0

msg_err:        db      'ERR: ', 0
msg_crlf:       db      13, 10, 0

err_no_gop:     db      'no Graphics Output Protocol', 0
err_no_mode:    db      'no GOP mode with a 32-bit linear framebuffer', 0
err_setmode:    db      'GOP SetMode failed', 0
err_fb_high:    db      'framebuffer sits above 4GB, beyond our identity map', 0
err_map:        db      'GetMemoryMap failed', 0
err_map_needs:  db      'memory map needs ', 0
err_map_have:   db      ' bytes, MAP_BUF_SIZE is ', 0
err_map_bytes:  db      ' - raise it', 0
err_no_tramp:   db      'no free page below 1MB for the AP trampoline', 0
err_ebs:        db      'ExitBootServices failed', 0
err_ebs_stale:  db      'ExitBootServices: map key still stale after 5 tries', 0

; EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID, 9042a9de-23dc-4a38-96fb-7aded080516a.
; A GUID is little-endian in its first three fields and big-endian in the last
; two, which is why this is written out field by field rather than as bytes.
        align   8
gop_guid:       dd      0x9042a9de
                dw      0x23dc
                dw      0x4a38
                db      0x96, 0xfb, 0x7a, 0xde, 0xd0, 0x80, 0x51, 0x6a

        align   8
gop_ptr:        dq      0               ; EFI_GRAPHICS_OUTPUT_PROTOCOL *
info_ptr:       dq      0               ; the mode info QueryMode allocates
info_size:      dq      0
fb_base:        dq      0               ; framebuffer physical address
fb_size:        dq      0               ; framebuffer length in bytes
fb_width:       dd      0               ; HorizontalResolution
fb_height:      dd      0               ; VerticalResolution
fb_pps:         dd      0               ; PixelsPerScanLine - the stride, in pixels
fb_format:      dd      0               ; 0 = RGB reserved, 1 = BGR reserved
best_area:      dd      0
best_w:         dd      0

        align   FILE_ALIGN, db 0
data_raw_end:
data_raw_size   equ     data_raw_end - data_start

; ===========================================================================
; .data - BSS.
;
; Declared with ABSOLUTE rather than plain resb. In -f bin everything is one
; contiguous progbits blob, so a bare resb is zero-FILLED into the output file;
; absolute reserves the addresses without emitting a byte, which is what we
; want - the loader zero-fills VirtualSize minus SizeOfRawData for us, and the
; artefact stays the size of the code that is actually in it.
; ===========================================================================
absolute data_raw_end
bss_start:
        alignb  16
map_size:       resq    1               ; in: buffer size; out: bytes used
map_key:        resq    1               ; the key ExitBootServices demands
desc_size:      resq    1               ; stride between descriptors, NOT 40
desc_ver:       resq    1
tramp_addr:     resq    1               ; where the AP trampoline landed

        alignb  16
map_buf:        resb    MAP_BUF_SIZE

        alignb  16
bsp_stack:      resb    BSP_STACK_SIZE
bsp_stack_top:
bss_end:

bss_size        equ     bss_end - bss_start
data_virt_size  equ     bss_end - data_start
image_size      equ     ((bss_end - $$) + SECT_ALIGN - 1) & ~(SECT_ALIGN - 1)
