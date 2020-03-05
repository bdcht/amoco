# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import CoreExec
import amoco.arch.superh.cpu_sh2 as cpu

HIGH_SPEED_PAGE = 0x4000

class SH726B(CoreExec):

    def __init__(self,p):
        CoreExec.__init__(self,p,cpu)
        self.load_binary()

    # load the program into internal RAM (populate the mmap dict)
    def load_binary(self):
        p = self.bin
        if p is None: return
        p.seek(0)
        self.state.mmap.write(0xFFF80000,p.read(0x2000))
        # create the stack zone:
        self.state.mmap.newzone(0xFFF90000-0x10000,'\0'*0x10000)
        for r in cpu.R:
            self.state[r] = p.cpu.cst(0,32)
        self.state[cpu.pc]     = p.cpu.cst(0xFFF80000,32)
        self.state[cpu.sp]     = p.cpu.cst(0xFFF90000,32)
        self.state[cpu.SR]     = p.cpu.cst(0,32)
        self.state[cpu.IMASK]  = p.cpu.cst(0xF,4)
        self.state[cpu.VBR]    = p.cpu.cst(0,32)
        self.state[cpu.FPSCR]  = p.cpu.cst(0,32)
        self.state[cpu.DN]     = p.cpu.bit1
        self.state[cpu.RM]     = p.cpu.cst(1,2)
        self.state[cpu.IBCR]   = p.cpu.cst(0,16)
        self.state[cpu.IBNR]   = p.cpu.cst(0,16)

