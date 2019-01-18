# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2018 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

from amoco.arch.v850.env import *
from amoco.cas.utils import *

#------------------------------------------------------------------------------
# low level functions :
def _push_(fmap,_x):
  fmap[sp] = fmap[sp]-_x.length
  fmap[mem(sp,_x.size)] = _x

def _pop_(fmap,_l):
  fmap[_l] = fmap(mem(sp,_l.size))
  fmap[sp] = fmap[sp]+_l.length

def _pc(f):
  def npc(i,fmap):
    fmap[pc] = fmap[pc]+i.length
  return npc

# i_xxx is the translation of V850E2S instruction xxx.
#------------------------------------------------------------------------------

# general purpose and cpu-related:
##################################

@_pc
def i_NOP(i,fmap):
  pass

def i_HALT(i,fmap):
  fmap[pc] = ext('HALT',size=pc.size).call(fmap)

@_pc
def i_DI(i,fmap):
  fmap[ID] = bit1

@_pc
def i_EI(i,fmap):
  fmap[ID] = bit0

# arithmetic & logic instructions:
##################################

@_pc
def i_ADD(i,fmap):
  src,dst = i.operands
  r,c,o = AddWithCarry(fmap(dst),fmap(src))
  fmap[Z] = (r==0)
  fmap[S] = (r<0)
  fmap[CY] = c
  fmap[OV] = o
  fmap[dst] = r

@_pc
def i_SATADD(i,fmap):
  src,dst = i.operands
  r,c,o = AddWithCarry(fmap(dst),fmap(src))
  fmap[Z] = (r==0)
  fmap[S] = (r<0)
  fmap[CY] = c
  fmap[OV] = o
  fmap[SAT] = tst(o,bit1,bit0)
  if len(i.operands)==3:
    dst = i.operands[2]
  fmap[dst] = tst(o,tst(r<0,cst(0x7fffffff,32),
                            cst(0x80000000,32))
                   ,r)

@_pc
def i_ADDI(i,fmap):
  imm16,src,dst = i.operands
  imm = imm16.signextend(dst.size)
  r,c,o = AddWithCarry(fmap(src),imm)
  fmap[Z] = (r==0)
  fmap[S] = (r<0)
  fmap[CY] = c
  fmap[OV] = o
  fmap[dst] = r

@_pc
def i_ADF(i,fmap):
  cond,src1,src2,dst = i.operands
  cond = CONDITION[cond][1]
  c = tst(cond,cst(1,dst.size),cst(0,dst.size))
  r,c,o = AddWithCarry(fmap(src1),fmap(src2),c)
  fmap[Z] = (r==0)
  fmap[S] = (r<0)
  fmap[CY] = c
  fmap[OV] = o
  fmap[dst] = r

@_pc
def i_AND(i,fmap):
  src,dst = i.operands
  r = fmap(dst & src)
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[OV] = bit0
  fmap[dst] = r

@_pc
def i_ANDI(i,fmap):
  imm16,src,dst = i.operands
  imm = imm16.zeroextend(dst.size)
  r = fmap(src & imm)
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[OV] = bit0
  fmap[dst] = r

@_pc
def i_DIVU(i,fmap):
  src1,src2,dst = i.operands
  r = fmap(src2/src1)
  fmap[OV] = fmap(tst(src1==0,bit1,bit0))
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[src2] = r
  fmap[dst] = fmap(src2%src1)

i_DIVQU = i_DIVU

@_pc
def i_DIVHU(i,fmap):
  src1,src2 = i.operands[0:2]
  if len(i.operands)==3:
    dst = i.operands[2]
  else:
    dst = None
  q = src1[0:16]
  r = fmap(src2/q)
  fmap[OV] = fmap(tst(q==0,bit1,bit0))
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[src2] = r
  if dst:
    fmap[dst] = fmap(src2%q)

@_pc
def i_MAC(i,fmap):
  src1,src2,src3,dst = i.operands
  r4 = i.misc['reg4']
  r3 = i.misc['reg3']
  off = fmap(composer([src3,R[r3+1]]))
  r = fmap(src1**src2)+off
  fmap[dst] = r[0:32]
  fmap[R[r4+1]] = r[32:64]

i_MACU = i_MAC

@_pc
def i_MUL(i,fmap):
  src1,src2,dst = i.operands
  if src1._is_cst:
    src1 = src1.signextend(32)
  r = src1**src2
  fmap[src2] = r[0:32]
  fmap[dst]  = r[32:64]

