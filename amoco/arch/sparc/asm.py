# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2013 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *
from .utils import *

from amoco.cas.utils import *

#------------------------------------------------------------------------------
# helpers and decorators :
def _push_(fmap,_x):
  fmap[sp] = fmap[sp]-_x.length
  fmap[mem(sp,_x.size)] = _x

def _pop_(fmap,_l):
  fmap[_l] = fmap(mem(sp,_l.size))
  fmap[sp] = fmap[sp]+_l.length

def __pcnpc(i_xxx):
    def pcnpc(ins,fmap):
        fmap[pc] = fmap(npc)
        fmap[npc] = fmap(npc)+ins.length
        i_xxx(ins,fmap)
    return pcnpc

def trap(ins,fmap,trapname):
    fmap.internals['trap'] = trapname

# i_xxx is the translation of SPARC V8 instruction xxx.
#------------------------------------------------------------------------------

@__pcnpc
def i_ldsb(ins,fmap):
    src,dst = ins.operands
    if dst is not g0:
        fmap[dst] = fmap(mem(src,8)).signextend(32)

@__pcnpc
def i_ldsh(ins,fmap):
    src,dst = ins.operands
    if dst is not g0:
        fmap[dst] = fmap(mem(src,16)).signextend(32)

@__pcnpc
def i_ldub(ins,fmap):
    src,dst = ins.operands
    if dst is not g0:
        fmap[dst] = fmap(mem(src,8)).zeroextend(32)

@__pcnpc
def i_lduh(ins,fmap):
    src,dst = ins.operands
    if dst is not g0:
        fmap[dst] = fmap(mem(src,16)).zeroextend(32)

@__pcnpc
def i_ld(ins,fmap):
    src,dst = ins.operands
    if dst is not g0:
        fmap[dst] = fmap(mem(src,32))

@__pcnpc
def i_ldd(ins,fmap):
    src,dst = ins.operands
    v = fmap(mem(src,64))
    if dst is not g0:
        fmap[dst] = v[32:64]
    fmap[r[ins.rd|1]] = v[0:32]

def i_ldsba(ins,fmap):
    i_ldsb(ins,fmap)
def i_ldsha(ins,fmap):
    i_ldsh(ins,fmap)
def i_lduba(ins,fmap):
    i_ldub(ins,fmap)
def i_lduha(ins,fmap):
    i_lduh(ins,fmap)
def i_lda(ins,fmap):
    i_ld(ins,fmap)
def i_ldda(ins,fmap):
    i_ldd(ins,fmap)
#def i_ldf(ins,fmap):
#    i_ld(ins,fmap)
#def i_lddf(ins,fmap):
#    i_ldd(ins,fmap)
#def i_ldfsr(ins,fmap):
#    i_ld(ins,fmap)
#def i_ldc(ins,fmap):
#    i_ld(ins,fmap)
#def i_lddc(ins,fmap):
#    i_ld(ins,fmap)
#def i_ldcsr(ins,fmap):
#    i_ld(ins,fmap)

@__pcnpc
def i_stb(ins,fmap):
    src,dst = ins.operands
    if dst.base is not g0:
        fmap[mem(dst,8)] = fmap(src[0:8])

@__pcnpc
def i_sth(ins,fmap):
    src,dst = ins.operands
    if dst.base is not g0:
        fmap[mem(dst,16)] = fmap(src[0:16])

@__pcnpc
def i_st(ins,fmap):
    src,dst = ins.operands
    if dst.base is not g0:
        fmap[mem(dst,32)] = fmap(src)

@__pcnpc
def i_std(ins,fmap):
    src,dst = ins.operands
    rr = comp(64)
    rr[32:64] = src
    rr[0:32] = r[ins.rd|1]
    if dst.base is not g0:
        fmap[mem(dst,64)] = fmap(rr)

def i_stba(ins,fmap):
    i_stb(ins,fmap)
def i_stha(ins,fmap):
    i_sth(ins,fmap)
def i_sta(ins,fmap):
    i_st(ins,fmap)
def i_stda(ins,fmap):
    i_std(ins,fmap)
