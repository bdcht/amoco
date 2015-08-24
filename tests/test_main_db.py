import pytest

import amoco
from amoco.db import Session

@pytest.fixture(scope='module')
def prog():
    p = amoco.system.loader.load_program('\x6a\x00\xff\xd0\x5f\x5b\x31\xc0\xc3')
    p.use_x86()
    return p

@pytest.fixture(scope='module')
def blocks(prog):
    z = amoco.lsweep(prog)
    ib = z.iterblocks()
    b0 = next(ib)
    b1 = next(ib)
    return (b0,b1)

def test_001_checkmaps(prog,blocks,m):
    p = prog
    b0,b1 = blocks
    m[p.cpu.eip] = p.cpu.cst(0,32)
    m01 = (b0.map>>b1.map)
    m10 = (b1.map<<b0.map)
    assert m01 == m10
    m >>= b0.map
    m >>= b1.map
    assert m[p.cpu.edi] == 4
    assert m[p.cpu.eax] == 0
    assert m[p.cpu.ebx] == 0
    t = m(p.cpu.eip).simplify()
    x = p.cpu.mem(p.cpu.esp,32)
    assert t == x

def test_002_session(tmpdir,prog,blocks):
    p = prog
    b0,b1 = blocks
    sfile = str(tmpdir.dirpath('amoco-session'))
    # create and commit:
    S = Session(sfile)
    S.add('m0',b0.map)
    S.commit()
    S.add('b1',b1)
    S.add('p',p)
    S.commit()
    S.db.close()
    # open existing and get:
    s = Session(sfile)
    if s.root:
        pcopy = s.root.get('p').build()
        b1copy = s.root.get('b1').build(pcopy.cpu)
        assert b1 == b1copy

def test_003_pickle(blocks):
    import pickle
    b0,b1 = blocks
    i = b0.instr[0]
    si = pickle.dumps(i,2)
    ii = pickle.loads(si)
    assert ii.mnemonic == 'PUSH'
    assert ii.operands[0]==0x0 and ii.length==2
