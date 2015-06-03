# -*- coding: utf-8 -*-

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
  fmap[rsp] = fmap(rsp-x.length)
  fmap[mem(rsp,x.size)] = x

def pop(fmap,l):
  fmap[l] = fmap(mem(rsp,l.size))
  fmap[rsp] = fmap(rsp+l.length)

def parity(x):
  x = x.zeroextend(64)
  x = x ^ (x>>1)
  x = (x ^ (x>>2)) & 0x1111111111111111L
  x = x * 0x1111111111111111L
  p = (x>>60).bit(0)
  return p

def parity8(x):
  y = x ^ (x>>4)
  y = cst(0x6996,16)>>(y[0:4])
  p = y.bit(0)
  return p

def halfcarry(x,y,c=None):
    s,carry,o = AddWithCarry(x[0:4],y[0:4],c)
    return carry

def halfborrow(x,y,c=None):
    s,carry,o = SubWithBorrow(x[0:4],y[0:4],c)
    return carry

#------------------------------------------------------------------------------
def i_BSWAP(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  dst = i.operands[0]
  _t = fmap(dst)
  if i.misc['REX'] and i.misc['REX'][0]==1:
      fmap[dst[0 : 8]] = _t[56:64]
      fmap[dst[8 :16]] = _t[48:56]
      fmap[dst[16:24]] = _t[40:48]
      fmap[dst[24:32]] = _t[32:40]
      fmap[dst[32:40]] = _t[24:32]
      fmap[dst[40:48]] = _t[16:24]
      fmap[dst[48:56]] = _t[8 :16]
      fmap[dst[56:64]] = _t[0 : 8]
  else:
      fmap[dst[0 : 8]] = _t[24:32]
      fmap[dst[8 :16]] = _t[16:24]
      fmap[dst[16:24]] = _t[8 :16]
      fmap[dst[24:32]] = _t[0 : 8]

def i_NOP(i,fmap):
  fmap[rip] = fmap[rip]+i.length

def i_WAIT(i,fmap):
  fmap[rip] = fmap[rip]+i.length

# LEAVE instruction is a shortcut for 'mov rsp,ebp ; pop ebp ;'
def i_LEAVE(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  fmap[rsp] = fmap[rbp]
  pop(fmap,rbp)

def i_RET(i,fmap):
  pop(fmap,rip)

def i_HLT(i,fmap):
  fmap[rip] = top(64)

#------------------------------------------------------------------------------
def _ins_(i,fmap,l):
  counter = cx if i.misc['adrsz'] else rcx
  loc = mem(rdi,l*8)
  src = ext('IN',size=l*8).call(fmap,port=fmap(dx))
  if i.misc['rep']:
      fmap[loc] = tst(fmap(counter)==0, fmap(loc), src)
      fmap[counter] = fmap(counter)-1
      fmap[rip] = tst(fmap(counter)==0, fmap[rip]+i.length, fmap[rip])
  else:
      fmap[loc] = src
      fmap[rip] = fmap[rip]+i.length
  fmap[rdi] = tst(fmap(df),fmap(rdi)-l,fmap(rdi)+l)

def i_INSB(i,fmap):
  _ins_(i,fmap,1)
def i_INSW(i,fmap):
  _ins_(i,fmap,2)
def i_INSD(i,fmap):
  _ins_(i,fmap,4)

#------------------------------------------------------------------------------
def _outs_(i,fmap,l):
  counter = cx if i.misc['adrsz'] else rcx
  src = fmap(mem(rsi,l*8))
  ext('OUT').call(fmap,src=fmap(mem(rsi,l*8)))
  if i.misc['rep']:
      fmap[counter] = fmap(counter)-1
      fmap[rip] = tst(fmap(counter)==0, fmap[rip]+i.length, fmap[rip])
  else:
      fmap[rip] = fmap[rip]+i.length
  fmap[rdi] = tst(fmap(df),fmap(rdi)-l,fmap(rdi)+l)

def i_OUTSB(i,fmap):
  _outs_(i,fmap,1)
def i_OUTSW(i,fmap):
  _outs_(i,fmap,2)
def i_OUTSD(i,fmap):
  _outs_(i,fmap,4)

#------------------------------------------------------------------------------
def i_INT3(i,fmap):
  fmap[rip] = ext('INT3',size=64)

def i_CLC(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  fmap[cf] = bit0

def i_STC(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  fmap[cf] = bit1

def i_CLD(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  fmap[df] = bit0

def i_STD(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  fmap[df] = bit1

def i_CMC(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  fmap[cf] = ~fmap(cf)

def i_CBW(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  fmap[ax] = fmap(al).signextend(16)

def i_CWDE(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  fmap[eax] = fmap(ax).signextend(32)

def i_CDQE(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  fmap[rax] = fmap(eax).signextend(64)

def i_CWD(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  x = fmap(ax).signextend(32)
  fmap[dx] = x[16:32]
  fmap[ax] = x[0:16]

def i_CDQ(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  x = fmap(eax).signextend(64)
  fmap[edx] = x[32:64]
  fmap[eax] = x[0:32]

def i_CQO(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  x = fmap(eax).signextend(128)
  fmap[rdx] = x[64:128]
  fmap[rax] = x[0:64]

def i_PUSHFQ(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  push(fmap,fmap(rflags)&0x0000000000fcffffL)

def i_POPFQ(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  pop(fmap,rflags)

#------------------------------------------------------------------------------
def _cmps_(i,fmap,l):
  counter,d,s = (ecx,edi,esi) if i.misc['adrsz'] else (rcx,rdi,rsi)
  dst = fmap(mem(d,l*8))
  src = fmap(mem(s,l*8))
  x, carry, overflow = SubWithBorrow(dst,src)
  if i.misc['rep']:
      fmap[af] = tst(fmap(counter)==0, fmap(af), halfborrow(dst,src))
      fmap[pf] = tst(fmap(counter)==0, fmap(pf), parity8(x[0:8]))
      fmap[zf] = tst(fmap(counter)==0, fmap(zf), x==0)
      fmap[sf] = tst(fmap(counter)==0, fmap(sf), x<0)
      fmap[cf] = tst(fmap(counter)==0, fmap(cf), carry)
      fmap[of] = tst(fmap(counter)==0, fmap(of), overflow)
      fmap[counter] = fmap(counter)-1
      fmap[rip] = tst(fmap(counter)==0, fmap[rip]+i.length, fmap[rip])
  else:
      fmap[af] = halfborrow(dst,src)
      fmap[pf] = parity8(x[0:8])
      fmap[zf] = x==0
      fmap[sf] = x<0
      fmap[cf] = carry
      fmap[of] = overflow
      fmap[rip] = fmap[rip]+i.length
  fmap[d] = fmap(tst(df,d-l,d+l))
  fmap[s] = fmap(tst(df,s-l,s+l))

def i_CMPSB(i,fmap):
  _cmps_(i,fmap,1)
def i_CMPSW(i,fmap):
  _cmps_(i,fmap,2)
def i_CMPSD(i,fmap):
  _cmps_(i,fmap,4)
def i_CMPSQ(i,fmap):
  _cmps_(i,fmap,8)

#------------------------------------------------------------------------------
def _scas_(i,fmap,l):
  counter,d = ecx,edi if i.misc['adrsz'] else rcx,rdi
  a = fmap({1:al, 2:ax, 4:eax, 8:rax}[l])
  src = fmap(mem(d,l*8))
  x, carry, overflow = SubWithBorrow(a,src)
  if i.misc['rep']:
      fmap[af] = tst(fmap(counter)==0, fmap(af), halfborrow(a,src))
      fmap[pf] = tst(fmap(counter)==0, fmap(pf), parity8(x[0:8]))
      fmap[zf] = tst(fmap(counter)==0, fmap(zf), x==0)
      fmap[sf] = tst(fmap(counter)==0, fmap(sf), x<0)
      fmap[cf] = tst(fmap(counter)==0, fmap(cf), carry)
      fmap[of] = tst(fmap(counter)==0, fmap(of), overflow)
      fmap[counter] = fmap(counter)-1
      fmap[rip] = tst(fmap(counter)==0, fmap[rip]+i.length, fmap[rip])
  else:
      fmap[af] = halfborrow(a,src)
      fmap[pf] = parity8(x[0:8])
      fmap[zf] = x==0
      fmap[sf] = x<0
      fmap[cf] = carry
      fmap[of] = overflow
      fmap[rip] = fmap[rip]+i.length
  fmap[d] = tst(fmap(df),fmap(d)-l,fmap(d)+l)

def i_SCASB(i,fmap):
  _scas_(i,fmap,1)
def i_SCASW(i,fmap):
  _scas_(i,fmap,2)
def i_SCASD(i,fmap):
  _scas_(i,fmap,4)
def i_SCASQ(i,fmap):
  _scas_(i,fmap,8)

#------------------------------------------------------------------------------
def _lods_(i,fmap,l):
  counter,s = (ecx,esi) if i.misc['adrsz'] else (rcx,rsi)
  loc = {1:al, 2:ax, 4:eax, 8:rax}[l]
  src = fmap(mem(s,l*8))
  if i.misc['rep']:
      fmap[loc] = tst(fmap(counter)==0, fmap(loc), src)
      fmap[counter] = fmap(counter)-1
      fmap[rip] = tst(fmap(counter)==0, fmap[rip]+i.length, fmap[rip])
  else:
      fmap[loc] = src
      fmap[rip] = fmap[rip]+i.length
  fmap[s] = fmap(tst(df,s-l,s+l))

def i_LODSB(i,fmap):
  _lods_(i,fmap,1)
def i_LODSW(i,fmap):
  _lods_(i,fmap,2)
def i_LODSD(i,fmap):
  _lods_(i,fmap,4)
def i_LODSQ(i,fmap):
  _lods_(i,fmap,8)

#------------------------------------------------------------------------------
def _stos_(i,fmap,l):
  if i.misc['adrsz']==32:
      counter,d = ecx,edi
  else:
      counter,d = rcx,rdi
  loc = mem(d,l*8)
  src = fmap({1:al, 2:ax, 4:eax, 8:rax}[l])
  if i.misc['rep']:
      fmap[loc] = tst(fmap(counter)==0, fmap(loc), src)
      fmap[counter] = fmap(counter)-1
      fmap[rip] = tst(fmap(counter)==0, fmap[rip]+i.length, fmap[rip])
  else:
      fmap[loc] = src
      fmap[rip] = fmap[rip]+i.length
  fmap[d] = tst(fmap(df),fmap(d)-l,fmap(d)+l)

def i_STOSB(i,fmap):
  _stos_(i,fmap,1)
def i_STOSW(i,fmap):
  _stos_(i,fmap,2)
def i_STOSD(i,fmap):
  _stos_(i,fmap,4)
def i_STOSQ(i,fmap):
  _stos_(i,fmap,8)

#------------------------------------------------------------------------------
def _movs_(i,fmap,l):
  if i.misc['adrsz']==32:
      counter,d,s = ecx,edi,esi
  else:
      counter,d,s = rcx,rdi,rsi
  loc = mem(d,l*8)
  src = fmap(mem(s,l*8))
  if i.misc['rep']:
      fmap[loc] = tst(fmap(counter)==0, fmap(loc), src)
      fmap[counter] = fmap(counter)-1
      fmap[rip] = tst(fmap(counter)==0, fmap[rip]+i.length, fmap[rip])
  else:
      fmap[loc] = src
      fmap[rip] = fmap[rip]+i.length
  fmap[s] = tst(fmap(df),fmap(s)-l,fmap(s)+l)
  fmap[d] = tst(fmap(df),fmap(d)-l,fmap(d)+l)

def i_MOVSB(i,fmap):
  _movs_(i,fmap,1)
def i_MOVSW(i,fmap):
  _movs_(i,fmap,2)
def i_MOVSD(i,fmap):
  _movs_(i,fmap,4)
def i_MOVSQ(i,fmap):
  _movs_(i,fmap,8)

#------------------------------------------------------------------------------
def i_IN(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[op1] = ext('IN%s'%op2,op1.size).call(fmap)

def i_OUT(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  op1 = fmap(i.operands[0])
  op2 = fmap(i.operands[1])
  ext('OUT%s'%op1).call(fmap,arg=op2)

#op1_src retreives fmap[op1] (op1 value):
def i_PUSH(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  op1 = fmap(i.operands[0])
  if op1.size==8: op1 = op1.signextend(64)
  push(fmap,op1)

#op1_dst retreives op1 location:
def i_POP(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  op1 = i.operands[0]
  pop(fmap,op1)

def i_CALL(i,fmap):
  pc = fmap[rip]+i.length
  push(fmap,pc)
  op1 = fmap(i.operands[0])
  op1 = op1.signextend(pc.size)
  target = pc+op1 if not i.misc['absolute'] else op1
  fmap[rip] = target


def i_CALLF(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  pc = fmap[rip]+i.length

def i_JMP(i,fmap):
  pc = fmap[rip]+i.length
  fmap[rip] = pc
  op1 = fmap(i.operands[0])
  op1 = op1.signextend(pc.size)
  target = pc+op1 if not i.misc['absolute'] else op1
  fmap[rip] = target

def i_JMPF(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  pc = fmap[rip]+i.length

#------------------------------------------------------------------------------
def _loop_(i,fmap,cond):
  opdsz = 16 if i.misc['opdsz'] else 64
  src = i.operands[0].signextend(64)
  loc = fmap[rip]+src
  loc = loc[0:opdsz].zeroextend(64)
  counter = cx if i.misc['adrsz'] else ecx
  REX = i.misc['REX']
  W = 0
  if REX: W=REX[0]
  if W==1: counter = rcx
  fmap[counter] = fmap(counter)-1
  fmap[rip] = tst(fmap(cond), loc, fmap[rip]+i.length)

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
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length

def i_LTR(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length

#######################

def i_Jcc(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  op1 = fmap(i.operands[0])
  op1 = op1.signextend(rip.size)
  cond = i.cond[1]
  fmap[rip] = tst(fmap(cond),fmap[rip]+op1,fmap[rip])

def i_RETN(i,fmap):
  src = i.operands[0].v
  pop(fmap,rip)
  fmap[rsp] = fmap(rsp)+src

def i_INT(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  op1 = fmap(i.operands[0])
  push(fmap,fmap[rip])
  fmap[rip] = ext('INT',port=op1,size=64)

def i_INC(i,fmap):
  op1 = i.operands[0]
  fmap[rip] = fmap[rip]+i.length
  a = fmap(op1)
  b = cst(1,a.size)
  x,carry,overflow = AddWithCarry(a,b)
  #cf not affected
  fmap[af] = halfcarry(a,b)
  fmap[pf] = parity8(x[0:8])
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[of] = overflow
  fmap[op1] = x

def i_DEC(i,fmap):
  op1 = i.operands[0]
  fmap[rip] = fmap[rip]+i.length
  a = fmap(op1)
  b = cst(1,a.size)
  x,carry,overflow = SubWithBorrow(a,b)
  #cf not affected
  fmap[af] = halfborrow(a,b)
  fmap[pf] = parity8(x[0:8])
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[of] = overflow
  fmap[op1] = x

def i_NEG(i,fmap):
  op1 = i.operands[0]
  fmap[rip] = fmap[rip]+i.length
  a = cst(0,op1.size)
  b = fmap(op1)
  x,carry,overflow = SubWithBorrow(a,b)
  fmap[af] = halfborrow(a,b)
  fmap[pf] = parity8(x[0:8])
  fmap[cf] = b!=0
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[of] = overflow
  fmap[op1] = x

def i_NOT(i,fmap):
  op1 = i.operands[0]
  fmap[rip] = fmap[rip]+i.length
  fmap[op1] = ~fmap(op1)

def i_SETcc(i,fmap):
  op1 = fmap(i.operands[0])
  fmap[rip] = fmap[rip]+i.length
  fmap[op1] = tst(fmap(i.cond[1]),cst(1,op1.size),cst(0,op1.size))

def i_MOV(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  fmap[op1] = op2

def i_MOVBE(i,fmap):
  dst = i.operands[0]
  _t = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  if i.misc['opdsz']==16:
    fmap[dst[0 : 8]] = _t[8 :16]
    fmap[dst[8 :16]] = _t[0 : 8]
  else:
    fmap[dst[0 : 8]] = _t[56:64]
    fmap[dst[8 :16]] = _t[48:56]
    fmap[dst[16:24]] = _t[40:48]
    fmap[dst[24:32]] = _t[32:40]
    fmap[dst[32:40]] = _t[24:32]
    fmap[dst[40:48]] = _t[16:24]
    fmap[dst[48:56]] = _t[8 :16]
    fmap[dst[56:64]] = _t[0 : 8]

def i_MOVSX(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  fmap[op1] = op2.signextend(op1.size)

def i_MOVSXD(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  fmap[op1] = op2.signextend(op1.size)

def i_MOVZX(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  fmap[op1] = op2.zeroextend(op1.size)

def i_ADC(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  a=fmap(op1)
  x,carry,overflow = AddWithCarry(a,op2,fmap(cf))
  fmap[pf]  = parity8(x[0:8])
  fmap[af]  = halfcarry(a,op2,c)
  fmap[zf]  = x==0
  fmap[sf]  = x<0
  fmap[cf]  = carry
  fmap[of]  = overflow
  fmap[op1] = x

def i_ADD(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  a=fmap(op1)
  x,carry,overflow = AddWithCarry(a,op2)
  fmap[pf]  = parity8(x[0:8])
  fmap[af]  = halfcarry(a,op2)
  fmap[zf]  = x==0
  fmap[sf]  = x<0
  fmap[cf]  = carry
  fmap[of]  = overflow
  fmap[op1] = x

def i_SBB(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  a=fmap(op1)
  c=fmap(cf)
  x,carry,overflow = SubWithBorrow(a,op2,c)
  fmap[pf]  = parity8(x[0:8])
  fmap[af]  = halfborrow(a,op2,c)
  fmap[zf]  = x==0
  fmap[sf]  = x<0
  fmap[cf]  = carry
  fmap[of]  = overflow
  fmap[op1] = x

def i_SUB(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  a=fmap(op1)
  x,carry,overflow = SubWithBorrow(a,op2)
  fmap[pf]  = parity8(x[0:8])
  fmap[af]  = halfborrow(a,op2)
  fmap[zf]  = x==0
  fmap[sf]  = x<0
  fmap[cf]  = carry
  fmap[of]  = overflow
  fmap[op1] = x

def i_AND(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  if op2.size<op1.size:
    op2 = op2.signextend(op1.size)
  x=fmap(op1)&op2
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[cf] = bit0
  fmap[of] = bit0
  fmap[pf] = parity8(x[0:8])
  fmap[op1] = x

def i_OR(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  x=fmap(op1)|op2
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[cf] = bit0
  fmap[of] = bit0
  fmap[pf] = parity8(x[0:8])
  fmap[op1] = x

def i_XOR(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  x=fmap(op1)^op2
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[cf] = bit0
  fmap[of] = bit0
  fmap[pf] = parity8(x[0:8])
  fmap[op1] = x

def i_CMP(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  op1 = fmap(i.operands[0])
  op2 = fmap(i.operands[1])
  x, carry, overflow = SubWithBorrow(op1,op2)
  fmap[af] = halfborrow(op1,op2)
  fmap[zf] = x==0
  fmap[sf] = x<0
  fmap[cf] = carry
  fmap[of] = overflow
  fmap[pf] = parity8(x[0:8])

def i_CMPXCHG(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  dst,src = i.operands
  acc = {8:al,16:ax,32:eax,64:rax}[dst.size]
  t = fmap(acc==dst)
  fmap[zf] = tst(t,bit1,bit0)
  v = fmap(dst)
  fmap[dst] = tst(t,fmap(src),v)
  fmap[acc] = v

def i_CMPXCHG8B(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  dst = i.operands[0]
  src = composer([ebx,ecx])
  acc = composer([eax,edx])
  t = fmap(acc==dst)
  fmap[zf] = tst(t,bit1,bit0)
  v = fmap(dst)
  fmap[dst] = tst(t,fmap(src),v)
  fmap[eax] = v[0:32]
  fmap[edx] = v[32:64]

def i_CMPXCHG16B(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  dst = i.operands[0]
  src = composer([rbx,rcx])
  acc = composer([rax,rdx])
  t = fmap(acc==dst)
  fmap[zf] = tst(t,bit1,bit0)
  v = fmap(dst)
  fmap[dst] = tst(t,fmap(src),v)
  fmap[rax] = v[0:64]
  fmap[rdx] = v[64:128]

def i_TEST(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  op1 = fmap(i.operands[0])
  op2 = fmap(i.operands[1])
  x = op1&op2
  fmap[zf] = x==0
  fmap[sf] = x[x.size-1:x.size]
  fmap[cf] = bit0
  fmap[of] = bit0
  fmap[pf] = parity8(x[0:8])

def i_LEA(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  op1 = i.operands[0]
  op2 = i.operands[1]
  adr = op2.addr(fmap)
  if   op1.size>adr.size: adr = adr.zeroextend(op1.size)
  elif op1.size<adr.size: adr = adr[0:op1.size]
  fmap[op1] = adr

def i_XCHG(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  op1 = i.operands[0]
  op2 = i.operands[1]
  tmp = fmap(op1)
  fmap[op1] = fmap(op2)
  fmap[op2] = tmp

def i_SHR(i,fmap):
  REX = i.misc['REX']
  W=0
  if REX: W=REX[0]
  mask = 0x3f if W==1 else 0x1f
  op1 = i.operands[0]
  count = fmap(i.operands[1]&mask)
  fmap[rip] = fmap[rip]+i.length
  a = fmap(op1)
  if count._is_cst:
    if count.value==0: return # flags unchanged
    if count.value==1:
        fmap[of] = a.bit(-1) # MSB of a
    else:
        fmap[of] = top(1)
    if count.value<=a.size:
        fmap[cf] = a.bit(count.value-1)
    else:
        fmap[cf] = bit0
  else:
    fmap[cf] = top(1)
    fmap[of] = top(1)
  res = a>>count
  fmap[op1] = res
  fmap[sf] = (res<0)
  fmap[zf] = (res==0)
  fmap[pf] = parity8(res[0:8])

def i_SAR(i,fmap):
  REX = i.misc['REX']
  W=0
  if REX: W=REX[0]
  mask = 0x3f if W==1 else 0x1f
  op1 = i.operands[0]
  count = fmap(i.operands[1]&mask)
  fmap[rip] = fmap[rip]+i.length
  a = fmap(op1)
  if count._is_cst:
    if count.value==0: return
    if count.value==1:
        fmap[of] = bit0
    else:
        fmap[of] = top(1)
    if count.value<=a.size:
        fmap[cf] = a.bit(count.value-1)
    else:
        fmap[cf] = a.bit(-1)
  else:
    fmap[cf] = top(1)
    fmap[of] = top(1)
  res = a//count  # (// is used as arithmetic shift in cas.py)
  fmap[op1] = res
  fmap[sf] = (res<0)
  fmap[zf] = (res==0)
  fmap[pf] = parity8(res[0:8])


def i_SHL(i,fmap):
  REX = i.misc['REX']
  W=0
  if REX: W=REX[0]
  mask = 0x3f if W==1 else 0x1f
  op1 = i.operands[0]
  count = fmap(i.operands[1]&mask)
  fmap[rip] = fmap[rip]+i.length
  a = fmap(op1)
  x = a<<count
  if count._is_cst:
    if count.value==0: return
    if count.value==1:
        fmap[of] = x.bit(-1)^fmap(cf)
    else:
        fmap[of] = top(1)
    if count.value<=a.size:
        fmap[cf] = a.bit(a.size-count.value)
    else:
        fmap[cf] = bit0
  else:
    fmap[cf] = top(1)
    fmap[of] = top(1)
  fmap[op1] = x
  fmap[sf] = (x<0)
  fmap[zf] = (x==0)
  fmap[pf] = parity8(x[0:8])

i_SAL = i_SHL

def i_ROL(i,fmap):
  REX = i.misc['REX']
  W=0
  if REX: W=REX[0]
  mask = 0x3f if W==1 else 0x1f
  op1 = i.operands[0]
  size = op1.size
  count = fmap(i.operands[1]&mask)%size
  fmap[rip] = fmap[rip]+i.length
  a = fmap(op1)
  x = ROL(a,count)
  if count._is_cst:
    if count.value==0: return
    fmap[cf] = x.bit(0)
    if count.value==1:
        fmap[of] = x.bit(-1)^fmap(cf)
    else:
        fmap[of] = top(1)
  else:
    fmap[cf] = top(1)
    fmap[of] = top(1)
  fmap[op1] = x

def i_ROR(i,fmap):
  REX = i.misc['REX']
  W=0
  if REX: W=REX[0]
  mask = 0x3f if W==1 else 0x1f
  op1 = i.operands[0]
  size = op1.size
  count = fmap(i.operands[1]&mask)%size
  fmap[rip] = fmap[rip]+i.length
  a = fmap(op1)
  x = ROR(a,count)
  if count._is_cst:
    if count.value==0: return
    fmap[cf] = x.bit(-1)
    if count.value==1:
        fmap[of] = x.bit(-1)^x.bit(-2)
    else:
        fmap[of] = top(1)
  else:
    fmap[cf] = top(1)
    fmap[of] = top(1)
  fmap[op1] = x

def i_RCL(i,fmap):
  REX = i.misc['REX']
  W=0
  if REX: W=REX[0]
  mask = 0x3f if W==1 else 0x1f
  op1 = i.operands[0]
  size = op1.size
  if size<32: size=size+1 # count cf
  count = fmap(i.operands[1]&mask)%size
  fmap[rip] = fmap[rip]+i.length
  a = fmap(op1)
  x,carry = ROLWithCarry(a,count,fmap(cf))
  if count._is_cst:
    if count.value==0: return
    fmap[cf] = carry
    if count.value==1:
        fmap[of] = x.bit(-1)^fmap(cf)
    else:
        fmap[of] = top(1)
  else:
    fmap[cf] = top(1)
    fmap[of] = top(1)
  fmap[op1] = x

def i_RCR(i,fmap):
  REX = i.misc['REX']
  W=0
  if REX: W=REX[0]
  mask = 0x3f if W==1 else 0x1f
  op1 = i.operands[0]
  size = op1.size
  if size<32: size=size+1 # count cf
  count = fmap(i.operands[1]&mask)%size
  fmap[rip] = fmap[rip]+i.length
  a = fmap(op1)
  x,carry = RORWithCarry(a,count,fmap(cf))
  if count._is_cst:
    if count.value==0: return
    if count.value==1:
        fmap[of] = a.bit(-1)^fmap(cf)
    else:
        fmap[of] = top(1)
  else:
    fmap[cf] = top(1)
    fmap[of] = top(1)
  fmap[cf] = carry
  fmap[op1] = x

def i_CMOVcc(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  fmap[rip] = fmap[rip]+i.length
  a = fmap(op1)
  fmap[op1] = tst(fmap(i.cond[1]),op2,a)

def i_SHRD(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  op3 = fmap(i.operands[2])
  fmap[rip] = fmap[rip]+i.length
  # op3 is a cst:
  n = op3.value
  r = op1.size-n
  x = (fmap(op1)>>n) | (op2<<r)
  fmap[op1] = x
  fmap[sf] = (x<0)
  fmap[zf] = (x==0)
  fmap[pf] = parity8(x[0:8])

def i_SHLD(i,fmap):
  op1 = i.operands[0]
  op2 = fmap(i.operands[1])
  op3 = fmap(i.operands[2])
  fmap[rip] = fmap[rip]+i.length
  n = op3.value
  r = op1.size-n
  x = (fmap(op1)<<n) | (op2>>r)
  fmap[op1] = x
  fmap[sf] = (x<0)
  fmap[zf] = (x==0)
  fmap[pf] = parity8(x[0:8])

def i_IMUL(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  if len(i.operands)==1:
    src = i.operands[0]
    m,d = {8:(al,ah), 16:(ax,dx), 32:(eax,edx), 64:(rax,rdx)}[src.size]
    r = fmap(m**src)
  elif len(i.operands)==2:
    dst,src = i.operands
    m = d = dst
    r = fmap(dst**src)
  else:
    dst,src,imm = i.operands
    m = d = dst
    r = fmap(src**imm.signextend(src.size))
  lo = r[0:src.size]
  hi = r[src.size:r.size]
  fmap[d]  = hi
  fmap[m]  = lo
  fmap[cf] = hi!=(lo>>31)
  fmap[of] = hi!=(lo>>31)

def i_MUL(i,fmap):
  fmap[rip] = fmap[rip]+i.length
  src = i.operands[0]
  m,d = {8:(al,ah), 16:(ax,dx), 32:(eax,edx), 64:(rax,rdx)}[src.size]
  r = fmap(m**src)
  lo = r[0:src.size]
  hi = r[src.size:r.size]
  fmap[d]  = hi
  fmap[m]  = lo
  fmap[cf] = hi!=0
  fmap[of] = hi!=0

def i_RDRAND(i,fmap):
   fmap[rip] = fmap[rip]+i.length
   dst = i.operands[0]
   fmap[dst] = top(dst.size)
   fmap[cf] = top(1)
   for f in (of,sf,zf,af,pf): fmap[f] = bit0

def i_RDTSC(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length
   fmap[rdx] = top(64)
   fmap[rax] = top(64)

def i_RDTSCP(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length
   fmap[rdx] = top(64)
   fmap[rax] = top(64)
   fmap[rcx] = top(64)

def i_BOUND(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length
   # #UD #BR exceptions not implemented

def i_LFENCE(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length

def i_MFENCE(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length

def i_SFENCE(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length

def i_MWAIT(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length

def i_LGDT(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length

def i_SGDT(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length

def i_LIDT(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length

def i_SIDT(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length

def i_LLDT(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length

def i_SLDT(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length

def i_LMSW(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length
   fmap[cr(0)[0:16]] = top(16)

def i_SMSW(i,fmap):
   logger.verbose('%s semantic is not defined'%i.mnemonic)
   fmap[rip] = fmap[rip]+i.length
   dst = i.operands[0]
   fmap[dst] = top(16)

def i_BSF(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  dst,src = i.operands
  x = fmap(src)
  fmap[zf] = x==0
  fmap[dst] = top(dst.size)

def i_BSR(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  dst,src = i.operands
  x = fmap(src)
  fmap[zf] = x==0
  fmap[dst] = top(dst.size)

def i_POPCNT(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  dst,src = i.operands
  fmap[dst] = top(dst.size)
  fmap[cf] = bit0
  fmap[of] = bit0
  fmap[sf] = bit0
  fmap[af] = bit0
  fmap[zf] = fmap(src)==0
  fmap[rip] = fmap[rip]+i.length

def i_LZCNT(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  dst,src = i.operands
  fmap[dst] = top(dst.size)
  fmap[cf] = fmap[zf] = top(1)
  fmap[rip] = fmap[rip]+i.length

def i_TZCNT(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  dst,src = i.operands
  fmap[dst] = top(dst.size)
  fmap[cf] = fmap[zf] = top(1)
  fmap[rip] = fmap[rip]+i.length

def i_BT(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  dst,src = i.operands
  fmap[cf] = top(1)

def i_BTC(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  dst,src = i.operands
  fmap[cf] = top(1)
  fmap[dst] = top(dst.size)

def i_BTR(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  dst,src = i.operands
  fmap[cf] = top(1)
  fmap[dst] = top(dst.size)

def i_BTS(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  dst,src = i.operands
  fmap[cf] = top(1)
  fmap[dst] = top(dst.size)

def i_CLFLUSH(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  # cache not supported

def i_INVD(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  # cache not supported

def i_INVLPG(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  # cache not supported

def i_CLI(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  # interruptions not supported

def i_PREFETCHT0(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  # interruptions not supported
def i_PREFETCHT1(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  # interruptions not supported
def i_PREFETCHT2(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  # interruptions not supported
def i_PREFETCHNTA(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  # interruptions not supported
def i_PREFETCHW(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  # interruptions not supported

def i_LAR(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  dst,src = i.operands
  fmap[zf] = top(1)
  fmap[dst] = top(dst.size)

def i_STR(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length
  dst = i.operands[0]
  fmap[dst] = top(dst.size)

def i_RDMSR(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length

def i_RDPMC(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length

def i_RSM(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = fmap[rip]+i.length

def i_SYSENTER(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = top(32)
  fmap[rsp] = top(32)
  fmap[cs]  = top(16)
  fmap[ss]  = top(16)

def i_SYSEXIT(i,fmap):
  logger.verbose('%s semantic is not defined'%i.mnemonic)
  fmap[rip] = top(32)
  fmap[rsp] = top(32)
  fmap[cs]  = top(16)
  fmap[ss]  = top(16)

