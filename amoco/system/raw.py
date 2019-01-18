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
        if cpu is None:
            logger.warning('a cpu module must be imported')

    # load the program into virtual memory (populate the mmap dict)
    def load_binary(self):
        p = self.bin
        if p!=None:
            try:
                p.load_binary(self.mmap)
            except AttributeError:
                self.mmap.write(0,p.read())

    def use_x86(self):
        from amoco.arch.x86 import cpu_x86
        self.cpu = cpu_x86

    def use_x64(self):
        from amoco.arch.x64 import cpu_x64
        self.cpu = cpu_x64

    def use_arm(self):
        from amoco.arch.arm import cpu_armv7
        self.cpu = cpu_armv7

    def use_avr(self):
        from amoco.arch.avr import cpu
        self.cpu = cpu

    def initenv(self):
        try:
            return self._initmap
        except AttributeError:
            return CoreExec.initenv()

    def relocate(self,vaddr):
        from amoco.cas.mapper import mapper
        m = mapper()
        mz = self.mmap._zones[None]
        for z in mz._map: z.vaddr += vaddr
        # force mmap cache update:
        self.mmap.restruct()
        # create _initmap with new pc as vaddr:
        pc = self.cpu.PC()
        m[pc] = self.cpu.cst(vaddr,pc.size)
        self._initmap = m


