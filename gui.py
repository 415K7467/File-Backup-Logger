import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Callable, List, Optional

from backup import BackupManager, BackupResult
from config import BackupConfig
from logger import BackupLogger


class BackupGUI:
    def __init__(self, root: tk.Tk, config: BackupConfig, manager: BackupManager, logger: BackupLogger):
        self.root = root
        self.config = config
        self.manager = manager
        self.logger = logger

        self.root.title("File Backup Logger")
        self.root.resizable(True, True)
        self.root.minsize(700, 550)

        self._build_ui()
        self._load_config_into_ui()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(self.root)
        notebook.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self._build_backup_tab(notebook)
        self._build_log_tab(notebook)
        self._build_settings_tab(notebook)

    # ── Backup tab ────────────────────────────────────────────────────────────

    def _build_backup_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Backup")
        frame.columnconfigure(0, weight=1)

        # Source folders
        src_lf = ttk.LabelFrame(frame, text="Source Folders")
        src_lf.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))
        src_lf.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.src_listbox = tk.Listbox(src_lf, selectmode=tk.EXTENDED, height=6)
        self.src_listbox.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        src_lf.rowconfigure(0, weight=1)

        sb = ttk.Scrollbar(src_lf, orient=tk.VERTICAL, command=self.src_listbox.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.src_listbox.configure(yscrollcommand=sb.set)

        src_btn_frame = ttk.Frame(src_lf)
        src_btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 4))
        ttk.Button(src_btn_frame, text="Add Folder", command=self._add_source).pack(side=tk.LEFT, padx=2)
        ttk.Button(src_btn_frame, text="Remove Selected", command=self._remove_source).pack(side=tk.LEFT, padx=2)

        # Destination folder
        dst_lf = ttk.LabelFrame(frame, text="Destination Folder")
        dst_lf.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        dst_lf.columnconfigure(0, weight=1)

        self.dst_var = tk.StringVar()
        ttk.Entry(dst_lf, textvariable=self.dst_var).grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        ttk.Button(dst_lf, text="Browse…", command=self._browse_destination).grid(row=0, column=1, padx=4, pady=4)

        # Options
        opt_lf = ttk.LabelFrame(frame, text="Options")
        opt_lf.grid(row=2, column=0, sticky="ew", padx=8, pady=4)

        self.zip_var = tk.BooleanVar()
        ttk.Checkbutton(opt_lf, text="Use ZIP compression", variable=self.zip_var).pack(anchor=tk.W, padx=6, pady=4)

        # Run button + progress
        action_frame = ttk.Frame(frame)
        action_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=(4, 8))
        action_frame.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(action_frame, mode="indeterminate")
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ttk.Button(action_frame, text="Run Backup", command=self._run_backup).grid(row=0, column=1)

        # Status label
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(frame, textvariable=self.status_var, anchor=tk.W).grid(
            row=4, column=0, sticky="ew", padx=8, pady=(0, 4)
        )

    # ── Log tab ───────────────────────────────────────────────────────────────

    def _build_log_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Log")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(frame, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        ttk.Button(frame, text="Refresh", command=self._refresh_log).grid(row=1, column=0, pady=(0, 8))

    # ── Settings tab ──────────────────────────────────────────────────────────

    def _build_settings_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Settings")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Log file path:").grid(row=0, column=0, sticky=tk.W, padx=8, pady=8)
        self.log_path_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.log_path_var).grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=8)

        ttk.Label(frame, text="Auto-backup interval (minutes, 0 = off):").grid(
            row=1, column=0, sticky=tk.W, padx=8, pady=4
        )
        self.interval_var = tk.IntVar()
        ttk.Spinbox(frame, from_=0, to=10080, textvariable=self.interval_var, width=8).grid(
            row=1, column=1, sticky=tk.W, padx=(0, 8), pady=4
        )

        ttk.Button(frame, text="Save Settings", command=self._save_settings).grid(
            row=2, column=0, columnspan=2, pady=16
        )

    # ── Config helpers ────────────────────────────────────────────────────────

    def _load_config_into_ui(self) -> None:
        for folder in self.config.source_folders:
            self.src_listbox.insert(tk.END, folder)
        self.dst_var.set(self.config.destination_folder)
        self.zip_var.set(self.config.use_compression)
        self.log_path_var.set(self.config.log_file)
        self.interval_var.set(self.config.backup_interval_minutes)
        self._refresh_log()

    def _save_settings(self) -> None:
        self.config.log_file = self.log_path_var.get().strip()
        self.config.backup_interval_minutes = self.interval_var.get()
        self.logger.log_path = self.config.log_file
        self._persist_config()
        messagebox.showinfo("Settings", "Settings saved.")

    def _persist_config(self) -> None:
        self.config.source_folders = list(self.src_listbox.get(0, tk.END))
        self.config.destination_folder = self.dst_var.get().strip()
        self.config.use_compression = self.zip_var.get()
        self.config.save()

    # ── Source folder actions ─────────────────────────────────────────────────

    def _add_source(self) -> None:
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.src_listbox.insert(tk.END, folder)
            self._persist_config()

    def _remove_source(self) -> None:
        for index in reversed(self.src_listbox.curselection()):
            self.src_listbox.delete(index)
        self._persist_config()

    def _browse_destination(self) -> None:
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dst_var.set(folder)
            self._persist_config()

    # ── Backup execution ──────────────────────────────────────────────────────

    def _run_backup(self) -> None:
        sources = list(self.src_listbox.get(0, tk.END))
        destination = self.dst_var.get().strip()
        use_zip = self.zip_var.get()

        if not sources:
            messagebox.showwarning("No Sources", "Please add at least one source folder.")
            return
        if not destination:
            messagebox.showwarning("No Destination", "Please select a destination folder.")
            return

        self._persist_config()
        self.status_var.set("Running backup…")
        self.progress.start(10)

        thread = threading.Thread(
            target=self._run_backup_thread,
            args=(sources, destination, use_zip),
            daemon=True,
        )
        thread.start()

    def _run_backup_thread(self, sources: List[str], destination: str, use_zip: bool) -> None:
        results = self.manager.backup_multiple(sources, destination, use_zip)
        self.root.after(0, self._on_backup_done, results)

    def _on_backup_done(self, results: List[BackupResult]) -> None:
        self.progress.stop()
        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count
        self.status_var.set(
            f"Done. {success_count} succeeded, {fail_count} failed. "
            f"Total files: {sum(r.file_count for r in results)}."
        )
        self._refresh_log()

        if fail_count:
            errors = "\n".join(r.error_message or "" for r in results if not r.success)
            messagebox.showerror("Backup Errors", f"{fail_count} backup(s) failed:\n{errors}")
        else:
            messagebox.showinfo("Backup Complete", f"All {success_count} backup(s) completed successfully.")

    # ── Log helpers ───────────────────────────────────────────────────────────

    def _refresh_log(self) -> None:
        contents = self.logger.get_log_contents()
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, contents if contents else "(No log entries yet.)")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
