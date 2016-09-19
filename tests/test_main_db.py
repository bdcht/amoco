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

