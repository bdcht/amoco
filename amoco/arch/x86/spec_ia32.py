# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.

from .utils import *

#------------------------------------------------------
# amoco IA32 instruction specs:
#------------------------------------------------------

ISPECS = []

# prefixes:
#------------------------------------------------------

def setpfx(obj,pfx,n):
    obj.misc.update((pfx,))
    if obj.misc['pfx'] is None:
        obj.misc['pfx'] = [None]*4
    if obj.misc['pfx'][n]!=None:
        logger.verbose('pfx %s grp %s redefined'%(pfx[0],n))
    obj.misc['pfx'][n]=pfx[0]

@ispec_ia32("8>[ {f0} ]+", _pfx=('lock', True))
@ispec_ia32("8>[ {f2} ]+", _pfx=('repne', True))
@ispec_ia32("8>[ {f3} ]+", _pfx=('rep', True))
def prefix_grp1(obj,_pfx):
    setpfx(obj,_pfx,0)

@ispec_ia32("8>[ {26} ]+", _pfx=('segreg', env.es))
@ispec_ia32("8>[ {2e} ]+", _pfx=('segreg', env.cs))
@ispec_ia32("8>[ {36} ]+", _pfx=('segreg', env.ss))
@ispec_ia32("8>[ {3e} ]+", _pfx=('segreg', env.ds))
@ispec_ia32("8>[ {64} ]+", _pfx=('segreg', env.fs))
@ispec_ia32("8>[ {65} ]+", _pfx=('segreg', env.gs))
def prefix_grp2(obj,_pfx):
    setpfx(obj,_pfx,1)

@ispec_ia32("8>[ {66} ]+", _pfx=('opdsz', 16))
def prefix_grp3(obj,_pfx):
    if env.internals['mode']==16: _pfx=('opdsz',32)
    setpfx(obj,_pfx,2)

@ispec_ia32("8>[ {67} ]+", _pfx=('adrsz', 16))
def prefix_grp4(obj,_pfx):
    if env.internals['mode']==16: _pfx=('adrsz',32)
    setpfx(obj,_pfx,3)

# IA32 opcodes:
#------------------------------------------------------

# no operands:
#-------------

@ispec_ia32(" 8>[ {90} ]", mnemonic = "NOP", type=type_cpu_state)
def ia32_nop(obj):
    if obj.misc['rep']: obj.mnemonic = "PAUSE"

@ispec_ia32(" 8>[ {37}         ]", mnemonic = "AAA",     type=type_data_processing)
@ispec_ia32(" 8>[ {3f}         ]", mnemonic = "AAS",     type=type_data_processing)
@ispec_ia32(" 8>[ {9b}         ]", mnemonic = "WAIT",    type=type_other)
@ispec_ia32(" 8>[ {c9}         ]", mnemonic = "LEAVE",   type=type_data_processing)
@ispec_ia32(" 8>[ {c3}         ]", mnemonic = "RET",     type=type_control_flow)
@ispec_ia32(" 8>[ {cb}         ]", mnemonic = "RETF",    type=type_control_flow)
@ispec_ia32(" 8>[ {f4}         ]", mnemonic = "HLT",     type=type_control_flow)
@ispec_ia32(" 8>[ {cc}         ]", mnemonic = "INT3",    type=type_cpu_state)
@ispec_ia32(" 8>[ {ce}         ]", mnemonic = "INTO",    type=type_cpu_state)
@ispec_ia32(" 8>[ {f8}         ]", mnemonic = "CLC",     type=type_data_processing)
@ispec_ia32(" 8>[ {f9}         ]", mnemonic = "STC",     type=type_data_processing)
@ispec_ia32(" 8>[ {f5}         ]", mnemonic = "CMC",     type=type_data_processing)
@ispec_ia32(" 8>[ {fc}         ]", mnemonic = "CLD",     type=type_data_processing)
@ispec_ia32(" 8>[ {fd}         ]", mnemonic = "STD",     type=type_data_processing)
@ispec_ia32(" 8>[ {fa}         ]", mnemonic = "CLI",     type=type_system)
@ispec_ia32(" 8>[ {fb}         ]", mnemonic = "STI",     type=type_system)
@ispec_ia32(" 8>[ {27}         ]", mnemonic = "DAA",     type=type_data_processing)
@ispec_ia32(" 8>[ {2f}         ]", mnemonic = "DAS",     type=type_data_processing)
@ispec_ia32(" 8>[ {9e}         ]", mnemonic = "SAHF",    type=type_data_processing)
@ispec_ia32(" 8>[ {9f}         ]", mnemonic = "LAHF",    type=type_data_processing)
@ispec_ia32(" 8>[ {d7}         ]", mnemonic = "XLATB",   type=type_data_processing)
@ispec_ia32(" 8>[ {61}         ]", mnemonic = "POPAD",   type=type_other)
@ispec_ia32(" 8>[ {9d}         ]", mnemonic = "POPFD",   type=type_other)
@ispec_ia32(" 8>[ {60}         ]", mnemonic = "PUSHAD",  type=type_other)
@ispec_ia32(" 8>[ {9c}         ]", mnemonic = "PUSHFD",  type=type_other)
@ispec_ia32("16>[ {0f}{06}     ]", mnemonic = "CLTS",    type=type_other)
@ispec_ia32("16>[ {0f}{a2}     ]", mnemonic = "CPUID",   type=type_other)
@ispec_ia32("16>[ {0f}{aa}     ]", mnemonic = "RSM",     type=type_system)
@ispec_ia32("16>[ {0f}{08}     ]", mnemonic = "INVD",    type=type_other)
@ispec_ia32("16>[ {0f}{09}     ]", mnemonic = "WBINVD",  type=type_cpu_state)
@ispec_ia32("16>[ {0f}{0b}     ]", mnemonic = "UD2",     type=type_undefined)
@ispec_ia32("16>[ {0f}{30}     ]", mnemonic = "WRMSR",   type=type_system)
@ispec_ia32("16>[ {0f}{31}     ]", mnemonic = "RDTSC",   type=type_cpu_state)
@ispec_ia32("16>[ {0f}{32}     ]", mnemonic = "RDMSR",   type=type_system)
@ispec_ia32("16>[ {0f}{33}     ]", mnemonic = "RDPMC",   type=type_cpu_state)
@ispec_ia32("16>[ {0f}{34}     ]", mnemonic = "SYSENTER",type=type_system)
@ispec_ia32("16>[ {0f}{35}     ]", mnemonic = "SYSEXIT", type=type_system)
@ispec_ia32("24>[ {0f}{01}{c8} ]", mnemonic = "MONITOR", type=type_cpu_state)
@ispec_ia32("24>[ {0f}{01}{c9} ]", mnemonic = "MWAIT",   type=type_cpu_state)
@ispec_ia32("24>[ {0f}{01}{d0} ]", mnemonic = "XGETBV",  type=type_system)
@ispec_ia32("24>[ {0f}{01}{d1} ]", mnemonic = "XSETBV",  type=type_system)
def ia32_nooperand(obj):
    pass

