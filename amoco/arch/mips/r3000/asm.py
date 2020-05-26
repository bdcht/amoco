# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .env import *

from amoco.cas.utils import *

# ------------------------------------------------------------------------------
# helpers and decorators :

def __npc(i_xxx):
    def pcnpc(ins, fmap):
        fmap[pc] = fmap[npc]
        fmap[npc] = fmap[npc] + ins.length
        i_xxx(ins, fmap)
    return pcnpc

# i_xxx is the translation of MIPS-R3000 instruction xxx.
# ------------------------------------------------------------------------------

@__npc
def i_ADD(ins, fmap):
    dst, src1, src2 = ins.operands
    _v = fmap(src1+src2)
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v


@__npc
def i_SUB(ins, fmap):
    dst, src1, src2 = ins.operands
    _v = fmap(src1-src2)
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

@__npc
def i_SUBU(ins, fmap):
    dst, src1, src2 = ins.operands
    _v = fmap(src1-src2)
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

@__npc
def i_AND(ins, fmap):
    dst, src1, src2 = ins.operands
    _v = fmap(src1&src2)
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

@__npc
def i_OR(ins, fmap):
    dst, src1, src2 = ins.operands
    _v = fmap(src1|src2)
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

@__npc
def i_NOR(ins, fmap):
    dst, src1, src2 = ins.operands
    _v = fmap(~(src1|src2))
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

@__npc
def i_XOR(ins, fmap):
    dst, src1, src2 = ins.operands
    _v = fmap(src1^src2)
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

i_ADDI = i_ADDIU = i_ADDU = i_ADD
i_SUBU = i_SUB
i_ANDI = i_AND
i_ORI  = i_OR
i_XORI = i_XOR

def i_J(ins,fmap):
    t = ins.operands[0]
    target = composer([cst(0,2),t,fmap(pc)[28:32]])
    _v = fmap(npc)
    fmap.update_delayed()
    fmap[pc] = _v
    fmap[npc] = target

def i_JAL(ins,fmap):
    t = ins.operands[0]
    target = composer([cst(0,2),t,fmap(pc)[28:32]])
    _v = fmap(npc)
    fmap.update_delayed()
    fmap[pc] = _v
    fmap[ra] = _v+4
    fmap[npc] = target

@__npc
def i_JALR(ins,fmap):
    rd, rs = ins.operands
    _v = fmap(npc)
    target = fmap(rs)
    fmap.update_delayed()
    if rd is not zero:
        fmap[rd] = _v
    fmap[npc] = target

@__npc
def i_JR(ins,fmap):
    rs = ins.operands[0]
    target = fmap(rs)
    fmap.update_delayed()
    fmap[npc] = target

@__npc
def i_BEQ(ins,fmap):
    rs, rt, offset = ins.operands
    cond = (fmap(rs)==fmap(rt))
    fmap.update_delayed()
    fmap[npc] = tst(cond,fmap(npc-4)+offset,fmap(npc))

@__npc
def i_BNE(ins,fmap):
    rs, rt, offset = ins.operands
    cond = (fmap(rs)!=fmap(rt))
    fmap.update_delayed()
    fmap[npc] = tst(cond,fmap(npc-4)+offset,fmap(npc))

@__npc
def i_BGEZ(ins,fmap):
    rs, offset = ins.operands
    cond = fmap(rs.bit(31))==bit0
    fmap.update_delayed()
    fmap[npc] = tst(cond,fmap(npc-4)+offset,fmap(npc))

@__npc
def i_BGEZAL(ins,fmap):
    rs, offset = ins.operands
    cond = fmap(rs.bit(31))==bit0
    fmap.update_delayed()
    fmap[ra] = fmap(npc)
    fmap[npc] = tst(cond,fmap(npc-4)+offset,fmap(npc))

@__npc
def i_BGTZ(ins,fmap):
    rs, offset = ins.operands
    cond = fmap( (rs.bit(31)==bit0) & (rs!=zero) )
    fmap.update_delayed()
    fmap[npc] = tst(cond,fmap(npc-4)+offset,fmap(npc))

@__npc
def i_BLEZ(ins,fmap):
    rs, offset = ins.operands
    cond = fmap( (rs.bit(31)==bit1) | (rs==zero) )
    fmap.update_delayed()
    fmap[npc] = tst(cond,fmap(npc-4)+offset,fmap(npc))

@__npc
def i_BLTZ(ins,fmap):
    rs, offset = ins.operands
    cond = fmap(rs.bit(31))==bit1
    fmap.update_delayed()
    fmap[npc] = tst(cond,fmap(npc-4)+offset,fmap(npc))

@__npc
def i_BLTZAL(ins,fmap):
    rs, offset = ins.operands
    cond = fmap(rs.bit(31))==bit1
    fmap.update_delayed()
    fmap[ra] = fmap(npc)
    fmap[npc] = tst(cond,fmap(npc-4)+offset,fmap(npc))

