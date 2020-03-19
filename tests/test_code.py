import pytest
import amoco
from amoco.sa import *

from pickle import dumps,loads,HIGHEST_PROTOCOL
pickler = lambda x: dumps(x,HIGHEST_PROTOCOL)

def test_block(sc1):
    p = amoco.load_program(sc1)
    p.use_x86()
    z = lsweep(p)
    ib = z.iterblocks()
    b0 = next(ib)
    assert b0._is_block
    b1 = next(ib)
    assert b1._is_block
    # test pickle:
    x = pickler(b0)
    y = pickler(b1)
    X = loads(x)
    assert len(X.instr)==1
    assert X.address==b0.address
    assert X.support==b0.support
    Y = loads(y)
    assert Y==b1
    addr = Y.instr[-2].address
    n = Y.cut(addr)
    assert len(Y.instr)==(len(b1.instr)-2)

def test_func(ploop):
    p = amoco.load_program(ploop)
    z = lsweep(p)
    # build func manually...
    fcfg = cfg.graph()
    b0 = cfg.node(z.getblock(0x804849d))
    b1 = cfg.node(z.getblock(0x80484ac))
    #b1.cut(0x80484d0)
    b2 = cfg.node(z.getblock(0x80484d0))
    b3 = cfg.node(z.getblock(0x80484d8))
    e0 = cfg.link(b0,b1)
    e1 = cfg.link(b1,b2)
    e2 = cfg.link(b2,b1)
    e3 = cfg.link(b2,b3)
    for e in (e0,e1,e2,e3):
        fcfg.add_edge(e)
    assert len(fcfg.C)==1
    # create func:
    f = code.func(fcfg.C[0])
    assert f.support==(0x804849d,0x80484e5)
    assert f.blocks==[n.data for n in f.cfg.sV]
    #s = cfg.signature(f.cfg)
    #sig = '{[(+Fcejv)] [(?Facjlv)(Fc)(-Fclr)]}'
    #assert s == sig
    # test pickle func:
    x = pickler(f)
    y = loads(x)
    assert y._is_func
    assert y.blocks==f.blocks
    assert y.support==f.support
    #assert cfg.signature(y.cfg) == sig
