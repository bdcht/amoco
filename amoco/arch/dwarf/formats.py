# -*- coding: utf-8 -*-

from .env import *
from amoco.arch.core import Formatter
from amoco.ui.render import Token, TokenListJoin

def mnemo(i):
    m = i.mnemonic.replace('DW_OP_','')
    return [(Token.Mnemonic,'%s'%(m.lower()).ljust(12))]

def mnemo_lit(i):
    return [(Token.Mnemonic,'lit%d'%i.operands[0])]

def mnemo_reg(i):
    return [(Token.Mnemonic,str(i.operands[0]))]

def mnemo_breg(i):
    return [(Token.Mnemonic,"b%s"%(i.operands[0]))]

def hexarg(i):
    if len(i.operands)>0:
        return [(Token.Constant,"%x"%(i.operands[0]))]
    else:
        return []

def intarg(i):
    return [(Token.Constant,str(i.operands[0]))]

def adrarg(i):
    loc = i.operands[0]
    return [(Token.Address,str(loc))]

def relarg(i):
    off = i.operands[0]
    loc = i.address + i.length + off
    return [(Token.Address,str(loc))]

DW_full_formats = {
    'dw_op_0'       : [mnemo],
    'dw_op_jmp'     : [mnemo, relarg],
    'dw_op_1'       : [mnemo, intarg],
    'dw_op_addr'    : [mnemo, adrarg],
    'dw_op_lit'     : [mnemo_lit],
    'dw_op_reg'     : [mnemo_reg],
    'dw_op_breg'    : [mnemo_breg],
}

DW_full = Formatter(DW_full_formats)
DW_full.default = [mnemo,hexarg]
