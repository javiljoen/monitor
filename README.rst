Monitor
=======

Resource monitor for profiling processes and their subprocesses


Usage
-----

::

   monitor [OPTIONS] CMD
   monitor -h


Options
^^^^^^^

::

   -i, --interval FLOAT            frequency of measurement in seconds
   -s, --separator TEXT            string for separating columns in output
   -p, --proctype [pname|cmdline]  pname: just process name;
                                   cmdline: full command
   -o, --output FILENAME           file to write the data to; - for stdout
   --measure-io                    measure reads and writes, in addition to
                                   CPU and RAM
   -h, --help                      Show this message and exit.


Records the resource usage of the command ``CMD``, including any child
processes it spawns. ``CMD`` is given as a regular shell command escaped
with single quotes. (If not escaped, it may be unclear whether the
options apply to the monitoring or the monitored process.)

e.g.::

   monitor 'sleep 2'

Note: If `--measure-io` was requested and the sampling interval is too short,
the I/O measurements may fail, in which case they will return a value of -1.

------------------------------------------------------------------------

This tool is inspired by:

-  https://github.com/jeetsukumaran/Syrupy
-  https://github.com/Dieterbe/profile-process

It differs from Syrupy in also accounting for child processes, while
being much less sophisticated in all other regards. It also uses the
``psutil`` module instead of ``subprocess`` in the standard library
since it makes use of the ``Process.get_children()`` method. (It might
also be cross-platform, since it does not rely on the ``ps`` shell
command, but I have only tested it in Linux.)

The ``psutil`` loop is a reimplementation of the one in
``profile-process``, returning the data instead of sending them to
Matplotlib for plotting, and breaking them up into usage stats per
subprocess.


Installation
------------

Download the source from GitHub::

   git clone [--depth=1] https://github.com/javiljoen/monitor.git

where the ``depth`` parameter will get you the latest version only
instead of the whole commit history.

Then install the package into a virtual environment, e.g.::

   conda create -n monitor python=3 psutil=1 click
   source activate monitor
   pip install monitor


Requirements
^^^^^^^^^^^^

-  Python 3
-  ``psutil 1.2`` (syntax changes in v. 2)
-  ``click``

Tested with Python 3.3.4 and ``psutil 1.2.1``.


Testing
-------

Running::

   monitor monitor/tests/testscript.sh

should result in output like:

==== ==== ======= === === ======== ========= ========== ============= ===== =============
Time CPU% Threads RSS VMS IO reads IO writes IO read MB IO written MB   PID Process
==== ==== ======= === === ======== ========= ========== ============= ===== =============
   0  0.0       1   2  12       11         0          0             0 24220 testscript.sh
 0.5  0.0       1   2  12       11         0          0             0 24220 testscript.sh
 0.5  0.0       1   7  26       61       620          0             0 24221 python
 0.5  0.0       1   1  15     1872      1240          0             0 24222 sed
 0.5  0.0       1   0   7     1247      1241          0             0 24223 tr
==== ==== ======= === === ======== ========= ========== ============= ===== =============


------------------------------------------------------------------------

Licence: MIT

