

from datetime import datetime
from enum import Enum
from typing import Union

from broker.SwitchState import SwitchState


class UsageData:
    unix_timestamp: int
    
    power: Union[float, None]
    temperature: Union[float, None]
    switchState: Union[SwitchState, None]
    latestMotion: Union[datetime, None]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def isoTimestamp(self):
        return datetime.fromtimestamp(self.unix_timestamp).isoformat()

    def __str__(self) -> str:
        return self.__dict__.__str__()
    

