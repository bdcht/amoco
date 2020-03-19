# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2013 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.arch.arm.v8 import env64 as env

from amoco.arch.core import *
from .utils import *


def DecodeBitMasks(M, targs):
    def Ones(n):
        return Bits([1] * n).int()

    immN, imms, immr, immediate = targs
    _z = Bits(~imms, 6) // Bits(immN, 1)
    len = str(_z).rindex("1")  # highest set bit
    if len < 1 or M < (1 << len):
        raise InstructionError("bitmasks error")
    levels = cst(-1, len).zeroextend(6)
    if immediate and (imms & levels.v) == levels.v:
        raise InstructionError("bitmasks error")
    S = imms & levels.v
    R = immr & levels.v
    diff = S - R
    esize = 1 << len
    if M % esize != 0:
        raise InstructionError("bitmasks error")
    d = diff % esize
    welem = cst(Ones(S + 1), esize)
    telem = cst(Ones(d + 1), esize)
    wmask = composer([ROR(welem, R)] * (M / esize))
    tmask = composer([telem] * (M / esize))
    return (wmask, tmask)


def ExtendReg(r, etype, shift=0):
    assert shift >= 0 and shift <= 4
    N = r.size
    signed = True if etype & 4 == 0 else False
    l = 8 << (etype & 3)
    l = min(l, N - shift)
    return r[0:l].extend(signed, N) << shift


def System_Reg(*args):
    # TODO: decode args into system register name (see §D.8).
    return reg("sysreg{%s}" % (" ".join(["{:b}".format(x) for x in args])), 64)


def sp2z(x):
    if x is env.sp:
        return env.xzr
    if x is env.wsp:
        return env.wzr
    return x


# ------------------------------------------------------
# amoco ARMv8-A instruction specs:
# ------------------------------------------------------

ISPECS = []


@ispec("32[ sf 0 S 11010000 Rm(5) 000000 Rn(5) Rd(5) ]", mnemonic="ADC")
@ispec("32[ sf 1 S 11010000 Rm(5) 000000 Rn(5) Rd(5) ]", mnemonic="SBC")
def A64_generic(obj, sf, S, Rm, Rn, Rd):
    obj.datasize = 64 if (sf == 1) else 32
    obj.setflags = S == 1
    regs = env.Xregs if sf == 1 else env.Wregs
    obj.m = sp2z(regs[Rm])
    obj.n = sp2z(regs[Rn])
    obj.d = sp2z(regs[Rd])
    obj.operands = [obj.d, obj.n, obj.m]
    obj.type = type_data_processing


@ispec("32[ sf 0 S 01011001 Rm(5) option(3) imm3(3) Rn(5) Rd(5) ]", mnemonic="ADD")
@ispec("32[ sf 1 S 01011001 Rm(5) option(3) imm3(3) Rn(5) Rd(5) ]", mnemonic="SUB")
def A64_generic(obj, sf, S, Rm, option, imm3, Rn, Rd):
    obj.datasize = 64 if (sf == 1) else 32
    obj.setflags = S == 1
    regs = env.Xregs if sf == 1 else env.Wregs
    obj.extend_type = option
    obj.shift = imm3
    obj.m = ExtendReg(sp2z(regs[Rm]), option, imm3)
    obj.n = regs[Rn]
    obj.d = regs[Rd] if S == 0 else sp2z(regs[Rd])
    obj.operands = [obj.d, obj.n, obj.m]
    obj.type = type_data_processing


@ispec("32[ sf 0 S 10001 shift(2) imm12(12) Rn(5) Rd(5) ]", mnemonic="ADD")
@ispec("32[ sf 1 S 10001 shift(2) imm12(12) Rn(5) Rd(5) ]", mnemonic="SUB")
def A64_generic(obj, sf, S, shift, imm12, Rn, Rd):
    obj.datasize = 64 if (sf == 1) else 32
    obj.setflags = S == 1
    regs = env.Xregs if sf == 1 else env.Wregs
    if shift == 0:
        imm = imm12
    elif shift == 1:
        imm = imm12 << 12
    else:
        raise InstructionError(obj)
    obj.imm = env.cst(imm, obj.datasize)
    obj.n = regs[Rn]
    obj.d = regs[Rd] if S == 0 else sp2z(regs[Rd])
    obj.operands = [obj.d, obj.n, obj.imm]
    obj.type = type_data_processing


@ispec("32[ sf 0 S 01011 shift(2) 0 Rm(5) imm6(6) Rn(5) Rd(5) ]", mnemonic="ADD")
@ispec("32[ sf 1 S 01011 shift(2) 0 Rm(5) imm6(6) Rn(5) Rd(5) ]", mnemonic="SUB")
def A64_generic(obj, sf, S, shift, Rm, imm6, Rn, Rd):
    obj.datasize = 64 if (sf == 1) else 32
    obj.setflags = S == 1
    regs = env.Xregs if sf == 1 else env.Wregs
    if shift == 3:
        raise InstructionError(obj)
    if sf == 0 and imm6 > 31:
        raise InstructionError(obj)
    shift_type = {0: "<<", 1: ">>", 2: "//", 3: ">>>"}[shift]
    obj.m = env.oper(shift_type, sp2z(regs[Rm]), cst(imm6))
    obj.n = sp2z(regs[Rn])
    obj.d = sp2z(regs[Rd])
    obj.operands = [obj.d, obj.n, obj.m]
    obj.type = type_data_processing


@ispec("32[ p immlo(2) 10000 immhi(19) Rd(5) ]", mnemonic="ADR")
def A64_adr(obj, p, immlo, immhi, Rd):
    obj.page = p == 1
    if obj.page == 1:
        obj.mnemonic += "P"
        obj.imm = env.cst((immhi << 14) + (immlo << 12), 64)
    else:
        obj.imm = env.cst((immhi << 2) + immlo, 64)
    obj.d = sp2z(env.Xregs[Rd])
    obj.operands = [obj.d, obj.imm]
    obj.type = type_data_processing


