# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *

# utilities:
# ----------

from .utils import *
from amoco.cas.utils import *
from amoco.arch.core import InstructionError
from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

# ------------------------------------------------------------------------------
# low level functions :


def __check_state(i, fmap):
    address = fmap(pc_)
    _s = internals["isetstate"]
    if address.bit(0) == 1:
        internals["isetstate"] = 1
        fmap[pc_] = fmap(pc_ ^ 1)
    elif address.bit(0) == 0:
        internals["isetstate"] = 0
    else:
        logger.verbose("impossible to check isetstate (ARM/Thumb) until pc is cst")
        return
    if _s != internals["isetstate"]:
        logger.info(
            "switch to %s instructions"
            % ({0: "ARM", 1: "Thumb",}[internals["isetstate"]])
        )


def __mem(a, sz):
    endian = 1
    if internals["endianstate"] == 1:
        endian = -1
    return mem(a, sz, endian=endian)


def __pre(i, fmap, _ld=False):
    if internals["isetstate"] == 1:
        fmap[pc] = fmap((pc_ + 4))
        if _ld:
            fmap[pc] = fmap(pc & 0xFFFFFFFC)
    else:
        fmap[pc] = fmap(pc_ + 8)
    fmap[pc_] = fmap(pc_ + i.length)
    cond = fmap(CONDITION[i.cond][1])
    if len(i.operands) == 0:
        return cond
    return (cond,) + tuple(i.operands)


def __setflags(fmap, cond, cout, result, overflow=None):
    if cout is None:
        cout = fmap(C)
    fmap[C] = stst(cond, cout, fmap(C))
    fmap[Z] = stst(cond, (result == 0), fmap(Z))
    sz = result.size
    sb = result[sz - 1 : sz]
    fmap[N] = stst(cond, (sb), fmap(N))
    if overflow is not None:
        fmap[V] = stst(cond, overflow, fmap(V))


# i_xxx is the translation of UAL (ARM/Thumb) instruction xxx.
# ------------------------------------------------------------------------------

# Branch instructions (A4.3, pA4-7)
def i_B(i, fmap):
    cond, pcoff = __pre(i, fmap)
    fmap[pc_] = stst(cond, fmap(pc + pcoff), fmap(pc_))
    # __check_state(i,fmap)


def i_CBNZ(i, fmap):
    cond, src, pcoff = __pre(i, fmap)
    fmap[pc_] = fmap(stst(src != 0, pc + pcoff, pc_))
    # __check_state(i,fmap)


def i_CBZ(i, fmap):
    cond, src, pcoff = __pre(i, fmap)
    fmap[pc_] = fmap(stst(src == 0, pc + pcoff, pc_))
    # __check_state(i,fmap)


def i_BL(i, fmap):
    fmap[lr] = fmap(pc_ + i.length)
    cond, pcoff = __pre(i, fmap)
    fmap[pc_] = stst(cond, fmap(pc + pcoff), fmap(pc_))
    # __check_state(i,fmap)


def i_BLX(i, fmap):
    cond, target = __pre(i, fmap)
    off = 4 if internals["isetstate"] == 0 else 2
    fmap[lr] = stst(cond, fmap(pc - off), fmap(lr))
    if target._is_cst:
        target = pc + target
    fmap[pc_] = stst(cond, fmap(target), fmap(pc_))
    __check_state(i, fmap)


def i_BX(i, fmap):
    cond, target = __pre(i, fmap)
    fmap[pc_] = stst(cond, fmap(target), fmap(pc_))
    __check_state(i, fmap)


def i_BXJ(i, fmap):
    fmap[lr] = fmap(pc_ + i.length)
    cond, src = __pre(i, fmap)
    fmap[pc_] = stst(cond, fmap(src), fmap(pc_))
    internals["isetstate"] = 2
    logger.error("switch to Jazelle instructions (unsupported)")


# Data processing instructions (A4.4)

