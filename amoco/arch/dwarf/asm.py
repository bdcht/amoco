# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.arch.dwarf.env import *

# ------------------------------------------------------------------------------
# low level functions :
def _push_(fmap, x):
    assert x.size == WORD
    fmap[stack_elt] = fmap[stack_elt] + 1
    fmap[sp] = fmap[sp] - (WORD // 8)
    fmap[mem(sp, x.size)] = x


def _pop_(fmap):
    x = fmap(mem(sp, WORD))
    fmap[sp] = fmap[sp] + (WORD // 8)
    fmap[stack_elt] = fmap[stack_elt] - 1
    return x


def __pc(f):
    def pcnpc(i, fmap):
        fmap[op_ptr] = fmap[op_ptr] + i.length
        f(i, fmap)

    return pcnpc


# ixxx is the translation of DWARF instruction xxx.
# ------------------------------------------------------------------------------


@__pc
def i_DW_OP_skip(i, fmap):
    fmap[op_ptr] = fmap(op_ptr + i.operands[0])


@__pc
def i_DW_OP_bra(i, fmap):
    cond = _pop_(fmap)
    fmap[op_ptr] = tst(cond != 0, fmap(op_ptr + i.operands[0]), fmap(op_ptr))


@__pc
def i_DW_OP_nop(i, fmap):
    pass


@__pc
def i_DW_OP_lit(i, fmap):
    _push_(fmap, i.operands[0])


@__pc
def i_DW_OP_addr(i, fmap):
    _push_(fmap, i.operands[0])


@__pc
def i_DW_OP_GNU_encoded_addr(i, fmap):
    _push_(fmap, i.operands[0])


@__pc
def i_DW_OP_const(i, fmap):
    _push_(fmap, i.operands[0])


@__pc
def i_DW_OP_reg(i, fmap):
    _push_(fmap, fmap(i.operands[0]))


@__pc
def i_DW_OP_regx(i, fmap):
    _push_(fmap, fmap(i.operands[0]))


@__pc
def i_DW_OP_breg(i, fmap):
    _push_(fmap, fmap(i.operands[0]))


@__pc
def i_DW_OP_bregx(i, fmap):
    _push_(fmap, fmap(i.operands[0]))


@__pc
def i_DW_OP_dup(i, fmap):
    x = fmap(mem(sp, WORD))
    _push_(fmap, x)


@__pc
def i_DW_OP_drop(i, fmap):
    _pop_(fmap)


@__pc
def i_DW_OP_pick(i, fmap):
    index = i.operands[0] * (WORD // 8)
    x = fmap(mem(sp + index, WORD))
    _push_(fmap, x)


@__pc
def i_DW_OP_over(i, fmap):
    index = WORD // 8
    x = fmap(mem(sp + index, WORD))
    _push_(fmap, x)


@__pc
def i_DW_OP_swap(i, fmap):  # [x,y,...] -> [y,x,...]
    index = WORD // 8
    x = fmap(mem(sp, WORD))
    y = fmap(mem(sp + index, WORD))
    fmap[mem(sp, WORD)] = y
    fmap[mem(sp + index, WORD)] = x


@__pc
def i_DW_OP_rot(i, fmap):  # [x,y,z,...] -> [y,z,x,...]
    index = WORD // 8
    x = fmap(mem(sp, WORD))
    y = fmap(mem(sp + index, WORD))
    z = fmap(mem(sp + index + index, WORD))
    fmap[mem(sp, WORD)] = y
    fmap[mem(sp + index, WORD)] = z
    fmap[mem(sp + index + index, WORD)] = x


@__pc
def i_DW_OP_deref(i, fmap):
    x = _pop_(fmap)
    _push_(fmap, fmap[mem(x, WORD)])


@__pc
def i_DW_OP_deref_size(i, fmap):
    x = _pop_(fmap)
    size = i.operands[0] * 8
    result = fmap[mem(x, size)].zeroextend(WORD)
    _push_(fmap, result)


@__pc
def i_DW_OP_abs(i, fmap):
    x = _pop_(fmap)
    result = tst(x[WORD - 1 : WORD] == 1, -x, x)
    _push_(fmap, result)


@__pc
def i_DW_OP_abs(i, fmap):
    x = _pop_(fmap)
    _push_(fmap, -x)


@__pc
def i_DW_OP_not(i, fmap):
    x = _pop_(fmap)
    _push_(fmap, ~x)


@__pc
def i_DW_OP_plus_uconst(i, fmap):
    x = _pop_(fmap)
    _push_(fmap, x + i.operands[0])


@__pc
def i_DW_OP_and(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    _push_(fmap, x & y)


@__pc
def i_DW_OP_div(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    _push_(fmap, x / y)


@__pc
def i_DW_OP_minus(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    _push_(fmap, x - y)


@__pc
def i_DW_OP_mod(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    _push_(fmap, x % y)


@__pc
def i_DW_OP_mul(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    _push_(fmap, x * y)


@__pc
def i_DW_OP_or(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    _push_(fmap, x | y)


@__pc
def i_DW_OP_plus(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    _push_(fmap, x + y)


@__pc
def i_DW_OP_shl(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    _push_(fmap, x << y)


@__pc
def i_DW_OP_shr(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    _push_(fmap, x >> y)


@__pc
def i_DW_OP_shra(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    _push_(fmap, x // y)


@__pc
def i_DW_OP_xor(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    _push_(fmap, x ^ y)


@__pc
def i_DW_OP_le(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    t = (x <= y).zeroextend(WORD)
    _push_(fmap, t)


@__pc
def i_DW_OP_ge(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    t = (x >= y).zeroextend(WORD)
    _push_(fmap, t)


@__pc
def i_DW_OP_eq(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    t = (x == y).zeroextend(WORD)
    _push_(fmap, t)


@__pc
def i_DW_OP_lt(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    t = (x < y).zeroextend(WORD)
    _push_(fmap, t)


@__pc
def i_DW_OP_gt(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    t = (x > y).zeroextend(WORD)
    _push_(fmap, t)


@__pc
def i_DW_OP_neq(i, fmap):
    y = _pop_(fmap)
    x = _pop_(fmap)
    t = (x != y).zeroextend(WORD)
    _push_(fmap, t)
