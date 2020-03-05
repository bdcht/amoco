# -*- coding: utf-8 -*-

"""
.. _backward:

backward.py
===========
The backward module of amoco implements backward CFG recovery strategies.

"""

# This code is part of Amoco
# Copyright (C) 2006-2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from .forward import *
from amoco.logger import Log
logger = Log(__name__)
logger.debug('loading module')

class fbackward(lforward):
    """Fast backward based analysis:
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
            :class:`target`:
              the PC expression evaluated from composition of
              *first-parent-path* symbolic maps.
        """
        pc = self.prog.cpu.PC()
        n = node
        mpc = pc
        while True:
            m = n.data.map.use((pc,n.data.address))
            mpc = m(mpc)
            T = target(mpc,node).expand()
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
            func = code.func(n.c)
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
                xpc.extend(target(cnpc,e.v[1]).expand())
            n.data.misc['func'] = func
        else:
            xpc.extend(target(mpc,node).expand())
        return xpc


# -----------------------------------------------------------------------------
class lbackward(fforward):
    """Link backward based analysis:
    a generalisation of *fast forward* where pc is evaluated by considering
    **all** paths that link to the current node.

    Note:
      This is currently the most advanced stategy for performing cfg recovery
      in amoco.
    """
    policy = {'depth-first': False, 'branch-lazy': False, 'frame-aliasing':False,
              'complexity': 100}

    def check_func(self,node):
        """Check if vtx node creates a function. In the fforward method
        this method does nothing.
        """
        if node is None: return
        for t in self.spool:
            if t.parent in node.c:
                return
        # create func object:
        f = code.func(node.c)
        alf = conf.Cas.noaliasing
        conf.Cas.noaliasing = not self.policy['frame-aliasing']
        cxl = conf.Cas.complexity
        conf.Cas.complexity = self.policy['complexity']
        SIG_FUNC.emit(args=f)
        m = f.makemap()
        # get pc @ node:
        pc = self.prog.cpu.PC()
        mpc = m(pc)
        T = target(mpc,node).expand()
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
                T.extend(target(cnpc,e.v[1]).expand())
        conf.Cas.noaliasing = alf
        conf.Cas.complexity = cxl
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
            :class:`target`:
              the PC expression evaluated from current node map.
        """
        pc = self.prog.cpu.PC()
        alf = conf.Cas.noaliasing
        cxl = conf.Cas.complexity
        conf.Cas.complexity = self.policy['complexity']
        conf.Cas.noaliasing = not self.policy['frame-aliasing']
        # make pc value explicit in every block:
        node.data.map = node.data.map.use((pc,node.data.address))
        # try fforward:
        T = super(lbackward,self).get_targets(node,parent)
        conf.Cas.noaliasing = alf
        conf.Cas.complexity = cxl
        return T

