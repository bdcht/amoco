# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.elf import *
from amoco.system.core import CoreExec
import amoco.arch.superh.cpu_sh2 as cpu

with Consts('e_flags'):
    EF_SH2E = 0xb
    EF_SH2A = 0xd
    EF_SH_MACH_MASK = 0x1f
    EF_SH2A_SH3E = 0x18
    EF_SH3E = 0x8
    EF_SH_DSP = 0x4
    EF_SH4AL_DSP = 0x6
    EF_SH4A = 0xc
    EF_SH2A_SH3_NOFPU = 0x16
    EF_SH4A_NOFPU = 0x11
    EF_SH3_DSP = 0x5
    EF_SH2A_NOFPU = 0x13
    EF_SH_UNKNOWN = 0x0
    EF_SH2A_SH4_NOFPU = 0x15
    EF_SH2 = 0x2
    EF_SH4_NOMMU_NOFPU = 0x12
    EF_SH1 = 0x1
    EF_SH3_NOMMU = 0x14
    EF_SH2A_SH4 = 0x17
    EF_SH3 = 0x3
    EF_SH4 = 0x9
    EF_SH4_NOFPU = 0x10

with Consts('r_type'):
    R_SH_PLT32 = 0xa1
    R_SH_NUM = 0x100
    R_SH_TLS_IE_32 = 0x93
    R_SH_JMP_SLOT = 0xa4
    R_SH_DIR8WPL = 0x5
    R_SH_GOTOFF = 0xa6
    R_SH_GNU_VTENTRY = 0x23
    R_SH_DIR8WPZ = 0x6
    R_SH_TLS_LE_32 = 0x94
    R_SH_GLOB_DAT = 0xa3
    R_SH_USES = 0x1b
    R_SH_SWITCH16 = 0x19
    R_SH_LABEL = 0x20
    R_SH_TLS_LDO_32 = 0x92
    R_SH_SWITCH32 = 0x1a
    R_SH_COPY = 0xa2
    R_SH_TLS_LD_32 = 0x91
    R_SH_NONE = 0x0
    R_SH_DIR8W = 0x8
    R_SH_DIR32 = 0x1
    R_SH_SWITCH8 = 0x21
    R_SH_DATA = 0x1f
    R_SH_DIR8WPN = 0x3
    R_SH_TLS_TPOFF32 = 0x97
    R_SH_GNU_VTINHERIT = 0x22
    R_SH_IND12W = 0x4
    R_SH_TLS_DTPOFF32 = 0x96
    R_SH_CODE = 0x1e
    R_SH_GOT32 = 0xa0
    R_SH_GOTPC = 0xa7
    R_SH_ALIGN = 0x1d
    R_SH_DIR8BP = 0x7
    R_SH_TLS_DTPMOD32 = 0x95
    R_SH_REL32 = 0x2
    R_SH_RELATIVE = 0xa5
    R_SH_TLS_GD_32 = 0x90
    R_SH_COUNT = 0x1c
    R_SH_DIR8L = 0x9

#------------------------------------------------------------------------------

class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of linux32.x86, the OS class will stub all libc
    functions including a simulated heap memory allocator API.
    """
    stubs = {}
    default_stub = (lambda env,**kargs:None)

    def __init__(self,conf=None):
        if conf is None:
            from amoco.config import System
            conf = System()
        self.PAGESIZE = conf.pagesize
        self.ASLR     = conf.aslr
        self.NX       = conf.nx
        self.tasks = []

    @classmethod
    def loader(cls,bprm,conf=None):
        return cls(conf).load_elf_binary(bprm)

    def load_elf_binary(self,bprm):
        "load the program into virtual memory (populate the mmap dict)"
        p = Task(bprm,cpu)
        p.OS = self
        self.tasks.append(p)
        # create text and data segments according to elf header:
        for s in bprm.Phdr:
            if s.p_type == PT_INTERP:
                interp = bprm.readsegment(s).strip(b'\0')
            elif s.p_type == PT_LOAD:
                ms = bprm.loadsegment(s,self.PAGESIZE)
                if ms!=None:
                    vaddr,data = ms.popitem()
                    p.mmap.write(vaddr,data)
            elif s.p_type == PT_GNU_STACK:
                #executable_stack = s.p_flags & PF_X
                pass
        # init task state:
        p.state = p.initstate()
        for r in cpu.R: p.state[r] = cpu.cst(0,32)
        p.state[cpu.SR] = cpu.cst(0,32)
        p.state[cpu.PC] = cpu.cst(p.bin.entrypoints[0],32)
        # create the stack space:
        if self.ASLR:
            p.mmap.newzone(p.cpu.esp)
        else:
            stack_base = 0x7fffffff & ~(self.PAGESIZE-1)
            stack_size = 2*self.PAGESIZE
            p.mmap.write(stack_base-stack_size,b'\0'*stack_size)
            p.state[cpu.sp] = cpu.cst(stack_base,32)
        # create the dynamic segments:
        if bprm.dynamic and interp:
            self.load_elf_interp(p,interp)
        # start task:
        return p

    def load_elf_interp(self,p,interp):
        for k,f in p.bin._Elf__dynamic(None).items():
            xf= cpu.ext(f,size=32)
            xf.stub = p.OS.stub(f)
            p.mmap.write(k,xf)

    def stub(self,refname):
        return self.stubs.get(refname,self.default_stub)


class Task(CoreExec):
    pass
