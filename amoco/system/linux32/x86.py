# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.elf import *
from amoco.system.core import CoreExec,DefineStub
from amoco.code import tag
import amoco.arch.x86.cpu_x86 as cpu

#Intel 80386 specific definitions. #i386 relocs.
with Consts('r_type'):
    R_386_NONE=0
    R_386_32=1
    R_386_PC32=2
    R_386_GOT32=3
    R_386_PLT32=4
    R_386_COPY=5
    R_386_GLOB_DAT=6
    R_386_JMP_SLOT=7
    R_386_RELATIVE=8
    R_386_GOTOFF=9
    R_386_GOTPC=10
    R_386_32PLT=11
    R_386_TLS_TPOFF=14
    R_386_TLS_IE=15
    R_386_TLS_GOTIE=16
    R_386_TLS_LE=17
    R_386_TLS_GD=18
    R_386_TLS_LDM=19
    R_386_16=20
    R_386_PC16=21
    R_386_8=22
    R_386_PC8=23
    R_386_TLS_GD_32=24
    R_386_TLS_GD_PUSH=25
    R_386_TLS_GD_CALL=26
    R_386_TLS_GD_POP=27
    R_386_TLS_LDM_32=28
    R_386_TLS_LDM_PUSH=29
    R_386_TLS_LDM_CALL=30
    R_386_TLS_LDM_POP=31
    R_386_TLS_LDO_32=32
    R_386_TLS_IE_32=33
    R_386_TLS_LE_32=34
    R_386_TLS_DTPMOD32=35
    R_386_TLS_DTPOFF32=36
    R_386_TLS_TPOFF32=37
    R_386_NUM=38

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
        else:
            self.PAGESIZE = conf.pagesize
            self.ASLR     = conf.aslr
            self.NX       = conf.nx
        from .abi import cdecl
        self.abi = cdecl
        self.tasks = []

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
                executable_stack = s.p_flags & PF_X
        # init task state registers:
        p.state[cpu.eip] = cpu.cst(p.bin.entrypoints[0],32)
        p.state[cpu.ebp] = cpu.cst(0,32)
        p.state[cpu.eax] = cpu.cst(0,32)
        p.state[cpu.ebx] = cpu.cst(0,32)
        p.state[cpu.ecx] = cpu.cst(0,32)
        p.state[cpu.edx] = cpu.cst(0,32)
        p.state[cpu.esi] = cpu.cst(0,32)
        p.state[cpu.edi] = cpu.cst(0,32)
        # create the stack space:
        if self.ASLR:
            p.state.mmap.newzone(p.cpu.esp)
        else:
            stack_base = 0x7fffffff & ~(self.PAGESIZE-1)
            stack_size = 2*self.PAGESIZE
            p.state.mmap.write(stack_base-stack_size,b'\0'*stack_size)
            p.state[cpu.esp] = cpu.cst(stack_base,32)
        # create the dynamic segments:
        if bprm.dynamic and interp:
            self.load_elf_interp(p,interp)
        # start task:
        self.tasks.append(p)
        return p

    def load_elf_interp(self,p,interp):
        for k,f in p.bin._Elf__dynamic(None).items():
            xf= cpu.ext(f,size=32)
            xf.stub = p.OS.stub(f)
            p.state.mmap.write(k,xf)

    def stub(self,refname):
        return self.stubs.get(refname,self.default_stub)

#------------------------------------------------------------------------------

