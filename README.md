Monitor
=======

Resource monitor for profiling processes and their subprocesses

Usage
-----

    monitor.py [-i INTERVAL] [-s SEP] [-o OUTPUT] CMD
    monitor.py -h

Options
-------

    -h --help    this message
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
being much less sophisticated in all other regards. It also requires
the `psutil` module to be installed to provide the `.get_children()`
method.

The `psutil` loop is a reimplementation of the one in `profile-process`
that does not send the data straight to matplotlib for plotting, and
breaks it up into usage stats per subprocess.

There is also a script for plotting the results, if you have R and
ggplot2 installed.

Usage:

	./plot_log.r log_file plot_file ['Title for plot']

Dependencies
------------

    * Python 3
    * psutil 1.2 (syntax changes in v.\ 2)
    * docopt

Tested with Python 3.3.4 and psutil 1.2.1.

The plotting script requires R and the R package `ggplot2`.
It has been tested with R 3.0 and ggplot2 v.\ 1.0.

Installation
------------

`monitor.py` is a simple, self-contained Python script, so just download
it from GitHub, `chmod +x` it, and run it.

The simplest way to get the whole source folder is:

	git clone [--depth=1] https://github.com/javiljoen/monitor

where the `depth` parameter will get you the latest version only
instead of the whole commit history.

