# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *

from amoco.cas.utils import *

# handlers for preinc/postinc/postdec virtual registers:
# ------------------------------------------------------

def _pre_(i,fmap,pos=0):
    v = i.misc['virts']
    if len(v)>pos:
        action,dst = v[pos]
        if action=='preinc':
            fmap[dst] = fmap(dst)+1

def _post_(i,fmap,pos=0):
    v = i.misc['virts']
    if len(v)>pos:
        action,dst = v[pos]
        if action=='postinc':
            fmap[dst] = fmap(dst)+1
        elif action=='postdec':
            fmap[dst] = fmap(dst)-1

# ------------------------------------------------------

def i_ADDLW(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    k = i.imm
    res,carry,overflow = AddWithCarry(fmap(wreg),k)
    fmap[wreg] = res
    fmap[nf]  = res[7:8]
    fmap[ovf] = overflow
    fmap[cf]  = carry
    fmap[dcf] = top(1)
    fmap[zf]  = (res==0)

def i_ADDWF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res,carry,overflow = AddWithCarry(fmap(wreg),fmap(src))
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[ovf] = overflow
    fmap[cf]  = carry
    fmap[dcf] = top(1)
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_ADDWFC(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res,carry,overflow = AddWithCarry(fmap(wreg),fmap(src),fmap(cf))
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[ovf] = overflow
    fmap[cf]  = carry
    fmap[dcf] = top(1)
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_ANDLW(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    k = i.imm
    res = fmap(wreg & k)
    fmap[wreg] = res
    fmap[nf]  = res[7:8]
    fmap[zf]  = (res==0)

def i_ANDWF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = fmap(wreg & src)
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_BC(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    n = i.offset.signextend(pc.size)
    fmap[pc] = tst(cf,fmap(pc)+(n<<1),fmap(pc))

def i_BCF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst, b = i.dst, i.b
    c = comp(dst.size)
    c[0:dst.size] = dst
    c[b:b+1] = bit0
    fmap[dst] = c
    _post_(i,fmap)

def i_BN(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    n = i.offset.signextend(pc.size)
    fmap[pc] = tst(nf,fmap(pc)+(n<<1),fmap(pc))

def i_BNC(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    n = i.offset.signextend(pc.size)
    fmap[pc] = tst(cf,fmap(pc),fmap(pc)+(n<<1))

def i_BNN(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    n = i.offset.signextend(pc.size)
    fmap[pc] = tst(nf,fmap(pc),fmap(pc)+(n<<1))

def i_BNOV(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    n = i.offset.signextend(pc.size)
    fmap[pc] = tst(ovf,fmap(pc),fmap(pc)+(n<<1))

def i_BNZ(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    n = i.offset.signextend(pc.size)
    fmap[pc] = tst(zf,fmap(pc),fmap(pc)+(n<<1))

def i_BRA(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    n = i.offset.signextend(pc.size)
    fmap[pc] = fmap(pc)+(n<<1)

def i_BSF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst, b = i.dst, i.b
    c = comp(dst.size)
    c[0:dst.size] = dst
    c[b:b+1] = bit1
    fmap[dst] = c
    _post_(i,fmap)

def i_BTFSC(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst, b = i.dst, i.b
    cond = fmap(dst[b:b+1]==bit0)
    fmap[pc] = tst(cond,fmap(pc)+2,fmap(pc))
    _post_(i,fmap)

def i_BTFSS(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst, b = i.dst, i.b
    cond = fmap(dst[b:b+1]==bit1)
    fmap[pc] = tst(cond,fmap(pc)+2,fmap(pc))
    _post_(i,fmap)

def i_BTG(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst, b = i.dst, i.b
    c = comp(dst.size)
    c[0:dst.size] = dst
    c[b:b+1] = ~dst[b:b+1]
    fmap[dst] = c
    _post_(i,fmap)

def i_BOV(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    n = i.offset.signextend(pc.size)
    fmap[pc] = tst(ovf,fmap(pc)+(n<<1),fmap(pc))

def i_BZ(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    n = i.offset.signextend(pc.size)
    fmap[pc] = tst(zf,fmap(pc)+(n<<1),fmap(pc))

def i_CALL(i,fmap):
    i_PUSH(i,fmap)
    k = i.offset
    fmap[pc] = k
    if i.misc['fast']:
        fmap[wregs] = fmap(wreg)
        fmap[bsrs] = fmap(bsr)
        fmap[statuss] = fmap(status)

def i_CLRF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst = i.dst
    fmap[dst] = cst(0,dst.size)
    fmap[zf] = bit1
    _post_(i,fmap)

def i_CLRWDT(i,fmap):
    fmap[pc] = fmap(pc)+i.length

def i_COMF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst = i.dst
    src = i.src
    res = fmap(~src)
    fmap[dst] = res
    fmap[zf] = (res==0)
    fmap[nf] = res[7:8]
    _post_(i,fmap)

def i_CPFSEQ(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst = i.dst
    src = i.src
    res = fmap(src-wreg)
    fmap[pc] = tst(res==0,fmap(pc)+2,fmap(pc))
    _post_(i,fmap)

def i_CPFSGT(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst = i.dst
    src = i.src
    res = fmap(src-wreg)
    fmap[pc] = tst(res>0,fmap(pc)+2,fmap(pc))
    _post_(i,fmap)

def i_CPFSLT(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst = i.dst
    src = i.src
    res = fmap(src-wreg)
    fmap[pc] = tst(res<0,fmap(pc)+2,fmap(pc))
    _post_(i,fmap)

def i_DAW(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    c = comp(8)
    c[0:8] = wreg
    x = fmap(wreg[0:4])
    a = (x>9)|dcf
    c[0:4] = tst(a, x+6, x)
    x = fmap(wreg[4:8]) + dcf.zeroextend(4)
    a = (x>9)|cf
    c[4:8] = tst(a, x+6, x)
    fmap[wreg] = c

def i_DECF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst = i.dst
    src = i.src
    res,carry,overflow = SubWithBorrow(fmap(src),cst(1,src.size))
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[ovf] = overflow
    fmap[cf]  = carry
    fmap[dcf] = top(1)
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_DECFSZ(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = fmap(src-1)
    fmap[dst] = res
    fmap[pc] = tst(res==0,fmap(pc)+2,fmap(pc))
    _post_(i,fmap)

def i_DCFSNZ(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = fmap(src-1)
    fmap[dst] = res
    fmap[pc] = tst(res!=0,fmap(pc)+2,fmap(pc))
    _post_(i,fmap)

def i_GOTO(i,fmap):
    k = i.operands[0]
    fmap[pc] = k

def i_INCF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res,carry,overflow = AddWithCarry(fmap(src),cst(1,src.size))
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[ovf] = overflow
    fmap[cf]  = carry
    fmap[dcf] = top(1)
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_INCFSZ(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = fmap(src+1)
    fmap[dst] = res
    fmap[pc] = tst(res==0,fmap(pc)+2,fmap(pc))
    _post_(i,fmap)

def i_INCFSNZ(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = fmap(src+1)
    fmap[dst] = res
    fmap[pc] = tst(res!=0,fmap(pc)+2,fmap(pc))
    _post_(i,fmap)

def i_IORLW(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    k = i.imm
    res = fmap(wreg | k)
    fmap[wreg] = res
    fmap[nf]  = res[7:8]
    fmap[zf]  = (res==0)

def i_IORWF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = fmap(wreg | src)
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_LFSR(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    dst,src = i.operands
    fmap[dst] = src.zeroextend(dst.size)

def i_MOVF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = fmap(src)
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_MOVFF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    res = fmap(i.src)
    _post_(i,fmap)
    _pre_(i,fmap,pos=1)
    dst = i.dst
    fmap[dst] = res
    _post_(i,fmap,pos=1)

def i_MOVLB(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    k = i.imm
    fmap[bsr] = k.zeroextend(bsr.size)

def i_MOVLW(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    k = i.imm
    fmap[wreg] = k

def i_MOVWF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst = i.dst
    res = fmap(wreg)
    fmap[dst] = res
    _post_(i,fmap)

def i_MULLW(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    k = i.imm
    res = fmap(wreg ** k)
    fmap[prod] = res

def i_MULWF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    src = i.imm
    res = fmap(wreg ** src)
    fmap[prod] = res

def i_NEGF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = src
    res,carry,overflow = SubWithBorrow(cst(0,8),fmap(src))
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[ovf] = overflow
    fmap[cf]  = carry
    fmap[dcf] = top(1)
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_NOP(i,fmap):
    fmap[pc] = fmap(pc)+i.length

def i_POP(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    fmap[tos]    = fmap(mem(stkptr,21,seg='rstack'))
    fmap[stkptr] = fmap(stkptr-1)

def i_PUSH(i,fmap):
    npc = fmap(pc)+i.length
    fmap[pc] = npc
    x = fmap(stkptr+1)
    fmap[stkptr] = x
    fmap[mem(x,21,seg='rstack')] = npc
    fmap[tos] = npc

def i_RCALL(i,fmap):
    npc = fmap(pc)+i.length
    fmap[tos] = npc
    n = i.offset.signextend(pc.size)
    fmap[pc]  = npc+(n<<1)

def i_RESET(i,fmap):
    fmap[pc] = top(21)

def i_RETFIE(i,fmap):
    fmap[pc] = fmap(tos)
    fmap[tos] = fmap(mem(stkptr,21,seg='rstack'))
    fmap[stkptr] = fmap(stkptr-1)
    # FIXME! GIE/GIEH & PEIE/GIEL flag should be affected
    s = i.operands[0]
    if s==1:
        fmap[wreg] = fmap(wregs)
        fmap[statuss] = fmap(statuss)
        fmap[bsr] = fmap(bsrs)

def i_RETLW(i,fmap):
    fmap[pc] = fmap(tos)
    fmap[tos] = fmap(mem(stkptr,21,seg='rstack'))
    fmap[stkptr] = fmap(stkptr-1)
    fmap[wreg] = i.imm

def i_RETURN(i,fmap):
    fmap[pc] = fmap(tos)
    fmap[tos] = fmap(mem(stkptr,21,seg='rstack'))
    fmap[stkptr] = fmap(stkptr-1)
    s = i.operands[0]
    if s==1:
        fmap[wreg] = fmap(wregs)
        fmap[statuss] = fmap(statuss)
        fmap[bsr] = fmap(bsrs)

def i_RLCF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res,carry = ROLWithCarry(fmap(src),1,fmap(cf))
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[cf]  = carry
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_RLNCF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = ROL(fmap(src),1)
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_RRCF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res,carry = RORWithCarry(fmap(src),1,fmap(cf))
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[cf]  = carry
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_RRNCF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = ROR(fmap(src),1)
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_SETF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    dst = i.dst
    fmap[dst] = cst(0xff,dst.size)
    _post_(i,fmap)

def i_SLEEP(i,fmap):
    fmap[pc] = fmap(pc)+i.length

def i_SUBFWB(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res,carry,overflow = SubWithBorrow(fmap(wreg),fmap(src),~fmap(cf))
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[ovf] = overflow
    fmap[cf]  = carry
    fmap[dcf] = top(1)
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_SUBLW(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    k = i.imm
    res,carry,overflow = SubWithBorrow(fmap(wreg),k)
    fmap[wreg] = res
    fmap[nf]  = res[7:8]
    fmap[ovf] = overflow
    fmap[cf]  = carry
    fmap[dcf] = top(1)
    fmap[zf]  = (res==0)

def i_SUBWF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res,carry,overflow = SubWithBorrow(fmap(wreg),fmap(src))
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[ovf] = overflow
    fmap[cf]  = carry
    fmap[dcf] = top(1)
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_SUBWFB(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res,carry,overflow = SubWithBorrow(fmap(src),fmap(wreg),~fmap(cf))
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[ovf] = overflow
    fmap[cf]  = carry
    fmap[dcf] = top(1)
    fmap[zf]  = (res==0)
    _post_(i,fmap)

def i_SUBWFB(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = fmap(src)
    c = comp(8)
    c[0:4] = res[4:8]
    c[4:8] = res[0:4]
    fmap[dst] = c
    _post_(i,fmap)

def i_TBLRD(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    fmap[tablat] = fmap(mem(tblptr,8,'PM'))
    _post_(i,fmap)

def i_TBLWT(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    fmap[mem(tblptr,8,'PM')] = fmap(tablat)
    _post_(i,fmap)

def i_TSTFSZ(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = fmap(src)
    fmap[pc] = tst(res==0,fmap(pc)+2,fmap(pc))
    _post_(i,fmap)

def i_XORLW(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    k = i.imm
    res = fmap(wreg ^ k)
    fmap[wreg] = res
    fmap[nf]  = res[7:8]
    fmap[zf]  = (res==0)

def i_XORWF(i,fmap):
    fmap[pc] = fmap(pc)+i.length
    _pre_(i,fmap)
    src = i.src
    dst = i.dst
    res = fmap(wreg) ^ src
    fmap[dst] = res
    fmap[nf]  = res[7:8]
    fmap[zf]  = (res==0)
    _post_(i,fmap)