@ispec_ia32(" 8>[ {cf}         ]", mnemonic = "IRETD",   type=type_other)
@ispec_ia32(" 8>[ {98}         ]", mnemonic = "CWDE",    type=type_data_processing)
@ispec_ia32(" 8>[ {99}         ]", mnemonic = "CDQ",     type=type_data_processing)
def ia32_nooperand(obj):
    if obj.misc['opdsz']:
        if obj.mnemonic=="CWDE": obj.mnemonic="CBW"
        if obj.mnemonic=="CDQ" : obj.mnemonic="CWD"
        if obj.mnemonic=="IRETD" : obj.mnemonic="IRET"

# instructions for which REP/REPNE is valid (see formats.py):
@ispec_ia32(" 8>[ {6c} ]", mnemonic = "INSB",    type=type_system)
@ispec_ia32(" 8>[ {6d} ]", mnemonic = "INSD",    type=type_system)
@ispec_ia32(" 8>[ {a4} ]", mnemonic = "MOVSB",   type=type_data_processing)
@ispec_ia32(" 8>[ {a5} ]", mnemonic = "MOVSD",   type=type_data_processing)
@ispec_ia32(" 8>[ {6e} ]", mnemonic = "OUTSB",   type=type_other)
@ispec_ia32(" 8>[ {6f} ]", mnemonic = "OUTSD",   type=type_other)
@ispec_ia32(" 8>[ {ac} ]", mnemonic = "LODSB",   type=type_other)
@ispec_ia32(" 8>[ {ad} ]", mnemonic = "LODSD",   type=type_other)
@ispec_ia32(" 8>[ {aa} ]", mnemonic = "STOSB",   type=type_data_processing)
@ispec_ia32(" 8>[ {ab} ]", mnemonic = "STOSD",   type=type_data_processing)
@ispec_ia32(" 8>[ {a6} ]", mnemonic = "CMPSB",   type=type_data_processing)
@ispec_ia32(" 8>[ {a7} ]", mnemonic = "CMPSD",   type=type_data_processing)
@ispec_ia32(" 8>[ {ae} ]", mnemonic = "SCASB",   type=type_data_processing)
@ispec_ia32(" 8>[ {af} ]", mnemonic = "SCASD",   type=type_data_processing)
def ia32_strings(obj):
    if obj.misc['rep']: obj.type=type_control_flow
    if obj.mnemonic[-1]=='D' and obj.misc['opdsz']:
        obj.mnemonic = obj.mnemonic[:-1]+'W'

# 1 operand
#----------

# imm8:
@ispec_ia32("16>[ {d5} ib(8) ]", mnemonic = "AAD",    type=type_data_processing)
@ispec_ia32("16>[ {d4} ib(8) ]", mnemonic = "AAM",    type=type_data_processing)
@ispec_ia32("16>[ {cd} ib(8) ]", mnemonic = "INT",    type=type_control_flow)
def ia32_imm8(obj,ib):
    obj.operands = [env.cst(ib,8)]

@ispec_ia32("16>[ {6a} ib(8) ]", mnemonic = "PUSH",   type=type_data_processing)
def ia32_imm8_signed(obj,ib):
    obj.operands = [env.cst(ib,8).signextend(8)]

@ispec_ia32("16>[ {eb} ib(8) ]", mnemonic = "JMP",    type=type_control_flow)
@ispec_ia32("16>[ {e2} ib(8) ]", mnemonic = "LOOP",   type=type_control_flow)
@ispec_ia32("16>[ {e1} ib(8) ]", mnemonic = "LOOPE",  type=type_control_flow)
@ispec_ia32("16>[ {e0} ib(8) ]", mnemonic = "LOOPNE", type=type_control_flow)
def ia32_imm_rel(obj,ib):
    size = obj.misc['adrsz'] or env.internals['mode']
    obj.operands = [env.cst(ib,8).signextend(size)]

@ispec_ia32("16>[ {e3} cb(8) ]", mnemonic = "JECXZ", type=type_control_flow)
def ia32_cb8(obj,cb):
    size = obj.misc['adrsz'] or env.internals['mode']
    if size==16: obj.mnemonic = "JCXZ"
    obj.operands = [env.cst(cb,8).signextend(size)]

# imm16:
@ispec_ia32("24>[ {c2} iw(16) ]", mnemonic = "RETN", type=type_control_flow)
def ia32_retn(obj,iw):
    obj.operands = [env.cst(iw,16)]

# imm16/32:
@ispec_ia32("*>[ {68} ~data(*) ]", mnemonic = "PUSH", type=type_data_processing)
def ia32_imm32(obj,data):
    size = obj.misc['opdsz'] or env.internals['mode']
    if data.size<size: raise InstructionError(obj)
    imm = data[0:size]
    obj.operands = [env.cst(imm.int(),size)]
    obj.bytes += pack(imm)

@ispec_ia32("*>[ {e8} ~data(*) ]", mnemonic = "CALL", type=type_control_flow)
@ispec_ia32("*>[ {e9} ~data(*) ]", mnemonic = "JMP",  type=type_control_flow)
def ia32_imm_rel(obj,data):
    size = obj.misc['opdsz'] or env.internals['mode']
    if data.size<size: raise InstructionError(obj)
    imm = data[0:size]
    op1 = env.cst(imm.int(-1),size)
    op1.sf = True
    obj.operands = [op1]
    obj.bytes += pack(imm)

# imm32/48 (far call/jmp):
@ispec_ia32("*>[ {9a} ~data(*) ]", mnemonic = "CALLF")
@ispec_ia32("*>[ {ea} ~data(*) ]", mnemonic = "JMPF")
def ia32_far_imm(obj,data):
    size = obj.misc['opdsz'] or env.internals['mode']
    if data.size<size+16: raise InstructionError(obj)
    offset,seg = data[0:size],data[size:size+16]
    p = env.ptr(env.cst(offset.int(),size),env.cst(seg.int(),16))
    obj.operands = [p]
    obj.bytes += pack(offset)+pack(seg)
    obj.type = type_control_flow

# explicit register:

# r16/32
@ispec_ia32("*>[ reg(3) 0 1010 ]", mnemonic = "PUSH") #50 +rd
@ispec_ia32("*>[ reg(3) 1 1010 ]", mnemonic = "POP")  #58 +rd
@ispec_ia32("*>[ reg(3) 0 0010 ]", mnemonic = "INC")  #40 +rd
@ispec_ia32("*>[ reg(3) 1 0010 ]", mnemonic = "DEC")  #48 +rd
def ia32_rm32(obj,reg):
    size = obj.misc['opdsz'] or env.internals['mode']
    op1 = env.getreg(reg,size)
    obj.operands = [op1]
    obj.type = type_data_processing

