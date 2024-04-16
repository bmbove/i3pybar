"""
@author David Brenner https://github.com/davidbrenner
"""

import re
import json

from .base import PluginBase


class WeatherPlugin(PluginBase):

    def configure(self):
        defaults = {
            "lat": 0,
            "lon": 0,
            "cache_time": "600",
            "format": "{conditions} {temp}",
        }
        return defaults

    def get_weather(self):

        points_base_uri = "https://api.weather.gov/points/{lat},{lon}"

        url = points_base_uri.format(
            lat=self.config["lat"], lon=self.config["lon"]
        )
        err, html = self.grab_page(url)
        if not err:
            j = json.loads(html)
            try:
                forecast_uri = j["properties"]["forecastHourly"]
            except Exception as e:
                return "error: {}".format(e)
            err, html = self.grab_page(forecast_uri)
            if not err:
                j = json.loads(html)
                w = j["properties"]["periods"][0]
                weather = {}
                weather["conditions"] = w["shortForecast"]
                weather["temp"] = w["temperature"]
                return weather
            else:
                return "error: {}".format(err)
        else:
            return "error: {}".format(err)

    def update(self):
        weather = self.get_weather()
        if type(weather) == dict:
            locals().update(weather)
            self.set_text(self.config["format"] % locals())
        else:
            self.set_text(weather)