@ispec(
    "32[ sf 00 100100 N immr(6) imms(6) Rn(5) Rd(5) ]", mnemonic="AND", setflags=False
)
@ispec(
    "32[ sf 01 100100 N immr(6) imms(6) Rn(5) Rd(5) ]", mnemonic="ORR", setflags=False
)
@ispec(
    "32[ sf 10 100100 N immr(6) imms(6) Rn(5) Rd(5) ]", mnemonic="EOR", setflags=False
)
@ispec(
    "32[ sf 11 100100 N immr(6) imms(6) Rn(5) Rd(5) ]", mnemonic="AND", setflags=True
)
def A64_generic(obj, sf, N, immr, imms, Rn, Rd):
    obj.datasize = 64 if (sf == 1) else 32
    regs = env.Xregs if sf == 1 else env.Wregs
    if sf == 0 and N != 0:
        raise InstructionError(obj)
    obj.d = regs[Rd] if not obj.setflags else sp2z(regs[Rd])
    obj.n = sp2z(regs[Rn])
    obj.imm, _ = DecodeBitMasks(obj.datasize, (N, imms, immr, True))
    obj.operands = [obj.d, obj.n, obj.imm]
    obj.type = type_data_processing


@ispec(
    "32[ sf 01 100110 N immr(6) imms(6) Rn(5) Rd(5) ]",
    mnemonic="BFM",
    inzero=False,
    extend=False,
)
@ispec(
    "32[ sf 00 100110 N immr(6) imms(6) Rn(5) Rd(5) ]",
    mnemonic="SBFM",
    inzero=True,
    extend=True,
)
@ispec(
    "32[ sf 10 100110 N immr(6) imms(6) Rn(5) Rd(5) ]",
    mnemonic="UBFM",
    inzero=True,
    extend=False,
)
def A64_xBFM(obj, sf, N, immr, imms, Rn, Rd):
    obj.datasize = 64 if (sf == 1) else 32
    regs = env.Xregs if sf == 1 else env.Wregs
    if sf == 1 and N != 1:
        raise InstructionError(obj)
    if sf == 0 and (N != 0 or immr < 32 or imms < 32):
        raise InstructionError(obj)
    obj.d = sp2z(regs[Rd])
    obj.n = sp2z(regs[Rn])
    obj.immr = cst(immr, 6)
    obj.imms = cst(imms, 6)
    obj.wmask, obj.tmask = DecodeBitMasks(obj.datasize, (N, imms, immr, False))
    obj.operands = [obj.d, obj.n, obj.immr, obj.imms]
    obj.type = type_data_processing


@ispec(
    "32[ sf 00 01010 shift(2) 0 Rm(5) imm6(6) Rn(5) Rd(5) ]",
    mnemonic="AND",
    setflags=False,
    invert=False,
)
@ispec(
    "32[ sf 01 01010 shift(2) 0 Rm(5) imm6(6) Rn(5) Rd(5) ]",
    mnemonic="ORR",
    setflags=False,
    invert=False,
)
@ispec(
    "32[ sf 10 01010 shift(2) 0 Rm(5) imm6(6) Rn(5) Rd(5) ]",
    mnemonic="EOR",
    setflags=False,
    invert=False,
)
@ispec(
    "32[ sf 11 01010 shift(2) 0 Rm(5) imm6(6) Rn(5) Rd(5) ]",
    mnemonic="AND",
    setflags=True,
    invert=False,
)
@ispec(
    "32[ sf 00 01010 shift(2) 1 Rm(5) imm6(6) Rn(5) Rd(5) ]",
    mnemonic="BIC",
    setflags=False,
    invert=True,
)
@ispec(
    "32[ sf 01 01010 shift(2) 1 Rm(5) imm6(6) Rn(5) Rd(5) ]",
    mnemonic="ORN",
    setflags=False,
    invert=True,
)
@ispec(
    "32[ sf 10 01010 shift(2) 1 Rm(5) imm6(6) Rn(5) Rd(5) ]",
    mnemonic="EON",
    setflags=False,
    invert=True,
)
@ispec(
    "32[ sf 11 01010 shift(2) 1 Rm(5) imm6(6) Rn(5) Rd(5) ]",
    mnemonic="BIC",
    setflags=True,
    invert=True,
)
def A64_generic(obj, sf, shift, Rm, imm6, Rn, Rd):
    obj.datasize = 64 if (sf == 1) else 32
    regs = env.Xregs if sf == 1 else env.Wregs
    obj.d = sp2z(regs[Rd])
    obj.n = sp2z(regs[Rn])
    if sf == 0 and imm6 > 31:
        raise InstructionError(obj)
    shift_type = {0: "<<", 1: ">>", 2: "//", 3: ">>>"}[shift]
    obj.m = env.oper(shift_type, sp2z(regs[Rm]), cst(imm6))
    obj.operands = [obj.d, obj.n, obj.m]
    obj.type = type_data_processing


@ispec("32[ sf 0 0 11010110 Rm(5) 0010 10 Rn(5) Rd(5) ]", mnemonic="ASRV")
@ispec("32[ sf 0 0 11010110 Rm(5) 0010 00 Rn(5) Rd(5) ]", mnemonic="LSLV")
@ispec("32[ sf 0 0 11010110 Rm(5) 0010 01 Rn(5) Rd(5) ]", mnemonic="LSRV")
@ispec("32[ sf 0 0 11010110 Rm(5) 0010 11 Rn(5) Rd(5) ]", mnemonic="RORV")
@ispec("32[ sf 0 0 11010110 Rm(5) 0000 11 Rn(5) Rd(5) ]", mnemonic="SDIV")
@ispec("32[ sf 0 0 11010110 Rm(5) 0000 10 Rn(5) Rd(5) ]", mnemonic="UDIV")
def A64_generic(obj, sf, Rm, Rn, Rd):
    obj.datasize = 64 if (sf == 1) else 32
    regs = env.Xregs if sf == 1 else env.Wregs
    obj.d = sp2z(regs[Rd])
    obj.n = sp2z(regs[Rn])
    obj.m = sp2z(regs[Rm])
    obj.operands = [obj.d, obj.n, obj.m]
    obj.type = type_data_processing


