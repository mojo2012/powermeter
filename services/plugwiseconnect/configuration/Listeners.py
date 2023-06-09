from types import SimpleNamespace

from configuration.HttpClientConfig import HttpClientConfig
from configuration.MqttClientConfig import MqttClientConfig
from configuration.DbClientConfig import DbClientConfig


class Listeners:
    http: HttpClientConfig | None
    mqtt: MqttClientConfig | None
    db: DbClientConfig | None

    def __init__(self, data: SimpleNamespace, rootPath: str):
        if hasattr(data, "http") and data.http:
            self.http = HttpClientConfig(data.http.__dict__)

        if hasattr(data, "mqtt") and data.mqtt:
            self.mqtt = MqttClientConfig(data.mqtt.__dict__)

        if hasattr(data, "db") and data.db:
            self.db = DbClientConfig(rootPath, data.db.__dict__)