@_pc
def i_MULH(i,fmap):
  src1,dst = i.operands
  r = src1[0:16]**dst[0:16]
  fmap[dst]  = r

@_pc
def i_MULHI(i,fmap):
  imm16,src,dst = i.operands
  r = imm16**src[0:16]
  fmap[dst]  = r

@_pc
def i_MULU(i,fmap):
  src1,src2,dst = i.operands
  if src1._is_cst:
    src1 = src1.zeroextend(32)
  r = src1**src2
  fmap[src2] = r[0:32]
  fmap[dst]  = r[32:64]

@_pc
def i_NOT(i,fmap):
  dst = i.operands
  r = fmap(~dst)
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[OV] = bit0
  fmap[dst] = r

@_pc
def i_NOT1(i,fmap):
  bnum,dst = i.operands
  if bnum._is_reg: bnum = fmap(bnum)
  if bnum._is_cst: bnum = bnum.value
  x = composer([fmap(dst)])
  fmap[Z] = ~(x.bit(bnum))
  x[bnum:bnum+1] = ~(x.bit(bnum))
  fmap[dst] = x

@_pc
def i_OR(i,fmap):
  src,dst = i.operands
  r = fmap(dst | src)
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[OV] = bit0
  fmap[dst] = r

@_pc
def i_ORI(i,fmap):
  imm16,src,dst = i.operands
  imm = imm16.zeroextend(dst.size)
  r = fmap(src | imm)
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[OV] = bit0
  fmap[dst] = r

@_pc
def i_XOR(i,fmap):
  src,dst = i.operands
  r = fmap(dst ^ src)
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[OV] = bit0
  fmap[dst] = r

@_pc
def i_XORI(i,fmap):
  imm16,src,dst = i.operands
  imm = imm16.zeroextend(dst.size)
  r = fmap(src ^ imm)
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[OV] = bit0
  fmap[dst] = r

@_pc
def i_SUB(i,fmap):
  src,dst = i.operands
  r,c,o = SubWithBorrow(fmap(dst),fmap(src))
  fmap[Z] = (r==0)
  fmap[S] = (r<0)
  fmap[CY] = c
  fmap[OV] = o
  fmap[dst] = r

@_pc
def i_SUB(i,fmap):
  src,dst = i.operands
  r,c,o = SubWithBorrow(fmap(src),fmap(dst))
  fmap[Z] = (r==0)
  fmap[S] = (r<0)
  fmap[CY] = c
  fmap[OV] = o
  fmap[dst] = r

@_pc
def i_SATSUB(i,fmap):
  src,dst = i.operands
  r,c,o = SubWithBorrow(fmap(dst),fmap(src))
  fmap[Z] = (r==0)
  fmap[S] = (r<0)
  fmap[CY] = c
  fmap[OV] = o
  fmap[SAT] = tst(o,bit1,bit0)
  if len(i.operands)==3:
    dst = i.operands[2]
  fmap[dst] = tst(o,tst(r<0,cst(0x7fffffff,32),
                            cst(0x80000000,32))
                   ,r)

i_SATSUBI = i_SATSUB

# branch :
##########

def i_B(i,fmap):
  disp = i.operands[0]
  tgt = fmap(pc)
  cond = fmap(CONDITION[i.cond][1])
  fmap[pc] = tst(cond,tgt+disp,tgt+i.length)

def i_CALLT(i,fmap):
  imm = i.operands[0]
  fmap[CTPC]  = fmap[pc]+i.length
  fmap[CTPSW] = fmap[PSW]
  offset = fmap(mem(CTBP+imm,32))
  fmap[pc] = fmap(CTBP)+offset

def i_CTRET(i,fmap):
  fmap[pc]  = fmap(CTPC)
  fmap[PSW] = fmap(CTPSW)

def i_EIRET(i,fmap):
  fmap[pc]  = fmap(EIPC)
  fmap[PSW] = fmap(EIPSW)

def i_FERET(i,fmap):
  fmap[pc]  = fmap(FEPC)
  fmap[PSW] = fmap(FEPSW)

def i_JARL(i,fmap):
  disp,dst = i.operands
  fmap[dst] = fmap(pc+i.length)
  fmap[pc] = fmap(pc+disp)

def i_JMP(i,fmap):
  dst = i.operands[-1]
  disp = 0
  if i.length>16:
      disp = i.operands[0]
  fmap[pc] = fmap(dst+disp)

