"""
@author Brian Bove https://github.com/bmbove
"""
import re
import subprocess
from .base import PluginBase
 
class PacmanPlugin(PluginBase):
 
    def configure(self):
        defaults = {
            'format': 'pacman {updates}'
        }
        return defaults

    def get_update_count(self):
        lines = subprocess.check_output(["checkupdates"])
        lines = lines.decode('ascii').strip()
        return {'updates': len(lines.split("\n"))}
 
    def update(self):
        res = self.get_update_count()
        if type(res) == dict:
            locals().update(res)
            self.set_text(self.config['format'] % locals())
        else:
            self.set_text(res)
