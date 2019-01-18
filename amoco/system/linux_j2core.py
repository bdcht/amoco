# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import *
from amoco.code import tag,xfunc

import amoco.arch.superh.cpu_sh2 as cpu

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
        self.mmap.newzone(cpu.R[15])

    # call dynamic linker to populate mmap with shared libs:
    # for now, the external libs are seen through the elf dynamic section:
    def load_shlib(self):
        for k,f in self.bin._Elf32__dynamic(None).items():
            self.mmap.write(k,cpu.ext(f,size=32))

    def initenv(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        m[cpu.pc] = cpu.cst(self.bin.entrypoints[0],32)
        for r in cpu.R:
            m[r] = cpu.cst(0,32)
        return m
