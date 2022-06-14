=====
Amoco
=====

.. image:: https://travis-ci.org/bdcht/amoco.svg?branch=release
    :target: https://travis-ci.org/bdcht/amoco

.. image:: http://readthedocs.org/projects/amoco/badge/?version=latest
    :target: http://amoco.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/lgtm/grade/python/g/bdcht/amoco.svg?logo=lgtm&logoWidth=18
    :target: https://lgtm.com/projects/g/bdcht/amoco/context:python
    :alt: Code Quality


+-----------+--------------------------------------------------+
| Status:   | Under Development                                |
+-----------+--------------------------------------------------+
| Location: | https://github.com/bdcht/amoco                   |
+-----------+--------------------------------------------------+
| Version:  | 2.9 (pre-3.0)                                    |
+-----------+--------------------------------------------------+
|  Doc:     | http://amoco.readthedocs.io/en/latest/index.html |
+-----------+--------------------------------------------------+

Description
===========

Amoco is a python (>=3.8) package dedicated to symbolic analysis of binaries.

It features:

- a generic framework for decoding instructions, developed to reduce
  the time needed to implement support for new architectures.
  For example the decoder for most IA32 instructions (general purpose)
  fits in less than 800 lines of Python.
  The full SPARCv8 RISC decoder (or the ARM THUMB-1 set as well) fits
  in less than 350 lines. The ARMv8 instruction set decoder is less than
  650 lines.
- a **symbolic** algebra module which allows to describe the semantics of
  every instructions and compute a functional representation of instruction
  blocks.
- a generic execution model which provides an abstract memory model to deal
  with concrete or symbolic values transparently, and other system-dependent
  features.
- various classes implementing usual disassembly techniques like linear sweep,
  recursive traversal, or more elaborated techniques like path-predicate
  which relies on SAT/SMT solvers to proceed with discovering the control
  flow graph or even to implement techniques like DARE (Directed Automated
  Random Exploration).
- various generic *helpers* and arch-dependent pretty printers to allow
  custom look-and-feel configurations (think AT&T vs. Intel syntax,
  absolute vs. relative offsets, decimal or hex immediates, etc).

Amoco is still *work in progress*. See Todo_ for a list of features to be
merged from develop branch or to be more thoroughly implemented.

User documentation and API can be found at
`http://amoco.readthedocs.io/en/latest/index.html`

.. image:: https://github.com/bdcht/amoco/blob/release/doc/gui_load.png
   :width: 600

Todo
====

Some components of Amoco are still in the
process of being pushed to the release branch or further developed.
More precisely:

- x86 fpu instructions semantics are not implemented,
- arm SIMD, VFP, NEON, TrustZone, Jazelle instruction sets are not implemented,
- some solver-based disassembling strategies are not merged yet.
- idb import/export features are not implemented.
- 6502 and PPC archs are planned.

Contributions to fulfill uncomplete/unimplemented parts are welcome.

Developer notes
===============

The default Qt stylesheet is inspired by the excellent QDarkStyleSheet_ and
uses most of its icons through the *QResource* API made available
from the generated *rc_icons.py* module::

  <pyenv>/lib/python3.<x>/site-packages/PySide6/rcc -g python icons.qrc > rc_icons.py


Licence
=======

Please see `LICENSE`_.


Changelog
=========

- `v2.9.8`_

  * update to PySide6 (Qt6)
  * add ole2 format
  * update structs subpackage to allow chosen pointer sizes
  * partial update of avr architecture

- `v2.9.7`_

  * drop python <3.8 support
  * improve structs package for bitfield support and computation of
    fields' offsets for chosen pointer size (32 or 64 bits)

- `v2.9.6`_

  * merge Qt GUI ImageView
  * improve Qt GUI binfmtview/HexView with entropy & InfoView
  * add specific Mach-O view
  * improve support for Qt ui dark mode
  * add Tricore architecture
  * add w65c02 architecture
  * add wasm architecture
  * add wasm binary format parser
  * move system.structs module into a package

- `v2.9.5`_

  * merge Qt GUI binfmtview/HexView
  * fix various ARM instructions' decoder and semantics
  * add structure view and specific ELF and PE views
  * add support for Qt ui dark mode
  * add MIPS loaders
  * add BitField support in structs

- `v2.9.4`_

  * add linux32 loaders for mips_le/sparc/riscv
  * update win32/win64 system interfaces
  * add mapper support for non-interlocking pipeline
  * fix MIPS R3000 load/store delayed pipeline effects
  * add archView class
  * add RISCV64 architecture (riscv.rv64i)
  * add precondition test for specs
  * update *all* arch specs to avoid collisions
  * improve/fix various arch formats
  * fix x86 parser