@ispec("32[ 1101010100 0 01 op1(3) CRn(4) CRm(4) op2(3) Rt(5) ]", mnemonic="SYS")
@ispec("32[ 1101010100 1 01 op1(3) CRn(4) CRm(4) op2(3) Rt(5) ]", mnemonic="SYSL")
def A64_sys(obj, op1, CRn, CRm, op2, Rt):
    obj.sys_op0 = 1
    obj.sys_op1 = op1
    obj.sys_op2 = op2
    obj.sys_crn = CRn
    obj.sys_crm = CRm
    obj.t = env.Xregs[Rt]
    obj.operands = [obj.sys_op1, obj.sys_crn, obj.sys_crm, obj.sys_op2, obj.t]
    obj.type = type_cpu_state


@ispec("32[ 1101010100 1 1 o0 op1(3) CRn(4) CRm(4) op2(3) Rt(5) ]", mnemonic="MRS")
def A64_mrs(obj, o0, op1, CRn, CRm, op2, Rt):
    obj.sys_op0 = 2 + o0
    obj.sys_op1 = op1
    obj.sys_op2 = op2
    obj.sys_crn = CRn
    obj.sys_crm = CRm
    obj.read = True
    obj.t = sp2z(env.Xregs[Rt])
    obj.systemreg = System_Reg(o0, op1, CRn, CRm, op2)
    obj.operands = [obj.t, obj.systemreg]
    obj.type = type_cpu_state


@ispec("32[ 1101010100 0 00 op1(3) 0100 CRm(4) op2(3) 11111 ]", mnemonic="MSR")
def A64_msr(obj, op1, CRm, op2):
    try:
        obj.pstatefield = {
            0b000101: env.SPSel,
            0b011110: env.DAIFSet,
            0b011111: env.DAIFClr,
        }[op1 << 3 + op2]
    except KeyError:
        raise InstructionError(obj)
    obj.imm = env.cst(CRm, 4)
    obj.operands = [obj.pstatefield, obj.imm]
    obj.type = type_cpu_state


@ispec("32[ 1101010100 0 1 o0 op1(3) CRn(4) CRm(4) op2(3) Rt(5) ]", mnemonic="MSR")
def A64_msr(obj, o0, op1, CRn, CRm, op2, Rt):
    obj.sys_op0 = 2 + o0
    obj.sys_op1 = op1
    obj.sys_op2 = op2
    obj.sys_crn = CRn
    obj.sys_crm = CRm
    obj.read = False
    obj.t = env.Xregs[Rt]
    obj.systemreg = System_Reg(o0, op1, CRn, CRm, obj.t)
    obj.operands = [obj.systemreg, obj.t]
    obj.type = type_cpu_state


@ispec("32[ 0101010 0 imm19(19) 0 cond(4) ]", mnemonic="Bcond")
def A64_Bcond(obj, imm19, cond):
    obj.offset = env.cst(imm19 << 2, 21).signextend(64)
    obj.misc["cond"] = env.CONDITION[cond][0]
    obj.cond = env.CONDITION[cond][1]
    obj.operands = [obj.offset]
    obj.type = type_control_flow


@ispec("32[ 0 00101 imm26(26) ]", mnemonic="B")
@ispec("32[ 1 00101 imm26(26) ]", mnemonic="BL")
def A64_B(obj, imm26):
    obj.offset = env.cst(imm26 << 2, 28).signextend(64)
    obj.operands = [obj.offset]
    obj.type = type_control_flow


@ispec("32[ 1101011 00 01 11111 000000 Rn(5) 00000 ]", mnemonic="BLR")
@ispec("32[ 1101011 00 00 11111 000000 Rn(5) 00000 ]", mnemonic="BR")
@ispec("32[ 1101011 00 10 11111 000000 Rn(5) 00000 ]", mnemonic="RET")
def A64_generic(obj, Rn):
    obj.n = sp2z(env.Xregs[Rn])
    obj.operands = [obj.n]
    obj.type = type_control_flow


@ispec("32[ 11010100 001 imm16(16) 000 00 ]", mnemonic="BRK")
@ispec("32[ 11010100 101 imm16(16) 000 01 ]", mnemonic="DCPS1")
@ispec("32[ 11010100 101 imm16(16) 000 10 ]", mnemonic="DCPS2")
@ispec("32[ 11010100 101 imm16(16) 000 11 ]", mnemonic="DCPS3")
@ispec("32[ 11010100 010 imm16(16) 000 00 ]", mnemonic="HLT")
@ispec("32[ 11010100 000 imm16(16) 000 10 ]", mnemonic="HVC")
@ispec("32[ 11010100 000 imm16(16) 000 11 ]", mnemonic="SMC")
@ispec("32[ 11010100 000 imm16(16) 000 01 ]", mnemonic="SVC")
def A64_generic(obj, imm16):
    obj.imm = env.cst(imm16, 16)
    obj.operands = [obj.imm]
    obj.type = type_cpu_state


@ispec("32[ sf 011010 1 imm19(19) Rt(5) ]", mnemonic="CBNZ")
@ispec("32[ sf 011010 0 imm19(19) Rt(5) ]", mnemonic="CBZ")
def A64_CBx(obj, sf, imm19, Rt):
    obj.datasize = 64 if (sf == 1) else 32
    regs = env.Xregs if sf == 1 else env.Wregs
    obj.t = sp2z(regs[Rt])
    obj.offset = env.cst(imm19 << 2, 21).signextend(64)
    obj.operands = [obj.t, obj.offset]
    obj.type = type_control_flow


