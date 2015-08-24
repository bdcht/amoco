import pytest

from amoco.system.pe import PE

def test_parser_PE(samples):
    for f in samples:
        if f[-4:]=='.exe':
            p = PE(f)

