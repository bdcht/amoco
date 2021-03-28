Overview
========

Amoco is composed of 5 sub-packages

- :ref:`arch <arch>`, deals with
  CPU architectures' to provide instructions disassemblers, and
  instructions' semantics for several CPUs, microcontrollers or
  "virtual machines":

  - x86, x64
  - armv7, armv8 (aarch64)
  - sparc (v8)
  - MIPS (R3000)
  - riscv
  - msp430
  - avr
  - pic/F46K22
  - v850
  - sh2, sh4
  - z80
  - BPF/eBPF (vm)
  - Dwarf (vm)

- :ref:`cas <cas>`, implements the *computer algebra system* to
  provide operations and mappings with symbolic expressions.
  It allows to represent architectures' registers values either
  as *concrete* or *symbolic* values,
  and to describe instructions' semantics as a *map* of expressions
  to registers or memory addresses. If z3 is installed, boolean expressions
  formulas can be translated to z3 bitvectors and checked by its solver.
  If satisfiable, a z3 model can be translated back into a
  :class:̀`mapper` instance (with amoco expressions.)

- :ref:`system <system>`, implements all *system* features like
  an abstract memory suited for symbolic expressions, as well as
  support for executable formats (ELF,PE,Mach-O,...) and their loaders
  to provide an abstraction of a "task" (a memory-mapped binary exectuable.)

- :ref:`sa <sa>` implements various *static analysis* methods to
  recover and build the control flow graph of functions.

- :ref:`ui <ui>` deals with how instructions and expressions are displayed
  either in a terminal or in a graphical *user interface*.

Modules :mod:`code` and :mod:`cfg`
provide high-level abstractions of basic blocks, functions, and
control flow graphs.
Module :mod:`config`, :mod:`logger`, and :mod:`signals`
provide the global configuration, logging and signaling facilities
to all other modules.
