#!/usr/bin/env python

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

from .env import *
from amoco.cas.utils import *

from amoco.logger import Log
logger = Log(__name__)

#------------------------------------------------------------------------------
# utils :
def push(fmap,x):
  fmap[esp] = fmap[esp]-x.length
  fmap[mem(esp,x.size)] = x

def pop(fmap,l):
  fmap[l] = fmap(mem(esp,l.size))
  fmap[esp] = fmap[esp]+l.length

#------------------------------------------------------------------------------
def i_AAA(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  alv = fmap(al)
  cond = (alv&0xf>9)|fmap(af)
  fmap[al] = tst(cond, (alv+6)&0xf, alv&0xf)
  fmap[ah] = tst(cond, fmap(ah)+1, fmap(ah))
  fmap[af] = cond
  fmap[cf] = cond

def i_DAA(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  alv = fmap(al)
  cfv = fmap(cf)
  cond = (alv&0xf>9)|fmap(af)
  _r,carry,overflow = AddWithCarry(alv,cst(6,8))
  fmap[al] = tst(cond, _r, alv)
  fmap[cf] = tst(cond, carry|cfv, cfv)
  fmap[af] = cond
  cond = (alv>0x99)|cfv
  alv = fmap(al)
  fmap[al] = tst(cond,alv+0x60, alv)
  fmap[cf] = cond

def i_AAS(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  alv = fmap(al)
  cond = (alv&0xf>9)|fmap(af)
  fmap[ax] = tst(cond, fmap(ax)-6, fmap(ax))
  fmap[ah] = tst(cond, fmap(ah)-1, fmap(ah))
  fmap[af] = cond
  fmap[cf] = cond
  fmap[al] = tst(cond, fmap(al)&0xf, alv&0xf)

def i_DAS(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  alv = fmap(al)
  cfv = fmap(cf)
  cond = (alv&0xf>9)|fmap(af)
  _r,carry,overflow = SubWithBorrow(alv,cst(6,8))
  fmap[al] = tst(cond, _r, alv)
  fmap[cf] = tst(cond, carry|cfv, cfv)
  fmap[af] = cond
  cond = (alv>0x99)|cfv
  alv = fmap(al)
  fmap[al] = tst(cond,alv-0x60, alv)
  fmap[cf] = cond

def i_AAD(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  imm8 = i.operands[0]
  _al = fmap(al)
  _ah = fmap(ah)
  _r  = _al + (_ah*imm8)
  fmap[al] = _r
  fmap[ah] = cst(0,8)
  fmap[zf] = _r==0
  fmap[sf] = _r<0

def i_AAM(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  imm8 = i.operands[0]
  _al = fmap(al)
  fmap[ah] = _al / imm8
  _r  = _al & (imm8-1)
  fmap[al] = _r
  fmap[zf] = _r==0
  fmap[sf] = _r<0

#------------------------------------------------------------------------------
def i_BSWAP(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  dst = i.operands[0]
  _t = fmap(dst)
  fmap[dst[0 : 8]] = _t[24:32]
  fmap[dst[8 :16]] = _t[16:24]
  fmap[dst[16:24]] = _t[8 :16]
  fmap[dst[24:32]] = _t[0 : 8]

def i_NOP(i,fmap):
  fmap[eip] = fmap[eip]+i.length

def i_WAIT(i,fmap):
  fmap[eip] = fmap[eip]+i.length

# LEAVE instruction is a shortcut for 'mov esp,ebp ; pop ebp ;'
def i_LEAVE(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  fmap[esp] = fmap[ebp]
  pop(fmap,ebp)

def i_RET(i,fmap):
  pop(fmap,eip)

def i_HLT(i,fmap):
  ext('halt').call(fmap)

#------------------------------------------------------------------------------
def _ins_(i,fmap,l):
  counter = cx if i.misc['adrsz'] else ecx
  loc = mem(fmap(edi),l*8)
  src = ext('IN%s'%fmap(dx),l*8).call(fmap)
  if i.misc['rep']:
      fmap[loc] = tst(fmap(counter)==0, fmap(loc), src)
      fmap[counter] = fmap(counter)-1
      fmap[eip] = tst(fmap(counter)==0, fmap[eip]+i.length, fmap[eip])
  else:
      fmap[loc] = src
      fmap[eip] = fmap[eip]+i.length
  fmap[edi] = tst(fmap(df),fmap(edi)-l,fmap(edi)+l)

def i_INSB(i,fmap):
  _ins_(i,fmap,1)
def i_INSW(i,fmap):
  _ins_(i,fmap,2)
def i_INSD(i,fmap):
  _ins_(i,fmap,4)

#------------------------------------------------------------------------------
def _outs_(i,fmap,l):
  counter = cx if i.misc['adrsz'] else ecx
  src = fmap(mem(esi,l*8))
  loc = ext('OUT%s'%fmap(dx),l*8).call(fmap)
  if i.misc['rep']:
      fmap[loc] = tst(fmap(counter)==0, fmap(loc), src)
      fmap[counter] = fmap(counter)-1
      fmap[eip] = tst(fmap(counter)==0, fmap[eip]+i.length, fmap[eip])
  else:
      fmap[loc] = src
      fmap[eip] = fmap[eip]+i.length
  fmap[edi] = tst(fmap(df),fmap(edi)-l,fmap(edi)+l)

def i_OUTSB(i,fmap):
  _outs_(i,fmap,1)
def i_OUTSW(i,fmap):
  _outs_(i,fmap,2)
def i_OUTSD(i,fmap):
  _outs_(i,fmap,4)

#------------------------------------------------------------------------------
def i_INT3(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  ext('INT3').call(fmap)

def i_CLC(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  fmap[cf] = bit0

def i_STC(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  fmap[cf] = bit1

def i_CLD(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  fmap[df] = bit0

def i_STD(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  fmap[df] = bit1

def i_CMC(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  fmap[cf] = ~fmap(cf)

def i_CBW(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  fmap[ax] = fmap(al).signextend(16)

def i_CWDE(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  fmap[eax] = fmap(ax).signextend(32)

def i_PUSHAD(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  tmp = fmap(esp)
  push(fmap,fmap(eax))
  push(fmap,fmap(ecx))
  push(fmap,fmap(edx))
  push(fmap,fmap(ebx))
  push(fmap,tmp)
  push(fmap,fmap(ebp))
  push(fmap,fmap(esi))
  push(fmap,fmap(edi))

def i_POPAD(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  pop(fmap,edi)
  pop(fmap,esi)
  pop(fmap,ebp)
  fmap[esp] = fmap[esp]+4
  pop(fmap,ebx)
  pop(fmap,edx)
  pop(fmap,ecx)
  pop(fmap,eax)

def i_PUSHFD(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  push(fmap,fmap(eflags)&0x00fcffffL)

def i_POPFD(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  pop(fmap,eflags)

def i_LAHF(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  x = composer(map(fmap,(sf,zf,bit0,af,bit0,pf,bit1,cf)))
  fmap[ah] = x

def i_SAHF(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  fmap[eflags[0:8]] = fmap(ah)

#------------------------------------------------------------------------------
def _scas_(i,fmap):
  counter = cx if i.misc['adrsz'] else ecx
  a = {1:al, 2:ax, 4:eax}[l]
  src = mem(fmap(edi),l*8)
  x, carry, overflow = SubWithBorrow(a,src)
  if i.misc['rep']:
      fmap[zf] = tst(fmap(counter)==0, fmap(zf), x==0)
      fmap[sf] = tst(fmap(counter)==0, fmap(sf), x<0)
      fmap[cf] = tst(fmap(counter)==0, fmap(cf), carry)
      fmap[of] = tst(fmap(counter)==0, fmap(of), overflow)
      fmap[counter] = fmap(counter)-1
      fmap[eip] = tst(fmap(counter)==0, fmap[eip]+i.length, fmap[eip])
  else:
      fmap[zf] = x==0
      fmap[sf] = x<0
      fmap[cf] = carry
      fmap[of] = overflow
      fmap[eip] = fmap[eip]+i.length
  fmap[edi] = tst(fmap(df),fmap(edi)-l,fmap(edi)+l)

def i_SCASB(i,fmap):
  _scas_(i,fmap,1)
def i_SCASW(i,fmap):
  _scas_(i,fmap,2)
def i_SCASD(i,fmap):
  _scas_(i,fmap,4)

#------------------------------------------------------------------------------
def _lods_(i,fmap,l):
  counter = cx if i.misc['adrsz'] else ecx
  loc = {1:al, 2:ax, 4:eax}[l]
  src = mem(fmap(esi),l*8)
  if i.misc['rep']:
      fmap[loc] = tst(fmap(counter)==0, fmap(loc), src)
      fmap[counter] = fmap(counter)-1
      fmap[eip] = tst(fmap(counter)==0, fmap[eip]+i.length, fmap[eip])
  else:
      fmap[loc] = src
      fmap[eip] = fmap[eip]+i.length
  fmap[esi] = tst(fmap(df),fmap(esi)-l,fmap(esi)+l)

def i_LODSB(i,fmap):
  _lods_(i,fmap,1)
def i_LODSW(i,fmap):
  _lods_(i,fmap,2)
def i_LODSD(i,fmap):
  _lods_(i,fmap,4)

#------------------------------------------------------------------------------
def _stos_(i,fmap,l):
  counter = cx if i.misc['adrsz'] else ecx
  src = {1:al, 2:ax, 4:eax}[l]
  loc = mem(fmap(edi),l*8)
  if i.misc['rep']:
      fmap[loc] = tst(fmap(counter)==0, fmap(loc), src)
      fmap[counter] = fmap(counter)-1
      fmap[eip] = tst(fmap(counter)==0, fmap[eip]+i.length, fmap[eip])
  else:
      fmap[loc] = src
      fmap[eip] = fmap[eip]+i.length
  fmap[edi] = tst(fmap(df),fmap(edi)-l,fmap(edi)+l)

def i_STOSB(i,fmap):
  _stos_(i,fmap,1)
def i_STOSW(i,fmap):
  _stos_(i,fmap,2)
def i_STOSD(i,fmap):
  _stos_(i,fmap,4)

#------------------------------------------------------------------------------
def _movs_(i,fmap):
  counter = cx if i.misc['adrsz'] else ecx
  loc = mem(fmap(edi),l*8)
  src = mem(fmap(esi),l*8)
  if i.misc['rep']:
      fmap[loc] = tst(fmap(counter)==0, fmap(loc), src)
      fmap[counter] = fmap(counter)-1
      fmap[eip] = tst(fmap(counter)==0, fmap[eip]+i.length, fmap[eip])
  else:
      fmap[loc] = src
      fmap[eip] = fmap[eip]+i.length
  fmap[esi] = tst(fmap(df),fmap(esi)-l,fmap(esi)+l)
  fmap[edi] = tst(fmap(df),fmap(edi)-l,fmap(edi)+l)

def i_MOVSB(i,fmap):
  _movs_(i,fmap,1)
def i_MOVSW(i,fmap):
  _movs_(i,fmap,2)
def i_MOVSD(i,fmap):
  _movs_(i,fmap,4)

#------------------------------------------------------------------------------
def i_IN(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  op1 = fmap[i.operands[0]]
  op2 = fmap[i.operands[1]]
  fmap[op1] = ext('IN%s'%op2).call(fmap)

def i_OUT(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  op1 = fmap[i.operands[0]]
  op2 = fmap[i.operands[1]]
  fmap[op1] = ext('OUT%s'%op2).call(fmap)

#op1_src retreives fmap[op1] (op1 value): 
def i_PUSH(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  op1 = fmap(i.operands[0])
  if op1.size==8: op1 = op1.signextend(32)
  push(fmap,op1)

#op1_dst retreives op1 location: 
def i_POP(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  op1 = i.operands[0]
  pop(fmap,op1)

def i_CALL(i,fmap):
  pc = fmap[eip]+i.length
  push(fmap,pc)
  op1 = fmap(i.operands[0])
  op1 = op1.signextend(pc.size)
  target = pc+op1 if not i.misc['absolute'] else op1
  if target._is_ext: target.call(fmap)
  else: fmap[eip] = target


def i_CALLF(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  pc = fmap[eip]+i.length

def i_JMP(i,fmap):
  pc = fmap[eip]+i.length
  op1 = fmap(i.operands[0])
  op1 = op1.signextend(pc.size)
  target = pc+op1 if not i.misc['absolute'] else op1
  if target._is_ext: target.call(fmap)
  else: fmap[eip] = target

def i_JMPF(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  pc = fmap[eip]+i.length

#------------------------------------------------------------------------------
def _loop_(i,fmap,cond):
  opdsz = 16 if i.misc['opdsz'] else 32
  src = i.operands[0].signextend(32)
  loc = fmap[eip]+src
  loc = loc[0:opdsz].zeroextend(32)
  counter = cx if i.misc['adrsz'] else ecx
  fmap[counter] = fmap(counter)-1
  fmap[eip] = tst(fmap(cond), loc, fmap[eip]+i.length)

def i_LOOP(i,fmap):
  cond = (counter!=0)
  _loop_(i,fmap,cond)

def i_LOOPE(i,fmap):
  cond = zf&(counter!=0)
  _loop_(i,fmap,cond)

def i_LOOPNE(i,fmap):
  cond = (~zf)&(counter!=0)
  _loop_(i,fmap,cond)

#------------------------------------------------------------------------------
def i_LSL(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length

def i_LTR(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length

#######################

def i_Jcc(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  op1 = fmap(i.operands[0])
  op1 = op1.signextend(eip.size)
  fmap[eip] = tst(i.cond[1],fmap[eip]+op1,fmap[eip])

def i_RETN(i,fmap):
  src = i.operands[0].v
  pop(fmap,eip)
  fmap[esp] = fmap(esp)+src

def i_INT(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  op1 = fmap(i.operands[0])
  push(fmap,fmap[eip])
  ext('INT%s'%op1).call(fmap)

def i_INC(i,fmap):
  op1 = i.operands[0]
  fmap[eip] = fmap[eip]+i.length
  a = fmap(op1)
  b = cst(1,a.size)
  x,carry,overflow = AddWithCarry(a,b)
  #cf not affected
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[of] = overflow
  fmap[op1] = x

def i_DEC(i,fmap):
  op1 = i.operands[0]
  fmap[eip] = fmap[eip]+i.length
  a = fmap(op1)
  b = cst(1,a.size)
  x,carry,overflow = SubWithBorrow(a,b)
  #cf not affected
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[of] = overflow
  fmap[op1] = x

def i_NEG(i,fmap):
  op1 = i.operands[0]
  fmap[eip] = fmap[eip]+i.length
  a = cst(0,op1.size)
  b = fmap(op1)
  x,carry,overflow = SubWithBorrow(a,b)
  fmap[cf] = b!=0
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[of] = overflow
  fmap[op1] = x

def i_NOT(i,fmap):
  op1 = i.operands[0]
  fmap[eip] = fmap[eip]+i.length
  fmap[op1] = ~fmap(op1)

def i_SETcc(i,fmap):
  op1 = fmap(i.operands[0])
  fmap[eip] = fmap[eip]+i.length
  fmap[op1] = tst(fmap(i.cond[1]),bit1,bit0)

def i_MOV(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  fmap[op1] = op2

def i_MOVBE(i,fmap):
  dst = i.operands[0]
  _t = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  if i.misc['opdsz']==16:
    fmap[dst[0 : 8]] = _t[8 :16]
    fmap[dst[8 :16]] = _t[0 : 8]
  else:
    fmap[dst[0 : 8]] = _t[24:32]
    fmap[dst[8 :16]] = _t[16:24]
    fmap[dst[16:24]] = _t[8 :16]
    fmap[dst[24:32]] = _t[0 : 8]

def i_MOVSX(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  fmap[op1] = op2.signextend(op1.size)

def i_MOVZX(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  fmap[op1] = op2.zeroextend(op1.size)

def i_ADC(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  a=fmap(op1)
  x,carry,overflow = AddWithCarry(a,op2,fmap(cf))
  fmap[zf]  = x==0
  fmap[sf]  = x<0
  fmap[cf]  = carry
  fmap[of]  = overflow
  fmap[op1] = x

def i_ADD(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  a=fmap(op1)
  x,carry,overflow = AddWithCarry(a,op2)
  fmap[zf]  = x==0
  fmap[sf]  = x<0
  fmap[cf]  = carry
  fmap[of]  = overflow
  fmap[op1] = x

def i_SBB(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  a=fmap(op1)
  x,carry,overflow = SubWithBorrow(a,op2,fmap(cf))
  fmap[zf]  = x==0
  fmap[sf]  = x<0
  fmap[cf]  = carry
  fmap[of]  = overflow
  fmap[op1] = x

def i_SUB(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  a=fmap(op1)
  x,carry,overflow = SubWithBorrow(a,op2)
  fmap[zf]  = x==0
  fmap[sf]  = x<0
  fmap[cf]  = carry
  fmap[of]  = overflow
  fmap[op1] = x

def i_AND(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  if op2.size<op1.size:
    op2 = op2.signextend(op1.size)
  x=fmap(op1)&op2
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[cf] = bit0
  fmap[of] = bit0
  fmap[op1] = x

def i_OR(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  x=fmap(op1)|op2
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[cf] = bit0
  fmap[of] = bit0
  fmap[op1] = x

def i_XOR(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  x=fmap(op1)^op2
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[cf] = bit0
  fmap[of] = bit0
  fmap[op1] = x

def i_CMP(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  op1 = fmap(i.operands[0])
  op2 = fmap(i.operands[1])
  x, carry, overflow = SubWithBorrow(op1,op2)
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[cf] = carry
  fmap[of] = overflow

def i_TEST(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  op1 = fmap(i.operands[0])
  op2 = fmap(i.operands[1])
  x = op1&op2
  fmap[zf] = x==0
  fmap[sf] = x[x.size-1:x.size]
  fmap[cf] = bit0
  fmap[of] = bit0

def i_LEA(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[op1] = op2.addr(fmap)

def i_XCHG(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  op1 = i.operands[0]
  op2 = i.operands[1]
  tmp = fmap(op1)
  fmap[op1] = fmap(op2)
  fmap[op2] = tmp

def i_SHR(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  a = fmap(op1)
  if op2._is_cst:
    if op2.value==0: return
    if (a.size>op2.value):
      fmap[cf] = slc(a,op2.value-1,1)
    else:
      fmap[cf] = bit0
  else:
    fmap[cf] = top(1)
  #shr must ignore sign:
  a.sf = +1
  fmap[op1] = a>>op2
  #of is always MSB of a:
  fmap[of] = slc(a,a.size-1,1)

def i_SAR(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  a = fmap(op1)
  if op2._is_cst:
    if op2.value==0: return
    if (a.size>op2.value):
      fmap[cf] = slc(a,op2.value-1,1)
      #of is cleared if 1 was shifted, undefined otherwise (see intel 4-278). 
      fmap[of] = tst(a[0:op2.value]<>0,bit0,top(1))
    else:
      fmap[cf] = slc(a,a.size-1,1)
      fmap[of] = tst(a<>0,bit0,top(1))
  else:
    fmap[cf] = top(1)
    fmap[of] = top(1)
  #sign of a is important because the result is filled with MSB(a)
  fmap[op1] = a>>op2

def i_SHL(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  a = fmap(op1)
  if op2._is_cst:
    if op2.value==0: return
    if (a.size>op2.value):
      fmap[cf] = slc(a,a.size-op2.value,1)
    else:
      fmap[cf] = bit0
  else:
    fmap[cf] = top(1)
  x = a<<op2
  fmap[op1] = x
  #of is cleared if MSB(x)==cf, set otherwise.
  fmap[of] = tst(slc(x,x.size-1,1)==fmap[cf],bit0,bit1)

i_SAL = i_SHL

def i_ROL(i,fmap):
  raise NotImplementedError

def i_ROR(i,fmap):
  raise NotImplementedError

def i_RCL(i,fmap):
  raise NotImplementedError

def i_RCR(i,fmap):
  raise NotImplementedError

def i_CMOVcc(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[eip] = fmap[eip]+i.length
  a = fmap(op1)
  fmap[op1] = tst(fmap(i.cond[1]),op2,a)

def i_SHRD(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  op3 = fmap(i.operands[2])
  fmap[eip] = fmap[eip]+i.length
  # op3 is a cst:
  n = op3.value
  r = op1.size-n
  fmap[op1] = (fmap(op1)>>n) | (op2<<r)

def i_SHLD(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  op3 = fmap(i.operands[2])
  fmap[eip] = fmap[eip]+i.length
  n = op3.value
  r = op1.size-n
  fmap[op1] = (fmap(op1)<<n) | (op2>>r)

def i_IMUL(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  if len(i.operands)==1:
    src = fmap(i.operands[0])
    m,d = {8:(al,ah), 16:(ax,dx), 32:(eax,edx)}[src.size]
    r = m**src
  elif len(i.operands)==2:
    dst,src = i.operands
    m = d = dst
    r = dst**src
  else:
    dst,src,imm = i.operands
    m = d = dst
    r = src**imm.signextend(src.size)
  lo = r[0:src.size]
  hi = r[src.size:r.size]
  fmap[d]  = hi
  fmap[m]  = lo
  fmap[cf] = hi!=(lo>>31)
  fmap[of] = hi!=(lo>>31)

def i_MUL(i,fmap):
  fmap[eip] = fmap[eip]+i.length
  src = fmap(i.operands[0])
  m,d = {8:(al,ah), 16:(ax,dx), 32:(eax,edx)}[src.size]
  r = m**src
  lo = r[0:src.size]
  hi = r[src.size:r.size]
  fmap[d]  = hi
  fmap[m]  = lo
  fmap[cf] = hi!=0
  fmap[of] = hi!=0

def i_RDRAND(i,fmap):
   fmap[eip] = fmap[eip]+i.length
   dst = i.operands[0]
   fmap[dst] = top(dst.size)
   fmap[cf] = top(1)
   for f in (of,sf,zf,af,pf): fmap[f] = bit0

def i_RDTSC(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length
   fmap[edx] = top(32)
   fmap[eax] = top(32)

def i_RDTSCP(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length
   fmap[edx] = top(32)
   fmap[eax] = top(32)
   fmap[ecx] = top(32)

def i_BOUND(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length
   # #UD #BR exceptions not implemented

def i_LFENCE(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length

def i_MFENCE(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length

def i_SFENCE(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length

def i_MWAIT(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length

def i_LGDT(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length

def i_SGDT(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length

def i_LIDT(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length

def i_SIDT(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length

def i_LLDT(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length

def i_SLDT(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length

def i_LMSW(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length
   fmap[cr(0)[0:16]] = top(16)

def i_SMSW(i,fmap):
   logger.warning('%s semantic is not defined'%i.mnemonic)
   fmap[eip] = fmap[eip]+i.length
   dst = i.operands[0]
   fmap[dst] = top(16)

def i_BSF(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  dst,src = i.operands
  x = fmap(src)
  fmap[zf] = x==0
  fmap[dst] = top(dst.size)

def i_BSR(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  dst,src = i.operands
  x = fmap(src)
  fmap[zf] = x==0
  fmap[dst] = top(dst.size)

def i_POPCNT(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  dst,src = i.operands
  fmap[dst] = top(dst.size)
  fmap[cf] = bit0
  fmap[of] = bit0
  fmap[sf] = bit0
  fmap[af] = bit0
  fmap[zf] = fmap(src)==0
  fmap[eip] = fmap[eip]+i.length

def i_LZCNT(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  dst,src = i.operands
  fmap[dst] = top(dst.size)
  fmap[cf] = fmap[zf] = top(1)
  fmap[eip] = fmap[eip]+i.length

def i_TZCNT(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  dst,src = i.operands
  fmap[dst] = top(dst.size)
  fmap[cf] = fmap[zf] = top(1)
  fmap[eip] = fmap[eip]+i.length

def i_BT(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  dst,src = i.operands
  fmap[cf] = top(1)

def i_BTC(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  dst,src = i.operands
  fmap[cf] = top(1)
  fmap[dst] = top(dst.size)

def i_BTR(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  dst,src = i.operands
  fmap[cf] = top(1)
  fmap[dst] = top(dst.size)

def i_BTS(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  dst,src = i.operands
  fmap[cf] = top(1)
  fmap[dst] = top(dst.size)

def i_CLFLUSH(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  # cache not supported

def i_INVD(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  # cache not supported

def i_INVLPG(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  # cache not supported

def i_CLI(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  # interruptions not supported

def i_PREFETCHT0(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  # interruptions not supported
def i_PREFETCHT1(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  # interruptions not supported
def i_PREFETCHT2(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  # interruptions not supported
def i_PREFETCHNTA(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  # interruptions not supported
def i_PREFETCHW(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  # interruptions not supported

def i_LAR(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  dst,src = i.operands
  fmap[zf] = top(1)
  fmap[dst] = top(dst.size)

def i_STR(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length
  dst = i.operands[0]
  fmap[dst] = top(dst.size)

def i_RDMSR(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length

def i_RDPMC(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length

def i_RSM(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = fmap[eip]+i.length

def i_SYSENTER(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = top(32)
  fmap[esp] = top(32)
  fmap[cs]  = top(16)
  fmap[ss]  = top(16)

def i_SYSEXIT(i,fmap):
  logger.warning('%s semantic is not defined'%i.mnemonic)
  fmap[eip] = top(32)
  fmap[esp] = top(32)
  fmap[cs]  = top(16)
  fmap[ss]  = top(16)

