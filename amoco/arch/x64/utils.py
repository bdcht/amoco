# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.

from amoco.arch.x64 import env

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

def getREX(obj):
    REX = obj.misc['REX']
    if REX is None:
        W=R=X=B=0
    else:
        W,R,X,B=REX
    return (W,R,X,B)

def getreg8_legacy(x):
    return (env.al,env.cl,env.dl,env.bl,env.ah,env.ch,env.dh,env.bh)[x]

# using REX.R to get ModRM 'reg' register
def getregR(obj,REG,size):
    if size==8 and obj.misc['REX'] is None:
        return getreg8_legacy(REG)
    W,R,X,B = getREX(obj)
    return env.getreg(REG+(R<<3),size)

# using REX.R + REX.W to get ModRM 'reg' register
def getregRW(obj,REG,size):
    if size==8 and obj.misc['REX'] is None:
        return getreg8_legacy(REG)
    W,R,X,B = getREX(obj)
    if W==1: size=64
    return env.getreg(REG+(R<<3),size)

# using REX.B to get ModRM 'r/m' register
def getregB(obj,REG,size):
    if size==8 and obj.misc['REX'] is None:
        return getreg8_legacy(REG)
    W,R,X,B = getREX(obj)
    return env.getreg(REG+(B<<3),size)

# read ModR/M + SIB values and update obj accordingly:
def getModRM(obj,Mod,RM,data,REX=None):
    opdsz = obj.misc['opdsz'] or 32
    adrsz = obj.misc['adrsz'] or 64
    seg   = obj.misc['segreg']
    if seg is None: seg=''
    W,R,X,B = REX or getREX(obj)
    if opdsz!=8 and W==1: opdsz = 64
    # r/16/32/64 case:
    if Mod==0b11:
        op1 = getregB(obj,RM,opdsz)
        return op1,data
    # SIB cases :
    if adrsz!=16 and RM==0b100:
        # read SIB byte in data:
        if data.size<8: raise InstructionError(obj)
        sib,data = data[0:8],data[8:data.size]
        # add sib byte:
        obj.bytes += pack(sib)
        # decode base & scaled index
        b = env.getreg((B<<3)+sib[0:3].int(),adrsz)
        i = env.getreg((X<<3)+sib[3:6].int(),adrsz)
        ss = 1<<(sib[6:8].int())
        s = i*ss if not i.ref in ('rsp','esp','sp') else 0
    else:
        s = 0
        if adrsz!=16:
            b = env.getreg((B<<3)+RM,adrsz)
        else:
            b =  (env.bx+env.si,
                  env.bx+env.di,
                  env.bp+env.si,
                  env.bp+env.di,
                  env.si,
                  env.di,
                  env.bp,
                  env.bx)[RM]
    # check special disp32 case (RIP-relative addressing):
    if Mod==0:
        if RM==0b101:
            b=env.rip
            if seg is '': seg = env.cs
            Mod = 0b10
        elif b.ref in ('rbp','r13'):
            b = env.cst(0,adrsz)
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
        immsz = adrsz
        if immsz==64: immsz=32
        if data.size<immsz: raise InstructionError(obj)
        d = data[0:immsz]
        obj.bytes += pack(d)
        data = data[immsz:data.size]
        d = d.int(-1)
    bs = b+s
    if bs._is_cst and bs.v==0x0:
        bs.v = d
        bs.size = adrsz
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
def set_opdsz_mm(obj):
    obj.misc['opdsz']='mm'
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

