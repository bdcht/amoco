# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2018 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

#reference documentation:
# The SH-2A, SH-2A-FPU Software Manual, rev. 3.00, July 8 2005.

#registers :
#-----------

#general registers:
R = [reg('R%d'%r,32) for r in range(16)]
sp = R[15]
is_reg_stack(sp)

#status register:
SR    = reg('SR',32)
is_reg_flags(SR)

#program counter(s):
with is_reg_pc:
  pc    = reg('PC',32)
  npc   = reg("PC'",32)

#multiply-and-accumulate regs:
MACH  = reg('MACH',32)
MACL  = reg('MACL',32)

#procedure link register:
PR    = reg('PR',32)

#global base register:
GBR   = reg('GBR',32)
#vector base register:
VBR   = reg('VBR',32)
#jumptable base register:
TBR   = reg('TBR',32)

#status sub-registers:
T  = slc(SR, 0,1,'T')            # true/false condition code flag
S  = slc(SR, 1,1,'S')            # multiply-accumulate saturation flag
IMASK = slc(SR, 4,4, 'IMASK')    # interrupt mask
Q  = slc(SR, 8,1,'Q')            # divide-step Q flag
M  = slc(SR, 9,1,'M')            # divide-step M flag
CS = slc(SR,13,1,'CS')           # CLIP saturation flag
BO = slc(SR,14,1,'BO')           # register bank overflow flag

#floating point status/control register:
FPSCR = reg('FPSCR',32)
is_reg_flags(FPSCR)
#floating point communication register:
FPUL  = reg('FPUL',32)
#floating point registers:
DR    = [reg('DR%d'%r,64) for r in range(0,16,2)]
FR = []
i  = 0
for r in DR:
    FR.append(slc(r,32,32,'FR%d'%i))
    FR.append(slc(r,0,32,'FR%d'%(i+1)))
    i+=2

qis = slc(FPSCR,22,1,'qis')
sz = slc(FPSCR,20,1,'sz')
pr = slc(FPSCR,19,1,'pr')
dn = slc(FPSCR,18,1,'dn')
RM = slc(FPSCR,0,2,'RM')

# register banks
IBCR = reg('IBCR',16)

IBNR = reg('IBNR',16)
is_reg_flags(IBNR)
BN0 = slc(IBNR,0,1,'BN0')
BN1 = slc(IBNR,1,1,'BN1')
BN2 = slc(IBNR,2,1,'BN2')
BN3 = slc(IBNR,3,1,'BN3')
BOVE = slc(IBNR,13,1,'BOVE')
BE0 = slc(IBNR,14,1,'BE0')
BE1 = slc(IBNR,15,1,'BE1')
