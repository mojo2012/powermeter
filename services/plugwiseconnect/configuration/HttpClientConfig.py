from typing import Dict


class HttpClientConfig:
    url: str
    authorization: str

    def __init__(self, data: Dict):
        self.__dict__.update(data)
