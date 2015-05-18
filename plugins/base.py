import re
import time
from threading import Thread

class PluginBase(Thread):

    daemon = True

    def __init__(self, out_q, config):

        self.out_q = out_q
        self.default_config = self.configure()
        self.config['cache_time'] = float(self.config.get('cache_time', 1.0))

        self._display = {
            'full_text': ' ',
            'color': '#%s' % config.get('color', 'FFFFFF')
        }

        super(PluginBase, self).__init__()

    def configure(self):
        return {} 

    def parse_config(self, defaults):
        pass

    def set_text(self, s):
        self._display['full_text'] = s

    def set_color(self, s):
        self.display['color'] = s

    def set_cache_time(self, d):
        self.config['cache_time'] = d

    def update(self):
        pass

    def fix_format(self, f):
        return re.sub(r'{(?P<item>[a-zA-Z0-9_]+)}', r'%(\g<item>)s', f)

    def read_file(self, filename, start=0):
        data = ""
        with open(filename, 'r') as fh:
            for i in range(start):
                fh.readline()
            for line in fh:
                data += line
        return data

    def run(self):
        while True:
            self.update()
            self.out_q.put([self.config['slot'], self._display])
            time.sleep(self.config['cache_time'])
