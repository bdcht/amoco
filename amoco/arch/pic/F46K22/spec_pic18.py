# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.arch.pic.F46K22 import env

from amoco.arch.core import *

# -------------------------------------------------------
# instruction PIC18(L)F2X/4XK22 decoders
# -------------------------------------------------------

ISPECS = []

# virtual registers/operations handler:


def check_virtual(obj, r, size=8, pos=0):
    if not obj.misc["virts"]:
        obj.misc["virts"] = []
    if not (r._is_reg and r.ref[-1] in ("0", "1", "2")):
        return r
    ref = r.ref[:-1]
    i = int(r.ref[-1])
    f = (env.fsr0, env.fsr1, env.fsr2)[i]
    if ref == "indf":
        dst = env.mem(f[0:12], size)
    elif ref == "plusw":
        dst = env.mem(f[0:12] + env.w.signextend(12), size)
    elif ref in ("postinc", "postdec", "preinc"):
        obj.misc["virts"].append((ref, f))
        dst = env.mem(f[0:12], size)
    else:
        dst = r
    return dst


# byte-oriented format:


@ispec("16<[ 0010 01   d a f(8) ]", mnemonic="ADDWF")
@ispec("16<[ 0010 00   d a f(8) ]", mnemonic="ADDWFC")
@ispec("16<[ 0001 01   d a f(8) ]", mnemonic="ANDWF")
@ispec("16<[ 0110 10 1=d a f(8) ]", mnemonic="CLRF")
@ispec("16<[ 0001 11   d a f(8) ]", mnemonic="COMF")
@ispec("16<[ 0000 01   d a f(8) ]", mnemonic="DECF")
@ispec("16<[ 0010 10   d a f(8) ]", mnemonic="INCF")
@ispec("16<[ 0001 00   d a f(8) ]", mnemonic="IORWF")
@ispec("16<[ 0101 00   d a f(8) ]", mnemonic="MOVF")
@ispec("16<[ 0110 11 1=d a f(8) ]", mnemonic="MOVWF")
@ispec("16<[ 0000 00 1=d a f(8) ]", mnemonic="MULWF")
@ispec("16<[ 0110 11 0=d a f(8) ]", mnemonic="NEGF")
@ispec("16<[ 0011 01   d a f(8) ]", mnemonic="RLCF")
@ispec("16<[ 0100 01   d a f(8) ]", mnemonic="RLNCF")
@ispec("16<[ 0011 00   d a f(8) ]", mnemonic="RRCF")
@ispec("16<[ 0100 00   d a f(8) ]", mnemonic="RRNCF")
@ispec("16<[ 0110 10 0=d a f(8) ]", mnemonic="SETF")
@ispec("16<[ 0101 01   d a f(8) ]", mnemonic="SUBFWB")
@ispec("16<[ 0101 11   d a f(8) ]", mnemonic="SUBWF")
@ispec("16<[ 0101 10   d a f(8) ]", mnemonic="SUBWFB")
@ispec("16<[ 0011 10   d a f(8) ]", mnemonic="SWAPF")
@ispec("16<[ 0001 10   d a f(8) ]", mnemonic="XORWF")
def byte_oriented(obj, d, a, f):
    src = env.getreg(a, f)
    obj.d = d
    obj.a = a
    obj.src = check_virtual(obj, src)
    obj.dst = env.wreg if d == 0 else obj.src
    obj.operands = [src]
    obj.type = type_data_processing


@ispec("16<[ 0110 00 1=d a f(8) ]", mnemonic="CPFSEQ")
@ispec("16<[ 0110 01 0=d a f(8) ]", mnemonic="CPFSGT")
@ispec("16<[ 0110 00 0=d a f(8) ]", mnemonic="CPFSLT")
@ispec("16<[ 0010 11   d a f(8) ]", mnemonic="DECFSZ")
@ispec("16<[ 0100 11   d a f(8) ]", mnemonic="DCFSNZ")
@ispec("16<[ 0011 11   d a f(8) ]", mnemonic="INCFSZ")
@ispec("16<[ 0100 10   d a f(8) ]", mnemonic="INFSNZ")
@ispec("16<[ 0110 01 1=d a f(8) ]", mnemonic="TSTFSZ")
def byte_oriented(obj, d, a, f):
    src = env.getreg(a, f)
    obj.d = d
    obj.a = a
    obj.src = check_virtual(obj, src)
    obj.dst = env.wreg if d == 0 else obj.src
    obj.operands = [src]
    obj.type = type_control_flow


