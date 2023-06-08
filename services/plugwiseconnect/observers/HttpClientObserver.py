from logging import debug

import requests

from broker.Observer import Observer
from broker.UsageData import UsageData
from configuration.DeviceEntry import DeviceEntry
from configuration.HttpClientConfig import HttpClientConfig


class HttpClientObserver(Observer):

    _url: str
    _authentication: str

    def __init__(self, httpConfig: HttpClientConfig):
        self._url = httpConfig.url
        self._authentication = httpConfig.authorization

    def onUsageDataUpdate(self, device: DeviceEntry, usageData: UsageData):
        debug(f'Power usage for {device.name} ({device.address}): {usageData}')

        response = requests.post(url=self._url, headers={"Authorization": self._authentication}, data=usageData.__dict__)

        debug(f'Got response: {str(response)}')
