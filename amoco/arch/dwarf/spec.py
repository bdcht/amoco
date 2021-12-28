# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")
from amoco.arch.core import *
from amoco.arch.dwarf import env
from amoco.system.utils import read_leb128, read_sleb128

ISPECS = []

WORD = env.WORD


@ispec("8>[ {06} ]", mnemonic="DW_OP_deref")
@ispec("8>[ {12} ]", mnemonic="DW_OP_dup")
@ispec("8>[ {13} ]", mnemonic="DW_OP_drop")
@ispec("8>[ {14} ]", mnemonic="DW_OP_over")
@ispec("8>[ {16} ]", mnemonic="DW_OP_swap")
@ispec("8>[ {17} ]", mnemonic="DW_OP_rot")
@ispec("8>[ {19} ]", mnemonic="DW_OP_abs")
@ispec("8>[ {1a} ]", mnemonic="DW_OP_and")
@ispec("8>[ {1b} ]", mnemonic="DW_OP_div")
@ispec("8>[ {1c} ]", mnemonic="DW_OP_minus")
@ispec("8>[ {1d} ]", mnemonic="DW_OP_mod")
@ispec("8>[ {1e} ]", mnemonic="DW_OP_mul")
@ispec("8>[ {1f} ]", mnemonic="DW_OP_neg")
@ispec("8>[ {20} ]", mnemonic="DW_OP_not")
@ispec("8>[ {21} ]", mnemonic="DW_OP_or")
@ispec("8>[ {22} ]", mnemonic="DW_OP_plus")
@ispec("8>[ {24} ]", mnemonic="DW_OP_shl")
@ispec("8>[ {25} ]", mnemonic="DW_OP_shr")
@ispec("8>[ {26} ]", mnemonic="DW_OP_shra")
@ispec("8>[ {27} ]", mnemonic="DW_OP_xor")
@ispec("8>[ {29} ]", mnemonic="DW_OP_eq")
@ispec("8>[ {2a} ]", mnemonic="DW_OP_ge")
@ispec("8>[ {2b} ]", mnemonic="DW_OP_gt")
@ispec("8>[ {2c} ]", mnemonic="DW_OP_le")
@ispec("8>[ {2d} ]", mnemonic="DW_OP_lt")
@ispec("8>[ {2e} ]", mnemonic="DW_OP_ne")
@ispec("8>[ {96} ]", mnemonic="DW_OP_nop")
def dw_op_0(obj):
    obj.operands = []
    obj.type = type_data_processing


@ispec("24>[ {28} ~offset(16) ]", mnemonic="DW_OP_bra")
@ispec("24>[ {2f} ~offset(16) ]", mnemonic="DW_OP_skip")
def dw_op_jmp(obj, offset):
    obj.operands = [env.cst(offset.int(-1), WORD)]
    obj.type = type_control_flow


@ispec("16>[ {15} offset(8) ]", mnemonic="DW_OP_pick")
@ispec("16>[ {94} offset(8) ]", mnemonic="DW_OP_deref_size")
def dw_op_1(obj, offset):
    obj.operands = [offset]
    obj.type = type_data_processing


@ispec("*>[ {94} ~data(*) ]", mnemonic="DW_OP_plus_uconst")
def dw_op_leb128(obj, data):
    data = pack(data)
    result, blen = read_leb128(data)
    obj.operands = [env.cst(result, WORD)]
    obj.bytes += data[:blen]
    obj.type = type_data_processing


for i in range(0x30, 0x50):
    @ispec("8>[ {%2x} ]" % i, mnemonic="DW_OP_lit", _num=i - 0x30)
    def dw_op_lit(obj, _num):
        obj.operands = [env.cst(_num, WORD)]
        obj.type = type_data_processing


@ispec("*>[ {03} ~data(*) ]", mnemonic="DW_OP_addr")
def dw_op_addr(obj, data):
    sz = env.op_ptr.size
    if data.size < sz:
        raise InstructionError(obj)
    result = data[0:sz]
    obj.operands = [env.cst(result.int(), sz)]
    obj.bytes += pack(result)
    obj.type = type_data_processing


