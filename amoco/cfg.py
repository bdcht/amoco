# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# we wrap the grandalf classes here

from amoco.logger import Log
logger = Log(__name__)

from grandalf.graphs import Vertex,Edge,Graph
from grandalf.layouts import SugiyamaLayout

from amoco.system.core import MemoryZone

#------------------------------------------------------------------------------
# node class is a graph vertex that embeds a block instance and inherits its
# name (default to the address of the block). It extends the Vertex class by
# overloading the __hash__ method in order to test membership based on the data
# rather than on the Vertex instance.
class node(Vertex):
    # protect from None data node:
    def __init__(self,acode):
        Vertex.__init__(self,data=acode)
        self.name = self.data.name
        self.view = self.data.view

    def __repr__(self):
        return '<%s [%s] at 0x%x>'%(self.__class__.__name__,self.name,id(self))

    def __cmp__(self,n):
        return cmp(hash(self),hash(n))

    def __hash__(self):
        return hash(self.data)

    def __len__(self):
        return self.data.length

    def __getitem__(self,i):
        res = node(self.data.__getitem__(i))
        return res

#------------------------------------------------------------------------------
# link is a direct graph edge between two nodes. It extends the Edge class by
# overloading the __hash__ method in order to test membership based on the data
# rather than on the Edge instance.
class link(Edge):

    def __str__(self):
        n0 = self.v[0].name
        n1 = self.v[1].name
        c = '?' if self.data else '-'
        return "%s -%s-> %s"%(n0,c,n1)

    def __repr__(self):
        return '<%s [%s] at 0x%x>'%(self.__class__.__name__,self.name,id(self))

    @property
    def name(self):
        n0 = self.v[0].name
        n1 = self.v[1].name
        return "%s -> %s"%(n0,n1)

    def __cmp__(self,e):
        return cmp(hash(self),hash(e))

    def __hash__(self):
        return hash(self.name)

#------------------------------------------------------------------------------
# graph is a Graph that represents a set of functions as individual components
class graph(Graph):

    def __init__(self,*args,**kargs):
        self.support = MemoryZone()
        self.overlay = None
        super(graph,self).__init__(*args,**kargs)

    def spool(self,n=None):
        L = []
        for v in self.V():
            if len(v.e_out())==0: L.append(v)
        return L

    def __cut_add_vertex(self,v,mz,vaddr,mo):
        oldnode = mo.data.val
        if oldnode==v: return oldnode
        # so v cuts an existing node/block:
        # repair oldblock and fix self
        childs = oldnode.N(+1)
        oldblock = oldnode.data
        # if vaddr is aligned with an oldblock instr, cut it:
        # this reduces oldblock up to vaddr if the cut is possible.
        cutdone = oldblock.cut(vaddr)
        if not cutdone:
            if mz is self.overlay:
                logger.warning("double overlay block at %s"%vaddr)
                v = super(graph,self).add_vertex(v)
                v.data.misc['double-overlay'] = 1
                return v
            overlay = self.overlay or MemoryZone()
            return self.add_vertex(v,support=overlay)
        else:
            v = super(graph,self).add_vertex(v) # ! avoid recursion for add_edge
            mz.write(vaddr,v)
            self.add_edge(link(oldnode,v))
            for n in childs:
                self.add_edge(link(v,n))
                self.remove_edge(oldnode.e_to(n))
            return v

    def add_vertex(self,v,support=None):
        if len(v)==0: return super(graph,self).add_vertex(v)
        vaddr=v.data.address
        if support is None:
            support=self.support
        else:
            logger.verbose("add overlay block at %s"%vaddr)
            self.overlay = support
        i = support.locate(vaddr)
        if i is not None:
            mo = support._map[i]
            if vaddr in mo:
                return self.__cut_add_vertex(v,support,vaddr,mo)
            else: #v does not cut an existing block,
                try: # but may swallow next one...
                    nextmo = support._map[i+1]
                except IndexError:
                    # no more nodes here so back to default case:
                    pass
                else:
                    nextnode = nextmo.data.val
                    if vaddr+len(v)>nextnode.data.address:
                        cutdone = v.data.cut(nextnode.data.address)
                        if not cutdone:
                            if support is self.overlay:
                                logger.warning("double overlay block at %s"%vaddr)
                                v = super(graph,self).add_vertex(v)
                                v.data.misc['double-overlay'] = 1
                                return v
                            support = self.overlay or MemoryZone()
        v = super(graph,self).add_vertex(v) # before support write !!
        support.write(vaddr,v)
        return v

    def get_by_name(self,name):
        for v in self.V():
            if v.name==name: return v
        return None

    def get_with_address(self,vaddr):
        i = self.support.locate(vaddr)
        if i is not None:
            mo = self.support._map[i]
            if vaddr in mo:
                return mo.data.val
        return None

    def signature(self):
        return ''.join([signature(g) for g in self.C])

def signature(g):
    P = g.partition()
    S = []
    for p in P:
        s = []
        for n in p:
            s.append(n.data.sig())
        S.append(''.join(s))
    return '{[%s]}'%']['.join(S)
