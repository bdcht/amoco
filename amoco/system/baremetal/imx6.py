from amoco.system.structs import struct, Consts, StructFormatter, StructDefine
from amoco.arch.arm import cpu_armv7
from amoco.system.core import DataIO
from amoco.system.raw import RawExec

with Consts("tag"):
    HAB_TAG_IVT = 0xD1
    HAB_TAG_DCD = 0xD2
    HAB_TAG_CSF = 0xD4
    HAB_TAG_CRT = 0xD7
    HAB_TAG_SIG = 0xD8
    HAB_TAG_EVT = 0xDB
    HAB_TAG_RVT = 0xDD
    HAB_TAG_WRP = 0x81
    HAB_TAG_MAC = 0xAC

with Consts("cmd"):
    HAB_CMD_SET = 0xB1
    HAB_CMD_INS_KEY = 0xBE
    HAB_CMD_AUT_DAT = 0xCA
    HAB_CMD_WRT_DAT = 0xCC
    HAB_CMD_CHK_DAT = 0xCF
    HAB_CMD_NOP = 0xC0
    HAB_CMD_INIT = 0xB4
    HAB_CMD_UNLK = 0xB2

with Consts("flg"):
    HAB_CMD_INS_KEY_CLR = 0
    HAB_CMD_INS_KEY_ABS = 1
    HAB_CMD_INS_KEY_CSF = 2
    HAB_CMD_INS_KEY_DAT = 4
    HAB_CMD_INS_KEY_CFG = 8
    HAB_CMD_INS_KEY_FID = 16
    HAB_CMD_INS_KEY_MID = 32
    HAB_CMD_INS_KEY_CID = 64
    HAB_CMD_INS_KEY_HSH = 128

with Consts("pcl"):
    HAB_PCL_SRK = 0x03
    HAB_PCL_X509 = 0x09
    HAB_PCL_CMS = 0xC5
    HAB_PCL_BLOB = 0xBB
    HAB_PCL_AEAD = 0xA3

with Consts("alg"):
    HAB_ALG_ANY = 0x00
    HAB_ALG_HASH = 0x01
    HAB_ALG_SIG = 0x02
    HAB_ALG_F = 0x03
    HAB_ALG_EC = 0x04
    HAB_ALG_CIPHER = 0x05
    HAB_ALG_MODE = 0x06
    HAB_ALG_WRAP = 0x07
    HAB_ALG_SHA1 = 0x11
    HAB_ALG_SHA256 = 0x17
    HAB_ALG_SHA512 = 0x1B
    HAB_ALG_PKCS1 = 0x21
    HAB_ALG_AES = 0x55
    HAB_MODE_CCM = 0x66
    HAB_ALG_BLOB = 0x71

with Consts("key_type"):
    HAB_KEY_PUBLIC = 0xE1
    HAB_KEY_HASH = 0xEE
    HAB_KEY_X509 = 0x30

with Consts("eng"):
    HAB_ENG_ANY = 0x00
    HAB_ENG_SCC = 0x03
    HAB_ENG_RTIC = 0x05
    HAB_ENG_SAHARA = 0x06
    HAB_ENG_CSU = 0x0A
    HAB_ENG_SRTC = 0x0C
    HAB_ENG_DCP = 0x1B
    HAB_ENG_CAAM = 0x1D
    HAB_ENG_SNVS = 0x1E
    HAB_ENG_OCOTP = 0x21
    HAB_ENG_DTCP = 0x22
    HAB_ENG_ROM = 0x36
    HAB_ENG_HDCP = 0x24
    HAB_ENG_SW = 0xFF

# ------------------------------------------------------------------------------


