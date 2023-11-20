from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

import ghidra_bridge

b = ghidra_bridge.GhidraBridge(namespace=locals())

def select_range(begin,end):
    AddressSet = ghidra.program.model.address.AddressSet
    setCurrentSelection(AddressSet(toAddr(begin),toAddr(end)))

def add_memory_block(name,start,size,val=None,access="rw",dt=None):
    mmap = currentProgram.memory
    segs = mmap.blocks
    S = {}
    for s in segs:
        S[s.getStart().getOffset()] = s

    blk = mmap.createInitializedBlock(name, toAddr(start), size,
                                      val, monitor, False)
    if "w" in access:
        blk.setWrite(True)

    if "x" in access:
        blk.setExecute(True)

    if isinstance(dt,str):
        s_ = getDataTypes(dt)
    else:
        s_ = [dt]
    if len(s_)==1:
        s_ = s_[0]
    else:
        logger.warn("too many structures named %s"%dt)
        s_ = None
    if s_ is not None:
        createData(toAddr(start), s_)
    return blk

def setPointer(address,size=4):
    PointerDataType = ghidra.program.model.data.PointerDataType
    if isinstance(address,int):
        address = toAddr(address)
    ls = currentProgram.getListing()
    ls.createData(address, PointerDataType.dataType, size)

def setFunctionName(address,name):
    USER_DEFINED = ghidra.program.model.symbol.SourceType.USER_DEFINED
    if isinstance(address,int):
        address = toAddr(address)
    f = getFunctionAt(address)
    f.setName(name, USER_DEFINED)

def create_labels(labels):
    USER_DEFINED = ghidra.program.model.symbol.SourceType.USER_DEFINED
    sym = currentProgram.symbolTable
    for a,r in labels.items():
        if isinstance(a,int):
            a = toAddr(a)
        sym.createLabel(a, r, USER_DEFINED)

def getFunctions_XRefd_at_Location(address):
    if isinstance(address,int):
        address = toAddr(address)
    loc = ghidra.program.util.ProgramLocation(currentProgram,address)
    F = []
    for r in ghidra.app.util.XReferenceUtils.getAllXrefs(loc):
        f = getFunctionContaining(r.getFromAddress())
        if f is None:
            logger.warn("no function containing reference %s"%r)
            continue
        F.append(f)
    return set(F)

def get_decompiled(func_name):
    func = getGlobalFunctions(func_name)[0]
    options = ghidra.app.decompiler.DecompileOptions()
    monitor = ghidra.util.task.ConsoleTaskMonitor()
    ifc = ghidra.app.decompiler.DecompInterface()
    ifc.setOptions(options)
    ifc.openProgram(func.getProgram())
    res = ifc.decompileFunction(func, 1000, monitor)
    return res

def get_decompiled_C(func_name):
    res = get_decompiled(func_name)
    # get decompiled C source from res:
    src = res.getDecompiledFunction().getC()
    return src

def get_decompiled_symbols(func_name):
    res = get_decompiled(func_name)
    # get (decompiled) high-function object from res:
    high_func = res.getHighFunction()
    # get local variables' symbols:
    lsm = high_func.getLocalSymbolMap()
    symbols = lsm.getSymbols()
    for i, symbol in enumerate(symbols):
        print("\nSymbol {}:".format(i+1))
        print("  name:         {}".format(symbol.name))
        print("  dataType:     {}".format(symbol.dataType))
        print("  getPCAddress: 0x{}".format(symbol.getPCAddress()))
        print("  size:         {}".format(symbol.size))
        print("  storage:      {}".format(symbol.storage))
        print("  parameter:    {}".format(symbol.parameter))
        print("  readOnly:     {}".format(symbol.readOnly))
        print("  typeLocked:   {}".format(symbol.typeLocked))
        print("  nameLocked:   {}".format(symbol.nameLocked))

