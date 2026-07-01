import os

from PyQt6.QtCore import QThread, pyqtSignal

from ntfs_scanner import scan_ntfs
from ntfs_scanner.volume import is_ntfs
from ntfs_scanner.navigator import find_frn_by_path
from ntfs_scanner.mft import NTFS_ROOT_FRN


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
        drive_part = os.path.splitdrive(self.target_dir)[0]
        drive_letter = drive_part[0] if drive_part else ""

        if drive_letter and is_ntfs(drive_letter):
            try:
                self._run_ntfs(drive_letter)
                return
            except Exception:
                pass  # fall through to os.walk fallback

        self._run_fallback()

    def _run_ntfs(self, drive_letter: str):
        self.status.emit("READING MFT...")
        result = scan_ntfs(drive_letter)

        if not self._is_running:
            self.finished.emit({})
            return

        drive_root = f"{drive_letter}:\\"
        rel_path = os.path.relpath(self.target_dir, drive_root)

        if rel_path == ".":
            start_frn = NTFS_ROOT_FRN
        else:
            start_frn = find_frn_by_path(rel_path, result.nodes, result.children)
            if start_frn is None:
                raise FileNotFoundError(f"Path not found in MFT: {self.target_dir}")

        # Pre-count files in subtree (all in RAM — fast)
        total_files = 0
        stack = [start_frn]
        while stack:
            frn = stack.pop()
            node = result.nodes.get(frn)
            if not node:
                continue
            if not node.is_dir:
                total_files += 1
            stack.extend(result.children.get(frn, []))

        if total_files == 0:
            self.finished.emit({})
            return

        self.status.emit("INDEXING...")
        groups: dict[str, list] = {}
        processed = 0

        stack = [(start_frn, self.target_dir)]
        while stack and self._is_running:
            frn, parent_path = stack.pop()
            for child_frn in result.children.get(frn, []):
                child = result.nodes.get(child_frn)
                if not child:
                    continue
                child_path = os.path.join(parent_path, child.name)

                if child.is_dir:
                    stack.append((child_frn, child_path))
                else:
                    _, ext = os.path.splitext(child.name)
                    ext = ext.lower().strip() if ext else "no extension"
                    groups.setdefault(ext, []).append((child.name, child_path, child.size))

                    processed += 1
                    if processed % 100 == 0 or processed == total_files:
                        self.progress.emit(processed, total_files)

        self.finished.emit(groups if self._is_running else {})

    def _run_fallback(self):
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
        groups: dict[str, list] = {}
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

                try:
                    size = os.path.getsize(full_path)
                except OSError:
                    size = 0

                groups.setdefault(ext, []).append((file, full_path, size))

                processed_files += 1
                if processed_files % 100 == 0 or processed_files == total_files:
                    self.progress.emit(processed_files, total_files)

        self.finished.emit(groups if self._is_running else {})

    def stop(self):
        self._is_running = False