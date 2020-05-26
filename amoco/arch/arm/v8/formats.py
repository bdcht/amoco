# -*- coding: utf-8 -*-

from .env64 import *
from .utils import *
from amoco.arch.core import Formatter
from amoco.ui.render import Token
from amoco.ui.render import TokenListJoin, LambdaTokenListJoin


def tok_mnemo(x):
    return [(Token.Mnemonic, "{:<12}".format(m.lower()))]


def mnemo(i):
    m = i.mnemonic
    if hasattr(i, "setflags") and i.setflags:
        m += "S"
    if m == "Bcond":
        m = "B.%s" % (i.misc["cond"])
    return tok_mnemo(m)


def regs(i, limit=None):
    ops = i.operands
    if limit:
        ops = ops[:limit]
    return [r.toks() for r in ops]


def deref(i, pos=-2):
    assert len(i.operands) > 2
    base, offset = i.operands[pos], i.operands[pos + 1]
    if offset._is_cst:
        offset.sf = True
        ostr = "%+0d" % offset.value
    else:
        ostr = str(offset)
    if hasattr(i, "wback"):
        wb = "!" if i.wback else ""
        if i.postindex:
            loc = "[%s], %s" % (base, ostr)
        else:
            loc = "[%s, %s]%s" % (base, ostr, wb)
    return [(Token.Memory, loc)]


def label(i, pos=0):
    _pc = i.address
    if _pc is None:
        _pc = pc
    offset = i.operands[pos]
    return [(Token.Address, str(_pc + offset))]


def label_adr(i):
    _pc = i.address
    if _pc is None:
        _pc = pc
    _pc = _pc & 0xFFFFFFFFFFFFF000
    offset = i.operands[1]
    return [(Token.Address, str(_pc + offset))]


# -----------------------------------------------------------------------------
# instruction aliases:


def alias_ADD(i):
    m = mnemo(i)
    r = regs(i)
    if not i.setflags:
        if (i.d == 0 or i.n == 0) and i.operands[-1] == 0:
            m = tok_mnemo("mov")
            r.pop(0)
    elif i.setflags and i.d == 0:
        m = tok_mnemo("cmn")
        r  = r.pop(0)
    return m + TokenListJoin(", ",r)


def alias_SUB(i):
    m = mnemo(i)
    r = regs(i)
    if not i.setflags:
        if i.n == 0:
            m = tok_mnemo("neg")
            r.pop(1)
    elif i.setflags:
        if i.d == 0:
            m = tok_mnemo("cmp")
            r.pop(1)
        elif i.n == 0:
            m = tok_mnemo("negs")
            r.pop(1)
    return m + TokenListJoin(", ",r)


def alias_AND(i):
    m = mnemo(i)
    r = regs(i)
    if i.setflags and i.d == 0:
        m = tok_mnemo("tst")
        r = r[1:]
    return m + TokenListJoin(", ",r)


def alias_BFM(i):
    r = regs(i)
    if i.imms < i.immr:
        r[3] = (Token.Constant, str(i.immr + 1))
        r[2] = (Token.Constant, str(-i.imms % i.datasize))
        m = tok_mnemo("bfi")
    else:
        r[3] = (Token.Constant, str(i.imms - i.immr + 1))
        m = tok_mnemo("bfxil")
    return m + TokenListJoin(", ",r)


def alias_SBFM(i):
    m = mnemo(i)
    r = regs(i)
    if i.imms == i.datasize - 1:
        r.pop()
        m = tok_mnemo("asr")
    elif i.imms < i.immr:
        m = tok_mnemo("sbfiz")
        r[3] = (Token.Constant, str(i.immr + 1))
        r[2] = (Token.Constant, str(-i.imms % i.datasize))
    elif i.immr == 0:
        if i.immr == 7:
            m = tok_mnemo("sxtb")
        if i.immr == 15:
            m = tok_mnemo("sxth")
        if i.immr == 31:
            m = tok_mnemo("sxtw")
        r.pop(1)
    return m + TokenListJoin(", ",r)


def alias_UBFM(i):
    m = mnemo(i)
    r = regs(i)
    if i.imms == i.datasize - 1:
        r.pop()
        m = tok_mnemo("lsr")
    elif i.imms + 1 == i.immr:
        m = tok_mnemo("lsl")
        r[2] = (Token.Constant, str(-i.imms % i.datasize))
        r.pop()
    elif i.imms < i.immr:
        m = tok_mnemo("ubfiz")
        r[3] = (Token.Constant, str(i.immr + 1))
        r[2] = (Token.Constant, str(-i.imms % i.datasize))
    elif i.immr == 0:
        if i.immr == 7:
            m = tok_mnemo("uxtb")
        if i.immr == 15:
            m = tok_mnemo("uxth")
        if i.immr == 31:
            m = tok_mnemo("uxtw")
        r = r[:2]
    return m + TokenListJoin(", ",r)


def alias_CSINC(i):
    m = mnemo(i)
    r = regs(i)
    if i.n is i.m:
        if i.cond >> 1 != 0b111:
            if i.n != 0:
                m = tok_mnemo("cinc")
                r = r[:2]
            else:
                m = tok_mnemo("cset")
                r = r[:1]
            r.append((Token.Literal,"%s"%CONDITION[i.cond ^ 1][0]))
    return m + TokenListJoin(", ",r)