@ispec_ia32("16>[ {0f} reg(3) 1 0011 ]", mnemonic = "BSWAP") # 0f c4 +rd
def ia32_bswap(obj,reg):
    obj.operands = [env.getreg(reg,32)] # BSWAP in not supported for 16-bit operations
    obj.type = type_data_processing

# implicit register:
# r16 (segments)
@ispec_ia32(" 8>[ {0e}     ]", mnemonic="PUSH", _seg=env.cs, type=type_data_processing)
@ispec_ia32(" 8>[ {16}     ]", mnemonic="PUSH", _seg=env.ss, type=type_data_processing)
@ispec_ia32(" 8>[ {17}     ]", mnemonic="POP",  _seg=env.ss, type=type_data_processing)
@ispec_ia32(" 8>[ {1e}     ]", mnemonic="PUSH", _seg=env.ds, type=type_data_processing)
@ispec_ia32(" 8>[ {1f}     ]", mnemonic="POP",  _seg=env.ds, type=type_data_processing)
@ispec_ia32(" 8>[ {06}     ]", mnemonic="PUSH", _seg=env.es, type=type_data_processing)
@ispec_ia32(" 8>[ {07}     ]", mnemonic="POP",  _seg=env.es, type=type_data_processing)
@ispec_ia32("16>[ {0f}{0a} ]", mnemonic="PUSH", _seg=env.fs, type=type_data_processing)
@ispec_ia32("16>[ {0f}{a1} ]", mnemonic="POP",  _seg=env.fs, type=type_data_processing)
@ispec_ia32("16>[ {0f}{a8} ]", mnemonic="PUSH", _seg=env.gs, type=type_data_processing)
@ispec_ia32("16>[ {0f}{a9} ]", mnemonic="POP",  _seg=env.gs, type=type_data_processing)
def ia32_push_pop(obj,_seg):
    obj.operands = [_seg]

# r/m operand:

# r/m8
@ispec_ia32("*>[ {fe} /0     ]", mnemonic = "INC",         type=type_data_processing)
@ispec_ia32("*>[ {fe} /1     ]", mnemonic = "DEC",         type=type_data_processing)
@ispec_ia32("*>[ {f6} /6     ]", mnemonic = "DIV",         type=type_data_processing)
@ispec_ia32("*>[ {f6} /7     ]", mnemonic = "IDIV",        type=type_data_processing)
@ispec_ia32("*>[ {f6} /4     ]", mnemonic = "MUL",         type=type_data_processing)
@ispec_ia32("*>[ {f6} /5     ]", mnemonic = "IMUL",        type=type_data_processing)
@ispec_ia32("*>[ {f6} /3     ]", mnemonic = "NEG",         type=type_data_processing)
@ispec_ia32("*>[ {f6} /2     ]", mnemonic = "NOT",         type=type_data_processing)
@ispec_ia32("*>[ {0f}{18} /0 ]", mnemonic = "PREFETCHNTA", type=type_other)
@ispec_ia32("*>[ {0f}{18} /1 ]", mnemonic = "PREFETCHT0" , type=type_other)
@ispec_ia32("*>[ {0f}{18} /2 ]", mnemonic = "PREFETCHT1" , type=type_other)
@ispec_ia32("*>[ {0f}{18} /3 ]", mnemonic = "PREFETCHT2" , type=type_other)
@ispec_ia32("*>[ {0f}{0d} /1 ]", mnemonic = "PREFETCHW" ,  type=type_other)
def ia32_rm8(obj,Mod,RM,data):
    obj.misc['opdsz']=8
    op1,data = getModRM(obj,Mod,RM,data)
    obj.operands = [op1]

# r/m16/32
@ispec_ia32("*>[ {ff} /0 ]", mnemonic = "INC",  type=type_data_processing)
@ispec_ia32("*>[ {ff} /1 ]", mnemonic = "DEC",  type=type_data_processing)
@ispec_ia32("*>[ {ff} /2 ]", mnemonic = "CALL", type=type_control_flow)
@ispec_ia32("*>[ {ff} /4 ]", mnemonic = "JMP",  type=type_control_flow)
@ispec_ia32("*>[ {ff} /6 ]", mnemonic = "PUSH", type=type_data_processing)
@ispec_ia32("*>[ {8f} /0 ]", mnemonic = "POP",  type=type_data_processing)
@ispec_ia32("*>[ {f7} /2 ]", mnemonic = "NOT",  type=type_data_processing)
@ispec_ia32("*>[ {f7} /3 ]", mnemonic = "NEG",  type=type_data_processing)
@ispec_ia32("*>[ {f7} /4 ]", mnemonic = "MUL",  type=type_data_processing)
@ispec_ia32("*>[ {f7} /5 ]", mnemonic = "IMUL", type=type_data_processing)
@ispec_ia32("*>[ {f7} /6 ]", mnemonic = "DIV",  type=type_data_processing)
@ispec_ia32("*>[ {f7} /7 ]", mnemonic = "IDIV", type=type_data_processing)
def ia32_rm32(obj,Mod,RM,data):
    op1,data = getModRM(obj,Mod,RM,data)
    obj.operands = [op1]
    if obj.mnemonic in ('JMP','CALL'):
        obj.misc['absolute']=True

# r/m32/48
@ispec_ia32("*>[ {ff} /3     ]", mnemonic = "CALLF", type=type_control_flow)
@ispec_ia32("*>[ {ff} /5     ]", mnemonic = "JMPF",  type=type_control_flow)
@ispec_ia32("*>[ {0f}{01} /0 ]", mnemonic = "SGDT",  type=type_system)
@ispec_ia32("*>[ {0f}{01} /1 ]", mnemonic = "SIDT",  type=type_system)
@ispec_ia32("*>[ {0f}{01} /2 ]", mnemonic = "LGDT",  type=type_system)
@ispec_ia32("*>[ {0f}{01} /3 ]", mnemonic = "LIDT",  type=type_system)
@ispec_ia32("*>[ {0f}{01} /4 ]", mnemonic = "SMSW",  type=type_system)
@ispec_ia32("*>[ {0f}{01} /7 ]", mnemonic = "INVLPG",type=type_system)
def ia32_op48(obj,Mod,RM,data):
    op1,data = getModRM(obj,Mod,RM,data)
    if op1._is_reg: raise InstructionError(obj)
    op1.size = 32 if obj.misc['opdsz']==16 else 48
    obj.operands = [op1]

