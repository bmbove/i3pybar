from .base import PluginBase


class MemoryPlugin(PluginBase):

    def configure(self, config):
        if 'divisor' not in config:
            config['divisor'] = 1024.0**2
        if 'format' not in config:
            config['format'] = "{used}/{total} {percent}%%"
        config['format'] = self.fix_format(config['format'])
        return config

    def get_meminfo(self):

        div = float(self.config['divisor'])
        mem_dict = {}
        lines = self.read_file('/proc/meminfo')
        for line in lines.split("\n"):
            data = [info for info in line.split(" ") if info]
            if len(data) > 0:
                mem_dict[data[0].replace(":", "")] = int(data[1])

        free_mem = mem_dict['MemFree']
        free_mem += mem_dict['Buffers'] 
        free_mem += mem_dict['Cached']

        used_mem = mem_dict['MemTotal'] - free_mem

        mem_info = {
            'used': '%.2f' % (used_mem/div),
            'total': '%.2f' % (mem_dict['MemTotal']/div),
            'free': '%.2f' % (free_mem/div),
        }

        percent_used = int((used_mem/mem_dict['MemTotal']) * 100)
        mem_info['percent'] = percent_used
        return mem_info

    def update(self):
        locals().update(self.get_meminfo())
        self.set_text(self.config['format'] % locals())
