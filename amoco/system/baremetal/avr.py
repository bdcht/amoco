# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import CoreExec
from amoco.arch.avr import cpu

PAGESIZE = 4096

class ELF(CoreExec):

    def __init__(self,p):
        CoreExec.__init__(self,p,cpu)
        self.load_binary()

    # load the program into virtual memory (populate the mmap dict)
    def load_binary(self):
        p = self.bin
        if p!=None:
            # create text and data segments according to elf header:
            for s in p.Phdr:
                ms = p.loadsegment(s,PAGESIZE)
                if ms!=None:
                    vaddr,data = ms.popitem()
                    self.state.mmap.write(vaddr,data)
        # create the stack zone:
        self.state.mmap.newzone(cpu.sp)
        self.state[cpu.pc] = cpu.cst(self.bin.entrypoints[0],16)
        for r in cpu.R : self.state[r] = cpu.cst(0,8)
