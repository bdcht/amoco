# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.elf import *
from amoco.system.core import CoreExec, DefineStub
from amoco.code import tag
from amoco.arch.sparc import cpu_v8 as cpu

# legal values for e_version (version):
with Consts("e_flags"):
    EF_CPU32 = 0x00810000
    EF_SPARCV9_MM = 3
    EF_SPARCV9_TSO = 0
    EF_SPARCV9_PSO = 1
    EF_SPARCV9_RMO = 2
    EF_SPARC_LEDATA = 0x800000  # little endian data
    EF_SPARC_EXT_MASK = 0xFFFF00
    EF_SPARC_32PLUS = 0x000100  # generic V8+ features
    EF_SPARC_SUN_US1 = 0x000200  # Sun UltraSPARC1 extensions
    EF_SPARC_HAL_R1 = 0x000400  # HAL R1 extensions
    EF_SPARC_SUN_US3 = 0x000800  # Sun UltraSPARCIII ex

with Consts("r_type"):
    R_SPARC_8 = 0x1
    R_SPARC_NONE = 0x0
    R_SPARC_TLS_LDM_ADD = 0x3E
    R_SPARC_GLOB_DAT = 0x14
    R_SPARC_GLOB_JMP = 0x2A
    R_SPARC_LOPLT10 = 0x1A
    R_SPARC_UA32 = 0x17
    R_SPARC_SIZE64 = 0x57
    R_SPARC_TLS_DTPOFF64 = 0x4D
    R_SPARC_HIPLT22 = 0x19
    R_SPARC_TLS_IE_LDX = 0x46
    R_SPARC_GNU_VTINHERIT = 0xFA
    R_SPARC_PCPLT22 = 0x1C
    R_SPARC_13 = 0xB
    R_SPARC_TLS_IE_ADD = 0x47
    R_SPARC_DISP8 = 0x4
    R_SPARC_TLS_DTPMOD64 = 0x4B
    R_SPARC_NUM = 0xFD
    R_SPARC_GOTDATA_HIX22 = 0x50
    R_SPARC_TLS_GD_HI22 = 0x38
    R_SPARC_REV32 = 0xFC
    R_SPARC_COPY = 0x13
    R_SPARC_6 = 0x2D
    R_SPARC_TLS_LDO_LOX10 = 0x41
    R_SPARC_TLS_LDO_HIX22 = 0x40
    R_SPARC_HH22 = 0x22
    R_SPARC_DISP16 = 0x5
    R_SPARC_PCPLT32 = 0x1B
    R_SPARC_TLS_LDM_CALL = 0x3F
    R_SPARC_TLS_TPOFF64 = 0x4F
    R_SPARC_H44 = 0x32
    R_SPARC_PC_HM10 = 0x26
    R_SPARC_TLS_TPOFF32 = 0x4E
    R_SPARC_PC10 = 0x10
    R_SPARC_GOT10 = 0xD
    R_SPARC_M44 = 0x33
    R_SPARC_PC22 = 0x11
    R_SPARC_HI22 = 0x9
    R_SPARC_LOX10 = 0x31
    R_SPARC_HM10 = 0x23
    R_SPARC_PLT32 = 0x18
    R_SPARC_HIX22 = 0x30
    R_SPARC_TLS_GD_CALL = 0x3B
    R_SPARC_TLS_IE_HI22 = 0x43
    R_SPARC_GNU_VTENTRY = 0xFB
    R_SPARC_LO10 = 0xC
    R_SPARC_LM22 = 0x24
    R_SPARC_L44 = 0x34
    R_SPARC_TLS_GD_LO10 = 0x39
    R_SPARC_GOT22 = 0xF
    R_SPARC_TLS_IE_LD = 0x45
    R_SPARC_GOT13 = 0xE
    R_SPARC_PC_LM22 = 0x27
    R_SPARC_TLS_LDM_HI22 = 0x3C
    R_SPARC_DISP64 = 0x2E
    R_SPARC_TLS_GD_ADD = 0x3A
    R_SPARC_JMP_IREL = 0xF8
    R_SPARC_TLS_LDO_ADD = 0x42
    R_SPARC_IRELATIVE = 0xF9
    R_SPARC_UA64 = 0x36
    R_SPARC_WDISP22 = 0x8
    R_SPARC_WDISP10 = 0x58
    R_SPARC_WPLT30 = 0x12
    R_SPARC_7 = 0x2B
    R_SPARC_WDISP19 = 0x29
    R_SPARC_TLS_DTPOFF32 = 0x4C
    R_SPARC_16 = 0x2
    R_SPARC_TLS_LE_HIX22 = 0x48
    R_SPARC_OLO10 = 0x21
    R_SPARC_TLS_LDM_LO10 = 0x3D
    R_SPARC_11 = 0x1F
    R_SPARC_22 = 0xA
    R_SPARC_JMP_SLOT = 0x15
    R_SPARC_PLT64 = 0x2F
    R_SPARC_SIZE32 = 0x56
    R_SPARC_WDISP30 = 0x7
    R_SPARC_GOTDATA_OP = 0x54
    R_SPARC_RELATIVE = 0x16
    R_SPARC_TLS_IE_LO10 = 0x44
    R_SPARC_PCPLT10 = 0x1D
    R_SPARC_H34 = 0x55
    R_SPARC_TLS_LE_LOX10 = 0x49
    R_SPARC_DISP32 = 0x6
    R_SPARC_UA16 = 0x37
    R_SPARC_GOTDATA_LOX10 = 0x51
    R_SPARC_GOTDATA_OP_LOX10 = 0x53
    R_SPARC_5 = 0x2C
    R_SPARC_PC_HH22 = 0x25
    R_SPARC_10 = 0x1E
    R_SPARC_REGISTER = 0x35
    R_SPARC_TLS_DTPMOD32 = 0x4A
    R_SPARC_WDISP16 = 0x28
    R_SPARC_64 = 0x20
    R_SPARC_GOTDATA_OP_HIX22 = 0x52
    R_SPARC_32 = 0x3


