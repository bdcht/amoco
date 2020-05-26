.. _arch:

The architecture package
========================

Supported CPU architectures are implemented in this package as subpackages and all
use the :mod:`arch.core` generic classes. The interface to a CPU used by
:ref:`system <system>` classes is implemented as a ``cpu_XXX.py``
module usually in the architecture's subpackage.

This CPU module will:

- provide the CPU *environment* (registers and other internals)
- provide an instance of :class:`arch.core.disassembler` class, which requires to:

  - define an instruction class based on :class:`arch.core.instruction`
  - define the :class:`arch.core.ispec` of every instruction for the generic decoder,
  - and define the *semantics* of every instruction with :mod:`cas.expressions`.

- optionnally define the output assembly format, and the GNU *as* (or any other)
  assembly parser.
- optionnally define the function :func:`PC()` that allows generic analysis to
  which register represents the instructions' pointer.

A simple example is provided by the :ref:`arch.arm.v8` architecture which implements
a model of ARM AArch64:
The interface CPU module is :mod:`arch.arm.cpu_armv8`,
which imports everything from the  :mod:`arch.arm.v8` subpackage.

Adding support for a new cpu module
-----------------------------------


The cpu environment
~~~~~~~~~~~~~~~~~~~

It all starts with the definition of the cpu *environment* in a dedicated module.
This module defines registers as instances of :class:`cas.expressions.reg`,
and associated register slices with :class:`cas.expressions.slc` if necessary.
For example, x86 register ``eax`` and its slices are defined in :mod:`arch.x86.env` as::

  eax = reg("eax",32)
  ax  = slc(eax, 0, 16, "ax")
  al  = slc(eax, 0, 8 , "al")
  ah  = slc(eax, 8, 8 , "ah")

In order to improve code analysis and views,
some registers should be bound to their special :class:`cas.expressions.regtype`,
using one of the dedicated callable or context manager.
For example, the stack pointer should be bound to regtype ``'STACK'`` using::

  esp = is_reg_stack(reg('esp',32))

or alternatively using a context manager::

  with is_reg_stack:
      esp = reg('esp',32)

Defined regtypes are:

 - :class:`cas.expressions.is_reg_pc`
 - :class:`cas.expressions.is_reg_flags`
 - :class:`cas.expressions.is_reg_stack`
 - :class:`cas.expressions.is_reg_other`

Once all needed registers are defined, it is recommended to define also an
ordered list called ``registers`` which will be used by emulator instances
for registers views.

Finally, the cpu *environment* sometimes also needs to define some
internal parameters that change the way instructions are decoded or the
memory endianness. For example, the `arch.arm.v7.env` module defines
internals for ``isetstate`` to change the instruction set from ARM to
Thumb, and ``endianstate`` to change endianness.
These *internal* parameters differ from regular registers by the fact
that they are not defined as expressions and thus cannot be symbolic.

Instructions specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The instructions' specifications are then defined in a module as well.
An instruction's *specification* is an instance of :class:`arch.core.ispec`
that decorates a function which performs setup of an instruction's instance.
The *specification* describes how the instruction is decoded out of bytes in
a way that allows the decorated function to setup instruction's operands and
any other characteristics from the decoded values. This description allows
to follow CPU datasheet's instructions manual very closely. Moreover, thanks
to how decorator work, several specs can share the same setup function.
For example, we have in the MIPS R3000 instructions' spec module::

  @ispec("32<[ 001100 rs(5) rt(5) imm(16) ]", mnemonic="ANDI")
  @ispec("32<[ 001101 rs(5) rt(5) imm(16) ]", mnemonic="ORI")
  @ispec("32<[ 001110 rs(5) rt(5) imm(16) ]", mnemonic="XORI")
  def mips1_dri(obj, rs, rt, imm):
      src1 = env.R[rs]
      imm = env.cst(imm, 32)
      dst = env.R[rt]
      obj.operands = [dst, src1, imm]
      obj.type = type_data_processing

Here, ``obj`` is an instruction instanciated by the disassembler, if decoded
bytes matches one of these spec definitions. In such case, the setup function
is called with arguments ``rs``, ``rt`` and ``imm`` being ints decoded from the
corresponding bits (see :class:`arch.core.ispec` below.)
Any instruction setup should define at least an ``obj.operands`` list and
should indicate one of the following ``obj.type``:

  - ``type_data_processing``, which are well-defined instructions,
  - ``type_control_flow``, which mark default ending of assembly blocks,
  - ``type_cpu_state``, which may change the cpu internal registers,
  - ``type_system``, which have usually no impact on code semantics,
  - ``type_other``

