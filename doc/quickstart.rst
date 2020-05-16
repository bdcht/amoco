===============
Getting started
===============


This part of the documentation is intended for reversers or pentesters
who want to get valuable informations about a binary blob without writting
complicated python scripts.
We give here a quick introduction to amoco without covering any of the
implementation details.

**Content**

.. contents::
    :local:


Loading binary data
===================

The recommended way to load binary data is to use the
:meth:`load_program <system.core.load_program>`
function, providing an input filename or a bytestring.
For example, from directory ``amoco/tests``, do::

   In [1]: import amoco
   In [2]: p = amoco.load_program(u'samples/x86/flow.elf')
   In [3]: print(p)
   <Task amoco.system.linux32.x86 'samples/x86/flow.elf'>

   In [4]: print(p.bin.Ehdr)
   [Ehdr]
   e_ident    :[IDENT]
               ELFMAG0      :127
               ELFMAG       :b'ELF'
               EI_CLASS     :ELFCLASS32
               EI_DATA      :ELFDATA2LSB
               EI_VERSION   :1
               EI_OSABI     :ELFOSABI_NONE
               EI_ABIVERSION:0
               unused       :(0, 0, 0, 0, 0, 0, 0)
   e_type     :ET_EXEC
   e_machine  :EM_386
   e_version  :EV_CURRENT
   e_entry    :0x8048380
   e_phoff    :52
   e_shoff    :4416
   e_flags    :0x0
   e_ehsize   :52
   e_phentsize:32
   e_phnum    :9
   e_shentsize:40
   e_shnum    :30
   e_shstrndx :27

If you have the click_ python package installed, you can also
rely on the ``amoco`` shell command and simply do::

  % amoco load samples/x86/flow.elf

If the binary data uses a registered executable format
(currently :mod:`system.pe`, :mod:`system.elf`, :mod:`system.macho`
or an HEX/SREC format in :mod:`system.utils`) and targets a
supported plateform (see :ref:`system <system>` and
:ref:`arch <arch>` packages), the returned object is
an *abstraction* of the memory mapped program::

   In [5]: print(p.state)
   eip <- { | [0:32]->0x8048380 | }
   ebp <- { | [0:32]->0x0 | }
   eax <- { | [0:32]->0x0 | }
   ebx <- { | [0:32]->0x0 | }
   ecx <- { | [0:32]->0x0 | }
   edx <- { | [0:32]->0x0 | }
   esi <- { | [0:32]->0x0 | }
   edi <- { | [0:32]->0x0 | }
   esp <- { | [0:32]->0x7ffff000 | }

   In [6]: print(p.state.mmap)
   <MemoryZone rel=None :
     <mo [08048000,08049000] data:b'\x7fELF\x01\x01\x01\x00\x00\x0...'>
     <mo [08049f14,08049ff0] data:b'\xff\xff\xff\xff\x00\x00\x00\x...'>
     <mo [08049ff0,08049ff4] data:@__gmon_start__>
     <mo [08049ff4,0804a000] data:b'(\x9f\x04\x08\x00\x00\x00\x00\...'>
     <mo [0804a000,0804a004] data:@__stack_chk_fail>
     <mo [0804a004,0804a008] data:@malloc>
     <mo [0804a008,0804a00c] data:@__gmon_start__>
     <mo [0804a00c,0804a010] data:@__libc_start_main>
     <mo [0804a010,0804af14] data:b'\x00\x00\x00\x00\x00\x00\x00\x...'>
     <mo [7fffd000,7ffff000] data:b'\x00\x00\x00\x00\x00\x00\x00\x...'>>

(other more specific executable formats are supported
but they need to be loaded manually.)
Also note that it is possible to provide a *raw* bytes string as input and
then manually load the architecture::

   In [1]: import amoco
   In [2]: shellcode = (b"\xeb\x16\x5e\x31\xd2\x52\x56\x89\xe1\x89\xf3\x31\xc0\xb0\x0b\xcd"
                        b"\x80\x31\xdb\x31\xc0\x40\xcd\x80\xe8\xe5\xff\xff\xff\x2f\x62\x69"
                        b"\x6e\x2f\x73\x68")
   In [3]: p = amoco.load_program(shellcode)
   [WARNING] amoco.system.core       : unknown format
   [WARNING] amoco.system.raw        : a cpu module must be imported

   In [4]: from amoco.arch.x86 import cpu_x86
   In [5]: p.cpu = cpu_x86

   In [6]: print(p)
   <RawExec - '(sc-eb165e31...)'>

   In [7]: print(p.state.mmap)
   <MemoryZone rel=None :
         <mo [00000000,00000024] data:'\xeb\x16^1\xd2RV\x89\xe1\x89\xf...'>>

The *shellcode* is mapped at address 0 by default, but can be relocated::

   In [8]: p.relocate(0x4000)
   In [9]: print(p.state.mmap)
   <MemoryZone rel=None :
   	 <mo [00004000,00004024] data:'\xeb\x16^1\xd2RV\x89\xe1\x89\xf...'>>


