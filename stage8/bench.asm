; ============================================================================
; stage8/bench.asm - ring 8b's bench (stage8/plan-8b.md, "The bench").
;
; A small EFI of its own, on the twin's machine shape, with no path into the
; seed. It takes the firmware's boot, runs CLI, builds its own identity map
; and never returns, so neither OVMF's NX nor its timer can touch it. Under
; QEMU's -icount shift=0,sleep=off the TSC is the instruction count.
;
; It feeds the corpus, byte by byte, to a decoder's `byte` entry through
; PARTS.md's calling convention, for a null decoder and two parts:
;
;     N  G C C G  G C C G  N
;
; (N the null decoder built in here, G the generic through the slot
; interface, C the candidate). Every block starts from a fresh copy.
;
; The cost of a byte is the instructions from the entry to its first upcall,
; or to its `ret` if it makes none. The guest computes nothing: it prints
; every cost and every event, and stage8/bench.py does the arithmetic.
;
; Built with, from the repo root:
;   nasm -f bin -DGENERIC='"g.bin"' -DCANDIDATE='"c.bin"' -DCORPUS='"c.dat"' \
;        stage8/bench.asm -o bench.efi
;
; The lines, on COM1, each ended by LF:
;   bench: corpus <n>            n in hex, the bytes in the corpus
;   B <i> <tag>                  block i (hex), tag N, G or C
;   k <key> <stamp>              a key_event upcall, in hex
;   p <dx> <dy> <buttons> <stamp>   a mouse_packet upcall, in hex, 64 bits
;   <cost>                       the byte's raw cost in hex; ends its record
;   bench: done
; ============================================================================

bits 64
default rel
org 0

%define IMAGE_BASE      0x0000000000400000
%define SECT_ALIGN      0x1000
%define FILE_ALIGN      0x1000

%define COM1            0x3F8
%define DEBUG_EXIT      0xF4            ; isa-debug-exit
%define REGION_SIZE     65536

%ifndef GENERIC
%error "GENERIC, CANDIDATE and CORPUS are given on the command line"
%endif

dos_header:
        db      'MZ'
        times   0x3C-($-$$) db 0
        dd      pe_header

pe_header:
        db      'PE', 0, 0
        dw      0x8664                  ; Machine
        dw      2                       ; NumberOfSections
        dd      0, 0, 0
        dw      opt_header_end - opt_header
        dw      0x022F                  ; RELOCS_STRIPPED, EXECUTABLE, ...

opt_header:
        dw      0x020B                  ; PE32+
        db      0, 0
        dd      text_size
        dd      data_raw_size
        dd      bss_size
        dd      efi_main
        dd      text_start
        dq      IMAGE_BASE
        dd      SECT_ALIGN
        dd      FILE_ALIGN
        dw      0, 0, 0, 0, 0, 0
        dd      0
        dd      image_size
        dd      headers_size
        dd      0
        dw      10                      ; EFI application
        dw      0
        dq      0x10000, 0x10000, 0x10000, 0x10000
        dd      0
        dd      16
        times   16 dq 0
opt_header_end:

section_table:
        db      '.text', 0, 0, 0
        dd      text_size, text_start, text_size, text_start
        dd      0, 0
        dw      0, 0
        dd      0x60000020
        db      '.data', 0, 0, 0
        dd      data_virt_size, data_start, data_raw_size, data_start
        dd      0, 0
        dw      0, 0
        dd      0xC0000040

        align   FILE_ALIGN, db 0
headers_size    equ     $ - $$

; ===========================================================================
text_start:

efi_main:
        cli
        cld
        lea     rsp, [stack_top]

        ; Our own identity map: 4 GB in 2 MB pages, no NX bit anywhere, so a
        ; part copied into the region below is executable.
        lea     rdi, [pml4]
        xor     eax, eax
        mov     ecx, 4096 * 6
        rep     stosb
        lea     rbx, [pdpt]
        lea     rax, [rbx + 3]
        lea     rcx, [pml4]
        mov     [rcx], rax
        lea     rsi, [pds]
        xor     edx, edx                ; which 1 GB
