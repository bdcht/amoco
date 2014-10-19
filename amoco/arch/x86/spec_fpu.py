#!/usr/bin/env python

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

# D9 C0+i
@ispec_ia32("16>[ {D9} reg(3) 0 0011 ]", mnemonic = "FLD")
# DD D0+i
@ispec_ia32("16>[ {DD} reg(3) 0 1011 ]", mnemonic = "FST")
# DD D8+i
@ispec_ia32("16>[ {DD} reg(3) 1 1011 ]", mnemonic = "FSTP")
# D9 C8+i
@ispec_ia32("16>[ {D9} reg(3) 1 0011 ]", mnemonic = "FXCH")
@ispec_ia32("16>[ {D8} reg(3) 0 1011 ]", mnemonic = "FCOM") # D8 D0+i
@ispec_ia32("16>[ {D8} reg(3) 1 1011 ]", mnemonic = "FCOMP") # D8 D8+i
@ispec_ia32("16>[ {DD} reg(3) 0 0111 ]", mnemonic = "FUCOM") # DD E0+i
@ispec_ia32("16>[ {DD} reg(3) 1 0111 ]", mnemonic = "FUCOMP") # DD E8+i
@ispec_ia32("16>[ {DD} reg(3) 0 0011 ]", mnemonic = "FFREE") # DD C0+i
def ia32_fpu_reg(obj, reg):
    obj.operands = [env.st(reg)]
    obj.type = type_data_processing


