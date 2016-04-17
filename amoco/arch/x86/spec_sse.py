# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.

from .utils import *

#------------------------------------------------------
# amoco SSE instruction specs:
#------------------------------------------------------

ISPECS = []

# NO pfx:
# -------

# (PACKED SINGLE)
# xmm, xmm/m128
@ispec_ia32("*>[ {0f}{10} /r ]", mnemonic="MOVUPS")
@ispec_ia32("*>[ {0f}{14} /r ]", mnemonic="UNPCKLPS")
@ispec_ia32("*>[ {0f}{15} /r ]", mnemonic="UNPCKHPS")
@ispec_ia32("*>[ {0f}{28} /r ]", mnemonic="MOVAPS")
@ispec_ia32("*>[ {0f}{51} /r ]", mnemonic="SQRTPS")
@ispec_ia32("*>[ {0f}{52} /r ]", mnemonic="RSQRTPS")
@ispec_ia32("*>[ {0f}{53} /r ]", mnemonic="RCPPS")
@ispec_ia32("*>[ {0f}{54} /r ]", mnemonic="ANDPS")
@ispec_ia32("*>[ {0f}{55} /r ]", mnemonic="ANDNPS")
@ispec_ia32("*>[ {0f}{56} /r ]", mnemonic="ORPS")
@ispec_ia32("*>[ {0f}{57} /r ]", mnemonic="XORPS")
@ispec_ia32("*>[ {0f}{58} /r ]", mnemonic="ADDPS")
@ispec_ia32("*>[ {0f}{59} /r ]", mnemonic="MULPS")
@ispec_ia32("*>[ {0f}{5b} /r ]", mnemonic="CVTDQ2PS")
@ispec_ia32("*>[ {0f}{5c} /r ]", mnemonic="SUBPS")
@ispec_ia32("*>[ {0f}{5d} /r ]", mnemonic="MINPS")
@ispec_ia32("*>[ {0f}{5e} /r ]", mnemonic="DIVPS")
@ispec_ia32("*>[ {0f}{5f} /r ]", mnemonic="MAXPS")
def sse_ps(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# xmm/mmx, xmm/m64
@ispec_ia32("*>[ {0f}{5a} /r ]", mnemonic="CVTPS2PD", _op1sz=128)
@ispec_ia32("*>[ {0f}{2c} /r ]", mnemonic="CVTTPS2PI", _op1sz=64)
@ispec_ia32("*>[ {0f}{2d} /r ]", mnemonic="CVTPS2PI", _op1sz=64)
def sse_ps(obj,Mod,REG,RM,data,_op1sz):
    if not check_nopfx(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = 64
    op1 = env.getreg(REG,_op1sz)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# xmm, mmx/m64
@ispec_ia32("*>[ {0f}{2a} /r ]", mnemonic="CVTPI2PS")
def sse_ps(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# inverted form:
# xmm/m128, xmm
@ispec_ia32("*>[ {0f}{11} /r ]", mnemonic="MOVUPS")
@ispec_ia32("*>[ {0f}{29} /r ]", mnemonic="MOVAPS")
def sse_ps(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op2,op1]
    obj.type = type_data_processing

# (PACKED SINGLE with ib)
# xmm, xmm/m128, imm8
@ispec_ia32("*>[ {0f}{c2} /r ]", mnemonic="CMPPS")
@ispec_ia32("*>[ {0f}{c6} /r ]", mnemonic="SHUFPS")
def sse_ps(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op1,op2]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# (SCALAR SINGLE)

# xmm, xmm/m32
@ispec_ia32("*>[ {0f}{2e} /r ]", mnemonic="UCOMISS")
@ispec_ia32("*>[ {0f}{2f} /r ]", mnemonic="COMISS")
def sse_ps(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = 32
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# mmx, mmx
@ispec_ia32("*>[ {0f}{f7} /r ]", mnemonic="MASKMOVQ")
def sse_ps(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_reg: raise InstructionError(obj)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# moves:

# mmx, r/m32
# r/m32, mmx
@ispec_ia32("*>[ {0f}{6e} /r ]", mnemonic="MOVD", _inv=False)
@ispec_ia32("*>[ {0f}{7e} /r ]", mnemonic="MOVD", _inv=True)
def sse_pd(obj,Mod,REG,RM,data, _inv):
    if not check_nopfx(obj,set_opdsz_32): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,64)
    obj.operands = [op1,op2] if not _inv else [op2,op1]
    obj.type = type_data_processing

# mmx, mmx/m64
@ispec_ia32("*>[ {0f}{38}{00} /r ]", mnemonic="PSHUFB")
@ispec_ia32("*>[ {0f}{38}{01} /r ]", mnemonic="PHADDW")
@ispec_ia32("*>[ {0f}{38}{02} /r ]", mnemonic="PHADDD")
@ispec_ia32("*>[ {0f}{38}{03} /r ]", mnemonic="PHADDSW")
@ispec_ia32("*>[ {0f}{38}{04} /r ]", mnemonic="PMADDUBSW")
@ispec_ia32("*>[ {0f}{38}{05} /r ]", mnemonic="PHSUBW")
@ispec_ia32("*>[ {0f}{38}{06} /r ]", mnemonic="PHSUBD")
@ispec_ia32("*>[ {0f}{38}{07} /r ]", mnemonic="PHSUBSW")
@ispec_ia32("*>[ {0f}{38}{08} /r ]", mnemonic="PSIGNB")
@ispec_ia32("*>[ {0f}{38}{09} /r ]", mnemonic="PSIGNW")
@ispec_ia32("*>[ {0f}{38}{0a} /r ]", mnemonic="PSIGND")
@ispec_ia32("*>[ {0f}{38}{0b} /r ]", mnemonic="PMULHRSW")
@ispec_ia32("*>[ {0f}{38}{1c} /r ]", mnemonic="PABSB")
@ispec_ia32("*>[ {0f}{38}{1d} /r ]", mnemonic="PABSW")
@ispec_ia32("*>[ {0f}{38}{1e} /r ]", mnemonic="PABSD")
@ispec_ia32("*>[ {0f}{60} /r ]", mnemonic="PUNPCKLBW")
@ispec_ia32("*>[ {0f}{61} /r ]", mnemonic="PUNPCKLWD")
@ispec_ia32("*>[ {0f}{62} /r ]", mnemonic="PUNPCKLDQ")
@ispec_ia32("*>[ {0f}{63} /r ]", mnemonic="PACKSSWB")
@ispec_ia32("*>[ {0f}{64} /r ]", mnemonic="PCMPGTB")
@ispec_ia32("*>[ {0f}{65} /r ]", mnemonic="PCMPGTW")
@ispec_ia32("*>[ {0f}{66} /r ]", mnemonic="PCMPGTD")
@ispec_ia32("*>[ {0f}{67} /r ]", mnemonic="PACKUSWB")
@ispec_ia32("*>[ {0f}{68} /r ]", mnemonic="PUNPCKHBW")
@ispec_ia32("*>[ {0f}{69} /r ]", mnemonic="PUNPCKHWD")
@ispec_ia32("*>[ {0f}{6a} /r ]", mnemonic="PUNPCKHDQ")
@ispec_ia32("*>[ {0f}{6b} /r ]", mnemonic="PACKSSDW")
@ispec_ia32("*>[ {0f}{6f} /r ]", mnemonic="MOVQ")
@ispec_ia32("*>[ {0f}{74} /r ]", mnemonic="PCMPEQB")
@ispec_ia32("*>[ {0f}{75} /r ]", mnemonic="PCMPEQW")
@ispec_ia32("*>[ {0f}{76} /r ]", mnemonic="PCMPEQD")
@ispec_ia32("*>[ {0f}{d1} /r ]", mnemonic="PSRLW")
@ispec_ia32("*>[ {0f}{d2} /r ]", mnemonic="PSRLD")
@ispec_ia32("*>[ {0f}{d3} /r ]", mnemonic="PSRLQ")
@ispec_ia32("*>[ {0f}{d5} /r ]", mnemonic="PMULLW")
@ispec_ia32("*>[ {0f}{d8} /r ]", mnemonic="PSUBUSB")
@ispec_ia32("*>[ {0f}{d9} /r ]", mnemonic="PSUBUSW")
@ispec_ia32("*>[ {0f}{da} /r ]", mnemonic="PMINUB")
@ispec_ia32("*>[ {0f}{db} /r ]", mnemonic="PAND")
@ispec_ia32("*>[ {0f}{dc} /r ]", mnemonic="PADDUSB")
@ispec_ia32("*>[ {0f}{dd} /r ]", mnemonic="PADDUSW")
@ispec_ia32("*>[ {0f}{de} /r ]", mnemonic="PMAXUB")
@ispec_ia32("*>[ {0f}{df} /r ]", mnemonic="PANDN")
@ispec_ia32("*>[ {0f}{e0} /r ]", mnemonic="PAVGB")
@ispec_ia32("*>[ {0f}{e1} /r ]", mnemonic="PSRAW")
@ispec_ia32("*>[ {0f}{e2} /r ]", mnemonic="PSRAD")
@ispec_ia32("*>[ {0f}{e3} /r ]", mnemonic="PAVGW")
@ispec_ia32("*>[ {0f}{e4} /r ]", mnemonic="PMULHUW")
@ispec_ia32("*>[ {0f}{e5} /r ]", mnemonic="PMULHW")
@ispec_ia32("*>[ {0f}{e8} /r ]", mnemonic="PSUBSB")
@ispec_ia32("*>[ {0f}{e9} /r ]", mnemonic="PSUBSW")
@ispec_ia32("*>[ {0f}{ea} /r ]", mnemonic="PMINSW")
@ispec_ia32("*>[ {0f}{eb} /r ]", mnemonic="POR")
@ispec_ia32("*>[ {0f}{ec} /r ]", mnemonic="PADDSB")
@ispec_ia32("*>[ {0f}{ed} /r ]", mnemonic="PADDSW")
@ispec_ia32("*>[ {0f}{ee} /r ]", mnemonic="PMAXSW")
@ispec_ia32("*>[ {0f}{ef} /r ]", mnemonic="PXOR")
@ispec_ia32("*>[ {0f}{f1} /r ]", mnemonic="PSLLW")
@ispec_ia32("*>[ {0f}{f2} /r ]", mnemonic="PSLLD")
@ispec_ia32("*>[ {0f}{f3} /r ]", mnemonic="PSLLQ")
@ispec_ia32("*>[ {0f}{f4} /r ]", mnemonic="PMULUDQ")
@ispec_ia32("*>[ {0f}{f5} /r ]", mnemonic="PMADDWD")
@ispec_ia32("*>[ {0f}{f6} /r ]", mnemonic="PSADBW")
@ispec_ia32("*>[ {0f}{f8} /r ]", mnemonic="PSUBB")
@ispec_ia32("*>[ {0f}{f9} /r ]", mnemonic="PSUBW")
@ispec_ia32("*>[ {0f}{fa} /r ]", mnemonic="PSUBD")
@ispec_ia32("*>[ {0f}{fb} /r ]", mnemonic="PSUBQ")
@ispec_ia32("*>[ {0f}{fc} /r ]", mnemonic="PADDB")
@ispec_ia32("*>[ {0f}{fd} /r ]", mnemonic="PADDW")
@ispec_ia32("*>[ {0f}{fe} /r ]", mnemonic="PADDD")
@ispec_ia32("*>[ {0f}{d4} /r ]", mnemonic="PADDQ")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,64)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# mmx, imm8
@ispec_ia32("*>[ {0f}{71} /2 ]", mnemonic="PSRLW")
@ispec_ia32("*>[ {0f}{71} /4 ]", mnemonic="PSRAW")
@ispec_ia32("*>[ {0f}{71} /6 ]", mnemonic="PSLLW")
@ispec_ia32("*>[ {0f}{72} /2 ]", mnemonic="PSRLD")
@ispec_ia32("*>[ {0f}{72} /4 ]", mnemonic="PSRAD")
@ispec_ia32("*>[ {0f}{72} /6 ]", mnemonic="PSLLD")
@ispec_ia32("*>[ {0f}{73} /2 ]", mnemonic="PSRLQ")
@ispec_ia32("*>[ {0f}{73} /6 ]", mnemonic="PSLLQ")
def sse_pd(obj,Mod,RM,data):
    if not check_nopfx(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    obj.operands = [op2]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# mmx, mmx/m64, imm8
@ispec_ia32("*>[ {0f}{70} /r ]", mnemonic="PSHUFW")
@ispec_ia32("*>[ {0f}{3a}{0f} /r ]", mnemonic="PALIGNR")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,64)
    obj.operands = [op1,op2]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# mmx, r32/m16, imm8
@ispec_ia32("*>[ {0f}{c4} /r ]", mnemonic="PINSRW")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_32): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = 16
    op1 = env.getreg(REG,64)
    obj.operands = [op1,op2]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# r32, mmx, imm8
@ispec_ia32("*>[ {0f}{c5} /r ]", mnemonic="PEXTRW")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: raise InstructionError(obj)
    op1 = env.getreg(REG,32)
    obj.operands = [op1,op2]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# inverted operands:
# mmx/m64, mmx
@ispec_ia32("*>[ {0f}{7f} /r ]", mnemonic="MOVQ")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,64)
    obj.operands = [op2,op1]
    obj.type = type_data_processing

# xmm, xmm
@ispec_ia32("*>[ {0f}{12} /r ]", mnemonic="MOVHLPS")
@ispec_ia32("*>[ {0f}{16} /r ]", mnemonic="MOVLHPS")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_reg: raise InstructionError(obj)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# xmm, m64
# m64, xmm
@ispec_ia32("*>[ {0f}{12} /r ]", mnemonic="MOVLPS", _inv=False)
@ispec_ia32("*>[ {0f}{13} /r ]", mnemonic="MOVLPS", _inv=True)
@ispec_ia32("*>[ {0f}{16} /r ]", mnemonic="MOVHPS", _inv=False)
@ispec_ia32("*>[ {0f}{17} /r ]", mnemonic="MOVHPS", _inv=True)
def sse_pd(obj,Mod,REG,RM,data,_inv):
    if not check_nopfx(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_mem: raise InstructionError(obj)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2] if not _inv else [op2, op1]
    obj.type = type_data_processing

# r32, xmm
@ispec_ia32("*>[ {0f}{50} /r ]", mnemonic="MOVMSKPS")
@ispec_ia32("*>[ {0f}{d7} /r ]", mnemonic="PMOVMSKB")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_nopfx(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_reg: raise InstructionError(obj)
    op1 = env.getreg(REG,32)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# xmm, m128
@ispec_ia32("*>[ {0f}{2b} /r ]", mnemonic="MOVNTPS",  _inv=True)
def sse_pd(obj,Mod,REG,RM,data,_inv):
    if not check_nopfx(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_mem: raise InstructionError(obj)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2] if not _inv else [op2,op1]
    obj.type = type_data_processing

# mmx, m64
@ispec_ia32("*>[ {0f}{e7} /r ]", mnemonic="MOVNTQ",  _inv=True)
def sse_pd(obj,Mod,REG,RM,data,_inv):
    if not check_nopfx(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_mem: raise InstructionError(obj)
    op1 = env.getreg(REG,64)
    obj.operands = [op1,op2] if not _inv else [op2,op1]
    obj.type = type_data_processing

# F2 prefixed:
# ------------

# xmm, xmm/m128
@ispec_ia32("*>[ {0f}{7c} /r ]", mnemonic="HADDPS")
@ispec_ia32("*>[ {0f}{7d} /r ]", mnemonic="HSUBPS")
@ispec_ia32("*>[ {0f}{e6} /r ]", mnemonic="CVTPD2DQ")
def sse_ps(obj,Mod,REG,RM,data):
    if not check_f2(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# (SCALAR DOUBLE)
# xmm, xmm/m64
@ispec_ia32("*>[ {0f}{10} /r ]", mnemonic="MOVSD")
@ispec_ia32("*>[ {0f}{12} /r ]", mnemonic="MOVDDUP")
@ispec_ia32("*>[ {0f}{51} /r ]", mnemonic="SQRTSD")
@ispec_ia32("*>[ {0f}{58} /r ]", mnemonic="ADDSD")
@ispec_ia32("*>[ {0f}{59} /r ]", mnemonic="MULSD")
@ispec_ia32("*>[ {0f}{5a} /r ]", mnemonic="CVTSD2SS")
@ispec_ia32("*>[ {0f}{5c} /r ]", mnemonic="SUBSD")
@ispec_ia32("*>[ {0f}{5d} /r ]", mnemonic="MINSD")
@ispec_ia32("*>[ {0f}{5e} /r ]", mnemonic="DIVSD")
@ispec_ia32("*>[ {0f}{5f} /r ]", mnemonic="MAXSD")
@ispec_ia32("*>[ {0f}{d0} /r ]", mnemonic="ADDSUBPS") # verified
def sse_sd(obj,Mod,REG,RM,data):
    if not check_f2(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = 64
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# SD inverted operands:
# xmm/m64, xmm
@ispec_ia32("*>[ {0f}{11} /r ]", mnemonic="MOVSD")
def sse_sd(obj,Mod,REG,RM,data):
    if not check_f2(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = 64
    op1 = env.getreg(REG,128)
    obj.operands = [op2,op1]
    obj.type = type_data_processing

# r32, xmm/m64
@ispec_ia32("*>[ {0f}{2c} /r ]", mnemonic="CVTTSD2SI")
@ispec_ia32("*>[ {0f}{2d} /r ]", mnemonic="CVTSD2SI")
def sse_sd(obj,Mod,REG,RM,data):
    if not check_f2(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = 64
    op1 = env.getreg(REG,32)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# xmm, r/m32
@ispec_ia32("*>[ {0f}{2a} /r ]", mnemonic="CVTSI2SD")
def sse_sd(obj,Mod,REG,RM,data):
    if not check_f2(obj,set_opdsz_32): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# (SCALAR DOUBLE with ib)
@ispec_ia32("*>[ {0f}{70} /r ]", mnemonic="PSHUFLW")
@ispec_ia32("*>[ {0f}{c2} /r ]", mnemonic="CMPSD")
def sse_sd(obj,Mod,REG,RM,data):
    if not check_f2(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem and obj.mnemonic=='CMPSD': op2.size = 64
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# xmm, m128
@ispec_ia32("*>[ {0f}{f0} /r ]", mnemonic="LDDQU")
def sse_sd(obj,Mod,REG,RM,data):
    if not check_f2(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_mem: raise InstructionError(obj)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# mmx, xmm
@ispec_ia32("*>[ {0f}{d6} /r ]", mnemonic="MOVDQ2Q")
def sse_sd(obj,Mod,REG,RM,data):
    if not check_f2(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_reg: raise InstructionError(obj)
    op1 = env.getreg(REG,64)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# F3 prefixed:
# ------------

# (SCALAR SINGLE)
# xmm, xmm/m32
@ispec_ia32("*>[ {0f}{10} /r ]", mnemonic="MOVSS")
@ispec_ia32("*>[ {0f}{51} /r ]", mnemonic="SQRTSS")
@ispec_ia32("*>[ {0f}{52} /r ]", mnemonic="RSQRTSS")
@ispec_ia32("*>[ {0f}{53} /r ]", mnemonic="RCPSS")
@ispec_ia32("*>[ {0f}{58} /r ]", mnemonic="ADDSS")
@ispec_ia32("*>[ {0f}{59} /r ]", mnemonic="MULSS")
@ispec_ia32("*>[ {0f}{5c} /r ]", mnemonic="SUBSS")
@ispec_ia32("*>[ {0f}{5d} /r ]", mnemonic="MINSS")
@ispec_ia32("*>[ {0f}{5e} /r ]", mnemonic="DIVSS")
@ispec_ia32("*>[ {0f}{5f} /r ]", mnemonic="MAXSS")
def sse_ss(obj,Mod,REG,RM,data):
    if not check_f3(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = 32
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# SS inverted operands:
# xmm/m32, xmm
@ispec_ia32("*>[ {0f}{11} /r ]", mnemonic="MOVSS")
def sse_ss(obj,Mod,REG,RM,data):
    if not check_f3(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = 32
    op1 = env.getreg(REG,128)
    obj.operands = [op2,op1]
    obj.type = type_data_processing

# (SCALAR SINGLE with ib)
# xmm, xmm/m128/m32, imm8
@ispec_ia32("*>[ {0f}{70} /r ]", mnemonic="PSHUFHW")
@ispec_ia32("*>[ {0f}{c2} /r ]", mnemonic="CMPSS")
def sse_ss(obj,Mod,REG,RM,data):
    if not check_f3(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem and obj.mnemonic=='CMPSS': op2.size = 32
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# xmm, xmm/m64/m32
@ispec_ia32("*>[ {0f}{e6} /r ]", mnemonic="CVTDQ2PD", _op2sz=64)
@ispec_ia32("*>[ {0f}{7e} /r ]", mnemonic="MOVQ", _op2sz=64)
@ispec_ia32("*>[ {0f}{5a} /r ]", mnemonic="CVTSS2SD",_op2sz=32)
def sse_pd(obj,Mod,REG,RM,data,_op2sz):
    if not check_f3(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = _op2sz
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# xmm, xmm/m128
# xmm/m128, xmm
@ispec_ia32("*>[ {0f}{16} /r ]", mnemonic="MOVSHDUP", _inv=False)
@ispec_ia32("*>[ {0f}{12} /r ]", mnemonic="MOVSLDUP", _inv=False)
@ispec_ia32("*>[ {0f}{5b} /r ]", mnemonic="CVTTPS2DQ", _inv=False)
@ispec_ia32("*>[ {0f}{6f} /r ]", mnemonic="MOVDQU", _inv=False)
@ispec_ia32("*>[ {0f}{7f} /r ]", mnemonic="MOVDQU", _inv=True)
def sse_pd(obj,Mod,REG,RM,data, _inv):
    if not check_f3(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2] if not _inv else [op2,op1]
    obj.type = type_data_processing

# xmm, mmx
@ispec_ia32("*>[ {0f}{d6} /r ]", mnemonic="MOVQ2DQ")
def sse_sd(obj,Mod,REG,RM,data):
    if not check_f3(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_reg: raise InstructionError(obj)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# xmm, r/m32
@ispec_ia32("*>[ {0f}{2a} /r ]", mnemonic="CVTSI2SS")
def sse_sd(obj,Mod,REG,RM,data):
    if not check_f3(obj,set_opdsz_32): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# r32, xmm/m32
@ispec_ia32("*>[ {0f}{2c} /r ]", mnemonic="CVTTSS2SI")
@ispec_ia32("*>[ {0f}{2d} /r ]", mnemonic="CVTSS2SI")
def sse_sd(obj,Mod,REG,RM,data):
    if not check_f3(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = 32
    op1 = env.getreg(REG,32)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# 66 prefixed :
# -------------
# Note that thos specs MUST APPEAR AFTER f2/f3 prefixes which have priority over 66,
# so that 66-related specs will be matched after identical f2/f3 specs

# (PACKED DOUBLE)
# xmm, xmm/m128
@ispec_ia32("*>[ {0f}{10} /r ]", mnemonic="MOVUPD")
@ispec_ia32("*>[ {0f}{14} /r ]", mnemonic="UNPCKLPD")
@ispec_ia32("*>[ {0f}{15} /r ]", mnemonic="UNPCKHPD")
@ispec_ia32("*>[ {0f}{28} /r ]", mnemonic="MOVAPD")
@ispec_ia32("*>[ {0f}{51} /r ]", mnemonic="SQRTPD")
@ispec_ia32("*>[ {0f}{57} /r ]", mnemonic="XORPD")
@ispec_ia32("*>[ {0f}{58} /r ]", mnemonic="ADDPD")
@ispec_ia32("*>[ {0f}{54} /r ]", mnemonic="ANDPD")
@ispec_ia32("*>[ {0f}{55} /r ]", mnemonic="ANDNPD")
@ispec_ia32("*>[ {0f}{56} /r ]", mnemonic="ORPD")
@ispec_ia32("*>[ {0f}{59} /r ]", mnemonic="MULPD")
@ispec_ia32("*>[ {0f}{5a} /r ]", mnemonic="CVTPD2PS")
@ispec_ia32("*>[ {0f}{5b} /r ]", mnemonic="CVTPS2DQ")
@ispec_ia32("*>[ {0f}{5c} /r ]", mnemonic="SUBPD")
@ispec_ia32("*>[ {0f}{5d} /r ]", mnemonic="MINPD")
@ispec_ia32("*>[ {0f}{5e} /r ]", mnemonic="DIVPD")
@ispec_ia32("*>[ {0f}{5f} /r ]", mnemonic="MAXPD")
@ispec_ia32("*>[ {0f}{60} /r ]", mnemonic="PUNPCKLBW")
@ispec_ia32("*>[ {0f}{61} /r ]", mnemonic="PUNPCKLWD")
@ispec_ia32("*>[ {0f}{62} /r ]", mnemonic="PUNPCKLDQ")
@ispec_ia32("*>[ {0f}{63} /r ]", mnemonic="PACKSSWB")
@ispec_ia32("*>[ {0f}{64} /r ]", mnemonic="PCMPGTB")
@ispec_ia32("*>[ {0f}{65} /r ]", mnemonic="PCMPGTW")
@ispec_ia32("*>[ {0f}{66} /r ]", mnemonic="PCMPGTD")
@ispec_ia32("*>[ {0f}{67} /r ]", mnemonic="PACKUSWB")
@ispec_ia32("*>[ {0f}{68} /r ]", mnemonic="PUNPCKHBW")
@ispec_ia32("*>[ {0f}{69} /r ]", mnemonic="PUNPCKHWD")
@ispec_ia32("*>[ {0f}{6a} /r ]", mnemonic="PUNPCKHDQ")
@ispec_ia32("*>[ {0f}{6b} /r ]", mnemonic="PACKSSDW")
@ispec_ia32("*>[ {0f}{6c} /r ]", mnemonic="PUNPCKLQDQ")
@ispec_ia32("*>[ {0f}{6d} /r ]", mnemonic="PUNPCKHQDQ")
@ispec_ia32("*>[ {0f}{6f} /r ]", mnemonic="MOVDQA")
@ispec_ia32("*>[ {0f}{74} /r ]", mnemonic="PCMPEQB")
@ispec_ia32("*>[ {0f}{75} /r ]", mnemonic="PCMPEQW")
@ispec_ia32("*>[ {0f}{76} /r ]", mnemonic="PCMPEQD")
@ispec_ia32("*>[ {0f}{7c} /r ]", mnemonic="HADDPD")
@ispec_ia32("*>[ {0f}{7d} /r ]", mnemonic="HSUBPD")
@ispec_ia32("*>[ {0f}{d0} /r ]", mnemonic="ADDSUBPD")
@ispec_ia32("*>[ {0f}{d1} /r ]", mnemonic="PSRLW")
@ispec_ia32("*>[ {0f}{d2} /r ]", mnemonic="PSRLD")
@ispec_ia32("*>[ {0f}{d3} /r ]", mnemonic="PSRLQ")
@ispec_ia32("*>[ {0f}{d4} /r ]", mnemonic="PADDQ")
@ispec_ia32("*>[ {0f}{d5} /r ]", mnemonic="PMULLW")
@ispec_ia32("*>[ {0f}{d8} /r ]", mnemonic="PSUBUSB")
@ispec_ia32("*>[ {0f}{d9} /r ]", mnemonic="PSUBUSW")
@ispec_ia32("*>[ {0f}{da} /r ]", mnemonic="PMINUB")
@ispec_ia32("*>[ {0f}{db} /r ]", mnemonic="PAND")
@ispec_ia32("*>[ {0f}{dc} /r ]", mnemonic="PADDUSB")
@ispec_ia32("*>[ {0f}{dd} /r ]", mnemonic="PADDUSW")
@ispec_ia32("*>[ {0f}{de} /r ]", mnemonic="PMAXUB")
@ispec_ia32("*>[ {0f}{df} /r ]", mnemonic="PANDN")
@ispec_ia32("*>[ {0f}{e0} /r ]", mnemonic="PAVGB")
@ispec_ia32("*>[ {0f}{e1} /r ]", mnemonic="PSRAW")
@ispec_ia32("*>[ {0f}{e2} /r ]", mnemonic="PSRAD")
@ispec_ia32("*>[ {0f}{e3} /r ]", mnemonic="PAVGW")
@ispec_ia32("*>[ {0f}{e4} /r ]", mnemonic="PMULHUW")
@ispec_ia32("*>[ {0f}{e5} /r ]", mnemonic="PMULHW")
@ispec_ia32("*>[ {0f}{e6} /r ]", mnemonic="CVTTPD2DQ")
@ispec_ia32("*>[ {0f}{e8} /r ]", mnemonic="PSUBSB")
@ispec_ia32("*>[ {0f}{e9} /r ]", mnemonic="PSUBSW")
@ispec_ia32("*>[ {0f}{ea} /r ]", mnemonic="PMINSW")
@ispec_ia32("*>[ {0f}{eb} /r ]", mnemonic="POR")
@ispec_ia32("*>[ {0f}{ec} /r ]", mnemonic="PADDSB")
@ispec_ia32("*>[ {0f}{ed} /r ]", mnemonic="PADDSW")
@ispec_ia32("*>[ {0f}{ee} /r ]", mnemonic="PMAXSW")
@ispec_ia32("*>[ {0f}{ef} /r ]", mnemonic="PXOR")
@ispec_ia32("*>[ {0f}{f1} /r ]", mnemonic="PSLLW")
@ispec_ia32("*>[ {0f}{f2} /r ]", mnemonic="PSLLD")
@ispec_ia32("*>[ {0f}{f3} /r ]", mnemonic="PSLLQ")
@ispec_ia32("*>[ {0f}{f4} /r ]", mnemonic="PMULUDQ")
@ispec_ia32("*>[ {0f}{f5} /r ]", mnemonic="PMADDWD")
@ispec_ia32("*>[ {0f}{f6} /r ]", mnemonic="PSADBW")
@ispec_ia32("*>[ {0f}{f8} /r ]", mnemonic="PSUBB")
@ispec_ia32("*>[ {0f}{f9} /r ]", mnemonic="PSUBW")
@ispec_ia32("*>[ {0f}{fa} /r ]", mnemonic="PSUBD")
@ispec_ia32("*>[ {0f}{fb} /r ]", mnemonic="PSUBQ")
@ispec_ia32("*>[ {0f}{fc} /r ]", mnemonic="PADDB")
@ispec_ia32("*>[ {0f}{fd} /r ]", mnemonic="PADDW")
@ispec_ia32("*>[ {0f}{fe} /r ]", mnemonic="PADDD")
@ispec_ia32("*>[ {0f}{38}{00} /r ]", mnemonic="PSHUFB")
@ispec_ia32("*>[ {0f}{38}{01} /r ]", mnemonic="PHADDW")
@ispec_ia32("*>[ {0f}{38}{02} /r ]", mnemonic="PHADDD")
@ispec_ia32("*>[ {0f}{38}{03} /r ]", mnemonic="PHADDSW")
@ispec_ia32("*>[ {0f}{38}{04} /r ]", mnemonic="PMADDUBSW")
@ispec_ia32("*>[ {0f}{38}{05} /r ]", mnemonic="PHSUBW")
@ispec_ia32("*>[ {0f}{38}{06} /r ]", mnemonic="PHSUBD")
@ispec_ia32("*>[ {0f}{38}{07} /r ]", mnemonic="PHSUBSW")
@ispec_ia32("*>[ {0f}{38}{08} /r ]", mnemonic="PSIGNB")
@ispec_ia32("*>[ {0f}{38}{09} /r ]", mnemonic="PSIGNW")
@ispec_ia32("*>[ {0f}{38}{0a} /r ]", mnemonic="PSIGND")
@ispec_ia32("*>[ {0f}{38}{0b} /r ]", mnemonic="PMULHRSW")
@ispec_ia32("*>[ {0f}{38}{10} /r ]", mnemonic="PBLENDVB")
@ispec_ia32("*>[ {0f}{38}{14} /r ]", mnemonic="BLENDVPS") # verified
@ispec_ia32("*>[ {0f}{38}{15} /r ]", mnemonic="BLENDVPD")
@ispec_ia32("*>[ {0f}{38}{17} /r ]", mnemonic="PTEST")
@ispec_ia32("*>[ {0f}{38}{1c} /r ]", mnemonic="PABSB")
@ispec_ia32("*>[ {0f}{38}{1d} /r ]", mnemonic="PABSW")
@ispec_ia32("*>[ {0f}{38}{1e} /r ]", mnemonic="PABSD")
@ispec_ia32("*>[ {0f}{38}{28} /r ]", mnemonic="PMULDQ")
@ispec_ia32("*>[ {0f}{38}{29} /r ]", mnemonic="PCMPEQQ")
@ispec_ia32("*>[ {0f}{38}{2b} /r ]", mnemonic="PACKUSDW")
@ispec_ia32("*>[ {0f}{38}{37} /r ]", mnemonic="PCMPGTQ")
@ispec_ia32("*>[ {0f}{38}{38} /r ]", mnemonic="PMINSB")
@ispec_ia32("*>[ {0f}{38}{39} /r ]", mnemonic="PMINSD")
@ispec_ia32("*>[ {0f}{38}{3a} /r ]", mnemonic="PMINUW")
@ispec_ia32("*>[ {0f}{38}{3b} /r ]", mnemonic="PMINUD")
@ispec_ia32("*>[ {0f}{38}{3c} /r ]", mnemonic="PMAXSB")
@ispec_ia32("*>[ {0f}{38}{3d} /r ]", mnemonic="PMAXSD")
@ispec_ia32("*>[ {0f}{38}{3e} /r ]", mnemonic="PMAXUW")
@ispec_ia32("*>[ {0f}{38}{3f} /r ]", mnemonic="PMAXUD")
@ispec_ia32("*>[ {0f}{38}{40} /r ]", mnemonic="PMULLD")
@ispec_ia32("*>[ {0f}{38}{41} /r ]", mnemonic="PHMINPOSUW")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_66(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# xmm, xmm/m(64/32/16)
@ispec_ia32("*>[ {0f}{38}{20} /r ]", mnemonic="PMOVSXBW", _op2sz=64)
@ispec_ia32("*>[ {0f}{38}{21} /r ]", mnemonic="PMOVSXBD", _op2sz=32)
@ispec_ia32("*>[ {0f}{38}{22} /r ]", mnemonic="PMOVSXBQ", _op2sz=16)
@ispec_ia32("*>[ {0f}{38}{23} /r ]", mnemonic="PMOVSXWD", _op2sz=64)
@ispec_ia32("*>[ {0f}{38}{24} /r ]", mnemonic="PMOVSXWQ", _op2sz=32)
@ispec_ia32("*>[ {0f}{38}{25} /r ]", mnemonic="PMOVSXDQ", _op2sz=64)
@ispec_ia32("*>[ {0f}{38}{30} /r ]", mnemonic="PMOVZXBW", _op2sz=64)
@ispec_ia32("*>[ {0f}{38}{31} /r ]", mnemonic="PMOVZXBD", _op2sz=32)
@ispec_ia32("*>[ {0f}{38}{32} /r ]", mnemonic="PMOVZXBQ", _op2sz=16)
@ispec_ia32("*>[ {0f}{38}{33} /r ]", mnemonic="PMOVZXWD", _op2sz=64)
@ispec_ia32("*>[ {0f}{38}{34} /r ]", mnemonic="PMOVZXWQ", _op2sz=32)
@ispec_ia32("*>[ {0f}{38}{35} /r ]", mnemonic="PMOVZXDQ", _op2sz=64)
def sse_pd(obj,Mod,REG,RM,data, _op2sz):
    if not check_66(obj,set_opdz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = _op2sz
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# PD instructions with inverted operands :
# xmm/m128, xmm
@ispec_ia32("*>[ {0f}{11} /r ]", mnemonic="MOVUPD")
@ispec_ia32("*>[ {0f}{29} /r ]", mnemonic="MOVAPD")
@ispec_ia32("*>[ {0f}{7f} /r ]", mnemonic="MOVDQA")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_66(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op2,op1]
    obj.type = type_data_processing

# (PACKED DOUBLE with ib)
# xmm, xmm/m128, imm8
@ispec_ia32("*>[ {0f}{70} /r ]", mnemonic="PSHUFD")
@ispec_ia32("*>[ {0f}{c2} /r ]", mnemonic="CMPPD")
@ispec_ia32("*>[ {0f}{c6} /r ]", mnemonic="SHUFPD")
@ispec_ia32("*>[ {0f}{3a}{08} /r ]", mnemonic="ROUNDPS") # verified
@ispec_ia32("*>[ {0f}{3a}{09} /r ]", mnemonic="ROUNDPD") # verified
@ispec_ia32("*>[ {0f}{3a}{0a} /r ]", mnemonic="ROUNDSS") # verified
@ispec_ia32("*>[ {0f}{3a}{0b} /r ]", mnemonic="ROUNDSD") # verified
@ispec_ia32("*>[ {0f}{3a}{0c} /r ]", mnemonic="BLENDPS") # verified
@ispec_ia32("*>[ {0f}{3a}{0d} /r ]", mnemonic="BLENDPD")
@ispec_ia32("*>[ {0f}{3a}{0e} /r ]", mnemonic="PBLENDW")
@ispec_ia32("*>[ {0f}{3a}{0f} /r ]", mnemonic="PALIGNR")
@ispec_ia32("*>[ {0f}{3a}{40} /r ]", mnemonic="DPPS")
@ispec_ia32("*>[ {0f}{3a}{41} /r ]", mnemonic="DPPD")
@ispec_ia32("*>[ {0f}{3a}{42} /r ]", mnemonic="MPSADBW")
@ispec_ia32("*>[ {0f}{3a}{44} /r ]", mnemonic="PCLMULQDQ")
@ispec_ia32("*>[ {0f}{3a}{60} /r ]", mnemonic="PCMPESTRM")
@ispec_ia32("*>[ {0f}{3a}{61} /r ]", mnemonic="PCMPESTRI")
@ispec_ia32("*>[ {0f}{3a}{62} /r ]", mnemonic="PCMPISTRM")
@ispec_ia32("*>[ {0f}{3a}{63} /r ]", mnemonic="PCMPISTRI")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_66(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem:
        if obj.mnemonic=='ROUNDSD': op2.size = 64
        if obj.mnemonic=='ROUNDSS': op2.size = 32
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op1,op2]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# (SCALAR DOUBLE)
# xmm, xmm/m64
# xmm/m64, xmm
@ispec_ia32("*>[ {0f}{2e} /r ]", mnemonic="UCOMISD", _inv=False)
@ispec_ia32("*>[ {0f}{2f} /r ]", mnemonic="COMISD", _inv=False)
@ispec_ia32("*>[ {0f}{d6} /r ]", mnemonic="MOVQ", _inv=True)
def sse_pd(obj,Mod,REG,RM,data,_inv):
    if not check_66(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem: op2.size = 64
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2] if not _inv else [op2,op1]
    obj.type = type_data_processing

# xmm, mmx/m64
@ispec_ia32("*>[ {0f}{2a} /r ]", mnemonic="CVTPI2PD")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_66(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# other...
# xmm, r/m32, imm8
# r/m32, xmm, imm8
@ispec_ia32("*>[ {0f}{3a}{14} /r ]", mnemonic="PEXTRB", _inv=True)
@ispec_ia32("*>[ {0f}{3a}{15} /r ]", mnemonic="PEXTRW", _inv=True)
@ispec_ia32("*>[ {0f}{3a}{16} /r ]", mnemonic="PEXTRD", _inv=True)
@ispec_ia32("*>[ {0f}{3a}{17} /r ]", mnemonic="EXTRACTPS", _inv=True)
@ispec_ia32("*>[ {0f}{3a}{20} /r ]", mnemonic="PINSRB", _inv=False)
@ispec_ia32("*>[ {0f}{c4}     /r ]", mnemonic="PINSRW", _inv=False)
@ispec_ia32("*>[ {0f}{3a}{22} /r ]", mnemonic="PINSRD", _inv=False)
def sse_pd(obj,Mod,REG,RM,data,_inv):
    if not check_66(obj,set_opdsz_32): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem:
        if   obj.mnemonic[-1]=='B':
            op2.size=8
        elif obj.mnemonic[-1]=='W':
            if _inv: raise InstructionError(obj)
            else: op2.size=16
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2] if not _inv else [op2,op1]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

@ispec_ia32("*>[ {0f}{c5}     /r ]", mnemonic="PEXTRW", _inv=False)
def sse_pd(obj,Mod,REG,RM,data,_inv):
    if not check_66(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem:
        if   obj.mnemonic[-1]=='B':
            op2.size=8
        elif obj.mnemonic[-1]=='W':
            if _inv: raise InstructionError(obj)
            else: op2.size=16
    op1 = env.getreg(REG,32)
    obj.operands = [op1,op2] if not _inv else [op2,op1]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

@ispec_ia32("*>[ {0f}{3a}{21} /r ]", mnemonic="INSERTPS")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_66(obj,set_opdsz_128): raise InstructionError(obj)
    op1 = env.getreg(REG,128)
    op2,data = getModRM(obj,Mod,RM,data)
    if op2._is_mem:
        op2.size=32
    obj.operands = [op1,op2]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# registers only:
# xmm, xmm
@ispec_ia32("*>[ {0f}{f7} /r ]", mnemonic="MASKMOVDQU")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_66(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_reg: raise InstructionError(obj)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# r32, xmm
@ispec_ia32("*>[ {0f}{d7} /r ]", mnemonic="PMOVMSKB")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_66(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_reg: raise InstructionError(obj)
    op1 = env.getreg(REG,32)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# mmx, xmm/m128
@ispec_ia32("*>[ {0f}{2c} /r ]", mnemonic="CVTTPD2PI")
@ispec_ia32("*>[ {0f}{2d} /r ]", mnemonic="CVTPD2PI")
def sse_pd(obj,Mod,REG,RM,data):
    if not check_66(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,64)
    obj.operands = [op1,op2]
    obj.type = type_data_processing

# xmm, imm8
@ispec_ia32("*>[ {0f}{71} /2 ]", mnemonic="PSRLW")
@ispec_ia32("*>[ {0f}{71} /4 ]", mnemonic="PSRAW")
@ispec_ia32("*>[ {0f}{71} /6 ]", mnemonic="PSLLW")
@ispec_ia32("*>[ {0f}{72} /2 ]", mnemonic="PSRLD")
@ispec_ia32("*>[ {0f}{72} /4 ]", mnemonic="PSRAD")
@ispec_ia32("*>[ {0f}{72} /6 ]", mnemonic="PSLLD")
@ispec_ia32("*>[ {0f}{73} /2 ]", mnemonic="PSRLQ")
@ispec_ia32("*>[ {0f}{73} /3 ]", mnemonic="PSRLDQ")
@ispec_ia32("*>[ {0f}{73} /6 ]", mnemonic="PSLLQ")
@ispec_ia32("*>[ {0f}{73} /7 ]", mnemonic="PSLLDQ")
def sse_pd(obj,Mod,RM,data):
    if not check_66(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_reg: raise InstructionError(obj)
    obj.operands = [op2]
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands.append(env.cst(imm.int(),8))
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# moves:

# xmm, xmm/m32
# xmm/m32, xmm
@ispec_ia32("*>[ {0f}{6e} /r ]", mnemonic="MOVD", _inv=False)
@ispec_ia32("*>[ {0f}{7e} /r ]", mnemonic="MOVD", _inv=True)
def sse_pd(obj,Mod,REG,RM,data, _inv):
    if not check_66(obj,set_opdsz_32): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2] if not _inv else [op2,op1]
    obj.type = type_data_processing

# xmm, m64
# m64, xmm
@ispec_ia32("*>[ {0f}{12} /r ]", mnemonic="MOVLPD", _inv=False)
@ispec_ia32("*>[ {0f}{13} /r ]", mnemonic="MOVLPD", _inv=True)
@ispec_ia32("*>[ {0f}{16} /r ]", mnemonic="MOVHPD", _inv=False)
@ispec_ia32("*>[ {0f}{17} /r ]", mnemonic="MOVHPD", _inv=True)
def sse_pd(obj,Mod,REG,RM,data,_inv):
    if not check_66(obj,set_opdsz_64): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_mem: raise InstructionError(obj)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2] if not _inv else [op2, op1]
    obj.type = type_data_processing

# xmm, m128
# m128, xmm
@ispec_ia32("*>[ {0f}{38}{2a} /r ]", mnemonic="MOVNTDQA", _inv=False)
@ispec_ia32("*>[ {0f}{e7}     /r ]", mnemonic="MOVNTDQ",  _inv=True)
@ispec_ia32("*>[ {0f}{2b}     /r ]", mnemonic="MOVNTPD",  _inv=True)
def sse_pd(obj,Mod,REG,RM,data,_inv):
    if not check_66(obj,set_opdsz_128): raise InstructionError(obj)
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_mem: raise InstructionError(obj)
    op1 = env.getreg(REG,128)
    obj.operands = [op1,op2] if not _inv else [op2,op1]
    obj.type = type_data_processing
