# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2021 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.structs import StructDefine,StructFormatter
from amoco.system.core import shellcode, DataIO, CoreExec, DefineStub
from amoco.system.memory import MemoryMap
from amoco.arch.w65c02 import cpu
from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")

IRQV = 0xfffe
RESETV  = 0xfffc
SOFTEV  = 0x03f2
PWREDUP = 0x03f4

IOMAP = [
    ("IO_KBD/80STOREOFF", 0xc000),
    ("80STOREON", 0xc001),
    ("RAMRDOFF", 0xc002),
    ("RAMRDON", 0xc003),
    ("RAMWRTOFF", 0xc004),
    ("RAMWRTON", 0xc005),
    ("ALTZPOFF", 0xc008),
    ("ALTZPON", 0xc009),
    ("80COLOFF", 0xc00c),
    ("80COLON", 0xc00d),
    ("ALTCHARSETOFF", 0xc00e),
    ("ALTCHARSETON", 0xc00f),
    ("KBDSTRB", 0xc010),
    ("RDBANK2", 0xc011),
    ("RDLCRAM", 0xc012),
    ("RAMRD", 0xc013),
    ("RAMWRT", 0xc014),
    ("MOUSEXINT", 0xc015),
    ("ALTZP", 0xc016),
    ("MOUSEYINT", 0xc017),
    ("80STORE", 0xc018),
    ("VBLINT", 0xc019),
    ("TEXT", 0xc01a),
    ("MIXED", 0xc01b),
    ("PAGE2", 0xc01c),
    ("HIRES", 0xc01d),
    ("ALTCHARSET", 0xc01e),
    ("80COL", 0xc01f),
    *[("SPEAKER", 0xc030+i) for i in range(16)],
    ("RDXYMSK", 0xc040),
    ("RDVBLMSK", 0xc041),
    ("RDX0EDGE", 0xc042),
    ("RDY0EDGE", 0xc043),
    ("RSTXY", 0xc048),
    ("TEXTOFF", 0xc050),
    ("TEXTON", 0xc051),
    ("MIXEDOFF", 0xc052),
    ("MIXEDON", 0xc053),
    ("PAGE2OFF", 0xc054),
    ("PAGE2ON", 0xc055),
    ("HIRESOFF", 0xc056),
    ("HIRESON", 0xc057),
    ("DISXY", 0xc058),
    ("ENBXY", 0xc059),
    ("DISVBL", 0xc05a),
    ("ENVBL", 0xc05b),
    ("RX0EDGE", 0xc05c),
    ("FX0EDGE", 0xc05d),
    ("RY0EDGE", 0xc05e),
    ("FY0EDGE", 0xc05f),
    ("RD80SW", 0xc060),
    ("PB0", 0xc061),
    ("PB1", 0xc062),
    ("RD63", 0xc063),
    ("PDL0", 0xc064),
    ("PDL1", 0xc065),
    ("MOUX1", 0xc066),
    ("MOUY1", 0xc067),
    ("PTRIG", 0xc070),
    *[("RDIOUDIS", i) for i in (0xc078, 0xc07a, 0xc07c, 0xc07e)],
    *[("DHIRES", i) for i in (0xc079, 0xc07b, 0xc07d, 0xc07f)],
    ("READBSR2", 0xc080),
    ("WRITEBSR2", 0xc081),
    ("OFFBSR2", 0xc082),
    ("RDWRBSR2", 0xc083),
    ("READBSR1", 0xc088),
    ("WRITEBSR1", 0xc089),
    ("OFFBSR1", 0xc08a),
    ("RDWRBSR1", 0xc08b),
    ("DATAREG1", 0xc098),
    ("STATUS1", 0xc099),
    ("COMMAND1", 0xc09a),
    ("CONTROL1", 0xc09b),
    ("DATAREG2", 0xc0a8),
    ("STATUS2", 0xc0a9),
    ("COMMAND2", 0xc0aa),
    ("CONTROL2", 0xc0ab),
 ]

# ----------------------------------------------------------------------------

class AppleROM(CoreExec):
    def __init__(self, romfile, cpu):
        try:
            f = open(romfile,"rb")
        except (ValueError, TypeError, IOError):
            print("romfile '%s' not found"%romfile)
        else:
            rom = DataIO(f)
            super().__init__(shellcode(rom),cpu)
            # setup memory space:
            # -------------------
            # [0x0000-0x00FF] zero page:
            self.state.mmap.write(0,b'\0'*0x100)
            # [0x0100-0x01FF] stack:
            self.state.mmap.write(0x100,b'\0'*0x100)
            # [0x0200-0x02FF] input buffer (keyboard/floppy):
            self.state.mmap.write(0x200,b'\0'*0x100)
            # [0x0300-0x03FF] program space & system API:
            self.state.mmap.write(0x300,b'\0'*0x100)
            # [0x0400-0x07FF] video page1:
            self.state.mmap.write(0x400,b'\0'*0x400)
            # [0x0800-0x0BFF] video page2:
            self.state.mmap.write(0x800,b'\0'*0x400)
            # [0x0C00-0x1FFF] is free...
            # [0x2000-0x3FFF] high-res video page1:
            self.state.mmap.write(0x2000,b'\0'*0x2000)
            # [0x4000-0x5FFF] high-res video page2:
            self.state.mmap.write(0x4000,b'\0'*0x2000)
            # [0x6000-0xBFFF] is free...
            # [0xC000-0xC0FF] memory-mapped I/O:
            for io,addr in IOMAP:
                xf = cpu.ext(io,size=8)
                xf.stub = Apple2c.stub(xf.ref)
                self.state.mmap.write(addr,xf)
            # [0xC100-0xFFFF] ROM memory:
            self.setup_rom()

    def setup_rom(self):
        # C100-CFFF contains extensions to the system monitor, and subroutines
        # to support 80-column text displau, printer, modem, mouse and disk.
        self.state.mmap.write(0x10000-self.bin.data.size(),self.bin.data[0:])
        # D000-F7FF contains the Applesoft ROM
        # F800-FFFF contains the system monitor ROM

# ----------------------------------------------------------------------------

class Apple2c(object):
    stubs = {}
    default_stub = DefineStub.warning

    def __init__(self, conf=None):
        if conf is None:
            from amoco.config import System

            conf = System()
        self.romfile = conf.romfile
        self.tasks = []
        self.abi = None
        self.symbols = {}

    @classmethod
    def loader(cls, bprm, conf=None):
        return cls(conf).load_bin(bprm)

    def load_bin(self,bprm):
        p = AppleROM(self.romfile, cpu)
        p.OS = self
        # define registers:
        p.state[cpu.sp_] = cpu.cst(0x1ff,16)
        p.state[cpu.A] = cpu.cst(0xff,8)
        p.state[cpu.X] = cpu.cst(0xff,8)
        p.state[cpu.Y] = cpu.cst(0xff,8)
        p.state[cpu.P] = cpu.cst(0xff,8)
        p.state[cpu.D] = cpu.bit0
        entry = p.state(cpu.mem(cpu.RESETV,16))
        p.state[cpu.pc] = entry
        # map the stack area:
        p.state.mmap.write(0x100,b'\0'*0x100)
        self.tasks.append(p)
        return p

    def stub(self, refname):
        return self.stubs.get(refname, self.default_stub)


# ----------------------------------------------------------------------------

@DefineStub(Apple2c, "IO_KBD/80STOREOFF")
def io_kbd_80storeoff(m, mode):
    m[cpu.pc] = m(cpu.mem(cpu.sp_,16))
    m[cpu.sp] = m(cpu.sp+2)

