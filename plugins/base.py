import time
from threading import Thread

class PluginBase(Thread):

    daemon = True

    def __init__(self, out_q, config):
        self.out_q = out_q

        if not config.get('cache_time', False):
            config['cache_time'] = 1.0
        else:
            config['cache_time'] = float(config['cache_time'])

        self.config = config
        self._display = {
            'full_text': '',
            'color': '#%s' % config.get('color', 'FFFFFF')
        }
        super(PluginBase, self).__init__()


    def set_text(self, s):
        self._display['full_text'] = s

    def set_color(self, s):
        self.display['color'] = s

    def update(self):
        pass

    def run(self):
        while True:
            self.update()
            self.out_q.put([self.config['slot'], self._display])
            time.sleep(self.config['cache_time'])
