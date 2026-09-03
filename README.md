# 🧹 PC Cleaner

**[Français](#français) | [English](#english) | [Español](#español) | [Deutsch](#deutsch)**

---

## Français

Outil simple pour nettoyer un dossier (ou un disque entier) des fichiers inutiles : logs, fichiers temporaires, fichiers vides, dossiers vides.

**Stack :** Python 3, Tkinter, `concurrent.futures.ThreadPoolExecutor`. Un seul fichier `pc_cleaner.pyw`, zéro dépendance externe.

### Ce qu'il fait
- Scan multi-thread d'un dossier donné
- Supprime : `.log .tmp .bak .old .cache .dmp .swp` etc., `thumbs.db`, `desktop.ini`, tout fichier de 0 octet
- Supprime les dossiers vides après nettoyage
- Détecte les dossiers 100% composés de fichiers inutiles et les détruit en un seul `rmtree` (plus rapide que fichier par fichier)
- Exclut automatiquement `Windows` du scan

### Lancer
```bash
python pc_cleaner.pyw
# ou double-clic si Python est associé aux .pyw
```
Aucune install requise (Tkinter est fourni avec Python).

### Structure du code
- `is_useless_file()` / `is_empty_file()` : détection des fichiers ciblés
- `scan_dir()` : worker de thread, analyse un dossier
- `clean()` : orchestration du scan multi-thread + suppression
- `CleanerApp` : GUI Tkinter

---

## English

Simple tool to clean a folder (or a whole drive) of useless files: logs, temp files, empty files, empty folders.

**Stack:** Python 3, Tkinter, `concurrent.futures.ThreadPoolExecutor`. Single file `pc_cleaner.pyw`, zero external dependencies.

### What it does
- Multi-threaded scan of a given folder
- Deletes: `.log .tmp .bak .old .cache .dmp .swp` etc., `thumbs.db`, `desktop.ini`, any 0-byte file
- Removes empty folders after cleanup
- Detects folders made entirely of useless files and deletes them in a single `rmtree` (faster than file-by-file)
- Automatically excludes `Windows` from the scan

### Run
```bash
python pc_cleaner.pyw
# or double-click if Python is associated with .pyw files
```
No install required (Tkinter ships with Python).

### Code structure
- `is_useless_file()` / `is_empty_file()`: target file detection
- `scan_dir()`: thread worker, scans one folder
- `clean()`: orchestrates the multi-threaded scan + deletion
- `CleanerApp`: Tkinter GUI

---

## Español

Herramienta simple para limpiar una carpeta (o un disco entero) de archivos inútiles: logs, archivos temporales, archivos vacíos, carpetas vacías.

**Stack:** Python 3, Tkinter, `concurrent.futures.ThreadPoolExecutor`. Un solo archivo `pc_cleaner.pyw`, sin dependencias externas.

### Qué hace
- Escaneo multi-hilo de una carpeta dada
- Elimina: `.log .tmp .bak .old .cache .dmp .swp` etc., `thumbs.db`, `desktop.ini`, cualquier archivo de 0 bytes
- Elimina carpetas vacías tras la limpieza
- Detecta carpetas compuestas únicamente por archivos inútiles y las elimina de una vez con `rmtree` (más rápido que archivo por archivo)
- Excluye automáticamente `Windows` del escaneo

### Ejecutar
```bash
python pc_cleaner.pyw
# o doble clic si Python está asociado a los .pyw
```
No requiere instalación (Tkinter viene incluido con Python).

### Estructura del código
- `is_useless_file()` / `is_empty_file()`: detección de archivos objetivo
- `scan_dir()`: worker de hilo, escanea una carpeta
- `clean()`: orquesta el escaneo multi-hilo + eliminación
- `CleanerApp`: GUI Tkinter

---

## Deutsch

Einfaches Tool zum Bereinigen eines Ordners (oder eines ganzen Laufwerks) von nutzlosen Dateien: Logs, temporäre Dateien, leere Dateien, leere Ordner.

**Stack:** Python 3, Tkinter, `concurrent.futures.ThreadPoolExecutor`. Einzelne Datei `pc_cleaner.pyw`, keine externen Abhängigkeiten.

### Was es macht
- Multi-Thread-Scan eines angegebenen Ordners
- Löscht: `.log .tmp .bak .old .cache .dmp .swp` usw., `thumbs.db`, `desktop.ini`, jede 0-Byte-Datei
- Entfernt leere Ordner nach der Bereinigung
- Erkennt Ordner, die vollständig aus nutzlosen Dateien bestehen, und löscht sie in einem einzigen `rmtree` (schneller als Datei für Datei)
- Schließt `Windows` automatisch vom Scan aus

### Ausführen
```bash
python pc_cleaner.pyw
# oder Doppelklick, wenn Python mit .pyw-Dateien verknüpft ist
```
Keine Installation nötig (Tkinter ist bei Python bereits enthalten).

### Code-Struktur
- `is_useless_file()` / `is_empty_file()`: Erkennung der Zieldateien
- `scan_dir()`: Thread-Worker, scannt einen Ordner
- `clean()`: orchestriert Multi-Thread-Scan + Löschung
- `CleanerApp`: Tkinter-GUI
