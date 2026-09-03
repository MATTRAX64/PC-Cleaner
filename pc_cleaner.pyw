import os, shutil, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

USELESS_EXT = {".log",".tmp",".temp",".bak",".old",".cache",".chk",".dmp",".err",".swp",".swo",".part",".crash",".trace",".dbg",".~tmp",".~lock",".ilk",".gid",".ncb",".sdf",".idb",".pdb"}
USELESS_NAMES = {"thumbs.db",".ds_store","desktop.ini"}
DEFAULT_EXCLUDES = {"windows"}


def human_size(n):
    for unit in ["o","Ko","Mo","Go","To"]:
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} Po"


def is_useless_file(name):
    n = name.lower()
    return n in USELESS_NAMES or any(n.endswith(e) for e in USELESS_EXT)


def is_empty_file(path):
    try:
        return os.path.getsize(path) == 0
    except OSError:
        return False


def is_excluded(path, excludes):
    parts = {p.lower() for p in path.split(os.sep)}
    return any(ex.lower() in parts for ex in excludes)


def file_age_days(path):
    try:
        return (time.time() - os.path.getmtime(path)) / 86400
    except OSError:
        return 0


class Stats:
    def __init__(self):
        self.files_removed = 0
        self.dirs_removed = 0
        self.bytes_freed = 0
        self.errors = 0
        self.scanned = 0

    def summary(self):
        return (f"Fichiers supprimés : {self.files_removed}\n"
                f"Dossiers supprimés : {self.dirs_removed}\n"
                f"Espace libéré      : {human_size(self.bytes_freed)}\n"
                f"Éléments scannés   : {self.scanned}\n"
                f"Erreurs            : {self.errors}")


def scan_dir(root, files, min_age_days):
    useless_files, kept_files = [], []
    for f in files:
        path = os.path.join(root, f)
        try:
            useless = is_useless_file(f) or is_empty_file(path)
            if useless and file_age_days(path) >= min_age_days:
                size = os.path.getsize(path) if os.path.exists(path) else 0
                useless_files.append((path, size))
            else:
                kept_files.append(f)
        except OSError:
            kept_files.append(f)
    return root, useless_files, kept_files


def clean(base, log_cb, stats, dry_run=False, excludes=None, min_age_days=0,
          min_size_mb=0, max_workers=8, stop_flag=None):

    excludes = excludes or set()
    base = os.path.abspath(base)
    if not os.path.isdir(base):
        log_cb(f"[SKIP] Chemin invalide : {base}")
        return

    log_cb(f"📂 Analyse de : {base}")
    if dry_run:
        log_cb("⚠️  Mode simulation (dry-run)")

    min_size_bytes = min_size_mb * 1024 * 1024

    walk_list = []
    for root, dirs, files in os.walk(base, topdown=True):
        if is_excluded(root, excludes | DEFAULT_EXCLUDES):
            dirs[:] = []
            continue
        walk_list.append((root, dirs, files))

    dir_had_subdirs = {root: bool(dirs) for root, dirs, files in walk_list}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(scan_dir, root, files, min_age_days): root
            for root, dirs, files in walk_list
        }

        fully_useless_dirs = set()

        for future in as_completed(futures):
            if stop_flag and stop_flag.is_set():
                break
            root, useless_files, kept_files = future.result()
            stats.scanned += len(useless_files) + len(kept_files)

            if not kept_files and not dir_had_subdirs.get(root) and useless_files and root != base:
                fully_useless_dirs.add(root)
                continue

            for path, size in useless_files:
                try:
                    if min_size_bytes > 0 and size >= min_size_bytes:
                        log_cb(f"[GROS FICHIER INUTILE] {path} ({human_size(size)})")
                    if dry_run:
                        log_cb(f"[DRY-RUN][FILE] {path} ({human_size(size)})")
                    else:
                        os.remove(path)
                        log_cb(f"[FILE REMOVED] {path} ({human_size(size)})")
                    stats.files_removed += 1
                    stats.bytes_freed += size
                except Exception as e:
                    stats.errors += 1
                    log_cb(f"[ERROR] {path} -> {e}")

    for root in sorted(fully_useless_dirs, key=len, reverse=True):
        if not os.path.isdir(root):
            continue
        try:
            dir_size = sum(
                os.path.getsize(os.path.join(dp, fn))
                for dp, _, fnames in os.walk(root)
                for fn in fnames if os.path.exists(os.path.join(dp, fn))
            )
            if dry_run:
                log_cb(f"[DRY-RUN][DIR 100% inutile] {root} ({human_size(dir_size)})")
            else:
                shutil.rmtree(root)
                log_cb(f"[DIR REMOVED] {root} ({human_size(dir_size)})")
            stats.dirs_removed += 1
            stats.bytes_freed += dir_size
        except Exception as e:
            stats.errors += 1
            log_cb(f"[DIR ERROR] {root} -> {e}")

    for root, dirs, files in reversed(walk_list):
        if root in fully_useless_dirs or not os.path.isdir(root):
            continue
        try:
            if not dry_run and not os.listdir(root) and root != base:
                os.rmdir(root)
                log_cb(f"[EMPTY DIR REMOVED] {root}")
                stats.dirs_removed += 1
        except Exception:
            pass


