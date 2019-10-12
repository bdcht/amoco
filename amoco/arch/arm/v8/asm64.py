# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2013 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.logger import Log
logger = Log(__name__)
logger.debug('loading module')
from .env64 import *
from .utils import *
from amoco.cas.utils import *

def __mem(a,sz,disp=0):
    endian = 1
    if internals['endianstate']==1:
        endian=-1
    return mem(a,sz,disp=disp,endian=endian)

def i_ADC(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    op1,op2 = map(fmap,i.operands[1:])
    x,carry,overflow = AddWithCarry(op1, op2, fmap(C))
    if i.setflags:
        fmap[N] = x<0
        fmap[Z] = x==0
        fmap[C] = carry
        fmap[V] = overflow
    fmap[i.d] = x

def i_SBC(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    op1,op2 = map(fmap,i.operands[1:])
    x,carry,overflow = SubWithBorrow(op1, op2, fmap(C))
    if i.setflags:
        fmap[N] = x<0
        fmap[Z] = x==0
        fmap[C] = carry
        fmap[V] = overflow
    fmap[i.d] = x

def i_ADD(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    op1,op2 = map(fmap,i.operands[1:])
    x,carry,overflow = AddWithCarry(op1,op2)
    if i.setflags:
        fmap[N] = x<0
        fmap[Z] = x==0
        fmap[C] = carry
        fmap[V] = overflow
    fmap[i.d] = x

def i_SUB(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    op1,op2 = map(fmap,i.operands[1:])
    x,carry,overflow = SubWithBorrow(op1,op2)
    if i.setflags:
        fmap[N] = x<0
        fmap[Z] = x==0
        fmap[C] = carry
        fmap[V] = overflow
    fmap[i.d] = x

def i_ADR(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    base = fmap(pc)
    fmap[i.d] = base+i.imm

def i_ADRP(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    base = fmap(pc & 0xFFFFFFFFFFFFF000)
    fmap[i.d] = base+i.imm

def i_AND(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst,src1,src2 = i.operands
    x = fmap(src1 & src2)
    fmap[dst] = x
    if i.setflags:
        fmap[N] = x[x.size-1:x.size]
        fmap[Z] = x==0
        fmap[C] = bit0
        fmap[V] = bit0

def i_ORR(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst,src1,src2 = i.operands
    x = fmap(src1 | src2)
    fmap[dst] = x
    if i.setflags:
        fmap[N] = x[x.size-1:x.size]
        fmap[Z] = x==0
        fmap[C] = bit0
        fmap[V] = bit0

def i_ORN(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst,src1,src2 = i.operands
    x = fmap(src1 | ~src2)
    fmap[dst] = x
    if i.setflags:
        fmap[N] = x[x.size-1:x.size]
        fmap[Z] = x==0
        fmap[C] = bit0
        fmap[V] = bit0

def i_EOR(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst,src1,src2 = i.operands
    x = fmap(src1 ^ src2)
    fmap[dst] = fmap(x)
    if i.setflags:
        fmap[N] = x[x.size-1:x.size]
        fmap[Z] = x==0
        fmap[C] = bit0
        fmap[V] = bit0

def i_EON(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst,src1,src2 = i.operands
    x = fmap(src1 ^ ~src2)
    fmap[dst] = x
    if i.setflags:
        fmap[N] = x[x.size-1:x.size]
        fmap[Z] = x==0
        fmap[C] = bit0
        fmap[V] = bit0

def i_ASRV(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    fmap[i.d] = fmap(i.n>>i.m)

def i_Bcond(i,fmap):
    cond = fmap(i.cond)
    fmap[pc] = tst(cond, fmap[pc]+i.offset, fmap[pc]+i.length)

def i_B(i,fmap):
    fmap[pc] = fmap[pc]+i.offset

def i_BL(i,fmap):
    fmap[r30] = fmap[pc]+i.length
    fmap[pc] = fmap[pc]+i.offset

def i_BR(i,fmap):
    fmap[pc] = fmap(i.n)

def i_BLR(i,fmap):
    fmap[r30] = fmap[pc]+i.length
    fmap[pc] = fmap(i.n)

def i_BFM(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst = cst(0,i.datasize) if i.inzero else fmap(i.d)
    src = fmap(i.n)
    lo = (dst & ~i.wmask) | (ROR(src,i.immr.value) & i.wmask)
    sta,sto = i.imms.value,i.imms.value+1
    hi = composer([src[sta:sto]]*i.datasize) if i.extend else dst
    fmap[i.d] = (hi & ~i.tmask) | (lo & i.tmask)

i_SBFM = i_BFM
i_UBFM = i_BFM

def i_BIC(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    op1 = fmap(i.n)
    op2 = fmap(i.m)
    if i.invert: op2 = ~op2
    _r = op1 & op2
    fmap[i.d] = _r
    if i.setflags:
        fmap[C] = bit0
        fmap[V] = bit0
        fmap[Z] = _r==0
        fmap[N] = _r[_r.size-1:_r.size]

def i_BRK(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    ext('BRK %s'%i.imm,size=pc.size).call(fmap)

def i_CBNZ(i,fmap):
    fmap[pc] = tst(fmap(i.t!=0), fmap[pc]+i.offset, fmap[pc]+i.length)

def i_CBZ(i,fmap):
    fmap[pc] = tst(fmap(i.t==0), fmap[pc]+i.offset, fmap[pc]+i.length)

def i_CCMN(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    op1, op2, nzcv, cond = i.operands
    _r, carry, overflow = AddWithCarry(fmap(op1),fmap(op2))
    fmap[N] = tst(fmap(cond), _r<0    , i.flags[0])
    fmap[Z] = tst(fmap(cond), _r==0   , i.flags[1])
    fmap[C] = tst(fmap(cond), carry   , i.flags[2])
    fmap[V] = tst(fmap(cond), overflow, i.flags[3])

def i_CCMP(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    op1, op2, nzcv, cond = i.operands
    _r, carry, overflow = SubWithBorrow(fmap(op1),fmap(op2))
    fmap[N] = tst(fmap(cond), _r<0    , i.flags[0])
    fmap[Z] = tst(fmap(cond), _r==0   , i.flags[1])
    fmap[C] = tst(fmap(cond), carry   , i.flags[2])
    fmap[V] = tst(fmap(cond), overflow, i.flags[3])

def i_CLREX(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_CLS(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    fmap[i.d] = top(i.d.size)
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_CLZ(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    fmap[i.d] = top(i.d.size)
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_CSEL(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst, op1, op2, cond = i.operands
    cond = CONDITION[cond^1][1]
    fmap[dst] = tst(fmap(cond), fmap(op1), fmap(op2))

def i_CSINC(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst, op1, op2, cond = i.operands
    cond = CONDITION[cond^1][1]
    fmap[dst] = tst(fmap(cond), fmap(op1), fmap(op2)+1)

def i_CSINV(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst, op1, op2, cond = i.operands
    cond = CONDITION[cond^1][1]
    fmap[dst] = tst(fmap(cond), fmap(op1), fmap(~op2))

def i_CSNEG(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst, op1, op2, cond = i.operands
    cond = CONDITION[cond^1][1]
    fmap[dst] = tst(fmap(cond), fmap(op1), fmap(-op2))

def i_DCPS1(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)
def i_DCPS2(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)
def i_DCPS3(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)
def i_DMB(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)
def i_DRPS(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)
def i_DSB(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)
def i_ISB(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_ERET(i,fmap):
    fmap[pc] = top(64)
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_EXTR(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst, op1, op2, lsb = i.operands
    concat = composer(fmap(op2),fmap(op1))
    result = concat[lsb:lsb+i.datasize]
    fmap[dst] = result

def i_HINT(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    if i.imm>0:
        logger.warning('semantic undefined for %s(%d)'%(i.mnemonic,i.imm))
def i_HLT(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)
def i_HVC(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_LDAR(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    data = fmap(__mem(i.n,i.datasize))
    if i.pair:
        if not i.excl: raise InstructionError(i)
        if i.elsize==32:
            if internals['endianstate']==0:
                fmap[i.t]  = data[0:i.elsize]
                fmap[i.t2] = data[i.elsize:i.datasize]
            else:
                fmap[i.t]  = data[i.elsize:i.datasize]
                fmap[i.t2] = data[0:i.elsize]
        else:
            fmap[i.t]  = fmap(__mem(i.n, 64))
            fmap[i.t2] = fmap(__mem(i.n, 64, disp=8))
    else:
        fmap[i.t] = data.zeroextend(i.regsize)

i_LDARB  = i_LDAR
i_LDARH  = i_LDAR
i_LDAXP  = i_LDAR
i_LDAXR  = i_LDAR
i_LDAXRB = i_LDAR
i_LDAXRH = i_LDAR
i_LDXP   = i_LDAR
i_LDXR   = i_LDAR
i_LDXRB  = i_LDAR
i_LDXRH  = i_LDAR

def i_STLR(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    address = fmap(i.n)
    if i.pair:
        if not i.excl: raise InstructionError(i)
        if internals['endianstate']==0:
            data = composer(i.t,i.t2)
        else:
            data = composer(i.t2,i.t)
    else:
        data = i.t
    if i.excl:
        fmap[i.s] = cst(1,32)
    fmap[address] = fmap(data)

i_STLRB  = i_STLR
i_STLRH  = i_STLR
i_STLXP  = i_STLR
i_STLXR  = i_STLR
i_STLXRB = i_STLR
i_STLXRH = i_STLR
i_STXP   = i_STLR
i_STXR   = i_STLR
i_STXRB  = i_STLR
i_STXRH  = i_STLR

def i_LDP(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    address = i.n
    if not i.postindex: address += i.offset
    data1 = __mem(address,i.datasize)
    data2 = __mem(address,i.datasize, disp=i.datasize/8)
    fmap[i.t]  = fmap(data1)
    fmap[i.t2] = fmap(data2)
    if i.wback:
        if i.postindex: address += i.offset
        fmap[i.n] = fmap(address)

def i_STP(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    address = i.n
    if not i.postindex: address += i.offset
    data1 = fmap(i.t)
    data2 = fmap(i.t2)
    fmap[__mem(address,i.datasize)]  = data1
    fmap[__mem(address,i.datasize,disp=i.datasize/8)] = data2
    if i.wback:
        if i.postindex: address += i.offset
        fmap[i.n] = fmap(address)

i_LDNP = i_LDP
i_STNP = i_STP

def i_LDPSW(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    address = i.n
    if not i.postindex: address += i.offset
    data1 = __mem(address,i.datasize)
    data2 = __mem(address,i.datasize, disp=i.datasize/8)
    fmap[i.t]  = fmap(data1).signextend(64)
    fmap[i.t2] = fmap(data2).signextend(64)
    if i.wback:
        if i.postindex: address += i.offset
        fmap[i.n] = fmap(address)

def i_LDR(i,fmap):
    if len(i.operands)==3:
        fmap[pc] = fmap[pc]+i.length
        Xt, Xn, offset = i.operands
        address = Xn
        if not i.postindex: address += offset
        data = __mem(address,i.datasize)
        if i.signed:
            fmap[Xt] = data.signextend(i.regsize)
        else:
            fmap[Xt] = data.zeroextend(i.regsize)
        if i.wback:
            if i.postindex: address += offset
            fmap[Xn] = fmap(address)
    else:# literal case:
        Xt, offset = i.operands
        address = fmap[pc] + offset
        fmap[pc] = fmap[pc]+i.length
        data = __mem(address,i.size)
        if i.signed:
            fmap[Xt] = fmap(data.signextend(64))
        else:
            fmap[Xt] = fmap(data.zeroextend(64))

i_LDRB   = i_LDR
i_LDRH   = i_LDR
i_LDRSB  = i_LDR
i_LDRSH  = i_LDR
i_LDRSW  = i_LDR
i_LDTR   = i_LDR
i_LDTRB  = i_LDR
i_LDTRH  = i_LDR
i_LDTRSB = i_LDR
i_LDTRSH = i_LDR
i_LDTRSW = i_LDR
i_LDUR   = i_LDR
i_LDURB  = i_LDR
i_LDURH  = i_LDR
i_LDURSB = i_LDR
i_LDURSH = i_LDR
i_LDURSW = i_LDR

def i_LSLV(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst, op1, op2 = i.operands
    op1.sf=False
    fmap[dst] = fmap(op1<<op2)

def i_LSRV(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    dst, op1, op2 = i.operands
    op1.sf=False
    fmap[dst] = fmap(op1>>op2)

def i_MADD(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    fmap[i.d] = fmap(i.a + i.r*i.m)

def i_MSUB(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    fmap[i.d] = fmap(i.a - i.r*i.m)

def i_MOVK(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    result = comp(i.d.size)
    result[0:i.d.size] = fmap(i.d)
    result[0:16] = i.imm
    fmap[i.d] = result

def i_MOVZ(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    result = i.imm.zeroextend(i.d.size)
    fmap[i.d] = result

def i_MOVN(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    result = i.imm.zeroextend(i.d.size)
    fmap[i.d] = ~result

def i_MRS(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_MSR(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    pstatefield, op2 = i.operands
    fmap[pstatefield] = op2[0:pstatefield.size]

def i_PRFM(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_RBIT(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    fmap[i.d] = top(i.datasize)
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_REV16(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    fmap[i.d] = top(i.datasize)
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_REV32(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    fmap[i.d] = top(i.datasize)
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_REV(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    fmap[i.d] = top(i.datasize)
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_RET(i,fmap):
    fmap[pc] = fmap(i.n)

def i_RORV(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    fmap[i.d] = ROR(fmap(i.n),fmap(i.m))

def i_SDIV(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    op1,op2 = fmap(i.n),fmap(i.m)
    op1.sf = op2.sf = True
    fmap[i.d] = op1/op2

def i_UDIV(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    op1,op2 = fmap(i.n),fmap(i.m)
    op1.sf = op2.sf = False
    fmap[i.d] = op1/op2

def i_SMADDL(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    _x = fmap(i.a + (i.n**i.m))
    _x.sf = True
    fmap[i.d] = _x

def i_SMSUBL(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    _x = fmap(i.a - (i.n**i.m))
    _x.sf = True
    fmap[i.d] = _x

def i_UMADDL(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    _x = fmap(i.a + (i.n**i.m))
    _x.sf = False
    fmap[i.d] = _x

def i_UMSUBL(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    _x = fmap(i.a - (i.n**i.m))
    _x.sf = False
    fmap[i.d] = _x

def i_SMULH(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    result = fmap(i.n**i.m)
    result.sf = True
    fmap[i.d] = result[64:128]

def i_UMULH(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    result = fmap(i.n**i.m)
    result.sf = False
    fmap[i.d] = result[64:128]

def i_STR(i,fmap):
    if len(i.operands)==3:
        fmap[pc] = fmap[pc]+i.length
        Xt, Xn, offset = i.operands
        address = Xn
        if not i.postindex: address += offset
        dst = __mem(address,i.datasize)
        data = fmap(Xt)
        fmap[dst] = data[0:i.datasize]
        if i.wback:
            if i.postindex: address += offset
            fmap[Xn] = fmap(address)

i_STRB   = i_STR
i_STRH   = i_STR
i_STTR   = i_STR
i_STTRB  = i_STR
i_STTRH  = i_STR
i_STUR   = i_STR
i_STURB  = i_STR
i_STURH  = i_STR

def i_SMC(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    ext('EXCEPTION.EL3 %s'%i.imm,size=pc.size).call(fmap)

def i_SVC(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    ext('EXCEPTION.EL1 %s'%i.imm,size=pc.size).call(fmap)

def i_SYS(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_SYSL(i,fmap):
    fmap[pc] = fmap[pc]+i.length
    fmap[i.t] = top(i.t.size)
    logger.warning('semantic undefined for %s'%i.mnemonic)

def i_TBNZ(i,fmap):
    op = fmap(i.t)
    fmap[pc] = tst(op[i.bitpos:i.bitpos+1]==1, fmap[pc]+i.offset, fmap[pc]+i.length)

def i_TBZ(i,fmap):
    op = fmap(i.t)
    fmap[pc] = tst(op[i.bitpos:i.bitpos+1]==0, fmap[pc]+i.offset, fmap[pc]+i.length)

