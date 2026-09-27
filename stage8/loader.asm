; ============================================================================
; Stage 8 ring 8a - the loader (stage8/spec.md decision 4; stage8/PARTS.md).
;
; The floor under the molt: the part of the seed that no grown part replaces
; and no part can write. stage8/stage8.asm includes this file at the start
; of .text, below its constants (NASM's %define is positional), so it
; assembles into the one image as ever; it is its own file so that it can be
; frozen apart from the seed - at ring 8a item 16b, after Cowork's review,
; and from then opened by the owner's hand alone.
;
; What it holds, moved here from the seed at item 14 without a changed
; instruction (plan decision 10):
;   - efi_main from the firmware to the handover: serial first, the GOP,
;     the memory map and ExitBootServices, the GDT, the page tables, the
;     IDT, the MADT and the cores, the regions, the disk, the notebook, the
;     home table, the NIC, the glass core, the PIC and the i8042 gates, and
;     the i8042's init - then a jump to the seed's seed_main;
;   - serial and the firmware's GetMemoryMap;
;   - paging: build_paging, and text_split, which maps the whole of .text
;     read-only on 4 KB pages; CR0.WP is set straight after the CR3 load
;     here and in the seed's AP trampoline, so the protection holds on every
;     core from before the first byte of any part runs;
;   - the IDT, the exception stubs and exc_common;
;   - PCI configuration access and the PIT wait;
;   - the disk's read path: the AHCI driver with its one command routine
;     (ahci_rw, which the seed's writers call through disk_rw and home_rw),
;     DISK.md's port choice and GPT validation, the notebook's scan and the
;     home table's read;
;   - SHA-256, and every constant the above reads, inside .text.
; What item 15 added, the molt's floor (PARTS.md): the notebook's molt
; scan, the boot with a molt note in mouse_init's place (the known answer,
; the door, the boot note, a live part's init), the header rule and the one
; call into a part; their constants inside .text with the rest.
; What item 16 added: the controller's minimal setup and the Esc window;
; the TCO found, its evidence read and cleared and the timer halted at
; step 2, then armed at step 6 (the owner's decision at item 16); the
; recovery table and the demoted notes; the heartbeat's breaths at the
; disk's command wait and the pet; the blame line in exc_common.
; Its mutable state is BSS: LOADER_STATE at the end of this file is one
; page-aligned block the seed places in its BSS, and no address in it is
; handed to a part. The seed's own code sets two of its flags - the health
; mark's health_done, and note_overflow's overflow, reached from the
; stubs, the live key upcall and mouse_sink when a ring is full - and
; reads in_wait and ready_tsc; nothing else of the seed's writes it.
;
; What it calls in the seed, which stays the seed's to change: the display's
; EDID, the ACPI walk and the wake of the cores, the TSC's calibration, the
; glass and the console, the PCI scan, gpt_write when DISK.md's rule formats
; a blank disk, home_recount and the choices row, the NIC, the PIC and the
; interrupt entries, and the i8042's init; and for the molt, molt_note (the
; notebook's writer), str_copy and put_dec, the home table's lookups,
; svc3_fill and pointer_centre, and the part stubs it gives IRQ1 and IRQ12;
; for Esc and the pet, i8042_wait_ibf, console_puts and console_putc, and
; it reads tsc_per_ms, the obs page's frame count and the part's region.
; ============================================================================
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

        ; The display's own word first (GLASS.md, "The screen"; line two):
        ; the EDID from the VGA device's BAR2, the preferred mode out of its
        ; first detailed timing descriptor - or none. The mode loop below
        ; remembers the mode that matches it, and takes it.
        call    edid_read

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

        ; Ring 7c (plan decision 2, A5): the console's fixed limits, judged
        ; here before a mode is a candidate - the same limits surf_describe
        ; and console_init enforce later with a halt, mirrored so that a
        ; GOP listing a mode the console cannot hold (Intel's on the HP
        ; lists the monitor's own) skips it and takes the next, instead of
        ; dying on it: at least 8 cells each way, at most STRIP_CELLS/2
        ; columns, the panels' rows (rows - 4) at most SURF_ROWS_MAX, the
        ; cells in all at most SHADOW_SIZE. PANEL_CELLS depends on the
        ; split and is judged as before.
        mov     edx, eax
        shr     edx, 4                  ; cells across
        cmp     edx, 8
        jb      .free_and_next
        cmp     edx, STRIP_CELLS / 2
        ja      .free_and_next
        mov     r8d, ecx
        shr     r8d, 4                  ; cells down
        cmp     r8d, 8
        jb      .free_and_next
        lea     r9d, [r8d - 4]          ; the panels' rows
        cmp     r9d, SURF_ROWS_MAX
        ja      .free_and_next
        imul    edx, r8d                ; cells in all
        cmp     edx, SHADOW_SIZE
        ja      .free_and_next

        cmp     eax, [edid_w]           ; the display's preferred mode, if this
        jne     .not_preferred          ; is it (edid_w is 0 when none was stated)
        cmp     ecx, [edid_h]
        jne     .not_preferred
        cmp     dword [edid_mode], -1
        jne     .not_preferred          ; the first match wins
        mov     [edid_mode], r12d
.not_preferred:
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
        ; The display's preferred mode wins when it is in the list; else
        ; Stage 1's highest stands (spec decision 8).
        cmp     dword [edid_mode], -1
        je      .keep_highest
        mov     r14d, [edid_mode]
.keep_highest:
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
        mov     rax, cr0                ; CR0.WP (ring 8a): from here a write
        or      rax, 1 << 16            ; into .text faults, in ring 0 too -
        mov     cr0, rax                ; PARTS.md, "The read-only floor"

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
        ; The clock - the time-stamp counter calibrated once against the PIT
        ; (Stage 5 plan decision 6), so ticks_ms can answer a component
        ; without a new interrupt. Interrupts are still off; nothing is
        ; racing the PIT.
        ; -------------------------------------------------------------------
        call    tsc_calibrate

        ; The obs page begins: the magic, the clock it is read with.
        mov     rax, 'OBSPAGE2'
        mov     [obs_page + OBS_MAGIC], rax
        mov     rax, [tsc_per_ms]
        mov     [obs_page + OBS_TSC_PER_MS], rax
        mov     rax, [tsc_boot]
        mov     [obs_page + OBS_TSC_BOOT], rax
        mov     rax, [tsc_per_ms]
        imul    rax, rax, 1000
        xor     edx, edx
        mov     ecx, FRAME_HZ
        div     rcx
        mov     [frame_ticks], rax      ; one sixtieth of a second, in ticks

        ; The service table a component is born into (GERMLINE.md, "The
        ; service table"): four addresses, filled here with RIP-relative
        ; leas - no absolute address anywhere, as the stripped relocations
        ; demand.
        lea     rax, [svc_draw_text]
        mov     [svc_table + 8], rax
        lea     rax, [svc_panel_size]
        mov     [svc_table + 16], rax
        lea     rax, [ticks_ms]
        mov     [svc_table + 24], rax
        lea     rax, [svc_fill]
        mov     [svc_table + 32], rax
        mov     rax, [tsc_per_ms]       ; consecutive steps begin this far apart
        imul    rax, rax, STEP_GAP_MS
        mov     [step_gap], rax

        ; -------------------------------------------------------------------
        ; The console - the second new organ. Clears the screen, replays the
        ; mirrored boot log, and from here every serial byte is drawn live by
        ; the tee - this very line included.
        ; -------------------------------------------------------------------
        call    glass_init              ; the four regions from the mode
        call    console_init            ; the conversation panel, a surface now
        mov     eax, [scr_cols]
        mov     [obs_page + OBS_COLS], rax
        mov     eax, [scr_rows]
        mov     [obs_page + OBS_ROWS], rax
        lea     rsi, [msg_console]
        call    serial_puts
        mov     eax, [scr_cols]
        call    serial_putdec
        mov     al, 'x'
        call    serial_putc
        mov     eax, [scr_rows]
        call    serial_putdec
        lea     rsi, [msg_crlf]
        call    serial_puts

        ; -------------------------------------------------------------------
        ; The disk (stage7/DISK.md, ring 7a): the AHCI controller found by
        ; class and owned, every port with a SATA disk identified and
        ; classified, one port chosen by the selection rule - a GermOS
        ; table, else a blank disk formatted ("S7: gpt written"), else a
        ; named refusal - and the two partition descriptors read from its
        ; table. Then the disk line. All of it with interrupts off and
        ; polled, so that S7: keyboard ready stays the last line before sti.
        ; -------------------------------------------------------------------
        call    ahci_find
        call    disk_select

        lea     rsi, [msg_disk]         ; the disk line
        call    serial_puts
        mov     eax, [ahci_port]
        call    serial_putdec
        mov     al, ' '
        call    serial_putc
        mov     eax, [ahci_sectors]
        call    serial_putdec
        lea     rsi, [msg_notes_at]
        call    serial_puts
        mov     eax, [part_notes + PART_BASE]
        call    serial_putdec
        lea     rsi, [msg_home_at]
        call    serial_puts
        mov     eax, [part_home + PART_BASE]
        call    serial_putdec
        lea     rsi, [msg_crlf]
        call    serial_puts
        mov     eax, [part_notes + PART_SECTORS]
        mov     [disk_sectors], eax     ; the notebook's capacity: its partition's

        ; -------------------------------------------------------------------
        ; The notebook, on the notes partition (NOTEBOOK.md unchanged): a
        ; recognised partition is scanned and counted; a blank one is
        ; formatted.
        ; -------------------------------------------------------------------
        call    notebook_init

        ; -------------------------------------------------------------------
        ; The home image (ring 6b, HOME.md), on the home partition: always
        ; present on a GermOS disk - formatted or scanned, then its line.
        ; -------------------------------------------------------------------
        mov     dword [home_present], 1
        call    home_init

        ; -------------------------------------------------------------------
        ; The NIC (stage7/WIRE.md, ring 7b): the e1000e when the scan found
        ; one - owned, reset, its MAC read from RAL0/RAH0, its link awaited,
        ; its rings given - else the virtio-net, negotiated as before. The
        ; nic line, and on the e1000e path the link line. Nothing is sent on
        ; the network at boot. Still with interrupts off and polled.
        ; -------------------------------------------------------------------
        call    nic_find

        ; -------------------------------------------------------------------
        ; The component region - where a grown component will live. Line
        ; twelve says where, because the address moves with every build and
        ; a component must never assume it (GERMLINE.md).
        ; -------------------------------------------------------------------
        lea     rsi, [msg_region]       ; line thirteen
        call    serial_puts
        lea     rax, [comp_region + APP_BLOB_OFF]
        call    serial_puthex64
        lea     rsi, [msg_region_cap]
        call    serial_puts

        ; The obs page - line fourteen says where, so the twin and the
        ; harness can read the machine's own numbers through the monitor.
        lea     rsi, [msg_obs]
        call    serial_puts
        lea     rax, [obs_page]
        call    serial_puthex64
        lea     rsi, [msg_crlf]
        call    serial_puts

        ; -------------------------------------------------------------------
        ; The glass core (GLASS.md, "Surfaces and the glass core"): the
        ; first application processor has been waiting since it checked in.
        ; Start it, and from this instruction the boot processor never
        ; writes a pixel again. No second core is a named error - shown on
        ; the screen too, by the one render the boot processor is allowed
        ; on that path, and then a halt.
        ; -------------------------------------------------------------------
        mov     r12d, 40
.wait_glass:
        cmp     dword [glass_ready], 0
        jne     .glass_there
        mov     ax, PIT_25MS
        call    pit_wait
        dec     r12d
        jnz     .wait_glass
        lea     rsi, [err_one_core]
        call    glass_err
.glass_there:
        mov     dword [glass_go], 1
        lea     rsi, [msg_glass]        ; line fifteen
        call    serial_puts
        mov     rax, [obs_page + OBS_GLASS_APIC]
        call    serial_putdec
        lea     rsi, [msg_crlf]
        call    serial_puts

        ; -------------------------------------------------------------------
        ; The keyboard - the third organ, and the machine's first sense.
        ; PIC remapped with only IRQ1 unmasked, the two gates installed, the
        ; i8042 drained, and only then the ready line, the prompt, and sti.
        ; -------------------------------------------------------------------
        call    pic_init

        lea     rdi, [idt + 0x21*16]    ; IRQ1, remapped
        lea     rax, [irq1_entry]
        call    idt_set_gate
        lea     rdi, [idt + 0x2C*16]    ; IRQ12, on the slave (ring 6c)
        lea     rax, [irq12_entry]
        call    idt_set_gate
        lea     rdi, [idt + 0x27*16]    ; the master's spurious vector
        lea     rax, [irq7_spurious]
        call    idt_set_gate
        lea     rdi, [idt + 0x2F*16]    ; the slave's spurious vector
        lea     rax, [irq15_spurious]
        call    idt_set_gate

        ; The i8042 configured for the first time, and the mouse reset,
        ; identified and told to report (ring 6c, GLASS.md "The device").
        ; Still interrupts off, polled; a missing mouse costs a moment. On a
        ; boot with a molt note the loader's molt_boot runs here instead,
        ; and a live part's init takes mouse_init's place.
        call    molt_boot

        ; The handover: from here the machine is the seed's (stage8.asm,
        ; seed_main). The loader's code stays below it, read-only.
        jmp     seed_main

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

; serial_puthex32 - EAX = value, as exactly 8 lowercase hex digits (a device
; register). The 64-bit routine's loop over the value's top half.
serial_puthex32:
        push    rax
        push    rbx
        push    rcx
        mov     rbx, rax
        shl     rbx, 32                 ; the eight digits now sit at the top
        mov     ecx, 8
.next:  rol     rbx, 4
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
; S7: lines the acceptance tests count, so a failure path can say what went
; wrong without changing the shape of the log the tests match - and the tests
; print the whole capture on failure, so it is seen.
serial_err:
        call    serial_err_line
        jmp     halt_forever

; serial_err_line - the line of serial_err without the halt, for the one
; path that goes on into the monitor (ring 7c item 20). Preserves everything.
serial_err_line:
        push    rsi
        lea     rsi, [msg_err]
        call    serial_puts
        pop     rsi
        call    serial_puts
        push    rsi
        lea     rsi, [msg_crlf]
        call    serial_puts
        pop     rsi
        ret

; serial_raw_puts - RSI = a NUL-terminated string, to the UART only: no
; mirror, no tee. The one line that goes out after the ready line without
; landing in the conversation (GLASS.md, "The eighteenth line").
serial_raw_puts:
        push    rax
        push    rdx
        push    rsi
.next:  lodsb
        test    al, al
        jz      .done
        mov     ah, al
.wait:  mov     dx, COM1_LSR
        in      al, dx
        test    al, 0x20
        jz      .wait
        mov     al, ah
        mov     dx, COM1
        out     dx, al
        jmp     .next
.done:  pop     rsi
        pop     rdx
        pop     rax
        ret

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

; ---------------------------------------------------------------------------
; Paging - the identity map, the read-only split of the image's 2 MB page,
; and the uncached mappings of a device's BAR. The tables themselves
; (pml4, pdpt, pd_tables, image_pt, spare_pages) are BSS, writable.
; ---------------------------------------------------------------------------

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
        jmp     text_split              ; ring 8a: .text read-only, then return

; text_split - the 2 MB page that holds .text, split into 512 pages of 4 KB
; in image_pt (PARTS.md, "The read-only floor"): each page of .text present
; and read-only, every other page present and writable, all with the 2 MB
; entry's cache bits. Reached from build_paging's end, still on the
; firmware's identity map, so a label's address is its physical address;
; the image is at ImageBase (relocations stripped), which is 2 MB aligned.
; A .text across two 2 MB pages is a named error, never a writable page.
text_split:
        lea     r8, [text_start]
        lea     r11, [text_end]
        mov     rdx, r8
        shr     rdx, 21                 ; the 2 MB page's index in pd_tables
        lea     rax, [r11 - 1]
        shr     rax, 21
        cmp     rax, rdx
        jne     .straddles
        lea     rdi, [pd_tables]
        mov     r10, [rdi + rdx*8]
        and     r10d, 0x18              ; PWT | PCD, as the 2 MB entry had them
        or      r10d, 1                 ; present
        mov     r9, rdx
        shl     r9, 21                  ; the page's base
        lea     rsi, [image_pt]
        xor     ecx, ecx
.pte:
        mov     rax, rcx
        shl     rax, 12
        add     rax, r9                 ; this 4 KB page's address
        cmp     rax, r8
        jb      .writable
        cmp     rax, r11
        jb      .entry                  ; inside .text: read-only
.writable:
        or      rax, 2
.entry:
        or      rax, r10
        mov     [rsi + rcx*8], rax
        inc     ecx
        cmp     ecx, 512
        jb      .pte
        lea     rax, [image_pt]
        or      rax, 3                  ; present | writable: the entries decide
        mov     [rdi + rdx*8], rax      ; the directory now names the table
        ret
.straddles:
        lea     rsi, [err_text_split]
        call    serial_err

; cpu_phys_bits - phys_limit = 1 << (the physical address width from CPUID
; 0x80000008, or 36 if the leaf is absent). Preserves everything.
cpu_phys_bits:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        mov     eax, 0x80000000
        cpuid
        cmp     eax, 0x80000008
        jb      .default
        mov     eax, 0x80000008
        cpuid
        movzx   ecx, al
        jmp     .set
.default:
        mov     ecx, 36
.set:
        mov     rax, 1
        shl     rax, cl
        mov     [phys_limit], rax
        pop     rdx
        pop     rcx
        pop     rbx
        pop     rax
        ret

; alloc_spare_page - RAX = a zeroed 4 KB page from the pool. Preserves
; everything else. Exhaustion is a reported error.
alloc_spare_page:
        push    rcx
        push    rdi
        mov     eax, [spare_next]
        cmp     eax, SPARE_PAGES
        jae     .exhausted
        inc     dword [spare_next]
        shl     eax, 12
        lea     rdi, [spare_pages]
        add     rdi, rax
        push    rdi
        xor     eax, eax
        mov     ecx, 512
        rep     stosq                   ; the loader zeroed BSS, but say so
        pop     rax
        pop     rdi
        pop     rcx
        ret
.exhausted:
        lea     rsi, [err_spare]
        call    serial_err

; map_mmio_2m - RAX = a physical address. Installs a present, writable,
; UNCACHED (PWT|PCD) 2 MB identity mapping of the page containing it,
; creating the PML4 and PDPT entries on the way if they are absent. Below
; 4 GB this overwrites an existing identity entry with an uncached one, which
; is what a BAR there would want too. Preserves everything.
map_mmio_2m:
        push    rax
        push    rcx
        push    rdx
        push    rdi
        push    r8
        mov     r8, rax
        cmp     r8, [phys_limit]
        jae     .too_high

        mov     rax, r8                 ; PML4 entry -> a PDPT
        shr     rax, 39
        and     eax, 511
        lea     rdi, [pml4]
        lea     rdi, [rdi + rax*8]
        call    .entry_or_new

        mov     rax, r8                 ; PDPT entry -> a PD
        shr     rax, 30
        and     eax, 511
        lea     rdi, [rdi + rax*8]
        call    .entry_or_new

        mov     rax, r8                 ; PD entry -> the 2 MB page itself
        shr     rax, 21
        and     eax, 511
        lea     rdi, [rdi + rax*8]
        mov     rdx, r8
        mov     rax, 0xFFFFFFFFFFE00000
        and     rdx, rax
        or      rdx, 0x83 | 0x18        ; present | writable | 2 MB | PWT | PCD
        mov     [rdi], rdx
        invlpg  [r8]

        pop     r8
        pop     rdi
        pop     rdx
        pop     rcx
        pop     rax
        ret

; RDI = the address of a table entry; returns RDI = the table it points to,
; allocating and linking a fresh one if the entry is not present.
.entry_or_new:
        mov     rdx, [rdi]
        test    rdx, 1
        jnz     .present
        call    alloc_spare_page
        mov     rdx, rax
        or      rdx, 3                  ; present | writable
        mov     [rdi], rdx
.present:
        mov     rax, 0x000FFFFFFFFFF000
        and     rdx, rax
        mov     rdi, rdx
        ret
.too_high:
        lea     rsi, [err_bar_high]
        call    serial_err

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
        cmp     dword [part_loaded], 0  ; ring 8a: the blame line, with a part
        je      halt_forever            ; loaded; with none, ring 7d's
        mov     rax, [rsp]
        mov     rdx, [rsp + 16]
        call    exc_blame
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

halt_forever:
        cli
.hang:  hlt
        jmp     .hang

; ---------------------------------------------------------------------------
; The loader's own port and timer primitives: PCI configuration space
; through CF8/CFC, and the PIT's channel 2 for a bounded wait.
; ---------------------------------------------------------------------------

; pci_cfg_read32 - EBX = bus<<16 | device<<11 | function<<8, ECX = register.
; Returns EAX. Preserves everything else.
pci_cfg_read32:
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

; pci_cfg_write32 - EBX, ECX as above, EAX = the value. Preserves everything.
pci_cfg_write32:
        push    rax
        push    rdx
        push    rax
        mov     eax, ecx
        and     eax, 0xFC
        or      eax, ebx
        or      eax, 0x80000000
        mov     dx, 0xCF8
        out     dx, eax
        pop     rax
        mov     dx, 0xCFC
        out     dx, eax
        pop     rdx
        pop     rax
        ret

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

; ---------------------------------------------------------------------------
; The disk - the AHCI driver (stage7/DISK.md, ring 7a), replacing Stage 3's
; virtio-blk driver. One controller found by class, every port with a SATA
; disk identified and classified, one port chosen by DISK.md's selection
; rule, one command slot, every transfer one sector, polled with a bounded
; wait, interrupts never enabled. The two stores are two PARTITION
; DESCRIPTORS over the chosen port: blk_rw keeps Stage 3's signature and
; adds the partition's base. Only the BSP ever calls any of this.
; ---------------------------------------------------------------------------

; ahci_find - the physical address width, the one-pass PCI scan, then the
; controller owned: memory, bus mastering and INTx off in its command
; register BEFORE its BAR is read (the standing gotcha); the ABAR mapped
; uncached wherever the firmware put it; AE set, IE clear; CAP and PI into
; the obs page. Called once from efi_main with interrupts off; clobbers
; registers freely.
ahci_find:
        call    cpu_phys_bits
        call    pci_scan
        cmp     dword [ahci_found], 0
        jne     .have
        lea     rsi, [err_no_ahci]
        call    serial_err
.have:
        mov     ebx, [ahci_bdf]
        mov     ecx, 0x04
        call    pci_cfg_read32
        and     eax, 0xFFFF             ; the status half is write-1-to-clear
        or      eax, PCI_CMD_MEMORY | PCI_CMD_MASTER | PCI_CMD_INTX_OFF
        call    pci_cfg_write32
        mov     ecx, 0x24               ; BAR5, the ABAR: a 32-bit memory BAR
        call    pci_cfg_read32
        test    al, 1
        jnz     .bar_io
        and     eax, 0xFFFFFFF0
        mov     [ahci_abar], rax        ; RAX's high half is zero
        call    map_mmio_2m             ; the page holding its first byte
        add     rax, 0x10FF
        call    map_mmio_2m             ; and its last (AHCI 1.3: 0x1100 bytes)
        mov     rdi, [ahci_abar]
        mov     eax, [rdi + HBA_GHC]
        or      eax, GHC_AE
        and     eax, ~GHC_IE
        mov     [rdi + HBA_GHC], eax
        mov     eax, [rdi + HBA_CAP]
        mov     [obs_page + OBS_AHCI_CAP], rax
        mov     eax, [rdi + HBA_PI]
        mov     [obs_page + OBS_AHCI_PI], rax
        mov     [ahci_pi], eax
        ret
.bar_io:
        lea     rsi, [err_bar_io]
        call    serial_err

; ahci_port_base - EAX = a port index; RDI = its register block. Clobbers
; EAX; preserves everything else.
ahci_port_base:
        mov     rdi, [ahci_abar]
        add     rdi, HBA_PORTS
        shl     eax, 7                  ; 0x80 bytes per port
        add     rdi, rax
        ret

; ahci_port_stop - RDI = a port's registers. ST cleared and CR awaited
; clear, then FRE cleared and FR awaited clear, each bounded; a port that
; will not stop is a named error. Preserves everything.
ahci_port_stop:
        push    rax
        push    r8
        and     dword [rdi + PX_CMD], ~PXCMD_ST
        mov     r8d, AHCI_STOP_TRIES
.wait_cr:
        test    dword [rdi + PX_CMD], PXCMD_CR
        jz      .cr_clear
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .wait_cr
        jmp     .would_not
.cr_clear:
        and     dword [rdi + PX_CMD], ~PXCMD_FRE
        mov     r8d, AHCI_STOP_TRIES
.wait_fr:
        test    dword [rdi + PX_CMD], PXCMD_FR
        jz      .fr_clear
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .wait_fr
.would_not:
        lea     rsi, [err_ahci_stop]
        call    serial_err
.fr_clear:
        pop     r8
        pop     rax
        ret

; ahci_port_open - EAX = the index of a port whose device is present.
; Stops the port, gives it this driver's command list and FIS receive area
; (zeroed), clears PxSERR and PxIS, masks PxIE, starts it (FRE, then ST
; once BSY and DRQ are clear). Records the port and its registers. Called
; for each port identified and again for the chosen one. Clobbers
; registers freely.
ahci_port_open:
        mov     [ahci_port], eax
        call    ahci_port_base
        mov     [ahci_port_regs], rdi
        call    ahci_port_stop

        lea     rdi, [ahci_clb]         ; the list, the FIS area and the table
        mov     ecx, (1024 + 256 + 256) / 8     ; contiguous in BSS, zeroed
        xor     eax, eax
        rep     stosq

        mov     rdi, [ahci_port_regs]
        lea     rax, [ahci_clb]
        mov     [rdi + PX_CLB], eax
        shr     rax, 32
        mov     [rdi + PX_CLBU], eax    ; zero: BSS lies below 4 GB
        lea     rax, [ahci_fb]
        mov     [rdi + PX_FB], eax
        shr     rax, 32
        mov     [rdi + PX_FBU], eax
        mov     dword [rdi + PX_SERR], 0xFFFFFFFF       ; write-1-to-clear
        mov     dword [rdi + PX_IS], 0xFFFFFFFF
        mov     dword [rdi + PX_IE], 0
        or      dword [rdi + PX_CMD], PXCMD_FRE
        mov     r8d, AHCI_STOP_TRIES
.wait_tfd:
        test    dword [rdi + PX_TFD], TFD_BSY | TFD_DRQ
        jz      .idle
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .wait_tfd
        lea     rsi, [err_ahci_stop]
        call    serial_err
.idle:
        or      dword [rdi + PX_CMD], PXCMD_ST
        ret

; ahci_cmd - one command in slot 0 on the open port. AL = the ATA command,
; EBX = the LBA (bits 47:32 zero), RDI = a 512-byte buffer, DL = 1 when the
; data flows to the device (the W bit), 0 for a read. Builds the header and
; the table, waits for the task file to be idle, issues, polls PxCI with a
; PIT breath between looks, bounded, then checks the task file; every
; failure is a named ERR: line. Counted and timed for the obs page as the
; virtio requests were. Preserves everything.
ahci_cmd:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        push    rsi
        push    rdi
        push    r8
        push    r9
        push    r10
        mov     r9, rdi                 ; the buffer
        lea     r10, [ahci_ct]
        push    rax
        mov     rdi, r10                ; the table, cleared
        mov     ecx, 256 / 8
        xor     eax, eax
        rep     stosq
        pop     rax
        mov     byte [r10 + 0], FIS_H2D
        mov     byte [r10 + 1], 0x80    ; C: a command, not control
        mov     [r10 + 2], al           ; the command
        mov     ecx, ebx
        mov     [r10 + 4], cl           ; LBA 7:0
        shr     ecx, 8
        mov     [r10 + 5], cl           ; LBA 15:8
        shr     ecx, 8
        mov     [r10 + 6], cl           ; LBA 23:16
        mov     byte [r10 + 7], 0x40    ; LBA mode
        shr     ecx, 8
        mov     [r10 + 8], cl           ; LBA 31:24; 47:32 stay zero
        mov     byte [r10 + 12], 1      ; one sector
        mov     [r10 + CT_PRDT], r9     ; DBA and DBAU
        mov     dword [r10 + CT_PRDT + 12], 511 ; byte count - 1, no interrupt
        lea     rsi, [ahci_clb]         ; slot 0's header
        mov     eax, 5 | (1 << 16)      ; CFL 5 dwords, PRDTL 1
        test    dl, dl
        jz      .header
        or      eax, 1 << 6             ; W
.header:
        mov     [rsi], eax
        mov     dword [rsi + 4], 0      ; PRDBC
        mov     [rsi + 8], r10          ; CTBA and CTBAU

        mov     rdi, [ahci_port_regs]
        mov     r8d, AHCI_STOP_TRIES
.wait_idle:
        test    dword [rdi + PX_TFD], TFD_BSY | TFD_DRQ
        jz      .issue
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .wait_idle
        jmp     .timeout
.issue:
        mov     dword [rdi + PX_IS], 0xFFFFFFFF ; a clean slate for this command
        mov     dword [rdi + PX_CI], 1
        inc     qword [obs_page + OBS_DISK_REQS]
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     [t_disk], rax
        mov     r8d, VQ_POLL_TRIES
.poll:
        call    molt_breath             ; ring 8a: the heartbeat, the pet (A1)
        test    dword [rdi + PX_CI], 1
        jz      .completed
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .poll
.timeout:
        lea     rsi, [err_disk_timeout]
        call    serial_err
.completed:
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        sub     rax, [t_disk]
        add     [obs_page + OBS_DISK_WAIT], rax
        test    dword [rdi + PX_IS], PXIS_TFES
        jnz     .failed
        test    dword [rdi + PX_TFD], TFD_ERR
        jnz     .failed
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
.failed:
        mov     dword [rdi + PX_SERR], 0xFFFFFFFF
        lea     rsi, [err_disk_failed]
        call    serial_err

; ahci_rw - EAX = VBLK_T_IN (a read) or VBLK_T_OUT (a write), EBX = the
; absolute LBA, RDI = a 512-byte buffer, on the open port. READ DMA EXT or
; WRITE DMA EXT, one sector. Returns only on success. Preserves everything.
ahci_rw:
        push    rax
        push    rdx
        cmp     ebx, [ahci_sectors]
        jae     .beyond
        mov     dl, al                  ; 0 a read, 1 a write: the W bit
        mov     al, ATA_READ_DMA_EXT
        test    dl, dl
        jz      .go
        mov     al, ATA_WRITE_DMA_EXT
.go:
        call    ahci_cmd
        pop     rdx
        pop     rax
        ret
.beyond:
        lea     rsi, [err_disk_beyond]
        call    serial_err

; ahci_identify - IDENTIFY DEVICE on the open port into ahci_ident: the
; sector count into ahci_sectors (the LBA48 count in words 100-103 when
; word 83 bit 10 says so, else words 60-61); 2^32 sectors or more, or a
; logical sector that is not 512 bytes (word 106 bit 12 with words 117-118
; not 256), a named error. Clobbers registers freely.
ahci_identify:
        mov     al, ATA_IDENTIFY
        xor     ebx, ebx
        lea     rdi, [ahci_ident]
        xor     edx, edx
        call    ahci_cmd
        lea     rsi, [ahci_ident]
        movzx   eax, word [rsi + 106 * 2]
        test    eax, 1 << 12
        jz      .sector_512
        cmp     dword [rsi + 117 * 2], 256      ; words 117-118: the logical sector, in words
        jne     .bad_sector
.sector_512:
        movzx   eax, word [rsi + 83 * 2]
        test    eax, 1 << 10
        jz      .lba28
        mov     rax, [rsi + 100 * 2]            ; words 100-103, a u64
        mov     rdx, rax
        shr     rdx, 32
        test    edx, edx
        jnz     .too_big
        jmp     .have
.lba28:
        mov     eax, [rsi + 60 * 2]             ; words 60-61
.have:
        mov     [ahci_sectors], eax
        ret
.bad_sector:
        lea     rsi, [err_sector_size]
        call    serial_err
.too_big:
        lea     rsi, [err_disk_big]
        call    serial_err

; disk_select - DISK.md's selection rule. Every implemented port whose
; device is present and active (DET 3, IPM 1 - a port with a Phy still
; coming up is given a bounded wait; a port with no device is passed at
; once) and whose signature is a SATA disk is opened, identified, and its
; first two sectors read and classified (disk_classify); the port is then
; stopped, so only the chosen port ever runs with this driver's list. Then:
; the first port holding a GermOS table is chosen; else the first blank
; port is chosen and formatted (gpt_write); else the named error naming
; every identified port, and a halt. Leaves the chosen port open, its count
; in ahci_sectors, the two descriptors filled. Clobbers registers freely.
disk_select:
        xor     r12d, r12d
        mov     dword [ports_mask], 0
.port:
        cmp     r12d, MAX_PORTS
        jae     .choose
        bt      dword [ahci_pi], r12d
        jnc     .next
        mov     eax, r12d
        call    ahci_port_base
        mov     r8d, AHCI_PROBE_TRIES
        ; Ring 7c (plan decision 4, A2): under staggered spin-up the device
        ; is not detected until the port has been told to spin it up, so
        ; DET 0 in the first microseconds means nothing. With CAP.SSS set,
        ; SUD is set here, DET is given a second to leave 0 - if it stays 0
        ; the port is empty and is passed - and a device that then appears
        ; is given ten seconds to reach DET 3, or the boot halts naming the
        ; port. With SSS clear (the twin) the path from .probe is the one
        ; ring 7a wrote, byte for byte. This path runs only on the metal.
        mov     rax, [ahci_abar]
        test    dword [rax + HBA_CAP], CAP_SSS
        jz      .probe
        or      dword [rdi + PX_CMD], PXCMD_SUD
.spinup_wait:
        mov     eax, [rdi + PX_SSTS]
        and     eax, 0xF                ; DET
        jnz     .spinning               ; a device is there: now the long wait
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .spinup_wait
        jmp     .next                   ; DET stayed 0 for a second: nothing plugged in
.spinning:
        mov     r8d, AHCI_SPINUP_TRIES
.spin_probe:
        mov     eax, [rdi + PX_SSTS]
        and     eax, 0xF0F
        cmp     eax, 0x103              ; DET 3, IPM 1
        je      .present
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .spin_probe
        lea     rsi, [msg_err]          ; ERR: ahci port N did not come up after spin-up
        call    serial_puts
        lea     rsi, [err_ahci_spinup]
        call    serial_puts
        mov     eax, r12d
        call    serial_putdec
        lea     rsi, [err_ahci_spinup_tail]
        call    serial_puts
        jmp     halt_forever
.probe:
        mov     eax, [rdi + PX_SSTS]
        mov     ecx, eax
        and     ecx, 0xF                ; DET
        jz      .next                   ; no device, no Phy: nothing to wait for
        and     eax, 0xF0F
        cmp     eax, 0x103              ; DET 3, IPM 1
        je      .present
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .probe
        jmp     .next
.present:
        cmp     dword [rdi + PX_SIG], SIG_SATA_DISK
        jne     .next
        mov     eax, r12d
        call    ahci_port_open
        call    ahci_identify
        mov     eax, [ahci_sectors]
        lea     rdx, [port_sectors]
        mov     [rdx + r12*4], eax
        call    disk_classify           ; AL = the word
        lea     rdx, [port_word]
        mov     [rdx + r12], al
        bts     dword [ports_mask], r12d
        mov     rdi, [ahci_port_regs]
        call    ahci_port_stop
.next:
        inc     r12d
        jmp     .port

.choose:
        cmp     dword [ports_mask], 0
        je      .no_disk
        mov     al, DISK_GERMOS
        call    port_with_word
        cmp     eax, -1
        jne     .chosen
        mov     al, DISK_BLANK
        call    port_with_word
        cmp     eax, -1
        je      .refuse
        call    ahci_port_open
        lea     rdx, [port_sectors]     ; the blank disk's count, for the writer
        mov     eax, [ahci_port]
        mov     eax, [rdx + rax*4]
        mov     [ahci_sectors], eax
        call    gpt_write               ; the table, then "S7: gpt written"
        mov     eax, [ahci_port]
.chosen:
        call    ahci_port_open          ; open again: another port may have held the list
        mov     eax, [ahci_port]
        lea     rdx, [port_sectors]
        mov     eax, [rdx + rax*4]
        mov     [ahci_sectors], eax
        mov     eax, [ahci_port]
        mov     [obs_page + OBS_AHCI_PORT], rax
        call    gpt_read                ; the descriptors from the table on the chosen disk
        ret
.no_disk:
        lea     rsi, [err_no_sata]
        call    serial_err
.refuse:
        ; ERR: no GermOS disk and no blank disk - port 0: other, port 1: gpt
        lea     rsi, [msg_err]
        call    serial_puts
        lea     rsi, [err_no_germos]
        call    serial_puts
        xor     r12d, r12d
        xor     r13d, r13d              ; ports named so far
.name:
        cmp     r12d, MAX_PORTS
        jae     .named
        bt      dword [ports_mask], r12d
        jnc     .name_next
        test    r13d, r13d
        jz      .first_name
        lea     rsi, [msg_comma]
        call    serial_puts
.first_name:
        lea     rsi, [msg_port]
        call    serial_puts
        mov     eax, r12d
        call    serial_putdec
        lea     rsi, [msg_colon]
        call    serial_puts
        lea     rdx, [port_word]
        movzx   eax, byte [rdx + r12]
        call    word_string
        call    serial_puts
        inc     r13d
.name_next:
        inc     r12d
        jmp     .name
.named:
        lea     rsi, [msg_crlf]
        call    serial_puts
        jmp     halt_forever

; word_string - AL = a word; RSI = its name. RIP-relative leas, never a
; table of addresses in data: relocations are stripped. Preserves
; everything else.
word_string:
        lea     rsi, [word_germos]
        cmp     al, DISK_GERMOS
        je      .out
        lea     rsi, [word_blank]
        cmp     al, DISK_BLANK
        je      .out
        lea     rsi, [word_gpt]
        cmp     al, DISK_GPT
        je      .out
        lea     rsi, [word_torn]
        cmp     al, DISK_TORN
        je      .out
        lea     rsi, [word_other]
.out:
        ret

; port_with_word - AL = a word; EAX = the first identified port holding a
; disk of that word, or -1. Preserves everything else.
port_with_word:
        push    rcx
        push    rdx
        mov     cl, al
        xor     eax, eax
.scan:
        cmp     eax, MAX_PORTS
        jae     .none
        bt      dword [ports_mask], eax
        jnc     .next
        lea     rdx, [port_word]
        cmp     [rdx + rax], cl
        je      .found
.next:
        inc     eax
        jmp     .scan
.none:
        mov     eax, -1
.found:
        pop     rdx
        pop     rcx
        ret

; disk_classify - the open port's disk in DISK.md's five words: sectors 0
; and 1 read into gpt_sec0 and gpt_hdr; both all zero is blank; no EFI PART
; signature at sector 1 is other; else gpt_validate says germos, gpt or
; torn. AL = the word. Clobbers registers freely.
disk_classify:
        mov     eax, VBLK_T_IN
        xor     ebx, ebx
        lea     rdi, [gpt_sec0]
        call    ahci_rw
        mov     eax, VBLK_T_IN
        mov     ebx, 1
        lea     rdi, [gpt_hdr]
        call    ahci_rw
        lea     rsi, [gpt_sec0]
        mov     ecx, 1024 / 8           ; the two sectors are contiguous
        call    buf_zero
        test    eax, eax
        jnz     .blank
        mov     rax, 'EFI PART'
        cmp     [gpt_hdr], rax
        jne     .other
        call    gpt_validate
        ret
.blank:
        mov     al, DISK_BLANK
        ret
.other:
        mov     al, DISK_OTHER
        ret

; buf_zero - RSI = a buffer, ECX = its length in qwords. EAX = 1 if every
; qword is zero, else 0. Preserves everything else.
buf_zero:
        push    rcx
        push    rsi
.qword:
        cmp     qword [rsi], 0
        jne     .no
        add     rsi, 8
        dec     ecx
        jnz     .qword
        mov     eax, 1
        jmp     .out
.no:
        xor     eax, eax
.out:
        pop     rsi
        pop     rcx
        ret

; gpt_validate - DISK.md's recognition rule on gpt_hdr (sector 1 of the
; open port's disk, its signature already seen): revision, size, reserved,
; the header's own CRC, MyLBA 1, the entries at LBA 2, 128 of 128 bytes,
; the usable range inside the disk, the tail zero; the 32 array sectors
; read into gpt_entries and their CRC; every entry either all zero or
; inside the usable range; an entry of each GermOS type. AL = DISK_GERMOS
; (the descriptors filled from the two entries), DISK_GPT (a valid table
; without both), or DISK_TORN. Clobbers registers freely but R12, which
; the caller's port loop keeps.
gpt_validate:
        push    r12
        call    .body
        pop     r12
        ret
.body:
        lea     rsi, [gpt_hdr]
        cmp     dword [rsi + 8], 0x00010000
        jne     .torn
        cmp     dword [rsi + 12], 92
        jne     .torn
        cmp     dword [rsi + 20], 0
        jne     .torn
        ; the header CRC: bytes 0-15, four zero bytes, bytes 20-91
        mov     eax, 0xFFFFFFFF
        mov     ecx, 16
        call    crc32_update
        push    rsi
        lea     rsi, [crc_zero4]
        mov     ecx, 4
        call    crc32_update
        pop     rsi
        push    rsi
        add     rsi, 20
        mov     ecx, 72
        call    crc32_update
        pop     rsi
        not     eax
        cmp     eax, [rsi + 16]
        jne     .torn
        cmp     qword [rsi + 24], 1                     ; MyLBA
        jne     .torn
        cmp     dword [rsi + 36], 0                     ; AlternateLBA, high half
        jne     .torn
        mov     eax, [rsi + 32]
        cmp     eax, [ahci_sectors]
        jae     .torn
        cmp     dword [rsi + 44], 0                     ; FirstUsable, high half
        jne     .torn
        cmp     dword [rsi + 52], 0                     ; LastUsable, high half
        jne     .torn
        mov     eax, [rsi + 40]
        cmp     eax, GPT_FIRST_USABLE
        jb      .torn
        mov     [gpt_usable_first], eax
        mov     edx, [rsi + 48]
        cmp     edx, [ahci_sectors]
        jae     .torn
        cmp     edx, eax
        jb      .torn
        mov     [gpt_usable_last], edx
        cmp     qword [rsi + 72], 2                     ; PartitionEntryLBA
        jne     .torn
        cmp     dword [rsi + 80], GPT_ENTRIES
        jne     .torn
        cmp     dword [rsi + 84], GPT_ENTRY
        jne     .torn
        push    rsi
        add     rsi, 92
        mov     ecx, (512 - 92) / 4                     ; 420 bytes: 105 dwords
.tail:
        cmp     dword [rsi], 0
        jne     .torn_pop
        add     rsi, 4
        dec     ecx
        jnz     .tail
        pop     rsi

        ; the array: 32 sectors from LBA 2
        mov     ebx, 2
        lea     rdi, [gpt_entries]
.read:
        mov     eax, VBLK_T_IN
        call    ahci_rw
        add     rdi, 512
        inc     ebx
        cmp     ebx, 2 + GPT_ENTRY_SECTORS
        jb      .read
        push    rsi
        lea     rsi, [gpt_entries]
        mov     eax, 0xFFFFFFFF
        mov     ecx, GPT_ENTRIES * GPT_ENTRY
        call    crc32_update
        not     eax
        pop     rsi
        cmp     eax, [rsi + 88]
        jne     .torn

        ; the entries
        mov     dword [part_notes + PART_SECTORS], 0
        mov     dword [part_home + PART_SECTORS], 0
        xor     r12d, r12d
.entry:
        cmp     r12d, GPT_ENTRIES
        jae     .entries_done
        lea     rsi, [gpt_entries]
        mov     eax, r12d
        shl     eax, 7
        add     rsi, rax                                ; RSI = the entry
        mov     ecx, 2
        call    buf_zero                                ; the type GUID
        test    eax, eax
        jz      .used
        mov     ecx, GPT_ENTRY / 8
        call    buf_zero                                ; unused: all zero
        test    eax, eax
        jz      .torn
        jmp     .entry_next
.used:
        cmp     dword [rsi + 36], 0                     ; FirstLBA, high half
        jne     .torn
        cmp     dword [rsi + 44], 0                     ; LastLBA, high half
        jne     .torn
        mov     eax, [rsi + 32]
        mov     edx, [rsi + 40]
        cmp     eax, [gpt_usable_first]
        jb      .torn
        cmp     edx, [gpt_usable_last]
        ja      .torn
        cmp     edx, eax
        jb      .torn
        sub     edx, eax
        inc     edx                                     ; EDX = sectors
        lea     rdi, [guid_notes_type]
        call    guid_equal
        jz      .not_notes
        cmp     dword [part_notes + PART_SECTORS], 0
        jne     .entry_next                             ; the first of each type wins
        mov     [part_notes + PART_BASE], eax
        mov     [part_notes + PART_SECTORS], edx
        jmp     .entry_next
.not_notes:
        lea     rdi, [guid_home_type]
        call    guid_equal
        jz      .entry_next
        cmp     dword [part_home + PART_SECTORS], 0
        jne     .entry_next
        mov     [part_home + PART_BASE], eax
        mov     [part_home + PART_SECTORS], edx
.entry_next:
        inc     r12d
        jmp     .entry
.entries_done:
        cmp     dword [part_notes + PART_SECTORS], 0
        je      .gpt
        cmp     dword [part_home + PART_SECTORS], 0
        je      .gpt
        mov     al, DISK_GERMOS
        ret
.gpt:
        mov     al, DISK_GPT
        ret
.torn_pop:
        pop     rsi
.torn:
        mov     al, DISK_TORN
        ret

; guid_equal - RSI = an entry (its type GUID at 0), RDI = a 16-byte GUID as
; stored. ZF clear when equal. Preserves everything.
guid_equal:
        push    rax
        push    rcx
        mov     rax, [rsi]
        cmp     rax, [rdi]
        jne     .no
        mov     rax, [rsi + 8]
        cmp     rax, [rdi + 8]
        jne     .no
        or      eax, 1                  ; ZF clear: equal
        jmp     .out
.no:
        xor     eax, eax                ; ZF set: different
.out:
        pop     rcx
        pop     rax
        ret

; gpt_read - the chosen disk's table read again and validated; the two
; descriptors are what gpt_validate filled. A disk chosen as germos is
; germos; a disk just formatted must read back as germos too - anything
; else is the writer's error, named. Clobbers registers freely.
gpt_read:
        call    disk_classify
        cmp     al, DISK_GERMOS
        je      .ok
        lea     rsi, [err_gpt_readback]
        call    serial_err
.ok:
        ret

; crc32_update - EAX = the running CRC-32 in its inverted form (begin with
; all ones, finish with NOT), RSI = bytes, ECX = how many. The reflected
; polynomial 0xEDB88320, bit by bit - the UEFI specification's CRC, whose
; check value over "123456789" is 0xCBF43926. Preserves everything but EAX.
crc32_update:
        push    rcx
        push    rdx
        push    rsi
.byte:
        test    ecx, ecx
        jz      .done
        movzx   edx, byte [rsi]
        inc     rsi
        xor     eax, edx
        mov     edx, 8
.bit:
        shr     eax, 1
        jnc     .no_xor
        xor     eax, 0xEDB88320
.no_xor:
        dec     edx
        jnz     .bit
        dec     ecx
        jmp     .byte
.done:
        pop     rsi
        pop     rdx
        pop     rcx
        ret

; disk_rw / home_rw - EAX = VBLK_T_IN (read) or VBLK_T_OUT (write), EBX =
; the sector within the partition, RDI = a 512-byte buffer, on the notes
; partition or the home partition. Returns only on success; every failure
; is a named ERR: line and a halt. Preserves everything. Both are blk_rw
; on their partition descriptor - Stage 3's signature, unchanged.
disk_rw:
        push    rbp
        lea     rbp, [part_notes]
        call    blk_rw
        pop     rbp
        ret

home_rw:
        push    rbp
        lea     rbp, [part_home]
        call    blk_rw
        pop     rbp
        ret

; blk_rw - RBP = a partition descriptor (PART_BASE, PART_SECTORS); EAX,
; EBX, RDI as above. The sector must lie inside the partition; the base is
; added and the port driven. Preserves everything.
blk_rw:
        push    rbx
        cmp     ebx, [rbp + PART_SECTORS]
        jae     .beyond
        add     ebx, [rbp + PART_BASE]
        call    ahci_rw
        pop     rbx
        ret
.beyond:
        lea     rsi, [err_disk_beyond]
        call    serial_err

; ---------------------------------------------------------------------------
; The notebook's scan and the home table's read (stage3/NOTEBOOK.md,
; stage6/HOME.md), at boot, from the disk's read path above. The seed
; keeps the writers - notebook_append, home_install, gpt_write - which
; drive the disk through disk_rw and home_rw here.
; ---------------------------------------------------------------------------

; notebook_init - read sector 0; on the magic and version, count the valid
; records and log "S7: notebook <N> notes"; otherwise write the header and a
; zeroed sector 1 and log "S7: notebook formatted". Called once from
; efi_main after vq_init; clobbers registers freely.
notebook_init:
        mov     eax, VBLK_T_IN
        xor     ebx, ebx
        lea     rdi, [sector_buf]
        call    disk_rw
        mov     rax, 'NOTEBOOK'
        cmp     [sector_buf], rax
        jne     .format
        cmp     dword [sector_buf + 8], 1
        jne     .format

        mov     dword [nb_count], 0
        mov     ebx, 1
.scan:
        cmp     ebx, [disk_sectors]
        jae     .scanned
        mov     eax, VBLK_T_IN
        lea     rdi, [sector_buf]
        call    disk_rw
        call    record_valid
        test    eax, eax
        jz      .scanned
        inc     dword [nb_count]
        inc     ebx
        jmp     .scan
.scanned:
        mov     [nb_next], ebx          ; the first sector that is not a record
        mov     eax, [nb_count]
        mov     [obs_page + OBS_NOTES], rax
        lea     rsi, [msg_nb]
        call    serial_puts
        mov     eax, [nb_count]
        call    serial_putdec
        lea     rsi, [msg_notes]
        call    serial_puts
        ret

.format:
        lea     rdi, [sector_buf]       ; the header, from a clean sector
        mov     ecx, 64
        xor     eax, eax
        rep     stosq
        mov     rax, 'NOTEBOOK'
        mov     [sector_buf], rax
        mov     dword [sector_buf + 8], 1       ; version
        mov     dword [sector_buf + 12], 512    ; sector size
        mov     qword [sector_buf + 16], 1      ; first journal sector
        mov     eax, [disk_sectors]
        dec     eax
        mov     [sector_buf + 24], rax          ; journal length (RAX high half is zero)
        mov     eax, VBLK_T_OUT
        xor     ebx, ebx
        lea     rdi, [sector_buf]
        call    disk_rw

        lea     rdi, [sector_buf]       ; sector 1 zeroed: no stale note can
        mov     ecx, 64                 ; survive the format
        xor     eax, eax
        rep     stosq
        mov     eax, VBLK_T_OUT
        mov     ebx, 1
        lea     rdi, [sector_buf]
        call    disk_rw

        mov     dword [nb_count], 0
        mov     dword [nb_next], 1
        lea     rsi, [msg_nb_fmt]
        call    serial_puts
        ret

; record_valid - EBX = the sector index; sector_buf holds the sector. EAX = 1
; if it is a valid record by NOTEBOOK.md's rule - magic, sequence equal to
; the index, length 1-500, reserved zero, printable text, zero padding - or
; 0. Preserves everything else.
record_valid:
        push    rcx
        push    rdx
        push    rsi
        cmp     dword [sector_buf], 'NOTE'
        jne     .no
        cmp     [sector_buf + 4], ebx
        jne     .no
        movzx   ecx, word [sector_buf + 8]
        test    ecx, ecx
        jz      .no
        cmp     ecx, NOTE_MAX
        ja      .no
        cmp     word [sector_buf + 10], 0
        jne     .no
        lea     rsi, [sector_buf + NB_TEXT_OFF]
        mov     edx, ecx
.text:
        lodsb
        cmp     al, 0x20
        jb      .no
        cmp     al, 0x7E
        ja      .no
        dec     edx
        jnz     .text
        mov     edx, 512 - NB_TEXT_OFF
        sub     edx, ecx                ; padding bytes after the text
.pad:
        test    edx, edx
        jz      .yes
        lodsb
        test    al, al
        jnz     .no
        dec     edx
        jmp     .pad
.yes:
        mov     eax, 1
        jmp     .out
.no:
        xor     eax, eax
.out:
        pop     rsi
        pop     rdx
        pop     rcx
        ret

; home_init - HOME.md, "The disk": sector 0 recognised (GERMHOME, version
; 1) or the image formatted (the header written, sectors 1-8 zeroed); the
; table read into home_table; the entries counted and the next free sector
; found (home_recount); line twelve. With no second disk, nothing at all.
; Called once from efi_main; clobbers registers freely.
home_init:
        cmp     dword [home_present], 0
        je      .none
        mov     eax, VBLK_T_IN
        xor     ebx, ebx
        lea     rdi, [sector_buf]
        call    home_rw
        mov     rax, 'GERMHOME'
        cmp     [sector_buf], rax
        jne     .format
        cmp     dword [sector_buf + 8], 1
        jne     .format
.scan:
        mov     ebx, HOME_TABLE_FIRST
        lea     rdi, [home_table]
.read:
        mov     eax, VBLK_T_IN
        call    home_rw
        add     rdi, 512
        inc     ebx
        cmp     ebx, HOME_TABLE_FIRST + HOME_TABLE_SECTORS
        jb      .read
        call    home_recount
        call    choices_update          ; the installed apps on the row
        lea     rsi, [msg_home]
        call    serial_puts
        mov     eax, [home_count]
        call    serial_putdec
        lea     rsi, [msg_apps]
        call    serial_puts
.none:
        ret

.format:
        lea     rdi, [sector_buf]       ; the header, from a clean sector
        mov     ecx, 64
        xor     eax, eax
        rep     stosq
        mov     rax, 'GERMHOME'
        mov     [sector_buf], rax
        mov     dword [sector_buf + 8], 1               ; version
        mov     dword [sector_buf + 12], 512            ; sector size
        mov     qword [sector_buf + 16], HOME_TABLE_FIRST
        mov     qword [sector_buf + 24], HOME_TABLE_SECTORS
        mov     qword [sector_buf + 32], HOME_DATA_FIRST
        mov     eax, [part_home + PART_SECTORS]
        mov     [sector_buf + 40], rax                  ; capacity (RAX high half zero)
        mov     eax, VBLK_T_OUT
        xor     ebx, ebx
        lea     rdi, [sector_buf]
        call    home_rw

        lea     rdi, [sector_buf]       ; sectors 1-8 zeroed: no stale entry
        mov     ecx, 64                 ; can survive the format
        xor     eax, eax
        rep     stosq
        mov     ebx, HOME_TABLE_FIRST
.zero:
        mov     eax, VBLK_T_OUT
        lea     rdi, [sector_buf]
        call    home_rw
        inc     ebx
        cmp     ebx, HOME_TABLE_FIRST + HOME_TABLE_SECTORS
        jb      .zero
        jmp     .scan                   ; and read it back, as a recognised image is

; ---------------------------------------------------------------------------
; SHA-256 (FIPS 180-4) - the door's hash, and the seed's install and
; launch checks.
; ---------------------------------------------------------------------------

; sha256 - RSI = the bytes, RCX = how many, RDI = 32 bytes for the digest.
; FIPS 180-4, one 64-byte block at a time, the message schedule and the
; sixty-four rounds in plain 32-bit arithmetic; the tail padded in its
; own buffer. Called at an install (the entry's hash) and at a launch (the
; check). Preserves the callee-saved registers; clobbers RAX, RCX, RDX,
; RSI, RDI, R8-R11.
sha256:
        push    rbx
        push    rbp
        push    r12
        push    r13
        push    r14
        push    r15
        mov     r12, rsi                ; the bytes still to hash
        mov     r13, rcx                ; how many remain
        mov     r14, rdi                ; the digest
        mov     r15, rcx                ; the whole length, for the tail
        lea     rsi, [sha_init]
        lea     rdi, [sha_state]
        mov     ecx, 8
        rep     movsd
.blocks:
        cmp     r13, 64
        jb      .tail
        mov     rsi, r12
        call    sha256_block
        add     r12, 64
        sub     r13, 64
        jmp     .blocks
.tail:                                  ; the remainder, 0x80, zeros, the
        lea     rdi, [sha_tail]         ; bit length big-endian - one block
        mov     ecx, 16                 ; if the remainder is under 56 bytes,
        xor     eax, eax                ; two otherwise
        rep     stosq
        lea     rdi, [sha_tail]
        mov     rsi, r12
        mov     rcx, r13
        rep     movsb
        mov     byte [rdi], 0x80
        mov     rax, r15
        shl     rax, 3
        bswap   rax
        mov     edx, 64
        cmp     r13, 56
        jb      .one_block
        mov     edx, 128
.one_block:
        lea     rdi, [sha_tail]
        mov     [rdi + rdx - 8], rax
        lea     rsi, [sha_tail]
        call    sha256_block
        cmp     edx, 64
        je      .digest
        lea     rsi, [sha_tail + 64]
        call    sha256_block
.digest:
        lea     rsi, [sha_state]
        mov     rdi, r14
        mov     ecx, 8
.out:
        lodsd
        bswap   eax
        stosd
        dec     ecx
        jnz     .out
        pop     r15
        pop     r14
        pop     r13
        pop     r12
        pop     rbp
        pop     rbx
        ret

; sha256_block - RSI = one 64-byte block, folded into sha_state.
; Preserves RSI's owner's registers: everything callee-saved is pushed.
sha256_block:
        push    rbx
        push    rbp
        push    r12
        push    r13
        push    r14
        push    r15
        push    rdx
        lea     rdi, [sha_w]
        mov     ecx, 16
.load:
        lodsd
        bswap   eax
        stosd
        dec     ecx
        jnz     .load
        mov     ecx, 16
        lea     rdi, [sha_w]
.schedule:                              ; W[t] = s1(W[t-2]) + W[t-7] + s0(W[t-15]) + W[t-16]
        mov     eax, [rdi + rcx*4 - 8]
        mov     edx, eax
        ror     edx, 17
        mov     ebx, eax
        ror     ebx, 19
        xor     edx, ebx
        shr     eax, 10
        xor     edx, eax                ; s1
        mov     eax, [rdi + rcx*4 - 60]
        mov     ebx, eax
        ror     ebx, 7
        mov     ebp, eax
        ror     ebp, 18
        xor     ebx, ebp
        shr     eax, 3
        xor     ebx, eax                ; s0
        add     edx, ebx
        add     edx, [rdi + rcx*4 - 28]
        add     edx, [rdi + rcx*4 - 64]
        mov     [rdi + rcx*4], edx
        inc     ecx
        cmp     ecx, 64
        jb      .schedule

        lea     rbx, [sha_state]        ; a..h
        mov     r8d, [rbx]
        mov     r9d, [rbx + 4]
        mov     r10d, [rbx + 8]
        mov     r11d, [rbx + 12]
        mov     r12d, [rbx + 16]
        mov     r13d, [rbx + 20]
        mov     r14d, [rbx + 24]
        mov     r15d, [rbx + 28]
        xor     ecx, ecx
        lea     rsi, [sha_w]
        lea     rdi, [sha_k]
.round:
        mov     eax, r12d               ; T1 = h + S1(e) + Ch(e, f, g) + K[t] + W[t]
        ror     eax, 6
        mov     edx, r12d
        ror     edx, 11
        xor     eax, edx
        mov     edx, r12d
        ror     edx, 25
        xor     eax, edx
        mov     edx, r12d
        and     edx, r13d
        mov     ebp, r12d
        not     ebp
        and     ebp, r14d
        xor     edx, ebp
        add     eax, edx
        add     eax, r15d
        add     eax, [rdi + rcx*4]
        add     eax, [rsi + rcx*4]
        mov     edx, r8d                ; T2 = S0(a) + Maj(a, b, c)
        ror     edx, 2
        mov     ebp, r8d
        ror     ebp, 13
        xor     edx, ebp
        mov     ebp, r8d
        ror     ebp, 22
        xor     edx, ebp
        mov     ebp, r8d
        and     ebp, r9d
        mov     ebx, r8d
        and     ebx, r10d
        xor     ebp, ebx
        mov     ebx, r9d
        and     ebx, r10d
        xor     ebp, ebx
        add     edx, ebp
        mov     r15d, r14d              ; h = g, g = f, f = e, e = d + T1,
        mov     r14d, r13d              ; d = c, c = b, b = a, a = T1 + T2
        mov     r13d, r12d
        mov     r12d, r11d
        add     r12d, eax
        mov     r11d, r10d
        mov     r10d, r9d
        mov     r9d, r8d
        mov     r8d, eax
        add     r8d, edx
        inc     ecx
        cmp     ecx, 64
        jb      .round
        lea     rbx, [sha_state]
        add     [rbx], r8d
        add     [rbx + 4], r9d
        add     [rbx + 8], r10d
        add     [rbx + 12], r11d
        add     [rbx + 16], r12d
        add     [rbx + 20], r13d
        add     [rbx + 24], r14d
        add     [rbx + 28], r15d
        pop     rdx
        pop     r15
        pop     r14
        pop     r13
        pop     r12
        pop     rbp
        pop     rbx
        ret

; ===========================================================================
; The molt's floor (stage8/PARTS.md), ring 8a item 15.
;
; The notes are the state: molt_scan walks the notebook and computes each
; slot's state, its counts and its probation by PARTS.md's rules, one
; forward pass equal to parts.py's history, counts_of, probation_of and
; arrival, so there is no second copy of the state to drift. The boot with
; a molt note (molt_boot) runs in mouse_init's place: the known answer, the
; door for each slot in shadow or live, the boot note, then a live part's
; init or the generic's. check_part is PARTS.md's header rule, which the
; seed's install calls too; part_call is the one way into a part.
;
; What it calls in the seed: molt_note (the notebook's writer), str_copy and
; put_dec, the home table's lookups, svc3_fill and pointer_centre, and the
; part stubs it installs at IRQ1 and IRQ12. Its state is LOADER_STATE's.
; ===========================================================================

; s8_line - RSI = a NUL-terminated line without its end: an S8: line
; (PARTS.md, "The serial lines"), through the tee before S7: keyboard
; ready, raw after it. Preserves everything.
s8_line:
        push    rsi
        cmp     dword [after_ready], 0
        jne     .raw
        call    serial_puts
        lea     rsi, [msg_crlf]
        call    serial_puts
        pop     rsi
        ret
.raw:
        call    serial_raw_puts
        lea     rsi, [msg_crlf]
        call    serial_raw_puts
        pop     rsi
        ret

; put_hex_bytes - RSI = bytes, ECX = how many, RDI = destination: two
; lowercase hex digits each; RDI advanced. Clobbers RAX, RCX, RDX, RSI.
put_hex_bytes:
        lea     rdx, [hex_digits]
.b:     test    ecx, ecx
        jz      .done
        movzx   eax, byte [rsi]
        shr     eax, 4
        mov     al, [rdx + rax]
        stosb
        movzx   eax, byte [rsi]
        and     eax, 15
        mov     al, [rdx + rax]
        stosb
        inc     rsi
        dec     ecx
        jmp     .b
.done:  ret

; put_hex_n - EAX = a value, ECX = digits (1..8), RDI = destination:
; lowercase, zero-padded; RDI advanced. Clobbers RAX, RCX, RDX.
put_hex_n:
        push    rbx
        mov     ebx, eax
        lea     rdx, [hex_digits]
.d:     dec     ecx
        js      .done
        mov     eax, ebx
        push    rcx
        shl     ecx, 2
        shr     eax, cl
        pop     rcx
        and     eax, 15
        mov     al, [rdx + rax]
        stosb
        jmp     .d
.done:  pop     rbx
        ret

; put_slot - EAX = a slot index: its name, RDI advanced. Clobbers RAX, RSI.
put_slot:
        lea     rsi, [slot_words]
        shl     eax, 3
        add     rsi, rax
        call    str_copy_n8
        ret

; str_copy_n8 - RSI = up to 8 bytes NUL-padded: copied to RDI. Clobbers RAX, RSI.
str_copy_n8:
        push    rcx
        mov     ecx, 8
.c:     lodsb
        test    al, al
        jz      .done
        stosb
        dec     ecx
        jnz     .c
.done:  pop     rcx
        ret

; put_state - RBX = a slot record: "generic", "shadow <b>", "live <b>" or
; "demoted <b> <why>" at RDI. Clobbers RAX, RCX, RSI.
put_state:
        movzx   eax, byte [rbx + SS_KIND]
        jmp     put_state_of
; put_state_of - EAX = kind, [RBX + SS_WHY], [RBX + SS_BUILD] as a state.
put_state_of:
        lea     rsi, [w_generic]
        cmp     eax, ST_GENERIC
        je      .word
        lea     rsi, [w_shadow]
        cmp     eax, ST_SHADOW
        je      .build
        lea     rsi, [w_live]
        cmp     eax, ST_LIVE
        je      .build
        lea     rsi, [w_demoted]
.build:
        call    str_copy
        mov     al, ' '
        stosb
        lea     rsi, [rbx + SS_BUILD]
        mov     ecx, 16
        rep     movsb
        movzx   eax, byte [rbx + SS_KIND]
        cmp     byte [rbx + SS_KIND], ST_DEMOTED
        jne     .out
        mov     al, ' '
        stosb
        lea     rsi, [w_watchdog]
        cmp     byte [rbx + SS_WHY], WHY_WATCHDOG
        je      .word
        lea     rsi, [w_unhealthy]
.word:
        call    str_copy
.out:   ret

; ---------------------------------------------------------- the scan ---

; molt_scan - the notebook read from disk, every molt note applied in
; journal order (parts.py's history, counts_of, probation_of, arrival and
; unhealthy_run as one forward pass). Clobbers registers freely; uses
; sector_buf.
molt_scan:
        xor     eax, eax
        mov     [ms_any], eax
        mov     [ms_boots], eax
        mov     [ms_run], eax
        mov     dword [ms_last], -1
        lea     rdi, [ms_slots]
        mov     ecx, SLOT_N * SS_SIZE
        rep     stosb
        mov     dword [ms_note_i], 1
.note:
        mov     ebx, [ms_note_i]
        cmp     ebx, [nb_count]
        ja      .done
        mov     eax, VBLK_T_IN
        lea     rdi, [sector_buf]
        call    disk_rw
        movzx   ecx, word [sector_buf + 8]
        cmp     ecx, 5
        jb      .next
        cmp     dword [sector_buf + NB_TEXT_OFF], 'molt'
        jne     .next
        cmp     byte [sector_buf + NB_TEXT_OFF + 4], ' '
        jne     .next
        mov     dword [ms_any], 1
        lea     rsi, [sector_buf + NB_TEXT_OFF]
        call    ms_tokenize
        jc      .next
        call    ms_apply
.next:
        inc     dword [ms_note_i]
        jmp     .note
.done:
        ret

; ms_tokenize - RSI = text, ECX = length: ms_nw words at ms_wptr/ms_wlen.
; CF set on an empty word (a double, leading or trailing space) or more
; than sixteen.
ms_tokenize:
        xor     r8d, r8d                ; words
        mov     r9, rsi                 ; this word's start
        lea     r10, [rsi + rcx]        ; the end
.byte:
        cmp     rsi, r10
        je      .last
        cmp     byte [rsi], ' '
        je      .space
        inc     rsi
        jmp     .byte
.space:
        call    .word
        jc      .bad
        inc     rsi
        mov     r9, rsi
        jmp     .byte
.last:
        call    .word
        jc      .bad
        mov     [ms_nw], r8d
        clc
        ret
.bad:
        stc
        ret
.word:                                  ; [r9, rsi) is a word
        mov     rax, rsi
        sub     rax, r9
        jz      .empty
        cmp     r8d, 16
        jae     .empty
        lea     rdx, [ms_wptr]
        mov     [rdx + r8*8], r9
        lea     rdx, [ms_wlen]
        mov     [rdx + r8*4], eax
        inc     r8d
        clc
        ret
.empty:
        stc
        ret

; w_is - EDX = a word's index, RDI = a literal, ECX = its length: ZF set
; when the word is the literal. Preserves everything but flags.
w_is:
        push    rax
        push    rcx
        push    rsi
        push    rdi
        lea     rax, [ms_wlen]
        cmp     [rax + rdx*4], ecx
        jne     .out
        lea     rax, [ms_wptr]
        mov     rsi, [rax + rdx*8]
        repe    cmpsb
.out:   pop     rdi
        pop     rsi
        pop     rcx
        pop     rax
        ret

%macro WIS 2                            ; word index, literal label
        mov     edx, %1
        lea     rdi, [%2]
        mov     ecx, %2_len
        call    w_is
%endmacro

; w_dec - EDX = a word's index: EAX = its value, CF set unless it is 1-9
; decimal digits. Preserves everything else.
w_dec:
        push    rcx
        push    rsi
        push    r8
        lea     rax, [ms_wlen]
        mov     ecx, [rax + rdx*4]
        cmp     ecx, 9
        ja      .bad
        lea     rax, [ms_wptr]
        mov     rsi, [rax + rdx*8]
        xor     eax, eax
.d:     movzx   r8d, byte [rsi]
        sub     r8d, '0'
        cmp     r8d, 9
        ja      .bad
        imul    eax, eax, 10
        add     eax, r8d
        inc     rsi
        dec     ecx
        jnz     .d
        pop     r8
        pop     rsi
        pop     rcx
        clc
        ret
.bad:   pop     r8
        pop     rsi
        pop     rcx
        stc
        ret

; w_hex16 - EDX = a word's index: RSI = its address, CF set unless it is
; sixteen lowercase hex digits. Preserves everything else.
w_hex16:
        push    rax
        push    rcx
        lea     rax, [ms_wlen]
        cmp     dword [rax + rdx*4], 16
        jne     .bad
        lea     rax, [ms_wptr]
        mov     rsi, [rax + rdx*8]
        xor     ecx, ecx
.h:     movzx   eax, byte [rsi + rcx]
        cmp     al, '0'
        jb      .bad
        cmp     al, '9'
        jbe     .ok
        cmp     al, 'a'
        jb      .bad
        cmp     al, 'f'
        ja      .bad
.ok:    inc     ecx
        cmp     ecx, 16
        jb      .h
        pop     rcx
        pop     rax
        clc
        ret
.bad:   pop     rcx
        pop     rax
        stc
        ret

; w_slot - EDX = a word's index: EAX = its slot word (0 i8042, 1 disk, 2
; wire, 3 kernel), or -1. Preserves everything else.
w_slot:
        push    rcx
        push    rdi
        push    rsi
        push    r8
        xor     r8d, r8d
.s:     lea     rdi, [slot_words]
        mov     eax, r8d
        shl     eax, 3
        add     rdi, rax
        xor     ecx, ecx                ; the word's length, from its NULs
.l:     cmp     ecx, 8
        je      .lend
        cmp     byte [rdi + rcx], 0
        je      .lend
        inc     ecx
        jmp     .l
.lend:  call    w_is
        je      .found
        inc     r8d
        cmp     r8d, 4
        jb      .s
        mov     eax, -1
        jmp     .out
.found: mov     eax, r8d
.out:   pop     r8
        pop     rsi
        pop     rdi
        pop     rcx
        ret

; w_state - EDX = a word's index: EAX = ST_SHADOW or ST_LIVE, or -1.
w_state:
        push    rdi
        push    rcx
        mov     eax, ST_SHADOW
        lea     rdi, [w_shadow]
        mov     ecx, 6
        call    w_is
        je      .out
        mov     eax, ST_LIVE
        lea     rdi, [w_live]
        mov     ecx, 4
        call    w_is
        je      .out
        mov     eax, -1
.out:   pop     rcx
        pop     rdi
        ret

; w_why - EDX = a word's index: EAX = WHY_WATCHDOG or WHY_UNHEALTHY, or -1.
w_why:
        push    rdi
        push    rcx
        mov     eax, WHY_WATCHDOG
        lea     rdi, [w_watchdog]
        mov     ecx, 8
        call    w_is
        je      .out
        mov     eax, WHY_UNHEALTHY
        lea     rdi, [w_unhealthy]
        mov     ecx, 9
        call    w_is
        je      .out
        mov     eax, -1
.out:   pop     rcx
        pop     rdi
        ret

; slot_rec - EAX = a slot's table index: RBX = its record. Preserves the rest.
slot_rec:
        push    rax
        push    rdx
        mov     edx, SS_SIZE
        imul    eax, edx
        lea     rbx, [ms_slots]
        add     rbx, rax
        pop     rdx
        pop     rax
        ret

; ms_apply - the tokenized note (word 0 is "molt") applied to the scan.
ms_apply:
        cmp     dword [ms_nw], 2
        jb      .ret
        WIS     1, w_boot
        je      .boot
        WIS     1, w_healthy
        je      .healthy
        WIS     1, w_recovery
        je      .recovery
        mov     edx, 1
        call    w_slot
        cmp     eax, -1
        je      .ret
        cmp     dword [ms_nw], 3
        jb      .ret
        mov     r12d, -2                ; a slot word outside this ring's table
        cmp     eax, SLOT_N
        jae     .slot_known
        mov     r12d, eax
.slot_known:                            ; R12D = the slot's index, or -2
        WIS     2, w_shadow
        je      .install
        WIS     2, w_live
        je      .take
        WIS     2, w_demoted
        je      .demoted
        WIS     2, w_undo
        je      .undo
        WIS     2, w_count
        je      .count
.ret:   ret

.boot:
        mov     eax, [ms_nw]
        cmp     eax, 5
        jb      .ret
        test    eax, 1
        jz      .ret
        mov     edx, 2
        call    w_dec
        jc      .ret
        mov     r13d, eax               ; the boot number
        mov     edx, 3                  ; every pair valid, or the note is none
.pair_check:
        cmp     edx, [ms_nw]
        jae     .pairs_ok
        call    w_slot
        cmp     eax, -1
        je      .ret
        inc     edx
        call    w_state
        cmp     eax, -1
        je      .ret
        inc     edx
        jmp     .pair_check
.pairs_ok:
        inc     dword [ms_boots]
        inc     dword [ms_run]
        mov     edx, 3
.pair:
        cmp     edx, [ms_nw]
        jae     .ret
        call    w_slot
        mov     r14d, eax
        inc     edx
        call    w_state
        inc     edx
        cmp     r14d, SLOT_N
        jae     .pair
        push    rdx
        mov     r15d, eax               ; shadow or live
        mov     eax, r14d
        call    slot_rec
        call    ms_boot_note
        pop     rdx
        jmp     .pair

.healthy:
        cmp     dword [ms_nw], 3
        jne     .ret
        mov     edx, 2
        call    w_dec
        jc      .ret
        mov     dword [ms_run], 0
        mov     r13d, eax
        xor     r14d, r14d
.h_slot:
        cmp     r14d, SLOT_N
        jae     .ret
        mov     eax, r14d
        call    slot_rec
        movzx   ecx, byte [rbx + SS_NACC]
        lea     rsi, [rbx + SS_ACC]
.h_acc: test    ecx, ecx
        jz      .h_next
        cmp     [rsi + AC_LBOOT], r13d
        jne     .h_skip
        cmp     [rsi + AC_HBOOT], r13d
        je      .h_skip
        mov     [rsi + AC_HBOOT], r13d
        inc     dword [rsi + AC_PROB]
.h_skip:
        add     rsi, ACC_SIZE
        dec     ecx
        jmp     .h_acc
.h_next:
        inc     r14d
        jmp     .h_slot

.recovery:
        cmp     dword [ms_nw], 3
        jne     .ret
        WIS     2, w_owner
        je      .rec_ok
        WIS     2, w_all
        jne     .ret
.rec_ok:
        mov     dword [ms_run], 0
        ret

.install:                               ; molt <slot> shadow <b> <B> <K> <M>
        cmp     dword [ms_nw], 7
        jne     .ret
        mov     edx, 3
        call    w_hex16
        jc      .ret
        mov     r13, rsi                ; the build
        mov     edx, 4
        call    w_dec
        jc      .ret
        mov     [ms_vals], eax
        mov     edx, 5
        call    w_dec
        jc      .ret
        mov     [ms_vals + 4], eax
        mov     edx, 6
        call    w_dec
        jc      .ret
        mov     [ms_vals + 8], eax
        mov     [ms_last], r12d
        cmp     r12d, 0
        jl      .ret
        mov     eax, r12d
        call    slot_rec
        mov     rsi, r13
        call    ms_bld_find             ; RDI = the build's record
        mov     eax, [ms_vals]
        mov     [rdi + BD_THR], eax
        mov     eax, [ms_vals + 4]
        mov     [rdi + BD_THR + 4], eax
        mov     eax, [ms_vals + 8]
        mov     [rdi + BD_THR + 8], eax
        mov     al, [rbx + SS_KIND]     ; the state before this install
        mov     [rdi + BD_BKIND], al
        mov     al, [rbx + SS_WHY]
        mov     [rdi + BD_BWHY], al
        push    rdi
        lea     rsi, [rbx + SS_BUILD]
        add     rdi, BD_BBUILD
        mov     ecx, 16
        rep     movsb
        pop     rdi
        mov     byte [rbx + SS_KIND], ST_SHADOW
        mov     byte [rbx + SS_WHY], 0
        mov     rsi, r13
        lea     rdi, [rbx + SS_BUILD]
        mov     ecx, 16
        rep     movsb
        mov     byte [rbx + SS_NACC], 0 ; the build entered shadow: the counts start
        mov     byte [rbx + SS_START], 1
        ret

.take:                                  ; molt <slot> live <b>
        cmp     dword [ms_nw], 4
        jne     .ret
        mov     edx, 3
        call    w_hex16
        jc      .ret
        mov     [ms_last], r12d
        cmp     r12d, 0
        jl      .ret
        mov     eax, r12d
        call    slot_rec
        mov     byte [rbx + SS_KIND], ST_LIVE
        mov     byte [rbx + SS_WHY], 0
        lea     rdi, [rbx + SS_BUILD]
        mov     ecx, 16
        rep     movsb
        ret

.demoted:                               ; molt <slot> demoted <b> <why>
        cmp     dword [ms_nw], 5
        jne     .ret
        mov     edx, 3
        call    w_hex16
        jc      .ret
        mov     r13, rsi
        mov     edx, 4
        call    w_why
        cmp     eax, -1
        je      .ret
        mov     dword [ms_run], 0
        mov     [ms_last], r12d
        cmp     r12d, 0
        jl      .ret
        mov     r14d, eax
        mov     eax, r12d
        call    slot_rec
        mov     byte [rbx + SS_KIND], ST_DEMOTED
        mov     [rbx + SS_WHY], r14b
        mov     rsi, r13
        lea     rdi, [rbx + SS_BUILD]
        mov     ecx, 16
        rep     movsb
        ret

.undo:                                  ; molt <slot> undo <state>
        call    ms_undo_state           ; ms_newst, or CF
        jc      .ret
        mov     [ms_last], r12d
        cmp     r12d, 0
        jl      .ret
        mov     eax, r12d
        call    slot_rec
        cmp     byte [rbx + SS_KIND], ST_DEMOTED
        jne     .undo_set
        cmp     byte [ms_newst], ST_SHADOW
        jne     .undo_set
        mov     byte [rbx + SS_NACC], 0 ; from demoted to shadow: the counts start again
        mov     byte [rbx + SS_START], 1
.undo_set:
        mov     al, [ms_newst]
        mov     [rbx + SS_KIND], al
        mov     al, [ms_newst + 1]
        mov     [rbx + SS_WHY], al
        lea     rsi, [ms_newst + 8]
        lea     rdi, [rbx + SS_BUILD]
        mov     ecx, 16
        rep     movsb
        ret

.count:                                 ; molt <slot> count <n> <k> <p> <d>
        cmp     dword [ms_nw], 7
        jne     .ret
        mov     edx, 3
        call    w_dec
        jc      .ret
        mov     r13d, eax
        mov     edx, 4
        call    w_dec
        jc      .ret
        mov     [ms_vals], eax
        mov     edx, 5
        call    w_dec
        jc      .ret
        mov     [ms_vals + 4], eax
        mov     edx, 6
        call    w_dec
        jc      .ret
        mov     [ms_vals + 8], eax
        cmp     r12d, 0
        jl      .ret
        mov     eax, r12d
        call    slot_rec
        movzx   ecx, byte [rbx + SS_NACC]
        lea     rsi, [rbx + SS_ACC]
.c_acc: test    ecx, ecx
        jz      .ret
        cmp     [rsi + AC_SBOOT], r13d
        jne     .c_next
        mov     eax, [ms_vals]
        mov     [rsi + AC_PKEYS], eax
        mov     eax, [ms_vals + 4]
        mov     [rsi + AC_PPK], eax
        mov     eax, [ms_vals + 8]
        mov     [rsi + AC_PD], eax
.c_next:
        add     rsi, ACC_SIZE
        dec     ecx
        jmp     .c_acc

; ms_undo_state - the words from 3 as a state (parts.py's state_words):
; ms_newst = kind, why, build; CF if not a state.
ms_undo_state:
        mov     byte [ms_newst], ST_GENERIC
        mov     byte [ms_newst + 1], 0
        mov     eax, [ms_nw]
        cmp     eax, 4
        jne     .two
        WIS     3, w_generic
        jne     .bad
        clc
        ret
.two:
        cmp     eax, 5
        jne     .three
        mov     edx, 3
        call    w_state
        cmp     eax, -1
        je      .bad
        mov     [ms_newst], al
        mov     edx, 4
        jmp     .build
.three:
        cmp     eax, 6
        jne     .bad
        WIS     3, w_demoted
        jne     .bad
        mov     edx, 5
        call    w_why
        cmp     eax, -1
        je      .bad
        mov     byte [ms_newst], ST_DEMOTED
        mov     [ms_newst + 1], al
        mov     edx, 4
.build:
        call    w_hex16
        jc      .bad
        lea     rdi, [ms_newst + 8]
        mov     ecx, 16
        rep     movsb
        clc
        ret
.bad:
        stc
        ret

; ms_boot_note - RBX = a slot's record, R13D = the boot's number, R15D =
; shadow or live as the note says: the build in the slot's state now gets
; the boot (a shadow boot: its pending count committed, a new one begun).
ms_boot_note:
        cmp     byte [rbx + SS_KIND], ST_GENERIC
        je      .ret
        lea     rsi, [rbx + SS_BUILD]
        call    ms_acc_find             ; RDI = the build's accumulator
        cmp     r15d, ST_SHADOW
        jne     .live
        inc     dword [rdi + AC_BOOTS]
        mov     eax, [rdi + AC_PKEYS]
        add     [rdi + AC_KEYS], eax
        mov     eax, [rdi + AC_PPK]
        add     [rdi + AC_PK], eax
        mov     eax, [rdi + AC_PD]
        add     [rdi + AC_D], eax
        xor     eax, eax
        mov     [rdi + AC_PKEYS], eax
        mov     [rdi + AC_PPK], eax
        mov     [rdi + AC_PD], eax
        mov     [rdi + AC_SBOOT], r13d
        ret
.live:
        mov     [rdi + AC_LBOOT], r13d
.ret:   ret

; ms_acc_find - RBX = a slot's record, RSI = 16 hex: RDI = the build's
; accumulator since the slot's start, made if absent (the fourth reused).
ms_acc_find:
        push    rcx
        push    rax
        movzx   ecx, byte [rbx + SS_NACC]
        lea     rdi, [rbx + SS_ACC]
        xor     eax, eax
.a:     cmp     eax, ecx
        jae     .new
        push    rsi
        push    rdi
        push    rcx
        mov     ecx, 16
        repe    cmpsb
        pop     rcx
        pop     rdi
        pop     rsi
        je      .out
        add     rdi, ACC_SIZE
        inc     eax
        jmp     .a
.new:
        cmp     ecx, ACC_MAX
        jb      .room
        sub     rdi, ACC_SIZE           ; full: the last one is reused
        dec     ecx
.room:
        inc     ecx
        mov     [rbx + SS_NACC], cl
        push    rdi
        push    rcx
        push    rax
        mov     ecx, ACC_SIZE
        xor     eax, eax
        rep     stosb
        pop     rax
        pop     rcx
        pop     rdi
        push    rsi
        push    rdi
        push    rcx
        mov     ecx, 16
        rep     movsb
        pop     rcx
        pop     rdi
        pop     rsi
.out:
        pop     rax
        pop     rcx
        ret

; ms_bld_find - RBX = a slot's record, RSI = 16 hex: RDI = the build's
; install record, made if absent (round robin over BLD_MAX).
ms_bld_find:
        push    rcx
        push    rax
        xor     eax, eax
        lea     rdi, [rbx + SS_BLD]
.b:     cmp     eax, BLD_MAX
        jae     .new
        push    rsi
        push    rdi
        mov     ecx, 16
        repe    cmpsb
        pop     rdi
        pop     rsi
        je      .out
        add     rdi, BLD_SIZE
        inc     eax
        jmp     .b
.new:
        mov     eax, [rbx + SS_NBLD]
        inc     dword [rbx + SS_NBLD]
        xor     edx, edx
        mov     ecx, BLD_MAX
        div     ecx
        imul    edx, edx, BLD_SIZE
        lea     rdi, [rbx + SS_BLD]
        add     rdi, rdx
        push    rsi
        push    rdi
        mov     ecx, 16
        rep     movsb
        pop     rdi
        pop     rsi
.out:
        pop     rax
        pop     rcx
        ret

; ms_bld_lookup - RBX = a slot's record, RSI = 16 hex: RDI = the build's
; install record, or 0.
ms_bld_lookup:
        push    rcx
        push    rax
        xor     eax, eax
        lea     rdi, [rbx + SS_BLD]
.b:     cmp     eax, BLD_MAX
        jae     .none
        push    rsi
        push    rdi
        mov     ecx, 16
        repe    cmpsb
        pop     rdi
        pop     rsi
        je      .out
        add     rdi, BLD_SIZE
        inc     eax
        jmp     .b
.none:  xor     edi, edi
.out:   pop     rax
        pop     rcx
        ret

; slot_counts - RBX = a slot's record: ms_vals = boots, keys, packets,
; disagreements over the current build's shadow boots (parts.py
; counts_of); EAX = its probation (probation_of).
slot_counts:
        xor     eax, eax
        mov     [ms_vals], eax
        mov     [ms_vals + 4], eax
        mov     [ms_vals + 8], eax
        mov     [ms_vals + 12], eax
        movzx   ecx, byte [rbx + SS_KIND]
        cmp     ecx, ST_SHADOW
        je      .has
        cmp     ecx, ST_LIVE
        jne     .out
.has:
        cmp     byte [rbx + SS_START], 0
        je      .out
        push    rdi
        push    rsi
        lea     rsi, [rbx + SS_BUILD]
        movzx   ecx, byte [rbx + SS_NACC]
        lea     rdi, [rbx + SS_ACC]
.a:     test    ecx, ecx
        jz      .none
        push    rsi
        push    rdi
        push    rcx
        mov     ecx, 16
        repe    cmpsb
        pop     rcx
        pop     rdi
        pop     rsi
        je      .found
        add     rdi, ACC_SIZE
        dec     ecx
        jmp     .a
.found:
        mov     eax, [rdi + AC_BOOTS]
        mov     [ms_vals], eax
        mov     eax, [rdi + AC_KEYS]
        add     eax, [rdi + AC_PKEYS]
        mov     [ms_vals + 4], eax
        mov     eax, [rdi + AC_PK]
        add     eax, [rdi + AC_PPK]
        mov     [ms_vals + 8], eax
        mov     eax, [rdi + AC_D]
        add     eax, [rdi + AC_PD]
        mov     [ms_vals + 12], eax
        xor     eax, eax
        cmp     byte [rbx + SS_KIND], ST_LIVE
        jne     .none
        mov     eax, [rdi + AC_PROB]
.none:
        pop     rsi
        pop     rdi
.out:
        ret

; slot_on_probation - EAX = a slot's index: ZF clear (EAX = 1) when it is
; live below probation's three, else EAX = 0.
slot_on_probation:
        push    rbx
        push    rcx
        call    slot_rec
        cmp     byte [rbx + SS_KIND], ST_LIVE
        jne     .no
        call    slot_counts
        cmp     eax, PROBATION
        jae     .no
        mov     eax, 1
        jmp     .out
.no:    xor     eax, eax
.out:   test    eax, eax
        pop     rcx
        pop     rbx
        ret

; ------------------------------------------------------- the boot block --

; molt_boot - PARTS.md, "The boot with a molt note", in place of
; mouse_init: after S7: glass core, before the controller's init. With no
; molt note it is mouse_init alone. Interrupts off, on the BSP. Clobbers
; registers freely.
molt_boot:
        mov     dword [part_loaded], 0
        mov     dword [part_state], 0
        call    molt_scan
        cmp     dword [ms_any], 0
        je      .generic
        ; 1. A3's minimal setup - port 1 enabled, the buffer drained - before
        ; the known answer's line, so that a hold sent when that line lands
        ; is never drained: the window's poll then finds its make. Then the
        ; known answer.
        call    esc_setup
        lea     rsi, [kat_abc]
        mov     ecx, 3
        lea     rdi, [ldr_kat]
        call    sha256
        lea     rsi, [ldr_kat]
        lea     rdi, [kat_digest]
        mov     ecx, 32
        repe    cmpsb
        jne     .kat_fail
        lea     rsi, [msg_s8_kat]
        call    s8_line
        ; 2. the evidence, read and cleared; then the timer halted, so that a
        ; boot that arms nothing (a recovery, Esc, a door refusal) never
        ; leans on the firmware to stop a timer an earlier boot armed (the
        ; owner's decision at item 16). Step 6 unhalts it when it arms.
        call    tco_find
        call    tco_evidence
        call    tco_halt
        ; 3. the recovery decision
        call    recovery_apply
        test    eax, eax
        jnz     .generic
        ; 4. Esc, when a slot is in shadow or live
        call    any_running
        test    eax, eax
        jz      .generic
        call    esc_window
        cmp     dword [esc_held], 0
        je      .door
        lea     rsi, [note_recovery_owner]
        call    molt_note
        lea     rsi, [msg_s8_owner]
        call    s8_line
        jmp     .generic
.door:
        ; 5. the door, for each slot in shadow or live
        xor     r12d, r12d
.door_slot:
        cmp     r12d, SLOT_N
        jae     .door_done
        mov     eax, r12d
        call    slot_rec
        movzx   eax, byte [rbx + SS_KIND]
        cmp     eax, ST_SHADOW
        je      .door_try
        cmp     eax, ST_LIVE
        jne     .door_next
.door_try:
        push    r12
        mov     eax, r12d
        call    door
        pop     r12
.door_next:
        inc     r12d
        jmp     .door_slot
.door_done:
        cmp     dword [part_loaded], 0
        je      .generic
        ; 6. the boot note, then the watchdog armed
        mov     eax, [ms_boots]
        inc     eax
        mov     [boot_n], eax
        lea     rdi, [ldr_note]
        lea     rsi, [w_molt_boot]
        call    str_copy
        mov     eax, [boot_n]
        call    put_dec
        mov     al, ' '
        stosb
        xor     eax, eax
        call    put_slot
        mov     al, ' '
        stosb
        lea     rsi, [w_shadow]
        cmp     dword [part_state], ST_SHADOW
        je      .bn_state
        lea     rsi, [w_live]
.bn_state:
        call    str_copy
        mov     byte [rdi], 0
        lea     rsi, [ldr_note]
        call    molt_note
        call    tco_arm
        call    svc3_fill
        ; 7. the controller: a live part's init, or the generic's
        cmp     dword [part_state], ST_LIVE
        jne     .shadow_init
        call    pointer_centre
        mov     eax, PH_INIT
        lea     rdi, [svc3_live]
        call    part_call
        jmp     .gates
.shadow_init:
        call    mouse_init
.gates:
        ; the stubs that feed the raw ring, in place of ring 7d's gates
        lea     rdi, [idt + 0x21*16]
        lea     rax, [irq1_part]
        call    idt_set_gate
        lea     rdi, [idt + 0x2C*16]
        lea     rax, [irq12_part]
        call    idt_set_gate
        ret
.kat_fail:
        lea     rsi, [err_kat]
        call    serial_err_line
.generic:
        call    mouse_init
        ret

; molt_ready - S7: keyboard ready is out: S8: lines go raw from here, and
; the health mark counts from now.
molt_ready:
        mov     dword [after_ready], 1
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     [ready_tsc], rax
        ret

; any_running - EAX = 1 when a slot is in shadow or live.
any_running:
        xor     ecx, ecx
.s:     cmp     ecx, SLOT_N
        jae     .no
        mov     eax, ecx
        call    slot_rec
        movzx   eax, byte [rbx + SS_KIND]
        cmp     eax, ST_SHADOW
        je      .yes
        cmp     eax, ST_LIVE
        je      .yes
        inc     ecx
        jmp     .s
.no:    xor     eax, eax
        ret
.yes:   mov     eax, 1
        ret

; recovery_apply - PARTS.md's recovery table (parts.py recovery_of) with
; the evidence: EAX = 1 when this boot is a recovery (its notes journaled,
; its line printed, no part to load), else 0.
recovery_apply:
        mov     r13d, WHY_WATCHDOG
        cmp     dword [evidence], 0
        jne     .why
        mov     r13d, WHY_UNHEALTHY
        cmp     dword [ms_run], 2
        jae     .why
        xor     eax, eax
        ret
.why:
        xor     r12d, r12d              ; the blamed: the first shadow or probation slot
.blame:
        cmp     r12d, SLOT_N
        jae     .no_blamed
        mov     eax, r12d
        call    slot_rec
        cmp     byte [rbx + SS_KIND], ST_SHADOW
        je      .blamed
        mov     eax, r12d
        call    slot_on_probation
        jnz     .blamed
        inc     r12d
        jmp     .blame
.blamed:
        mov     eax, r12d
        call    demote_note
        lea     rdi, [ldr_line]
        lea     rsi, [w_s8_recovery]
        call    str_copy
        mov     eax, r12d
        call    put_slot
        mov     al, ' '
        stosb
        lea     rsi, [w_watchdog]
        cmp     r13d, WHY_WATCHDOG
        je      .bw
        lea     rsi, [w_unhealthy]
.bw:    call    str_copy
        mov     byte [rdi], 0
        lea     rsi, [ldr_line]
        call    s8_line
        mov     eax, 1
        ret
.no_blamed:
        xor     r12d, r12d
        xor     r14d, r14d              ; demoted any
.all:
        cmp     r12d, SLOT_N
        jae     .all_done
        mov     eax, r12d
        call    slot_rec
        movzx   eax, byte [rbx + SS_KIND]
        cmp     eax, ST_SHADOW
        je      .all_one
        cmp     eax, ST_LIVE
        jne     .all_next
.all_one:
        mov     eax, r12d
        call    demote_note
        mov     r14d, 1
.all_next:
        inc     r12d
        jmp     .all
.all_done:
        test    r14d, r14d              ; the evidence with nothing running:
        jz      .none                   ; cleared, and nothing else happens
        lea     rsi, [note_recovery_all]
        call    molt_note
        lea     rsi, [msg_s8_all]
        call    s8_line
        mov     eax, 1
        ret
.none:
        xor     eax, eax
        ret

; demote_note - EAX = a slot, R13D = the why: "molt <slot> demoted <b> <why>".
demote_note:
        push    rax
        call    slot_rec
        lea     rdi, [ldr_note]
        lea     rsi, [w_molt_sp]
        call    str_copy
        pop     rax
        call    put_slot
        lea     rsi, [w_sp_demoted_sp]
        call    str_copy
        lea     rsi, [rbx + SS_BUILD]
        mov     ecx, 16
        rep     movsb
        mov     al, ' '
        stosb
        lea     rsi, [w_watchdog]
        cmp     r13d, WHY_WATCHDOG
        je      .w
        lea     rsi, [w_unhealthy]
.w:     call    str_copy
        mov     byte [rdi], 0
        lea     rsi, [ldr_note]
        call    molt_note
        ret

; ---------------------------------------------------------- the door ----

; door - EAX = a slot in shadow or live (PARTS.md, step 5): the home
; entry part-<slot>, its build's first 16 hex the state's, its bytes
; hashing to the entry; the header valid. i8042's part is copied to its
; region and loaded; another slot's is only judged (this ring loads i8042
; alone). Its S8: line either way.
door:
        mov     r12d, eax
        call    slot_rec
        mov     r13, rbx                ; the slot's record
        call    part_name               ; name_buf = "part-<slot>"
        lea     r14, [name_buf]
        call    home_find_entry
        cmp     eax, -1
        je      .bad_hash
        mov     r15d, eax
        call    home_entry_addr         ; RDI = the entry
        mov     rbx, rdi
        lea     rsi, [rbx + HE_CUR + HB_SHA]
        lea     rdi, [ldr_hex]
        mov     ecx, 8
        call    put_hex_bytes
        lea     rsi, [ldr_hex]
        lea     rdi, [r13 + SS_BUILD]
        mov     ecx, 16
        repe    cmpsb
        jne     .bad_hash
        mov     r8d, [rbx + HE_CUR + HB_SIZE]
        cmp     r8d, PART_MAX
        ja      .bad_header
        lea     rdi, [part_region]
        test    r12d, r12d
        jz      .read
        lea     rdi, [comp_region + APP_BLOB_OFF]   ; a slot this ring cannot load: judged only
.read:
        mov     r9, rdi                 ; the bytes' home
        push    rbx
        mov     ecx, [rbx + HE_CUR + HB_SECTORS]
        mov     ebx, [rbx + HE_CUR + HB_FIRST]
.sector:
        mov     eax, VBLK_T_IN
        call    home_rw
        add     rdi, 512
        inc     ebx
        dec     ecx
        jnz     .sector
        pop     rbx
        mov     rsi, r9
        mov     ecx, r8d
        lea     rdi, [sha_digest]
        push    r8
        push    r9
        call    sha256
        pop     r9
        pop     r8
        lea     rsi, [sha_digest]
        lea     rdi, [rbx + HE_CUR + HB_SHA]
        mov     ecx, 32
        repe    cmpsb
        jne     .bad_hash
        mov     rsi, r9
        mov     ecx, r8d
        mov     edx, r12d
        call    check_part
        jc      .bad_header
        test    r12d, r12d
        jnz     .judged
        movzx   eax, byte [r13 + SS_KIND]
        mov     [part_state], eax
        mov     dword [part_loaded], 1
.judged:
        lea     rdi, [ldr_line]            ; "S8: part <slot> <state> <b>"
        lea     rsi, [w_s8_part]
        call    str_copy
        mov     eax, r12d
        call    put_slot
        mov     al, ' '
        stosb
        mov     rbx, r13
        call    put_state
        mov     byte [rdi], 0
        lea     rsi, [ldr_line]
        call    s8_line
        ret
.bad_hash:
        lea     rdx, [w_bad_hash]
        jmp     .bad
.bad_header:
        lea     rdx, [w_bad_header]
.bad:
        lea     rdi, [ldr_line]
        lea     rsi, [w_s8_part]
        call    str_copy
        mov     eax, r12d
        call    put_slot
        mov     al, ' '
        stosb
        mov     rsi, rdx
        call    str_copy
        mov     byte [rdi], 0
        lea     rsi, [ldr_line]
        call    s8_line
        ret

; part_name - EAX = a slot: name_buf = "part-<slot>", NUL-padded to 32.
part_name:
        push    rax
        lea     rdi, [name_buf]
        mov     ecx, 4
        xor     eax, eax
.z:     mov     [rdi + rcx*8 - 8], rax
        dec     ecx
        jnz     .z
        mov     dword [rdi], 'part'
        mov     byte [rdi + 4], '-'
        add     rdi, 5
        pop     rax
        call    put_slot
        ret

; check_part - RSI = a part, ECX = its length, EDX = the slot asked for
; (an index) or -1: PARTS.md's header rule (parts.py check_part). CF clear
; when valid; else CF set and EAX = 1 bad header, 2 bad hash, 3 wrong slot.
; Clobbers registers but RBX, R12-R15.
check_part:
        push    rbx
        push    r12
        push    r13
        mov     r12, rsi
        mov     r13d, ecx
        mov     r11d, edx
        cmp     ecx, PART_HDR
        jbe     .header
        cmp     ecx, PART_MAX
        ja      .header
        cmp     dword [rsi], 'PART'
        jne     .header
        cmp     byte [rsi + PH_ABI], PART_ABI
        jne     .header
        cmp     word [rsi + 5], 0
        jne     .header
        cmp     byte [rsi + 7], 0
        jne     .header
        ; the slot: one of this ring's table, NUL-padded
        xor     r10d, r10d
.slot:  cmp     r10d, SLOT_N
        jae     .header
        lea     rdi, [slot_words]
        mov     eax, r10d
        shl     eax, 3
        mov     rax, [rdi + rax]
        cmp     [rsi + PH_SLOT], rax
        je      .slot_ok
        inc     r10d
        jmp     .slot
.slot_ok:
        mov     eax, r13d
        sub     eax, PART_HDR
        cmp     [rsi + PH_BODY], eax
        jne     .header
        mov     ecx, 3
        lea     rdi, [rsi + PH_INIT]
.off:   mov     eax, [rdi]
        cmp     eax, PART_HDR
        jb      .header
        cmp     eax, r13d
        jae     .header
        add     rdi, 4
        dec     ecx
        jnz     .off
        ; the name: [a-z0-9][a-z0-9-]{0,15}, NUL-padded
        movzx   eax, byte [rsi + PH_NAME]
        call    .alnum
        jc      .header
        mov     ecx, 1
.name:  cmp     ecx, 16
        jae     .zeros
        movzx   eax, byte [rsi + PH_NAME + rcx]
        test    al, al
        jz      .pad
        cmp     al, '-'
        je      .name_ok
        call    .alnum
        jc      .header
.name_ok:
        inc     ecx
        jmp     .name
.pad:   cmp     byte [rsi + PH_NAME + rcx], 0
        jne     .header
        inc     ecx
        cmp     ecx, 16
        jb      .pad
.zeros: mov     ecx, 80
.z:     cmp     byte [rsi + rcx], 0
        jne     .header
        inc     ecx
        cmp     ecx, PART_HDR
        jb      .z
        ; the body's hash
        lea     rsi, [r12 + PART_HDR]
        mov     ecx, r13d
        sub     ecx, PART_HDR
        lea     rdi, [sha_digest]
        push    r10
        push    r11
        call    sha256
        pop     r11
        pop     r10
        lea     rsi, [sha_digest]
        lea     rdi, [r12 + PH_SHA]
        mov     ecx, 32
        repe    cmpsb
        jne     .hash
        cmp     r11d, -1
        je      .ok
        cmp     r10d, r11d
        jne     .wrong
.ok:
        pop     r13
        pop     r12
        pop     rbx
        clc
        ret
.header:
        mov     eax, 1
        jmp     .fail
.hash:
        mov     eax, 2
        jmp     .fail
.wrong:
        mov     eax, 3
.fail:
        pop     r13
        pop     r12
        pop     rbx
        stc
        ret
.alnum:                                 ; AL: CF clear for [a-z0-9]
        cmp     al, '0'
        jb      .no
        cmp     al, '9'
        jbe     .yes
        cmp     al, 'a'
        jb      .no
        cmp     al, 'z'
        ja      .no
.yes:   clc
        ret
.no:    stc
        ret

; part_call - EAX = an entry's header offset (PH_INIT, PH_BYTE,
; PH_HEALTH); RDI, RSI, RDX, RCX its arguments. The call into the part in
; slot i8042's region: RSP 16-aligned and kept in memory, since a part may
; clobber every register but RSP; DF cleared after. Returns RAX.
part_call:
        lea     r11, [part_region]
        mov     eax, [r11 + rax]
        add     rax, r11
        push    rbx
        push    rbp
        push    r12
        push    r13
        push    r14
        push    r15
        mov     [part_saved_rsp], rsp
        and     rsp, -16
        call    rax
        mov     rsp, [part_saved_rsp]
        cld
        pop     r15
        pop     r14
        pop     r13
        pop     r12
        pop     rbp
        pop     rbx
        ret

; ---------------------------------------------------------- Esc --------

; esc_setup - A3: wait for the input buffer to empty, enable port 1 (0xAE),
; let the controller settle, drain the output buffer. Clobbers RAX, RCX.
esc_setup:
        call    i8042_wait_ibf
        mov     al, 0xAE
        out     0x64, al
        mov     ax, PIT_1MS * 2
        call    pit_wait
.drain: in      al, 0x64
        test    al, 1
        jz      .done
        in      al, 0x60
        jmp     .drain
.done:  ret

; esc_window - "hold Esc for the seed" on the console alone, then the
; ports polled for W = 3,000 ms by the TSC: bytes with status bit 5 set
; dropped; Esc held when a make (0x01 translated, 0x76 untranslated) that
; did not follow 0xF0 arrived and no break followed it (parts.py esc_held:
; F0 76 is Esc's set 2 break, and F0 01 is F9's, neither a make).
; Clobbers RAX, RCX, RDX, RSI, R9-R11.
esc_window:
        lea     rsi, [msg_hold_esc]
        call    console_puts
        mov     al, 10
        call    console_putc
        mov     dword [esc_held], 0
        xor     r9d, r9d                ; the previous byte
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     r10, rax
        mov     rax, [tsc_per_ms]
        imul    rax, rax, ESC_W_MS
        mov     r11, rax
.poll:
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        sub     rax, r10
        cmp     rax, r11
        jae     .done
        in      al, 0x64
        test    al, 1
        jz      .poll
        mov     cl, al
        in      al, 0x60
        test    cl, 0x20
        jnz     .poll
        movzx   eax, al
        cmp     eax, 0x01
        je      .set1
        cmp     eax, 0x76
        je      .set2
        cmp     eax, 0x81
        je      .released
        jmp     .prev
.set1:  cmp     r9d, 0xF0               ; F0 01: F9's break, not Esc
        je      .prev
        jmp     .make
.set2:  cmp     r9d, 0xF0               ; F0 76: Esc's break
        je      .released
.make:
        mov     dword [esc_held], 1
        jmp     .prev
.released:
        mov     dword [esc_held], 0
.prev:
        mov     r9d, eax
        jmp     .poll
.done:
        ret

; ------------------------------------------------------- the watchdog ---

; tco_find - the LPC bridge at 00:1f.0 (Intel's): PMBASE, and TCOBASE from
; it; RCBA, mapped uncached, when its enable bit is set. tco_base 0 when
; there is no TCO; rcba 0 when RCBA is not enabled, which leaves NO_REBOOT
; beyond reach, so tco_arm reports the TCO locked. Clobbers RAX, RBX, RCX.
tco_find:
        mov     dword [tco_base], 0
        mov     dword [pm_base], 0
        mov     dword [rcba], 0
        mov     ebx, LPC_BDF
        xor     ecx, ecx
        call    pci_cfg_read32
        cmp     ax, PCI_VENDOR_INTEL
        jne     .out
        mov     ecx, 0x40
        call    pci_cfg_read32
        and     eax, 0xFF80
        jz      .out
        mov     [pm_base], eax
        add     eax, 0x60
        mov     [tco_base], eax
        mov     ecx, 0xF0
        call    pci_cfg_read32
        test    eax, 1
        jz      .out
        and     eax, 0xFFFFC000
        mov     [rcba], eax
        call    map_mmio_2m
.out:   ret

; tco_evidence - SECOND_TO_STS read into evidence, then cleared by writing
; 1, SECOND_TO_STS before BOOT_STS (the datasheet's order).
tco_evidence:
        mov     dword [evidence], 0
        mov     edx, [tco_base]
        test    edx, edx
        jz      .out
        add     edx, TCO2_STS
        in      ax, dx
        shr     eax, 1
        and     eax, 1
        mov     [evidence], eax
        mov     ax, 0x0002
        out     dx, ax
        mov     ax, 0x0004
        out     dx, ax
.out:   ret

; tco_halt - TCO_TMR_HLT set in TCO1_CNT when there is a TCO; NMI_NOW is
; write-1-to-clear, so it is never written back. Clobbers RAX, RDX.
tco_halt:
        mov     edx, [tco_base]
        test    edx, edx
        jz      .out
        add     edx, TCO1_CNT
        in      ax, dx
        and     ax, 0xFEFF
        or      ax, 0x0800
        out     dx, ax
.out:   ret

; tco_arm - PARTS.md's arming and its line. Clobbers RAX, RCX, RDX, RSI,
; RDI.
tco_arm:
        cmp     dword [tco_base], 0
        je      .none
        call    tco_halt                ; 1. halt (step 2 halted it already)
        mov     edi, [rcba]             ; 2. NO_REBOOT cleared and read back;
        test    edi, edi                ; no RCBA, no reaching it: locked
        jz      .locked
        add     edi, GCS_OFF
        mov     eax, [rdi]
        and     eax, ~0x20
        mov     [rdi], eax
        mov     eax, [rdi]
        test    eax, 0x20
        jnz     .locked
        mov     edx, [pm_base]          ; 3. TCO_EN cleared
        add     edx, SMI_EN
        in      eax, dx
        and     eax, ~0x2000
        out     dx, eax
        mov     edx, [tco_base]         ; 4. TCO_TMR
        add     edx, TCO_TMR_REG
        mov     ax, TCO_TMR_VALUE
        out     dx, ax
        mov     edx, [tco_base]         ; 5. TIMEOUT, SECOND_TO_STS, BOOT_STS
        add     edx, TCO1_STS
        mov     ax, 0x0008
        out     dx, ax
        mov     edx, [tco_base]
        add     edx, TCO2_STS
        mov     ax, 0x0002
        out     dx, ax
        mov     ax, 0x0004
        out     dx, ax
        mov     edx, [tco_base]         ; 6. reload, then unhalt
        add     edx, TCO_RLD
        mov     ax, 1
        out     dx, ax
        mov     edx, [tco_base]
        add     edx, TCO1_CNT
        in      ax, dx
        and     ax, 0xF6FF              ; TCO_TMR_HLT and NMI_NOW clear
        out     dx, ax
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     [last_pet_tsc], rax
        mov     rax, [heartbeat]
        mov     [last_pet_hb], rax
        mov     rax, [obs_page + OBS_FRAMES]
        mov     [last_pet_fr], rax
        mov     dword [tco_armed], 1
        lea     rsi, [msg_s8_tco]       ; 7. its line
        call    s8_line
        ret
.locked:
        lea     rsi, [msg_s8_locked]    ; halted, unguarded: decision 5's fallback
        call    s8_line
        ret
.none:
        lea     rsi, [msg_s8_none]
        call    s8_line
        ret

; molt_breath - a heartbeat at every breath of a bounded wait (the wire's
; TCP poll, the disk's command wait): the boot processor is inside a wait
; until the main loop's next turn (PARTS.md, "Overflows"), the heartbeat
; moves and the pet is asked (A1). molt_turn - the same at a main loop turn
; with a part loaded, which leaves any wait. Preserves every register;
; the flags are not preserved.
molt_breath:
        mov     dword [in_wait], 1
        inc     qword [heartbeat]
        cmp     dword [tco_armed], 0
        jne     molt_pet
        ret
molt_turn:
        mov     dword [in_wait], 0
        inc     qword [heartbeat]
        cmp     dword [tco_armed], 0
        jne     molt_pet
        ret

; molt_pet - the timer reloaded only when all five held since the last
; pet (PARTS.md, "The pet"), at most once per 1,000 ms by the TSC.
; Preserves every register.
molt_pet:
        cmp     dword [tco_armed], 0
        je      .ret
        SAVE_ALL
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     r12, rax
        sub     rax, [last_pet_tsc]
        mov     rcx, [tsc_per_ms]
        imul    rcx, rcx, PET_MS
        cmp     rax, rcx
        jb      .out
        mov     rax, [heartbeat]        ; 1. the heartbeat moved
        cmp     rax, [last_pet_hb]
        je      .out
        mov     rax, [obs_page + OBS_FRAMES]   ; 2. the glass core's frames moved
        cmp     rax, [last_pet_fr]
        je      .out
        cmp     dword [exc_flag], 0     ; 3. no exception
        jne     .out
        cmp     dword [overflow], 0     ; 5b. no ring overflowed between turns
        jne     .out
        in      al, 0x64                ; 5a. the controller's status is sane
        cmp     al, 0xFF
        je      .out
        test    al, 0xC0
        jnz     .out
        cmp     dword [part_state], ST_LIVE     ; 4. a live part's health
        jne     .pet
        mov     eax, PH_HEALTH
        lea     rdi, [svc3_live]
        call    part_call
        test    rax, rax
        jnz     .out
.pet:
        mov     edx, [tco_base]
        add     edx, TCO_RLD
        mov     ax, 1
        out     dx, ax
        mov     [last_pet_tsc], r12
        mov     rax, [heartbeat]
        mov     [last_pet_hb], rax
        mov     rax, [obs_page + OBS_FRAMES]
        mov     [last_pet_fr], rax
.out:
        RESTORE_ALL
.ret:
        ret

; ---------------------------------------------------------- the blame ---

; exc_blame - exc_common's second line (PARTS.md, "The blame line"), with
; a part loaded: RAX = the vector, RDX = the RIP. The flag that stops the
; pets is set first.
exc_blame:
        mov     dword [exc_flag], 1
        mov     r8, rax
        mov     r9, rdx
        lea     rsi, [msg_exc]
        call    serial_puts
        mov     rax, r8
        call    serial_putdec
        lea     rcx, [part_region]
        mov     rax, r9
        sub     rax, rcx
        jb      .seed
        cmp     rax, PART_MAX
        jae     .seed
        mov     r10, rax
        lea     rsi, [msg_in_part]
        call    serial_puts
        lea     rdi, [ldr_hex]
        mov     eax, r10d
        mov     ecx, 8
        call    put_hex_n
        mov     byte [rdi], 0
        lea     rsi, [ldr_hex]
        call    serial_puts
        jmp     .end
.seed:
        lea     rsi, [msg_in_seed]
        call    serial_puts
.end:
        lea     rsi, [msg_crlf]
        call    serial_puts
        ret

; ---------------------------------------------------------------------------
; The loader's constants, inside .text and so read-only with it: its
; serial lines and errors, the words and GUIDs the disk's rule reads,
; the GOP's GUID, and SHA-256's constants.
; ---------------------------------------------------------------------------

msg_alive:      db      'S7: alive', 13, 10, 0
msg_gop:        db      'S7: gop ', 0
msg_fb:         db      ' fb 0x', 0
msg_exited:     db      'S7: boot services exited', 13, 10, 0
msg_paging:     db      'S7: gdt and paging ours', 13, 10, 0
msg_idt:        db      'S7: idt ready', 13, 10, 0
msg_found:      db      'S7: cores found ', 0
msg_woken:      db      'S7: cores woken ', 0
msg_console:    db      'S7: console ', 0
msg_disk:       db      'S7: disk port ', 0
msg_notes_at:   db      ' notes ', 0
msg_home_at:    db      ' home ', 0
msg_port:       db      'port ', 0
msg_colon:      db      ': ', 0
msg_comma:      db      ', ', 0
word_germos:    db      'germos', 0
word_blank:     db      'blank', 0
word_gpt:       db      'gpt', 0
word_torn:      db      'torn', 0
word_other:     db      'other', 0
crc_zero4:      dd      0
guid_notes_type: db     0x57,0x55,0x84,0x50,0x34,0xee,0x31,0x47,0x8b,0x83,0xd1,0xd6,0xf1,0x4f,0xd8,0xc5
guid_home_type: db      0x07,0x40,0x6d,0x45,0x03,0xd8,0xa0,0x41,0xa6,0x61,0xca,0x73,0x6d,0xdc,0xf9,0x6b
msg_nb:         db      'S7: notebook ', 0
msg_notes:      db      ' notes', 13, 10, 0
msg_nb_fmt:     db      'S7: notebook formatted', 13, 10, 0
msg_home:       db      'S7: home ', 0
msg_apps:       db      ' apps', 13, 10, 0
msg_region:     db      'S7: component region 0x', 0
msg_region_cap: db      ' 1048576 bytes', 13, 10, 0     ; COMP_BLOB_MAX, spelled
msg_obs:        db      'S7: obs page 0x', 0
msg_glass:      db      'S7: glass core ', 0
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
err_one_core:   db      'the glass needs a second core - boot with -smp 2 or more', 0
err_no_ahci:    db      'no AHCI controller on PCI bus 0', 0
err_no_sata:    db      'no SATA disk on any AHCI port', 0
err_ahci_stop:  db      'AHCI port would not stop', 0
err_ahci_spinup: db     'ahci port ', 0                            ; ring 7c: under CAP.SSS, a device that
err_ahci_spinup_tail: db ' did not come up after spin-up', 13, 10, 0   ; appeared after SUD but never reached DET 3
err_sector_size: db     'disk sector is not 512 bytes', 0
err_no_germos:  db      'no GermOS disk and no blank disk - ', 0
err_gpt_readback: db    'the table written does not read back as GermOS', 0
err_bar_io:     db      'virtio capability names an I/O BAR or a BAR beyond 5 - not a modern device', 0
err_bar_high:   db      'BAR lies beyond the physical address width', 0
err_spare:      db      'page-table pool exhausted - raise SPARE_PAGES', 0
err_disk_big:   db      'disk has 2^32 sectors or more - beyond this stage', 0
err_disk_beyond: db     'disk request beyond the capacity', 0
err_disk_timeout: db    'disk request timed out', 0
err_disk_failed: db     'disk request failed - task file error', 0

; EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID, 9042a9de-23dc-4a38-96fb-7aded080516a.
; A GUID is little-endian in its first three fields and big-endian in the last
; two, which is why this is written out field by field rather than as bytes.
        align   8
gop_guid:       dd      0x9042a9de
                dw      0x23dc
                dw      0x4a38
                db      0x96, 0xfb, 0x7a, 0xde, 0xd0, 0x80, 0x51, 0x6a

; The SHA-256 constants (FIPS 180-4): the sixty-four round constants and
; the eight initial hash words.
        align   4
sha_k:
        dd 0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5
        dd 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174
        dd 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da
        dd 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967
        dd 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85
        dd 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070
        dd 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3
        dd 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
sha_init:
        dd 0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19

err_text_split: db      'the image', 39, 's .text spans two 2 MB pages - it cannot be made read-only', 0

; The molt's constants: the slot words, SHA-256's known answer for "abc",
; the hex digits, the note grammar's words, the S8: lines the loader prints
; and the words of the notes it writes.
        align   8
slot_words:     db      'i8042', 0, 0, 0, 'disk', 0, 0, 0, 0, 'wire', 0, 0, 0, 0, 'kernel', 0, 0
kat_abc:        db      'abc'
kat_digest:     db      0xba, 0x78, 0x16, 0xbf, 0x8f, 0x01, 0xcf, 0xea
                db      0x41, 0x41, 0x40, 0xde, 0x5d, 0xae, 0x22, 0x23
                db      0xb0, 0x03, 0x61, 0xa3, 0x96, 0x17, 0x7a, 0x9c
                db      0xb4, 0x10, 0xff, 0x61, 0xf2, 0x00, 0x15, 0xad
hex_digits:     db      '0123456789abcdef'

%macro MWORD 2
%1:             db      %2, 0
%1_len          equ     $ - %1 - 1
%endmacro
MWORD w_shadow, 'shadow'
MWORD w_live, 'live'
MWORD w_generic, 'generic'
MWORD w_demoted, 'demoted'
MWORD w_watchdog, 'watchdog'
MWORD w_unhealthy, 'unhealthy'
MWORD w_boot, 'boot'
MWORD w_healthy, 'healthy'
MWORD w_recovery, 'recovery'
MWORD w_undo, 'undo'
MWORD w_count, 'count'
MWORD w_owner, 'owner'
MWORD w_all, 'all'

msg_s8_kat:     db      'S8: sha256 ok', 0
err_kat:        db      'sha256 known answer', 0
w_molt_sp:      db      'molt ', 0
w_molt_boot:    db      'molt boot ', 0
w_s8_part:      db      'S8: part ', 0
w_bad_hash:     db      'bad hash', 0
w_bad_header:   db      'bad header', 0
w_sp_demoted_sp: db     ' demoted ', 0
w_s8_recovery:  db      'S8: recovery ', 0
note_recovery_owner: db 'molt recovery owner', 0
msg_s8_owner:   db      'S8: recovery owner', 0
note_recovery_all: db   'molt recovery all', 0
msg_s8_all:     db      'S8: recovery all', 0
msg_hold_esc:   db      'hold Esc for the seed', 0
msg_s8_tco:     db      'S8: watchdog tco 30 s', 0
msg_s8_locked:  db      'S8: watchdog tco locked', 0
msg_s8_none:    db      'S8: watchdog none', 0
msg_in_part:    db      ' in part i8042 +0x', 0
msg_in_seed:    db      ' in seed', 0

; ---------------------------------------------------------------------------
; LOADER_STATE - the loader's mutable state, one page-aligned block the seed
; places in its BSS (PARTS.md, "The read-only floor"): writable, and never
; handed to a part. SHA-256's working state (sha_digest is where the seed's
; install and launch take a build's hash); the scan's state; the boot's
; molt state; the loader's own line buffers.
; ---------------------------------------------------------------------------
%macro LOADER_STATE 0
        alignb  4096
loader_state:
sha_state:      resb    32
sha_w:          resb    256
sha_tail:       resb    128
sha_digest:     resb    32

; The scan (molt_scan)
ms_any:         resd    1               ; a note begins "molt "
ms_boots:       resd    1               ; molt boot notes
ms_run:         resd    1               ; the unhealthy run
ms_last:        resd    1               ; the slot whose state changed last, -1 none, -2 another
ms_note_i:      resd    1               ; the note being scanned
ms_nw:          resd    1               ; its words
        alignb  16
ms_wptr:        resq    16              ; each word's address
ms_wlen:        resd    16              ; and length
        alignb  16
ms_slots:       resb    SLOT_N * SS_SIZE
ms_before:      resb    24              ; scratch: a state (kind, why, build)
ms_newst:       resb    24              ; scratch: an undo's state
ms_vals:        resd    4               ; scratch: a note's numbers

; The boot (molt_boot)
part_loaded:    resd    1               ; a part is loaded this boot
part_state:     resd    1               ; ST_SHADOW or ST_LIVE for i8042, 0 none
boot_n:         resd    1               ; this boot's molt boot number
after_ready:    resd    1               ; S7: keyboard ready is out: S8: lines go raw
        alignb  8
part_saved_rsp: resq    1               ; RSP across a call into a part

; The evidence, Esc, the watchdog, the pet and the health mark
evidence:       resd    1               ; SECOND_TO_STS as read at step 2
esc_held:       resd    1               ; the window's verdict
tco_base:       resd    1               ; TCOBASE, PMBASE + 0x60; 0 none
pm_base:        resd    1               ; PMBASE
rcba:           resd    1               ; RCBA when enabled, mapped; 0 not
tco_armed:      resd    1               ; the verdict: 1 when the TCO was armed
exc_flag:       resd    1               ; exc_common set it: the pets stop
overflow:       resd    1               ; a ring overflowed between two main loop turns
in_wait:        resd    1               ; inside a bounded wait, its first breath to the next turn
health_done:    resd    1               ; the health mark taken
        alignb  8
ready_tsc:      resq    1               ; the TSC at S7: keyboard ready
heartbeat:      resq    1               ; the boot processor's, every turn and breath
last_pet_tsc:   resq    1
last_pet_hb:    resq    1
last_pet_fr:    resq    1

; The loader's line buffers
        alignb  16
ldr_line:       resb    160             ; an S8: line
ldr_note:       resb    160             ; the boot note
ldr_hex:        resb    32              ; a build's first 16 hex
ldr_kat:        resb    32              ; the known answer's digest
        alignb  4096
loader_state_end:
%endmacro
