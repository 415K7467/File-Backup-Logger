import json
import os
from typing import List, Optional


DEFAULT_CONFIG = {
    "source_folders": [],
    "destination_folder": "",
    "use_compression": False,
    "backup_interval_minutes": 0,
    "log_file": "backup.log",
}

CONFIG_FILE = "backup_config.json"


class BackupConfig:
    def __init__(self, config_path: str = CONFIG_FILE):
        self.config_path = config_path
        self._data: dict = {}
        self.load()

    def load(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data = {**DEFAULT_CONFIG, **loaded}
            except (json.JSONDecodeError, OSError):
                self._data = DEFAULT_CONFIG.copy()
        else:
            self._data = DEFAULT_CONFIG.copy()

    def save(self) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=4)

    @property
    def source_folders(self) -> List[str]:
        return self._data["source_folders"]

    @source_folders.setter
    def source_folders(self, value: List[str]) -> None:
        self._data["source_folders"] = value

    @property
    def destination_folder(self) -> str:
        return self._data["destination_folder"]

    @destination_folder.setter
    def destination_folder(self, value: str) -> None:
        self._data["destination_folder"] = value

    @property
    def use_compression(self) -> bool:
        return self._data["use_compression"]

    @use_compression.setter
    def use_compression(self, value: bool) -> None:
        self._data["use_compression"] = value

    @property
    def backup_interval_minutes(self) -> int:
        return self._data["backup_interval_minutes"]

    @backup_interval_minutes.setter
    def backup_interval_minutes(self, value: int) -> None:
        self._data["backup_interval_minutes"] = value

    @property
    def log_file(self) -> str:
        return self._data["log_file"]

    @log_file.setter
    def log_file(self, value: str) -> None:
        self._data["log_file"] = value