@ispec("32[ sf 0 1 11010010 imm5(5) cond(4) 1 0 Rn(5) 0 nzcv(4) ]", mnemonic="CCMN")
@ispec("32[ sf 1 1 11010010 imm5(5) cond(4) 1 0 Rn(5) 0 nzcv(4) ]", mnemonic="CCMP")
def A64_CCMx(obj, sf, imm5, cond, Rn, nzcv):
    obj.datasize = 64 if (sf == 1) else 32
    regs = env.Xregs if sf == 1 else env.Wregs
    obj.n = sp2z(regs[Rn])
    obj.imm = env.cst(imm5, obj.datasize)
    obj.flags = env.cst(nzcv, 4)
    obj.misc["cond"] = env.CONDITION[cond][0]
    obj.cond = env.CONDITION[cond][1]
    obj.operands = [obj.n, obj.imm, obj.flags, obj.cond]
    obj.type = type_data_processing


@ispec("32[ sf 0 1 11010010 Rm(5) cond(4) 0 0 Rn(5) 0 nzcv(4) ]", mnemonic="CCMN")
@ispec("32[ sf 1 1 11010010 Rm(5) cond(4) 0 0 Rn(5) 0 nzcv(4) ]", mnemonic="CCMP")
def A64_CCMx_reg(obj, sf, Rm, cond, Rn, nzcv):
    obj.datasize = 64 if (sf == 1) else 32
    regs = env.Xregs if sf == 1 else env.Wregs
    obj.n = sp2z(regs[Rn])
    obj.m = sp2z(regs[Rm])
    obj.flags = env.cst(nzcv, 4)
    obj.misc["cond"] = env.CONDITION[cond][0]
    obj.cond = env.CONDITION[cond][1]
    obj.operands = [obj.n, obj.m, obj.flags, obj.cond]
    obj.type = type_data_processing


@ispec("32[ sf 0 0 11010100 Rm(5) cond(4) 0 1 Rn(5) Rd(5) ]", mnemonic="CSINC")
@ispec("32[ sf 1 0 11010100 Rm(5) cond(4) 0 0 Rn(5) Rd(5) ]", mnemonic="CSINV")
@ispec("32[ sf 1 0 11010100 Rm(5) cond(4) 0 1 Rn(5) Rd(5) ]", mnemonic="CSNEG")
@ispec("32[ sf 0 0 11010100 Rm(5) cond(4) 0 0 Rn(5) Rd(5) ]", mnemonic="CSEL")
def A64_CSx(obj, sf, Rm, cond, Rn, Rd):
    obj.datasize = 64 if (sf == 1) else 32
    regs = env.Xregs if sf == 1 else env.Wregs
    obj.d = sp2z(regs[Rd])
    obj.n = sp2z(regs[Rn])
    obj.m = sp2z(regs[Rm])
    obj.cond = cond
    obj.operands = [obj.d, obj.n, obj.m, obj.cond]
    obj.type = type_data_processing


@ispec("32[ 1101010100 0 00 011 0011 CRm(4) 010 11111 ]", mnemonic="CLREX")
@ispec("32[ 1101010100 0 00 011 0011 CRm(4) 101 11111 ]", mnemonic="DMB")
@ispec("32[ 1101010100 0 00 011 0011 CRm(4) 100 11111 ]", mnemonic="DSB")
@ispec("32[ 1101010100 0 00 011 0011 CRm(4) 110 11111 ]", mnemonic="ISB")
def A64_generic(obj, CRm):
    obj.imm = env.cst(CRm, 4)
    obj.operands = [obj.imm]
    obj.type = type_cpu_state


@ispec("32[ 1101010100 0 00 011 0010 CRm(4) op2(3) 11111 ]", mnemonic="HINT")
def A64_sync(obj, CRm, op2):
    obj.imm = env.cst(CRm << 3 + op2, 7)
    obj.operands = [obj.imm]
    obj.type = type_cpu_state


@ispec("32[ 1101011 0101 11111 000000 11111 00000 ]", mnemonic="DRPS")
@ispec("32[ 1101011 0100 11111 000000 11111 00000 ]", mnemonic="ERET")
def A64_generic(obj):
    obj.type = type_cpu_state


@ispec("32[   sf 1 0 11010110  00000 00010 1 Rn(5) Rd(5) ]", mnemonic="CLS")
@ispec("32[   sf 1 0 11010110  00000 00010 0 Rn(5) Rd(5) ]", mnemonic="CLZ")
@ispec("32[   sf 1 0 11010110  00000 00000 0 Rn(5) Rd(5) ]", mnemonic="RBIT")
@ispec("32[   sf 1 0 11010110  00000 00000 1 Rn(5) Rd(5) ]", mnemonic="REV16")
@ispec("32[ 1=sf 1 0 11010110  00000 00001 0 Rn(5) Rd(5) ]", mnemonic="REV32")
@ispec("32[ 0=sf 1 0 11010110  00000 0000 10 Rn(5) Rd(5) ]", mnemonic="REV")
@ispec("32[ 1=sf 1 0 11010110  00000 0000 11 Rn(5) Rd(5) ]", mnemonic="REV")
def A64_generic(obj, sf, Rn, Rd):
    obj.datasize = 64 if (sf == 1) else 32
    regs = env.Xregs if sf == 1 else env.Wregs
    obj.d = sp2z(regs[Rd])
    obj.n = sp2z(regs[Rn])
    obj.operands = [obj.d, obj.n]
    obj.type = type_data_processing