The cpu disassembler
~~~~~~~~~~~~~~~~~~~~

When the specification module is done, the cpu disassembler can be instanciated.
First a new local instruction class should be derived from the generic
:class:`arch.core.instruction` with::

  from amoco.arch.core import instruction
  instruction_X = type("instruction_X", (instruction,), {})

Then, a disassembler instance is obtained with::

  from amoco.arch.core import disassembler
  from amoco.arch.X import spec_X, spec_thumb
  disassemble = disassembler([spec_X], iclass=instruction_X)

The first argument is the list of available specifications. Most architectures
have only one mode but some like ARM can switch from a default mode (ARM) to
an alternate mode like Thumb (see class definition ``mode`` argument.)
The second is our new instruction class.
By default, disassemblers will fetch instructions in little-endian, but the
``endian`` parameter allows to fetch in big-endian. For example the ARMv7
architecture's disassembler is::

  mode = lambda: internals["isetstate"]
  endian = lambda: 1 if internals["ibigend"] == 0 else -1
  disassemble = disassembler([spec_armv7, spec_thumb],
                             instruction_armv7,
                             mode,
                             endian)

which allows the semantics to possibly change both the mode and the
instructions' endianness dynamically.


Instructions semantics
~~~~~~~~~~~~~~~~~~~~~~

An instruction's semantics is a function associated to the instruction's
mnemonic which operates on a :class:`cas.mapper.mapper` object.
The function's name should be "i_XXX" for mnemonic "XXX".
The mapper argument enables transitions from a state to another state.
For example, the semantics of all MIPS R3000 ``AND`` instructions is::

  @__npc
  def i_AND(ins, fmap):
      dst, src1, src2 = ins.operands
      if dst is not zero:
          fmap[dst] = fmap(src1&src2)

The first argument is the disassembled instruction object and the
second argument is the mapper (i.e. the state).
We simply create local variables from the operands list and then
update the state according to these operands:
Thus, the mapper is modified by
setting the first operand expression to the mapper's evaluation
of the :class:`cas.expressions.op` formed by ``src1 & src2``.

Of course, since we want *symbolic* semantics these functions might
end-up being quite complex especially for conditional stuff.
For example, like in the case of this weird
*unaligned load word* MIPS R3000 instruction::

  @__npc
  def i_LWL(ins, fmap):
      dst, base, src = ins.operands
      addr = base+src
      if dst is not zero:
          fmap[dst[24:32]] = fmap(mem(addr,8))
          cond1 = (addr%4)!=0
          fmap[dst[16:24]]  = fmap(tst(cond1,mem(addr-1,8),dst[16:24]))
          addr = addr - 1
          cond2 = cond1 & ((addr%4)!=0)
          fmap[dst[8:16]] = fmap(tst(cond2,mem(addr-1,8),dst[8:16]))
          fmap[dst] = fmap[dst].simplify()

Here, the number of bytes read from memory depends on the word-alignement
of the address value. This instruction is thus normally
coupled with a LWR which performs the read from memory of the rest of
bytes accross the word-alignment.
In concrete semantics, this is quite simple to write since address
alignment is always computable and thus 3 cases are possible.
In *symbolic* semantics, things are more tricky since address is
symbolic and thus the resulting writeback to dst register
is a symbolic expression that must take into account 3 cases at
once.

Updating the cpu instruction pointer
####################################

Now, instruction's semantics must also update the cpu :func:`PC()`.
In the MIPS case, this is performed by using
the ``__npc`` decorator role which updates ``pc`` and ``npc`` as well
to handle delay slot cases.
Architectures without delay slots can just advance their program's
counter by the length of the instruction. Architectures with delay
slots can always handle delayed branches by relying on intermediate
(hidden) program counters. This is the case for :mod:`arch.sparc` and
:mod:`arch.MIPS` where ``__npc`` does::

  pc  <- npc
  npc <- npc+4

and since branch instructions have an effect on ``npc``
once they have been processed, the next instruction to execute
(the one located at ``pc``,) is still just after the branch instruction.

However, special care must be taken to avoid pitfalls...
A common mistake is to believe that the delay slot instruction
is executed *before* the branch instruction as if the two
instructions were simply swapped. This is not true.
The branch effectively occurs after, but its operands are
still evaluated before the delay slot has had time to execute!
For example the MIPS R3000 sequence::

  liu   t7, 0x5
  liu   t6, 0x2
  bne   t7, t6, *somewhere
  addiu t7, t7, -0x3

