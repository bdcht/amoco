# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2021 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.
# These objects are wrapped and created by disasm.py.

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")
from amoco.arch.core import *
from amoco.arch.wasm import env
from amoco.system.utils import read_leb128, read_uleb128, read_sleb128

ISPECS = []


@ispec("8>[ {00} ]", mnemonic="unreachable")
@ispec("8>[ {01} ]", mnemonic="nop")
@ispec("8>[ {d1} ]", mnemonic="ref",action="is_null")
@ispec("8>[ {1a} ]", mnemonic="drop")
@ispec("8>[ {1b} ]", mnemonic="select")
@ispec("8>[ {45} ]", mntype="i32", mnemonic="eqz")
@ispec("8>[ {46} ]", mntype="i32", mnemonic="eq")
@ispec("8>[ {47} ]", mntype="i32", mnemonic="ne")
@ispec("8>[ {48} ]", mntype="i32", mnemonic="lt_s")
@ispec("8>[ {49} ]", mntype="i32", mnemonic="lt_u")
@ispec("8>[ {4a} ]", mntype="i32", mnemonic="gt_s")
@ispec("8>[ {4b} ]", mntype="i32", mnemonic="gt_u")
@ispec("8>[ {4c} ]", mntype="i32", mnemonic="le_s")
@ispec("8>[ {4d} ]", mntype="i32", mnemonic="le_u")
@ispec("8>[ {4e} ]", mntype="i32", mnemonic="ge_s")
@ispec("8>[ {4f} ]", mntype="i32", mnemonic="ge_u")
@ispec("8>[ {50} ]", mntype="i64", mnemonic="eqz")
@ispec("8>[ {51} ]", mntype="i64", mnemonic="eq")
@ispec("8>[ {52} ]", mntype="i64", mnemonic="ne")
@ispec("8>[ {53} ]", mntype="i64", mnemonic="lt_s")
@ispec("8>[ {54} ]", mntype="i64", mnemonic="lt_u")
@ispec("8>[ {55} ]", mntype="i64", mnemonic="gt_s")
@ispec("8>[ {56} ]", mntype="i64", mnemonic="gt_u")
@ispec("8>[ {57} ]", mntype="i64", mnemonic="le_s")
@ispec("8>[ {58} ]", mntype="i64", mnemonic="le_u")
@ispec("8>[ {59} ]", mntype="i64", mnemonic="ge_s")
@ispec("8>[ {5a} ]", mntype="i64", mnemonic="ge_u")
@ispec("8>[ {5b} ]", mntype="f32", mnemonic="eq")
@ispec("8>[ {5c} ]", mntype="f32", mnemonic="ne")
@ispec("8>[ {5d} ]", mntype="f32", mnemonic="lt")
@ispec("8>[ {5e} ]", mntype="f32", mnemonic="gt")
@ispec("8>[ {5f} ]", mntype="f32", mnemonic="le")
@ispec("8>[ {60} ]", mntype="f32", mnemonic="ge")
@ispec("8>[ {61} ]", mntype="f64", mnemonic="eq")
@ispec("8>[ {62} ]", mntype="f64", mnemonic="ne")
@ispec("8>[ {63} ]", mntype="f64", mnemonic="lt")
@ispec("8>[ {64} ]", mntype="f64", mnemonic="gt")
@ispec("8>[ {65} ]", mntype="f64", mnemonic="le")
@ispec("8>[ {66} ]", mntype="f64", mnemonic="ge")
@ispec("8>[ {67} ]", mntype="i32", mnemonic="clz")
@ispec("8>[ {68} ]", mntype="i32", mnemonic="ctz")
@ispec("8>[ {69} ]", mntype="i32", mnemonic="popcnt")
@ispec("8>[ {6a} ]", mntype="i32", mnemonic="add")
@ispec("8>[ {6b} ]", mntype="i32", mnemonic="sub")
@ispec("8>[ {6c} ]", mntype="i32", mnemonic="mul")
@ispec("8>[ {6d} ]", mntype="i32", mnemonic="div_s")
@ispec("8>[ {6e} ]", mntype="i32", mnemonic="div_u")
@ispec("8>[ {6f} ]", mntype="i32", mnemonic="rem_s")
@ispec("8>[ {70} ]", mntype="i32", mnemonic="rem_u")
@ispec("8>[ {71} ]", mntype="i32", mnemonic="and")
@ispec("8>[ {72} ]", mntype="i32", mnemonic="or")
@ispec("8>[ {73} ]", mntype="i32", mnemonic="xor")
@ispec("8>[ {74} ]", mntype="i32", mnemonic="shl")
@ispec("8>[ {75} ]", mntype="i32", mnemonic="shr_s")
@ispec("8>[ {76} ]", mntype="i32", mnemonic="shr_u")
@ispec("8>[ {77} ]", mntype="i32", mnemonic="rotl")
@ispec("8>[ {78} ]", mntype="i32", mnemonic="rotr")
@ispec("8>[ {79} ]", mntype="i64", mnemonic="clz")
@ispec("8>[ {7a} ]", mntype="i64", mnemonic="ctz")
@ispec("8>[ {7b} ]", mntype="i64", mnemonic="popcnt")
@ispec("8>[ {7c} ]", mntype="i64", mnemonic="add")
@ispec("8>[ {7d} ]", mntype="i64", mnemonic="sub")
@ispec("8>[ {7e} ]", mntype="i64", mnemonic="mul")
@ispec("8>[ {7f} ]", mntype="i64", mnemonic="div_s")
@ispec("8>[ {80} ]", mntype="i64", mnemonic="div_u")
@ispec("8>[ {81} ]", mntype="i64", mnemonic="rem_s")
@ispec("8>[ {82} ]", mntype="i64", mnemonic="rem_u")
@ispec("8>[ {83} ]", mntype="i64", mnemonic="and")
@ispec("8>[ {84} ]", mntype="i64", mnemonic="or")
@ispec("8>[ {85} ]", mntype="i64", mnemonic="xor")
@ispec("8>[ {86} ]", mntype="i64", mnemonic="shl")
@ispec("8>[ {87} ]", mntype="i64", mnemonic="shr_s")
@ispec("8>[ {88} ]", mntype="i64", mnemonic="shr_u")
@ispec("8>[ {89} ]", mntype="i64", mnemonic="rotl")
@ispec("8>[ {8a} ]", mntype="i64", mnemonic="rotr")
@ispec("8>[ {8b} ]", mntype="f32", mnemonic="abs")
@ispec("8>[ {8c} ]", mntype="f32", mnemonic="neg")
@ispec("8>[ {8d} ]", mntype="f32", mnemonic="ceil")
@ispec("8>[ {8e} ]", mntype="f32", mnemonic="floor")
@ispec("8>[ {8f} ]", mntype="f32", mnemonic="trunc")
@ispec("8>[ {90} ]", mntype="f32", mnemonic="nearest")
@ispec("8>[ {91} ]", mntype="f32", mnemonic="sqrt")
@ispec("8>[ {92} ]", mntype="f32", mnemonic="add")
@ispec("8>[ {93} ]", mntype="f32", mnemonic="sub")
@ispec("8>[ {94} ]", mntype="f32", mnemonic="mul")
@ispec("8>[ {95} ]", mntype="f32", mnemonic="div")
@ispec("8>[ {96} ]", mntype="f32", mnemonic="min")
@ispec("8>[ {97} ]", mntype="f32", mnemonic="max")
@ispec("8>[ {98} ]", mntype="f32", mnemonic="copysign")
@ispec("8>[ {99} ]", mntype="f64", mnemonic="abs")
@ispec("8>[ {9a} ]", mntype="f64", mnemonic="neg")
@ispec("8>[ {9b} ]", mntype="f64", mnemonic="ceil")
@ispec("8>[ {9c} ]", mntype="f64", mnemonic="floor")
@ispec("8>[ {9d} ]", mntype="f64", mnemonic="trunc")
@ispec("8>[ {9e} ]", mntype="f64", mnemonic="nearest")
@ispec("8>[ {9f} ]", mntype="f64", mnemonic="sqrt")
@ispec("8>[ {a0} ]", mntype="f64", mnemonic="add")
@ispec("8>[ {a1} ]", mntype="f64", mnemonic="sub")
@ispec("8>[ {a2} ]", mntype="f64", mnemonic="mul")
@ispec("8>[ {a3} ]", mntype="f64", mnemonic="div")
@ispec("8>[ {a4} ]", mntype="f64", mnemonic="min")
@ispec("8>[ {a5} ]", mntype="f64", mnemonic="max")
@ispec("8>[ {a6} ]", mntype="f64", mnemonic="copysign")
@ispec("8>[ {a7} ]", mntype="i32", mnemonic="wrap_i64")
@ispec("8>[ {a8} ]", mntype="i32", mnemonic="trunc_f32_s")
@ispec("8>[ {a9} ]", mntype="i32", mnemonic="trunc_f32_u")
@ispec("8>[ {aa} ]", mntype="i32", mnemonic="trunc_f64_s")
@ispec("8>[ {ab} ]", mntype="i32", mnemonic="trunc_f64_u")
@ispec("8>[ {ac} ]", mntype="i64", mnemonic="extend_i32_s")
@ispec("8>[ {ad} ]", mntype="i64", mnemonic="extend_i32_u")
@ispec("8>[ {ae} ]", mntype="i64", mnemonic="trunc_f32_s")
@ispec("8>[ {af} ]", mntype="i64", mnemonic="trunc_f32_u")
@ispec("8>[ {b0} ]", mntype="i64", mnemonic="trunc_f64_s")
@ispec("8>[ {b1} ]", mntype="i64", mnemonic="trunc_f64_u")
@ispec("8>[ {b2} ]", mntype="f32", mnemonic="convert_i32_s")
@ispec("8>[ {b3} ]", mntype="f32", mnemonic="convert_i32_u")
@ispec("8>[ {b4} ]", mntype="f32", mnemonic="convert_i64_s")
@ispec("8>[ {b5} ]", mntype="f32", mnemonic="convert_i64_u")
@ispec("8>[ {b6} ]", mntype="f32", mnemonic="demote_f64")
@ispec("8>[ {b7} ]", mntype="f64", mnemonic="convert_i32_s")
@ispec("8>[ {b8} ]", mntype="f64", mnemonic="convert_i32_u")
@ispec("8>[ {b9} ]", mntype="f64", mnemonic="convert_i64_s")
@ispec("8>[ {ba} ]", mntype="f64", mnemonic="convert_i64_u")
@ispec("8>[ {bb} ]", mntype="f64", mnemonic="promote_f32")
@ispec("8>[ {bc} ]", mntype="i32", mnemonic="reinterpret_f32")
@ispec("8>[ {bd} ]", mntype="i64", mnemonic="reinterpret_f64")
@ispec("8>[ {be} ]", mntype="f32", mnemonic="reinterpret_i32")
@ispec("8>[ {bf} ]", mntype="f64", mnemonic="reinterpret_i64")
@ispec("8>[ {c0} ]", mntype="i32", mnemonic="extend8_s")
@ispec("8>[ {c1} ]", mntype="i32", mnemonic="extend16_s")
@ispec("8>[ {c2} ]", mntype="i64", mnemonic="extend8_s")
@ispec("8>[ {c3} ]", mntype="i64", mnemonic="extend16_s")
@ispec("8>[ {c4} ]", mntype="i64", mnemonic="extend32_s")
def dw_op_0(obj):
    obj.operands = []
    obj.type = type_data_processing