def get_ast_nodes(func_name):
    res = get_decompiled(func_name)
    # get (decompiled) high-function object from res:
    def walk(node,L):
        if type(node) == ghidra.app.decompiler.ClangStatement:
            L.append(node)
        else:
            for i in range(node.numChildren()):
                walk(node.Child(i),L)
    nodes = []
    walk(res.getCCodeMarkup(),nodes)
    return nodes

def propagateType(addr, dt, level=2, data=None, force=True, create=True, _stack=[]):
    """at given address 'addr', apply structure type 'dt' and try to
       propagate pointers to sub-structures with given depth level (default is 2.)
       All other arguments are used internally for recursion...
    """
    if len(_stack)==level:
        return 0
    if isinstance(addr,int):
        cur = toAddr(addr)
    else:
        cur = addr
        addr = cur.getOffset()
    if addr<0x40000000:
        return 0
    logger.debug("address: %s"%str(cur))
    if isinstance(dt,str):
        S = getDataTypes(dt)
        if len(S)>1:
            logger.warn("too many types found for '%s'"%dt)
            return 1
        elif len(S)==0:
            logger.warn("no type named '%s'"%dt)
            return 2
        else:
            dt = S[0]
    logger.debug("type: %s"%dt.getName())
    if create:
        if force:
            clearListing(cur, toAddr(addr+dt.length-1))
            logger.debug("listing cleared for zone [%08x,%08x]"%(addr,addr+dt.length-1))
        elif (getInstructionAt(cur) is not None) or (getDataAt(cur) is not None):
            logger.warn("can't overwrite existing instr/data at 0x%08x"%addr)
            return 3
        logger.verbose("creating data...")
        createData(cur, dt)
    if data is None:
        s =  getDataAt(cur)
    else:
        s = data
    # start propagating sub-types...using recursion limited to a given level depth:
    _stack.append(s)
    logger.verbose("propagating fields of %s"%str(s))
    for i in range(s.getNumComponents()):
        f = s.getComponent(i)
        logger.debug("  [%d] field %s"%(i,f.componentPathName))
        t = f.getDataType()
        if f.isPointer() and t.dataType.__class__.__name__=='StructureDB':
            logger.debug("    --(pointer)--")
            try:
                err = propagateType(f.value, t.dataType, level)
            except Exception as e:
                logger.error("can't propagate %s at %s"%(t.dataType.getName(), str(f.address)))
                logger.debug("exception was: %s"%e)
                err = 4
            if err!=0:
                logger.warn("error during propagation of type %s at 0x08x"%(dt.getName(), addr))
            else:
                logger.verbose("  done")
        elif f.isStructure():
            logger.debug("    --(structure)--")
            try:
                err = propagateType(f.address, t, data=f, create=False)
            except Exception as e:
                logger.error("can't propagate field %s (error is '%s')"%(str(f),str(e)))
    _stack.pop()
    return 0

def propagate_here(level=1):
    """at current address which should be on a pointer field within a mapped structure,
       find the current (pointer) sub-field's type and apply it at the pointer address
       with given depth level (default is 1).
    """
    found = False
    addr = currentAddress.getOffset()
    s = getDataContaining(currentAddress)
    logger.verbose("searching for component at address %s"%currentAddress)
    while not found:
        if s.isStructure() or s.isArray():
            if s.isStructure():
                logger.verbose("component is in structure %s..."%s)
            if s.isArray():
                logger.verbose("component is in array %s..."%s)
            saddr = s.address.getOffset()
            off = addr-saddr
            c = s.getComponentContaining(off)
            if c is None:
                logger.warn("component not found...")
                break
            if c.isPointer() and c.address.getOffset()==addr:
                logger.verbose("found Pointer component field %s"%c.componentPathName)
                found = True
            else:
                s = c
        else:
            logger.warn("currentAddress is not a structure field ??")
            break
    if found:
        t = c.getDataType().dataType
        logger.verbose("propagating type %s at address %s"%(t.getName(),c.value))
        err = propagateType(c.value,t,level)
        return c.value
    else:
        return currentAddress

