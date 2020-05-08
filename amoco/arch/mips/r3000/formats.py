# -*- coding: utf-8 -*-

from .env import *
from amoco.cas.expressions import regtype
from amoco.arch.core import Formatter, Token

def mnemo(i):
    mn = i.mnemonic.lower()
    return [(Token.Mnemonic, "{: <12}".format(mn))]

def deref(base,off):
    return "+%d(%s)" % (off, base)

def opers(i):
    s = []
    for op in i.operands:
        if op._is_cst:
            if i.misc["imm_ref"] is not None:
                s.append((Token.Address, "%s" % (i.misc["imm_ref"])))
            elif op.sf:
                s.append((Token.Constant, "%+d" % op.value))
            else:
                s.append((Token.Constant, op.__str__()))
        elif op._is_reg:
            s.append((Token.Register, op.__str__()))
        s.append((Token.Literal, ", "))
    if len(s) > 0:
        s.pop()
    return s

def opers_mem(i):
    s = []
    op = i.operands[0]
    s.append((Token.Register, op.__str__()))
    s.append((Token.Literal, ", "))
    s.append((Token.Memory,deref(*(i.operands[1:]))))
    return s

def opers_adr(i):
    s = opers(i)
    if i.misc["imm_ref"] is None and i.address is not None:
        imm_ref = i.address + 4 + i.operands[-1]
        s[-1] = (Token.Address, "%s" % (imm_ref))
    return s

def opers_rel(i):
    s = opers(i)
    if i.misc["imm_ref"] is None and i.address is not None:
        imm_ref = composer([cst(0,2),i.operands[-1],i.address[28:32]])
        s[-1] = (Token.Address, "%s" % (imm_ref))
    return s


format_default = (mnemo, opers)

MIPS_full_formats = {
    "mips1_loadstore": (mnemo, opers_mem),
    "mips1_jump_abs": (mnemo, opers),
    "mips1_jump_rel": (mnemo, opers_rel),
    "mips1_branch": (mnemo, opers_adr),
}

MIPS_full = Formatter(MIPS_full_formats)
MIPS_full.default = format_default


def MIPS_synthetic(null, i, toks=False):
    s = MIPS_full(i, toks)
    return MIPS_Synthetic_renaming(s, i)


def MIPS_Synthetic_renaming(s, i):
    # TODO
    return s
