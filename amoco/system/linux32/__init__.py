from amoco.config import conf
from amoco.system.core import DefineLoader,logger
from amoco.system import elf


@DefineLoader("elf", elf.EM_ARM)
def loader_arm(p):
    from amoco.system.linux32.arm import OS
    logger.info("linux32/armv7 task loaded")
    return OS.loader(p, conf.System)


@DefineLoader("elf", elf.EM_386)
def loader_x86(p):
    from amoco.system.linux32.x86 import OS
    logger.info("linux32/x86 task loaded")
    return OS.loader(p, conf.System)


@DefineLoader("elf", elf.EM_SH)
def loader_sh2(p):
    from amoco.system.linux32.sh2 import OS
    logger.info("linux32/sh2 task loaded")
    return OS.loader(p, conf.System)
