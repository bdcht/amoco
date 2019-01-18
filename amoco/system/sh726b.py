# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import *
import amoco.arch.superh.cpu_sh2 as cpu

HIGH_SPEED_PAGE = 0x4000

class SH726B(CoreExec):

    def __init__(self,p):
        CoreExec.__init__(self,p,cpu)

    # load the program into internal RAM (populate the mmap dict)
    def load_binary(self):
        p = self.bin
        if p is None: return
        p.seek(0)
        self.mmap.write(0xFFF80000,p.read(0x2000))
        # create the stack zone:
        self.mmap.newzone(0xFFF90000-0x10000,'\0'*0x10000)

    def initenv(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        for r in cpu.R:
            m[r] = p.cpu.cst(0,32)
        m[cpu.pc]     = p.cpu.cst(0xFFF80000,32)
        m[cpu.sp]     = p.cpu.cst(0xFFF90000,32)
        m[cpu.SR]     = p.cpu.cst(0,32)
        m[cpu.IMASK]  = p.cpu.cst(0xF,4)
        m[cpu.VBR]    = p.cpu.cst(0,32)
        m[cpu.FPSCR]  = p.cpu.cst(0,32)
        m[cpu.DN]     = p.cpu.bit1
        m[cpu.RM]     = p.cpu.cst(1,2)
        m[cpu.IBCR]   = p.cpu.cst(0,16)
        m[cpu.IBNR]   = p.cpu.cst(0,16)
        return m

