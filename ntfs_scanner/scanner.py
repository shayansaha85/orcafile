# ntfs_scanner/scanner.py

import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .volume import open_volume, close_volume, is_ntfs
from .mft import enum_mft_records, NTFS_ROOT_FRN
from .tree import FsNode, build_tree, rollup_sizes
from .navigator import find_frn_by_path, list_folder, build_full_paths, FolderEntry


@dataclass
class ScanResult:
    """Everything produced by a full volume scan."""
    drive_letter: str
    nodes: dict[int, FsNode]
    children: dict[int, list[int]]
    total_files: int
    total_dirs: int
    root_size_bytes: int

    def get_folder(self, path: str) -> list[FolderEntry] | None:
        """
        Browse any folder by relative path after scanning.
        e.g. result.get_folder("Users\\Soumik\\Downloads")

        Returns None if path doesn't exist.
        """
        frn = find_frn_by_path(path, self.nodes, self.children)
        if frn is None:
            return None
        return list_folder(frn, self.nodes, self.children)

    def get_size(self, path: str) -> int | None:
        """Returns total size in bytes for any path. None if not found."""
        frn = find_frn_by_path(path, self.nodes, self.children)
        if frn is None:
            return None
        return self.nodes[frn].total_size


def scan_ntfs(drive_letter: str) -> ScanResult:
    """
    Full NTFS volume scan via USN journal.
    Requires administrator privileges.
    """
    handle = open_volume(drive_letter)
    try:
        records = enum_mft_records(handle)
        nodes, children = build_tree(records)
    finally:
        close_volume(handle)

    rollup_sizes(nodes, children, root_frn=NTFS_ROOT_FRN)

    total_files = sum(1 for n in nodes.values() if not n.is_dir)
    total_dirs  = sum(1 for n in nodes.values() if n.is_dir)
    root_size   = nodes[NTFS_ROOT_FRN].total_size if NTFS_ROOT_FRN in nodes else 0

    return ScanResult(
        drive_letter=drive_letter,
        nodes=nodes,
        children=children,
        total_files=total_files,
        total_dirs=total_dirs,
        root_size_bytes=root_size
    )


def _scan_dir_size(path: str) -> int:
    """Recursively sum file sizes under a path. Used by fallback scanner."""
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat().st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += _scan_dir_size(entry.path)
                except (PermissionError, OSError):
                    pass
    except (PermissionError, OSError):
        pass
    return total


def scan_fallback(root_path: str, max_workers: int = 8) -> dict[str, int]:
    """
    Fallback scanner for non-NTFS paths:
    network drives (SMB/NAS), FAT32/exFAT USBs, cloud-synced folders.

    Uses ThreadPoolExecutor to scan top-level subdirs in parallel,
    then sums recursively. Returns dict: path → total_size_bytes.
    """
    results: dict[str, int] = {}

    try:
        top_entries = [
            e for e in os.scandir(root_path)
            if e.is_dir(follow_symlinks=False)
        ]
    except (PermissionError, OSError) as e:
        raise RuntimeError(f"Cannot access {root_path}: {e}")

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_scan_dir_size, entry.path): entry.path
            for entry in top_entries
        }
        for future, path in futures.items():
            try:
                results[path] = future.result()
            except Exception:
                results[path] = 0

    return results


def scan(drive_letter: str, path: str | None = None):
    """
    Smart entry point: auto-detects NTFS vs fallback.

    drive_letter: e.g. "C", "D"
    path: optional subfolder to drill into after scanning,
          e.g. "Users\\Soumik\\Downloads"

    Returns ScanResult for NTFS, or dict[path→size] for fallback.
    """
    if is_ntfs(drive_letter):
        result = scan_ntfs(drive_letter)
        if path:
            entries = result.get_folder(path)
            if entries is None:
                raise FileNotFoundError(f"Path not found: {drive_letter}:\\{path}")
            return entries
        return result
    else:
        root = f"{drive_letter}:\\" if path is None else f"{drive_letter}:\\{path}"
        return scan_fallback(root)