.pdpt:
        lea     rax, [rsi + 3]
        mov     [rbx + rdx * 8], rax
        mov     rax, rdx
        shl     rax, 30
        or      rax, 0x83               ; present, writable, 2 MB
        xor     ecx, ecx
.pd:
        mov     [rsi + rcx * 8], rax
        add     rax, 0x200000
        inc     ecx
        cmp     ecx, 512
        jb      .pd
        add     rsi, 4096
        inc     edx
        cmp     edx, 4
        jb      .pdpt
        lea     rax, [pml4]
        mov     cr3, rax

        ; The service table: absolute addresses, built at run time.
        lea     rdi, [svc]
        mov     dword [rdi], 3
        mov     dword [rdi + 4], 80
        lea     rax, [svc_zero]
        mov     [rdi + 8], rax
        mov     [rdi + 16], rax
        mov     [rdi + 24], rax
        mov     [rdi + 32], rax
        mov     [rdi + 40], rax
        mov     [rdi + 48], rax
        mov     [rdi + 56], rax
        lea     rax, [key_event]
        mov     [rdi + 64], rax
        lea     rax, [mouse_packet]
        mov     [rdi + 72], rax

        call    serial_init
        lea     rsi, [msg_corpus]
        call    puts
        mov     rax, corpus_n
        call    puthex
        call    newline

        mov     dword [block], 0
        call    run_null
        call    run_abba
        call    run_abba
        call    run_null

        lea     rsi, [msg_done]
        call    puts
        call    newline
        mov     al, 0x31
        out     DEBUG_EXIT, al
.dead:
        hlt
        jmp     .dead

run_abba:
        call    run_generic
        call    run_candidate
        call    run_candidate
        call    run_generic
        ret

run_null:
        lea     rax, [null_byte]
        mov     [cur_entry], rax
        mov     al, 'N'
        jmp     run_block

run_generic:
        lea     rsi, [generic]
        mov     ecx, generic_len
        call    place
        mov     al, 'G'
        jmp     run_block

run_candidate:
        lea     rsi, [candidate]
        mov     ecx, candidate_len
        call    place
        mov     al, 'C'
        jmp     run_block

; place - RSI = a part, ECX = its length: a fresh copy in the zeroed region,
; and cur_entry set to its byte entry.
place:
        push    rsi
        push    rcx
        lea     rdi, [region]
        mov     ecx, REGION_SIZE
        xor     eax, eax
        rep     stosb
        pop     rcx
        pop     rsi
        lea     rdi, [region]
        rep     movsb
        lea     rdi, [region]
        mov     eax, [rdi + 24]         ; the header's byte entry offset
        add     rax, rdi
        mov     [cur_entry], rax
        ret

; run_block - AL = the tag; cur_entry is set. Everything a decoder may clobber
; is kept in memory: nothing but RSP survives the call.
run_block:
        push    rax
        lea     rsi, [msg_block]
        call    puts
        mov     eax, [block]
        call    puthex
        mov     al, ' '
        call    putc
        pop     rax
        call    putc
        call    newline
        inc     dword [block]
        mov     qword [idx], 0
.loop:
        mov     rax, [idx]
        cmp     rax, corpus_n
        jae     .out
        mov     qword [got_first], 0

        rdtsc
        shl     rdx, 32
        or      rax, rdx
        mov     [t0], rax

        mov     rax, [idx]
        lea     rcx, [corpus]
        movzx   edi, byte [rcx + rax * 2]
        movzx   esi, byte [rcx + rax * 2 + 1]
        lea     rdx, [rax + 1]
        shl     rdx, 8                  ; the stamp: (index + 1) << 8
        lea     rcx, [svc]
        call    [cur_entry]

        rdtsc
        shl     rdx, 32
        or      rax, rdx
        cmp     qword [got_first], 0
        je      .have
        mov     rax, [t_first]
.have:
        sub     rax, [t0]
        call    puthex
        call    newline
        inc     qword [idx]
        jmp     .loop
.out:
        ret

; The null decoder: what the path costs with no decoder in it.
null_byte:
        ret

; The upcalls. The first instruction that matters is the RDTSC; R8 keeps
; mouse_packet's RDX. They preserve RBX, RBP and R12-R15 by not using them.
key_event:
        mov     r8, rdx
        rdtsc
        cmp     qword [got_first], 0
        jne     .printed
        shl     rdx, 32
        or      rax, rdx
        mov     [t_first], rax
        mov     qword [got_first], 1
