# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# spec_xxx files are providers for instruction objects.

from .utils import *

#------------------------------------------------------
# amoco x86 FPU (x87) instruction specs:
#------------------------------------------------------

ISPECS = []

@ispec_ia32("16>[ {0f}{77} ]", mnemonic = "EMMS", type=type_cpu_state)
def ia32_nooperand(obj):
    pass

@ispec_ia32("16>[ {d9} reg(3) 0 0011 ]", mnemonic = "FLD")    # D9 C0+i
@ispec_ia32("16>[ {d9} reg(3) 1 0011 ]", mnemonic = "FXCH")   # D9 C8+i
@ispec_ia32("16>[ {d8} reg(3) 0 1011 ]", mnemonic = "FCOM")   # D8 D0+i
@ispec_ia32("16>[ {d8} reg(3) 1 1011 ]", mnemonic = "FCOMP")  # D8 D8+i
@ispec_ia32("16>[ {dd} reg(3) 0 0011 ]", mnemonic = "FFREE")  # DD C0+i
@ispec_ia32("16>[ {dd} reg(3) 0 1011 ]", mnemonic = "FST")    # DD D0+i
@ispec_ia32("16>[ {dd} reg(3) 1 1011 ]", mnemonic = "FSTP")   # DD D8+i
@ispec_ia32("16>[ {dd} reg(3) 0 0111 ]", mnemonic = "FUCOM")  # DD E0+i
@ispec_ia32("16>[ {dd} reg(3) 1 0111 ]", mnemonic = "FUCOMP") # DD E8+i
def ia32_fpu_reg(obj, reg):
    obj.operands = [env.st(reg)]
    obj.type = type_data_processing