will lead to a branch *not taken*. See pipelining discussion
below for details...

A Note on cpu pipelining and cycle-accurate emulation
#####################################################

For most architectures, the instruction parallelism introduced
by the underlying pipeline does not interfer with the semantics.
What this means is that for example,
assuming ``R1=0, R2=1, R3=1`` the generic case of::

  OR   R1, R2, R3
  ADD  R4, R1, 1

should obviously lead to ``R4=2`` anyways, because pipelining is
implemented to improve performance but shouldn't have any impact
on semantics.
Hence, **we can always emulate instructions as if
no parallelism existed**. Right ? Well, not exactly...

All pipelines have *pipeline hazard*, ie. situations
that could lead to undefined behaviors if not handled correctly.
In our example above, the ``R1`` register is really updated after
the ALU has performed its operation on ``R2`` and ``R3`` values.
Meanwhile, the ``ADD`` instruction wants to read ``R1`` value as soon
as the instruction is decoded (after it was fetched,)
and would consequently read its value *before* it is updated.
Thus, pipelines have internal mechanism to detect these kind of situations
and either stall the pipeline (wait for ``R1`` to be written back before
being used) or forward things back to other stages as soon as possible.
In this case, the ALU forwards its result immediately to back to
the ALU entry multiplexer before being updated in ``R1`` later.