# MOVFF is tricky ! (try a MOVFF POSTINC0, POSTINC0 ... and variants ;)
@ispec("32<[ 1111 fd(12) 1100 fs(12) ]", mnemonic="MOVFF")
def decode_movff(obj, fd, fs):
    if fs >> 8 == 0xF:
        src = env.getreg(0, fs & 0xFF)
    else:
        src = env.mem(env.cst(fs, 12), 8)
    if fd >> 8 == 0xF:
        dst = env.getreg(0, fd & 0xFF)
    else:
        dst = env.mem(env.cst(fd, 12), 8)
    if dst in (env.pcl, env.tosu, env.tosh, env.tosl):
        raise InstructionError(obj)
    obj.src = check_virtual(obj, src)
    obj.dst = check_virtual(obj, dst)
    obj.operands = [src, dst]
    obj.type = type_data_processing


# bit-oriented format:


@ispec("16<[ 1001 b(3) a f(8) ]", mnemonic="BCF", type=type_data_processing)
@ispec("16<[ 1000 b(3) a f(8) ]", mnemonic="BSF", type=type_data_processing)
@ispec("16<[ 1011 b(3) a f(8) ]", mnemonic="BTFSC", type=type_control_flow)
@ispec("16<[ 1010 b(3) a f(8) ]", mnemonic="BTFSS", type=type_control_flow)
@ispec("16<[ 0111 b(3) a f(8) ]", mnemonic="BTG", type=type_data_processing)
def bit_oriented(obj, b, a, f):
    dst = env.getreg(a, f)
    obj.dst = check_virtual(obj, dst)
    obj.a = a
    obj.b = b
    obj.operands = [dst, b]


# control operations format:


@ispec("16<[ 1110 0010 n(8) ]", mnemonic="BC")
@ispec("16<[ 1110 0110 n(8) ]", mnemonic="BN")
@ispec("16<[ 1110 0011 n(8) ]", mnemonic="BNC")
@ispec("16<[ 1110 0111 n(8) ]", mnemonic="BNN")
@ispec("16<[ 1110 0101 n(8) ]", mnemonic="BNOV")
@ispec("16<[ 1110 0001 n(8) ]", mnemonic="BNZ")
@ispec("16<[ 1110 0100 n(8) ]", mnemonic="BOV")
@ispec("16<[ 1101 0   n(11) ]", mnemonic="BRA")
@ispec("16<[ 1110 0000 n(8) ]", mnemonic="BZ")
@ispec("16<[ 1101 1   n(11) ]", mnemonic="RCALL")
def control_rel(obj, n):
    obj.offset = env.cst(n, 8)
    obj.offset.sf = True
    obj.operands = [obj.offset]
    obj.type = type_control_flow


@ispec("32<[ 1111 kh(12) 1110 110 s kl(8) ]", mnemonic="CALL")
def control(obj, kh, s, kl):
    obj.offset = env.cst(((kh << 8) + kl) << 1, 21)
    obj.misc["fast"] = s == 1
    obj.operands = [obj.offset]
    obj.type = type_control_flow