# r/m16
@ispec_ia32("*>[ {0f}{00} /1 ]", mnemonic = "STR",  type=type_system)
@ispec_ia32("*>[ {0f}{00} /2 ]", mnemonic = "LLDT", type=type_system)
@ispec_ia32("*>[ {0f}{00} /3 ]", mnemonic = "LTR",  type=type_system)
@ispec_ia32("*>[ {0f}{00} /4 ]", mnemonic = "VERR", type=type_system)
@ispec_ia32("*>[ {0f}{00} /5 ]", mnemonic = "VERW", type=type_system)
@ispec_ia32("*>[ {0f}{01} /6 ]", mnemonic = "LMSW", type=type_system)
def ia32_lldt(obj,Mod,RM,data):
    obj.misc['opdsz']=16
    op1,data = getModRM(obj,Mod,RM,data)
    obj.operands = [op1]

# conditionals:
@ispec_ia32("16>[ cc(4) 1110 cb(8) ]", mnemonic = "Jcc") # 7x cb(8)
def ia32_imm_rel(obj,cc,cb):
    obj.cond = CONDITION_CODES[cc]
    obj.operands = [env.cst(cb,8).signextend(32)]
    obj.type = type_control_flow

@ispec_ia32("*>[ {0f} cc(4) 0001 ~data(*) ]", mnemonic = "Jcc") # 0f 8x cw/d
def ia32_imm_rel(obj,cc,data):
    obj.cond = CONDITION_CODES[cc]
    size = obj.misc['opdsz'] or env.internals['mode']
    if data.size<size: raise InstructionError(obj)
    imm = data[0:size]
    op1 = env.cst(imm.int(-1),size)
    op1.sf = True
    obj.operands = [op1]
    obj.bytes += pack(imm)
    obj.type = type_control_flow

# 2 operands
# ----------

# implicit ax/eax, r16/32
@ispec_ia32("8>[ rd(3) 0 1001 ]", mnemonic = "XCHG") # 9x
def ia32_xchg(obj,rd):
    size = obj.misc['opdsz'] or env.internals['mode']
    op1 = env.getreg(0,size)
    op2 = env.getreg(rd,size)
    obj.operands = [op1, op2]
    obj.type = type_data_processing

# implicit al , imm8:
@ispec_ia32("16>[ {04} ib(8) ]", mnemonic = "ADD")
@ispec_ia32("16>[ {14} ib(8) ]", mnemonic = "ADC")
@ispec_ia32("16>[ {1c} ib(8) ]", mnemonic = "SBB")
@ispec_ia32("16>[ {24} ib(8) ]", mnemonic = "AND")
@ispec_ia32("16>[ {2c} ib(8) ]", mnemonic = "SUB")
@ispec_ia32("16>[ {34} ib(8) ]", mnemonic = "XOR")
@ispec_ia32("16>[ {3c} ib(8) ]", mnemonic = "CMP")
@ispec_ia32("16>[ {0c} ib(8) ]", mnemonic = "OR")
@ispec_ia32("16>[ {a8} ib(8) ]", mnemonic = "TEST")
def ia32_al_imm8(obj,ib):
    obj.operands = [env.al, env.cst(ib,8)]
    obj.type = type_data_processing

# implicit al/ax/eax , adr16/32:
@ispec_ia32("*>[ {a0} ~data(*) ]", mnemonic = "MOV", _flg8=True, _inv=False)
@ispec_ia32("*>[ {a1} ~data(*) ]", mnemonic = "MOV", _flg8=False, _inv=False)
@ispec_ia32("*>[ {a2} ~data(*) ]", mnemonic = "MOV", _flg8=True, _inv=True)
@ispec_ia32("*>[ {a3} ~data(*) ]", mnemonic = "MOV", _flg8=False, _inv=True)
def ia32_mov_adr(obj,data,_flg8,_inv):
    opdsz = obj.misc['opdsz'] or env.internals['mode']
    if _flg8: opdsz=8
    op1 = env.getreg(0,opdsz)
    adrsz = obj.misc['adrsz'] or env.internals['mode']
    seg  = obj.misc['segreg']
    if seg is None: seg=''
    if data.size<adrsz: raise InstructionError(obj)
    moffs8 = env.cst(data[0:adrsz].int(),adrsz)
    op2 = env.mem(moffs8,opdsz,seg)
    obj.operands = [op1, op2] if not _inv else [op2, op1]
    obj.bytes += pack(data[0:adrsz])
    obj.type = type_data_processing

# implicit ax/eax , imm16/32:
@ispec_ia32("*>[ {05} ~data(*) ]", mnemonic = "ADD")
@ispec_ia32("*>[ {0d} ~data(*) ]", mnemonic = "OR")
@ispec_ia32("*>[ {15} ~data(*) ]", mnemonic = "ADC")
@ispec_ia32("*>[ {1d} ~data(*) ]", mnemonic = "SBB")
@ispec_ia32("*>[ {25} ~data(*) ]", mnemonic = "AND")
@ispec_ia32("*>[ {2d} ~data(*) ]", mnemonic = "SUB")
@ispec_ia32("*>[ {35} ~data(*) ]", mnemonic = "XOR")
@ispec_ia32("*>[ {3d} ~data(*) ]", mnemonic = "CMP")
@ispec_ia32("*>[ {a9} ~data(*) ]", mnemonic = "TEST")
def ia32_eax_imm(obj,data):
    size = obj.misc['opdsz'] or env.internals['mode']
    if data.size<size: raise InstructionError(obj)
    imm = data[0:size]
    op1 = env.eax if size==32 else env.ax
    obj.operands = [op1, env.cst(imm.int(),size)]
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# imm16 , imm8:
@ispec_ia32("32>[ {c8} iw(16) ib(8) ]", mnemonic = "ENTER")
def ia32_enter(obj,iw,ib):
    obj.operands = [env.cst(iw,16),env.cst(ib,8)]
    obj.type = type_other

# r/m8 , implicit
@ispec_ia32("*>[ {d0} /0 ]", mnemonic = "ROL", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d0} /1 ]", mnemonic = "ROR", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d0} /2 ]", mnemonic = "RCL", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d0} /3 ]", mnemonic = "RCR", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d0} /4 ]", mnemonic = "SAL", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d0} /5 ]", mnemonic = "SHR", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d0} /6 ]", mnemonic = "SHL", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d0} /7 ]", mnemonic = "SAR", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d2} /0 ]", mnemonic = "ROL", _op2=env.cl)
@ispec_ia32("*>[ {d2} /1 ]", mnemonic = "ROR", _op2=env.cl)
@ispec_ia32("*>[ {d2} /2 ]", mnemonic = "RCL", _op2=env.cl)
@ispec_ia32("*>[ {d2} /3 ]", mnemonic = "RCR", _op2=env.cl)
@ispec_ia32("*>[ {d2} /4 ]", mnemonic = "SAL", _op2=env.cl)
@ispec_ia32("*>[ {d2} /5 ]", mnemonic = "SHR", _op2=env.cl)
@ispec_ia32("*>[ {d2} /6 ]", mnemonic = "SHL", _op2=env.cl)
@ispec_ia32("*>[ {d2} /7 ]", mnemonic = "SAR", _op2=env.cl)
def ia32_rm8_op2(obj,Mod,RM,data,_op2):
    obj.misc['opdsz']=8
    op1,data = getModRM(obj,Mod,RM,data)
    obj.operands = [op1, _op2]
    obj.type = type_data_processing

