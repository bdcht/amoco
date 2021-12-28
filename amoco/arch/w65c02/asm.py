# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *
from amoco.cas.utils import *

# ------------------------------------------------------------------------------
# helpers and decorators :
def _push8(fmap, _x):
    assert _x.size==8
    fmap[mem(sp_, 8)] = _x
    fmap[sp] = fmap(sp - 1)


def _pop8(fmap, _l):
    assert _l.size==8
    fmap[sp] = fmap(sp + 1)
    fmap[_l] = fmap(mem(sp_, 8))

def _push16(fmap, _x):
    assert _x.size==16
    fmap[sp] = fmap(sp - 1)
    fmap[mem(sp_, 16)] = _x
    fmap[sp] = fmap(sp - 1)

def _pop16(fmap, _l):
    assert _l.size==16
    fmap[sp] = fmap(sp + 1)
    fmap[_l] = fmap(mem(sp_, 16))
    fmap[sp] = fmap(sp + 1)

def __npc(i_xxx):
    def npc(ins, fmap):
        fmap[pc] = fmap(pc) + ins.length
        i_xxx(ins, fmap)
    return npc

def overflow(res,a,v):
    return ((res^a) & (res^v))[7:8]

def get_op_16(i,fmap):
    return fmap(i.operands[0]).zeroextend(16)

# i_xxx is the translation of W65C02(S) instruction xxx.
# ------------------------------------------------------------------------------

@__npc
def i_ADC(i,fmap):
    c = fmap(C).zeroextend(16)
    a = fmap(A_)
    v = get_op_16(i,fmap)
    res = a+v+c
    fmap[Z] = res==0
    fmap[V] = overflow(res,a,v)
    fmap[N] = Sign(res)
    c = ~D&((res&0xff00)!=0)
    a = fmap(A)
    cond = tst(a[0:4]>9, a+6, a)[4:8]>9
    fmap[C] = tst(D&cond,bit1,c)
    fmap[A] = res[0:8]

@__npc
def i_AND(i,fmap):
    res = fmap(i.operands[0]&A)
    fmap[N] = res[7:8]
    fmap[Z] = res==0
    fmap[A] = res

@__npc
def i_ASL(i,fmap):
    dst = i.operands[0]
    res = get_op_16(i,fmap)<<1
    fmap[C] = res[8:16]>0
    fmap[N] = res[7:8]
    fmap[Z] = res[0:8]==0
    fmap[dst] = res[0:8]

@__npc
def i_BCC(i,fmap):
    reladdr = i.operands[0]
    fmap[pc] = fmap(tst(C==bit0,pc+reladdr,pc))

@__npc
def i_BCS(i,fmap):
    reladdr = i.operands[0]
    fmap[pc] = fmap(tst(C==bit1,pc+reladdr,pc))

@__npc
def i_BEQ(i,fmap):
    reladdr = i.operands[0]
    fmap[pc] = fmap(tst(Z==bit1,pc+reladdr,pc))

@__npc
def i_BIT(i,fmap):
    val = fmap(i.operands[0])
    fmap[V] = val[6:7]
    fmap[N] = Sign(val)
    fmap[Z] = (fmap(A)&val)==0

@__npc
def i_BMI(i,fmap):
    reladdr = i.operands[0]
    fmap[pc] = fmap(tst(N==bit1,pc+reladdr,pc))

@__npc
def i_BNE(i,fmap):
    reladdr = i.operands[0]
    fmap[pc] = fmap(tst(Z==bit0,pc+reladdr,pc))

@__npc
def i_BPL(i,fmap):
    reladdr = i.operands[0]
    fmap[pc] = fmap(tst(N==bit0,pc+reladdr,pc))

@__npc
def i_BRA(i,fmap):
    reladdr = i.operands[0]
    fmap[pc] = pc+reladdr

def i_BRK(i,fmap):
    _push16(fmap,fmap[pc]+1)
    _push8(fmap,fmap(P|0x10))
    fmap[D] = bit0
    fmap[B] = bit1
    fmap[pc] = fmap(mem(IRQ_VECTOR,16))

@__npc
def i_BVC(i,fmap):
    reladdr = i.operands[0]
    fmap[pc] = fmap(tst(V==bit0,pc+reladdr,pc))

@__npc
def i_BVS(i,fmap):
    reladdr = i.operands[0]
    fmap[pc] = fmap(tst(V==bit1,pc+reladdr,pc))

