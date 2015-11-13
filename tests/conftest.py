import pytest

@pytest.fixture
def m():
    '''return a aliasing mapper with function scope'''
    from amoco.cas.mapper import mapper
    mapper.assume_no_aliasing = False
    return mapper()

@pytest.fixture(scope='module')
def map():
    '''return a no_aliasing mapper with module scope'''
    from amoco.cas.mapper import mapper
    mapper.assume_no_aliasing = True
    return mapper()

#------------------------------------------------------------------------------

from amoco.cas.expressions import reg
@pytest.fixture
def a():
    '''return 'a' register with default size (32)'''
    return reg('a')

@pytest.fixture
def b():
    '''return 'b' register with default size (32)'''
    return reg('b')

@pytest.fixture
def w():
    '''return 'w' 32 bits register'''
    return reg('w',32)

@pytest.fixture
def x():
    '''return 'x' 32 bits register'''
    return reg('x',32)

@pytest.fixture
def y():
    '''return 'y' 32 bits register'''
    return reg('y',32)

@pytest.fixture
def z():
    '''return 'z' 32 bits register'''
    return reg('z',32)

@pytest.fixture
def r():
    '''return 'r' 32 bits register'''
    return reg('r',32)

#------------------------------------------------------------------------------

@pytest.fixture
def sc1():
    '''return a simple x86 shellcode'''
    _sc = ("\xeb\x16\x5e\x31\xd2\x52\x56\x89\xe1\x89\xf3\x31\xc0\xb0\x0b\xcd"
           "\x80\x31\xdb\x31\xc0\x40\xcd\x80\xe8\xe5\xff\xff\xff\x2f\x62\x69"
           "\x6e\x2f\x73\x68")
    return _sc

#------------------------------------------------------------------------------

import os
samples_dir = os.path.join(os.path.dirname(__file__), 'samples')

samples_all = []

for R,D,F in os.walk(samples_dir):
    for f in F:
        filename = os.path.join(R,f)
        samples_all.append(filename)

@pytest.fixture(scope='session')
def samples():
    return samples_all

@pytest.fixture(scope='session')
def x86samples(samples):
    return filter(lambda s: 'x86/' in s, samples)

@pytest.fixture(scope='session')
def ploop(x86samples):
    for s in x86samples:
        if 'loop_simple' in s:
            return s
    return None
