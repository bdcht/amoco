# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *


def __npc(i_xxx):
    def npc(ins, fmap):
        fmap[pc] = fmap(pc) + ins.length
        i_xxx(ins, fmap)

    return npc


# i_xxx is the translation of eBPF instruction xxx.
# ------------------------------------------------------------------------------


@__npc
def i_add(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(dst + src)


@__npc
def i_sub(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(dst - src)


@__npc
def i_mul(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(dst * src)


@__npc
def i_div(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(dst / src)


@__npc
def i_or(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(dst | src)


@__npc
def i_xor(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(dst ^ src)


@__npc
def i_and(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(dst & src)


@__npc
def i_lsh(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(dst << src)


@__npc
def i_rsh(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(dst >> src)


@__npc
def i_arsh(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(oper(OP_ASR, dst, src))


@__npc
def i_neg(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(-src)


@__npc
def i_mod(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(dst % src)


@__npc
def i_mov(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(src)


@__npc
def i_ld(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(src).zeroextend(dst.size)


i_ldxb = i_ldxh = i_ldxw = i_ldxdw = i_ld
i_ldb = i_ldh = i_ldw = i_lddw = i_ld

i_stxb = i_stxh = i_stxw = i_stxdw = i_mov
i_stb = i_sth = i_stw = i_stdw = i_mov


@__npc
def i_end(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(src)


@__npc
def i_xadd(i, fmap):
    dst, src = i.operands
    fmap[dst] = fmap(dst + src)


def i_exit(i, fmap):
    fmap[pc] = top(pc.size)


@__npc
def i_call(i, fmap):
    cmd = i.misc["imm_ref"]
    cmd(fmap)


@__npc
def i_ja(i, fmap):
    dst, src, off = i.operands
    fmap[pc] = fmap(pc) + (off * 8)


@__npc
def i_jeq(i, fmap):
    dst, src, off = i.operands
    npc = fmap(pc) + (off * 8)
    fmap[pc] = tst(fmap(dst == src), npc, fmap(pc))


@__npc
def i_jgt(i, fmap):
    dst, src, off = i.operands
    npc = fmap(pc) + (off * 8)
    fmap[pc] = tst(fmap(oper(OP_LTU, src, dst)), npc, fmap(pc))


@__npc
def i_jge(i, fmap):
    dst, src, off = i.operands
    npc = fmap(pc) + (off * 8)
    fmap[pc] = tst(fmap(oper(OP_GEU, dst, src)), npc, fmap(pc))


@__npc
def i_jset(i, fmap):
    dst, src, off = i.operands
    npc = fmap(pc) + (off * 8)
    fmap[pc] = tst(fmap((dst & src) != 0), npc, fmap(pc))


@__npc
def i_jne(i, fmap):
    dst, src, off = i.operands
    npc = fmap(pc) + (off * 8)
    fmap[pc] = tst(fmap(dst != src), npc, fmap(pc))


@__npc
def i_jsgt(i, fmap):
    dst, src, off = i.operands
    npc = fmap(pc) + (off * 8)
    fmap[pc] = tst(fmap(dst > src), npc, fmap(pc))


@__npc
def i_jsge(i, fmap):
    dst, src, off = i.operands
    npc = fmap(pc) + (off * 8)
    fmap[pc] = tst(fmap(dst >= src), npc, fmap(pc))
