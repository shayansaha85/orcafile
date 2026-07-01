# ntfs_scanner/__init__.py

from .scanner import scan, scan_ntfs, scan_fallback, ScanResult
from .navigator import FolderEntry

__all__ = ["scan", "scan_ntfs", "scan_fallback", "ScanResult", "FolderEntry"]