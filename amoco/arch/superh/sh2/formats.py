# -*- coding: utf-8 -*-

from .env import *
from .utils import *
from amoco.cas.expressions import regtype
from amoco.arch.core import Formatter, Token


def mnemo(i):
    if hasattr(i, "cond"):
        res = "%s/%s  " % (i.mnemonic, i.cond)
    elif hasattr(i, "size"):
        sz = {8: "B", 16: "W", 32: "L"}[i.size]
        res = "%s.%s  " % (i.mnemonic, sz)
    else:
        res = i.mnemonic
    return [(Token.Mnemonic, "{: <12}".format(res.lower()))]


def operands(i):
    res = []
    decr = i.misc["decr"] or set()
    incr = i.misc["incr"] or set()
    for j, r in enumerate(i.operands):
        if r._is_mem:
            if j in decr:
                x = "@-%s" % (r.a)
            elif j in incr:
                x = "@%s+" % (r.a)
            else:
                x = "@%s" % (r.a)
            res.append((Token.Memory, x))
        elif r._is_cst:
            res.append((Token.Constant, "#%s" % r))
        else:
            res.append((Token.Register, "%s" % r))
        res.append((Token.Literal, ","))
    if len(res) > 0:
        res.pop()
    return res


def target(i):
    res = []
    if i.operands:
        r = i.operands[0]
        if r._is_cst:
            res.append((Token.Constant, ".%+d" % r.value))
        elif r._is_mem:
            res.append((Token.Memory, "@%s" % r.a))
        else:
            res.append((Token.Register, "%s" % r))
    return res


format_sh2_default = (mnemo, operands)

SH2_full_formats = {
    "sh2_branch": [mnemo, target],
    "sh2_jsr_nn": [mnemo, lambda i: [(Token.Memory, "@@(%s)" % i.operands[0].ptr)]],
}

SH2_full = Formatter(SH2_full_formats)
SH2_full.default = format_sh2_default
