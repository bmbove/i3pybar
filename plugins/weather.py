"""
@author David Brenner https://github.com/davidbrenner
"""
import re

from urllib.request import urlopen
from urllib.request import HTTPError
 
from .base import PluginBase
 
class WeatherPlugin(PluginBase):
 
    def configure(self, config):
        if 'metric' not in config:
            config['metric'] = False
        if 'location' not in config:
            # NY, NY zip code
            config['location'] = 10001
        if not config.get('cache_time', False):
            config['cache_time'] = 600.0
        if 'format' not in config:
            config['format'] = "{conditions}: {temperature}"
        config['format'] = self.fix_format(config['format'])
        return config
 
    def get_weather(self):
 
        base_uri = 'http://rss.accuweather.com/rss/liveweather_rss.asp'
        url = '%s?metric={metric}&locCode={location}' % base_uri
        url = url.format(
            metric=self.config['metric'],
            location=self.config['location']
        )

        try:
            q = urlopen(url)
        except HTTPError as e:
            return 'error: {}'.format(e.code)

        weather = ''
        re_str = ">Currently: (?P<conditions>[\s\w]+?): (?P<temp>[\w]+?)<"
        m = re.search(re_str, q.read().decode('ascii'))
        weather = {}
        weather['conditions'] = m.group('conditions')
        weather['temperature'] = m.group('temp')
 
        return weather
 
    def update(self):
        locals().update(self.get_weather())
        self.set_text(self.config['format'] % locals())
