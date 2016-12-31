===============
Getting started
===============


The "end-user" documentation is intended for reversers or pentesters
who want to get valuable informations about a binary blob without writting
complicated python scripts.
We give here a quick introduction to amoco without covering any of the
details.

**Content**

.. contents::
    :local:


Loading binary data
===================

The recommended way to load binary data is to use the ``load_program``
function, providing an input file or string.
For example, from the directory ``amoco/tests``, do::

   In [1]: import amoco
   In [2]: p = amoco.system.loader.load_program('samples/x86/flow.elf')
   In [3]: print p
   <amoco.system.linux_x86.ELF object at 0x7f834b4187d0>
   In [4]: print p.bin.Ehdr
   ELF header:
   [Elf32_Ehdr]
   	e_ident     :ELF; ELFOSABI_SYSV; 1; ELFCLASS32; ELFDATA2LSB; 0; 127
   	e_type      :ET_EXEC
   	e_machine   :EM_386
   	e_version   :EV_CURRENT
   	e_entry     :0x8048380
   	e_phoff     :52
   	e_shoff     :4416
   	e_flags     :0x0
   	e_ehsize    :52
   	e_phentsize :32
   	e_phnum     :9
   	e_shentsize :40
   	e_shnum     :30
   	e_shstrndx  :27

If the file uses a supported executable format (currently ``PE`` of ``ELF``) and
targets a supported plateform (see :ref:`system` and :ref:`arch` packages),
the returned object is an *abstraction* of the memory mapped program::

   In [5]: print p.mmap
   <MemoryZone rel=None :
   	 <mo [08048000,08049000] data:'\x7fELF\x01\x01\x01\x00\x00\x00...'>
   	 <mo [08049f14,08049ff0] data:'\xff\xff\xff\xff\x00\x00\x00\x0...'>
   	 <mo [08049ff0,08049ff4] data:@__gmon_start__>
   	 <mo [08049ff4,0804a000] data:'(\x9f\x04\x08\x00\x00\x00\x00\x...'>
   	 <mo [0804a000,0804a004] data:@__stack_chk_fail>
   	 <mo [0804a004,0804a008] data:@malloc>
   	 <mo [0804a008,0804a00c] data:@__gmon_start__>
   	 <mo [0804a00c,0804a010] data:@__libc_start_main>
   	 <mo [0804a010,0804af14] data:'\x00\x00\x00\x00\x00\x00\x00\x0...'>>
   <MemoryZone rel=esp :>

Note that it is also possible to provide a *raw* bytes
string as input and then manually load the suited architecture::

   In [1]: import amoco
   In [2]: shellcode = ("\xeb\x16\x5e\x31\xd2\x52\x56\x89\xe1\x89\xf3\x31\xc0\xb0\x0b\xcd"
                        "\x80\x31\xdb\x31\xc0\x40\xcd\x80\xe8\xe5\xff\xff\xff\x2f\x62\x69"
                        "\x6e\x2f\x73\x68")
   In [3]: p = amoco.system.loader.load_program(shellcode)
   amoco.system.loader: WARNING: unknown format
   amoco.system.raw: WARNING: a cpu module must be imported
   In [4]: from amoco.arch.x86 import cpu_x86
   In [5]: p.cpu = cpu_x86
   In [6]: print p
   <amoco.system.raw.RawExec object at 0x7f3dc3d1cef0>
   In [7]: print p.mmap
   <MemoryZone rel=None :
         <mo [00000000,00000024] data:'\xeb\x16^1\xd2RV\x89\xe1\x89\xf...'>>

The shellcode is loaded at address 0 by default, but can be relocated with::

   In [8]: p.relocate(0x4000)
   In [9]: print p.mmap
   <MemoryZone rel=None :
   	 <mo [00004000,00004024] data:'\xeb\x16^1\xd2RV\x89\xe1\x89\xf...'>>


Decoding blocks of instructions
===============================

Decoding a bytes stream as instruction needs only to load the desired cpu module, for
example::

   In [10]: cpu_x86.disassemble('\xeb\x16')
   Out[10]: <amoco.arch.x86.spec_ia32 JMP ( length=2 type=2 )>
   In [11]: print _
   jmp         .+22

But when a mapped binary program is available, we can start disassembling instructions
or *data* located at virtual addresses::

   In [12]: print p.read_instruction(p.cpu.cst(0x4000,32))
   jmp         *0x4018
   In [13]: p.read_data(p.cpu.cst(0x4000,32),2)
   Out[13]: ['\xeb\x16']

However, rather than manually adjusting the address to fetch the next instruction, we
can use any of the code analysis strategies implemented in amoco to disassemble
*basic blocks* directly::

   In [1]: import amoco
   In [2]: p = amoco.system.loader.load_program('samples/x86/flow.elf')
   In [3]: z = amoco.lsweep(p)
   In [4]: z.getblock(0x8048380)
   Out[4]: <block object (0x8048380) at 0x7f1decec4c50>
   In [5]: b=_
   In [6]: print b
   0x8048380 '31ed'          xor         ebp, ebp
   0x8048382 '5e'            pop         esi
   0x8048383 '89e1'          mov         ecx, esp
   0x8048385 '83e4f0'        and         esp, 0xfffffff0
   0x8048388 '50'            push        eax
   0x8048389 '54'            push        esp
   0x804838a '52'            push        edx
   0x804838b '6810860408'    push        #__libc_csu_fini
   0x8048390 '68a0850408'    push        #__libc_csu_init
   0x8048395 '51'            push        ecx
   0x8048396 '56'            push        esi
   0x8048397 '68fd840408'    push        #main
   0x804839c 'e8cfffffff'    call        *0x8048370



Symbolic representations of blocks
==================================

Starting some analysis
======================


