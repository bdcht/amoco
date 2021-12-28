import pytest

from amoco.system.core import DataIO
from amoco.system.structs.HEX import HEX, HEXline, EndOfFile
from amoco.system.structs.SREC import SREC

def test_parser_hex(samples):
    for filename in samples:
        if filename[-4:]=='.hex':
            with open(filename,'rb') as f:
                p = HEX(DataIO(f))
                assert len(p.L)==163
                assert isinstance(p.L[0],HEXline)
                assert p.L[-1].HEXcode == EndOfFile

def test_parser_srec(samples):
    for filename in samples:
        if filename[-4:]=='.srec':
            with open(filename,'rb') as f:
                p = SREC(DataIO(f))