@__npc
def i_CLC(i,fmap):
    fmap[C] = bit0

@__npc
def i_CLD(i,fmap):
    fmap[D] = bit0

@__npc
def i_CLI(i,fmap):
    fmap[I] = bit0

@__npc
def i_CLV(i,fmap):
    fmap[V] = bit0

@__npc
def i_CMP(i,fmap):
    v = get_op_16(i,fmap)
    a = fmap(A)
    fmap[S] = (a.zeroextend(16) - v)[7:8]
    fmap[C] = (a>=v[0:8])
    fmap[Z] = (a==v[0:8])

@__npc
def i_CPX(i,fmap):
    v = get_op_16(i,fmap)
    a = fmap(X)
    fmap[S] = (a.zeroextend(16) - v)[7:8]
    fmap[C] = (a>=v[0:8])
    fmap[Z] = (a==v[0:8])

@__npc
def i_CPY(i,fmap):
    v = get_op_16(i,fmap)
    a = fmap(Y)
    fmap[S] = (a.zeroextend(16) - v)[7:8]
    fmap[C] = (a>=v[0:8])
    fmap[Z] = (a==v[0:8])

@__npc
def i_DEC(i,fmap):
    dst = src = i.operands[0]
    val = fmap(src)
    res = val-1
    fmap[dst] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_DEX(i,fmap):
    dst = src = X
    val = fmap(src)
    res = val-1
    fmap[dst] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_DEY(i,fmap):
    dst = src = Y
    val = fmap(src)
    res = val-1
    fmap[dst] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_EOR(i,fmap):
    val = fmap(i.operands[0])
    res = val^fmap(A_)
    fmap[Z] = res==0
    fmap[N] = Sign(res)
    fmap[A] = res

@__npc
def i_INC(i,fmap):
    dst = src = i.operands[0]
    val = fmap(src)
    res = val+1
    fmap[dst] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_INX(i,fmap):
    dst = src = X
    val = fmap(src)
    res = val+1
    fmap[dst] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_INY(i,fmap):
    dst = src = X
    val = fmap(src)
    res = val+1
    fmap[dst] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

def i_JMP(i,fmap):
    fmap[pc] = fmap(i.operands[0])

@__npc
def i_JSR(i,fmap):
    _push16(fmap,fmap(pc-1)) # not an error ;)
    fmap[pc] = fmap(i.operands[0])

@__npc
def i_LDA(i,fmap):
    res = fmap(i.operands[0])
    fmap[A] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_LDX(i,fmap):
    res = fmap(i.operands[0])
    fmap[X] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_LDY(i,fmap):
    res = fmap(i.operands[0])
    fmap[Y] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_LSR(i,fmap):
    dst = src = i.operands[0]
    val = fmap(src)
    fmap[C] = val[0:1]
    res = val>>1
    fmap[dst] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_NOP(i,fmap):
    pass

@__npc
def i_ORA(i,fmap):
    res = fmap(A|i.operands[0])
    fmap[Z] = res==0
    fmap[N] = Sign(res)
    fmap[A] = res

@__npc
def i_PHA(i,fmap):
    _push8(fmap,fmap(A))

@__npc
def i_PHP(i,fmap):
    _push8(fmap,fmap(P|0x10))

@__npc
def i_PHY(i,fmap):
    _push8(fmap,fmap(Y))

@__npc
def i_PHX(i,fmap):
    _push8(fmap,fmap(X))

@__npc
def i_PLA(i,fmap):
    _pop8(fmap,A)
    a = fmap(A)
    fmap[Z] = a==0
    fmap[N] = Sign(a)

@__npc
def i_PLP(i,fmap):
    _pop8(fmap,P)
    fmap[P] = fmap(P)|0x20

@__npc
def i_PLX(i,fmap):
    _pop8(fmap,X)

@__npc
def i_PLY(i,fmap):
    _pop8(fmap,Y)

@__npc
def i_ROL(i,fmap):
    dst = i.operands[0]
    val = get_op_16(i,fmap)<<1
    res = val|(fmap(C).zeroextend(16))
    fmap[dst] = res[0:8]
    fmap[C] = val[8:9]
    fmap[Z] = res[0:8]==0
    fmap[N] = Sign(res)

