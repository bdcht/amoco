from amoco.system.structs import *

SUPERBLOCK_SIZE = 2048
BBLOCK = 0
BBSIZE = 8192
BBOFF = 0
SBOFF = BBOFF + BBSIZE
SBLOCK = 8192
SBSIZE = 8192
SECTOR_SIZE = 512
SECTOR_BITS = 9

UFSROOTINO = 2
LOSTFOUNDINO = 3
MAXNAMLEN = 255
MAXMNTLEN = 512


with Consts("fs_magic"):
    UFS_MAGIC = 0x00011954
    UFS2_MAGIC = 0x19540119

with Consts("fs_state"):
    FSOK = 0x7C269D38

with Consts("fs_clean"):
    FSACTIVE = 0x00
    FSCLEAN = 0x01
    FSSTABLE = 0x02
    FSOSF1 = 0x03
    FSBAD = 0xFF
    FSSUSPEND = 0xFE
    FSLOG = 0xFD
    FSFIX = 0xFC

with Consts("fs_flags"):
    FSLARGEFILES = 0x1

with Consts("fs_reclaim"):
    FS_RECLAIM = 0x00000001
    FS_RECLAIMING = 0x00000002
    FS_CHECKCLEAN = 0x00000004
    FS_CHECKRECLAIM = 0x00000008

with Consts("fs_rolled"):
    FS_PRE_FLAG = 0
    FS_ALL_ROLLED = 1
    FS_NEED_ROLL = 2

with Consts("fs_si"):
    FS_SI_OK = 0
    FS_SI_BAD = 1


UFS_DE_OLD = 0x00000000
UFS_DE_44BSD = 0x00000010
UFS_UID_OLD = 0x00000000
UFS_UID_44BSD = 0x00000020
UFS_UID_EFT = 0x00000040
UFS_ST_OLD = 0x00000000
UFS_ST_44BSD = 0x00000100
UFS_ST_SUN = 0x00000200
UFS_ST_SUNx86 = 0x00000400
UFS_CG_OLD = 0x00000000
UFS_CG_44BSD = 0x00002000
UFS_CG_SUN = 0x00001000
UFS_TYPE_UFS1 = 0x00000000
UFS_TYPE_UFS2 = 0x00010000


