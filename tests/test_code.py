import pytest
from amoco.main import *

from cPickle import dumps,loads,HIGHEST_PROTOCOL
pickler = lambda x: dumps(x,HIGHEST_PROTOCOL)

def test_block(sc1):
    p = system.loader.load_program(sc1)
    p.use_x86()
    z = lsweep(p)
    ib = z.iterblocks()
    b0 = next(ib)
    b1 = next(ib)
    b1.map
    # test pickle block:
    x = pickler(b0)
    y = pickler(b1)
    X = loads(x)
    assert len(X.instr)==1
    Y = loads(y)
    assert Y.map.inputs()[0]==code.mem(code.reg('esp',32),32)

def test_func(ploop):
    p = system.loader.load_program(ploop)
    z = lbackward(p)
    z.getcfg(code.cst(0x804849d,32))
    f = z.functions()[0]
    s = cfg.signature(f.cfg)
    sig = '{[(+Fcejv)] [(?Facjlv)(?Facjv)(-Fclr)]}'
    assert s == sig
    # test pickle func:
    x = pickler(f)
    y = loads(x)
    assert cfg.signature(y.cfg) == sig