# standard (4.4.1):
def i_ADC(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result, cout, overflow = AddWithCarry(fmap(op1), fmap(op2), fmap(C))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result, overflow)


def i_ADD(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result, cout, overflow = AddWithCarry(fmap(op1), fmap(op2))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result, overflow)


def i_ADR(i, fmap):
    cond, dest, offset = __pre(i, fmap)
    if i.add:
        result = fmap(pc & 0xFFFFFFFC) + offset
    else:
        result = fmap(pc & 0xFFFFFFFC) - offset
    cond = fmap(CONDITION[i.cond][1])
    fmap[dest] = stst(cond, result, fmap(i.d))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)


def i_AND(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result = fmap(op1 & op2)
    cout = fmap(op2.bit(31))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result)


def i_BIC(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result = fmap(op1 & (~op2))
    cout = fmap(op2.bit(31))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result)


def i_CMN(i, fmap):
    cond, dest, op1 = __pre(i, fmap)
    if i.stype != None:
        shifted = Shift_C(fmap(op1), i.stype, i.shift, fmap(C))
    else:
        shifted = fmap(op1)
    result, cout, overflow = AddWithCarry(fmap(dest), shifted, bit0)
    __setflags(fmap, cond, cout, result, overflow)


def i_CMP(i, fmap):
    cond, dest, op1 = __pre(i, fmap)
    if i.stype != None:
        shifted = Shift_C(fmap(op1), i.stype, i.shift, fmap(C))
    else:
        shifted = fmap(op1)
    result, cout, overflow = AddWithCarry(fmap(dest), ~shifted, bit1)
    __setflags(fmap, cond, cout, result, overflow)


def i_EOR(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result = fmap(op1 ^ op2)
    cout = fmap(op2.bit(31))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result)


def i_MOV(i, fmap):
    cond, dest, op1 = __pre(i, fmap)
    result = fmap(op1)
    cout = fmap(op1.bit(31))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result)


def i_MOVT(i, fmap):
    cond, dest, op1 = __pre(i, fmap)
    result = fmap(op1)
    cout = fmap(op1.bit(31))
    fmap[dest[16:32]] = stst(cond, result, fmap(dest[16:32]))


def i_MOVW(i, fmap):
    cond, dest, op1 = __pre(i, fmap)
    result = fmap(op1)
    cout = fmap(op1.bit(31))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result)


def i_MVN(i, fmap):
    cond, dest, op1 = __pre(i, fmap)
    result = fmap(~op1)
    cout = fmap(op1.bit(31))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result)


def i_ORN(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result = fmap(op1 | ~op2)
    cout = fmap(op2.bit(31))
    fmap[dest] = stst(cond, result, fmap(dest)).simplify()
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result)


def i_ORR(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result = fmap(op1 | op2)
    cout = fmap(op2.bit(31))
    fmap[dest] = stst(cond, result, fmap(dest)).simplify()
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result)


