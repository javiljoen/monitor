#!/usr/bin/env python3
"""Per-process resource monitor

Usage:
    monitor [-i INTERVAL] [-s SEP] [-p PROCTYPE] [-o OUTPUT] CMD
    monitor -h

Options:
    -h --help    this message
    -i INTERVAL  frequency of measurement in seconds [default: 0.5]
    -s SEP       string for separating columns in output [default: \t]
    -p PROCTYPE  just process name ('pname') or
                 full command ('cmdline') [default: pname]
    -o OUTPUT    file to write the data to, if not stdout [default: -]

Records the resource usage of the command CMD, including any child
processes it spawns. CMD is given as a regular shell command escaped
with single quotes. (If not escaped, it may be unclear whether the
options apply to the monitoring or the monitored process.)

e.g.
    monitor 'sleep 2'

Warning: Likely to fail on short-running commands (like `du -s .`)!

"""
from time import sleep

import psutil
from docopt import docopt


def monitor(command, interval=1.0, sep='\t', proctype='pname'):
    """Record resource usage of `command` every `interval` seconds.

    Returns the resource usage of `command` and each subprocess it
    spawned as a list of `sep`-separated strings:
    one for each process at each sampling point in time.

    `proctype` must be either 'pname' or 'cmdline'.
    """

    def measure_resources(process):
        if process.is_running():
            cpu_percent = process.get_cpu_percent(interval=0)
            n_threads = process.get_num_threads()
            mem_info = process.get_memory_info()
            io_counters = process.get_io_counters()
            return cpu_percent, n_threads, mem_info, io_counters

    def format_resources(t, pid, pname, res=None, sep='\t'):
        """Convert bytes to MB and return fields as a `sep`-separated string.

        If measure_resources() returned None, return the string with empty
        fields where appropriate.
        """
        if res is not None:
            cpu_percent, n_threads, mem_info, io_counters = res
            bytes_per_mb = 2 ** 20
            mem_rss = mem_info[0] // bytes_per_mb
            mem_vms = mem_info[1] // bytes_per_mb
            reads, writes, read_bytes, written_bytes = io_counters
            read_mb = read_bytes // bytes_per_mb
            written_mb = written_bytes // bytes_per_mb
            data = (t,
                    cpu_percent, n_threads, mem_rss, mem_vms,
                    reads, writes, read_mb, written_mb,
                    pid, pname)
        else:
            data = (t, '' * 8, pid, pname)

        return sep.join((str(n) for n in data))

    # res_use = []
    t = 0

    process = psutil.Popen(command, shell=False)

    # In each sampling interval:
    # * check that the main process has not yet terminated
    # * get a list of its child processes
    # * then for each one, measure resource usage
    while process.poll() is None:
        processes = [process] + process.get_children(recursive=True)

        # Do all measurements first:
        # If doing formatting inside this `for` loop, the next process
        # might have ended before it is measured.
        resource_use = [measure_resources(p) for p in processes]

        for proc, res in zip(processes, resource_use):
            if proctype == 'cmdline':
                pname = ' '.join(proc.cmdline)
            else:
                pname = proc.name

            yield format_resources(t, proc.pid, pname, res, sep)

        sleep(interval)
        t += interval


def main():
    args = docopt(__doc__)
    interval = float(args['-i'])
    sep = args['-s']
    proctype = args['-p']
    child_args = args['CMD'].split()
    outfile = args['-o']

    data_heads = ('Time',
                  'CPU%', 'Threads', 'RSS', 'VMS',
                  'IO reads', 'IO writes', 'IO read MB', 'IO written MB',
                  'PID', 'Process')

    resource_usage = monitor(child_args, interval, sep, proctype)

    if outfile != '-':
        with open(outfile, 'w') as out:
            out.write(sep.join(data_heads) + '\n')

            for i, line in enumerate(resource_usage):
                out.write(line + '\n')
                if i % 100 == 0:
                    out.flush()
    else:
        print(sep.join(data_heads))
        for line in resource_usage:
            print(line)


if __name__ == '__main__':
    main()
