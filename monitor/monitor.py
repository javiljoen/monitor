from time import sleep

import click
import psutil


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
def main(cmd, interval, separator, proctype, output):
    """Per-process resource monitor

    Records the resource usage of the command CMD, including any child
    processes it spawns. CMD is given as a regular shell command escaped
    with single quotes. (If not escaped, it may be unclear whether the
    options apply to the monitoring or the monitored process.)

    e.g.
        monitor 'sleep 2'

    Warning: Likely to fail on short-running commands (like `du -s .`)!
    """
    cmd = cmd.split()
    resource_usage = monitor(cmd, interval, separator, proctype)

    data_heads = ('Time',
                  'CPU%', 'Threads', 'RSS', 'VMS',
                  'IO reads', 'IO writes', 'IO read MB', 'IO written MB',
                  'PID', 'Process')
    output.write(separator.join(data_heads) + '\n')

    for i, line in enumerate(resource_usage):
        output.write(line + '\n')
        if i % 100 == 0:
            output.flush()
