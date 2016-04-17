# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# 64bits registers :
#-------------------

rax    = reg('rax',64)     # accumulator for operands and results data
rbx    = reg('rbx',64)     # pointer to data in the DS segment
rcx    = reg('rcx',64)     # counter for string and loop operations
rdx    = reg('rdx',64)     # I/O pointer
rbp    = reg('rbp',64)     # pointer to data in the stack (SS segment)
rsp    = reg('rsp',64)     # stack pointer (SS segment)
rsi    = reg('rsi',64)     # ptr to data in segment pointed by DS; src ptr for strings
rdi    = reg('rdi',64)     # ptr to data in segment pointed by ES; dst ptr for strings
rip    = reg('rip',64)     # instruction pointer in 64 bit mode
rflags = reg('rflags',64)


# 32bits registers :
#-------------------

eax = slc(rax,0,32,'eax')
ebx = slc(rbx,0,32,'ebx')
ecx = slc(rcx,0,32,'ecx')
edx = slc(rdx,0,32,'edx')
ebp = slc(rbp,0,32,'ebp')
esp = slc(rsp,0,32,'esp')
esi = slc(rsi,0,32,'esi')
edi = slc(rdi,0,32,'edi')
eflags = slc(rflags, 0, 32,'eflags')

ax = slc(rax,0,16,'ax')
bx = slc(rbx,0,16,'bx')
cx = slc(rcx,0,16,'cx')
dx = slc(rdx,0,16,'dx')
bp = slc(rbp,0,16,'bp')
sp = slc(rsp,0,16,'sp')
si = slc(rsi,0,16,'si')
di = slc(rdi,0,16,'di')

al = slc(rax,0,8,'al')
bl = slc(rbx,0,8,'bl')
cl = slc(rcx,0,8,'cl')
dl = slc(rdx,0,8,'dl')

spl = slc(rsp,0,8,'spl')
bpl = slc(rbp,0,8,'bpl')
sil = slc(rsi,0,8,'sil')
dil = slc(rdi,0,8,'dil')

ah = slc(rax,8,8,'ah')
bh = slc(rbx,8,8,'bh')
ch = slc(rcx,8,8,'ch')
dh = slc(rdx,8,8,'dh')

cf = slc(rflags,0,1,'cf')   # carry/borrow flag
pf = slc(rflags,2,1,'pf')   # parity flag
af = slc(rflags,4,1,'af')   # aux carry flag
zf = slc(rflags,6,1,'zf')   # zero flag
sf = slc(rflags,7,1,'sf')   # sign flag
df = slc(rflags,10,1,'df')  # direction flag
of = slc(rflags,11,1,'of')  # overflow flag

# segment registers & other mappings:
cs = reg('cs',16)      # segment selector for the code segment
ds = reg('ds',16)      # segment selector to a data segment
ss = reg('ss',16)      # segment selector to the stack segment
es = reg('es',16)      # (data)
fs = reg('fs',16)      # (data)
gs = reg('gs',16)      # (data)

r8 = reg('r8',64); r8d = slc(r8,0,32,'r8d'); r8w = slc(r8,0,16,'r8w'); r8l = slc(r8,0,8,'r8l')
r9 = reg('r9',64); r9d = slc(r9,0,32,'r9d'); r9w = slc(r9,0,16,'r9w'); r9l = slc(r9,0,8,'r9l')
r10 = reg('r10',64); r10d = slc(r10,0,32,'r10d'); r10w = slc(r10,0,16,'r10w'); r10l = slc(r10,0,8,'r10l')
r11 = reg('r11',64); r11d = slc(r11,0,32,'r11d'); r11w = slc(r11,0,16,'r11w'); r11l = slc(r11,0,8,'r11l')
r12 = reg('r12',64); r12d = slc(r12,0,32,'r12d'); r12w = slc(r12,0,16,'r12w'); r12l = slc(r12,0,8,'r12l')
r13 = reg('r13',64); r13d = slc(r13,0,32,'r13d'); r13w = slc(r13,0,16,'r13w'); r13l = slc(r13,0,8,'r13l')
r14 = reg('r14',64); r14d = slc(r14,0,32,'r14d'); r14w = slc(r14,0,16,'r14w'); r14l = slc(r14,0,8,'r14l')
r15 = reg('r15',64); r15d = slc(r15,0,32,'r15d'); r15w = slc(r15,0,16,'r15w'); r15l = slc(r15,0,8,'r15l')

# return R/M register (see ModR/M Byte encoding) :
def getreg(i,size=32):
    return {8   : (al,cl,dl,bl,spl,bpl,sil,dil,r8l,r9l,r10l,r11l,r12l,r13l,r14l,r15l),
            16  : (ax,cx,dx,bx,sp,bp,si,di,r8w,r9w,r10w,r11w,r12w,r13w,r14w,r15w),
            32  : (eax,ecx,edx,ebx,esp,ebp,esi,edi,r8d,r9d,r10d,r11d,r12d,r13d,r14d,r15d),
            64  : (rax,rcx,rdx,rbx,rsp,rbp,rsi,rdi,r8,r9,r10,r11,r12,r13,r14,r15),
           'mm' : mmregs,
            128 : xmmregs,
            256 : ymmregs,
           }[size][i]

# fpu registers (80 bits holds double extended floats see Intel Vol1--4.4.2):
def st(num):
  return reg('st%d'%num,80)

def cr(num):
  return reg('cr%d'%num,64)
def dr(num):
  return reg('dr%d'%num,64)

mmregs = [reg('mm%d'%n,64) for n in range(16)]

xmmregs = [reg('xmm%d'%n, 128) for n in range(16)]
ymmregs = [reg('ymm%d'%n, 256) for n in range(16)]

internals = {'mode':64}