@ispec("32[ 0 0 0 11010110 Rm(5) 010 0 00=sz(2) Rn(5) Rd(5) ]", mnemonic="CRC32B")
@ispec("32[ 0 0 0 11010110 Rm(5) 010 0 01=sz(2) Rn(5) Rd(5) ]", mnemonic="CRC32H")
@ispec("32[ 0 0 0 11010110 Rm(5) 010 0 10=sz(2) Rn(5) Rd(5) ]", mnemonic="CRC32W")
@ispec("32[ 1 0 0 11010110 Rm(5) 010 0 11=sz(2) Rn(5) Rd(5) ]", mnemonic="CRC32X")
@ispec("32[ 0 0 0 11010110 Rm(5) 010 1 00=sz(2) Rn(5) Rd(5) ]", mnemonic="CRC32CB")
@ispec("32[ 0 0 0 11010110 Rm(5) 010 1 01=sz(2) Rn(5) Rd(5) ]", mnemonic="CRC32CH")
@ispec("32[ 0 0 0 11010110 Rm(5) 010 1 10=sz(2) Rn(5) Rd(5) ]", mnemonic="CRC32CW")
@ispec("32[ 1 0 0 11010110 Rm(5) 010 1 11=sz(2) Rn(5) Rd(5) ]", mnemonic="CRC32CX")
def A64_generic(obj, Rm, sz, Rn, Rd):
    obj.d = sp2z(env.Wregs[Rd])
    obj.n = sp2z(env.Wregs[Rn])
    obj.m = sp2z(env.Xregs[Rm]) if sz == 0b11 else sp2z(env.Wregs[Rm])
    obj.size = 8 << sz
    obj.operands = [obj.d, obj.n, obj.m]
    obj.type = type_data_processing


@ispec("32[ 1 00 11011 0 10 Rm(5) 0 11111 Rn(5) Rd(5) ]", mnemonic="SMULH")
@ispec("32[ 1 00 11011 1 10 Rm(5) 0 11111 Rn(5) Rd(5) ]", mnemonic="UMULH")
def A64_CRC32Cx(obj, Rm, Rn, Rd):
    obj.datasize = 64
    regs = env.Xregs
    obj.d = regs[Rd]
    obj.n = regs[Rn]
    obj.m = regs[Rm]
    obj.operands = [obj.d, obj.n, obj.m]
    obj.type = type_data_processing


@ispec("32[ sf 0 0 100111 N 0 Rm(5) imms(6) Rn(5) Rd(5) ]", mnemonic="EXTR")
def A64_EXTR(obj, sf, N, Rm, imms, Rn, Rd):
    if sf != N:
        raise InstructionError(obj)
    if sf == 0 and imms > 31:
        raise InstructionError(obj)
    obj.datasize = 64 if (sf == 1) else 32
    regs = env.Xregs if sf == 1 else env.Wregs
    obj.d = sp2z(regs[Rd])
    obj.n = sp2z(regs[Rn])
    obj.m = sp2z(regs[Rm])
    obj.lsb = env.cst(imms, 6)
    obj.operands = [obj.d, obj.n, obj.m, obj.lsb]
    obj.type = type_data_processing


@ispec(
    "32[ 1-=size(2) 001000 1=o2 1 0=o1 11111=Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDAR",
)
@ispec(
    "32[ 1-=size(2) 001000 0=o2 1 0=o1 11111=Rs(5) 0=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDXR",
)
@ispec(
    "32[ 1-=size(2) 001000 0=o2 1 0=o1 11111=Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDAXR",
)
@ispec(
    "32[ 1-=size(2) 001000 1=o2 0 0=o1 11111=Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STLR",
)
@ispec(
    "32[ 1-=size(2) 001000 1=o2 0 1=o1       Rs(5) 1=o0       Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STLXP",
)
@ispec(
    "32[ 1-=size(2) 001000 0=o2 0 1=o1       Rs(5) 0=o0       Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STXP",
)
@ispec(
    "32[ 1-=size(2) 001000 0=o2 0 0=o1       Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STLXR",
)
@ispec(
    "32[ 1-=size(2) 001000 0=o2 0 0=o1       Rs(5) 0=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STXR",
)
@ispec(
    "32[ 00=size(2) 001000 0=o2 0 0=o1       Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STLXRB",
)
@ispec(
    "32[ 01=size(2) 001000 0=o2 0 0=o1       Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STLXRH",
)
@ispec(
    "32[ 00=size(2) 001000 0=o2 0 0=o1       Rs(5) 0=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STXRB",
)
@ispec(
    "32[ 01=size(2) 001000 0=o2 0 0=o1       Rs(5) 0=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STXRH",
)
@ispec(
    "32[ 00=size(2) 001000 1=o2 1 0=o1 11111=Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDARB",
)
@ispec(
    "32[ 00=size(2) 001000 1=o2 0 0=o1 11111=Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STLRB",
)
@ispec(
    "32[ 01=size(2) 001000 1=o2 1 0=o1 11111=Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDARH",
)
@ispec(
    "32[ 01=size(2) 001000 1=o2 0 0=o1 11111=Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STLRH",
)
@ispec(
    "32[ 00=size(2) 001000 0=o2 1 0=o1 11111=Rs(5) 0=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDXRB",
)
@ispec(
    "32[ 00=size(2) 001000 0=o2 1 0=o1 11111=Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDAXRB",
)
@ispec(
    "32[ 01=size(2) 001000 0=o2 1 0=o1 11111=Rs(5) 0=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDXRH",
)
@ispec(
    "32[ 01=size(2) 001000 0=o2 1 0=o1 11111=Rs(5) 1=o0 11111=Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDAXRH",
)
@ispec(
    "32[ 1-=size(2) 001000 0=o2 1 1=o1 11111=Rs(5) 1=o0       Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDAXP",
)
@ispec(
    "32[ 1-=size(2) 001000 0=o2 1 1=o1 11111=Rs(5) 0=o0       Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDXP",
)
def A64_load_store(obj, size, o2, o1, Rs, o0, Rt2, Rn, Rt):
    obj.acctype = o0
    obj.excl = o2 == 0
    obj.pair = o1 == 1
    obj.elsize = 8 << size
    obj.regsize = 64 if obj.elsize == 64 else 32
    obj.datasize = obj.elsize * 2 if obj.pair else obj.elsize
    regs = env.Xregs if obj.regsize == 64 else env.Wregs
    obj.t = sp2z(regs[Rt])
    obj.n = env.Xregs[Rn]
    obj.operands = [obj.t, obj.n]
    if Rt2 != 0b11111:
        obj.t2 = sp2z(regs[Rt2])
        obj.operands.insert(1, obj.t2)
    if Rs != 0b11111:
        obj.s = sp2z(env.Wregs[Rs])
        obj.operands.insert(0, obj.s)
    obj.type = type_data_processing


