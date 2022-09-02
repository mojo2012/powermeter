from abc import abstractmethod

from broker import UsageData
from configuration.DeviceEntry import DeviceEntry


class Observer:

    @abstractmethod
    def onUsageDataUodate(self, device: DeviceEntry, usageData: UsageData):
        pass
