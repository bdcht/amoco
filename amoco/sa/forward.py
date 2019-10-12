# -*- coding: utf-8 -*-

"""
.. _forward:

forward.py
==========
The forward module of amoco implements simple strategies to help CFG reconstruction.

The *fast forward* method (:class:`fforward`) strictly follows the instruction
flow. It relies on *linear sweep* to produce a block of instructions but proceeds to
the next block by disassembling instructions located at the program's
counter address *iff* this address is a :class:`cas.expressions.cst`.
Even if for most functions's *inner* blocks this address is indeed a constant, this
method generally discovers only very small parts of the control flow due to its
inhability to deal with interprocedural flow.
This class however provides the generic method :meth:`itercfg` to its parent classes
and introduces the use of :class:`target` objects as locations of next blocks.

The *link forward* method (:class:`lforward`) extends *fast forward* in order
to assume that function calls always return to the *link address* of the call.
"""

# This code is part of Amoco
# Copyright (C) 2006-2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .lsweep import *

logger = Log(__name__)
logger.debug('loading module')

# -----------------------------------------------------------------------------

class target(object):
    '''Candidate for extending a :class:`cfg.graph` under construction.

    A :class:`target` is an internal object used during cfg recovery to point
    to addresses that are candidates for extending the cfg with a new link or
    a new block.

    Attributes:
       cst (exp): the targeted address expression, usually a constant but can
                  be an instance of any :mod:`cas.expressions` class.
       parent (node): the basic block that targets this address
       econd (exp): the conditional expression by which the execution would
                    proceed from parent to the basic block at this address
    '''
    def __init__(self,cst,parent,econd=None):
        if cst is not None:
            cst.sf=False
        self.cst = cst
        self.parent = parent
        self.econd = econd
        self.dirty = False

    def expand(self):
        """Returns the list of constant (or external) expressions associated
        with this target.
        """
        x=self.cst
        if x._is_ext:
            SIG_TRGT.emit(args=self)
            return [self]
        if x._is_cst:
            SIG_TRGT.emit(args=self)
            return [self]
        if x._is_vec:
            l = []
            for e in x.l:
                l.extend(target(e,self.parent,self.econd).expand())
            return l
        if x._is_tst:
            ltrue  = self.select(True).expand()
            lfalse = self.select(False).expand()
            return ltrue+lfalse
        return []

    def select(self,side):
        """Returns the target of the selected ``True`` or ``False`` *side* of
        the current conditional branch target expression.
        """
        x=self.cst
        assert x._is_tst
        v = x.l if side is True else x.r
        econd = self.econd or []
        econd.append(x.tst==side)
        return target(v,self.parent,econd)

    def __eq__(self,t):
        return (self.cst==t.cst and self.parent==t.parent)

    def __repr__(self):
        pfx = 'dirty ' if self.dirty else ''
        cnd = [str(x) for x in (self.econd or [])]
        parent = self.parent
        if parent is not None: parent = parent.name
        return '<%starget %s by %s %s>'%(pfx,self.cst,parent,cnd)


# -----------------------------------------------------------------------------

