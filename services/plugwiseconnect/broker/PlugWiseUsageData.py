

from datetime import datetime
from enum import Enum
from typing import Union

from broker.SwitchState import SwitchState


class PlugWiseUsageData:
    unix_timestamp: int
    
    watts_1s: float
    watts_8s: float
    watts_1h: float
    watts_production_1h: float

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def isoTimestamp(self):
        return datetime.fromtimestamp(self.unix_timestamp).isoformat()

    def __str__(self) -> str:
        return self.__dict__.__str__()
    

