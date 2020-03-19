# -*- coding: utf-8 -*-

from .env import *
from amoco.cas.expressions import regtype
from amoco.arch.core import Formatter, Token


def mnemo(i):
    mn = i.mnemonic.lower()
    return [(Token.Mnemonic, "{: <12}".format(mn))]


def deref(opd):
    return "+%d(%s)" % (opd.a.disp, opd.a.base)


def opers(i):
    s = []
    for op in i.operands:
        if op._is_mem:
            s.append((Token.Memory, deref(op)))
        elif op._is_cst:
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


def opers_adr(i):
    s = opers(i)
    if i.misc["imm_ref"] is None and i.address is not None:
        imm_ref = i.address + i.operands[-1]
        s[-1] = (Token.Address, "%s" % (imm_ref))
    return s


format_default = (mnemo, opers)

RISCV_full_formats = {
    "riscv_b": (mnemo, opers_adr),
    "riscv_jal": (mnemo, opers_adr),
}

RISCV_full = Formatter(RISCV_full_formats)
RISCV_full.default = format_default


def RISCV_synthetic(null, i, toks=False):
    s = RISCV_full(i, toks)
    return RISCV_Synthetic_renaming(s, i)


def RISCV_Synthetic_renaming(s, i):
    if (
        i.mnemonic == "jalr"
        and i.operands[0] == x[0]
        and i.operands[1] == x[1]
        and i.operands[2] == 0
    ):
        return "ret"
    if (
        i.mnemonic == "addi"
        and i.operands[0] == i.operands[1] == x[0]
        and i.operands[2] == 0
    ):
        return "nop"
    if i.mnemonic == "addi" and i.operands[2] == 0:
        return s.replace("addi", "mv").replace(", 0", "")
    if i.mnemonic == "xori" and i.operands[2] == -1:
        return s.replace("xori", "not").replace(", -1", "")
    return s
