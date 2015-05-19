import os.path
import time

from .base import PluginBase


class CPUPlugin(PluginBase):

    def configure(self):
        defaults = {
            'format': '{cpu}%%',
            'use_proc': False,
        }
        self.last_usage = []
        self.last_time = 0
        self.source = '/sys/fs/cgroup/cpu/cpuacct.usage_percpu'
        if not os.path.isfile(self.source) or bool(defaults['use_proc']):
            self.source = '/proc/stat'
        return defaults

    def get_usage(self):
        stats = []
        usage = self.read_file(self.source).strip()
        if 'sys' in self.source:
            stats = [int(ns) for ns in usage.split(" ")]
            total = int(self.read_file('/sys/fs/cgroup/cpu/cpuacct.usage'))
            stats.append(total)
            stats.insert(0, stats.pop())
        else:
            # not sure of the accuracy of this..
            usage_l = [line for line in usage.split("\n") if 'cpu' in line]
            for i in range(0, len(usage_l)):
                info = [item for item in usage_l[i].split(" ") if item]
                busy = (int(info[1]) + int(info[2]) + int(info[3])) * 10000000
                stats.append(busy)
        return stats 

    def calc_percents(self, usage):

        if len(self.last_usage) < len(usage):
            self.last_usage = [0] * len(usage)

        d_usage = []
        for i in range(0, len(usage)):
            d_usage.append(usage[i] - self.last_usage[i])

        dt = (time.time() - self.last_time) * (10**9)
        percents = [int((dns/dt) * 100) for dns in d_usage]
        self.last_time = time.time()
        self.last_usage = usage
        return percents

    def update(self):
        stats = {}
        percents = self.calc_percents(self.get_usage())

        stats['cpu'] = percents[0]
        for i in range(1, len(percents) - 1):
            stats['cpu%d' % (i-1)] = percents[i]

        locals().update(stats)
        self.set_text(self.config['format'] % locals())
