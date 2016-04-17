# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.

from amoco.arch.x86 import env

from amoco.arch.core import *

# for ia32 arch we want some specialized 'modrm' format
# so we redefine ispec decorator here to allow /0-/7 and /r
# tokens in the spec format, following the Intel doc to
# indicate how ModR/M byte should be used :
class ispec_ia32(ispec):
    def __init__(self,format,**kargs):
        n = format.find('/')
        if 0<n<len(format)-1:
            c = format[n+1]
            if c=='r':
                f=format.replace('/r','RM(3) REG(3) Mod(2) ~data(*)')
            else:
                f=format.replace('/%c'%c,'RM(3) %s Mod(2) ~data(*)'%Bits(int(c,8),3))
        else:
            f=format
        ispec.__init__(self,f,**kargs)

# read ModR/M + SIB values and update obj:
def getModRM(obj,Mod,RM,data):
    opdsz = obj.misc['opdsz'] or env.internals['mode']
    adrsz = obj.misc['adrsz'] or env.internals['mode']
    seg   = obj.misc['segreg']
    if seg is None: seg=''
    # r/16/32 case:
    if Mod==0b11:
        op1 = env.getreg(RM,opdsz)
        return op1,data
    # 32-bit SIB cases:
    if adrsz==32 and RM==0b100:
        # read SIB byte in data:
        if data.size<8: raise InstructionError(obj)
        sib,data = data[0:8],data[8:data.size]
        # add sib byte:
        obj.bytes += pack(sib)
        # decode base & scaled index
        b = env.getreg(sib[0:3].int(),adrsz)
        i = env.getreg(sib[3:6].int(),adrsz)
        ss = 1<<(sib[6:8].int())
        s = i*ss if not i.ref in ('esp','sp') else 0
    else:
        s = 0
        if adrsz==32:
            b = env.getreg(RM,adrsz)
        else:
            b =  (env.bx+env.si,
                  env.bx+env.di,
                  env.bp+env.si,
                  env.bp+env.di,
                  env.si,
                  env.di,
                  env.bp,
                  env.bx)[RM]
    # check [disp16/32] case:
    if (b is env.ebp or b is env.bp) and Mod==0:
        b=env.cst(0,adrsz)
        Mod = 0b10
    # now read displacement bytes:
    if Mod==0b00:
        d = 0
    elif Mod==0b01:
        if data.size<8: raise InstructionError(obj)
        d = data[0:8]
        data = data[8:data.size]
        obj.bytes += pack(d)
        d = d.signextend(adrsz).int(-1)
    elif Mod==0b10:
        if data.size<adrsz: raise InstructionError(obj)
        d = data[0:adrsz]
        obj.bytes += pack(d)
        data = data[adrsz:data.size]
        d = d.int(-1)
    bs = b+s
    if bs._is_cst and bs.v==0x0:
        bs.size = adrsz
        bs.v = d & bs.mask
        d = 0
    return env.mem(bs,opdsz,seg,d),data

# Condition codes:
CONDITION_CODES = {
    0x0: ('O' , (env.of==1)),
    0x1: ('NO', (env.of==0)),
    0x2: ('B/NAE/C', (env.cf==1)),
    0x3: ('NB/AE/NC', (env.cf==0)),
    0x4: ('Z/E', (env.zf==1)),
    0x5: ('NZ/NE', (env.zf==0)),
    0x6: ('BE/NA', (env.cf==1)|(env.zf==1)),
    0x7: ('NBE/A', (env.cf==0)&(env.zf==0)),
    0x8: ('S', (env.sf==1)),
    0x9: ('NS', (env.sf==0)),
    0xa: ('P/PE', (env.pf==1)),
    0xb: ('NP/PO', (env.pf==0)),
    0xc: ('L/NGE', (env.sf!=env.of)),
    0xd: ('NL/GE', (env.sf==env.of)),
    0xe: ('LE/NG', (env.zf==1)|(env.sf!=env.of)),
    0xf: ('NLE/G', (env.zf==0)&(env.sf==env.of)),
}

def do_nothing(obj):
    pass

def set_opdsz_128(obj):
    obj.misc['opdsz']=128
def set_opdsz_64(obj):
    obj.misc['opdsz']=64
def set_opdsz_32(obj):
    obj.misc['opdsz']=32

def check_f2(obj,f=do_nothing):
    if obj.misc['pfx'] and obj.misc['pfx'][0]=='repne':
        f(obj)
        return True
    return False

def check_f3(obj,f=do_nothing):
    if obj.misc['pfx'] and obj.misc['pfx'][0]=='rep':
        f(obj)
        return True
    return False

def check_66(obj,f=do_nothing):
    if obj.misc['opdsz']==16:
        f(obj)
        return True
    return False

def check_nopfx(obj,f=do_nothing):
    if obj.misc['pfx'] is None:
        f(obj)
        return True
    return False