class fforward(lsweep):
    """The fast forward based analysis follows the :meth:`PC` expression evaluated
    within a single block only. Exploration goes forward until expressions
    are not :class:`~cas.expressions.cst`. This class is a base for most of the
    main analysis classes.

    Attributes:
        policy (dict): holds various useful parameters for the analysis.

                   * 'depth-first' : walk the graph with *depth-first* policy if True.
                   * 'branch-lazy' : proceed with linear sweep whenever the target \
                           expression does not evaluate to a constant address.
                   * 'frame-aliasing' : assume no pointer aliasing if False.
                   * 'complexity' : limit expressions complexity.

        spool (list[target]): the list of current targets to extend the
            :class:`cfg.graph`.

    """
    policy = {'depth-first': True, 'branch-lazy': True}

    def init_spool(self,loc):
        self.spool = [target(loc,None)]

    def update_spool(self,vtx,parent):
        T = self.get_targets(vtx,parent)
        if len(T)>0:
            if vtx.misc['tbc']:
                del vtx.misc['tbc']
            self.spool.extend(T)
            return
        err = '%s analysis stopped at node %s'%(self.__class__.__name__,vtx.name)
        logger.info(err)
        vtx.misc['tbc'] = 1

    def get_targets(self,node,parent):
        """Computes expression of target address in the given node, based
        on its address and the architecture's program counter (PC).

        Arguments:
            node: the current node, not yet added to the cfg.
            parent: the parent node in the cfg that has targeted the
                current node. (Unused by :class:`fforward` but required as
                a generic API for parent classes).

        Returns:
            :class:`target`: the evaluated PC expression.
        """
        m = code.mapper()
        pc = self.prog.cpu.PC()
        m[pc] = node.data.address
        pc = (node.map(pc)).eval(m)
        return target(pc,node).expand()

    def add_root_node(self,vtx):
        """The given vertex node (vtx) is added as a root node of a new connected
        component in the cfg referenced by :attr:`self.G`.
        """
        vtx.misc[code.tag.FUNC_START]=1
        vtx.misc['callers'] = []
        self.G.add_vertex(vtx)
        logger.verbose('root node %s added'%vtx.name)

    def add_call_node(self,vtx,parent,econd):
        """When a (parent) block performs a call, the (vtx) targeted block
        will not be linked with its parent but rather will possibly start a
        new connected component of the cfg. When the component is declared
        as a function, the parent block is linked to a new node that embeds
        the function instead.
        """
        callers = vtx.misc['callers']
        if callers:
            if parent in callers:
                for n in parent.N(+1):
                    if vtx.data.address == n.data.address: return n
                return None
            callers.append(parent)
        else:
            logger.verbose('block %s starts a new cfg component'%vtx.name)
            vtx.misc['callers']  = [parent]
        vtx.misc[code.tag.FUNC_START]+=1
        parent.misc[code.tag.FUNC_CALL] += 1
        if vtx.misc['func']:
            logger.verbose('function %s called'%b.misc['func'])
            vtx = cfg.node(vtx.misc['func'])
            e = parent.c.add_edge(cfg.link(parent,vtx,data=econd))
            vtx = e.v[1]
        else:
            vtx = self.G.add_vertex(vtx)
        return vtx

    def check_func(self,vtx):
        """check if vtx node creates a function. (In the fforward method
        this method does nothing.)
        """
        pass

    def check_ext_target(self,t):
        """Check if the :class:`target` is the address of an external function.
        If True, the :class:`code.xfunc` node is linked to the parent
        and the spool is updated with this node.

        Returns:
            `True` if target is external, `False` otherwise.
        """
        if t.cst is None: return False
        if t.cst._is_ext:
            b = code.xfunc(t.cst)
            vtx = cfg.node(b)
            e = cfg.link(t.parent,vtx,data=t.econd)
            e = t.parent.c.add_edge(e)
            self.update_spool(e.v[1],t.parent)
            self.check_func(e.v[1])
            return True
        return False

    def getcfg(self,loc=None,debug=False):
        """The getcfg method is the cfg recovery method of any analysis
        class.

        Arguments:
            loc (Optional[cst]): the address expression of the cfg root node
                (defaults to the program's entrypoint).
            debug (bool): A python debugger :func:`set_trace()` call is
                emitted at every node added to the cfg.
                (Default to False.)
        """
        if debug:
            import pdb
            pdb.set_trace()
        try:
            for x in self.itercfg(loc):
                pass
        except KeyboardInterrupt:
            pass
        return self.G

    def itercfg(self,loc=None):
        """A generic *forward* analysis explorer. The default policy
        is *depth-first* search (use policy=0 for breadth-first search.)
        The ret instructions are not followed (see lbackward analysis).

        Arguments:
            loc (Optional[cst]): the address to start the cfg recovery
                (defaults to the program's entrypoint).

        Yields:
            :class:`cfg.node`: every nodes added to the graph.
        """
        G = self.G
        # spool is the list of targets (target_ instances) to be analysed
        self.init_spool(loc)
        # order is the index to pop elements from spool
        order = -1 if self.policy['depth-first'] else 0
        # lazy is a flag to fallback to linear sweep
        lazy  = self.policy['branch-lazy']
        # proceed with exploration of every spool element:
        while len(self.spool)>0:
            t = self.spool.pop(order)
            parent = t.parent
            econd  = t.econd
            if self.check_ext_target(t):
                continue
            for b in self.iterblocks(loc=t.cst):
                vtx = G.get_by_name(b.name) or cfg.node(b)
                do_update = (vtx not in G)
                # if block is a FUNC_START, we add it as a new graph component (no link to parent),
                # otherwise we add the new (parent,vtx) edge.
                if parent is None:
                    self.add_root_node(vtx)
                elif parent.misc[code.tag.FUNC_CALL]:
                    vtx = self.add_call_node(vtx,parent,econd)
                else:
                    if parent.misc['cut']: continue
                    e_ = cfg.link(parent,vtx,data=econd)
                    e  = G.add_edge(e_)
                    if e is e_:
                        logger.verbose(u'edge %s added'%e)
                # now we try to populate spool with target addresses of current block:
                if do_update:
                    self.update_spool(vtx,parent)
                self.check_func(vtx)
                yield vtx
                if (not do_update or not lazy or
                   vtx.misc[code.tag.FUNC_END]): break
                logger.verbose(u"lsweep fallback at %s"%vtx.data.address)
                parent = vtx
                econd  = None

# -----------------------------------------------------------------------------

class lforward(fforward):
    """Link forward based analysis:
    follows PC expression evaluated with parent block mapping.
    Exploration goes forward until expressions are not cst.
    """
    policy = {'depth-first': True, 'branch-lazy': False}

    def get_targets(self,node,parent):
        """Computes expression of target address in the given node, based
        on its parent address and symbolic map, using the architecture's
        program counter (PC).

        Arguments:
            node: the current node, not yet added to the cfg.
            parent: the parent node in the cfg that has targeted the
                current node.

        Returns:
            :class:`target`:
               the PC expression evaluated from the parent
               symbolic map and the current node's map.
        """
        pc = self.prog.cpu.PC()
        if parent is None:
            pc = node.map.use((pc,node.data.address))(pc)
        else:
            m = parent.map.use((pc,parent.data.address)) # work on copy
            m[pc] = node.data.address
            pc = m(node.map(pc))
        return target(pc,node).expand()


