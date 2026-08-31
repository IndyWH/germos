; ============================================================================
; Stage 2 - Senses.
;
; Grown on Stage 1's proven body: the same hand-assembled PE32+ UEFI
; application, serial first, GOP at the highest 32-bit mode, ExitBootServices
; with the stale-key retry, our own GDT and identity map, the MADT walk, and
; every core woken with INIT-SIPI-SIPI. The bands retire - the APs now park -
; and three organs grow in their place across plan items 8 to 10: an IDT that
; turns CPU exceptions into readable serial lines, a text console on the
; framebuffer, and an interrupt-driven PS/2 keyboard. The console is the
; picture; you type, and the machine answers.
;
; Built with:  nasm -f bin stage2/stage2.asm -o stage2/out/BOOTX64.EFI
;              (run from the repo root - the font incbin path is repo-relative)
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

; Every byte sent to serial is also teed into this mirror buffer, so the
; console (plan item 9) can replay the boot log exactly as the wire carried
; it. 8 KB holds the nine boot lines many times over; once full, the mirror
; quietly stops growing rather than wrapping - the boot log is what matters.
%define LOG_BUF_SIZE    0x2000

; The console's text shadow: one byte per cell. 64 KB holds 128x128 cells -
; this machine's 2048x2048 mode exactly - with room over for larger modes; a
; mode needing more is a reported error, not an overrun.
%define SHADOW_SIZE     0x10000

; More enabled processors than this in the MADT is an error we report, not a
; buffer we overrun. mlrig has 32 logical CPUs; the mirror run uses all of them.
%define MAX_CORES       64
%define AP_STACK_SIZE   0x2000

; Fixed offsets of the patch area inside the trampoline page. The BSP fills
; these in before waking anyone, so the application processors never write to
; the page and there is no race in it.
%define TR_GDTR32       0x100           ; limit16 + base32, for a real-mode lgdt
%define TR_CR3          0x108
%define TR_FPTR_PM32    0x110           ; offset32 + selector16
%define TR_FPTR_LONG    0x118           ; offset32 + selector16
%define TR_PAGE_USED    0x200           ; how much of the page we copy

; PIT channel 2 counts at 1.193182 MHz. Boot services' Stall() is gone by the
; time we need these, so the delays INIT-SIPI-SIPI requires are our own.
%define PIT_10MS        11932
%define PIT_200US       239
%define PIT_25MS        29830

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

        ; -------------------------------------------------------------------
        ; Step 4 of the spec: our own GDT and our own page tables. The
        ; firmware's are gone; from here the machine stands on structures we
        ; built.
        ; -------------------------------------------------------------------
        lea     rax, [gdt]
        mov     [gdtr + 2], rax         ; base is only known at runtime
        lgdt    [gdtr]

        ; Reload CS through a far return - there is no far jump to a label in
        ; long mode. The data selectors follow.
        push    qword 0x08
        lea     rax, [.cs_reloaded]
        push    rax
        o64 retf
.cs_reloaded:
        mov     ax, 0x10
        mov     ds, ax
        mov     es, ax
        mov     ss, ax
        mov     fs, ax
        mov     gs, ax

        call    build_paging
        lea     rax, [pml4]
        mov     cr3, rax                ; and the firmware's tables are gone

        lea     rsi, [msg_paging]
        call    serial_puts

        ; -------------------------------------------------------------------
        ; The IDT - the stage's first new organ. From here a CPU exception is
        ; a readable serial line and a halt, not a silent triple-fault reboot.
        ; Installed before the MADT walk and the wake, so both run covered.
        ; -------------------------------------------------------------------
        call    setup_idt
        lea     rsi, [msg_idt]
        call    serial_puts

        ; -------------------------------------------------------------------
        ; Step 5 of the spec: ask ACPI how many processors this machine has.
        ;
        ; Still valid after ExitBootServices: the EFI system table is
        ; EfiRuntimeServicesData and the ACPI tables are EfiACPIReclaimMemory,
        ; both preserved by definition, and both inside our identity map.
        ; -------------------------------------------------------------------
        call    apic_probe
        mov     [bsp_apic_id], eax

        call    find_rsdp
        test    rax, rax
        jnz     .have_rsdp
        lea     rsi, [err_no_rsdp]
        call    serial_err
.have_rsdp:
        call    find_madt
        test    rax, rax
        jnz     .have_madt
        lea     rsi, [err_no_madt]
        call    serial_err
.have_madt:

        ; Walk the MADT, counting processors and recording their APIC IDs.
        mov     rbx, rax
        mov     ecx, [rbx + 4]          ; Length of the whole table
        mov     r13, rbx
        add     r13, rcx                ; one past the last entry
        lea     rdx, [rbx + 44]         ; entries start after the fixed part
        xor     r14d, r14d              ; how many we have found
        lea     r15, [apic_ids]
.entry:
        cmp     rdx, r13
        jae     .madt_done
        movzx   eax, byte [rdx + 1]     ; entry Length
        test    eax, eax
        jz      .bad_entry              ; a zero length would loop for ever
        movzx   ecx, byte [rdx]         ; entry Type
        cmp     ecx, 0
        je      .local_apic
        cmp     ecx, 9
        je      .local_x2apic
        jmp     .entry_step
