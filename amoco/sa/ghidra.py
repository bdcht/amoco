import ghidra_bridge

b = ghidra_bridge.GhidraBridge(namespace=locals())

def select_range(begin,end):
    AddressSet = ghidra.program.model.address.AddressSet
    setCurrentSelection(AddressSet(toAddr(begin),toAddr(end)))

def add_memory_block(name,start,size,val=None,access="rw"):
    mmap = currentProgram.memory
    blk = mmap.createInitializedBlock(name, toAddr(start), size,
                                      val, monitor, False)
    if "w" in access:
        blk.setWrite(True)

    if "x" in access:
        blk.setExecute(True)

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
            print("no function containing reference %s"%r)
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

