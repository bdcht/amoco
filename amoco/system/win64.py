# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2007 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import *
from amoco.code import tag

import amoco.arch.x64.cpu_x64 as cpu

PAGESIZE = 4096

class PE(CoreExec):

    def __init__(self,p):
        CoreExec.__init__(self,p,cpu)

    def load_binary(self):
        p = self.bin
        if p!=None:
            # create text and data segments according to PE headers:
            base,headers = p.loadsegment(0).popitem()
            self.mmap.write(base,headers) # load Headers
            for s in p.sections:          # load other Sections
                ms = p.loadsegment(s,PAGESIZE)
                if ms!=None:
                    vaddr,data = ms.popitem()
                    self.mmap.write(vaddr,data)
            # create the dynamic segments:
            self.load_shlib()
        # create the stack zone:
        self.mmap.newzone(cpu.rsp)

    # call dynamic linker to populate mmap with shared libs:
    # for now, the external libs are seen through the elf dynamic section:
    def load_shlib(self):
        for k,f in self.bin.functions.iteritems():
            self.mmap.write(k,cpu.ext(f,size=64))

    def initenv(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        for k,v in ((cpu.rip, cpu.cst(self.bin.entrypoints[0],64)),
                    (cpu.rbp, cpu.cst(0,64)),
                    (cpu.rax, cpu.cst(0,64)),
                    (cpu.rbx, cpu.cst(0,64)),
                    (cpu.rcx, cpu.cst(0,64)),
                    (cpu.rdx, cpu.cst(0,64)),
                    (cpu.rsi, cpu.cst(0,64)),
                    (cpu.rdi, cpu.cst(0,64))):
            m[k] = v
        return m

    # lookup in bin if v is associated with a function or variable name:
    def check_sym(self,v):
        if v._is_cst:
            x = self.bin.functions.get(v.value,None) or self.bin.variables.get(v.value,None)
            if x is not None:
                if isinstance(x,str): x=cpu.ext(x,size=64)
                else: x=cpu.sym(x[0],v.value,v.size)
                return x
        return None

    def codehelper(self,**kargs):
        if 'seq' in kargs: return self.seqhelper(kargs['seq'])
        if 'block' in kargs: return self.blockhelper(kargs['block'])
        if 'func' in kargs: return self.funchelper(kargs['func'])

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
                    continue
            # check operands (globals & .got calls):
            for op in i.operands:
                if op._is_mem:
                    if op.a.base is cpu.rbp:
                        if op.a.disp<0: i.misc[tag.FUNC_ARG]=1
                        else: i.misc[tag.FUNC_VAR]=1
                    elif op.a.base._is_cst:
                        x = self.check_sym(op.a.base)
                        if x is not None: op.a.base=x
                elif op._is_cst:
                    x = self.check_sym(op)
                    i.misc['imm_ref'] = x
        return seq

    def blockhelper(self,block):
        for i in self.seqhelper(block):
            block.misc.update(i.misc)
        # delayed computation of block.map:
        def _helper(block,m):
            # annotations based on block semantics:
            sta,sto = block.support
            if m[cpu.mem(cpu.rbp-8,64)] == cpu.rbp:
                block.misc[tag.FUNC_START]=1
            if m[cpu.rip]==cpu.mem(cpu.rsp-8,64):
                block.misc[tag.FUNC_END]=1
            if m[cpu.mem(cpu.rsp,64)]==sto:
                block.misc[tag.FUNC_CALL]=1
        block._helper = _helper
        return block

    def funchelper(self,f):
        roots = f.cfg.roots()
        if len(roots)==0:
            roots = filter(lambda n:n.data.misc[tag.FUNC_START],f.cfg.sV)
            if len(roots)==0:
                logger.warning("no entry to function %s found"%f)
        if len(roots)>1:
            logger.verbose('multiple entries into function %s ?!'%f)
        rets = f.cfg.leaves()
        if len(rets)==0:
            logger.warning("no exit to function %s found"%f)
        if len(rets)>1:
            logger.verbose('multiple exits in function %s'%f)
        for r in rets:
            if r.data.misc[tag.FUNC_CALL]: f.misc[tag.FUNC_CALL] += 1


# HOOKS DEFINED HERE :
#----------------------------------------------------------------------------

@stub_default
def pop_rip(m,**kargs):
    cpu.pop(m,cpu.rip)


