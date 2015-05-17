import configparser
import importlib
import inspect
import json
import os
import sys
import time

from datetime import datetime
from threading import Thread, Event

from plugins.base import PluginBase


class I3Bar(Thread):

    daemon = True
    _stop = Event()

    def __init__(self):
        self.load_config()
        self.load_plugins()
        super(I3Bar, self).__init__()

    def handle_err(self, err):
        print(err)

    def load_plugins(self):
        mods = []
        for mod in [mod for mod in self.config.sections() if mod != 'general']:
            try:
                plugin = importlib.import_module('plugins.%s' % mod)
                mod_list = dir(plugin)
                for method in mod_list:
                    cls = getattr(plugin, method)
                    if inspect.isclass(cls) and cls != PluginBase:
                        if issubclass(cls, PluginBase):
                            mods.append(cls(self.config[mod]))
            except Exception as e:
                print(e)
                self.handle_err("Could not load module %s" % mod)

        self.mods = mods

    def load_config(self):
        config = configparser.ConfigParser(interpolation=None)
        try:
            path = os.path.dirname(os.path.realpath(__file__))
            config.read(os.path.join(path, 'settings.conf'))
        except Exception as e:
            config['general'] = { 
                'interval': '1',
            }
            config['clock'] = { 
                'format': '%a %d %b %H:%M:%S',
            }

        self.config = config
        self.interval = float(config['general']['interval'])

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):

        print('{"version":1}')
        print('[')
        print('[],')

        while not self.stopped():
            out = []
            for mod in self.mods:
                out.append(mod.output())
                #print([key for key in mod.config.items()])
            print("%s," % json.dumps(out))
            sys.stdout.flush()
            time.sleep(self.interval)
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
