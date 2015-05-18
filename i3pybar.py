import importlib
import inspect
import json
import os
import re
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
        for mod in [mod for mod in self.config if mod['name'] != 'general']:
            try:
                plugin = importlib.import_module('plugins.%s' % mod['name'])
                mod_list = dir(plugin)
                for method in mod_list:
                    cls = getattr(plugin, method)
                    if inspect.isclass(cls) and cls != PluginBase:
                        if issubclass(cls, PluginBase):
                            mods.append(cls(mod['settings']))
            except Exception as e:
                print(e)
                self.handle_err("Could not load module %s" % mod['name'])

        self.mods = mods

    def load_config(self):
        config = []
        section_re = re.compile('^\[(?P<plugin>[-\w]+)\]$')
        option_re = re.compile('^(?P<option>[\w-]+)[\s+]?=[\s+]?(?P<value>.*)')
        plugin_name = ''
        try:
            path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(path, 'settings.conf'), 'r') as fh:
                lines = [line.strip() for line in fh]
            for line in lines:
                sec_m = section_re.match(line)
                opt_m = option_re.match(line)
                if sec_m:
                    plugin_name = sec_m.group('plugin')
                    config.append({'name': plugin_name, 'settings':{}})
                if opt_m:
                    option = opt_m.group('option')
                    value = opt_m.group('value')
                    config[len(config)-1]['settings'][option] = value
        except Exception as e:
            config.append({ 
                'name': 'general',
                'settings': {'interval': '1'}
            })
            config.append({ 
                'name': 'clock',
                'settings': {'format': '%a %d %b %H:%M:%S'},
            })

        for i, dic in enumerate(config):
            if dic['name'] == 'general':
                config.insert(0, config.pop(i))

        self.config = config
        self.interval = float(config[0]['settings']['interval'])

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
