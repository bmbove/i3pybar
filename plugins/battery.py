import os
import shutil

from .base import PluginBase
 

class BatteryPlugin(PluginBase):
 
    def configure(self):
        defaults = {
            'path': '/',
            'cache_time': '1',
            'format': '{status}'
        }
        self.sysfs_path = "/sys/class/power_supply"
        return defaults

    def get_battery_data(self):
        data = self.read_file(os.path.join(self.sysfs_path, 'BAT0', 'uevent'))
        batinfo = {}
        for line in data.split("\n"):
            try:
                line_l = line.strip().split("=")
                batinfo[line_l[0]] = line_l[1]
            except:
                pass
        return batinfo

    def update(self):
        try:
            data = self.get_battery_data()
            status = data['POWER_SUPPLY_STATUS']
            locals().update(data)
            self.set_text(self.config['format'] % locals())
        except Exception as e:
            self.set_text(str(e))
