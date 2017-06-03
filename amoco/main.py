# -*- coding: utf-8 -*-

"""
.. _main:

main.py
=======
The main module of amoco implements various strategies to perform CFG recovery.

.. inheritance-diagram:: main
   :parts: 1

"""

# This code is part of Amoco
# Copyright (C) 2006-2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.logger import Log, set_debug,set_quiet,set_log_all
logger = Log(__name__)

from amoco import cfg
from amoco import code
from amoco import system

from amoco.arch.core import INSTRUCTION_TYPES

# -----------------------------------------------------------------------------
class lsweep(object):
    """linear sweep based analysis: fast & dumb way of disassembling prog,
    but provides :meth:`iterblocks` for all parent classes.

    Arguments:
        prog: the :class:`system.core.CoreExec` inherited program's instance
              to analyze.

    Attributes:
        prog: the :class:`system.core.CoreExec` inherited program's instance
              to analyze.
        G (graph): the placeholder for the recovered :class:`cfg.graph`.
    """
    __slots__ = ['prog','G']
    def __init__(self,prog):
        self.prog = prog
        self.G = cfg.graph()

    def sequence(self,loc=None):
        """iterator over linearly sweeped instructions.

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
                m = p.initenv()
                loc = m(p.cpu.PC())
            except (TypeError,ValueError):
                loc = 0
        while True:
            i = p.read_instruction(loc)
            if i is None: raise StopIteration
            loc += i.length
            yield i

    def iterblocks(self,loc=None):
        """iterator over basic blocks. The :attr:`instruction.type`
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
        inblock = (lambda i: INSTRUCTION_TYPES[i.type]!='control_flow')
        l = []
        seq = self.sequence(loc)
        for i in seq:
            if inblock(i):
                l.append(i)
            else:
                # add branching instruction inside block:
                l.append(i)
                # check if branch is delayed (e.g. sparc)
                # if so, include next (delay slot) instruction
                if i.misc['delayed']:
                    try:
                        l.append(next(seq))
                    except StopIteration:
                        logger.warning(u'no instruction in delay slot')
                # create block instance:
                b = code.block(l)
                b.misc['cfi'] = i
                l = []
                # return block with additional platform-specific misc infos
                b=self.prog.codehelper(block=b)
                yield b
        if len(l)>0:
            b = code.block(l)
            b=self.prog.codehelper(block=b)
            yield b

    def getblock(self,val):
        """getblock is just a wrapper of iterblocks to
        return the first block located at a *Python Integer* provided address.
        """
        p = self.prog
        target = p.cpu.cst(val,p.cpu.PC().size)
        ib = self.iterblocks(target)
        b = next(ib)
        ib.close()
        return b

    @property
    def functions(self):
        """provides the list of functions recovered so far.
        """
        F = []
        for c in self.G.C:
            f = c.sV[0].data.misc['func']
            if f: F.append(f)
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

    def getcfg(self,loc=None):
        """the most basic cfg recovery method: it assumes that calls always
        return to the following block, and links blocks based on direct
        concrete targets without computing any symbolic map.
        Its *fast* but probably very wrong...
        """
        from collections import OrderedDict,defaultdict
        D = OrderedDict()
        C = defaultdict(lambda: [])
        for b in self.iterblocks(loc):
            n = cfg.node(b)
            D[n.data.address] = n
        # now we have collected an overapprox. of all blocks,
        # lets link those "super-blocks" together:
        while len(D)>0:
            k,n = D.popitem(last=False)
            # add node (does nothing if n is already in G)
            n = self.G.add_vertex(n)
            b = n.data
            # find its links:
            if b.misc[code.tag.FUNC_CALL]:
                aret = b.misc['retto']+0
                nret = D.get(aret,None) or self.G.get_with_address(aret)
                if nret is not None:
                    e = cfg.link(n,nret)
                    self.G.add_edge(e)
                    ato  = b.misc['to']
                    if ato is not 0 and b.misc[code.tag.FUNC_CALL]>0:
                        C[ato+0].append((e,code.tag.FUNC_CALL))
            elif b.misc[code.tag.FUNC_GOTO] and b.misc['to'] is not 0:
                ato = b.misc['to']+0
                nto = D.get(ato,None) or self.G.get_with_address(ato)
                if nto is not None:
                    e = cfg.link(n,nto)
                    self.G.add_edge(e)
                else:
                    C[ato].append((n,'to'))
                if b.misc['cond']:
                    ato = n.data.support[1]
                    nto = D.get(ato,None) or self.G.get_with_address(ato)
                    if nto is not None:
                        e = cfg.link(n,nto,data=b.misc['cond'][1])
                        self.G.add_edge(e)
                    else:
                        C[ato].append((n,b.misc['cond']))
        # now all super-blocks have been processed, but some may need
        # to be cut, lets handle those missed targets:
        while len(C)>0:
            ato,L = C.popitem()
            ib = self.iterblocks(ato)
            n = cfg.node(next(ib))
            ib.close()
            n = self.G.add_vertex(n)
            for (p,why) in L:
                if why is code.tag.FUNC_CALL:
                    if n.data.misc['callers']:
                        n.data.misc['callers'].append(p)
                    else:
                        n.data.misc['callers']=[p]
                else:
                    e = cfg.link(p,n)
                    self.G.add_edge(e)
        # finally create func objects and insert nodes:
        for n in self.G.V():
            if n.data.misc['callers']:
                n.data.misc['func'] = f = code.func(n.c)
                calls = []
                for e in n.data.misc['callers']:
                    fn = cfg.node(f)
                    p = e.v[0]
                    p.c.add_edge(cfg.link(p,fn))
                    p.c.add_edge(cfg.link(fn,e.v[1]))
                    p.c.remove_edge(e)
                    calls.append(p)
                n.data.misc['callers'] = calls
        return self.G