# r/m8 , imm8
@ispec_ia32("*>[ {80} /0 ]", mnemonic = "ADD")
@ispec_ia32("*>[ {80} /1 ]", mnemonic = "OR")
@ispec_ia32("*>[ {80} /2 ]", mnemonic = "ADC")
@ispec_ia32("*>[ {80} /3 ]", mnemonic = "SBB")
@ispec_ia32("*>[ {80} /4 ]", mnemonic = "AND")
@ispec_ia32("*>[ {80} /5 ]", mnemonic = "SUB")
@ispec_ia32("*>[ {80} /6 ]", mnemonic = "XOR")
@ispec_ia32("*>[ {80} /7 ]", mnemonic = "CMP")
@ispec_ia32("*>[ {c6} /0 ]", mnemonic = "MOV")
@ispec_ia32("*>[ {f6} /0 ]", mnemonic = "TEST")
def ia32_ptr_ib(obj,Mod,RM,data):
    obj.misc['opdsz']=8
    op1,data = getModRM(obj,Mod,RM,data)
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands = [op1, env.cst(imm.int(),8)]
    obj.bytes += pack(imm)
    obj.type = type_data_processing

@ispec_ia32("*>[ {c0} /0 ]", mnemonic = "ROL")
@ispec_ia32("*>[ {c0} /1 ]", mnemonic = "ROR")
@ispec_ia32("*>[ {c0} /2 ]", mnemonic = "RCL")
@ispec_ia32("*>[ {c0} /3 ]", mnemonic = "RCR")
@ispec_ia32("*>[ {c0} /4 ]", mnemonic = "SAL")
@ispec_ia32("*>[ {c0} /5 ]", mnemonic = "SHR")
@ispec_ia32("*>[ {c0} /6 ]", mnemonic = "SHL")
@ispec_ia32("*>[ {c0} /7 ]", mnemonic = "SAR")
def ia32_ptr_ib(obj,Mod,RM,data):
    obj.misc['opdsz']=8
    op1,data = getModRM(obj,Mod,RM,data)
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands = [op1, env.cst(imm.int()&0x1f,8)]
    obj.bytes += pack(imm)
    obj.type = type_data_processing

@ispec_ia32("16>[ rb(3) 0 1101 ib(8) ]", mnemonic = "MOV") # b0 + rb ib
def ia32_mov_adr(obj,rb,ib):
    op1 = env.getreg(rb,8)
    op2 = env.cst(ib,8)
    obj.operands = [op1, op2]
    obj.type = type_data_processing

@ispec_ia32("*>[ rb(3) 1 1101 ~data(*) ]", mnemonic = "MOV") # b8+rd  id
def ia32_mov_adr(obj,rb,data):
    size = obj.misc['opdsz'] or env.internals['mode']
    op1 = env.getreg(rb,size)
    if data.size<size: raise InstructionError(obj)
    imm = data[0:size]
    op2 = env.cst(imm.int(),size)
    obj.operands = [op1, op2]
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# r/m16/32, imm8
@ispec_ia32("*>[ {c1} /0 ]", mnemonic = "ROL")
@ispec_ia32("*>[ {c1} /1 ]", mnemonic = "ROR")
@ispec_ia32("*>[ {c1} /2 ]", mnemonic = "RCL")
@ispec_ia32("*>[ {c1} /3 ]", mnemonic = "RCR")
@ispec_ia32("*>[ {c1} /4 ]", mnemonic = "SAL")
@ispec_ia32("*>[ {c1} /5 ]", mnemonic = "SHR")
@ispec_ia32("*>[ {c1} /6 ]", mnemonic = "SHL")
@ispec_ia32("*>[ {c1} /7 ]", mnemonic = "SAR")
def ia32_rm32_imm8(obj,Mod,RM,data):
    op1,data = getModRM(obj,Mod,RM,data)
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    obj.operands = [op1, env.cst(imm.int()&0x1f,8)]
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# r/m16/32 , implicit
@ispec_ia32("*>[ {d1} /0 ]", mnemonic = "ROL", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d1} /1 ]", mnemonic = "ROR", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d1} /2 ]", mnemonic = "RCL", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d1} /3 ]", mnemonic = "RCR", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d1} /4 ]", mnemonic = "SAL", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d1} /5 ]", mnemonic = "SHR", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d1} /6 ]", mnemonic = "SHL", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d1} /7 ]", mnemonic = "SAR", _op2=env.cst(1,8))
@ispec_ia32("*>[ {d3} /0 ]", mnemonic = "ROL", _op2=env.cl)
@ispec_ia32("*>[ {d3} /1 ]", mnemonic = "ROR", _op2=env.cl)
@ispec_ia32("*>[ {d3} /2 ]", mnemonic = "RCL", _op2=env.cl)
@ispec_ia32("*>[ {d3} /3 ]", mnemonic = "RCR", _op2=env.cl)
@ispec_ia32("*>[ {d3} /4 ]", mnemonic = "SAL", _op2=env.cl)
@ispec_ia32("*>[ {d3} /5 ]", mnemonic = "SHR", _op2=env.cl)
@ispec_ia32("*>[ {d3} /6 ]", mnemonic = "SHL", _op2=env.cl)
@ispec_ia32("*>[ {d3} /7 ]", mnemonic = "SAR", _op2=env.cl)
def ia32_rm32_op2(obj,Mod,RM,data,_op2):
    op1,data = getModRM(obj,Mod,RM,data)
    obj.operands = [op1, _op2]
    obj.type = type_data_processing