def i_RSB(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result, cout, overflow = AddWithCarry(fmap(~op1), fmap(op2), bit1)
    fmap[dest] = stst(cond, result, fmap(dest)).simplify()
    if i.setflags:
        __setflags(fmap, cond, cout, result, overflow)


def i_RSC(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result, cout, overflow = AddWithCarry(fmap(~op1), fmap(op2), fmap(C))
    fmap[dest] = stst(cond, result, fmap(dest)).simplify()
    if i.setflags:
        __setflags(fmap, cond, cout, result, overflow)


def i_SBC(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result, cout, overflow = AddWithCarry(fmap(op1), fmap(~op2), fmap(C))
    fmap[dest] = stst(cond, result, fmap(dest)).simplify()
    if i.setflags:
        __setflags(fmap, cond, cout, result, overflow)


def i_SUB(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result, cout, overflow = AddWithCarry(fmap(op1), fmap(~op2), bit1)
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result, overflow)


def i_TEQ(i, fmap):
    cond, dest, op1 = __pre(i, fmap)
    result = fmap(dest ^ op1)
    cout = fmap(op1.bit(31))
    __setflags(fmap, cond, cout, result)


def i_TST(i, fmap):
    cond, dest, op1 = __pre(i, fmap)
    result = fmap(dest & op1)
    cout = fmap(op1.bit(31))
    __setflags(fmap, cond, cout, result)


# shifts (4.4.2)
def i_ASR(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    shift = fmap(op2)
    if shift._is_cst:
        result, cout = ASR_C(fmap(op1), shift.value)
    else:
        result, cout = fmap(op1 >> op2), top(1)
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result)


def i_LSL(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    shift = fmap(op2)
    if shift._is_cst:
        result, cout = LSL_C(fmap(op1), shift.value)
    else:
        result, cout = fmap(op1 << op2), top(1)
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result)


def i_LSR(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    shift = fmap(op2)
    if shift._is_cst:
        result, cout = LSR_C(fmap(op1), shift.value)
    else:
        result, cout = fmap(op1 >> op2), top(1)
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    elif i.setflags:
        __setflags(fmap, cond, cout, result)


def i_ROR(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    shift = fmap(op2)
    if shift._is_cst:
        result, cout = ROR_C(fmap(op1), shift.value)
    else:
        result, cout = ror(op1, op2), top(1)
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    if i.setflags:
        __setflags(fmap, cond, cout, result)


def i_RRX(i, fmap):
    cond, dest, op1 = __pre(i, fmap)
    result, cout = RRX_C(fmap(op1), fmap(C))
    fmap[dest] = stst(cond, result, fmap(dest))
    if i.setflags:
        __setflags(fmap, cond, cout, result)


# multiply (4.4.3)
# general:
def i_MLA(i, fmap):
    cond, dest, op1, op2, addend = __pre(i, fmap)
    result = fmap((op1 * op2) + addend)
    fmap[dest] = stst(cond, result, fmap(dest))
    if i.setflags:
        fmap[Z] = stst(cond, (result == 0), fmap(Z))
        fmap[N] = stst(cond, (result < 0), fmap(N))


def i_MLS(i, fmap):
    cond, dest, op1, op2, addend = __pre(i, fmap)
    result = fmap(addend - (op1 * op2))
    fmap[dest] = stst(cond, result, fmap(dest))


def i_MUL(i, fmap):
    cond, dest, op1, op2 = __pre(i, fmap)
    result = fmap(op1 * op2)
    fmap[dest] = stst(cond, result, fmap(dest))


# signed:
# SMLABB, SMLABT, SMLATB, SMLATT
def i_SMLABB(i, fmap):
    cond, dest, Rn, Rm, Ra = __pre(i, fmap)
    op1 = Rn[0:16]
    op2 = Rm[0:16]
    result = fmap((op1 ** op2) + Ra)
    fmap[dest] = stst(cond, result, fmap(dest))
    overflow = top(1)
    fmap[V] = stst(cond, overflow, fmap(V))


def i_SMLABT(i, fmap):
    cond, dest, Rn, Rm, Ra = __pre(i, fmap)
    op1 = Rn[0:16]
    op2 = Rm[16:32]
    result = fmap((op1 ** op2) + Ra)
    fmap[dest] = stst(cond, result, fmap(dest))
    overflow = top(1)
    fmap[V] = stst(cond, overflow, fmap(V))


def i_SMLATT(i, fmap):
    cond, dest, Rn, Rm, Ra = __pre(i, fmap)
    op1 = Rn[16:32]
    op2 = Rm[16:32]
    result = fmap((op1 ** op2) + Ra)
    fmap[dest] = stst(cond, result, fmap(dest))
    overflow = top(1)
    fmap[V] = stst(cond, overflow, fmap(V))


def i_SMLATB(i, fmap):
    cond, dest, Rn, Rm, Ra = __pre(i, fmap)
    op1 = Rn[16:32]
    op2 = Rm[0:16]
    result = fmap((op1 ** op2) + Ra)
    fmap[dest] = stst(cond, result, fmap(dest))
    overflow = top(1)
    fmap[V] = stst(cond, overflow, fmap(V))


def i_SMLAD(i, fmap):
    cond, dest, Rn, Rm, Ra = __pre(i, fmap)
    p1 = Rn[0:16] ** Rm[0:16]
    p2 = Rn[16:32] ** Rm[16:32]
    result = fmap(p1 + p2 + Ra)
    fmap[dest] = stst(cond, result, fmap(dest))
    overflow = top(1)
    fmap[V] = stst(cond, overflow, fmap(V))


def i_SMLADX(i, fmap):
    cond, dest, Rn, Rm, Ra = __pre(i, fmap)
    p1 = Rn[0:16] ** Rm[16:32]
    p2 = Rn[16:32] ** Rm[0:16]
    result = fmap(p1 + p2 + Ra)
    fmap[dest] = stst(cond, result, fmap(dest))
    overflow = top(1)
    fmap[V] = stst(cond, overflow, fmap(V))


def i_SMLAL(i, fmap):
    cond, RdLo, RdHi, Rn, Rm = __pre(i, fmap)
    result = fmap(Rn ** Rm + composer([RdLo, RdHi]))
    fmap[RdLo] = stst(cond, result[0:32], fmap(RdLo))
    fmap[RdHi] = stst(cond, result[32:64], fmap(RdHi))
    if i.setflags:
        fmap[Z] = stst(cond, (result == 0), fmap(Z))
        fmap[N] = stst(cond, result.bit(63), fmap(N))


def i_SMLALBB(i, fmap):
    cond, RdLo, RdHi, Rn, Rm = __pre(i, fmap)
    op1 = Rn[0:16]
    op2 = Rm[0:16]
    result = fmap((op1 ** op2).signextend(64) + composer([RdLo, RdHi]))
    fmap[RdLo] = stst(cond, result[0:32], fmap(RdLo))
    fmap[RdHi] = stst(cond, result[32:64], fmap(RdHi))


def i_SMLALBT(i, fmap):
    cond, RdLo, RdHi, Rn, Rm = __pre(i, fmap)
    op1 = Rn[0:16]
    op2 = Rm[16:32]
    result = fmap((op1 ** op2).signextend(64) + composer([RdLo, RdHi]))
    fmap[RdLo] = stst(cond, result[0:32], fmap(RdLo))
    fmap[RdHi] = stst(cond, result[32:64], fmap(RdHi))


def i_SMLALTT(i, fmap):
    cond, RdLo, RdHi, Rn, Rm = __pre(i, fmap)
    op1 = Rn[16:32]
    op2 = Rm[16:32]
    result = fmap((op1 ** op2).signextend(64) + composer([RdLo, RdHi]))
    fmap[RdLo] = stst(cond, result[0:32], fmap(RdLo))
    fmap[RdHi] = stst(cond, result[32:64], fmap(RdHi))


def i_SMLALTB(i, fmap):
    cond, RdLo, RdHi, Rn, Rm = __pre(i, fmap)
    op1 = Rn[16:32]
    op2 = Rm[0:16]
    result = fmap((op1 ** op2).signextend(64) + composer([RdLo, RdHi]))
    fmap[RdLo] = stst(cond, result[0:32], fmap(RdLo))
    fmap[RdHi] = stst(cond, result[32:64], fmap(RdHi))


# SMLALD
# SMLAWB, SMLAWT
# SMLSD
# SMLSLD
# SMMLA
# SMMLS
# SMMUL
# SMUAD
# SMULB, SMULBT, SMULTB, SMULTT
# SMULL
# SMULWB, SMULWT
# SMUSD

# saturation (4.4.4)
# SSAT
# SSAT16
# USAT
# USAT16

# packing/unpacking (4.4.5)
# PKH
# SXTAB
# SXTAB16
# SXTAH
# SXTB
# SXTB16
# SXTH
# UXTAB
# UXTAB16
# UXTAH
# UXTB
# UXTB16
# UXTH

# miscellaneous (4.4.6)
def i_BFC(i, fmap):
    cond, dest, lsb, size = __pre(i, fmap)
    src = fmap(dest)
    result = composer([src[0:lsb], cst(0, size), src[lsb + size : src.size]])
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        raise InstructionError(i)


def i_BFI(i, fmap):
    cond, dest, src, lsb, size = __pre(i, fmap)
    src = fmap(src)
    result = composer([dest[0:lsb], src[lsb, lsb + size], dest[lsb + size : dest.size]])
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        raise InstructionError(i)


def i_CLZ(i, fmap):
    cond, dest, src = __pre(i, fmap)
    result = fmap(src)
    if result._is_cst:
        result = [(result.value >> i) & 1 for i in range(result.size)]
        result = cst(result.find(1), dest.size)
    else:
        result = top(dest.size)
    fmap[dest] = stst(cond, result, fmap(dest))


# RBIT
# REV
# REV16
# REVSH
# SBFX
# SEL
# UBFX
# USAD8
# USADA8

# parallel addition/substraction (4.4.7)
# ADD16
# ASX
# SAX
# SUB16
# ADD8
# SUB8


# divide (4.4.8)
# SDIV
# UDIV

# apsr access (A4.5)
# CPS
# MRS
# MSR

# load/store (A4.6)
def i_LDR(i, fmap):
    cond, dest, src, sht = __pre(i, fmap, True)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.index else src
    result = fmap(__mem(adr, 32))
    if i.wback:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)


def i_LDREX(i, fmap):
    cond, dest, src, imm = __pre(i, fmap)
    off_addr = src + imm
    adr = off_addr
    result = fmap(__mem(adr, 32))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    # exclusive monitor not supported


def i_LDRB(i, fmap):
    cond, dest, src, sht = __pre(i, fmap, True)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.index else src
    result = fmap(mem(adr, 8)).zeroextend(32)
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    if i.wback:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))


def i_LDREXB(i, fmap):
    cond, dest, src, imm = __pre(i, fmap)
    off_addr = src + imm
    adr = off_addr
    result = fmap(mem(adr, 8)).zeroextend(32)
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    # exclusive monitor not supported


def i_LDRH(i, fmap):
    cond, dest, src, sht = __pre(i, fmap, True)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.index else src
    result = fmap(__mem(adr, 16)).zeroextend(32)
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    if i.wback:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))


