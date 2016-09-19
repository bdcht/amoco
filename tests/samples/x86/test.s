.global main
.intel_syntax noprefix

.extern getchar
.extern printf

.section .data
jmpTable:
        .long _stub0
        .long _stub1
        .long _stub2
fmt: .asciz "%x\n"

.section .text

main:
        call getchar
        mov dl, 4
        imul dl
        add eax, offset jmpTable
        jmp [eax]
        .long 3851

_stub0:
        mov eax, 0
        jmp _end
        .long 3851

_stub1:
        mov eax, 1
        jmp _end
        .long 3851

_stub2:
        mov eax, 2
        jmp _end
        .long 3851

_end:
        push eax
        push offset fmt
        call printf
        add esp, 8
        ret
