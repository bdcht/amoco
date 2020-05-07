# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# reference documentation:
# "ARM Architecture Reference Manual ARMv7-A and ARMv7-R" (DDI0406B)

# registers (application level, see B1.3.2) :
# -------------------------------------------

r0 = reg("r0", 32)  #
r1 = reg("r1", 32)  #
r2 = reg("r2", 32)  #
r3 = reg("r3", 32)  #
r4 = reg("r4", 32)  #
r5 = reg("r5", 32)  #
r6 = reg("r6", 32)  #
r7 = reg("r7", 32)  #
r8 = reg("r8", 32)  #
r9 = reg("r9", 32)  #
r10 = reg("r10", 32)  #
r11 = reg("r11", 32)  #
r12 = reg("r12", 32)  #
r13 = reg("r13", 32)  #
r14 = reg("r14", 32)  #
r15 = reg("r15", 32)  #

regs = [r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15]

sp = r13
sp.ref = "sp"  # stack pointer
lr = r14
lr.ref = "lr"  # link register (return address)
pc = r15
pc.ref = "pc"  # program counter (instructions are always word-aligned)
# pc is pc_+4 in Thumb mode and pc_+8 in ARM mode,
pc_ = reg("pc_", 32)  # current instruction pointer

apsr = reg("apsr", 32)  # current program status register

N = slc(apsr, 31, 1, ref="N")  # negative result from ALU
Z = slc(apsr, 30, 1, ref="Z")  # zero flag
C = slc(apsr, 29, 1, ref="C")  # carry flag
V = slc(apsr, 28, 1, ref="V")  # overflow flag
Q = slc(apsr, 27, 1, ref="Q")  # overflow/saturation (DSP)

is_reg_flags(apsr)
is_reg_pc(pc)
is_reg_pc(pc_)
is_reg_stack(sp)

CONDITION_EQ = 0x0  # ==
CONDITION_NE = 0x1  # !=
CONDITION_CS = 0x2  # >= (unsigned)
CONDITION_CC = 0x3  # <  (unsigned)
CONDITION_MI = 0x4  # <0
CONDITION_PL = 0x5  # >=0
CONDITION_VS = 0x6  # overflow
CONDITION_VC = 0x7  # no overflow
CONDITION_HI = 0x8  # >  (unsigned)
CONDITION_LS = 0x9  # <= (unsigned)
CONDITION_GE = 0xA  # >= (signed)
CONDITION_LT = 0xB  # <  (signed)
CONDITION_GT = 0xC  # >  (signed)
CONDITION_LE = 0xD  # <= (signed)
CONDITION_AL = 0xE  # always
CONDITION_UNDEFINED = 0xF

CONDITION = {
    CONDITION_EQ: ("eq", Z == 1),  # ==
    CONDITION_NE: ("ne", Z == 0),  # !=
    CONDITION_CS: ("cs", C == 1),  # >= (unsigned)
    CONDITION_CC: ("cc", C == 0),  # <  (unsigned)
    CONDITION_MI: ("mi", N == 1),  # <0
    CONDITION_PL: ("pl", N == 0),  # >=0
    CONDITION_VS: ("vs", V == 1),  # overflow
    CONDITION_VC: ("vc", V == 0),  # no overflow
    CONDITION_HI: ("hi", (C == 1) & (Z == 0)),  # >  (unsigned)
    CONDITION_LS: ("ls", (C == 0) | (Z == 1)),  # <= (unsigned)
    CONDITION_GE: ("ge", (N == V)),  # >= (signed)
    CONDITION_LT: ("lt", (N != V)),  # <  (signed)
    CONDITION_GT: ("gt", (Z == 0) & (N == V)),  # >  (signed)
    CONDITION_LE: ("le", (Z == 1) | (N != V)),  # <= (signed)
    CONDITION_AL: ("  ", bit1),  # always
    CONDITION_UNDEFINED: ("??", top(1)),
}

# internal states not exposed to symbolic interpreter:
# -----------------------------------------------------
internals = {  # states MUST be in a mutable object !
    "isetstate": 0,  # 0: ARM, 1: Thumb, 2: Jazelle, 3: ThumbEE
    "itstate": 0,  # thumb internal parameter (see IT instruction)
    "endianstate": 0,  # 0: LE, 1: BE
    "ibigend": 0,  # instruction endianess (0: LE, 1:BE)
}

# SIMD and VFP (floating point) extensions:
# NOT IMPLEMENTED

# Coprocessor (CPxx) support:

cpname = ["p%02d" % x for x in range(16)]

cpregs = {}
cpregs["p15"] = [reg("c%02d" % x, 32) for x in range(16)]
