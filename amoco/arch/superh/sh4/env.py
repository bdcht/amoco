# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2018 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

#reference documentation:
# The SH-4 CPU Core Architecture, 12 september 2002.

#registers :
#-----------

#general registers:
R = [reg('R%2d'%r,32) for r in range(16)]

#bank1 for R0-R7:
r = [reg('r%d'%r,32) for r in range(8)]

#system registers:

#status register:
SR    = reg('SR',32)
#program counter(s):
PC    = reg('PC',32)
npc   = reg("PC'",32)
nnpc  = reg('PC"',32)
#floating point status/control register:
FPSCR = reg('FPSCR',32)
#floating point communication register:
FPUL  = reg('FPUL',32)
#multiply-and-accumulate regs:
MACH  = reg('MACH',32)
MACL  = reg('MACL',32)
#procedure link register:
PR    = reg('PR',32)
#global base register:
GBR   = reg('GBR',32)

#status sub-registers:
T  = slc(SR, 0,1,'SR.T')            # condition code flag
S  = slc(SR, 1,1,'SR.S')            # multiply-accumulate saturation flag
IMASK = slc(SR, 2,4, 'SR.IMASK')
Q  = slc(SR, 8,1,'SR.Q')            # divide-step Q flag
M  = slc(SR, 9,1,'SR.M')            # divide-step M flag
FD = slc(SR,15,1,'SR.FD')
BL = slc(SR,28,1,'SR.BL')
RB = slc(SR,29,1,'SR.RB')
MD = slc(SR,30,1,'SR.MD')

#PTE registers:
PTEH  = reg('PTEH',32)
PTEL  = reg('PTEL',32)
TTB   = reg('TTB',32)
TEA   = reg('TEA',32)
MMUCR = reg('MMUCR',32)

#PTEH sub-registers:
ASID  = slc(PTEH,0,8,'PTEH.ASID')
VPN   = slc(PTEH,10,22,'PTEH.VPN')

#PTEL sub-registers:
WT    = slc(PTEL,0,1,'PTEL.WT')
SH    = slc(PTEL,1,1,'PTEL.SH')
D     = slc(PTEL,2,1,'PTEL.D')
C     = slc(PTEL,3,1,'PTEL.C')
SZ0   = slc(PTEL,4,1,'PTEL.SZ0')
PR_   = slc(PTEL,5,2,'PTEL.PR')
SZ1   = slc(PTEL,7,1,'PTEL.SZ1')
V     = slc(PTEL,8,1,'PTEL.V')
PPN   = slc(PTEL,10,19,'PTEL.PPN')

#MMUCR sub-registers:
AT    = slc(MMUCR,0,1,'MMUCR.AT')
TI    = slc(MMUCR,2,1,'MMUCR.TI')
SV    = slc(MMUCR,8,1,'MMUCR.SV')
SQMD  = slc(MMUCR,9,1,'MMUCR.SQMD')
URC   = slc(MMUCR,10,6,'MMUCR.URC')
URB   = slc(MMUCR,18,6,'MMUCR.URB')
LRUI  = slc(MMUCR,26,6,'MMUCR.LRUI')

