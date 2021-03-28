# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.elf import *
from amoco.system.core import CoreExec
import amoco.arch.arm.cpu_armv8 as cpu

with Consts("r_type"):
    R_AARCH64_MOVW_GOTOFF_G0 = 0x12C
    R_AARCH64_CONDBR19 = 0x118
    R_AARCH64_TLSDESC_CALL = 0x239
    R_AARCH64_TLSLD_LDST32_DTPREL_LO12_NC = 0x218
    R_AARCH64_JUMP_SLOT = 0x402
    R_AARCH64_RELATIVE = 0x403
    R_AARCH64_NONE = 0x0
    R_AARCH64_LD64_GOTPAGE_LO15 = 0x139
    R_AARCH64_MOVW_PREL_G1 = 0x121
    R_AARCH64_LDST16_ABS_LO12_NC = 0x11C
    R_AARCH64_MOVW_UABS_G1_NC = 0x10A
    R_AARCH64_IRELATIVE = 0x408
    R_AARCH64_TLSLE_MOVW_TPREL_G1_NC = 0x222
    R_AARCH64_MOVW_SABS_G2 = 0x110
    R_AARCH64_MOVW_UABS_G0_NC = 0x108
    R_AARCH64_TLSLD_MOVW_G1 = 0x208
    R_AARCH64_ADR_PREL_PG_HI21 = 0x113
    R_AARCH64_MOVW_PREL_G2_NC = 0x124
    R_AARCH64_TLSDESC_LD64_LO12 = 0x233
    R_AARCH64_TLSGD_MOVW_G1 = 0x203
    R_AARCH64_TLSLD_MOVW_DTPREL_G1_NC = 0x20D
    R_AARCH64_COPY = 0x400
    R_AARCH64_P32_JUMP_SLOT = 0xB6
    R_AARCH64_ADR_PREL_LO21 = 0x112
    R_AARCH64_MOVW_SABS_G1 = 0x10F
    R_AARCH64_P32_TLS_TPREL = 0xBA
    R_AARCH64_TLSLE_MOVW_TPREL_G0 = 0x223
    R_AARCH64_P32_TLS_DTPMOD = 0xB8
    R_AARCH64_TLSLD_LDST8_DTPREL_LO12 = 0x213
    R_AARCH64_TLSLD_MOVW_DTPREL_G2 = 0x20B
    R_AARCH64_TLSLD_LDST8_DTPREL_LO12_NC = 0x214
    R_AARCH64_LD_PREL_LO19 = 0x111
    R_AARCH64_TLSLD_LDST128_DTPREL_LO12_NC = 0x23D
    R_AARCH64_PREL32 = 0x105
    R_AARCH64_TLSGD_ADD_LO12_NC = 0x202
    R_AARCH64_TLSLD_LDST32_DTPREL_LO12 = 0x217
    R_AARCH64_GLOB_DAT = 0x401
    R_AARCH64_MOVW_UABS_G3 = 0x10D
    R_AARCH64_ABS32 = 0x102
    R_AARCH64_TLSLD_MOVW_DTPREL_G1 = 0x20C
    R_AARCH64_P32_ABS32 = 0x1
    R_AARCH64_TLSIE_LD64_GOTTPREL_LO12_NC = 0x21E
    R_AARCH64_TLS_TPREL = 0x406
    R_AARCH64_TLSLE_ADD_TPREL_LO12_NC = 0x227
    R_AARCH64_MOVW_PREL_G1_NC = 0x122
    R_AARCH64_TLSIE_MOVW_GOTTPREL_G1 = 0x21B
    R_AARCH64_TLSDESC_ADR_PREL21 = 0x231
    R_AARCH64_TLSDESC = 0x407
    R_AARCH64_MOVW_UABS_G2_NC = 0x10C
    R_AARCH64_TLSLE_LDST64_TPREL_LO12_NC = 0x22F
    R_AARCH64_MOVW_PREL_G0_NC = 0x120
    R_AARCH64_TSTBR14 = 0x117
    R_AARCH64_P32_GLOB_DAT = 0xB5
    R_AARCH64_TLSLD_ADD_DTPREL_HI12 = 0x210
    R_AARCH64_TLSLD_MOVW_DTPREL_G0 = 0x20E
    R_AARCH64_TLSDESC_ADR_PAGE21 = 0x232
    R_AARCH64_TLSLE_LDST8_TPREL_LO12 = 0x228
    R_AARCH64_TLSDESC_LDR = 0x237
    R_AARCH64_TLSLD_ADR_PREL21 = 0x205
    R_AARCH64_TLSIE_ADR_GOTTPREL_PAGE21 = 0x21D
    R_AARCH64_TLSGD_MOVW_G0_NC = 0x204
    R_AARCH64_TLSLD_LDST64_DTPREL_LO12 = 0x219
    R_AARCH64_TLSDESC_ADD = 0x238
    R_AARCH64_PREL16 = 0x106
    R_AARCH64_TLSLD_ADD_DTPREL_LO12_NC = 0x212
    R_AARCH64_ADR_GOT_PAGE = 0x137
    R_AARCH64_MOVW_GOTOFF_G1_NC = 0x12F
    R_AARCH64_TLSLD_LDST128_DTPREL_LO12 = 0x23C
    R_AARCH64_TLSLE_LDST64_TPREL_LO12 = 0x22E
    R_AARCH64_LDST32_ABS_LO12_NC = 0x11D
    R_AARCH64_ABS64 = 0x101
    R_AARCH64_TLSDESC_ADD_LO12 = 0x234
    R_AARCH64_MOVW_PREL_G0 = 0x11F
    R_AARCH64_MOVW_GOTOFF_G2_NC = 0x131
    R_AARCH64_TLSLD_MOVW_G0_NC = 0x209
    R_AARCH64_LDST8_ABS_LO12_NC = 0x116
    R_AARCH64_TLSLD_LDST64_DTPREL_LO12_NC = 0x21A
    R_AARCH64_MOVW_UABS_G2 = 0x10B
    R_AARCH64_TLSLE_LDST32_TPREL_LO12_NC = 0x22D
    R_AARCH64_TLSLD_ADD_LO12_NC = 0x207
    R_AARCH64_TLSLD_LDST16_DTPREL_LO12_NC = 0x216
    R_AARCH64_TLSLD_ADR_PAGE21 = 0x206
    R_AARCH64_GOTREL64 = 0x133
    R_AARCH64_TLSLE_ADD_TPREL_LO12 = 0x226
    R_AARCH64_P32_TLSDESC = 0xBB
    R_AARCH64_MOVW_PREL_G3 = 0x125
    R_AARCH64_ABS16 = 0x103
    R_AARCH64_TLSLD_LD_PREL19 = 0x20A
    R_AARCH64_MOVW_UABS_G0 = 0x107
    R_AARCH64_PREL64 = 0x104
    R_AARCH64_TLSLE_LDST16_TPREL_LO12 = 0x22A
    R_AARCH64_CALL26 = 0x11B
    R_AARCH64_P32_COPY = 0xB4
    R_AARCH64_GOT_LD_PREL19 = 0x135
    R_AARCH64_TLSIE_MOVW_GOTTPREL_G0_NC = 0x21C
    R_AARCH64_TLSGD_ADR_PAGE21 = 0x201
    R_AARCH64_TLSIE_LD_GOTTPREL_PREL19 = 0x21F
    R_AARCH64_TLSLE_LDST128_TPREL_LO12_NC = 0x23B
    R_AARCH64_LDST128_ABS_LO12_NC = 0x12B
    R_AARCH64_GOTREL32 = 0x134
    R_AARCH64_TLSGD_ADR_PREL21 = 0x200
    R_AARCH64_JUMP26 = 0x11A
    R_AARCH64_MOVW_GOTOFF_G0_NC = 0x12D
    R_AARCH64_ADR_PREL_PG_HI21_NC = 0x114
    R_AARCH64_TLSLD_LDST16_DTPREL_LO12 = 0x215
    R_AARCH64_P32_TLS_DTPREL = 0xB9
    R_AARCH64_TLSLE_LDST32_TPREL_LO12 = 0x22C
    R_AARCH64_LD64_GOT_LO12_NC = 0x138
    R_AARCH64_TLSLE_ADD_TPREL_HI12 = 0x225
    R_AARCH64_P32_RELATIVE = 0xB7
    R_AARCH64_MOVW_GOTOFF_G2 = 0x130
    R_AARCH64_LD64_GOTOFF_LO15 = 0x136
    R_AARCH64_TLSLE_LDST8_TPREL_LO12_NC = 0x229
    R_AARCH64_TLSLE_LDST16_TPREL_LO12_NC = 0x22B
    R_AARCH64_TLSLE_MOVW_TPREL_G0_NC = 0x224
    R_AARCH64_MOVW_UABS_G1 = 0x109
    R_AARCH64_TLSLE_MOVW_TPREL_G1 = 0x221
    R_AARCH64_MOVW_GOTOFF_G1 = 0x12E
    R_AARCH64_TLSLE_MOVW_TPREL_G2 = 0x220
    R_AARCH64_TLSDESC_OFF_G0_NC = 0x236
    R_AARCH64_TLSDESC_LD_PREL19 = 0x230
    R_AARCH64_LDST64_ABS_LO12_NC = 0x11E
    R_AARCH64_ADD_ABS_LO12_NC = 0x115
    R_AARCH64_TLSDESC_OFF_G1 = 0x235
    R_AARCH64_MOVW_SABS_G0 = 0x10E
    R_AARCH64_TLSLE_LDST128_TPREL_LO12 = 0x23A
    R_AARCH64_MOVW_PREL_G2 = 0x123
    R_AARCH64_TLSLD_ADD_DTPREL_LO12 = 0x211
    R_AARCH64_P32_IRELATIVE = 0xBC
    R_AARCH64_MOVW_GOTOFF_G3 = 0x132
    R_AARCH64_TLS_DTPREL = 0x405
    R_AARCH64_TLS_DTPMOD = 0x404
    R_AARCH64_TLSLD_MOVW_DTPREL_G0_NC = 0x20F


