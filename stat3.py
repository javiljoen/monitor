#!/usr/bin/env python3

## inspiration from:
##    https://github.com/Dieterbe/profile-process

import sys
from time import sleep
import psutil

out = sys.stdout

if len(sys.argv) < 2:
    out.write('usage: ' + sys.argv[0] + ' <command to profile>\n')
    sys.exit(2)

child_args = sys.argv[1:]

interval = 0.5 # in seconds
sep = '\t'

proc = psutil.Popen(child_args, shell=False)

data_heads = ('Time',
              'CPU%', 'RSS', 'VMS', 'Threads',
              'IO reads', 'IO writes', 'IO read MB', 'IO written MB',
              'PID', 'Process')
out.write(sep.join(data_heads) + '\n')

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

