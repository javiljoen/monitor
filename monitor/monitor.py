from time import sleep

import click
import psutil


def monitor(command, interval=1.0, sep='\t', proctype='pname', measure_io=False):
    """Record resource usage of `command` every `interval` seconds.

    Returns the resource usage of `command` and each subprocess it
    spawned as a list of `sep`-separated strings:
    one for each process at each sampling point in time.

    `proctype` must be either 'pname' or 'cmdline'.
    """

    def measure_resources(process, measure_io=False):
        if process.is_running():
            cpu_percent = process.get_cpu_percent(interval=0)
            n_threads = process.get_num_threads()
            mem_info = process.get_memory_info()

            if not measure_io:
                return cpu_percent, n_threads, mem_info

            try:
                io_counters = process.get_io_counters()
            except psutil.AccessDenied:
                io_counters = [-1] * 4

            return cpu_percent, n_threads, mem_info, io_counters

    def format_resources(t, pid, pname, res=None, sep='\t'):
        bytes_per_mb = 2 ** 20

        if len(res) == 4:
            cpu_percent, n_threads, mem_info, io_counters = res
            mem_rss = mem_info[0] // bytes_per_mb
            mem_vms = mem_info[1] // bytes_per_mb

            reads, writes, read_bytes, written_bytes = io_counters

            # Don't convert to MB if -1 (i.e. AccessDenied error)
            if read_bytes >= 0:
                read_mb = read_bytes // bytes_per_mb
                written_mb = written_bytes // bytes_per_mb
            else:
                read_mb = -1
                written_mb = -1

            data = (t,
                    cpu_percent, n_threads, mem_rss, mem_vms,
                    reads, writes, read_mb, written_mb,
                    pid, pname)
        else:
            cpu_percent, n_threads, mem_info = res
            mem_rss = mem_info[0] // bytes_per_mb
            mem_vms = mem_info[1] // bytes_per_mb
            data = (t,
                    cpu_percent, n_threads, mem_rss, mem_vms,
                    pid, pname)

        return sep.join(str(n) for n in data)

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
        resource_use = [measure_resources(p, measure_io) for p in processes]

        for proc, res in zip(processes, resource_use):
            if res is None:
                continue

            if proctype == 'cmdline':
                pname = ' '.join(proc.cmdline)
            else:
                pname = proc.name

            yield format_resources(t, proc.pid, pname, res, sep)

        sleep(interval)
        t += interval


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('cmd')
@click.option('-i', '--interval', default=0.5, show_default=True,
              help='frequency of measurement in seconds')
@click.option('-s', '--separator', default='\t', show_default=False,
              help=r'string for separating columns in output [default: \t]')
@click.option('-p', '--proctype', default='pname', show_default=True,
              type=click.Choice(['pname', 'cmdline']),
              help='pname: just process name; cmdline: full command')
@click.option('-o', '--output', default='-', show_default=True,
              type=click.File('w'),
              help='file to write the data to; - for stdout')
@click.option('--measure-io', default=False, show_default=False, is_flag=True,
              help='measure reads and writes, in addition to CPU and RAM')
def main(cmd, interval, separator, proctype, output, measure_io):
    """Per-process resource monitor

    Records the resource usage of the command CMD, including any child
    processes it spawns. CMD is given as a regular shell command escaped
    with single quotes. (If not escaped, it may be unclear whether the
    options apply to the monitoring or the monitored process.)

    e.g.
        monitor 'sleep 2'

    Note: If `--measure-io` was requested and the sampling interval is too
    short, the I/O measurements may fail, in which case they will return a
    value of -1.
    """
    if measure_io:
        data_heads = ('Time',
                      'CPU%', 'Threads', 'RSS', 'VMS',
                      'IO reads', 'IO writes', 'IO read MB', 'IO written MB',
                      'PID', 'Process')
    else:
        data_heads = ('Time',
                      'CPU%', 'Threads', 'RSS', 'VMS',
                      'PID', 'Process')
    output.write(separator.join(data_heads) + '\n')

    cmd = cmd.split()
    resource_usage = monitor(cmd, interval, separator, proctype, measure_io)

    for i, line in enumerate(resource_usage):
        output.write(line + '\n')
        if i % 100 == 0:
            output.flush()