.local_apic:                            ; Processor Local APIC
        mov     ecx, [rdx + 4]          ; Flags
        test    ecx, 3                  ; Enabled | Online Capable
        jz      .entry_step
        movzx   ecx, byte [rdx + 3]     ; APIC ID
        jmp     .record
.local_x2apic:                          ; Processor Local x2APIC
        mov     ecx, [rdx + 8]          ; Flags
        test    ecx, 3
        jz      .entry_step
        mov     ecx, [rdx + 4]          ; X2APIC ID
.record:
        cmp     r14d, MAX_CORES
        jae     .too_many
        mov     [r15 + r14*4], ecx
        inc     r14d
.entry_step:
        add     rdx, rax                ; stride is the entry's own length
        jmp     .entry
.bad_entry:
        lea     rsi, [err_madt_len]
        call    serial_err
.too_many:
        lea     rsi, [err_too_many]
        call    serial_err
.madt_done:
        test    r14d, r14d
        jnz     .have_cores
        lea     rsi, [err_no_cores]
        call    serial_err
.have_cores:
        mov     [core_count], r14d

        lea     rsi, [msg_found]
        call    serial_puts
        mov     eax, [core_count]
        call    serial_putdec
        lea     rsi, [msg_crlf]
        call    serial_puts

        ; -------------------------------------------------------------------
        ; Wake every application processor, as Stage 1 proved we can. The
        ; bands retire this stage: each AP takes its index and a stack of its
        ; own, checks in, and parks - the console is the picture now. Only the
        ; BSP ever touches COM1 or the screen; the APs have no path to either,
        ; which is the concurrency doctrine's one-owner-per-device rule
        ; enforced by construction rather than by care.
        ;
        ; The BSP is index 0 by fiat, so the others hand themselves out
        ; indices from 1 upwards.
        ; -------------------------------------------------------------------
        mov     dword [next_index], 1
        mov     dword [checkin], 0

        call    setup_trampoline
        call    wake_cores

        lock inc dword [checkin]        ; the BSP checks itself in

        ; Bounded wait, about a second. A core that never arrives then shows up
        ; as woken disagreeing with found, in one second, with a readable
        ; number - rather than as a hang until the test's 60s timeout with
        ; nothing to read.
        mov     r12d, 40
.wait_cores:
        mov     eax, [checkin]
        cmp     eax, [core_count]
        jae     .all_in
        mov     ax, PIT_25MS
        call    pit_wait
        dec     r12d
        jnz     .wait_cores
.all_in:
        lea     rsi, [msg_woken]
        call    serial_puts
        mov     eax, [checkin]          ; what actually happened, not what we hoped
        call    serial_putdec
        lea     rsi, [msg_crlf]
        call    serial_puts

        ; -------------------------------------------------------------------
        ; The console - the second new organ. Clears the screen, replays the
        ; mirrored boot log, and from here every serial byte is drawn live by
        ; the tee - this very line included.
        ; -------------------------------------------------------------------
        call    console_init
        lea     rsi, [msg_console]
        call    serial_puts
        mov     eax, [con_cols]
        call    serial_putdec
        mov     al, 'x'
        call    serial_putc
        mov     eax, [con_rows]
        call    serial_putdec
        lea     rsi, [msg_crlf]
        call    serial_puts

        call    console_prompt          ; console-only; item 10 moves this
                                        ; after the keyboard-ready line

halt_forever:
        cli
.hang:  hlt
        jmp     .hang

; ---------------------------------------------------------------------------
; The IDT and its exception stubs.
;
; Vectors 8, 10-14, 17, 21 and 30 arrive with a CPU-pushed error code; the
; rest do not. Every stub normalises the frame by pushing a dummy zero where
; the CPU pushed nothing, then pushes its own vector number, so the common
; handler sees one shape: [rsp] = vector, [rsp+8] = error code, [rsp+16] = RIP.
;
; The stubs are padded to a fixed 16 bytes each, so their addresses are
; exc_stubs + vector*16, computed with a RIP-relative lea at runtime - no
; absolute address anywhere, keeping the discipline that earned the stripped
; relocations.
; ---------------------------------------------------------------------------
%define EXC_STUB_SIZE   16
%assign ERRCODE_MASK (1<<8)|(1<<10)|(1<<11)|(1<<12)|(1<<13)|(1<<14)|(1<<17)|(1<<21)|(1<<30)

align 16
exc_stubs:
%assign vec 0
%rep 32
.stub_%+ vec:
  %if ((1 << vec) & ERRCODE_MASK) == 0
        push    byte 0                  ; the dummy where no error code came
  %endif
        push    byte vec
        jmp     exc_common
        times   EXC_STUB_SIZE-($-.stub_%+ vec) db 0xCC
%assign vec vec+1
%endrep

; exc_common - print "ERR: exception <vector> at 0x<rip>" and stop the world.
;
; A parked AP that somehow faults arrives here too and writes serial - a
; deliberate breach of one-owner (plan decision 9): the machine is already
; lost, and an interleaved message beats a silent machine-wide reboot.
exc_common:
        cli
        cld                             ; the serial helpers use lodsb
        lea     rsi, [msg_exc]
        call    serial_puts
        mov     rax, [rsp]              ; the vector the stub pushed
        call    serial_putdec
        lea     rsi, [msg_exc_at]
        call    serial_puts
        mov     rax, [rsp + 16]         ; the RIP the CPU pushed
        call    serial_puthex64
        lea     rsi, [msg_crlf]
        call    serial_puts
        jmp     halt_forever

