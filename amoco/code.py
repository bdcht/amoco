# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from collections import defaultdict
from amoco.cas.mapper import mapper

from amoco.config import conf
from amoco.logger import Log
logger = Log(__name__)

#------------------------------------------------------------------------------
# A block instance is a 'continuous' sequence of instructions.
#------------------------------------------------------------------------------
class block(object):
    __slots__=['_map','instr','_name','misc']

    # the init of a block takes a list of instructions and creates a map of it:
    def __init__(self, instrlist, name=None):
        self._map  = None
        # base/offset need to be defined before code (used in setcode)
        self.instr = instrlist
        self._name = name
        self.misc  = defaultdict(lambda :0)

    @property
    def map(self):
        if self._map is None:
            self._map = mapper(self.instr)
        if self.misc['func']:
            return self.misc['func'].map
        return self._map
    @map.setter
    def map(self,m):
        self._map = m

    @property
    def address(self):
        return self.instr[0].address if len(self.instr)>0 else None

    @property
    def length(self):
        return sum([i.length for i in self.instr],0)

    @property
    def support(self):
        return (self.address,self.address+self.length) if len(self.instr)>0 else (None,None)

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
            self.map.clear()
            for i in self.instr: i(self.map)
            # TODO: update misc annotations too
            return len(I)-pos

    def __str__(self):
        L = []
        n = len(self.instr)
        if conf.getboolean('block','header'):
            L.append('# --- block %s ---' % self.name)
        if conf.getboolean('block','bytecode'):
            bcs = [ "'%s'"%(i.bytes.encode('hex')) for i in self.instr ]
            pad = conf.getint('block','padding') or 0
            maxlen = max(map(len,bcs))+pad
            bcs = [ s.ljust(maxlen) for s in bcs ]
        else:
            bcs = ['']*n
        ins = [ ('{:<10}'.format(i.address),i.formatter(i)) for i in self.instr ]
        for j in range(n):
            L.append('%s %s %s'%(ins[j][0],bcs[j],ins[j][1]))
        return '\n'.join(L)

    def __repr__(self):
        return '<%s object (name=%s) at 0x%08x>'%(self.__class__.__name__,self.name,id(self))

    def raw(self):
        return ''.join([i.bytes for i in self.instr])

    def __cmp__(self,b):
        return cmp(self.raw(),b.raw())


#------------------------------------------------------------------------------
# func is a cfg connected component that generally represents a called function
# It appears in the other graphs whenever the function is called and provides a
# synthetic map that captures the semantics of the function.
#------------------------------------------------------------------------------
class func(block):
    __slots__ = ['cfg']

    # the init of a func takes a core_graph and creates a map of it:
    def __init__(self, g=None, name=None):
        self._map  = None
        self.cfg = g
        self.instr = []
        # base/offset need to be defined before code (used in setcode)
        self._name = name
        self.misc  = defaultdict(lambda :0)

    @property
    def address(self):
        return self.blocks[0].address

    @property
    def blocks(self):
        V = self.cfg.sV.o
        return [n.data for n in V]

    @property
    def support(self):
        smin = self.address
        smax = max((b.address+b.length for b in self.blocks))
        return (smin,smax)

    def makemap(self):
        raise NotImplementedError

    def __str__(self):
        return "%s{%d}"%(self.name,len(self.blocks))

#------------------------------------------------------------------------------
# xfunc represents external functions. It is associated with an ext expression.
# The map provided by an xfunc instance is constructed by executing the stub
# defined in the ext expression.
#------------------------------------------------------------------------------
class xfunc(object):
    __slots__ = ['map','name','address','length','misc']

    def __init__(self, x):
        self.map = mapper()
        x(self.map)
        self.name = str(x)
        self.address = x
        self.length = 0
        self.misc  = defaultdict(lambda :0)

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
    FUNC_ARG     = 'func_arg'
    FUNC_VAR     = 'func_var'
    FUNC_IN      = 'func_in'
    FUNC_OUT     = 'func_out'
    LOOP_START   = 'loop_start'
    LOOP_END     = 'loop_end'
    LOOP_COND    = 'loop_cond'