@ispec_ia32("*>[ {d8} /0 ]", mnemonic = "FADD",    _size = 32)
@ispec_ia32("*>[ {d8} /1 ]", mnemonic = "FMUL",    _size = 32)
@ispec_ia32("*>[ {d8} /2 ]", mnemonic = "FCOM",    _size = 32)
@ispec_ia32("*>[ {d8} /3 ]", mnemonic = "FCOMP",   _size = 32)
@ispec_ia32("*>[ {d8} /4 ]", mnemonic = "FSUB",    _size = 32)
@ispec_ia32("*>[ {d8} /5 ]", mnemonic = "FSUBR",   _size = 32)
@ispec_ia32("*>[ {d8} /6 ]", mnemonic = "FDIV",    _size = 32)
@ispec_ia32("*>[ {d8} /7 ]", mnemonic = "FDIVR",   _size = 32)
@ispec_ia32("*>[ {d9} /0 ]", mnemonic = "FLD",     _size = 32)
@ispec_ia32("*>[ {d9} /2 ]", mnemonic = "FST",     _size = 32)
@ispec_ia32("*>[ {d9} /3 ]", mnemonic = "FSTP",    _size = 32)
@ispec_ia32("*>[ {d9} /4 ]", mnemonic = "FLDENV",  _size = 28*8) #TODO : 16 bits size
@ispec_ia32("*>[ {d9} /5 ]", mnemonic = "FLDCW",   _size = 16)
@ispec_ia32("*>[ {d9} /6 ]", mnemonic = "FNSTENV", _size = 28*8)
@ispec_ia32("*>[ {d9} /7 ]", mnemonic = "FNSTCW",  _size = 16)
@ispec_ia32("*>[ {da} /0 ]", mnemonic = "FIADD",   _size = 32)
@ispec_ia32("*>[ {da} /1 ]", mnemonic = "FIMUL",   _size = 32)
@ispec_ia32("*>[ {da} /2 ]", mnemonic = "FICOM",   _size = 32)
@ispec_ia32("*>[ {da} /3 ]", mnemonic = "FICOMP",  _size = 32)
@ispec_ia32("*>[ {da} /4 ]", mnemonic = "FISUB",   _size = 32)
@ispec_ia32("*>[ {da} /5 ]", mnemonic = "FISUBR",  _size = 32)
@ispec_ia32("*>[ {da} /6 ]", mnemonic = "FIDIV",   _size = 32)
@ispec_ia32("*>[ {da} /7 ]", mnemonic = "FIDIVR",  _size = 32)
@ispec_ia32("*>[ {db} /0 ]", mnemonic = "FILD",    _size = 32)
@ispec_ia32("*>[ {db} /1 ]", mnemonic = "FISTTP",  _size = 32)
@ispec_ia32("*>[ {db} /2 ]", mnemonic = "FIST",    _size = 32)
@ispec_ia32("*>[ {db} /3 ]", mnemonic = "FISTP",   _size = 32)
@ispec_ia32("*>[ {db} /5 ]", mnemonic = "FLD",     _size = 80)
@ispec_ia32("*>[ {db} /7 ]", mnemonic = "FSTP",    _size = 80)
@ispec_ia32("*>[ {dc} /0 ]", mnemonic = "FADD",    _size = 64)
@ispec_ia32("*>[ {dc} /1 ]", mnemonic = "FMUL",    _size = 64)
@ispec_ia32("*>[ {dc} /2 ]", mnemonic = "FCOM",    _size = 64)
@ispec_ia32("*>[ {dc} /3 ]", mnemonic = "FCOMP",   _size = 64)
@ispec_ia32("*>[ {dc} /4 ]", mnemonic = "FSUB",    _size = 64)
@ispec_ia32("*>[ {dc} /5 ]", mnemonic = "FSUBR",   _size = 64)
@ispec_ia32("*>[ {dc} /6 ]", mnemonic = "FDIV",    _size = 64)
@ispec_ia32("*>[ {dc} /7 ]", mnemonic = "FDIVR",   _size = 64)
@ispec_ia32("*>[ {dd} /0 ]", mnemonic = "FLD",     _size = 64)
@ispec_ia32("*>[ {dd} /1 ]", mnemonic = "FISTTP",  _size = 64)
@ispec_ia32("*>[ {dd} /2 ]", mnemonic = "FST",     _size = 64)
@ispec_ia32("*>[ {dd} /3 ]", mnemonic = "FSTP",    _size = 64)
@ispec_ia32("*>[ {dd} /4 ]", mnemonic = "FRSTOR",  _size = 108*8) #TODO : 16 bits size
@ispec_ia32("*>[ {dd} /6 ]", mnemonic = "FNSAVE",  _size = 108*8) #TODO : 16 bits size
@ispec_ia32("*>[ {de} /0 ]", mnemonic = "FIADD",   _size = 16)
@ispec_ia32("*>[ {de} /1 ]", mnemonic = "FIMUL",   _size = 16)
@ispec_ia32("*>[ {de} /2 ]", mnemonic = "FICOM",   _size = 16)
@ispec_ia32("*>[ {de} /3 ]", mnemonic = "FICOMP",  _size = 16)
@ispec_ia32("*>[ {de} /4 ]", mnemonic = "FISUB",   _size = 16)
@ispec_ia32("*>[ {de} /5 ]", mnemonic = "FISUBR",  _size = 16)
@ispec_ia32("*>[ {de} /6 ]", mnemonic = "FIDIV",   _size = 16)
@ispec_ia32("*>[ {de} /7 ]", mnemonic = "FIDIVR",  _size = 16)
@ispec_ia32("*>[ {df} /0 ]", mnemonic = "FILD",    _size = 16)
@ispec_ia32("*>[ {df} /1 ]", mnemonic = "FISTTP",  _size = 16)
@ispec_ia32("*>[ {df} /2 ]", mnemonic = "FIST",    _size = 16)
@ispec_ia32("*>[ {df} /3 ]", mnemonic = "FISTP",   _size = 16)
@ispec_ia32("*>[ {df} /4 ]", mnemonic = "FBLD",    _size = 80)
@ispec_ia32("*>[ {df} /5 ]", mnemonic = "FILD",    _size = 64)
@ispec_ia32("*>[ {df} /6 ]", mnemonic = "FBSTP",   _size = 80)
@ispec_ia32("*>[ {df} /7 ]", mnemonic = "FISTP",   _size = 64)
@ispec_ia32("*>[ {9b}{d9} /7 ]", mnemonic = "FSTCW",   _size = 16)
@ispec_ia32("*>[ {9b}{d9} /6 ]", mnemonic = "FSTENV",  _size = 28*8)
@ispec_ia32("*>[ {9b}{dd} /6 ]", mnemonic = "FSAVE",   _size = 108*8) #TODO : 16 bits size
@ispec_ia32("*>[ {0f}{ae} /0 ]", mnemonic = "FXSAVE",  _size = 512*8)
@ispec_ia32("*>[ {0f}{ae} /1 ]", mnemonic = "FXRSTOR", _size = 512*8)
def ia32_fpu_mem(obj, Mod, RM, data, _size):
    op1, data = getModRM(obj,Mod,RM,data)
    if op1._is_reg: raise InstructionError(obj)
    op1.size = _size
    obj.operands = [op1]
    obj.type = type_data_processing