def i_LDREXH(i, fmap):
    cond, dest, src, imm = __pre(i, fmap)
    off_addr = src + imm
    adr = off_addr
    result = fmap(__mem(adr, 16)).zeroextend(32)
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    # exclusive monitor not supported


def i_LDRSB(i, fmap):
    cond, dest, src, sht = __pre(i, fmap, True)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.index else src
    result = fmap(mem(adr, 8)).signextend(32)
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    if i.wback:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))


def i_LDRSH(i, fmap):
    cond, dest, src, sht = __pre(i, fmap, True)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.index else src
    result = fmap(__mem(adr, 16)).signextend(32)
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)
    if i.wback:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))


def i_LDRD(i, fmap):
    cond, dst1, dst2, src, sht = __pre(i, fmap, True)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.index else src
    res1 = fmap(__mem(adr, 32))
    res2 = fmap(__mem(adr + 4, 32))
    fmap[dst1] = stst(cond, res1, fmap(dst1))
    fmap[dst2] = stst(cond, res2, fmap(dst2))
    if i.wback:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))


def i_LDRT(i, fmap):
    cond, dest, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.postindex else src
    result = fmap(__mem(adr, 32))
    if i.postindex:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)


def i_LDRBT(i, fmap):
    cond, dest, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.postindex else src
    result = fmap(mem(adr, 8)).zeroextend(32)
    if i.postindex:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)


