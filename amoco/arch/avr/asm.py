# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.arch.avr.env import *
from amoco.cas.mapper import mapper

# ------------------------------------------------------------------------------
# low level functions :
def _push_(fmap, x):
    fmap[sp] = fmap[sp] - x.length
    fmap[mem(sp, x.size)] = x


def _pop_(fmap, _l):
    fmap[_l] = fmap(mem(sp, _l.size))
    fmap[sp] = fmap[sp] + _l.length


def __pc(f):
    def pcnpc(i, fmap):
        fmap[pc] = fmap[pc] + i.length
        if len(fmap.conds) > 0:
            cond = fmap.conds.pop()
            m = mapper()
            f(i, m)
            for l, v in m:
                fmap[l] = tst(cond, v, fmap(l))
        else:
            f(i, fmap)

    return pcnpc


def __nopc(f):
    return f.__closure__[0].cell_contents


def __nopc(f):
    return f.__closure__[0].cell_contents

# flags for arithmetic operations:
def __setflags__A(i, fmap, a, b, x, neg=False):
    fmap[zf] = x == 0
    fmap[nf] = x.bit(7)
    if neg:
        a, x = ~a, ~x
    fmap[cf] = (
        ((a.bit(7)) & (b.bit(7)))
        | ((b.bit(7)) & (~x.bit(7)))
        | ((a.bit(7)) & (~x.bit(7)))
    )
    fmap[vf] = ((a.bit(7)) & (b.bit(7)) & (~x.bit(7))) | (
        (~a.bit(7)) & (~b.bit(7)) & (x.bit(7))
    )
    fmap[sf] = fmap[nf] ^ fmap[vf]
    fmap[hf] = (
        ((a.bit(3)) & (b.bit(3)))
        | ((b.bit(3)) & (~x.bit(3)))
        | ((a.bit(3)) & (~x.bit(3)))
    )


# flags for logical operations:
def __setflags__L(i, fmap, a, b, x):
    fmap[zf] = x == 0
    fmap[nf] = x.bit(7)
    fmap[vf] = bit0
    fmap[sf] = fmap[nf] ^ fmap[vf]


# flags for shift operations:
def __setflags__S(i, fmap, a, x):
    # cf must be set before calling this function.
    fmap[zf] = x == 0
    fmap[nf] = x.bit(7)
    fmap[vf] = fmap[nf] ^ fmap[cf]
    fmap[sf] = fmap[nf] ^ fmap[vf]


# ixxx is the translation of AVR instruction xxx.
# ------------------------------------------------------------------------------


@__pc
def i_NOP(i, fmap):
    pass


def i_SLEEP(i, fmap):
    fmap[pc] = ext("SLEEP", size=pc.size).call(fmap)


def i_BREAK(i, fmap):
    fmap[pc] = ext("BREAK", size=pc.size).call(fmap)


def i_IN(i, fmap):
    r, port = i.operands
    fmap[pc] = ext("IN", size=pc.size).call(fmap)


def i_OUT(i, fmap):
    port, r = i.operands
    fmap[pc] = ext("OUT", size=pc.size).call(fmap)


# arithmetic & logic instructions:
##################################


@__pc
def i_ADD(i, fmap):
    dst, src = i.operands
    a = fmap(dst)
    b = fmap(src)
    x = a + b
    __setflags__A(i, fmap, a, b, x)
    fmap[dst] = x


@__pc
def i_ADIW(i, fmap):
    dst, src = i.operands
    if i.misc["W"]:
        assert dst is R[24]
        a = fmap(composer([dst, R[25]]))
    else:
        a = fmap(dst)
    b = fmap(src)
    x = a + b
    __setflags__A(i, fmap, a, b, x)
    fmap[dst] = x[0 : dst.size]
    if i.misc["W"]:
        assert x.size == 16
        fmap[R[25]] = x[8:16]


@__pc
def i_ADC(i, fmap):
    dst, src = i.operands
    _c = fmap[cf]
    __nopc(i_ADD)(i, fmap)
    a = fmap(dst)
    b = tst(_c, cst(1, a.size), cst(0, a.size))
    x = a + b
    __setflags__A(i, fmap, a, b, x)
    fmap[dst] = x


@__pc
def i_INC(i, fmap):
    dst = i.operands[0]
    a = fmap(dst)
    b = cst(1, dst.size)
    x = a + b
    fmap[zf] = x == 0
    fmap[nf] = x.bit(7)
    fmap[vf] = a == cst(0x7F, 8)
    fmap[sf] = fmap[nf] ^ fmap[vf]
    fmap[dst] = x


