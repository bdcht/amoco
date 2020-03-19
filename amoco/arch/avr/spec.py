# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")
from amoco.arch.core import *
from amoco.arch.avr import env

ISPECS = []


@ispec("16<[ 0001 11 R d(5) r(4) ]", mnemonic="ADC")
@ispec("16<[ 0000 11 R d(5) r(4) ]", mnemonic="ADD")
@ispec("16<[ 0010 00 R d(5) r(4) ]", mnemonic="ADD")
@ispec("16<[ 0001 01 R d(5) r(4) ]", mnemonic="CP")
@ispec("16<[ 0000 01 R d(5) r(4) ]", mnemonic="CPC")
@ispec("16<[ 0001 00 R d(5) r(4) ]", mnemonic="CPSE")
@ispec("16<[ 0010 01 R d(5) r(4) ]", mnemonic="EOR")
@ispec("16<[ 0010 11 R d(5) r(4) ]", mnemonic="MOV")
@ispec("16<[ 1001 11 R d(5) r(4) ]", mnemonic="MUL")
@ispec("16<[ 0010 10 R d(5) r(4) ]", mnemonic="OR")
@ispec("16<[ 0000 10 R d(5) r(4) ]", mnemonic="SBC")
@ispec("16<[ 0001 10 R d(5) r(4) ]", mnemonic="SUB")
def avr_default(obj, R, d, r):
    dst, src = env.R[d], env.R[r + (R << 4)]
    obj.operands = [dst, src]
    obj.type = type_data_processing


@ispec("16<[ 0000 0001 d(4) r(4)]", mnemonic="MOVW")
def avr_default(obj, d, r):
    dst = env.R[d << 1]
    src = env.R[r << 1]
    obj.operands = [dst, src]
    obj.misc["d"] = d << 1
    obj.misc["r"] = r << 1
    obj.misc["W"] = (dst, src)
    obj.type = type_data_processing


@ispec("16<[ 1001 0110 K(2) d(2) k(4)]", mnemonic="ADIW")
@ispec("16<[ 1001 0111 K(2) d(2) k(4)]", mnemonic="SBIW")
def avr_default(obj, K, d, k):
    dst = (env.R[24], env.X, env.Y, env.Z)[d]
    if d == 0:
        obj.misc["W"] = (dst,)
    imm = env.cst(k + (K << 4), 16)
    obj.operands = [dst, imm]
    obj.type = type_data_processing


@ispec("16<[ 0111 K(4) d(4) k(4)]", mnemonic="ANDI")
@ispec("16<[ 0011 K(4) d(4) k(4)]", mnemonic="CPI")
@ispec("16<[ 1110 K(4) d(4) k(4)]", mnemonic="LDI")
@ispec("16<[ 0110 K(4) d(4) k(4)]", mnemonic="ORI")
@ispec("16<[ 0100 K(4) d(4) k(4)]", mnemonic="SBCI")
@ispec("16<[ 0110 K(4) d(4) k(4)]", mnemonic="SBR")
@ispec("16<[ 0101 K(4) d(4) k(4)]", mnemonic="SUBI")
def avr_default(obj, K, d, k):
    dst = env.R[16 + d]
    imm = env.cst(k + (K << 4), 8)
    if obj.mnemonic in ("ANDI", "ORI"):
        imm.sf = False
    obj.operands = [dst, imm]
    obj.type = type_data_processing


@ispec("16<[ 1001 010 d(5) 0000]", mnemonic="COM")
@ispec("16<[ 1001 010 d(5) 0001]", mnemonic="NEG")
@ispec("16<[ 1001 010 d(5) 0011]", mnemonic="INC")
@ispec("16<[ 1001 010 d(5) 0101]", mnemonic="ASR")
@ispec("16<[ 1001 010 d(5) 0110]", mnemonic="LSR")
@ispec("16<[ 1001 010 d(5) 0111]", mnemonic="ROR")
@ispec("16<[ 1001 010 d(5) 1010]", mnemonic="DEC")
@ispec("16<[ 1001 000 d(5) 1111]", mnemonic="POP")
@ispec("16<[ 1001 001 d(5) 1111]", mnemonic="PUSH")
@ispec("16<[ 1001 010 d(5) 0010]", mnemonic="SWAP")
def avr_default(obj, d):
    dst = env.R[d]
    obj.operands = [dst]
    obj.type = type_data_processing


