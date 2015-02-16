# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.logger import Log
logger = Log(__name__)

from amoco.system.core import CoreExec

class RawExec(CoreExec):

    def __init__(self,p,cpu=None):
        CoreExec.__init__(self,p,cpu)
        if cpu is None: logger.warning('a cpu module must be imported')

    # load the program into virtual memory (populate the mmap dict)
    def load_binary(self):
        p = self.bin
        if p!=None:
            self.mmap.write(0,p.read())

    def use_x86(self):
        from amoco.arch.x86 import cpu_x86
        self.cpu = cpu_x86
        self.PC  = lambda :self.cpu.eip

    def relocate(self,vaddr):
        from amoco.cas.mapper import mapper
        m = mapper()
        mz = self.mmap._zones[None]
        for z in mz._map: z.vaddr += vaddr
        pc = self.PC()
        m[pc] = self.cpu.cst(vaddr,pc.size)
        self._initmap = m
        self.initenv = lambda : self._initmap
