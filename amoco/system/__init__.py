# -*- coding: utf-8 -*-

from . import core
from . import raw

def load_program(f,cpu=None):
    '''
    Detects program format header (ELF/PE), and *maps* the program in abstract
    memory, loading the associated "system" (linux/win) and "arch" (x86/arm),
    based header informations.

    Arguments:
        f (str): the program filename or string of bytes.

    Returns:
        an ELF/CoreExec, PE/CoreExec or RawExec system instance
    '''

    from . import linux32
    from . import linux64
    from . import win32
    from . import win64
    from . import osx
    from . import baremetal

    p = core.read_program(f)
    Loaders = core.DefineLoader.LOADERS
    if p.is_ELF:
        try:
            x = Loaders[p.Ehdr.e_machine](p)
        except KeyError:
            core.logger.error(u'ELF machine type not supported:\n%s'%p.Ehdr)
            x = None
    elif p.is_PE:
        try:
            x = Loaders[p.NT.Machine](p)
        except KeyError:
            core.logger.error(u'PE machine type not supported:\n%s'%p.NT)
            x = None
    elif p.is_MachO:
        try:
            x = Loaders[p.header.cputype](p)
        except KeyError:
            core.logger.error(u'Mach-O machine type not supported:\n%s'%p.header.cputype)
            x = None
    else:
        x = Loaders['raw'](p,cpu)
    return x
