import shutil

from .base import PluginBase
 

class DiskUsagePlugin(PluginBase):
 
    def configure(self):
        defaults = {
            'path': '/',
            'cache_time': '10',
            'format': '{path} {used}/{total} {percent_used}%%'
        }
        return defaults
 
    def update(self):
        disk = shutil.disk_usage(self.config['path'])
        data = {
            'free': '%7s' % self.format_size(disk.free),
            'used': '%7s' % self.format_size(disk.used),
            'total': '%7s' % self.format_size(disk.total),
            'path': self.config['path']
        }
        data['percent_used'] = int((disk.used/disk.total) * 100)

        locals().update(data)
        self.set_text(self.config['format'] % locals())
