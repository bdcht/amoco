import pytest

from amoco.system.elf import Elf32,Elf64
from amoco.system.core import DataIO

def test_parser_elf32(samples):
    for filename in samples:
        if filename[-4:]=='.elf':
            with open(filename,'rb') as f:
                p = Elf32(DataIO(f))
                assert p.Ehdr.e_ident['ELFMAG']==b'ELF'

def test_parser_elf64(samples):
    for filename in samples:
        if filename[-4:]=='.elf64':
            with open(filename,'rb') as f:
                p = Elf64(DataIO(f))
                assert p.Ehdr.e_ident['ELFMAG']==b'ELF'

