from amoco.config import conf
from amoco.system.core import DefineLoader
from amoco.system import elf

@DefineLoader(elf.EM_ARM)
def loader_arm(p):
    from amoco.system.linux32.arm import OS
    return OS.loader(p,conf.System)

@DefineLoader(elf.EM_386)
def loader_x86(p):
    from amoco.system.linux32.x86 import OS
    return OS.loader(p,conf.System)

@DefineLoader(elf.EM_SH)
def loader_sh2(p):
    from amoco.system.linux32.sh2 import OS
    return OS.loader(p,conf.System)

