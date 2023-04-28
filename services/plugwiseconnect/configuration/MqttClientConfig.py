from typing import Dict


class MqttClientConfig:
    host: str
    port: int

    def __init__(self, data: Dict):
        self.__dict__.update(data)
