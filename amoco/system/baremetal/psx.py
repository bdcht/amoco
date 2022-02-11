# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.structs import StructDefine,StructFormatter
from amoco.system.core import BinFormat, CoreExec, DefineStub
from amoco.system.memory import MemoryMap
from amoco.arch.mips import cpu_r3000LE as cpu
from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")

# define psx exe format (size: 0x800 bytes)
@StructDefine(
"""
c*8   : magic            ; must be 'PS-X EXE'
I*2   : zerofilled
I     : start
I     : gp               ; usually 0
I     : text             ; usually 80010000h
I     : filesize         ; excluding 800h-byte header
I*2   : reserved3
I     : memfill_addr
I     : memfill_size
I     : stack            ; usually 801FFFF0h
I     : offset
I     : reserved5
I*4   : reserved6
c*1970: signature
"""
)
class Header(StructFormatter):
    def __init__(self, data=None,offset=0):
        self.name_formatter("magic","signature")
        self.address_formatter("start","gp","text","stack")
        if data:
            self.unpack(data,offset)

    def unpack(self, data, offset=0, psize=0):
        super().unpack(data, offset)
        if self.magic != b"PS-X EXE":
            raise TypeError("Wrong magic number, not a PS-X EXE file ?")
        return self

# ----------------------------------------------------------------------------

class EXE(BinFormat):

    def __init__(self,f):
        self.__file = f
        self.Header = Header(f)
        self.text   = f[len(self.Header):]

    @property
    def entrypoints(self):
        return [self.Header.start]

    @property
    def filename(self):
        return self.__file.name

    @property
    def header(self):
        return self.Header


# ----------------------------------------------------------------------------

class BIOS(object):
    stubs = {}
    default_stub = DefineStub.warning

    def __init__(self, conf=None):
        if conf is None:
            from amoco.config import System

            conf = System()
        self.tasks = []
        self.abi = None
        self.symbols = {}

    @classmethod
    def loader(cls, bprm, conf=None):
        return cls(conf).load_psx_exe(bprm)

    def load_psx_exe(self,bprm):
        p = Task(bprm, cpu)
        p.OS = self
        # map the CODE area:
        p.state.mmap.write(0x80018000,b'\0'*0x4800)
        data = bprm.text[0:bprm.Header.filesize]
        vaddr = bprm.Header.text
        p.state.mmap.write(vaddr,data)
        # define registers:
        p.state[cpu.pc] = cpu.cst(bprm.Header.start,32)
        p.state[cpu.npc] = p.state(cpu.pc+4)
        p.state[cpu.sp] = cpu.cst(bprm.Header.stack,32)
        p.state[cpu.fp] = cpu.cst(bprm.Header.stack,32)
        p.state[cpu.gp] = cpu.cst(bprm.Header.gp,32)
        p.state[cpu.a0] = p.state(cpu.pc)
        p.state[cpu.a1] = p.state(cpu.gp)
        p.state[cpu.a2] = p.state(cpu.sp)
        p.state[cpu.a3] = p.state(cpu.fp)
        # map the stack area:
        p.state.mmap.write(bprm.Header.stack-0x800,b'\0'*0x800)
        # map the BIOS functions as external symbols:
        self.load_bios(p.state.mmap)
        self.tasks.append(p)
        return p

    def load_bios(self,mmap):
        xf = cpu.ext("bios_a0",size=32)
        xf.stub = self.stub(xf.ref)
        mmap.write(0xa0,xf)
        xf = cpu.ext("bios_b0",size=32)
        xf.stub = self.stub(xf.ref)
        mmap.write(0xb0,xf)
        xf = cpu.ext("bios_c0",size=32)
        xf.stub = self.stub(xf.ref)
        mmap.write(0xc0,xf)

    def stub(self, refname):
        return self.stubs.get(refname, self.default_stub)


# ----------------------------------------------------------------------------

class Task(CoreExec):
    pass

# ----------------------------------------------------------------------------

@DefineStub(BIOS, "ret_0", default=True)
def nullstub(m, **kargs):
    m[cpu.pc] = m(cpu.ra)
    m[cpu.npc] = m(cpu.pc)+4

