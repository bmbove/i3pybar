#!/usr/bin/python
import configparser
import importlib
import sys
import time

from datetime import datetime
from threading import Thread, Event


class I3Bar(Thread):

    daemon = True
    _stop = Event()

    def __init__(self):
        self.text = '[{ "full_text" : "XXX " , "color" : "#FFFFFF" }],'
        print('{"version":1}')
        print('[')
        print('[],')
        #self.load_config()
        super(I3Bar, self).__init__()

    def load_config(self):
        config = configparser.ConfigParser()
        config['clock'] = { 
            'format': '%a %d %b %H:%M:%S',
            'rate': '1'
        }
        try:
            config.read('config.ini')
        except:
            pass

        for mod in config.sections():
            mods.append(importlib.import_module('modules.clock'))

        self.config = config

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):

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

