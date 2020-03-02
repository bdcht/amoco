from amoco.config import conf
from amoco.system.core import DefineLoader
from amoco.system import macho

@DefineLoader(macho.X86_64)
def loader_osx(p):
    from amoco.system.osx.x64 import OS
    return OS.loader(p,conf.System)

