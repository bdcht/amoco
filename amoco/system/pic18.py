# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import *
from amoco.code import tag

import amoco.arch.pic.cpu_pic18f46k22 as cpu

class PIC18(CoreExec):

    def __init__(self,p):
        self.cpu = cpu
        self.cmap = MemoryMap()
        self.mmap = MemoryMap()
        self.bin = p
        self.bin.seek(0)
        self.cmap.write(0,self.bin.read())
        self.cpu.ptr.segment_handler = self.pic_seg_handler

    def read_data(self,vaddr,size):
        return self.mmap.read(vaddr,size)

    def read_instruction(self,vaddr,**kargs):
        maxlen = self.cpu.disassemble.maxlen
        try:
            istr = self.cmap.read(vaddr,maxlen)
        except MemoryError,e:
            logger.warning("vaddr %s is not mapped"%vaddr)
            raise MemoryError(e)
        i = self.cpu.disassemble(istr[0],**kargs)
        if i is None:
            logger.warning("disassemble failed at vaddr %s"%vaddr)
            if len(istr)>1 and istr[1]._is_def:
                logger.warning("symbol found in instruction buffer"%vaddr)
                raise MemoryError(vaddr)
            return None
        else:
            i.address = vaddr
            return i

    def initenv(self):
        from amoco.cas.mapper import mapper
        m = mapper()
        m[self.cpu.pc] = self.cpu.cst(0,21)
        return m

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
            elif i.mnemonic == 'PUSH':
                i.misc[tag.FUNC_STACK]=1
            elif i.mnemonic == 'POP':
                i.misc[tag.FUNC_UNSTACK]=1
            # provide hints of absolute location from relative offset:
            elif i.mnemonic in ('BC','BNC','BN','BNN','BNOV','BNZ','BOV','BRA','BZ','RCALL'):
                if i.mnemonic == 'RCALL':
                    i.misc[tag.FUNC_CALL]=1
                    i.misc['retto'] = i.address+i.length
                if (i.address is not None) and i.operands[0]._is_cst:
                    offset = i.operands[0].value
                    v = i.address+i.length+(2*offset)
                    i.misc['to'] = v
                    continue
        return seq

    def blockhelper(self,blk):
        self.seqhelper(blk)
        return blk

    def pic_seg_handler(self,env,seg,base_disp):
        base,disp = base_disp
        if not isinstance(seg,str):
            base[8:12] = seg[0:4]
            seg = ''
        return self.cpu.ptr(base,seg,disp)
