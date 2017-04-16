import pytest

from amoco.system.core import DataIO
from amoco.system.raw import RawExec

def test_raw_001(samples):
    for f in samples:
        if f[-4:]=='.raw':
            p = RawExec(DataIO(open(f,'rb')))

def test_raw_002(sc1):
    p = RawExec(DataIO(sc1))