@StructDefine(
    """
I    : fs_link                  ; unused
I    : fs_rolled                ; unused
I    : fs_sblkno                ; addr of superblock in fs (in number of sectors)
I    : fs_cblkno                ; offset of cyl block in fs (in number of fragments)
I    : fs_iblkno                ; offset of inodes blocks in fs
I    : fs_dblkno                ; offset of 1st data in cyl
I    : fs_cgoffset              ; cyl grp offset in cyl
I    : fs_cgmask
I    : fs_time                  ; last time written
I    : fs_size                  ; number of blocks in fs
I    : fs_dsize                 ; number of data blocks in fs
I    : fs_ncg                   ; number of cyl grp
I    : fs_bsize                 ; size of basic block
I    : fs_fsize                 ; size of frags in a block
I    : fs_frag                  ; number of frags in a block
I    : fs_minfree               ; min percentage of free blks
I    : fs_rotdelay              ; number of ms for optimal next blk
I    : fs_rps                   ; disk revolutions/s
I    : fs_bmask                 ; blkoff calc of blk offsets
I    : fs_fmask                 ; fragoff calc of frag offsets
I    : fs_bshift                ; lblkno calc of logical blkno
I    : fs_fshift                ; numfrags calc number of frags
I    : fs_maxcontig             ; max number of contiguous blks
I    : fs_maxbpg                ; max number of blks/cyl grp
I    : fs_fragshift             ; block to frag shift
I    : fs_fsbtodb               ; fsbtodb and dbtofsb shift const
I    : fs_sbsize                ; actual size of superblock
I    : fs_csmask                ; csum block offset
I    : fs_csshift               ; csum block number
I    : fs_nindir
I    : fs_inopb
I    : fs_nspf
I    : fs_optim                 ; optimisation pref
I    : fs_npsect                ; sectors/track including spares
I    : fs_interleave            ; hardware sector interleave
I    : fs_trackskew             ; sector 0 skew pre track
I*2  : fs_id                    ; filesystem id
I    : fs_csaddr                ; blk addr of cyl grp summary area
I    : fs_cssize                ; size of cyl grp summary area
I    : fs_cgsize                ; cyl grp size
I    : fs_ntrak                 ; tracks/cyl
I    : fs_nsect                 ; sectors/track
I    : fs_spc                   ; sectors/cyl
I    : fs_ncyl                  ; cylinders in fs
I    : fs_cpg                   ; cyl/grp
I    : fs_ipg                   ; inodes/cyl grp
I    : fs_fpg                   ; blocks/(grp * fs_frag)
I    : fs_cstotal_cs_ndir       ; number of directories
I    : fs_cstotal_cs_nbfree     ; number of free blocks
I    : fs_cstotal_cs_nifree     ; number of free inodes
I    : fs_cstotal_cs_nffree     ; number of free frags
B    : fs_fmod                  ; superblock modified flag
B    : fs_clean                 ; filesystem clean flag
B    : fs_ronly                 ; mounted read-only flag
B    : fs_flags                 ; unused
s*512: fs_fsmnt
I    : fs_cgrotor               ; last cg searched
I*32 : fs_csp
i    : fs_cpc
h*128: fs_opostbl               ; old rotation block list head
i*51 : fs_sparecon
i    : fs_version
i    : fs_logbno
I    : fs_reclaim
I    : fs_sparecon2
I    : fs_state
Q    : fs_qbmask
Q    : fs_qfmask
I    : fs_postblformat
I    : fs_nrpos
I    : fs_postbloff
I    : fs_rotbloff
I    : fs_magic
B    : fs_space
"""
)
class superblock(StructFormatter):
    def __init__(self, data="", offset=0):
        self.name_formatter("fs_magic")
        self.name_formatter("fs_clean")
        self.flag_formatter("fs_flags")
        self.name_formatter("fs_reclaim", "fs_rolled", "fs_si")
        self.func_formatter(fs_time=token_datetime_fmt)
        self.func_formatter(fs_cgmask=token_mask_fmt)
        self.func_formatter(fs_csmask=token_mask_fmt)
        self.func_formatter(fs_bmask=token_mask_fmt)
        self.func_formatter(fs_fmask=token_mask_fmt)
        self.func_formatter(fs_qbmask=token_mask_fmt)
        self.func_formatter(fs_qfmask=token_mask_fmt)
        self.func_formatter(qbmask=token_mask_fmt)
        self.func_formatter(qfmask=token_mask_fmt)
        self.address_formatter("fs_csaddr")
        if data:
            self.unpack(data, offset)
            assert self.fs_magic == 0x011954

    def cgbase(self, c):
        return self.fs_fpg * c

    def cgstart(self, c):
        return self.cgbase(c) + (self.fs_cgoffset * (c & (~self.fs_cgmask)))

    def cgsblock(self, c):
        return self.cgstart(c) + self.fs_sblkno

    def cgtod(self, c):
        return self.cgstart(c) + self.fs_cblkno

    def cgimin(self, c):
        return self.cgstart(c) + self.fs_iblkno

    def cgdmin(self, c):
        return self.cgstart(c) + self.fs_dblkno

    def itoo(self, i):
        "inode number to file system block offset"
        return i % self.fs_inopb

    def itog(self, i):
        "inode number to cylinder group number"
        return i // self.fs_ipg

    def itod(self, i):
        "inode number to file system block address"
        return self.cgimin(self.itog(i)) + self.blkstofrags(
            (i % self.fs_ipg) // self.fs_inopb
        )

    def blkstofrags(self, b):
        return b << self.fs_fragshift

    def fragstoblks(self, f):
        return f >> self.fs_fragshift


# ------------------------------------------------------------------------------
# CYLINDER GROUP :

with Consts("cg_magic"):
    CG_MAGIC = 0x090255