#def i_stf(ins,fmap):
#    i_std(ins,fmap)
#def i_stdf(ins,fmap):
#    i_std(ins,fmap)
#def i_stfsr(ins,fmap):
#    i_std(ins,fmap)
#def i_stdfq(ins,fmap):
#    i_std(ins,fmap)
#def i_stc(ins,fmap):
#    i_std(ins,fmap)
#def i_stdc(ins,fmap):
#    i_std(ins,fmap)
#def i_stcsr(ins,fmap):
#    i_std(ins,fmap)
#def i_stdcq(ins,fmap):
#    i_std(ins,fmap)

def i_ldstub(ins,fmap):
    i_ldub(ins,fmap)
    src = ins.operands[0]
    fmap[mem(src,8)] = cst(0xff,8)

def i_ldstuba(ins,fmap):
    i_ldstub(ins,fmap)

@__pcnpc
def i_swap(ins,fmap):
    src,dst = ins.operands
    _tmp = fmap(mem(src,32))
    fmap[mem(src,32)] = fmap(dst)
    if dst is not g0:
        fmap[dst] = _tmp

def i_swapa(ins,fmap):
    i_swap(ins,fmap)

@__pcnpc
def i_sethi(ins,fmap):
    src,dst = ins.operands
    if dst is not g0:
        fmap[dst] = cst(0,32)
        fmap[dst[10:32]] = src

@__pcnpc
def i_nop(ins,fmap):
    pass

@__pcnpc
def i_and(ins,fmap):
    src1,src2,dst = ins.operands
    _r = fmap(src1 & src2)
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = bit0
        fmap[cf] = bit0
    if dst is not g0:
        fmap[dst] = _r

@__pcnpc
def i_andn(ins,fmap):
    src1,src2,dst = ins.operands
    _r = fmap(src1 & ~src2)
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = bit0
        fmap[cf] = bit0
    if dst is not g0:
        fmap[dst] = _r

@__pcnpc
def i_or(ins,fmap):
    src1,src2,dst = ins.operands
    _r = fmap(src1 | src2)
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = bit0
        fmap[cf] = bit0
    if dst is not g0:
        fmap[dst] = _r

@__pcnpc
def i_orn(ins,fmap):
    src1,src2,dst = ins.operands
    _r = fmap(src1 | ~src2)
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = bit0
        fmap[cf] = bit0
    if dst is not g0:
        fmap[dst] = _r

@__pcnpc
def i_xor(ins,fmap):
    src1,src2,dst = ins.operands
    _r = fmap(src1 ^ src2)
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = bit0
        fmap[cf] = bit0
    if dst is not g0:
        fmap[dst] = _r

@__pcnpc
def i_xnor(ins,fmap):
    src1,src2,dst = ins.operands
    _r = fmap(src1 ^ ~src2)
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = bit0
        fmap[cf] = bit0
    if dst is not g0:
        fmap[dst] = _r

@__pcnpc
def i_sll(ins,fmap):
    src1,src2,dst = ins.operands
    src1.sf = src2.sf = False
    if dst is not g0:
        fmap[dst] = fmap(src1<<src2)

@__pcnpc
def i_srl(ins,fmap):
    src1,src2,dst = ins.operands
    src1.sf = src2.sf = False
    if dst is not g0:
        fmap[dst] = fmap(src1>>src2)

@__pcnpc
def i_sra(ins,fmap):
    src1,src2,dst = ins.operands
    src1.sf = True
    if dst is not g0:
        fmap[dst] = fmap(src1>>src2)

@__pcnpc
def i_add(ins,fmap):
    src1,src2,dst = ins.operands
    _s1 = fmap(src1)
    _s2 = fmap(src2)
    _r,carry,overflow = AddWithCarry(_s1,_s2)
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = overflow
        fmap[cf] = carry
    if dst is not g0:
        fmap[dst] = _r

@__pcnpc
def i_addx(ins,fmap):
    src1,src2,dst = ins.operands
    _s1 = fmap(src1)
    _s2 = fmap(src2)
    _r,carry,overflow = AddWithCarry(_s1,_s2,fmap(cf))
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = overflow
        fmap[cf] = carry
    if dst is not g0:
        fmap[dst] = _r

@__pcnpc
def i_taddcc(ins,fmap):
    src1,src2,dst = ins.operands
    _s1 = fmap(src1)
    _s2 = fmap(src2)
    _r,carry,overflow = AddWithCarry(_s1,_s2)
    fmap[nf] = _r[31:32]
    fmap[zf] = _r==0
    fmap[vf] = overflow | (_s1[0:2]!=0 | _s2[0:2]!=0)
    fmap[cf] = carry
    if dst is not g0:
        fmap[dst] = _r