@ispec("8>[ {0b} ]", mnemonic="end")
@ispec("8>[ {0f} ]", mnemonic="return")
@ispec("8>[ {05} ]", mnemonic="else")
def dw_op_0(obj):
    obj.operands = []
    obj.type = type_control_flow

@ispec("16>[ {d0} t(8) ]", mnemonic="ref",action="null")
def dw_reftype(obj,t):
    if t in env.reftype:
        obj.operands = [env.reftype[t]]
    else:
        raise InstructionError(obj)
    obj.type = type_data_processing

@ispec("16>[ {3f} {00} ]", mnemonic="memory",action="size")
@ispec("16>[ {40} {00} ]", mnemonic="memory",action="grow")
def dw_memory(obj):
    obj.operands = []
    obj.type = type_data_processing

def xdata_select(obj,**kargs):
    addr = kargs['address']
    code = kargs['code']
    obj.t = []
    addr = addr+len(obj.bytes)
    off = 0
    for l in range(obj.x):
        n, sz = read_leb128(code,1,addr+off)
        obj.t.append(n)
        off += sz
    obj.operands[0] = obj.t
    obj.bytes += code[addr:addr+off]

@ispec("*>[ {d2} ~data(*) ]", mnemonic="ref",action="func")
@ispec("*>[ {1c} ~data(*) ] &", mnemonic="select")
@ispec("*>[ {20} ~data(*) ]", mnemonic="local", action="get")
@ispec("*>[ {21} ~data(*) ]", mnemonic="local", action="set")
@ispec("*>[ {22} ~data(*) ]", mnemonic="local", action="tee")
@ispec("*>[ {23} ~data(*) ]", mnemonic="global", action="get")
@ispec("*>[ {24} ~data(*) ]", mnemonic="global", action="set")
@ispec("*>[ {25} ~data(*) ]", mnemonic="table", action="get")
@ispec("*>[ {26} ~data(*) ]", mnemonic="table", action="set")
def dw_uleb128(obj, data):
    data = pack(data)
    obj.x,blen = read_uleb128(data)
    obj.bytes += data[0:blen]
    obj.operands = [obj.x]
    obj.type = type_data_processing
    if obj.mnemonic=="select":
        obj.xdata = xdata_select