@__npc
def i_ROR(i,fmap):
    dst = i.operands[0]
    val = get_op_16(i,fmap)
    res = (val>>1)|(fmap(C).zeroextend(16)<<7)
    fmap[dst] = res[0:8]
    fmap[C] = val[0:1]
    fmap[Z] = res[0:8]==0
    fmap[N] = Sign(res)

def i_RTI(i,fmap):
    _pop8(fmap,P)
    _pop16(fmap,pc)

def i_RTS(i,fmap):
    _pop16(fmap,pc)
    fmap[pc] = fmap(pc)+1

@__npc
def i_SBC(i,fmap):
    c = fmap(C).zeroextend(16)
    a = fmap(A_)
    v = get_op_16(i,fmap)^0x00ff
    res = a+v+c
    fmap[Z] = res==0
    fmap[V] = overflow(res,a,v)
    fmap[N] = Sign(res)
    c = ~D&((res&0xff00)!=0)
    a = fmap(A)-0x66
    cond = tst(a[0:4]>9, a+6, a)[4:8]>9
    fmap[C] = tst(D&cond,bit1,c)
    fmap[A] = res[0:8]

@__npc
def i_SEC(i,fmap):
    fmap[C] = bit1

@__npc
def i_SED(i,fmap):
    fmap[D] = bit1

@__npc
def i_SEI(i,fmap):
    fmap[I] = bit1

@__npc
def i_STA(i,fmap):
    fmap[i.operands[0]] = fmap(A)

@__npc
def i_STX(i,fmap):
    fmap[i.operands[0]] = fmap(X)

@__npc
def i_STY(i,fmap):
    fmap[i.operands[0]] = fmap(Y)

@__npc
def i_STZ(i,fmap):
    fmap[i.operands[0]] = cst(0,8)

@__npc
def i_TAX(i,fmap):
    res = fmap(A)
    fmap[X] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_TAY(i,fmap):
    res = fmap(A)
    fmap[Y] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_TRB(i,fmap):
    raise NotImplementedError

@__npc
def i_TSB(i,fmap):
    raise NotImplementedError

@__npc
def i_TSX(i,fmap):
    res = fmap(sp)
    fmap[X] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_TXA(i,fmap):
    res = fmap(X)
    fmap[A] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

@__npc
def i_TXS(i,fmap):
    res = fmap(X)
    fmap[sp] = res
    # no update of Z & N

@__npc
def i_TYA(i,fmap):
    res = fmap(Y)
    fmap[A] = res
    fmap[Z] = res==0
    fmap[N] = Sign(res)

def bbrx(n,i,fmap):
    cond = i.operands[0]
    reladdr = i.operands[1]
    fmap[pc] = fmap(tst(cond[0:1]==bit0,pc+reladdr,pc))

@__npc
def i_BBR0(i,fmap):
    bbrx(0,i,fmap)
@__npc
def i_BBR1(i,fmap):
    bbrx(1,i,fmap)
@__npc
def i_BBR2(i,fmap):
    bbrx(2,i,fmap)
@__npc
def i_BBR3(i,fmap):
    bbrx(3,i,fmap)
@__npc
def i_BBR4(i,fmap):
    bbrx(4,i,fmap)
@__npc
def i_BBR5(i,fmap):
    bbrx(5,i,fmap)
@__npc
def i_BBR6(i,fmap):
    bbrx(6,i,fmap)
@__npc
def i_BBR7(i,fmap):
    bbrx(7,i,fmap)

def bbsx(n,i,fmap):
    cond = mem(i.operands[0],8)
    reladdr = i.operands[1]
    fmap[pc] = fmap(tst(cond[0:1]==bit1,pc+reladdr,pc))

@__npc
def i_BBS0(i,fmap):
    bbsx(0,i,fmap)
@__npc
def i_BBS1(i,fmap):
    bbsx(1,i,fmap)
@__npc
def i_BBS2(i,fmap):
    bbsx(2,i,fmap)
@__npc
def i_BBS3(i,fmap):
    bbsx(3,i,fmap)
@__npc
def i_BBS4(i,fmap):
    bbsx(4,i,fmap)
@__npc
def i_BBS5(i,fmap):
    bbsx(5,i,fmap)
@__npc
def i_BBS6(i,fmap):
    bbsx(6,i,fmap)
@__npc
def i_BBS7(i,fmap):
    bbsx(7,i,fmap)

@__npc
def i_WAI(i,fmap):
    raise NotImplementedError

@__npc
def i_STP(i,fmap):
    raise NotImplementedError