Unfortunately, some old architectures like MIPS[#]_ R3000 handled only
a limited set of these *pipeline hazard* and heavily relied on
the compiler to avoid some instructions' flows
(usually by inserting nops.) In MIPS R3000 architecture,
the above case is handled correctly unless a load/store is involved
like in::

  lbu v0, 0x1(a1)
  nop
  sll v0, v0, 0x8

Here, the compiler has inserted a ``nop`` to ensure that the loaded
byte has been fetched and can be forwarded to the ALU for ``sll``.
Hence, as long as we emulate code produced by compliant compilers,
we still can ignore the underlying pipeline operations. But this
is not true anymore in the general cases.
Since most of the time we can't make this assumption, instructions
can't formally be emulated as if no parallelism existed.
If we ever have MIPS R3000 code with::

  lbu v0, 0x1(a1)
  sll v0, v0, 0x8

then the resulting mapper is not ``v0 <- mem(a1+0x1,8)<<8`` but rather
something that highly depends on the involved pipeline interlocking
mechanism, most likely ``v0 <- v0<<8``.

Like for delay slots of branch instructions that can be handled with
an additional ``npc`` register, we can always simulate the pipeline
delay by introducing a kind of hidden "register".
In amoco the mapper has an internal ``delayed`` attribute that allows
explict delayed updates.
(these updates are triggered by explicit calls to
:func:`mapper.update_delayed`, usually right in the middle of
every instructions, as if the result of the delayed load was forwarded
to the current ALU stage.)

.. [#]: "Microprocessor without Interlocked Pipeline Stages" 

Instructions format
~~~~~~~~~~~~~~~~~~~

Now that instructions specifications and semantics are defined, it is
recommended to define at least one formatter to print
instructions according to the CPU's Instruction Set Assembly manual.
Available formatters for a CPU ISA are instances of the
:class:`arch.core.Formatter` class. These formatters are initiated from
a dict object that maps instructions' mnemonic or setup function name
to iterable formatting functions operating on the instruction object.
For example::

  format_default = (mnemo, opers)
  
  MIPS_full_formats = {
      "mips1_loadstore": (mnemo, opers_mem),
      "mips1_jump_abs": (mnemo, opers),
      "mips1_jump_rel": (mnemo, opers_rel),
      "mips1_branch": (mnemo, opers_adr),
  }
  
  MIPS_full = Formatter(MIPS_full_formats)
  MIPS_full.default = format_default

Here, the available format is ``MIPS_full``, instanciated from the
``MIPS_full_formats`` dict which maps spec setup functions to their
corresponding formatting tuples.
Functions ``mnemo``, and ``opers`` take the instruction and return
a Pygments-compatible list of tokens if support for pretty-printing is
implemented, or simply a string. When an instruction is printed, the
formatter starts by matching its mnemonic or its setup function, or
takes the default formatting iterable, and then joins all
outputs from the iterables.


The cpu module
~~~~~~~~~~~~~~

Finally, the `cpu` module can be fully created. This module
should import all from the architecture's *environment* and define
its disassembler as shown above.

The semantics is associated to the instruction class with the
:func:`arch.core.instruction.set_uarch(dict)` which takes a mapping
from mnemonics to the corresponding instruction semantics function.
Thus, in most cpu modules this binding is done with::

  from .asm import *
  uarch = dict(filter(lambda kv: kv[0].startswith("i_"), locals().items()))
  instruction_X.set_uarch(uarch)

The chosen formatter is bound to the instruction class with::

  from .formats import X_full
  instruction_X.set_formatter(X_full)

(Eventually, if not already defined in the *environment*,
the :func:`PC()` function is defined to return the instruction's pointer.)

Note that whenever a disassembler is available, the entire
architecture ISA decision tree can be displayed with::

  >>> from amoco.ui.views import archView
  >>> from amoco.arch.mips.cpu_r3000LE import disassemble
  >>> print(archView(disassemble))
  ─[& f0000000 == 0]
    │─[& fc000000 == 0]
    │  │─[& fc00003f == 8]
    │  │  │─JR              : 32<[ 000000 rs(5) 00000 00000 00000 001000]
    │  │─[& fc00003f == 12]
    │  │  │─MFLO            : 32<[ 000000 00000 00000 rd(5) 00000 010010 ]
    │  │─[& fc00003f == 10]
    │  │  │─MFHI            : 32<[ 000000 00000 00000 rd(5) 00000 010000 ]
    │  │─[& fc00003f == 13]
    │  │  │─MTLO            : 32<[ 000000 rs(5) 00000 00000 00000 010011 ]
    │  │─[& fc00003f == 11]
    │  │  │─MTHI            : 32<[ 000000 rs(5) 00000 00000 00000 010001 ]
    │  │─[& fc00003f == 19]
    │  │  │─MULTU           : 32<[ 000000 rs(5) rt(5) 00000 00000 011001]
    │  │─[& fc00003f == 18]
    │  │  │─MULT            : 32<[ 000000 rs(5) rt(5) 00000 00000 011000]
    │  │─[& fc00003f == 1b]
    │  │  │─DIVU            : 32<[ 000000 rs(5) rt(5) 00000 00000 011011]
    │  │─[& fc00003f == 1a]
    │  │  │─DIV             : 32<[ 000000 rs(5) rt(5) 00000 00000 011010]
    │  │─[& fc00003f == 9]
    │  │  │─JALR            : 32<[ 000000 rs(5) 00000 rd(5) 00000 001001]
    │  │─[& fc00003f == 2b]
    │  │  │─SLTU            : 32<[ 000000 rs(5) rt(5) rd(5) 00000 101011]
    │  │─[& fc00003f == 2a]
    │  │  │─SLT             : 32<[ 000000 rs(5) rt(5) rd(5) 00000 101010]
    │  │─[& fc00003f == 6]
    │  │  │─SRLV            : 32<[ 000000 rs(5) rt(5) rd(5) 00000 000110]
    │  │─[& fc00003f == 7]
    │  │  │─SRAV            : 32<[ 000000 rs(5) rt(5) rd(5) 00000 000111]
    │  │─[& fc00003f == 4]
    │  │  │─SLLV            : 32<[ 000000 rs(5) rt(5) rd(5) 00000 000100]
    │  │─[& fc00003f == 26]
    │  │  │─XOR             : 32<[ 000000 rs(5) rt(5) rd(5) 00000 100110]
    │  │─[& fc00003f == 25]
    │  │  │─OR              : 32<[ 000000 rs(5) rt(5) rd(5) 00000 100101]
    │  │─[& fc00003f == 27]
    │  │  │─NOR             : 32<[ 000000 rs(5) rt(5) rd(5) 00000 100111]
    │  │─[& fc00003f == 24]
    │  │  │─AND             : 32<[ 000000 rs(5) rt(5) rd(5) 00000 100100]
    │  │─[& fc00003f == 23]
    │  │  │─SUBU            : 32<[ 000000 rs(5) rt(5) rd(5) 00000 100011]
    │  │─[& fc00003f == 21]
    │  │  │─ADDU            : 32<[ 000000 rs(5) rt(5) rd(5) 00000 100001]
    │  │─[& fc00003f == 22]
    │  │  │─SUB             : 32<[ 000000 rs(5) rt(5) rd(5) 00000 100010]
    │  │─[& fc00003f == 20]
    │  │  │─ADD             : 32<[ 000000 rs(5) rt(5) rd(5) 00000 100000]
    │  │─[& fc00003f == 2]
    │  │  │─SRL             : 32<[ 000000 00000 rt(5) rd(5) sa(5) 000010 ]
    │  │─[& fc00003f == 3]
    │  │  │─SRA             : 32<[ 000000 00000 rt(5) rd(5) sa(5) 000011 ]
    │  │─[& fc00003f == 0]
    │  │  │─SLL             : 32<[ 000000 00000 rt(5) rd(5) sa(5) 000000 ]
    │  │─[& fc00003f == c]
    │  │  │─SYSCALL         : 32<[ 000000 .code(20) 001100]
    │  │─[& fc00003f == d]
    │  │  │─BREAK           : 32<[ 000000 .code(20) 001101]
    │─[& fc000000 == 4000000]
    │  │─BLTZAL          : 32<[ 000001 rs(5) 10000 ~imm(16) ]
    │  │─BLTZ            : 32<[ 000001 rs(5) 00000 ~imm(16) ]
    │  │─BGEZAL          : 32<[ 000001 rs(5) 10001 ~imm(16) ]
    │  │─BGEZ            : 32<[ 000001 rs(5) 00001 ~imm(16) ]
    │─[& fc000000 == c000000]
    │  │─JAL             : 32<[ 000011 t(26)]
    │─[& fc000000 == 8000000]
    │  │─J               : 32<[ 000010 t(26)]
  ─[& f0000000 == 40000000]
    │─[& f2000000 == 40000000]
    │  │─MTC             : 32<[ 0100 .z(2) 00100 rt(5) rd(5) 00000000000 ]
    │  │─CTC             : 32<[ 0100 .z(2) 00110 rt(5) rd(5) 00000000000 ]
    │  │─MFC             : 32<[ 0100 .z(2) 00000 rt(5) rd(5) 00000000000 ]
    │  │─CFC             : 32<[ 0100 .z(2) 00010 rt(5) rd(5) 00000000000 ]
    │─[& f2000000 == 42000000]
    │  │─COP             : 32<[ 0100 .z(2) 1 .cofun(25) ]
  ─[& f0000000 == 30000000]
    │─LUI             : 32<[ 001111 00000 rt(5) imm(16) ]
    │─XORI            : 32<[ 001110 rs(5) rt(5) imm(16) ]
    │─ORI             : 32<[ 001101 rs(5) rt(5) imm(16) ]
    │─ANDI            : 32<[ 001100 rs(5) rt(5) imm(16) ]
  ─[& f0000000 == 10000000]
    │─BLEZ            : 32<[ 000110 rs(5) 00000 ~imm(16) ]
    │─BGTZ            : 32<[ 000111 rs(5) 00000 ~imm(16) ]
    │─BNE             : 32<[ 000101 rs(5) rt(5) ~imm(16) ]
    │─BEQ             : 32<[ 000100 rs(5) rt(5) ~imm(16) ]
  ─[& f0000000 == 20000000]
    │─SLTIU           : 32<[ 001011 rs(5) rt(5) ~imm(16) ]
    │─SLTI            : 32<[ 001010 rs(5) rt(5) ~imm(16) ]
    │─ADDIU           : 32<[ 001001 rs(5) rt(5) ~imm(16) ]
    │─ADDI            : 32<[ 001000 rs(5) rt(5) ~imm(16) ]
  ─[& f0000000 == b0000000]
    │─SWR             : 32<[ 101110 base(5) rt(5) offset(16) ]
  ─[& f0000000 == 90000000]
    │─LWR             : 32<[ 100110 base(5) rt(5) offset(16) ]
    │─LHU             : 32<[ 100101 base(5) rt(5) offset(16) ]
    │─LBU             : 32<[ 100100 base(5) rt(5) offset(16) ]
  ─[& f0000000 == a0000000]
    │─SWL             : 32<[ 101010 base(5) rt(5) offset(16) ]
    │─SW              : 32<[ 101011 base(5) rt(5) offset(16) ]
    │─SH              : 32<[ 101001 base(5) rt(5) offset(16) ]
    │─SB              : 32<[ 101000 base(5) rt(5) offset(16) ]
  ─[& f0000000 == 80000000]
    │─LWL             : 32<[ 100010 base(5) rt(5) offset(16) ]
    │─LW              : 32<[ 100011 base(5) rt(5) offset(16) ]
    │─LH              : 32<[ 100001 base(5) rt(5) offset(16) ]
    │─LB              : 32<[ 100000 base(5) rt(5) offset(16) ]
  ─[& f0000000 == e0000000]
    │─SWC             : 32<[ 1110 .z(2) base(5) rt(5) offset(16) ]
  ─[& f0000000 == c0000000]
    │─LWC             : 32<[ 1100 .z(2) base(5) rt(5) offset(16) ]


If several specification modes are provided, they are listed one
after the other.

.. automodule:: arch.core
   :members:

