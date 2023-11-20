# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2022 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# registers :
# -----------

# general purpose:
GPR = [reg("r%d"%i,32) for i in range(32)]

# Integer Exception register:
XER = reg("XER", 32)
# XER flags:
SO = slc(XER,31,1,"SO")
OV = slc(XER,30,1,"OV")
CA = slc(XER,29,1,"CA")
NoB = slc(XER,0,7,"NoB")

# floating-point registers:
FPR = [reg("f%d"%i,64) for i in range(32)]
FPSCR = reg("FPSCR", 32)

CR = reg("CR",32)     # control register
MSR = reg("MSR",32)
CTR = reg("CTR",32)   # counter register
LR = reg("lr",32)     # link register

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

PID = reg("PID",32)

pc = reg("pc",32)
sp = reg("sp",32)

is_reg_pc(pc)
is_reg_stack(sp)
is_reg_flags(CR0)

R = GPR

# list of registers used by emulator views:
registers = R+[SO,CR0,LR,pc]

def DCREG(indx):
    return reg("DCRN_%d"%indx,32)
def SPREG(indx):
    return D_SPREG.get(indx,reg("SPREG#%d"%indx,32))

D_SPREG = {
        58: reg("CSRR0",32),
        59: reg("CSRR1",32),
        9: CTR,
        316: reg("DAC1",32),
        317: reg("DAC2",32),
        308: reg("DBCR0",32),
        309: reg("DBCR1",32),
        310: reg("DBCR2",32),
        304: reg("DBSR",32),
        61: reg("DEAR",32),
        22: reg("DEC",32),
        54: reg("DECAR",32),
        318: reg("DVC1",32),
        319: reg("DVC2",32),
        62: reg("ESR",32),
        63: reg("IVPR",32),
        312: reg("IAC1",32),
        313: reg("IAC2",32),
        314: reg("IAC3",32),
        315: reg("IAC4",32),
        400: reg("IVOR0",32),
        401: reg("IVOR1",32),
        402: reg("IVOR2",32),
        403: reg("IVOR3",32),
        404: reg("IVOR4",32),
        405: reg("IVOR5",32),
        406: reg("IVOR6",32),
        407: reg("IVOR7",32),
        408: reg("IVOR8",32),
        409: reg("IVOR9",32),
        410: reg("IVOR10",32),
        411: reg("IVOR11",32),
        412: reg("IVOR12",32),
        413: reg("IVOR13",32),
        414: reg("IVOR14",32),
        415: reg("IVOR15",32),
        8: LR,
        48: PID,
        286: reg("PIR",32),
        287: reg("PVR",32),
        1: XER,
}