; idt_set_gate - RDI = the gate, RAX = the handler. Clobbers RAX.
; 64-bit interrupt gate: present, DPL 0, type 0xE, IST 0, selector 0x08.
idt_set_gate:
        mov     [rdi], ax               ; offset 15:0
        mov     word [rdi + 2], 0x08
        mov     word [rdi + 4], 0x8E00
        shr     rax, 16
        mov     [rdi + 6], ax           ; offset 31:16
        shr     rax, 16
        mov     [rdi + 8], eax          ; offset 63:32
        mov     dword [rdi + 12], 0
        ret

; setup_idt - fill gates 0..31 with the stubs and load IDTR. Gates 32..255
; stay zero-filled BSS - not present - until the keyboard item claims its two.
setup_idt:
        push    rax
        push    rcx
        push    rsi
        push    rdi
        lea     rdi, [idt]
        lea     rsi, [exc_stubs]
        xor     ecx, ecx
.fill:
        mov     rax, rsi
        call    idt_set_gate
        add     rdi, 16
        add     rsi, EXC_STUB_SIZE
        inc     ecx
        cmp     ecx, 32
        jb      .fill
        lea     rax, [idt]
        mov     [idtr + 2], rax         ; base is only known at runtime
        lidt    [idtr]
        pop     rdi
        pop     rsi
        pop     rcx
        pop     rax
        ret

; ---------------------------------------------------------------------------
; The console - the framebuffer as a text screen. Only the BSP ever calls any
; of this: one owner per screen, the same doctrine as serial. 16x16 pixel
; cells (the 8x8 font scaled 2x), COLS = W/16, ROWS = H/16, dark background,
; light glyphs.
;
; The framebuffer is mapped uncached and is WRITE-ONLY here, always: the
; console keeps a text shadow buffer, and anything that needs old pixels
; (scrolling) re-renders from the shadow instead of reading them back.
; ---------------------------------------------------------------------------

%define CHAR_SPACE      0x20

; console_init - measure the cells, clear the screen, replay the boot log.
; Called exactly once, from efi_main; clobbers registers freely.
console_init:
        mov     eax, [fb_width]
        shr     eax, 4                  ; /16: cells across
        mov     [con_cols], eax
        mov     ecx, [fb_height]
        shr     ecx, 4
        mov     [con_rows], ecx

        mul     ecx                     ; EDX:EAX = cols * rows
        test    edx, edx
        jnz     .too_big
        cmp     eax, SHADOW_SIZE
        ja      .too_big

        ; The two console colours, encoded for the mode's pixel order. Format
        ; 1 stores B,G,R in ascending bytes, so 0x00RRGGBB lands as is;
        ; format 0 stores R,G,B, so red and blue swap. The grey foreground is
        ; the same both ways.
        mov     eax, 0x00101018         ; rgb(16,16,24), format 1 encoding
        cmp     dword [fb_format], 0
        jne     .bg_done
        mov     eax, 0x00181010         ; the same colour, format 0 encoding
.bg_done:
        mov     [bg_pix], eax
        mov     dword [fg_pix], 0x00E0E0E0      ; rgb(224,224,224)

        lea     rdi, [shadow]           ; a screen full of spaces
        mov     ecx, SHADOW_SIZE / 4
        mov     eax, CHAR_SPACE * 0x01010101
        rep     stosd

        ; Clear the whole framebuffer - stride padding and any part-cell edge
        ; included - so everything on screen is one of our two colours.
        mov     eax, [fb_pps]
        mul     dword [fb_height]       ; EDX:EAX = pixels to paint
        mov     ecx, eax
        mov     rdi, [fb_base]
        mov     eax, [bg_pix]
        rep     stosd

        mov     dword [cur_row], 0
        mov     dword [cur_col], 0
        mov     dword [con_ready], 1

        ; Replay the mirror: the boot log appears on screen byte for byte as
        ; the wire carried it. From here the serial tee draws live as well.
        xor     ebx, ebx
.replay:
        cmp     ebx, [log_len]
        jae     .done
        lea     rsi, [log_buf]
        mov     al, [rsi + rbx]
        call    console_putc
        inc     ebx
        jmp     .replay
.done:
        ret
.too_big:
        lea     rsi, [err_shadow]
        call    serial_err

; console_putc - AL = the byte, drawn at the cursor. Preserves everything.
;
; CR is a no-op (our lines are CRLF and LF does the work), LF is a new line,
; BS steps back and erases one cell, printables draw and advance with wrap.
; Everything else is ignored. Scrolls when the bottom is passed.
console_putc:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        push    rsi
        push    rdi
        cmp     dword [con_ready], 0
        je      .out
        cmp     al, 13
        je      .out
        cmp     al, 10
        je      .newline
        cmp     al, 8
        je      .backspace
        cmp     al, 0x20
        jb      .out                    ; not printable
        cmp     al, 0x7E
        ja      .out

        movzx   eax, al
        mov     ecx, [cur_row]          ; shadow[row * cols + col] = char
        imul    ecx, [con_cols]
        add     ecx, [cur_col]
        lea     rdx, [shadow]
        mov     [rdx + rcx], al

        mov     ebx, [cur_row]
        mov     ecx, [cur_col]
        call    draw_cell

        inc     dword [cur_col]
        mov     eax, [con_cols]
        cmp     [cur_col], eax
        jb      .out                    ; no wrap; else fall into the new line
