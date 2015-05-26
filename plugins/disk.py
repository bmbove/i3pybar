import shutil

from .base import PluginBase
 

class DiskUsagePlugin(PluginBase):
 
    def configure(self):
        defaults = {
            'path': '/',
            'cache_time': '10',
            'format': '{path} {used}G/{total}G {percent_used}%%'
        }
        return defaults
 
    def update(self):
        disk = shutil.disk_usage(self.config['path'])
        data = {
            'free': '%.1f' % (disk.free/(2**30)),
            'used': '%.1f' % (disk.used/(2**30)),
            'total': '%.1f' % (disk.total/(2**30)),
            'path': self.config['path']
        }
        data['percent_used'] = int((disk.used/disk.total) * 100)

        locals().update(data)
        self.set_text(self.config['format'] % locals())
