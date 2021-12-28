.. _ui:

The user interface package
==========================

The amoco user interface is meant to display informations about a binary
in a much more useful way than what can be shown on a simple terminal.
Ideally, we want to allow rich graphic display without losing the
ability to develop programs that access all parts of the framework API.

One common approach is to have a GUI application that has the ability to run
"scripts" when required, either loaded from a file or from a dedicated
GUI widget that provides interactive input/output from/to the user. This
approach favors user interaction based on the predefined fonctionalities
available from the graphical interface. Tools like IDA Pro and Ghidra both
follow this approach efficiently. In amoco we wanted the graphical interface
to be just a way of displaying information obtained from programming the analysis
of a binary.



Running the framework inside a graphical user interface
is to limit possible actions to a very small set of predefined
operations.