.newline:
        mov     dword [cur_col], 0
        inc     dword [cur_row]
        mov     eax, [con_rows]
        cmp     [cur_row], eax
        jb      .out
        call    console_scroll
        dec     dword [cur_row]         ; back onto the (new) last row
.out:
        pop     rdi
        pop     rsi
        pop     rdx
        pop     rcx
        pop     rbx
        pop     rax
        ret
.backspace:
        cmp     dword [cur_col], 0
        je      .out                    ; never off the left edge
        dec     dword [cur_col]
        mov     ecx, [cur_row]
        imul    ecx, [con_cols]
        add     ecx, [cur_col]
        lea     rdx, [shadow]
        mov     byte [rdx + rcx], CHAR_SPACE
        mov     eax, CHAR_SPACE
        mov     ebx, [cur_row]
        mov     ecx, [cur_col]
        call    draw_cell
        jmp     .out

; draw_cell - EAX = character, EBX = cell row, ECX = cell column. Preserves
; everything. Each glyph bit becomes a 2x2 block of foreground or background;
; bit 0 of a font byte is the leftmost pixel (see stage2/FONT.md).
draw_cell:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        push    rsi
        push    rdi
        push    r8
        push    r9
        push    r10

        and     eax, 0x7F
        lea     rsi, [font8x8]
        lea     rsi, [rsi + rax*8]      ; the glyph's 8 row bytes

        mov     r8d, [fb_pps]
        shl     r8d, 2                  ; R8 = stride in bytes

        mov     eax, ebx                ; cell row -> scanline -> byte offset
        shl     eax, 4
        imul    rax, r8
        mov     rdi, [fb_base]
        add     rdi, rax
        mov     eax, ecx                ; cell column -> byte offset
        shl     eax, 6                  ; * 16 pixels * 4 bytes
        add     rdi, rax

        mov     r9d, [fg_pix]
        mov     r10d, [bg_pix]

        mov     ecx, 8                  ; the glyph's 8 rows
.frow:
        lodsb
        mov     bl, al
        push    rcx
        push    rdi
        mov     edx, 8                  ; the row's 8 bits, LSB first
.fbit:
        mov     eax, r10d
        test    bl, 1
        jz      .paint
        mov     eax, r9d
.paint:
        mov     [rdi], eax              ; 2x2: two pixels on this scanline
        mov     [rdi + 4], eax
        mov     [rdi + r8], eax         ; and two on the next
        mov     [rdi + r8 + 4], eax
        add     rdi, 8
        shr     bl, 1
        dec     edx
        jnz     .fbit
        pop     rdi
        pop     rcx
        lea     rdi, [rdi + r8*2]       ; down two scanlines
        dec     ecx
        jnz     .frow

        pop     r10
        pop     r9
        pop     r8
        pop     rdi
        pop     rsi
        pop     rdx
        pop     rcx
        pop     rbx
        pop     rax
        ret

; draw_cursor - the solid block at the cursor cell. Preserves everything.
; No blinking: nothing on this machine moves without cause.
draw_cursor:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        push    rdi
        push    r8

        mov     r8d, [fb_pps]
        shl     r8d, 2
        mov     eax, [cur_row]
        shl     eax, 4
        imul    rax, r8
        mov     rdi, [fb_base]
        add     rdi, rax
        mov     eax, [cur_col]
        shl     eax, 6
        add     rdi, rax

        mov     eax, [fg_pix]
        mov     ebx, 16                 ; 16 scanlines
.line:
        mov     rdx, rdi
        mov     ecx, 16                 ; of 16 pixels
        rep     stosd
        mov     rdi, rdx
        add     rdi, r8
        dec     ebx
        jnz     .line

        pop     r8
        pop     rdi
        pop     rdx
        pop     rcx
        pop     rbx
        pop     rax
        ret

; erase_cursor - redraw the cursor cell from the shadow. Preserves everything.
erase_cursor:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        mov     ecx, [cur_row]
        imul    ecx, [con_cols]
        add     ecx, [cur_col]
        lea     rdx, [shadow]
        movzx   eax, byte [rdx + rcx]
        mov     ebx, [cur_row]
        mov     ecx, [cur_col]
        call    draw_cell
        pop     rdx
        pop     rcx
        pop     rbx
        pop     rax
        ret

; console_scroll - shift the shadow up one text row and re-render the whole
; screen from it. The framebuffer is never read. Preserves everything.
console_scroll:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        push    rsi
        push    rdi

        mov     ecx, [con_rows]
        dec     ecx
        imul    ecx, [con_cols]         ; bytes that move up
        lea     rdi, [shadow]
        lea     rsi, [shadow]
        mov     eax, [con_cols]
        add     rsi, rax
        rep     movsb                   ; forward copy, dest below src: safe

        mov     ecx, [con_cols]         ; blank the new last row
        mov     al, CHAR_SPACE
        rep     stosb

        xor     ebx, ebx                ; re-render: row by row, cell by cell
