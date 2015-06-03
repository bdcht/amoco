# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

import importlib

from amoco.logger import Log
logger = Log(__name__)

from amoco.cas.expressions import exp
from amoco.arch.core import instruction
from amoco.system.core import CoreExec
from amoco.code import mapper,block,func,xfunc
from amoco.cfg import node,link,graph

class db_core(object):
    @staticmethod
    def dump(self):
        raise NotImplementedError
    @staticmethod
    def load(self):
        raise NotImplementedError

#------------------------------------------------------------------------------
class db_instruction(db_core):

    def __init__(self,i):
        self.address = i.address
        self.misc = dict(i.misc)
        self.bytes = i.bytes
        self.view = str(i)

    def build(self,cpu):
        i = cpu.disassemble(self.bytes)
        i.misc.update(self.misc)
        i.address = self.address
        return i

#------------------------------------------------------------------------------
class db_mapper(db_core):

    def __init__(self,m):
        self.map = [(db_exp(l),db_exp(x)) for l,x in m]
        self.conds = [db_exp(c) for c in m.conds]
        self.view = str(m)

    def build(self):
        m = mapper()
        for k,v in self.map:
            m[k.build()] = v.build()
            m.conds = [c.build() for c in self.conds]
        return m

#------------------------------------------------------------------------------
class db_block(db_core, list):

    def __init__(self,b):
        self.name = b.name
        self.misc = dict(b.misc)
        self.extend(db_instruction(i) for i in b)
        self.map = db_mapper(b.map)
        self.view = str(b)

    def build(self,cpu):
        instr = [i.build(cpu) for i in self]
        b = block(instr)
        b.map = self.map.build()
        b.misc.update(self.misc)
        return b

#------------------------------------------------------------------------------
class db_exp(db_core):

    def __init__(self,x):
        self.view = x.dumps()

    def build(self):
        return exp().loads(self.view)

#------------------------------------------------------------------------------
class db_graph(db_core):

    def __init__(self,g):
        self.nodes = [db_block(n.data) for n in g.V()]
        self.links = [(e.v[0].name,e.v[1].name) for e in g.E()]

    def build(self,cpu):
        g = graph()
        nodes = dict([(b.name,node(b.build(cpu))) for b in self.nodes])
        for l in [link(nodes[n1],nodes[n2]) for (n1,n2) in self.links]:
            g.add_edge(l)
        return g

#------------------------------------------------------------------------------
class db_exec(db_core):

    def __init__(self,p):
        self.filename = p.bin.filename
        self.format = p.bin.__class__
        self.cls = p.__class__
        self.cpu = p.cpu.__name__

    def build(self):
        f = self.format(self.filename)
        p = self.cls(f)
        p.cpu = importlib.import_module(self.cpu)
        return p


#------------------------------------------------------------------------------
try:
    import transaction
    from ZODB import DB, FileStorage
    from persistent import Persistent
except ImportError,e:
    logger.warning(e.message)

    # declare void Session class:
    class Session(object):
        _is_active = False
    def __init__(self,filename=None):
        logger.info('this session is not active')
    def add(self,key,obj):
        pass
    def commit(self):
        pass
else:

    # Session database class:
    class Session(object):
        _is_active = True

        def __init__(self,filename):
            storage = FileStorage.FileStorage(filename)
            self.db = DB(storage)
            self.conn = self.db.open()
            self.root = self.conn.root()

        def add(self,key,obj):
            self.root[key] = db_interface(obj)

        def commit(self):
            transaction.commit()

        def restore(self):
            pass

def db_interface(obj):
    if isinstance(obj,block): return db_block(obj)
    if isinstance(obj,mapper): return db_mapper(obj)
    if isinstance(obj,exp): return db_exp(obj)
    elif isinstance(obj,graph): return db_graph(obj)
    elif isinstance(obj,CoreExec): return db_exec(obj)
    else:
        logger.warning("no db interface defined for %s, using str..."%obj.__class__)
        return str(obj)

