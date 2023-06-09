from types import SimpleNamespace
from typing import Union

from configuration.HttpClientConfig import HttpClientConfig
from configuration.MqttClientConfig import MqttClientConfig
from configuration.DbClientConfig import DbClientConfig


class Listeners:
    http: Union[HttpClientConfig, None]
    mqtt: Union[MqttClientConfig, None]
    db: Union[DbClientConfig, None]

    def __init__(self, data: SimpleNamespace, rootPath: str):
        if hasattr(data, "http") and data.http:
            self.http = HttpClientConfig(data.http.__dict__)
        else:
            self.http = None

        if hasattr(data, "mqtt") and data.mqtt:
            self.mqtt = MqttClientConfig(data.mqtt.__dict__)
        else:
            self.mqtt = None

        if hasattr(data, "db") and data.db:
            self.db = DbClientConfig(rootPath, data.db.__dict__)
        else:
            self.db = None