.row:
        xor     ecx, ecx
.col:
        mov     eax, ebx
        imul    eax, [con_cols]
        add     eax, ecx
        lea     rdx, [shadow]
        movzx   eax, byte [rdx + rax]
        call    draw_cell
        inc     ecx
        cmp     ecx, [con_cols]
        jb      .col
        inc     ebx
        cmp     ebx, [con_rows]
        jb      .row

        pop     rdi
        pop     rsi
        pop     rdx
        pop     rcx
        pop     rbx
        pop     rax
        ret

; console_prompt - "> " and the cursor, console-only: the serial channel
; carries the nine lines and then the raw echo, never the prompt. Records
; where the typed text begins, so backspace can never eat the prompt.
console_prompt:
        push    rax
        mov     al, '>'
        call    console_putc
        mov     al, ' '
        call    console_putc
        mov     eax, [cur_col]
        mov     [prompt_min], eax
        call    draw_cursor
        pop     rax
        ret

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
;
; Also the tee of the boot-log mirror: every byte that goes to the wire lands
; in log_buf too, so the console can later replay the boot log byte for byte
; (plan decision 10). Only the BSP calls this, so the append needs no lock.
serial_putc:
        push    rax
        push    rbx
        push    rdx
        mov     ebx, [log_len]
        cmp     ebx, LOG_BUF_SIZE
        jae     .mirrored               ; full: the mirror stops, serial goes on
        lea     rdx, [log_buf]
        mov     [rdx + rbx], al
        inc     dword [log_len]
.mirrored:
        cmp     dword [con_ready], 0    ; once the console is up, the tee
        je      .wire                   ; draws every serial byte live
        call    console_putc
.wire:
        mov     ah, al
.wait:  mov     dx, COM1_LSR
        in      al, dx
        test    al, 0x20                ; transmit holding register empty?
        jz      .wait
        mov     al, ah
        mov     dx, COM1
        out     dx, al
        pop     rdx
        pop     rbx
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
; S2: lines the acceptance tests count, so a failure path can say what went
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

; ---------------------------------------------------------------------------
; Waking the other processors.
; ---------------------------------------------------------------------------

; pit_wait - AX = ticks of the 1.193182 MHz PIT, so at most about 54 ms.
; Channel 2, mode 0, gated by port 0x61 bit 0, polled on OUT2 in bit 5. The
; speaker bit is deliberately left clear.
pit_wait:
        push    rax
        push    rcx
        mov     cx, ax
        in      al, 0x61
        and     al, 0xFC                ; speaker off
        or      al, 0x01                ; gate 2 on
        out     0x61, al
        mov     al, 0xB0                ; channel 2, lo/hi, mode 0, binary
        out     0x43, al
        mov     al, cl
        out     0x42, al
        mov     al, ch
        out     0x42, al
.wait:
        in      al, 0x61
        test    al, 0x20                ; OUT2 high means terminal count
        jz      .wait
        pop     rcx
        pop     rax
        ret

; apic_send_ipi - EAX = the ICR low value, R13D = destination APIC ID.
apic_send_ipi:
        push    rax
        push    rcx
        push    rdx
        cmp     dword [apic_x2], 0
        jne     .x2

        ; xAPIC: destination high first, then the low word, which sends it.
        mov     rcx, [apic_mmio]
        mov     edx, r13d
        shl     edx, 24
        mov     [rcx + 0x310], edx
        mov     [rcx + 0x300], eax
.status:
        mov     edx, [rcx + 0x300]
        test    edx, 1 << 12            ; delivery status: still pending?
        jnz     .status
        jmp     .done

.x2:
        ; x2APIC: one 64-bit MSR write, destination in the high half.
        ;
        ; There is deliberately NO delivery-status poll here. In x2APIC mode
        ; bit 12 of the ICR is reserved and the wrmsr is itself the serialising
        ; event, so polling it would spin for ever on a bit that never changes.
        mov     edx, r13d
        mov     ecx, 0x830
        wrmsr
.done:
        pop     rdx
        pop     rcx
        pop     rax
        ret

; setup_trampoline - copy the blob to the page we claimed and fill in the four
; values it cannot know at assembly time.
setup_trampoline:
        lea     rax, [ap_entry]         ; the far pointer is offset32:selector,
        mov     rdx, rax                ; so the entry must live below 4 GB
        shr     rdx, 32
        jz      .entry_ok
        lea     rsi, [err_ap_high]
        call    serial_err