@__pc
def i_CP(i, fmap):
    dst, src = i.operands
    a = fmap(dst)
    b = fmap(src)
    x = a - b
    __setflags__A(i, fmap, a, b, x, neg=True)


@__pc
def i_CPSE(i, fmap):
    rd, rr = i.operands
    fmap.conds[fmap(rd == rr)]


@__pc
def i_SBRC(i, fmap):
    b = i.operands[0]
    fmap.conds[fmap(b == bit0)]


@__pc
def i_SBRS(i, fmap):
    b = i.operands[0]
    fmap.conds[fmap(b == bit1)]


@__pc
def i_SUB(i, fmap):
    dst, src = i.operands
    a = fmap(dst)
    b = fmap(src)
    x = a - b
    __setflags__A(i, fmap, a, b, x, neg=True)
    fmap[dst] = x


i_SUBI = i_SUB


@__pc
def i_SBIW(i, fmap):
    dst, src = i.operands
    if i.misc["W"]:
        assert dst is R[24]
        a = fmap(composer([dst, R[25]]))
    else:
        a = fmap(dst)
    b = fmap(src)
    x = a - b
    __setflags__A(i, fmap, a, b, x, neg=True)
    fmap[dst] = x[0 : dst.size]
    if i.misc["W"]:
        assert x.size == 16
        fmap[R[25]] = x[8:16]


@__pc
def i_COM(i, fmap):
    dst, src = i.operands
    a = cst(0xFF, 8)
    b = fmap(dst)
    x = a - b
    __setflags__A(i, fmap, a, b, x, neg=True)
    fmap[dst] = x


@__pc
def i_NEG(i, fmap):
    dst = i.operands[0]
    a = cst(0, dst.size)
    b = fmap(dst)
    x = a - b
    __setflags__A(i, fmap, a, b, x, neg=True)
    fmap[dst] = x


@__pc
def i_DEC(i, fmap):
    dst = i.operands[0]
    a = fmap(dst)
    b = cst(1, dst.size)
    x = a - b
    fmap[zf] = x == 0
    fmap[nf] = x.bit(7)
    fmap[vf] = a == cst(0x80, 8)
    fmap[sf] = fmap[nf] ^ fmap[vf]
    fmap[dst] = x


@__pc
def i_CPC(i, fmap):
    dst, src = i.operands
    a = fmap(dst)
    b = fmap(src)
    _c = fmap[cf]
    __nopc(i_CP)(i, fmap)
    a = fmap(a - b)
    b = tst(_c, cst(1, a.size), cst(0, a.size))
    x = a - b
    __setflags__A(i, fmap, a, b, x, neg=True)


@__pc
def i_SBC(i, fmap):
    dst, src = i.operands
    _c = fmap[cf]
    __nopc(i_SUB)(i, fmap)
    a = fmap(dst)
    b = tst(_c, cst(1, a.size), cst(0, a.size))
    x = a - b
    __setflags__A(i, fmap, a, b, x, neg=True)
    fmap[dst] = x


i_SBCI = i_SBC


@__pc
def i_AND(i, fmap):
    dst, src = i.operands
    a = fmap(dst)
    b = fmap(src)
    x = a & b
    __setflags__L(i, fmap, a, b, x)
    fmap[dst] = x


i_ANDI = i_AND


@__pc
def i_OR(i, fmap):
    dst, src = i.operands
    a = fmap(dst)
    b = fmap(src)
    x = a | b
    __setflags__L(i, fmap, a, b, x)
    fmap[dst] = x


i_ORI = i_OR


@__pc
def i_EOR(i, fmap):
    dst, src = i.operands
    a = fmap(dst)
    b = fmap(src)
    x = a ^ b
    __setflags__L(i, fmap, a, b, x)
    fmap[dst] = x


@__pc
def i_MUL(i, fmap):
    dst, src = i.operands
    a = fmap(dst)
    b = fmap(src)
    x = a ** b
    fmap[cf] = x[15:16]
    fmap[zf] = x == 0
    fmap[R[0]] = x[0:8]
    fmap[R[1]] = x[8:16]


# shift/rotate instructions:
############################


@__pc
def i_LSL(i, fmap):
    dst = i.operands[0]
    a = fmap(dst)
    fmap[cf] = a.bit(7)
    x = a << 1
    __setflags__S(i, fmap, a, x)
    fmap[dst] = x


@__pc
def i_LSR(i, fmap):
    dst = i.operands[0]
    a = fmap(dst)
    fmap[cf] = a.bit(0)
    x = a >> 1
    __setflags__S(i, fmap, a, x)
    fmap[dst] = x


@__pc
def i_ASR(i, fmap):
    dst = i.operands[0]
    a = fmap(dst)
    fmap[cf] = a.bit(0)
    x = a & 0x80
    x |= a >> 1
    __setflags__S(i, fmap, a, x)
    fmap[dst] = x