# r/m16/32 , imm16/32
@ispec_ia32("*>[ {81} /0 ]", mnemonic = "ADD")
@ispec_ia32("*>[ {81} /1 ]", mnemonic = "OR")
@ispec_ia32("*>[ {81} /2 ]", mnemonic = "ADC")
@ispec_ia32("*>[ {81} /3 ]", mnemonic = "SBB")
@ispec_ia32("*>[ {81} /4 ]", mnemonic = "AND")
@ispec_ia32("*>[ {81} /5 ]", mnemonic = "SUB")
@ispec_ia32("*>[ {81} /6 ]", mnemonic = "XOR")
@ispec_ia32("*>[ {81} /7 ]", mnemonic = "CMP")
@ispec_ia32("*>[ {c7} /0 ]", mnemonic = "MOV")
@ispec_ia32("*>[ {f7} /0 ]", mnemonic = "TEST")
def ia32_ptr_iwd(obj,Mod,RM,data):
    op1,data = getModRM(obj,Mod,RM,data)
    if data.size<op1.size: raise InstructionError(obj)
    imm = data[0:op1.size]
    x = env.cst(imm.int(),op1.size)
    obj.operands = [op1, x]
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# r/m16/32 , sign extended imm8
@ispec_ia32("*>[ {83} /0 ]", mnemonic = "ADD")
@ispec_ia32("*>[ {83} /1 ]", mnemonic = "OR")
@ispec_ia32("*>[ {83} /2 ]", mnemonic = "ADC")
@ispec_ia32("*>[ {83} /3 ]", mnemonic = "SBB")
@ispec_ia32("*>[ {83} /4 ]", mnemonic = "AND")
@ispec_ia32("*>[ {83} /5 ]", mnemonic = "SUB")
@ispec_ia32("*>[ {83} /6 ]", mnemonic = "XOR")
@ispec_ia32("*>[ {83} /7 ]", mnemonic = "CMP")
def ia32_ptr_iwd(obj,Mod,RM,data):
    op1,data = getModRM(obj,Mod,RM,data)
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    x = env.cst(imm.int(),8).signextend(op1.size)
    if obj.mnemonic in ('OR','AND','XOR'): x.sf=False
    obj.operands = [op1, x]
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# r/m16/32 , imm8
@ispec_ia32("*>[ {0f}{ba} /4 ]", mnemonic = "BT")
@ispec_ia32("*>[ {0f}{ba} /7 ]", mnemonic = "BTC")
@ispec_ia32("*>[ {0f}{ba} /6 ]", mnemonic = "BTR")
@ispec_ia32("*>[ {0f}{ba} /5 ]", mnemonic = "BTS")
def ia32_BTx(obj,Mod,RM,data):
    op1,data = getModRM(obj,Mod,RM,data)
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    x = env.cst(imm.int(),8)
    obj.operands = [op1, x]
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# r/m8 , r8
@ispec_ia32("*>[ {00} /r     ]", mnemonic = "ADD")
@ispec_ia32("*>[ {08} /r     ]", mnemonic = "OR")
@ispec_ia32("*>[ {10} /r     ]", mnemonic = "ADC")
@ispec_ia32("*>[ {18} /r     ]", mnemonic = "SBB")
@ispec_ia32("*>[ {20} /r     ]", mnemonic = "AND")
@ispec_ia32("*>[ {28} /r     ]", mnemonic = "SUB")
@ispec_ia32("*>[ {30} /r     ]", mnemonic = "XOR")
@ispec_ia32("*>[ {38} /r     ]", mnemonic = "CMP")
@ispec_ia32("*>[ {0f}{b0} /r ]", mnemonic = "CMPXCHG")
@ispec_ia32("*>[ {0f}{c0} /r ]", mnemonic = "XADD")
@ispec_ia32("*>[ {88} /r     ]", mnemonic = "MOV")
@ispec_ia32("*>[ {84} /r     ]", mnemonic = "TEST")
def ia32_reg_8(obj,Mod,RM,REG,data):
    obj.misc['opdsz']=8
    op1,data = getModRM(obj,Mod,RM,data)
    op2 = env.getreg(REG,op1.size)
    obj.operands = [op1, op2]
    obj.type = type_data_processing

# r8 , r/m8
@ispec_ia32("*>[ {02} /r ]", mnemonic = "ADD")
@ispec_ia32("*>[ {0a} /r ]", mnemonic = "OR")
@ispec_ia32("*>[ {12} /r ]", mnemonic = "ADC")
@ispec_ia32("*>[ {1a} /r ]", mnemonic = "SBB")
@ispec_ia32("*>[ {22} /r ]", mnemonic = "AND")
@ispec_ia32("*>[ {2a} /r ]", mnemonic = "SUB")
@ispec_ia32("*>[ {32} /r ]", mnemonic = "XOR")
@ispec_ia32("*>[ {3a} /r ]", mnemonic = "CMP")
@ispec_ia32("*>[ {86} /r ]", mnemonic = "XCHG")
@ispec_ia32("*>[ {8a} /r ]", mnemonic = "MOV")
def ia32_reg_8_inv(obj,Mod,RM,REG,data):
    obj.misc['opdsz']=8
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op1, op2]
    obj.type = type_data_processing


# r16 (segment selectors), r/m16
@ispec_ia32("*>[ {63} /r ]", mnemonic = "ARPL", _inv=True)
@ispec_ia32("*>[ {8c} /r ]", mnemonic = "MOV", _inv=True)
@ispec_ia32("*>[ {8e} /r ]", mnemonic = "MOV", _inv=False)
def ia32_arpl(obj,Mod,REG,RM,data,_inv):
    obj.misc['opdsz']=16
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,op2.size)
    if obj.mnemonic=='MOV':
        if REG==6 or REG==7: raise InstructionError(obj)
        op1 = [env.es,env.cs,env.ss,env.ds,env.fs,env.gs][REG]
    obj.operands = [op1, op2] if not _inv else [op2, op1]
    obj.type = type_data_processing

# r/m16/32 , r16/32
@ispec_ia32("*>[ {01} /r     ]", mnemonic = "ADD")
@ispec_ia32("*>[ {09} /r     ]", mnemonic = "OR")
@ispec_ia32("*>[ {11} /r     ]", mnemonic = "ADC")
@ispec_ia32("*>[ {19} /r     ]", mnemonic = "SBB")
@ispec_ia32("*>[ {21} /r     ]", mnemonic = "AND")
@ispec_ia32("*>[ {29} /r     ]", mnemonic = "SUB")
@ispec_ia32("*>[ {31} /r     ]", mnemonic = "XOR")
@ispec_ia32("*>[ {39} /r     ]", mnemonic = "CMP")
@ispec_ia32("*>[ {89} /r     ]", mnemonic = "MOV")
@ispec_ia32("*>[ {85} /r     ]", mnemonic = "TEST")
@ispec_ia32("*>[ {0f}{a3} /r ]", mnemonic = "BT")
@ispec_ia32("*>[ {0f}{bb} /r ]", mnemonic = "BTC")
@ispec_ia32("*>[ {0f}{b3} /r ]", mnemonic = "BTR")
@ispec_ia32("*>[ {0f}{ab} /r ]", mnemonic = "BTS")
@ispec_ia32("*>[ {0f}{b1} /r ]", mnemonic = "CMPXCHG")
@ispec_ia32("*>[ {0f}{c1} /r ]", mnemonic = "XADD")
def ia32_reg_32(obj,Mod,RM,REG,data):
    op1,data = getModRM(obj,Mod,RM,data)
    op2 = env.getreg(REG,op1.size)
    obj.operands = [op1, op2]
    obj.type = type_data_processing

