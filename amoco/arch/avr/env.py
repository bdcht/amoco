# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# registers :
# -----------

# main reg set:
R = [reg("R%d" % r, 8) for r in range(32)]

X = reg("X", 16)
R[26] = slc(X, 0, 8, "XL")
R[27] = slc(X, 8, 8, "XH")
Y = reg("Y", 16)
R[28] = slc(X, 0, 8, "YL")
R[29] = slc(X, 8, 8, "YH")
Z = reg("Z", 16)
R[30] = slc(X, 0, 8, "ZL")
R[31] = slc(X, 8, 8, "ZH")

with is_reg_flags:
    SREG = reg("SREG", 8)
    cf = slc(SREG, 0, 1, "C")  # Carry
    zf = slc(SREG, 1, 1, "Z")  # Zero
    nf = slc(SREG, 2, 1, "N")  # Negative
    vf = slc(SREG, 3, 1, "V")  # Overflow
    sf = slc(SREG, 4, 1, "S")  # N^V (sign test)
    hf = slc(SREG, 5, 1, "H")  # Half-carry
    tf = slc(SREG, 6, 1, "T")  # Transfer
    i_ = slc(SREG, 7, 1, "I")  # Global Interrupt

with is_reg_pc:
    pc = reg("PC", 16)

with is_reg_stack:
    sp = reg("SP", 16)

RAMPX = reg("RAMPX", 8)
RAMPY = reg("RAMPY", 8)
RAMPZ = reg("RAMPZ", 8)
RAMPD = reg("RAMPD", 8)
EIND = reg("EIND", 8)
