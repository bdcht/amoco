Installation
============

Amoco is a pure python package which depends on the following packages:

- grandalf_ used for building, walking and rendering Control Flow Graphs
- crysp_ used by the generic intruction decoder (:mod:`arch.core`)
- traitlets_ used for managing the configuration
- pyparsing_ used for parsing instruction specifications

Recommended *optional* packages are:

- z3_ used to simplify expressions and solve constraints
- pygments_ used for pretty printing of assembly code and expressions
- ccrawl_ used to define and import data structures

Some optional features related to UI and persistence require:

- click_ used to define amoco command-line app
- blessings_ used for terminal based debugger frontend
- tqdm_ used for terminal based debugger frontend
- ply_ for parsing *GNU as* files
- sqlalchemy_ for persistence of amoco objects in a database
- pyside2_ for the Qt-based graphical user interface

Installation is straightforward for most packages using pip_.

The z3_ SMT solver is highly recommended (do ``pip install z3-solver``).
The pygments_ package is also recommended for pretty printing, and
sqlalchemy_ is needed if you want to store analysis results and objects.

If you want to use the graphical interface you will need **all** packages.

.. _grandalf: https://github.com/bdcht/grandalf
.. _crysp: https://github.com/bdcht/crysp
.. _traitlets:  https://pypi.org/project/traitlets/
.. _pyparsing: https://pypi.org/project/pyparsing/
.. _z3: http://z3.codeplex.com/
.. _pygments: http://pygments.org/
.. _ccrawl: https://github.com/bdcht/ccrawl
.. _click: https://click.palletsprojects.com/
.. _blessings: https://github.com/erikrose/blessings
.. _tqdm: https://github.com/tqdm/tqdm
.. _ply: http://www.dabeaz.com/ply/
.. _sqlalchemy: http://www.sqlalchemy.org/
.. _pyside2: https://wiki.qt.io/Qt_for_Python
.. _pip: https://pypi.python.org/pypi/pip
