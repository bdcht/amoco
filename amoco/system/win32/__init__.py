from amoco.config import conf
from amoco.system.core import DefineLoader,logger
from amoco.system import pe


@DefineLoader("pe", pe.IMAGE_FILE_MACHINE_I386)
def loader_win32(p):
    from amoco.system.win32.x86 import OS
    logger.info("win32/x86 task loaded")
    return OS.loader(p, conf.System)
