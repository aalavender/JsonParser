"""
A component which allows you to parse an josn web server to a sensor
for example 163 headline: https://c.m.163.com/nc/article/headline/T1348647853363/0-10.html
For more details about this component, please refer to the documentation at
https://github.com/aalavender/JsonParser

"""
import logging
import asyncio
import voluptuous as vol
from datetime import timedelta
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from homeassistant.const import (CONF_NAME, CONF_URL)
import requests
import json

__version__ = '0.1.0'
_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['requests']

CONF_JSON_ATTR = 'json_attr'
CONF_ATTR_FROM = 'attr_from'
CONF_ATTR_TO = 'attr_to'

DEFAULT_SCAN_INTERVAL = timedelta(hours=2)

SCAN_INTERVAL = timedelta(hours=1)
ICON = 'mdi:rss'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_URL): cv.string,
    vol.Required(CONF_JSON_ATTR): cv.string,
    vol.Optional(CONF_ATTR_FROM, default=1): cv.positive_int,
    vol.Optional(CONF_ATTR_TO, default=10): cv.positive_int,
})


@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    _LOGGER.info("start async_setup_platform JsonParserSensor")
    url = config[CONF_URL]
    name = config[CONF_NAME]
    json_attr = config[CONF_JSON_ATTR]
    attr_from = config[CONF_ATTR_FROM]
    attr_to = config[CONF_ATTR_TO]
    async_add_devices([JsonParserSensor(url, name, json_attr, attr_from, attr_to)], True)


class JsonParserSensor(Entity):
    def __init__(self, url, name, json_attr, attr_from, attr_to):
        self._url = url
        self._name = name
        self._json_attr = json_attr
        self._attr_from = attr_from
        self._attr_to = attr_to

        self._state = None
        self._entries = []

    def update(self):
        _LOGGER.info("sensor JsonParserSensor update from " + self._url)
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
        }
        json_text = requests.get(self._url, headers=header).content
        json_data = json.loads(json_text)
        if json_data[self._json_attr]: #查询成功
            ff = self._attr_from - 1 if self._attr_from > 0 else 0
            tt = self._attr_to if len(json_data[self._json_attr]) > self._attr_to else len(json_data[self._json_attr])
            self._state = tt - ff
            self._entries = []
            for i in range(ff, tt):
                self._entries.append(json_data[self._json_attr][i])

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def device_state_attributes(self):
        return {
            'entries': self._entries
        }
