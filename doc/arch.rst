.. _arch:

The architecture package
========================

Supported CPU architectures are implemented in this package as subpackages and all
use the :mod:`arch.core` generic classes. The interface to a CPU used by
:ref:`system <system>` classes is generally provided by a ``cpu_XXX.py``
module in the architecture's subpackage.

This CPU module shall:

- provide the CPU *environment* (registers and other internals)
- provide an instruction class based on :class:`arch.core.instruction`
- provide an instance of :class:`core.disassembler` class, which requires to:

  - define the :class:`@ispec` of every instruction for the generic decoder,
  - and define the *semantics* of every instruction with :mod:`cas.expressions`.

- optionnally define the output assembly format, and the *GNU as* (or any other)
  assembly parser.

A simple example is provided by the ``arch/arm/v8`` architecture which implements
a model of ARM AArch64:
The interface module is :mod:`arch.arm.cpu_armv8`, which imports everything from
the v8 subpackage.


.. automodule:: arch.core
   :members:

.. automodule:: arch.x86.cpu_x86
   :members:

.. automodule:: arch.arm.cpu_armv8
   :members:

.. _arch: `The architecture package`_
