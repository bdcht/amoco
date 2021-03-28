import pytest

from amoco.system.core import DataIO, shellcode
from amoco.system.raw import RawExec

def test_raw_001(samples):
    for filename in samples:
        if filename[-4:]=='.raw':
            with open(filename,'rb') as f:
                p = RawExec(shellcode(DataIO(f)))

def test_raw_002(sc1):
    p = RawExec(shellcode(DataIO(sc1)))