@ispec_ia32("24>[ {9b}{df}{e0} ]", mnemonic = "FSTSW")
@ispec_ia32("16>[     {df}{e0} ]", mnemonic = "FNSTSW")
def ia32_fstsw_ax(obj):
    obj.operands = [ env.getreg(0, 16) ]
    obj.type = type_data_processing

@ispec_ia32("*>[ {9b}{dd} /7 ]", mnemonic = "FSTSW")
@ispec_ia32("*>[     {dd} /7 ]", mnemonic = "FNSTSW")
def ia32_fstsw(obj, Mod, RM, data):
    op1,data = getModRM(obj,Mod,RM,data)
    obj.operands = [op1]
    obj.type = type_data_processing

@ispec_ia32("16>[ {d9}{d0} ]", mnemonic = "FNOP")
@ispec_ia32("16>[ {d9}{e0} ]", mnemonic = "FCHS")
@ispec_ia32("16>[ {d9}{e1} ]", mnemonic = "FABS")
@ispec_ia32("16>[ {d9}{e4} ]", mnemonic = "FTST")
@ispec_ia32("16>[ {d9}{e5} ]", mnemonic = "FXAM")
@ispec_ia32("16>[ {d9}{e8} ]", mnemonic = "FLD1")
@ispec_ia32("16>[ {d9}{e9} ]", mnemonic = "FLDL2T")
@ispec_ia32("16>[ {d9}{ea} ]", mnemonic = "FLDL2E")
@ispec_ia32("16>[ {d9}{eb} ]", mnemonic = "FLDPI")
@ispec_ia32("16>[ {d9}{ec} ]", mnemonic = "FLDLG2")
@ispec_ia32("16>[ {d9}{ed} ]", mnemonic = "FLDLN2")
@ispec_ia32("16>[ {d9}{ee} ]", mnemonic = "FLDZ")
@ispec_ia32("16>[ {d9}{f0} ]", mnemonic = "F2XM1")
@ispec_ia32("16>[ {d9}{f1} ]", mnemonic = "FYL2X")
@ispec_ia32("16>[ {d9}{f2} ]", mnemonic = "FPTAN")
@ispec_ia32("16>[ {d9}{f3} ]", mnemonic = "FPATAN")
@ispec_ia32("16>[ {d9}{f4} ]", mnemonic = "FXTRACT")
@ispec_ia32("16>[ {d9}{f5} ]", mnemonic = "FPREM1")
@ispec_ia32("16>[ {d9}{f6} ]", mnemonic = "FDECSTP")
@ispec_ia32("16>[ {d9}{f7} ]", mnemonic = "FINCSTP")
@ispec_ia32("16>[ {d9}{f8} ]", mnemonic = "FPREM")
@ispec_ia32("16>[ {d9}{f9} ]", mnemonic = "FYL2XP1")
@ispec_ia32("16>[ {d9}{fa} ]", mnemonic = "FSQRT")
@ispec_ia32("16>[ {d9}{fb} ]", mnemonic = "FSINCOS")
@ispec_ia32("16>[ {d9}{fc} ]", mnemonic = "FRNDINT")
@ispec_ia32("16>[ {d9}{fd} ]", mnemonic = "FSCALE")
@ispec_ia32("16>[ {d9}{fe} ]", mnemonic = "FSIN")
@ispec_ia32("16>[ {d9}{ff} ]", mnemonic = "FCOS")
@ispec_ia32("16>[ {da}{e9} ]", mnemonic = "FUCOMPP")
@ispec_ia32("16>[ {db}{e2} ]", mnemonic = "FNCLEX")
@ispec_ia32("16>[ {db}{e3} ]", mnemonic = "FNINIT")
@ispec_ia32("16>[ {de}{d9} ]", mnemonic = "FCOMPP")
@ispec_ia32("24>[ {9b}{db}{e2} ]", mnemonic = "FCLEX")
@ispec_ia32("24>[ {9b}{db}{e3} ]", mnemonic = "FINIT")
def fld_fpu_noop(obj):
    obj.type = type_data_processing

