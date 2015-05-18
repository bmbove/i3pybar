from datetime import datetime

from .base import PluginBase


class ClockModule(PluginBase):

    def update(self):
        timestr = datetime.now().strftime(self.config['format'])
        self.set_text(timestr)
