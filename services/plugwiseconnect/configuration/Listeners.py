from types import SimpleNamespace

from configuration.HttpClientConfig import HttpClientConfig
from configuration.MqttClientConfig import MqttClientConfig
from configuration.DbClientConfig import DbClientConfig


class Listeners:
    http: HttpClientConfig
    mqtt: MqttClientConfig
    db: DbClientConfig

    def __init__(self, data: SimpleNamespace, rootPath: str):
        if data.http:
            self.http = HttpClientConfig(data.http.__dict__)

        if data.mqtt:
            self.mqtt = MqttClientConfig(data.mqtt.__dict__)

        if data.mqtt:
            self.db = DbClientConfig(rootPath, data.db.__dict__)
