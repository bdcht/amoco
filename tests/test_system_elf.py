import pytest

from amoco.system.elf import Elf32,Elf64

def test_parser_elf32(samples):
    for f in samples:
        if f[-4:]=='.elf':
            p = Elf32(f)
            assert p.Ehdr.e_ident['ELFMAG']=='ELF'

def test_parser_elf64(samples):
    for f in samples:
        if f[-4:]=='.elf64':
            p = Elf64(f)
            assert p.Ehdr.e_ident['ELFMAG']=='ELF'

