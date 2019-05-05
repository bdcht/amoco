# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/dwarf.py
===============

The system dwarf module implements DWARF and C++ eh_frame* classes for executable format.
"""

from amoco.ui.render import Token,highlight
from amoco.logger import Log
logger = Log(__name__)

from amoco.system.structs import Consts,StructDefine,StructFormatter

try:
    IntType = (int,long)
except NameError:
    IntType = (int,)

# ccrawl -b None -l ~/gcc.db show -f amoco "enum dwarf_location_atom"
with Consts('dwarf_location_atom'):
  DW_OP_skip = 47
  DW_OP_mod = 29
  DW_OP_reg25 = 105
  DW_OP_shra = 38
  DW_OP_GNU_const_type = 244
  DW_OP_lit13 = 61
  DW_OP_reg23 = 103
  DW_OP_shl = 36
  DW_OP_const4u = 12
  DW_OP_const4s = 13
  DW_OP_GNU_addr_index = 251
  DW_OP_PGI_omp_thread_num = 248
  DW_OP_form_tls_address = 155
  DW_OP_HP_fltconst4 = 226
  DW_OP_addrx = 161
  DW_OP_lit12 = 60
  DW_OP_GNU_reinterpret = 249
  DW_OP_shr = 37
  DW_OP_consts = 17
  DW_OP_constu = 16
  DW_OP_implicit_value = 158
  DW_OP_constx = 162
  DW_OP_lo_user = 224
  DW_OP_bra = 40
  DW_OP_drop = 19
  DW_OP_GNU_implicit_pointer = 242
  DW_OP_deref_size = 148
  DW_OP_GNU_deref_type = 246
  DW_OP_call_ref = 154
  DW_OP_abs = 25
  DW_OP_call2 = 152
  DW_OP_call4 = 153
  DW_OP_gt = 43
  DW_OP_eq = 41
  DW_OP_rot = 23
  DW_OP_stack_value = 159
  DW_OP_breg5 = 117
  DW_OP_swap = 22
  DW_OP_breg7 = 119
  DW_OP_breg6 = 118
  DW_OP_breg1 = 113
  DW_OP_breg0 = 112
  DW_OP_breg3 = 115
  DW_OP_breg2 = 114
  DW_OP_neg = 31
  DW_OP_breg9 = 121
  DW_OP_breg8 = 120
  DW_OP_call_frame_cfa = 156
  DW_OP_div = 27
  DW_OP_GNU_regval_type = 245
  DW_OP_pick = 21
  DW_OP_xderef = 24
  DW_OP_GNU_parameter_ref = 250
  DW_OP_addr = 3
  DW_OP_over = 20
  DW_OP_lt = 45
  DW_OP_breg28 = 140
  DW_OP_breg29 = 141
  DW_OP_breg20 = 132
  DW_OP_breg21 = 133
  DW_OP_breg22 = 134
  DW_OP_breg23 = 135
  DW_OP_breg24 = 136
  DW_OP_breg25 = 137
  DW_OP_breg26 = 138
  DW_OP_breg27 = 139
  DW_OP_GNU_push_tls_address = 224
  DW_OP_GNU_encoded_addr = 241
  DW_OP_push_object_address = 151
  DW_OP_not = 32
  DW_OP_plus = 34
  DW_OP_nop = 150
  DW_OP_GNU_uninit = 240
  DW_OP_reg14 = 94
  DW_OP_reg15 = 95
  DW_OP_reg16 = 96
  DW_OP_reg17 = 97
  DW_OP_reg10 = 90
  DW_OP_reg11 = 91
  DW_OP_reg12 = 92
  DW_OP_reg13 = 93
  DW_OP_breg31 = 143
  DW_OP_breg30 = 142
  DW_OP_reg18 = 98
  DW_OP_reg19 = 99
  DW_OP_bregx = 146
  DW_OP_const8s = 15
  DW_OP_ne = 46
  DW_OP_const8u = 14
  DW_OP_minus = 28
  DW_OP_AARCH64_operation = 234
  DW_OP_dup = 18
  DW_OP_plus_uconst = 35
  DW_OP_deref_type = 166
  DW_OP_hi_user = 255
  DW_OP_GNU_const_index = 252
  DW_OP_reg29 = 109
  DW_OP_reg28 = 108
  DW_OP_reg21 = 101
  DW_OP_reg20 = 100
  DW_OP_const1s = 9
  DW_OP_reg22 = 102
  DW_OP_and = 26
  DW_OP_reg24 = 104
  DW_OP_reg27 = 107
  DW_OP_reg26 = 106
  DW_OP_GNU_entry_value = 243
  DW_OP_GNU_convert = 247
  DW_OP_breg4 = 116
  DW_OP_entry_value = 163
  DW_OP_xderef_size = 149
  DW_OP_HP_fltconst8 = 227
  DW_OP_lit31 = 79
  DW_OP_lit30 = 78
  DW_OP_regval_type = 165
  DW_OP_HP_unknown = 224
  DW_OP_HP_is_value = 225
  DW_OP_const1u = 8
  DW_OP_GNU_variable_value = 253
  DW_OP_xderef_type = 167
  DW_OP_const2s = 11
  DW_OP_HP_tls = 230
  DW_OP_const2u = 10
  DW_OP_mul = 30
  DW_OP_reg30 = 110
  DW_OP_reg31 = 111
  DW_OP_breg11 = 123
  DW_OP_breg10 = 122
  DW_OP_breg13 = 125
  DW_OP_breg12 = 124
  DW_OP_breg15 = 127
  DW_OP_breg14 = 126
  DW_OP_breg17 = 129
  DW_OP_breg16 = 128
  DW_OP_breg19 = 131
  DW_OP_breg18 = 130
  DW_OP_implicit_pointer = 160
  DW_OP_lit28 = 76
  DW_OP_lit29 = 77
  DW_OP_le = 44
  DW_OP_regx = 144
  DW_OP_lit20 = 68
  DW_OP_lit21 = 69
  DW_OP_lit22 = 70
  DW_OP_lit23 = 71
  DW_OP_lit24 = 72
  DW_OP_lit25 = 73
  DW_OP_lit26 = 74
  DW_OP_lit27 = 75
  DW_OP_lit9 = 57
  DW_OP_lit8 = 56
  DW_OP_HP_unmod_range = 229
  DW_OP_piece = 147
  DW_OP_lit1 = 49
  DW_OP_lit0 = 48
  DW_OP_lit3 = 51
  DW_OP_lit2 = 50
  DW_OP_lit5 = 53
  DW_OP_lit4 = 52
  DW_OP_lit7 = 55
  DW_OP_lit6 = 54
  DW_OP_lit15 = 63
  DW_OP_lit14 = 62
  DW_OP_reinterpret = 169
  DW_OP_convert = 168
  DW_OP_lit17 = 65
  DW_OP_HP_mod_range = 228
  DW_OP_or = 33
  DW_OP_const_type = 164
  DW_OP_lit16 = 64
  DW_OP_xor = 39
  DW_OP_lit11 = 59
  DW_OP_fbreg = 145
  DW_OP_ge = 42
  DW_OP_lit10 = 58
  DW_OP_deref = 6
  DW_OP_bit_piece = 157
  DW_OP_lit19 = 67
  DW_OP_lit18 = 66
  DW_OP_reg8 = 88
  DW_OP_reg9 = 89
  DW_OP_reg6 = 86
  DW_OP_reg7 = 87
  DW_OP_reg4 = 84
  DW_OP_reg5 = 85
  DW_OP_reg2 = 82
  DW_OP_reg3 = 83
  DW_OP_reg0 = 80
  DW_OP_reg1 = 81

# ccrawl -b None -l ~/gcc.db show -f amoco "enum dwarf_call_frame_info"
with Consts('dwarf_call_frame_info'):
  DW_CFA_offset_extended = 5
  DW_CFA_def_cfa_sf = 18
  DW_CFA_def_cfa_offset = 14
  DW_CFA_val_offset = 20
  DW_CFA_GNU_window_save = 45
  DW_CFA_restore_extended = 6
  DW_CFA_def_cfa_expression = 15
  DW_CFA_register = 9
  DW_CFA_MIPS_advance_loc8 = 29
  DW_CFA_hi_user = 63
  DW_CFA_set_loc = 1
  DW_CFA_same_value = 8
  DW_CFA_offset_extended_sf = 17
  DW_CFA_def_cfa_register = 13
  DW_CFA_advance_loc = 64
  DW_CFA_lo_user = 28
  DW_CFA_expression = 16
  DW_CFA_def_cfa = 12
  DW_CFA_def_cfa_offset_sf = 19
  DW_CFA_undefined = 7
  DW_CFA_val_expression = 22
  DW_CFA_nop = 0
  DW_CFA_advance_loc4 = 4
  DW_CFA_advance_loc1 = 2
  DW_CFA_advance_loc2 = 3
  DW_CFA_restore_state = 11
  DW_CFA_GNU_args_size = 46
  DW_CFA_GNU_negative_offset_extended = 47
  DW_CFA_AARCH64_negate_ra_state = 45
  DW_CFA_remember_state = 10
  DW_CFA_val_offset_sf = 21
  DW_CFA_offset = 128
  DW_CFA_restore = 192

@StructDefine("""
I : length
I : id
b : version
""")
class CIE(StructFormatter):
  pass

from amoco.system.core import CoreExec
from amoco.cas.expressions import complexity
from amoco.arch.dwarf import cpu

PAGESIZE = 4096

class DwarfExec(CoreExec):

    def __init__(self,p):
        CoreExec.__init__(self,p,cpu)
        self.VAR = {}
        self.varid = 0

    # load the program into virtual memory (populate the mmap dict)
    def load_binary(self):
        p = self.bin
        if p!=None:
            # create text and data segments according to elf header:
            for s in p.Phdr:
                ms = p.loadsegment(s,PAGESIZE)
                if ms!=None:
                    vaddr,data = list(ms.items())[0]
                    self.mmap.write(vaddr,data)
        # create stack:
        self.mmap.newzone(cpu.stack_elt)

    def initenv(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        m.setmemory(self.mmap)
        m[cpu.stack_elt] = cst(0,6)
        return m

    def relocate(self,vaddr):
        from amoco.cas.mapper import mapper
        m = mapper()
        mz = self.mmap._zones[None]
        for z in mz._map: z.vaddr += vaddr
        # force mmap cache update:
        self.mmap.restruct()
        # create _initmap with new pc as vaddr:
        pc = self.cpu.opt_ptr
        m[pc] = self.cpu.cst(vaddr,pc.size)
        self._initmap = m

    def setstack(self,*args):
        m0 = mapper()
        m0.setmemory(self.mmap)
        m0[self.cpu.stack_elt] = cst(0,6)
        for x in args:
            if isinstance(x,str):
                x = reg(x,64)
            elif isinstance(x,int):
                x = cst(x,64)
            self.cpu._push_(m0,x)
        return m0

    def printstack(self,m,ssa=False):
       n = m[self.cpu.stack_elt]
       for x in reversed(range(n)):
           v = m(self.cpu.mem(self.cpu.sp+8*x,64))
           if ssa and complexity(v)>10:
               self.VAR['v%d'%self.varid] = v
               m[self.cpu.mem(self.cpu.sp+8*x,64)] = v = self.cpu.reg('v%d'%self.varid,64)
               self.varid += 1
           print("% 2d: %s"%(x,v.pp()))

    def setvar(m,idx,name):
        x = m(self.cpu.mem(self.cpu.sp+idx*8,64))
        self.VAR[name] = x
        m[self.cpu.mem(self.cpu.sp+idx*8,64)] = self.cpu.reg(name,64)
        self.printstack(m)