class Task(CoreExec):

    # helper provides arch-dependent information to amoco.sa classes
    def misc_block(self,blk):
        for i in blk.instr:
            # some basic hints:
            if i.mnemonic.startswith('RET'):
                i.misc[tag.FUNC_END]=1
            elif i.mnemonic in ('PUSH','ENTER'):
                i.misc[tag.FUNC_STACK]=1
                if i.operands and i.operands[0] is cpu.ebp:
                    i.misc[tag.FUNC_START]=1
            elif i.mnemonic in ('POP','LEAVE'):
                i.misc[tag.FUNC_UNSTACK]=1
                if i.operands and i.operands[0] is cpu.ebp:
                    i.misc[tag.FUNC_END]=1
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
                    v = i.address+i.operands[0].signextend(32)+i.length
                    x = self.check_sym(v)
                    if x is not None: v=x
                    i.misc['to'] = v
                    if i.misc[tag.FUNC_CALL] and i.misc['retto']==v:
                        # this looks like a fake call
                        i.misc[tag.FUNC_CALL]=-1
            # check operands (globals & .got calls):
            for op in i.operands:
                if op._is_mem:
                    if op.a.base is cpu.ebp:
                        if   op.a.disp<0: i.misc[tag.FUNC_VAR]=True
                        elif op.a.disp>=8: i.misc[tag.FUNC_ARG]=True
                    elif op.a.base._is_cst:
                        x = self.check_sym(op.a.base+op.a.disp)
                        if x is not None:
                            op.a.base=x
                            op.a.disp=0
                            if i.mnemonic == 'JMP': # PLT jumps:
                                i.misc[tag.FUNC_START]=1
                                i.misc[tag.FUNC_END]=1
                elif op._is_cst:
                    x = self.check_sym(op)
                    i.misc['imm_ref'] = x

    def funchelper(self,f):
        # check single root node:
        roots = f.cfg.roots()
        if len(roots)==0:
            roots = filter(lambda n:n.data.misc[tag.FUNC_START],f.cfg.sV)
            if len(roots)==0:
                logger.warning("no entry to function %s found"%f)
        if len(roots)>1:
            logger.verbose('multiple entries into function %s ?!'%f)
        # check _start symbol:
        elif roots[0].data.address == self.bin.entrypoints[0]:
            f.name = '_start'
        # get section symbol if any:
        f.misc['section'] = section = self.bin.getinfo(f.address.value)[0]
        # check leaves:
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
        # check vars & args:
            f.misc[tag.FUNC_VAR] = []
            f.misc[tag.FUNC_ARG] = []
            for x in set(f.map.inputs()):
                f.misc[tag.FUNC_IN] += 1
                if x._is_mem and x.a.base==cpu.esp:
                    if x.a.disp>=4:
                        f.misc[tag.FUNC_ARG].append(x)
            for x in set(f.map.outputs()):
                if x in (cpu.esp, cpu.ebp): continue
                f.misc[tag.FUNC_OUT] += 1
                if x._is_mem and x.a.base==cpu.esp:
                    if x.a.disp<0:
                        f.misc[tag.FUNC_VAR].append(x)



#----------------------------------------------------------------------------
# the block helper that will be called
# only when the map is computed.
def block_helper_(block,m):
    # update block.misc based on semantics:
    sta,sto = block.support
    if m[cpu.mem(cpu.ebp-4,32)] == cpu.ebp:
        block.misc[tag.FUNC_START]=1
    if m[cpu.eip]==cpu.mem(cpu.esp-4,32):
        block.misc[tag.FUNC_END]=1
    if m[cpu.mem(cpu.esp,32)]==sto:
        block.misc[tag.FUNC_CALL]=1

# STUBS DEFINED HERE :
#----------------------------------------------------------------------------

@DefineStub(OS,'*',default=True)
def pop_eip(m,**kargs):
    cpu.pop(m,cpu.eip)

@DefineStub(OS,'__libc_start_main')
def libc_start_main(m,**kargs):
    "tags: func_call"
    m[cpu.eip] = m(cpu.mem(cpu.esp+4,32))
    cpu.push(m,cpu.ext('exit',size=32))

@DefineStub(OS,'exit')
def libc_exit(m,**kargs):
    m[cpu.eip] = top(32)
@DefineStub(OS,'abort')
def libc_abort(m,**kargs):
    m[cpu.eip] = top(32)
@DefineStub(OS,'__assert')
def libc_assert(m,**kargs):
    m[cpu.eip] = top(32)
@DefineStub(OS,'__assert_fail')
def libc_assert_fail(m,**kargs):
    m[cpu.eip] = top(32)
@DefineStub(OS,'_assert_perror_fail')
def _assert_perror_fail(m,**kargs):
    m[cpu.eip] = top(32)

#----------------------------------------------------------------------------

