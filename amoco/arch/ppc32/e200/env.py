# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2022 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# registers :
# -----------

GPR = [reg("r%d"%i,32) for i in range(32)]

XER = reg("XER", 32)
SO = slc(XER,31,1,"SO")
OV = slc(XER,30,1,"OV")
CA = slc(XER,29,1,"CA")
NoB = slc(XER,0,7,"NoB")

FPR = [reg("f%d"%i,32) for i in range(32)]
FPSCR = reg("FPSCR", 32)

CR = reg("CR",32)
MSR = reg("MSR",32)
CTR = reg("CTR",32)
LR = reg("lr",32)

CR0 = slc(CR,28,4,"CR0")
CR1 = slc(CR,24,4,"CR1")
CR2 = slc(CR,20,4,"CR2")
CR3 = slc(CR,16,4,"CR3")
CR4 = slc(CR,12,4,"CR4")
CR5 = slc(CR, 8,4,"CR5")
CR6 = slc(CR, 4,4,"CR6")
CR7 = slc(CR, 0,4,"CR7")

LT = slc(CR0,3,1,"LT")
GT = slc(CR0,2,1,"GT")
EQ = slc(CR0,1,1,"EQ")
SO_ = slc(CR0,0,1,"SO")


pc = reg("pc",32)
sp = reg("sp",32)

is_reg_pc(pc)
is_reg_stack(sp)
is_reg_flags(CR0)

R = GPR

# list of registers used by emulator views:
registers = R+[SO,CR0,LR,pc]

