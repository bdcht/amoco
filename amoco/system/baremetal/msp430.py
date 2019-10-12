# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import *

from amoco.arch.msp430 import cpu

#----------------------------------------------------------------------------

class MSP430(CoreExec):

    def __init__(self,p):
        CoreExec.__init__(self,p,cpu)
        self.load_binary()

    # load the program into virtual memory (populate the mmap dict)
    def load_binary(self):
        # use 32K RAM
        self.state.mmap.write(0x0200,b'\0'*0x8000)
        self.state.mmap.write(0x4400,self.bin)
        for r in self.cpu.R: self.state[r] = self.cpu.cst(0,16)
        self.state[self.cpu.pc] = self.cpu.cst(0x4400,16)

    # optional codehelper method allows platform-specific analysis of
    # either a (raw) list of instruction, a block/func object (see amoco.code)
    # the default helper is a no-op:
    def codehelper(self,seq=None,block=None,func=None):
        if seq is not None: return seq
        if block is not None: return block
        if func is not None: return func