@ispec("*>[ {41} ~data(*) ]", mnemonic="i32")
@ispec("*>[ {42} ~data(*) ]", mnemonic="i64")
@ispec("*>[ {43} ~data(*) ]", mnemonic="f32")
@ispec("*>[ {44} ~data(*) ]", mnemonic="f64")
def dw_uleb128(obj, data):
    data = pack(data)
    obj.n,blen = read_uleb128(data)
    obj.bytes += data[0:blen]
    obj.operands = [obj.n]
    obj.action = "const"
    obj.type = type_data_processing

@ispec("*>[ {fc} ~data(*) ]", mnemonic="table")
def dw_table(obj, data):
    data = pack(data)
    v,blen = read_uleb128(data)
    obj.bytes += data[0:blen]
    obj.type = type_data_processing
    if v>17:
        raise InstructionError(obj)
    if v<8:
        obj.mntype = "i32" if v<4 else "i64"
        post = "f32" if v in (0,2,4,5) else "f64"
        su = "_s" if v%2==0 else "_u"
        obj.mnemonic = "trunc_sat_"+post+su
    if v==10:
        obj.mnemonic = "memory"
        obj.action = "copy"
        if data[blen:blen+2]!=b'\x00\x00':
            raise InstructionError(obj)
        obj.bytes += data[blen:blen+2]
        return
    elif v==11:
        obj.mnemonic = "memory"
        obj.action = "fill"
        if data[blen:blen+1]!=b'\x00':
            raise InstructionError(obj)
        obj.bytes += data[blen:blen+1]
        return
    data = data[blen:]
    obj.x,blen1 = read_leb128(data,1,0)
    obj.bytes += data[0:blen1]
    if v==8:
        obj.mnemonic = "memory"
        obj.action = "init"
        if data[blen1:blen1+1]!=b'\x00':
            raise InstructionError(obj)
        obj.bytes += data[blen1:blen1+1]
    elif v==9:
        obj.mnemonic = "data"
        obj.action = "drop"
    elif v==12:
        obj.y = obj.x
        obj.x,blen2 = read_leb128(data,1,blen1)
        obj.bytes += data[blen1:blen1+blen2]
        obj.action = "init"
    elif v==13:
        obj.mnemonic = "elem"
        obj.action = "drop"
    elif v==14:
        obj.y,blen2 = read_leb128(data,1,blen1)
        obj.bytes += data[blen1:blen1+blen2]
        obj.action = "copy"
    else:
        obj.action = {15:"grow",16:"size",17:"fill"}[v]

