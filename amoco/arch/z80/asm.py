# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2012 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.arch.z80.env import *

# ------------------------------------------------------------------------------
# low level functions :
def _push_(fmap, _x):
    fmap[sp] = fmap[sp] - _x.length
    fmap[mem(sp, _x.size)] = _x


def _pop_(fmap, _l):
    fmap[_l] = fmap(mem(sp, _l.size))
    fmap[sp] = fmap[sp] + _l.length


def _push_cc(fmap, _cc, _x):
    fmap[sp] = tst(_cc, fmap[sp] - _x.length, None)
    fmap[mem(sp, _x.size)] = tst(_cc, _x, None)


def _pop_cc(fmap, _cc, _l):
    fmap[_l] = tst(_cc, fmap(mem(sp, _l.size)), None)
    fmap[sp] = tst(_cc, fmap[sp] + _l.length, None)


def __halfcarry__(_a, _b):
    return (_a[0:4] > 0xF) | (_b[0:4] > 0xF)


# i_xxx is the translation of z80 instruction xxx.
# ------------------------------------------------------------------------------

# general purpose and cpu-related:
##################################


def i_NOP(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length


def i_HALT(i_, fmap):
    fmap[pc] = ext("HALT", size=pc.size).call(fmap)


def i_STOP(i_, fmap):
    fmap[pc] = ext("STOP", size=pc.size).call(fmap)


def i_DI(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    fmap[iff1] = bit0
    fmap[iff2] = bit0


def i_EI(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    fmap[iff1] = bit1
    fmap[iff2] = bit1


# loads :
#########


def i_LD(i_, fmap):
    dst, src = i_.operands
    fmap[pc] = fmap[pc] + i_.length
    fmap[dst] = fmap(src)
    if (src == i) or (src == r):
        fmap[sf] = tst(fmap[src] < 0, bit1, bit0)
        fmap[zf] = tst(fmap[src] == 0, bit1, bit0)
        fmap[hf] = bit0
        fmap[nf] = bit0
        fmap[pf] = fmap[iff2]


def i_LDHL(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _x = fmap[sp] + i_.operands[1]
    fmap[hl] = _x
    fmap[zf] = bit0
    fmap[nf] = bit0
    fmap[cf] = tst(_x < fmap[sp], bit1, bit0)
    fmap[hf] = __halfcarry__(fmap(sp), i_.operands[1])


def i_PUSH(i_, fmap):
    src = i_.operands[0]
    fmap[pc] = fmap[pc] + i_.length
    _push_(fmap, fmap(src))


def i_POP(i_, fmap):
    dst = i_.operands[0]
    fmap[pc] = fmap[pc] + i_.length
    _pop_(fmap, dst)


def i_EX(i_, fmap):
    dst, src = i_.operands
    fmap[pc] = fmap[pc] + i_.length
    t = fmap(dst)
    fmap[dst] = fmap(src)
    fmap[src] = t


def i_EXX(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    for _x, x_ in ((bc, bc_), (de, de_), (hl, hl_)):
        t = fmap[_x]
        fmap[_x] = fmap[x_]
        fmap[x_] = t


def i_LDI(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst = fmap(mem(de, 8))
    fmap[dst] = fmap(mem(hl, 8))
    fmap[de] = fmap[de] + 1
    fmap[hl] = fmap[hl] + 1
    fmap[bc] = fmap[bc] - 1
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[pf] = tst(fmap[bc] != 0, bit1, bit0)


def i_LDIR(i_, fmap):
    i_ldi(i_, fmap)
    fmap[pf] = bit0
    if fmap[bc] != bit0:
        fmap[pc] = fmap[pc] - i_.length


def i_LDD(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst = fmap(mem(de, 8))
    fmap[dst] = fmap(mem(hl, 8))
    fmap[de] = fmap[de] - 1
    fmap[hl] = fmap[hl] - 1
    fmap[bc] = fmap[bc] - 1
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[pf] = tst(fmap[bc] != 0, bit1, bit0)


def i_LDDR(i_, fmap):
    i_ldd(i_, fmap)
    fmap[pf] = bit0
    if fmap[bc] != bit0:
        fmap[pc] = fmap[pc] - i_.length


def i_CPI(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _a = fmap(a)
    _b = fmap(mem(hl, 8))
    _x = _a - _b
    fmap[hl] = fmap[hl] + 1
    fmap[bc] = fmap[bc] - 1
    fmap[sf] = _x[7:8]
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[hf] = __halfcarry__(_a, _b)
    fmap[pf] = tst(fmap[bc] != 0, bit1, bit0)
    fmap[nf] = bit1


def i_CPIR(i_, fmap):
    i_cpi(i_, fmap)
    if fmap[zf] != 0 or fmap[pf] != 0:
        fmap[pc] = fmap[pc] - i_.length


def i_CPD(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _a = fmap(a)
    _b = fmap(mem(hl, 8))
    _x = _a - _b
    fmap[hl] = fmap[hl] - 1
    fmap[bc] = fmap[bc] - 1
    fmap[sf] = _x[7:8]
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[hf] = __halfcarry__(_a, _b)
    fmap[pf] = tst(fmap[bc] != 0, bit1, bit0)
    fmap[nf] = bit1


def i_CPDR(i_, fmap):
    i_cpd(i_, fmap)
    if fmap[zf] != 0 or fmap[pf] != 0:
        fmap[pc] = fmap[pc] - i_.length


def i_ADD(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst, src = i_.operands
    _a = fmap(dst)
    _b = fmap(src)
    _x = _a + _b
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[sf] = tst(_x < 0, bit1, bit0)
    fmap[cf] = tst(_x < _a, bit1, bit0)
    fmap[hf] = __halfcarry__(_a, _b)
    fmap[nf] = bit0
    fmap[dst] = _x


def i_ADC(i_, fmap):
    dst, src = i_.operands
    _c = fmap[cf]
    i_ADD(i_, fmap)
    _a = fmap(dst)
    _x = _a + tst(_c, cst(1, _a.size), cst(0, _a.size))
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[sf] = tst(_x < 0, bit1, bit0)
    fmap[cf] = tst(_x < _a, bit1, bit0)
    fmap[hf] = __halfcarry__(_a, _c)
    fmap[dst] = _x


def i_SUB(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    src = i_.operands[0]
    dst = a
    _a = fmap(a)
    _b = fmap(src)
    _x = _a - _b
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[sf] = tst(_x < 0, bit1, bit0)
    fmap[cf] = tst(_x > _a, bit1, bit0)
    fmap[hf] = __halfcarry__(_a, -_b)
    fmap[nf] = bit0
    fmap[dst] = _x


def i_SBC(i_, fmap):
    _c = fmap[cf]
    i_add(i_, fmap)
    _a = fmap(a)
    _x = _a - tst(_c, cst(1, _a.size), cst(0, _a.size))
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[sf] = tst(_x < 0, bit1, bit0)
    fmap[cf] = tst(_x < _a, bit1, bit0)
    fmap[hf] = __halfcarry__(_a, _c)
    fmap[dst] = _x


def i_AND(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    src = i_.operands[0]
    dst = a
    _a = fmap(a)
    _b = fmap(src)
    _x = _a & _b
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[sf] = tst(_x < 0, bit1, bit0)
    fmap[cf] = bit0
    fmap[hf] = bit1
    fmap[nf] = bit0
    fmap[dst] = _x


def i_OR(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    src = i_.operands[0]
    dst = a
    _a = fmap(a)
    _b = fmap(src)
    _x = _a | _b
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[sf] = tst(_x < 0, bit1, bit0)
    fmap[cf] = bit0
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[dst] = _x


def i_XOR(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    src = i_.operands[0]
    dst = a
    _a = fmap(a)
    _b = fmap(src)
    _x = _a ^ _b
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[sf] = tst(_x < 0, bit1, bit0)
    fmap[cf] = bit0
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[dst] = _x


def i_CP(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    src = i_.operands[0]
    _a = fmap(a)
    _b = fmap(src)
    _x = _a - _b
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[sf] = tst(_x < 0, bit1, bit0)
    fmap[cf] = tst(_x > _a, bit1, bit0)
    fmap[hf] = __halfcarry__(_a, -_b)
    fmap[nf] = bit1


def i_INC(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst = i_.operands[0]
    _a = fmap(dst)
    _x = _a + 1
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[sf] = tst(_x < 0, bit1, bit0)
    fmap[cf] = tst(_x < _a, bit1, bit0)
    fmap[hf] = __halfcarry__(_a, cst(1, 8))
    fmap[pf] = tst(_a == 0x7F, bit1, bit0)
    fmap[nf] = bit0
    fmap[dst] = _x


def i_DEC(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst = i_.operands[0]
    _a = fmap(dst)
    _x = _a - 1
    fmap[zf] = tst(_x == 0, bit1, bit0)
    fmap[sf] = tst(_x < 0, bit1, bit0)
    fmap[cf] = tst(_x > _a, bit1, bit0)
    fmap[hf] = __halfcarry__(_a, cst(-1, _a.size))
    fmap[pf] = tst(_a == 0x80, bit1, bit0)
    fmap[nf] = bit1
    fmap[dst] = _x


def i_DAA(i_, fmap):
    raise NotImplementedError


def i_CPL(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _a = fmap(a)
    fmap[hf] = bit1
    fmap[nf] = bit1
    fmap[a] = ~_a


def i_NEG(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _a = fmap(a)
    fmap[cf] = tst(_a != 0, bit1, bit0)
    fmap[pf] = tst(_a == 0x80, bit1, bit0)
    fmap[a] = -_a
    fmap[nf] = bit1
    fmap[zf] = tst(_a == 0, bit1, bit0)
    fmap[sf] = tst(_a < 0, bit1, bit0)


def i_CCF(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _c = fmap[cf]
    fmap[hf] = _c
    fmap[cf] = ~_c
    fmap[nf] = bit1


def i_SCF(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    fmap[cf] = bit1
    fmap[hf] = bit0
    fmap[nf] = bit0


def i_RLCA(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    fmap[cf] = fmap[a][7:8]
    fmap[a[1:8]] = fmap[a][0:7]
    fmap[a[0:1]] = fmap[cf]
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[zf] = tst(fmap[a] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[a] < 0, bit1, bit0)


def i_RLA(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _c = fmap[cf]
    fmap[cf] = fmap[a][7:8]
    fmap[a[1:8]] = fmap[a][0:7]
    fmap[a[0:1]] = _c
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[zf] = tst(fmap[a] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[a] < 0, bit1, bit0)


def i_RRCA(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    fmap[cf] = fmap[a][0:1]
    fmap[a[0:7]] = fmap[a][1:8]
    fmap[a[7:8]] = fmap[cf]
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[zf] = tst(fmap[a] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[a] < 0, bit1, bit0)


def i_RRA(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _c = fmap[cf]
    fmap[cf] = fmap[a][0:1]
    fmap[a[0:7]] = fmap[a][1:8]
    fmap[a[7:8]] = _c
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[zf] = tst(fmap[a] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[a] < 0, bit1, bit0)


def i_RLC(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst = i_.operands[0]
    fmap[cf] = fmap[dst][7:8]
    fmap[dst[1:8]] = fmap[dst][0:7]
    fmap[dst[0:1]] = fmap[cf]
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[zf] = tst(fmap[dst] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[dst] < 0, bit1, bit0)


def i_RL(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst = i_.operands[0]
    fmap[cf] = fmap[dst][7:8]
    fmap[dst[1:8]] = fmap[dst][0:7]
    fmap[dst[0:1]] = fmap[cf]
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[zf] = tst(fmap[dst] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[dst] < 0, bit1, bit0)


def i_RRC(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst = i_.operands[0]
    fmap[cf] = fmap[dst][0:1]
    fmap[dst[0:7]] = fmap[dst][1:8]
    fmap[dst[7:8]] = fmap[cf]
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[zf] = tst(fmap[dst] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[dst] < 0, bit1, bit0)


def i_RR(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst = i_.operands[0]
    fmap[cf] = fmap[dst][0:1]
    fmap[dst[0:7]] = fmap[dst][1:8]
    fmap[dst[7:8]] = fmap[cf]
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[zf] = tst(fmap[dst] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[dst] < 0, bit1, bit0)


def i_SLA(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst = i_.operands[0]
    fmap[cf] = fmap[dst][7:8]
    fmap[dst[1:8]] = fmap[dst][0:7]
    fmap[dst[0:1]] = bit0
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[zf] = tst(fmap[dst] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[dst] < 0, bit1, bit0)


def i_SLL(i_, fmap):
    i_SLA(i_, fmap)


def i_SRA(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst = i_.operands[0]
    fmap[cf] = fmap[dst][0:1]
    fmap[dst[0:7]] = fmap[dst][1:8]
    # dst[7:8] is unchanged
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[zf] = tst(fmap[dst] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[dst] < 0, bit1, bit0)


def i_SRL(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    dst = i_.operands[0]
    fmap[cf] = fmap[dst][0:1]
    fmap[dst[0:7]] = fmap[dst][1:8]
    fmap[dst[7:8]] = bit0
    fmap[hf] = bit0
    fmap[nf] = bit0
    fmap[zf] = tst(fmap[dst] == 0, bit1, bit0)
    fmap[sf] = bit0


def i_RLD(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _l = mem(hl, 8)
    _b = fmap[_l]
    fmap[_l[0:4]] = fmap[a[0:4]]
    fmap[a[0:4]] = _b[4:8]
    fmap[_l[4:8]] = _b[0:4]
    fmap[zf] = tst(fmap[a] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[a] < 0, bit1, bit0)
    fmap[hf] = bit0
    fmap[nf] = bit0


def i_RRD(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _l = mem(hl, 8)
    _b = fmap[_l]
    fmap[_l[4:8]] = fmap[a[0:4]]
    fmap[a[0:4]] = _b[0:4]
    fmap[_l[0:4]] = _b[4:8]
    fmap[zf] = tst(fmap[a] == 0, bit1, bit0)
    fmap[sf] = tst(fmap[a] < 0, bit1, bit0)
    fmap[hf] = bit0
    fmap[nf] = bit0


def i_BIT(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _b, _r = i_.operands
    fmap[zf] = tst(slc(fmap[_r], _b, _b + 1), bit1, bit0)
    fmap[hf] = bit1
    fmap[nf] = bit0


def i_SET(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _b, _r = i_.operands
    fmap[slc(_r, _b, _b + 1)] = bit1


def i_RES(i_, fmap):
    fmap[pc] = fmap[pc] + i_.length
    _b, _r = i_.operands
    fmap[slc(_r, _b, _b + 1)] = bit0


def i_JP(i_, fmap):
    src = i_.operands[0]
    fmap[pc] = fmap(src)


def i_JPcc(i_, fmap):
    src = i_.operands[1]
    fmap[pc] = tst(i_.cond[1], fmap(src), fmap[pc] + i_.length)


def i_JR(i_, fmap):
    src = i_.operands[0]
    fmap[pc] = fmap[pc] + i_.length
    fmap[pc] = fmap[pc] + fmap(src)


def i_JRcc(i_, fmap):
    src = i_.operands[1]
    fmap[pc] = fmap[pc] + i_.length
    fmap[pc] = tst(i_.cond[1], fmap[pc] + fmap(src), fmap[pc])


def i_DJNZ(i_, fmap):
    src = i_.operands[0]
    _b = fmap[b]
    fmap[pc] = fmap[pc] + i_.length
    fmap[pc] = tst(_b != 0, fmap[pc] + fmap(src), fmap[pc])


# call and rets :
#################


def i_CALL(i_, fmap):
    src = i_.operands[0]
    _push_(fmap, fmap[pc] + i_.length)
    fmap[pc] = fmap(src)


def i_CALLcc(i_, fmap):
    src = i_.operands[1]
    _back = fmap[pc] + i_.length
    _push_cc(fmap, i_.cond[1], _back)
    fmap[pc] = tst(i_.cond[1], fmap(src), _back)


def i_RET(i_, fmap):
    _pop_(fmap, pc)


def i_RETcc(i_, fmap):
    _back = fmap[pc] + i_.length
    _pop_cc(fmap, i_.cond[1], _back)


def i_RETI(i_, fmap):
    _pop_(fmap, pc)


def i_RETN(i_, fmap):
    fmap[iff1] = fmap[iff2]
    _pop_(fmap, pc)


def i_RST(i_, fmap):
    src = i_.operands[0]
    _push_(fmap, pc)
    fmap[pc] = src.zeroextend(16)


# def i_IN(i_,fmap):
#  pass
# def i_INI(i_,fmap):
#  pass
# def i_INIR(i_,fmap):
#  pass
# def i_IND(i_,fmap):
#  pass
# def i_INDR(i_,fmap):
#  pass
# def i_OUT(i_,fmap):
#  pass
# def i_OUTI(i_,fmap):
#  pass
# def i_OTIR(i_,fmap):
#  pass
# def i_OUTD(i_,fmap):
#  pass
# def i_OTDR(i_,fmap):
#  pass