@StructDefine(
    """
I    : cg_link                  ; not used
i    : cg_magic                 ; magic number
i    : cg_time                  ; last written time
i    : cg_cgx                   ; cg index number
h    : cg_ncyl                  ; nbr of cyl
h    : cg_niblk                 ; nbr of inode blocks
i    : cg_ndblk                 ; nbr of data blocks
i    : cg_cs_ndir               ; cyl summary info : nbr of directories
i    : cg_cs_nbfree             ;                    nbr of free blocks
i    : cg_cs_nifree             ;                    nbr of free inodes
i    : cg_cs_nffree             ;                    nbr of free frags
i    : cg_rotor                 ; position of last used block
i    : cg_frotor                ; position of last used frag
i    : cg_irotor                ; position of last used inode
i*8  : cg_frsum                 ; counts of available frags
i    : cg_btotoff               ; block totals / cyl
i    : cg_boff                  ; free block positions
i    : cg_iusedoff              ; used inode map
i    : cg_freeoff               ; free block map
i    : cg_nextfreeoff           ; next avail space
i*16 : cg_sparecon              ; reserved
B    : cg_space                 ; space for cg map
"""
)
class cylinder(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        self.name_formatter("cg_magic")
        self.func_formatter(cg_time=token_datetime_fmt)
        if data:
            self.unpack(data, offset)
            assert self.cg_magic == CG_MAGIC


# ------------------------------------------------------------------------------
# INODE:

with Consts("ic_smode"):
    IFMT = 0xF000
    IFIFO = 0x1000
    IFCHR = 0x2000
    IFDIR = 0x4000
    IFBLK = 0x6000
    IFREG = 0x8000
    IFLNK = 0xA000
    IFSHAD = 0xB000
    IFSOCK = 0xC000
    IFATTRDIR = 0xE000


def token_smode_fmt(k, x, cls):
    return (
        token_name_fmt(k, IFMT & x, cls)
        + ", "
        + token_constant_fmt(k, oct(x & 511), cls)
    )


with Consts("ic_uid"):
    ISUID = 0xF000
    ISGID = 0x1000
    ISVTX = 0x1000
    IREAD = 0x4000
    IWRITE = 0x6000
    IEXEC = 0x8000


@StructDefine(
    """
H    : ic_smode                 ; mode and type of file
H    : ic_nlink                 ; nbr of links to file
H    : ic_suid                  ; owner's user id
H    : ic_sgid                  ; owner's grp id
Q    : ic_lsize                 ; nbr of bytes in file
i    : ic_atime                 ; last access time
i    : ic_atspare
i    : ic_mtime                 ; last modified time
i    : ic_mtspare
i    : ic_ctime                 ; last inode changed time
i    : ic_ctspare
i*12 : ic_db                    ; disk block addresses (in nbr of fragments)
i*3  : ic_ib                    ; indirect blocks (in nbr of fragments)
i    : ic_flags                 ; cflags
i    : ic_blocks                ; nbr of disk blocks (512-bytes)
i    : ic_gen                   ; generation number
i    : ic_shadow                ; shadow inode
i    : ic_uid                   ; long eft uid
i    : ic_gid                   ; long eft gid
I    : ic_oeftflag
"""
)
class inode(StructFormatter):
    def __init__(self, data="", offset=0):
        self.func_formatter(ic_smode=token_smode_fmt)
        self.flag_formatter("ic_suid")
        self.func_formatter(ic_atime=token_datetime_fmt)
        self.func_formatter(ic_mtime=token_datetime_fmt)
        self.func_formatter(ic_ctime=token_datetime_fmt)
        if data:
            self.unpack(data, offset)

    def is_dir(self):
        return self.ic_smode & IFDIR

    def is_shadow(self):
        return self.ic_smode & IFSHAD

    def is_reg(self):
        return self.ic_smode & IFREG


with Consts("fsd_type"):
    FSD_FREE = 0
    FSD_ACL = 1
    FSD_DFACL = 2


@StructDefine(
    """
i    : fsd_type
i    : fsd_size
s    : fsd_data
"""
)
class fsd(StructFormatter):
    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)

    def unpack(self, data, offset=0):
        sz = 0
        for f in self.fields[:2]:
            setattr(self, f.name, f.unpack(data, offset + sz, self.order))
            sz += f.size
        f = self.fields[-1]
        f.count = self.fsd_size - sz
        setattr(self, f.name, f.unpack(data, offset + sz, self.order))
        return self


@StructDefine(
    """
I    : acl_un
H    : acl_perm
i    : acl_who
"""
)
class acl(StructFormatter):
    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
# DIRECTORY:


@StructDefine(
    """
i    : d_ino
h    : d_reclen
h    : d_namlen
s    : d_name
"""
)
class direct(StructFormatter):
    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)

    def unpack(self, data, offset=0):
        sz = 0
        for f in self.fields[:3]:
            setattr(self, f.name, f.unpack(data, offset + sz, self.order))
            sz += f.size
        f = self.fields[-1]
        assert self.d_namlen < (MAXNAMLEN + 1)
        f.count = self.d_namlen
        setattr(self, f.name, f.unpack(data, offset + sz, self.order))
        return self


