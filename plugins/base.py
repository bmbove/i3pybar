import time

class PluginBase(object):

    def __init__(self, config):
        if not config.get('cache_time', False):
            config['cache_time'] = 1.0
        else:
            config['cache_time'] = float(config['cache_time'])
        self.config = config
        self._display = {
            'full_text': '',
            'color': '#%s' % config.get('color', 'FFFFFF')
        }
        self.last_update = 0

    def set_text(self, s):
        self._display['full_text'] = s

    def set_color(self, s):
        self.display['color'] = s

    def run(self):
        pass

    def output(self):
        if (time.time() - self.last_update) > self.config['cache_time']:
            self.run()
            self.last_update = time.time()
        return self._display 
