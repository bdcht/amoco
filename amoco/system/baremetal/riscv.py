# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.elf import *
from amoco.system.core import CoreExec, DefineStub
from amoco.code import tag
import amoco.arch.riscv.cpu_rv32i as cpu

# TODO implement OS and Task classes in remplacement of ELF CoreExec.

class ELF(CoreExec):
    PAGESIZE = 4096

    def __init__(self, p):
        CoreExec.__init__(self, p, cpu)
        self.load_binary()

    # load the program into virtual memory (populate the mmap dict)
    def load_binary(self):
        p = self.bin
        if p != None:
            # create text and data segments according to elf header:
            for s in p.Phdr:
                if s.p_type == PT_INTERP:
                    interp = p.readsegment(s).strip(b"\0")
                elif s.p_type == PT_LOAD:
                    ms = p.loadsegment(s, self.PAGESIZE)
                    if ms != None:
                        vaddr, data = ms.popitem()
                        self.state.mmap.write(vaddr, data)
        # create the stack zone:
        self.state.mmap.newzone(cpu.sp)
        self.state[cpu.pc] = cpu.cst(self.bin.entrypoints[0], 32)
        for r in cpu.x[1:]:
            self.state[r] = cpu.cst(0, 32)

    # seqhelper provides arch-dependent information to amoco.main classes
    def seqhelper(self, seq):
        for i in seq:
            if i.mnemonic in ("JAL", "JALR"):
                if i.operands[1] == cpu.ra:
                    i.misc[tag.FUNC_END] = 1
                elif i.operands[0] == cpu.ra:
                    i.misc[tag.FUNC_CALL] = 1
                    i.misc["retto"] = i.address + i.length
            # check operands (globals & .got calls):
            for op in i.operands:
                if op._is_mem:
                    if op.a.base is cpu.sp:
                        if op.a.disp < 0:
                            i.misc[tag.FUNC_VAR] = True
                        elif op.a.disp >= 4:
                            i.misc[tag.FUNC_ARG] = True
                    elif op.a.base._is_cst:
                        x = self.check_sym(op.a.base + op.a.disp)
                        if x is not None:
                            op.a.base = x
                            op.a.disp = 0
                elif op._is_cst:
                    x = self.check_sym(op)
                    i.misc["imm_ref"] = x
        return seq

    def blockhelper(self, block):
        block._helper = block_helper_
        return CoreExec.blockhelper(self, block)

    def funchelper(self, f):
        return f


# ----------------------------------------------------------------------------
# the block helper that will be called
# only when the map is computed.
def block_helper_(block, m):
    # update block.misc based on semantics:
    sta, sto = block.support
    if m[cpu.pc] == cpu.mem(cpu.sp - 4, 32):
        block.misc[tag.FUNC_END] = 1
    if m[cpu.mem(cpu.sp, 32)] == sto:
        block.misc[tag.FUNC_CALL] = 1


# HOOKS DEFINED HERE :
# ----------------------------------------------------------------------------

#@DefineStub('*',default=True)
#def pop_pc(m,**kargs):
#   cpu.pop(m,cpu.pc)