@ispec("*>[ {02} ~data(*) ]", mnemonic="block")
@ispec("*>[ {03} ~data(*) ]", mnemonic="loop")
@ispec("*>[ {04} ~data(*) ]", mnemonic="if")
def dw_op_block(obj, data):
    data = pack(data)
    bt = data[0]
    if bt == 0x40:
        obj.bt = 0x40
        obj.bytes += data[0:1]
    elif bt in env.valtype:
        obj.bt = env.valtype[bt]
        obj.bytes += data[0:1]
    else:
        obj.bt,blen = read_sleb128(data)
        obj.bytes += data[0:blen]
    obj.operands = [obj.bt]
    obj.type = type_control_flow

def xdata_br_table(obj,**kargs):
    addr = kargs['address']
    code = kargs['code']
    obj.labels = []
    addr += len(obj.bytes)
    off = 0
    for l in range(obj.l):
        n, sz = read_leb128(code,1,addr+off)
        obj.labels.append(n)
        off += sz
    n, sz = read_leb128(code,1,addr+off)
    obj.default = n
    off += sz
    obj.bytes += code[addr:addr+off]

@ispec("*>[ {0c} ~data(*) ]", mnemonic="br")
@ispec("*>[ {0d} ~data(*) ]", mnemonic="br_if")
@ispec("*>[ {0e} ~data(*) ] &", mnemonic="br_table")
def dw_op_br(obj, data):
    data = pack(data)
    obj.l,blen = read_uleb128(data)
    obj.bytes += data[0:blen]
    obj.operands = [obj.l]
    obj.type = type_control_flow
    if obj.mnemonic=="br_table":
        obj.xdata = xdata_br_table

