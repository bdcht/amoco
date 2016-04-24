# -*- coding: utf-8 -*-

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
# linear sweep based analysis:
# fast & dumb way of disassembling prog,
# but provides iterblocks() for all parent classes.
class lsweep(object):
    __slots__ = ['prog','G']
    def __init__(self,prog):
        self.prog = prog
        self.G = cfg.graph()

    # iterator over linearly sweeped instructions
    # starting at address loc (defaults to entrypoint).
    # If not None, loc argument should be a cst object.
    def sequence(self,loc=None):
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

    # iterator over basic blocks using the instruction.type attribute
    # to detect the end of block (type_control_flow). The returned block
    # object is enhanced with plateform-specific infos (see block.misc).
    def iterblocks(self,loc=None):
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
                        logger.warning('no instruction in delay slot')
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

    # getblock is a handy wrapper of iterblocks to
    # return the block located at address val provided as Python Int.
    def getblock(self,val):
        p = self.prog
        target = p.cpu.cst(val,p.cpu.PC().size)
        return next(self.iterblocks(target))

    # poorman's cfg builder that assumes calls return to next block.
    # and link blocks based on direct concrete targets without computing
    # the block semantics (map). => Fast but possibly wrong...
    def getcfg(self,loc=None):
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
            n = cfg.node(next(self.iterblocks(ato)))
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
    ''' Candidate for extending a CFG.

    A _target is an internal object used during CFG reconstruction to point
    to addresses that are candidates for extending the CFG with either new edge
    or new basic block.

    Attributes:
       cst (exp): the targeted address expression
       parent (node): the basic block that targets this address
       econd (exp): the conditional expression by which the execution would
                    proceed from parent to the basic block at this address
    '''
    def __init__(self,cst,parent,econd=None):
        self.cst = cst
        self.parent = parent
        self.econd = econd
        self.dirty = False

    def expand(self):
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
# fast forward based analysis:
# follows PC expression evaluated within a single block only.
# exploration goes forward until expressions are not cst.
class fforward(lsweep):
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

    # compute expression of target address (PC) in node.data.map
    def get_targets(self,node,parent):
        blk = node.data
        m = code.mapper()
        pc = self.prog.cpu.PC()
        m[pc] = blk.address
        pc = (blk.map(pc)).eval(m)
        return _target(pc,node).expand()

    def add_root_node(self,vtx):
        vtx.data.misc[code.tag.FUNC_START]=1
        vtx.data.misc['callers'] = []
        self.G.add_vertex(vtx)
        logger.verbose('root node %s added'%vtx.name)

    def add_call_node(self,vtx,parent,econd):
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
        pass

    def check_ext_target(self,t):
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
        if debug: import pdb
        try:
            for x in self.itercfg(loc):
                if debug: pdb.set_trace()
        except KeyboardInterrupt:
            if debug: pdb.set_trace()
        return self.G

    # generic 'forward' analysis explorer.
    # default explore policy is depth-first search (use policy=0 for breadth-first search.)
    # return instructions are not followed (see lbackward analysis).
    def itercfg(self,loc=None):
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
                elif parent.data.misc[code.tag.FUNC_CALL]>0:
                    vtx = self.add_call_node(vtx,parent,econd)
                else:
                    e_ = cfg.link(parent,vtx,data=econd)
                    e  = G.add_edge(e_)
                    if e is e_:
                        logger.verbose('edge %s added'%e)
                # now we try to populate spool with target addresses of current block:
                if do_update:
                    self.update_spool(vtx,parent)
                self.check_func(vtx)
                yield vtx
                if (not do_update or not lazy or
                   vtx.data.misc[code.tag.FUNC_END]): break
                logger.verbose("lsweep fallback at %s"%vtx.data.name)
                parent = vtx
                econd  = None

# -----------------------------------------------------------------------------
# link forward based analysis:
# follows PC expression evaluated with parent block mapping.
# Exploration goes forward until expressions are not cst.
class lforward(fforward):
    policy = {'depth-first': True, 'branch-lazy': False}

    def get_targets(self,node,parent):
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
# fast backward based analysis:
# a generalisation of link forward where pc is evaluated backwardly by taking
# the first-parent-node path until no parent exists (entry of a function)
# fbackward is the first class to instanciate code.func objects.
# The 'frame_aliasing' policy indicates wether memory aliasing of pc expression
# outside of the function frame can occur or if the frame is assumed to be clean.
# Default frame-aliasing is set to False (assume no aliasing) otherwise any
# function that writes in memory results in potential aliasing (say for an arch
# that uses a memory stack for storing return addresses).
class fbackward(lforward):
    policy = {'depth-first': True, 'branch-lazy': False, 'frame-aliasing':False}

    def get_targets(self,node,parent):
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
# link backward based analysis:
# a generalisation of link forward where pc is evaluated by considering all paths
# that link to the current node.
class lbackward(fforward):
    policy = {'depth-first': False, 'branch-lazy': False, 'frame-aliasing':False,
              'complexity': 30}

    def check_func(self,node):
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
                for k,v in f.misc['heads'].iteritems():
                    if v(pc)==t.cst: t.parent = k
        else:
            logger.info('lbackward: function %s done'%f)
            f.map = m
            self.prog.codehelper(func=f)
            mpc = f.map(pc)
            roots = f.view.layout.layers[0]
            if len(roots)>1:
                logger.verbose('lbackward: multiple entries into function %s ?!'%f)
            assert len(roots)>0
            nroot = roots[0]
            nroot.data.misc['func'] = f
            try:
                fsym = nroot.data.misc['callers'][0].data.misc['to'].ref
            except (IndexError,TypeError,AttributeError):
                fsym = 'f'
            f.name = "%s:%s"%(fsym,nroot.name)
            for cn in nroot.data.misc['callers']:
                cnpc = cn.data.map(mpc)
                fn = cfg.node(f)
                e = cn.c.add_edge(cfg.link(cn,fn))
                logger.verbose('edge %s added'%str(e))
                T.extend(_target(cnpc,e.v[1]).expand())
        code.mapper.assume_no_aliasing = alf
        self.spool.extend(T)

    def get_targets(self,node,parent):
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

