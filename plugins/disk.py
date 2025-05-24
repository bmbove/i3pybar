import shutil

from .base import PluginBase
 

class DiskUsagePlugin(PluginBase):
 
    def configure(self):
        defaults = {
            'path': '/',
            'cache_time': '10',
            'format': '{path} {used}/{total} {percent_used}%'
        }
        return defaults
 
    def update(self):
        disk = shutil.disk_usage(self.config['path'])
        fvars = {
            'free': '{:7s}'.format(self.format_size(disk.free)),
            'used': '{:7s}'.format(self.format_size(disk.used)),
            'total': '{:7s}'.format(self.format_size(disk.total)),
            'path': self.config['path']
        }
        fvars['percent_used'] = int((disk.used/disk.total) * 100)

        
        self.set_text(
            self.format_from_dict(self.config['format'], fvars)
        )
