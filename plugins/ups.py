import subprocess
from .base import PluginBase

class UPSPlugin(PluginBase):

    def configure(self):
        defaults = {
                'format': 'UPS: {STATUS} Load: {LOADPCT} Charge: {BCHARGE} Left: {TIMELEFT}',
            #'format': 'UPS: {STATUS}',
            'color': 'FFFFFF'
        }
        return defaults

    def get_apc_status(self):
        command = ['apcaccess', 'status']
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        text = p.stdout.read()
        p.wait()
        text = text.decode().split("\n")
        status = {'STATUS': 'Error'}

        for line in text:
            line = line.split(":")
            if len(line) == 2:
                status[line[0].strip()] = line[1].strip()

        for key, value in status.items():
            status[key] = value.replace('Volts', 'V')
            status[key] = value.replace('Seconds', 's')
            status[key] = value.replace('Minutes', 'm')
            status[key] = value.replace('Minute', 'm')
            status[key] = value.replace('Percent', '%')



        return status

    def update(self):
        locals().update(self.get_apc_status())
        self.set_text(self.config['format'] % locals())
