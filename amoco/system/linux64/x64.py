# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.elf import *
from amoco.system.core import CoreExec
from amoco.code import tag
import amoco.arch.x64.cpu_x64 as cpu

#AMD 64 specific definitions. #x86_64 relocs.
with Consts('r_type'):
    R_X86_64_PLTOFF64 = 0x1f
    R_X86_64_GOTPCREL64 = 0x1c
    R_X86_64_GOTOFF64 = 0x19
    R_X86_64_TPOFF64 = 0x12
    R_X86_64_GOT32 = 0x3
    R_X86_64_32 = 0xa
    R_X86_64_DTPOFF64 = 0x11
    R_X86_64_PC32 = 0x2
    R_X86_64_16 = 0xc
    R_X86_64_32S = 0xb
    R_X86_64_TPOFF32 = 0x17
    R_X86_64_64 = 0x1
    R_X86_64_GOTPCREL = 0x9
    R_X86_64_TLSDESC = 0x24
    R_X86_64_TLSGD = 0x13
    R_X86_64_GOTPC32 = 0x1a
    R_X86_64_PC8 = 0xf
    R_X86_64_DTPOFF32 = 0x15
    R_X86_64_PLT32 = 0x4
    R_X86_64_8 = 0xe
    R_X86_64_GOTPC32_TLSDESC = 0x22
    R_X86_64_IRELATIVE = 0x25
    R_X86_64_PC16 = 0xd
    R_X86_64_COPY = 0x5
    R_X86_64_GLOB_DAT = 0x6
    R_X86_64_GOT64 = 0x1b
    R_X86_64_SIZE32 = 0x20
    R_X86_64_TLSLD = 0x14
    R_X86_64_JUMP_SLOT = 0x7
    R_X86_64_TLSDESC_CALL = 0x23
    R_X86_64_GOTTPOFF = 0x16
    R_X86_64_NUM = 0x27
    R_X86_64_SIZE64 = 0x21
    R_X86_64_GOTPC64 = 0x1d
    R_X86_64_PC64 = 0x18
    R_X86_64_RELATIVE64 = 0x26
    R_X86_64_RELATIVE = 0x8
    R_X86_64_NONE = 0x0
    R_X86_64_DTPMOD64 = 0x10
    R_X86_64_GOTPLT64 = 0x1e

#------------------------------------------------------------------------------

