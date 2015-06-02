import os
import shutil
import time

from .base import PluginBase
 

class BatteryPlugin(PluginBase):
 
    def configure(self):
        defaults = {
            'path': '/',
            'cache_time': '1',
            'format': '{status}'
        }
        self.sysfs_path = "/sys/class/power_supply"
        self.last_charge = 0
        self.last_time = time.time() - 21
        self.time_rem = ''
        self.prev_status = 'Unknown'
        self.start_time = time.time()
        self.get_battery_data()
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

        batinfo_h = {
            'status': batinfo['POWER_SUPPLY_STATUS'],
            'charge': int(batinfo['POWER_SUPPLY_CHARGE_NOW']),
            'full': int(batinfo['POWER_SUPPLY_CHARGE_FULL']),
            'time_rem': '',
            'percent': 0,
        }
        batinfo_h['percent'] = int((batinfo_h['charge']/batinfo_h['full']) * 100)

        check_time = (batinfo_h['status'] != 'Unknown')
        if check_time and (time.time() - self.last_time > 10):
            check_time = True
        else:
            check_time = False

        if batinfo_h['status'] != self.prev_status:
            check_time = True

        if (time.time() - self.start_time) < 5: 
            check_time = True

        self.prev_status = batinfo_h['status']

        if check_time:
            try:
                delta_c = batinfo_h['charge'] - self.last_charge
                delta_t = time.time() - self.last_time
                charge_left = batinfo_h['full'] - batinfo_h['charge']
                time_left = int(charge_left * (delta_t/delta_c))
                self.last_charge = batinfo_h['charge']
                self.last_time = time.time()
                m, s = divmod(time_left, 60)
                h, m = divmod(m, 60)
                batinfo_h['time_rem'] = "%dh %02dm" % (abs(h), m)
                self.time_rem = batinfo_h['time_rem']
            except:
                pass
        else:
            batinfo_h['time_rem'] = self.time_rem


        return batinfo_h

    def update(self):
        try:
            data = self.get_battery_data()
            status = data['status']
            locals().update(data)
            self.set_text(self.config['format'] % locals())
        except Exception as e:
            self.set_text(str(e))
