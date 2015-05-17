import configparser
import importlib
import inspect
import sys
import time

from datetime import datetime
from threading import Thread, Event

from plugins.base import ModBase


class I3Bar(Thread):

    daemon = True
    _stop = Event()

    def __init__(self):
        self.text = '[{ "full_text" : "XXX " , "color" : "#FFFFFF" }],'
        self.load_config()
        self.load_plugins()
        super(I3Bar, self).__init__()

    def load_plugins(self):
        mods = {}
        for mod in [mod for mod in self.config.sections() if mod != 'general']:
            try:
                plugin = importlib.import_module('plugins.%s' % mod)
                mod_list = dir(plugin)
                for method in mod_list:
                    cls = getattr(plugin, method)
                    if inspect.isclass(cls):
                        if issubclass(cls, ModBase):
                            mods[mod] = {
                                'instance': cls(config[mod]),
                                'config': config[mod],
                            }
            except Exception as e:
                print("Could not load module")
        self.mods = mods

    def load_config(self):
        config = configparser.ConfigParser(interpolation=None)
        config['clock'] = { 
            'format': '%a %d %b %H:%M:%S',
            'rate': '1'
        }
        try:
            config.read('config.ini')
        except:
            pass

        self.config = config

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):

        print('{"version":1}')
        print('[')
        print('[],')

        while not self.stopped():
            text = self.text.replace(
                "XXX",
                datetime.now().strftime("%a %d %b %H:%M:%S")
            )
            print(text)
            sys.stdout.flush()
            time.sleep(1)
        exit(0)


bar = I3Bar()

def main():
    global bar
    bar.start()

    while bar.isAlive():
        time.sleep(3)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        bar.stop()
        exit(0)
