# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.logger import Log
logger = Log(__name__)

from amoco.system.core import DataIO
from amoco.system import elf
from amoco.system import pe
from amoco.system import utils

#------------------------------------------------------------------------------
def read_program(filename):
    '''
    Identifies the program header (ELF/PE) and returns an ELF, PE or DataIO
    instance.

    Args:
        filename (str): the program to read.

    Returns:
        an instance of currently supported program format (ELF, PE)

    '''

    try:
        data = open(filename,'rb')
    except (TypeError,IOError):
        data = bytes(filename)

    f = DataIO(data)

    try:
        # open file as a ELF object:
        p = elf.Elf(f)
        logger.info("ELF format detected")
        return p
    except elf.ElfError:
        f.seek(0)
        logger.debug('ElfError raised for %s'%f.name)

    try:
        # open file as a PE object:
        p = pe.PE(f)
        logger.info("PE format detected")
        return p
    except pe.PEError:
        f.seek(0)
        logger.debug('PEError raised for %s'%f.name)

    try:
        # open file as a HEX object:
        p = utils.HEX(f)
        logger.info("HEX format detected")
        return p
    except utils.FormatError:
        f.seek(0)
        logger.debug(' HEX FormatError raised for %s'%f.name)

    try:
        # open file as a SREC object:
        p = utils.SREC(f)
        logger.info("SREC format detected")
        return p
    except utils.FormatError:
        f.seek(0)
        logger.debug(' SREC FormatError raised for %s'%f.name)

    logger.warning('unknown format')
    return f
##

#------------------------------------------------------------------------------
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

    p = read_program(f)

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
        elif p.Ehdr.e_machine==elf.EM_AVR:
            from amoco.system.avr import ELF
            logger.info("AVR program created")
            return ELF(p)
        elif p.Ehdr.e_machine==elf.EM_RISCV:
            from amoco.system.riscv import ELF
            logger.info("RISC-V program created")
            return ELF(p)
        elif p.Ehdr.e_machine==elf.EM_BPF:
            from amoco.system.ebpf import ELF
            logger.info("EBPF program created")
            return ELF(p)
        elif p.Ehdr.e_machine==elf.EM_SH:
            from amoco.system.linux_j2core import ELF
            logger.info("J2 core (SH-2A) program created")
            return ELF(p)
        else:
            logger.error(u'machine type not supported:\n%s'%p.Ehdr)
            return None

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
            return None

    else:
        assert isinstance(p,(utils.HEX,DataIO))
        from amoco.system.raw import RawExec
        return RawExec(p,cpu)