@__npc
def i_BREAK(ins,fmap):
    ext("BREAK").call(fmap,code=ins.code)

@__npc
def i_CFC(ins, fmap):
    rt, rd = ins.operands
    ext("CFC%d"%(ins.z)).call(fmap,rt=rt,rd=rd)

@__npc
def i_MFC(ins, fmap):
    rt, rd = ins.operands
    ext("MFC%d"%(ins.z)).call(fmap,rt=rt,rd=rd)

@__npc
def i_COP(ins, fmap):
    fun = ins.cofun
    ext("COP%d"%(ins.z)).call(fmap,cofun=fun)

@__npc
def i_CTC(ins, fmap):
    rt, rd = ins.operands
    ext("CTC%d"%(ins.z)).call(fmap,rd=rd,rt=rt)

@__npc
def i_MTC(ins, fmap):
    rt, rd = ins.operands
    ext("MTC%d"%(ins.z)).call(fmap,rd=rd,rt=rt)

@__npc
def i_LWC(ins, fmap):
    rt, base, offset = ins.operands
    data = mem(base+offset,32)
    ext("LWC%d"%(ins.z)).call(fmap,rt=rt,data=data)

@__npc
def i_SWC(ins, fmap):
    rt, base, offset = ins.operands
    addr = fmap(base+offset)
    ext("SWC%d"%(ins.z)).call(fmap,rt=rt,addr=addr)

@__npc
def i_DIV(ins, fmap):
    rs, rt = ins.operands
    if fmap(rt!=zero):
        _v_hi = fmap(rs/rt)
        _v_lo = fmap(rs%rt)
        fmap.update_delayed()
        fmap[HI] = _v_hi
        fmap[LO] = _v_lo
    else:
        fmap.update_delayed()
        fmap[HI] = top(32)
        fmap[LO] = top(32)

i_DIVU = i_DIV

@__npc
def i_MULT(ins, fmap):
    rs, rt = ins.operands
    res = fmap(rs**rt)
    fmap.update_delayed()
    fmap[LO] = res[0:32]
    fmap[HI] = res[32:64]

i_MULTU = i_MULT

@__npc
def i_LH(ins, fmap):
    dst, base, src = ins.operands
    addr = base+src
    _v = fmap(mem(addr,16)).signextend(32)
    fmap.update_delayed()
    if dst is not zero:
        fmap.delayed(dst, _v)

@__npc
def i_LHU(ins, fmap):
    dst, base, src = ins.operands
    addr = base+src
    _v = fmap(mem(addr,16)).zeroextend(32)
    fmap.update_delayed()
    if dst is not zero:
        fmap.delayed(dst, _v)

@__npc
def i_LUI(ins, fmap):
    dst, src1 = ins.operands
    _v = src1.zeroextend(32)<<16
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

@__npc
def i_LW(ins, fmap):
    dst, base, src = ins.operands
    addr = base+src
    _v = fmap(mem(addr,32))
    fmap.update_delayed()
    if dst is not zero:
        fmap.delayed(dst, _v)

@__npc
def i_LWL(ins, fmap):
    dst, base, src = ins.operands
    addr  = base+src
    _v_b3 = fmap(mem(addr,8))
    cond1 = (addr%4)!=0
    _v_b2 = fmap(tst(cond1,mem(addr-1,8),dst[16:24]))
    addr  = addr - 1
    cond2 = cond1 & ((addr%4)!=0)
    _v_b1 = fmap(tst(cond2,mem(addr-1,8),dst[8:16]))
    _v_b0 = fmap(dst[0:8])
    fmap.update_delayed()
    if dst is not zero:
        _v = comp(dst.size)
        _v[24:32] = _v_b3
        _v[16:24] = _v_b2
        _v[ 8:16] = _v_b1
        _v[ 0: 8] = _v_b0
        fmap.delayed(dst, _v.simplify())

@__npc
def i_LWR(ins, fmap):
    dst, base, src = ins.operands
    addr  = base+src
    _v_b0 = fmap(mem(addr,8))
    addr  = addr + 1
    cond1 = (addr%4)!=0
    _v_b1 = fmap(tst(cond1,mem(addr,8),dst[8:16]))
    addr  = addr + 1
    cond2 = cond1 & ((addr%4)!=0)
    _v_b2 = fmap(tst(cond2,mem(addr,8),dst[16:24]))
    _v_b3 = fmap(dst[24:32])
    fmap.update_delayed()
    if dst is not zero:
        _v = comp(dst.size)
        _v[0 : 8] = _v_b0
        _v[8 :16] = _v_b1
        _v[16:24] = _v_b2
        _v[24:32] = _v_b3
        fmap.delayed(dst, _v.simplify())

