"""
@author David Brenner https://github.com/davidbrenner
"""
import re

from urllib.request import urlopen
from urllib.request import HTTPError
 
from .base import PluginBase
 
class WeatherPlugin(PluginBase):
 
    def configure(self):
        defaults = {
            'metric': False,
            'location': '10001',
            'cache_time': '600',
            'format': '{conditions} {temp}'
        }
        return defaults
 
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
        except:
            return 'error: {}'.format('connection')

        weather = ''
        re_str = ">Currently: (?P<conditions>[\s\w]+?): (?P<temp>[\w]+?)<"
        m = re.search(re_str, q.read().decode('ascii'))
        weather = {}
        weather['conditions'] = m.group('conditions')
        weather['temp'] = m.group('temp')
 
        return weather
 
    def update(self):
        weather = self.get_weather()
        if type(weather) == dict:
            locals().update(weather)
            self.set_text(self.config['format'] % locals())
        else:
            self.set_text(weather)
