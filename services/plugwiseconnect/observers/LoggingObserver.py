from logging import info

from broker.Observer import Observer
from broker.UsageData import UsageData
from configuration.DeviceEntry import DeviceEntry


class LoggingObserver(Observer):

    def onUsageDataUpdate(self, device: DeviceEntry, usageData: UsageData):
        info(f'Usage for {device.name} ({device.address}): {usageData}')
