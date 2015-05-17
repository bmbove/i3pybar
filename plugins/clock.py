from datetime import datetime

from .base import PluginBase


class ClockModule(PluginBase):

    def run(self):
        timestr = datetime.now().strftime(self.config['format'])
        self.set_text(timestr)
