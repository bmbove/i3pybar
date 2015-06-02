import os.path
import time

from .base import PluginBase


class CPUPlugin(PluginBase):

    def configure(self):
        defaults = {
            'format': '{cpu}%%',
        }
        self.source = '/proc/stat'
        self.last_usage = [0] * (self.num_cpus() + 1)
        self.last_time = 0
        return defaults

    def num_cpus(self):
        cores = -1
        for line in self.read_file(self.source).split("\n"):
            if 'cpu' in line:
                cores += 1
        return cores

    """
    /proc/stat isn't as 'accurate' as getting information from sysfs as far
    as I can tell (sysfs cpu data is in nanoseconds), but... CPU percentage
    isn't an exact science anyways.
    """
    def proc_usage(self):
        percents = []
        cur_time = time.time()
        usage = self.read_file(self.source).strip()
        d_time = cur_time - self.last_time
        self.last_time = cur_time
        usage_l = [line for line in usage.split("\n") if 'cpu' in line]
        for i in range(0, len(usage_l)):
            info = [int(item) for item in usage_l[i].split(" ") if ('cpu' not in item and item)]
            total = sum(info[0:-2])
            busy = total - info[3] - info[4]
            d_busy = busy - self.last_usage[i]
            percent = int((d_busy/(d_time*100)) * 100)
            percents.append(percent)
            self.last_usage[i] = busy 

        return percents 

    def update(self):
        stats = {}
        percents = self.proc_usage()
        stats['cpu'] = percents[0]
        for i in range(1, len(percents) - 1):
            stats['cpu%d' % (i-1)] = '%3d' % percents[i]

        locals().update(stats)
        self.set_text(self.config['format'] % locals())
