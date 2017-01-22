Installation
============

Amoco is a pure python package which depends on the following packages:

- grandalf_ used for building CFG (and eventually rendering it)
- crysp_    used by the generic intruction decoder (:mod:`arch.core`)
- z3_       used to simplify expressions and solve constraints
- pygments_ used for pretty printing of assembly code and expressions
- pyparsing_ for parsing instruction decoder formats
- ply_ (optional), for parsing *GNU as* files
- sqlalchemy_ (optional), provides analysis results as well as persistence of amoco objects in a database
- pyqt5_ (optional), for the graphical user interface

Installation is straightforward for most packages using pip_/pip3.
Note that for python2, the future_ package is now required to support new
python3 *bytes* when needed.

Grandalf, crysp, and pyparsing are mandatory, while others are optional.
The z3_ SMT solver is highly recommended (follow instructions from z3_ doc,
to build the python3 package just replace ``python scripts/mk_make.py`` by
``python3 scripts/mk_make.py``).
The pygments_ package is also recommended for pretty printing, and
sqlalchemy_ is required if you want to store analysis results and objects.
If you want to use the graphical interface you will need **all** packages.

.. _grandalf: https://github.com/bdcht/grandalf
.. _crysp: https://github.com/bdcht/crysp
.. _minisat: http://minisat.se/
.. _z3: http://z3.codeplex.com/
.. _pygments: http://pygments.org/
.. _armv8: http://www.cs.utexas.edu/~peterson/arm/DDI0487A_a_armv8_arm_errata.pdf
.. _pyparsing: http://pyparsing.wikispaces.com/
.. _ply: http://www.dabeaz.com/ply/
.. _sqlalchemy: http://www.sqlalchemy.org/
.. _pyqt5: https://www.riverbankcomputing.com/software/pyqt/download5
.. _pip: https://pypi.python.org/pypi/pip
.. _future: http://python-future.org/
