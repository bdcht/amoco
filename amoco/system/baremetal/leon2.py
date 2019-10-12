# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import *
import amoco.arch.sparc.cpu_v8 as cpu

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
                  vaddr,data = list(ms.items())[0]
                  self.state.mmap.write(vaddr,data)
        # create the stack zone:
        self.state.mmap.newzone(cpu.sp)
        e = self.bin.entrypoints[0]
        for k,v in ((cpu.pc , cpu.cst(e,32)),
                    (cpu.npc, cpu.cst(e+4,32)),
                    (cpu.sp , cpu.cst(0xc0000000,32)),
                    (cpu.fp , cpu.cst(0xc0000000,32))):
            self.state[k] = v
