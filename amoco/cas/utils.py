# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license


# utilities for 2's complement number representation system:
# (from: "Digital Arithmetic", M.D.Ercegovac and T.Lang, MK Pulisher)

from amoco.logger import Log
logger = Log(__name__)

from .expressions import *

def Abs(x):
    if x.sf==False: return x
    y = x//(x.size-1)
    return (x+y)^y

def Sign(x):
    return x[x.size-1:x.size]

def AddWithCarry(x,y,c=None):
    if c is None: c = bit0
    c = c.zeroextend(y.size)
    x.sf = y.sf = True
    result = x+y+c
    sx,sy,sz = Sign(x), Sign(y), Sign(result)
    carry = (sx & sy) | ( ~sz & (sx | sy))
    overflow  = (sz^sx) & (sz^sy)
    result.sf = True
    return (result,carry,overflow)

def SubWithBorrow(x,y,c=None):
    if c is None: c = bit0
    c = c.zeroextend(y.size)
    x.sf = y.sf = True
    result = x-y-c
    sx,sy,sz = Sign(x), Sign(y), Sign(result)
    carry = (~sx & sy) | ( sz & (~sx | sy))
    overflow  = (sx^sy) & (sz^sx)
    result.sf = True
    return (result,carry,overflow)

def ROR(x,n):
    return oper('>>>',x,n) #(x>>n | x<<(x.size-n))

def ROL(x,n):
    return oper('<<<',x,n) #(x<<n | x>>(x.size-n))

def RORWithCarry(x,n,c):
    y = composer([x,c])
    ry = ROR(y,n)
    return (ry[0:x.size],ry[x.size:y.size])

def ROLWithCarry(x,n,c):
    y = composer([x,c])
    ry = ROL(y,n)
    return (ry[0:x.size],ry[x.size:y.size])

def get_lsb_msb(v):
    msb = v.bit_length()-1
    lsb = (v & -v).bit_length()-1
    return (lsb,msb)

def ismask(v):
    i1,i2 = get_lsb_msb(v)
    return ((1<<(i2+1))-1) ^ ((1<<i1)-1) == v