.entry_ok:

        mov     rdi, [tramp_addr]
        lea     rsi, [tramp_start]
        mov     ecx, TR_PAGE_USED
        rep     movsb

        mov     rdi, [tramp_addr]

        lea     rax, [gdt]              ; our GDT, as a 32-bit base
        mov     [gdtr32 + 2], eax
        mov     ax, [gdtr32]
        mov     [rdi + TR_GDTR32], ax
        mov     eax, [gdtr32 + 2]
        mov     [rdi + TR_GDTR32 + 2], eax

        lea     rax, [pml4]
        mov     [rdi + TR_CR3], eax

        mov     rax, [tramp_addr]       ; where the 32-bit stage will live
        add     rax, tramp_pm32 - tramp_start
        mov     [rdi + TR_FPTR_PM32], eax
        mov     word [rdi + TR_FPTR_PM32 + 4], 0x18

        lea     rax, [ap_entry]
        mov     [rdi + TR_FPTR_LONG], eax
        mov     word [rdi + TR_FPTR_LONG + 4], 0x08
        ret

; wake_cores - INIT, then SIPI twice, to every recorded APIC ID but our own.
wake_cores:
        xor     r12d, r12d
.next_core:
        cmp     r12d, [core_count]
        jae     .done
        lea     rax, [apic_ids]
        mov     r13d, [rax + r12*4]
        cmp     r13d, [bsp_apic_id]
        je      .skip

        mov     eax, 0x00004500         ; INIT, assert, edge, no shorthand
        call    apic_send_ipi
        mov     ax, PIT_10MS
        call    pit_wait

        mov     eax, [tramp_addr]       ; SIPI vector is the page number
        shr     eax, 12
        or      eax, 0x00004600
        call    apic_send_ipi
        mov     ax, PIT_200US
        call    pit_wait

        mov     eax, [tramp_addr]       ; the second SIPI, as the manual asks
        shr     eax, 12
        or      eax, 0x00004600
        call    apic_send_ipi
        mov     ax, PIT_200US
        call    pit_wait
.skip:
        inc     r12d
        jmp     .next_core
.done:
        ret

; ---------------------------------------------------------------------------
; ap_entry - where every woken processor arrives, in long mode, on our tables.
;
; No serial. No screen. No firmware. Nothing shared but two locked counters.
; The bands are gone: each core takes its index and a stack of its own - a
; later ring will want both - checks in, and parks.
; ---------------------------------------------------------------------------
ap_entry:
        mov     ax, 0x10
        mov     ds, ax
        mov     es, ax
        mov     ss, ax
        mov     fs, ax
        mov     gs, ax
        cld

        ; The same IDT as the BSP, already built - the BSP ran setup_idt long
        ; before any SIPI went out. A parked core that somehow faults then
        ; halts with a message instead of triple-faulting the whole machine.
        lidt    [idtr]

        mov     eax, 1                  ; needs no stack, so it comes first
        lock xadd [next_index], eax     ; EAX = the index that is now ours

        cmp     eax, MAX_CORES
        jae     .park                   ; more cores than stacks: park quietly

        mov     ecx, eax
        imul    rcx, rcx, AP_STACK_SIZE
        lea     rsp, [ap_stacks_top]
        sub     rsp, rcx

        lock inc dword [checkin]
.park:
        cli
.hang:  hlt
        jmp     .hang

; ---------------------------------------------------------------------------
; ACPI and the local APIC.
; ---------------------------------------------------------------------------

; apic_probe - work out how this processor's local APIC is addressed, enable
; it, and return the BSP's own APIC ID in EAX.
;
; Both addressing modes are supported because we cannot assume which one the
; firmware left us in, and guessing wrong is a silent hang rather than an error.
apic_probe:
        mov     ecx, 0x1B               ; IA32_APIC_BASE
        rdmsr
        mov     r8d, edx
        shl     r8, 32
        or      r8, rax
        mov     [apic_base_msr], r8

        xor     ecx, ecx
        test    r8d, 1 << 10            ; bit 10: x2APIC mode enabled
        setnz   cl
        mov     [apic_x2], ecx

        mov     rax, r8
        mov     rdx, 0x000FFFFFFFFFF000 ; the base address field, bits 12..51
        and     rax, rdx
        mov     [apic_mmio], rax

        test    ecx, ecx
        jnz     .x2

        ; xAPIC: memory mapped, and the identity map already covers it.
        mov     r9, rax
        mov     eax, [r9 + 0xF0]        ; spurious interrupt vector register
        or      eax, 0x100              ; APIC software enable
        mov     [r9 + 0xF0], eax
        mov     eax, [r9 + 0x20]        ; APIC ID register
        shr     eax, 24
        ret
.x2:
        mov     ecx, 0x80F              ; IA32_X2APIC_SIVR
        rdmsr
        or      eax, 0x100
        wrmsr
        mov     ecx, 0x802              ; IA32_X2APIC_APICID
        rdmsr
        ret

; find_rsdp - the ACPI 2.0 RSDP from the EFI configuration table, or 0.
find_rsdp:
        mov     rax, [system_table]
        mov     rcx, [rax + 0x68]       ; NumberOfTableEntries
        mov     rdx, [rax + 0x70]       ; ConfigurationTable
        lea     rsi, [acpi_guid]
        mov     r8, [rsi]
        mov     r9, [rsi + 8]
.next:
        test    rcx, rcx
        jz      .none
        cmp     [rdx], r8               ; a GUID is 16 bytes: two compares
        jne     .step
        cmp     [rdx + 8], r9
        jne     .step
        mov     rax, [rdx + 16]         ; VendorTable is the RSDP
        ret
.step:
        add     rdx, 24                 ; GUID + pointer
        dec     rcx
        jmp     .next
