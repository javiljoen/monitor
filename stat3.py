#!/usr/bin/env python3
'''Per-process resource monitor

Usage:
    stat3.py CMD
    stat3.py -h

Options:
    -h --help   this message

Records the resource usage of the command CMD, including any child
processes it spawns. CMD is specified just like a regular space-
delimited shell command.

e.g.
    stat3.py du -s /tmp

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

Dependencies:
    * Python 3
    * psutil 1.2 (syntax changes in v. 2)
    * docopt

Tested with Python 3.3.4 and psutil 1.2.1.

'''

import sys
from time import sleep
import psutil

if __name__ == '__main__':
    from docopt import docopt

    ## settings
    args = docopt(__doc__)
    child_args = args['CMD']
    out = sys.stdout
    interval = 0.5 # in seconds
    sep = '\t'

    ## table header
    data_heads = ('Time',
                'CPU%', 'RSS', 'VMS', 'Threads',
                'IO reads', 'IO writes', 'IO read MB', 'IO written MB',
                'PID', 'Process')
    out.write(sep.join(data_heads) + '\n')

    ## start the process & record resource usage,
    ## outputting to `out` every `interval` seconds
    proc = psutil.Popen(child_args, shell=False)

    t = 0
    while proc.poll() is None:
        procs = [proc] + proc.get_children(recursive=True)

        for p in procs:
            CPU = p.get_cpu_percent(interval=0)
            THD = p.get_num_threads()

            MEM = p.get_memory_info()
            RSS = MEM[0] // 1048576 # convert to MB
            VMS = MEM[1] // 1048576 # convert to MB

            IOr, IOw, IOrb, IOwb = p.get_io_counters()
            IOrb = IOrb // 1048576 # convert to MB
            IOwb = IOwb // 1048576 # convert to MB

            data = (t, CPU, RSS, VMS, THD, IOr, IOw, IOrb, IOwb, p.pid, p.name)
            out.write(sep.join([str(n) for n in data]) + '\n')

        sleep(interval)
        t += interval

    sys.exit(proc.returncode)