@DefineStub(BIOS, "bios_a0")
def bios_a0(m, **kargs):
    index = m(cpu.t1)
    if index._is_cst:
        name = A0.get(index.value,None)
        logger.debug("BIOS A0(0x%02x) '%s'"%(index.value,name))
        return BIOS.stubs.get(name,nullstub)(m,**kargs)
    else:
        logger.warning("BIOS A0(0x%02x) not implemented, using nullstub"%index)
        return nullstub(m,**kargs)

@DefineStub(BIOS, "bios_b0")
def bios_b0(m, **kargs):
    index = m(cpu.t1)
    if index._is_cst:
        name = B0.get(index.value,None)
        logger.debug("BIOS B0(0x%02x) '%s'"%(index.value,name))
        return BIOS.stubs.get(name,nullstub)(m,**kargs)
    else:
        logger.warning("BIOS B0(0x%02x) not implemented, using nullstub"%index)
        return nullstub(m,**kargs)

@DefineStub(BIOS, "bios_c0")
def bios_c0(m, **kargs):
    index = m(cpu.t1)
    if index._is_cst:
        logger.debug("BIOS C0(0x%02x) '%s'"%(index.value,name))
        name = C0.get(index.value,None)
        return BIOS.stubs.get(name,nullstub)(m,**kargs)
    else:
        logger.warning("BIOS C0(0x%02x) not implemented, using nullstub"%index)
        return nullstub(m,**kargs)

