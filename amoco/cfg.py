# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

# we wrap the grandalf classes here

from grandalf.graphs import Vertex,Edge,Graph

from amoco.system.core import MemoryZone

#------------------------------------------------------------------------------
class node(Vertex):
    # protect from None data node:
    def __init__(self,acode):
        Vertex.__init__(self,data=acode)
    # shortcut:
    @property
    def name(self):
        return self.data.name

    def __repr__(self):
        return '<%s [%s] at 0x%x>'%(self.__class__.__name__,self.name,id(self))

    def __cmp__(self,n):
        return cmp(self.name,n.name)

    def __len__(self):
        return self.data.length

    def __getitem__(self,i):
        self.data = self.data.__getitem__(i)
        return res

#------------------------------------------------------------------------------
class link(Edge):
    def __init__(self,orig,dest):
        Edge.__init__(self,orig,dest)

    def __str__(self):
        n0 = repr(self.v[0])
        n1 = repr(self.v[1])
        return "%s -> %s"%(n0,n1)

    def __repr__(self):
        return '<%s [%s] at 0x%x>'%(self.__class__.__name__,self.name,id(self))

    @property
    def name(self):
        n0 = self.v[0].name
        n1 = self.v[1].name
        return "%s -> %s"%(n0,n1)

    def __cmp__(self,e):
        return cmp(self.name,e.name)

#------------------------------------------------------------------------------
class func(Graph):

    def __init__(self,*args,**kargs):
        self.support = MemoryZone()
        Graph.__init__(self,*args,**kargs)

    def spool(self,n=None):
        L = []
        for v in self.V():
            if len(v.e_out())==0: L.append(v)
        return L

    def add_vertex(self,v):
        vaddr=v.data.address
        i = self.support.locate(vaddr)
        if i is not None:
            mo = self.support._map[i]
            if vaddr in mo:
                oldnode = mo.data.val
                if oldnode==v: return 0
                # so v cuts an existing node/block:
                # repair oldblock and fix self
                childs = oldnode.N(+1)
                oldblock = oldnode.data
                oldblock.cut(vaddr)
                Graph.add_vertex(self,v) # ! avoid recursion for add_edge
                self.support.write(vaddr,v)
                self.add_edge(link(oldnode,v))
                for n in childs:
                    self.add_edge(link(v,n))
                    self.remove_edge(oldnode.e_to(n))
                return 1
            else: #v does not cut an existing block,
                try: # but may swallow next one...
                    nextmo = self.support._map[i+1]
                except IndexError:
                    # no more nodes here so back to default case:
                    pass
                else:
                    nextnode = nextmo.data.val
                    if vaddr+len(v)>=nextnode.data.address:
                        v.data.cut(nextnode.data.address)
        Graph.add_vertex(self,v) # before support write !!
        self.support.write(vaddr,v)
        return 1

    def get_node(self,name):
        for v in self.V():
            if v.name==name: return v
        return None