.none:
        xor     eax, eax
        ret

; find_madt - RAX = RSDP in; the MADT ("APIC" table) or 0 out.
find_madt:
        mov     rax, [rax + 24]         ; XsdtAddress
        test    rax, rax
        jz      .none
        mov     rbx, rax
        mov     ecx, [rbx + 4]          ; Length
        cmp     ecx, 36
        jbe     .none
        sub     ecx, 36                 ; the fixed header
        shr     ecx, 3                  ; ... leaves 8-byte pointers
        lea     rdx, [rbx + 36]
.next:
        test    ecx, ecx
        jz      .none
        mov     rax, [rdx]
        test    rax, rax
        jz      .step
        cmp     dword [rax], 'APIC'
        je      .found
.step:
        add     rdx, 8
        dec     ecx
        jmp     .next
.none:
        xor     eax, eax
.found:
        ret

; build_paging - identity-map the first 4 GB with 2 MB pages.
;
; One PML4, one PDPT, four page directories: 24 KB of tables for 4 GB of
; address space. That covers low memory, the trampoline page, our own image and
; stack, and the framebuffer. 1 GB pages would halve it again but need a CPUID
; check that QEMU's default CPU may not pass, so 2 MB is the safe unit.
;
; Everything not written here is left as the loader zero-filled it, which is
; exactly the "not present" we want.
build_paging:
        lea     rax, [pdpt]
        or      rax, 3                  ; present | writable
        lea     rdi, [pml4]
        mov     [rdi], rax              ; PML4[0] -> PDPT, the first 512 GB

        lea     rdi, [pdpt]
        lea     rsi, [pd_tables]
        mov     ecx, 4                  ; four directories, 1 GB each
.pdpt:
        mov     rax, rsi
        or      rax, 3
        mov     [rdi], rax
        add     rdi, 8
        add     rsi, 0x1000
        dec     ecx
        jnz     .pdpt

        lea     rdi, [pd_tables]
        xor     rax, rax                ; physical address of the current page
        mov     r8, [fb_base]
        mov     r9, r8
        add     r9, [fb_size]
        mov     ecx, 2048               ; 2048 * 2 MB = 4 GB
.pd:
        mov     rdx, rax
        or      rdx, 0x83               ; present | writable | 2 MB page

        ; A page overlapping the framebuffer is marked uncached. Left
        ; writeback, our pixels could sit in a cache line and never reach the
        ; screen - a black screen with a serial log claiming success.
        mov     r10, rax
        add     r10, 0x200000
        cmp     rax, r9
        jae     .store
        cmp     r10, r8
        jbe     .store
        or      rdx, 0x18               ; PWT | PCD
.store:
        mov     [rdi], rdx
        add     rdi, 8
        add     rax, 0x200000
        dec     ecx
        jnz     .pd
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

; ---------------------------------------------------------------------------
; The AP trampoline.
;
; Copied to a 4 KB-aligned page below 1 MB, because a processor coming out of
; INIT-SIPI-SIPI starts in real mode at CS = vector<<8, IP = 0. It therefore
; cannot contain a single absolute address of its own: it derives its base from
; CS, and every value it cannot compute is patched in by the BSP beforehand.
;
; Real mode -> 32-bit protected mode -> long mode, the conventional route. The
; one-shot trick of setting PE and PG together is deliberately NOT used: it
; runs briefly with a real-mode CS cache in long mode, which is not
; architecturally defined, and this code has to survive Stage 7 on real metal.
; ---------------------------------------------------------------------------
tramp_start:
bits 16
        cli
        cld
        mov     ax, cs
        mov     ds, ax
        movzx   ebx, ax
        shl     ebx, 4                  ; EBX = this page's physical address

        o32 lgdt [TR_GDTR32]            ; DS is CS, so this is page-relative
        mov     eax, cr0
        or      eax, 1                  ; PE
        mov     cr0, eax
        jmp     far dword [TR_FPTR_PM32]

bits 32
tramp_pm32:
        mov     ax, 0x10
        mov     ds, ax
        mov     es, ax
        mov     ss, ax
        mov     fs, ax
        mov     gs, ax

        mov     eax, cr4
        or      eax, 1 << 5             ; PAE
        mov     cr4, eax

        mov     eax, [ebx + TR_CR3]
        mov     cr3, eax                ; the BSP's tables, already built

        mov     ecx, 0xC0000080         ; EFER
        rdmsr
        or      eax, 1 << 8             ; LME
        wrmsr

        mov     eax, cr0
        or      eax, 0x80000001         ; PG | PE
        mov     cr0, eax
        jmp     far dword [ebx + TR_FPTR_LONG]

        ; Everything above must fit below the patch area.
        times   TR_GDTR32-($-tramp_start) db 0
        times   TR_PAGE_USED-($-tramp_start) db 0
tramp_end:
bits 64

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

; The nine lines of the spec (items 8 to 10 add idt, console and keyboard),
; then the raw echo of what is typed, and nothing else on this channel.
msg_alive:      db      'S2: alive', 13, 10, 0

