import pytest

from amoco.system.core import DataIO
from amoco.system.raw import RawExec

def test_raw_001(samples):
    for f in samples:
        if f[-4:]=='.raw':
            p = RawExec(DataIO(file(f,'rb')))