@StructDefine(
    """
B :  tag
H :> length
B :  version
""",
    packed=True,
)
class HAB_Header(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        self.name_formatter("tag")
        self.func_formatter(version=self.token_ver_format)
        if data:
            self.unpack(data, offset)

    @staticmethod
    def token_ver_format(k, x, cls=None, fmt=None):
        return highlight([(Token.Literal, "%d.%d" % (x >> 4, x & 0xF))],fmt)


# ------------------------------------------------------------------------------


@StructDefine(
    """
HAB_Header : header
I          : entry
I          : reserved1
I          : dcd
I          : boot_data
I          : self
I          : csf
I          : reserved2
""",
    packed=True,
)
class IVT(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        self.address_formatter("entry")
        self.address_formatter("dcd")
        self.address_formatter("boot_data")
        self.address_formatter("self")
        self.address_formatter("csf")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------


@StructDefine(
    """
I          : start
I          : size
I          : plugin
""",
    packed=True,
)
class BootData(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        self.address_formatter("start")
        self.address_formatter("size")
        self.flag_formatter("plugin")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------


@StructDefine(
    """
B          :  key_type
H          :> len
B          :  unk
I          :  unk_flags
H          :> nlen
H          :> elen
""",
    packed=True,
)
class PublicKey(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        self.name_formatter("key_type")
        if data:
            self.unpack(data, offset)

    def unpack(self, data, offset=0, psize=0):
        StructFormatter.unpack(self, data, offset)
        offset += 12
        self.modulus = data[offset : offset + self.nlen]
        offset += self.nlen
        self.exponent = data[offset : offset + self.elen]
        return self

    def size(self):
        return 12 + self.nlen + self.elen


# ------------------------------------------------------------------------------


@StructDefine(
    """
HAB_Header : header
""",
    packed=True,
)
class CRT(StructFormatter):
    def __init__(self, data="", offset=0):
        self.keys = []
        if data:
            self.unpack(data, offset)

    def unpack(self, data, offset=0, psize=0):
        StructFormatter.unpack(self, data, offset)
        assert self.header.tag == HAB_TAG_CRT
        crtend = offset + self.header.length
        offset += self.size()
        crt = data[offset:crtend]
        if crt[0] == HAB_KEY_PUBLIC:
            while offset < csfend:
                k = PublicKey(data, offset)
                self.keys.append(k)
                offset += k.size()
        else:
            self.data = crt
        return self

    def size(self):
        S = struct.calcsize(self.order + self.format())
        S += sum((len(c) for c in self.keys), 0)
        return S


# ------------------------------------------------------------------------------


@StructDefine(
    """
HAB_Header : header
""",
    packed=True,
)
class CSF(StructFormatter):
    def __init__(self, data="", offset=0):
        self.cmds = []
        if data:
            self.unpack(data, offset)

    def unpack(self, data, offset=0, psize=0):
        StructFormatter.unpack(self, data, offset)
        assert self.header.tag == HAB_TAG_CSF
        csfend = offset + self.header.length
        offset += self.size()
        self.cmds = []
        while offset < csfend:
            k = self.CMD(data, offset)
            self.cmds.append(k)
            offset += k.size()
        return self

    def size(self):
        S = struct.calcsize(self.format())
        S += sum((len(c) for c in self.cmds), 0)
        return S

    @staticmethod
    def CMD(data, offset):
        tag = ord(data[offset : offset + 1])
        if tag == HAB_CMD_CHK_DAT:
            return CheckData(data, offset)
        if tag == HAB_CMD_NOP:
            return NOP(data, offset)
        if tag == HAB_CMD_INS_KEY:
            return InstallKey(data, offset)
        if tag == HAB_CMD_AUT_DAT:
            return Authenticate(data, offset)
        if tag == HAB_CMD_UNLK:
            return Unlock(data, offset)
        else:
            return HAB_Header(data, offset)


# ------------------------------------------------------------------------------


@StructDefine(
    """
B        :  cmd
H        :> len
B        :  par
I        :  address
I        :  mask
""",
    packed=True,
)
class CheckData(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        self.name_formatter("cmd")
        self.address_formatter("address")
        self.flag_formatter("mask")
        if data:
            self.unpack(data, offset)

    def unpack(self, data, offset=0, psize=0):
        StructFormatter.unpack(self, data, offset)
        assert self.cmd == HAB_CMD_CHK_DAT
        self.flags = self.par >> 3
        self.bytes = self.par & 0x7
        if self.len > 8:
            cnt = RawField("I", fname="count")
            offset += self.size()
            self.count = cnt.unpack(data, offset)
        return self

    def size(self):
        S = struct.calcsize(self.format())
        if hasattr(self, "count"):
            S += 4
        return S


# ------------------------------------------------------------------------------


@StructDefine(
    """
B        :  cmd
H        :> len
B        :  und
""",
    packed=True,
)
class NOP(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        self.name_formatter("cmd")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------


@StructDefine(
    """
B        :  cmd
H        :> len
B        :  eng
""",
    packed=True,
)
class Unlock(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        self.name_formatter("cmd")
        if data:
            self.unpack(data, offset)

    def unpack(self, data, offset=0, psize=0):
        StructFormatter.unpack(self, data, offset)
        assert self.cmd == HAB_CMD_UNLK
        if self.len > self.size():
            nb = (self.len - self.size()) // 4
            val = RawField("I", nb, fname="val", forder=">")
            offset += self.size()
            self.val = val.unpack(data, offset)
        return self

    def size(self):
        S = struct.calcsize(self.format())
        if hasattr(self, "val"):
            S += 4 * len(self.val)
        return S


# ------------------------------------------------------------------------------


@StructDefine(
    """
B        :  cmd
H        :> len
B        :  flg
B        :  pcl
B        :  alg
B        :  src
B        :  tgt
I        :> key_dat
""",
    packed=True,
)
class InstallKey(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        self.name_formatter("cmd")
        self.flag_formatter("flg")
        self.name_formatter("pcl")
        self.name_formatter("alg")
        self.address_formatter("key_dat")
        if data:
            self.unpack(data, offset)

    def unpack(self, data, offset=0, psize=0):
        StructFormatter.unpack(self, data, offset)
        assert self.cmd == HAB_CMD_INS_KEY
        if self.len > self.size():
            nb = (self.len - self.size()) // 4
            crt_hsh = RawField("I", nb, fname="crt_hsh")
            self.address_formatter("crt_hsh")
            offset += self.size()
            self.crt_hsh = crt_hsh.unpack(data, offset)
        return self

    def size(self):
        S = struct.calcsize(self.format())
        if hasattr(self, "crt_hsh"):
            S += 4 * len(self.crt_hsh)
        return S


# ------------------------------------------------------------------------------
@StructDefine(
    """
B        :  cmd
H        :> len
B        :  flg
B        :  key
B        :  pcl
B        :  eng
B        :  cfg
I        :> aut_start
""",
    packed=True,
)
class Authenticate(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        self.name_formatter("cmd")
        self.flag_formatter("flg")
        self.name_formatter("pcl")
        self.name_formatter("eng")
        self.flag_formatter("cfg")
        self.address_formatter("aut_start")
        if data:
            self.unpack(data, offset)

    @staticmethod
    def blks_format(k, x, cls=None):
        s = []
        for b in range(0, len(x), 2):
            adr = (Token.Address, hex(x[b]))
            sz = (Token.Constant, str(x[b + 1]))
            s.append((Token.Literal, "("))
            s.append(adr)
            s.append((Token.Literal, ","))
            s.append(sz)
            s.append((Token.Literal, ")"))
        return highlight(s)

    def unpack(self, data, offset=0, psize=0):
        StructFormatter.unpack(self, data, offset)
        assert self.cmd == HAB_CMD_AUT_DAT
        if self.len > self.size():
            offset += self.size()
            nb = (self.len - self.size()) // 4
            blks = RawField("I", fcount=nb, fname="blks", forder=">")
            self.func_formatter(blks=self.blks_format)
            self.blks = blks.unpack(data, offset)
        return self

    def size(self):
        S = struct.calcsize(self.format())
        if hasattr(self, "blks"):
            S += 4 * len(self.blks)
        return S

    def __str__(self):
        s = StructFormatter.__str__(self)
        if hasattr(self, "blks"):
            s += "\nblks: %s\n" % (self.blks_format(0, self.blks))
        return s


# ------------------------------------------------------------------------------


class HABstub(RawExec):
    ILR_size = 0x4000
    IVT_offset = 0x400

    def __init__(self, filename):
        from amoco.system.core import read_program

        self.rom = read_program(filename)
        self.ivt = IVT(self.rom, offset=self.IVT_offset)
        assert self.ivt.self != 0
        ILR = DataIO(self.rom[0:4096])
        RawExec.__init__(self, ILR, cpu=cpu_armv7)
        start = self.ivt.self - self.IVT_offset
        self.relocate(start)
        if self.ivt.boot_data:
            self.boot_data = BootData(self.state.mmap, self.ivt.boot_data)
            off = self.boot_data.start - start
            data = self.rom[off : off + self.boot_data.size]
        self.state.mmap.write(self.boot_data.start, data)
        if self.ivt.csf != 0:
            self.csf = CSF(self.state.mmap, self.ivt.csf)
        else:
            self.csf = None
        self.state[self.cpu.apsr] = self.cpu.cst(0, 32)
