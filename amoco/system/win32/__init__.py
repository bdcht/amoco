from amoco.config import conf
from amoco.system.core import DefineLoader
from amoco.system import pe

@DefineLoader(pe.IMAGE_FILE_MACHINE_I386)
def loader_win32(p):
    from amoco.system.win32.x86 import OS
    return OS.loader(p,conf.System)