class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of linux64.x64, the OS class will stub all libc
    functions including a simulated heap memory allocator API.
    """

    stubs = {}
    default_stub = lambda env, **kargs: None

    def __init__(self, conf=None):
        if conf is None:
            from amoco.config import System

            conf = System()
        self.PAGESIZE = conf.pagesize
        self.ASLR = conf.aslr
        self.NX = conf.nx
        self.tasks = []
        self.abi = None

    @classmethod
    def loader(cls, bprm, conf=None):
        return cls(conf).load_elf_binary(bprm)

    def load_elf_binary(self, bprm):
        "load the program into virtual memory (populate the mmap dict)"
        p = Task(bprm, cpu)
        p.OS = self
        self.tasks.append(p)
        # create text and data segments according to elf header:
        for s in bprm.Phdr:
            if s.p_type == PT_INTERP:
                interp = bprm.readsegment(s).strip(b"\0")
            elif s.p_type == PT_LOAD:
                ms = bprm.loadsegment(s, self.PAGESIZE)
                if ms != None:
                    vaddr, data = ms.popitem()
                    p.mmap.write(vaddr, data)
            elif s.p_type == PT_GNU_STACK:
                # executable_stack = s.p_flags & PF_X
                pass
        # init task state:
        p.state = p.initstate()
        p.state[cpu.pc] = cpu.cst(p.bin.entrypoints[0], 64)
        for r in cpu.Xregs:
            p.state[r] = cst(0, 64)
        p.state[cpu.pstate] = cst(0, 64)
        # create the stack space:
        if self.ASLR:
            p.mmap.newzone(p.cpu.rsp)
        else:
            stack_base = 0x00007FFFFFFFFFFF & ~(self.PAGESIZE - 1)
            stack_size = 2 * self.PAGESIZE
            p.mmap.write(stack_base - stack_size, b"\0" * stack_size)
            p.state[cpu.sp] = cpu.cst(stack_base, 64)
        # create the dynamic segments:
        if bprm.dynamic and interp:
            self.load_elf_interp(p, interp)
        # return task:
        return p

    def load_elf_interp(self, p, interp):
        for k, f in p.bin._Elf__dynamic(None).items():
            xfunc = cpu.ext(f, size=64)
            xfunc.stub = p.OS.stub(f)
            p.mmap.write(k, xfunc)

    def stub(self, refname):
        return self.stubs.get(refname, self.default_stub)


class Task(CoreExec):
    pass


from amoco.system.core import DefineStub


@DefineStub(OS, "*", default=True)
def pop_rip(m, **kargs):
    cpu.pop(m, cpu.pc)


@DefineStub(OS, "__libc_start_main")
def libc_start_main(m, **kargs):
    "tags: func_call"
    m[cpu.pc] = m(cpu.r0)


@DefineStub(OS, "exit")
def libc_exit(m, **kargs):
    m[cpu.pc] = top(64)


@DefineStub(OS, "abort")
def libc_abort(m, **kargs):
    m[cpu.pc] = top(64)


@DefineStub(OS, "__assert")
def libc_assert(m, **kargs):
    m[cpu.pc] = top(64)


@DefineStub(OS, "__assert_fail")
def libc_assert_fail(m, **kargs):
    m[cpu.pc] = top(64)


@DefineStub(OS, "_assert_perror_fail")
def _assert_perror_fail(m, **kargs):
    m[cpu.pc] = top(64)