def alias_CSINV(i):
    m = mnemo(i)
    r = regs(i)
    if i.n is i.m:
        if i.cond >> 1 != 0b111:
            if i.n != 0:
                m = tok_mnemo("cinv")
                r = r[:2]
            else:
                m = tok_mnemo("csetm")
                r = r[:1]
            r.append((Token.Literal,"%s"%CONDITION[i.cond ^ 1][0]))
    return m + TokenListJoin(", ",r)


def alias_CSNEG(i):
    m = mnemo(i)
    r = regs(i)
    if i.n is i.m:
        if i.cond >> 1 != 0b111:
            m = tok_mnemo("cneg")
            r = r[:2]
            r.append((Token.Literal,"%s"%CONDITION[i.cond ^ 1][0]))
    return m + TokenListJoin(", ",r)


def alias_EXTR(i):
    m = mnemo(i)
    r = regs(i)
    if i.n is i.m:
        m = tok_mnemo("ror")
        r.pop(1)
    return m + TokenListJoin(", ",r)


def alias_HINT(i):
    m = {0: "nop", 5: "sevl", 4: "sev", 2: "wfe", 3: "wfi", 1: "yield"}
    return tok_mnemo(m.get(i.imm.value, "nop"))


def alias_MADD(i):
    m = mnemo(i)
    r = regs(i)
    if i.a == 0:
        m = tok_mnemo("mul")
        r.pop()
    return m + TokenListJoin(", ",r)


def alias_SMADDL(i):
    m = mnemo(i)
    r = regs(i)
    if i.a == 0:
        m = tok_mnemo("smull")
        r.pop()
    return m + TokenListJoin(", ",r)


def alias_UMADDL(i):
    m = mnemo(i)
    r = regs(i)
    if i.a == 0:
        m = tok_mnemo("umull")
        r.pop()
    return m + TokenListJoin(", ",r)


def alias_MSUB(i):
    m = mnemo(i)
    r = regs(i)
    if i.a == 0:
        m = tok_mnemo("mneg")
        r.pop()
    return m + TokenListJoin(", ",r)


def alias_SMSUBL(i):
    m = mnemo(i)
    r = regs(i)
    if i.a == 0:
        m = tok_mnemo("smnegl")
        r.pop()
    return m + TokenListJoin(", ",r)


def alias_UMSUBL(i):
    m = mnemo(i)
    r = regs(i)
    if i.a == 0:
        m = tok_mnemo("umnegl")
        r.pop()
    return m + TokenListJoin(", ",r)


def alias_ORR(i):
    m = mnemo(i)
    r = regs(i)
    if i.n == 0:
        m = tok_mnemo("mov")
        r.pop(1)
    return m + TokenListJoin(", ",r)


def alias_ORN(i):
    m = mnemo(i)
    r = regs(i)
    if i.n == 0:
        m = tok_mnemo("mvn")
        r.pop(1)
    return m + TokenListJoin(", ",r)


def alias_SBC(i):
    m = mnemo(i)
    r = regs(i)
    if i.n == 0:
        m = m[0][1].replace("sbc","ngc")
        m = tok_mnemo(m)
        r.pop(1)
    return m + TokenListJoin(", ",r)


condreg = lambda i: [(Token.Literal, "'%s'" % CONDITION[i.cond][0])]
allregs = LambdaTokenListJoin(", ",regs)
format_default = [mnemo, LambdaTokenListJoin(", ",regs)]
format_ld_st = [mnemo, lambda i: TokenListJoin(", ",regs(i, -2) +
                                                    deref(i, -2))]
format_B = [mnemo, label]
format_ADR = [mnemo, lambda i: TokenListJoin(", ", i.operands[0].toks() +
                                                   label_adr(i))]
format_CBx = [mnemo, lambda i: TokenListJoin(", ",  i.t.toks() + label(i, 1))]
format_CCMx = [mnemo, lambda i: TokenListJoin(", ", regs(i, 2)),
                      lambda i: i.flags.toks(),
                      condreg]

ARM_V8_full_formats = {
    "A64_generic": format_default,
    "A64_load_store": format_ld_st,
    "A64_adr": format_ADR,
    "A64_Bcond": format_B,
    "A64_B": format_B,
    "A64_CBx": format_CBx,
    "A64_CCMx": format_CCMx,
    "ASRV": ["asr ", allregs],
    "LSLV": ["lsl ", allregs],
    "LSRV": ["lsr ", allregs],
    "RORV": ["ror ", allregs],
    "ADD": [alias_ADD],
    "SUB": [alias_SUB],
    "AND": [alias_AND],
    "BFM": [alias_BFM],
    "SBFM": [alias_SBFM],
    "UBFM": [alias_UBFM],
    "CSINC": [alias_CSINC],
    "CSINV": [alias_CSINV],
    "CSNEG": [alias_CSNEG],
    "EXTR": [alias_EXTR],
    "HINT": [alias_HINT],
    "MADD": [alias_MADD],
    "SMADDL": [alias_SMADDL],
    "MSUB": [alias_MSUB],
    "ORR": [alias_ORR],
    "ORN": [alias_ORN],
    "SBC": [alias_SBC],
}

ARM_V8_full = Formatter(ARM_V8_full_formats)
