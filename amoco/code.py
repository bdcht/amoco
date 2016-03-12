# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
The code module defines classes that represent assembly blocks, functions,
and *external functions*.
"""

import pdb
import heapq
from collections import defaultdict

from amoco.cas.mapper import *

from amoco.config import conf
from amoco.logger import Log
logger = Log(__name__)

from amoco.ui.views import blockView, funcView, xfuncView

#-------------------------------------------------------------------------------
class block(object):
    """
    A block instance is a 'continuous' sequence of instructions.
    """
    __slots__=['_map','instr','_name','misc','_helper','view']

    def __init__(self, instrlist, name=None):
        """
        the init of a block takes a list of instructions and creates a `map` of it
        """
        self._map  = None
        self.instr = instrlist
        self._name = name
        self.misc  = defaultdict(lambda :0)
        self._helper = None
        self.view  = blockView(self)

    @property
    def map(self):
        if self._map is None:
            self._map = mapper(self.instr)
            self.helper(self._map)
        if self.misc['func']:
            return self.misc['func'].map
        return self._map
    @map.setter
    def map(self,m):
        self._map = m

    def helper(self,m):
        if self._helper: self._helper(self,m)

    @property
    def address(self):
        return self.instr[0].address if len(self.instr)>0 else None

    @property
    def length(self):
        return sum([i.length for i in self.instr],0)

    @property
    def support(self):
        if len(self.instr)>0:
            return (self.address,self.address+self.length)
        else:
            return (None,None)

    def getname(self):
        return str(self.address) if not self._name else self._name
    def setname(self,name):
        self._name = name
    name = property(getname,setname)

    def __getitem__(self,i):
        sta,sto,stp = i.indices(self.length)
        assert stp==1
        pos = [0]
        for i in self.instr:
            pos.append(pos[-1]+i.length)
        try:
            ista = pos.index(sta)
            isto = pos.index(sto)
        except ValueError:
            logger.warning("can't slice block: indices must match instruction boudaries")
            return None
        I = self.instr[ista:isto]
        if len(I)>0:
            return block(self.instr[ista:isto])

    # cut the block at given address will remove instructions after this address,
    # which needs to be aligned with instructions boundaries. The effect is thus to
    # reduce the block size. The returned value is the number of instruction removed.
    def cut(self,address):
        I = [i.address for i in self.instr]
        try:
            pos = I.index(address)
        except ValueError:
            logger.warning("invalid attempt to cut block %s at %s"%(self.name,address))
            return 0
        else:
            self.instr = self.instr[:pos]
            if self._map:
                self._map.clear()
                for i in self.instr:
                    i(self._map)
            # TODO: update misc annotations too
            return len(I)-pos

    def __str__(self):
        T = self.view._vltable(formatter='Null')
        return '\n'.join([r.show(raw=True,**T.rowparams) for r in T.rows])

    def __repr__(self):
        return '<%s object (name=%s) at 0x%08x>'%(self.__class__.__name__,self.name,id(self))

    def raw(self):
        return ''.join([i.bytes for i in self.instr])

    def __cmp__(self,b):
        return cmp(self.raw(),b.raw())

    def __hash__(self):
        return hash(self.name)

    def sig(self):
        misc = defaultdict(lambda :None)
        misc.update(self.misc)
        if len(misc)==0:
            for i in self.instr: misc.update(i.misc)
        s = [tag.sig(k) for k in misc]
        return '(%s)'%(''.join(s))

#------------------------------------------------------------------------------
# func is a cfg connected component that generally represents a called function
# It appears in the other graphs whenever the function is called and provides a
# synthetic map that captures the semantics of the function.
#------------------------------------------------------------------------------
class func(block):
    __slots__ = ['cfg']

    # the init of a func takes a core_graph and creates a map of it:
    def __init__(self, g=None, name=None):
        self._map = None
        self.cfg = g
        self.instr = []
        # base/offset need to be defined before code (used in setcode)
        self._name = name
        self.misc  = defaultdict(lambda :0)
        self._helper = None
        self.view  = funcView(self)

    @property
    def address(self):
        return self.blocks[0].address

    @property
    def blocks(self):
        return [n.data for n in self.cfg.sV]

    @property
    def support(self):
        smin = self.address
        smax = max((b.address+b.length for b in self.blocks))
        return (smin,smax)

    #(re)compute the map of the entire function cfg:
    def makemap(self,withmap=None,widening=True):
        # spawn a cfg layout to detect loops and allow to
        # walk the cfg by using the nodes rank.
        gr = self.view.layout
        gr.init_all()
        # init the walking process heap queue and heads:
        # spool is a heap queue ordered by node rank. It is associated
        # with the list of current walking "heads" (a mapper that captures
        # execution up to this block.
        count = 0
        spool = []
        heads = {}
        for t in gr.layers[0]:
            heapq.heappush(spool,(0,t))
            tmap = t.data._map
            if withmap is not None:
                tmap <<= withmap
            heads[t] = tmap
        self.misc['heads'] = heads
        # lets walk the function's cfg, in rank priority order:
        while len(spool)>0:
            count += 1
            logger.progress(count,pfx='in %s makemap: '%self.name)
            # take lowest ranked node from spool:
            l,n = heapq.heappop(spool)
            m = heads.pop(n)
            # keep head for exit or merging points:
            if len(n.e_out())==0 or len(n.e_in())>1: heads[n] = m
            # we want to update the mapper by going through all edges out of n:
            for e in n.e_out():
                tn = e.v[1]
                # compute constraints that lead to this path with this mapper:
                econd = []
                if e.data:
                    econd = [m(c) for c in e.data]
                # increment loop index for widening:
                if e in gr.alt_e:
                    n.data.misc[tag.LOOP_END]+=1
                    tn.data.misc[tag.LOOP_START]+=1
                # compute new mapper state:
                try:
                    # apply edge contraints to the current mapper and
                    # try to execute target:
                    mtn = m.assume(econd)>>tn.data.map
                except ValueError,err:
                    logger.warning("link %s ignored"%e)
                    continue
                # and update heads and spool...
                if tn in heads:
                    # check for widening:
                    if widening and tn.data.misc[tag.LOOP_START]==1:
                        logger.verbose('widening at %s'%tn.name)
                        mm = merge(heads[tn],mtn,widening)
                    else:
                        mm = merge(heads[tn],mtn)
                    fixpoint = (mm==heads[tn])
                else:
                    mm = mtn
                    fixpoint = False
                # update heads:
                heads[tn] = mm
                # update spool if not on a fixpoint:
                if not fixpoint:
                    r = gr.grx[tn].rank
                    if not (r,tn) in spool:
                        heapq.heappush(spool,(r,tn))
                else:
                    logger.verbose('fixpoint at %s'%tn.name)
        out = [heads[x] for x in self.cfg.leaves()]
        _map = reduce(merge,out) if out else None
        return _map

    def __str__(self):
        return "%s{%d}"%(self.name,len(self.blocks))

#------------------------------------------------------------------------------
# xfunc represents external functions. It is associated with an ext expression.
# The map provided by an xfunc instance is constructed by executing the stub
# defined in the ext expression.
#------------------------------------------------------------------------------
class xfunc(object):
    __slots__ = ['map','name','address','length','misc','view']

    def __init__(self, x):
        self.map = mapper()
        x(self.map)
        self.name = str(x)
        self.address = x
        self.length = 0
        self.misc  = defaultdict(lambda :0)
        doc = x.stub(x.ref).func_doc
        if doc:
            for (k,v) in tag.list():
                if (k in doc) or (v in doc):
                    self.misc[v] = 1
        self.view  = xfuncView(self)

    @property
    def support(self):
        return (self.address,self.address)

#------------------------------------------------------------------------------
class tag:
    FUNC_START   = 'func_start'
    FUNC_END     = 'func_end'
    FUNC_STACK   = 'func_stack'
    FUNC_UNSTACK = 'func_unstack'
    FUNC_CALL    = 'func_call'
    FUNC_GOTO    = 'func_goto'
    FUNC_ARG     = 'func_arg'
    FUNC_VAR     = 'func_var'
    FUNC_IN      = 'func_in'
    FUNC_OUT     = 'func_out'
    LOOP_START   = 'loop_start'
    LOOP_END     = 'loop_end'
    LOOP_COND    = 'loop_cond'

    @classmethod
    def list(cls):
        return filter(lambda kv: kv[0].startswith('FUNC_'), cls.__dict__.items())

    @classmethod
    def sig(cls,name):
        return {
         'cond'           : '?',
         'func'           : 'F',
         cls.FUNC_START   : 'e',
         cls.FUNC_END     : 'r',
         cls.FUNC_STACK   : '+',
         cls.FUNC_UNSTACK : '-',
         cls.FUNC_CALL    : 'c',
         cls.FUNC_GOTO    : 'j',
         cls.FUNC_ARG     : 'a',
         cls.FUNC_VAR     : 'v',
         cls.FUNC_IN      : 'i',
         cls.FUNC_OUT     : 'o',
         cls.LOOP_START   : 'l' }.get(name,'')