@__npc
def i_SWL(ins, fmap):
    src, base, off = ins.operands
    addr = fmap(base+off)
    val = fmap(src)
    fmap.update_delayed()
    fmap[mem(addr,8)] = val[24:32]
    cond1 = (addr%4)!=0
    fmap[mem(addr-1,8)] = tst(cond1,val[16:24],fmap[mem(addr-1,8)])
    addr = addr - 1
    cond2 = cond1 & ((addr%4)!=0)
    fmap[mem(addr-1,8)] = tst(cond2,val[8:16],fmap[mem(addr-1,8)])

@__npc
def i_SWR(ins, fmap):
    src, base, off = ins.operands
    addr = fmap(base+off)
    val = fmap(src)
    fmap.update_delayed()
    fmap[mem(addr,8)] = val[0:8]
    addr = addr + 1
    cond1 = (addr%4)!=0
    fmap[mem(addr,8)] = tst(cond1,val[8:16],fmap[mem(addr,8)])
    addr = addr + 1
    cond2 = cond1 & ((addr%4)!=0)
    fmap[mem(addr,8)] = tst(cond2,val[16:24],fmap[mem(addr,8)])

@__npc
def i_LB(ins, fmap):
    dst, base, src = ins.operands
    addr = base+src
    _v = fmap(mem(addr,8)).signextend(32)
    fmap.update_delayed()
    if dst is not zero:
        fmap.delay(dst, _v)

@__npc
def i_LBU(ins, fmap):
    dst, base, src = ins.operands
    addr = base+src
    _v = fmap(mem(addr,8)).zeroextend(32)
    fmap.update_delayed()
    if dst is not zero:
        fmap.delay(dst, _v)

@__npc
def i_MFHI(ins,fmap):
    dst = ins.operands[0]
    _v = fmap(HI)
    fmap.update_delayed()
    fmap[dst] = _v

@__npc
def i_MFLO(ins,fmap):
    dst = ins.operands[0]
    _v = fmap(LO)
    fmap.update_delayed()
    fmap[dst] = _v

@__npc
def i_MTHI(ins,fmap):
    src = ins.operands[0]
    _v = fmap(src)
    fmap.update_delayed()
    fmap[HI] = _v

@__npc
def i_MTLO(ins,fmap):
    src = ins.operands[0]
    _v = fmap(src)
    fmap.update_delayed()
    fmap[LO] = _v

@__npc
def i_SB(ins, fmap):
    src, base, off = ins.operands
    addr = fmap(base+off)
    fmap.update_delayed()
    fmap[mem(addr,8)] = fmap(src[0:8])

@__npc
def i_SH(ins, fmap):
    src, base, off = ins.operands
    addr = fmap(base+off)
    fmap.update_delayed()
    fmap[mem(addr,16)] = fmap(src[0:16])

@__npc
def i_SW(ins, fmap):
    src, base, off = ins.operands
    addr = fmap(base+off)
    fmap.update_delayed()
    fmap[mem(addr,32)] = fmap(src)

@__npc
def i_SLL(ins, fmap):
    rt, rd, sa = ins.operands
    res = fmap(rt<<sa).unsigned()
    fmap.update_delayed()
    if rd is not zero:
        fmap[rd] = res

@__npc
def i_SLLV(ins, fmap):
    dst, src, s2 = ins.operands
    _v = fmap(src << s2).unsigned()
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

@__npc
def i_SLT(ins, fmap):
    dst, src1, src2 = ins.operands
    s1 = fmap(src1).signed()
    s2 = fmap(src2).signed()
    if dst is not zero:
        fmap[dst] = tst(s1<s2,cst(1,32),cst(0,32)).simplify()

@__npc
def i_SLTU(ins, fmap):
    dst, src1, src2 = ins.operands
    s1 = fmap(src1).unsigned()
    s2 = fmap(src2).unsigned()
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = tst(s1<s2,cst(1,32),cst(0,32)).simplify()

@__npc
def i_SLTI(ins, fmap):
    dst, src1, imm = ins.operands
    s1 = fmap(src1).signed()
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = tst(s1<imm,cst(1,32),cst(0,32)).simplify()

@__npc
def i_SLTIU(ins, fmap):
    dst, src1, imm = ins.operands
    s1 = fmap(src1).unsigned()
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = tst(s1<imm,cst(1,32),cst(0,32)).simplify()

@__npc
def i_SRA(ins, fmap):
    dst, src1, src2 = ins.operands
    _v = fmap(src1//src2).signed()
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

@__npc
def i_SRAV(ins, fmap):
    dst, src1, src2 = ins.operands
    _v = fmap(src1//src2).signed()
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

@__npc
def i_SRL(ins, fmap):
    dst, src1, src2 = ins.operands
    _v = fmap(src1>>src2).unsigned()
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

@__npc
def i_SRLV(ins, fmap):
    dst, src1, src2 = ins.operands
    _v = fmap(src1>>src2).unsigned()
    fmap.update_delayed()
    if dst is not zero:
        fmap[dst] = _v

@__npc
def i_SYSCALL(ins, fmap):
    ext("SYSCALL").call(fmap,code=ins.code)