@ispec_ia32("*>[ {D9} /0 ]", mnemonic = "FLD", _size = 32)
@ispec_ia32("*>[ {DD} /0 ]", mnemonic = "FLD", _size = 64)
@ispec_ia32("*>[ {DB} /5 ]", mnemonic = "FLD", _size = 80)
@ispec_ia32("*>[ {DF} /0 ]", mnemonic = "FILD", _size = 16)
@ispec_ia32("*>[ {DB} /0 ]", mnemonic = "FILD", _size = 32)
@ispec_ia32("*>[ {DF} /5 ]", mnemonic = "FILD", _size = 64)
@ispec_ia32("*>[ {D9} /2 ]", mnemonic = "FST", _size = 32)
@ispec_ia32("*>[ {DD} /2 ]", mnemonic = "FST", _size = 64)
@ispec_ia32("*>[ {D9} /3 ]", mnemonic = "FSTP", _size = 32)
@ispec_ia32("*>[ {DD} /3 ]", mnemonic = "FSTP", _size = 64)
@ispec_ia32("*>[ {DB} /7 ]", mnemonic = "FSTP", _size = 80)
@ispec_ia32("*>[ {DF} /2 ]", mnemonic = "FIST", _size = 16)
@ispec_ia32("*>[ {DB} /2 ]", mnemonic = "FIST", _size = 32)
@ispec_ia32("*>[ {DF} /3 ]", mnemonic = "FISTP", _size = 16)
@ispec_ia32("*>[ {DB} /3 ]", mnemonic = "FISTP", _size = 32)
@ispec_ia32("*>[ {DF} /7 ]", mnemonic = "FISTP", _size = 64)
@ispec_ia32("*>[ {DF} /1 ]", mnemonic = "FISTPP", _size = 16)
@ispec_ia32("*>[ {DB} /1 ]", mnemonic = "FISTPP", _size = 32)
@ispec_ia32("*>[ {DD} /1 ]", mnemonic = "FISTPP", _size = 64)
@ispec_ia32("*>[ {D8} /2 ]", mnemonic = "FCOM", _size = 32)
@ispec_ia32("*>[ {DC} /2 ]", mnemonic = "FCOM", _size = 64)
@ispec_ia32("*>[ {D8} /3 ]", mnemonic = "FCOMP", _size = 32)
@ispec_ia32("*>[ {DC} /3 ]", mnemonic = "FCOMP", _size = 64)
@ispec_ia32("*>[ {D8} /4 ]", mnemonic = "FSUB", _size = 32)
@ispec_ia32("*>[ {DC} /4 ]", mnemonic = "FSUB", _size = 64)
@ispec_ia32("*>[ {DA} /4 ]", mnemonic = "FISUB", _size = 32)
@ispec_ia32("*>[ {DE} /4 ]", mnemonic = "FISUB", _size = 16)
@ispec_ia32("*>[ {D8} /5 ]", mnemonic = "FSUBR", _size = 32)
@ispec_ia32("*>[ {DC} /5 ]", mnemonic = "FSUBR", _size = 64)
@ispec_ia32("*>[ {DA} /5 ]", mnemonic = "FISUBR", _size = 32)
@ispec_ia32("*>[ {DE} /5 ]", mnemonic = "FISUBR", _size = 16)
@ispec_ia32("*>[ {D8} /0 ]", mnemonic = "FADD", _size = 32)
@ispec_ia32("*>[ {DC} /0 ]", mnemonic = "FADD", _size = 64)
@ispec_ia32("*>[ {DA} /0 ]", mnemonic = "FIADD", _size = 32)
@ispec_ia32("*>[ {DE} /0 ]", mnemonic = "FIADD", _size = 16)
@ispec_ia32("*>[ {D8} /6 ]", mnemonic = "FDIV", _size = 32)
@ispec_ia32("*>[ {DC} /6 ]", mnemonic = "FDIV", _size = 64)
@ispec_ia32("*>[ {DA} /6 ]", mnemonic = "FIDIV", _size = 32)
@ispec_ia32("*>[ {DE} /6 ]", mnemonic = "FIDIV", _size = 16)
@ispec_ia32("*>[ {D8} /7 ]", mnemonic = "FDIVR", _size = 32)
@ispec_ia32("*>[ {DC} /7 ]", mnemonic = "FDIVR", _size = 64)
@ispec_ia32("*>[ {DA} /7 ]", mnemonic = "FIDIVR", _size = 32)
@ispec_ia32("*>[ {DE} /7 ]", mnemonic = "FIDIVR", _size = 16)
@ispec_ia32("*>[ {D8} /1 ]", mnemonic = "FMUL", _size = 32)
@ispec_ia32("*>[ {DC} /1 ]", mnemonic = "FMUL", _size = 64)
@ispec_ia32("*>[ {DA} /1 ]", mnemonic = "FIMUL", _size = 32)
@ispec_ia32("*>[ {DE} /1 ]", mnemonic = "FIMUL", _size = 16)
@ispec_ia32("*>[ {DF} /4 ]", mnemonic = "FBLD", _size = 80)
@ispec_ia32("*>[ {DF} /6 ]", mnemonic = "FBSTP", _size = 80)
@ispec_ia32("*>[ {DE} /2 ]", mnemonic = "FICOM", _size = 16)
@ispec_ia32("*>[ {DA} /2 ]", mnemonic = "FICOM", _size = 32)
@ispec_ia32("*>[ {DE} /3 ]", mnemonic = "FICOMP", _size = 16)
@ispec_ia32("*>[ {DA} /3 ]", mnemonic = "FICOMP", _size = 32)
@ispec_ia32("*>[ {D9} /5 ]", mnemonic = "FLDCW", _size = 16)
@ispec_ia32("*>[ {9B}{D9} /7 ]", mnemonic = "FSTCW", _size = 16)
@ispec_ia32("*>[ {D9} /7 ]", mnemonic = "FNSTCW", _size = 16)
@ispec_ia32("*>[ {9B}{D9} /6 ]", mnemonic = "FSTENV", _size = 28*8)
@ispec_ia32("*>[ {D9} /6 ]", mnemonic = "FNSTENV", _size = 28*8)
@ispec_ia32("*>[ {D9} /4 ]", mnemonic = "FLDENV", _size = 28*8) #TODO : 16 bits size
@ispec_ia32("*>[ {DD} /4 ]", mnemonic = "FRSTOR", _size = 108*8) #TODO : 16 bits size
@ispec_ia32("*>[ {9B}{DD} /6 ]", mnemonic = "FSAVE", _size = 108*8) #TODO : 16 bits size
@ispec_ia32("*>[ {DD} /6 ]", mnemonic = "FNSAVE", _size = 108*8) #TODO : 16 bits size
@ispec_ia32("*>[ {0F}{AE} /0 ]", mnemonic = "FXSAVE", _size = 512*8)
@ispec_ia32("*>[ {0F}{AE} /1 ]", mnemonic = "FXRSTOR", _size = 512*8)
def ia32_fpu_mem(obj, Mod, RM, data, _size):
    # registers are not allowed
    if Mod == 3:
        raise InstructionError(obj)
    op1, data = getModRM(obj,Mod,RM,data)
    op1.size = _size
    obj.operands = [op1]
    obj.type = type_data_processing

