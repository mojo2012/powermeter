

from datetime import datetime


class UsageData:
    unix_timestamp: int
    
    watts_1s: float
    watts_8s: float
    watts_1h: float
    watts_production_1h: float
    # pulse_1s: float
    # pulse_8s: float
    # pulse_1h: float
    # pulse_production_1h: float

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        pass

    def isoTimestamp(self):
        return datetime.fromtimestamp(self.unix_timestamp).isoformat()

    def __str__(self) -> str:
        return self.__dict__.__str__()