@ispec(
    "32[ -0=opc(2) 101 0 000 1 imm7(7) Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDNP",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ -0=opc(2) 101 0 001 1 imm7(7) Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDP",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ -0=opc(2) 101 0 011 1 imm7(7) Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDP",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ -0=opc(2) 101 0 010 1 imm7(7) Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDP",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ -0=opc(2) 101 0 000 0 imm7(7) Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STNP",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ -0=opc(2) 101 0 001 0 imm7(7) Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STP",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ -0=opc(2) 101 0 011 0 imm7(7) Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STP",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ -0=opc(2) 101 0 010 0 imm7(7) Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="STP",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 01=opc(2) 101 0 001 1 imm7(7) Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDPSW",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ 01=opc(2) 101 0 011 1 imm7(7) Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDPSW",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ 01=opc(2) 101 0 010 1 imm7(7) Rt2(5) Rn(5) Rt(5) ]",
    mnemonic="LDPSW",
    wback=False,
    postindex=False,
)
def A64_load_store(obj, opc, imm7, Rt2, Rn, Rt):
    x = opc >> 1
    obj.scale = 2 + x
    obj.datasize = 8 << obj.scale
    obj.offset = env.cst(imm7, 7).signextend(64) << obj.scale
    regs = env.Xregs if opc else env.Wregs
    obj.t = sp2z(regs[Rt])
    obj.t2 = sp2z(regs[Rt2])
    obj.n = env.Xregs[Rn]
    obj.operands = [obj.t, obj.t2, obj.n, obj.offset]
    obj.type = type_data_processing


@ispec(
    "32[ 1-=size(2) 111 0 00 01=opc(2) 0 imm9(9) 01 Rn(5) Rt(5) ]",
    mnemonic="LDR",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ 1-=size(2) 111 0 00 01=opc(2) 0 imm9(9) 11 Rn(5) Rt(5) ]",
    mnemonic="LDR",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ 1-=size(2) 111 0 00 01=opc(2) 0 imm9(9) 10 Rn(5) Rt(5) ]",
    mnemonic="LDTR",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 1-=size(2) 111 0 00 00=opc(2) 0 imm9(9) 10 Rn(5) Rt(5) ]",
    mnemonic="STTR",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 1-=size(2) 111 0 00 01=opc(2) 0 imm9(9) 00 Rn(5) Rt(5) ]",
    mnemonic="LDUR",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 1-=size(2) 111 0 00 00=opc(2) 0 imm9(9) 00 Rn(5) Rt(5) ]",
    mnemonic="STUR",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 1-=size(2) 111 0 00 00=opc(2) 0 imm9(9) 01 Rn(5) Rt(5) ]",
    mnemonic="STR",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ 1-=size(2) 111 0 00 00=opc(2) 0 imm9(9) 11 Rn(5) Rt(5) ]",
    mnemonic="STR",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 00 01=opc(2) 0 imm9(9) 01 Rn(5) Rt(5) ]",
    mnemonic="LDRB",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ 00=size(2) 111 0 00 01=opc(2) 0 imm9(9) 11 Rn(5) Rt(5) ]",
    mnemonic="LDRB",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 00 00=opc(2) 0 imm9(9) 01 Rn(5) Rt(5) ]",
    mnemonic="STRB",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ 00=size(2) 111 0 00 00=opc(2) 0 imm9(9) 11 Rn(5) Rt(5) ]",
    mnemonic="STRB",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 00 01=opc(2) 0 imm9(9) 10 Rn(5) Rt(5) ]",
    mnemonic="LDTRB",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 00 00=opc(2) 0 imm9(9) 10 Rn(5) Rt(5) ]",
    mnemonic="STTRB",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 00 01=opc(2) 0 imm9(9) 00 Rn(5) Rt(5) ]",
    mnemonic="LDURB",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 00 00=opc(2) 0 imm9(9) 00 Rn(5) Rt(5) ]",
    mnemonic="STURB",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 00 01=opc(2) 0 imm9(9) 01 Rn(5) Rt(5) ]",
    mnemonic="LDRH",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ 01=size(2) 111 0 00 01=opc(2) 0 imm9(9) 11 Rn(5) Rt(5) ]",
    mnemonic="LDRH",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 00 00=opc(2) 0 imm9(9) 01 Rn(5) Rt(5) ]",
    mnemonic="STRH",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ 01=size(2) 111 0 00 00=opc(2) 0 imm9(9) 11 Rn(5) Rt(5) ]",
    mnemonic="STRH",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 00 01=opc(2) 0 imm9(9) 10 Rn(5) Rt(5) ]",
    mnemonic="LDTRH",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 00 00=opc(2) 0 imm9(9) 10 Rn(5) Rt(5) ]",
    mnemonic="STTRH",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 00 01=opc(2) 0 imm9(9) 00 Rn(5) Rt(5) ]",
    mnemonic="LDURH",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 00 00=opc(2) 0 imm9(9) 00 Rn(5) Rt(5) ]",
    mnemonic="STURH",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 10=size(2) 111 0 00 10=opc(2) 0 imm9(9) 01 Rn(5) Rt(5) ]",
    mnemonic="LDRSW",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ 10=size(2) 111 0 00 10=opc(2) 0 imm9(9) 11 Rn(5) Rt(5) ]",
    mnemonic="LDRSW",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ 10=size(2) 111 0 00 10=opc(2) 0 imm9(9) 10 Rn(5) Rt(5) ]",
    mnemonic="LDTRSW",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 10=size(2) 111 0 00 10=opc(2) 0 imm9(9) 00 Rn(5) Rt(5) ]",
    mnemonic="LDURSW",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 11=size(2) 111 0 00 10=opc(2) 0 imm9(9) 00 Rn(5) Rt(5) ]",
    mnemonic="PRFUM",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 00 1-=opc(2) 0 imm9(9) 01 Rn(5) Rt(5) ]",
    mnemonic="LDRSB",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ 00=size(2) 111 0 00 1-=opc(2) 0 imm9(9) 11 Rn(5) Rt(5) ]",
    mnemonic="LDRSB",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 00 1-=opc(2) 0 imm9(9) 10 Rn(5) Rt(5) ]",
    mnemonic="LDTRSB",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 00 1-=opc(2) 0 imm9(9) 00 Rn(5) Rt(5) ]",
    mnemonic="LDURSB",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 00 1-=opc(2) 0 imm9(9) 01 Rn(5) Rt(5) ]",
    mnemonic="LDRSH",
    wback=True,
    postindex=True,
)
@ispec(
    "32[ 01=size(2) 111 0 00 1-=opc(2) 0 imm9(9) 11 Rn(5) Rt(5) ]",
    mnemonic="LDRSH",
    wback=True,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 00 1-=opc(2) 0 imm9(9) 10 Rn(5) Rt(5) ]",
    mnemonic="LDTRSH",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 00 1-=opc(2) 0 imm9(9) 00 Rn(5) Rt(5) ]",
    mnemonic="LDURSH",
    wback=False,
    postindex=False,
)
def A64_load_store(obj, size, opc, imm9, Rn, Rt):
    obj.scale = size
    obj.datasize = 8 << obj.scale
    obj.offset = env.cst(imm9, 9).signextend(64)
    obj.n = env.Xregs[Rn]
    if opc & 2 == 0:
        obj.regsize = 64 if size == 0b11 else 32
        obj.signed = False
    else:
        if size == 0b11:  # special case of PRFUM
            obj.prfop = Rt
            obj.operands = [obj.prfop, obj.n, obj.offset]
            obj.type = type_cpu_state
            return
        obj.regsize = 32 if opc & 1 == 1 else 64
        obj.signed = True
    obj.t = sp2z(env.Xregs[Rt]) if obj.regsize == 64 else sp2z(env.Wregs[Rt])
    obj.operands = [obj.t, obj.n, obj.offset]
    obj.type = type_data_processing