def xdata_call_indirect(obj,**kargs):
    addr = kargs['address']
    code = kargs['code']
    off = 0
    n, sz = read_leb128(code,1,addr+off)
    obj.y = n
    obj.operands.append(obj.y)
    off += sz
    obj.bytes += code[addr:addr+off]

@ispec("*>[ {10} ~data(*) ]", mnemonic="call")
@ispec("*>[ {11} ~data(*) ] &", mnemonic="call_indirect")
def dw_op_call(obj, data):
    data = pack(data)
    obj.x,blen = read_uleb128(data)
    obj.bytes += data[0:blen]
    obj.operands = [obj.x]
    obj.type = type_control_flow
    if obj.mnemonic=="call_indirect":
        obj.xdata = xdata_call_indirect

@ispec("*>[ {28} ~data(*) ]", mnemonic="i32", action="load")
@ispec("*>[ {29} ~data(*) ]", mnemonic="i64", action="load")
@ispec("*>[ {2a} ~data(*) ]", mnemonic="f32", action="load")
@ispec("*>[ {2b} ~data(*) ]", mnemonic="f64", action="load")
@ispec("*>[ {2c} ~data(*) ]", mnemonic="i32", action="load8_s")
@ispec("*>[ {2d} ~data(*) ]", mnemonic="i32", action="load8_u")
@ispec("*>[ {2e} ~data(*) ]", mnemonic="i32", action="load16_s")
@ispec("*>[ {2f} ~data(*) ]", mnemonic="i32", action="load16_u")
@ispec("*>[ {30} ~data(*) ]", mnemonic="i64", action="load8_s")
@ispec("*>[ {31} ~data(*) ]", mnemonic="i64", action="load8_u")
@ispec("*>[ {32} ~data(*) ]", mnemonic="i64", action="load16_s")
@ispec("*>[ {33} ~data(*) ]", mnemonic="i64", action="load16_u")
@ispec("*>[ {34} ~data(*) ]", mnemonic="i64", action="load32_s")
@ispec("*>[ {35} ~data(*) ]", mnemonic="i64", action="load32_u")
@ispec("*>[ {36} ~data(*) ]", mnemonic="i32", action="store")
@ispec("*>[ {37} ~data(*) ]", mnemonic="i64", action="store")
@ispec("*>[ {38} ~data(*) ]", mnemonic="f32", action="store")
@ispec("*>[ {39} ~data(*) ]", mnemonic="f64", action="store")
@ispec("*>[ {3a} ~data(*) ]", mnemonic="i32", action="store8")
@ispec("*>[ {3b} ~data(*) ]", mnemonic="i32", action="store16")
@ispec("*>[ {3c} ~data(*) ]", mnemonic="i64", action="store8")
@ispec("*>[ {3d} ~data(*) ]", mnemonic="i64", action="store16")
@ispec("*>[ {3e} ~data(*) ]", mnemonic="i64", action="store32")
def dw_memarg(obj, data):
    data = pack(data)
    obj.a,blen1 = read_leb128(data,1,0)
    obj.bytes += data[0:blen]
    obj.o,blen2 = read_leb128(data,1,blen1)
    obj.bytes += data[blen:blen1+blen2]
    obj.type = type_data_processing
