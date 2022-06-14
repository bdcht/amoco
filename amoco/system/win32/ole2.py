from amoco.system.structs import *
from codecs import utf_16_decode
import datetime


with Consts("magic"):
    OLE = tuple(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1")

def token_uuid_fmt(k, x, cls=None, fmt=None):
    return "%02X%02X%02X%02X-%02X%02X-%02X%02X-%02X%02X-%02X%02X%02X%02X%02X%02X"%x


with Consts("endian"):
    BIG_ENDIAN = (-1, -2)
    LITTLE_ENDIAN = (-2, -1)

@StructDefine("""
  B*8   : magic
  B*16  : clsid
  B*2   : ver_min
  B*2   : ver_maj
  b*2   : endian
  H     : bb_shift
  H     : sb_shift
  b*6   : reserved
  I     : csectdir
  I     : bb_count
  i     : bb_start
  I     : transaction
  I     : threshold
  i     : sb_start
  I     : sb_count
  i     : db_start
  I     : db_count
  i*109 : difat
""",packed=True)
class CompoundDocumentHeader(StructFormatter):

    def __init__(self, data=None, offset=0):
        self.name_formatter('magic','endian')
        self.func_formatter(clsid=token_uuid_fmt)
        if data:
            self.unpack(data, offset)

    def unpack(self,data,offset=0,psize=0):
        for f in self.fields[:5]:
            self[f.name] = f.unpack(data,offset)
            offset += f.size()
        if self.endian == BIG_ENDIAN:
            #FF FE: Big-Endian
            for f in self.fields:
                f.order = '>'
        # unpack the rest with correct endianness:
        for f in self.fields[5:]:
            self[f.name] = f.unpack(data,offset)
            offset += f.size()

class OLE2(object):

    def __init__(self, f):
        self.__file = f
        self.header = CompoundDocumentHeader(f)
        offset = self.header.size()
        f.seek(offset)
        self.sector = []
        sec_size = 1<<self.header.bb_shift
        while True:
            s = f.read(sec_size)
            if len(s)>0:
                self.sector.append(s)
            else:
                break
        order = '>' if self.header.endian == BIG_ENDIAN else '<'
        # create the MSAT list of secIDs:
        # -------------------------------
        # first part is given by the header's difat list:
        msat = [secID for secID in self.header.difat if secID!=-1]
        msat = msat[:self.header.bb_count]
        # remaining part is to read from some sector(s):
        if len(msat)<self.header.bb_count:
            secID = self.header.db_start
            n = 0
            while secID!=-2:
                if secID>=0:
                    offset = self.sector_offset(secID)
                    s = self.__file[offset:offset+sec_size]
                    l = struct.unpack(order+'%di'%(sec_size//4),s)
                    secID = l.pop()
                    msat.extend(l)
                    n+=1
                else:
                    print("secID error: %i"%secID)
                    secID==-2
            if n!=self.header.db_count:
                print("inconsistent sector count for MSAT")
        if len(msat)>self.header.bb_count:
            msat = msat[:self.header.bb_count]
        self.msat = msat
        # create the SAT list of secIDs:
        # ------------------------------
        sat = []
        for secID in self.msat:
            offset = self.sector_offset(secID)
            s = self.__file[offset:offset+sec_size]
            l = struct.unpack(order+'%di'%(sec_size//4),s)
            sat.extend(l)
        self.sat = sat
        if len(self.sat) != len(self.sector):
            print("inconsistent SAT length")
        # create the SSAT list of secIDs:
        # -------------------------------
        ssat = []
        secID = self.header.sb_start
        n = 0
        while secID != -2:
            offset = self.sector_offset(secID)
            s = self.__file[offset:offset+sec_size]
            l = struct.unpack(order+'%di'%(sec_size//4),s)
            ssat.extend(l)
            n += 1
            secID = self.sat[secID]
        if n!=self.header.sb_count:
            print("inconsistent sector count for SSAT")
        self.ssat = ssat
        # read the Directory stream:
        # --------------------------
        dir_chain = self.get_secID_chain(self.header.bb_start)
        esize = DirectoryEntry.size()
        self.directory = []
        self.ssc = None
        for secID in dir_chain:
            if secID==-2: break
            base = self.sector_offset(secID)
            for offset in range(base,base+sec_size,esize):
                e = DirectoryEntry()
                e.set_order(order)
                e.unpack(self.__file,offset)
                self.directory.append(e)
                if self.ssc is None and e.type == ROOT_STORAGE:
                    self.ssc = self.read_stream(e)

    def sector_offset(self,secID):
        return self.header.size()+(secID*(1<<self.header.bb_shift))

    def short_sector_pos(self,secID):
        return (secID*(1<<self.header.sb_shift))

    def get_secID_chain(self,secID,table=None):
        if table is None:
            table = self.sat
        chain = [secID]
        while secID != -2:
            secID = table[secID]
            chain.append(secID)
        return chain

    def read_stream(self,entry):
        sec_size = 1<<self.header.bb_shift
        if entry._v.size < self.header.threshold:
            return self.read_short_stream(entry)
        name = utf_16_decode(entry.name)[0].strip()
        print("read_stream: %s"%name)
        chain = self.get_secID_chain(entry.secID)
        data = b''
        for secID in chain:
            if secID == -2:
                break
            offset = self.sector_offset(secID)
            data += self.__file[offset:offset+sec_size]
        return data[:entry._v.size]

    def read_raw_stream(self,secID):
        sec_size = 1<<self.header.bb_shift
        chain = self.get_secID_chain(secID)
        data = b''
        for secID in chain:
            if secID == -2:
                break
            offset = self.sector_offset(secID)
            data += self.__file[offset:offset+sec_size]
        return data

    def read_short_stream(self,entry):
        ss_size = 1<<self.header.sb_shift
        name = utf_16_decode(entry.name)[0].strip()
        print("read_short_stream: %s"%name)
        chain = self.get_secID_chain(entry.secID,self.ssat)
        data = b''
        for secID in chain:
            if secID == -2:
                break
            offset = self.short_sector_pos(secID)
            data += self.ssc[offset:offset+ss_size]
        return data[:entry._v.size]

with Consts("type"):
    EMPTY = 0
    USER_STORAGE = 1
    USER_STREAM = 2
    LOCK_BYTES = 3
    PROPERTY = 4
    ROOT_STORAGE = 5

def token_time_fmt(k, x, cls=None, fmt=None):
    t0 = datetime.datetime(1601, 1, 1, 0, 0, 0)
    t = t0+datetime.timedelta(seconds=x//10000000)
    return str(t)

@StructDefine("""
  c*64    : name
  H       : nlen
  B       : type
  B       : black
  i       : left
  i       : right
  i       : root
  B*16    : uuid
  I       : flags
  Q       : creation
  Q       : modified
  i       : secID
  I       : size
  I       : reserved
""",packed=True)
class DirectoryEntry(StructFormatter):

    def __init__(self, data=None, offset=0):
        self.name_formatter('type')
        self.func_formatter(uuid=token_uuid_fmt)
        self.func_formatter(creation=token_time_fmt)
        self.func_formatter(modified=token_time_fmt)
        if data:
            self.unpack(data, offset)

    def set_order(self,order):
        for f in self.fields:
            f.order = order

