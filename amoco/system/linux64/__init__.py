from amoco.config import conf
from amoco.system.core import DefineLoader
from amoco.system import elf


@DefineLoader("elf", elf.EM_X86_64)
def loader_x64(p):
    from amoco.system.linux64.x64 import OS

    return OS.loader(p, conf.System)


@DefineLoader("elf", elf.EM_AARCH64)
def loader_aarch64(p):
    from amoco.system.linux64.aarch64 import OS

    return OS.loader(p, conf.System)
