# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# 32bits registers :
#-------------------

eax    = reg('eax',32)     # accumulator for operands and results data
ebx    = reg('ebx',32)     # pointer to data in the DS segment
ecx    = reg('ecx',32)     # counter for string and loop operations
edx    = reg('edx',32)     # I/O pointer
ebp    = reg('ebp',32)     # pointer to data in the stack (SS segment)
esp    = reg('esp',32)     # stack pointer (SS segment)
esi    = reg('esi',32)     # ptr to data in segment pointed by DS; src ptr for strings
edi    = reg('edi',32)     # ptr to data in segment pointed by ES; dst ptr for strings
eip    = reg('eip',32)     # instruction pointer in 32 bit mode
eflags = reg('eflags',32)

is_reg_pc(eip)
is_reg_flags(eflags)
is_reg_stack(esp)
is_reg_stack(ebp)

ax = slc(eax,0,16,'ax')
bx = slc(ebx,0,16,'bx')
cx = slc(ecx,0,16,'cx')
dx = slc(edx,0,16,'dx')
bp = slc(ebp,0,16,'bp')
sp = slc(esp,0,16,'sp')
si = slc(esi,0,16,'si')
di = slc(edi,0,16,'di')

al = slc(eax,0,8,'al')
bl = slc(ebx,0,8,'bl')
cl = slc(ecx,0,8,'cl')
dl = slc(edx,0,8,'dl')

ah = slc(eax,8,8,'ah')
bh = slc(ebx,8,8,'bh')
ch = slc(ecx,8,8,'ch')
dh = slc(edx,8,8,'dh')

cf = slc(eflags,0,1,'cf')   # carry/borrow flag
pf = slc(eflags,2,1,'pf')   # parity flag
af = slc(eflags,4,1,'af')   # aux carry flag
zf = slc(eflags,6,1,'zf')   # zero flag
sf = slc(eflags,7,1,'sf')   # sign flag
tf = slc(eflags,8,1,'tf')   # trap flag
df = slc(eflags,10,1,'df')  # direction flag
of = slc(eflags,11,1,'of')  # overflow flag

with is_reg_other:
    # segment registers & other mappings:
    cs = reg('cs',16)      # segment selector for the code segment
    ds = reg('ds',16)      # segment selector to a data segment
    ss = reg('ss',16)      # segment selector to the stack segment
    es = reg('es',16)      # (data)
    fs = reg('fs',16)      # (data)
    gs = reg('gs',16)      # (data)

    mmregs = [reg('mm%d'%n,64) for n in range(8)]

    xmmregs = [reg('xmm%d'%n, 128) for n in range(16)]

# fpu registers (80 bits holds double extended floats see Intel Vol1--4.4.2):
def st(num):
  return is_reg_other(reg('st%d'%num,80))


# return R/M register (see ModR/M Byte encoding) :
def getreg(i,size=32):
    return {8   : (al,cl,dl,bl,ah,ch,dh,bh),
            16  : (ax,cx,dx,bx,sp,bp,si,di),
            32  : (eax,ecx,edx,ebx,esp,ebp,esi,edi),
            64  : mmregs,
            128 : xmmregs[:8],
            }[size][i]

# system registers:

# control regs:
def cr(num):
    return is_reg_other(reg('cr%d'%num,32))

# debug regs:
def dr(num):
    return is_reg_other(reg('dr%d'%num,32))

internals = {'mode': 32}