Decoding blocks of instructions
===============================

Decoding some bytes as an :class:`arch.core.instruction` needs only to load the desired cpu module, for
example::

   In [10]: cpu_x86.disassemble(b'\xeb\x16')
   Out[10]: <amoco.arch.x86.spec_ia32 JMP ( length=2 type=2 )>
   In [11]: print(_)
   jmp         .+22

If a mapped binary program has been instanciated, we can start disassembling instructions
or *data* located at some virtual address::

   In [12]: print(p.read_instruction(0x4000))
   jmp         *0x4018
   In [13]: p.read_data(0x4000,2)
   Out[13]: ['\xeb\x16']

Now, rather than manually adjusting the address to fetch the next instruction, we
can use any of the code analysis strategies implemented in amoco to disassemble
*basic blocks* directly::

   % amoco load samples/x86/flow.elf
   [...]
   In [3]: z = amoco.sa.lsweep(p)

   In [4]: z.getblock(0x8048380)
   Out[4]: <block object (0x8048380-0x80483a1) with 13 instructions> 

   In [5]: b=_
   In [6]: print(b.view)
   ─────────── block 0x8048380 ──────────────────────────
   0x8048380  '31ed'          xor         ebp, ebp
   0x8048382  '5e'            pop         esi
   0x8048383  '89e1'          mov         ecx, esp
   0x8048385  '83e4f0'        and         esp, 0xfffffff0
   0x8048388  '50'            push        eax
   0x8048389  '54'            push        esp
   0x804838a  '52'            push        edx
   0x804838b  '6810860408'    push        0x8048610
   0x8048390  '68a0850408'    push        0x80485a0
   0x8048395  '51'            push        ecx
   0x8048396  '56'            push        esi
   0x8048397  '68fd840408'    push        0x80484fd
   0x804839c  'e8cfffffff'    call        *0x8048370
   ──────────────────────────────────────────────────────