@ispec_ia32("16>[ {d8} reg(3) 0 0111 ]", mnemonic = "FSUB",     _src=None, _dest=0) # D8 E0+i
@ispec_ia32("16>[ {dc} reg(3) 1 0111 ]", mnemonic = "FSUB",     _src=0, _dest=None) # DC E8+i
@ispec_ia32("16>[ {de} reg(3) 1 0111 ]", mnemonic = "FSUBP",    _src=0, _dest=None) # DE E8+i
@ispec_ia32("16>[ {d8} reg(3) 1 0111 ]", mnemonic = "FSUBR",    _src=None, _dest=0) # D8 E8+i
@ispec_ia32("16>[ {dc} reg(3) 0 0111 ]", mnemonic = "FSUBR",    _src=0, _dest=None) # DC E0+i
@ispec_ia32("16>[ {de} reg(3) 0 0111 ]", mnemonic = "FSUBRP",   _src=0, _dest=None) # DE E0+i
@ispec_ia32("16>[ {d8} reg(3) 0 0011 ]", mnemonic = "FADD",     _src=None, _dest=0) # D8 C0+i
@ispec_ia32("16>[ {dc} reg(3) 0 0011 ]", mnemonic = "FADD",     _src=0, _dest=None) # DC C0+i
@ispec_ia32("16>[ {de} reg(3) 0 0011 ]", mnemonic = "FADDP",    _src=0, _dest=None) # DE C0+i
@ispec_ia32("16>[ {d8} reg(3) 0 1111 ]", mnemonic = "FDIV",     _src=None, _dest=0) # D8 F0+i
@ispec_ia32("16>[ {dc} reg(3) 1 1111 ]", mnemonic = "FDIV",     _src=0, _dest=None) # DC F8+i
@ispec_ia32("16>[ {de} reg(3) 1 1111 ]", mnemonic = "FDIVP",    _src=0, _dest=None) # DE F8+i
@ispec_ia32("16>[ {d8} reg(3) 1 1111 ]", mnemonic = "FDIVR",    _src=None, _dest=0) # D8 F8+i
@ispec_ia32("16>[ {dc} reg(3) 0 1111 ]", mnemonic = "FDIVR",    _src=0, _dest=None) # DC F0+i
@ispec_ia32("16>[ {de} reg(3) 0 1111 ]", mnemonic = "FDIVRP",   _src=0, _dest=None) # DE F0+i
@ispec_ia32("16>[ {d8} reg(3) 1 0011 ]", mnemonic = "FMUL",     _src=None, _dest=0) # D8 C8+i
@ispec_ia32("16>[ {dc} reg(3) 1 0011 ]", mnemonic = "FMUL",     _src=0, _dest=None) # DC C8+i
@ispec_ia32("16>[ {de} reg(3) 1 0011 ]", mnemonic = "FMULP",    _src=0, _dest=None) # DE C8+i
@ispec_ia32("16>[ {da} reg(3) 0 0011 ]", mnemonic = "FCMOVB",   _src=None, _dest=0) # DA C0+i
@ispec_ia32("16>[ {da} reg(3) 1 0011 ]", mnemonic = "FCMOVE",   _src=None, _dest=0) # DA C8+i
@ispec_ia32("16>[ {da} reg(3) 0 1011 ]", mnemonic = "FCMOVBE",  _src=None, _dest=0) # DA D0+i
@ispec_ia32("16>[ {da} reg(3) 1 1011 ]", mnemonic = "FCMOVU",   _src=None, _dest=0) # DA D8+i
@ispec_ia32("16>[ {db} reg(3) 0 0011 ]", mnemonic = "FCMOVNB",  _src=None, _dest=0) # DB C0+i
@ispec_ia32("16>[ {db} reg(3) 1 0011 ]", mnemonic = "FCMOVNE",  _src=None, _dest=0) # DB C8+i
@ispec_ia32("16>[ {db} reg(3) 0 1011 ]", mnemonic = "FCMOVNBE", _src=None, _dest=0) # DB D0+i
@ispec_ia32("16>[ {db} reg(3) 1 1011 ]", mnemonic = "FCMOVNU",  _src=None, _dest=0) # DB D8+i
@ispec_ia32("16>[ {db} reg(3) 0 1111 ]", mnemonic = "FCOMI",    _src=None, _dest=0) # DB F0+i
@ispec_ia32("16>[ {df} reg(3) 0 1111 ]", mnemonic = "FCOMIP",   _src=None, _dest=0) # DF F0+i
@ispec_ia32("16>[ {db} reg(3) 1 0111 ]", mnemonic = "FUCOMI",   _src=None, _dest=0) # DB E8+i
@ispec_ia32("16>[ {df} reg(3) 1 0111 ]", mnemonic = "FUCOMIP",  _src=None, _dest=0) # DF E8+i
def ia32_fpu_st(obj, reg, _dest, _src):
    # FSUBP
    if _dest is None and _src is None:
        return
    if _dest is None:
        _dest = reg
    elif _src is None:
        _src = reg
    op1 = env.st(_dest)
    op2 = env.st(_src)
    obj.operands = [op1, op2]
    obj.type = type_data_processing

