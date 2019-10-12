from amoco.config import conf
from amoco.system.core import DefineLoader
from amoco.system import pe

@DefineLoader(pe.IMAGE_FILE_MACHINE_AMD64)
def loader_win64(p):
    from amoco.system.win64.x64 import OS
    return OS.loader(p,conf.System)
