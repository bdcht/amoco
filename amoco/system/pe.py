# This code is part of Amoco
# Copyright (C) 2007 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

import pefile

# our exception handler:
class PEError(Exception):
    def __init__(self,message):
        self.message = message
    def __str__(self):
        return str(self.message)
##

# The PE file header.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
        ##
        ## parse and provide information about PE files
        ##
#------------------------------------------------------------------------------

class PE(pefile.PE):

    basemap   = None
    symtab    = None
    strtab    = None
    reltab    = None
    functions = None
    variables = None

    def entrypoint(self):
        return self.OPTIONAL_HEADER.AddressOfEntryPoint+self.basemap

    def __init__(self,filename):
        try:
            pefile.PE.__init__(self,filename)
        except pefile.PEFormatError:
            raise PEError('not a PE file')
        self.basemap = self.OPTIONAL_HEADER.ImageBase
        self.functions = self.__functions()
        self.variables = self.__variables()
    ##

    def data(self,target,size):
        rva = target-self.basemap
        return self.get_data(rva,size)

    def getinfo(self,target):
        rva = None
        if isinstance(target,str):
            try:
                rva = int(target,16)
            except ValueError:
                for a,f in self.functions.iteritems():
                    if f[0]==target: rva = int(a,16); break
        elif isinstance(target,(int,long)):
            rva = target
        if rva is None:
            return None,0,0
        rva = rva-self.basemap
        s = self.get_section_by_rva(rva)
        if s is None: return None,0,0
        return s,rva-s.VirtualAddress,s.VirtualAddress+self.basemap
    ##

    def loadsegment(self,S,pagesize):
        if S and not S.IMAGE_SCN_LNK_REMOVE:
            addr = self.basemap+S.VirtualAddress
            bytes = S.data
            if pagesize:
                # note: bytes are not truncated, only extended if needed...
                bytes = bytes.ljust(pagesize,'\x00')
            return {addr: bytes}
        return None

    def readcode(self,target):
        s,offset,base = self.getinfo(target)
        if s==None: return None,0,0
        return self.get_data(s.VirtualAddress+offset),0,base+offset

    def __functions(self):
        D = {}
        if hasattr(self,'DIRECTORY_ENTRY_IMPORT'):
            for module in self.DIRECTORY_ENTRY_IMPORT:
                for symbol in module.imports:
                        D[symbol.address] = '%s__%s'%(module.dll,symbol.name)
        return D

    def __variables(self):
        D = {}
        return D

## End of class PE

