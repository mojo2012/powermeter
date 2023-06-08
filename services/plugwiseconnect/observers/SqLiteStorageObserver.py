import os
from logging import debug
from pathlib import Path

from sqlite_utils import Database

from broker.Observer import Observer
from broker.UsageData import UsageData
from configuration.DeviceEntry import DeviceEntry


class SqLiteStorageObserver(Observer):

    _storage_location: str
    _db: Database

    def __init__(self, storageLocation: str):
        self._storage_location = storageLocation

        folderPath = Path(storageLocation).parent.absolute();
        
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        self._db = Database(storageLocation, recreate=True)

    def onUsageDataUpdate(self, device: DeviceEntry, usageData: UsageData):
        debug(f'Power usage for {device.name} ({device.address}): {usageData}')

        self._db["usage_data"].insert_all(  # type: ignore
            [{
                "device_mac": device.address,
                "timestamp": usageData.isoTimestamp,
                "watts": usageData.power,
            }],
            pk=["timestamp", "device_mac"])  # type: ignore