A0 = {
  0x00: 'FileOpen',
  0x01: 'FileSeek',
  0x02: 'FileRead',
  0x03: 'FileWrite',
  0x04: 'FileClose',
  0x05: 'FileIoctl',
  0x06: 'exit',
  0x07: 'FileGetDeviceFlag',
  0x08: 'FileGetc',
  0x09: 'FilePutc',
  0x0A: 'todigit',
  0x0B: 'atof',
  0x0C: 'strtoul',
  0x0D: 'strtol',
  0x0E: 'abs',
  0x0F: 'labs',
  0x10: 'atoi',
  0x11: 'atol',
  0x12: 'atob',
  0x13: 'SaveState',
  0x14: 'RestoreState',
  0x15: 'strcat',
  0x16: 'strncat',
  0x17: 'strcmp',
  0x18: 'strncmp',
  0x19: 'strcpy',
  0x1A: 'strncpy',
  0x1B: 'strlen',
  0x1C: 'index',
  0x1D: 'rindex',
  0x1E: 'strchr',
  0x1F: 'strrchr',
  0x20: 'strpbrk',
  0x21: 'strspn',
  0x22: 'strcspn',
  0x23: 'strtok',
  0x24: 'strstr',
  0x25: 'toupper',
  0x26: 'tolower',
  0x27: 'bcopy',
  0x28: 'bzero',
  0x29: 'bcmp',
  0x2A: 'memcpy',
  0x2B: 'memset',
  0x2C: 'memmove',
  0x2D: 'memcmp',
  0x2E: 'memchr',
  0x2F: 'rand',
  0x30: 'srand',
  0x31: 'qsort',
  0x32: 'strtod',
  0x33: 'malloc',
  0x34: 'free',
  0x35: 'lsearch',
  0x36: 'bsearch',
  0x37: 'calloc',
  0x38: 'realloc',
  0x39: 'InitHeap',
  0x3A: 'SystemErrorExit',
  0x3B: 'std_in_getchar',
  0x3C: 'std_out_putchar',
  0x3D: 'std_in_gets',
  0x3E: 'std_out_puts',
  0x3F: 'printf',
  0x40: 'SystemErrorUnresolvedException',
  0x41: 'LoadExeHeader',
  0x42: 'LoadExeFile',
  0x43: 'DoExecute',
  0x44: 'FlushCache',
  0x45: 'init_a0_b0_c0_vectors',
  0x46: 'GPU_dw',
  0x47: 'gpu_send_dma',
  0x48: 'SendGP1Command',
  0x49: 'GPU_cw',
  0x4A: 'GPU_cwp',
  0x4B: 'send_gpu_linked_list',
  0x4C: 'gpu_abort_dma',
  0x4D: 'GetGPUStatus',
  0x4E: 'gpu_sync',
  0x4F: 'SystemError',
  0x50: 'SystemError',
  0x51: 'LoadAndExecute',
  0x52: 'SystemError',
  0x53: 'SystemError',
  0x54: 'CdInit',
  0x55: '_bu_init',
  0x56: 'CdRemove',
  0x5B: 'dev_tty_init',
  0x5C: 'dev_tty_open',
  0x5D: 'dev_tty_in_out',
  0x5E: 'dev_tty_ioctl',
  0x5F: 'dev_cd_open',
  0x60: 'dev_cd_read',
  0x61: 'dev_cd_close',
  0x62: 'dev_cd_firstfile',
  0x63: 'dev_cd_nextfile',
  0x64: 'dev_cd_chdir',
  0x65: 'dev_card_open',
  0x66: 'dev_card_read',
  0x67: 'dev_card_write',
  0x68: 'dev_card_close',
  0x69: 'dev_card_firstfile',
  0x6A: 'dev_card_nextfile',
  0x6B: 'dev_card_erase',
  0x6C: 'dev_card_undelete',
  0x6D: 'dev_card_format',
  0x6E: 'dev_card_rename',
  0x6F: 'card_clear_error',
  0x70: '_bu_init',
  0x71: 'CdInit',
  0x72: 'CdRemove',
  0x78: 'CdAsyncSeekL',
  0x7C: 'CdAsyncGetStatus',
  0x7E: 'CdAsyncReadSector',
  0x81: 'CdAsyncSetMode',
  0x90: 'CdromIoIrqFunc1',
  0x91: 'CdromDmaIrqFunc1',
  0x92: 'CdromIoIrqFunc2',
  0x93: 'CdromDmaIrqFunc2',
  0x94: 'CdromGetInt5errCode',
  0x95: 'CdInitSubFunc',
  0x96: 'AddCDROMDevice',
  0x97: 'AddMemCardDevice',
  0x98: 'AddDuartTtyDevice',
  0x99: 'AddDummyTtyDevice',
  0x9A: 'SystemError',
  0x9B: 'SystemError',
  0x9C: 'SetConf',
  0x9D: 'GetConf',
  0x9E: 'SetCdromIrqAutoAbort',
  0x9F: 'SetMemSize',
  0xA0: 'WarmBoot',
  0xA1: 'SystemErrorBootOrDiskFailure',
  0xA2: 'EnqueueCdIntr',
  0xA3: 'DequeueCdIntr',
  0xA4: 'CdGetLbn',
  0xA5: 'CdReadSector',
  0xA6: 'CdGetStatus',
  0xA7: 'bu_callback_okay',
  0xA8: 'bu_callback_err_write',
  0xA9: 'bu_callback_err_busy',
  0xAA: 'bu_callback_err_eject',
  0xAB: '_card_info',
  0xAC: '_card_async_load_directory',
  0xAD: 'set_card_auto_format',
  0xAE: 'bu_callback_err_prev_write',
  0xAF: 'card_write_test',
  0xB2: 'ioabort_raw',
  0xB4: 'GetSystemInfo',
}


