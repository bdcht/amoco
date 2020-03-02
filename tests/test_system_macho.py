import pytest

from amoco.system.macho import *
from amoco.system.core import DataIO

def test_parser_macho(samples):
    for filename in samples:
        if filename[-7:]=='.mach-o':
            with open(filename,'rb') as f:
                p = MachO(DataIO(f))
                assert p.header.magic in (MH_MAGIC, MH_MAGIC_64)
                if 'dylib' in filename:
                    assert p.header.filetype==MH_DYLIB
                else:
                    assert p.header.filetype==MH_EXECUTE

