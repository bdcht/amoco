.. _cas:

The computer algebra system package
===================================

.. contents::

Symbolic expressions are provided by several classes found
in module :mod:`cas/expressions`:

- Constant  :class:`cst`, which represents immediate (signed or unsigned) value of fixed size (bitvector),
- Symbol    :class:`sym`, a Constant equipped with a reference string (non-external symbol),
- Register  :class:`reg`, a fixed size CPU register *location*,
- External  :class:`ext`, a reference to an external location (external symbol),
- Floats    :class:`cfp`, constant (fixed size) floating-point values,
- Composite :class:`comp`, a bitvector composed of several elements,
- Pointer   :class:`ptr`, a memory *location* in a segment, with possible displacement,
- Memory    :class:`mem`, a Pointer to represent a value of fixed size in memory,
- Slice     :class:`slc`, a bitvector slice of any element,
- Test      :class:`tst`, a conditional expression, (see below.)
- Operator  :class:`uop`, an unary operator expression,
- Operator  :class:`op`, a binary operator expression. The list of supported operations is
  not fixed althrough several predefined operators allow to build expressions directly from
  Python expressions: say, you don't need to write ``op('+',x,y)``, but can write ``x+y``.
  Supported operators are:

  + ``+``, ``-``, ``*`` (multiply low), ``**`` (multiply extended), ``/``
  + ``&``, ``|``, ``^``, ``~``
  + ``==``, ``!=``, ``<=``, ``>=``, ``<``, ``>``
  + ``>>``, ``<<``, ``//`` (arithmetic shift right), ``>>>`` and ``<<<`` (rotations).

  See `cas.expressions._operator` for more details.

All elements inherit from the :class:`exp` class which defines all default methods/properties.
Common attributes and methods for all elements are:

- ``size``,  a Python integer representing the size in bits,
- ``sf``,    the True/False *sign-flag*.
- ``length`` (size/8)
- ``mask``   (1<<size)-1
- extend methods (``signextend(newsize)``, ``zeroextend(newsize)``)
- ``bytes(sta,sto,endian=1)`` method to retreive the expression of extracted bytes from sta to sto indices.

All manipulation of an expression object usually result in a new expression object except for
``simplify()`` which performs a few in-place elementary simplifications.

.. automodule:: cas.expressions
   :members:

.. automodule:: cas.smt
   :members:

.. automodule:: cas.mapper
   :members: mapper, merge
   :undoc-members:
