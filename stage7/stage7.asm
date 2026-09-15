; ============================================================================
; Stage 7 ring 7a - The disk.
;
; Grown on Stage 6's proven body (the glass, the store of plans, the
; pointer - all kept, every serial line under S7: now): across ring 7a's
; plan items 9 and 10 the virtio-blk driver is replaced by an AHCI driver
; per stage7/DISK.md - one SATA disk, a GPT the guest writes, the notebook
; and the home image as two partitions with their frozen formats unchanged
; inside. Below this paragraph the file is the ring 6c source as copied at
; item 1, with the prefix renamed; the item 9 and 10 diffs are the ring's
; work. Stage 6's own text follows.
;
; Stage 6 ring 6a - The glass.
;
; Grown on Stage 5's proven body: the same hand-assembled PE32+ UEFI
; application, serial first, GOP, ExitBootServices with the stale-key
; retry, our own GDT and identity map, the IDT, the MADT walk, every core
; woken with INIT-SIPI-SIPI, the text console, the interrupt-driven
; keyboard, the virtio-blk disk and the notebook, the virtio-net NIC with
; ARP, IPv4 and a client-only TCP, the question per stage4/UMBILICAL.md,
; the forgiving marker parse and the grow request per stage5/GERMLINE.md -
; all kept. Across plan items 10 to 13 the machine grows a face
; (stage6/GLASS.md): the display's EDID read from the VGA device's own
; memory and its preferred mode taken; an obs page every counter is
; written into by the thing doing the work; four regions on the console's
; grid - the obs strip, the choices row, the conversation panel, the app
; panel - each a surface in RAM with dirty rows; a GLASS CORE, the first
; application processor, that alone paints the framebuffer from those
; surfaces at sixty frames a second and draws the strip from the page;
; and ABI 2 - an app is four callbacks, init, step, key and exit, with four
; services into its own panel, stepped by the main loop while the
; conversation stays alive beside it, Tab moving the keys between them,
; Esc the way out. The network is slirp's cage: restrict=on and one
; guestfwd, so the guest's whole world is the broker at 10.0.2.4:9999 -
; which rehearses every candidate in a headless boot of a copy of THIS
; image before delivering it.
;
; The hard safety rule, from the foundation: storage code touches only QEMU
; disk images until Stage 7, and never any disk holding real data. The only
; disk this code has ever seen is a raw file under a stage's out/. Plaintext
; inside the cage this ring; TLS lives in the broker.
;
; Built with:  nasm -f bin stage7/stage7.asm -o stage7/out/BOOTX64.EFI
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

; The scancode ring between the keyboard interrupt and the main loop. A power
; of two, so head and tail wrap with a mask. 256 bytes is dozens of
; keystrokes of headroom; a full ring drops bytes rather than overwriting.
%define KBD_RING_SIZE   0x100

; The mouse ring (ring 6c, GLASS.md "The device"): one entry per complete
; packet - the stamp, the cell word, the buttons held, the buttons newly
; pressed - the keyboard ring's discipline. 64 entries, dropped when full.
%define MSE_RING_SIZE   64
%define MSE_ENTRY       16
%define ME_STAMP        0               ; u64  the TSC at the packet's first byte
%define ME_CELL         8               ; u32  row << 16 | col
%define ME_BUTTONS      12              ; u8   bits 0-2 held after the packet
%define ME_PRESSED      13              ; u8   bits newly set by the packet
%define I8042_WAIT_TRIES 100            ; x 10 ms: the bound on one controller or mouse answer
                                        ; (ring 7c: a second - a PS/2 mouse's self-test after
                                        ; a reset is specified at up to 500 ms; the twin
                                        ; answers on the first poll)

; The choices row's click targets (ring 6c, GLASS.md "The click on the
; choices row"): rebuilt by choices_update with the row, one entry per item -
; its first and last column, what a press does (a key, or the launch of a
; home entry) and the argument.
%define HIT_MAX         5
%define HIT_ENTRY       8
%define HT_FIRST        0               ; u16
%define HT_LAST         2               ; u16
%define HT_KIND         4               ; u8: HIT_KEY or HIT_LAUNCH
%define HT_ARG          5               ; u8: the key byte, or the home entry's index
%define HIT_KEY         1
%define HIT_LAUNCH      2

; Spare 4 KB page-table pages for map_mmio_2m: a BAR above the identity map
; needs a new PDPT and a new PD (and, above 512 GB, a new PML4 entry pointing
; at them). Two pages per region beyond the map; eight is room for four such
; regions, and exhaustion is a reported error, not an overrun.
%define SPARE_PAGES     8

; The virtqueue (see "The disk" below): our static ring capacity, the
; descriptor and ring flags, the virtio-blk request types, and the bound on
; the completion poll.
%define VQ_MAX              256
%define VQ_DESC_NEXT        1
%define VQ_DESC_WRITE       2
%define VQ_AVAIL_NO_INT     1
%define VBLK_T_IN           0           ; a read
%define VBLK_T_OUT          1           ; a write
%define VBLK_S_OK           0
%define VQ_POLL_TRIES       25000       ; x 200 us = about five seconds

; The virtio DEVICE BLOCK (plan decision 9): one per device in BSS, addressed
; through RBP by every virtio routine. The four capability addresses are
; consecutive and indexed by cfg_type (1-4) in vio_attach, so their order is
; load-bearing. Queue blocks follow, one per virtqueue.
%define VIO_BDF             0           ; u32  bus<<16 | device<<11 | function<<8
%define VIO_FOUND           4           ; u32  non-zero once the scan placed a BDF here
%define VIO_COMMON          8           ; u64  common configuration, linear address
%define VIO_NOTIFY          16          ; u64  notification region base
%define VIO_ISR             24          ; u64  ISR status (never read - we poll)
%define VIO_DEVICE          32          ; u64  device-specific configuration
%define VIO_NMULT           40          ; u32  notify_off_multiplier
%define VIO_Q               48          ; the queue blocks start here
%define VQ_BLK              48          ; bytes per queue block
%define Q_SIZE              0           ; u32  the queue's size, from the device
%define Q_MASK              4           ; u32  size - 1
%define Q_LAST_USED         8           ; u32  the next used index we expect
%define Q_DOORBELL          16          ; u64  where a 16-bit write of the queue number notifies
%define Q_DESC              24          ; u64  descriptor table
%define Q_AVAIL             32          ; u64  available ring
%define Q_USED              40          ; u64  used ring
%define VIO_QUEUES          2           ; queue blocks per device block
%define VIO_SECTORS         (VIO_Q + VIO_QUEUES * VQ_BLK)  ; u32 a disk's capacity (ring 6b)
%define VIO_BLOCK_SIZE      (VIO_SECTORS + 8)

; The AHCI controller (stage7/DISK.md, ring 7a): the HBA's registers, a
; port's registers, the command header and table this driver builds, and
; the two partition descriptors over the chosen port.
%define AHCI_CLASS          0x010601    ; class 01, subclass 06, interface 01: bits 31:8 of register 8
%define HBA_CAP             0x00
%define HBA_GHC             0x04
%define HBA_PI              0x0C
%define HBA_PORTS           0x100       ; port 0's registers; 0x80 bytes per port
%define GHC_AE              (1 << 31)
%define GHC_IE              (1 << 1)
%define PX_CLB              0x00
%define PX_CLBU             0x04
%define PX_FB               0x08
%define PX_FBU              0x0C
%define PX_IS               0x10
%define PX_IE               0x14
%define PX_CMD              0x18
%define PX_TFD              0x20
%define PX_SIG              0x24
%define PX_SSTS             0x28
%define PX_SERR             0x30
%define PX_CI               0x38
%define PXCMD_ST            (1 << 0)
%define PXCMD_SUD           (1 << 1)    ; spin-up device (ring 7c)
%define PXCMD_FRE           (1 << 4)
%define PXCMD_FR            (1 << 14)
%define PXCMD_CR            (1 << 15)
%define PXIS_TFES           (1 << 30)
%define TFD_ERR             (1 << 0)
%define TFD_DRQ             (1 << 3)
%define TFD_BSY             (1 << 7)
%define SIG_SATA_DISK       0x00000101
%define FIS_H2D             0x27
%define ATA_IDENTIFY        0xEC
%define ATA_READ_DMA_EXT    0x25
%define ATA_WRITE_DMA_EXT   0x35
%define CT_PRDT             0x80        ; the one PRD, after the 64-byte FIS and the 16-byte ACMD
%define AHCI_STOP_TRIES     2500        ; x 200 us = half a second
%define AHCI_PROBE_TRIES    5000        ; x 200 us = one second for a port's Phy to come up
%define AHCI_SPINUP_TRIES   50000       ; x 200 us = ten seconds for a disk spinning up from rest (ring 7c, AHCI 1.3 10.1.2)
%define CAP_SSS             (1 << 27)   ; staggered spin-up supported: a port's device is not detected until PxCMD.SUD
%define MAX_PORTS           32
%define PART_BASE           0           ; u32  the partition's first LBA
%define PART_SECTORS        4           ; u32  its length in sectors
%define DISK_GERMOS         0           ; DISK.md's five words
%define DISK_BLANK          1
%define DISK_GPT            2
%define DISK_TORN           3
%define DISK_OTHER          4
%define GPT_FIRST_USABLE    34
%define GPT_ENTRIES         128
%define GPT_ENTRY           128
%define GPT_ENTRY_SECTORS   32
%define GPT_MIN_SECTORS     67617       ; DISK.md: the smallest disk the two partitions fit
%define GPT_NOTES_FIRST     2048        ; DISK.md: the partitions the writer makes
%define GPT_HOME_FIRST      34816

; The NIC's receive buffers (plan decision 8): sixteen of 2048 bytes, each
; holding the 12-byte virtio-net header and a whole frame, since buffers do
; not merge. One transmit buffer of the same size.
%define NIC_RX_BUFS         16
%define NIC_RX_BUF          2048
%define VNET_HDR_LEN        12          ; struct virtio_net_hdr with num_buffers

; The e1000e (stage7/WIRE.md, ring 7b): the NIC the metal has, beside the
; virtio-net driver above. Found by vendor, class and a table of three
; device ids; BAR0 is the 128 KB register set, mapped uncached. Legacy
; descriptors, sixteen bytes each: the receive ring over the virtio
; driver's sixteen buffers (offset by its twelve-byte header, so the
; frame arithmetic is shared), the transmit ring over the one transmit
; buffer. Polled, interrupts masked, every wait bounded.
%define PCI_VENDOR_INTEL    0x8086
%define E1K_CLASS           0x020000    ; class 02, subclass 00, interface 00: bits 31:8 of register 8
%define E1K_ID_COUNT        3           ; the ids in e1k_ids: 82574L (the twin), 82579LM (the HP), 82579V
%define E1K_BAR_SIZE        0x20000     ; 128 KB, the register set
%define E1K_CTRL            0x0000
%define E1K_STATUS          0x0008
%define E1K_ICR             0x00C0
%define E1K_IMC             0x00D8
%define E1K_RCTL            0x0100
%define E1K_TCTL            0x0400
%define E1K_TIPG            0x0410
%define E1K_RDBAL           0x2800
%define E1K_RDBAH           0x2804
%define E1K_RDLEN           0x2808
%define E1K_RDH             0x2810
%define E1K_RDT             0x2818
%define E1K_TDBAL           0x3800
%define E1K_TDBAH           0x3804
%define E1K_TDLEN           0x3808
%define E1K_TDH             0x3810
%define E1K_TDT             0x3818
%define E1K_RFCTL           0x5008
%define E1K_MTA             0x5200      ; 128 dwords
%define E1K_RAL0            0x5400
%define E1K_RAH0            0x5404
%define E1K_MRQC            0x5818
%define CTRL_SLU            (1 << 6)
%define CTRL_ILOS           (1 << 7)
%define CTRL_FRCSPD         (1 << 11)
%define CTRL_FRCDPX         (1 << 12)
%define CTRL_RST            (1 << 26)
%define CTRL_PHY_RST        (1 << 31)
%define CTRL_LINK_KEEP      ((~(CTRL_FRCSPD | CTRL_FRCDPX | CTRL_ILOS | CTRL_PHY_RST)) & 0xFFFFFFFF)
%define STATUS_LU           (1 << 1)
%define RAH_AV              (1 << 31)
%define RCTL_EN             (1 << 1)
%define RCTL_BAM            (1 << 15)
%define RCTL_SECRC          (1 << 26)   ; BSIZE 00 and BSEX 0: 2048-byte buffers; LPE clear
%define RFCTL_EXSTEN        (1 << 15)
%define TCTL_EN             (1 << 1)
%define TCTL_PSP            (1 << 3)
%define TCTL_CT             (0x0F << 4)
%define TCTL_COLD           (0x3F << 12)
%define E1K_TIPG_COPPER     0x00602008  ; IPGT 8, IPGR1 8, IPGR2 6 - the reset default, written anyway
%define E1K_DESC            16
%define E1K_RX_DESCS        16          ; NIC_RX_BUFS
%define E1K_TX_DESCS        8           ; the smallest ring, 128 bytes
%define RXD_LEN             8           ; u16
%define RXD_STATUS          12          ; u8: DD bit 0, EOP bit 1
%define RXD_ERRORS          13          ; u8: non-zero, the frame is recycled unread (A4)
%define RXD_DD              1
%define RXD_EOP             2
%define TXD_LEN             8           ; u16
%define TXD_CMD             11          ; u8: EOP, IFCS, RS
%define TXD_STA             12          ; u8: DD bit 0
%define TXD_EOP             1
%define TXD_IFCS            2
%define TXD_RS              8
%define TXD_DD              1
%define E1K_RESET_TRIES     5000        ; x 200 us = one second
%define E1K_LINK_TRIES      50000       ; x 200 us = ten seconds (measured at item 1)
%define NIC_VIRTIO          1           ; nic_kind: which driver owns net_send and net_poll
%define NIC_E1000E          2

; The notebook (stage3/NOTEBOOK.md): one note per 512-byte sector, the text
; from offset 12, so a note is at most 500 bytes. The line buffer is capped
; there: what is on screen is exactly what will be on disk.
%define NOTE_MAX            500
%define NB_TEXT_OFF         12

; The home image (stage6/HOME.md, ring 6b): the home partition, from Stage
; 7 (DISK.md). Sector 0 the header, sectors 1-8 the table of sixteen
; 256-byte entries, the builds from sector 9 - every sector relative to
; the partition. The table lives in RAM from boot.
%define HOME_TABLE_FIRST    1
%define HOME_TABLE_SECTORS  8
%define HOME_DATA_FIRST     9
%define HOME_ENTRY          256
%define HOME_ENTRIES        16
%define HE_NAME             0x00        ; 32 bytes, NUL-padded
%define HE_CUR              0x20        ; the current build: size, first, sectors, zero, sha256
%define HE_PREV             0x50        ; the previous build, the same shape
%define HE_CHOICES          0x80        ; the frame's four 13-byte choice slots
%define HE_PAD              0xB4        ; zero to the end of the entry
%define HB_SIZE             0           ; a build's fields, from its start
%define HB_FIRST            4
%define HB_SECTORS          8
%define HB_ZERO             12
%define HB_SHA              16
%define HB_BYTES            0x30

; The component region (stage5/GERMLINE.md, "The component region, and line
; twelve"): 0x100040 bytes of our own BSS, page-aligned. A grow response is
; received straight into it from +28, so the 4-byte length prefix sits at
; +28..+31, the kind byte and header at +32..+63, and the blob - byte 32 of
; the frame's content - at +64, 64-aligned; the largest legal frame (4 + 32
; + 1 MB) ends exactly at +0x100040. Measured before planning: a blob
; copied here and called returns - our page tables carry no NX bits.
; Ring 6a (GLASS.md, "The wire"): the region grows to 0x100080 so that an
; app frame - a 96-byte header, the blob at byte 100 of the frame - received
; at +28 puts the blob at +128, 64-aligned, and the largest legal frame
; (4 + 96 + 1 MB) ends exactly at +0x100080. Line thirteen prints +128.
%define COMP_REGION_SIZE    0x100080
%define COMP_RX_OFF         28          ; where the response stream begins
%define COMP_BLOB_OFF       64          ; a Stage 5 component's first byte (kind 0x01; retired at item 13)
%define COMP_HDR            32          ; a Stage 5 component's header (retired at item 13)
%define APP_HDR             96          ; an app frame's kind byte and the 95 after it
%define APP_BLOB_OFF        128         ; where an app's first byte lives
%define COMP_BLOB_MAX       0x100000    ; the cap, 1048576 bytes
%define COMP_RX_MAX         (4 + APP_HDR + COMP_BLOB_MAX)

; The display's EDID (GLASS.md, "The screen"): 128 bytes read from the VGA
; device's BAR2, the preferred mode from the first detailed timing
; descriptor at byte 54.
%define EDID_QEMU_VGA       0x11111234  ; device 0x1111 : vendor 0x1234 - the one display whose BAR2 is an EDID
%define EDID_BYTES          128
%define EDID_DTD1           54

