# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2012-2013 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

#reference documentation:
# The SPARC Architecture Manual Version 8, Revision SAV080SI9308.

#registers :
#-----------
NWINDOWS = 32 # in [2,32]

# general registers:
R = [reg('r%d'%x,32) for x in range(520)]
# fpu registers:
f = [reg('f%d'%x,32) for x in range(32)]
# coprocessor registers:
c = [reg('c%d'%x,32) for x in range(32)]

# symbols for r0 ... r7:
g0,g1,g2,g3,g4,g5,g6,g7 = (reg('g%d'%x,32) for x in range(8))
# window registers symbols:
o0,o1,o2,o3,o4,o5,o6,o7 = (reg('o%d'%x,32) for x in range(8))
l0,l1,l2,l3,l4,l5,l6,l7 = (reg('l%d'%x,32) for x in range(8))
i0,i1,i2,i3,i4,i5,i6,i7 = (reg('i%d'%x,32) for x in range(8))

r = [g0,g1,g2,g3,g4,g5,g6,g7,
     o0,o1,o2,o3,o4,o5,o6,o7,
     l0,l1,l2,l3,l4,l5,l6,l7,
     i0,i1,i2,i3,i4,i5,i6,i7]

fp     = i6 ; i6.ref = "fp"
sp     = o6 ; o6.ref = "sp"

psr    = reg('psr',32)    # Processor State Register
wim    = reg('wim',32)    # Window Invalid Mask
tbr    = reg('tbr',32)    # Trap Base Register
y      = reg('y',32)      # Multiply/Divide Register
# Program Counters
pc     = reg('pc',32)     # current
npc    = reg('npc',32)    # next
# implementation-dependent Ancillary State Registers
asr    = [reg('asr%d'%x,32) for x in range(32)]
# fpu control/status registers:
fsr    = reg('fsr',32)    # Floating-point State Register
fq     = reg('fq',32)     # implementation-dependent Floating-point Deffered-Trap Queue
# coprocessor control/status registers:
csr    = reg('csr',32)    # implementation-dependent coprocessor State Register
cq     = reg('cq',32)     # implementation-dependent Coprocessor Deffered-Trap Queue

def hi(r):
    return slc(r,10,22)

def lo(r):
    return slc(r,0,10)

# psr symbols:
impl = slc(psr,28,4)       # implementation
ver  = slc(psr,24,4)       # version
icc  = slc(psr,20,4)       # condition codes:
nf   = slc(icc,3,1)        # negative flag
zf   = slc(icc,2,1)        # zero flag
vf   = slc(icc,1,1)        # overflow flag
cf   = slc(icc,0,1)        # carry flag
EC   = slc(psr,13,1)       # enable coprocessor
EF   = slc(psr,12,1)       # enable floating-point
PIL  = slc(psr,8,4)        # proc_interrupt_level
S    = slc(psr,7,1)        # supervisor mode
PS   = slc(psr,6,1)        # previous supervisor
ET   = slc(psr,5,1)        # enable Trap
cwp  = slc(psr,0,4)        # current window pointer

# tbr symbols:
tba  = slc(tbr,12,20)      # trap base address
tt   = slc(tbr,4,8)        # trap type

# fsr symbols:
RD   = slc(fsr,30,2)       # rounding direction (0: nearest, 1: 0, 2:+inf, 3=-inf)
TEM  = slc(fsr,23,5)       # trap enable mask
NS   = slc(fsr,22,1)       # non-standard fp
fver = slc(fsr,17,3)       # FPU architecture version
ftt  = slc(fsr,14,3)       # fp trap type (see table 4-4, p.36)
qne  = slc(fsr,13,1)       # fsr FQ not empty
fcc  = slc(fsr,10,2)       # condition codes (=,<,>,?)
aexc = slc(fsr,5,5)        # IEEE 754 fp exceptions accumulator
cexc = slc(fsr,0,5)        # current IEEE 754 exception
