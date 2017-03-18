Monitor
=======

Resource monitor for profiling processes and their subprocesses

Usage
-----

    monitor.py [-i INTERVAL] [-s SEP] [-o OUTPUT] CMD
    monitor.py -h

Options
-------

    -h --help    help message
    -i INTERVAL  frequency of measurement in seconds [default: 0.5]
    -s SEP       string for separating columns in output [default: \t]
    -o OUTPUT    file to write the data to, if not stdout [default: -]

Records the resource usage of the command `CMD`, including any child
processes it spawns. `CMD` is given as a regular shell command escaped
with single quotes. (If not escaped, it may be unclear whether the
options apply to the monitoring or the monitored process.)

e.g.

    monitor.py 'sleep 2'

Warning: Likely to fail on short-running commands (like `du -s .`)!

This script is inspired by:

* https://github.com/jeetsukumaran/Syrupy
* https://github.com/Dieterbe/profile-process

It differs from Syrupy in also accounting for child processes, while
being much less sophisticated in all other regards. It also uses
the `psutil` module instead of `subprocess` in the standard library
since it makes use of the `Process.get_children()` method.
(It might also be cross-platform, since it does not rely on the `ps`
shell command, but I have only tested it in Linux.)

The `psutil` loop is a reimplementation of the one in `profile-process`,
returning the data instead of sending them to matplotlib for plotting,
and breaking them up into usage stats per subprocess.

Dependencies
------------

* Python 3
* `psutil 1.2` (syntax changes in v. 2)
* `docopt`

Tested with Python 3.3.4 and `psutil 1.2.1`.

Installation
------------

`monitor.py` is a simple, self-contained Python script, so just download
it from GitHub, `chmod +x` it, and run it.

The simplest way to get the whole source folder is:

	git clone [--depth=1] https://github.com/javiljoen/monitor.git

where the `depth` parameter will get you the latest version only
instead of the whole commit history.

