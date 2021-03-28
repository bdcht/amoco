.text
.global _start

.code 16
_start:
	adr r0, _string
	eor r1, r1, r1
	eor r2, r2, r2
	strb r1, [r0, #7]
	mov r7, #11
	svc #1

_string:
.ascii  "/bin/shA"
