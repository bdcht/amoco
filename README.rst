=====
Amoco
=====
+-----------+-----------------------------------+
| Status:   | Under Development                 |
+-----------+-----------------------------------+
| Location: | https://github.com/bdcht/amoco    |
+-----------+-----------------------------------+
| Version:  | 2.4                               |
+-----------+-----------------------------------+

.. contents:: **Table of Contents**
    :local:
    :depth: 3
    :backlinks: top

Description
===========

Amoco is a python package dedicated to the (static) analysis of binaries.

It features:

- a generic framework for decoding instructions, developed to reduce
  the time needed to implement support for new architectures.
  For example the decoder for most IA32 instructions (general purpose)
  fits in less than 800 lines of Python.
  The full SPARCv8 RISC decoder (or the ARM THUMB-1 set as well) fits
  in less than 350 lines. The ARMv8 instruction set decoder is less than
  650 lines. See arch_ for details.
- a **symbolic** algebra module which allows to describe the semantics of
  every instructions and compute a functional representation of instruction
  blocks. See cas_ for details.
- a generic execution model wich provides an abstract memory model to deal
  with concrete or symbolic values transparently, and other system-dependent
  features. See system_ for details.
- various classes implementing usual disassembly techniques like linear sweep,
  recursive traversal, or more elaborated techniques like path-predicate
  which relies on SAT/SMT solvers to proceed with discovering the control
  flow graph or even to implement techniques like DARE (Directed Automated
  Random Exploration). See main.py_ for details.
- various generic "helpers" and arch-dependent pretty printers to allow
  custom look-and-feel configurations (think AT&T vs. Intel syntax,
  absolute vs. relative offsets, decimal or hex immediates, etc).
  See arch_ for details.

Amoco is still *work in progress*. See Todo_ for a list of features to be
merged from develop branch or to be more thoroughly implemented.

History
=======

Development started in late 2006 with a proof-of-concept for symbolic
interpretation of x86 ELF programs. At that time it used a modified
version of minisat_ for simplifying symbolic expressions.
In 2009, it was fully rewritten with support for various other architectures
(``z80, armv7/thumb``) and executable formats (``PE, Gameboy Cardridge``).
In 2013 the internal decoding system was redesigned, and the minisat solver
was replaced by z3_. The ``armv8`` and ``sparc`` architectures were added.

Despite being (just) yet another tool for analysing binaries,
in 2014 a dedicated 'release' branch was created with most of the above
features to be open-sourced.

Todo
====

Some components of Amoco are still in the
process of being pushed to the release branch or further developed.
More precisely:

- x86 fpu and sse instructions semantics are not implemented,
- arm SIMD, VFP, NEON, TrustZone, Jazelle instruction sets are not implemented,
- pretty printers based on pygments package are not merged,
- solver-based disassembling strategies are not merged yet.
- persistent database (session) and idb import/export features are planned (Q2 2015).
- sphinx documentation is planned.
- MIPS, 6502 and PPC archs are planned.

Contributions to fulfill uncomplete/unimplemented parts are welcome.


Install
=======

Amoco is tested on python 2.7 and depends on the following python packages:

- grandalf_ used for building CFG (and eventually rendering it)
- crysp_    used by the generic intruction decoder (``arch/core.py``)
- z3_       used to simplify expressions and solve constraints
- pygments_ (not in current release, planned for 2.4.2 release)
- pyparsing_ for parsing instruction decoder formats
- ply_ (optional), for parsing *GNU as* files
- zodb_ (optional), provides persistence of amoco objects in a database


Quickstart
==========

Below is a very simple example where basic blocks are build with linear sweep:

.. sourcecode:: python

 >>> import amoco
 >>> p = amoco.system.loader.load_program('tests/samples/flow.elf')
 amoco.system.loader: INFO: Elf32 file detected
 amoco.system.loader: INFO: linux_x86 program created
 >>> p
 <amoco.system.linux_x86.ELF object at 0x8b23d4c>


We are analysing file ``flow.elf``. Since we don't know nothing about it
we start by using a high level loader which will try to detect its format
and target platform and provide some feedback info. Here the loader
creates a ``linux_x86.ELF`` object which shall represent the program task.


.. sourcecode:: python

 >>> p.bin
 <amoco.system.elf.Elf32 object at 0xb721a48c>
 >>> print p.mmap
 <MemoryZone rel=None :
          <mo [08048000,08049ff0] data:'\x7fELF\x01\x01\x01\x00\x00\x00...'>
          <mo [08049f14,08049ff0] data:'\xff\xff\xff\xff\x00\x00\x00\x0...'>
          <mo [08049ff0,08049ff4] data:@__gmon_start__>
          <mo [08049ff4,0804a000] data:'(\x9f\x04\x08\x00\x00\x00\x00\x...'>
          <mo [0804a000,0804a004] data:@__stack_chk_fail>
          <mo [0804a004,0804a008] data:@malloc>
          <mo [0804a008,0804a00c] data:@__gmon_start__>
          <mo [0804a00c,0804a010] data:@__libc_start_main>
          <mo [0804a010,0804af14] data:'\x00\x00\x00\x00\x00\x00\x00\x0...'>>
 <MemoryZone rel=esp :>
 >>> p.mmap.read(0x0804a004,4)
 [<amoco.cas.expressions.ext object at 0x8cff054>]
 >>> print _[0]
 @malloc
 >>> p.mmap.read(0x0804a00c,6)
 [<amoco.cas.expressions.ext object at 0x8cff0a4>, '\x00\x00']


The object gives access to the Elf32 object and its mapping in our abstract
memory model. We can note that in this model, imports location in .got segment
are modeled as abstract expressions of type ``ext``. Note also that fetching
compound data (symbolic+concrete) is possible. See MemoryZone_ for more details.
Lets proceed with getting some basic blocks...

.. sourcecode:: python

 >>> z = amoco.lsweep(p)
 >>> ib = z.iterblocks()
 >>> next(ib)
 <block object (name=0x8048380) at 0x09e8939c>
 >>> b=_
 >>> print b
 # --- block 0x8048380 ---
 0x8048380  31ed                           xor         ebp,ebp
 0x8048382  5e                             pop         esi
 0x8048383  89e1                           mov         ecx,esp
 0x8048385  83e4f0                         and         esp,0xfffffff0
 0x8048388  50                             push        eax
 0x8048389  54                             push        esp
 0x804838a  52                             push        edx
 0x804838b  6810860408                     push        #__libc_csu_fini
 0x8048390  68a0850408                     push        #__libc_csu_init
 0x8048395  51                             push        ecx
 0x8048396  56                             push        esi
 0x8048397  68fd840408                     push        #main
 0x804839c  e8cfffffff                     call        *0x8048370
 >>> list(b)
 [<amoco.arch.x86.spec_ia32 [0x8048380]  XOR ( length=2 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048382]  POP ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048383]  MOV ( length=2 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048385]  AND ( length=3 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048388]  PUSH ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048389]  PUSH ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x804838a]  PUSH ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x804838b]  PUSH ( length=5 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048390]  PUSH ( length=5 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048395]  PUSH ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048396]  PUSH ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048397]  PUSH ( length=5 type=1 )>, <amoco.arch.x86.spec_ia32 [0x804839c]  CALL ( length=5 type=2 )>]
 >>> i = b[-1]
 >>> i
 <amoco.arch.x86.spec_ia32 [0x804839c]  CALL ( length=5 type=2 )>
 >>> print i
 0x804839c  e8cfffffff                     call        *0x8048370
 >>> i.mnemonic
 'CALL'
 >>> i.bytes
 '\xe8\xcf\xff\xff\xff'
 >>> i._uarch['i_CALL']
 <function i_CALL at 0x8cf85a4>
 >>> str(i.operands[0])
 '-0x31'
 >>> i.operands[0].value
 -49L
 >>> i.typename()
 'control_flow'


