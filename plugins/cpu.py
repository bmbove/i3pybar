import time

from .base import PluginBase


class CPUPlugin(PluginBase):

    def configure(self):
        defaults = {
            'format': '{cpu}%%'
        }
        self.last_usage = []
        self.last_time = 0
        return defaults

    def get_usage(self):
        usage = self.read_file('/sys/fs/cgroup/cpu/cpuacct.usage_percpu').strip()
        usage = [int(ns) for ns in usage.split(" ")]
        total = int(self.read_file('/sys/fs/cgroup/cpu/cpuacct.usage'))
        usage.append(total)
        return usage 

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

        for i in range(0, len(percents) - 1):
            stats['cpu%d' % i] = percents[i]
        stats['cpu'] = percents[len(percents)-1]

        locals().update(stats)
        self.set_text(self.config['format'] % locals())
