import pytest

from amoco.cas.expressions import *

@pytest.fixture(scope='module')
def M():
    from amoco.system.core import MemoryMap
    return MemoryMap()

@pytest.fixture
def p(x):
    return ptr(x)

def test_memory_001(M,sc1):
    M.write(0x0, sc1)
    assert len(M)==len(sc1)
    z = M._zones[None]
    assert z.range() == (0,len(sc1))
    assert len(z._map)==1
    o = z._map[0]
    assert o.data.val==sc1

def test_memory_002(M,sc1,p):
    M.write(0x0, sc1)
    M.write(p, b'A'*8)
    assert len(M._zones)==2
    # write little-endian 16 bits constant:
    M.write(p+2,cst(0x4243,16))
    assert len(M._zones)==2
    z = M._zones[p.base]
    assert len(z._map)==3
    assert M.read(p+3,1)[0]==0x42

def test_memory_003(M,sc1,p,y):
    M.write(0x0, sc1)
    M.write(p, b'A'*8)
    M.write(p+2,cst(0x4243,16))
    # overwrite string with symbolic reg y:
    M.write(cst(0x10,32), y)
    assert len(M._zones)==2
    z = M._zones[None]
    assert len(z._map)==3
    assert z._map[1].data.val==y

def test_memory_004(M,sc1,p,y):
    M.write(0x0, sc1, endian=-1)
    M.write(p, b'A'*8, endian=-1)
    M.write(p+2,cst(0x4243,16),endian=-1)
    M.write(cst(0x10,32), y, endian=-1)
    # test big endian cases:
    z = M._zones[p.base]
    assert M.read(p+3,1)[0]==0x43
    res = M.read(cst(0x12,32),4)
    assert res[0] == y[0:16]
    assert res[1] == b'\xc0@'
    res = M.read(p,6)
    assert res[0]==res[2]==b'AA'
    M.write(cst(0x12,32),p.base,endian=-1)
    res = M.read(cst(0x10,32),8)
    assert res[0]==y[16:32]
    assert res[1]==p.base
    assert res[2]==b'\xcd\x80'

def test_pickle_memorymap(a,m):
    from pickle import dumps,loads,HIGHEST_PROTOCOL
    pickler = lambda x: dumps(x,HIGHEST_PROTOCOL)
    m[mem(a,32)] = cst(0xcafebabe,32)
    p = pickler(m.mmap)
    M = loads(p)
    parts = M.read(ptr(a+1),2)
    assert len(parts)==1
    assert parts[0]==cst(0xfeba,16)