def i_taddcctv(ins,fmap):
    i_taddcc(ins,fmap)

@__pcnpc
def i_sub(ins,fmap):
    src1,src2,dst = ins.operands
    _s1 = fmap(src1)
    _s2 = fmap(src2)
    _r,carry,overflow = SubWithBorrow(_s1,_s2)
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = overflow
        fmap[cf] = carry
    if dst is not g0:
        fmap[dst] = _r

@__pcnpc
def i_subx(ins,fmap):
    src1,src2,dst = ins.operands
    _s1 = fmap(src1)
    _s2 = fmap(src2)
    _r,carry,overflow = SubWithBorrow(_s1,_s2,fmap(cf))
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = overflow
        fmap[cf] = carry
    if dst is not g0:
        fmap[dst] = _r

@__pcnpc
def i_tsubcc(ins,fmap):
    src1,src2,dst = ins.operands
    _s1 = fmap(src1)
    _s2 = fmap(src2)
    _r,carry,overflow = SubWithBorrow(_s1,_s2,fmap(cf))
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = overflow | (_s1[0:2]!=0 | _s2[0:2]!=0)
        fmap[cf] = carry
    if dst is not g0:
        fmap[dst] = _r

def i_tsubcctv(ins,fmap):
    i_tsubcc(ins,fmap)

@__pcnpc
def i_mulscc(ins,fmap):
    src1,src2,dst = ins.operands
    s10 = fmap(src1[0:1])
    multiplier = fmap(src2)
    _rs1 = fmap(src1>>1)
    _rs1[31:32] = fmap(nf^vf)
    if fmap(y[0:1])==0:
        op2 = cst(0,32)
    else:
        op2 = fmap(src2)
    _r,carry,overflow = AddWithCarry(_rs1,op2)
    # update icc:
    fmap[nf] = _r[31:32]
    fmap[zf] = (_r==0)
    fmap[vf] = overflow
    fmap[cf] = carry
    if dst is not g0:
        fmap[dst] = _r
    #update Y:
    _y = fmap(y>>1)
    _y[31:32] = s10
    fmap[y] = _y

@__pcnpc
def i_umul(ins,fmap):
    src1,src2,dst = ins.operands
    src1.sf = src2.sf = False
    _r = fmap(src1**src2) #pow is used for long mul (_r is 64 bits here)
    fmap[y] = _r[32:64]
    if dst is not g0:
        fmap[dst] = _r[0:32]
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = bit0  # umul does not set overflow (compilers are supposed to check Y!=0 if needed)
        fmap[cf] = bit0

@__pcnpc
def i_smul(ins,fmap):
    src1,src2,dst = ins.operands
    src1.sf = src2.sf = True
    _r = fmap(src1**src2) #pow is used for long mul (_r is 64 bits here)
    fmap[y] = _r[32:64]
    if dst is not g0:
        fmap[dst] = _r[0:32]
    if ins.misc['icc']:
        fmap[nf] = _r[31:32]
        fmap[zf] = _r==0
        fmap[vf] = bit0 # smul does not set overflow (compilers are supposed to check Y!=(_r>>31) if needed)
        fmap[cf] = bit0

@__pcnpc
def i_udiv(ins,fmap):
    src1,src2,dst = ins.operands
    _xs1 = comp(64)
    _xs1[0:32] = src1
    _xs1[32:64] = y
    _xs2 = src2.zeroextend(64)
    _xs1.sf = _xs2.sf = False
    _r = fmap(_xs1/_xs2)
    _v = cst(0xffffffff,32)
    _dst = tst(_r>_v, _v, _r[0:32])
    #fmap[y] = _r[32:64]
    fmap[y] = top(32)
    if dst is not g0:
        fmap[dst] = _dst
    if ins.misc['icc']:
        fmap[nf] = _dst[31:32]
        fmap[zf] = _dst==0
        fmap[vf] = (_r>_v)
        fmap[cf] = bit0