def i_JR(i,fmap):
  disp = i.operands[0]
  fmap[pc] = fmap(pc+disp)

def i_RETI(i,fmap):
  fmap[pc]  = fmap(tst(NP,FEPC,EIPC))
  fmap[PSW] = fmap(tst(NP,FEPSW,EIPSW))

@_pc
def i_SWITCH(i,fmap):
  adr = i.operands[0]
  x = mem(pc+adr<<1,16)
  fmap[pc] = fmap(pc+(x.signextend(pc.size))<<1)

# shift & rotate :
##################

@_pc
def i_BSH(i,fmap):
  src,dst = i.operands
  r = fmap(src)
  fmap[CY] = tst((r[0:8]==0)|(r[8:16]==0),bit1,bit0)
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[OV] = bit0
  fmap[dst] = composer([r[8:16],r[0:8],r[24:32],r[16:24]])

@_pc
def i_BSW(i,fmap):
  src,dst = i.operands
  r = fmap(src)
  fmap[CY] = tst((r[0:8]==0)|(r[8:16]==0)|(r[16:24]==0)|(r[24:32]==0),bit1,bit0)
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[OV] = bit0
  fmap[dst] = composer([r[24:32],r[16:24],r[8:16],r[0:8]])

@_pc
def i_CAXI(i,fmap):
  msrc,rsrc,dst = i.operands
  r,c,o = SubWithBorrow(fmap(rsrc),fmap(msrc))
  fmap[Z] = (r==0)
  fmap[S] = (r<0)
  fmap[CY] = c
  fmap[OV] = o
  fmap[msrc] = tst(r==0,fmap(dst),r)
  fmap[dst] = adr

@_pc
def i_CLR1(i,fmap):
  bnum,dst = i.operands
  if bnum._is_reg: bnum = fmap(bnum)
  if bnum._is_cst: bnum = bnum.value
  x = composer([fmap(dst)])
  fmap[Z] = ~(x.bit(bnum))
  x[bnum:bnum+1] = bit0
  fmap[dst] = x

@_pc
def i_SET1(i,fmap):
  bnum,dst = i.operands
  if bnum._is_reg: bnum = fmap(bnum)
  if bnum._is_cst: bnum = bnum.value
  x = composer([fmap(dst)])
  fmap[Z] = ~(x.bit(bnum))
  x[bnum:bnum+1] = bit1
  fmap[dst] = x

@_pc
def i_TST1(i,fmap):
  bnum,dst = i.operands
  if bnum._is_reg: bnum = fmap(bnum)
  if bnum._is_cst: bnum = bnum.value
  x = composer([fmap(dst)])
  fmap[Z] = ~(x.bit(bnum))
  x[bnum:bnum+1] = bit1

@_pc
def i_HSH(i,fmap):
  src,dst = i.operands
  r = fmap(src)
  fmap[CY] = tst(r[0:16]==0,bit1,bit0)
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[OV] = bit0
  fmap[dst] = r

@_pc
def i_HSW(i,fmap):
  src,dst = i.operands
  r = fmap(src)
  fmap[CY] = tst((r[0:16]==0)|(r[16:32]==0),bit1,bit0)
  fmap[Z] = (r==0)
  fmap[S] = r.bit(r.size-1)
  fmap[OV] = bit0
  fmap[dst] = composer([r[16:32],r[0:16]])

@_pc
def i_SHR(i,fmap):
  shift,src = i.operands[0:2]
  if len(i.operands)==3:
    dst = i.operands[2]
  if shift._is_reg: shift=fmap(shift)
  if shift._is_cst: shift=shift.value
  x = fmap(src)
  if shift>0:
    r = x>>shift
    fmap[CY] = x.bit(shift-1)
    fmap[Z] = (r==0)
    fmap[S] = r.bit(r.size-1)
    fmap[OV] = bit0
    fmap[dst] = x

@_pc
def i_SHL(i,fmap):
  shift,src = i.operands[0:2]
  if len(i.operands)==3:
    dst = i.operands[2]
  if shift._is_reg: shift=fmap(shift)
  if shift._is_cst: shift=shift.value
  x = fmap(src)
  if shift>0:
    r = x<<shift
    fmap[CY] = x.bit(shift-1)
    fmap[Z] = (r==0)
    fmap[S] = r.bit(r.size-1)
    fmap[OV] = bit0
    fmap[dst] = x

# conditionals :
################

