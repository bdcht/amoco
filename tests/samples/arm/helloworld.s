.file "helloworld.s"
.section ".text"
.align 4
.global main
.type main, #function

main:
      push  {r0,r10,pc}
      ldr   r3, [pc, #228]
      cmp   r3, #0

