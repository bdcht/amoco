=====
Amoco
=====
 +-----------+-----------------------------------+
 | Status:   | Under Development                 |
 +-----------+-----------------------------------+
 | Location: | https://github.com/bdcht/amoco    |
 +-----------+-----------------------------------+
 | Version:  | 2.3                               |
 +-----------+-----------------------------------+

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
- a symbolic algebra module which allows to describe the semantics of
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
(z80, armv7/thumb) and executable formats (PE, Gameboy Cardridge).
In 2013 the internal decoding system was redesigned, and the minisat solver
was replaced by z3_. The armv8 and sparc architectures were added.

Despite being (just) yet another tool for analysing binaries,
in 2014 a dedicated 'release' branch was created with most of the above
features to be open-sourced.

Todo
====

Some components of Amoco are still in the
process of being pushed to the release branch or further developed.
More precisely:

- x86 fpu and sse decoder specs (arch/x86/spec_{fpu,sse2}.py) are not implemented,
- arm v7 semantics (arch/arm/v7/asm.py) is currently not merged,
- arm SIMD, VFP, NEON, TrustZone, Jazelle instruction sets are not implemented,
- z80 arch is currently not merged,
- pretty printers based on pygments package are not merged,
- interface to z3 solver (and associated analysis) is currently not merged,
- backward and solver-based disassembling strategies are not merged yet.

Contributions to fulfill uncomplete/unimplemented parts are welcome.

Install
=======

Amoco depends on the following python packages:

- grandalf_
- crysp_
- z3_  (not in current release)
- pygments_ (not in current release)

Quickstart
==========

Look for various examples in tests/. Below is a very simple example where
basic blocks are build with linear sweep:

.. sourcecode:: python

 >>> import amoco
 >>> p = amoco.system.loader.load_program('tests/samples/flow.elf')
 amoco.system.loader: INFO: Elf32 file detected
 amoco.system.loader: INFO: linux_x86 program created
 >>> p
 <amoco.system.linux_x86.ELF object at 0x8b23d4c>


We are analysing 'flow.elf' file. Since we don't know nothing about it
we start by using a high level loader which will try to detect its format
and target platform and provide some feedback info. Here the loader
creates a ``linux_x86.ELF`` object which shall represent the program task.

.. sourcecode:: python

 >>> p.bin
 <amoco.system.elf.Elf32 object at 0xb721a48c>
 >>> print p.mmap
 <MemoryZone rel=None :
          <mo [08048000,08049ff0] data:'\x7fELF\x01\x01\x01\x00\x00\x00...>
          <mo [08049ff0,08049ff4] data:@__gmon_start__>
          <mo [08049ff4,0804a000] data:'(\x9f\x04\x08\x00\x00\x00\x00\x...>
          <mo [0804a000,0804a004] data:@__stack_chk_fail>
          <mo [0804a004,0804a008] data:@malloc>
          <mo [0804a008,0804a00c] data:@__gmon_start__>
          <mo [0804a00c,0804a010] data:@__libc_start_main>
          <mo [0804a010,0804a02c] data:'\x00\x00\x00\x00\x00\x00\x00\x0...>>
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
 0x804839c  e8cfffffff                     call        \*0x8048370
 >>> b.instr
 [<amoco.arch.x86.spec_ia32 [0x8048380]  XOR ( length=2 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048382]  POP ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048383]  MOV ( length=2 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048385]  AND ( length=3 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048388]  PUSH ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048389]  PUSH ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x804838a]  PUSH ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x804838b]  PUSH ( length=5 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048390]  PUSH ( length=5 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048395]  PUSH ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048396]  PUSH ( length=1 type=1 )>, <amoco.arch.x86.spec_ia32 [0x8048397]  PUSH ( length=5 type=1 )>, <amoco.arch.x86.spec_ia32 [0x804839c]  CALL ( length=5 type=2 )>]
 >>> i = b.instr[-1]
 >>> i
 <amoco.arch.x86.spec_ia32 [0x804839c]  CALL ( length=5 type=2 )>
 >>> print i
 0x804839c  e8cfffffff                     call        \*0x8048370
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


We use here the most basic 'linear sweep' approach and spawn a basic
block iterator. The first block is well known. We can see that the default
x86 pretty printer uses Intel syntax and codehelpers that show PLT refs
as associated .got ``ext`` objects. Also, relative offsets are displayed
as absolute addresses (indicated by the '*' prefix).

Lets look at the symbolic execution of this block:

.. sourcecode:: python

 >>> b.map
 <amoco.cas.mapper.mapper object at 0x9cba3ec>
 >>> print b.map
 ebp <- { | [0:32]->0x0 | }
 esi <- { | [0:32]->M32(esp) | }
 ecx <- { | [0:32]->(esp+0x4) | }
 eflags <- { | [0:1]->0x0 | [6:7]->((((esp+0x4)&0xfffffff0)==0x0) ? 0x1 : 0x0) | [12:32]->eflags[12:32] | [11:12]->0x0 | [8:11]->eflags[8:11] | [1:6]->eflags[1:6] | [7:8]->((((esp+0x4)&0xfffffff0)<0x0) ? 0x1 : 0x0) | }
 ((((esp+0x4)&0xfffffff0)-0x4)) <- eax
 ((((esp+0x4)&0xfffffff0)-0x8)) <- (((esp+0x4)&0xfffffff0)-0x4)
 ((((esp+0x4)&0xfffffff0)-0xc)) <- edx
 ((((esp+0x4)&0xfffffff0)-0x10)) <- 0x8048610
 ((((esp+0x4)&0xfffffff0)-0x14)) <- 0x80485a0
 ((((esp+0x4)&0xfffffff0)-0x18)) <- (esp+0x4)
 ((((esp+0x4)&0xfffffff0)-0x1c)) <- M32(esp)
 ((((esp+0x4)&0xfffffff0)-0x20)) <- 0x80484fd
 esp <- { | [0:32]->(((esp+0x4)&0xfffffff0)-0x24) | }
 ((((esp+0x4)&0xfffffff0)-0x24)) <- (eip+0x21)
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

Overview
========

main.py
-------

code.py
-------

cfg.py
------

system
------

MemoryZone
~~~~~~~~~~

arch
----

cas
---

.. _grandalf: https://github.com/bdcht/grandalf
.. _crysp: https://github.com/bdcht/crysp
.. _minisat: http://minisat.se/
.. _z3: http://z3.codeplex.com/
.. _pygments: http://pygments.org/
