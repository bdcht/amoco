.. amoco documentation master file

===================
Amoco documentation
===================

Amoco is a python (>=3.5) package dedicated to the static symbolic
analysis of binary programs.

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
- a generic execution model wich provides an abstract memory model to deal
  with concrete or symbolic values transparently, and other system-dependent
  features.
- various classes implementing usual disassembly techniques like linear sweep,
  recursive traversal, or more elaborated techniques like path-predicate
  which relies on SAT/SMT solvers to proceed with discovering the control
  flow graph or even to implement techniques like DARE (Directed Automated
  Random Exploration).
- various generic "helpers" and arch-dependent pretty printers to allow
  custom look-and-feel configurations (think AT&T vs. Intel syntax,
  absolute vs. relative offsets, decimal or hex immediates, etc).
- a persistent database facility that allows to compare discovered graphs
  with other previously analysed piece of codes.
- a graphical user interface that can either be run as a standalone client or
  as an IDA plugin.


.. ----------------------------------------------------------------------------  
.. _user-docs:

.. toctree::
   :maxdepth: 1
   :caption: User Documentation

   installation
   quickstart
   examples
   configure
   advanced

.. ----------------------------------------------------------------------------  
.. _devel-docs:

.. toctree::
   :maxdepth: 1
   :caption: Application Programming Interface

   overview
   main
   code
   cfg
   arch
   system
   cas
   ui
   db
   config
   logger


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