class OS(object):
    """OS class is a provider for all the environment in which a Task runs.
    It is responsible for setting up the (virtual) memory of the Task as well
    as providing stubs for dynamic library calls and possibly system calls.

    In the specific case of linux64.x64, the OS class will stub all libc
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
        self.abi = None

    @classmethod
    def loader(cls,bprm,conf=None):
        return cls(conf).load_elf_binary(bprm)

    def load_elf_binary(self,bprm):
        "load the program into virtual memory (populate the mmap dict)"
        p = Task(bprm,cpu)
        p.OS = self
        # create text and data segments according to elf header:
        for s in bprm.Phdr:
            if s.p_type == PT_INTERP:
                interp = bprm.readsegment(s).strip(b'\0')
            elif s.p_type == PT_LOAD:
                ms = bprm.loadsegment(s,self.PAGESIZE)
                if ms!=None:
                    vaddr,data = ms.popitem()
                    p.state.mmap.write(vaddr,data)
            elif s.p_type == PT_GNU_STACK:
                #executable_stack = s.p_flags & PF_X
                pass
        # init task state:
        p.state[cpu.rip] = cpu.cst(p.bin.entrypoints[0],64)
        p.state[cpu.rbp] = cpu.cst(0,64)
        p.state[cpu.rax] = cpu.cst(0,64)
        p.state[cpu.rbx] = cpu.cst(0,64)
        p.state[cpu.rcx] = cpu.cst(0,64)
        p.state[cpu.rdx] = cpu.cst(0,64)
        p.state[cpu.rsi] = cpu.cst(0,64)
        p.state[cpu.rdi] = cpu.cst(0,64)
        p.state[cpu.r8]  = cpu.cst(0,64)
        p.state[cpu.r9]  = cpu.cst(0,64)
        p.state[cpu.r10] = cpu.cst(0,64)
        p.state[cpu.r11] = cpu.cst(0,64)
        p.state[cpu.r12] = cpu.cst(0,64)
        p.state[cpu.r13] = cpu.cst(0,64)
        p.state[cpu.r14] = cpu.cst(0,64)
        p.state[cpu.r15] = cpu.cst(0,64)
        p.state[cpu.rflags] = cpu.cst(0,64)
        # create the stack space:
        if self.ASLR:
            p.state.mmap.newzone(p.cpu.rsp)
        else:
            stack_base = (0x00007fffffffffff & ~(self.PAGESIZE-1))
            stack_size = 2*self.PAGESIZE
            p.state.mmap.write(stack_base-stack_size,b'\0'*stack_size)
            p.state[cpu.rsp] = cpu.cst(stack_base,64)
        # create the dynamic segments:
        if bprm.dynamic and interp:
            self.load_elf_interp(p,interp)
        # return task:
        self.tasks.append(p)
        return p

    def load_elf_interp(self,p,interp):
        for k,f in p.bin._Elf__dynamic(None).items():
            xfunc = cpu.ext(f,size=64)
            xfunc.stub = p.OS.stub(f)
            p.state.mmap.write(k,xfunc)

    def stub(self,refname):
        return self.stubs.get(refname,self.default_stub)


class Task(CoreExec):

    # seqhelper provides arch-dependent information to amoco.main classes
    def seqhelper(self,seq):
        for i in seq:
            # some basic hints:
            if i.mnemonic.startswith('RET'):
                i.misc[tag.FUNC_END]=1
                continue
            elif i.mnemonic in ('PUSH','ENTER'):
                i.misc[tag.FUNC_STACK]=1
                if i.operands and i.operands[0] is cpu.rbp:
                    i.misc[tag.FUNC_START]=1
                    continue
            elif i.mnemonic in ('POP','LEAVE'):
                i.misc[tag.FUNC_UNSTACK]=1
                if i.operands and i.operands[0] is cpu.rbp:
                    i.misc[tag.FUNC_END]=1
                    continue
            # provide hints of absolute location from relative offset:
            elif i.mnemonic in ('CALL','JMP','Jcc'):
                if i.mnemonic == 'CALL':
                    i.misc[tag.FUNC_CALL]=1
                    i.misc['retto'] = i.address+i.length
                else:
                    i.misc[tag.FUNC_GOTO]=1
                    if i.mnemonic == 'Jcc':
                        i.misc['cond'] = i.cond
                if (i.address is not None) and i.operands[0]._is_cst:
                    v = i.address+i.operands[0].signextend(64)+i.length
                    x = self.check_sym(v)
                    if x is not None: v=x
                    i.misc['to'] = v
                    if i.misc[tag.FUNC_CALL] and i.misc['retto']==v:
                        # this looks like a fake call
                        i.misc[tag.FUNC_CALL]=-1
                    continue
            # check operands (globals & .got calls):
            for op in i.operands:
                if op._is_mem:
                    if op.a.base is cpu.rbp:
                        if   op.a.disp<0: i.misc[tag.FUNC_VAR]=True
                        elif op.a.disp>=16: i.misc[tag.FUNC_ARG]=True
                    elif op.a.base._is_cst or (op.a.base is cpu.rip):
                        b = op.a.base
                        if b is cpu.rip: b=i.address+i.length
                        x = self.check_sym(b+op.a.disp)
                        if x is not None:
                            op.a.base=x
                            op.a.disp=0
                            if i.mnemonic == 'JMP': # PLT jumps:
                                i.misc[tag.FUNC_START]=1
                                i.misc[tag.FUNC_END]=1
                elif op._is_cst:
                    x = self.check_sym(op)
                    i.misc['imm_ref'] = x
        return seq

    def blockhelper(self,block):
        block._helper = block_helper_
        return CoreExec.blockhelper(self,block)

    def funchelper(self,f):
        # check single root node:
        roots = f.cfg.roots()
        if len(roots)==0:
            roots = filter(lambda n:n.data.misc[tag.FUNC_START],f.cfg.sV)
            if len(roots)==0:
                logger.warning("no entry to function %s found"%f)
        if len(roots)>1:
            logger.verbose('multiple entries into function %s ?!'%f)
        # check start symbol:
        elif roots[0].data.address == self.bin.entrypoints[0]:
            f.name = '_start'
        # get section symbol if any:
        f.misc['section'] = section = self.bin.getinfo(f.address.value)[0]
        rets = f.cfg.leaves()
        if len(rets)==0:
            logger.warning("no exit to function %s found"%f)
        if len(rets)>1:
            logger.verbose('multiple exits in function %s'%f)
        for r in rets:
           # export PLT external symbol name:
            if section and section.name=='.plt':
                if isinstance(r.data,xfunc): f.name = section.name+r.name
            if r.data.misc[tag.FUNC_CALL]:
                f.misc[tag.FUNC_CALL] += 1
        if f.map:
        # check vars & args: should reflect x64 register calling convention
            f.misc[tag.FUNC_VAR] = []
            f.misc[tag.FUNC_ARG] = []
            for x in set(f.map.inputs()):
                f.misc[tag.FUNC_IN] += 1
                if x._is_mem and x.a.base==cpu.rsp:
                    if x.a.disp>=8:
                        f.misc[tag.FUNC_ARG].append(x)
            for x in set(f.map.outputs()):
                if x in (cpu.rsp, cpu.rbp): continue
                f.misc[tag.FUNC_OUT] += 1
                if x._is_mem and x.a.base==cpu.rsp:
                    if x.a.disp<0:
                        f.misc[tag.FUNC_VAR].append(x)


def block_helper_(block,m):
    # annotations based on block semantics:
    sta,sto = block.support
    if m[cpu.mem(cpu.rbp-8,64)] == cpu.rbp:
        block.misc[tag.FUNC_START]=1
    if m[cpu.rip]==cpu.mem(cpu.rsp-8,64):
        block.misc[tag.FUNC_END]=1
    if m[cpu.mem(cpu.rsp,64)]==sto:
        block.misc[tag.FUNC_CALL]=1

#----------------------------------------------------------------------------

# STUBS DEFINED HERE :
#----------------------------------------------------------------------------

from amoco.system.core import DefineStub

@DefineStub(OS,'*',default=True)
def pop_rip(m,**kargs):
    cpu.pop(m,cpu.rip)

@DefineStub(OS,'__libc_start_main')
def libc_start_main(m,**kargs):
    "tags: func_call"
    m[cpu.rip] = m(cpu.rdi)
    cpu.push(m,cpu.ext('exit',size=64))

@DefineStub(OS,'exit')
def libc_exit(m,**kargs):
    m[cpu.rip] = top(64)
@DefineStub(OS,'abort')
def libc_abort(m,**kargs):
    m[cpu.rip] = top(64)
@DefineStub(OS,'__assert')
def libc_assert(m,**kargs):
    m[cpu.rip] = top(64)
@DefineStub(OS,'__assert_fail')
def libc_assert_fail(m,**kargs):
    m[cpu.rip] = top(64)
@DefineStub(OS,'_assert_perror_fail')
def _assert_perror_fail(m,**kargs):
    m[cpu.rip] = top(64)

#----------------------------------------------------------------------------

