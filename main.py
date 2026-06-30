import tkinter as tk

from backup import BackupManager
from config import BackupConfig
from gui import BackupGUI
from logger import BackupLogger


def main() -> None:
    config = BackupConfig()
    logger = BackupLogger(log_path=config.log_file)
    manager = BackupManager(logger=logger)

    root = tk.Tk()
    BackupGUI(root, config, manager, logger)
    root.mainloop()


if __name__ == "__main__":
    main()
