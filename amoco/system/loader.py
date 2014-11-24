# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

from amoco.logger import *
logger = Log(__name__)

from amoco.system import elf
from amoco.system import pe

#------------------------------------------------------------------------------
# read_program is responsible of identifying the program header (ELF/PE).
# It returns an ELF or PE class instance.
# loading the associated "system" (Linux/Windows) and "environment" (x86/etc), 
# based on information from its header.
#------------------------------------------------------------------------------
def read_program(file):
    obj = None
    try:
        # open file as a ELF object:
        p = elf.Elf(file)
        logger.info("ELF file detected")
        return p
    except elf.ElfError:
        pass

    try:
        # open file as a PE object:
        p = pe.PE(file)
        logger.info("PE file detected")
        return p
    except pe.PEError:
        pass

    logger.error('unknown file format')
    raise ValueError
    ## 
##

#------------------------------------------------------------------------------
# load_program is responsible of providing a "program" class instance
# depending on the detected "system" (Linux/Win32) and "environment" (x86).
#------------------------------------------------------------------------------
def load_program(file):

    p = read_program(file)

    if isinstance(p,(elf.Elf32,elf.Elf64)):

        if p.Ehdr.e_machine==elf.EM_386:
            if p.Ehdr.e_ident['EI_CLASS']==elf.ELFCLASS32 and \
               p.Ehdr.e_ident['EI_DATA']==elf.ELFDATA2LSB:
                from amoco.system.linux_x86 import ELF
                logger.info("linux_x86 program created")
                return ELF(p)
        elif p.Ehdr.e_machine==elf.EM_X86_64:
            if p.Ehdr.e_ident['EI_CLASS']==elf.ELFCLASS64 and \
               p.Ehdr.e_ident['EI_DATA']==elf.ELFDATA2LSB:
                from amoco.system.linux_x64 import ELF
                logger.info("linux_x64 program created")
                return ELF(p)
        elif p.Ehdr.e_machine==elf.EM_ARM:
            from amoco.system.linux_arm import ELF
            logger.info("linux_arm program created")
            return ELF(p)
        elif p.Ehdr.e_machine==elf.EM_SPARC:
            from amoco.system.leon2 import ELF
            logger.info("leon2 program created")
            return ELF(p)
        else:
            logger.error('machine type not supported:\n%s'%p.Ehdr)
            raise ValueError

    elif isinstance(p,pe.PE):

        if p.NT.Machine==pe.IMAGE_FILE_MACHINE_I386:
            from amoco.system.win32 import PE
            logger.info("win32 program created")
            return PE(p)
        elif p.NT.Machine==pe.IMAGE_FILE_MACHINE_AMD64:
            from amoco.system.win64 import PE
            logger.info("win64 program created")
            return PE(p)
        else:
            logger.error('machine type not supported')
            raise ValueError