@ispec(
    "32[ 1-=size(2) 111 0 01 01=opc(2) imm12(12) Rn(5) Rt(5) ]",
    mnemonic="LDR",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 1-=size(2) 111 0 01 00=opc(2) imm12(12) Rn(5) Rt(5) ]",
    mnemonic="STR",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 01 01=opc(2) imm12(12) Rn(5) Rt(5) ]",
    mnemonic="LDRB",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 01 00=opc(2) imm12(12) Rn(5) Rt(5) ]",
    mnemonic="STRB",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 01 01=opc(2) imm12(12) Rn(5) Rt(5) ]",
    mnemonic="LDRH",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 01 00=opc(2) imm12(12) Rn(5) Rt(5) ]",
    mnemonic="STRH",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 10=size(2) 111 0 01 10=opc(2) imm12(12) Rn(5) Rt(5) ]",
    mnemonic="LDRSW",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 11=size(2) 111 0 01 10=opc(2) imm12(12) Rn(5) Rt(5) ]",
    mnemonic="PRFM",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 00=size(2) 111 0 01 1-=opc(2) imm12(12) Rn(5) Rt(5) ]",
    mnemonic="LDRSB",
    wback=False,
    postindex=False,
)
@ispec(
    "32[ 01=size(2) 111 0 01 1-=opc(2) imm12(12) Rn(5) Rt(5) ]",
    mnemonic="LDRSH",
    wback=False,
    postindex=False,
)
def A64_load_store(obj, size, opc, imm12, Rn, Rt):
    obj.scale = size
    obj.datasize = 8 << obj.scale
    obj.offset = env.cst(imm12, 64) << obj.scale
    obj.n = env.Xregs[Rn]
    if opc & 2 == 0:
        obj.regsize = 64 if size == 0b11 else 32
        obj.signed = False
    else:
        if size == 0b11:  # special case of PRFM
            obj.prfop = Rt
            obj.operands = [obj.prfop, obj.n, obj.offset]
            obj.type = type_cpu_state
            return
        obj.regsize = 32 if opc & 1 == 1 else 64
        obj.signed = True
    obj.t = sp2z(env.Xregs[Rt]) if obj.regsize == 64 else sp2z(env.Wregs[Rt])
    obj.operands = [obj.t, obj.n, obj.offset]
    obj.type = type_data_processing


@ispec("32[ 0-=opc(2) 011 0 00 imm19(19) Rt(5) ]", mnemonic="LDR")
@ispec("32[ 10=opc(2) 011 0 00 imm19(19) Rt(5) ]", mnemonic="LDRSW")
@ispec("32[ 11=opc(2) 011 0 00 imm19(19) Rt(5) ]", mnemonic="PRFM")
def A64_load_store(obj, opc, imm19, Rt):
    obj.offset = env.cst(imm19 << 2, 21).signextend(64)
    if opc == 0b11:  # PRFM:
        obj.prfop = Rt
        obj.operands = [obj.prfop, obj.offset]
        obj.type = type_cpu_state
        return
    obj.signed = False
    obj.size = 4 << opc
    if opc == 2:
        obj.size = 4
        obj.signed = True
    obj.t = sp2z(env.Xregs[Rt]) if obj.size == 8 else sp2z(env.Wregs[Rt])
    obj.operands = [obj.t, obj.offset]
    obj.type = type_data_processing


