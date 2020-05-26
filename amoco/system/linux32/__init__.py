from amoco.config import conf
from amoco.system.core import DefineLoader,logger
from amoco.system import elf


@DefineLoader("elf", elf.EM_ARM)
def loader_arm(p):
    from amoco.system.linux32.arm import OS
    logger.info("linux32/armv7 task loading...")
    return OS.loader(p, conf.System)


@DefineLoader("elf", elf.EM_386)
def loader_x86(p):
    from amoco.system.linux32.x86 import OS
    logger.info("linux32/x86 task loading...")
    return OS.loader(p, conf.System)


@DefineLoader("elf", elf.EM_SPARC)
def loader_sparc(p):
    from amoco.system.linux32.sparc import OS
    logger.info("linux32/sparc task loading...")
    return OS.loader(p, conf.System)


@DefineLoader("elf", elf.EM_RISCV)
def loader_sparc(p):
    from amoco.system.linux32.riscv import OS
    logger.info("linux32/riscv task loading...")
    return OS.loader(p, conf.System)


@DefineLoader("elf", elf.EM_SH)
def loader_sh2(p):
    from amoco.system.linux32.sh2 import OS
    logger.info("linux32/sh2 task loading...")
    return OS.loader(p, conf.System)

@DefineLoader("elf", elf.EM_MIPS)
def loader_sh2(p):
    from amoco.system.linux32.mips_le import OS
    logger.info("linux32/mips_le task loading...")
    return OS.loader(p, conf.System)
