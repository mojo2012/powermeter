import time
from datetime import datetime
from logging import error
from threading import Thread
from typing import List

from broker.DeviceBroker import DeviceBroker
from broker.UsageData import UsageData
from configuration.Configuration import Configuration
from configuration.DeviceEntry import DeviceEntry
from configuration.DeviceType import DeviceType


class DummyBroker(DeviceBroker):

    _devices: List[DeviceEntry]

    def __init__(self, config: Configuration):
        self._config = config

        self._devices = list(filter(lambda d: d.type == DeviceType.Dummy, self._config.devices))

    def _observeNodes(self):
        while self._started:
            now = time.mktime(datetime.now().timetuple())

            for device in self._config.devices:
                usage = UsageData(unix_timestamp=now, watts_1s=10, watts_8s=10, watts_1h=10, watts_production_1h=0)

                for observer in self._observers:
                    try:
                        observer.onUsageDataUodate(device, usage)
                    except Exception as ex:
                        error(f'Calling objserver {observer} failed: {str(ex)}')

            time.sleep(10)


    def start(self, observeNodes: bool):
        self._started = True

        thread = Thread(target=self._observeNodes)
        thread.start()
