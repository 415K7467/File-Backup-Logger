# File Backup Logger

A Python desktop application that backs up files and directories with automatic versioning, ZIP compression, and detailed logging. Built with `tkinter` for the GUI and `shutil`/`zipfile` for backup operations.

---

## Features

- Copy or ZIP-compress folders to a destination of your choice
- Automatic version detection from `package.json`, `setup.cfg`, `VERSION`, etc.
- Timestamped backup folder names (e.g. `myapp_backup_2026-06-30_14-22-01_v2-7-1`)
- Detailed `.log` file — backup time, status, file count, duration
- Persistent settings saved in `backup_config.json`
- Multi-folder backup in one click
- Background execution so the UI stays responsive

---

## Requirements

- Python 3.8+
- No external packages — only the standard library (`tkinter`, `shutil`, `zipfile`, `json`)

---

## Installation

```bash
git clone https://github.com/your-username/File-Backup-Logger.git
cd File-Backup-Logger
python main.py
```

No `pip install` required.

---

## File Structure

```
File-Backup-Logger/
├── main.py                  # Entry point
├── backup.py                # BackupManager — copy/zip logic, version detection
├── config.py                # BackupConfig — loads/saves backup_config.json
├── logger.py                # BackupLogger — writes the .log file
├── gui.py                   # BackupGUI — tkinter interface
├── generate_test_folder.py  # Utility to create a sample folder for testing
├── backup_config.json       # Auto-generated on first run
└── backup.log               # Auto-generated on first backup
```

---

## How to Use

### 1. Launch the app

```bash
python main.py
```

### 2. Add source folders — Backup tab

Click **Add Folder** to open a folder picker. Add as many folders as you want. Use **Remove Selected** to delete entries from the list.

### 3. Choose a destination

Click **Browse…** next to the destination field to pick where backups will be saved.

### 4. Choose compression mode

Tick **Use ZIP compression** to save each backup as a `.zip` archive. Leave it unchecked for a plain folder copy.

### 5. Run the backup

Click **Run Backup**. A progress bar animates while the backup runs in the background. A dialog confirms success or reports any errors when done.

### 6. Check the log

Switch to the **Log** tab and click **Refresh** to see the full log of all backup operations.

### 7. Adjust settings

The **Settings** tab lets you change the log file path and configure an auto-backup interval (stored in `backup_config.json`).

---

## Screenshots

### Backup Tab

![Backup tab](screenshots/Capture%20d'%C3%A9cran%202026-06-30%20150033.png)

### Folder Picker

![Folder picker dialog](screenshots/Capture%20d'%C3%A9cran%202026-06-30%20150120.png)

### Backup Complete

![Backup complete dialog](screenshots/Capture%20d'%C3%A9cran%202026-06-30%20150251.png)

### Log Tab

![Log tab](screenshots/Capture%20d'%C3%A9cran%202026-06-30%20150441.png)

### Settings Tab

![Settings tab](screenshots/Capture%20d'%C3%A9cran%202026-06-30%20150406.png)

---

## Backup Naming Convention

Backup names follow this pattern:

```
<folder-name>_backup_<YYYY-MM-DD>_<HH-MM-SS>[_v<version>]
```

| Example source                                | Detected version | Backup name                                      |
| --------------------------------------------- | ---------------- | ------------------------------------------------ |
| `my-project/` (has `package.json` v2.7.1) | `2.7.1`        | `my-project_backup_2026-06-30_14-22-01_v2-7-1` |
| `photos/` (no version file)                 | —               | `photos_backup_2026-06-30_14-22-01`            |

Version is detected automatically from: `package.json`, `setup.cfg`, `pyproject.toml`, `.version`, `VERSION`, `version.txt`.

---

## Log Format

Each line in `backup.log` follows this format:

```
[YYYY-MM-DD HH:MM:SS] [LEVEL] message
```

Example:

```
[2026-06-30 14:22:01] [INFO] Backup started | Source: C:/my-project | Destination: C:/Backups | Mode: ZIP
[2026-06-30 14:22:03] [INFO] Backup SUCCESS | Source: C:/my-project | Destination: C:/Backups/my-project_backup_2026-06-30_14-22-01_v2-7-1.zip | Files: 42 | Duration: 1.87s
[2026-06-30 14:22:04] [ERROR] Backup FAILURE | Source: C:/missing | Destination: C:/Backups | Files: 0 | Duration: 0.00s | Error: Source folder does not exist: C:/missing
```

---

## Config File

`backup_config.json` is created automatically and updated every time you make a change in the GUI:

```json
{
    "source_folders": [
        "C:/Users/vincent/Documents/my-project"
    ],
    "destination_folder": "C:/Backups",
    "use_compression": true,
    "backup_interval_minutes": 0,
    "log_file": "backup.log"
}
```

---

## Generating a Test Folder

A helper script is included to create a realistic sample folder for testing:

```bash
python generate_test_folder.py
```

This creates `test_project/` with 13 files across nested subdirectories and a `package.json` containing version `2.7.1`, so the backup name will include the detected version.

---

## Development Tasks

- [X] Research `shutil` and create project structure
- [X] Implement folder selection and copy to backup location
- [X] Add timestamp and version to backup folder names
- [X] Add error handling and `.log` file
- [X] Clean up code — split into `backup.py`, `logger.py`, `config.py`
- [X] Add ZIP compression — user chooses plain copy or zip
- [X] Improve log format — file count and duration
- [X] Add `tkinter` GUI
- [X] Add JSON config file for user preferences
- [X] Final testing, README with instructions and screenshots

