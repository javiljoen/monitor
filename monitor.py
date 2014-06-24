#!/usr/bin/env python3
'''Per-process resource monitor

Usage:
    monitor.py [-i INTERVAL] [-s SEP] [-o OUTPUT] CMD
    monitor.py -h

Options:
    -h --help    this message
    -i INTERVAL  frequency of measurement in seconds [default: 0.5]
    -s SEP       string for separating columns in output [default: \t]
    -o OUTPUT    file to write the data to, if not stdout [default: -]

Records the resource usage of the command CMD, including any child
processes it spawns. CMD is given as a regular shell command escaped
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

Dependencies:
    * Python 3
    * psutil 1.2 (syntax changes in v. 2)
    * docopt

Tested with Python 3.3.4 and psutil 1.2.1.

'''

from time import sleep
import psutil

def monitor(command, interval, sep):
    '''(str, float, str) -> list(str)

    Record resource usage of `command` every `interval` seconds,
    do some formatting and return the resource usage of `command` and
    each subprocess it spawned as a list of `sep`-separated strings:
    one line for each process at each sampling point in time.

    '''
    def measure_resources(p):
        '''Process -> (int, int, [int, int], [int, int, int, int])'''
        if p.is_running():
            CPU = p.get_cpu_percent(interval=0)
            THD = p.get_num_threads()
            MEM = p.get_memory_info()
            IO  = p.get_io_counters()
            return (CPU, THD, MEM, IO)

    def format_resources(t, pid, pname, res, sep):
        '''(float, int, str, (result of measure_resources()), str) -> str

        Convert bytes to MB and return fields as a `sep`-separated string.
        If measure_resources() returned None, return the string with empty
        fields where appropriate.

        '''
        if res is not None:
            CPU, THD, MEM, IO = res
            RSS = MEM[0] // 1048576 # convert to MB
            VMS = MEM[1] // 1048576 # convert to MB
            IOr, IOw, IOrb, IOwb = IO
            IOrb = IOrb // 1048576 # convert to MB
            IOwb = IOwb // 1048576 # convert to MB
            data = (t, CPU, THD, RSS, VMS, IOr, IOw, IOrb, IOwb, pid, pname)
        else:
            data = (t, '' * 8, pid, pname)

        return sep.join((str(n) for n in data))

    ## initialize
    res_use = []
    t = 0

    ## start the command running
    proc = psutil.Popen(command, shell=False)

    ## in each sampling interval:
    ## * check that the main process has not yet terminated
    ## * get a list of its child processes
    ## * then for each one, measure resource usage
    while proc.poll() is None:
        procs = [proc] + proc.get_children(recursive=True)

        # for p in procs:
            # resource_use = measure_resources(p)
            # output_str = format_resources(t, p.pid, p.name, resource_use, sep)
            # res_use.append(output_str)

        ## do all measurements first.
        ## if using a `for` loop with formatting and IO (as above),
        ## the next process might end before it is measured
        resource_use = [measure_resources(p) for p in procs]
        output_str = [format_resources(t, procs[i].pid, procs[i].name, resource_use[i], sep)
                      for i in range(len(procs))]
        res_use += output_str

        sleep(interval)
        t += interval

    return res_use


if __name__ == '__main__':
    from docopt import docopt
    import sys

    ## parse user settings
    args = docopt(__doc__)
    interval = float(args['-i'])
    sep = args['-s']
    child_args = args['CMD'].split()
    outfile = args['-o']

    if outfile == '-':
        out = sys.stdout
    else:
        out = open(outfile, 'w')

    ## run the command and record resource usage
    resource_use = monitor(child_args, interval, sep)

    ## write out results
    data_heads = ('Time',
                  'CPU%', 'Threads', 'RSS', 'VMS',
                  'IO reads', 'IO writes', 'IO read MB', 'IO written MB',
                  'PID', 'Process')
    out.write(sep.join(data_heads) + '\n')

    for l in resource_use:
        out.write(l + '\n')