@ispec_ia32("24>[ {9B}{DF}{E0} ]", mnemonic = "FSTSW")
@ispec_ia32("16>[ {DF}{E0} ]", mnemonic = "FNSTSW")
def ia32_fstsw_ax(obj):
    obj.operands = [ env.getreg(0, 16) ]
    obj.type = type_data_processing

@ispec_ia32("*>[ {DD} /7 ]", mnemonic = "FNSTSW")
@ispec_ia32("*>[ {9B}{DD} /7 ]", mnemonic = "FSTSW")
def ia32_fstsw(obj, Mod, RM, data):
    op1,data = getModRM(obj,Mod,RM,data)
    obj.operands = [op1]
    obj.type = type_data_processing

@ispec_ia32("16>[ {D9}{E0} ]", mnemonic = "FCHS")
@ispec_ia32("16>[ {D9}{E8} ]", mnemonic = "FLD1")
@ispec_ia32("16>[ {D9}{E9} ]", mnemonic = "FLDL2T")
@ispec_ia32("16>[ {D9}{EA} ]", mnemonic = "FLDL2E")
@ispec_ia32("16>[ {D9}{EB} ]", mnemonic = "FLDPI")
@ispec_ia32("16>[ {D9}{EC} ]", mnemonic = "FLDLG2")
@ispec_ia32("16>[ {D9}{ED} ]", mnemonic = "FLDLN2")
@ispec_ia32("16>[ {D9}{EE} ]", mnemonic = "FLDZ")
@ispec_ia32("16>[ {DE}{D9} ]", mnemonic = "FCOMPP")
@ispec_ia32("16>[ {DA}{E9} ]", mnemonic = "FUCOMPP")
@ispec_ia32("16>[ {D9}{F0} ]", mnemonic = "F2XM1")
@ispec_ia32("16>[ {D9}{E1} ]", mnemonic = "FABS")
@ispec_ia32("16>[ {DB}{E2} ]", mnemonic = "FNCLEX")
@ispec_ia32("24>[ {9B}{DB}{E2} ]", mnemonic = "FCLEX")
@ispec_ia32("16>[ {DB}{E3} ]", mnemonic = "FNINIT")
@ispec_ia32("24>[ {9B}{DB}{E3} ]", mnemonic = "FINIT")
@ispec_ia32("16>[ {D9}{E4} ]", mnemonic = "FTST")
@ispec_ia32("16>[ {D9}{E5} ]", mnemonic = "FXAM")
@ispec_ia32("16>[ {D9}{F1} ]", mnemonic = "FYL2X")
@ispec_ia32("16>[ {D9}{F2} ]", mnemonic = "FPTAN")
@ispec_ia32("16>[ {D9}{F3} ]", mnemonic = "FPATAN")
@ispec_ia32("16>[ {D9}{FA} ]", mnemonic = "FSQRT")
@ispec_ia32("16>[ {D9}{FB} ]", mnemonic = "FSINCOS")
@ispec_ia32("16>[ {D9}{FE} ]", mnemonic = "FSIN")
@ispec_ia32("16>[ {D9}{FF} ]", mnemonic = "FCOS")
@ispec_ia32("16>[ {D9}{F8} ]", mnemonic = "FPREM")
@ispec_ia32("16>[ {D9}{F9} ]", mnemonic = "FYL2XP1")
@ispec_ia32("16>[ {D9}{F4} ]", mnemonic = "FXTRACT")
@ispec_ia32("16>[ {D9}{F5} ]", mnemonic = "FPREM1")
@ispec_ia32("16>[ {D9}{F6} ]", mnemonic = "FDECSTP")
@ispec_ia32("16>[ {D9}{F7} ]", mnemonic = "FINCSTP")
@ispec_ia32("16>[ {D9}{FC} ]", mnemonic = "FRNDINT")
@ispec_ia32("16>[ {D9}{FD} ]", mnemonic = "FSCALE")
@ispec_ia32("16>[ {D9}{D0} ]", mnemonic = "FNOP")
def fld_fpu_noop(obj):
    obj.type = type_data_processing

