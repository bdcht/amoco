# -*- coding: utf-8 -*-

from .env import *
from .utils import *
from amoco.arch.core import Formatter
from amoco.ui.render import highlight, Token
from amoco.ui.render import TokenListJoin, LambdaTokenListJoin
from amoco.ui.render import replace_mnemonic_token, replace_opn_token


def regs(i):
    "returns a list of Register tokens"
    return [(Token.Register, "%{0}".format(r)) for r in i.operands]


def regn(i, n):
    "returns a list of a single Register token from n-th operand"
    return [(Token.Register, "%{0}".format(i.operands[n]))]


def address(a):
    "returns a list of a single Address token from given expression"
    if not a._is_eqn:
        return reg_or_imm(a)
    l = reg_or_imm(a.l)[0][1]
    op = a.op.symbol
    r = reg_or_imm(a.r)[0][1]
    return [(Token.Address, "%s%s%s"%(l, op, r))]


def deref(a):
    "returns a list of a single Memory token for address a"
    if a.seg is None:
        seg = ""
    else:
        seg = a.seg
    res = "[%s]%s"%(address(a.base+a.disp)[0][1],seg)
    return [(Token.Memory, res)]

def mnemo(i):
    "returns a list of a single Mnemonic token"
    return [(Token.Mnemonic, "{i.mnemonic:<8}".format(i=i))]

def mnemo_icc(i):
    "returns a list of a single Mnemonic token with condition code"
    s = i.mnemonic
    if i.misc["icc"]:
        s += "cc"
    return [(Token.Mnemonic, "{:<8}".format(s))]


def mnemo_cond(i):
    "returns a list of a single Mnemonic token with CONDxB and annul suffix"
    s = CONDxB[i.mnemonic][i.cond]
    if i.misc["annul"]:
        s += ",a"
    return [(Token.Mnemonic, "{:<8}".format(s))]


def reg_or_imm(x, t="%d"):
    "returns a list of a single token constructed from x"
    # Special detections for %hi or %lo
    hilo = None
    if x._is_cmp:
        if sorted(x.parts.keys()) == [(0, 10), (10, 32)]:
            if str(x.parts[(10, 32)]) == "0x0":
                hilo = ["%lo", x.parts[(0, 10)].x]
            if str(x.parts[(0, 10)]) == "0x0":
                hilo = ["%hi", x.parts[(10, 32)].x]
    elif x._is_slc:
        if x.pos == 10 and x.size == 22:
            hilo = ["%hi", x.x]
        if x.pos == 0 and x.size == 10:
            hilo = ["%lo", x.x]
    # Other cases
    elif x._is_ext:
        return [(Token.Address, "%s"%x.ref)]
    elif x._is_reg:
        return [(Token.Register, "%"+x.ref)]
    elif x._is_cst:
        return [(Token.Constant, t % x.value)]
    elif x._is_eqn:
        if x.r is None:
            res = ("%s" + t) % (x.op.symbol, x.l)
        elif x.l is None:
            res = ("%s" + t) % (x.op.symbol, x.r)
        else:
            res = (t + "%s" + t) % (x.l, x.op.symbol, x.r)
        return [(Token.Constant, res)]
    # Now dealing with hilo
    if hilo is None:
        return [(Token.Register, str(x))]
    else:
        res = "%s(%s)"%(hilo[0],address(hilo[1])[0][1])
    return [(Token.Address, res)]


def label(i):
    "returns a list of a single token for label cases"
    _pc = i.address
    if _pc is None:
        _pc = pc
    if i.operands[0]._is_ext:
        return [(Token.Address, str(i.operands[0].ref))]
    if i.operands[0]._is_reg:
        return [(Token.Register, "%%%s"%(i.operands[0].ref))]
    if i.operands[0]._is_cst:
        offset = i.operands[0].signextend(32) * 4
        target = i.misc["dst"] or (_pc+offset)
        return [(Token.Address, str(target))]
    raise TypeError("operand type not supported")


format_ld = [mnemo, lambda i: TokenListJoin(", ", deref(i.operands[0]) + regn(i, 1))]
format_st = [mnemo, lambda i: TokenListJoin(", ", regn(i, 0) + deref(i.operands[1]))]
format_logic = [
    mnemo_icc,
    lambda i: TokenListJoin(
        ", ", regn(i, 0) + reg_or_imm(i.operands[1], "%#x") + regn(i, 2)
    ),
]
format_sethi = [
    mnemo,
    lambda i: TokenListJoin(", ", reg_or_imm(i.operands[0]) + regn(i, 1)),
]
format_arith = [
    mnemo_icc,
    lambda i: TokenListJoin(
        ", ", regn(i, 0) + reg_or_imm(i.operands[1], "%d") + regn(i, 2)
    ),
]
format_xb = [mnemo_cond, label]
format_call = [mnemo, lambda i: TokenListJoin(", ", label(i) +
                                                    [(Token.Constant, "0")])]
