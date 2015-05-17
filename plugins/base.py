class PluginBase(object):

    def __init__(self, config):
        self.config = config
        self._display = {
            'full_text': '',
            'color': '#%s' % config.get('color', 'FFFFFF')
        }

    def set_text(self, s):
        self._display['full_text'] = s

    def set_color(self, s):
        self.display['color'] = s

    def run(self):
        pass

    def output(self):
        self.run()
        return self._display 