# r16/32 , r/m16/32
@ispec_ia32("*>[ {03} /r     ]", mnemonic = "ADD")
@ispec_ia32("*>[ {0b} /r     ]", mnemonic = "OR")
@ispec_ia32("*>[ {13} /r     ]", mnemonic = "ADC")
@ispec_ia32("*>[ {1b} /r     ]", mnemonic = "SBB")
@ispec_ia32("*>[ {23} /r     ]", mnemonic = "AND")
@ispec_ia32("*>[ {2b} /r     ]", mnemonic = "SUB")
@ispec_ia32("*>[ {33} /r     ]", mnemonic = "XOR")
@ispec_ia32("*>[ {3b} /r     ]", mnemonic = "CMP")
@ispec_ia32("*>[ {87} /r     ]", mnemonic = "XCHG")
@ispec_ia32("*>[ {8b} /r     ]", mnemonic = "MOV")
@ispec_ia32("*>[ {8d} /r     ]", mnemonic = "LEA")
@ispec_ia32("*>[ {0f}{bc} /r ]", mnemonic = "BSF")
@ispec_ia32("*>[ {0f}{bd} /r ]", mnemonic = "BSR")
@ispec_ia32("*>[ {0f}{af} /r ]", mnemonic = "IMUL")
@ispec_ia32("*>[ {0f}{03} /r ]", mnemonic = "LSL")
@ispec_ia32("*>[ {0f}{b8} /r ]", mnemonic = "POPCNT")
def ia32_reg_32_inv(obj,Mod,RM,REG,data):
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op1, op2]
    obj.type = type_data_processing
    if obj.mnemonic=="BSR" and obj.misc['rep']:
        obj.mnemonic = "LZCNT"
    elif obj.mnemonic=="POPCNT" and not obj.misc['rep']:
        raise InstructionError(obj)
    elif obj.mnemonic=="LEA" and not op2._is_mem:
        raise InstructionError(obj)

# r16/32 , m16:16/32
@ispec_ia32("*>[ {c5} /r     ]", mnemonic = "LDS", _seg=env.ds)
@ispec_ia32("*>[ {0f}{b2} /r ]", mnemonic = "LSS", _seg=env.ss)
@ispec_ia32("*>[ {c4} /r     ]", mnemonic = "LES", _seg=env.es)
@ispec_ia32("*>[ {0f}{b4} /r ]", mnemonic = "LFS", _seg=env.fs)
@ispec_ia32("*>[ {0f}{b5} /r ]", mnemonic = "LGS", _seg=env.gs)
def ia32_r32_seg(obj,Mod,RM,REG,data,_seg):
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_mem: raise InstructionError(obj)
    op1 = env.getreg(REG,op2.size)
    op2 = env.mem(op2.a,op1.size+16,_seg)
    obj.operands = [op1, op2]
    obj.type = type_system

@ispec_ia32("*>[ {0f}{ad} /r ]", mnemonic = "SHRD")
@ispec_ia32("*>[ {0f}{a5} /r ]", mnemonic = "SHLD")
def ia32_rm32_op3cl(obj,Mod,RM,REG,data):
    op1,data = getModRM(obj,Mod,RM,data)
    op2 = env.getreg(REG,op1.size)
    obj.operands = [op1, op2, env.cl]
    obj.type = type_data_processing

@ispec_ia32("*>[ {0f}{ac} /r ]", mnemonic = "SHRD")
@ispec_ia32("*>[ {0f}{a4} /r ]", mnemonic = "SHLD")
def ia32_rm32_op3cst(obj,Mod,RM,REG,data):
    op1,data = getModRM(obj,Mod,RM,data)
    op2 = env.getreg(REG,op1.size)
    imm = data[0:8]
    obj.operands = [op1, op2, env.cst(imm.int(),8)]
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# r16/32 , m16&16/32&32
@ispec_ia32("*>[ {62} /r     ]", mnemonic = "BOUND")
def ia32_r32_bound(obj,Mod,RM,REG,data):
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_mem: raise InstructionError(obj)
    op1 = env.getreg(REG,op2.size)
    op2 = env.mem(op2.a,op1.size*2)
    obj.operands = [op1, op2]
    obj.type = type_data_processing

# conditionals:
@ispec_ia32("*>[ {0f} cc(4) 0010 /r ]", mnemonic = "CMOVcc") # 0f 4x /r
def ia32_CMOVcc(obj,cc,Mod,RM,REG,data):
    obj.cond = CONDITION_CODES[cc]
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op1, op2]
    obj.type = type_data_processing

@ispec_ia32("*>[ {0f} cc(4) 1001 /r ]", mnemonic = "SETcc")  # 0f 9x /r
def ia32_SETcc(obj,cc,Mod,RM,REG,data):
    obj.misc['opdsz'] = 8
    obj.cond = CONDITION_CODES[cc]
    op1,data = getModRM(obj,Mod,RM,data)
    obj.operands = [op1]
    obj.type = type_data_processing

# 3 operands:
# -----------

# r16/32, r/m16/32, sign extended imm8
@ispec_ia32("*>[ {6b} /r ]", mnemonic = "IMUL")
def ia32_reg_rm_8(obj,Mod,RM,REG,data):
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,op2.size)
    if data.size<8: raise InstructionError(obj)
    imm = data[0:8]
    x = env.cst(imm.int(),8).signextend(op1.size)
    obj.operands = [op1, op2, x]
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# r16/32, r/m16/32, imm16/32
@ispec_ia32("*>[ {69} /r ]", mnemonic = "IMUL")
def ia32_reg_rm_wd(obj,Mod,RM,REG,data):
    op2,data = getModRM(obj,Mod,RM,data)
    op1 = env.getreg(REG,op2.size)
    if data.size<op2.size: raise InstructionError(obj)
    imm = data[0:op2.size]
    x = env.cst(imm.int(),op2.size)
    obj.operands = [op1, op2, x]
    obj.bytes += pack(imm)
    obj.type = type_data_processing

# special cases:
# --------------

@ispec_ia32("*>[ {0f}{c7} /6  ]", mnemonic = "RDRAND")
def ia32_rdrand(obj,Mod,RM,data):
    op1,data = getModRM(obj,Mod,RM,data)
    if not op1._is_reg: raise InstructionError
    obj.operands = [op1]
    obj.type = type_other

@ispec_ia32("*>[ {0f}{c3} /r ]", mnemonic = "MOVNTI")
def ia32_rdrand(obj,Mod,RM,REG,data):
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_mem: raise InstructionError(obj)
    op1 = env.getreg(REG,op2.size)
    obj.operands = [op2,op1]
    obj.type = type_data_processing

@ispec_ia32("*>[ {0f}{c7} /1 ]", mnemonic = "CMPXCHG8B")
def ia32_cmpxchg(obj,Mod,RM,data):
    op2,data = getModRM(obj,Mod,RM,data)
    if not op2._is_mem: raise InstructionError(obj)
    op2.size = 64
    obj.operands = [op2]
    obj.type = type_data_processing