@ispec("16<[ 1001 000=s d(5) 1100]", mnemonic="LD", _flg=0)
@ispec("16<[ 1001 000=s d(5) 1101]", mnemonic="LD", _flg=1)
@ispec("16<[ 1001 000=s d(5) 1110]", mnemonic="LD", _flg=-1)
@ispec("16<[ 1001 001=s d(5) 1100]", mnemonic="ST", _flg=0)
@ispec("16<[ 1001 001=s d(5) 1101]", mnemonic="ST", _flg=1)
@ispec("16<[ 1001 001=s d(5) 1110]", mnemonic="ST", _flg=-1)
def avr_ld(obj, s, d, _flg):
    dst = env.R[d]
    obj.operands = [dst, env.X] if s == 0 else [env.X, dst]
    obj.type = type_data_processing
    obj.misc["mem"] = s + 1
    obj.misc["flg"] = _flg


@ispec("32<[ k(16) 1001 000=s d(5) 0000]", mnemonic="LDS")
@ispec("32<[ k(16) 1001 001=s d(5) 0000]", mnemonic="STS")
def avr_ld(obj, s, d, k):
    dst = env.R[d]
    adr = env.cst(k, 16)
    adr.sf = False
    obj.operands = [dst, adr] if s == 0 else [adr, dst]
    obj.misc["mem"] = s + 1
    obj.type = type_data_processing


@ispec("16<[ 1010 0=s ~kh(2) ~ks(1) d(4) ~k(4)]", mnemonic="LDS")
@ispec("16<[ 1010 1=s ~kh(2) ~ks(1) d(4) ~k(4)]", mnemonic="STS")
def avr_ld(obj, s, kh, ks, d, k):
    dst = env.R[16 + d]
    adr = k // kh // ks // ~ks
    adr = env.cst(adr.int(), 16)
    obj.operands = [dst, adr] if s == 0 else [adr, dst]
    obj.misc["mem"] = s + 1
    obj.type = type_data_processing


@ispec("16<[ 1000 000=s d(5) 1000]", mnemonic="LD", _flg=0)
@ispec("16<[ 1001 000=s d(5) 1001]", mnemonic="LD", _flg=1)
@ispec("16<[ 1001 000=s d(5) 1010]", mnemonic="LD", _flg=-1)
@ispec("16<[ 1000 001=s d(5) 1000]", mnemonic="ST", _flg=0)
@ispec("16<[ 1001 001=s d(5) 1001]", mnemonic="ST", _flg=1)
@ispec("16<[ 1001 001=s d(5) 1010]", mnemonic="ST", _flg=-1)
def avr_ld(obj, s, d, _flg):
    dst = env.R[d]
    obj.operands = [dst, env.Y] if s == 0 else [env.Y, dst]
    obj.type = type_data_processing
    obj.misc["mem"] = s + 1
    obj.misc["flg"] = _flg


@ispec("16<[ 10 q 0 qh(2) 0=s d(5) 1 ql(3)]", mnemonic="LDD")
@ispec("16<[ 10 q 0 qh(2) 1=s d(5) 1 ql(3)]", mnemonic="STD")
def avr_ld(obj, q, qh, s, d, ql):
    dst = env.R[d]
    off = env.cst((q << 5) + (qh << 3) + ql, 16)
    obj.operands = [dst, env.Y + off] if s == 0 else [env.Y + off, dst]
    obj.misc["mem"] = s + 1
    obj.type = type_data_processing