def i_LDRHT(i, fmap):
    cond, dest, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.postindex else src
    result = fmap(__mem(adr, 16)).zeroextend(32)
    if i.postindex:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)


def i_LDRSBT(i, fmap):
    cond, dest, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.postindex else src
    result = fmap(mem(adr, 8)).signextend(32)
    if i.postindex:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)


def i_LDRSHT(i, fmap):
    cond, dest, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.postindex else src
    result = fmap(__mem(adr, 16)).signextend(32)
    if i.postindex:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))
    fmap[dest] = stst(cond, result, fmap(dest))
    if dest == pc:
        fmap[pc_] = fmap(pc)
        __check_state(i, fmap)


def i_STR(i, fmap):
    cond, dest, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.index else src
    result = fmap(dest)
    if i.wback:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))
    fmap[__mem(adr, 32)] = stst(cond, result, fmap(__mem(adr, 32)))


def i_STREX(i, fmap):
    cond, dest, src, imm = __pre(i, fmap)
    off_addr = src + imm
    adr = off_addr
    result = fmap(dest)
    fmap[__mem(adr, 32)] = stst(cond, result, fmap(__mem(adr, 32)))
    # exclusive monitor not supported


def i_STRB(i, fmap):
    cond, dest, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.index else src
    result = fmap(dest[0:8])
    fmap[mem(adr, 8)] = stst(cond, result, mem(adr, 8))
    if i.wback:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))