TRANSLATIONS = {
    "fr": {
        "title": "🧹 PC Cleaner",
        "no_folder": "Aucun dossier sélectionné",
        "choose_folder": "📁 Choisir un dossier",
        "clean_btn": "🧹 Nettoyer",
        "ready_choose": "Choisis un dossier pour commencer",
        "ready_clean": "Prêt à nettoyer",
        "cleaning": "Nettoyage en cours...",
        "done_status": "✅ Terminé : {files} fichiers et {dirs} dossiers vides supprimés ({size} libérés)",
        "done_title": "PC Cleaner",
        "done_msg": "Nettoyage terminé.\n\nFichiers log, vides et temporaires supprimés : {files}\nDossiers vides supprimés : {dirs}\nEspace libéré : {size}",
        "lang_title": "Choisir la langue",
        "lang_prompt": "Choisis ta langue :",
        "continue": "Continuer",
    },
    "en": {
        "title": "🧹 PC Cleaner",
        "no_folder": "No folder selected",
        "choose_folder": "📁 Choose a folder",
        "clean_btn": "🧹 Clean",
        "ready_choose": "Choose a folder to get started",
        "ready_clean": "Ready to clean",
        "cleaning": "Cleaning in progress...",
        "done_status": "✅ Done: {files} files and {dirs} empty folders removed ({size} freed)",
        "done_title": "PC Cleaner",
        "done_msg": "Cleanup complete.\n\nLog, empty and temp files removed: {files}\nEmpty folders removed: {dirs}\nSpace freed: {size}",
        "lang_title": "Select language",
        "lang_prompt": "Choose your language:",
        "continue": "Continue",
    },
    "es": {
        "title": "🧹 PC Cleaner",
        "no_folder": "Ninguna carpeta seleccionada",
        "choose_folder": "📁 Elegir carpeta",
        "clean_btn": "🧹 Limpiar",
        "ready_choose": "Elige una carpeta para empezar",
        "ready_clean": "Listo para limpiar",
        "cleaning": "Limpieza en curso...",
        "done_status": "✅ Listo: {files} archivos y {dirs} carpetas vacías eliminadas ({size} liberados)",
        "done_title": "PC Cleaner",
        "done_msg": "Limpieza completada.\n\nArchivos log, vacíos y temporales eliminados: {files}\nCarpetas vacías eliminadas: {dirs}\nEspacio liberado: {size}",
        "lang_title": "Seleccionar idioma",
        "lang_prompt": "Elige tu idioma:",
        "continue": "Continuar",
    },
    "de": {
        "title": "🧹 PC Cleaner",
        "no_folder": "Kein Ordner ausgewählt",
        "choose_folder": "📁 Ordner wählen",
        "clean_btn": "🧹 Bereinigen",
        "ready_choose": "Wähle einen Ordner, um zu starten",
        "ready_clean": "Bereit zum Bereinigen",
        "cleaning": "Bereinigung läuft...",
        "done_status": "✅ Fertig: {files} Dateien und {dirs} leere Ordner entfernt ({size} freigegeben)",
        "done_title": "PC Cleaner",
        "done_msg": "Bereinigung abgeschlossen.\n\nLog-, leere und temporäre Dateien entfernt: {files}\nLeere Ordner entfernt: {dirs}\nFreigegebener Speicher: {size}",
        "lang_title": "Sprache wählen",
        "lang_prompt": "Wähle deine Sprache:",
        "continue": "Weiter",
    },
}


class LanguageDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = "en"
        self.title("Language")
        self.geometry("300x200")
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="🌐 Choose your language\nChoisir la langue", font=("Segoe UI", 11, "bold")).pack(pady=15)

        options = [("Français", "fr"), ("English", "en"), ("Español", "es"), ("Deutsch", "de")]
        for label, code in options:
            tk.Button(self, text=label, width=20, command=lambda c=code: self._select(c)).pack(pady=3)

        self.protocol("WM_DELETE_WINDOW", lambda: self._select("en"))

    def _select(self, code):
        self.result = code
        self.destroy()


class CleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        lang_dialog = LanguageDialog(root)
        root.wait_window(lang_dialog)
        self.lang = lang_dialog.result
        self.t = TRANSLATIONS[self.lang]
        self.root.deiconify()

        self.root.title(self.t["title"])
        self.root.geometry("480x320")
        self.root.resizable(False, False)

        self.folder = tk.StringVar(value=self.t["no_folder"])
        self.stop_flag = threading.Event()

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text=self.t["title"], font=("Segoe UI", 16, "bold")).pack(pady=(0, 15))

        tk.Label(frame, textvariable=self.folder, wraplength=420, fg="#555").pack(pady=(0, 10))

        tk.Button(frame, text=self.t["choose_folder"], font=("Segoe UI", 10),
                  command=self.choose_folder).pack(pady=5)

        self.start_btn = tk.Button(frame, text=self.t["clean_btn"], font=("Segoe UI", 12, "bold"),
                                    bg="#4CAF50", fg="white", width=20, height=2,
                                    command=self.start_clean, state="disabled")
        self.start_btn.pack(pady=15)

        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=5)

        self.status = tk.Label(frame, text=self.t["ready_choose"], fg="#777")
        self.status.pack(pady=(10, 0))

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_path = folder
            self.folder.set(folder)
            self.start_btn.config(state="normal")
            self.status.config(text=self.t["ready_clean"])

    def start_clean(self):
        self.start_btn.config(state="disabled")
        self.progress.start(10)
        self.status.config(text=self.t["cleaning"])

        def run():
            stats = Stats()
            clean(self.selected_path, lambda m: None, stats, dry_run=False,
                  excludes=set(), min_age_days=0, min_size_mb=0,
                  max_workers=8, stop_flag=self.stop_flag)
            self.root.after(0, lambda: self._on_finished(stats))

        threading.Thread(target=run, daemon=True).start()

    def _on_finished(self, stats):
        self.progress.stop()
        self.start_btn.config(state="normal")
        size = human_size(stats.bytes_freed)
        self.status.config(text=self.t["done_status"].format(files=stats.files_removed, dirs=stats.dirs_removed, size=size))
        messagebox.showinfo(
            self.t["done_title"],
            self.t["done_msg"].format(files=stats.files_removed, dirs=stats.dirs_removed, size=size)
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = CleanerApp(root)
    root.mainloop()