@ispec_ia32("*>[ {0f}{1f} /0  ]", mnemonic = "NOP",     type=type_cpu_state)
def ia32_longnop(obj,Mod,RM,data):
    op1, data = getModRM(obj,Mod,RM,data)

@ispec_ia32("*>[ {0f}{ae} /0  ]", mnemonic = "FXSAVE",  type=type_cpu_state)
@ispec_ia32("*>[ {0f}{ae} /1  ]", mnemonic = "FXRSTOR", type=type_cpu_state)
@ispec_ia32("*>[ {0f}{ae} /2  ]", mnemonic = "LDMXCSR", type=type_cpu_state)
@ispec_ia32("*>[ {0f}{ae} /3  ]", mnemonic = "STMXCSR", type=type_cpu_state)
@ispec_ia32("*>[ {0f}{ae} /4  ]", mnemonic = "XSAVE",   type=type_cpu_state)
@ispec_ia32("*>[ {0f}{ae} /5  ]", mnemonic = "XRSTOR",  type=type_cpu_state)
@ispec_ia32("*>[ {0f}{ae} /6  ]", mnemonic = "XSAVEOPT",type=type_cpu_state)
@ispec_ia32("*>[ {0f}{ae} /7  ]", mnemonic = "CLFLUSH", type=type_cpu_state)
def ia32_xfence(obj,Mod,RM,data):
    op1, data = getModRM(obj,Mod,RM,data)
    if Mod == 0b11:
        table = {
            "XRSTOR":   "LFENCE",
            "XSAVEOPT": "MFENCE",
            "CLFLUSH":  "SFENCE",
            }
        if obj.mnemonic in table:
            obj.mnemonic = table[obj.mnemonic]
        else:
            raise InstructionError(obj)
    else:
        obj.operands = [op1]
        if obj.mnemonic == "CLFLUSH":
            obj.misc['opdsz']=8

@ispec_ia32("*>[ {0f}{20} /r ]", mnemonic = "MOV", _inv=False)
@ispec_ia32("*>[ {0f}{22} /r ]", mnemonic = "MOV", _inv=True)
def ia32_mov_cr(obj,Mod,REG,RM,data,_inv):
    if REG not in (0,2,3,4): raise InstructionError(obj)
    op1 = env.cr(REG)
    op2 = env.getreg(RM,32)
    obj.operands = [op1, op2] if not _inv else [op2, op1]
    obj.type = type_system

@ispec_ia32("*>[ {0f}{21} /r ]", mnemonic = "MOV", _inv=False)
@ispec_ia32("*>[ {0f}{23} /r ]", mnemonic = "MOV", _inv=True)
def ia32_mov_dr(obj,Mod,REG,RM,data,_inv):
    op1 = env.dr(REG)
    op2 = env.getreg(RM,32)
    obj.operands = [op1, op2] if not _inv else [op2, op1]
    obj.type = type_system

@ispec_ia32("*>[ {0f}{02} /r ]", mnemonic = "LAR")
def ia32_mov_dr(obj,Mod,REG,RM,data):
    op1 = env.dr(REG)
    op2,data = getModRM(obj,Mod,RM,data)
    obj.operands = [op1, op2]
    obj.type = type_system

# IN/OUT:

# implicit al/ax/eax register:
@ispec_ia32("8>[ {ec} ]", mnemonic = "IN")
@ispec_ia32("8>[ {ee} ]", mnemonic = "OUT")
def ia32_inout_8(obj):
    obj.operands = [env.al,env.dx] if obj.mnemonic=='IN' else [env.dx,env.al]
    obj.type = type_system

@ispec_ia32("8>[ {ed} ]", mnemonic = "IN")
@ispec_ia32("8>[ {ef} ]", mnemonic = "OUT")
def ia32_inout_32(obj):
    op1 = env.ax if obj.misc['opdsz']==16 else env.eax
    obj.operands = [op1,env.dx] if obj.mnemonic=='IN' else [env.dx,op1]
    obj.type = type_system

@ispec_ia32("16>[ {e4} ib(8) ]", mnemonic = "IN")
@ispec_ia32("16>[ {e6} ib(8) ]", mnemonic = "OUT")
def ia32_in_out(obj,ib):
    r,x = env.al, env.cst(ib,8)
    obj.operands = [r,x] if obj.mnemonic=='IN' else [x,r]
    obj.type = type_system

@ispec_ia32("16>[ {e5} ib(8) ]", mnemonic = "IN")
@ispec_ia32("16>[ {e7} ib(8) ]", mnemonic = "OUT")
def ia32_ADC_eax_imm(obj,ib):
    size = obj.misc['opdsz'] or env.internals['mode']
    r = env.eax if size==32 else env.ax
    x = env.cst(ib,8)
    obj.operands = [r,x] if obj.mnemonic=='IN' else [x,r]
    obj.type = type_system

@ispec_ia32("*>[ {0f}{b6} /r ]", mnemonic = "MOVZX", _flg8=True)
@ispec_ia32("*>[ {0f}{b7} /r ]", mnemonic = "MOVZX", _flg8=False)
@ispec_ia32("*>[ {0f}{be} /r ]", mnemonic = "MOVSX", _flg8=True)
@ispec_ia32("*>[ {0f}{bf} /r ]", mnemonic = "MOVSX", _flg8=False)
def ia32_movx(obj,Mod,RM,REG,data,_flg8):
    size = obj.misc['opdsz'] or env.internals['mode']
    op1 = env.getreg(REG,size)
    obj.misc['opdsz']=8 if _flg8 else 16
    op2,data = getModRM(obj,Mod,RM,data)
    obj.operands = [op1, op2]
    obj.type = type_data_processing

# MOVBE & CRC32:
@ispec_ia32("*>[ {0f}{38} s 000 1111 /r ]") # (f2) 0f 38 f0/f1
def ia32_movbe_crc32(obj,s,Mod,RM,REG,data):
    if obj.misc['repne'] and obj.misc['pfx'][0]=='repne':
        obj.mnemonic = "CRC32"
        op1 = env.getreg(REG,32)
        if s==0: obj.misc['opdsz']=8
        op2,data = getModRM(obj,Mod,RM,data)
        obj.operands = [op1, op2]
        obj.type = type_data_processing
    else:
        obj.mnemonic = "MOVBE"
        op1,data = getModRM(obj,Mod,RM,data)
        if not op1._is_mem: raise InstructionError(obj)
        op2 = env.getreg(REG,op1.size)
        obj.operands = [op1, op2] if s else [op2, op1]
        obj.type = type_data_processing


# FPU instructions:
# -----------------

from amoco.arch.x86 import spec_fpu
ISPECS += spec_fpu.ISPECS
#
## SSE instructions:
## -----------------
#
from amoco.arch.x86 import spec_sse
ISPECS += spec_sse.ISPECS