@ispec("16<[ 1000 000=s d(5) 0000]", mnemonic="LD", _flg=0)
@ispec("16<[ 1001 000=s d(5) 0001]", mnemonic="LD", _flg=1)
@ispec("16<[ 1001 000=s d(5) 0010]", mnemonic="LD", _flg=-1)
@ispec("16<[ 1001 000=s d(5) 0110]", mnemonic="ELPM", _flg=0)
@ispec("16<[ 1001 000=s d(5) 0111]", mnemonic="ELPM", _flg=1)
@ispec("16<[ 1001 000=s d(5) 0100]", mnemonic="LPM", _flg=0)
@ispec("16<[ 1001 000=s d(5) 0101]", mnemonic="LPM", _flg=1)
@ispec("16<[ 1000 001=s d(5) 0000]", mnemonic="ST", _flg=0)
@ispec("16<[ 1001 001=s d(5) 0001]", mnemonic="ST", _flg=1)
@ispec("16<[ 1001 001=s d(5) 0010]", mnemonic="ST", _flg=-1)
def avr_ld(obj, s, d, _flg):
    dst = env.R[d]
    obj.operands = [dst, env.Z] if s == 0 else [env.Z, dst]
    obj.type = type_data_processing
    obj.misc["mem"] = True
    obj.misc["flg"] = _flg


@ispec("16<[ 10 q 0 q2(2) 0=s d(5) 0 q3(3)]", mnemonic="LDD")
@ispec("16<[ 10 q 0 q2(2) 1=s d(5) 0 q3(3)]", mnemonic="STD")
def avr_ld(obj, q, q2, s, d, q3):
    dst = env.R[d]
    off = env.cst((q << 5) + (q2 << 3) + q3, 16)
    obj.operands = [dst, env.Z + off] if s == 0 else [env.Z + off, dst]
    obj.misc["mem"] = True
    obj.type = type_data_processing


@ispec("16<[ 1001 0100 1 s(3) 1000]", mnemonic="BCLR")
@ispec("16<[ 1001 0100 0 s(3) 1000]", mnemonic="BSET")
def avr_default(obj, s):
    dst = env.SREG[s : s + 1]
    obj.operands = [dst]
    obj.type = type_data_processing


@ispec("16<[ 0000 0011 0 d(3) 0 r(3)]", mnemonic="MULSU")
@ispec("16<[ 0000 0011 0 d(3) 1 r(3)]", mnemonic="FMUL")
@ispec("16<[ 0000 0011 1 d(3) 0 r(3)]", mnemonic="FMULS")
@ispec("16<[ 0000 0011 1 d(3) 1 r(3)]", mnemonic="FMULSU")
def avr_default(obj, d, r):
    dst = env.R[16 + d]
    src = env.R[16 + r]
    obj.operands = [dst, src]
    obj.type = type_data_processing


@ispec("16<[ 0000 0010 d(4) r(4)]", mnemonic="MULS")
def avr_default(obj, d, r):
    dst = env.R[16 + d]
    src = env.R[16 + r]
    obj.operands = [dst, src]
    obj.type = type_data_processing


@ispec("16<[ 1111 100 d(5) 0 b(3)]", mnemonic="BLD")
@ispec("16<[ 1111 101 d(5) 0 b(3)]", mnemonic="BST")
def avr_default(obj, d, b):
    dst = env.R[d]
    obj.operands = [dst[b : b + 1]]
    obj.type = type_data_processing


@ispec("16<[ 1111 110 r(5) 0 b(3)]", mnemonic="SBRC")
@ispec("16<[ 1111 111 r(5) 0 b(3)]", mnemonic="SBRS")
def avr_default(obj, r, b):
    src = env.R[r]
    obj.operands = [src[b : b + 1]]
    obj.type = type_data_processing


