# ntfs_scanner/volume.py

import win32file
import win32api
import win32con


def open_volume(drive_letter: str):
    """
    Opens a raw handle to the NTFS volume (e.g. "C" → \\.\C:).
    Requires administrator privileges.
    Returns a pywin32 handle object.
    """
    path = f"\\\\.\\{drive_letter.upper()}:"

    handle = win32file.CreateFile(
        path,
        win32file.GENERIC_READ,
        win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
        None,
        win32file.OPEN_EXISTING,
        0,
        None
    )

    if handle == win32file.INVALID_HANDLE_VALUE:
        raise OSError(f"Failed to open volume {path}. Are you running as administrator?")

    return handle


def close_volume(handle) -> None:
    """Closes the volume handle."""
    win32file.CloseHandle(handle)


def is_ntfs(drive_letter: str) -> bool:
    """
    Returns True if the given drive is NTFS formatted.
    FAT32/exFAT/network drives must use the fallback scanner.
    """
    try:
        root = f"{drive_letter.upper()}:\\"
        # GetVolumeInformation returns (name, serial, maxlen, flags, fs_type)
        _, _, _, _, fs_type = win32api.GetVolumeInformation(root)
        return fs_type.upper() == "NTFS"
    except Exception:
        return False