Note that a :class:`block <code.block>` view will show non-transformed instructions' operands
(appart from PC-relative branch offsets which are shown as absolute addresses.)
Block views can be *enhanced* by several analyses that will possibly add symbols related to addresses
(provided by the program's symbol table) or more semantic-related information. These views
are usually available only through the higher level *task* view object and add various
comment tokens to instruction lines. For example::

   In [7]: print( p.view.codeblock(b) )
   ───────── codeblock 0x8048380 ──────────────────────────────────────────
   0x8048380.text  '31ed'          xor         ebp, ebp                    
   0x8048382.text  '5e'            pop         esi                         
   0x8048383.text  '89e1'          mov         ecx, esp                    
   0x8048385.text  '83e4f0'        and         esp, 0xfffffff0             
   0x8048388.text  '50'            push        eax                         
   0x8048389.text  '54'            push        esp                         
   0x804838a.text  '52'            push        edx                         
   0x804838b.text  '6810860408'    push        0x8048610<__libc_csu_fini>  
   0x8048390.text  '68a0850408'    push        0x80485a0<__libc_csu_init>  
   0x8048395.text  '51'            push        ecx                         
   0x8048396.text  '56'            push        esi                         
   0x8048397.text  '68fd840408'    push        0x80484fd<main>             
   0x804839c.text  'e8cfffffff'    call        0x8048370<__libc_start_main>
   ────────────────────────────────────────────────────────────────────────


Symbolic representations of blocks
==================================

A :class:`block <code.block>` object provides instructions of the program located at some address in memory.
A :class:`node <cfg.node>` object takes a block and
allows to get a symbolic functional representation of what this block sequence
of instructions is doing::

   In [8]: n = amoco.cfg.node(b)
   In [8]: print(n.map.view)
   eip                                               ⇽ (eip+-0x10)                                        
   eflags:                                          
    │ cf                                             ⇽ 0x0                                                
    │ pf                                             ⇽ (0x6996>>(esp+0x4)[4:8])[0:1]                      
    │ af                                             ⇽ af                                                 
    │ zf                                             ⇽ ({[ 0: 4] -> 0x0, [ 4:32] -> (esp+0x4)[4:32]}==0x0)
    │ sf                                             ⇽ ({[ 0: 4] -> 0x0, [ 4:32] -> (esp+0x4)[4:32]}<0x0) 
    │ tf                                             ⇽ tf                                                 
    │ df                                             ⇽ df                                                 
    │ of                                             ⇽ 0x0                                                
   ebp                                               ⇽ 0x0                                                
   esp                                               ⇽ ({[ 0: 4] -> 0x0, [ 4:32] -> (esp+0x4)[4:32]}-0x24)
   esi                                               ⇽ M32(esp)                                           
   ecx                                               ⇽ (esp+0x4)                                          
   ({ | [0:4]->0x0 | [4:32]->(esp+0x4)[4:32] | }-4)  ⇽ eax                                                
   ({ | [0:4]->0x0 | [4:32]->(esp+0x4)[4:32] | }-8)  ⇽ ({[ 0: 4] -> 0x0, [ 4:32] -> (esp+0x4)[4:32]}-0x4) 
   ({ | [0:4]->0x0 | [4:32]->(esp+0x4)[4:32] | }-12) ⇽ edx                                                
   ({ | [0:4]->0x0 | [4:32]->(esp+0x4)[4:32] | }-16) ⇽ 0x8048610                                          
   ({ | [0:4]->0x0 | [4:32]->(esp+0x4)[4:32] | }-20) ⇽ 0x80485a0                                          
   ({ | [0:4]->0x0 | [4:32]->(esp+0x4)[4:32] | }-24) ⇽ (esp+0x4)                                          
   ({ | [0:4]->0x0 | [4:32]->(esp+0x4)[4:32] | }-28) ⇽ M32(esp)                                           
   ({ | [0:4]->0x0 | [4:32]->(esp+0x4)[4:32] | }-32) ⇽ 0x80484fd                                          
   ({ | [0:4]->0x0 | [4:32]->(esp+0x4)[4:32] | }-36) ⇽ (eip+0x21)    

Here we are with the *map* of the block.
Now what this :class:`mapper <cas.mapper.mapper>` object says is for example that once the block
is executed ``esi`` register will be set to the 32 bits value pointed by ``esp``, that the carry flag will be 0, or
that the top of the stack will hold value ``eip+0x21``.
Rather than extracting the entire view of the mapper we can query any :mod:`expression <cas.expressions>` out if it::

   In [9]: print(n.map(p.cpu.ecx))
   (esp+0x4)

There are some caveats when it comes to query memory expressions but we will leave this
for later (see :class:`cas.mapper.mapper`).

The ``n.map`` object also provides a better way to see how the memory is modified by the block::

   In [10]: print(n.map.mmap)
   <MemoryZone rel=None :>
   <MemoryZone rel={ | [0:4]->0x0 | [4:32]->(esp+0x4)[4:32] | } :
   	       <mo [-0000024,-0000020] data:(eip+0x21)>
   	       <mo [-0000020,-000001c] data:b'\xfd\x84\x04\x08'>
   	       <mo [-000001c,-0000018] data:M32(esp)>
   	       <mo [-0000018,-0000014] data:(esp+0x4)>
   	       <mo [-0000014,-0000010] data:b'\xa0\x85\x04\x08'>
   	       <mo [-0000010,-000000c] data:b'\x10\x86\x04\x08'>
   	       <mo [-000000c,-0000008] data:edx>
   	       <mo [-0000008,-0000004] data:({ | [0:4]->0x0 | [4:32]->(esp+0...>
   	       <mo [-0000004,00000000] data:eax>>


The :class:`cas.mapper.mapper` class is an essential part of amoco that captures the semantics
of the block by interpreting its' instructions in a symbolic way. Note that it takes no input state
or whatever but just expresses what the block would do independently of what has been done
before and even where the block is actually located.

For any mapper object, we can get the lists of *input* and *output* expressions, and replace
inputs by any chosen expression::

   In [11]: for x in set(n.map.inputs()): print(x)
   esp
   eip
   M32(esp)

   In [12]: m = n.map.use(eip=0x8048380, esp=0x7fcfffff)
   In [13]: print(m.view)
   eip             <- 0x8048370
   eflags:
   | cf            <- 0x0
   | sf            <- 0x0
   | tf            <- tf
   | zf            <- 0x0
   | pf            <- 0x0
   | of            <- 0x0
   | df            <- df
   | af            <- af
   ebp             <- 0x0
   esp             <- 0x7fcfffdc
   esi             <- M32(0x7fcfffff)
   ecx             <- 0x7fd00003
   (0x7fd00000-4)  <- eax
   (0x7fd00000-8)  <- 0x7fcffffc
   (0x7fd00000-12) <- edx
   (0x7fd00000-16) <- 0x8048610
   (0x7fd00000-20) <- 0x80485a0
   (0x7fd00000-24) <- 0x7fd00003
   (0x7fd00000-28) <- M32(0x7fcfffff)
   (0x7fd00000-32) <- 0x80484fd
   (0x7fd00000-36) <- 0x80483a1

Its fine to disassemble a block at some address and get some symbolic representation of it,
but we are still far from getting the picture of the entire program.
In order to reason later about execution paths, we need a way to *chain* block mappers.
This is provided by the mapper's shifts operators::

   In [14]: mm = amoco.cas.mapper.mapper()
   In [15]: amoco.conf.Cas.noaliasing = True
   In [16]: mm[p.cpu.eip] = p.cpu.mem(p.cpu.esp+4,32)
   In [17]: print( (n.map>>mm)(p.cpu.eip) )
   0x80484fd

Here, taking a new mapper as if it came either from a block or a stub, and assuming
that there is no memory aliasing, the sequential execution of ``n.map`` followed by ``mm``
would branch to address ``0x80484fd`` (``<main>``).

Starting some analysis
======================

Important note:

  *** The merge with emul branch has broken the static-analysis module.
      This is going to be fixed only once the merge is fully integrated ***

