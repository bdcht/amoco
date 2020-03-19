# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# reference documentation:
# MSP430x1xx User's Guide, Texas Instruments, 2006.

# registers :
# -----------

# general registers:
R = [reg("r%d" % x, 16) for x in range(16)]

pc = R[0]
sp = R[1]
sr = R[2]
cg1 = sr
cg2 = R[3]

pc.ref = "pc"
sp.ref = "sp"
sr.ref = "sr"

cf = slc(sr, 0, 1, ref="cf")
zf = slc(sr, 1, 1, ref="zf")
nf = slc(sr, 2, 1, ref="nf")
vf = slc(sr, 8, 1, ref="vf")

COND = {
    0b000: ("NE/NZ", zf == bit0),
    0b001: ("EQ/Z", zf == bit1),
    0b010: ("NC/LO", cf == bit0),
    0b011: ("C/HS", cf == bit1),
    0b100: ("N", nf == bit1),
    0b101: ("GE", vf == nf),
    0b110: ("L", vf != nf),
    0b111: ("", bit1),
}