@ispec("16<[ 1111 01 ~k(7) s(3)]", mnemonic="BRBC", _cc=env.bit0)
@ispec("16<[ 1111 00 ~k(7) s(3)]", mnemonic="BRBS", _cc=env.bit1)
def avr_brc(obj, k, s, _cc):
    bit = env.SREG[s : s + 1]
    off = env.cst(k.int(-1), 16)
    obj.operands = [bit, off]
    obj.cond = bit == _cc
    obj.type = type_control_flow


@ispec("16<[ 1101 ~k(12)]", mnemonic="RCALL")
@ispec("16<[ 1100 ~k(12)]", mnemonic="RJMP")
def avr_br(obj, k):
    off = env.cst(k.int(-1), 16)
    obj.operands = [off]
    obj.type = type_control_flow


@ispec("16<[ 0000 0000 0000 0000]", mnemonic="NOP", type=type_system)
@ispec("16<[ 1001 0101 1001 1000]", mnemonic="BREAK", type=type_system)
@ispec("16<[ 1001 0101 1010 1000]", mnemonic="WDR", type=type_system)
@ispec("16<[ 1001 0101 1000 1000]", mnemonic="SLEEP", type=type_system)
@ispec("16<[ 1001 0101 1001 1000]", mnemonic="EICALL", type=type_control_flow)
@ispec("16<[ 1001 0100 0001 1001]", mnemonic="EIJMP", type=type_control_flow)
@ispec("16<[ 1001 0101 1101 1000]", mnemonic="ELPM", type=type_data_processing)
@ispec("16<[ 1001 0101 1100 1000]", mnemonic="LPM", type=type_data_processing)
@ispec("16<[ 1001 0101 1110 1000]", mnemonic="SPM", type=type_data_processing)
@ispec("16<[ 1001 0101 1111 1000]", mnemonic="SPM2", type=type_data_processing)
@ispec("16<[ 1001 0101 0000 1001]", mnemonic="ICALL", type=type_control_flow)
@ispec("16<[ 1001 0100 0000 1001]", mnemonic="IJMP", type=type_control_flow)
@ispec("16<[ 1001 0101 0000 1000]", mnemonic="RET", type=type_control_flow)
@ispec("16<[ 1001 0101 0001 1000]", mnemonic="RETI", type=type_control_flow)
def avr_noops(obj):
    obj.operands = []


@ispec("32<[ ~klo(16) 1001 010 ~khi(5) 111 ~k16]", mnemonic="CALL")
@ispec("32<[ ~klo(16) 1001 010 ~khi(5) 110 ~k16]", mnemonic="JMP")
def avr_call(obj, khi, k16, klo):
    adr = env.cst((klo // k16 // khi).int(), 22)
    adr.sf = False
    obj.operands = [adr]
    obj.type = type_control_flow


@ispec("16<[ 1001 1000 a(5) b(3)]", mnemonic="CBI")
@ispec("16<[ 1001 1010 a(5) b(3)]", mnemonic="SBI")
@ispec("16<[ 1001 1001 a(5) b(3)]", mnemonic="SBIC")
@ispec("16<[ 1001 1011 a(5) b(3)]", mnemonic="SBIS")
def avr_io(obj, a, b):
    port = env.cst(a, 5)
    port.sf = False
    obj.operands = [env.cst(a, 5), env.cst(b, 3)]
    obj.type = type_data_processing


@ispec("16<[ 1011 0 A(2) d(5) a(4)]", mnemonic="IN")
def avr_io(obj, A, d, a):
    port = env.cst(a + (A << 4), 8)
    port.sf = False
    obj.operands = [env.R[d], port]
    obj.type = type_other


@ispec("16<[ 1011 1 A(2) r(5) a(4)]", mnemonic="OUT")
def avr_io(obj, A, r, a):
    port = env.cst(a + (A << 4), 8)
    port.sf = False
    obj.operands = [port, env.R[r]]
    obj.type = type_other
