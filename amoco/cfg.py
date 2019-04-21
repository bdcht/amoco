# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
cfg.py
======

This module provides elements to define *control flow graphs* (CFG).
It is based essentially on classes provided by the `grandalf`_ package.

.. _grandalf: https://grandalf.readthedocs.io/

"""

from amoco.logger import Log
logger = Log(__name__)

from grandalf.graphs import Vertex,Edge,Graph

from amoco.system.core import MemoryZone

#------------------------------------------------------------------------------
class node(Vertex):
    """A node is a graph vertex that embeds a :mod:`code` object.
    It extends the :ref:`Vertex <grandalf:Vertex>` class in order to compare
    nodes by their data blocks rather than their id.

    Args:
        acode : an instance of :class:`block`, :class:`func` or :class:`xfunc`.

    Attributes:
        data : the reference to the ``acode`` argument above.
        e (list[link]): inherited from `grandalf`_, the list of edges with this
            node. In amoco, edges and vertices are called links and nodes.
        c (graph_core): reference to the connected component that contains this
            node.

    Methods:
        deg(): returns the *degree* of this node (number of its links).

        N(dir=0): provides a list of *neighbor* nodes, all if *dir* parameter is 0,
            parent nodes if *dir<0*, children nodes if *dir>0*.

        e_dir(dir=0): provides a list of *links*, all if *dir* parameter is 0,
            incoming links if *dir<0*, outgoing links if *dir>0*.

        e_in(): a shortcut for ``e_dir(-1)``.

        e_out(): a shortcut for ``e_dir(+1)``.

        e_with(v): provides a *link* to or from v. Should be used with caution: if there is
            several links between current node and v this method gives the first one
            listed only, independently of the direction.

        e_to(v): provides the *link* from current node to node v.

        e_from(v): provides the *link* to current node from node v.

    """

    def __init__(self,acode):
        Vertex.__init__(self,data=acode)

    @property
    def name(self):
        """name (str): name property of the node's code object.
        """
        return self.data.name

    @property
    def view(self):
        """view : view property of the node's code object.
        """
        return self.data.view

    def __repr__(self):
        return u'<%s [%s] at 0x%x>'%(self.__class__.__name__,self.name,id(self))

    def __cmp__(self,n):
        return cmp(hash(self.data),hash(n.data))

    def __hash__(self):
        return id(self)

    def __len__(self):
        return self.data.length

    def __eq__(self,n):
        return hash(self)==hash(n)
    def __lt__(self,n):
        return hash(self)<hash(n)

    def __getitem__(self,i):
        res = node(self.data.__getitem__(i))
        return res

    def __getstate__(self):
        return (self.index,self.data)

    def __setstate__(self,state):
        self.__index,self.data = state
        self.c = None
        self.e = []

#------------------------------------------------------------------------------
class link(Edge):
    """A directed edge between two nodes. It extends :ref:`Edge <grandalf:Edge>`
    class in order to compare edges based on their data rather than id.

    Args:
        x (node) : the source node.
        y (node) : the destination node.
        w (int)  : an optional weight value, default 1.
        data     : a list of conditional expressions associated with the link.
        connect  : a flag to indicate that a new node should be automatically
                   added to the connected component of its parent/child if it
                   is defined (default False).

    Attributes:
        name : the name property returns the string composed of source and
               destination node's *addresses*.
        deg (int): 1 if source and destination are the same node, 0 otherwise.
        v (tuple[node]): inherited from `grandalf`_, the 2-tuple (source,dest)
            nodes of the link.
        feedback: a flag indicating that this link is involved in a loop,
                  used internally by `grandalf`_ layout algorithm.

    Methods:
        attach(): add current link to its :attr:`node.e` attribute list.

        detach(): remove current link from its :attr:`node.e` attribute list.

    """

    def __str__(self):
        n0 = self.v[0].name
        n1 = self.v[1].name
        c = u'?' if self.data else u'-'
        return u"%s -%s-> %s"%(n0,c,n1)

    def __repr__(self):
        return u'<%s [%s] at 0x%x>'%(self.__class__.__name__,self.name,id(self))

    @property
    def name(self):
        n0 = self.v[0].data.address
        n1 = self.v[1].data.address
        return u"%s -> %s"%(n0,n1)

    def __cmp__(self,e):
        return cmp(hash(self),hash(e))
    def __eq__(self,e):
        return hash(self)==hash(e)
    def __lt__(self,e):
        return hash(self)<hash(e)

    def __hash__(self):
        return hash(self.name)

    def __getstate__(self):
        xi,yi = (self.v[0].index,self.v[1].index)
        return (xi,yi,self.w,self.data,self.feedback)

    def __setstate__(self,state):
        xi,yi,self.w,self.data,self.feedback = state
        self._v = [xi,yi]
        self.deg = 0 if xi==yi else 1

#------------------------------------------------------------------------------
class graph(Graph):
    """a :ref:`<grandalf:Graph>` that represents a set of functions as its
    individual components.

    Args:
        V (iterable[node]) : the set of (possibly detached) nodes.
        E (iterable[link]) : the set of links of this graph.

    Attributes:
        C : the list of :class:`graph_core <grandalf:graph_core>` connected
            components of the graph.
        support (:class:`~system.core.MemoryZone`): the abstract memory zone
            holding all nodes contained in this graph.
        overlay : defaults to None, another instance of MemoryZone
            with nodes of the graph that overlap other nodes already mapped
            in :attr:`support`.

    Methods:
        get_by_name(name): get the node with the given name (as string).

        get_with_address(vaddr): get the node that contains the given *vaddr*
            :class:`~cas.expressions.cst` expression.

        signature(): returns the full signature string of all connected
            components.

        add_vertex(v,[support=None]): add node v to the graph and declare
            node support in the default MemoryZone or the overlay zone if
            provided as support argument. This method deals with a node v
            that cuts or swallows a previously added node.

        remove_vertex(v): remove node v from the graph.

        add_edge(e): add link to the graph as well as possible new nodes.

        remove_edge(e): remove the provided link.

        get_vertices_count(): a synonym for :meth:`order`.

        V(): generator of all nodes of the graph.

        E(): generator of all links of the graph.

        N(v,f_io=0): returns the neighbors of node v in direction f_io.

        path(x,y,f_io=0,hook=None):

        order(): number of nodes in the graph.

        norm(): number of links in the graph.

        deg_min(): minimum degree of nodes.

        deg_max(): maximum degree of nodes.

        deg_avg(): average degree of nodes.

        eps(): ratio of links over nodes (norm/order).

        connected(): boolean flag indicating that the graph as
            only one connected component.

        components(): synonym for attribute :attr:`C`.

    """
    def __init__(self,*args,**kargs):
        self.support = MemoryZone()
        self.overlay = None
        super(graph,self).__init__(*args,**kargs)

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
        oldblock.misc['cut'] = cutdone
        if not cutdone:
            if mz is self.overlay:
                logger.warning(u"double overlay block at %s"%vaddr)
                v = super(graph,self).add_vertex(v)
                v.data.misc[u'double-overlay'] = 1
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
            logger.verbose(u"add overlay block at %s"%vaddr)
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
                                logger.warning(u"double overlay block at %s"%vaddr)
                                v = super(graph,self).add_vertex(v)
                                v.data.misc[u'double-overlay'] = 1
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
        return u''.join([signature(g) for g in self.C])

    def to_dot(self,name=None,full=True):
        dot  = "digraph G {\n"
        dot += '    graph [orientation=landscape, labeljust=left];\n'
        dot += "    node [shape=box,fontname=monospace,fontsize=8];\n"
        if name:
            g = self.get_by_name(name).c
        else:
            g = self
        for v in g.V():
            txt = u"%s"%v.data if full else "%s [%d]"%(v.name,len(v.data.instr))
            dot += '    "%s" [label="%s"];\n'%(id(v),txt)
        for e in g.E():
            dot += '    "%s" -> "%s"'%(id(e.v[0]),id(e.v[1]))
            dot += " [style=bold];\n" if e.feedback else ';\n'
        dot += '}\n'
        return dot

#------------------------------------------------------------------------------

def signature(g):
    """compute the signature of a :ref:`graph_core <grandalf:graph_core>` component
    based on :meth:`block.sig` value of nodes in every partion of the graph.

    Returns:
        str: the signature string.
    """
    P = g.partition()
    S = []
    for p in P:
        s = []
        for n in p:
            s.append(n.data.sig())
        S.append(u''.join(s))
    return u'{[%s]}'%u'] ['.join(S)
