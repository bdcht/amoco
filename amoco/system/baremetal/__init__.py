from amoco.system.core import DefineLoader
from amoco.system import elf

@DefineLoader(elf.EM_AVR)
def loader_avr(p):
    from amoco.system.baremetal.avr import ELF
    return ELF(p)

@DefineLoader(elf.EM_SPARC)
def loader_sparc(p):
    from amoco.system.baremetal.leon2 import ELF
    return ELF(p)

@DefineLoader(elf.EM_RISCV)
def loader_riscv(p):
    from amoco.system.baremetal.riscv import ELF
    return ELF(p)