@ispec_ia32("16>[ {D8} reg(3) 0 0111 ]", mnemonic = "FSUB", _src=None, _dest=0) # D8 E0+i
@ispec_ia32("16>[ {DC} reg(3) 1 0111 ]", mnemonic = "FSUB", _src=0, _dest=None) # DC E8+i
@ispec_ia32("16>[ {DE} reg(3) 1 0111 ]", mnemonic = "FSUBP", _src=0, _dest=None) # DE E8+i
@ispec_ia32("16>[ {D8} reg(3) 1 0111 ]", mnemonic = "FSUBR", _src=None, _dest=0) # D8 E8+i
@ispec_ia32("16>[ {DC} reg(3) 0 0111 ]", mnemonic = "FSUBR", _src=0, _dest=None) # DC E0+i
@ispec_ia32("16>[ {DE} reg(3) 0 0111 ]", mnemonic = "FSUBRP", _src=0, _dest=None) # DE E0+i
@ispec_ia32("16>[ {D8} reg(3) 0 0011 ]", mnemonic = "FADD", _src=None, _dest=0) # D8 C0+i
@ispec_ia32("16>[ {DC} reg(3) 0 0011 ]", mnemonic = "FADD", _src=0, _dest=None) # DC C0+i
@ispec_ia32("16>[ {DE} reg(3) 0 0011 ]", mnemonic = "FADDP", _src=0, _dest=None) # DE C0+i
@ispec_ia32("16>[ {D8} reg(3) 0 1111 ]", mnemonic = "FDIV", _src=None, _dest=0) # D8 F0+i
@ispec_ia32("16>[ {DC} reg(3) 1 1111 ]", mnemonic = "FDIV", _src=0, _dest=None) # DC F8+i
@ispec_ia32("16>[ {DE} reg(3) 1 1111 ]", mnemonic = "FDIVP", _src=0, _dest=None) # DE F8+i
@ispec_ia32("16>[ {D8} reg(3) 1 1111 ]", mnemonic = "FDIVR", _src=None, _dest=0) # D8 F8+i
@ispec_ia32("16>[ {DC} reg(3) 0 1111 ]", mnemonic = "FDIVR", _src=0, _dest=None) # DC F0+i
@ispec_ia32("16>[ {DE} reg(3) 0 1111 ]", mnemonic = "FDIVRP", _src=0, _dest=None) # DE F0+i
@ispec_ia32("16>[ {D8} reg(3) 1 0011 ]", mnemonic = "FMUL", _src=None, _dest=0) # D8 C8+i
@ispec_ia32("16>[ {DC} reg(3) 1 0011 ]", mnemonic = "FMUL", _src=0, _dest=None) # DC C8+i
@ispec_ia32("16>[ {DE} reg(3) 1 0011 ]", mnemonic = "FMULP", _src=0, _dest=None) # DE C8+i
@ispec_ia32("16>[ {DA} reg(3) 0 0011 ]", mnemonic = "FCMOVB", _src=None, _dest=0) # DA C0+i
@ispec_ia32("16>[ {DA} reg(3) 1 0011 ]", mnemonic = "FCMOVE", _src=None, _dest=0) # DA C8+i
@ispec_ia32("16>[ {DA} reg(3) 0 1011 ]", mnemonic = "FCMOVBE", _src=None, _dest=0) # DA D0+i
@ispec_ia32("16>[ {DA} reg(3) 1 1011 ]", mnemonic = "FCMOVU", _src=None, _dest=0) # DA D8+i
@ispec_ia32("16>[ {DB} reg(3) 0 0011 ]", mnemonic = "FCMOVNB", _src=None, _dest=0) # DB C0+i
@ispec_ia32("16>[ {DB} reg(3) 1 0011 ]", mnemonic = "FCMOVNE", _src=None, _dest=0) # DB C8+i
@ispec_ia32("16>[ {DB} reg(3) 0 1011 ]", mnemonic = "FCMOVNBE", _src=None, _dest=0) # DB D0+i
@ispec_ia32("16>[ {DB} reg(3) 1 1011 ]", mnemonic = "FCMOVNU", _src=None, _dest=0) # DB D8+i
@ispec_ia32("16>[ {DB} reg(3) 0 1111 ]", mnemonic = "FCOMI", _src=None, _dest=0) # DB F0+i
@ispec_ia32("16>[ {DF} reg(3) 0 1111 ]", mnemonic = "FCOMIP", _src=None, _dest=0) # DF F0+i
@ispec_ia32("16>[ {DB} reg(3) 1 0111 ]", mnemonic = "FUCOMI", _src=None, _dest=0) # DB E8+i
@ispec_ia32("16>[ {DF} reg(3) 1 0111 ]", mnemonic = "FUCOMIP", _src=None, _dest=0) # DF E8+i
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

