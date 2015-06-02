from .base import PluginBase


class MemoryPlugin(PluginBase):

    def configure(self):
        defaults = {
            'divisor': str(1024**2),
            'format': '{used}/{total} {percent}%%'
        }
        return defaults

    def get_meminfo(self):

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
            'used': '%7s' % self.format_size(used_mem * 1024),
            'total': '%s' % self.format_size(mem_dict['MemTotal'] * 1024),
            'free': '%7s' % self.format_size(free_mem),
        }

        percent_used = int((used_mem/mem_dict['MemTotal']) * 100)
        mem_info['percent'] = percent_used
        return mem_info

    def update(self):
        locals().update(self.get_meminfo())
        self.set_text(self.config['format'] % locals())