@ispec("16<[ 0000 0000 0000 0100 ]", mnemonic="CLRWDT")
@ispec("16<[ 0000 0000 0000 0111 ]", mnemonic="DAW")
@ispec("16<[ 0000 0000 0000 0000 ]", mnemonic="NOP")
@ispec("16<[ 1111 ---- ---- ---- ]", mnemonic="NOP")
@ispec("16<[ 0000 0000 0000 0110 ]", mnemonic="POP")
@ispec("16<[ 0000 0000 0000 0101 ]", mnemonic="PUSH")
@ispec("16<[ 0000 0000 1111 1111 ]", mnemonic="RESET")
@ispec("16<[ 0000 0000 0000 0011 ]", mnemonic="SLEEP")
def noop(obj):
    obj.operands = []
    obj.type = type_data_processing


@ispec("16<[ 0000 0000 0000 1000 ]", mnemonic="TBLRD", _flg=None)
@ispec("16<[ 0000 0000 0000 1001 ]", mnemonic="TBLRD", _flg="postinc")
@ispec("16<[ 0000 0000 0000 1010 ]", mnemonic="TBLRD", _flg="postdec")
@ispec("16<[ 0000 0000 0000 1011 ]", mnemonic="TBLRD", _flg="preinc")
@ispec("16<[ 0000 0000 0000 1100 ]", mnemonic="TBLWT", _flg=None)
@ispec("16<[ 0000 0000 0000 1101 ]", mnemonic="TBLWT", _flg="postinc")
@ispec("16<[ 0000 0000 0000 1110 ]", mnemonic="TBLWT", _flg="postdec")
@ispec("16<[ 0000 0000 0000 1111 ]", mnemonic="TBLWT", _flg="preinc")
def tblrw(obj, _flg):
    obj.operands = []
    # tblrd/wt instructions use implicit virtual operations:
    obj.misc["virts"] = []
    if _flg:
        obj.misc["virts"].append((_flg, env.tblptr))
    obj.type = type_data_processing


@ispec("32<[ 1111 kh(12) 1110 1111 kl(8) ]", mnemonic="GOTO")
def control(obj, kh, kl):
    obj.imm = env.cst(((kh << 8) + kl) << 1, 21)
    obj.operands = [obj.imm]
    obj.type = type_control_flow


@ispec("16<[ 0000 0000 0001 000 s ]", mnemonic="RETFIE")
@ispec("16<[ 0000 0000 0001 001 s ]", mnemonic="RETURN")
def control(obj, s):
    obj.operands = [s]
    obj.type = type_control_flow


@ispec("16<[ 0000 1100 k(8) ]", mnemonic="RETLW")
def control(obj, k):
    obj.imm = env.cst(k, 8)
    obj.operands = [obj.imm]
    obj.type = type_control_flow


# literal operations format:


@ispec("16<[ 0000 1111 k(8) ]", mnemonic="ADDLW")
@ispec("16<[ 0000 1011 k(8) ]", mnemonic="ANDLW")
@ispec("16<[ 0000 1001 k(8) ]", mnemonic="IORLW")
@ispec("16<[ 0000 1110 k(8) ]", mnemonic="MOVLW")
@ispec("16<[ 0000 1101 k(8) ]", mnemonic="MULLW")
@ispec("16<[ 0000 1100 k(8) ]", mnemonic="RETLW")
@ispec("16<[ 0000 1000 k(8) ]", mnemonic="SUBLW")
@ispec("16<[ 0000 1010 k(8) ]", mnemonic="XORLW")
def literal(obj, k):
    obj.imm = env.cst(k, 8)
    obj.operands = [obj.imm]
    obj.type = type_data_processing


@ispec("32<[ 1111 0000 kl(8) 1110 1110 00 f(2) kh(4) ]", mnemonic="LFSR")
def literal(obj, kh, f, kl):
    if f == 3:
        raise InstructionError(obj)
    dst = (env.fsr0, env.fsr1, env.fsr2)[f]
    src = env.cst(((kh << 8) + kl), 12)
    obj.dst = dst
    obj.src = src
    obj.operands = [dst, src]
    obj.type = type_data_processing


@ispec("16<[ 0000 0001 0000 k(4) ]", mnemonic="MOVLB")
def literal(obj, k):
    obj.imm = env.cst(k, 4)
    obj.operands = [obj.imm]
    obj.type = type_data_processing
