from setuptools import setup, find_packages

long_descr = '''
Amoco is a python package dedicated to the (static) analysis of binaries.

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
'''

setup(
    name = 'amoco',
    version = '2.4.2',
    description = 'yet another binary analysis framework',
    long_description = long_descr,
    # Metadata
    author = 'Axel Tillequin',
    author_email = 'bdcht3@gmail.com',
    license = 'GPLv2',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      'Programming Language :: Python :: 2.7',
      'Topic :: Scientific/Engineering :: Information Analysis',
      'Topic :: Security',
      'Topic :: Software Development :: Disassemblers',
      'Topic :: Software Development :: Interpreters',
    ],
    keywords='binary analysis symbolic execution',
    packages=find_packages(exclude=['docs','tests*']),
    url = 'https://github.com/bdcht/amoco',
    install_requires = ['grandalf>=0.555', 'crysp>0.1', 'pyparsing'],
    extras_require={
        'test': ['pytest'],
        'full': ['pygments','ply','zodb'],
    },
    package_data = {
    },
    data_files = [],
    entry_points={
    },
)