We use here the most basic **linear sweep** approach and spawn a basic
block iterator. The first block is well known. We can see that the default
x86 pretty printer uses Intel syntax and codehelpers that show PLT refs
as associated .got ``ext`` expression. Also, relative offsets are displayed
as absolute addresses (indicated by the \* prefix).

Lets look at the symbolic execution of this block:

.. sourcecode:: python

 >>> b.map
 <amoco.cas.mapper.mapper object at 0x9cba3ec>
 >>> print b.map
 ebp <- { | [0:32]->0x0 | }
 esi <- { | [0:32]->M32(esp) | }
 ecx <- { | [0:32]->(esp+0x4) | }
 eflags <- { | [0:1]->0x0 | [1:2]->eflags[1:2] | [2:3]->(0x6996>>(((esp+0x4)&0xfffffff0)[0:8]^(((esp+0x4)&0xfffffff0)[0:8]>>0x4))[0:4])[0:1] | [3:6]->eflags[3:6] | [6:7]->(((esp+0x4)&0xfffffff0)==0x0) | [7:8]->(((esp+0x4)&0xfffffff0)<0x0) | [8:11]->eflags[8:11] | [11:12]->0x0 | [12:32]->eflags[12:32] | }
 ((((esp+0x4)&0xfffffff0)-4)) <- eax
 ((((esp+0x4)&0xfffffff0)-8)) <- (((esp+0x4)&0xfffffff0)-0x4)
 ((((esp+0x4)&0xfffffff0)-12)) <- edx
 ((((esp+0x4)&0xfffffff0)-16)) <- 0x8048610
 ((((esp+0x4)&0xfffffff0)-20)) <- 0x80485a0
 ((((esp+0x4)&0xfffffff0)-24)) <- (esp+0x4)
 ((((esp+0x4)&0xfffffff0)-28)) <- M32(esp)
 ((((esp+0x4)&0xfffffff0)-32)) <- 0x80484fd
 esp <- { | [0:32]->(((esp+0x4)&0xfffffff0)-0x24) | }
 ((((esp+0x4)&0xfffffff0)-36)) <- (eip+0x21)
 eip <- { | [0:32]->(eip+-0x10) | }
 >>> b.map[p.cpu.esi]
 <amoco.cas.expressions.mem object at 0x8b2fa6c>
 >>> e=_
 >>> print e
 M32(esp)
 >>> e.length
 4
 >>> e.size
 32


When a block is instanciated, a ``mapper`` object is automatically created.
This function can map any input state to an output state corresponding to the
interpretation of this block.

A mapper object is now also equipped with a MemoryMap to mitigate aliasing issues
and ease updating the global mmap state.

.. sourcecode:: python

 >>> print b.map.memory()
 <MemoryZone rel=None :>
 <MemoryZone rel=((esp+0x4)&0xfffffff0) :
          <mo [-0000024,-0000020] data:(eip+0x21)>
          <mo [-0000020,-000001c] data:0x80484fd>
          <mo [-000001c,-0000018] data:M32(esp)>
          <mo [-0000018,-0000014] data:(esp+0x4)>
          <mo [-0000014,-0000010] data:0x80485a0>
          <mo [-0000010,-000000c] data:0x8048610>
          <mo [-000000c,-0000008] data:edx>
          <mo [-0000008,-0000004] data:(((esp+0x4)&0xfffffff0)-0x4)>
          <mo [-0000004,00000000] data:eax>>
 >>> print b.map(p.cpu.mem(p.cpu.esp,64))
 { | [0:32]->(eip+0x21) | [32:64]->0x80484fd | }
 >>> print b.map(p.cpu.mem(p.cpu.ebx,32))
 M32$9(ebx)


As shown above, reading memory in the mapper can return a compound expression.
Note also that unmapped areas are returned as symbolic mem objects.
Since aliasing between different MemoryZones is possible, the returned
symbolic expression of fetching memory at pointer ``ebx`` is special:
the ``M32$9(ebx)`` expression says "in input state, take 32 bits found at
pointer ebx *after* applying 9 possibly aliasing memory writes to the state.
More details in mapper_.


-----

Lets try a (little) more elaborated analysis that will not only allow to
build a list of basic blocks but will also help us discover (parts of)
the control flow graph of the program:

.. sourcecode:: python

 >>> ff = amoco.fforward(p)
 >>> ff.policy
 {'depth-first': True, 'branch-lazy': True}
 >>> ff.policy['branch-lazy']=False
 >>> ff.getcfg()
 amoco.cas.expressions: INFO: stub __libc_start_main called
 amoco.main: INFO: fforward analysis stopped at block 0x8048370
 <amoco.cfg.graph object at 0xb72e330c>
 >>> G=_
 >>> G.C
 [<grandalf.graphs.graph_core object at 0x8f6d78c>]

Here we use the **fast-forward** analysis (see below) and set its "branch-lazy" policy
to ``False`` to avoid falling back to linear sweep when analysis of branch fails.
Interestingly, we can see that the PLT jump to ``__libc_start_main`` external function
has been followed thanks to a ``@stub`` defined for this external (see ``system/linux_x86.py``).

Let's have a look at the graph instance:

.. sourcecode:: python

 >>> print G.C[0].sV
 0.| <node [0x8048380] at 0x8db764c>
 1.| <node [0x8048370] at 0x8db740c>
 >>> print G.C[0].sE
 0.| <link [0x8048380 -> 0x8048370] at 0x8db742c>
 >>> G.get_node('0x8048370')
 <node [0x8048370] at 0x8db740c>
 >>> n=_
 >>> print n.data
 # --- block 0x8048370 ---
 0x8048370  'ff250ca00408'     jmp         [@__libc_start_main]
 >>> print n.data.map
 eip <- { | [0:32]->M32(esp+4) | }
 esp <- { | [0:32]->(esp-0x4) | }
 (esp-4) <- @exit

Ok, so the program counter is correctly pointing to the ``#main`` address located
at offset +4 in the stack, but since the fast-forward method only look at one block,
it cannot know that this location holds this address.

A little more elaborated analysis like **link-forward** would have started analysing
``#main``:

