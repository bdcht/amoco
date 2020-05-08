# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# reference documentations:
# The MIPS Instruction Set Manual


# registers :
# -----------

zero = cst(0,32)

# return values:
v0 = reg("v0",32)
v1 = reg("v1",32)

# arguments:
a0 = reg("a0",32)
a1 = reg("a1",32)
a2 = reg("a2",32)
a3 = reg("a3",32)

# temporary:
t0 = reg("t0",32)
t1 = reg("t1",32)
t2 = reg("t2",32)
t3 = reg("t3",32)
t4 = reg("t4",32)
t5 = reg("t5",32)
t6 = reg("t6",32)
t7 = reg("t7",32)

# saved:
s0 = reg("s0",32)
s1 = reg("s1",32)
s2 = reg("s2",32)
s3 = reg("s3",32)
s4 = reg("s4",32)
s5 = reg("s5",32)
s6 = reg("s6",32)
s7 = reg("s7",32)

# more temporary
t8 = reg("t8",32)
t9 = reg("t9",32)

# kernel
k0 = reg("k0",32)
k1 = reg("k1",32)

# global area pointer
gp = reg("gp",32)

# stack pointer
sp = reg("sp",32)

# frame pointer
fp = reg("fp",32)

# return address
ra = reg("ra",32)

HI = reg("HI",32)
LO = reg("LO",32)

f = [reg("f%d"%i,32) for i in range(32)]

pc = reg("pc",32)
npc = reg("npc",32)

# status register
sr = reg("sr",32)

# assembler temp
at = reg("at",32)

IEc = slc(sr,0,1,"IEc")
KUc = slc(sr,1,1,"KUc")
IEp = slc(sr,2,1,"IEp")
KUp = slc(sr,3,1,"KUp")
IEo = slc(sr,4,1,"IEo")
KUo = slc(sr,5,1,"KUo")
IM  = slc(sr,8,8,"IM")
IsC = slc(sr,16,1,"IsC")
SwC = slc(sr,17,1,"SwC")
PZ  = slc(sr,18,1,"PZ")
CM  = slc(sr,19,1,"CM")
PE  = slc(sr,20,1,"PE")
TS  = slc(sr,21,1,"TS")
BEV = slc(sr,22,1,"BEV")
RE  = slc(sr,25,1,"RE")
CU0 = slc(sr,28,1,"CU0")
CU1 = slc(sr,29,1,"CU1")
CU2 = slc(sr,30,1,"CU2")
CU3 = slc(sr,31,1,"CU3")

is_reg_pc(pc)
is_reg_stack(sp)
is_reg_flags(sr)

R = [zero,at,v0,v1,a0,a1,a2,a3,
     t0,t1,t2,t3,t4,t5,t6,t7,
     s0,s1,s2,s3,s4,s5,s6,s7,
     t8,t9,
     k0,k1,
     gp,sp,fp,ra]

# list of registers used by emulator views:
registers = [v0,v1,a0,a1,a2,a3,
             t0,t1,t2,t3,t4,t5,t6,t7,t8,t9,
             s0,s1,s2,s3,s4,s5,s6,s7,
             gp,sp,fp,ra,pc]