@__pc
def i_ROL(i, fmap):
    dst = i.operands[0]
    a = fmap(dst)
    c = fmap[cf].zeroextend(a.size)
    fmap[cf] = a.bit(7)
    x = a << 1
    x |= c
    __setflags__S(i, fmap, a, x)
    fmap[dst] = x


@__pc
def i_ROR(i, fmap):
    dst = i.operands[0]
    a = fmap(dst)
    c = fmap[cf]
    fmap[cf] = a.bit(0)
    x = composer([cst(0, 7), c])
    x |= a >> 1
    __setflags__S(i, fmap, a, x)
    fmap[dst] = x


# bit instructions:
###################


@__pc
def i_SWAP(i, fmap):
    b = i.operands[0]
    x = fmap(b)
    fmap[b] = composer([x[4:8], x[0:4]])


@__pc
def i_BCLR(i, fmap):
    b = i.operands[0]
    fmap[b] = bit0


@__pc
def i_BSET(i, fmap):
    b = i.operands[0]
    fmap[b] = bit1


@__pc
def i_BST(i, fmap):
    b = i.operands[0]
    fmap[tf] = fmap(b)


@__pc
def i_BLD(i, fmap):
    b = i.operands[0]
    fmap[b] = fmap(tf)


# stack instructions:
#####################


@__pc
def i_POP(i, fmap):
    dst = i.operands[0]
    _pop_(fmap, dst)


@__pc
def i_PUSH(i, fmap):
    src = i.operands[0]
    _push_(fmap, src)


# load-store instructions:
##########################


@__pc
def i_LD(i, fmap):
    dst, src = i.operands
    if i.misc["flg"] == -1:
        fmap[src] = fmap(src - 1)
    fmap[dst] = fmap(mem(src, dst.size))
    if i.misc["flg"] == 1:
        fmap[src] = fmap(src + 1)


i_LDS = i_LD
i_LDD = i_LD


@__pc
def i_ST(i, fmap):
    dst, src = i.operands
    if i.misc["flg"] == -1:
        fmap[dst] = fmap(dst - 1)
    adr = fmap(dst)
    fmap[ptr(adr)] = fmap(src)
    if i.misc["flg"] == 1:
        fmap[dst] = fmap(dst + 1)


i_STS = i_ST
i_STD = i_ST


@__pc
def i_MOV(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(src)


i_LDI = i_MOV


@__pc
def i_MOVW(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(src)
    nd = R[R.index(dst) + 1]
    nr = R[R.index(src) + 1]
    fmap[nd] = fmap(nr)


@__pc
def i_SPM(i, fmap):
    fmap[mem(Z, 16)] = fmap(composer([R[0], R[1]]))


@__pc
def i_LPM(i, fmap):
    try:
        dst, src = i.operands
    except ValueError:
        dst, src = R[0], Z
    fmap[dst] = fmap(Z)
    if i.misc["flg"] == 1:
        fmap[Z] = fmap(Z + 1)


# control-flow instructions:
############################


@__pc
def i_BRBC(i, fmap):
    b, offset = i.operands
    fmap[pc] = fmap(tst(b == bit0, pc + (2 * offset), pc))


@__pc
def i_BRBS(i, fmap):
    b, offset = i.operands
    fmap[pc] = fmap(tst(b == bit1, pc + (2 * offset), pc))


@__pc
def i_CALL(i, fmap):
    adr = i.operands[0]
    _push_(fmap, fmap(pc))
    fmap[pc] = fmap(2 * adr)


@__pc
def i_JMP(i, fmap):
    adr = i.operands[0]
    fmap[pc] = fmap(2 * adr)


@__pc
def i_RET(i, fmap):
    _pop_(fmap, pc)


@__pc
def i_RETI(i, fmap):
    _pop_(fmap, pc)
    fmap[i_] = bit1


@__pc
def i_RCALL(i, fmap):
    offset = i.operands[0]
    _push_(fmap, fmap(pc))
    fmap[pc] = fmap(pc + (2 * offset))


@__pc
def i_RJMP(i, fmap):
    offset = i.operands[0]
    fmap[pc] = fmap(pc + (2 * offset))


@__pc
def i_EICALL(i, fmap):
    raise NotImplementedError


@__pc
def i_EIJMP(i, fmap):
    raise NotImplementedError


@__pc
def i_ICALL(i, fmap):
    _push_(fmap, fmap(pc))
    fmap[pc] = fmap(Z)


@__pc
def i_IJMP(i, fmap):
    fmap[pc] = fmap(Z)
