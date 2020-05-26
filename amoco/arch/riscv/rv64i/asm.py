# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *
from ..utils import *

from amoco.cas.utils import *

# ------------------------------------------------------------------------------
# helpers and decorators :
def _push_(fmap, _x):
    fmap[sp] = fmap[sp] - _x.length
    fmap[mem(sp, _x.size)] = _x


def _pop_(fmap, _l):
    fmap[_l] = fmap(mem(sp, _l.size))
    fmap[sp] = fmap[sp] + _l.length


def __npc(i_xxx):
    def npc(ins, fmap):
        fmap[pc] = fmap(pc) + ins.length
        i_xxx(ins, fmap)

    return npc


def trap(ins, fmap, trapname):
    fmap.internals["trap"] = trapname


# i_xxx is the translation of RISC-V instruction xxx.
# ------------------------------------------------------------------------------


@__npc
def i_LB(ins, fmap):
    dst, src = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src).signextend(64)


@__npc
def i_LBU(ins, fmap):
    dst, src = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src).zeroextend(64)


@__npc
def i_LH(ins, fmap):
    dst, src = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src).signextend(64)


@__npc
def i_LHU(ins, fmap):
    dst, src = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src).zeroextend(64)


@__npc
def i_LW(ins, fmap):
    dst, src = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src)


@__npc
def i_SB(ins, fmap):
    dst, src = ins.operands
    if dst.a.base is not zero:
        fmap[dst] = fmap(src[0:8])


@__npc
def i_SH(ins, fmap):
    dst, src = ins.operands
    if dst.a.base is not zero:
        fmap[dst] = fmap(src[0:16])


@__npc
def i_SW(ins, fmap):
    dst, src = ins.operands
    if dst.a.base is not zero:
        fmap[dst] = fmap(src)


@__npc
def i_ADD(ins, fmap):
    dst, src1, src2 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src1 + src2)


@__npc
def i_ADDI(ins, fmap):
    dst, src1, src2 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src1 + src2)


@__npc
def i_SUB(ins, fmap):
    dst, src1, src2 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src1 - src2)


@__npc
def i_AND(ins, fmap):
    dst, src1, src2 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src1 & src2)


@__npc
def i_OR(ins, fmap):
    dst, src1, src2 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src1 | src2)


@__npc
def i_XOR(ins, fmap):
    dst, src1, src2 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src1 ^ src2)


@__npc
def i_ANDI(ins, fmap):
    dst, src1, src2 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src1 & src2)


@__npc
def i_ORI(ins, fmap):
    dst, src1, src2 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src1 | src2)


@__npc
def i_XORI(ins, fmap):
    dst, src1, src2 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src1 ^ src2)


@__npc
def i_SLT(ins, fmap):
    dst, rs1, rs2 = ins.operands
    if dst is not zero:
        _t = rs1 < rs2
        fmap[dst] = fmap(tst(_t, cst(1, 64), cst(0, 64)))


@__npc
def i_SLTU(ins, fmap):
    dst, rs1, rs2 = ins.operands
    if dst is not zero:
        _t = oper(OP_LTU, rs1, rs2)
        fmap[dst] = fmap(tst(_t, cst(1, 64), cst(0, 64)))


@__npc
def i_SLTI(ins, fmap):
    dst, rs1, rs2 = ins.operands
    if dst is not zero:
        _t = rs1 < rs2
        fmap[dst] = fmap(tst(_t, cst(1, 64), cst(0, 64)))


@__npc
def i_SLTIU(ins, fmap):
    dst, rs1, rs2 = ins.operands
    if dst is not zero:
        _t = oper(OP_LTU, rs1, rs2)
        fmap[dst] = fmap(tst(_t, cst(1, 64), cst(0, 64)))


@__npc
def i_SLL(ins, fmap):
    dst, src1, src2 = ins.operands
    src1.sf = src2.sf = False
    src2 = src2 & 0x1F
    if dst is not zero:
        fmap[dst] = fmap(src1 << src2)


@__npc
def i_SRL(ins, fmap):
    dst, src1, src2 = ins.operands
    src1.sf = src2.sf = False
    src2 = src2 & 0x1F
    if dst is not zero:
        fmap[dst] = fmap(src1 >> src2)


@__npc
def i_SRA(ins, fmap):
    dst, src1, src2 = ins.operands
    src1.sf = True
    src2.sf = False
    src2 = src2 & 0x1F
    if dst is not zero:
        fmap[dst] = fmap(oper(OP_ASR, src1, src2))


@__npc
def i_SLLI(ins, fmap):
    dst, src1, src2 = ins.operands
    src1.sf = src2.sf = False
    if dst is not zero:
        fmap[dst] = fmap(src1 << src2)


@__npc
def i_SRLI(ins, fmap):
    dst, src1, src2 = ins.operands
    src1.sf = src2.sf = False
    if dst is not zero:
        fmap[dst] = fmap(src1 >> src2)


@__npc
def i_SRAI(ins, fmap):
    dst, src1, src2 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(oper(OP_ASR, src1, src2))


@__npc
def i_LUI(ins, fmap):
    dst, src1 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(src1)


@__npc
def i_AUIPC(ins, fmap):
    dst, src1 = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(pc + src1)


def i_JAL(ins, fmap):
    dst, imm = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(pc + ins.length)
    fmap[pc] = fmap(pc + imm)


def i_JALR(ins, fmap):
    dst, src1, imm = ins.operands
    if dst is not zero:
        fmap[dst] = fmap(pc + ins.length)
    fmap[pc] = fmap(src1 + imm)


def i_BEQ(ins, fmap):
    r1, r2, imm = ins.operands
    fmap[pc] = fmap(tst(r1 == r2, pc + imm, pc + ins.length))


def i_BNE(ins, fmap):
    r1, r2, imm = ins.operands
    fmap[pc] = fmap(tst(r1 != r2, pc + imm, pc + ins.length))


def i_BLT(ins, fmap):
    r1, r2, imm = ins.operands
    fmap[pc] = fmap(tst(r1 < r2, pc + imm, pc + ins.length))


def i_BLTU(ins, fmap):
    r1, r2, imm = ins.operands
    fmap[pc] = fmap(tst(oper(OP_LTU, r1, r2), pc + imm, pc + ins.length))


def i_BGE(ins, fmap):
    r1, r2, imm = ins.operands
    fmap[pc] = fmap(tst(r1 >= r2, pc + imm, pc + ins.length))


def i_BGEU(ins, fmap):
    r1, r2, imm = ins.operands
    fmap[pc] = fmap(tst(oper(OP_GEU, r1, r2), pc + imm, pc + ins.length))


@__npc
def i_SB(ins, fmap):
    dst, src = ins.operands
    fmap[dst] = fmap(src[0:8])


@__npc
def i_SH(ins, fmap):
    dst, src = ins.operands
    fmap[dst] = fmap(src[0:16])


@__npc
def i_SW(ins, fmap):
    dst, src = ins.operands
    fmap[dst] = fmap(src)


@__npc
def i_LB(ins, fmap):
    dst, src = ins.operands
    fmap[dst] = fmap(src).signextend(64)


i_LH = i_LW = i_LB


@__npc
def i_LBU(ins, fmap):
    dst, src = ins.operands
    fmap[dst] = fmap(src).zeroextend(64)


i_LHU = i_LBU


@__npc
def i_FENCE(ins, fmap):
    pass


@__npc
def i_FENCE_I(ins, fmap):
    pass


@__npc
def i_ECALL(ins, fmap):
    pass
