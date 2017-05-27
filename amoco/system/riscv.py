# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import *
from amoco.code import tag,xfunc

import amoco.arch.riscv.cpu_rvi32 as cpu

PAGESIZE = 4096

class ELF(CoreExec):

    def __init__(self,p):
        CoreExec.__init__(self,p,cpu)
        if self.bin:
            self.symbols.update(self.bin.functions)
            self.symbols.update(self.bin.variables)

    # load the program into virtual memory (populate the mmap dict)
    def load_binary(self):
        p = self.bin
        if p!=None:
            # create text and data segments according to elf header:
            for s in p.Phdr:
                ms = p.loadsegment(s,PAGESIZE)
                if ms!=None:
                    vaddr,data = ms.popitem()
                    self.mmap.write(vaddr,data)
            # create the dynamic segments:
            self.load_shlib()
        # create the stack zone:
        self.mmap.newzone(cpu.sp)

    # call dynamic linker to populate mmap with shared libs:
    # for now, the external libs are seen through the elf dynamic section:
    def load_shlib(self):
        for k,f in self.bin._Elf32__dynamic(None).items():
            self.mmap.write(k,cpu.ext(f,size=32))

    def initenv(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        m[cpu.pc] = cpu.cst(self.bin.entrypoints[0],32)
        for r in cpu.x[1:] : m[r] = cpu.cst(0,32)
        return m

    # seqhelper provides arch-dependent information to amoco.main classes
    def seqhelper(self,seq):
        for i in seq:
            if i.mnemonic in ('JAL','JALR'):
                if i.operands[1]==cpu.ra:
                    i.misc[tag.FUNC_END]=1
                elif i.operands[0]==cpu.ra:
                    i.misc[tag.FUNC_CALL]=1
                    i.misc['retto'] = i.address+i.length
            # check operands (globals & .got calls):
            for op in i.operands:
                if op._is_mem:
                    if op.a.base is cpu.sp:
                        if   op.a.disp<0: i.misc[tag.FUNC_VAR]=True
                        elif op.a.disp>=4: i.misc[tag.FUNC_ARG]=True
                    elif op.a.base._is_cst:
                        x = self.check_sym(op.a.base+op.a.disp)
                        if x is not None:
                            op.a.base=x
                            op.a.disp=0
                elif op._is_cst:
                    x = self.check_sym(op)
                    i.misc['imm_ref'] = x
        return seq

    def blockhelper(self,block):
        block._helper = block_helper_
        return CoreExec.blockhelper(self,block)

    def funchelper(self,f):
        return f


#----------------------------------------------------------------------------
# the block helper that will be called
# only when the map is computed.
def block_helper_(block,m):
    # update block.misc based on semantics:
    sta,sto = block.support
    if m[cpu.pc]==cpu.mem(cpu.sp-4,32):
        block.misc[tag.FUNC_END]=1
    if m[cpu.mem(cpu.sp,32)]==sto:
        block.misc[tag.FUNC_CALL]=1

# HOOKS DEFINED HERE :
#----------------------------------------------------------------------------

@stub_default
def pop_pc(m,**kargs):
    cpu.pop(m,cpu.pc)

