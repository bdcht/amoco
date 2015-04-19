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
                l = []
                # return block with additional platform-specific misc infos
                yield self.prog.codehelper(block=b)
        if len(l)>0:
            b = code.block(l)
            yield self.prog.codehelper(block=b)

    # getblock is a handy wrapper of iterblocks to
    # return the block located at address val provided as Python Int.
    def getblock(self,val):
        p = self.prog
        target = p.cpu.cst(val,p.cpu.PC().size)
        return next(self.iterblocks(target))

    # poorman's cfg builder that only groups blocks that belong to the
    # same function based on FUNC_START/FUNC_STOP tags heuristics.
    def getcfg(self,loc=None):
        nprev = None
        for b in self.iterblocks(loc):
            n = cfg.node(b)
            if b.misc[code.tag.FUNC_START]:
                nprev = None
            if nprev is None:
                self.G.add_vertex(n)
            else:
                self.G.add_edge(cfg.link(nprev,n))
            nprev = n

# -----------------------------------------------------------------------------
class _target(object):
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


# -----------------------------------------------------------------------------
# fast forward based analysis:
# follows PC expression evaluated within a single block only.
# exploration goes forward until expressions are not cst.
class fforward(lsweep):
    policy = {'depth-first': True, 'branch-lazy': True}

    def init_spool(self,loc):
        self.spool = [_target(loc,None)]

    def update_spool(self,vtx,parent):
        if vtx is None: return
        # if vtx was visited before targets have been added already:
        if len(vtx.e_out())>0 or vtx in (s.parent for s in self.spool):
            return
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

    def check_ext_target(self,t):
        if t.cst is None: return False
        if t.cst._is_ext:
            b = code.xfunc(t.cst)
            vtx = cfg.node(b)
            e = cfg.link(t.parent,vtx,data=t.econd)
            e = t.parent.c.add_edge(e)
            self.update_spool(e.v[1],t.parent)
            return True
        return False

    def getcfg(self,loc=None):
        try:
            for x in self.itercfg(loc): pass
        except KeyboardInterrupt:
            pass
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
            if t.dirty: continue
            parent = t.parent
            econd  = t.econd
            if self.check_ext_target(t):
                continue
            for b in self.iterblocks(loc=t.cst):
                vtx = G.get_by_name(b.name) or cfg.node(b)
                b = vtx.data
                # if block is a FUNC_START, we add it as a new graph component (no link to parent),
                # otherwise we add the new (parent,vtx) edge.
                if parent is None:
                    self.add_root_node(vtx)
                elif parent.data.misc[code.tag.FUNC_CALL]:
                    vtx = self.add_call_node(vtx,parent,econd)
                else:
                    e = cfg.link(parent,vtx,data=econd)
                    e = G.add_edge(e)
                    if e is not None:
                        logger.verbose('edge %s added'%e)
                # now we try to populate spool with target addresses of current block:
                self.update_spool(vtx,parent)
                yield vtx
                if not lazy or b.misc[code.tag.FUNC_END]: break
                logger.verbose("lsweep fallback at %s"%b.name)
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
# a generalisation of link forward where pc is evaluated by evaluating all paths
# that link to the current node.
class lbackward(fforward):
    policy = {'depth-first': False, 'branch-lazy': False, 'frame-aliasing':False}

    def update_spool(self,vtx,parent):
        if vtx is None: return
        root = vtx.c.sV[0]
        if root.data.misc['func']: return
        T = self.get_targets(vtx,parent)
        if len(T)>0:
            #self.spool.extend(filter(lambda t:t not in self.spool,T))
            self.spool.extend(T)
            return
        err = '%s analysis stopped at node %s'%(self.__class__.__name__,vtx.name)
        logger.info(err)
        vtx.data.misc['tbc'] = 1

    def get_targets(self,node,parent):
        pc = self.prog.cpu.PC()
        alf = code.mapper.assume_no_aliasing
        code.mapper.assume_no_aliasing = not self.policy['frame-aliasing']
        # try fforward first:
        T = fforward.get_targets(self,node,parent)
        if len(T)>0:
            code.mapper.assume_no_aliasing = alf
            return T
        # create func object:
        f = code.func(node.c)
        m = f.backward(node)
        if m is None:
            logger.verbose('dead end at %s'%node.name)
        else:
            m = m.use((pc,f.address))
            # get pc @ node:
            mpc = m(pc)
            T = _target(mpc,node).expand()
            # if a target is defined here, it means that func cfg is not completed
            # so we can return now :
            if len(T)>0:
                code.mapper.assume_no_aliasing = alf
                return T
        # otherwise if func cfg is complete compute pc out of function callers:
        xpc = []
        # check if a leaf is still going to be explored
        for x in f.cfg.leaves():
            if x in (s.parent for s in self.spool):
                code.mapper.assume_no_aliasing = alf
                return xpc
        # f is now fully explored so we can "return" to callers:
        logger.info('lbackward: function %s done'%f)
        # cleanup spool:
        for t in self.spool:
            if t.parent.c is f.cfg: t.dirty=True
        # if needed compute the full map:
        if f.misc['partial']: m = f.makemap()
        f.map = m
        self.prog.codehelper(func=f)
        mpc = f.map(pc)
        roots = filter(lambda n: n.data.misc[code.tag.FUNC_START],f.cfg.sV)
        if len(roots)<=0:
            code.mapper.assume_no_aliasing = alf
            return xpc
        if len(roots)>1:
            logger.verbose('lbackward: multiple entries into function %s ?!'%f)
        nroot = roots[0]
        nroot.data.misc['func'] = f
        try:
            fsym = nroot.data.misc['callers'][0].data.misc['to'].ref
        except (IndexError,TypeError,AttributeError):
            fsym = 'f'
        f.name = "%s:%s"%(fsym,nroot.name)
        for cn in nroot.data.misc['callers']:
            cnpc = cn.data.map.use((pc,cn.data.address))(mpc)
            fn = cfg.node(f)
            e = cn.c.add_edge(cfg.link(cn,fn))
            xpc.extend(_target(cnpc,e.v[1]).expand())
        code.mapper.assume_no_aliasing = alf
        return xpc