@__pcnpc
def i_sdiv(ins,fmap):
    src1,src2,dst = ins.operands
    _xs1 = comp(64)
    _xs1[0:32] = src1
    _xs1[32:64] = y
    _xs2 = src2.zeroextend(64)
    _xs1.sf = _xs2.sf = True
    _r = fmap(_xs1/_xs2)
    _v = cst(0x7fffffff,32)
    _dst = tst(_r>_v, _v, _r[0:32])
    #fmap[y] = _r[32:64]
    fmap[y] = top(32)
    if dst is not g0:
        fmap[dst] = _dst
    if ins.misc['icc']:
        fmap[nf] = _dst[31:32]
        fmap[zf] = _dst==0
        fmap[vf] = (_r>_v)
        fmap[cf] = bit0

@__pcnpc
def i_save(ins,fmap):
    src1,src2,dst = ins.operands
    _cur_cwp = fmap(cwp)
    _cur_wim = fmap(wim)
    if _cur_cwp._is_cst:
        _new_cwp = (_cur_cwp.v-1)%NWINDOWS
        if _cur_wim[_new_cwp]==bit1:
            trap(ins,fmap,'window_overflow')
        else:
            fmap[cwp] = _new_cwp
    else:
        fmap[cwp] = top(cwp.size)
    if dst is not g0:
        fmap[dst] = fmap(src1+src2)

@__pcnpc
def i_restore(ins,fmap):
    src1,src2,dst = ins.operands
    _cur_cwp = fmap(cwp)
    _cur_wim = fmap(wim)
    if _cur_cwp._is_cst:
        _new_cwp = (_cur_cwp.v+1)%NWINDOWS
        if _cur_wim[_new_cwp]==bit1:
            trap(ins,fmap,'window_underflow')
        else:
            fmap[cwp] = _new_cwp
    else:
        fmap[cwp] = top(cwp.size)
    if dst is not g0:
        fmap[dst] = fmap(src1+src2)

def i_b(ins,fmap):
    def eval_icc(ins,fmap):
        _zf = fmap(zf)
        _nf = fmap(nf)
        _vf = fmap(vf)
        _cf = fmap(cf)
        return {
           'bne' : _zf==bit0,
           'be'  : _zf==bit1,
           'bg'  : (_zf | (_nf^_vf))==bit0,
           'ble' : (_zf | (_nf^_vf))==bit1,
           'bge' : (_nf^_vf)==bit0,
           'bl'  : (_nf^_vf)==bit1,
           'bgu' : (~_cf&~_zf),
           'bleu': (_cf&_zf),
           'bcc' : _cf==bit0,
           'bcs' : _cf==bit1,
           'bpos': _nf==bit0,
           'bneg': _nf==bit1,
           'bvc' : _vf==bit0,
           'bvs' : _vf==bit1,
           'ba'  : bit1,
           'bn'  : bit0
        }[CONDB[ins.cond]]
    _pc = fmap(pc)
    fmap[pc] = fmap(npc)
    _t = eval_icc(ins,fmap)
    fmap[npc] = tst(_t,_pc+ins.operands[0]*4, fmap(npc)+4)

def i_FBcc(ins,fmap):raise NotImplementedError
def i_CBcc(ins,fmap):raise NotImplementedError

def i_call(ins,fmap):
    _pc = fmap(pc)
    fmap[r[15]] = _pc
    fmap[pc] = fmap(npc)
    fmap[npc] = _pc+(ins.operands[0]*4)

@__pcnpc
def i_jmpl(ins,fmap):
    op1, op2 = ins.operands
    if op2 is not g0:
        fmap[op2] = fmap[pc]
    fmap[pc] = fmap(op1)

@__pcnpc
def i_rett(ins,fmap):raise NotImplementedError

@__pcnpc
def i_Ticc(ins,fmap):raise NotImplementedError

@__pcnpc
def i_rd(ins,fmap):
    src,dst = ins.operands
    fmap[dst] = fmap(src)

@__pcnpc
def i_wr(ins,fmap):
    src,val,dst = ins.operands
    fmap[dst] = fmap(src)^fmap(val)

@__pcnpc
def i_flush(ins,fmap):raise NotImplementedError

@__pcnpc
def i_FPop1(ins,fmap):
    raise NotImplementedError
@__pcnpc
def i_FPop2(ins,fmap):
    raise NotImplementedError

@__pcnpc
def i_CPop1(ins,fmap):
    raise NotImplementedError
@__pcnpc
def i_CPop2(ins,fmap):
    raise NotImplementedError

@__pcnpc
def i_unimp(ins,fmap):
    raise NotImplementedError