format_jmpl = [
    mnemo,
    lambda i: TokenListJoin(", ", address(i.operands[0]) + regn(i, 1)),
]
format_addr = [mnemo, lambda i: address(i.operands[0])]
format_t = [lambda i: [(Token.Mnemonic, "{:<8}".format(CONDT[i.cond]))] +
            reg_or_imm(i.operands[0])]
format_wr = [
    mnemo,
    lambda i: TokenListJoin(", ",regn(i, 0) +
                                 reg_or_imm(i.operands[1], "%#x") +
                                 regn(i, 2)),
]
format_cpop = [
    mnemo,
    lambda i: [(Token.Constant, "{i.operands[0]:d}")]
              + TokenListJoin(", ", regs(i)[1:]),
]

SPARC_V8_full_formats = {
    "sparc_ld_"           : format_ld,
    "sparc_ldf_ldc"       : format_ld,
    "sparc_st_"           : format_st,
    "sparc_stf_stc"       : format_st,
    "sparc_logic_"        : format_logic,
    "sethi"               : format_sethi,
    "nop"                 : [mnemo],
    "sparc_arith_"        : format_arith,
    "sparc_shift_"        : format_arith,
    "sparc_tagged_"       : format_arith,
    "sparc_Bicc"          : format_xb,
    "call"                : format_call,
    "jmpl"                : format_jmpl,
    "rett"                : format_addr,
    "t"                   : format_t,
    "sparc_rd_"           : [mnemo, LambdaTokenListJoin(", ", regs)],
    "sparc_wr_"           : format_wr,
    "stbar"               : [mnemo],
    "flush"               : format_addr,
    "sparc_Fpop1_group1"  : [mnemo, LambdaTokenListJoin(", ", regs)],
    "sparc_Fpop1_group2"  : [mnemo, LambdaTokenListJoin(", ", regs)],
    "sparc_Fpop2_"        : [mnemo, LambdaTokenListJoin(", ", regs)],
    "sparc_Cpop"          : format_cpop,
}

SPARC_V8_full = Formatter(SPARC_V8_full_formats)

CONDB = {
    0b1000: "ba",
    0b0000: "bn",
    0b1001: "bne",
    0b0001: "be",
    0b1010: "bg",
    0b0010: "ble",
    0b1011: "bge",
    0b0011: "bl",
    0b1100: "bgu",
    0b0100: "bleu",
    0b1101: "bcc",
    0b0101: "bcs",
    0b1110: "bpos",
    0b0110: "bneg",
    0b1111: "bvc",
    0b0111: "bvs",
}
CONDFB = {
    0b1000: "fba",
    0b0000: "fbn",
    0b0111: "fbu",
    0b0110: "fbg",
    0b0101: "fbug",
    0b0100: "fbl",
    0b0011: "fbul",
    0b0010: "fblg",
    0b0001: "fbne",
    0b1001: "fbe",
    0b1010: "fbue",
    0b1011: "fbge",
    0b1100: "fbuge",
    0b1101: "fble",
    0b1110: "fbule",
    0b1111: "fbo",
}
CONDCB = {
    0b1000: "cba",
    0b0000: "cbn",
    0b0111: "cb3",
    0b0110: "cb2",
    0b0101: "cb23",
    0b0100: "cb1",
    0b0011: "cb13",
    0b0010: "cb12",
    0b0001: "cb123",
    0b1001: "cb0",
    0b1010: "cb03",
    0b1011: "cb02",
    0b1100: "cb023",
    0b1101: "cb01",
    0b1110: "cb013",
    0b1111: "cb012",
}
CONDT = {
    0b1000: "ta",
    0b0000: "tn",
    0b1001: "tne",
    0b0001: "te",
    0b1010: "tg",
    0b0010: "tle",
    0b1011: "tge",
    0b0011: "tl",
    0b1100: "tgu",
    0b0100: "tleu",
    0b1101: "tcc",
    0b0101: "tcs",
    0b1110: "tpos",
    0b0110: "tneg",
    0b1111: "tvc",
    0b0111: "tvs",
}

CONDxB = {"b": CONDB, "fb": CONDFB, "cb": CONDCB}


def SPARC_V8_synthetic(null, i, toks=False):
    s = SPARC_V8_full(i, True)
    return SPARC_Synthetic_renaming(s, i, toks)


