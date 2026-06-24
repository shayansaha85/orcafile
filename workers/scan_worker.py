import os

from PyQt6.QtCore import QThread, pyqtSignal


class ScanWorker(QThread):
    """Background worker thread that scans a directory and groups files by extension."""

    finished = pyqtSignal(dict)
    progress = pyqtSignal(int, int)
    status = pyqtSignal(str)

    def __init__(self, target_dir):
        super().__init__()
        self.target_dir = target_dir
        self._is_running = True

    def run(self):
        self.status.emit("CALCULATING TOTAL SIZE...")
        total_files = 0

        for root, _, files in os.walk(self.target_dir):
            if not self._is_running:
                return
            total_files += len(files)

        if total_files == 0:
            self.finished.emit({})
            return

        self.status.emit("INDEXING...")
        groups = {}
        processed_files = 0

        for root_path, _, files in os.walk(self.target_dir):
            if not self._is_running:
                break

            for file in files:
                if not self._is_running:
                    break
                full_path = os.path.join(root_path, file)
                _, ext = os.path.splitext(file)
                ext = ext.lower().strip() if ext else "no extension"

                if ext not in groups:
                    groups[ext] = []
                groups[ext].append((file, full_path))

                processed_files += 1

                if processed_files % 100 == 0 or processed_files == total_files:
                    self.progress.emit(processed_files, total_files)

        self.finished.emit(groups if self._is_running else {})

    def stop(self):
        self._is_running = False