@_pc
def i_CMOV(i,fmap):
  cond,src1,src2,dst = i.operands
  cond = CONDITION[cond][1]
  fmap[dst] = fmap(tst(cond,src1,src2))

@_pc
def i_CMP(i,fmap):
  cond,src1,src2 = i.operands
  cond = CONDITION[cond][1]
  r,c,o = SubWithBorrow(fmap(src2),fmap(src1))
  fmap[Z] = (r==0)
  fmap[S] = (r<0)
  fmap[CY] = c
  fmap[OV] = o

@_pc
def i_SASF(i,fmap):
  cond,dst = i.operands
  cond = CONDITION[cond][1]
  x = fmap(dst)<<1
  strue  = x|cst(1,x.size)
  sfalse = x
  fmap[dst] = tst(fmap(cond),strue,sfalse)

@_pc
def i_SBSF(i,fmap):
  cond,src1,src2,dst = i.operands
  cond = CONDITION[cond][1]
  r,c,o = SubWithBorrow(fmap(src2),fmap(src1))
  fmap[Z] = (r==0)
  fmap[S] = (r<0)
  fmap[CY] = c
  fmap[OV] = o
  strue  = r-cst(1,x.size)
  sfalse = r
  fmap[dst] = tst(fmap(cond),strue,sfalse)

@_pc
def i_SETF(i,fmap):
  cond,dst = i.operands
  cond = CONDITION[cond][1]
  fmap[dst] = fmap(tst(cond,cst(1,dst.size),cst(0,dst.size)))

# load & store :
################

@_pc
def i_DISPOSE(i,fmap):
  if len(i.operands)==3:
      dst = i.operands[2]
      fmap[pc] = fmap(dst)
  src,L = i.operands[0:2]
  x = src.a.disp
  # set regs:
  for r in L:
      fmap[r] = fmap(src)
      src.a.disp += 4
  # update sp:
  fmap[sp] = fmap(src.a.base+src.a.disp)
  #restore original operand:
  src.a.disp = x

@_pc
def i_PREPARE(i,fmap):
  L,imm5 = i.operands[0:2]
  disp = 0
  # set regs:
  for r in L:
      fmap[mem(sp,32,disp)] = fmap(r)
      disp -= 4
  # update sp:
  fmap[sp] = fmap(sp)-imm5.zeroextend(32)-disp
  if len(i.operands)==3:
      op3 = i.operands[2]
      fmap[EP] = fmap(op3)

@_pc
def i_LDB(i,fmap):
  src,dst = i.operands
  fmap[dst] = fmap(src).signextend(dst.size)

i_LDH = i_LDB
i_SLDB = i_LDB
i_SLDH = i_LDB

@_pc
def i_LDW(i,fmap):
  src,dst = i.operands
  fmap[dst] = fmap(src)

i_SLDW = i_LDW

@_pc
def i_LDBU(i,fmap):
  src,dst = i.operands
  fmap[dst] = fmap(src).zeroextend(dst.size)

i_LDHU = i_LDBU
i_SLDHU = i_LDBU

@_pc
def i_SSTB(i,fmap):
  src,dst = i.operands
  fmap[dst[0:src.size]] = fmap(src)

i_SSTH = i_SSTB
i_STB = i_SSTB

@_pc
def i_SSTW(i,fmap):
  src,dst = i.operands
  fmap[dst] = fmap(src)

i_STW = i_SSTW

@_pc
def i_MOV(i,fmap):
  src,dst = i.operands
  fmap[dst] = fmap(src)

@_pc
def i_MOVEA(i,fmap):
  imm16,src,dst = i.operands
  fmap[dst] = fmap(src)+imm16.signextend(dst.size)

@_pc
def i_MOVHI(i,fmap):
  imm16,src,dst = i.operands
  fmap[dst] = fmap(src)+composer([cst(0,16),imm16])

@_pc
def i_SXB(i,fmap):
  dst = src = i.operands[0]
  fmap[dst] = fmap(src[0:8]).signextend(dst.size)

@_pc
def i_SXH(i,fmap):
  dst = src = i.operands[0]
  fmap[dst] = fmap(src[0:16]).signextend(dst.size)

@_pc
def i_ZXB(i,fmap):
  dst = src = i.operands[0]
  fmap[dst] = fmap(src[0:8]).zeroextend(dst.size)

@_pc
def i_ZXH(i,fmap):
  dst = src = i.operands[0]
  fmap[dst] = fmap(src[0:16]).zeroextend(dst.size)