# -----------------------------------------------------------------------------

class _target(object):
    ''' Candidate for extending a :class:`cfg.graph` under construction.

    A :class:`_target` is an internal object used during cfg recovery to point
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
            return [self]
        if x._is_cst:
            return [self]
        if x._is_vec:
            l = []
            for e in x.l:
                l.extend(_target(e,self.parent,self.econd).expand())
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
        return _target(v,self.parent,econd)

    def __eq__(self,t):
        return (self.cst==t.cst and self.parent==t.parent)

    def __repr__(self):
        pfx = 'dirty ' if self.dirty else ''
        cnd = [str(x) for x in (self.econd or [])]
        parent = self.parent
        if parent is not None: parent = parent.name
        return '<%s_target %s by %s %s>'%(pfx,self.cst,parent,cnd)


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

        spool (list[_target]): the list of current targets to extend the
            :class:`cfg.graph`.

    """
    policy = {'depth-first': True, 'branch-lazy': True}

    def init_spool(self,loc):
        self.spool = [_target(loc,None)]

    def update_spool(self,vtx,parent):
        T = self.get_targets(vtx,parent)
        if len(T)>0:
            if vtx.data.misc['tbc']:
                del vtx.data.misc['tbc']
            self.spool.extend(T)
            return
        err = '%s analysis stopped at node %s'%(self.__class__.__name__,vtx.name)
        logger.info(err)
        vtx.data.misc['tbc'] = 1

    def get_targets(self,node,parent):
        """Computes expression of target address in the given node, based
        on its address and the architecture's program counter (PC).

        Arguments:
            node: the current node, not yet added to the cfg.
            parent: the parent node in the cfg that has targeted the
                current node. (Unused by :class:`fforward` but required as
                a generic API for parent classes).

        Returns:
            :class:`_target`: the evaluated PC expression.
        """
        blk = node.data
        m = code.mapper()
        pc = self.prog.cpu.PC()
        m[pc] = blk.address
        pc = (blk.map(pc)).eval(m)
        return _target(pc,node).expand()

    def add_root_node(self,vtx):
        """The given vertex node (vtx) is added as a root node of a new connected
        component in the cfg referenced by :attr:`self.G`.
        """
        vtx.data.misc[code.tag.FUNC_START]=1
        vtx.data.misc['callers'] = []
        self.G.add_vertex(vtx)
        logger.verbose('root node %s added'%vtx.name)

    def add_call_node(self,vtx,parent,econd):
        """When a (parent) block performs a call, the (vtx) targeted block
        will not be linked with its parent but rather will possibly start a
        new connected component of the cfg. When the component is declared
        as a function, the parent block is linked to a new node that embeds
        the function instead.
        """
        b = vtx.data
        callers = b.misc['callers']
        if callers:
            if parent in callers:
                for n in parent.N(+1):
                    if vtx.data.address == n.data.address: return n
                return None
            callers.append(parent)
        else:
            logger.verbose('block %s starts a new cfg component'%vtx.name)
            b.misc['callers']  = [parent]
        b.misc[code.tag.FUNC_START]+=1
        parent.data.misc[code.tag.FUNC_CALL] += 1
        if b.misc['func']:
            logger.verbose('function %s called'%b.misc['func'])
            vtx = cfg.node(b.misc['func'])
            e = parent.c.add_edge(cfg.link(parent,vtx,data=econd))
            vtx = e.v[1]
        else:
            vtx = self.G.add_vertex(vtx)
        return vtx

    def check_func(self,vtx):
        """check if vtx node creates a function. In the fforward method
        this method does nothing.
        """
        pass

    def check_ext_target(self,t):
        """check if the target is the address of an external function.
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
            loc (Optional[cst]): the address to start the cfg recovery
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
        # spool is the list of (target,parent) addresses to be analysed
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
                elif parent.data.misc[code.tag.FUNC_CALL]:
                    vtx = self.add_call_node(vtx,parent,econd)
                else:
                    if parent.data.misc['cut']: continue
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
                   vtx.data.misc[code.tag.FUNC_END]): break
                logger.verbose(u"lsweep fallback at %s"%vtx.data.name)
                parent = vtx
                econd  = None

# -----------------------------------------------------------------------------

class lforward(fforward):
    """link forward based analysis:
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
            :class:`_target`:
               the PC expression evaluated from the parent
               symbolic map and the current node's map.
        """
        blk = node.data
        pc = self.prog.cpu.PC()
        if parent is None:
            pc = blk.map.use((pc,blk.address))(pc)
        else:
            m = parent.data.map.use((pc,parent.data.address)) # work on copy
            m[pc] = blk.address
            pc = m(blk.map(pc))
        return _target(pc,node).expand()


# -----------------------------------------------------------------------------
class fbackward(lforward):
    """fast backward based analysis:
    a generalisation of *link forward* where pc is evaluated backwardly by taking
    the *first-parent-node* path until no parent exists (entry of a function).
    *fbackward* is the first class to instanciate :class:`code.func` objects.

    Note:
      The 'frame_aliasing' policy indicates wether memory aliasing of pc expression
      outside of the function frame can occur or if the frame is assumed to be clean.
      Default frame-aliasing is set to False (assume no aliasing) otherwise any
      function that writes in memory results in potential aliasing (say for an arch
      that uses a memory stack for storing return addresses).
    """
    policy = {'depth-first': True, 'branch-lazy': False, 'frame-aliasing':False}

    def get_targets(self,node,parent):
        """Computes expression of target address in the given node, based
        on backward evaluation of all *first-parent* symbolic maps, until the
        program counter (PC) expression is a constant or the function entry block
        is reached.

        Arguments:
            node: the current node, not yet added to the cfg.
            parent: the parent node in the cfg that has targeted the
                current node.

        Returns:
            :class:`_target`:
              the PC expression evaluated from composition of
              *first-parent-path* symbolic maps.
        """
        pc = self.prog.cpu.PC()
        n = node
        mpc = pc
        while True:
            m = n.data.map.use((pc,n.data.address))
            mpc = m(mpc)
            T = _target(mpc,node).expand()
            if len(T)>0: return T
            try:
                n = n.N(-1)[0] # get first parent node (parent arg is unused)
            except IndexError:
                break # we are at function entry node
        # create func nodes:
        xpc = []
        if n.data.misc[code.tag.FUNC_START]:
            if node.data.misc[code.tag.FUNC_END]:
                n.data.misc[code.tag.FUNC_START] += 1
            try:
                fsym = n.data.misc['callers'][0].data.misc['to'].ref
            except (IndexError,TypeError,AttributeError):
                fsym = 'f'
            func = code.func(n.c,name="%s:%s"%(fsym,n.name))
            logger.verbose("function %s created"%func)
            if mpc._is_mem and len(mpc.mods)>0:
                pol = '(assume_no_aliasing)' if self.policy['frame-aliasing']==False else ''
                logger.verbose("pc is memory aliased in %s %s"%(str(func),pol))
                if self.policy['frame-aliasing']==False: mpc.mods = []
            func.map[pc] = mpc
            for cn in n.data.misc['callers']:
                cnpc = cn.data.map.use((pc,cn.data.address))(mpc)
                f = cfg.node(func)
                e = cn.c.add_edge(cfg.link(cn,f))
                xpc.extend(_target(cnpc,e.v[1]).expand())
            n.data.misc['func'] = func
        else:
            xpc.extend(_target(mpc,node).expand())
        return xpc


# -----------------------------------------------------------------------------
class lbackward(fforward):
    """link backward based analysis:
    a generalisation of *fast forward* where pc is evaluated by considering
    **all** paths that link to the current node.

    Note:
      This is currently the most advanced stategy for performing cfg recovery
      in amoco.
    """
    policy = {'depth-first': False, 'branch-lazy': False, 'frame-aliasing':False,
              'complexity': 30}

    def check_func(self,node):
        """check if vtx node creates a function. In the fforward method
        this method does nothing.
        """
        if node is None: return
        for t in self.spool:
            if t.parent in node.c:
                return
        # create func object:
        f = code.func(node.c)
        alf = code.mapper.assume_no_aliasing
        code.mapper.assume_no_aliasing = not self.policy['frame-aliasing']
        m = f.makemap()
        # get pc @ node:
        pc = self.prog.cpu.PC()
        mpc = m(pc)
        T = _target(mpc,node).expand()
        # if a target is defined here, it means that func cfg is not completed
        # so we can return now :
        if len(T)>0:
            logger.verbose('extending cfg of %s (new target found)'%f)
            for t in T:
                for k,v in f.misc['heads'].items():
                    if v(pc)==t.cst: t.parent = k
        else:
            logger.info('lbackward: function %s done'%f)
            f.map = m
            #self.prog.codehelper(func=f)
            mpc = f.map(pc)
            roots = f.view.layout.layers[0]
            assert len(roots)>0
            nroot = roots[0]
            nroot.data.misc['func'] = f
            try:
                fsym = nroot.data.misc['callers'][0].data.misc['to'].ref
            except (IndexError,TypeError,AttributeError):
                fsym = 'f'
            f.name = "%s:%s"%(fsym,nroot.name)
            self.prog.codehelper(func=f)
            for cn in nroot.data.misc['callers']:
                cnpc = cn.data.map(mpc)
                fn = cfg.node(f)
                e = cn.c.add_edge(cfg.link(cn,fn))
                logger.verbose('edge %s added'%str(e))
                T.extend(_target(cnpc,e.v[1]).expand())
        code.mapper.assume_no_aliasing = alf
        self.spool.extend(T)

    def get_targets(self,node,parent):
        """Computes expression of target address in the given node, based
        on fast-forward evaluation taking into account the expressions
        complexity and frame-aliasing parameters.

        Arguments:
            node: the current node, not yet added to the cfg.
            parent: the parent node in the cfg that has targeted the
                current node.

        Returns:
            :class:`_target`:
              the PC expression evaluated from current node map.
        """
        pc = self.prog.cpu.PC()
        alf = code.mapper.assume_no_aliasing
        cxl = code.op.threshold
        code.op.limit(self.policy['complexity'])
        code.mapper.assume_no_aliasing = not self.policy['frame-aliasing']
        # make pc value explicit in every block:
        node.data.map = node.data.map.use((pc,node.data.address))
        # try fforward:
        T = super(lbackward,self).get_targets(node,parent)
        code.mapper.assume_no_aliasing = alf
        code.op.limit(cxl)
        return T

