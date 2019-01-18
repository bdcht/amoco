# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2017 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.raw import RawExec
from amoco.system.core import CoreExec,stub
from amoco.code import tag
from amoco.arch.eBPF import cpu_bpf as cpu

class BPF(RawExec):
    "This class allows to analyze old bpf bytecodes"

    def __init__(self,p):
        RawExec.__init__(self,p,cpu)

    def initenv(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        m[cpu.pc] = cpu.cst(0,64)
        return m

    def load_binary(self):
        'load the program into virtual memory (populate the mmap dict)'
        p = self.bin
        if p!=None:
            self.mmap.write(0,p.read())
        self.mmap.newzone(cpu.reg('#skb',64))


    def seqhelper(self,seq):
        'seqhelper provides arch-dependent information to amoco.main classes'
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

from linux_x64 import IDT
