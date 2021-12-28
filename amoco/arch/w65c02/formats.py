# -*- coding: utf-8 -*-

from .env import *
from amoco.cas.expressions import regtype
from amoco.arch.core import Formatter, Token


def mnemo(i):
    mn = i.mnemonic.lower()
    return [(Token.Mnemonic, "{: <6}".format(mn))]


def deref(opd):
    return "+%d(%s)" % (opd.a.disp, opd.a.base)


def opers(i):
    s = []
    for op in i.operands:
        if op._is_mem:
            s.append((Token.Memory, deref(op)))
        elif op._is_cst:
            if i.misc["ref"] is not None:
                s.append((Token.Address, "%s" % (i.misc["ref"])))
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


def opers_pcr(i):
    s = opers(i)
    if i.misc["pc_ref"] is not None and i.address is not None:
        adr = i.address + i.length + i.misc["pc_ref"].value
        s[-1] = (Token.Address, "%s" % (adr))
    return s


format_default = (mnemo, opers)

w65c02_full_formats = {
    "w65c02_pcr": (mnemo, opers_pcr),
    "w65c02_bb": (mnemo, opers_pcr),
}

w65c02_full = Formatter(w65c02_full_formats)
w65c02_full.default = format_default

