import json
import os
import re
import shutil
import time
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

from logger import BackupLogger


@dataclass
class BackupResult:
    source: str
    destination: str
    file_count: int
    duration_seconds: float
    success: bool
    error_message: Optional[str] = None
    compressed: bool = False


def _detect_version(folder: str) -> Optional[str]:
    """Try to detect a version string from common version files in a folder."""
    candidates = [
        ("package.json", lambda d: d.get("version")),
        ("setup.cfg", None),
        ("pyproject.toml", None),
        (".version", None),
        ("VERSION", None),
        ("version.txt", None),
    ]

    for filename, extractor in candidates:
        path = os.path.join(folder, filename)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if extractor:
                data = json.loads(content)
                version = extractor(data)
                if version:
                    return _sanitize_version(str(version))
            else:
                match = re.search(r"\bversion\s*[=:]\s*[\"']?([\d][^\s\"',]+)", content, re.IGNORECASE)
                if match:
                    return _sanitize_version(match.group(1))
        except Exception:
            continue
    return None


def _sanitize_version(version: str) -> str:
    """Replace dots with dashes so the version is safe in folder/file names."""
    return re.sub(r"[^\w\-]", "-", version)


def _build_backup_name(source: str, timestamp: str, version: Optional[str]) -> str:
    folder_name = os.path.basename(os.path.normpath(source))
    if version:
        return f"{folder_name}_backup_{timestamp}_v{version}"
    return f"{folder_name}_backup_{timestamp}"


def _count_files(path: str) -> int:
    total = 0
    for _, _, files in os.walk(path):
        total += len(files)
    return total


class BackupManager:
    def __init__(self, logger: BackupLogger):
        self.logger = logger

    def backup(
        self,
        source: str,
        destination_root: str,
        use_compression: bool = False,
    ) -> BackupResult:
        source = os.path.normpath(source)
        destination_root = os.path.normpath(destination_root)

        if not os.path.exists(source):
            msg = f"Source folder does not exist: {source}"
            self.logger.error(msg)
            return BackupResult(source, destination_root, 0, 0.0, False, msg, use_compression)

        if not os.path.isdir(source):
            msg = f"Source path is not a directory: {source}"
            self.logger.error(msg)
            return BackupResult(source, destination_root, 0, 0.0, False, msg, use_compression)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        version = _detect_version(source)
        backup_name = _build_backup_name(source, timestamp, version)

        self.logger.log_backup_start(source, destination_root, use_compression)

        start = time.time()
        file_count = 0

        try:
            os.makedirs(destination_root, exist_ok=True)

            if use_compression:
                destination, file_count = self._backup_zip(source, destination_root, backup_name)
            else:
                destination, file_count = self._backup_copy(source, destination_root, backup_name)

        except PermissionError as e:
            duration = time.time() - start
            msg = f"Permission denied: {e}"
            self.logger.log_backup_result(source, destination_root, file_count, duration, False, msg)
            return BackupResult(source, destination_root, file_count, duration, False, msg, use_compression)
        except OSError as e:
            duration = time.time() - start
            msg = f"OS error: {e}"
            self.logger.log_backup_result(source, destination_root, file_count, duration, False, msg)
            return BackupResult(source, destination_root, file_count, duration, False, msg, use_compression)

        duration = time.time() - start
        self.logger.log_backup_result(source, destination, file_count, duration, True)
        return BackupResult(source, destination, file_count, duration, True, compressed=use_compression)

    def _backup_copy(self, source: str, destination_root: str, backup_name: str) -> Tuple[str, int]:
        destination = os.path.join(destination_root, backup_name)
        shutil.copytree(source, destination)
        file_count = _count_files(destination)
        return destination, file_count

    def _backup_zip(self, source: str, destination_root: str, backup_name: str) -> Tuple[str, int]:
        zip_path = os.path.join(destination_root, backup_name + ".zip")
        file_count = 0
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, _, filenames in os.walk(source):
                for filename in filenames:
                    file_abs = os.path.join(dirpath, filename)
                    arcname = os.path.relpath(file_abs, os.path.dirname(source))
                    zf.write(file_abs, arcname)
                    file_count += 1
        return zip_path, file_count

    def backup_multiple(
        self,
        sources: List[str],
        destination_root: str,
        use_compression: bool = False,
    ) -> List[BackupResult]:
        results = []
        for source in sources:
            result = self.backup(source, destination_root, use_compression)
            results.append(result)
        return results