# ------------------------------------------------------------------------------


class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of linux32.sparc, the OS class will stub all libc
    functions including a simulated heap memory allocator API.
    """

    stubs = {}
    default_stub = DefineStub.warning

    def __init__(self, conf=None):
        if conf is None:
            from amoco.config import System

            conf = System()
        self.PAGESIZE = conf.pagesize
        self.ASLR = conf.aslr
        self.NX = conf.nx
        from .abi import cdecl

        self.abi = cdecl
        self.tasks = []
        self.symbols = {}

    @classmethod
    def loader(cls, bprm, conf=None):
        return cls(conf).load_elf_binary(bprm)

    def load_elf_binary(self, bprm):
        "load the program into virtual memory (populate the mmap dict)"
        p = Task(bprm, cpu)
        p.OS = self
        # create text and data segments according to elf header:
        for s in bprm.Phdr:
            if s.p_type == PT_INTERP:
                interp = bprm.readsegment(s).strip(b"\0")
            elif s.p_type == PT_LOAD:
                ms = bprm.loadsegment(s, self.PAGESIZE)
                if ms != None:
                    vaddr, data = ms.popitem()
                    p.state.mmap.write(vaddr, data)
            elif s.p_type == PT_GNU_STACK:
                # executable_stack = s.p_flags & PF_X
                pass
        # init task state registers:
        e = p.bin.entrypoints[0]
        p.state[cpu.pc] = cpu.cst(e, 32)
        p.state[cpu.npc] = cpu.cst(e+4,32)
        for r in cpu.r:
            p.state[r] = cpu.cst(0,r.size)
        # create the stack space:
        if self.ASLR:
            p.state.mmap.newzone(p.cpu.esp)
        else:
            stack_base = 0x7FFFFFFF & ~(self.PAGESIZE - 1)
            stack_size = 2 * self.PAGESIZE
            p.state.mmap.write(stack_base - stack_size, b"\0" * stack_size)
            p.state[cpu.sp] = cpu.cst(stack_base, 32)
            p.state[cpu.fp] = cpu.cst(stack_base, 32)
        # create the dynamic segments:
        if bprm.dynamic and interp:
            self.load_elf_interp(p)
        # start task:
        self.tasks.append(p)
        return p

    def load_elf_interp(self, p):
        for k, f in p.bin._Elf__dynamic(None).items():
            xf = cpu.ext(f, size=32)
            xf.stub = self.stub(xf.ref)
            p.state.mmap.write(k, xf)
        # we want to add .plt addresses as symbols as well
        # to improve asm block views:
        plt = got = None
        for s in p.bin.Shdr:
            if s.name=='.plt':
                plt = s
            elif s.name=='.got':
                got = s
        if plt and got:
            address = plt.sh_addr
            pltco = p.bin.readsection(plt)
            while(pltco):
                i = p.cpu.disassemble(pltco)
                #TODO update to match plt structure for sparc
                if i.mnemonic=='jmpl' and i.operands[0]._is_mem:
                    target = i.operands[0].a
                    if target.base is p.cpu.pc:
                        target = address+target.disp
                    elif target.base._is_reg:
                        target = got.sh_addr+target.disp
                    elif target.base._is_cst:
                        target = target.base.value+target.disp
                    if target in p.bin.functions:
                        p.bin.functions[address] = p.bin.functions[target]
                pltco = pltco[i.length:]
                address += i.length

    def stub(self, refname):
        return self.stubs.get(refname, self.default_stub)


# ------------------------------------------------------------------------------


class Task(CoreExec):
    pass


# ----------------------------------------------------------------------------


@DefineStub(OS, "*", default=True)
def pop_pc(m, **kargs):
    cpu.pop(m, cpu.pc)
    m[cpu.npc] = m(cpu.pc)+4


@DefineStub(OS, "__libc_start_main")
def libc_start_main(m, **kargs):
    "tags: func_call"
    m[cpu.pc] = m(cpu.mem(cpu.sp + 4, 32))
    m[cpu.npc] = m(cpu.pc)+4
    cpu.push(m, cpu.ext("exit", size=32))


@DefineStub(OS, "exit")
def libc_exit(m, **kargs):
    m[cpu.pc] = top(32)


@DefineStub(OS, "abort")
def libc_abort(m, **kargs):
    m[cpu.pc] = top(32)


@DefineStub(OS, "__assert")
def libc_assert(m, **kargs):
    m[cpu.pc] = top(32)


@DefineStub(OS, "__assert_fail")
def libc_assert_fail(m, **kargs):
    m[cpu.pc] = top(32)


@DefineStub(OS, "_assert_perror_fail")
def _assert_perror_fail(m, **kargs):
    m[cpu.pc] = top(32)


# ----------------------------------------------------------------------------