- `v2.9.3`_

  * merge/update dbgui emul and srv commands
  * merge/update emulator views
  * add PSX system
  * add MIPS architecture (R3000 only)
  * improve support for changes in config
  * rework ext/stub interface
  * fixing sparc formatter
  * fixing PE32+ DataDirectories parsing

- `v2.9.2`_

  * prepare merge with dbgui
  * drop python 2.7 support
  * rework subpackage/module imports and logging
  * various code sanitizing
  * blackified sources

- `v2.9.1`_

  * add Mach-O loader and system.osx skeleton
  * improve emulator module
  * add server and basic client cmdcli ui
  * fix various errors/warnings

- `v2.9.0`_

  * add skeleton of emulator module (emul class)
  * reorganize system modules into subpackages
  * add System, OS, Task and DefineStub classes
  * add AVR architecture
  * modified block class => map attribute moved to cfg.node class
  * moved memory classes in system.memory module
  * moved cfg analysis classes in 'sa' subpackage
  * improve debug logs
  * improve PE/ELF parsers with amoco.structs module
  * add checksec method in Elf class
  * fix armv7 semantics and formats

- `v2.6.3`_

  * add DWARF architecture
  * update and improve elf loader
  * improve expression simplify for shifts+and ops
  * merge variable-length struct fields class "VarField"

- `v2.6.2`_

  * fix support for structs "slop"
  * allow self-defined alignements of structs

- `v2.6.1`_

  * use native structure size/aligment by default

- `v2.6.0`_

  * add V850(E2S) architecture
  * add SH2-A architecture
  * add support for analysing i.MX6 HAB structures
  * merge AVR architecture
  * add system/structs classes
  * export 'crawl' out of amoco tree (libclang C-to-structs)
  * add eBPF instructions semantics
  * add support for (old)BPF instructions specs
  * add support for HEX/SREC binary format
  * add MemoryMap 'merge' method
  * add 'step_instruction' method in CoreExec (emulator)
  * add support for UFS structures
  * merge signals dispatcher for ui
  * improve setuptools support
  * remove tox and rely on travis only
  * improve armv7 instructions semantics and code helpers
  * improve armv7 instructions specs and formats
  * add spec tree debug level logging
  * fix decoder for archs with bigendian variable length instruction
  * improve decoder efficency with indicator of extended fetcher
  * add pygments support for sparc, msp430 instruction formatter
  * improve expressions widening
  * improve config module

- `v2.5.3`_

  * complete fix of issue #77 (typical x64 madness)

- `v2.5.2`_

  * partial fix of issue #77 (github) related to LEA instruction semantics on x64 arch.

- `v2.5.1`_

  * add RISC-V architecture
  * add eBPF architecture
  * use unicode outputs with unicode symbols for most operators if supported
  * add less-than-unsigned (ltu) and greater-or-equal-unsigned (geu) operators needed by riscv architecture
  * fix simplify method for comp expressions
  * improve simplify methods with a 'bitslice' optional parameter
  * improve mapper memory interface
  * fix smt model_to_mapper method
  * add cfg 'dot' format (elementary) output
  * add 'getfileoffset' method in ELF and PE classes
  * remove global endianness flag
  * update x86/x64 formats to be compatible with gnu as and clang
  * add some x86/x64 instructions semantics (movnti, wbinvd, div, ...)
  * fix some x86/x64 rare instructions specs (pmovmskb, ...)