@ispec(
    "32[ 1-=size(2) 111 0 00 01=opc(2) 1 Rm(5) option(3) S 10 Rn(5) Rt(5) ]",
    mnemonic="LDR",
)
@ispec(
    "32[ 1-=size(2) 111 0 00 00=opc(2) 1 Rm(5) option(3) S 10 Rn(5) Rt(5) ]",
    mnemonic="STR",
)
@ispec(
    "32[ 00=size(2) 111 0 00 01=opc(2) 1 Rm(5) option(3) S 10 Rn(5) Rt(5) ]",
    mnemonic="LDRB",
)
@ispec(
    "32[ 00=size(2) 111 0 00 00=opc(2) 1 Rm(5) option(3) S 10 Rn(5) Rt(5) ]",
    mnemonic="STRB",
)
@ispec(
    "32[ 01=size(2) 111 0 00 01=opc(2) 1 Rm(5) option(3) S 10 Rn(5) Rt(5) ]",
    mnemonic="LDRH",
)
@ispec(
    "32[ 01=size(2) 111 0 00 00=opc(2) 1 Rm(5) option(3) S 10 Rn(5) Rt(5) ]",
    mnemonic="STRH",
)
@ispec(
    "32[ 00=size(2) 111 0 00 1-=opc(2) 1 Rm(5) option(3) S 10 Rn(5) Rt(5) ]",
    mnemonic="LDRSB",
)
@ispec(
    "32[ 01=size(2) 111 0 00 1-=opc(2) 1 Rm(5) option(3) S 10 Rn(5) Rt(5) ]",
    mnemonic="LDRSH",
)
@ispec(
    "32[ 10=size(2) 111 0 00 10=opc(2) 1 Rm(5) option(3) S 10 Rn(5) Rt(5) ]",
    mnemonic="LDRSW",
)
@ispec(
    "32[ 11=size(2) 111 0 00 10=opc(2) 1 Rm(5) option(3) S 10 Rn(5) Rt(5) ]",
    mnemonic="PRFM",
)
def A64_load_store(obj, size, opc, Rm, option, S, Rn, Rt):
    obj.wback = False
    obj.postindex = False
    obj.scale = size
    obj.datasize = 8 << obj.scale
    if option & 2 == 0:
        raise InstructionError(obj)
    obj.extend_type = option
    obj.shift = obj.scale if S == 1 else 0
    obj.n = env.Xregs[Rn]
    m = sp2z(env.Wregs[Rm]) if option & 1 == 0 else sp2z(env.Xregs[Rm])
    obj.m = ExtendReg(m, option, obj.shift)
    if opc & 2 == 0:
        obj.regsize = 64 if size == 0b11 else 32
        obj.signed = False
    else:
        if size == 0b11:  # special case of PRFM
            obj.prfop = Rt
            obj.operands = [obj.prfop, obj.n, obj.offset]
            obj.type = type_cpu_state
            return
        obj.regsize = 32 if opc & 1 == 1 else 64
        obj.signed = True
    obj.t = sp2z(env.Xregs[Rt]) if obj.regsize == 64 else sp2z(env.Wregs[Rt])
    obj.operands = [obj.t, obj.n, obj.m]
    obj.type = type_data_processing


@ispec("32[ sf 00 11011 000 Rm(5) 0 Ra(5) Rn(5) Rd(5) ]", mnemonic="MADD")
@ispec("32[ sf 00 11011 000 Rm(5) 1 Ra(5) Rn(5) Rd(5) ]", mnemonic="MSUB")
def A64_generic(obj, sf, Rm, Ra, Rn, Rd):
    obj.destsize = 64 if sf == 1 else 32
    obj.datasize = obj.destsize
    regs = env.Wregs if obj.datasize == 32 else env.Xregs
    obj.d = sp2z(regs[Rd])
    obj.n = sp2z(regs[Rn])
    obj.m = sp2z(regs[Rm])
    obj.a = sp2z(regs[Ra])
    obj.operands = [obj.d, obj.n, obj.m, obj.a]
    obj.type = type_data_processing


@ispec("32[ 1 00 11011 0 01 Rm(5) 0 Ra(5) Rn(5) Rd(5) ]", mnemonic="SMADDL")
@ispec("32[ 1 00 11011 0 01 Rm(5) 1 Ra(5) Rn(5) Rd(5) ]", mnemonic="SMSUBL")
@ispec("32[ 1 00 11011 1 01 Rm(5) 0 Ra(5) Rn(5) Rd(5) ]", mnemonic="UMADDL")
@ispec("32[ 1 00 11011 1 01 Rm(5) 1 Ra(5) Rn(5) Rd(5) ]", mnemonic="UMSUBL")
def A64_generic(obj, Rm, Ra, Rn, Rd):
    obj.destsize = 64
    obj.datasize = 32
    obj.d = sp2z(env.Xregs[Rd])
    obj.n = sp2z(env.Wregs[Rn])
    obj.m = sp2z(env.Wregs[Rm])
    obj.a = sp2z(env.Xregs[Ra])
    obj.operands = [obj.d, obj.n, obj.m, obj.a]
    obj.type = type_data_processing


@ispec("32[ sf 00 100101 hw(2) imm16(16) Rd(5) ]", mnemonic="MOVN")
@ispec("32[ sf 10 100101 hw(2) imm16(16) Rd(5) ]", mnemonic="MOVZ")
@ispec("32[ sf 11 100101 hw(2) imm16(16) Rd(5) ]", mnemonic="MOVK")
def A64_generic(obj, sf, hw, imm16, Rd):
    if sf == 1 and hw & 2 == 1:
        raise InstructionError(obj)
    obj.datasize = 64 if sf == 1 else 32
    pos = hw << 4
    obj.imm = env.cst(imm16, 16) << pos
    obj.d = sp2z(env.Xregs[Rd]) if sf == 1 else sp2z(env.Wregs[Rd])
    obj.operands = [obj.d, obj.imm]
    obj.type = type_data_processing


@ispec("32[ b5 011011 1 b40(5) imm14(14) Rt(5) ]", mnemonic="TBNZ")
@ispec("32[ b5 011011 0 b40(5) imm14(14) Rt(5) ]", mnemonic="TBZ")
def A64_generic(obj, b5, b40, imm14, Rt):
    obj.datasize = 64 if b5 == 1 else 32
    obj.bitpos = b5 << 5 + b40
    obj.offset = env.cst(imm14 << 2, 16).signextend(64)
    obj.t = sp2z(env.Xregs[Rt]) if b5 == 1 else sp2z(env.Wregs[Rt])
    obj.operands = [obj.t, obj.bitpos, obj.offset]
    obj.type = type_data_processing