def i_STREXB(i, fmap):
    cond, dest, src, imm = __pre(i, fmap)
    off_addr = src + imm
    adr = off_addr
    result = fmap(dest[0:8])
    fmap[mem(adr, 8)] = stst(cond, result, fmap(mem(adr, 8)))
    # exclusive monitor not supported


def i_STRH(i, fmap):
    cond, dest, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.index else src
    result = fmap(dest[0:16])
    fmap[__mem(adr, 16)] = stst(cond, result, fmap(__mem(adr, 16)))
    if i.wback:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))


def i_STREXH(i, fmap):
    cond, dest, src, imm = __pre(i, fmap)
    off_addr = src + imm
    adr = off_addr
    result = fmap(dest[0:16])
    fmap[__mem(adr, 16)] = stst(cond, result, fmap(__mem(adr, 16)))
    # exclusive monitor not supported


def i_STRD(i, fmap):
    cond, dst1, dst2, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.index else src
    adr1 = __mem(adr, 32)
    adr2 = __mem(adr + 4, 32)
    res1 = fmap(dst1)
    res2 = fmap(dst2)
    fmap[adr1] = stst(cond, res1, fmap(adr1))
    fmap[adr2] = stst(cond, res2, fmap(adr2))
    if i.wback:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))


def i_STRT(i, fmap):
    cond, dest, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.postindex else src
    adr1 = __mem(adr, 32)
    result = fmap(dest)
    if i.postindex:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))
    fmap[adr1] = stst(cond, result, fmap(adr1))


def i_STRBT(i, fmap):
    cond, dest, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.postindex else src
    adr1 = mem(adr, 8)
    result = fmap(dest[0:8])
    if i.postindex:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))
    fmap[adr1] = stst(cond, result, fmap(adr1))


def i_STRHT(i, fmap):
    cond, dest, src, sht = __pre(i, fmap)
    off_addr = (src + sht) if i.add else (src - sht)
    adr = off_addr if i.postindex else src
    adr1 = __mem(adr, 16)
    result = fmap(dest[0:16])
    if i.postindex:
        fmap[src] = stst(cond, fmap(off_addr), fmap(src))
    fmap[adr1] = stst(cond, result, fmap(adr1))


# load/store multiple (A4.7)


def i_LDM(i, fmap):
    cond, src, dests = __pre(i, fmap)
    _adr = __mem(src, 32)
    for _r in dests:
        fmap[_r] = stst(cond, fmap(_adr), fmap(_r))
        _adr.a.disp += 4
    if i.wback:
        fmap[src] = stst(cond, fmap(src + 4 * len(dests)), fmap(src))