msg_gop:        db      'S2: gop ', 0
msg_fb:         db      ' fb 0x', 0
msg_exited:     db      'S2: boot services exited', 13, 10, 0
msg_paging:     db      'S2: gdt and paging ours', 13, 10, 0
msg_idt:        db      'S2: idt ready', 13, 10, 0
msg_found:      db      'S2: cores found ', 0
msg_woken:      db      'S2: cores woken ', 0
msg_console:    db      'S2: console ', 0

msg_err:        db      'ERR: ', 0
msg_exc:        db      'ERR: exception ', 0
msg_exc_at:     db      ' at 0x', 0
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
err_no_rsdp:    db      'no ACPI 2.0 RSDP in the EFI configuration table', 0
err_no_madt:    db      'no MADT (APIC table) in the XSDT', 0
err_madt_len:   db      'MADT has an entry of length zero', 0
err_too_many:   db      'more enabled processors than MAX_CORES - raise it', 0
err_no_cores:   db      'MADT lists no enabled processors at all', 0
err_ap_high:    db      'ap_entry sits above 4GB - the trampoline cannot reach it', 0
err_shadow:     db      'console shadow too small for this mode - raise SHADOW_SIZE', 0

; The shared font, byte for byte the file the pixel checker renders from.
; 128 glyphs, 8 bytes each, row per byte, bit 0 leftmost - stage2/FONT.md.
        align   8
font8x8:        incbin  "stage2/font8x8.bin"

; Our own GDT. Four descriptors, flat, base 0, limit 4 GB.
;
;   0x08  64-bit code   - what the BSP and every woken core runs in
;   0x10  data          - flat, for every data selector
;   0x18  32-bit code   - used only by the AP trampoline's middle step, on the
;                         way from real mode up to long mode
        align   8
gdt:
        dq      0x0000000000000000      ; 0x00 null
        dq      0x00AF9A000000FFFF      ; 0x08 code64: L=1, present, ring 0
        dq      0x00CF92000000FFFF      ; 0x10 data:   writable, 4 GB
        dq      0x00CF9A000000FFFF      ; 0x18 code32: D=1, present, ring 0
gdt_end:

; The 64-bit pseudo-descriptor for lgdt. The base is filled in at runtime,
; because we do not know where we were loaded.
gdtr:           dw      gdt_end - gdt - 1
                dq      0
; And the 32-bit form the trampoline needs, since a processor in real mode
; cannot load a 64-bit base. The GDT is below 4 GB, so this is always enough.
gdtr32:         dw      gdt_end - gdt - 1
                dd      0

; The IDT pseudo-descriptor. Base filled in by setup_idt at runtime; loaded by
; the BSP there and by every AP before it parks.
idtr:           dw      256*16 - 1
                dq      0

; EFI_ACPI_20_TABLE_GUID, 8868e871-e4f1-11d3-bc22-0080c73c8881. The entry in
; the EFI configuration table under this GUID is the ACPI 2.0 RSDP.
        align   8
acpi_guid:      dd      0x8868e871
                dw      0xe4f1
                dw      0x11d3
                db      0xbc, 0x22, 0x00, 0x80, 0xc7, 0x3c, 0x88, 0x81

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

        alignb  64
next_index:     resd    1               ; next free core index, handed out with xadd
checkin:        resd    1               ; cores that have arrived and parked

        alignb  16
log_len:        resd    1               ; bytes of boot log mirrored so far
        alignb  16
log_buf:        resb    LOG_BUF_SIZE    ; the mirror the console will replay

        alignb  16
core_count:     resd    1               ; enabled processors the MADT listed
bsp_apic_id:    resd    1
apic_x2:        resd    1               ; non-zero if the APIC is in x2APIC mode
apic_base_msr:  resq    1
apic_mmio:      resq    1               ; xAPIC register block, normally FEE00000
apic_ids:       resd    MAX_CORES

; One stack per core. Index 0 is the BSP's and it keeps bsp_stack, so these are
; indices 1 upwards; the array is sized for MAX_CORES either way.
        alignb  16
ap_stacks:      resb    MAX_CORES * AP_STACK_SIZE
ap_stacks_top:

; The IDT itself: 256 gates of 16 bytes. Zero-filled BSS means every gate not
; explicitly set is simply not present.
        alignb  16
idt:            resb    256*16

; The console. One owner - the BSP - so none of this needs a lock.
        alignb  16
con_cols:       resd    1               ; cells across = width / 16
con_rows:       resd    1               ; cells down   = height / 16
cur_row:        resd    1
cur_col:        resd    1
con_ready:      resd    1               ; non-zero once the tee may draw
prompt_min:     resd    1               ; the column typed text starts at
bg_pix:         resd    1               ; background, encoded for the mode
fg_pix:         resd    1               ; foreground, encoded for the mode
        alignb  16
shadow:         resb    SHADOW_SIZE     ; one byte per cell - what is on screen

; Page tables. 4 KB alignment is architectural, not a preference.
        alignb  4096
pml4:           resb    4096
pdpt:           resb    4096
pd_tables:      resb    4 * 4096        ; four directories, 2048 entries in all
bss_end:

bss_size        equ     bss_end - bss_start
data_virt_size  equ     bss_end - data_start
image_size      equ     ((bss_end - $$) + SECT_ALIGN - 1) & ~(SECT_ALIGN - 1)