.printed:
        mov     r9, rdi
        mov     r10, rsi
        mov     al, 'k'
        call    putc
        mov     al, ' '
        call    putc
        mov     rax, r9
        call    puthex
        mov     al, ' '
        call    putc
        mov     rax, r10
        call    puthex
        jmp     newline

mouse_packet:
        mov     r8, rdx
        rdtsc
        cmp     qword [got_first], 0
        jne     .printed
        shl     rdx, 32
        or      rax, rdx
        mov     [t_first], rax
        mov     qword [got_first], 1
.printed:
        mov     r9, rdi
        mov     r10, rsi
        mov     r11, rcx
        mov     al, 'p'
        call    putc
        mov     al, ' '
        call    putc
        mov     rax, r9
        call    puthex
        mov     al, ' '
        call    putc
        mov     rax, r10
        call    puthex
        mov     al, ' '
        call    putc
        mov     rax, r8
        call    puthex
        mov     al, ' '
        call    putc
        mov     rax, r11
        call    puthex
        jmp     newline

svc_zero:
        xor     eax, eax
        ret

; ------------------------------------------------------------- serial -----
serial_init:
        mov     dx, COM1 + 1
        xor     al, al
        out     dx, al                  ; no interrupts
        mov     dx, COM1 + 3
        mov     al, 0x80
        out     dx, al                  ; DLAB
        mov     dx, COM1
        mov     al, 1
        out     dx, al                  ; 115200
        mov     dx, COM1 + 1
        xor     al, al
        out     dx, al
        mov     dx, COM1 + 3
        mov     al, 3
        out     dx, al                  ; 8N1
        ret

; putc - AL; preserves everything but RAX and RDX.
putc:
        push    rax
        mov     dx, COM1 + 5
.w:     in      al, dx
        test    al, 0x20
        jz      .w
        pop     rax
        mov     dx, COM1
        out     dx, al
        ret

newline:
        mov     al, 10
        jmp     putc

; puts - RSI = a NUL-terminated string.
puts:
.n:     lodsb
        test    al, al
        jz      .out
        call    putc
        jmp     .n
.out:   ret

; puthex - RAX in hex, no leading zeros; clobbers RAX, RCX, RDX, RSI, RDI.
puthex:
        mov     rsi, rax
        mov     ecx, 60
.skip:
        mov     rax, rsi
        shr     rax, cl
        test    al, 0x0F
        jnz     .digit
        sub     ecx, 4
        jnz     .skip
.digit:
        mov     rax, rsi
        shr     rax, cl
        and     eax, 0x0F
        lea     rdi, [hexdigits]
        mov     al, [rdi + rax]
        push    rcx
        call    putc
        pop     rcx
        sub     ecx, 4
        jns     .digit
        ret

hexdigits:      db      '0123456789abcdef'
msg_corpus:     db      'bench: corpus ', 0
msg_block:      db      'B ', 0
msg_done:       db      'bench: done', 0

        align   FILE_ALIGN, db 0
text_size       equ     $ - text_start

; ===========================================================================
data_start:
generic:        incbin  GENERIC
generic_len     equ     $ - generic
        align   8, db 0
candidate:      incbin  CANDIDATE
candidate_len   equ     $ - candidate
        align   8, db 0
corpus:         incbin  CORPUS
corpus_n        equ     ($ - corpus) / 2
        align   FILE_ALIGN, db 0
data_raw_size   equ     $ - data_start

absolute data_start + data_raw_size
svc:            resb    80
cur_entry:      resq    1
idx:            resq    1
t0:             resq    1
t_first:        resq    1
got_first:      resq    1
block:          resd    1
                alignb  4096
pml4:           resb    4096
pdpt:           resb    4096
pds:            resb    4096 * 4
region:         resb    REGION_SIZE
                resb    65536
stack_top:
bss_end:

data_virt_size  equ     bss_end - data_start
bss_size        equ     data_virt_size - data_raw_size
image_size      equ     data_start + ((data_virt_size + 0xFFF) & ~0xFFF)
