import pytest

from amoco.system.pe import PE
from amoco.system.core import DataIO

def test_parser_PE(samples):
    for filename in samples:
        if filename[-4:]=='.exe':
            with open(filename,'rb') as f:
                p = PE(DataIO(f))

