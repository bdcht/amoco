# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

from collections import defaultdict
from amoco.cas.mapper import mapper

from amoco.config import conf

#------------------------------------------------------------------------------
# A block instance is a 'continuous' (atomic) set of instructions.
# It is build from a bytecode 
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
        # translate into a interpreter:
        #acode.__init__(self,mapper(self.instr))

    @property
    def map(self):
        if self._map is None:
            self._map = mapper(self.instr)
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
        ista = pos.index(sta)
        isto = pos.index(sto)
        I = self.instr[ista:isto]
        if len(I)>0:
            return block(self.instr[ista:isto])

    def cut(self,address):
        I = [i.address for i in self.instr]
        try:
            pos = I.index(address)
        except ValueError:
            pass
        else:
            self.instr = self.instr[:pos]
            self.map.clear()
            for i in self.instr: i(self.map)
            # TODO: update misc annotations too

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
# A func instance is an acode where the map is build from a cfg by
# unions and fixpoints on (sub)maps contained in this cfg.
#------------------------------------------------------------------------------
class func(object):
    __slots__ = ['name','cfg']
    def __init__(self,name,cfg):
        self.name = name
        self.cfg = cfg

    def __str__(self):
        s = '# --- func %s ---\n%s' % (self.name,str(self.cfg))
        return s


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

