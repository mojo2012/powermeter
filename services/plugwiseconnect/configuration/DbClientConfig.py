import os
from pathlib import Path
from typing import Dict


class DbClientConfig:
    _rootPath: str

    storageLocation: str

    def __init__(self, rootPath: str, data: Dict):
        self._rootPath = rootPath
        self.__dict__.update(data)

        storageLocation: str = self.storageLocation

        if storageLocation:
            if storageLocation.startswith("."):
                storageLocation = os.path.join(self._rootPath, Path(storageLocation))

            self.storageLocation = str(
                Path(os.path.join(Path(storageLocation), Path("usageData.sqlite"))).resolve().absolute())