def i_LDMDB(i, fmap):
    cond, src, dests = __pre(i, fmap)
    _adr = __mem(src, 32)
    _adr.a.disp -= 4 * len(dests)
    for _r in dests:
        fmap[_r] = stst(cond, fmap(_adr), fmap(_r))
        _adr.a.disp += 4
    if i.wback:
        fmap[src] = stst(cond, fmap(src - 4 * len(dests)), fmap(src))


def i_STM(i, fmap):
    cond, dest, srcs = __pre(i, fmap)
    _adr = __mem(dest, 32)
    for _r in srcs:
        fmap[_adr] = stst(cond, fmap(_r), fmap(_adr))
        _adr.a.disp += 4
    if i.wback:
        fmap[dest] = stst(cond, fmap(dest + 4 * len(srcs)), fmap(dest))


def i_STMDB(i, fmap):
    cond, dest, srcs = __pre(i, fmap)
    _adr = __mem(dest, 32)
    _adr.a.disp -= 4 * len(srcs)
    for _r in srcs:
        fmap[_adr] = stst(cond, fmap(_r), fmap(_adr))
        _adr.a.disp += 4
    if i.wback:
        fmap[dest] = stst(cond, fmap(dest - 4 * len(srcs)), fmap(dest))


def i_POP(i, fmap):
    cond, regs = __pre(i, fmap)
    adr = sp
    for _r in regs:
        fmap[_r] = fmap(stst(cond, __mem(adr, 32), _r))
        adr = adr + 4
    fmap[sp] = stst(cond, fmap(sp + (4 * len(regs))), sp)


def i_PUSH(i, fmap):
    cond, regs = __pre(i, fmap)
    adr = sp - (4 * len(regs))
    for _r in regs:
        fmap[__mem(adr, 32)] = fmap(stst(cond, _r, __mem(adr, 32)))
        adr = adr + 4
    fmap[sp] = stst(cond, fmap(sp - (4 * len(regs))), sp)


# STM, STMIA, STMEA
# STMDA, STMED
# STMDB, STMFD
# STMIB, STMFA

# miscellaneous (A4.8)


def i_CLREX(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)
    # exclusive monitor not supported


def i_DBG(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)
    # debug hint


def i_DMB(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)


def i_DSB(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)


def i_ISB(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)


def i_IT(i, fmap):
    assert internals["isetstate"] == 1
    fmap[pc_] = fmap(pc_ + i.length)
    internals["itstate"] = 1


def i_NOP(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)


def i_WFE(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)


def i_WFI(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)


def i_YIELD(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)


# pre-load data hint
def i_PLD(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)


# pre-load data wide hint
def i_PLDW(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)


# pre-load instruction hint
def i_PLI(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)


# change endianess
def i_SETEND(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)
    internals["endianstate"] = -1 if i.set_bigend else 1


# event hint
def i_SEV(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)


# supervisor call
def i_SVC(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)
    logger.info("call to supervisor is unsupported")


def i_SWP(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)
    Rt, Rt2, Rn = i.operands
    data = fmap(__mem(Rn, 32))
    fmap[__mem(Rn, 32)] = fmap(Rt2)
    fmap[Rt] = data


def i_SWPB(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)
    Rt, Rt2, Rn = i.operands
    data = fmap(mem(Rn, 8))
    fmap[mem(Rn, 8)] = fmap(Rt2)[0:8]
    fmap[Rt] = data.zeroextend(32)


def i_ENTERX(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)
    internals["isetstate"] = 3


def i_LEAVEX(i, fmap):
    fmap[pc_] = fmap(pc_ + i.length)
    internals["isetstate"] = 1


def i_SMC(i, fmap):
    raise InstructionError(i)


# coprocessor (A4.9)
# MCR, MCR2
# MCRR, MCRR2
# MRC, MRC2
# MRRC, MRRC2
# LDC, LDC2
# STC, STC2

# SIMD and VFP (A4.10)
# NOT IMPLEMENTED
