# -*- coding: utf-8 -*-

"""
.. _lsweep:

lsweep.py
=========
The lsweep module of amoco implements basic CFG recovery by linear sweep.

The *linear sweep* method (:class:`main.lsweep`) works basically like *objdump*.
It produces instructions by disassembling bytes one after the other, ignoring the
effective control flow. For standard x86/x64 binaries, the result is not so bad
because code and data are rarely interlaced, but for many other architectures
the result is incorrect.
Still, it provides - at almost no cost - an overapproximation of the set of all
*basic blocks* for architectures with strict fixed-length instruction alignment.

"""

# This code is part of Amoco
# Copyright (C) 2006-2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.config import conf
from amoco.logger import Log
logger = Log(__name__)
logger.debug('loading module')

from amoco import cfg
from amoco import code
from amoco.signals import SIG_TRGT,SIG_NODE,SIG_EDGE,SIG_BLCK,SIG_FUNC
from amoco.arch.core import type_control_flow

__all__ = ['cfg','code',
           'SIG_TRGT','SIG_NODE','SIG_EDGE','SIG_BLCK','SIG_FUNC',
           'lsweep']

# -----------------------------------------------------------------------------
class lsweep(object):
    """Linear sweep based analysis: a fast but somehow dumb way of
    disassembling a program. Other strategies usually inherit from this class
    which provides generic methods :meth:`sequence` and :meth:`iterblocks`
    as instruction and basic block iterators.

    Arguments:
        prog: the program object to analyze. This object needs to inherit from
              :class:`system.core.CoreExec` or to provide access to a cpu module
              and methods :meth:`initstate`, :meth:`read_instruction`,
              and :meth:`codehelper`.

    Attributes:
        prog: (see arguments.)
        G (graph): the placeholder for the recovered :class:`cfg.graph`.
    """
    __slots__ = ['prog','G']
    def __init__(self,prog):
        self.prog = prog
        self.G = cfg.graph()
        SIG_NODE.sender(self.G.add_vertex)
        SIG_EDGE.sender(self.G.add_edge)

    def sequence(self,loc=None):
        """Iterator over linearly sweeped instructions.

        Arguments:
            loc (Optional[cst]): the address to start disassembling
                (defaults to the program's entrypoint).

        Yields:
            instructions from given address, until a non-instruction
            byte sequence is reached.
        """
        p = self.prog
        if loc is None:
            try:
                m = p.state
                loc = m(p.cpu.PC())
            except (TypeError,ValueError):
                loc = 0
        while True:
            i = p.read_instruction(loc)
            if i is None: raise StopIteration
            loc += i.length
            yield i

    def iterblocks(self,loc=None):
        """Iterator over basic blocks. The :attr:`instruction.type`
        attribute is used to detect the end of a block (type_control_flow).
        The returned :class:`block` object is enhanced with plateform-specific
        informations (see :attr:`block.misc`).

        Arguments:
            loc (Optional[cst]): the address of the first block
                (defaults to the program's entrypoint).

        Yields:
            linear sweeped blocks of instructions from given address,
            until :meth:`sequence` stops.
        """
        l = []
        seq = self.sequence(loc)
        is_delay_slot = False
        for i in seq:
            # add branching instruction inside block:
            l.append(i)
            if i.misc['delayed']:
                is_delay_slot = True
            elif i.type==type_control_flow or is_delay_slot:
                # check if branch is delayed (e.g. sparc)
                # create block instance:
                b = code.block(l)
                l = []
                is_delay_slot = False
                SIG_BLCK.emit(args=b)
                yield b
        if len(l)>0:
            if is_delay_slot:
                logger.warning(u'no instruction in delay slot')
            b = code.block(l)
            SIG_BLCK.emit(args=b)
            yield b

    def getblock(self,val):
        """getblock is just a wrapper of iterblocks to
        return the first block located at given (int) address.
        """
        p = self.prog
        target = p.cpu.cst(val,p.cpu.PC().size)
        ib = self.iterblocks(target)
        try:
            b = next(ib)
        except StopIteration:
            return None
        else:
            ib.close()
            return b

    @property
    def functions(self):
        """provides the list of functions recovered so far.
        """
        F = []
        for c in self.G.C:
            f = c.sV[0]
            if f and f.data._is_func: F.append(f)
        return F

    def signature(self,func=None):
        """provides the signature of a given function,
        or the entire signature string.
        """
        if func is not None:
            return cfg.signature(func.cfg)
        return self.G.signature()

    def score(self,func=None):
        """a measure for the *complexity* of the program.
        For the moment it is associated only with the
        signature length.
        """
        sig = self.signature(func)
        return len(sig)

