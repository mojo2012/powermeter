from types import SimpleNamespace

from configuration.HttpClientConfig import HttpClientConfig
from configuration.MqttClientConfig import MqttClientConfig


class Listeners:
    http: HttpClientConfig
    mqtt: MqttClientConfig

    def __init__(self, data: SimpleNamespace):
        if data.http:
            self.http = HttpClientConfig(data.http.__dict__)

        if data.mqtt:
            self.mqtt = MqttClientConfig(data.mqtt.__dict__)
