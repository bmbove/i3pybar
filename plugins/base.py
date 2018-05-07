import json
import math
import re
import time

from urllib.request import urlopen, HTTPError, URLError

from threading import Thread

class PluginBase(Thread):

    daemon = True

    def __init__(self, out_q, config):

        self.out_q = out_q

        self.config = config
        defaults = self.configure()
        self.parse_config(defaults)

        self._display = {
            'full_text': ' ',
            'color': '#%s' % config.get('color', 'FFFFFF')
        }

        super(PluginBase, self).__init__()

    def configure(self):
        return {} 

    def parse_config(self, defaults):

        global_defaults = {
            'cache_time': '1',
            'format': '',
        }

        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value

        for key, value in global_defaults.items():
            if key not in self.config:
                self.config[key] = value

        self.config['format'] = self.fix_format(self.config['format'])
        self.config['cache_time'] = float(self.config['cache_time'])

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

    def format_size(self, size):
        size_name = ("B", "K", "M", "G", "T")
        try:
            i = int(math.floor(math.log(size,1024)))
        except:
            return '0B'
        p = math.pow(1024,i)
        s = round(size/p,2)
        if (s > 0):
            return '%.2f%s' % (s,size_name[i])
        else:
            return '0B'

    def read_file(self, filename, start=0):
        data = ""
        with open(filename, 'r') as fh:
            for i in range(start):
                fh.readline()
            for line in fh:
                data += line
        return data

    def grab_page(self, url):
        err = False 
        html = b''
        try: 
            response = urlopen(url)
            html = response.read()
        except HTTPError as e:
            err = e.code
        except URLError as e:
            err = 'url error'
        except:
            err = 'connection'

        return err, html.decode('ascii')

    def run(self):
        while True:
            try:
                self.update()
            except Exception as e:
                self._display = {
                    'full_text': "DISPLAY ERROR: {}".format(str(e)),
                    'color': '#FF2D00'
                }

            self.out_q.put([self.config['slot'], self._display])
            time.sleep(self.config['cache_time'])