B0 = {
  0x00: 'alloc_kernel_memory',
  0x01: 'free_kernel_memory',
  0x02: 'init_timer',
  0x03: 'get_timer',
  0x04: 'enable_timer_irq',
  0x05: 'disable_timer_irq',
  0x06: 'restart_timer',
  0x07: 'DeliverEvent',
  0x08: 'OpenEvent',
  0x09: 'CloseEvent',
  0x0A: 'WaitEvent',
  0x0B: 'TestEvent',
  0x0C: 'EnableEvent',
  0x0D: 'DisableEvent',
  0x0E: 'OpenThread',
  0x0F: 'CloseThread',
  0x10: 'ChangeThread',
  0x11: 'jump_to_00000000h',
  0x12: 'InitPad',
  0x13: 'StartPad',
  0x14: 'StopPad',
  0x15: 'OutdatedPadInitAndStart',
  0x16: 'OutdatedPadGetButtons',
  0x17: 'ReturnFromException',
  0x18: 'SetDefaultExitFromException',
  0x19: 'SetCustomExitFromException',
  0x1A: 'SystemError',
  0x1B: 'SystemError',
  0x1C: 'SystemError',
  0x1D: 'SystemError',
  0x1E: 'SystemError',
  0x1F: 'SystemError',
  0x20: 'UnDeliverEvent',
  0x21: 'SystemError',
  0x22: 'SystemError',
  0x23: 'SystemError',
  0x24: 'jump_to_00000000h',
  0x25: 'jump_to_00000000h',
  0x26: 'jump_to_00000000h',
  0x27: 'jump_to_00000000h',
  0x28: 'jump_to_00000000h',
  0x29: 'jump_to_00000000h',
  0x2A: 'SystemError',
  0x2B: 'SystemError',
  0x2C: 'jump_to_00000000h',
  0x2D: 'jump_to_00000000h',
  0x2E: 'jump_to_00000000h',
  0x2F: 'jump_to_00000000h',
  0x30: 'jump_to_00000000h',
  0x31: 'jump_to_00000000h',
  0x32: 'FileOpen',
  0x33: 'FileSeek',
  0x34: 'FileRead',
  0x35: 'FileWrite',
  0x36: 'FileClose',
  0x37: 'FileIoctl',
  0x38: 'exit',
  0x39: 'FileGetDeviceFlag',
  0x3A: 'FileGetc',
  0x3B: 'FilePutc',
  0x3C: 'std_in_getchar',
  0x3D: 'std_out_putchar',
  0x3E: 'std_in_gets',
  0x3F: 'std_out_puts',
  0x40: 'chdir',
  0x41: 'FormatDevice',
  0x42: 'firstfile',
  0x43: 'nextfile',
  0x44: 'FileRename',
  0x45: 'FileDelete',
  0x46: 'FileUndelete',
  0x47: 'AddDevice  ',
  0x48: 'RemoveDevice',
  0x49: 'PrintInstalledDevices',
  0x4A: 'InitCard  ',
  0x4B: 'StartCard',
  0x4C: 'StopCard',
  0x4D: '_card_info_subfunc  ',
  0x4E: 'write_card_sector',
  0x4F: 'read_card_sector',
  0x50: 'allow_new_card',
  0x51: 'Krom2RawAdd',
  0x52: 'SystemError',
  0x53: 'Krom2Offset',
  0x54: 'GetLastError',
  0x55: 'GetLastFileError',
  0x56: 'GetC0Table',
  0x57: 'GetB0Table',
  0x58: 'get_bu_callback_port',
  0x59: 'testdevice',
  0x5A: 'SystemError',
  0x5B: 'ChangeClearPad',
  0x5C: 'get_card_status',
  0x5D: 'wait_card_status',
}

C0 = {
  0x00: 'EnqueueTimerAndVblankIrqs',
  0x01: 'EnqueueSyscallHandler',
  0x02: 'SysEnqIntRP',
  0x03: 'SysDeqIntRP',
  0x04: 'get_free_EvCB_slot',
  0x05: 'get_free_TCB_slot',
  0x06: 'ExceptionHandler',
  0x07: 'InstallExceptionHandlers',
  0x08: 'SysInitMemory',
  0x09: 'SysInitKernelVariables',
  0x0A: 'ChangeClearRCnt',
  0x0B: 'SystemError',
  0x0C: 'InitDefInt',
  0x0D: 'SetIrqAutoAck',
  0x12: 'InstallDevices',
  0x13: 'FlushStdInOutPut',
  0x15: 'tty_cdevinput',
  0x16: 'tty_cdevscan',
  0x17: 'tty_circgetc',
  0x18: 'tty_circputc',
  0x19: 'ioabort',
  0x1A: 'set_card_find_mode',
  0x1B: 'KernelRedirect',
  0x1C: 'AdjustA0Table',
  0x1D: 'get_card_find_mode',
}


