from typing import List

from broker.Observer import Observer
from configuration.Configuration import Configuration


class DeviceBroker():

    _config: Configuration
    _observers: List[Observer] = []

    _started = False

    def __init__(self, config: Configuration):
        self._config = config

    def start(self, observeNodes: bool):
        """
        Starts reading data from the connected devices
        """

    def stop(self):
        self._started = False

    def registerObserver(self, observer: Observer):
        self._observers.append(observer)