- `v2.5.0`_

  * support python3 (>=3.5)
  * allow loading multiple cpu archs (fix issue #21 and #64)
  * update README and sphinx docs

- `v2.4.6`_

  * add sphinx documentation (rst files and docstrings)
  * add functions method for main classes
  * improve ELF pretty printing
  * changed db module to use sqlalchemy rather than zodb
  * make all objects pickable (with highest protocol)
  * add new x86 & x64 formatters
  * fix many x64 specs and semantics
  * some performance improvements
  * improve simplify mem(vec) and slc(vec)
  * fix slc.simplify for '**' operator

- `v2.4.5`_

  * add x86/x64 internals 'mode' selector
  * add 'lab' expression for labels
  * improve MemoryZone/Map with a 'grep' method
  * improve MemoryZone to allow "shifting" to some address
  * improve x86 AT&T formatter
  * add x64 decoder tests
  * fix x64 rip-relative addressing mode
  * fix many x64 specs
  * add x64 packed-instructions semantics
  * fix various x86 SSE instructions
  * fix various x86 issues (fisttp/SETcc/PUSH imm8/movq)

- `v2.4.4`_

  * add some SSE instruction semantics
  * add ui.graphics qt package with block/func/xfunc items classes
  * add initial ui.graphics gtk package
  * move vltable in ui.views.blockView class
  * fix various x86/64 decoding/formating/semantics

- `v2.4.3`_

  * add ui.graphics packages (emptied)
  * add ui.views module with support for block/func/xfunc
  * add ui.render.vltable class to pretty print tables
  * improve instruction formatter class to access pp tokens
  * cleaner itercfg and lbackward algorithms
  * add vecw expression class to represent 'widened' vec expressions
  * improve Memory write of vec expressions
  * improve widening and fixpoint in func.makemap()
  * add 'type' attribute (std/pc/flags/stack/other)
  * define register type for x86 arch
  * fix some x86/64 decoding/formating/semantics
  * update travis config, fix pytest vs. Token.

- `v2.4.2`_

  * merge support for pygments pretty printing methods (in ui.render module)
  * add x86 hilighted syntax formatter (in arch.x86.formats)
  * expose expression's pretty printing interface (exp.pp(), exp.toks())
  * remove default config class fallback (ConfigParser is standard)
  * merge some samples and tests ported to pytest package
  * use setuptools, add tox.ini and travis-ci config
  * fix some x86/x64 semantics
  * improve sparc v8 formats
  * add sparc coprocessor registers
  * update README

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
.. _sqlalchemy: http://www.sqlalchemy.org
.. _QDarkStyleSheet: https://github.com/ColinDuquesnoy/QDarkStyleSheet
.. _LICENSE: https://github.com/bdcht/amoco/blob/release/LICENSE
.. _v2.9.8: https://github.com/bdcht/amoco/releases/tag/v2.9.8
.. _v2.9.7: https://github.com/bdcht/amoco/releases/tag/v2.9.7
.. _v2.9.6: https://github.com/bdcht/amoco/releases/tag/v2.9.6
.. _v2.9.5: https://github.com/bdcht/amoco/releases/tag/v2.9.5
.. _v2.9.4: https://github.com/bdcht/amoco/releases/tag/v2.9.4
.. _v2.9.3: https://github.com/bdcht/amoco/releases/tag/v2.9.3
.. _v2.9.2: https://github.com/bdcht/amoco/releases/tag/v2.9.2
.. _v2.9.1: https://github.com/bdcht/amoco/releases/tag/v2.9.1
.. _v2.9.0: https://github.com/bdcht/amoco/releases/tag/v2.9.0
.. _v2.6.3: https://github.com/bdcht/amoco/releases/tag/v2.6.3
.. _v2.6.2: https://github.com/bdcht/amoco/releases/tag/v2.6.2
.. _v2.6.1: https://github.com/bdcht/amoco/releases/tag/v2.6.1
.. _v2.6.0: https://github.com/bdcht/amoco/releases/tag/v2.6.0
.. _v2.5.3: https://github.com/bdcht/amoco/releases/tag/v2.5.3
.. _v2.5.2: https://github.com/bdcht/amoco/releases/tag/v2.5.2
.. _v2.5.1: https://github.com/bdcht/amoco/releases/tag/v2.5.1
.. _v2.5.0: https://github.com/bdcht/amoco/releases/tag/v2.5.0
.. _v2.4.6: https://github.com/bdcht/amoco/releases/tag/v2.4.6
.. _v2.4.5: https://github.com/bdcht/amoco/releases/tag/v2.4.5
.. _v2.4.4: https://github.com/bdcht/amoco/releases/tag/v2.4.4
.. _v2.4.3: https://github.com/bdcht/amoco/releases/tag/v2.4.3
.. _v2.4.2: https://github.com/bdcht/amoco/releases/tag/v2.4.2
.. _v2.4.1: https://github.com/bdcht/amoco/releases/tag/v2.4.1
.. _v2.4.0: https://github.com/bdcht/amoco/releases/tag/v2.4.0
.. _v2.3.5: https://github.com/bdcht/amoco/releases/tag/v2.3.5
.. _v2.3.4: https://github.com/bdcht/amoco/releases/tag/v2.3.4
.. _v2.3.3: https://github.com/bdcht/amoco/releases/tag/v2.3.3
.. _v2.3.2: https://github.com/bdcht/amoco/releases/tag/v2.3.2
.. _v2.3.1: https://github.com/bdcht/amoco/releases/tag/v2.3.1
