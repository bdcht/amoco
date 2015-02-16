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
                loc = m(p.PC())
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
        target = p.cpu.cst(val,p.PC().size)
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

    def expand(self):
        if self.cst._is_ext:
            return [self]
        if self.cst._is_cst:
            return [self]
        if self.cst._is_tst:
            ltrue  = self.select(True).expand()
            lfalse = self.select(False).expand()
            return ltrue+lfalse
        return []

    def select(self,side):
        assert self.cst._is_tst
        x = self.cst.l if side is True else self.cst.r
        econd = self.econd or []
        econd.append(self.cst.tst==side)
        return _target(x,self.parent,econd)


# -----------------------------------------------------------------------------
# fast forward based analysis:
# follows PC expression evaluated within a single block only.
# exploration goes forward until expressions are not cst.
class fforward(lsweep):
    policy = {'depth-first': True, 'branch-lazy': True}

    def init_spool(self,loc):
        return [_target(loc,None)]

    def update_spool(self,spool,vtx,parent):
        T = self.get_targets(vtx,parent)
        if len(T)>0:
            spool.extend(T)
            return
        err = '%s analysis stopped at %s'%(self.__class__.__name__,vtx)
        logger.info(err)
        vtx.data.misc['tbc'] = 1

    # compute expression of target address (PC) in node.data.map
    def get_targets(self,node,parent):
        blk = node.data
        m = code.mapper()
        pc = self.prog.PC()
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
        b.misc[code.tag.FUNC_START]+=1
        parent.data.misc[code.tag.FUNC_CALL] += 1
        try:
            b.misc['callers'] += [parent]
        except TypeError:
            b.misc['callers']  = [parent]
        if b.misc['func']:
            logger.verbose('function %s called'%b.misc['func'])
            vtx = cfg.node(b.misc['func'])
            e = cfg.link(parent,vtx,data=econd)
            self.G.add_edge(e)
        else:
            self.G.add_vertex(vtx)
            logger.verbose('block %s starts a new cfg component'%vtx.name)
        return vtx

    def check_ext_target(self,t,spool):
        if t.cst is None: return False
        if t.cst._is_ext:
            b = code.xfunc(t.cst)
            vtx = cfg.node(b)
            e = cfg.link(t.parent,vtx,data=t.econd)
            self.G.add_edge(e)
            self.update_spool(spool,vtx,t.parent)
            return True
        return False

    # generic 'forward' analysis explorer.
    # default explore policy is depth-first search (use policy=0 for breadth-first search.)
    # return instructions are not followed (see lbackward analysis).
    def getcfg(self,loc=None):
        G = self.G
        # spool is the list of (target,parent) addresses to be analysed
        spool = self.init_spool(loc)
        # order is the index to pop elements from spool
        order = -1 if self.policy['depth-first'] else 0
        # lazy is a flag to fallback to linear sweep
        lazy  = self.policy['branch-lazy']
        # proceed with exploration of every spool element:
        while len(spool)>0:
            t = spool.pop(order)
            parent = t.parent
            econd  = t.econd
            if self.check_ext_target(t,spool): continue
            for b in self.iterblocks(loc=t.cst):
                vtx = G.get_node(b.name) or cfg.node(b)
                b = vtx.data
                # if block is a FUNC_START, we add it as a new graph component (no link to parent),
                # otherwise we add the new (parent,vtx) edge.
                if parent is None:
                    self.add_root_node(vtx)
                elif parent.data.misc[code.tag.FUNC_CALL]:
                    vtx = self.add_call_node(vtx,parent,econd)
                else:
                    e = cfg.link(parent,vtx,data=econd)
                    G.add_edge(e)
                    logger.verbose('edge %s added'%e)
                # if vtx was visited before targets have been added already:
                if len(vtx.e_in())>1: break
                # now we try to populate spool with target addresses of current block:
                self.update_spool(spool,vtx,parent)
                if not lazy or b.misc[code.tag.FUNC_END]: break
                logger.verbose("lsweep fallback at %s"%b.name)
                parent = vtx
                econd  = None
        return G

# -----------------------------------------------------------------------------
# link forward based analysis:
# follows PC expression evaluated with parent block mapping.
# Exploration goes forward until expressions are not cst.
class lforward(fforward):
    policy = {'depth-first': True, 'branch-lazy': False}

    def get_targets(self,node,parent):
        blk = node.data
        pc = self.prog.PC()
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
        pc = self.prog.PC()
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
                cfg.link(cn,f,connect=True)
                xpc.extend(_target(cnpc,f).expand())
            n.data.misc['func'] = func
        else:
            xpc.extend(_target(mpc,node).expand())
        return xpc


