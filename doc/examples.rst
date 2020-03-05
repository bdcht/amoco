Examples
========

.. contents::
   :local:

Solving the SSTIC2017 challenge (2/5): *don't let him escape*
-------------------------------------------------------------

Context
=======

In each part of the challenge_ the goal is to find some *lum*
leading ultimately to a *key* that unlocks other parts.

Part 2 is based on reversing an eBPF_ program that checks
data transmitted in a raw socket. To find a *lum* or a *key*
we basically need to find how to trigger some specific filters
within this program.

Playground
==========

This part is provided as `server.py` and `bpf.py` files.
The server module contains the base64 encoded eBPF_ program and the
bpf module essentially wraps the *bpf* system interface ...

From the provided server written in python we can see that filtered packets
are probably in UDP. The destination port is yet unknown. A *state* variable
is stored in a *bpf map* and has value 1 when the *lum* was filtered
or 2 when the *key* was filtered by the eBPF program.

The extracted eBPF program is located in 'tests/samples/ebpf/bpf_patched_prog'.
This program is loaded in the linux kernel which has a dedicated
interpreter for eBPF instructions (see eBPF_ specifications.)

We can either implement the eBPF architecture in amoco or rely on the
jit eBPF compiler in the kernel to get a x64 version of the eBPF program.


.. _challenge: http://communaute.sstic.org/ChallengeSSTIC2017
.. _eBPF: http://www.kernel.org/doc/Documentation/networking/filter.txt

Verifying  a custom iMX.6 secure boot implementation
----------------------------------------------------

