# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2018 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# registers :
# -----------

# main reg set:
R = [reg("r%d" % r, 32) for r in range(32)]

with is_reg_flags:
    PSW = reg("psw", 32)  # program-status word
    Z = slc(PSW, 0, 1, "z")  # Zero
    S = slc(PSW, 1, 1, "s")  # Sign
    OV = slc(PSW, 2, 1, "ov")  # Overlfow
    CY = slc(PSW, 3, 1, "cy")  # Carry
    SAT = slc(PSW, 4, 1, "sat")  # Saturation
    ID = slc(PSW, 5, 1, "id")  # EI exception (TRAP)
    EP = slc(PSW, 6, 1, "ep")  # exception type (0: interrupt, 1:other)
    NP = slc(PSW, 7, 1, "np")  # FE exception

    IMP = slc(
        PSW, 16, 1, "imp"
    )  # instruction memory protection (0: trusted, 1: not trusted)
    DMP = slc(PSW, 17, 1, "dmp")  # data memory protection (0: trusted, 1: not trusted)
    NPV = slc(PSW, 18, 1, "npv")  # non-protected value (0: trusted, 1: not trusted)

with is_reg_pc:
    pc = reg("pc", 16)

with is_reg_stack:
    sp = reg("sp", 32)  # stack ptr

R[0] = cst(0, 32).to_sym("zero")
R[3] = sp
R[4] = reg("gp", 32)  # global variable ptr
R[5] = reg("tp", 32)  # text area ptr
R[30] = reg("ep", 32)  # array/struct base ptr
R[31] = reg("lp", 32)  # link ptr

registers = R + [PSW, pc]

# system registers:
EIPC = reg("eipc", 32)
EIPSW = reg("eipsw", 32)
FEPC = reg("fepc", 32)
FEPSW = reg("fepsw", 32)
ECR = reg("ecr", 32)  # exception cause

SCCFG = reg("sccfg", 32)  # SYSCAL op setting
SCBP = reg("scbp", 32)  # SYSCAL base ptr
EIIC = reg("eiic", 32)
FEIC = reg("feic", 32)
DBIC = reg("dbic", 32)
CTPC = reg("ctpc", 32)
CTPSW = reg("ctpsw", 32)
DBPC = reg("dbpc", 32)
DBPSW = reg("dbpsw", 32)
CTBP = reg("ctbp", 32)  # CALLT base ptr

EIWR = reg("eiwr", 32)
FEWR = reg("fewr", 32)
DBWR = reg("dbwr", 32)
BSEL = reg("bsel", 32)  # register bank select

BNK = slc(BSEL, 0, 8, "bnk")
GRP = slc(BSEL, 8, 8, "grp")

CONDITION_V = 0b0000  # ==
CONDITION_NV = 0b1000  # !=
CONDITION_C = 0b0001  # >= (unsigned)
CONDITION_NC = 0b1001  # <  (unsigned)
CONDITION_Z = 0b0010  # <0
CONDITION_NZ = 0b1010  # <0
CONDITION_NH = 0b0011  # <0
CONDITION_H = 0b1011  # <0
CONDITION_S = 0b0100  # <0
CONDITION_NS = 0b1100  # <0
CONDITION_T = 0b0101  # <0
CONDITION_SA = 0b1101  # <0
CONDITION_LT = 0b0110  # <0
CONDITION_GE = 0b1110  # <0
CONDITION_LE = 0b0111  # <0
CONDITION_GT = 0b1111  # <0

CONDITION = {
    CONDITION_V: ("v", OV == 1),
    CONDITION_NV: ("nv", OV == 0),
    CONDITION_C: ("c", CY == 1),
    CONDITION_NC: ("nc", CY == 0),
    CONDITION_Z: ("z", Z == 1),
    CONDITION_NZ: ("nz", Z == 0),
    CONDITION_NH: ("nh", (CY | Z) == 1),
    CONDITION_H: ("h", (CY | Z) == 0),
    CONDITION_S: ("neg", S == 1),
    CONDITION_NS: ("pos", S == 0),
    CONDITION_T: ("", bit1),
    CONDITION_SA: ("sat", SAT == 1),
    CONDITION_LT: ("lt", (S ^ OV) == 1),
    CONDITION_GE: ("ge", (S ^ OV) == 0),
    CONDITION_LE: ("le", ((S ^ OV) | Z) == 1),
    CONDITION_GT: ("gt", ((S ^ OV) | Z) == 0),
}
