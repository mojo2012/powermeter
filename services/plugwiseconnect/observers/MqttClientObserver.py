from logging import debug

from broker.Observer import Observer
from broker.UsageData import UsageData
from configuration.DeviceEntry import DeviceEntry
from configuration.MqttClientConfig import MqttClientConfig


class MqttClientObserver(Observer):

    _host: str
    _port: str

    def __init__(self, httpConfig: MqttClientConfig):
        self._host = httpConfig.host
        self._port = httpConfig.port

    def onUsageDataUodate(self, device: DeviceEntry, usageData: UsageData):
        debug(f'Power usage for {device.name} ({device.macAddress}): {usageData}')