@ispec("*>[ {f1} enc(8) ~data(*) ]", mnemonic="DW_OP_GNU_encoded_addr")
def dw_op_gnu(obj, enc, data):
    sz = env.op_ptr.size
    if data.size < sz:
        raise InstructionError(obj)
    result = XXX
    obj.operands = [env.cst(XXX.int(), sz)]
    obj.bytes += pack(result)
    obj.type = type_data_processing


@ispec("*>[ {08} ~data(*) ]", mnemonic="DW_OP_const", sz=1, sign=+1)
@ispec("*>[ {09} ~data(*) ]", mnemonic="DW_OP_const", sz=1, sign=-1)
@ispec("*>[ {0a} ~data(*) ]", mnemonic="DW_OP_const", sz=2, sign=+1)
@ispec("*>[ {0b} ~data(*) ]", mnemonic="DW_OP_const", sz=2, sign=-1)
@ispec("*>[ {0c} ~data(*) ]", mnemonic="DW_OP_const", sz=4, sign=+1)
@ispec("*>[ {0d} ~data(*) ]", mnemonic="DW_OP_const", sz=4, sign=-1)
@ispec("*>[ {0e} ~data(*) ]", mnemonic="DW_OP_const", sz=8, sign=+1)
@ispec("*>[ {0f} ~data(*) ]", mnemonic="DW_OP_const", sz=8, sign=-1)
def dw_op_const(obj, data):
    sz = 8 * obj.sz
    if data.size < sz:
        raise InstructionError(obj)
    result = data[0:sz]
    obj.operands = [env.cst(result.int(obj.sign), WORD)]
    obj.bytes += pack(result)
    obj.type = type_data_processing


@ispec("*>[ {10} ~data(*) ]", mnemonic="DW_OP_const", sz=0, sign=+1)
@ispec("*>[ {11} ~data(*) ]", mnemonic="DW_OP_const", sz=0, sign=-1)
def dw_op_const(obj, data):
    sz = env.op_ptr.size
    if data.size < sz:
        raise InstructionError(obj)
    data = pack(data)
    result, blen = read_leb128(data, obj.sign)
    obj.operands = [env.cst(result, WORD)]
    obj.bytes += data[:blen]
    obj.type = type_data_processing


for i in range(0x50, 0x70):
    @ispec("8>[ {%2x} ]" % i, mnemonic="DW_OP_reg", _num=i - 0x50)
    def dw_op_reg(obj, _num):
        sz = env.op_ptr.size
        obj.operands = [env.reg("reg%d" % _num, sz)]
        obj.type = type_data_processing


@ispec("*>[ {90} ~data(*) ]", mnemonic="DW_OP_regx")
def dw_op_regx(obj, data):
    data = pack(data)
    indx, blen = read_leb128(data)
    sz = env.op_ptr.size
    r = env.reg("reg%d" % indx, sz)
    obj.operands = [r]
    obj.bytes += data[:blen]
    obj.type = type_data_processing


for i in range(0x70, 0x90):
    @ispec("*>[ {%2x} ~data(*) ]" % i, mnemonic="DW_OP_breg", _num=i - 0x70)
    def dw_op_breg(obj, data, _num):
        data = pack(data)
        result, blen = read_sleb128(data)
        sz = env.op_ptr.size
        offset = env.cst(result, blen * 8).signextend(sz)
        obj.operands = [env.reg("reg%d" % _num, sz) + offset]
        obj.bytes += data[:blen]
        obj.type = type_data_processing


@ispec("*>[ {92} ~data(*) ]", mnemonic="DW_OP_bregx")
def dw_op_bregx(obj, data):
    data = pack(data)
    indx, blen = read_leb128(data)
    sz = env.op_ptr.size
    r = env.reg("reg%d" % indx, sz)
    obj.bytes += data[:blen]
    data = data[blen:]
    result, blen = read_sleb128(data)
    offset = env.cst(result, blen * 8).signextend(sz)
    obj.operands = [r + offset]
    obj.bytes += data[:blen]
    obj.type = type_data_processing