def SPARC_Synthetic_renaming(s, i, toks=False):
    if i.mnemonic == "sethi" and i.operands[0] == cst(0, 22) and i.operands[1] == g0:
        return "nop"
    if (
        i.mnemonic == "or"
        and not i.misc["icc"]
        and i.operands[0] == i.operands[1] == g0
    ):
        replace_mnemonic_token(s,"clr")
        replace_opn_token(s,1,None)
        replace_opn_token(s,0,None)
    elif i.mnemonic == "or" and not i.misc["icc"] and i.operands[0] == g0:
        replace_mnemonic_token(s,"mov")
        replace_opn_token(s,0,None)
    elif i.mnemonic == "or" and not i.misc["icc"] and i.operands[0] == i.operands[2]:
        replace_mnemonic_token(s,"bset")
        replace_opn_token(s,0,None)
    elif i.mnemonic == "rd":
        op1 = str(i.operands[0])
        if op1.startswith("asr") or op1 in ("y", "psr", "wim", "tbr"):
            replace_mnemonic_token(s,"mov")
    elif i.mnemonic == "wr" and i.operands[0] == g0:
        replace_mnemonic_token(s,"mov")
        replace_opn_token(s,0,None)
    elif i.mnemonic == "sub" and i.misc["icc"] and i.operands[2] == g0:
        replace_mnemonic_token(s,"cmp")
        replace_opn_token(s,2,None)
    elif i.mnemonic == "jmpl" and i.operands[1] == g0:
        if i.operands[0] == (i7 + cst(8)):
            s = [(Token.Mnemonic, "ret")]
        elif i.operands[0] == (o7 + cst(8)):
            s = [(Token.Mnemonic, "retl")]
        else:
            replace_mnemonic_token(s,"jmp")
            replace_opn_token(s,1,None)
    elif i.mnemonic == "jmpl" and i.operands[1] == o7:
        replace_mnemonic_token(s,"call")
        replace_opn_token(s,1,None)
    elif (
        i.mnemonic == "or"
        and i.misc["icc"]
        and i.operands[1]._is_reg
        and i.operands[0] == i.operands[2] == g0
    ):
        replace_mnemonic_token(s,"tst")
        replace_opn_token(s,2,None)
        replace_opn_token(s,0,None)
    elif (
        i.mnemonic == "restore"
        and i.operands[0] == i.operands[1] == i.operands[2] == g0
    ):
        s = [(Token.Mnemonic, "restore")]
    if i.mnemonic == "save" and i.operands[0] == i.operands[1] == i.operands[2] == g0:
        s = [(Token.Mnemonic, "save")]
    if i.mnemonic == "xnor" and i.operands[1] == g0:
        replace_mnemonic_token(s,"not")
        replace_opn_token(s,1,None)
        if i.operands[0] == i.operands[2]:
            replace_opn_token(s,2,None)
    elif i.mnemonic == "sub" and i.operands[0] == g0 and i.operands[1]._is_reg:
        replace_mnemonic_token(s,"neg")
        replace_opn_token(s,0,None)
        if i.operands[1] == i.operands[2]:
            replace_opn_token(s,2,None)
    elif i.mnemonic == "add" and i.operands[0] == i.operands[2] and i.operands[1]._is_cst:
        m = "inccc" if i.misc["icc"] else "inc"
        replace_mnemonic_token(s,m)
        if i.operands[1] == 1:
            replace_opn_token(s,2,None)
            replace_opn_token(s,1,None)
        else:
            replace_opn_token(s,0,None)
    elif i.mnemonic == "sub" and i.operands[0] == i.operands[2] and i.operands[1]._is_cst:
        m = "deccc" if i.misc["icc"] else "dec"
        replace_mnemonic_token(s,m)
        if i.operands[1] == 1:
            replace_opn_token(s,2,None)
            replace_opn_token(s,1,None)
        else:
            replace_opn_token(s,0,None)
    elif i.mnemonic == "and" and i.misc["icc"] and i.operands[2] == g0:
        replace_mnemonic_token(s,"btst")
        replace_opn_token(s,2,None)
        s[1],s[3] = s[3],s[1]
    elif i.mnemonic == "andn" and not i.misc["icc"] and i.operands[0] == i.operands[2]:
        replace_mnemonic_token(s,"bclr")
        replace_opn_token(s,0,None)
    elif i.mnemonic == "xor" and not i.misc["icc"] and i.operands[0] == i.operands[2]:
        replace_mnemonic_token(s,"btog")
        replace_opn_token(s,0,None)
    elif i.mnemonic == "stb" and i.operands[0] == g0:
        replace_mnemonic_token(s,"clrb")
        replace_opn_token(s,0,None)
    elif i.mnemonic == "sth" and i.operands[0] == g0:
        replace_mnemonic_token(s,"clrh")
        replace_opn_token(s,0,None)
    elif i.mnemonic == "st" and i.operands[0] == g0:
        replace_mnemonic_token(s,"clr")
        replace_opn_token(s,0,None)
    return s if toks else highlight(s)
