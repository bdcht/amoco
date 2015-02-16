# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import *
import amoco.arch.arm.cpu_armv8 as cpu

PAGESIZE = 4096

class ELF(CoreExec):
    def __init__(self,p):
        CoreExec.__init__(self,p,cpu)

    # load the program into virtual memory (populate the mmap dict)
    def load_binary(self):
        p = self.bin
        if p!=None:
            # create text and data segments according to elf header:
            for s in p.Phdr:
                ms = p.loadsegment(s,PAGESIZE)
                if ms!=None:
                    vaddr,data = ms.items()[0]
                    self.mmap.write(vaddr,data)
            # create the dynamic segments:
            self.load_shlib()
        # create the stack zone:
        self.mmap.newzone(cpu.sp)

    # call dynamic linker to populate mmap with shared libs:
    # for now, the external libs are seen through the elf dynamic section:
    def load_shlib(self):
        for k,f in self.bin._Elf64__dynamic(None).iteritems():
            self.mmap.write(k,cpu.ext(f))

    def initenv(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        for k,v in ((cpu.pc, cpu.cst(self.bin.entrypoints[0],64)),
                   ):
            m[k] = v
        return m

    def PC(self):
        return self.cpu.pc

# LIBC HOOKS DEFINED HERE :
#----------------------------------------------------------------------------
@stub
def __libc_start_main(m):
    m[cpu.pc] = m(cpu.mem(cpu.sp+8,64))

@stub
def exit(m):
    m[cpu.pc] = cpu.top(64)

@stub
def abort(m):
    m[cpu.pc] = cpu.top(64)

@stub
def __assert(m):
    m[cpu.pc] = cpu.top(64)

@stub
def __assert_fail(m):
    m[cpu.pc] = cpu.top(64)

@stub
def _assert_perror_fail(m):
    m[cpu.pc] = cpu.top(64)
#----------------------------------------------------------------------------

