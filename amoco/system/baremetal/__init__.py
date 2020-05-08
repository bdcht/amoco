from amoco.system.core import DefineLoader,logger
from amoco.system import elf


@DefineLoader("elf", elf.EM_AVR)
def loader_avr(p):
    from amoco.system.baremetal.avr import ELF
    logger.info("baremetal/avr firmware loaded")
    return ELF(p)


@DefineLoader("elf", elf.EM_SPARC)
def loader_sparc(p):
    from amoco.system.baremetal.leon2 import ELF
    logger.info("baremetal/leon2 firmware loaded")
    return ELF(p)


@DefineLoader("elf", elf.EM_RISCV)
def loader_riscv(p):
    from amoco.system.baremetal.riscv import ELF
    logger.info("baremetal/riscv firmware loaded")
    return ELF(p)
