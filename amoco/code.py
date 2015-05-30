# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from collections import defaultdict
from amoco.cas.mapper import *

from amoco.config import conf
from amoco.logger import Log
logger = Log(__name__)

#------------------------------------------------------------------------------
# A block instance is a 'continuous' sequence of instructions.
#------------------------------------------------------------------------------
class block(list):
    """
    A block instance is a 'continuous' sequence of instructions.

    Example usage:

        .. code-block:: python

            block  = amoco.code.block()

            while address < len(bytes):
              i = cpu.disassemble(bytes[address:], address=address)
              address += i.length
              block.append(i)
    """

    __slots__=['_map','instr','_name','misc','_helper']

    # the init of a block takes a list of instructions and creates a map of it:
    def __init__(self, instrlist=[], name=None):
        super(block, self).__init__(instrlist)
        self._map  = None
        # base/offset need to be defined before code (used in setcode)
        self._name = name
        self.misc  = defaultdict(lambda :0)
        self._helper = None

    @property
    def map(self):
        if self._map is None:
            self._map = mapper(self)
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
        return self[0].address if len(self)>0 else None

    @property
    def length(self):
        return sum([i.length for i in self],0)

    @property
    def support(self):
        return (self.address,self.address+self.length) if len(self)>0 else (None,None)

    def getname(self):
        return str(self.address) if not self._name else self._name
    def setname(self,name):
        self._name = name
    name = property(getname,setname)

    # cut the block at given address will remove instructions after this address,
    # which needs to be aligned with instructions boundaries. The effect is thus to
    # reduce the block size. The returned value is the number of instruction removed.
    def cut(self,address):
        I = [i.address for i in self]
        try:
            pos = I.index(address)
        except ValueError:
            logger.warning("invalid attempt to cut block %s at %s"%(self.name,address))
            return 0
        else:
            self = self[:pos]
            if self._map:
                self._map.clear()
                for i in self:
                    i(self._map)
            # TODO: update misc annotations too
            return len(I)-pos

    def __str__(self):
        L = []
        n = len(self)
        if conf.getboolean('block','header'):
            L.append('# --- block %s ---' % self.name)
        if conf.getboolean('block','bytecode'):
            bcs = [ "'%s'"%(i.bytes.encode('hex')) for i in self ]
            pad = conf.getint('block','padding') or 0
            maxlen = max(map(len,bcs))+pad
            bcs = [ s.ljust(maxlen) for s in bcs ]
        else:
            bcs = ['']*n
        ins = [ ('{:<10}'.format(i.address),i.formatter(i)) for i in self ]
        for j in range(n):
            L.append('%s %s %s'%(ins[j][0],bcs[j],ins[j][1]))
        return '\n'.join(L)

    def __repr__(self):
        return '<%s object (name=%s) at 0x%08x>'%(self.__class__.__name__,self.name,id(self))

    def raw(self):
        return ''.join([i.bytes for i in self])

    def __cmp__(self,b):
        return cmp(self.raw(),b.raw())

    def __hash__(self):
        return hash(self.name)

    def sig(self):
        misc = defaultdict(lambda :None)
        misc.update(self.misc)
        if len(misc)==0:
            for i in self: misc.update(i.misc)
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
        # base/offset need to be defined before code (used in setcode)
        self._name = name
        self.misc  = defaultdict(lambda :0)

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

    def backward(self,node):
        D = self.cfg.dijkstra(node,f_io=-1)
        logger.verbose('computing backward map from %s',node.name)
        return self.makemap(tagged=D.keys())

    #(re)compute the map of the entire function cfg:
    def makemap(self,tagged=None,withmap=None):
        _map = None
        if tagged is None: tagged = self.cfg.sV
        if self.cfg.order()==0: return
        # get entrypoint:
        t0 = self.cfg.roots()
        if len(t0)==0:
            logger.warning("function %s seems recursive: first block taken as entrypoint",self)
            t0 = [self.cfg.sV[0]]
        if len(t0)>1:
            logger.warning("%s map computed with first entrypoint",self)
        t0 = t0[0]
        assert (t0 in tagged)
        t0map = t0.data._map
        if withmap is not None:
            t0map <<= withmap
        # init structs:
        # spool is the list of current walking "heads" each having a mapper that captures
        # execution up to this point, waitl is the list of nodes that have been reach
        # by a path but are waiting for some other paths to reach them in order to collect
        # and ultimately merge associated mappers before going into spool.
        spool = [(t0,t0map)]
        waitl = defaultdict(lambda :[])
        visit = defaultdict(lambda :0)
        dirty = defaultdict(lambda :0)
        count = 0
        # lets walk func cfg:
        while len(spool)>0:
            n,m = spool.pop(0)
            if dirty[n]: continue
            count += 1
            logger.progress(count,pfx='in %s makemap: '%self.name)
            E = n.e_out()
            exit = True
            # we update spool/waitl with target nodes
            for e in E:
                visit[e]=1
                if e.data and any([m(c)==0 for c in e.data]): continue
                tn = e.v[1]
                if not (tn in tagged): continue
                exit = False
                # if tn is a loop entry, n is marked as a loop end:
                if tn.data.misc[tag.LOOP_START] and self.cfg.path(tn,n,f_io=1):
                    if not n.data.misc[tag.LOOP_END]:
                        logger.verbose('loop end at node %s'%n.name)
                    n.data.misc[tag.LOOP_END] += 1
                tm = tn.data.map.assume(e.data)
                try:
                    waitl[tn].append(m>>tm)
                except ValueError:
                    logger.warning("link %s ignored"%e)
                # if target node has been reach by all parent path, we
                # can merge its mappers and proceed, otherwise it stays
                # in wait list and we take next node from spool
                if all(visit[x] for x in tn.e_in()):
                    wtn = waitl[tn]
                    if len(wtn)>0:
                        spool.append((tn,reduce(merge,wtn)))
                    del waitl[tn]
            # if its an exit node, we update _map and check if widening is possible
            if exit:
                _map = merge(_map,m) if _map else m
                if widening(_map):
                    # if widening has occured, we stop walking the loop by
                    # removing the associated spool node:
                    for s in spool:
                        if self.cfg.path(s[0],n,f_io=1):
                            dirty[s[0]] = 1
                    logger.verbose('widening needed at node %s'%n.name)
            # if spool is empty but wait list is not then we check if
            # its a loop entry and update spool:
            if len(spool)==0 and len(waitl)>0:
                tn = waitl.keys()[0]
                # if tn has output edges its a loop entry:
                if len(tn.e_out())>0:
                    if not tn.data.misc[tag.LOOP_START]:
                        logger.verbose('loop start at node %s'%tn.name)
                    tn.data.misc[tag.LOOP_START] = 1
                spool.append((tn,reduce(merge,waitl[tn])))
                del waitl[tn]
        assert len(waitl)==0
        if len(tagged)<self.cfg.order() or sum(visit.values())<self.cfg.norm():
            self.misc['partial']=True
        else:
            logger.verbose('map of function %s computed'%self)
        return _map

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
        doc = x.stub(x.ref).func_doc
        if doc:
            for (k,v) in tag.list():
                if (k in doc) or (v in doc):
                    self.misc[v] = 1

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


