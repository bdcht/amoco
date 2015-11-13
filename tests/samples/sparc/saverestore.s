	.file	"saverestore.c"
	.section ".text"
	.align 4
	.proc	020
main:
	save	%sp, -8, %sp
        mov     %i0, %o3
        mov     %i1, %g3
        add     %i1,%o3,%l2
        save
        add     %g3,%i3,%i0
        restore
        sub     %o0,%l2,%i2
        restore
	jmp	%o7+8
	nop
	.size	main, .-main
	.ident	"GCC: (GNU) 4.4.2"
