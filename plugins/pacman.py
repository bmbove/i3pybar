"""
@author Brian Bove https://github.com/bmbove
"""
import re
import subprocess
import time
from .base import PluginBase

# update every 10 minutes
UPDATE_TIME = 600

# checkupdates script is in `pacman-contrib` package
 
class PacmanPlugin(PluginBase):

    update_count = 0
    last_update = 0
 
    def configure(self):
        defaults = {
            'format': 'pacman {updates}'
        }
        return defaults

    def get_update_count(self):
        now = time.time()
        if now - self.last_update > UPDATE_TIME:
            try:
                lines = subprocess.check_output(["checkupdates"])
            except:
                return {'updates': '-'}
            lines = lines.decode('ascii').strip()
            self.update_count = max(0, len(lines.split("\n")) - 1)
            self.last_update = now
        return {'updates': self.update_count}
 
    def update(self):
        res = self.get_update_count()
        if type(res) == dict:
            locals().update(res)
            self.set_text(self.config['format'] % locals())
        else:
            self.set_text(res)