# ------------------------------------------------------------------------------
# LOGGING:


@StructDefine(
    """
I         : lbno   ; logical blk number
I         : pbno   ; physical blk number (in fragments)
I         : nbno   ; nbr of blocks in this extent
"""
)
class extent(StructFormatter):
    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)


@StructDefine(
    """
I         : type
i         : chksum     ; chksum over entire block
I         : nextents   ; nbr of extents
I         : nbytes     ; bytesize of extent_block
I         : nextbno    ; blkno of next extent_block (in frags)
extent*1  : extents    ; list of extent structs
"""
)
class extent_block(StructFormatter):
    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)

    def unpack(self, data, offset=0):
        sz = 0
        for f in self.fields[:-1]:
            setattr(self, f.name, f.unpack(data, offset + sz, self.order))
            sz += f.size
        f = self.fields[-1]
        f.count = self.nextents
        setattr(self, f.name, f.unpack(data, offset + sz, self.order))
        return self


@StructDefine(
    """
I    : od_version        ; version number
I    : od_badlog         ; is log ok ?
I    : od_unused1
I    : od_maxtransfer
I    : od_devbsize
i    : od_bol_lof        ; byte-offset to begin of log
i    : od_eol_lof        ; byte-offset to end of log
I    : od_requestsize
I    : od_statesize
I    : od_logsize
i    : od_statebno       ; first blk of state area
i    : od_unused2
i    : od_head_lof       ; byte-offset of head
I    : od_head_ident     ; head sector id number
i    : od_tail_lof       ; byte-offset to tail
I    : od_tail_ident     ; tail sector id number
I    : od_chksum         ; checksum to verify ondisk content
I    : od_head_tid
i    : od_debug
i    : od_timestamp      ; time of last state change
"""
)
class ml_odunit(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        self.func_formatter(od_timestamp=token_datetime_fmt)
        if data:
            self.unpack(data, offset)


with Consts("d_typ"):
    DT_NONE = 0
    DT_SB = 1
    DT_CG = 2
    DT_SI = 3
    DT_AB = 4
    DT_ABZERO = 5
    DT_DIR = 6
    DT_INODE = 7
    DT_FBI = 8
    DT_QR = 9
    DT_COMMIT = 10
    DT_CANCEL = 11
    DT_BOT = 12
    DT_EOT = 13
    DT_UD = 14
    DT_SUD = 15
    DT_SHAD = 16
    DT_MAX = 17


@StructDefine(
    """
q    : d_mof
i    : d_nb
i    : d_typ
"""
)
class delta(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)


with Consts("st_tid"):
    TOP_READ_SYNC = 0
    TOP_WRITE = 1
    TOP_WRITE_SYNC = 2
    TOP_SETATTR = 3
    TOP_CREATE = 4
    TOP_REMOVE = 5
    TOP_LINK = 6
    TOP_RENAME = 7
    TOP_MKDIR = 8
    TOP_RMDIR = 9
    TOP_SYMLINK = 10
    TOP_FSYNC = 11
    TOP_GETPAGE = 12
    TOP_PUTPAGE = 13
    TOP_SBUPDATE_FLUSH = 14
    TOP_SBUPDATE_UPDATE = 15
    TOP_SBUPDATE_UNMOUNT = 16
    TOP_SYNCIP_CLOSEDQ = 17
    TOP_SYNCIP_FLUSHI = 18
    TOP_SYNCIP_HLOCK = 19
    TOP_SYNCIP_SYNC = 20
    TOP_SYNCIP_FREE = 21
    TOP_SBWRITE_RECLAIM = 22
    TOP_SBWRITE_STABLE = 23
    TOP_IFREE = 24
    TOP_IUPDAT = 25
    TOP_MOUNT = 26
    TOP_COMMIT_ASYNC = 27
    TOP_COMMIT_FLUSH = 28
    TOP_COMMIT_UPDATE = 29
    TOP_COMMIT_UNMOUNT = 30
    TOP_SETSECATTR = 31
    TOP_QUOTA = 32
    TOP_ITRUNC = 33
    TOP_ALLOCSP = 34
    TOP_MAX = 35


@StructDefine(
    """
I    : st_tid
I    : st_ident
"""
)
class sect_trailer(StructFormatter):
    order = "<"

    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------


class UFS(object):
    def __init__(self, dataIO, offset=0):
        self.data = dataIO
        # bootblk = dataIO[BBOFF:BBSIZE]
        S = superblock(dataIO, offset=SBOFF)
        cylinders = []
        for c in range(S.fs_ncg):
            cg = cylinder(dataIO, offset=(S.cgtod(c) * S.fs_fsize))
            cylinders.append(cg)
        inodes = []
        for c in cylinders:
            offset = S.fs_fsize * S.cgimin(c.cg_cgx)
            I = []
            for x in range(c.cg_niblk):
                I.append(inode(dataIO, offset))
                offset += inode.size()
            inodes.extend(I)
        self.superblock = S
        self.cylinders = cylinders
        self.inodes = inodes

    def lookup(self, name, cwd=None):
        i = cwd or self.inodes[UFSROOTINO]
        path = name.strip("/")
        for d in path.split("/"):
            if d == "":
                continue
            E = self.readdir(i)
            i = None
            for e in E:
                if e.d_name == d:
                    i = self.inodes[e.d_ino]
                    break
            if i is None:
                logger.info("file not found: %s" % d)
                break
        return i

    def readdir(self, i):
        assert i.is_dir()
        f = self.geti(i)
        off = 0
        E = []
        while off < len(f):
            d = direct(f, offset=off)
            E.append(d)
            off += d.d_reclen
        return E

    def readfsd(self, i):
        assert i.is_shadow()
        f = self.geti(i)
        off = 0
        shads = []
        while off < len(f):
            s = fsd(f, offset=off)
            shads.append(s)
            off += s.fsd_size
        return shads

    def readlog(self):
        S = self.superblock
        off = S.fs_logbno * S.fs_fsize
        if off != 0:
            return extent_block(self.data, offset=off)
        else:
            return None

    def geti(self, i):
        S = self.superblock

        def getblks(blist, data, fsz, lsz):
            blks = []
            sz = 0
            for b in blist:
                if b == 0:
                    continue
                off = b * fsz
                blks.append(data[off : off + fsz])
                sz += fsz
                if sz >= lsz:
                    cut = fsz - (sz - lsz)
                    blks[-1] = blks[-1][0:cut]
                    sz = lsz
                    break
            return (blks, sz)

        def getindir(pos, data, bsz, order):
            data.seek(pos)
            return struct.unpack(order + "%di" % (bsz // 4), data.read(bsz))

        f, sz = getblks(i.ic_db, self.data, S.fs_fsize, i.ic_lsize)
        # first-indirect blocks:
        if sz < i.ic_lsize:
            indir0 = getindir(i.ic_ib[0] * S.fs_fsize, self.data, S.fs_bsize, S.order)
            l, isz = getblks(indir0, self.data, S.fs_fsize, i.ic_lsize - sz)
            f.extend(l)
            sz += isz
        # second-indirect blocks:
        if sz < i.ic_lsize:
            indir1 = getindir(i.ic_ib[1] * S.fs_fsize, self.data, S.fs_bsize, S.order)
            for ind0 in [
                getindir(pos, self.data, S.fs_bsize, S.order) for pos in indir1
            ]:
                l, isz = getblks(ind0, self.data, S.fs_fsize, i.ic_lsize - sz)
                f.extend(l)
                sz += isz
                if sz == i.ic_lsize:
                    break
        # third-indirect blocks:
        if sz < i.ic_lsize:
            indir2 = getindir(i.ic_ib[2] * S.fs_fsize, self.data, S.fs_bsize, S.order)
            for indir1 in [
                getindir(pos1, self.data, S.fs_bsize, S.order) for pos1 in indir2
            ]:
                for ind0 in [
                    getindir(pos0, self.data, S.fs_bsize, S.order) for pos0 in indir1
                ]:
                    l, isz = getblks(ind0, self.data, S.fs_fsize, i.ic_lsize - sz)
                    f.extend(l)
                    sz += isz
                    if sz == i.ic_lsize:
                        break
                if sz == i.ic_lsize:
                    break
        if sz != i.ic_lsize:
            logger.warning("incomplete inode %s" % repr(i))
        return "".join(f)
