# -*- coding: utf-8 -*-

from .env import *
from amoco.cas.expressions import regtype
from amoco.arch.core import Formatter, Token


def mnemo(i):
    mn = i.mnemonic.replace('_','.').lower()
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
            s.append((Token.Register, op.__str__().ljust(3,' ')))
        elif op._is_cmp:
            s.append((Token.Register,
                    "/".join(x.__str__() for x in [op[0:32],op[32:64]])))
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

tricore_full_formats = {
    "tricore_branch": (mnemo, opers_adr),
    "tricore_jcc": (mnemo, opers_adr),
}

TriCore_full = Formatter(tricore_full_formats)
TriCore_full.default = format_default