; The obs page (GLASS.md, "The obs page"): one page of u64 fields, each
; written by the thing doing the work and read by the glass core, the twin
; and the harness (through the monitor's xp). Line fourteen says where.
%define OBS_MAGIC           0x00
%define OBS_TSC_PER_MS      0x08
%define OBS_TSC_BOOT        0x10
%define OBS_MODE            0x18
%define OBS_GLASS_APIC      0x20
%define OBS_FRAMES          0x28
%define OBS_FRAME_LAST      0x30
%define OBS_FRAME_WORST     0x38
%define OBS_PHOTON_LAST     0x40
%define OBS_PHOTON_WORST    0x48
%define OBS_KEYS            0x50
%define OBS_KEYS_HW         0x58
%define OBS_ERRORS          0x60
%define OBS_QUESTIONS       0x68
%define OBS_REQUESTS        0x70
%define OBS_NOTES           0x78
%define OBS_DISK_REQS       0x80
%define OBS_DISK_WAIT       0x88
%define OBS_WIRE_CONNS      0x90
%define OBS_BYTES_IN        0x98
%define OBS_BYTES_OUT       0xA0
%define OBS_WIRE_WAIT       0xA8
%define OBS_GROWS_GEN       0xB0
%define OBS_GROWS_SERVED    0xB8
%define OBS_STEPS           0xC0
%define OBS_STEP_LAST       0xC8
%define OBS_STEP_WORST      0xD0
%define OBS_TT_LAST         0xD8
%define OBS_TT_WORST        0xE0
%define OBS_FOCUS           0xE8
%define OBS_COLS            0xF0
%define OBS_ROWS            0xF8
%define OBS_NAME            0x100
%define OBS_ECHO_STAMP      0x120
%define OBS_ECHO_PENDING    0x128
%define OBS_NOW             0x130
%define OBS_SURF_STRIP      0x140
%define OBS_SURF_CHOICES    0x180
%define OBS_SURF_CONV       0x1C0
%define OBS_SURF_APP        0x200
; Ring 6c (GLASS.md, "The obs page, from 0x240"): the pointer's fields.
%define OBS_PTR_X           0x240
%define OBS_PTR_Y           0x248
%define OBS_PTR_CELL        0x250
%define OBS_PACKETS         0x258
%define OBS_BUTTONS         0x260
%define OBS_MOUSE_HW        0x268
%define OBS_PTR_STAMP       0x270
%define OBS_PTR_PENDING     0x278
%define OBS_POINTER_LAST    0x280
%define OBS_POINTER_WORST   0x288
%define OBS_CLICKS          0x290
%define OBS_HITS            0x298
%define OBS_MOUSE_BYTES     0x2A0
%define OBS_RESYNCS         0x2A8
%define OBS_MOUSE_ID        0x2B0
%define OBS_I8042_CMD       0x2B8
%define OBS_AHCI_CAP        0x2C0       ; DISK.md: the HBA's CAP, PI, the chosen port
%define OBS_AHCI_PI         0x2C8
%define OBS_AHCI_PORT       0x2D0
%define SURF_CELLS          0
%define SURF_DIRTY          8
%define SURF_ROW0           16
%define SURF_COL0           24
%define SURF_ROWS           32
%define SURF_COLS           40
%define SURF_CURSOR         48
%define MODE_PROMPT         0
%define MODE_ASKING         1
%define MODE_GROWING        2
%define MODE_RUNNING        3
%define MODE_INSTALLING     4           ; ring 6b: a request that begins "install"

; The surfaces (GLASS.md, "Surfaces and the glass core"): cell buffers and
; a dirty byte per row. Capacities are for any mode we can run; the sizes
; used are measured from the mode at boot.
%define SURF_ROWS_MAX       256
%define STRIP_CELLS         0x400       ; 2 rows of up to 512 columns
%define PANEL_CELLS         0x10000     ; the conversation's SHADOW_SIZE, and the app's
%define STRIP_LEN           87          ; each strip row's text
%define CELL_BLOCK          0x01        ; a solid foreground block
%define FRAME_HZ            60

; ABI 2 (GLASS.md, "An app is four callbacks", "The wire"): the frame's
; header fields, the blob's offset table, the step pacing.
%define APP_KIND            2
%define APP_ABI             2
%define APPH_ABI            1           ; header offsets, from the kind byte
%define APPH_SOURCE         2
%define APPH_LEN            4
%define APPH_NAME           8
%define APPH_INSTALLED      40
%define APPH_CHOICES        44
%define APP_NAME_MAX        32
%define APP_CHOICES         4
%define APP_CHOICE_BYTES    13
%define APP_LABEL_MAX       12
%define APP_CHOICES_SHOWN   3
%define BLOB_HDR            16          ; four u32 offsets: init, step, key, exit
%define CB_INIT             0
%define CB_STEP             4
%define CB_KEY              8
%define CB_EXIT             12
%define CB_POINT            24          ; ring 6c: the fifth offset, after the magic
%define POINT_HDR           28          ; the five-callback header's length
%define POINT_MAGIC_OFF     16          ; the eight bytes POINTER2
%define STEP_GAP_MS         10
%define FOCUS_PROMPT        0
%define FOCUS_APP           1

; The strip's field offsets, computed from GLASS.md's format strings.
%define STRIP0_UP     3
%define STRIP0_CORE   15
%define STRIP0_FR     21
%define STRIP0_FL     28
%define STRIP0_FW     33
%define STRIP0_PL     41
%define STRIP0_PW     46
%define STRIP0_K      53
%define STRIP0_HW     61
%define STRIP0_ERR    69
%define STRIP0_SL     78
%define STRIP0_SW     83
%define STRIP1_MODE   0
%define STRIP1_Q      21
%define STRIP1_N      27
%define STRIP1_GG     33
%define STRIP1_GS     37
%define STRIP1_DR     46
%define STRIP1_DW     51
%define STRIP1_WC     60
%define STRIP1_WW     64
%define STRIP1_IN     74
%define STRIP1_OUT    81
; Ring 6c: the strip's third field, row 0 from column 88, only once the
; mouse has spoken (GLASS.md, "Pointer input-to-photon, and the strip's
; third field"). Column 87 stays blank.
%define STRIP0_PT     91                ; pt LL.L
%define STRIP0_PTW    96                ; /WW.W
%define STRIP0_PK     104               ; pk NNNN
%define STRIP0_CL     112               ; cl NNN
%define STRIP_PT_LEN  28                ; " pt 00.0/00.0 pk 0000 cl 000"

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
        ; Still interrupts off, polled; a missing mouse costs a moment.
        call    mouse_init

.drain:                                 ; stale bytes in the output buffer
        in      al, 0x64                ; would fire the moment we sti
        test    al, 1
        jz      .drained
        in      al, 0x60
        jmp     .drain
.drained:

        lea     rsi, [msg_kbd]          ; line thirteen; after this the channel
        call    serial_puts             ; carries only the raw echo

        ; The machine's memory, drawn on the console - and only the console -
        ; immediately above the first prompt (plan decisions 2 and 3).
        call    notebook_replay
        call    console_prompt

        ; -------------------------------------------------------------------
        ; The main loop - the screen's one owner. The interrupt handler only
        ; buffers scancodes; every glyph is drawn here.
        ;
        ; Amendment A1: never hlt while the ring holds data. With interrupts
        ; off, look at the ring; only if it is empty, sti and hlt back to
        ; back - the sti shadow carries a pending interrupt into the hlt's
        ; wake instead of letting it fire uselessly before the hlt sleeps.
        ; -------------------------------------------------------------------
main_loop:
        ; The eighteenth line (GLASS.md): once, serial only, the first time
        ; the mouse's packet counter is above zero.
        cmp     dword [mouse_announced], 0
        jne     .announced
        cmp     qword [obs_page + OBS_PACKETS], 0
        je      .announced
        mov     dword [mouse_announced], 1
        lea     rsi, [msg_mouse]
        call    serial_raw_puts
.announced:
        cli
        mov     eax, [kbd_tail]
        cmp     eax, [kbd_head]
        jne     .have
        mov     eax, [mse_tail]
        cmp     eax, [mse_head]
        jne     .have_mouse
        cmp     dword [app_running], 0
        jne     .app_turn               ; an app never lets the loop sleep
        sti                             ; the shadow: no interrupt lands
        hlt                             ; between these two instructions
        jmp     main_loop
.have_mouse:
        sti
        call    mouse_next              ; one packet out of the ring
        test    al, al
        jz      main_loop
        call    click_dispatch          ; its presses, if any (ring 6c)
        jmp     main_loop
.app_turn:
        sti
        call    app_step_maybe          ; its step, if 10 ms have passed
        pause
        jmp     main_loop
.have:
        sti
        call    kbd_next                ; AL = the next translated key, or 0
        test    al, al
        jz      main_loop
        movzx   ebx, al
        call    handle_key
        jmp     main_loop

; handle_key - EBX = one translated key: a printable with Shift applied, 13
; Enter, 8 Backspace, 9 Tab, 0x1B Esc. Ring 6a's main-loop body, lifted out
; so that a click's synthetic keys take the identical path a typed key
; takes (ring 6c, plan decision 7): the tee, the journal, the parse, the
; app. Returns when the key has been acted on. Clobbers registers freely.
handle_key:
        ; With an app running (GLASS.md, "Running an app"): Esc closes it
        ; whoever has the keys; Tab moves the keys; with the app in focus
        ; every other key is the app's; with the prompt in focus the key
        ; takes the prompt's path below.
        cmp     dword [app_running], 0
        je      .prompt_key
        cmp     bl, 0x1B
        je      .app_close
        cmp     bl, 9
        je      .toggle_focus
        cmp     qword [obs_page + OBS_FOCUS], FOCUS_APP
        jne     .prompt_key
        mov     edi, ebx
        call    app_key
        call    photon_mark
        ret
.app_close:
        call    app_close
        call    photon_mark
        ret
.toggle_focus:
        xor     qword [obs_page + OBS_FOCUS], 1
        call    choices_update
        call    photon_mark
        ret

.prompt_key:
        cmp     bl, 13
        je      .enter
        cmp     bl, 8
        je      .backspace
        cmp     bl, 0x1B                ; Esc at the prompt does nothing - it
        je      .done                   ; is an app's way home, not ours
        cmp     bl, 9                   ; Tab with no app: nothing
        je      .done

        ; A printable: into the line buffer if there is room (a key beyond
        ; the cap is ignored - not echoed, not drawn - so the screen and the
        ; disk always agree), one byte to the wire, and the tee draws the
        ; glyph over the cursor cell; the cursor moves on behind it.
        mov     eax, [line_len]
        cmp     eax, NOTE_MAX
        jae     .done
        lea     rdx, [line_buf]
        mov     [rdx + rax], bl
        inc     dword [line_len]
        mov     al, bl
        call    serial_putc
        call    draw_cursor
        call    photon_mark
        ret
.enter:
        call    erase_cursor            ; the block would linger at line end
        mov     rax, [key_stamp]        ; time-to-done starts here (obs tt)
        mov     [enter_stamp], rax
        mov     al, 13                  ; Enter echoes CRLF...
        call    serial_putc
        mov     al, 10
        call    serial_putc
        call    photon_mark             ; the new line IS Enter's echo: the
                                        ; photon is stamped here, never after a
                                        ; wait that has its own counter (w, tt)
        ; The forgiving marker parse (GERMLINE.md, "What is a question, what
        ; is a request"): leading spaces skipped, "?" asks, "!" requests,
        ; anything else is a note on Stage 3's path. Nothing after this
        ; reaches the wire.
        call    parse_marker            ; EAX = 0, '?' or '!'; RSI, ECX = the body
        cmp     eax, '?'
        je      .question
        cmp     eax, '!'
        je      .request
        call    notebook_append         ; ...the line goes to disk, and only
        call    console_prompt          ; then a new prompt, console-only
        ret
.question:
        call    ask_question            ; console-only, then the prompt
        ret
.request:
        call    bang_line               ; undo, a launch, or the broker; then the prompt
        ret
.backspace:
        mov     eax, [cur_col]          ; only within this line's typed text -
        cmp     eax, [prompt_min]       ; at the prompt there is nothing to
        jbe     .done                   ; erase, so the key is not accepted
        cmp     dword [line_len], 0     ; the buffer follows the screen
        je      .bs_draw
        dec     dword [line_len]
.bs_draw:
        call    erase_cursor
        mov     al, 8
        call    serial_putc             ; the tee steps back and erases
        call    draw_cursor
        call    photon_mark
.done:
        ret

; click_dispatch - mse_cur holds the packet mouse_next popped. Every button
; newly pressed counts one click; a left press on the choices row within an
; item's text is a hit and does what the item's key does, through
; handle_key, with the press's stamp as the key's stamp (GLASS.md, "The
; click on the choices row"); a launch item acts only on an empty prompt
; line (A3). A press in the app panel while an app runs is item 12's.
; Clobbers registers freely.
click_dispatch:
        movzx   eax, byte [mse_cur + ME_PRESSED]
        test    al, al
        jz      .ret
        mov     ecx, eax
.count:                                 ; each pressed bit is one click
        test    cl, 1
        jz      .counted
        inc     qword [obs_page + OBS_CLICKS]
.counted:
        shr     ecx, 1
        jnz     .count
        mov     rdx, [mse_cur + ME_STAMP]
        mov     [key_stamp], rdx
        mov     edx, [mse_cur + ME_CELL]
        mov     ebx, edx
        shr     ebx, 16                 ; the row
        movzx   ecx, dx                 ; the column
        mov     edx, [scr_rows]
        sub     edx, 2
        cmp     ebx, edx                ; the choices row, R-2 ...
        je      .row
        inc     edx
        cmp     ebx, edx                ; ... or its margin, R-1: a press there is
        jne     .not_row                ; judged by its column as one on R-2
.row:                                   ; (item 12c - Fitts: the edge hits the target)
        test    al, 1                   ; button 1 clicks the row
        jz      .ret
        call    choices_hit             ; EAX = kind or 0, EDX = the argument
        test    eax, eax
        jz      .ret
        cmp     eax, HIT_LAUNCH
        je      .launch
        inc     qword [obs_page + OBS_HITS]
        mov     ebx, edx                ; the item's key, as if typed
        call    handle_key
        ret
.launch:
        cmp     dword [line_len], 0     ; only on an empty prompt line
        jne     .ret
        inc     qword [obs_page + OBS_HITS]
        mov     r12d, edx               ; the home entry's index
        mov     ebx, '!'
        call    handle_key
        mov     ebx, ' '
        call    handle_key
        lea     r13, [home_table]
        mov     eax, r12d
        shl     eax, 8
        add     r13, rax
        mov     r14d, APP_NAME_MAX
.name:
        movzx   ebx, byte [r13]
        test    ebx, ebx
        jz      .named
        call    handle_key
        inc     r13
        dec     r14d
        jnz     .name
.named:
        mov     ebx, 13
        call    handle_key
        ret
.not_row:
        call    click_panel             ; item 12: point, for an app that has it
.ret:
        ret

; click_panel - EBX = the row, ECX = the column, AL = the pressed bits: a
; press in the app panel while an app runs calls point(row, col, button)
; for each button newly pressed - 1 left, 2 right, 3 middle - with the row
; and column relative to the panel, when the app announces point; a
; four-callback app is clicked on without effect (GLASS.md, "An app is
; five callbacks, when it says so"). Clobbers registers freely.
click_panel:
        cmp     dword [app_running], 0
        je      .ret
        cmp     dword [app_has_point], 0
        je      .ret
        mov     edx, ebx
        sub     edx, 2                  ; the panel begins at screen row 2
        js      .ret
        cmp     edx, [app_rows]
        jae     .ret
        mov     esi, ecx
        sub     esi, [con_cols]         ; and at the conversation's right edge
        js      .ret
        cmp     esi, [app_cols]
        jae     .ret
        mov     r12d, edx               ; the panel row
        mov     r13d, esi               ; the panel column
        mov     r14d, eax               ; the pressed bits
        mov     r15d, 1                 ; the button number
.button:
        test    r14d, 1
        jz      .next
        inc     qword [obs_page + OBS_HITS]
        mov     edi, r12d
        mov     esi, r13d
        mov     edx, r15d
        mov     eax, CB_POINT
        ; Nothing survives a call into grown code but memory and the stack
        ; (GLASS.md: an app may clobber every register but RSP; app_call
        ; restores RSP from saved_rsp, so what is pushed here is still here
        ; after). The loop's state rides the stack, whatever a fixture
        ; happens to preserve (Cowork's pre-oracle review, item 12b).
        push    r12
        push    r13
        push    r14
        push    r15
        call    app_call
        pop     r15
        pop     r14
        pop     r13
        pop     r12
.next:
        shr     r14d, 1
        inc     r15d
        cmp     r15d, 3
        jbe     .button
.ret:
        ret

; choices_hit - ECX = a column of row R-2: EAX = the item's kind (HIT_KEY or
; HIT_LAUNCH) with EDX = its argument, or EAX = 0 for a gap or the tail.
; Clobbers RSI, R8.
choices_hit:
        mov     r8d, [hit_count]
        lea     rsi, [hit_table]
.item:
        test    r8d, r8d
        jz      .miss
        movzx   eax, word [rsi + HT_FIRST]
        cmp     ecx, eax
        jb      .next
        movzx   eax, word [rsi + HT_LAST]
        cmp     ecx, eax
        ja      .next
        movzx   eax, byte [rsi + HT_KIND]
        movzx   edx, byte [rsi + HT_ARG]
        ret
.next:
        add     rsi, HIT_ENTRY
        dec     r8d
        jmp     .item
.miss:
        xor     eax, eax
        ret

; hit_reset - an empty table; hit_add - EAX = first column, EDX = last
; column, CL = kind, CH = argument: one more entry. Preserve everything.
hit_reset:
        mov     dword [hit_count], 0
        ret
hit_add:
        push    rsi
        push    rax
        cmp     dword [hit_count], HIT_MAX
        jae     .full
        lea     rsi, [hit_table]
        push    rax
        mov     eax, [hit_count]
        shl     eax, 3
        add     rsi, rax
        pop     rax
        mov     [rsi + HT_FIRST], ax
        mov     [rsi + HT_LAST], dx
        mov     [rsi + HT_KIND], cl
        mov     [rsi + HT_ARG], ch
        inc     dword [hit_count]
.full:
        pop     rax
        pop     rsi
        ret

; photon_mark - a key has been acted on (GLASS.md, "Input-to-photon"): its
; stamp becomes the pending echo unless one is already pending, so the
; glass core credits the frame that paints it. Preserves everything.
photon_mark:
        push    rax
        cmp     qword [obs_page + OBS_ECHO_PENDING], 0
        jne     .pending
        mov     rax, [key_stamp]
        mov     [obs_page + OBS_ECHO_STAMP], rax
        mov     qword [obs_page + OBS_ECHO_PENDING], 1
.pending:
        pop     rax
        ret

; kbd_next - the keyboard's consumer, factored out of the main loop (plan
; decision 8) so a running component's poll_key sees exactly what the prompt
; would: pops scancodes from the ring until one translates, and returns it
; in AL - a printable with Shift applied, 13 Enter, 8 Backspace, 0x1B Esc -
; or 0 with the ring empty. The handler still only buffers; this is the one
; consumer, on the BSP. Preserves everything but RAX.
kbd_next:
        push    rbx
        push    rdx
.again:
        mov     eax, [kbd_tail]
        cmp     eax, [kbd_head]
        je      .none
        lea     rdx, [kbd_ring]         ; pop one scancode
        movzx   ebx, byte [rdx + rax]
        lea     rdx, [kbd_stamps]       ; and its stamp: the last one popped
        mov     rdx, [rdx + rax*8]      ; before a key translates is the key's
        mov     [key_stamp], rdx
        inc     eax
        and     eax, KBD_RING_SIZE - 1
        mov     [kbd_tail], eax

        ; An 0xE0 prefix marks an extended key; the byte after it would
        ; otherwise read as an ordinary make code (E0 53, keypad Delete,
        ; would print '.'), so the prefix swallows its successor.
        cmp     dword [kbd_e0], 0
        je      .no_pending
        mov     dword [kbd_e0], 0
        jmp     .again
.no_pending:
        cmp     bl, 0xE0
        jne     .not_e0
        mov     dword [kbd_e0], 1
        jmp     .again
.not_e0:
        ; Shift is a state, not a key: both Shift keys' make and break codes
        ; set and clear it, and select which table translates what follows.
        ; (E0 2A, the fake shift around some extended keys, is already
        ; swallowed by the prefix rule above.)
        cmp     bl, 0x2A                ; LShift make
        je      .shift_down
        cmp     bl, 0x36                ; RShift make
        je      .shift_down
        cmp     bl, 0xAA                ; LShift break
        je      .shift_up
        cmp     bl, 0xB6                ; RShift break
        je      .shift_up
        test    bl, 0x80                ; other break codes: ignored
        jnz     .again

        lea     rdx, [scan1_map]        ; set 1, US, unshifted...
        cmp     dword [kbd_shift], 0
        je      .translate
        lea     rdx, [scan1_shift_map]  ; ...or shifted
.translate:
        movzx   eax, byte [rdx + rbx]
        test    al, al
        jz      .again                  ; not a key this stage listens to
        inc     qword [obs_page + OBS_KEYS]
        pop     rdx
        pop     rbx
        ret
.shift_down:
        mov     dword [kbd_shift], 1
        jmp     .again
.shift_up:
        mov     dword [kbd_shift], 0
        jmp     .again
.none:
        xor     eax, eax
        pop     rdx
        pop     rbx
        ret

; tsc_calibrate - count time-stamp ticks across one PIT wait of 10 ms, and
; keep the rate per millisecond and the reading at boot. A rate of zero (a
; TSC that does not run, in some future twin) is clamped to one so that a
; division can never fault. Clobbers RAX, RBX, RDX.
tsc_calibrate:
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     [tsc_boot], rax
        mov     rbx, rax
        mov     ax, PIT_10MS
        call    pit_wait
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        sub     rax, rbx
        xor     edx, edx
        mov     ebx, 10
        div     rbx                     ; ticks per millisecond
        test    rax, rax
        jnz     .keep
        mov     eax, 1
.keep:
        mov     [tsc_per_ms], rax
        ret

; ticks_ms - RAX = milliseconds since boot, from the calibrated TSC.
; Clobbers RDX. The service table's fourth entry calls straight here.
ticks_ms:
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        sub     rax, [tsc_boot]
        xor     edx, edx
        div     qword [tsc_per_ms]
        ret

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
; The PIC and the keyboard interrupt.
;
; Both PICs are remapped - the master to 0x20-0x27, the slave to 0x28-0x2F:
; left at the reset default of 0x08, a spurious or stray IRQ would land on a
; CPU exception vector and read as a double fault. Every line is masked
; except IRQ1, the cascade IRQ2 and IRQ12 - the keyboard and the mouse, both
; on the i8042 (ring 6c). The timer stays masked; nothing in this stage
; wants it.
; ---------------------------------------------------------------------------

; pic_init - the classic two-chip initialisation, with a POST-port breather
; between writes for old silicon's sake (QEMU does not need it; Stage 7 might).
pic_init:
        push    rax
        mov     al, 0x11                ; ICW1: initialise, ICW4 to follow
        out     0x20, al
        out     0x80, al
        out     0xA0, al
        out     0x80, al
        mov     al, 0x20                ; ICW2 master: vectors 0x20-0x27
        out     0x21, al
        out     0x80, al
        mov     al, 0x28                ; ICW2 slave: vectors 0x28-0x2F
        out     0xA1, al
        out     0x80, al
        mov     al, 0x04                ; ICW3 master: a slave hangs off IRQ2
        out     0x21, al
        out     0x80, al
        mov     al, 0x02                ; ICW3 slave: cascade identity 2
        out     0xA1, al
        out     0x80, al
        mov     al, 0x01                ; ICW4: 8086 mode
        out     0x21, al
        out     0x80, al
        out     0xA1, al
        out     0x80, al
        mov     al, 0xF9                ; OCW1 master: IRQ1 and the cascade IRQ2 open
        out     0x21, al
        mov     al, 0xEF                ; OCW1 slave: IRQ12 open (ring 6c)
        out     0xA1, al
        pop     rax
        ret

; The i8042 interrupts (ring 6c, GLASS.md "The device"): IRQ1 and IRQ12
; enter one body, i8042_service, which reads the status byte first and,
; while the output buffer is full, takes one byte and routes it by status
; bit 5 - clear, the keyboard's ring; set, the mouse's packet machine. A
; handler that finds the buffer empty (the other vector's drain took its
; byte) does nothing but EOI. The handlers own nothing but the rings'
; heads; the main loop and the glass core own everything else.
irq1_entry:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        push    rsi
        push    rdi
        push    r8
        call    i8042_service
        mov     al, 0x20                ; EOI to the master; IRQ1 is its line
        out     0x20, al
        pop     r8
        pop     rdi
        pop     rsi
        pop     rdx
        pop     rcx
        pop     rbx
        pop     rax
        iretq

irq12_entry:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        push    rsi
        push    rdi
        push    r8
        call    i8042_service
        mov     al, 0x20                ; EOI to the slave, then the master
        out     0xA0, al
        out     0x20, al
        pop     r8
        pop     rdi
        pop     rsi
        pop     rdx
        pop     rcx
        pop     rbx
        pop     rax
        iretq

i8042_service:
.next:
        in      al, 0x64
        test    al, 1                   ; output buffer full?
        jz      .done
        mov     bl, al                  ; the status byte
        in      al, 0x60                ; reading the byte is the acknowledge
        test    bl, 0x20                ; bit 5: the byte is the mouse's
        jnz     .mouse
        call    kbd_push
        jmp     .next
.mouse:
        call    mouse_byte
        jmp     .next
.done:
        ret

; kbd_push - AL = a scancode: into the keyboard ring with its stamp, the
; ring's high-water kept. Ring 6a's IRQ1 body, unchanged but for its name.
; Single producer, single consumer, one writer per index - no lock.
kbd_push:
        mov     ebx, [kbd_head]
        mov     edx, ebx
        inc     edx
        and     edx, KBD_RING_SIZE - 1
        cmp     edx, [kbd_tail]         ; ring full: drop the byte rather than
        je      .done                   ; overwrite what the loop has not read
        lea     rdx, [kbd_ring]
        mov     [rdx + rbx], al
        ; The stamp beside the scancode (GLASS.md, "Input-to-photon"): the
        ; TSC the moment the key arrived, kept in a ring of its own with the
        ; same index, so the consumer can hand it on with the key.
        mov     ecx, ebx
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        lea     rdx, [kbd_stamps]
        mov     [rdx + rcx*8], rax
        mov     ebx, [kbd_head]
        inc     ebx
        and     ebx, KBD_RING_SIZE - 1
        mov     [kbd_head], ebx
        sub     ebx, [kbd_tail]         ; the ring's occupancy now ...
        and     ebx, KBD_RING_SIZE - 1
        cmp     rbx, [obs_page + OBS_KEYS_HW]
        jbe     .done                   ; ... and its high-water mark
        mov     [obs_page + OBS_KEYS_HW], rbx
.done:
        ret

; mouse_byte - AL = a byte from the mouse: the three-byte packet machine
; (GLASS.md, "The packet"). Phase 0 wants bit 3 set - a byte without it is
; dropped and counted in resyncs - and records the packet's stamp; the third
; byte completes the packet: the deltas applied to the position, clamped to
; the mode, the cell word stored last as one u64, the buttons and the
; presses, one packet counted, the stamp made pending if none is, and one
; entry into the mouse ring. Runs in the handler, so the cursor is live
; whatever the boot processor is doing.
mouse_byte:
        inc     qword [obs_page + OBS_MOUSE_BYTES]
        mov     ecx, [mse_phase]
        test    ecx, ecx
        jnz     .later
        test    al, 0x08                ; byte 0 always has bit 3 set
        jnz     .first
        inc     qword [obs_page + OBS_RESYNCS]
        ret
.first:
        mov     [mse_pkt], al
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     [mse_stamp0], rax
        mov     dword [mse_phase], 1
        ret
.later:
        lea     rdx, [mse_pkt]          ; lea first: [label + reg] cannot be
        mov     [rdx + rcx], al         ; RIP-relative (CLAUDE.md)
        inc     ecx
        mov     [mse_phase], ecx
        cmp     ecx, 3
        jb      .ret
        mov     dword [mse_phase], 0

        ; dx: byte 1 as a signed byte; x clamped to the console's cells,
        ; 0 .. 16C-1 - not the mode: a mode is not a whole number of cells,
        ; and a cell word naming a column the console lacks would draw past
        ; the screen and leave ghosts (item 12c, the oracle's finding).
        movsx   rax, byte [mse_pkt + 1]
        mov     rcx, [obs_page + OBS_PTR_X]
        add     rcx, rax
        test    rcx, rcx
        jns     .x_low_ok
        xor     ecx, ecx
.x_low_ok:
        mov     eax, [scr_cols]
        shl     eax, 4
        dec     eax
        cmp     rcx, rax
        jbe     .x_ok
        mov     rcx, rax
.x_ok:
        mov     [obs_page + OBS_PTR_X], rcx
        ; dy: byte 2 as a signed byte, positive upwards; y clamped to 0 .. 16R-1.
        movsx   rax, byte [mse_pkt + 2]
        mov     rdx, [obs_page + OBS_PTR_Y]
        sub     rdx, rax
        test    rdx, rdx
        jns     .y_low_ok
        xor     edx, edx
.y_low_ok:
        mov     eax, [scr_rows]
        shl     eax, 4
        dec     eax
        cmp     rdx, rax
        jbe     .y_ok
        mov     rdx, rax
.y_ok:
        mov     [obs_page + OBS_PTR_Y], rdx
        ; The cell word, stored after both positions: the glass reads only it.
        shr     rdx, 4
        shl     rdx, 16
        shr     rcx, 4
        or      rdx, rcx
        mov     [obs_page + OBS_PTR_CELL], rdx
        mov     r8d, edx                ; the cell, for the ring entry

        ; The buttons held, and the presses: bits set now that were clear.
        movzx   eax, byte [mse_pkt]
        and     eax, 7
        mov     ecx, [mse_prev]
        mov     [mse_prev], eax
        mov     [obs_page + OBS_BUTTONS], rax
        not     ecx
        and     ecx, eax                ; CL = pressed
        inc     qword [obs_page + OBS_PACKETS]

        ; The stamp awaiting its frame: the first byte's, unless one is pending.
        cmp     qword [obs_page + OBS_PTR_PENDING], 0
        jne     .pending
        mov     rdx, [mse_stamp0]
        mov     [obs_page + OBS_PTR_STAMP], rdx
        mov     qword [obs_page + OBS_PTR_PENDING], 1
.pending:
        ; The ring entry: dropped when full, the high-water kept.
        mov     ebx, [mse_head]
        mov     edx, ebx
        inc     edx
        and     edx, MSE_RING_SIZE - 1
        cmp     edx, [mse_tail]
        je      .ret
        shl     ebx, 4                  ; * MSE_ENTRY
        lea     rsi, [mse_ring]
        add     rsi, rbx
        mov     rbx, [mse_stamp0]
        mov     [rsi + ME_STAMP], rbx
        mov     [rsi + ME_CELL], r8d
        mov     [rsi + ME_BUTTONS], al
        mov     [rsi + ME_PRESSED], cl
        mov     word [rsi + ME_PRESSED + 1], 0
        mov     [mse_head], edx
        sub     edx, [mse_tail]
        and     edx, MSE_RING_SIZE - 1
        cmp     rdx, [obs_page + OBS_MOUSE_HW]
        jbe     .ret
        mov     [obs_page + OBS_MOUSE_HW], rdx
.ret:
        ret

; mouse_next - the boot processor's consumer: pops one entry of the mouse
; ring into mse_cur and returns AL = 1, or AL = 0 with the ring empty.
; Preserves everything but RAX.
mouse_next:
        push    rsi
        push    rdi
        push    rcx
        mov     eax, [mse_tail]
        cmp     eax, [mse_head]
        je      .none
        mov     ecx, eax
        shl     ecx, 4
        lea     rsi, [mse_ring]
        add     rsi, rcx
        lea     rdi, [mse_cur]
        mov     ecx, MSE_ENTRY
        rep     movsb
        inc     eax
        and     eax, MSE_RING_SIZE - 1
        mov     [mse_tail], eax
        mov     eax, 1
        jmp     .out
.none:
        xor     eax, eax
.out:
        pop     rcx
        pop     rdi
        pop     rsi
        ret

; irq7_spurious - a spurious IRQ7 gets no EOI: the PIC does not consider it
; in service. Only IRQ1 and the cascade are unmasked on the master, so a
; real IRQ7 cannot occur.
irq7_spurious:
        iretq

; irq15_spurious - a spurious IRQ15 on the slave: the cascade was real, so
; the master gets its EOI and the slave none.
irq15_spurious:
        push    rax
        mov     al, 0x20
        out     0x20, al
        pop     rax
        iretq

; ---------------------------------------------------------------------------
; The i8042 configured cold, and the mouse (ring 6c, GLASS.md "The device";
; ring 7c, the cold init - stage7/spec.md). All of it polled with
; interrupts off at boot, before the ready line. Every wait is bounded and
; every failure named: the controller's - a self-test not answered by 0x55,
; a command byte not answered, an input buffer that never empties - is an
; ERR: line and a halt; the mouse's - no ACK, no 0xAA, no ID - is the line
; "i8042: mouse none" and the boot goes on, a keyboard-only machine being a
; machine. The two lines carry their own prefix so no S7: count moves.
; ---------------------------------------------------------------------------

; i8042_wait_ibf - spin until the input buffer is empty (bounded); a
; controller that never empties it is a named halt.
i8042_wait_ibf:
        push    rax
        push    rcx
        mov     ecx, 0x10000
.w:     in      al, 0x64
        test    al, 2
        jz      .ok
        dec     ecx
        jnz     .w
        lea     rsi, [err_i8042_ibf]
        call    serial_err
.ok:    pop     rcx
        pop     rax
        ret

; i8042_cmd - AL = a controller command, to port 0x64.
i8042_cmd:
        call    i8042_wait_ibf
        out     0x64, al
        ret

; i8042_data - AL = a byte for the controller or the device it addresses.
i8042_data:
        call    i8042_wait_ibf
        out     0x60, al
        ret

; i8042_read - one byte from the output buffer, waited for up to
; I8042_WAIT_TRIES x 10 ms: AL = the byte, AH = the status byte it came
; with, CF clear; or CF set on a timeout. Clobbers RCX.
i8042_read:
        mov     ecx, I8042_WAIT_TRIES
.poll:
        in      al, 0x64
        test    al, 1
        jnz     .got
        mov     ax, PIT_10MS
        call    pit_wait
        dec     ecx
        jnz     .poll
        stc
        ret
.got:
        mov     ah, al
        in      al, 0x60
        clc
        ret

; i8042_read_mouse - as i8042_read, but a byte the keyboard sent meanwhile
; (status bit 5 clear) is dropped and the wait goes on: only the mouse's
; answer comes back. Clobbers RCX.
i8042_read_mouse:
        call    i8042_read
        jc      .out
        test    ah, 0x20
        jz      i8042_read_mouse
.out:
        ret

; i8042_drain - read and drop whatever the output buffer holds.
i8042_drain:
        in      al, 0x64
        test    al, 1
        jz      .done
        in      al, 0x60
        jmp     i8042_drain
.done:
        ret

; mouse_cmd - AL = a command for the mouse: D4 to 0x64, the byte to 0x60,
; then the mouse's ACK (FA) awaited. CF set on a timeout or anything but
; an ACK. Clobbers RAX, RCX.
mouse_cmd:
        push    rax
        mov     al, 0xD4
        call    i8042_cmd
        pop     rax
        call    i8042_data
        call    i8042_read_mouse
        jc      .out
        cmp     al, 0xFA
        je      .ack
        stc
        ret
.ack:
        clc
.out:
        ret

; mouse_init - the cold init: both ports off, drained; the controller's
; self-test (0xAA, answered 0x55 - or a named halt), both ports off again
; and the buffer drained (the self-test may re-enable them), its line; the
; command byte read AFTER the self-test (which may reset it), bits 0 and 1
; set (both interrupts), 4 and 5 cleared (both ports enabled), the rest
; kept (translation above all), written and read back; the auxiliary port
; enabled; the mouse reset (FA AA and its ID), defaults, reporting enabled,
; and its line - or "i8042: mouse none" and mouse_id 0; drained. The
; pointer starts at the screen's centre. Records i8042_cmd (as read after
; the self-test, as written) and mouse_id in the obs page. Clobbers RAX,
; RCX, RDX, RSI.
mouse_init:
        mov     eax, [fb_width]
        shr     eax, 1
        mov     [obs_page + OBS_PTR_X], rax
        mov     edx, [fb_height]
        shr     edx, 1
        mov     [obs_page + OBS_PTR_Y], rdx
        shr     rdx, 4
        shl     rdx, 16
        shr     rax, 4
        or      rdx, rax
        mov     [obs_page + OBS_PTR_CELL], rdx

        mov     al, 0xAD                ; the keyboard port off
        call    i8042_cmd
        mov     al, 0xA7                ; the auxiliary port off
        call    i8042_cmd
        call    i8042_drain
        mov     al, 0xAA                ; the controller's self-test (ring 7c)
        call    i8042_cmd
        call    i8042_read
        jc      .self_test_failed       ; no answer within the bound
        cmp     al, 0x55
        jne     .self_test_failed       ; an answer that is not "passed"
        ; Ring 7c item 15 (Cowork's pre-oracle review): on some real
        ; controllers the self-test resets the controller and re-enables
        ; both ports, and a device's power-on byte (the keyboard's 0xAA,
        ; the mouse's 0xAA 0x00) can then sit in the output buffer ahead
        ; of the command byte - the 0x20 read below would take a device
        ; byte as the command byte, clear translation and write it back:
        ; a dead keyboard. So both ports off again, and the buffer drained,
        ; before the command byte is read. The twin cannot show the
        ; difference; the rule stands here.
        mov     al, 0xAD                ; the keyboard port off, again
        call    i8042_cmd
        mov     al, 0xA7                ; the auxiliary port off, again
        call    i8042_cmd
        call    i8042_drain
        lea     rsi, [msg_i8042_ok]
        call    serial_puts
        mov     al, 0x20                ; read the command byte - after the
        call    i8042_cmd               ; self-test, which may have reset it
        call    i8042_read
        jc      .no_cmd_byte            ; a controller that passed and then fell silent
        movzx   edx, al                 ; DL = as read
        or      al, 0x03                ; both interrupts on
        and     al, 0xCF                ; both ports enabled
        mov     dh, al                  ; DH = as written
        push    rdx
        push    rax
        mov     al, 0x60                ; write the command byte
        call    i8042_cmd
        pop     rax
        call    i8042_data
        pop     rdx
        mov     [obs_page + OBS_I8042_CMD], rdx
        mov     al, 0x20                ; read it back (GLASS.md: "read back
        call    i8042_cmd               ; with 20") - a confirmation only;
        call    i8042_read              ; i8042_cmd in the page keeps its
                                        ; meaning: as read, as written
        mov     al, 0xA8                ; the auxiliary port enabled
        call    i8042_cmd

        mov     al, 0xFF                ; reset: FA, then AA, then the ID
        call    mouse_cmd
        jc      .no_mouse
        call    i8042_read_mouse
        jc      .no_mouse
        cmp     al, 0xAA
        jne     .no_mouse
        call    i8042_read_mouse
        jc      .no_mouse
        movzx   eax, al
        inc     eax                     ; 1 + the ID byte: 1 for a standard mouse
        mov     [obs_page + OBS_MOUSE_ID], rax
        mov     al, 0xF6                ; defaults
        call    mouse_cmd
        jc      .mouse_lost
        mov     al, 0xF4                ; enable reporting
        call    mouse_cmd
        jc      .mouse_lost
        lea     rsi, [msg_mouse_ok]
        call    serial_puts
.done:
        call    i8042_drain
        ret
.mouse_lost:                            ; answered its reset, then not: the page tells the truth
        mov     qword [obs_page + OBS_MOUSE_ID], 0
.no_mouse:
        lea     rsi, [msg_mouse_none]   ; a line, not an error: the boot goes on
        call    serial_puts
        jmp     .done
.self_test_failed:
        lea     rsi, [err_i8042_self]
        call    serial_err
.no_cmd_byte:
        lea     rsi, [err_i8042_cmd]
        call    serial_err

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
; Virtio on PCI - two devices now (plan decision 9): the disk from Stage 3
; and the NIC that arrives at item 10. Each has a DEVICE BLOCK in BSS (the
; VIO_* offsets at the top of the file) holding its BDF, its four modern
; capability regions, the notify multiplier, and one queue block per
; virtqueue; every routine below takes the block in RBP. Only the BSP ever
; calls any of this: one owner per device.
;
; PCI configuration space is read the plain way, mechanism #1 through ports
; 0xCF8/0xCFC: OVMF leaves ECAM unprogrammed here, and the legacy ports are
; always there for bus 0. The modern capability regions sit wherever the
; firmware put the BARs - on this machine both at 768 GB, the NIC's at
; 0xC000000000 and the disk's at 0xC000004000, above the 4 GB identity map
; and above the first PML4 entry - so they are mapped at runtime, uncached,
; by map_mmio_2m. Nothing is assumed about an address: it is read from the
; BAR the capability names, per device.
; ---------------------------------------------------------------------------

%define PCI_VENDOR_VIRTIO   0x1AF4
%define PCI_DEV_NET_TRANS   0x1000      ; transitional virtio-net
%define PCI_DEV_NET_MODERN  0x1041      ; modern-only virtio-net
%define PCI_CMD_MEMORY      (1 << 1)
%define PCI_CMD_MASTER      (1 << 2)    ; no DMA without it
%define PCI_CMD_INTX_OFF    (1 << 10)   ; we poll; the PIC has only IRQ1 open
%define VIRTIO_PCI_CAP      0x09        ; the vendor-specific capability id
%define VCAP_COMMON         1
%define VCAP_NOTIFY         2
%define VCAP_ISR            3
%define VCAP_DEVICE         4

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

; edid_read - the display's preferred mode (GLASS.md, "The screen"). Scans
; bus 0 for a device of class 0x0300 (display, VGA-compatible), reads the
; 128 bytes at its BAR2 one byte at a time, requires the EDID header and a
; non-zero pixel clock in the first detailed timing descriptor, and takes
; the preferred width and height out of it. Prints line two either way.
; Called before the GOP mode loop, boot services still up (the BAR is
; mapped by the firmware's tables). Clobbers registers freely.
edid_read:
        mov     dword [edid_w], 0
        mov     dword [edid_h], 0
        mov     dword [edid_mode], -1
        xor     esi, esi                ; device number
.dev:
        cmp     esi, 32
        jae     .none
        mov     ebx, esi
        shl     ebx, 11                 ; bus 0, function 0
        xor     ecx, ecx
        call    pci_cfg_read32
        cmp     ax, 0xFFFF
        je      .next_dev               ; nothing in this slot
        mov     ecx, 0x0C
        call    pci_cfg_read32          ; header type in bits 16-23
        mov     r9d, 1                  ; functions to look at
        test    eax, 1 << 23            ; multi-function
        jz      .fns
        mov     r9d, 8
.fns:
        xor     r8d, r8d                ; function number
.fn:
        mov     ebx, esi
        shl     ebx, 11
        mov     eax, r8d
        shl     eax, 8
        or      ebx, eax
        xor     ecx, ecx
        call    pci_cfg_read32
        cmp     ax, 0xFFFF
        je      .next_fn
        mov     r10d, eax               ; device:vendor, kept for the guard
        mov     ecx, 0x08
        call    pci_cfg_read32          ; class code in bits 31..8
        shr     eax, 16
        cmp     ax, 0x0300
        jne     .next_fn
        ; The EDID guard (ring 7c, spec decision 3): BAR2 is an EDID only on
        ; QEMU's VGA (vendor 0x1234, device 0x1111). Any other display -
        ; Intel's, whose BAR2 is its graphics aperture - is "edid none", and
        ; the mode loop keeps the highest mode by area, Stage 1's rule.
        cmp     r10d, EDID_QEMU_VGA
        jne     .none
        mov     ecx, 0x18               ; BAR2
        call    pci_cfg_read32
        test    al, 1
        jnz     .next_fn                ; an I/O BAR is not it
        and     eax, ~0xF
        test    eax, eax
        jz      .next_fn
        mov     [edid_bar], eax
        mov     esi, eax                ; below 4 GB: a 32-bit BAR
        lea     rdi, [edid_buf]
        mov     ecx, EDID_BYTES
        rep     movsb                   ; byte reads, the region's own width
        lea     rsi, [edid_buf]
        cmp     byte [rsi], 0
        jne     .none
        cmp     dword [rsi + 1], 0xFFFFFFFF
        jne     .none
        cmp     word [rsi + 5], 0xFFFF
        jne     .none
        cmp     byte [rsi + 7], 0
        jne     .none
        cmp     word [rsi + EDID_DTD1], 0        ; pixel clock zero: not a timing
        je      .none
        movzx   eax, byte [rsi + EDID_DTD1 + 2]
        movzx   edx, byte [rsi + EDID_DTD1 + 4]
        shr     edx, 4
        shl     edx, 8
        or      eax, edx                ; horizontal active
        movzx   ecx, byte [rsi + EDID_DTD1 + 5]
        movzx   edx, byte [rsi + EDID_DTD1 + 7]
        shr     edx, 4
        shl     edx, 8
        or      ecx, edx                ; vertical active
        test    eax, eax
        jz      .none
        test    ecx, ecx
        jz      .none
        mov     [edid_w], eax
        mov     [edid_h], ecx
        lea     rsi, [msg_edid]
        call    serial_puts
        call    serial_putdec
        mov     al, 'x'
        call    serial_putc
        mov     eax, ecx
        call    serial_putdec
        lea     rsi, [msg_crlf]
        call    serial_puts
        ret
.next_fn:
        inc     r8d
        cmp     r8d, r9d
        jb      .fn
.next_dev:
        inc     esi
        jmp     .dev
.none:
        mov     dword [edid_w], 0
        mov     dword [edid_h], 0
        lea     rsi, [msg_edid_none]
        call    serial_puts
        ret

; pci_scan - one pass over bus 0, devices 0-31, every function of a
; multi-function device, recording the first virtio-net (1000 or 1041) into
; nic_dev (the BDF and the found flag), the first AHCI controller (class
; 0x010601) into ahci_bdf, and the first Intel class-0200 function whose
; device id is in e1k_ids into e1k_bdf (WIRE.md). Called once. Preserves
; everything.
pci_scan:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        push    rsi
        push    r8
        push    r9
        push    r10
        push    rbp
        xor     esi, esi                ; device number
.dev:
        cmp     esi, 32
        jae     .done
        mov     ebx, esi
        shl     ebx, 11                 ; bus 0, function 0
        xor     ecx, ecx
        call    pci_cfg_read32
        cmp     ax, 0xFFFF
        je      .next_dev               ; nothing in this slot
        mov     ecx, 0x0C
        call    pci_cfg_read32          ; header type in bits 16-23
        mov     edx, 1                  ; functions to look at
        test    eax, 1 << 23            ; bit 7 of the header type: multi-function
        jz      .fns
        mov     edx, 8
.fns:
        xor     r8d, r8d                ; function number
.fn:
        mov     ebx, esi
        shl     ebx, 11
        mov     eax, r8d
        shl     eax, 8
        or      ebx, eax
        xor     ecx, ecx
        call    pci_cfg_read32          ; vendor | device<<16
        cmp     ax, 0xFFFF
        je      .next_fn
        cmp     ax, PCI_VENDOR_VIRTIO
        jne     .not_virtio
        shr     eax, 16
        lea     rbp, [nic_dev]
        cmp     ax, PCI_DEV_NET_TRANS
        je      .match
        cmp     ax, PCI_DEV_NET_MODERN
        jne     .next_fn
        jmp     .match
.not_virtio:
        mov     r9d, eax                ; vendor | device<<16, kept for the NIC
        mov     ecx, 0x08
        call    pci_cfg_read32          ; class code in bits 31:8
        shr     eax, 8
        cmp     eax, AHCI_CLASS         ; the AHCI controller, by class (DISK.md)
        je      .ahci
        cmp     eax, E1K_CLASS          ; an Ethernet controller: Intel, and one of ours?
        jne     .next_fn
        cmp     r9w, PCI_VENDOR_INTEL
        jne     .next_fn
        shr     r9d, 16
        lea     r10, [e1k_ids]
        xor     ecx, ecx
.e1k_id:
        cmp     r9w, [r10 + rcx*2]
        je      .e1k_hit
        inc     ecx
        cmp     ecx, E1K_ID_COUNT
        jb      .e1k_id
        jmp     .next_fn
.e1k_hit:
        cmp     dword [e1k_found], 0
        jne     .next_fn                ; the first e1000e wins
        mov     [e1k_bdf], ebx
        mov     dword [e1k_found], 1
        jmp     .next_fn
.ahci:
        cmp     dword [ahci_found], 0
        jne     .next_fn                ; the first controller wins
        mov     [ahci_bdf], ebx
        mov     dword [ahci_found], 1
        jmp     .next_fn
.match:
        cmp     dword [rbp + VIO_FOUND], 0
        jne     .next_fn                ; first of each kind wins
        mov     [rbp + VIO_BDF], ebx
        mov     dword [rbp + VIO_FOUND], 1
.next_fn:
        inc     r8d
        cmp     r8d, edx
        jb      .fn
.next_dev:
        inc     esi
        jmp     .dev
.done:
        pop     rbp
        pop     r10
        pop     r9
        pop     r8
        pop     rsi
        pop     rdx
        pop     rcx
        pop     rbx
        pop     rax
        ret

; vio_attach - RBP = a device block the scan filled. Owns the device (command
; register), walks its capabilities, maps each modern region wherever the
; firmware put it and records the four addresses and the notify multiplier
; in the block. Every failure is a named ERR: line. Called once per device
; with interrupts off; clobbers registers freely.
vio_attach:
        mov     ebx, [rbp + VIO_BDF]

        ; Command register: memory space on, bus mastering on (the device
        ; cannot DMA our rings without it), INTx off (we poll, and the line
        ; must never be asserted into a PIC that has only IRQ1 unmasked).
        ; The status half of this dword is write-1-to-clear, so only the
        ; command half is written back.
        mov     ecx, 0x04
        call    pci_cfg_read32
        and     eax, 0xFFFF
        or      eax, PCI_CMD_MEMORY | PCI_CMD_MASTER | PCI_CMD_INTX_OFF
        call    pci_cfg_write32

        ; The capability list, walked from the pointer at 0x34. Bounded, so
        ; a looping list is a message rather than a hang.
        mov     ecx, 0x04
        call    pci_cfg_read32
        test    eax, 1 << 20            ; status bit 4: a capability list exists
        jz      .no_caps
        mov     ecx, 0x34
        call    pci_cfg_read32
        and     eax, 0xFC
        mov     r12d, eax               ; this capability's offset
        mov     r13d, 48                ; the bound
.cap:
        test    r12d, r12d
        jz      .caps_done
        dec     r13d
        jz      .caps_done
        mov     ecx, r12d
        call    pci_cfg_read32          ; id | next<<8 | cap_len<<16 | cfg_type<<24
        mov     r15d, eax
        shr     r15d, 8
        and     r15d, 0xFC              ; the next capability
        cmp     al, VIRTIO_PCI_CAP
        jne     .cap_next
        shr     eax, 24                 ; cfg_type
        test    eax, eax
        jz      .cap_next
        cmp     eax, VCAP_DEVICE
        ja      .cap_next               ; type 5 (PCI cfg access) and unknown types
        mov     r8d, eax

        ; First of each type wins: a slot already filled is left alone. The
        ; four slots are consecutive in the block, indexed by cfg_type.
        cmp     qword [rbp + VIO_COMMON - 8 + r8*8], 0
        jne     .cap_next

        lea     ecx, [r12 + 4]
        call    pci_cfg_read32
        movzx   r9d, al                 ; the BAR this capability lives in
        cmp     r9d, 5
        ja      .bad_bar
        lea     ecx, [r12 + 8]
        call    pci_cfg_read32
        mov     r10d, eax               ; offset within the BAR
        lea     ecx, [r12 + 12]
        call    pci_cfg_read32
        mov     r11d, eax               ; length of the region

        ; The BAR itself: a memory BAR, 32- or 64-bit, low four bits masked.
        lea     ecx, [r9*4 + 0x10]
        call    pci_cfg_read32
        test    eax, 1
        jnz     .bar_io
        mov     edx, eax
        and     eax, 0xFFFFFFF0
        mov     rdi, rax
        and     edx, 6
        cmp     edx, 4                  ; type 2 in bits 2:1 - a 64-bit BAR
        jne     .bar32
        add     ecx, 4
        call    pci_cfg_read32
        shl     rax, 32
        or      rdi, rax
.bar32:
        add     rdi, r10                ; RDI = the region's physical address

        ; Map the page holding its first byte and the page holding its last,
        ; uncached, wherever they are.
        mov     rax, rdi
        call    map_mmio_2m
        lea     rax, [rdi + r11 - 1]
        call    map_mmio_2m

        mov     [rbp + VIO_COMMON - 8 + r8*8], rdi     ; common, notify, isr, device
        cmp     r8d, VCAP_NOTIFY
        jne     .cap_next
        lea     ecx, [r12 + 16]
        call    pci_cfg_read32
        mov     [rbp + VIO_NMULT], eax
.cap_next:
        mov     r12d, r15d
        jmp     .cap
.caps_done:
        cmp     qword [rbp + VIO_COMMON], 0
        je      .no_caps
        cmp     qword [rbp + VIO_NOTIFY], 0
        je      .no_caps
        cmp     qword [rbp + VIO_DEVICE], 0
        je      .no_caps
        ret
.no_caps:
        lea     rsi, [err_vio_cap]
        call    serial_err
.bad_bar:
.bar_io:
        lea     rsi, [err_bar_io]
        call    serial_err

; The common configuration structure (virtio 1.1, 4.1.4.3). Every field is
; accessed at exactly its own width, and the 64-bit ones as two 32-bit
; halves: the spec says so, and QEMU enforces it (Stage 3 plan decision 12).
%define VC_DEV_FEAT_SEL     0x00        ; u32
%define VC_DEV_FEAT         0x04        ; u32
%define VC_DRV_FEAT_SEL     0x08        ; u32
%define VC_DRV_FEAT         0x0C        ; u32
%define VC_NUM_QUEUES       0x12        ; u16
%define VC_STATUS           0x14        ; u8
%define VC_Q_SELECT         0x16        ; u16
%define VC_Q_SIZE           0x18        ; u16
%define VC_Q_ENABLE         0x1C        ; u16
%define VC_Q_NOTIFY_OFF     0x1E        ; u16
%define VC_Q_DESC           0x20        ; u64
%define VC_Q_DRIVER         0x28        ; u64
%define VC_Q_DEVICE         0x30        ; u64

%define VS_ACKNOWLEDGE      1
%define VS_DRIVER           2
%define VS_DRIVER_OK        4
%define VS_FEATURES_OK      8
%define VF_VERSION_1_HI     1           ; feature bit 32 = bit 0 of the high word

; vio_negotiate - RBP = block, ECX = the feature bits 0-31 this driver wants,
; EDX = bits 32-63 (VERSION_1 among them, always). Reset, ACKNOWLEDGE,
; DRIVER; the device must offer VERSION_1 and every wanted bit, nothing else
; is accepted; FEATURES_OK written and read back. Only the modern interface
; is spoken: a device without VERSION_1 is a message, not a fallback.
; DRIVER_OK is set by vio_driver_ok once the queues exist. Clobbers
; registers freely.
vio_negotiate:
        mov     rdi, [rbp + VIO_COMMON]

        mov     byte [rdi + VC_STATUS], 0       ; reset
        mov     r8d, 100000
.reset_wait:
        cmp     byte [rdi + VC_STATUS], 0       ; the device says so by reading 0
        je      .reset_done
        pause
        dec     r8d
        jnz     .reset_wait
        lea     rsi, [err_vio_reset]
        call    serial_err
.reset_done:
        mov     byte [rdi + VC_STATUS], VS_ACKNOWLEDGE
        mov     byte [rdi + VC_STATUS], VS_ACKNOWLEDGE | VS_DRIVER

        mov     dword [rdi + VC_DEV_FEAT_SEL], 1
        mov     eax, [rdi + VC_DEV_FEAT]        ; feature bits 32-63
        test    eax, VF_VERSION_1_HI
        jz      .no_v1
        and     eax, edx
        cmp     eax, edx                ; every wanted high bit offered?
        jne     .missing
        mov     dword [rdi + VC_DEV_FEAT_SEL], 0
        mov     eax, [rdi + VC_DEV_FEAT]        ; feature bits 0-31
        and     eax, ecx
        cmp     eax, ecx                ; every wanted low bit offered?
        jne     .missing

        mov     dword [rdi + VC_DRV_FEAT_SEL], 0
        mov     [rdi + VC_DRV_FEAT], ecx
        mov     dword [rdi + VC_DRV_FEAT_SEL], 1
        mov     [rdi + VC_DRV_FEAT], edx
        mov     byte [rdi + VC_STATUS], VS_ACKNOWLEDGE | VS_DRIVER | VS_FEATURES_OK
        movzx   eax, byte [rdi + VC_STATUS]
        test    eax, VS_FEATURES_OK             ; the device must leave it set
        jz      .not_ok
        ret
.no_v1:
        lea     rsi, [err_vio_v1]
        call    serial_err
.missing:
        lea     rsi, [err_vio_missing]
        call    serial_err
.not_ok:
        lea     rsi, [err_vio_feat]
        call    serial_err

; vq_init - RBP = block, ECX = the queue number, RSI = its descriptor table,
; RDI = its available ring, R8 = its used ring (all 4 KB aligned in BSS; the
; identity map makes their linear addresses the physical ones the device is
; given). Takes the queue's size from the device, hands the three rings over
; as 32-bit halves, enables the queue, finds its doorbell, and sets
; NO_INTERRUPT - we poll, always. The queue block in the device block is
; filled. Clobbers registers freely.
vq_init:
        mov     eax, ecx
        imul    eax, VQ_BLK
        lea     r9, [rbp + VIO_Q]
        add     r9, rax                 ; R9 = this queue's block
        mov     r10, [rbp + VIO_COMMON]

        mov     [r10 + VC_Q_SELECT], cx
        movzx   eax, word [r10 + VC_Q_SIZE]
        test    eax, eax
        jz      .bad_size
        cmp     eax, VQ_MAX
        ja      .bad_size
        lea     edx, [rax - 1]
        test    eax, edx                ; a power of two shares no bit with itself minus one
        jnz     .bad_size
        mov     [r9 + Q_SIZE], eax
        mov     [r9 + Q_MASK], edx
        mov     [r9 + Q_DESC], rsi
        mov     [r9 + Q_AVAIL], rdi
        mov     [r9 + Q_USED], r8

        mov     rax, rsi
        mov     [r10 + VC_Q_DESC], eax
        shr     rax, 32
        mov     [r10 + VC_Q_DESC + 4], eax
        mov     rax, rdi
        mov     [r10 + VC_Q_DRIVER], eax
        shr     rax, 32
        mov     [r10 + VC_Q_DRIVER + 4], eax
        mov     rax, r8
        mov     [r10 + VC_Q_DEVICE], eax
        shr     rax, 32
        mov     [r10 + VC_Q_DEVICE + 4], eax

        mov     word [r10 + VC_Q_ENABLE], 1

        movzx   eax, word [r10 + VC_Q_NOTIFY_OFF]
        imul    eax, dword [rbp + VIO_NMULT]
        add     rax, [rbp + VIO_NOTIFY]
        mov     [r9 + Q_DOORBELL], rax

        mov     word [rdi], VQ_AVAIL_NO_INT     ; we poll; never interrupt
        mov     dword [r9 + Q_LAST_USED], 0
        ret
.bad_size:
        lea     rsi, [err_vq_size]
        call    serial_err

; vio_driver_ok - RBP = block. The queues exist; tell the device so.
; Preserves everything.
vio_driver_ok:
        push    rdi
        mov     rdi, [rbp + VIO_COMMON]
        mov     byte [rdi + VC_STATUS], VS_ACKNOWLEDGE | VS_DRIVER | VS_FEATURES_OK | VS_DRIVER_OK
        pop     rdi
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

; gpt_write - DISK.md's table written over the open blank disk, one sector
; a command: LBA 0 the protective MBR, LBA 1 the header, LBAs 2-33 the
; entry array (entries 0 and 1 from the document's bytes, the rest zero),
; LBAs N-33 .. N-2 the array again, LBA N-1 the backup header; then sector
; 0 of each partition written as zeros, so both stores format themselves
; on this boot; then "S7: gpt written". A disk too small for the two
; partitions is a named error before anything is written. Clobbers
; registers freely.
gpt_write:
        mov     eax, [ahci_sectors]
        cmp     eax, GPT_MIN_SECTORS
        jb      .too_small

        lea     rdi, [gpt_sec0]         ; LBA 0: the protective MBR
        mov     ecx, 512 / 8
        xor     eax, eax
        rep     stosq
        lea     rdi, [gpt_sec0]
        mov     byte [rdi + 0x1C0], 0x02        ; starting CHS 00 02 00
        mov     byte [rdi + 0x1C2], 0xEE        ; the protective type
        mov     dword [rdi + 0x1C3], 0x00FFFFFF ; ending CHS FF FF FF, then
        mov     dword [rdi + 0x1C6], 1          ; starting LBA 1
        mov     eax, [ahci_sectors]
        dec     eax
        mov     [rdi + 0x1CA], eax              ; size in LBAs: N - 1 (below 2^32 here)
        mov     word [rdi + 0x1FE], 0xAA55
        mov     eax, VBLK_T_OUT
        xor     ebx, ebx
        call    ahci_rw

        lea     rdi, [gpt_entries]      ; the array: the document's two entries, then zeros
        mov     ecx, GPT_ENTRIES * GPT_ENTRY / 8
        xor     eax, eax
        rep     stosq
        lea     rsi, [gpt_entry_image]
        lea     rdi, [gpt_entries]
        mov     ecx, 256 / 8
        rep     movsq
        lea     rsi, [gpt_entries]
        mov     eax, 0xFFFFFFFF
        mov     ecx, GPT_ENTRIES * GPT_ENTRY
        call    crc32_update
        not     eax
        mov     [gpt_ecrc], eax

        mov     r12d, 1                 ; the primary header: MyLBA 1,
        mov     r13d, [ahci_sectors]    ; AlternateLBA N - 1,
        dec     r13d
        mov     r14d, 2                 ; the entries at 2
        call    gpt_build_header
        mov     eax, VBLK_T_OUT
        mov     ebx, 1
        lea     rdi, [gpt_hdr]
        call    ahci_rw

        mov     ebx, 2                  ; LBAs 2-33
        lea     rdi, [gpt_entries]
.array:
        mov     eax, VBLK_T_OUT
        call    ahci_rw
        add     rdi, 512
        inc     ebx
        cmp     ebx, 2 + GPT_ENTRY_SECTORS
        jb      .array
        mov     ebx, [ahci_sectors]     ; LBAs N-33 .. N-2
        sub     ebx, 33
        lea     rdi, [gpt_entries]
        mov     ecx, GPT_ENTRY_SECTORS
.backup:
        mov     eax, VBLK_T_OUT
        call    ahci_rw
        add     rdi, 512
        inc     ebx
        dec     ecx
        jnz     .backup

        mov     r12d, [ahci_sectors]    ; the backup header: MyLBA N - 1,
        dec     r12d
        mov     r13d, 1                 ; AlternateLBA 1,
        mov     r14d, [ahci_sectors]    ; the entries at N - 33
        sub     r14d, 33
        call    gpt_build_header
        mov     eax, VBLK_T_OUT
        mov     ebx, [ahci_sectors]
        dec     ebx
        lea     rdi, [gpt_hdr]
        call    ahci_rw

        lea     rdi, [sector_buf]       ; sector 0 of each partition, zero
        mov     ecx, 512 / 8
        xor     eax, eax
        rep     stosq
        lea     rdi, [sector_buf]
        mov     eax, VBLK_T_OUT
        mov     ebx, GPT_NOTES_FIRST
        call    ahci_rw
        mov     eax, VBLK_T_OUT
        mov     ebx, GPT_HOME_FIRST
        call    ahci_rw

        lea     rsi, [msg_gpt_written]
        call    serial_puts
        ret
.too_small:
        lea     rsi, [err_disk_small]
        call    serial_err

; gpt_build_header - R12D = MyLBA, R13D = AlternateLBA, R14D = the entry
; array's LBA, gpt_ecrc the array's CRC: DISK.md's header built in gpt_hdr
; with its CRC computed over the 92 bytes with the CRC field zero.
; Clobbers registers freely.
gpt_build_header:
        lea     rdi, [gpt_hdr]
        mov     ecx, 512 / 8
        xor     eax, eax
        rep     stosq
        lea     rdi, [gpt_hdr]
        mov     rax, 'EFI PART'
        mov     [rdi], rax
        mov     dword [rdi + 8], 0x00010000
        mov     dword [rdi + 12], 92
        mov     eax, r12d
        mov     [rdi + 24], rax
        mov     eax, r13d
        mov     [rdi + 32], rax
        mov     qword [rdi + 40], GPT_FIRST_USABLE
        mov     eax, [ahci_sectors]
        sub     eax, GPT_FIRST_USABLE
        mov     [rdi + 48], rax
        lea     rsi, [guid_disk]
        push    rdi
        add     rdi, 56
        mov     ecx, 2
        rep     movsq
        pop     rdi
        mov     eax, r14d
        mov     [rdi + 72], rax
        mov     dword [rdi + 80], GPT_ENTRIES
        mov     dword [rdi + 84], GPT_ENTRY
        mov     eax, [gpt_ecrc]
        mov     [rdi + 88], eax
        mov     rsi, rdi
        mov     eax, 0xFFFFFFFF
        mov     ecx, 92
        call    crc32_update
        not     eax
        mov     [rdi + 16], eax
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
; The home image (stage6/HOME.md, ring 6b), on the home partition now: the
; format is HOME.md's byte for byte, every sector number relative to the
; partition. Always present on a GermOS disk (DISK.md).
; ---------------------------------------------------------------------------

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

; home_recount - the table in RAM walked: home_valid[i] = 1 for each valid
; entry (HOME.md's rule), home_count = how many, home_next = the next free
; sector (the data's first, or one past the furthest build). Preserves
; nothing but the callee-saved registers.
home_recount:
        push    rbx
        push    r12
        push    r13
        mov     dword [home_count], 0
        mov     dword [home_next], HOME_DATA_FIRST
        xor     r12d, r12d              ; the entry index
.entry:
        lea     rsi, [home_table]
        mov     eax, r12d
        shl     eax, 8
        add     rsi, rax                ; RSI = the entry
        lea     rax, [home_valid]
        mov     byte [rax + r12], 0
        cmp     byte [rsi], 0
        je      .next                   ; an empty slot
        call    home_entry_valid
        test    eax, eax
        jz      .next
        lea     rax, [home_valid]
        mov     byte [rax + r12], 1
        inc     dword [home_count]
        lea     rdi, [rsi + HE_CUR]
        call    .extend
        lea     rdi, [rsi + HE_PREV]
        cmp     dword [rdi + HB_SIZE], 0
        je      .next
        call    .extend
.next:
        inc     r12d
        cmp     r12d, HOME_ENTRIES
        jb      .entry
        pop     r13
        pop     r12
        pop     rbx
        ret
.extend:                                ; RDI = a build: home_next past it
        mov     eax, [rdi + HB_FIRST]
        add     eax, [rdi + HB_SECTORS]
        cmp     eax, [home_next]
        jbe     .no_extend
        mov     [home_next], eax
.no_extend:
        ret

; home_entry_valid - RSI = a 256-byte entry whose first byte is not zero.
; EAX = 1 if it is valid by HOME.md's rule: a well-formed NUL-padded name,
; a valid current build, an absent or valid previous build, legal choice
; slots, zero padding - else 0. Preserves RSI; clobbers RAX, RCX, RDX,
; RDI, R8-R11.
home_entry_valid:
        movzx   eax, byte [rsi]
        cmp     al, 'a'
        jb      .no
        cmp     al, 'z'
        ja      .no
        mov     ecx, 1
.name:
        cmp     ecx, 32
        jae     .name_done
        movzx   eax, byte [rsi + rcx]
        test    al, al
        jz      .pad
        cmp     al, '-'
        je      .name_ok
        cmp     al, '0'
        jb      .no
        cmp     al, '9'
        jbe     .name_ok
        cmp     al, 'a'
        jb      .no
        cmp     al, 'z'
        ja      .no
.name_ok:
        inc     ecx
        jmp     .name
.pad:
        inc     ecx
        cmp     ecx, 32
        jae     .name_done
        cmp     byte [rsi + rcx], 0
        jne     .no
        jmp     .pad
.name_done:
        lea     rdi, [rsi + HE_CUR]
        mov     r8d, 1                  ; required
        call    home_build_valid
        test    eax, eax
        jz      .no
        lea     rdi, [rsi + HE_PREV]
        xor     r8d, r8d                ; may be absent
        call    home_build_valid
        test    eax, eax
        jz      .no
        lea     rdi, [rsi + HE_CHOICES]
        call    choices_valid
        test    eax, eax
        jz      .no
        mov     ecx, HE_PAD
.zero:
        cmp     byte [rsi + rcx], 0
        jne     .no
        inc     ecx
        cmp     ecx, HOME_ENTRY
        jb      .zero
        mov     eax, 1
        ret
.no:
        xor     eax, eax
        ret

; home_build_valid - RDI = a build's fields (size, first, sectors, zero,
; hash); R8D = 1 if the build must be present. EAX = 1 if absent (every
; field zero) when allowed, or present and valid: the size 16 to the cap,
; the sector count ceil(size / 512), the zero field zero, the extent from
; the data's first sector and within the capacity. Clobbers RAX, RCX, RDX.
home_build_valid:
        mov     eax, [rdi + HB_SIZE]
        test    eax, eax
        jnz     .present
        test    r8d, r8d
        jnz     .no
        mov     ecx, 4
.absent:
        cmp     dword [rdi + rcx], 0
        jne     .no
        add     ecx, 4
        cmp     ecx, HB_BYTES
        jb      .absent
        mov     eax, 1
        ret
.present:
        cmp     eax, BLOB_HDR
        jb      .no
        cmp     eax, COMP_BLOB_MAX
        ja      .no
        mov     edx, eax
        add     edx, 511
        shr     edx, 9                  ; ceil(size / 512)
        cmp     edx, [rdi + HB_SECTORS]
        jne     .no
        cmp     dword [rdi + HB_ZERO], 0
        jne     .no
        mov     ecx, [rdi + HB_FIRST]
        cmp     ecx, HOME_DATA_FIRST
        jb      .no
        add     ecx, edx
        jc      .no
        cmp     ecx, [part_home + PART_SECTORS]
        ja      .no
        mov     eax, 1
        ret
.no:
        xor     eax, eax
        ret

; home_install - the frame in the region has been checked and carries
; installed 1 (HOME.md, "What becomes an app on disk"): the blob's tail
; zeroed to the sector boundary, its sectors written from the next free
; one, its SHA-256 taken, the table entry made (the first empty slot) or
; replaced (the current build becoming the previous), that table sector
; written, the table recounted, and "installed <name>" on the console.
; With no home image, or no room, the app is not kept, the console says
; so, an error is counted - and the app runs anyway: it passed the twin.
; Clobbers registers freely.
home_install:
        lea     rsi, [comp_region + COMP_RX_OFF + 4]    ; the content
        lea     r14, [rsi + APPH_NAME]                  ; the name
        cmp     dword [home_present], 0
        je      .no_home
        mov     r12d, [rsi + APPH_LEN]                  ; L, the size
        lea     rdi, [comp_region + APP_BLOB_OFF]
        add     rdi, r12
        mov     ecx, r12d
        neg     ecx
        and     ecx, 511                                ; bytes to the boundary
        xor     eax, eax
        rep     stosb
        mov     r13d, r12d
        add     r13d, 511
        shr     r13d, 9                                 ; the sectors
        mov     eax, [home_next]
        add     eax, r13d
        jc      .full
        cmp     eax, [part_home + PART_SECTORS]
        ja      .full
        call    home_find_entry                         ; EAX = the entry, or -1
        cmp     eax, -1
        jne     .replace
        call    home_free_slot
        cmp     eax, -1
        je      .full
        mov     r15d, eax
        call    home_entry_addr                         ; RDI = the entry
        push    rdi
        mov     ecx, HOME_ENTRY / 8
        xor     eax, eax
        rep     stosq                                   ; a fresh entry, zero
        pop     rdi
        mov     rsi, r14
        mov     ecx, APP_NAME_MAX
        rep     movsb                                   ; the name in
        jmp     .write_blob
.replace:
        mov     r15d, eax
        call    home_entry_addr
        lea     rsi, [rdi + HE_CUR]                     ; the current build
        add     rdi, HE_PREV                            ; becomes the previous
        mov     ecx, HB_BYTES / 8
        rep     movsq
.write_blob:
        mov     ebx, [home_next]
        lea     rdi, [comp_region + APP_BLOB_OFF]
        mov     ecx, r13d
.sector:
        mov     eax, VBLK_T_OUT
        call    home_rw
        add     rdi, 512
        inc     ebx
        dec     ecx
        jnz     .sector
        lea     rsi, [comp_region + APP_BLOB_OFF]       ; the digest
        mov     rcx, r12
        lea     rdi, [sha_digest]
        call    sha256
        call    home_entry_addr                         ; R15D = the entry
        mov     [rdi + HE_CUR + HB_SIZE], r12d
        mov     eax, [home_next]
        mov     [rdi + HE_CUR + HB_FIRST], eax
        mov     [rdi + HE_CUR + HB_SECTORS], r13d
        mov     dword [rdi + HE_CUR + HB_ZERO], 0
        push    rdi
        lea     rsi, [sha_digest]
        add     rdi, HE_CUR + HB_SHA
        mov     ecx, 4
        rep     movsq
        pop     rdi
        lea     rsi, [comp_region + COMP_RX_OFF + 4 + APPH_CHOICES]
        add     rdi, HE_CHOICES
        mov     ecx, APP_CHOICES * APP_CHOICE_BYTES
        rep     movsb                                   ; the frame's slots
        call    home_write_entry_sector                 ; only now: the blob is on disk
        call    home_recount                            ; the row is rebuilt when the app closes
        lea     rsi, [msg_installed]
        mov     rdx, r14
        lea     rcx, [msg_empty]
        call    home_say
        ret
.full:
        lea     rsi, [msg_home_full]
        mov     rdx, r14
        lea     rcx, [msg_not_kept]
        call    home_say
        inc     qword [obs_page + OBS_ERRORS]
        ret
.no_home:
        lea     rsi, [msg_no_home]
        mov     rdx, r14
        lea     rcx, [msg_not_kept]
        call    home_say
        inc     qword [obs_page + OBS_ERRORS]
        ret

; home_entry_addr - R15D = an entry index: RDI = its address in the table.
home_entry_addr:
        lea     rdi, [home_table]
        mov     eax, r15d
        shl     eax, 8
        add     rdi, rax
        ret

; home_write_entry_sector - R15D = an entry index: the table sector holding
; it written through. Clobbers RAX, RBX, RDI.
home_write_entry_sector:
        mov     eax, r15d
        shr     eax, 1
        lea     ebx, [rax + HOME_TABLE_FIRST]
        shl     eax, 9
        lea     rdi, [home_table]
        add     rdi, rax
        mov     eax, VBLK_T_OUT
        call    home_rw
        ret

; home_find_entry - R14 = a 32-byte NUL-padded name: EAX = the index of the
; valid entry with that name, or -1. Clobbers RAX, RCX, RSI, RDI, R8.
home_find_entry:
        xor     r8d, r8d
.entry:
        lea     rax, [home_valid]
        cmp     byte [rax + r8], 0
        je      .next
        lea     rsi, [home_table]
        mov     eax, r8d
        shl     eax, 8
        add     rsi, rax
        mov     rdi, r14
        mov     ecx, APP_NAME_MAX
        repe    cmpsb
        jne     .next
        mov     eax, r8d
        ret
.next:
        inc     r8d
        cmp     r8d, HOME_ENTRIES
        jb      .entry
        mov     eax, -1
        ret

; home_free_slot - EAX = the first entry that is not valid (empty, or
; invalid and so overwritable), or -1. Clobbers RAX, R8.
home_free_slot:
        xor     r8d, r8d
.entry:
        lea     rax, [home_valid]
        cmp     byte [rax + r8], 0
        jne     .next
        mov     eax, r8d
        ret
.next:
        inc     r8d
        cmp     r8d, HOME_ENTRIES
        jb      .entry
        mov     eax, -1
        ret

; home_say - RSI = a NUL-terminated prefix, RDX = a name (32 bytes, NUL
; padded), RCX = a NUL-terminated suffix: "<prefix><name><suffix>" on the
; console, and only the console. The line is finished by whoever prompts
; next. Preserves everything.
home_say:
        push    rax
        push    rcx
        push    rdx
        push    rsi
        push    rdi
        lea     rdi, [say_buf]
.prefix:
        lodsb
        test    al, al
        jz      .name
        stosb
        jmp     .prefix
.name:
        mov     rsi, rdx
        mov     edx, APP_NAME_MAX
.name_byte:
        lodsb
        test    al, al
        jz      .suffix
        stosb
        dec     edx
        jnz     .name_byte
.suffix:
        mov     rsi, rcx
.suffix_byte:
        lodsb
        stosb
        test    al, al
        jnz     .suffix_byte
        lea     rsi, [say_buf]
        call    console_puts
        pop     rdi
        pop     rsi
        pop     rdx
        pop     rcx
        pop     rax
        ret

; body_is_install - RSI = a request body, ECX = its length: EAX = 1 if it
; is the word "install" alone or followed by a space (PLANS.md: every such
; body is an install, and the strip says so). Preserves RSI, ECX.
body_is_install:
        cmp     ecx, 7
        jb      .no
        push    rsi
        push    rcx
        push    rdi
        lea     rdi, [msg_install_word]
        mov     ecx, 7
        repe    cmpsb
        pop     rdi
        pop     rcx
        pop     rsi
        jne     .no
        cmp     ecx, 7
        je      .yes
        cmp     byte [rsi + 7], ' '
        jne     .no
.yes:
        mov     eax, 1
        ret
.no:
        xor     eax, eax
        ret

; bang_line - RSI = a "!" line's trimmed body, ECX = its length (HOME.md,
; "What a ! line does now"): empty, or anything unknown, takes ring 6a's
; path to the broker (grow_request); "undo install <name>" is the undo;
; a body equal to a valid home entry's name is a launch from the home
; image with nothing on the wire. Each path ends in finish_line, whose
; ret is the caller's. Clobbers registers freely.
bang_line:
        test    ecx, ecx
        jz      grow_request                    ; "nothing to grow"
        cmp     ecx, 13
        jbe     .not_undo                       ; "undo install " and a name
        push    rsi
        push    rcx
        push    rdi
        lea     rdi, [msg_undo_word]
        mov     ecx, 13
        repe    cmpsb
        pop     rdi
        pop     rcx
        pop     rsi
        jne     .not_undo
        add     rsi, 13
        sub     ecx, 13
        jmp     home_undo
.not_undo:
        call    home_lookup_name                ; EAX = the entry, or -1
        cmp     eax, -1
        je      grow_request                    ; the broker, as ring 6a
        mov     r15d, eax
        jmp     home_launch

; home_lookup_name - RSI = a name, ECX = its length: name_buf holds it NUL
; padded (cut at 32), and EAX = the valid entry of that exact name, or -1.
; Preserves RSI and RCX (the body goes on to the broker on a miss);
; clobbers RAX, RDI, R8, R14.
home_lookup_name:
        push    rsi
        push    rcx
        call    .lookup
        pop     rcx
        pop     rsi
        ret
.lookup:
        lea     rdi, [name_buf]
        push    rdi
        mov     eax, ecx
        xor     ecx, ecx
        mov     [rdi], rcx
        mov     [rdi + 8], rcx
        mov     [rdi + 16], rcx
        mov     [rdi + 24], rcx
        mov     ecx, eax
        cmp     ecx, APP_NAME_MAX
        jbe     .copy
        mov     ecx, APP_NAME_MAX
        pop     rdi
        rep     movsb
        mov     eax, -1                         ; longer than a name can be
        ret
.copy:
        pop     rdi
        rep     movsb
        cmp     dword [home_present], 0
        je      .none
        lea     r14, [name_buf]
        call    home_find_entry
        ret
.none:
        mov     eax, -1
        ret

; home_undo - RSI = the name after "undo install ", ECX = its length: the
; entry's two builds swapped and its table sector written, or the reason
; why not. Console only; then finish_line.
home_undo:
        call    app_close_if_running            ; a ! line closes the app first
        call    home_lookup_name
        cmp     eax, -1
        je      .no_app
        mov     r15d, eax
        call    home_entry_addr                 ; RDI = the entry
        cmp     dword [rdi + HE_PREV + HB_SIZE], 0
        je      .no_previous
        push    rdi
        lea     rsi, [rdi + HE_CUR]             ; the current build aside
        lea     rdi, [sha_tail]
        mov     ecx, HB_BYTES / 8
        rep     movsq
        pop     rdi
        push    rdi
        lea     rsi, [rdi + HE_PREV]            ; the previous becomes current
        add     rdi, HE_CUR
        mov     ecx, HB_BYTES / 8
        rep     movsq
        pop     rdi
        lea     rsi, [sha_tail]                 ; and the old current, previous
        add     rdi, HE_PREV
        mov     ecx, HB_BYTES / 8
        rep     movsq
        call    home_write_entry_sector
        call    home_recount
        lea     rsi, [msg_empty]
        lea     rdx, [name_buf]
        lea     rcx, [msg_restored]
        call    home_say
        jmp     finish_line
.no_previous:
        lea     rsi, [msg_empty]
        lea     rdx, [name_buf]
        lea     rcx, [msg_no_previous]
        call    home_say
        inc     qword [obs_page + OBS_ERRORS]
        jmp     finish_line
.no_app:
        lea     rsi, [msg_no_app]
        lea     rdx, [name_buf]
        lea     rcx, [msg_empty]
        call    home_say
        inc     qword [obs_page + OBS_ERRORS]
        jmp     finish_line

; home_launch - R15D = a valid entry: its current build read from the home
; image into the component region at +128, hashed and checked against the
; entry, a frame header synthesised in the region (kind 2, ABI 2, source
; 0, installed 1, the name, the entry's choices), and the app run exactly
; as a delivered one - with nothing on the wire, and neither grows counter
; moved. A hash mismatch runs nothing and says so. Then finish_line.
home_launch:
        call    app_close_if_running
        call    home_entry_addr                 ; RDI = the entry
        mov     r12d, [rdi + HE_CUR + HB_SIZE]
        mov     ebx, [rdi + HE_CUR + HB_FIRST]
        mov     r13d, [rdi + HE_CUR + HB_SECTORS]
        push    rdi
        lea     rdi, [comp_region + APP_BLOB_OFF]
        mov     ecx, r13d
.sector:
        mov     eax, VBLK_T_IN
        call    home_rw
        add     rdi, 512
        inc     ebx
        dec     ecx
        jnz     .sector
        lea     rsi, [comp_region + APP_BLOB_OFF]
        mov     rcx, r12
        lea     rdi, [sha_digest]
        call    sha256
        pop     rdi
        push    rdi
        lea     rsi, [sha_digest]
        add     rdi, HE_CUR + HB_SHA
        mov     ecx, 32
        repe    cmpsb
        pop     rdi
        jne     .bad_hash
        ; the header, as the wire would have carried it
        push    rdi
        lea     rdi, [comp_region + COMP_RX_OFF]
        mov     eax, r12d
        add     eax, APP_HDR
        mov     [rdi], eax                      ; N, for tidiness
        add     rdi, 4
        mov     ecx, APP_HDR / 8
        xor     eax, eax
        rep     stosq
        pop     rsi                             ; the entry
        lea     rdi, [comp_region + COMP_RX_OFF + 4]
        mov     byte [rdi], APP_KIND
        mov     byte [rdi + APPH_ABI], APP_ABI
        mov     [rdi + APPH_LEN], r12d
        mov     byte [rdi + APPH_INSTALLED], 1
        push    rsi
        push    rdi
        add     rdi, APPH_NAME
        mov     ecx, APP_NAME_MAX
        rep     movsb                           ; the name (RSI at the entry's)
        pop     rdi
        pop     rsi
        add     rsi, HE_CHOICES
        add     rdi, APPH_CHOICES
        mov     ecx, APP_CHOICES * APP_CHOICE_BYTES
        rep     movsb
        mov     dword [launch_home], 1
        call    run_app
        mov     dword [launch_home], 0
        jmp     finish_line
.bad_hash:
        lea     rsi, [msg_empty]
        lea     rdx, [name_buf]
        lea     rcx, [msg_bad_hash]
        call    home_say
        inc     qword [obs_page + OBS_ERRORS]
        jmp     finish_line

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

; ---------------------------------------------------------------------------
; The NIC - a virtio-net device on the same plumbing (plan decision 8). Two
; feature bits, MAC and VERSION_1, nothing else: no mergeable buffers, no
; offloads, no control queue. Queue 0 receives, queue 1 transmits; both
; polled, NO_INTERRUPT set, INTx off. With VERSION_1 every packet carries a
; 12-byte virtio-net header; a receive buffer is one device-writable
; descriptor holding header and frame contiguously, and must hold the whole
; packet since buffers do not merge - 2048 bytes covers 12 + 1514. One
; transmit descriptor in flight, reaped before the next. Only the BSP ever
; touches any of it.
; ---------------------------------------------------------------------------

%define VNET_F_MAC          (1 << 5)    ; the config MAC is valid only if negotiated
%define VNET_CFG_MAC        0           ; the six MAC bytes in device config

; nic_find - the NIC attached and its lines printed, or a named error: the
; e1000e when the scan found one (e1k_attach prints the nic line and the
; link line), else the virtio-net (attached, negotiated, its queues given,
; the nic line - no link line: ring 7a's gate counts on it). nic_kind says
; which driver owns net_send and net_poll. Called once from efi_main after
; the disk is up, interrupts off; clobbers registers freely.
nic_find:
        cmp     dword [e1k_found], 0
        je      .virtio
        mov     dword [nic_kind], NIC_E1000E
        call    e1k_attach
        ret
.virtio:
        lea     rbp, [nic_dev]
        cmp     dword [rbp + VIO_FOUND], 0
        jne     .have
        lea     rsi, [err_no_nic]
        call    serial_err
.have:
        mov     dword [nic_kind], NIC_VIRTIO
        call    vio_attach
        call    nic_negotiate
        call    nic_queue_init
        lea     rsi, [msg_nic]
        call    serial_puts
        call    serial_putmac
        lea     rsi, [msg_crlf]
        call    serial_puts
        ret

; nic_negotiate - MAC | VERSION_1, and the MAC read into nic_mac. Clobbers.
nic_negotiate:
        lea     rbp, [nic_dev]
        mov     ecx, VNET_F_MAC
        mov     edx, VF_VERSION_1_HI
        call    vio_negotiate
        mov     rsi, [rbp + VIO_DEVICE]
        lea     rdi, [nic_mac]
        mov     ecx, 6
.mac:
        mov     al, [rsi + VNET_CFG_MAC]
        mov     [rdi], al
        inc     rsi
        inc     rdi
        dec     ecx
        jnz     .mac
        ret

; nic_queue_init - queue 0 (receive) on the rx rings with every receive
; buffer posted, queue 1 (transmit) on the tx rings, then DRIVER_OK and one
; kick of the receive queue. The receive descriptors are filled once -
; descriptor i always names buffer i - and a buffer is re-posted later by
; putting its descriptor index back in the available ring. Clobbers
; registers freely.
nic_queue_init:
        lea     rbp, [nic_dev]
        xor     ecx, ecx
        lea     rsi, [nic_rx_desc]
        lea     rdi, [nic_rx_avail]
        lea     r8, [nic_rx_used]
        call    vq_init
        mov     ecx, 1
        lea     rsi, [nic_tx_desc]
        lea     rdi, [nic_tx_avail]
        lea     r8, [nic_tx_used]
        call    vq_init

        lea     rsi, [nic_rx_desc]
        lea     rdx, [nic_rx_bufs]
        lea     rdi, [nic_rx_avail]
        xor     ecx, ecx
.rx_desc:
        mov     [rsi], rdx                      ; descriptor i: buffer i, whole,
        mov     dword [rsi + 8], NIC_RX_BUF     ; device-writable, no chain
        mov     word [rsi + 12], VQ_DESC_WRITE
        mov     word [rsi + 14], 0
        mov     [rdi + 4 + rcx*2], cx           ; available ring[i] = i
        add     rsi, 16
        add     rdx, NIC_RX_BUF
        inc     ecx
        cmp     ecx, NIC_RX_BUFS
        jb      .rx_desc
        mfence
        mov     word [rdi + 2], NIC_RX_BUFS     ; all of them, at once
        mfence

        ; The one transmit descriptor: the tx buffer, length set per send.
        lea     rsi, [nic_tx_desc]
        lea     rdx, [nic_tx_buf]
        mov     [rsi], rdx
        mov     word [rsi + 12], 0
        mov     word [rsi + 14], 0

        call    vio_driver_ok
        mov     rax, [rbp + VIO_Q + Q_DOORBELL] ; tell the device its buffers exist
        mov     word [rax], 0
        ret

; serial_putmac - the six bytes at nic_mac as lowercase hex pairs, colon
; separated. Preserves everything.
serial_putmac:
        push    rax
        push    rcx
        push    rsi
        lea     rsi, [nic_mac]
        mov     ecx, 6
.pair:
        lodsb
        call    serial_puthex8
        dec     ecx
        jz      .done
        mov     al, ':'
        call    serial_putc
        jmp     .pair
.done:
        pop     rsi
        pop     rcx
        pop     rax
        ret

; serial_puthex8 - AL as two lowercase hex digits. Preserves everything.
serial_puthex8:
        push    rax
        push    rbx
        push    rdx
        mov     dl, al
        lea     rbx, [hex_digits]
        shr     al, 4
        xlatb
        call    serial_putc
        mov     al, dl
        and     al, 15
        xlatb
        call    serial_putc
        pop     rdx
        pop     rbx
        pop     rax
        ret

; ---------------------------------------------------------------------------
; The wire - Ethernet, ARP and IPv4 (plan decisions 6 and 7), the smallest
; honest stack for a world of one on-link peer: the guest is 10.0.2.15, the
; broker is 10.0.2.4, and there is no gateway and no route. Frames are built
; in nic_tx_buf behind the 12-byte virtio-net header and sent one at a time;
; received frames are dispatched by EtherType from the receive buffers and
; the buffers re-posted. Checksums are computed on send and verified on
; receive; a bad one is dropped in silence, exactly as slirp drops ours.
; Only the BSP calls any of this. Everything here clobbers registers freely
; unless it says otherwise.
;
; Offsets inside a frame (Ethernet header first): ETH_* for the header,
; ARP_* for an ARP body at 14, IP_* for an IPv4 header at 14; the transmit
; buffer adds TX_BASE for the virtio header in front.
; ---------------------------------------------------------------------------

%define TX_BASE             VNET_HDR_LEN        ; the Ethernet frame starts here
%define TX_IP               (TX_BASE + 14)      ; the IPv4 header
%define TX_PAYLOAD          (TX_IP + 20)        ; what rides on IPv4 (TCP)

%define ETH_DST             0
%define ETH_SRC             6
%define ETH_TYPE            12
%define ETH_HDR             14
%define ETHTYPE_ARP         0x0608              ; 08 06 in memory order
%define ETHTYPE_IP          0x0008              ; 08 00 in memory order

%define ARP_HTYPE           14
%define ARP_PTYPE           16
%define ARP_HLEN            18
%define ARP_PLEN            19
%define ARP_OPER            20
%define ARP_SHA             22
%define ARP_SPA             28
%define ARP_THA             32
%define ARP_TPA             38
%define ARP_LEN             42
%define ARP_OP_REQUEST      0x0100              ; 00 01 in memory order
%define ARP_OP_REPLY        0x0200              ; 00 02 in memory order

%define IP_VER              14
%define IP_TOS              15
%define IP_TOTLEN           16
%define IP_IDENT            18
%define IP_FRAG             20
%define IP_TTL              22
%define IP_PROTO            23
%define IP_CSUM             24
%define IP_SRC              26
%define IP_DST              30
%define IP_HDR              20
%define IP_PROTO_TCP        6

%define OUR_IP              0x0F02000A          ; 10.0.2.15 in memory order
%define BROKER_IP           0x0402000A          ; 10.0.2.4 in memory order

%define ARP_TRIES           3
%define ARP_WAIT_TICKS      5000                ; x 200 us = one second

; net_send - the Ethernet frame is in nic_tx_buf at TX_BASE; ECX = its
; length. Pads to the 60-byte minimum, counts the bytes, then hands the
; frame to the driver that owns the NIC (nic_kind): e1k_send, or the
; virtio path below - the virtio-net header zeroed, the one transmit
; descriptor given, queue 1 rung, the completion awaited - bounded, a dead
; device being an ERR:, not a hang.
net_send:
        cmp     ecx, 60
        jae     .long_enough
        lea     rdi, [nic_tx_buf + TX_BASE]
        add     rdi, rcx
        push    rcx
        mov     ecx, 60
        sub     ecx, [rsp]
        xor     eax, eax
        rep     stosb                   ; zero the padding
        pop     rcx
        mov     ecx, 60
.long_enough:
        mov     eax, ecx
        add     [obs_page + OBS_BYTES_OUT], rax
        cmp     dword [nic_kind], NIC_E1000E
        je      e1k_send
        lea     rdi, [nic_tx_buf]       ; the virtio-net header: all zero -
        xor     eax, eax                ; no checksum offload, no GSO
        mov     [rdi], rax
        mov     [rdi + 8], eax
        add     ecx, VNET_HDR_LEN

        lea     rbp, [nic_dev]
        lea     r9, [rbp + VIO_Q + VQ_BLK]      ; queue 1's block
        mov     rsi, [r9 + Q_DESC]
        mov     [rsi + 8], ecx          ; descriptor 0: the whole buffer, this long
        mov     word [rsi + 12], 0      ; device-readable, no chain

        mov     rsi, [r9 + Q_AVAIL]     ; publish: ring[idx & mask] = 0, idx++
        movzx   ecx, word [rsi + 2]
        mov     edx, ecx
        and     edx, [r9 + Q_MASK]
        mov     word [rsi + 4 + rdx*2], 0
        mfence
        inc     ecx
        mov     [rsi + 2], cx
        mfence
        mov     rdx, [r9 + Q_DOORBELL]
        mov     word [rdx], 1

        mov     rsi, [r9 + Q_USED]      ; reaped before the next send
        mov     r8d, VQ_POLL_TRIES
.poll:
        movzx   eax, word [rsi + 2]
        cmp     eax, [r9 + Q_LAST_USED]
        jne     .done
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .poll
        lea     rsi, [err_nic_tx]
        call    serial_err
.done:
        lfence
        inc     dword [r9 + Q_LAST_USED]
        and     dword [r9 + Q_LAST_USED], 0xFFFF
        ret

; net_poll - every frame the device has delivered since the last look:
; dispatched by EtherType (ARP or IPv4; anything else dropped), then its
; buffer re-posted. Returns EAX = the number of frames taken. Called from
; every wait loop; also safe to call when there is nothing. The driver
; that owns the NIC does the work: e1k_poll, or the virtio path below.
net_poll:
        cmp     dword [nic_kind], NIC_E1000E
        je      e1k_poll
        push    r12
        push    r13
        push    r14
        xor     r14d, r14d              ; frames taken
        lea     rbp, [nic_dev]
        lea     r12, [rbp + VIO_Q]      ; queue 0's block
.next:
        mov     rsi, [r12 + Q_USED]
        movzx   eax, word [rsi + 2]
        cmp     eax, [r12 + Q_LAST_USED]
        je      .out
        lfence
        mov     edx, [r12 + Q_LAST_USED]
        and     edx, [r12 + Q_MASK]
        mov     r13d, [rsi + 4 + rdx*8]         ; the descriptor id = the buffer index
        mov     ecx, [rsi + 8 + rdx*8]          ; bytes written, header included
        inc     dword [r12 + Q_LAST_USED]
        and     dword [r12 + Q_LAST_USED], 0xFFFF
        inc     r14d
        cmp     r13d, NIC_RX_BUFS
        jae     .repost                 ; not ours - never happens, never trusted
        cmp     ecx, VNET_HDR_LEN + ETH_HDR
        jb      .repost                 ; too short to carry a type
        sub     ecx, VNET_HDR_LEN       ; ECX = the Ethernet frame length
        mov     eax, ecx
        add     [obs_page + OBS_BYTES_IN], rax
        mov     eax, r13d
        shl     eax, 11                 ; x NIC_RX_BUF
        lea     rsi, [nic_rx_bufs + VNET_HDR_LEN]
        add     rsi, rax                ; RSI = the Ethernet frame
        cmp     word [rsi + ETH_TYPE], ETHTYPE_ARP
        jne     .not_arp
        call    arp_input
        jmp     .repost
.not_arp:
        cmp     word [rsi + ETH_TYPE], ETHTYPE_IP
        jne     .repost
        call    ip_input
.repost:
        mov     rdi, [r12 + Q_AVAIL]    ; the buffer goes back: ring[idx & mask] = id
        movzx   ecx, word [rdi + 2]
        mov     edx, ecx
        and     edx, [r12 + Q_MASK]
        mov     [rdi + 4 + rdx*2], r13w
        mfence
        inc     ecx
        mov     [rdi + 2], cx
        mfence
        mov     rdx, [r12 + Q_DOORBELL]
        mov     word [rdx], 0
        jmp     .next
.out:
        mov     eax, r14d
        pop     r14
        pop     r13
        pop     r12
        ret

; ---------------------------------------------------------------------------
; The NIC the metal has - the e1000e driver (stage7/WIRE.md, ring 7b), per
; the 82574 datasheet, the register set the 82579LM shares. Chosen over the
; virtio-net above whenever both are present: nic_find dispatches on kind,
; and net_send / net_poll below dispatch on nic_kind. The function is owned
; before BAR0 is read; BAR0 is mapped uncached wherever the firmware put it;
; the device is reset with interrupts masked, so nothing a firmware driver
; left is trusted; the MAC is read from RAL0/RAH0; the link is awaited for
; ten seconds and its absence is a named error; then the two legacy rings.
; Only the BSP calls any of this, interrupts off, polled. Clobbers freely.
; ---------------------------------------------------------------------------

e1k_attach:
        mov     ebx, [e1k_bdf]
        mov     ecx, 0x04
        call    pci_cfg_read32
        and     eax, 0xFFFF             ; the status half is write-1-to-clear
        or      eax, PCI_CMD_MEMORY | PCI_CMD_MASTER | PCI_CMD_INTX_OFF
        call    pci_cfg_write32         ; owned BEFORE the BAR is read

        mov     ecx, 0x10               ; BAR0: a memory BAR, 32- or 64-bit
        call    pci_cfg_read32
        test    al, 1
        jnz     .bar_io
        mov     edx, eax
        and     eax, 0xFFFFFFF0
        mov     rdi, rax
        and     edx, 6
        cmp     edx, 4                  ; type 2 in bits 2:1 - a 64-bit BAR
        jne     .bar32
        mov     ecx, 0x14
        call    pci_cfg_read32
        shl     rax, 32
        or      rdi, rax
.bar32:
        mov     [e1k_bar], rdi
        mov     rax, rdi
        call    map_mmio_2m             ; the page holding its first byte
        lea     rax, [rdi + E1K_BAR_SIZE - 1]
        call    map_mmio_2m             ; and its last

        ; The reset: interrupts masked, CTRL.RST set and awaited clear,
        ; interrupts masked again, ICR read once. Assume nothing about the
        ; state a firmware driver left.
        mov     dword [rdi + E1K_IMC], 0xFFFFFFFF
        mov     eax, [rdi + E1K_CTRL]
        or      eax, CTRL_RST
        mov     [rdi + E1K_CTRL], eax
        mov     r8d, E1K_RESET_TRIES
.reset_wait:
        mov     eax, [rdi + E1K_CTRL]
        test    eax, CTRL_RST
        jz      .reset_done
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .reset_wait
        lea     rsi, [err_e1k_reset]
        call    serial_err
.reset_done:
        mov     dword [rdi + E1K_IMC], 0xFFFFFFFF
        mov     eax, [rdi + E1K_ICR]

        ; The MAC, from the receive address the firmware loaded from the
        ; EEPROM: RAL0 the first four bytes, RAH0's low half the last two,
        ; and RAH0.AV must say the address is valid. Then the nic line.
        mov     eax, [rdi + E1K_RAH0]
        test    eax, RAH_AV
        jz      .no_mac
        mov     [nic_mac + 4], ax
        mov     eax, [rdi + E1K_RAL0]
        mov     [nic_mac], eax
        lea     rsi, [msg_nic]
        call    serial_puts
        call    serial_putmac
        lea     rsi, [msg_crlf]
        call    serial_puts

        ; The link: SLU set, the forced speed and duplex, ILOS and PHY_RST
        ; cleared (the PHY autonegotiates; MDIC untouched this ring), then
        ; STATUS.LU awaited for ten seconds or a named error.
        mov     eax, [rdi + E1K_CTRL]
        and     eax, CTRL_LINK_KEEP
        or      eax, CTRL_SLU
        mov     [rdi + E1K_CTRL], eax
        mov     r8d, E1K_LINK_TRIES
.link_wait:
        mov     eax, [rdi + E1K_STATUS]
        test    eax, STATUS_LU
        jnz     .link_up
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .link_wait
        lea     rsi, [err_e1k_link]
        call    serial_err
.link_up:
        lea     rsi, [msg_link]
        call    serial_puts

        ; Receive: the multicast table zeroed, sixteen descriptors over the
        ; virtio driver's buffers (offset by the twelve-byte header), the
        ; ring's base, length, head and tail; legacy descriptors on one
        ; queue; RCTL enabled with broadcast accepted, 2048-byte buffers, the
        ; CRC stripped; then the tail moved to the last descriptor - the
        ; hardware owns 0..14 and stops at the tail.
        lea     rax, [e1k_rx_ring]
        mov     rdx, rax
        shr     rdx, 32
        jnz     .ring_high
        lea     rax, [e1k_tx_ring]
        mov     rdx, rax
        shr     rdx, 32
        jnz     .ring_high
        xor     ecx, ecx
.mta:   mov     dword [rdi + E1K_MTA + rcx*4], 0
        inc     ecx
        cmp     ecx, 128
        jb      .mta
        lea     rsi, [e1k_rx_ring]
        lea     rdx, [nic_rx_bufs + VNET_HDR_LEN]
        xor     ecx, ecx
.rx_desc:
        mov     [rsi], rdx              ; the buffer's address
        mov     qword [rsi + 8], 0      ; length, checksum, status, errors, special: zero
        add     rsi, E1K_DESC
        add     rdx, NIC_RX_BUF
        inc     ecx
        cmp     ecx, E1K_RX_DESCS
        jb      .rx_desc
        lea     rax, [e1k_rx_ring]
        mov     [rdi + E1K_RDBAL], eax
        shr     rax, 32
        mov     [rdi + E1K_RDBAH], eax
        mov     dword [rdi + E1K_RDLEN], E1K_RX_DESCS * E1K_DESC
        mov     dword [rdi + E1K_RDH], 0
        mov     dword [rdi + E1K_RDT], 0
        mov     eax, [rdi + E1K_RFCTL]
        and     eax, ~RFCTL_EXSTEN
        mov     [rdi + E1K_RFCTL], eax
        mov     dword [rdi + E1K_MRQC], 0
        mov     dword [rdi + E1K_RCTL], RCTL_EN | RCTL_BAM | RCTL_SECRC
        mov     dword [rdi + E1K_RDT], E1K_RX_DESCS - 1
        mov     dword [e1k_rx_head], 0

        ; Transmit: eight descriptors zeroed, the ring's base, length, head
        ; and tail, the inter-packet gap, TCTL enabled with the standard
        ; collision threshold and distance.
        push    rdi
        lea     rdi, [e1k_tx_ring]
        mov     ecx, E1K_TX_DESCS * E1K_DESC / 8
        xor     eax, eax
        rep     stosq
        pop     rdi
        lea     rax, [e1k_tx_ring]
        mov     [rdi + E1K_TDBAL], eax
        shr     rax, 32
        mov     [rdi + E1K_TDBAH], eax
        mov     dword [rdi + E1K_TDLEN], E1K_TX_DESCS * E1K_DESC
        mov     dword [rdi + E1K_TDH], 0
        mov     dword [rdi + E1K_TDT], 0
        mov     dword [rdi + E1K_TIPG], E1K_TIPG_COPPER
        mov     dword [rdi + E1K_TCTL], TCTL_EN | TCTL_PSP | TCTL_CT | TCTL_COLD
        mov     dword [e1k_tx_idx], 0
        ret
.bar_io:
        lea     rsi, [err_e1k_bar]
        call    serial_err
.no_mac:
        lea     rsi, [err_e1k_mac]
        call    serial_err
.ring_high:
        lea     rsi, [err_e1k_ring]
        call    serial_err

; e1k_send - the Ethernet frame is at nic_tx_buf + TX_BASE, ECX = its
; length (60 or more: net_send padded it and counted it). One legacy
; descriptor at e1k_tx_idx: the address, the length, EOP | IFCS | RS; the
; tail moved past it; its DD awaited - bounded, a dead device being an
; ERR:, not a hang.
e1k_send:
        mov     rdi, [e1k_bar]
        mov     eax, [e1k_tx_idx]
        shl     eax, 4                  ; x E1K_DESC
        lea     rsi, [e1k_tx_ring]
        add     rsi, rax                ; RSI = this send's descriptor
        lea     rax, [nic_tx_buf + TX_BASE]
        mov     [rsi], rax              ; the frame's address
        mov     [rsi + TXD_LEN], cx
        mov     byte [rsi + 10], 0      ; CSO: no checksum offload
        mov     byte [rsi + TXD_CMD], TXD_EOP | TXD_IFCS | TXD_RS
        mov     byte [rsi + TXD_STA], 0
        mov     byte [rsi + 13], 0      ; CSS
        mov     word [rsi + 14], 0      ; special
        sfence
        mov     eax, [e1k_tx_idx]
        inc     eax
        and     eax, E1K_TX_DESCS - 1
        mov     [e1k_tx_idx], eax
        mov     [rdi + E1K_TDT], eax    ; the tail past the descriptor: sent
        mov     r8d, VQ_POLL_TRIES
.poll:
        test    byte [rsi + TXD_STA], TXD_DD
        jnz     .done
        mov     ax, PIT_200US
        call    pit_wait
        dec     r8d
        jnz     .poll
        lea     rsi, [err_nic_tx]
        call    serial_err
.done:
        ret

; e1k_poll - every frame the device has delivered since the last look,
; dispatched by EtherType and its descriptor handed back. Returns EAX = the
; number of frames taken; preserves R12-R14 as the virtio path does.
e1k_poll:
        push    r12
        push    r13
        push    r14
        xor     r14d, r14d              ; frames taken
        mov     r12, [e1k_bar]
.next:
        mov     r13d, [e1k_rx_head]
        mov     eax, r13d
        shl     eax, 4                  ; x E1K_DESC
        lea     rsi, [e1k_rx_ring]
        add     rsi, rax                ; RSI = the head descriptor
        test    byte [rsi + RXD_STATUS], RXD_DD
        jz      .out
        lfence
        inc     r14d
        movzx   ecx, word [rsi + RXD_LEN]       ; ECX = the frame's length, CRC stripped
        cmp     byte [rsi + RXD_ERRORS], 0
        jne     .recycle                ; A4: an errored frame is recycled unread
        test    byte [rsi + RXD_STATUS], RXD_EOP
        jz      .recycle                ; a frame that did not fit one buffer: dropped
        cmp     ecx, ETH_HDR
        jb      .recycle                ; too short to carry a type
        mov     eax, ecx
        add     [obs_page + OBS_BYTES_IN], rax
        mov     eax, r13d
        shl     eax, 11                 ; x NIC_RX_BUF
        lea     rsi, [nic_rx_bufs + VNET_HDR_LEN]
        add     rsi, rax                ; RSI = the Ethernet frame
        cmp     word [rsi + ETH_TYPE], ETHTYPE_ARP
        jne     .not_arp
        call    arp_input
        jmp     .recycle
.not_arp:
        cmp     word [rsi + ETH_TYPE], ETHTYPE_IP
        jne     .recycle
        call    ip_input
.recycle:
        mov     eax, r13d
        shl     eax, 4
        lea     rsi, [e1k_rx_ring]
        add     rsi, rax
        mov     qword [rsi + 8], 0      ; length, status and errors cleared: ours again
        sfence
        mov     [r12 + E1K_RDT], r13d   ; this descriptor back to the hardware
        inc     r13d
        and     r13d, E1K_RX_DESCS - 1
        mov     [e1k_rx_head], r13d
        jmp     .next
.out:
        mov     eax, r14d
        pop     r14
        pop     r13
        pop     r12
        ret

; csum_add - RSI = bytes, ECX = how many, EAX = the running sum in. Returns
; EAX = the running sum out: 16-bit words in memory order added into a
; 32-bit accumulator, an odd trailing byte as the low byte of a final word.
; Byte order does not matter to a one's complement sum as long as the
; result is stored the same way, which csum_fold's caller does. Preserves
; everything but EAX.
csum_add:
        push    rcx
        push    rdx
        push    rsi
.words:
        cmp     ecx, 2
        jb      .odd
        movzx   edx, word [rsi]
        add     eax, edx
        add     rsi, 2
        sub     ecx, 2
        jmp     .words
.odd:
        test    ecx, ecx
        jz      .done
        movzx   edx, byte [rsi]
        add     eax, edx
.done:
        pop     rsi
        pop     rdx
        pop     rcx
        ret

; csum_fold - EAX = a running sum. Returns AX = its one's complement, the
; value to store in a checksum field; a verified header sums to 0xFFFF
; before the complement, so a verifier checks for AX == 0 after it.
csum_fold:
        push    rdx
        mov     edx, eax
        shr     edx, 16
        and     eax, 0xFFFF
        add     eax, edx
        mov     edx, eax
        shr     edx, 16
        and     eax, 0xFFFF
        add     eax, edx                ; two folds cover any 32-bit sum
        not     eax
        and     eax, 0xFFFF
        pop     rdx
        ret

; arp_input - RSI = an Ethernet frame carrying ARP, ECX = its length. A
; request for our address is answered; a reply from the broker's address
; caches its MAC. Anything else is dropped.
arp_input:
        cmp     ecx, ARP_LEN
        jb      .drop
        cmp     word [rsi + ARP_HTYPE], 0x0100  ; Ethernet
        jne     .drop
        cmp     word [rsi + ARP_PTYPE], ETHTYPE_IP
        jne     .drop
        cmp     byte [rsi + ARP_HLEN], 6
        jne     .drop
        cmp     byte [rsi + ARP_PLEN], 4
        jne     .drop
        cmp     word [rsi + ARP_OPER], ARP_OP_REPLY
        je      .reply
        cmp     word [rsi + ARP_OPER], ARP_OP_REQUEST
        jne     .drop
        cmp     dword [rsi + ARP_TPA], OUR_IP
        jne     .drop

        ; A request for us: the reply, built from the request.
        lea     rdi, [nic_tx_buf + TX_BASE]
        push    rsi
        lea     rsi, [rsi + ETH_SRC]            ; to the asker
        movsd
        movsw
        pop     rsi
        push    rsi
        lea     rsi, [nic_mac]                  ; from us
        movsd
        movsw
        pop     rsi
        mov     word [rdi], ETHTYPE_ARP
        mov     word [rdi + 2], 0x0100
        mov     word [rdi + 4], ETHTYPE_IP
        mov     byte [rdi + 6], 6
        mov     byte [rdi + 7], 4
        mov     word [rdi + 8], ARP_OP_REPLY
        add     rdi, 10                         ; sender: our MAC, our IP
        push    rsi
        lea     rsi, [nic_mac]
        movsd
        movsw
        pop     rsi
        mov     dword [rdi], OUR_IP
        add     rdi, 4
        push    rsi
        lea     rsi, [rsi + ARP_SHA]            ; target: the asker's MAC and IP
        movsd
        movsw
        movsd
        pop     rsi
        mov     ecx, ARP_LEN
        call    net_send
        ret
.reply:
        cmp     dword [rsi + ARP_SPA], BROKER_IP
        jne     .drop
        lea     rdi, [broker_mac]
        add     rsi, ARP_SHA
        movsd
        movsw
        mov     dword [broker_mac_ok], 1
.drop:
        ret

; arp_resolve - the broker's MAC into broker_mac, from the cache or by
; asking: a broadcast request, then up to a second of polling, three tries.
; Returns EAX = 1 with the MAC known, or 0. Nothing here halts.
arp_resolve:
        cmp     dword [broker_mac_ok], 0
        jne     .known
        mov     r15d, ARP_TRIES
.try:
        lea     rdi, [nic_tx_buf + TX_BASE]
        mov     eax, -1
        stosd                                   ; broadcast
        stosw
        lea     rsi, [nic_mac]
        movsd
        movsw
        mov     word [rdi], ETHTYPE_ARP
        mov     word [rdi + 2], 0x0100
        mov     word [rdi + 4], ETHTYPE_IP
        mov     byte [rdi + 6], 6
        mov     byte [rdi + 7], 4
        mov     word [rdi + 8], ARP_OP_REQUEST
        add     rdi, 10
        lea     rsi, [nic_mac]                  ; sender: us
        movsd
        movsw
        mov     dword [rdi], OUR_IP
        xor     eax, eax                        ; target MAC unknown
        mov     [rdi + 4], eax
        mov     [rdi + 8], ax
        mov     dword [rdi + 10], BROKER_IP
        mov     ecx, ARP_LEN
        call    net_send

        mov     r14d, ARP_WAIT_TICKS
.wait:
        call    net_poll
        cmp     dword [broker_mac_ok], 0
        jne     .known
        mov     ax, PIT_200US
        call    pit_wait
        dec     r14d
        jnz     .wait
        dec     r15d
        jnz     .try
        xor     eax, eax
        ret
.known:
        mov     eax, 1
        ret

; ip_input - RSI = an Ethernet frame carrying IPv4, ECX = its length. Plain
; 20-byte headers only, addressed to us, unfragmented, checksum verified,
; protocol TCP - anything else is dropped without a word. Hands tcp_input
; RSI = the frame, ECX = the frame length, EDX = the IPv4 payload length.
ip_input:
        cmp     ecx, ETH_HDR + IP_HDR
        jb      .drop
        cmp     byte [rsi + IP_VER], 0x45       ; IPv4, no options
        jne     .drop
        cmp     dword [rsi + IP_DST], OUR_IP
        jne     .drop
        mov     ax, [rsi + IP_FRAG]
        and     ax, 0xFF3F                      ; MF and the fragment offset (memory order)
        jnz     .drop
        cmp     byte [rsi + IP_PROTO], IP_PROTO_TCP
        jne     .drop
        movzx   edx, word [rsi + IP_TOTLEN]
        xchg    dl, dh                          ; total length, host order
        cmp     edx, IP_HDR
        jb      .drop
        lea     eax, [rdx + ETH_HDR]
        cmp     eax, ecx
        ja      .drop                           ; claims more than arrived
        push    rcx
        push    rdx
        push    rsi
        add     rsi, ETH_HDR
        mov     ecx, IP_HDR
        xor     eax, eax
        call    csum_add
        call    csum_fold
        pop     rsi
        pop     rdx
        pop     rcx
        test    ax, ax
        jnz     .drop                           ; a bad header checksum is silence
        sub     edx, IP_HDR                     ; EDX = the payload length
        call    tcp_input
.drop:
        ret

; ip_send - the payload is already at nic_tx_buf + TX_PAYLOAD; ECX = its
; length, DL = the protocol. Builds the Ethernet and IPv4 headers to the
; broker (its MAC must be known), computes the header checksum, sends.
ip_send:
        push    rcx
        push    rdx
        lea     rdi, [nic_tx_buf + TX_BASE]
        lea     rsi, [broker_mac]
        movsd
        movsw
        lea     rsi, [nic_mac]
        movsd
        movsw
        mov     word [rdi], ETHTYPE_IP
        pop     rdx
        pop     rcx
        lea     rdi, [nic_tx_buf + TX_IP]
        mov     byte [rdi + 0], 0x45
        mov     byte [rdi + 1], 0
        lea     eax, [rcx + IP_HDR]
        xchg    al, ah
        mov     [rdi + 2], ax                   ; total length, big endian
        mov     ax, [ip_ident]
        inc     word [ip_ident]
        xchg    al, ah
        mov     [rdi + 4], ax
        mov     word [rdi + 6], 0x0040          ; DF, offset 0 (40 00 in memory)
        mov     byte [rdi + 8], 64              ; TTL
        mov     [rdi + 9], dl
        mov     word [rdi + 10], 0
        mov     dword [rdi + 12], OUR_IP
        mov     dword [rdi + 16], BROKER_IP
        push    rcx
        mov     rsi, rdi
        mov     ecx, IP_HDR
        xor     eax, eax
        call    csum_add
        call    csum_fold
        mov     [rdi + 10], ax
        pop     rcx
        add     ecx, ETH_HDR + IP_HDR
        call    net_send
        ret

; ---------------------------------------------------------------------------
; TCP, client-only (plan decisions 4, 5 and 6): one connection at a time,
; one segment in flight, in-order delivery only, immediate ACKs, MSS 1460
; offered, a 4096-byte window, the guest the active closer, a RST honoured
; from any state. Timers count PIT breaths of 200 us. Nothing here halts:
; every failure is a verdict umbilical_ask turns into "no answer from the
; broker". The connection block is tcb (the TCB_* offsets below); the
; response is assembled by its length prefix into rx_stream. Only the BSP
; calls any of this.
; ---------------------------------------------------------------------------

%define TCB_STATE           0           ; u32  one of TS_*
%define TCB_LPORT           4           ; u32  our port, host order
%define TCB_ISS             8           ; u32  our initial sequence number
%define TCB_SND_NXT         12          ; u32  next sequence number to send
%define TCB_SND_UNA         16          ; u32  oldest unacknowledged
%define TCB_RCV_NXT         20          ; u32  next sequence number expected
%define TCB_PEER_FIN        24          ; u32  the peer has finished sending
%define TCB_PEER_RST        28          ; u32  the peer reset the connection
%define TCB_SIZE            32

%define TS_CLOSED           0
%define TS_SYN_SENT         1
%define TS_ESTABLISHED      2
%define TS_FIN_SENT         3

%define TCP_SPORT           0           ; offsets inside a TCP header
%define TCP_DPORT           2
%define TCP_SEQ             4
%define TCP_ACK             8
%define TCP_DOFF            12
%define TCP_FLAGS           13
%define TCP_WINDOW          14
%define TCP_CSUM            16
%define TCP_URG             18
%define TCP_HDR             20

%define TF_FIN              0x01
%define TF_SYN              0x02
%define TF_RST              0x04
%define TF_PSH              0x08
%define TF_ACK              0x10

%define BROKER_PORT         9999
%define BROKER_PORT_BE      0x0F27      ; 27 0F in memory order
%define FIRST_PORT          49152
%define TCP_WINDOW_BYTES    4096
%define TCP_MSS_OPTION      0xB4050402  ; 02 04 05 B4 in memory order

%define TICKS_PER_SECOND    5000        ; 200 us breaths
%define SYN_TRIES           5
%define DATA_TRIES          5
%define RESPONSE_TICKS      750000      ; 150 s, a question (UMBILICAL.md)
%define GROW_TICKS          3000000     ; 600 s, a request (GERMLINE.md)
%define QUESTION_MAX        498         ; a question's body, bytes
%define REQUEST_BODY_MAX    497         ; a request's body: the marker takes one
%define CLOSE_TICKS         5000        ; a second, then we stop caring

%define RX_STREAM_MAX       (4 + RESPONSE_MAX)
%define RESPONSE_MAX        4096
%define REQUEST_MAX         498

; net_breathe - one 200 us breath of a wait loop: poll the wire, and give
; the working indicator its tick. Preserves everything.
net_breathe:
        push    rax
        push    rcx
        push    rdx
        push    rsi
        push    rdi
        push    rbp
        push    r8
        push    r9
        push    r10
        push    r11
        call    net_poll
        test    eax, eax
        jnz     .polled                 ; something arrived: no nap this breath
        mov     ax, PIT_200US
        call    pit_wait
.polled:
        call    spinner_tick
        pop     r11
        pop     r10
        pop     r9
        pop     r8
        pop     rbp
        pop     rdi
        pop     rsi
        pop     rdx
        pop     rcx
        pop     rax
        ret

; tcp_checksum - RSI = a TCP segment (header and payload), ECX = its length,
; EDX = the peer's IP as it sits in memory. Returns AX = the checksum with
; the pseudo-header folded in. Preserves everything else.
tcp_checksum:
        push    rcx
        push    rdx
        push    rsi
        push    rdi
        lea     rdi, [pseudo_hdr]
        mov     dword [rdi], OUR_IP             ; source, then destination -
        mov     [rdi + 4], edx                  ; order does not change a sum
        mov     byte [rdi + 8], 0
        mov     byte [rdi + 9], IP_PROTO_TCP
        mov     eax, ecx
        xchg    al, ah
        mov     [rdi + 10], ax                  ; TCP length, big endian
        push    rsi
        push    rcx
        mov     rsi, rdi
        mov     ecx, 12
        xor     eax, eax
        call    csum_add
        pop     rcx
        pop     rsi
        call    csum_add
        call    csum_fold
        pop     rdi
        pop     rsi
        pop     rdx
        pop     rcx
        ret

; tcp_output - AL = flags, ECX = payload length (the payload already sits at
; nic_tx_buf + TX_PAYLOAD + TCP_HDR, or + TCP_HDR + 4 when AL has SYN, which
; carries the MSS option), EBX = the sequence number to send. Builds the
; header with the current acknowledgement and window, checksums with the
; pseudo-header, and hands it to ip_send.
tcp_output:
        push    rax
        lea     rdi, [nic_tx_buf + TX_PAYLOAD]
        mov     edx, [tcb + TCB_LPORT]
        xchg    dl, dh
        mov     [rdi + TCP_SPORT], dx
        mov     word [rdi + TCP_DPORT], BROKER_PORT_BE
        mov     edx, ebx
        bswap   edx
        mov     [rdi + TCP_SEQ], edx
        mov     edx, [tcb + TCB_RCV_NXT]
        bswap   edx
        mov     [rdi + TCP_ACK], edx
        mov     edx, 5                          ; header words
        test    al, TF_SYN
        jz      .no_option
        mov     edx, 6
        mov     dword [rdi + TCP_HDR], TCP_MSS_OPTION
.no_option:
        shl     dl, 4
        mov     [rdi + TCP_DOFF], dl
        mov     [rdi + TCP_FLAGS], al
        mov     word [rdi + TCP_WINDOW], (TCP_WINDOW_BYTES >> 8) | ((TCP_WINDOW_BYTES & 0xFF) << 8)
        mov     word [rdi + TCP_CSUM], 0
        mov     word [rdi + TCP_URG], 0
        shr     dl, 4
        movzx   edx, dl
        shl     edx, 2                          ; header bytes
        add     ecx, edx                        ; ECX = the segment length
        mov     rsi, rdi
        mov     edx, BROKER_IP
        call    tcp_checksum
        mov     [rdi + TCP_CSUM], ax
        mov     dl, IP_PROTO_TCP
        call    ip_send
        pop     rax
        ret

; tcp_input - RSI = an Ethernet frame carrying IPv4/TCP, ECX = the frame
; length, EDX = the IPv4 payload length. Ours only (the broker's port to our
; port), checksum verified with the pseudo-header, then the state machine:
; RST from any state; SYN-ACK while connecting; in-order data and FIN while
; established, acknowledged at once; the ACK of our FIN. Must preserve
; R12-R14 (net_poll's loop) - it uses none of them.
tcp_input:
        cmp     edx, TCP_HDR
        jb      .drop
        cmp     dword [tcb + TCB_STATE], TS_CLOSED
        je      .drop
        cmp     dword [rsi + IP_SRC], BROKER_IP
        jne     .drop
        lea     rdi, [rsi + ETH_HDR + IP_HDR]   ; RDI = the TCP header
        cmp     word [rdi + TCP_SPORT], BROKER_PORT_BE
        jne     .drop
        movzx   eax, word [rdi + TCP_DPORT]
        xchg    al, ah
        cmp     eax, [tcb + TCB_LPORT]
        jne     .drop

        push    rsi
        push    rcx
        mov     rsi, rdi
        mov     ecx, edx
        push    rdx
        mov     edx, BROKER_IP
        call    tcp_checksum
        pop     rdx
        pop     rcx
        pop     rsi
        test    ax, ax
        jnz     .drop                           ; a bad checksum is silence

        movzx   ecx, byte [rdi + TCP_DOFF]
        shr     ecx, 4
        shl     ecx, 2                          ; ECX = header bytes
        cmp     ecx, TCP_HDR
        jb      .drop
        cmp     ecx, edx
        ja      .drop
        sub     edx, ecx                        ; EDX = payload bytes
        lea     r8, [rdi + rcx]                 ; R8 = the payload
        movzx   r9d, byte [rdi + TCP_FLAGS]
        mov     r10d, [rdi + TCP_SEQ]
        bswap   r10d                            ; R10D = seq
        mov     r11d, [rdi + TCP_ACK]
        bswap   r11d                            ; R11D = ack

        test    r9d, TF_RST
        jz      .not_rst
        mov     dword [tcb + TCB_PEER_RST], 1
        mov     dword [tcb + TCB_STATE], TS_CLOSED
        ret
.not_rst:
        cmp     dword [tcb + TCB_STATE], TS_SYN_SENT
        jne     .open
        and     r9d, TF_SYN | TF_ACK
        cmp     r9d, TF_SYN | TF_ACK
        jne     .drop
        cmp     r11d, [tcb + TCB_SND_NXT]       ; must acknowledge our SYN
        jne     .drop
        lea     eax, [r10 + 1]
        mov     [tcb + TCB_RCV_NXT], eax
        mov     [tcb + TCB_SND_UNA], r11d
        mov     dword [tcb + TCB_STATE], TS_ESTABLISHED
        jmp     .ack

.open:
        test    r9d, TF_ACK
        jz      .no_ack
        ; Accept an acknowledgement that lies within what is outstanding:
        ; snd_una < ack <= snd_nxt, in modular arithmetic.
        mov     eax, r11d
        sub     eax, [tcb + TCB_SND_UNA]
        mov     ecx, [tcb + TCB_SND_NXT]
        sub     ecx, [tcb + TCB_SND_UNA]
        cmp     eax, ecx
        ja      .no_ack
        mov     [tcb + TCB_SND_UNA], r11d
.no_ack:
        test    edx, edx
        jnz     .has_data
        test    r9d, TF_FIN
        jz      .done                           ; a bare ACK: nothing to answer
.has_data:
        cmp     r10d, [tcb + TCB_RCV_NXT]
        jne     .ack                            ; not the next byte: repeat our ACK
        ; In order: take what fits in the stream, then the FIN if everything fit.
        mov     ecx, [rx_max]                   ; room left in this response's home
        sub     ecx, [rx_len]
        cmp     ecx, edx
        jbe     .take
        mov     ecx, edx
.take:
        push    rsi
        push    rdi
        mov     rsi, r8
        mov     rdi, [rx_dst]                   ; rx_stream, or the component region
        mov     eax, [rx_len]
        add     rdi, rax
        mov     eax, ecx
        rep     movsb
        pop     rdi
        pop     rsi
        add     [rx_len], eax
        add     [tcb + TCB_RCV_NXT], eax
        cmp     eax, edx
        jne     .ack                            ; the rest waits for room
        test    r9d, TF_FIN
        jz      .ack
        inc     dword [tcb + TCB_RCV_NXT]
        mov     dword [tcb + TCB_PEER_FIN], 1
.ack:
        mov     al, TF_ACK
        xor     ecx, ecx
        mov     ebx, [tcb + TCB_SND_NXT]
        call    tcp_output
.done:
.drop:
        ret

; tcp_connect - a fresh port and initial sequence number, SYN sent and
; retransmitted after a second up to SYN_TRIES times. Returns EAX = 1
; established, or 0.
tcp_connect:
        inc     qword [obs_page + OBS_WIRE_CONNS]
        lea     rdi, [tcb]
        mov     ecx, TCB_SIZE / 4
        xor     eax, eax
        rep     stosd
        mov     dword [rx_len], 0
        movzx   eax, word [next_port]   ; a fresh port per question, from
        test    eax, eax                ; FIRST_PORT on the first
        jnz     .have_port
        mov     eax, FIRST_PORT
.have_port:
        mov     [tcb + TCB_LPORT], eax
        inc     eax
        mov     [next_port], ax
        rdtsc
        mov     [tcb + TCB_ISS], eax
        mov     [tcb + TCB_SND_UNA], eax
        inc     eax
        mov     [tcb + TCB_SND_NXT], eax        ; the SYN takes one number
        mov     dword [tcb + TCB_STATE], TS_SYN_SENT
        mov     r15d, SYN_TRIES
.try:
        mov     al, TF_SYN
        xor     ecx, ecx
        mov     ebx, [tcb + TCB_ISS]
        call    tcp_output
        mov     edx, TICKS_PER_SECOND
.wait:
        cmp     dword [tcb + TCB_STATE], TS_ESTABLISHED
        je      .yes
        cmp     dword [tcb + TCB_PEER_RST], 0
        jne     .no
        call    net_breathe
        dec     edx
        jnz     .wait
        dec     r15d
        jnz     .try
.no:
        mov     dword [tcb + TCB_STATE], TS_CLOSED
        xor     eax, eax
        ret
.yes:
        mov     eax, 1
        ret

; tcp_send - RSI = bytes, ECX = how many (at most one segment). Sent with
; PSH|ACK, retransmitted after a second up to DATA_TRIES times, until the
; peer acknowledges every byte. Returns EAX = 1 acknowledged, or 0.
tcp_send:
        mov     [send_ptr], rsi
        mov     [send_len], ecx
        ; The data occupies [snd_una, snd_una + len). snd_nxt advances past it
        ; now, so the peer's acknowledgement of it falls inside the window the
        ; ACK check accepts; each (re)transmission goes out from snd_una.
        mov     eax, [tcb + TCB_SND_UNA]
        add     eax, ecx
        mov     [tcb + TCB_SND_NXT], eax
        mov     [send_want], eax                ; acknowledged when snd_una reaches this
        mov     r15d, DATA_TRIES
.try:
        mov     rsi, [send_ptr]
        mov     ecx, [send_len]
        lea     rdi, [nic_tx_buf + TX_PAYLOAD + TCP_HDR]
        rep     movsb
        mov     al, TF_PSH | TF_ACK
        mov     ecx, [send_len]
        mov     ebx, [tcb + TCB_SND_UNA]        ; retransmit from the oldest unacked
        call    tcp_output
        mov     edx, TICKS_PER_SECOND
.wait:
        mov     eax, [tcb + TCB_SND_UNA]
        cmp     eax, [send_want]
        je      .yes
        cmp     dword [tcb + TCB_PEER_RST], 0
        jne     .no
        call    net_breathe
        dec     edx
        jnz     .wait
        dec     r15d
        jnz     .try
.no:
        xor     eax, eax
        ret
.yes:
        mov     eax, 1
        ret

; tcp_recv_response - waits for one whole response frame at [rx_dst]: the
; length prefix, then that many bytes, within [rx_deadline] breaths. Returns
; EAX = 1 with [rx_len] covering the frame, or 0 on a RST, a FIN before the
; frame is whole, a length above what [rx_max] can hold, or the deadline.
tcp_recv_response:
        mov     edx, [rx_deadline]
.loop:
        mov     eax, [rx_len]
        cmp     eax, 4
        jb      .more
        mov     rdi, [rx_dst]
        mov     ecx, [rdi]                      ; the length prefix
        mov     edi, [rx_max]
        sub     edi, 4
        cmp     ecx, edi                        ; above this response's cap
        ja      .no
        add     ecx, 4
        cmp     eax, ecx
        jae     .yes
.more:
        cmp     dword [tcb + TCB_PEER_RST], 0
        jne     .no
        cmp     dword [tcb + TCB_PEER_FIN], 0
        jne     .no                             ; finished without a whole frame
        call    net_breathe
        dec     edx
        jnz     .loop
.no:
        xor     eax, eax
        ret
.yes:
        mov     eax, 1
        ret

; tcp_close - our FIN, then up to a second for its acknowledgement; either
; way the connection is closed afterwards. A fresh port per question makes
; the rest of the close moot.
tcp_close:
        cmp     dword [tcb + TCB_STATE], TS_ESTABLISHED
        jne     .closed
        mov     al, TF_FIN | TF_ACK
        xor     ecx, ecx
        mov     ebx, [tcb + TCB_SND_NXT]
        call    tcp_output
        inc     dword [tcb + TCB_SND_NXT]       ; the FIN takes one number
        mov     dword [tcb + TCB_STATE], TS_FIN_SENT
        mov     edx, CLOSE_TICKS
.wait:
        mov     eax, [tcb + TCB_SND_UNA]
        cmp     eax, [tcb + TCB_SND_NXT]
        je      .closed
        cmp     dword [tcb + TCB_PEER_RST], 0
        jne     .closed
        call    net_breathe
        dec     edx
        jnz     .wait
.closed:
        mov     dword [tcb + TCB_STATE], TS_CLOSED
        ret

; umbilical_ask - RSI = the question, ECX = its length (1..REQUEST_MAX).
; ARP, connect, one request frame, one response frame, close. Returns
; EAX = 1 with the answer at rx_stream + 4 and its length at [rx_stream],
; or 0: no answer from the broker.
umbilical_ask:
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     [t_wire], rax
        call    umbilical_ask_inner
        push    rax
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        sub     rax, [t_wire]
        add     [obs_page + OBS_WIRE_WAIT], rax
        pop     rax
        ret
umbilical_ask_inner:
        lea     rdi, [req_buf]
        mov     [rdi], ecx                      ; the frame: length, then bytes
        add     rdi, 4
        push    rcx
        rep     movsb
        pop     rcx
        add     ecx, 4
        mov     [req_len], ecx

        call    arp_resolve
        test    eax, eax
        jz      .fail
        call    tcp_connect
        test    eax, eax
        jz      .fail
        lea     rsi, [req_buf]
        mov     ecx, [req_len]
        call    tcp_send
        test    eax, eax
        jz      .fail_close
        call    tcp_recv_response
        test    eax, eax
        jz      .fail_close
        call    tcp_close
        mov     eax, 1
        ret
.fail_close:
        call    tcp_close
.fail:
        xor     eax, eax
        ret

; parse_marker - the line buffer, read by GERMLINE.md's rule ("What is a
; question, what is a request"). Returns EAX = '?' for a question, '!' for a
; request, or 0 for a note (the line buffer left for notebook_append). For a
; marker line RSI and ECX are the body - the bytes after the marker with
; leading and trailing spaces removed, cut at the wire's maximum - and the
; line buffer is emptied: a marker line is never a note. Clobbers RDX.
parse_marker:
        lea     rsi, [line_buf]
        mov     ecx, [line_len]
.lead:
        test    ecx, ecx
        jz      .note
        cmp     byte [rsi], ' '
        jne     .first
        inc     rsi
        dec     ecx
        jmp     .lead
.first:
        movzx   eax, byte [rsi]
        cmp     al, '?'
        je      .marker
        cmp     al, '!'
        jne     .note
.marker:
        inc     rsi                     ; past the marker
        dec     ecx
.body_lead:
        test    ecx, ecx
        jz      .trimmed
        cmp     byte [rsi], ' '
        jne     .body_trail
        inc     rsi
        dec     ecx
        jmp     .body_lead
.body_trail:                            ; ECX >= 1 and [RSI] is not a space here
        cmp     byte [rsi + rcx - 1], ' '
        jne     .trimmed
        dec     ecx
        jmp     .body_trail
.trimmed:
        mov     edx, QUESTION_MAX
        cmp     al, '?'
        je      .cap
        mov     edx, REQUEST_BODY_MAX
.cap:
        cmp     ecx, edx
        jbe     .done
        mov     ecx, edx
.done:
        mov     dword [line_len], 0
        ret
.note:
        xor     eax, eax
        ret

; ask_question - RSI = the question, ECX = its length. Sends it to the
; broker as UMBILICAL.md's request frame, shows the working indicator
; meanwhile, draws the answer or the no-answer line, discards any keys
; pressed during the wait, and prompts. An empty question sends nothing and
; says so. Console only: nothing here reaches the wire.
ask_question:
        test    ecx, ecx
        jnz     .ask
        lea     rsi, [msg_nothing_ask]
        call    console_puts
        inc     qword [obs_page + OBS_ERRORS]
        jmp     finish_line
.ask:
        inc     qword [obs_page + OBS_QUESTIONS]
        mov     qword [obs_page + OBS_MODE], MODE_ASKING
        lea     rax, [rx_stream]        ; the answer lands in the 4 KB stream
        mov     [rx_dst], rax
        mov     dword [rx_max], RX_STREAM_MAX
        mov     dword [rx_deadline], RESPONSE_TICKS
        call    spinner_start
        call    umbilical_ask
        push    rax
        call    spinner_stop
        pop     rax
        test    eax, eax
        jz      .no_answer
        mov     ecx, [rx_stream]        ; the response frame: length, then bytes
        lea     rsi, [rx_stream + 4]
        call    draw_answer
        jmp     finish_line
.no_answer:
        lea     rsi, [msg_no_answer]
        call    console_puts
        inc     qword [obs_page + OBS_ERRORS]
        jmp     finish_line

; grow_request - RSI = the body, ECX = its length. GERMLINE.md's grow
; request - the marker byte 0x01, then the body - goes to the broker with
; the response received straight into the component region under the 600 s
; deadline. A refusal is drawn like an answer; a component frame is checked
; against the document and run; anything else is named. An empty body
; sends nothing and says so. Console only.
grow_request:
        test    ecx, ecx
        jnz     .grow
        lea     rsi, [msg_nothing_grow]
        call    console_puts
        inc     qword [obs_page + OBS_ERRORS]
        jmp     finish_line
.grow:
        call    app_close_if_running    ; one app at a time (GLASS.md)
        inc     qword [obs_page + OBS_REQUESTS]
        mov     qword [obs_page + OBS_MODE], MODE_GROWING
        call    body_is_install         ; "install ..." says so on the strip
        test    eax, eax
        jz      .mode_set
        mov     qword [obs_page + OBS_MODE], MODE_INSTALLING
.mode_set:
        lea     rdi, [grow_buf]
        mov     byte [rdi], 0x01        ; the grow marker
        inc     rdi
        push    rcx
        rep     movsb
        pop     rcx
        inc     ecx                     ; the marker counts
        lea     rsi, [grow_buf]
        lea     rax, [comp_region + COMP_RX_OFF]
        mov     [rx_dst], rax
        mov     dword [rx_max], COMP_RX_MAX
        mov     dword [rx_deadline], GROW_TICKS
        call    spinner_start
        call    umbilical_ask
        push    rax
        call    spinner_stop
        pop     rax
        test    eax, eax
        jz      .no_answer
        lea     rsi, [comp_region + COMP_RX_OFF]
        mov     ecx, [rsi]              ; N
        add     rsi, 4                  ; the content: the kind byte first
        test    ecx, ecx
        jz      .bad
        mov     al, [rsi]
        test    al, al
        jz      .refusal
        cmp     al, APP_KIND            ; kind 0x01 - a Stage 5 component -
        jne     .bad                    ; has no callbacks: bad component frame
        call    app_valid               ; RSI = the content, ECX = N
        test    eax, eax
        jz      .bad
        cmp     byte [rsi + APPH_INSTALLED], 1
        jne     .run
        call    home_install            ; kept on the home image first (HOME.md)
.run:
        call    run_app
        jmp     finish_line
.refusal:
        inc     rsi
        dec     ecx
        call    draw_answer
        inc     qword [obs_page + OBS_ERRORS]
        jmp     finish_line
.no_answer:
        lea     rsi, [msg_no_answer]
        call    console_puts
        inc     qword [obs_page + OBS_ERRORS]
        jmp     finish_line
.bad:
        lea     rsi, [msg_bad_frame]
        call    console_puts
        inc     qword [obs_page + OBS_ERRORS]
        jmp     finish_line

; app_valid - RSI = an app frame's content (the kind byte first), ECX =
; its length N. EAX = 1 if it is what GLASS.md describes - ABI 2, source 0
; or 1, byte 3 zero, L in 16..cap, N = 96 + L, a name of 1..32 printable
; bytes NUL-padded, installed 0 or 1, bytes 41-43 zero, four choice slots
; each empty (all zero) or a printable key with a 1..12 byte printable
; NUL-padded label, packed from the first, and four callback offsets each
; below L - else 0. Preserves RSI and ECX; clobbers RAX, RDX, RDI, R8-R11.
app_valid:
        cmp     ecx, APP_HDR + BLOB_HDR
        jb      .no
        cmp     byte [rsi + APPH_ABI], APP_ABI
        jne     .no
        cmp     byte [rsi + APPH_SOURCE], 1
        ja      .no
        cmp     byte [rsi + 3], 0
        jne     .no
        mov     edx, [rsi + APPH_LEN]   ; L
        cmp     edx, BLOB_HDR
        jb      .no
        cmp     edx, COMP_BLOB_MAX
        ja      .no
        lea     eax, [rdx + APP_HDR]
        cmp     eax, ecx
        jne     .no
        ; the name: printable bytes, then NUL padding, at least one byte
        lea     rdi, [rsi + APPH_NAME]
        mov     r8d, APP_NAME_MAX
        call    padded_text
        test    eax, eax
        jz      .no
        cmp     byte [rsi + APPH_INSTALLED], 1
        ja      .no
        cmp     byte [rsi + APPH_INSTALLED + 1], 0
        jne     .no
        cmp     word [rsi + APPH_INSTALLED + 2], 0
        jne     .no
        ; the choices: packed from the first; an empty slot all zero
        lea     rdi, [rsi + APPH_CHOICES]
        call    choices_valid
        test    eax, eax
        jz      .no
        ; the blob's four offsets, each below L
        lea     rdi, [rsi + APP_HDR]
        mov     edx, [rsi + APPH_LEN]
        mov     r9d, 4
.offset:
        mov     eax, [rdi]
        cmp     eax, edx
        jae     .no
        add     rdi, 4
        dec     r9d
        jnz     .offset
        ; A blob that announces point (ring 6c, GLASS.md "An app is five
        ; callbacks, when it says so"): L at least 28, POINTER2 at 16, the
        ; u32 at 24 in [28, L). Without the magic it is a four-callback app.
        lea     rdi, [rsi + APP_HDR]
        call    blob_has_point          ; EAX = 1 with the magic, else 0
        test    eax, eax
        jz      .valid
        mov     eax, [rdi + CB_POINT]
        cmp     eax, POINT_HDR
        jb      .no
        cmp     eax, edx
        jae     .no
.valid:
        mov     eax, 1
        ret
.no:
        xor     eax, eax
        ret

; blob_has_point - RDI = a blob's first byte, EDX = its length L: EAX = 1
; when L >= 28 and bytes 16-23 read POINTER2, else 0. Preserves the rest.
blob_has_point:
        xor     eax, eax
        cmp     edx, POINT_HDR
        jb      .out
        push    rcx
        mov     rcx, [rdi + POINT_MAGIC_OFF]
        push    rdx
        mov     rdx, 'POINTER2'
        cmp     rcx, rdx
        pop     rdx
        pop     rcx
        jne     .out
        mov     eax, 1
.out:
        ret

; choices_valid - RDI = four 13-byte choice slots (a frame's, or a home
; entry's): EAX = 1 if each is empty (all zero) or a printable key with a
; 1..12 byte printable NUL-padded label, packed from the first - else 0.
; Preserves RDI; clobbers RAX, R8-R11.
choices_valid:
        push    rdi
        mov     r9d, APP_CHOICES
        xor     r10d, r10d              ; 1 once an empty slot was seen
.slot:
        movzx   eax, byte [rdi]
        test    al, al
        jnz     .used
        mov     r11d, APP_CHOICE_BYTES  ; every byte of an empty slot zero
.zero:
        cmp     byte [rdi + r11 - 1], 0
        jne     .no
        dec     r11d
        jnz     .zero
        mov     r10d, 1
        jmp     .next_slot
.used:
        test    r10d, r10d
        jnz     .no                     ; a used slot after an empty one
        cmp     al, 0x20
        jb      .no
        cmp     al, 0x7E
        ja      .no
        push    rdi
        inc     rdi
        mov     r8d, APP_LABEL_MAX
        call    padded_text
        pop     rdi
        test    eax, eax
        jz      .no
.next_slot:
        add     rdi, APP_CHOICE_BYTES
        dec     r9d
        jnz     .slot
        mov     eax, 1
        pop     rdi
        ret
.no:
        xor     eax, eax
        pop     rdi
        ret

; padded_text - RDI = a field of R8D bytes: EAX = 1 if it is one or more
; printable bytes followed only by NULs, else 0. Clobbers RAX, R8, R11.
padded_text:
        xor     r11d, r11d              ; bytes of text seen
.byte:
        test    r8d, r8d
        jz      .end
        movzx   eax, byte [rdi + r11]
        test    al, al
        jz      .pad
        cmp     al, 0x20
        jb      .bad
        cmp     al, 0x7E
        ja      .bad
        inc     r11d
        dec     r8d
        jmp     .byte
.pad:
        cmp     byte [rdi + r11], 0     ; the rest must be NUL
        jne     .bad
        inc     r11d
        dec     r8d
        jnz     .pad
.end:
        test    r11d, r11d
        jz      .bad
        movzx   eax, byte [rdi]         ; the first byte was text?
        test    al, al
        jz      .bad
        mov     eax, 1
        ret
.bad:
        xor     eax, eax
        ret

; run_app - the loader (GLASS.md, "Running an app"). The frame has been
; received into the component region and checked; the blob's first byte
; is at comp_region + APP_BLOB_OFF. The name and the choices are copied
; out of the header, the source counted, the app panel cleared, the mode,
; focus, strip name and choices row set, and init called with RDI = the
; service table. Clobbers registers freely.
run_app:
        lea     rsi, [comp_region + COMP_RX_OFF + 4]    ; the content
        lea     rdi, [obs_page + OBS_NAME]
        push    rsi
        add     rsi, APPH_NAME
        mov     ecx, APP_NAME_MAX
        rep     movsb
        pop     rsi
        push    rsi
        add     rsi, APPH_CHOICES
        lea     rdi, [app_choices]
        mov     ecx, APP_CHOICES * APP_CHOICE_BYTES
        rep     movsb
        pop     rsi
        cmp     dword [launch_home], 0  ; a launch from the home image received
        jne     .counted                ; no frame: neither counter moves
        cmp     byte [rsi + APPH_SOURCE], 0
        jne     .served
        inc     qword [obs_page + OBS_GROWS_GEN]
        jmp     .counted
.served:
        inc     qword [obs_page + OBS_GROWS_SERVED]
.counted:
        call    app_clear
        ; Does the blob announce point? A launch from the home image and a
        ; delivered frame alike: the blob is in the region either way.
        push    rsi
        lea     rdi, [comp_region + APP_BLOB_OFF]
        mov     edx, [rsi + APPH_LEN]
        call    blob_has_point
        mov     [app_has_point], eax
        pop     rsi
        mov     dword [app_running], 1
        mov     qword [obs_page + OBS_MODE], MODE_RUNNING
        mov     qword [obs_page + OBS_FOCUS], FOCUS_APP
        mov     qword [obs_page + OBS_STEPS], 0
        mov     qword [obs_page + OBS_STEP_LAST], 0
        mov     qword [obs_page + OBS_STEP_WORST], 0
        mov     qword [step_begin], 0
        call    choices_update
        mov     eax, CB_INIT
        lea     rdi, [svc_table]
        call    app_call
        ret

; app_call - EAX = the callback's slot in the blob's header (0, 4, 8, 12,
; or 24 for point); RDI, RSI, RDX = its arguments, untouched here. The call
; into the grown code: RSP 16-aligned, kept in memory because the callback
; may clobber every register but RSP.
app_call:
        lea     r11, [comp_region + APP_BLOB_OFF]
        mov     eax, [r11 + rax]        ; the offset
        add     rax, r11
        mov     [saved_rsp], rsp
        and     rsp, -16
        call    rax                     ; the grown code runs here
        mov     rsp, [saved_rsp]
        cld                             ; the contract says clear; be sure
        ret

; app_step_maybe - step, if at least STEP_GAP_MS have passed since the
; previous step began; timed for the obs page. Clobbers registers freely.
app_step_maybe:
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     rdx, rax
        sub     rdx, [step_begin]
        cmp     rdx, [step_gap]
        jb      .not_yet
        mov     [step_begin], rax
        mov     eax, CB_STEP
        xor     edi, edi
        call    app_call
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        sub     rax, [step_begin]
        mov     [obs_page + OBS_STEP_LAST], rax
        cmp     rax, [obs_page + OBS_STEP_WORST]
        jbe     .no_worst
        mov     [obs_page + OBS_STEP_WORST], rax
.no_worst:
        inc     qword [obs_page + OBS_STEPS]
.not_yet:
        ret

; app_key - EDI = the key: the app's key callback.
app_key:
        mov     eax, CB_KEY
        call    app_call
        ret

; app_close_if_running - a request while an app runs closes it first.
app_close_if_running:
        cmp     dword [app_running], 0
        je      .none
        call    app_close
.none:
        ret

; app_close - exit called, the app panel cleared, the prompt's mode, focus
; and choices row back, the name empty. The conversation is untouched.
app_close:
        mov     eax, CB_EXIT
        xor     edi, edi
        call    app_call
        mov     dword [app_running], 0
        call    app_clear
        mov     qword [obs_page + OBS_MODE], MODE_PROMPT
        mov     qword [obs_page + OBS_FOCUS], FOCUS_PROMPT
        lea     rdi, [obs_page + OBS_NAME]
        mov     ecx, APP_NAME_MAX / 8
        xor     eax, eax
        rep     stosq
        call    choices_update
        ret

; choices_update - the choices row for the state (GLASS.md, "The choices
; row"): no app; the app with the keys (its first three choices, Esc exit,
; Tab prompt); the prompt with the keys beside a running app.
choices_update:
        call    hit_reset               ; the click targets follow the row (ring 6c)
        cmp     dword [app_running], 0
        jne     .running
        ; No app: the markers, then up to three installed apps as "! <name>"
        ; in table order (HOME.md, "The choices row") - five items at most.
        lea     rdi, [choices_line]
        lea     rsi, [msg_choices_prompt]
        mov     ecx, msg_choices_prompt_len
        rep     movsb
        xor     eax, eax                ; "? ask" at 0-4, "! grow" at 8-13
        mov     edx, 4
        mov     ecx, HIT_KEY | '?' << 8
        call    hit_add
        mov     eax, 8
        mov     edx, 13
        mov     ecx, HIT_KEY | '!' << 8
        call    hit_add
        cmp     dword [home_present], 0
        je      .prompt_done
        xor     r8d, r8d                ; the entry index
        xor     r9d, r9d                ; items shown
.prompt_entry:
        cmp     r9d, APP_CHOICES_SHOWN
        jae     .prompt_done
        lea     rax, [home_valid]
        cmp     byte [rax + r8], 0
        je      .prompt_next
        mov     eax, '   '              ; three spaces between items
        stosw
        mov     al, ' '
        stosb
        lea     rax, [choices_line]
        mov     r10, rdi
        sub     r10, rax                ; R10 = the item's first column
        mov     al, '!'
        stosb
        mov     al, ' '
        stosb
        lea     rsi, [home_table]
        mov     eax, r8d
        shl     eax, 8
        add     rsi, rax
        mov     ecx, APP_NAME_MAX
.prompt_name:
        lodsb
        test    al, al
        jz      .prompt_named
        stosb
        dec     ecx
        jnz     .prompt_name
.prompt_named:
        lea     rax, [choices_line]
        mov     rdx, rdi
        sub     rdx, rax
        dec     edx                     ; the item's last column
        mov     eax, r10d
        mov     ecx, r8d
        shl     ecx, 8
        or      ecx, HIT_LAUNCH         ; the launch of entry R8
        call    hit_add
        inc     r9d
.prompt_next:
        inc     r8d
        cmp     r8d, HOME_ENTRIES
        jb      .prompt_entry
.prompt_done:
        lea     rsi, [choices_line]
        mov     rcx, rdi
        sub     rcx, rsi
        call    choices_set
        ret
.running:
        cmp     qword [obs_page + OBS_FOCUS], FOCUS_APP
        je      .app_keys
        lea     rsi, [msg_choices_prompt_app]
        mov     ecx, msg_choices_prompt_app_len
        call    choices_set
        ; "? ask   ! grow   Tab app   Esc exit": 0-4, 8-13, 17-23, 27-34.
        xor     eax, eax
        mov     edx, 4
        mov     ecx, HIT_KEY | '?' << 8
        call    hit_add
        mov     eax, 8
        mov     edx, 13
        mov     ecx, HIT_KEY | '!' << 8
        call    hit_add
        mov     eax, 17
        mov     edx, 23
        mov     ecx, HIT_KEY | 9 << 8
        call    hit_add
        mov     eax, 27
        mov     edx, 34
        mov     ecx, HIT_KEY | 0x1B << 8
        call    hit_add
        ret
.app_keys:
        lea     rdi, [choices_line]
        lea     rsi, [app_choices]
        mov     r8d, APP_CHOICES_SHOWN
.choice:
        movzx   eax, byte [rsi]
        test    al, al
        jz      .choices_done
        lea     rdx, [choices_line]
        mov     r10, rdi
        sub     r10, rdx                ; R10 = the item's first column
        mov     r11d, eax               ; R11 = its key
        stosb                           ; the key
        mov     al, ' '
        stosb
        push    rsi
        inc     rsi
        mov     ecx, APP_LABEL_MAX
.label:
        lodsb
        test    al, al
        jz      .label_done
        stosb
        dec     ecx
        jnz     .label
.label_done:
        pop     rsi
        lea     rdx, [choices_line]
        push    rdi
        sub     rdi, rdx
        dec     edi                     ; the item's last column
        mov     edx, edi
        pop     rdi
        mov     eax, r10d
        mov     ecx, r11d
        shl     ecx, 8
        or      ecx, HIT_KEY
        call    hit_add
        mov     eax, '   '              ; three spaces between items
        stosw
        mov     al, ' '
        stosb
        add     rsi, APP_CHOICE_BYTES
        dec     r8d
        jnz     .choice
.choices_done:
        lea     rdx, [choices_line]
        mov     rax, rdi
        sub     rax, rdx                ; the tail's first column: "Esc exit" then "Tab prompt"
        mov     edx, eax
        add     edx, 7
        mov     ecx, HIT_KEY | 0x1B << 8
        call    hit_add
        add     eax, 11
        mov     edx, eax
        add     edx, 9
        mov     ecx, HIT_KEY | 9 << 8
        call    hit_add
        push    rdi
        lea     rsi, [msg_choices_app_tail]
        mov     ecx, msg_choices_app_tail_len
        rep     movsb
        pop     rax
        lea     rsi, [choices_line]
        mov     rcx, rdi
        sub     rcx, rsi
        call    choices_set
        ret

; draw_answer - RSI = bytes, ECX = how many: drawn through console_putc from
; the cursor, LF a new line, anything outside the wire's alphabet ignored
; (the broker never sends it). Console only.
draw_answer:
.draw:
        test    ecx, ecx
        jz      .done
        lodsb
        dec     ecx
        cmp     al, 10
        je      .draw_byte
        cmp     al, 0x20
        jb      .draw
        cmp     al, 0x7E
        ja      .draw
.draw_byte:
        call    console_putc
        jmp     .draw
.done:
        ret

; console_puts - RSI = a NUL-terminated string, drawn on the console only.
; Preserves everything.
console_puts:
        push    rax
        push    rsi
.next:
        lodsb
        test    al, al
        jz      .done
        call    console_putc
        jmp     .next
.done:
        pop     rsi
        pop     rax
        ret

; finish_line - after an answer, a refusal or a console line: a fresh line
; unless we already start one; the keys pressed meanwhile discarded (they
; showed nothing, so they do nothing - the screen owes the user no invisible
; debt); the prompt. Jumped to from the routines above, so its ret is theirs.
finish_line:
        mov     qword [obs_page + OBS_MODE], MODE_PROMPT
        cmp     dword [app_running], 0
        je      .mode_set
        mov     qword [obs_page + OBS_MODE], MODE_RUNNING
.mode_set:
        cmp     dword [cur_col], 0
        je      .discard
        mov     al, 10
        call    console_putc
.discard:
        cli
        mov     eax, [kbd_head]
        mov     [kbd_tail], eax
        mov     dword [kbd_e0], 0
        mov     eax, [mse_head]         ; presses made while the machine was
        mov     [mse_tail], eax         ; busy are dropped like those keys
        sti
        call    console_prompt
        ret

; run_component - the loader (GERMLINE.md, "The entry contract" and "What
; the screen does around a component"). The frame has been received into
; the component region and checked; the blob's first byte is at
; comp_region + COMP_BLOB_OFF. The framebuffer is cleared (the shadow
; kept), the blob is called with RDI = the service table and RSP 16-aligned,
; on the BSP's own stack, interrupts enabled; when it returns the console is
; re-rendered from the shadow. The component may clobber every register but
; RSP, so RSP is kept in memory, not a register. Clobbers registers freely.
run_component:
        call    app_clear
        lea     rdi, [svc_table]
        lea     rax, [comp_region + COMP_BLOB_OFF]
        mov     [saved_rsp], rsp
        and     rsp, -16
        call    rax                     ; the grown code runs here
        mov     rsp, [saved_rsp]
        cld                             ; the contract says clear; be sure
        call    console_redraw
        ret

; svc_draw_text - RDI = row, RSI = column (panel-relative), RDX = the
; bytes, RCX = how many. Each byte into the next cell along the row of the
; app panel, stopping at its right edge; a row outside the panel draws
; nothing; a byte outside 0x20-0x7E draws as a space. Cells only: the glass
; core paints them. Preserves RBX, RBP, RSP, R12-R15 (the service contract).
svc_draw_text:
        push    rbx
        push    r12
        push    r13
        push    r14
        push    r15
        mov     r12, rdi                ; row
        mov     r13, rsi                ; column
        mov     r14, rdx                ; the bytes
        mov     r15, rcx                ; how many
        mov     eax, [app_rows]
        cmp     r12, rax
        jae     .done
.next:
        test    r15, r15
        jz      .done
        mov     eax, [app_cols]
        cmp     r13, rax
        jae     .done                   ; the right edge
        movzx   eax, byte [r14]
        cmp     al, 0x20
        jb      .space
        cmp     al, 0x7E
        jbe     .draw
.space:
        mov     eax, ' '
.draw:
        mov     ebx, r12d
        mov     ecx, r13d
        call    app_put
        inc     r14
        inc     r13
        dec     r15
        jmp     .next
.done:
        pop     r15
        pop     r14
        pop     r13
        pop     r12
        pop     rbx
        ret

; svc_panel_size - RAX = cols | rows << 32 of the app panel.
svc_panel_size:
        mov     eax, [app_cols]
        mov     edx, [app_rows]
        shl     rdx, 32
        or      rax, rdx
        ret

; svc_fill - RDI = row, RSI = column, RDX = rows, RCX = columns, R8 = the
; colour: 0 the background, 1 the foreground block, anything else the
; background; the rectangle clipped to the panel. Preserves RBX, RBP,
; RSP, R12-R15.
svc_fill:
        push    rbx
        push    r12
        push    r13
        push    r14
        push    r15
        mov     r12, rdi                ; row
        mov     r13, rsi                ; column
        mov     r14, rdx                ; rows
        mov     r15, rcx                ; columns
        mov     eax, ' '
        cmp     r8, 1
        jne     .colour
        mov     eax, CELL_BLOCK
.colour:
        mov     r8d, eax
.row:
        test    r14, r14
        jz      .done
        mov     eax, [app_rows]
        cmp     r12, rax
        jae     .done
        mov     rcx, r13
        mov     rdx, r15
.col:
        test    rdx, rdx
        jz      .next_row
        mov     eax, [app_cols]
        cmp     rcx, rax
        jae     .next_row
        mov     eax, r8d
        mov     ebx, r12d
        call    app_put
        inc     rcx
        dec     rdx
        jmp     .col
.next_row:
        inc     r12
        dec     r14
        jmp     .row
.done:
        pop     r15
        pop     r14
        pop     r13
        pop     r12
        pop     rbx
        ret

; The working indicator: one cell at column 0 of the fresh line, cycling
; - \ | / every SPIN_TICKS breaths of 200 us (about four times a second),
; erased when the wait ends. Console only.
%define SPIN_TICKS          1250

spinner_start:
        mov     dword [spin_phase], 0
        mov     dword [spin_count], 0
        mov     al, '-'
        call    console_putc
        ret

; spinner_tick - called once per breath by net_breathe. Preserves everything.
spinner_tick:
        push    rax
        push    rbx
        push    rdx
        inc     dword [spin_count]
        cmp     dword [spin_count], SPIN_TICKS
        jb      .done
        mov     dword [spin_count], 0
        mov     eax, [spin_phase]
        inc     eax
        and     eax, 3
        mov     [spin_phase], eax
        lea     rbx, [spin_chars]
        movzx   edx, byte [rbx + rax]
        mov     al, 8                   ; back to column 0 (this blanks it)...
        call    console_putc
        mov     al, dl                  ; ...and draw the next glyph there,
        call    console_putc            ; leaving the cursor at column 1
.done:
        pop     rdx
        pop     rbx
        pop     rax
        ret

; spinner_stop - erase the indicator cell, leaving column 0 blank and the
; cursor on it, ready for the answer. The cursor sits at column 1 (just past
; the glyph), so one backspace blanks column 0 and lands there.
spinner_stop:
        push    rax
        mov     al, 8
        call    console_putc
        pop     rax
        ret

; ---------------------------------------------------------------------------
; The notebook - stage3/NOTEBOOK.md in code. Sector 0 is the header; the
; journal is one note per sector from sector 1; the journal ends at the first
; sector that is not a valid record. The reader here and the checker on the
; host apply the same rule, byte for byte. Only the BSP calls any of this.
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

; notebook_replay - draw every note on the console, in order, one per line
; from column 0, text only. Console only: nothing here touches the wire.
; Called once from efi_main after "S7: keyboard ready"; clobbers registers.
notebook_replay:
        mov     ebx, 1
.note:
        cmp     ebx, [nb_count]
        ja      .done
        mov     eax, VBLK_T_IN
        lea     rdi, [sector_buf]
        call    disk_rw
        movzx   ecx, word [sector_buf + 8]
        lea     rsi, [sector_buf + NB_TEXT_OFF]
.char:
        lodsb
        call    console_putc
        dec     ecx
        jnz     .char
        mov     al, 10
        call    console_putc
        inc     ebx
        jmp     .note
.done:
        ret

; notebook_append - the line buffer becomes the next record on disk, written
; through before this returns; the buffer is emptied. An empty line is not a
; note, and a full journal drops the line and carries on (plan decisions 6
; and 8). Called from the main loop on Enter. Preserves everything.
notebook_append:
        push    rax
        push    rbx
        push    rcx
        push    rsi
        push    rdi
        mov     ecx, [line_len]
        test    ecx, ecx
        jz      .out
        mov     ebx, [nb_next]
        cmp     ebx, [disk_sectors]
        jae     .full

        lea     rdi, [rec_buf]          ; a clean record
        push    rcx
        mov     ecx, 64
        xor     eax, eax
        rep     stosq
        pop     rcx
        mov     dword [rec_buf], 'NOTE'
        mov     eax, [nb_count]
        inc     eax
        mov     [rec_buf + 4], eax      ; sequence
        mov     [rec_buf + 8], cx       ; length
        lea     rsi, [line_buf]
        lea     rdi, [rec_buf + NB_TEXT_OFF]
        rep     movsb

        mov     eax, VBLK_T_OUT
        lea     rdi, [rec_buf]
        call    disk_rw                 ; returns only once the device says OK

        inc     dword [nb_count]
        inc     dword [nb_next]
        mov     eax, [nb_count]
        mov     [obs_page + OBS_NOTES], rax
.full:
        mov     dword [line_len], 0
.out:
        pop     rdi
        pop     rsi
        pop     rcx
        pop     rbx
        pop     rax
        ret

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
; glass_init - the four regions from the mode (GLASS.md, "The screen"),
; their surfaces cleared and every row dirty, the descriptors in the obs
; page, the choices row for the prompt. A mode too small is a named error,
; shown once by the boot processor before the halt. Called before
; console_init; clobbers registers freely.
glass_init:
        mov     eax, [fb_width]
        shr     eax, 4                  ; /16: cells across
        mov     [scr_cols], eax
        mov     ecx, [fb_height]
        shr     ecx, 4
        mov     [scr_rows], ecx
        cmp     eax, 8
        jb      .too_small
        cmp     ecx, 8
        jb      .too_small
        cmp     eax, STRIP_CELLS / 2
        ja      .too_small
        mov     edx, eax
        shr     edx, 1                  ; the conversation's columns
        mov     [con_cols], edx
        sub     eax, edx                ; the app panel's
        mov     [app_cols], eax
        sub     ecx, 4                  ; the panels' rows
        mov     [con_rows], ecx
        mov     [app_rows], ecx
        mov     eax, ecx
        mul     dword [con_cols]
        test    edx, edx
        jnz     .too_small
        cmp     eax, PANEL_CELLS
        ja      .too_small
        mov     eax, ecx
        mul     dword [app_cols]
        test    edx, edx
        jnz     .too_small
        cmp     eax, PANEL_CELLS
        ja      .too_small
        cmp     ecx, SURF_ROWS_MAX
        ja      .too_small

        ; The descriptors: strip, choices, conversation, app.
        lea     rbp, [obs_page + OBS_SURF_STRIP]
        lea     rax, [strip_cells]
        lea     rdx, [strip_dirty]
        xor     ecx, ecx                ; row0 0, col0 0
        xor     r8d, r8d
        mov     r9d, 2
        mov     r10d, [scr_cols]
        call    surf_describe
        lea     rbp, [obs_page + OBS_SURF_CHOICES]
        lea     rax, [choices_cells]
        lea     rdx, [choices_dirty]
        mov     ecx, [scr_rows]
        sub     ecx, 2
        xor     r8d, r8d
        mov     r9d, 2
        mov     r10d, [scr_cols]
        call    surf_describe
        lea     rbp, [obs_page + OBS_SURF_CONV]
        lea     rax, [shadow]
        lea     rdx, [conv_dirty]
        mov     ecx, 2
        xor     r8d, r8d
        mov     r9d, [con_rows]
        mov     r10d, [con_cols]
        call    surf_describe
        lea     rbp, [obs_page + OBS_SURF_APP]
        lea     rax, [app_cells]
        lea     rdx, [app_dirty]
        mov     ecx, 2
        mov     r8d, [con_cols]
        mov     r9d, [app_rows]
        mov     r10d, [app_cols]
        call    surf_describe

        lea     rsi, [msg_choices_prompt]
        mov     ecx, msg_choices_prompt_len
        call    choices_set
        ret
.too_small:
        lea     rsi, [err_too_small]
        call    glass_err

; surf_describe - RBP = the descriptor, RAX = cells, RDX = dirty bytes,
; ECX = row0, R8D = col0, R9D = rows, R10D = cols. Fills the descriptor,
; clears the cells to spaces and marks every row dirty.
surf_describe:
        mov     r11, rdx                ; mul below clobbers RDX
        mov     [rbp + SURF_CELLS], rax
        mov     [rbp + SURF_DIRTY], rdx
        mov     [rbp + SURF_ROW0], rcx
        mov     [rbp + SURF_COL0], r8
        mov     [rbp + SURF_ROWS], r9
        mov     [rbp + SURF_COLS], r10
        mov     qword [rbp + SURF_CURSOR], 0
        mov     rdi, rax
        mov     eax, r9d
        mul     r10d
        mov     ecx, eax
        mov     al, ' '
        rep     stosb
        mov     rdi, r11
        mov     ecx, r9d
        mov     al, 1
        rep     stosb
        ret

; surf_dirty_all - RBP = a descriptor: every row dirty. Preserves everything.
surf_dirty_all:
        push    rax
        push    rcx
        push    rdi
        mov     rdi, [rbp + SURF_DIRTY]
        mov     rcx, [rbp + SURF_ROWS]
        mov     al, 1
        rep     stosb
        pop     rdi
        pop     rcx
        pop     rax
        ret

; choices_set - RSI = text, ECX = length: row 0 of the choices surface,
; the rest of the row and row 1 blank, both rows dirty. Preserves
; everything.
choices_set:
        push    rax
        push    rcx
        push    rdx
        push    rsi
        push    rdi
        lea     rdi, [choices_cells]
        mov     edx, [scr_cols]
.cell:
        test    edx, edx
        jz      .filled
        mov     al, ' '
        test    ecx, ecx
        jz      .put
        lodsb
        dec     ecx
.put:
        stosb
        dec     edx
        jmp     .cell
.filled:
        mov     ecx, [scr_cols]
        mov     al, ' '
        rep     stosb                   ; row 1
        mov     word [choices_dirty], 0x0101
        pop     rdi
        pop     rsi
        pop     rdx
        pop     rcx
        pop     rax
        ret

; app_put - EBX = row, ECX = column (panel-relative), EAX = the cell: into
; the app surface, its row dirty; outside the panel, nothing. Preserves
; everything.
app_put:
        push    rax
        push    rdx
        cmp     ebx, [app_rows]
        jae     .out
        cmp     ecx, [app_cols]
        jae     .out
        push    rax
        mov     eax, ebx
        imul    eax, [app_cols]
        add     eax, ecx
        lea     rdx, [app_cells]
        add     rdx, rax                ; the cell's address, before RAX is the
        pop     rax                     ; character again
        mov     [rdx], al
        lea     rdx, [app_dirty]
        mov     byte [rdx + rbx], 1
.out:
        pop     rdx
        pop     rax
        ret

; app_clear - the app surface blank, every row dirty. Preserves everything.
app_clear:
        push    rax
        push    rcx
        push    rdx                     ; mul clobbers it
        push    rdi
        push    rbp
        lea     rdi, [app_cells]
        mov     eax, [app_rows]
        mul     dword [app_cols]
        mov     ecx, eax
        mov     al, ' '
        rep     stosb
        lea     rbp, [obs_page + OBS_SURF_APP]
        call    surf_dirty_all
        pop     rbp
        pop     rdi
        pop     rdx
        pop     rcx
        pop     rax
        ret

; conv_dirty_row - EBX = a conversation row: dirty. Preserves everything.
conv_dirty_row:
        push    rax
        lea     rax, [conv_dirty]
        mov     byte [rax + rbx], 1
        pop     rax
        ret

; glass_err - RSI = message. Prints "ERR: <msg>", renders the conversation
; surface to the framebuffer once - the one paint the boot processor is
; allowed, on a path where no glass core will ever run - and halts.
glass_err:
        push    rsi
        lea     rsi, [msg_err]
        call    serial_puts
        pop     rsi
        call    serial_puts
        lea     rsi, [msg_crlf]
        call    serial_puts
        call    fb_clear
        lea     rbp, [obs_page + OBS_SURF_CONV]
        cmp     qword [rbp + SURF_CELLS], 0
        je      halt_forever            ; too small to have a surface at all
        call    surf_render
        jmp     halt_forever

; console_init - the conversation panel's shadow and the boot log replay.
; The geometry is glass_init's; nothing is painted - the glass core will.
; Called exactly once, from efi_main; clobbers registers freely.
console_init:
        mov     eax, [con_rows]
        mul     dword [con_cols]        ; EDX:EAX = cols * rows
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

        lea     rdi, [shadow]           ; a panel full of spaces
        mov     ecx, SHADOW_SIZE / 4
        mov     eax, CHAR_SPACE * 0x01010101
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

; fb_clear - the whole framebuffer painted with the background, stride
; padding and any part-cell edge included. The shadow is not touched: the
; loader clears the screen for a component this way and re-renders the
; conversation from the shadow afterwards. Preserves everything.
fb_clear:
        push    rax
        push    rcx
        push    rdx
        push    rdi
        mov     eax, [fb_pps]
        mul     dword [fb_height]       ; EDX:EAX = pixels to paint
        mov     ecx, eax
        mov     rdi, [fb_base]
        mov     eax, [bg_pix]
        rep     stosd
        pop     rdi
        pop     rdx
        pop     rcx
        pop     rax
        ret

; console_redraw - re-render the whole screen from the shadow, row by row,
; cell by cell. The framebuffer is never read. Preserves everything.
console_redraw:
        push    rbp
        lea     rbp, [obs_page + OBS_SURF_CONV]
        call    surf_dirty_all
        pop     rbp
        ret

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
        call    conv_dirty_row

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
        mov     ebx, [cur_row]
        call    conv_dirty_row
        jmp     .out

; draw_glyph - RSI = eight glyph bytes, EBX = cell row, ECX = cell column:
; the cell painted from those bytes exactly as draw_cell paints a font
; glyph. The arrow's painter (ring 6c). Preserves everything.
draw_glyph:
        push    rax
        push    rbx
        push    rcx
        push    rdx
        push    rsi
        push    rdi
        push    r8
        push    r9
        push    r10
        jmp     draw_cell.from_font

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

        cmp     al, 0x20
        jb      .special
        cmp     al, 0x7E
        jbe     .glyph
        mov     eax, 0x20               ; not printable: background
        jmp     .glyph
.special:
        cmp     al, CELL_BLOCK
        jne     .blank
        mov     eax, 0x7F               ; a glyph made of foreground below
        jmp     .glyph
.blank:
        mov     eax, 0x20
.glyph:
        and     eax, 0x7F
        lea     rsi, [font8x8]
        lea     rsi, [rsi + rax*8]      ; the glyph's 8 row bytes
        cmp     eax, 0x7F
        jne     .from_font
        lea     rsi, [block_glyph]      ; CELL_BLOCK: every bit set
.from_font:

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
        push    rdx
        mov     rdx, [obs_page + OBS_SURF_CONV + SURF_CURSOR]     ; the old word
        mov     eax, [cur_row]
        shl     eax, 16
        or      eax, [cur_col]
        or      eax, 1 << 31
        mov     [obs_page + OBS_SURF_CONV + SURF_CURSOR], rax       ; one store, first
        test    edx, 1 << 31            ; then the row the cursor was on: dirty,
        jz      .was_off                ; after the new word is in place, so the
        mov     ebx, edx                ; glass core can never render the old row
        shr     ebx, 16                 ; with the old word and leave a ghost
        and     ebx, 0x7FFF
        call    conv_dirty_row
.was_off:
        mov     ebx, [cur_row]
        call    conv_dirty_row
        pop     rdx
        pop     rbx
        pop     rax
        ret

; erase_cursor - redraw the cursor cell from the shadow. Preserves everything.
erase_cursor:
        push    rax
        push    rbx
        mov     rax, [obs_page + OBS_SURF_CONV + SURF_CURSOR]
        test    eax, 1 << 31
        jz      .done
        mov     ebx, eax
        shr     ebx, 16
        and     ebx, 0x7FFF
        and     eax, ~(1 << 31)
        mov     [obs_page + OBS_SURF_CONV + SURF_CURSOR], rax
        call    conv_dirty_row
.done:
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

        call    console_redraw          ; re-render: row by row, cell by cell

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
        push    rdx
        ; Time-to-done (GLASS.md, "The obs page"): the Enter that led here
        ; to this prompt, last and worst. Nothing at boot's first prompt.
        mov     rdx, [enter_stamp]
        test    rdx, rdx
        jz      .no_tt
        mov     qword [enter_stamp], 0
        push    rdx
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        pop     rdx
        sub     rax, rdx
        mov     [obs_page + OBS_TT_LAST], rax
        cmp     rax, [obs_page + OBS_TT_WORST]
        jbe     .no_tt
        mov     [obs_page + OBS_TT_WORST], rax
.no_tt:
        pop     rdx
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
; S7: lines the acceptance tests count, so a failure path can say what went
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
        cmp     eax, 1                  ; the first application processor
        je      glass_main              ; owns the screen (GLASS.md)
.park:
        cli
.hang:  hlt
        jmp     .hang

; ---------------------------------------------------------------------------
; The glass core (GLASS.md, "Surfaces and the glass core"). Runs on the
; first application processor, interrupts off, on its own stack, for ever:
; records its APIC id, signals ready, waits to be started, then paints
; every dirty row of every surface into the framebuffer, draws the strip
; from the obs page, times itself, and paces at sixty frames a second. The
; only code that writes pixels after boot.
; ---------------------------------------------------------------------------
glass_main:
        cmp     dword [apic_x2], 0
        jne     .x2
        mov     rax, [apic_mmio]
        mov     eax, [rax + 0x20]
        shr     eax, 24
        jmp     .have_id
.x2:
        mov     ecx, 0x802              ; IA32_X2APIC_APICID
        rdmsr
.have_id:
        mov     [obs_page + OBS_GLASS_APIC], rax
        mov     dword [glass_ready], 1
.wait_go:
        pause
        cmp     dword [glass_go], 0
        je      .wait_go
        call    fb_clear                ; the first and only whole-screen paint
.frame:
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     r15, rax                ; t0
        mov     [obs_page + OBS_NOW], rax
        mov     r14, [obs_page + OBS_ECHO_PENDING]      ; snapshot, before the copy
        mov     rax, [obs_page + OBS_PTR_PENDING]       ; and the pointer's (ring 6c)
        mov     [ptr_pend_snap], rax
        lea     rbp, [obs_page + OBS_SURF_CHOICES]
        call    surf_render
        lea     rbp, [obs_page + OBS_SURF_CONV]
        call    surf_render
        lea     rbp, [obs_page + OBS_SURF_APP]
        call    surf_render
        call    strip_format            ; the strip, from the page, every frame
        lea     rbp, [obs_page + OBS_SURF_STRIP]
        call    surf_render
        call    cursor_draw             ; step 3b: the arrow, last of all (ring 6c)
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     rbx, rax                ; the frame's end
        sub     rax, r15
        mov     [obs_page + OBS_FRAME_LAST], rax
        cmp     rax, [obs_page + OBS_FRAME_WORST]
        jbe     .no_worst
        mov     [obs_page + OBS_FRAME_WORST], rax
.no_worst:
        inc     qword [obs_page + OBS_FRAMES]
        test    r14, r14
        jz      .pace
        mov     rax, rbx                ; input-to-photon: the key's stamp to
        sub     rax, [obs_page + OBS_ECHO_STAMP]        ; the end of this copy
        mov     [obs_page + OBS_PHOTON_LAST], rax
        cmp     rax, [obs_page + OBS_PHOTON_WORST]
        jbe     .photon_done
        mov     [obs_page + OBS_PHOTON_WORST], rax
.photon_done:
        mov     qword [obs_page + OBS_ECHO_PENDING], 0
.pace:
        cmp     qword [ptr_pend_snap], 0
        je      .paced
        mov     rax, rbx                ; pointer input-to-photon: the packet's
        sub     rax, [obs_page + OBS_PTR_STAMP]         ; first byte to this copy's end
        mov     [obs_page + OBS_POINTER_LAST], rax
        cmp     rax, [obs_page + OBS_POINTER_WORST]
        jbe     .ptr_done
        mov     [obs_page + OBS_POINTER_WORST], rax
.ptr_done:
        mov     qword [obs_page + OBS_PTR_PENDING], 0
.paced:
        pause
        rdtsc
        shl     rdx, 32
        or      rax, rdx
        sub     rax, r15
        cmp     rax, [frame_ticks]
        jb      .paced
        jmp     .frame

; cursor_draw - the arrow, the last thing painted in every frame (GLASS.md,
; "The cursor"): nothing until the first packet; then, if the cell has
; changed since the arrow was last drawn, the old cell repainted from its
; surface, and the arrow painted at the page's cell - every frame, since a
; dirty row may just have repainted its cell. Clobbers registers freely.
cursor_draw:
        cmp     qword [obs_page + OBS_PACKETS], 0
        je      .ret
        mov     rax, [obs_page + OBS_PTR_CELL]
        cmp     dword [arrow_on], 0
        je      .draw
        cmp     rax, [arrow_cell]
        je      .draw
        mov     rdx, [arrow_cell]       ; the cell the arrow is leaving
        mov     ebx, edx
        shr     ebx, 16
        and     ebx, 0xFFFF
        movzx   ecx, dx
        push    rax
        call    cell_repaint
        pop     rax
.draw:
        mov     [arrow_cell], rax
        mov     dword [arrow_on], 1
        mov     ebx, eax
        shr     ebx, 16
        and     ebx, 0xFFFF
        movzx   ecx, ax
        lea     rsi, [arrow_glyph]
        call    draw_glyph
.ret:
        ret

; cell_repaint - EBX = a screen row, ECX = a screen column: the cell painted
; from the surface that owns it - the first of the four descriptors in the
; obs page whose bounds contain it - with the conversation's block cursor
; overlaid when it sits there. Clobbers RAX, RDX, RSI, RDI, R8.
cell_repaint:
        lea     rsi, [obs_page + OBS_SURF_STRIP]
        mov     r8d, 4
.surface:
        mov     rax, rbx
        sub     rax, [rsi + SURF_ROW0]
        js      .next
        cmp     rax, [rsi + SURF_ROWS]
        jae     .next
        mov     rdx, rcx
        sub     rdx, [rsi + SURF_COL0]
        js      .next
        cmp     rdx, [rsi + SURF_COLS]
        jae     .next
        ; RAX = the row, RDX = the column, relative to the surface.
        mov     rdi, [rsi + SURF_CURSOR]
        test    edi, 1 << 31
        jz      .no_cursor
        push    rdi
        shr     edi, 16
        and     edi, 0x7FFF
        cmp     rdi, rax
        pop     rdi
        jne     .no_cursor
        movzx   edi, di
        cmp     rdi, rdx
        jne     .no_cursor
        mov     eax, CELL_BLOCK
        jmp     .paint
.no_cursor:
        imul    rax, [rsi + SURF_COLS]
        add     rax, rdx
        mov     rdi, [rsi + SURF_CELLS]
        movzx   eax, byte [rdi + rax]
.paint:
        call    draw_cell
        ret
.next:
        add     rsi, 64
        dec     r8d
        jnz     .surface
        ret

; surf_render - RBP = a surface descriptor in the obs page. Every dirty row:
; the flag exchanged to zero, then its cells painted at the region's place,
; the cursor's block overlaid on its cell. Clobbers registers freely
; (the glass core owns them all).
surf_render:
        xor     r12d, r12d              ; row
.row:
        cmp     r12, [rbp + SURF_ROWS]
        jae     .done
        mov     rdx, [rbp + SURF_DIRTY]
        xor     eax, eax
        xchg    al, [rdx + r12]         ; take the flag; a later store sets it again
        test    al, al
        jz      .next_row
        mov     r8, [rbp + SURF_CURSOR]
        xor     r13d, r13d              ; column
.col:
        cmp     r13, [rbp + SURF_COLS]
        jae     .next_row
        mov     rax, r12
        imul    rax, [rbp + SURF_COLS]
        add     rax, r13
        mov     rdx, [rbp + SURF_CELLS]
        movzx   eax, byte [rdx + rax]
        test    r8d, 1 << 31            ; the cursor, on and on this cell?
        jz      .plain
        mov     edx, r8d
        shr     edx, 16
        and     edx, 0x7FFF
        cmp     rdx, r12
        jne     .plain
        movzx   edx, r8w
        cmp     rdx, r13
        jne     .plain
        mov     eax, CELL_BLOCK
.plain:
        mov     rbx, [rbp + SURF_ROW0]
        add     rbx, r12
        mov     rcx, [rbp + SURF_COL0]
        add     rcx, r13
        call    draw_cell
        inc     r13
        jmp     .col
.next_row:
        inc     r12
        jmp     .row
.done:
        ret

; strip_format - the two strip rows from the obs page into the strip
; surface (GLASS.md, "The obs strip"), both rows dirty. Every number is
; counted or stamped by the guest; grows served is the one taken from the
; broker's source byte.
strip_format:
        ; Row 0.
        lea     rdi, [strip_line]
        lea     rsi, [strip_tmpl0]
        mov     ecx, STRIP_LEN
        rep     movsb
        mov     rax, [obs_page + OBS_NOW]
        sub     rax, [obs_page + OBS_TSC_BOOT]
        xor     edx, edx
        div     qword [tsc_per_ms]
        xor     edx, edx
        mov     ecx, 1000
        div     rcx                     ; seconds since boot
        lea     rdi, [strip_line + STRIP0_UP]
        mov     ecx, 6
        call    put_num
        mov     rax, [obs_page + OBS_GLASS_APIC]
        lea     rdi, [strip_line + STRIP0_CORE]
        mov     ecx, 2
        call    put_num
        mov     rax, [obs_page + OBS_FRAMES]
        lea     rdi, [strip_line + STRIP0_FR]
        mov     ecx, 6
        call    put_num
        mov     rax, [obs_page + OBS_FRAME_LAST]
        lea     rdi, [strip_line + STRIP0_FL]
        call    put_ms
        mov     rax, [obs_page + OBS_FRAME_WORST]
        lea     rdi, [strip_line + STRIP0_FW]
        call    put_ms
        mov     rax, [obs_page + OBS_PHOTON_LAST]
        lea     rdi, [strip_line + STRIP0_PL]
        call    put_ms
        mov     rax, [obs_page + OBS_PHOTON_WORST]
        lea     rdi, [strip_line + STRIP0_PW]
        call    put_ms
        mov     rax, [obs_page + OBS_KEYS]
        lea     rdi, [strip_line + STRIP0_K]
        mov     ecx, 4
        call    put_num
        mov     rax, [obs_page + OBS_KEYS_HW]
        lea     rdi, [strip_line + STRIP0_HW]
        mov     ecx, 3
        call    put_num
        mov     rax, [obs_page + OBS_ERRORS]
        lea     rdi, [strip_line + STRIP0_ERR]
        mov     ecx, 3
        call    put_num
        mov     rax, [obs_page + OBS_STEP_LAST]
        lea     rdi, [strip_line + STRIP0_SL]
        call    put_ms
        mov     rax, [obs_page + OBS_STEP_WORST]
        lea     rdi, [strip_line + STRIP0_SW]
        call    put_ms
        mov     dword [strip_line_len], STRIP_LEN
        cmp     qword [obs_page + OBS_PACKETS], 0
        je      .row0_done
        ; The third field (ring 6c): " pt LL.L/WW.W pk NNNN cl NNN" from
        ; column 87, the pointer's photon, the packets and the clicks.
        lea     rdi, [strip_line + STRIP_LEN]
        lea     rsi, [strip_tmpl_pt]
        mov     ecx, STRIP_PT_LEN
        rep     movsb
        mov     rax, [obs_page + OBS_POINTER_LAST]
        lea     rdi, [strip_line + STRIP0_PT]
        call    put_ms
        mov     rax, [obs_page + OBS_POINTER_WORST]
        lea     rdi, [strip_line + STRIP0_PTW]
        call    put_ms
        mov     rax, [obs_page + OBS_PACKETS]
        lea     rdi, [strip_line + STRIP0_PK]
        mov     ecx, 4
        call    put_num
        mov     rax, [obs_page + OBS_CLICKS]
        lea     rdi, [strip_line + STRIP0_CL]
        mov     ecx, 3
        call    put_num
        mov     dword [strip_line_len], STRIP_LEN + STRIP_PT_LEN
.row0_done:
        xor     ebx, ebx
        call    strip_put_row

        ; Row 1.
        lea     rdi, [strip_line]
        lea     rsi, [strip_tmpl1]
        mov     ecx, STRIP_LEN
        rep     movsb
        mov     dword [strip_line_len], STRIP_LEN
        ; The mode word, in its 18-column field.
        lea     rdi, [strip_line + STRIP1_MODE]
        mov     rax, [obs_page + OBS_MODE]
        cmp     rax, 4
        ja      .mode_unknown
        lea     rsi, [mode_words]
        imul    eax, eax, 11
        add     rsi, rax                ; each word padded to 11 bytes
        mov     ecx, 11
        rep     movsb
        cmp     qword [obs_page + OBS_MODE], MODE_RUNNING
        jne     .mode_done
        lea     rdi, [strip_line + STRIP1_MODE + 8]     ; after "running "
        lea     rsi, [obs_page + OBS_NAME]
        mov     ecx, 10                 ; the name cut to ten characters
.name:
        lodsb
        test    al, al
        jz      .mode_done
        stosb
        dec     ecx
        jnz     .name
        jmp     .mode_done
.mode_unknown:
        mov     byte [rdi], '?'
.mode_done:
        mov     rax, [obs_page + OBS_QUESTIONS]
        lea     rdi, [strip_line + STRIP1_Q]
        mov     ecx, 3
        call    put_num
        mov     rax, [obs_page + OBS_NOTES]
        lea     rdi, [strip_line + STRIP1_N]
        mov     ecx, 3
        call    put_num
        mov     rax, [obs_page + OBS_GROWS_GEN]
        lea     rdi, [strip_line + STRIP1_GG]
        mov     ecx, 3
        call    put_num
        mov     rax, [obs_page + OBS_GROWS_SERVED]
        lea     rdi, [strip_line + STRIP1_GS]
        mov     ecx, 3
        call    put_num
        mov     rax, [obs_page + OBS_DISK_REQS]
        lea     rdi, [strip_line + STRIP1_DR]
        mov     ecx, 4
        call    put_num
        mov     rax, [obs_page + OBS_DISK_WAIT]
        xor     edx, edx
        div     qword [tsc_per_ms]
        lea     rdi, [strip_line + STRIP1_DW]
        mov     ecx, 6
        call    put_num
        mov     rax, [obs_page + OBS_WIRE_CONNS]
        lea     rdi, [strip_line + STRIP1_WC]
        mov     ecx, 3
        call    put_num
        mov     rax, [obs_page + OBS_WIRE_WAIT]
        xor     edx, edx
        div     qword [tsc_per_ms]
        lea     rdi, [strip_line + STRIP1_WW]
        mov     ecx, 6
        call    put_num
        mov     rax, [obs_page + OBS_BYTES_IN]
        lea     rdi, [strip_line + STRIP1_IN]
        mov     ecx, 6
        call    put_num
        mov     rax, [obs_page + OBS_BYTES_OUT]
        lea     rdi, [strip_line + STRIP1_OUT]
        mov     ecx, 6
        call    put_num
        mov     ebx, 1
        call    strip_put_row
        ret

; strip_put_row - EBX = 0 or 1: strip_line_len bytes of strip_line into
; that row of the strip
; surface, cut at the screen's width, padded with spaces, the row dirty.
strip_put_row:
        lea     rdi, [strip_cells]
        mov     eax, ebx
        imul    eax, [scr_cols]
        add     rdi, rax
        lea     rsi, [strip_line]
        mov     ecx, [scr_cols]
        mov     edx, [strip_line_len]   ; 87, or 115 with the pointer's field
.cell:
        test    ecx, ecx
        jz      .filled
        mov     al, ' '
        test    edx, edx
        jz      .put
        lodsb
        dec     edx
.put:
        stosb
        dec     ecx
        jmp     .cell
.filled:
        lea     rax, [strip_dirty]      ; lea first: [label + reg] cannot be
        mov     byte [rax + rbx], 1     ; RIP-relative, and an absolute is the RVA
        ret

; put_num - RDI = destination, RAX = value, ECX = width. The value as
; exactly width decimal digits, zero padded, all nines if it does not fit.
; Clobbers RAX, RCX, RDX, R8, R9.
put_num:
        mov     r8d, ecx
        mov     r9, 1                   ; 10^width
.pow:
        imul    r9, r9, 10
        dec     ecx
        jnz     .pow
        cmp     rax, r9
        jb      .fits
        mov     ecx, r8d
.nines:
        mov     byte [rdi + rcx - 1], '9'
        dec     ecx
        jnz     .nines
        ret
.fits:
        mov     ecx, r8d
        mov     r9d, 10
.digit:
        xor     edx, edx
        div     r9
        add     dl, '0'
        mov     [rdi + rcx - 1], dl
        dec     ecx
        jnz     .digit
        ret

; put_ms - RDI = destination, RAX = ticks: milliseconds to one decimal,
; "%02d.%d", capped at 99.9. Clobbers RAX, RCX, RDX, R8, R9.
put_ms:
        imul    rax, rax, 10
        xor     edx, edx
        div     qword [tsc_per_ms]      ; tenths of a millisecond
        cmp     rax, 999
        jbe     .capped
        mov     eax, 999
.capped:
        xor     edx, edx
        mov     ecx, 10
        div     rcx                     ; RAX = whole ms, RDX = the tenth
        push    rdx
        mov     ecx, 2
        call    put_num
        mov     byte [rdi + 2], '.'
        pop     rax
        add     rdi, 3
        mov     ecx, 1
        call    put_num
        ret

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

; The eleven lines of the spec (items 10 and 12 add disk and notebook), then
; the raw echo of what is typed, and nothing else on this channel.
msg_alive:      db      'S7: alive', 13, 10, 0

msg_edid:       db      'S7: edid ', 0
msg_edid_none:  db      'S7: edid none', 13, 10, 0
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
msg_gpt_written: db     'S7: gpt written', 13, 10, 0
msg_port:       db      'port ', 0
msg_colon:      db      ': ', 0
msg_comma:      db      ', ', 0
word_germos:    db      'germos', 0
word_blank:     db      'blank', 0
word_gpt:       db      'gpt', 0
word_torn:      db      'torn', 0
word_other:     db      'other', 0
crc_zero4:      dd      0
; DISK.md's GUIDs as stored: the first three fields little-endian.
guid_notes_type: db     0x57,0x55,0x84,0x50,0x34,0xee,0x31,0x47,0x8b,0x83,0xd1,0xd6,0xf1,0x4f,0xd8,0xc5
guid_home_type: db      0x07,0x40,0x6d,0x45,0x03,0xd8,0xa0,0x41,0xa6,0x61,0xca,0x73,0x6d,0xdc,0xf9,0x6b
guid_disk:      db      0x05,0xa5,0x74,0x2b,0x46,0xe2,0x9d,0x46,0x8d,0x73,0x3b,0xfd,0xc5,0x2a,0x8d,0xf0
; DISK.md's entries 0 and 1, byte for byte from the document's own Python:
; the notes partition at 2048-34815, the home at 34816-67583.
gpt_entry_image:
                db      0x57,0x55,0x84,0x50,0x34,0xee,0x31,0x47,0x8b,0x83,0xd1,0xd6,0xf1,0x4f,0xd8,0xc5
                db      0x7e,0x29,0x5d,0x6e,0xcb,0x0e,0xc5,0x48,0x92,0xc8,0x4a,0x93,0xf4,0xe9,0x8d,0x44
                db      0x00,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0xff,0x87,0x00,0x00,0x00,0x00,0x00,0x00
                db      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x47,0x00,0x65,0x00,0x72,0x00,0x6d,0x00
                db      0x4f,0x00,0x53,0x00,0x20,0x00,0x6e,0x00,0x6f,0x00,0x74,0x00,0x65,0x00,0x73,0x00
                db      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
                db      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
                db      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
                db      0x07,0x40,0x6d,0x45,0x03,0xd8,0xa0,0x41,0xa6,0x61,0xca,0x73,0x6d,0xdc,0xf9,0x6b
                db      0x69,0x91,0xbc,0x82,0x31,0xce,0xd9,0x4f,0xbf,0x05,0x63,0xc7,0x52,0x17,0x26,0xeb
                db      0x00,0x88,0x00,0x00,0x00,0x00,0x00,0x00,0xff,0x07,0x01,0x00,0x00,0x00,0x00,0x00
                db      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x47,0x00,0x65,0x00,0x72,0x00,0x6d,0x00
                db      0x4f,0x00,0x53,0x00,0x20,0x00,0x68,0x00,0x6f,0x00,0x6d,0x00,0x65,0x00,0x00,0x00
                db      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
                db      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
                db      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
msg_nb:         db      'S7: notebook ', 0
msg_notes:      db      ' notes', 13, 10, 0
msg_nb_fmt:     db      'S7: notebook formatted', 13, 10, 0
msg_home:       db      'S7: home ', 0
msg_apps:       db      ' apps', 13, 10, 0
msg_install_word: db    'install'                       ; 7 bytes, compared
msg_undo_word:  db      'undo install '                 ; 13 bytes, compared
msg_installed:  db      'installed ', 0                 ; HOME.md's console lines
msg_home_full:  db      'home image full: ', 0
msg_no_home:    db      'no home image: ', 0
msg_not_kept:   db      ' not kept', 0
msg_restored:   db      ': previous build restored', 0
msg_no_previous: db     ' has no previous build', 0
msg_no_app:     db      'no app named ', 0
msg_bad_hash:   db      ': build does not match its hash', 0
msg_empty:      db      0
msg_nic:        db      'S7: nic ', 0
msg_link:       db      'S7: link up', 13, 10, 0
                align   2
e1k_ids:        dw      0x10D3, 0x1502, 0x1503  ; 82574L, 82579LM, 82579V (WIRE.md)
msg_region:     db      'S7: component region 0x', 0
msg_region_cap: db      ' 1048576 bytes', 13, 10, 0     ; COMP_BLOB_MAX, spelled
msg_obs:        db      'S7: obs page 0x', 0
msg_glass:      db      'S7: glass core ', 0
msg_choices_prompt: db  '? ask   ! grow'
msg_choices_prompt_len equ $ - msg_choices_prompt
msg_choices_prompt_app: db '? ask   ! grow   Tab app   Esc exit'
msg_choices_prompt_app_len equ $ - msg_choices_prompt_app
msg_choices_app_tail: db 'Esc exit   Tab prompt'
msg_choices_app_tail_len equ $ - msg_choices_app_tail
strip_tmpl0:    db      'up 000000 core 00 fr 000000 00.0/00.0 ph 00.0/00.0 k 0000 hw 000 err 000 step 00.0/00.0'
strip_tmpl1:    db      'prompt             q 000 n 000 g 000/000 disk 0000 000000 w 000 000000 io 000000/000000'
mode_words:     db      'prompt     ', 'asking     ', 'growing    ', 'running    ', 'installing '
block_glyph:    db      0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF
arrow_glyph:    db      0x01, 0x03, 0x07, 0x0F, 0x1F, 0x0D, 0x19, 0x30   ; GLASS.md, "The cursor"
strip_tmpl_pt:  db      ' pt 00.0/00.0 pk 0000 cl 000'
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
msg_no_answer:  db      'no answer from the broker', 0
msg_nothing_ask: db     'nothing to ask', 0
msg_nothing_grow: db    'nothing to grow', 0
msg_bad_frame:  db      'bad component frame', 0
spin_chars:     db      '-', '\', '|', '/'
msg_kbd:        db      'S7: keyboard ready', 13, 10, 0
msg_mouse:      db      'S7: mouse ready', 13, 10, 0
msg_i8042_ok:   db      'i8042: self-test ok', 13, 10, 0      ; ring 7c: their own prefix, no S7: count moves
msg_mouse_ok:   db      'i8042: mouse reset ok', 13, 10, 0
msg_mouse_none: db      'i8042: mouse none', 13, 10, 0
err_i8042_self: db      'i8042 self-test failed', 0
err_i8042_cmd:  db      'i8042 command byte not answered', 0
err_i8042_ibf:  db      'i8042 input buffer never emptied', 0
hex_digits:     db      '0123456789abcdef'

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
err_one_core:   db      'the glass needs a second core - boot with -smp 2 or more', 0
err_too_small:  db      'mode too small for the glass', 0
err_no_ahci:    db      'no AHCI controller on PCI bus 0', 0
err_no_sata:    db      'no SATA disk on any AHCI port', 0
err_ahci_stop:  db      'AHCI port would not stop', 0
err_ahci_spinup: db     'ahci port ', 0                            ; ring 7c: under CAP.SSS, a device that
err_ahci_spinup_tail: db ' did not come up after spin-up', 13, 10, 0   ; appeared after SUD but never reached DET 3
err_sector_size: db     'disk sector is not 512 bytes', 0
err_no_germos:  db      'no GermOS disk and no blank disk - ', 0
err_gpt_readback: db    'the table written does not read back as GermOS', 0
err_disk_small: db      'disk too small for the two partitions', 0
err_vio_cap:    db      'virtio device lacks a modern capability (common, notify or device)', 0
err_bar_io:     db      'virtio capability names an I/O BAR or a BAR beyond 5 - not a modern device', 0
err_bar_high:   db      'BAR lies beyond the physical address width', 0
err_spare:      db      'page-table pool exhausted - raise SPARE_PAGES', 0
err_vio_reset:  db      'virtio device did not complete its reset', 0
err_vio_v1:     db      'virtio device does not offer VIRTIO_F_VERSION_1 - legacy only', 0
err_vio_feat:   db      'virtio device refused our features - FEATURES_OK not set', 0
err_vio_missing: db     'virtio device does not offer a feature this driver needs', 0
err_no_nic:     db      'no network device on PCI bus 0 (e1000e or virtio-net)', 0
err_e1k_bar:    db      'nic BAR0 is not a memory BAR', 0
err_e1k_reset:  db      'nic did not complete its reset', 0
err_e1k_mac:    db      'nic has no address in RAL/RAH', 0
err_e1k_link:   db      'nic link did not come up within 10 s', 0
err_e1k_ring:   db      'nic ring sits above 4GB', 0
err_nic_tx:     db      'nic transmit timed out', 0
err_disk_big:   db      'disk has 2^32 sectors or more - beyond this stage', 0
err_vq_size:    db      'virtqueue size is 0, above VQ_MAX, or not a power of two', 0
err_disk_beyond: db     'disk request beyond the capacity', 0
err_disk_timeout: db    'disk request timed out', 0
err_disk_failed: db     'disk request failed - task file error', 0

; The shared font, byte for byte the file the pixel checker renders from.
; 128 glyphs, 8 bytes each, row per byte, bit 0 leftmost - stage2/FONT.md.
        align   8
font8x8:        incbin  "stage2/font8x8.bin"

; Scancode set 1, US layout, unshifted - the owner's decision 3. Make code in,
; character out: 13 is Enter, 8 is Backspace, 0 is "not a key this stage
; listens to" (Esc, Tab, the modifiers, the function keys, the keypad).
        align   8
scan1_map:
        db      0, 0x1B                                 ; 00 -, 01 Esc (a component's way home)
        db      '1','2','3','4','5','6','7','8','9','0' ; 02-0B
        db      '-','='                                 ; 0C, 0D
        db      8, 9                                    ; 0E Backspace, 0F Tab (focus, ring 6a)
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

; The shifted US layout: capitals, the symbols over the digits, and '?' over
; '/' - the smallest thing that makes the "? " marker typeable (plan decision
; 10). Same shape as the unshifted table; Caps Lock, Ctrl and Alt stay
; ignored.
scan1_shift_map:
        db      0, 0x1B                                 ; 00 -, 01 Esc
        db      '!','@','#','$','%','^','&','*','(',')' ; 02-0B
        db      '_','+'                                 ; 0C, 0D
        db      8, 9                                    ; 0E Backspace, 0F Tab (focus, ring 6a)
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

; The service table (GERMLINE.md): ABI version, size, four addresses filled
; at boot. A component finds it in RDI.
        align   8
svc_table:      dd      APP_ABI         ; ABI version, 2
                dd      40              ; the table's size in bytes
                dq      0               ; draw_text
                dq      0               ; panel_size
                dq      0               ; ticks_ms
                dq      0               ; fill

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

; The screen's cells, and the conversation panel's (GLASS.md, "The
; screen"). The console's shadow is the conversation surface's cells.
        alignb  16
scr_cols:       resd    1               ; the screen's cells across = width / 16
scr_rows:       resd    1               ; cells down = height / 16
app_cols:       resd    1               ; the app panel's
app_rows:       resd    1
con_cols:       resd    1               ; the conversation panel's
con_rows:       resd    1
cur_row:        resd    1
cur_col:        resd    1
con_ready:      resd    1               ; non-zero once the tee may draw
prompt_min:     resd    1               ; the column typed text starts at
bg_pix:         resd    1               ; background, encoded for the mode
fg_pix:         resd    1               ; foreground, encoded for the mode
        alignb  16
shadow:         resb    SHADOW_SIZE     ; one byte per cell - what is on screen

; The other surfaces and every dirty-row array; the glass core's
; handshake, its frame slot, and its line buffer.
        alignb  64
strip_cells:    resb    STRIP_CELLS
choices_cells:  resb    STRIP_CELLS
        alignb  64
app_cells:      resb    PANEL_CELLS
        alignb  64
strip_dirty:    resb    SURF_ROWS_MAX
choices_dirty:  resb    SURF_ROWS_MAX
conv_dirty:     resb    SURF_ROWS_MAX
app_dirty:      resb    SURF_ROWS_MAX
        alignb  64
glass_ready:    resd    1               ; the glass core has checked in
glass_go:       resd    1               ; the boot processor has started it
        alignb  8
frame_ticks:    resq    1               ; TSC ticks per frame slot

; The running app (GLASS.md, "Running an app"): whether one runs, its
; declared choices as the header carried them, the step pacing, and the
; choices row's line buffer.
        alignb  16
app_running:    resd    1
app_has_point:  resd    1               ; the running blob announces point (ring 6c)
        alignb  8
step_begin:     resq    1               ; the TSC when the last step began
step_gap:       resq    1               ; STEP_GAP_MS in ticks
app_choices:    resb    APP_CHOICES * APP_CHOICE_BYTES
choices_line:   resb    128
strip_line:     resb    128             ; the glass core's formatting scratch

; The keyboard ring. The interrupt writes head, the main loop writes tail,
; and neither touches the other's index - single producer, single consumer.
        alignb  64
kbd_head:       resd    1
kbd_tail:       resd    1
kbd_e0:         resd    1               ; an 0xE0 prefix swallows its successor
kbd_shift:      resd    1               ; non-zero while a Shift key is held
spin_phase:     resd    1               ; which of - \ | / is on screen
spin_count:     resd    1               ; breaths since the last spin
        alignb  16
kbd_ring:       resb    KBD_RING_SIZE
        alignb  16
kbd_stamps:     resq    KBD_RING_SIZE   ; the TSC when each scancode arrived
key_stamp:      resq    1               ; the stamp of the key kbd_next last returned

; The mouse ring (ring 6c): the handler writes head, the main loop writes
; tail; the packet machine's phase, bytes and stamp; the buttons held by the
; previous packet; whether the eighteenth line has gone out.
        alignb  64
mse_head:       resd    1
mse_tail:       resd    1
mse_phase:      resd    1               ; 0, 1 or 2: bytes of the packet so far
mse_prev:       resd    1               ; the buttons held after the previous packet
mouse_announced: resd   1
        alignb  8
mse_stamp0:     resq    1               ; the TSC at the packet's first byte
mse_pkt:        resb    4               ; the packet's bytes as they arrive
        alignb  16
mse_ring:       resb    MSE_RING_SIZE * MSE_ENTRY
mse_cur:        resb    MSE_ENTRY       ; the entry mouse_next last popped

; The glass core's cursor state (ring 6c): where the arrow was last drawn,
; whether it has been drawn at all, the pointer's pending snapshot for the
; frame, and the strip line's length for the row being put.
        alignb  16
arrow_cell:     resq    1
arrow_on:       resd    1
strip_line_len: resd    1
ptr_pend_snap:  resq    1

; The choices row's click targets (ring 6c), rebuilt with the row.
        alignb  16
hit_count:      resd    1
hit_table:      resb    HIT_MAX * HIT_ENTRY

; The display's EDID (GLASS.md, "The screen").
        alignb  16
edid_w:         resd    1               ; the preferred width, 0 if none stated
edid_h:         resd    1
edid_mode:      resd    1               ; the GOP mode that matches it, or -1
edid_bar:       resd    1
edid_buf:       resb    EDID_BYTES

; The virtio devices. One owner - the BSP - so none of this needs a lock. A
; device block per device (the VIO_* layout at the top of the file): the
; disk's, with its one queue, and the NIC's, with its receive and transmit
; queues.
        alignb  16
spare_next:     resd    1               ; pages handed out of the spare pool
phys_limit:     resq    1               ; 1 << physical address width
        alignb  16
nic_dev:        resb    VIO_BLOCK_SIZE

; The AHCI controller and the chosen port (DISK.md): the BDF and the ABAR,
; the port's registers, the ports identified and their words, the two
; partition descriptors, then the command list (1 KB aligned), the FIS
; receive area (256-aligned), the command table (128-aligned), the IDENTIFY
; data, and the table's sectors as read. One owner - the BSP.
        alignb  16
ahci_bdf:       resd    1
ahci_found:     resd    1
ahci_abar:      resq    1
ahci_port_regs: resq    1
ahci_port:      resd    1               ; the chosen port's index
ahci_pi:        resd    1
ahci_sectors:   resd    1               ; the open port's disk, in 512-byte sectors
ports_mask:     resd    1               ; the ports identified, one bit each
gpt_usable_first: resd  1
gpt_usable_last: resd   1
gpt_ecrc:       resd    1
        alignb  16
port_sectors:   resd    MAX_PORTS
port_word:      resb    MAX_PORTS
        alignb  16
part_notes:     resb    8               ; PART_BASE, PART_SECTORS
part_home:      resb    8
disk_sectors:   resd    1               ; the notes partition's capacity, in sectors
        alignb  1024
ahci_clb:       resb    1024            ; 32 command headers; slot 0 is the one used
        alignb  256
ahci_fb:        resb    256
        alignb  128
ahci_ct:        resb    256             ; the FIS, the ACMD, one PRD
        alignb  512
ahci_ident:     resb    512
gpt_sec0:       resb    512             ; sector 0 and sector 1 of a disk, contiguous
gpt_hdr:        resb    512
gpt_entries:    resb    GPT_ENTRY_SECTORS * 512

; The home image's state (HOME.md): whether there is one, its table in
; RAM, which entries are valid, how many, and the next free sector.
        alignb  16
home_present:   resd    1
home_count:     resd    1
home_next:      resd    1
launch_home:    resd    1               ; 1 while run_app serves a home launch
home_valid:     resb    HOME_ENTRIES
        alignb  16
name_buf:       resb    APP_NAME_MAX    ; a typed name, NUL-padded, for the lookups
        alignb  512
home_table:     resb    HOME_TABLE_SECTORS * 512

; SHA-256's working state, and the line a home message is built in.
        alignb  16
sha_state:      resb    32
sha_w:          resb    256
sha_tail:       resb    128
sha_digest:     resb    32
say_buf:        resb    128

        alignb  512
sector_buf:     resb    512             ; one sector, for the notebook's reads
rec_buf:        resb    512             ; the record being written

; The notebook's state and the line being typed. One owner - the BSP.
        alignb  16
nb_count:       resd    1               ; valid records found or written
nb_next:        resd    1               ; the sector the next note goes to
line_len:       resd    1               ; bytes typed since the prompt
        alignb  16
line_buf:       resb    512             ; NOTE_MAX of them used at most

; The NIC: its address, its two queues' rings, its receive buffers and the
; one transmit buffer. Rings 4 KB aligned - more than the spec's 16/2/4 -
; so each sits in its own page and none straddles anything.
        alignb  16
nic_mac:        resb    6
        alignb  4096
nic_rx_desc:    resb    VQ_MAX * 16
        alignb  4096
nic_rx_avail:   resb    6 + VQ_MAX * 2
        alignb  4096
nic_rx_used:    resb    6 + VQ_MAX * 8
        alignb  4096
nic_tx_desc:    resb    VQ_MAX * 16
        alignb  4096
nic_tx_avail:   resb    6 + VQ_MAX * 2
        alignb  4096
nic_tx_used:    resb    6 + VQ_MAX * 8
        alignb  4096
nic_rx_bufs:    resb    NIC_RX_BUFS * NIC_RX_BUF
nic_tx_buf:     resb    NIC_RX_BUF

; The e1000e (WIRE.md): which driver owns the NIC, the function's BDF and
; BAR0, the two legacy rings each in its own page, and the ring indices.
        alignb  16
nic_kind:       resd    1
e1k_bdf:        resd    1
e1k_found:      resd    1
e1k_rx_head:    resd    1
e1k_tx_idx:     resd    1
        alignb  16
e1k_bar:        resq    1
        alignb  4096
e1k_rx_ring:    resb    E1K_RX_DESCS * E1K_DESC
        alignb  4096
e1k_tx_ring:    resb    E1K_TX_DESCS * E1K_DESC

; The wire's state: the broker's MAC once ARP has answered, and the IPv4
; identification counter.
        alignb  16
broker_mac:     resb    6
        alignb  4
broker_mac_ok:  resd    1
ip_ident:       resw    1

; TCP: the connection block, the response stream assembled by its length
; prefix, the request frame kept for retransmission, the pseudo-header
; scratch, and the next source port.
        alignb  16
tcb:            resb    TCB_SIZE
rx_len:         resd    1               ; bytes of the response stream so far
next_port:      resw    1               ; 0 until the first question
        alignb  16
pseudo_hdr:     resb    12
send_ptr:       resq    1
send_len:       resd    1
send_want:      resd    1
req_len:        resd    1
        alignb  16
req_buf:        resb    4 + 512         ; the request frame: length, then bytes
        alignb  16
rx_stream:      resb    4 + 4096        ; a question's response frame as it arrives
        alignb  16
rx_dst:         resq    1               ; where the current response is assembled
rx_max:         resd    1               ; the most it may hold, prefix included
rx_deadline:    resd    1               ; breaths allowed for the whole response
        alignb  16
grow_buf:       resb    1 + 512         ; the grow request's text: the marker, then the body

; The clock: the TSC's rate per millisecond and its reading at boot.
        alignb  16
tsc_per_ms:     resq    1
tsc_boot:       resq    1
saved_rsp:      resq    1               ; the loader's stack pointer across a component
enter_stamp:    resq    1               ; the last Enter's key stamp, until its prompt
t_disk:         resq    1               ; the TSC when a disk request was posted
t_wire:         resq    1               ; the TSC when an exchange began

; The obs page (GLASS.md, "The obs page"): one page, page-aligned, its
; address on line fourteen.
        alignb  4096
obs_page:       resb    4096

; The component region (the COMP_* layout at the top of the file): a grow
; response lands here from +28, and a component runs from +64. Page-aligned
; BSS, so the loader zero-fills it and the identity map already covers it.
        alignb  4096
comp_region:    resb    COMP_REGION_SIZE

; Page tables. 4 KB alignment is architectural, not a preference.
        alignb  4096
pml4:           resb    4096
pdpt:           resb    4096
pd_tables:      resb    4 * 4096        ; four directories, 2048 entries in all
spare_pages:    resb    SPARE_PAGES * 4096      ; for map_mmio_2m
bss_end:

bss_size        equ     bss_end - bss_start
data_virt_size  equ     bss_end - data_start
image_size      equ     ((bss_end - $$) + SECT_ALIGN - 1) & ~(SECT_ALIGN - 1)
