#!/usr/bin/env python

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

from amoco.system.core import *

from amoco.arch.msp430 import cpu

#----------------------------------------------------------------------------

class MSP430(CoreExec):

    def __init__(self,p):
        CoreExec.__init__(self,p,cpu)

    # load the program into virtual memory (populate the mmap dict)
    def load_binary(self):
        # use 32K RAM
        self.mmap.write(0x0200,'\0'*0x8000)
        self.mmap.write(0x4400,self.bin)

    def initenv(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        for r in self.cpu.R: m[r] = self.cpu.cst(0,16)
        m[self.cpu.pc] = self.cpu.cst(0x4400,16)
        return m

    def PC(self):
        return self.cpu.pc

    # optional codehelper method allows platform-specific analysis of
    # either a (raw) list of instruction, a block/func object (see amoco.code)
    # the default helper is a no-op:
    def codehelper(self,seq=None,block=None,func=None):
        if seq is not None: return seq
        if block is not None: return block
        if func is not None: return func