.. sourcecode:: python

 >>> lf = amoco.lforward(p)
 >>> lf.getcfg()
 amoco.cas.expressions: INFO: stub __libc_start_main called
 amoco.main: INFO: lforward analysis stopped at block 0x80484d4
 <amoco.cfg.graph object at 0x88552ec>
 >>> G=_
 >>> print G.C
 [<grandalf.graphs.graph_core object at 0x8a0b7ec>,
 <grandalf.graphs.graph_core object at 0x8a0c1cc>,
 <grandalf.graphs.graph_core object at 0x8a0d2fc>,
 <grandalf.graphs.graph_core object at 0x8a3156c>]
 >>> for g in G.C:
 ...   print g.sV
 ...   print '------'
 ...
 0.| <node [0x8048380] at 0x885566c>
 1.| <node [0x8048370] at 0xb72c830c>
 2.| <node [0x80484fd] at 0x885532c>
 ------
 0.| <node [0x8048434] at 0x8a0c16c>
 ------
 0.| <node [0x8048483] at 0x8a31dec>
 1.| <node [0x804845e] at 0x8a3316c>
 ------
 0.| <node [0x80484d4] at 0x8a38a1c>
 ------
 >>> print G.get_node('0x8048434').data
 # --- block 0x8048434 ---
 0x8048434  '55'                   push        ebp
 0x8048435  '89e5'                 mov         ebp,esp
 0x8048437  '83ec38'               sub         esp,0x38
 0x804843a  '8b4508'               mov         eax,[ebp+8]
 0x804843d  '83c001'               add         eax,0x1
 0x8048440  '8945f4'               mov         [ebp-12],eax
 0x8048443  '8b45f4'               mov         eax,[ebp-12]
 0x8048446  'a320a00408'           mov         [#global_var],eax
 0x804844b  'c744240403000000'     mov         [esp+4],0x3
 0x8048453  '8b45f4'               mov         eax,[ebp-12]
 0x8048456  '890424'               mov         [esp],eax
 0x8048459  'e825000000'           call        *#fct_b
 >>> print G.get_node('0x8048483').data
 # --- block 0x8048483 ---
 0x8048483  '55'         push        ebp
 0x8048484  '89e5'       mov         ebp,esp
 0x8048486  '8b450c'     mov         eax,[ebp+12]
 0x8048489  '8b5508'     mov         edx,[ebp+8]
 0x804848c  '01d0'       add         eax,edx
 0x804848e  '5d'         pop         ebp
 0x804848f  'c3'         ret


The **fast-backward** is another analysis that tries to evaluate the expression of
the program counter backwardly and thus reconstructs function frames in simple cases.

.. sourcecode:: python

 >>> amoco.Log.loggers['amoco.main'].setLevel(15)
 >>> z = amoco.fbackward(p)
 >>> z.getcfg()
 amoco.main: VERBOSE: root node 0x8048380 added
 amoco.main: VERBOSE: block #PLT@__libc_start_main starts a new cfg component
 amoco.cas.expressions: INFO: stub __libc_start_main called
 amoco.main: VERBOSE: function f:#PLT@__libc_start_main{2} created
 amoco.main: VERBOSE: edge <node [f:#PLT@__libc_start_main] at 0x7f422393ccd0> ---> <node [0x80484fd] at 0x7f422389a050> added
 amoco.main: VERBOSE: block 0x8048434 starts a new cfg component
 amoco.main: VERBOSE: block 0x8048483 starts a new cfg component
 amoco.main: VERBOSE: function fct_b:0x8048483{1} created
 amoco.main: VERBOSE: edge <node [fct_b:0x8048483] at 0x7f42238bd1d0> ---> <node [0x804845e] at 0x7f4223c0bbd0> added
 amoco.main: VERBOSE: block 0x80484d4 starts a new cfg component
 amoco.main: VERBOSE: function fct_e:0x80484d4{1} created
 amoco.main: VERBOSE: pc is memory aliased in fct_e:0x80484d4{1} (assume_no_aliasing)
 amoco.main: VERBOSE: edge <node [fct_e:0x80484d4] at 0x7f4223847950> ---> <node [0x804846d] at 0x7f42238bdc50> added
 amoco.main: VERBOSE: function fct_a:0x8048434{5} created
 amoco.main: VERBOSE: pc is memory aliased in fct_a:0x8048434{5} (assume_no_aliasing)
 amoco.main: VERBOSE: edge <node [fct_a:0x8048434] at 0x7f4223868150> ---> <node [0x8048561] at 0x7f4223868950> added
 amoco.main: VERBOSE: function fct_b:0x8048483{1} called
 amoco.main: VERBOSE: edge <node [fct_b:0x8048483] at 0x7f4223868c10> ---> <node [0x8048576] at 0x7f4223868f10> added
 amoco.main: VERBOSE: block 0x8048490 starts a new cfg component
 amoco.main: VERBOSE: block 0x80484ab starts a new cfg component
 amoco.main: VERBOSE: block #PLT@malloc starts a new cfg component
 amoco.cas.expressions: INFO: stub malloc called
 amoco.main: VERBOSE: function f:#PLT@malloc{2} created
 amoco.main: VERBOSE: edge <node [f:#PLT@malloc] at 0x7f422385dd90> ---> <node [0x80484c4] at 0x7f422385d9d0> added
 amoco.main: VERBOSE: function fct_d:0x80484ab{3} created
 amoco.main: VERBOSE: pc is memory aliased in fct_d:0x80484ab{3} (assume_no_aliasing)
 amoco.main: VERBOSE: edge <node [fct_d:0x80484ab] at 0x7f422385d6d0> ---> <node [0x80484a1] at 0x7f422387ba90> added
 amoco.main: VERBOSE: function fct_c:0x8048490{3} created
 amoco.main: VERBOSE: edge <node [fct_c:0x8048490] at 0x7f422387b850> ---> <node [0x8048582] at 0x7f422387bf10> added
 amoco.main: VERBOSE: edge <node [0x8048582] at 0x7f422387bf10> -?-> <node [0x8048598] at 0x7f422387bc50> added
 amoco.main: VERBOSE: block #PLT@__stack_chk_fail starts a new cfg component
 amoco.cas.expressions: INFO: stub __stack_chk_fail called
 amoco.main: VERBOSE: function f:#PLT@__stack_chk_fail{2} created
 amoco.main: VERBOSE: edge <node [f:#PLT@__stack_chk_fail] at 0x7f4223802350> ---> <node [0x804859d] at 0x7f4223802b10> added
 amoco.main: VERBOSE: function f:0x8048380{12} created
 amoco.main: VERBOSE: pc is memory aliased in f:0x8048380{12} (assume_no_aliasing)
 amoco.main: INFO: fbackward analysis stopped at <node [0x804859d] at 0x7f4223802b10>
 amoco.main: VERBOSE: edge <node [0x8048582] at 0x7f422387bf10> -?-> <node [0x804859d] at 0x7f4223802b10> added
 <amoco.cfg.graph at 0x7f13466d18d0>
 >>>

.. **

API Overview
============

Amoco is composed of 3 packages arch_, cas_ and system_, on top of which the
classes implemented in ``code.py``, ``cfg.py`` and ``main.py`` provide high-level
abstractions of basic blocks, functions, control flow graphs and
disassembling/analysis techniques.

We will now describe this architecture starting from low-level layers (arch_, cas_)
up to system_ and finally to higher level classes.

A *Sphinx* generated doc will be available soon.


arch
----

Supported CPU architectures are implemented in this package as subpackages and all
use the ``arch/core.py`` generic classes. The interface to a CPU used by
system_ classes is generally provided by a ``cpu_XXX.py`` module in the CPU subpackage.
This module shall:

- provide the CPU *environment* (registers and other internals)
- provide an instance of ``core.disassembler`` class, which requires to:

  + define the ``@ispec`` of every instruction for the generic decoder,
  + and define the *semantics* of every instruction with cas_ expressions.

- optionnally define the output assembly format, and the *GNU as* (or any other)
  assembly parser.

A simple example is provided by the ``arch/arm/v8`` architecture which provides
a model of ARM AArch64:
The interface module is ``arch/arm/cpu_armv8.py``, which imports everything from
the v8 subpackage.

instruction specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``v8/spec_armv8.py`` module implements all decoding specifications thanks
to an original decorating mechanism. For example, the EXTR instruction encoding
is defined like this:

.. sourcecode:: python

 @ispec("32[ sf 0 0 100111 N 0 Rm(5) imms(6) Rn(5) Rd(5) ]",mnemonic="EXTR")
 def A64_EXTR(obj,sf,N,Rm,imms,Rn,Rd):
     if sf!=N: raise InstructionError(obj)
     if sf==0 and imms>31: raise InstructionError(obj)
     obj.datasize = 64 if (sf==1) else 32
     regs = env.Xregs if sf==1 else env.Wregs
     obj.d = sp2z(regs[Rd])
     obj.n = sp2z(regs[Rn])
     obj.m = sp2z(regs[Rm])
     obj.lsb = env.cst(imms,6)
     obj.operands = [obj.d,obj.n,obj.m,obj.lsb]
     obj.type = type_data_processing


The ``@ispec(...)`` decorator indicates that whenever the decoder buffer is filled
with 32 bits that matches a given pattern, the decorated function is called with
first argument being a ``arch.core.instruction`` instance with ``mnemonic`` attribute
set to EXTR, and other arguments being extracted from corresponding bitfields.
The function itself is responsible for filling the instruction instance with useful
other attributes like operands, type, etc.
If you look at page 480 of armv8_, you will likely feel at home...

The same is true for ``x86/spec_ia32.py`` and the Intel manuals, for example
the CMOVcc instruction(s) specification is:

.. sourcecode:: python

 # conditionals:
 @ispec_ia32("*>[ {0f} cc(4) 0010 /r ]", mnemonic = "CMOVcc") # 0f 4x /r
 def ia32_CMOVcc(obj,cc,Mod,RM,REG,data):
     obj.cond = CONDITION_CODES[cc]
     op2,data = getModRM(obj,Mod,RM,data)
     op1 = env.getreg(REG,op2.size)
     obj.operands = [op1, op2]
     obj.type = type_data_processing

.. **

A detailed description of the ispec decorator class pattern format is provided in
``arch/core.py``. Since implementing these specifications from CPUs docs
is always error-prone, Amoco will check several things for you:

- the size of the ispec format (the "pattern" to match) is consistent with its declared length (if not \*).
- the prototype of the decorated function match the identifiers in the ispec format (count and names must match).
- the ispec format is unique: the fixed part of the pattern does not exist in any other ispec instance.

Internally, the decoder will collect all ispec instances declared within the module.
The ``core.disassembler`` setup will later organize the list in a tree based on fixed patterns of each ispec.
Note that identifying *holes* of the architecture's encoding scheme becomes relatively simple once this tree
is built.
Architectures with multiple (disjoint) instructions sets (think armv7/thumb) is supported by instanciating
the core disassembler with respective specs modules and with the function that decides how to switch
from one set to the other.

instruction semantics
~~~~~~~~~~~~~~~~~~~~~

The semantics of instructions are defined separately from their decoder specs,
generally in a ``asm.py`` module. An ``instruction`` instance with mnemonic *XXX*
will find its semantics definition by looking for a function ``i_XXX(i,fmap): ...``.

For example (in ``arch/x86/asm.py``):

.. sourcecode:: python

 def i_CMOVcc(i,fmap):
     fmap[eip] = fmap(eip)+i.length
     op1 = i.operands[0]
     op2 = i.operands[1]
     fmap[op1] = fmap(tst(i.cond[1],op2,op1))

The function takes as input the instruction instance *i* and a ``mapper``
instance *fmap* (see cas_) and implements (an approximation of) the opcode semantics.

instruction formats
~~~~~~~~~~~~~~~~~~~

How an instruction object is printed is also defined separately to allow various
outputs. A ``Formatter`` instance can be associated to the core instruction class
to handle "pretty printing", including aliases of instructions.

Basically, a ``Formatter`` object is created from a dict associating a key with a list
of functions or format string. The key is either one of the mnemonics or possibly
the name of a ispec-decorated function (this allows to group formatting styles
rather than having to declare formats for every possible mnemonic.)
When the instruction is printed, the formatting list elements are "called" and
concatenated to produce the output string.

An example follows from ``arch/x86/formats.py``:

.. sourcecode:: python

 def mnemo(i):
     mnemo = i.mnemonic.replace('cc','')
     if hasattr(i,'cond'): mnemo += i.cond[0].split('/')[0]
     return '{: <12}'.format(mnemo.lower())

 def opsize(i):
     s = [op.size for op in i.operands if op._is_mem]
     if len(s)==0: return ''
     m = max(s)
     return {8:'byte ptr ',16:'word ptr ',32:''}[m]

 ...
 format_intel_ptr = (mnemo,opsize,opers)
 ...
 IA32_Intel_formats = {
     ....
     'ia32_mov_adr' : format_intel_ptr,
     'ia32_ptr_ib'  : format_intel_ptr,
     ...
 }

The formatter is also used to take care of aliasing instructions like for example
in the arm architectures where the *ANDS* instruction is replaced by *TST* when
the destination register is X0/W0 :

.. sourcecode:: python

 def alias_AND(i):
     m = mnemo(i)
     r = regs(i)
     if i.setflags and i.d==0:
         m = 'tst'
         r.pop(0)
     return m.ljust(12) + ', '.join(r)


cas
---

The *computer algebra system* of Amoco is built with the following elements implemented
in ``cas/expressions.py``:

- Constant ``cst``, which represents immediate (signed or unsigned) value of fixed size (bitvector),
- Symbol ``sym``, a Constant equipped with a reference string (non-external symbol),
- Register ``reg``, a fixed size CPU register **location**,
- External ``ext``, a reference to an external location (external symbol),
- Floats ``cfp``, constant (fixed size) floating-point values,
- Composite ``comp``, a bitvector composed of several elements,
- Pointer ``ptr``, a memory **location** in a segment, with possible displacement,
- Memory ``mem``, a Pointer to represent a value of fixed size in memory,
- Slice ``slc``, a bitvector slice of any element,
- Test ``tst``, a conditional expression, (see Tests_ below.)
- Operator ``uop``, an unary operator expression,
- Operator ``op``, a binary operator expression. The list of supported operations is
  not fixed althrough several predefined operators allow to build expressions directly from
  Python expressions: say, you don't need to write ``op('+',x,y)``, but can write ``x+y``.
  Supported operators are:

  + ``+``, ``-``, ``*`` (multiply low), ``**`` (multiply extended), ``/``
  + ``&``, ``|``, ``^``, ``~``
  + ``==``, ``!=``, ``<=``, ``>=``, ``<``, ``>``
  + ``>>``, ``<<``, ``//`` (arithmetic shift right), ``>>>`` and ``<<<`` (rotations).

  See Operators_ for more details.

All elements inherit from the ``exp`` class which defines all default methods/properties.
Common attributes and methods for all elements are:

- ``size``,  a Python integer representing the size in bits,
- ``sf``,    the True/False *sign-flag*.
- ``length`` (size/8)
- ``mask``   (1<<size)-1
- extend methods (``signextend(newsize)``, ``zeroextend(newsize)``)
- ``_endian`` the (global class attribute) endianess for writing expression in memory can
  be set to 1 (default little endian) or -1 (big endian) with setendian() method.
- ``bytes(sta,sto)`` method to retreive the expression of extracted bytes from sta to sto indices.

All manipulation of an expression object usually result in a new expression object except for
``simplify()`` which performs in-place elementary simplifications.

Constants
~~~~~~~~~

Some examples of ``cst`` and ``sym`` expressions follow:

.. sourcecode:: python

 >>> from amoco.cas.expressions import *
 >>> c = cst(253,8)
 >>> print c
 0xfd
 >>> c.sf
 False
 >>> c.sf=True
 >>> print c
 -0x3
 >>> print c.value, type(c.value)
 -3 <type 'int'>
 >>> print c.v, c.mask, c.size
 253 255 8
 >>> c.zeroextend(16)
 <amoco.cas.expressions.cst object at 0xb728df4c>
 >>> c2 = _
 >>> print c2.sf, c2
 False 0xfd
 >>> assert c2.bytes(1,2)==0
 >>> e = c2+c.signextend(16)+5
 >>> print e
 0xff
 >>> c3 = e[0:8]
 >>> print c3==cst(-1,8)
 0x1

Here, after declaring an 8-bit constant with value 253, we can see that by default the
associated ``cst`` object is unsigned. The internal storage is always the unsigned
representation of the value. If we set its ``sf`` *sign-flag* attribute to True,
the ``value`` property will return a signed Python integer.
If the constant is inited from a negative integer, the resulting object's *sign-flag* is set to True.
If a constant is *signextended* its *sign-flag* is set automatically, unset if *zeroextended*.
Basically, during interpretation, the flag is set or unset depending on how the expression is
used by the instructions. Logical operators tend to unset it, explicit sign-relevant instructions
need to set it.

The ``cst`` class is special because it is the only class that can be used as a
Python boolean type:

.. sourcecode:: python

 >>> e==0xff
 <amoco.cas.expressions.cst object at 0x9efd7ac>
 >>> t=_
 >>> print t
 0x1
 >>> if t==True: print 'OK'
 ...
 OK
 >>> t.size
 1

In above examples, the ``==`` Python operator is used. The return value is not a Python
True/False value but as expected a new expression object. Since the operation here involves
only constants, the result need not be an ``op`` element but can be readily simplified to
a 1-bit constant with value 0 or 1.
In Amoco, the **only** expression that evaluates to True is ``cst(1,1)``.

Expressions of type ``sym`` are constants equipped with a symbol string for printing purpose only:

.. sourcecode:: python

 >>> s = sym('Hubble',42,8)
 >>> print s
 #Hubble
 >>> s.value
 42
 >>> print s+1
 0x2b

(Note that as seen above, usage of a ``sym`` object in another expression will obviously
forget the symbol string in the resulting expression.)

Registers
~~~~~~~~~

Expressions of class ``reg`` are pure symbolic values.
They are essentially used for representing the registers of a CPU, as "right-values"
or left-values (locations). More details on *locations* in mapper_.

.. sourcecode:: python

 >>> a = reg('%a',32)
 >>> print a
 %a
 >>> e = 2+a
 >>> print e
 (%a+0x2)
 >>> x = e-2
 >>> print x
 (%a-0x0)
 >>> x.simplify()
 <amoco.cas.expressions.reg object at 0xb7250f6c>
 >>> print _
 %a

As shown above, elementary simplification rules are applied such that ``(2+a)-2``
leads to an ``op`` expression with operator ``-``, right member 0 and left member ``r1``,
which eventually also simplifies further to the r1 register.
Most real simplification rules should rely on SMT solvers like z3_ (see smt_).

Externals
~~~~~~~~~

Class ``ext`` inherit from registers as pure symbolic values
but is used to represent external symbols that are equipped with a ``stub`` function.
When "called", these objects can invoke their stub function in two ways:

- when the program counter is an ``ext`` expression,
  the object invokes its __call__ method to modify the provided mapper by calling the
  registered *stub* with the mapper and possibly other needed parameters.
- when used to simulate actions of *interruptions* like for example
  in the semantics of ``IN/OUT`` or ``INT`` instructions which invoke the object's ``call``
  method to eventually return an expression.

(More details on ``@stub`` decorated functions are provided in system_.)

Pointers and Memory objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``ptr`` object is a memory **location**. These objects are generally not found
in expressions but only as mapper_ locations or addresses in ``mem`` objects.
They have a ``base`` expression, a ``disp`` integer offset,
and an optional ``seg`` attribute to be used by MemoryZone_ objects.

As illustrated below, simplification of ``ptr`` objects tends to extract constant
offsets found in the base expression to adjust the ``disp`` field.

.. sourcecode:: python

 >>> a = reg('a',32)
 >>> p = ptr(a)
 >>> q = ptr(a,disp=17)
 >>> print p,q
 (a) (a+17)
 >>> assert p+17 == q
 >>> assert p+2  == q-15
 >>> assert (p+3).base == (q-5).base


A ``mem`` object is a symbolic memory value equipped with a pointer, a size, and
a special ``.mods`` attribute that will be discussed in mapper_.

.. sourcecode:: python

 >>> x = mem(p,64,disp=2)
 >>> y = mem(q-5,48,disp=-10)
 >>> print x,y
 M64(a+2) M48(a+2)
 >>> assert x.bytes(4,6) == y[32:48]


Note: the segment attribute is currently not used by the core memory classes.


Operators
~~~~~~~~~

Unary operators (``+``, ``-`` and ``~``) have elementary simplification rules:

.. sourcecode:: python

 >>> a = reg('a',32)
 >>> assert +a == -(-a)
 >>> assert -a == 0-a

Most operations in Amoco involve left and right members sub-expressions. The operation
will then usually proceed only if both member have the same size. If one member is not
an expression but a Python integer, it will be implicitly "casted" to a constant of size
required by the other expression member. Thus, it is possible to write ``r1+2`` and not
``r1+cst(2,32)``.

Binary operations have elementary simplification rules that try to arrange symbols
in lexical order and move constants to the right side of the expression.

.. sourcecode:: python

 >>> a = reg('a',32)
 >>> b = reg('b',32)
 >>> print a+0, a*1, a^a, a*0, a&0, a|0
 a a 0x0 0x0 0x0 a
 >>> print (b-a)|0
 ((-a)+b)
 >>> assert b-a == (-a)+b
 >>> assert -(a+b) == (-a)-b
 >>> assert -(a-b) == b-a
 >>> assert -(b-a) == (a-b)*1
 >>> assert -(1-a) == a-1
 >>> assert (-a+(b-1)) == b-a-1
 >>> e = -((b-1)-a)
 >>> assert e == 1+(a-b)
 >>> print e
 ((a-b)+0x1)
 >>> extract_offset(e)
 (<amoco.cas.expressions.op object at 0x7f864e8496b0>, 1)
 >>> print _[0]
 (a-b)

Internal attributes and methods of ``op`` instances are:

- ``.op``, the operator symbol (``.op.symbol``) and function (``.op.impl``),
- ``.r``, the left member sub-expression,
- ``.l``, the right member sub-expression of binary ops.
- ``.prop``, an or-ed flag indicating the kind of operators involved:

  + 1 means only arithmetic,
  + 2 means only logic,
  + 4 means only conditional,
  + 8 means only shifts and rotations,

- ``depth()`` returns the expression tree depth,
- ``limit(value)`` is a class method used to set a threshold parameter involved
  in simplifying the expression to ``top`` when the expression's complexity is too high.

The ``symbols_of(e)`` function returns the list of registers expressions involved in ``e``.
The ``locations_of(e)`` function returns the list of *locations* used in ``e``.
The ``complexity(e)`` function computes an arbitrary complexity measure of expression ``e``
which is linear in depth and number of symbols, and increases by a factor of ``prop``.

Composer and Slicer
~~~~~~~~~~~~~~~~~~~

A ``comp`` object is a composite expression corresponding to a bit-vector made of
several expression parts.
A ``slc`` object is the expression obtained by extracting a bit-vector slice out
of an expression.

The ``composer(parts)`` function, which takes as input the parts as a list of expressions in
least-to-most significant order, is the preferred method for instanciating composite objects.
Since ``comp`` is essentially a container class for other expressions, the resulting object
is possibly of another class if some simplification occured.

.. sourcecode:: python

 >>> composer([cst(1,8),cst(2,8),cst(3,8)])
 <amoco.cas.expressions.cst at 0x7f9468252c20>
 >>> c=_
 >>> assert c == 0x030201
 >>> a = reg('a',32)
 >>> b = reg('b',32)
 >>> c = comp(24)
 >>> c[0:8] = (a+b)[24:32]
 >>> c[8:24] = b[0:16]
 >>> print c
 { | [0:8]->(a+b)[24:32] | [8:24]->b[0:16] | }
 >>> c[8:16] = cst(0xff,8)
 >>> print c
 { | [0:8]->(a+b)[24:32] | [8:16]->0xff | [16:24]->b[8:16] | }
 >>> c[0:8] = cst(0x01,8)
 >>> print c
 { | [0:8]->0x1 | [8:16]->0xff | [16:24]->b[8:16] | }
 >>> print c.simplify()
 { | [0:16]->0xff01 | [16:24]->b[8:16] | }

As shown above, a composite instance supports dynamic asignment of any parts defined by a python
slice object. Simplification of composite objects tends to merge contiguous constant parts.

A ``slc`` expression is obtained by using a python slice object of the form [start:stop]
where start/stop are non-negative integers in the bit range of the sliced expression.
Simplification occurs when the sliced expression is itself of class ``slc`` or ``mem``:

.. sourcecode:: python

 >>> a = reg('%a',32)
 >>> ah = slc(a,24,8,ref='%ah')
 >>> assert ah.x == a
 >>> print ah.pos
 24
 >>> print ah
 %ah
 >>> ax = a[16:32]
 >>> print ax
 %a[16:32]
 >>> print ax[0:8]
 %a[16:24]
 >>> print ax[8:16]
 ah
 >>> y = mem(a,64)
 >>> print y[16:48]
 M32(%a+2)

Note that, as shown above, slices of registers can be instanciated with an optional
reference string that is used for printing whenever the matching register slice is involved.

Note also that parts and slices [start:stop] bounds are limited to python integers only
(indices can't be symbolic!)


Conditionals
~~~~~~~~~~~~

The ``tst`` class is used for conditional expressions in the form ``tst(cond, eT, eF)``
where ``cond`` is an expression, ``eT`` is the resulting expression whenever
``cond==1`` and ``eF`` is the resulting expression whenever ``cond==0``.

.. sourcecode:: python

 >>> t = tst(a>0, c, cst(0xdeadbe,24))
 >>> print t
 ((%a>0x0) ? { | [0:16]->0xff01 | [16:24]->b[8:16] | } : 0xdeadbe)
 >>> t.l[16:24] = cst(0xab,8)
 >>> print t.simplify()
 ((%a>0x0) ? 0xabff01 : 0xdeadbe)
 >>> t.tst.l = cst(-1,32)
 >>> print t
 ((-0x1>0x0) ? 0xabff01 : 0xdeadbe)
 >>> print t.simplify()
 0xdeadbe


mapper
~~~~~~

A ``mapper`` object captures the symbolic operations of a sequence of instructions by
mapping input expressions to output *locations* which are registers or pointers.
It represents the transition function from an input state to an output state corresponding
to the execution of the captured instructions.
As shown in the ``i_MOVcc`` example above, the ``fmap`` argument of every instruction semantics
is a mapper on which the instruction currently operates (see asm_).

.. sourcecode:: python

 >>> from amoco.arch.x86.env import *
 >>> from amoco.cas.mapper import mapper
 >>> m = mapper()
 >>> m[eax] = cst(0xabff01,32)
 >>> print m
 eax <- { | [0:32]->0xabff01 | }
 >>> print m(eax)
 0xabff01
 >>> print m(ah)
 0xff
 >>> m[eax[16:32]] = bx
 >>> print m
 eax <- { | [0:16]->0xff01 | [16:32]->bx | }
 >>> print m(ax+cx)
 (cx+0xff01)
 >>> print m(eax[16:32]^ecx[16:32])
 (bx^ecx[16:32])
 >>> print m(mem(ecx+2,8))
 M8(ecx+2)
 >>> print m(mem(eax+2,8))
 M8({ | [0:16]->0xff01 | [16:32]->bx | }+2)

The mapper class defines two essential methods to set and get expressions in and out.

- ``__setitem__`` is used for mapping any expression to a location which can be a register
  (or a register slice), a pointer or a memory expression. When the location is a pointer,
  the base expression refers to input state values, whereas a memory expression refers to
  the output state (see example below).
- ``__call__`` is used for evaluating any expression in the mapper, by replacing every
  register and memory object of the expression by their mapped expressions.

A *push* instruction could thus be implemented using:

.. sourcecode:: python

 >>> def push(fmap,x):
 ...   fmap[esp] = fmap(esp)-x.length
 ...   fmap[mem(esp,x.size)] = x      # put x at the current (updated) esp address
 ...
 >>> m.clear()
 >>> push(m, cst(0x41414141,32))
 >>> print m
 esp <- { | [0:32]->(esp-0x4) | }
 (esp-4) <- 0x41414141
 >>> push(m, ebx)
 >>> print m
 (esp-4) <- 0x41414141
 esp <- { | [0:32]->(esp-0x8) | }
 (esp-8) <- ebx

Note that a ``__getitem__`` method is implemented as well in order to fetch items
that are locations of the mapper. So here, to get the value at the top of stack, we
can do:

.. sourcecode:: python

 >>> print m[mem(esp-8,32)]  # fetch the expression associated with ptr (esp-8)
 ebx
 >>> print m(mem(esp,32))    # evaluates mem(esp,32) => first evaluate ptr, then fetch.
 ebx
 >>> print m(mem(esp+4,32))
 0x41414141
 >>> print m[mem(esp-4,32)]
 0x41414141

The internal memory model of a mapper is a MemoryMap_: symbolic memory locations are related
to individual separated MemoryZone_ objects that deal with all read/write to/from location's
``ptr.base`` expression.

.. sourcecode:: python

 >>> print m.memory()
 <MemoryZone rel=None :>
 <MemoryZone rel=esp :
          <mo [-0000008,-0000004] data:ebx>
          <mo [-0000004,00000000] data:0x41414141>>

This model allows to access offsets that have not been explicitly written to before.
For example, if we now execute *mov ecx, [esp+2]* we still fetch the correct expression:

.. sourcecode:: python

 >>> m[ecx] = m(mem(esp+2,32))
 >>> print m(ecx)
 { | [0:16]->ebx[16:32] | [16:32]->0x4141 | }

However, aliasing between zones is possible a must be avoided: imagine that we now
execute *mov byte ptr [eax], 0x42*, we obtain:

.. sourcecode:: python

 >>> m[mem(eax,8)] = cst(0x42,8)
 >>> print m
 (esp-4) <- 0x41414141
 esp <- { | [0:32]->(esp-0x8) | }
 (esp-8) <- ebx
 ecx <- { | [0:16]->ebx[16:32] | [16:32]->0x4141 | }
 (eax) <- 0x42
 >>> print m.memory()
 <MemoryZone rel=None :>
 <MemoryZone rel=eax :
         <mo [00000000,00000001] data:0x42>>
 <MemoryZone rel=esp :
         <mo [-0000008,-0000004] data:ebx>
         <mo [-0000004,00000000] data:0x41414141>>

If we now again fetch memory at ``esp+2`` the previous answer is not valid anymore due
to a possible aliasing (overlapping) of ``eax`` and ``esp`` zones. Think of what should
the memory look like if ``eax`` value was ``esp-4`` for example. Let's try:

.. sourcecode:: python

 >>> print m(mem(esp+2,32))
 M32$3(esp-6)
 >>> mprev = mapper()
 >>> mprev[eax] = esp-4
 >>> print mprev( m(mem(esp+2,32)) )
 { | [0:16]->ebx[16:32] | [16:32]->0x4142 | }

Indeed, the mapper returns a special memory expression that embeds modifications
(saved in ``.mods`` of the mem expression) that have been applied on its memory until now,
and that must be executed in order to return a correct answer. As demonstrated above,
these mods are taken into account whenever the expression is evaluated in another mapper.

Note that it is possible to force the mapper class to *assume no aliasing* :

.. sourcecode:: python

 >>> print mapper.assume_no_aliasing
 False
 >>> mapper.assume_no_aliasing = True
 >>> print m(mem(esp+2,32))
 { | [0:16]->ebx[16:32] | [16:32]->0x4141 | }

In Amoco, a mapper instance is created for every basic block. The right
and left shift operators allow for right of left composition so that symbolic
forward or backward execution of several basic blocks is easy:

.. sourcecode:: python

 >>> m1 = mapper()
 >>> m1[eax] = ebx
 >>> push(m1,eax)
 >>> m2 = mapper()
 >>> m2[ebx] = cst(0x33,32)
 >>> push(m2,ebx)
 >>> m2[eax] = m2(mem(esp,32))
 >>> print m1
 eax <- { | [0:32]->ebx | }
 esp <- { | [0:32]->(esp-0x4) | }
 (esp-4) <- eax
 >>> print m2
 ebx <- { | [0:32]->0x33 | }
 esp <- { | [0:32]->(esp-0x4) | }
 (esp-4) <- ebx
 eax <- { | [0:32]->ebx | }
 >>> print m1>>m2 # forward execute m1 -> m2
 (esp-4) <- eax
 ebx <- { | [0:32]->0x33 | }
 esp <- { | [0:32]->(esp-0x8) | }
 (esp-8) <- ebx
 eax <- { | [0:32]->ebx | }
 >>> print m2<<m1 # backward execute the same blocks/mappers
 (esp-4) <- eax
 ebx <- { | [0:32]->0x33 | }
 esp <- { | [0:32]->(esp-0x8) | }
 (esp-8) <- ebx
 eax <- { | [0:32]->ebx | }

TODO: mapper unions.

smt
~~~

Amoco uses z3_ for constraint solving by translating its equation expressions
into z3_ equivalent objects. The interface with z3_ is implemented in ``cas/smt.py``.

- ``cst`` expressions are translated as ``BitVecVal`` objects
- ``cfp`` expressions are translated as ``RealVal`` objects
- ``reg`` expressions are translated as ``BitVec`` objects
- ``comp`` expressions use the z3_ ``Concat`` function
- ``slc`` expressions use the z3_ ``Extract`` function
- ``mem`` expressions are converted as Concat of ``Array`` of ``BitVecSort(8)``,
  with current endianess taken into account.
- ``tst`` expressions use the z3_ ``If`` function
- operators are translated by propagating translations to left & right sides.

When the ``smt`` module is imported it replaces the ``.to_smtlib()`` method of
every expression class (which by default raises UnImplementedError).

.. sourcecode:: python

 >>> from amoco.arch.x86.env import *
 >>> from amoco.cas import smt
 >>> z = (eax^cst(0xcafebabe,32))+(ebx+(eax>>2))
 >>> print z
 ((eax^0xcafebabe)+(ebx+(eax>>0x2)))
 >>> print z.to_smtlib()
 (eax ^ 3405691582) + ebx + LShR(eax, 2)
 >>> print z.to_smtlib().sexpr()
 (bvadd (bvxor eax #xcafebabe) ebx (bvlshr eax #x00000002))
 >>> r = smt.solver([z==cst(0x0,32),al==0xa,ah==0x84]).get_model()
 >>> print r
 [eax = 33802, ebx = 889299018]
 >>> x,y = [r[v].as_long() for v in r]
 >>> ((x^0xcafebabe)+(y+(x>>2)))&0xffffffffL
 0L
 >>> p = mem(esp,32)
 >>> q = mem(esp+2,32)
 >>> ql = q[0:16]
 >>> ph = p[16:32]
 >>> z = (p^cst(0xcafebabe,32))+(q+(p>>2))
 >>> m = smt.solver().get_mapper([z==cst(0,32),esp==0x0804abcd])
 >>> print m
 (esp+2) <- 0x7ffc9151
 (esp) <- 0x9151babe
 esp <- { | [0:32] -> 0x0804abcd | }


In the ``smt`` module, the ``solver`` class is typically used to verify that some
properties hold and find a set of input (concrete) values to be set for example in
an emulator or debugger to reach a chosen branch. A solver instance can be created with
a python list of expressions, or expressions can be added afterward.

The ``.get_model()`` method will check added contraint equations and return a
z3_ ``ModelRef`` object if the z3_ solver has returned ``z3.sat`` or None otherwise.
A list of equations to be taken into account can be provided as well with ``.add()``.

The ``.get_mapper()`` method calls ``get_model`` and returns a mapper object with
locations set to their ``cst`` values. A list of equations can be provided here too.

main.py
-------

This module contains *high-level* analysis techniques implemented as classes that
take a program abstraction provided by the system_ package.

The first 3 basic techniques are:

- *linear-sweep* (``lsweep`` class) disassembles instructions without taking
  into account any branching instruction.

  Methods exposed by the ``lsweep`` class are:

  * ``sequence(loc=None)``: returns an iterator that will yield disassembled
    instructions starting at virtual address *loc* (defaults to entrypoint).
  * ``iterblocks(loc=None)``: which returns an iterator that will yield (basic) block_
    of instructions starting at virtual address *loc*.

- *fast forward* (``fforward``) inherits from ``lsweep`` and adds an algorithm that
  tries to build the control-flow graph of the program by following branching
  instructions when the program counter is composed essentially of constant
  expressions when evaluated within block scope only.
  The default policy is to fallback to linear sweep otherwise.

- *link forward* (``lforward``) inherits from ``fforward`` but uses a strict
  follow branch policy to avoid linear sweep and evaluates the program counter
  by taking into account the parent block semantics.

Other more elaborated techniques are:

- *fast backward* (``fbackward``) inherits from ``lforward`` but evaluates the
  program counter backardly by taking *first-parent* block until either the
  expression is a constant target or the root node of the graph component (entry of function)
  is reached. The analysis proceeds then by evaluating the pc expression in every
  caller blocks, assuming that no frame-aliasing occured (pointer arguments did not
  mess up with the caller's stack.) A ``func`` instance is created but its mapper
  contains by default only the computed pc expression.

- *link-backward* (``lbackward``) inherits from ``fbackward`` but walks back *all*
  parent-paths up to the entry node, composing and assembling all mappers to end up
  with an approximated mapper of the entire function.

code.py
-------

The ``code`` module defines two main classes:

- a ``block`` contains a list of instructions and computes the associated mapper object.
  The arch-dependent CoreExec classes (see system_ below) can add ``tag`` indicators like
  ``FUNC_START`` (if block looks like a function entry), ``FUNC_CALL`` if block makes a call, etc.
- a ``func`` contains the cfg graph component of a function once it has been fully
  recovered by an analysis class. It inherits from ``block`` and contains a mapper that
  captures an approximation of the entire function.

blocks are created by the ``lsweep.iterblocks()`` iterator (or by  ``.get_block()``) which
is inherited by all ``main`` analysis classes discussed above. Functions are created by
``fbackward`` and ``lbackward`` classes only.

The ``xfunc`` class is used when an external expression is called. It contains a mapper
build by a ``stub`` function. Instances are present in graph nodes but have a zero length
and no address and thus do not exist in memory.

cfg.py
------

Classes ``node``, ``link`` and ``graph`` use *grandalf* Vertex/Edge/Graph with additional
formatters or way to compare instances by name. A node's data is a block instance, and an
edge's data is possibly a set of conditional expressions. A graph connected component is
a function's control-flow graph  (a *graph_core* object).
The ``graph.add_vertex`` extends Graph.add_vertex to detect that the node to be added *cuts*
an existing node and adjust the graph structure accordingly.
The ``graph.spool()`` method provides a list of the current leaves in the graph.
The ``graph.get_node(name)`` method allows to get a node object by its name.

system
------

The system_ package is the main interface with the binary program. It contains executable
format parsers, the memory model, the execution engine, and some operating system
models responsible for mapping the binary in the memory model, setting up the environment
and taking care of system calls.

The ``loader.py`` module is the frontend that will try to parse the input file and import the
targeted system_ and arch_ modules. If the executable format is unkown or if the input is a
bytecode python string, the binary is mapped at address 0 in a ``RawExec`` instance.

The ``elf.py`` module implements the ``Elf32`` and ``Elf64`` classes. The ``pe.py`` module
implements the ``PE`` class which handles both PE32 and PE32+ (64-bits).

The ``core.py`` module implements the memory model classes and the CoreExec_ generic
execution engine inherited by various system's classes like ``linux_x86.ELF``,
``linux_arm.ELF`` or ``win32.PE`` and ``win64.PE``.

MemoryZone
~~~~~~~~~~

The memory model in Amoco is implemented by the MemoryMap class in ``system/core.py``. Instance
of MemoryMap are created by the system's CoreExec classes and by every block's mapper_ objects.
This model associates memory locations with raw bytes or symbolic expressions in separated *zones*
implemented by the MemoryZone_ class.
Each zone is associated with a symbolic location reference, the default ``None`` reference zone
being used for concrete (cst) locations.
In a MemoryZone_, an *address* is an integer offset to the reference location expression, and
the associated *value* is a ``mo`` memory object that stores bytes or an expression wrapped in
a ``datadiv`` object.

CoreExec
~~~~~~~~

The execution engine core class is the users's frontend to the binary. It is responsible for
creating a MemoryMap with the binary image, reading data in memory, or reading instructions
at some address by calling ``cpu.disassemble()``.

stubs
~~~~~

System calls and externals are emulated by implementing ``stubs`` that modify a mapper instance. A *stub*
is a Python function decorated with ``@stub``. For example, for example in
the *Linux* system (see ``linux_x86.py``), the *__libc_start_main* is approximated by:

.. sourcecode:: python

 @stub
 def __libc_start_main(m,**kargs):
     m[cpu.eip] = m(cpu.mem(cpu.esp+4,32))
     cpu.push(m,cpu.ext('exit',size=32))

The default stub performs only a ``ret``-like instruction.

Licence
=======

Please see `LICENSE`_.


Changelog
=========

- `v2.4.1`_

  * add lbackward analysis and func.makemap() implementations
  * add vec expression class to represent a set of expressions
  * add mapper merge and widening functions
  * allow to pass smt solver instance in exp.to_smtlib()
  * add funchelpers methods in x86-based system classes
  * add session/db classes and pickle-specific methods
  * add "progress" method in Log class to provide feedback
  * add required external packages in setup.py
  * fix some x86/x64 semantics
  * improve sparc v8 formats
  * update README

- `v2.4.0`_

  * merge Z3 solver interface, see smt.py and smtlib() exp method
  * merge fbackward analysis and code func class.
  * improve expressions: separate unary and binary ops, "normalize" expressions
  * improve mapper with memory() method and aliasing-resistant composition operators
  * improve MemoryZone class: return top expression parts instead of raising MemoryError.
  * adding RawExec class for shellcode-like input
  * support string input in ELF/PE classes.
  * fix various x86/x64 bugs
  * protect against resizing of env registers
  * add win64 loader
  * adjust log levels and optional file from conf
  * update README

- `v2.3.5`_

  * add x64 arch + full x86/64 SSE decoder
  * hotfix x86/x64 inversion of {88}/{8a} mov instructions
  * fix various x86 decoders and semantics
  * code cosmetics

- `v2.3.4`_

  * merge armv7/thumb fixed semantics
  * add x86 fpu decoders
  * add locate function in MemoryMap
  * Fix core read_instruction on map boundary
  * Fix PE import parsing and TLS Table builder
  * faster generic decoder
  * hotfix various x86 decoders
  * add some x86 SSE decoders

- `v2.3.3`_

  * support for MSP430 and PIC18 microcontrollers
  * fix sparc rett, udiv/sdiv and formats
  * fix x86 jcxz instruction decoding

- `v2.3.2`_

  * merge z80/GB architecture, fix sparc reported issues
  * add example of SSE2 decoding (fixed)

- `v2.3.1`_

  * add licence file
  * fix sparc architecture
  * avoid ptr expression when address is not deref
  * fix eqn_helpers simplifier rules
  * README updated
  * new PE class (tested on CoST.exe) + support for multiple entrypoints.


.. _grandalf: https://github.com/bdcht/grandalf
.. _crysp: https://github.com/bdcht/crysp
.. _minisat: http://minisat.se/
.. _z3: http://z3.codeplex.com/
.. _pygments: http://pygments.org/
.. _armv8: http://www.cs.utexas.edu/~peterson/arm/DDI0487A_a_armv8_arm_errata.pdf
.. _pyparsing: http://pyparsing.wikispaces.com/
.. _ply: http://www.dabeaz.com/ply/
.. _zodb: http://www.zodb.org
.. _LICENSE: https://github.com/bdcht/amoco/blob/release/LICENSE
.. _v2.4.1: https://github.com/bdcht/amoco/releases/tag/v2.4.1
.. _v2.4.0: https://github.com/bdcht/amoco/releases/tag/v2.4.0
.. _v2.3.5: https://github.com/bdcht/amoco/releases/tag/v2.3.5
.. _v2.3.4: https://github.com/bdcht/amoco/releases/tag/v2.3.4
.. _v2.3.3: https://github.com/bdcht/amoco/releases/tag/v2.3.3
.. _v2.3.2: https://github.com/bdcht/amoco/releases/tag/v2.3.2
.. _v2.3.1: https://github.com/bdcht/amoco/releases/tag/v2.3.1
