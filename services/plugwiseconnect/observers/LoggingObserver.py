from logging import info

from broker.Observer import Observer
from broker.UsageData import UsageData
from configuration.DeviceEntry import DeviceEntry


class LoggingObserver(Observer):

    def onUsageDataUodate(self, device: DeviceEntry, usageData: UsageData):
        watts = "{:.2f} W".format(usageData.watts_1s)
        info(f'Power usage for {device.name} ({device.macAddress}): {watts}')
