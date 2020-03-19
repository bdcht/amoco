# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2013 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *

from amoco.cas.utils import *


def autoinc(i, fmap):
    rr = i.misc["autoinc"]
    sz = 2 if i.BW else 1
    if rr is not None:
        fmap[rr] = fmap(rr + sz)


# Ref: MSP430x1xx Family Users's Guide (Rev. F)
# ------------------------------------------------------------------------------


def i_MOV(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    src, dst = i.operands
    fmap[dst] = fmap(src)
    autoinc(i, fmap)


def i_ADD(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    src, dst = i.operands
    result, carry, overflow = AddWithCarry(fmap(src), fmap(dst))
    fmap[dst] = result
    fmap[cf] = carry
    fmap[zf] = result == 0
    fmap[nf] = result[dst.size - 1 : dst.size]
    fmap[vf] = overflow
    autoinc(i, fmap)


def i_ADDC(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    src, dst = i.operands
    result, carry, overflow = AddWithCarry(fmap(src), fmap(dst), fmap(cf))
    fmap[dst] = result
    fmap[cf] = carry
    fmap[zf] = result == 0
    fmap[nf] = result[dst.size - 1 : dst.size]
    fmap[vf] = overflow
    autoinc(i, fmap)


def i_SUB(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    src, dst = i.operands
    result, carry, overflow = AddWithCarry(fmap(src), fmap(dst))
    fmap[dst] = result
    fmap[cf] = carry
    fmap[zf] = result == 0
    fmap[nf] = result[dst.size - 1 : dst.size]
    fmap[vf] = overflow
    autoinc(i, fmap)


def i_CMP(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    src, dst = i.operands
    result, carry, overflow = AddWithCarry(fmap(src), fmap(dst))
    fmap[cf] = carry
    fmap[zf] = result == 0
    fmap[nf] = result[dst.size - 1 : dst.size]
    fmap[vf] = overflow
    autoinc(i, fmap)


def i_SUBC(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    src, dst = i.operands
    result, carry, overflow = AddWithCarry(fmap(src), fmap(dst), fmap(cf))
    fmap[dst] = result
    fmap[cf] = carry
    fmap[zf] = result == 0
    fmap[nf] = result[dst.size - 1 : dst.size]
    fmap[vf] = overflow
    autoinc(i, fmap)


def i_AND(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    src, dst = i.operands
    result = fmap(src & dst)
    fmap[dst] = result
    fmap[nf] = result[dst.size - 1 : dst.size]
    fmap[zf] = result == 0
    fmap[cf] = ~fmap(zf)
    fmap[vf] = bit0
    autoinc(i, fmap)


def i_XOR(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    src, dst = i.operands
    fmap[dst] = fmap(src ^ dst)
    fmap[nf] = result[dst.size - 1 : dst.size]
    fmap[zf] = result == 0
    fmap[cf] = ~fmap(zf)
    fmap[vf] = bit0
    autoinc(i, fmap)


def i_BIC(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    src, dst = i.operands
    fmap[dst] = fmap((~src) & dst)
    autoinc(i, fmap)


def i_BIS(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    src, dst = i.operands
    fmap[dst] = fmap(src | dst)
    autoinc(i, fmap)


def i_BIT(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    src, dst = i.operands
    result = fmap(src | dst)
    fmap[nf] = result[dst.size - 1 : dst.size]
    fmap[zf] = result == 0
    fmap[cf] = ~fmap(zf)
    fmap[vf] = bit0
    autoinc(i, fmap)


def i_CALL(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    dst = i.operands[0]
    tmp = fmap(dst)
    fmap[sp] = fmap(sp - 2)
    fmap[mem(sp, pc.size)] = fmap(pc)
    fmap[pc] = tmp
    autoinc(i, fmap)


# def i_RETI(i,fmap):
#    dst = i.operands[0]

# def i_DADD(i,fmap):
#    NotImplemented


def i_RRC(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    dst = i.operands[0]
    res, carry = RORWithCarry(fmap(dst), 1, fmap(cf))
    fmap[dst] = res
    fmap[cf] = carry
    fmap[nf] = res[dst.size - 1 : dst.size]
    fmap[zf] = res == 0
    fmap[vf] = bit0


def i_SWPB(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    dst = i.operands[0]
    res = composer([fmap(dst[8:16]), fmap(dst[0:8])])
    fmap[dst] = res


def i_RRA(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    dst = i.operands[0]
    res, carry = RORWithCarry(fmap(dst), 1, fmap(dst[dst.size - 1 : dst.size]))
    fmap[dst] = res
    fmap[cf] = carry
    fmap[nf] = res[dst.size - 1 : dst.size]
    fmap[zf] = res == 0
    fmap[vf] = bit0


def i_SXT(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    dst = i.operands[0]
    res = fmap(dst[0:8]).signextend(16)
    fmap[dst] = res
    fmap[nf] = res[dst.size - 1 : dst.size]
    fmap[zf] = res == 0
    fmap[cf] = ~fmap(zf)
    fmap[vf] = bit0


def i_PUSH(i, fmap):
    src = i.operands[0]
    fmap[sp] = fmap(sp - src.size)
    fmap[mem(sp, src.size)] = fmap(src)
    autoinc(i, fmap)


def i_JMP(i, fmap):
    offset = i.operands[0] * 2
    fmap[pc] = fmap(pc + i.length + offset)
    autoinc(i, fmap)


def i_Jcc(i, fmap):
    fmap[pc] = fmap[pc] + i.length
    offset = i.operands[0] * 2
    cond = fmap(COND[i.cond][1])
    fmap[pc] = tst(cond, fmap(pc + offset), fmap(pc))
    autoinc(i, fmap)
