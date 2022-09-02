from typing import Dict


class MqttClientConfig:
    host: str
    port: str

    def __init__(self, data: Dict):
        self.__dict__.update(data)
