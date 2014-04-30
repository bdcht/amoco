# This code is part of Amoco
# Copyright (C) 2006-2014 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

from amoco.logger import Log
logger = Log(__name__)

from amoco import cfg
from amoco import code
from amoco import system

from amoco.arch.core import INSTRUCTION_TYPES

# linear sweep based analysis.
class lsweep(object):
    __slots__ = ['prog','G']
    def __init__(self,prog):
        self.prog = prog
        self.G = {}

    # iterator over linearly sweeped instructions
    # starting at address loc (defaults to entrypoint).
    def sequence(self,loc=None):
        p = self.prog
        if loc is None:
            m = p.initenv()
            loc = m[p.PC()]
        while True:
            i = p.read_instruction(loc)
            if i is None: raise StopIteration
            loc += i.length
            yield i

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

    def getcfg(self,loc=None):
        F = []
        for b in self.iterblocks(loc):
            if b.misc[code.tag.FUNC_START]:
                f = cfg.func()
            if b.misc[code.tag.FUNC_END]:
                F.append(f)
            try:
                f.add_vertex(cfg.node(b))
            except NameError:
                logger.warning('linear sweep orfan block %s'%b.name)
                F.append(b)
        return F

# -----------------------------------------------------------------------------
# fast forward based analysis
# follows PC expression evaluated within a single block only. 
# exploration goes forward until expressions are not cst.
class fforward(lsweep):
    policy = {'depth-first': True, 'branch-lazy': True}

    def init_spool(self,loc):
        return [(loc,None)]

    def get_target(self,blk,withmap):
        # withmap unused in fforward
        m = code.mapper()
        pc = self.prog.PC()
        m[pc] = blk.address
        target = (blk.map[pc]).eval(m)
        return target.simplify()

    # generic 'forward' analysis explorer.
    # default explore policy is depth-first search (use policy=0 for breadth-first search.)
    # return instructions are not followed (see backward analysis).
    def getcfg(self,loc=None):
        spool = self.init_spool(loc)
        order = -1 if self.policy['depth-first'] else 0
        lazy  = self.policy['branch-lazy']
        F = cfg.func()
        pc = self.prog.PC()
        while len(spool)>0:
            current,parent = spool.pop(order)
            for b in self.iterblocks(loc=current):
                err = '%s analysis failed at block %s'%(self.__class__.__name__,b.name)
                sta,sto = b.support
                vtx = cfg.node(b)
                if vtx in F.V(): break
                if parent is None or (parent.data.address is None):
                    b.misc[code.tag.FUNC_START]=1
                    F.add_vertex(vtx)
                    logger.verbose('root node %s added'%vtx.name)
                else:
                    if b.misc[code.tag.FUNC_START] and parent.data.misc[code.tag.FUNC_CALL]:
                        b.misc[code.tag.FUNC_START]+=1
                        F.add_vertex(vtx)
                        logger.verbose('function node %s added'%vtx.name)
                    else:
                        e = cfg.link(parent,vtx)
                        F.add_edge(e)
                        logger.verbose('edge %s added'%e)
                # continue and update spool...
                target = self.get_target(b,withmap=parent)
                parent = vtx
                if target==sto:
                    continue
                elif target._is_cst:
                    spool.append((target,parent))
                    if not lazy: break
                elif target._is_tst:
                    t1 = target.l
                    t2 = target.r
                    if t1._is_cst:
                        spool.append((t1,parent))
                    else:
                        logger.info(err+' (true branch)')
                    if t2._is_cst:
                        spool.append((t2,parent))
                    else:
                        logger.info(err+' (false branch)')
                    break
                else:
                    logger.info(err)
                    if not lazy: break
        return F

# -----------------------------------------------------------------------------
# link forward based analysis
# follows PC expression evaluated with parent block mapping.
# exploration goes forward until expressions are not cst.
class lforward(fforward):
    policy = {'depth-first': True, 'branch-lazy': False}

    def init_spool(self,loc):
        return [(loc,cfg.node(code.block([])))]

    def get_target(self,blk,withmap):
        # use withmap for blk.map eval:
        m = withmap.data.map.use() #work on copy
        pc = self.prog.PC()
        m[pc] = blk.address
        target = (blk.map[pc]).eval(m)
        return target.simplify()

