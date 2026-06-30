import os
from datetime import datetime
from typing import Optional


class BackupLogger:
    def __init__(self, log_path: str = "backup.log"):
        self.log_path = log_path

    def _write(self, level: str, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line)

    def info(self, message: str) -> None:
        self._write("INFO", message)

    def warning(self, message: str) -> None:
        self._write("WARNING", message)

    def error(self, message: str) -> None:
        self._write("ERROR", message)

    def log_backup_start(self, source: str, destination: str, compressed: bool) -> None:
        mode = "ZIP" if compressed else "COPY"
        self.info(f"Backup started | Source: {source} | Destination: {destination} | Mode: {mode}")

    def log_backup_result(
        self,
        source: str,
        destination: str,
        file_count: int,
        duration_seconds: float,
        success: bool,
        error_msg: Optional[str] = None,
    ) -> None:
        status = "SUCCESS" if success else "FAILURE"
        if success:
            self.info(
                f"Backup {status} | Source: {source} | Destination: {destination} "
                f"| Files: {file_count} | Duration: {duration_seconds:.2f}s"
            )
        else:
            self.error(
                f"Backup {status} | Source: {source} | Destination: {destination} "
                f"| Files: {file_count} | Duration: {duration_seconds:.2f}s | Error: {error_msg}"
            )

    def get_log_contents(self) -> str:
        if not os.path.exists(self.log_path):
            return ""
        with open(self.log_path, "r", encoding="utf-8") as f:
            return f.read()
