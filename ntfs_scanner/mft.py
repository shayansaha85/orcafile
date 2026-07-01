# ntfs_scanner/mft.py

import struct
from typing import Generator

# Control code for FSCTL_ENUM_USN_DATA
# Computed as: CTL_CODE(FILE_DEVICE_FILE_SYSTEM=9, 44, METHOD_NEITHER=3, FILE_ANY_ACCESS=0)
FSCTL_ENUM_USN_DATA = 0x900B3

# Windows file attribute flag for directories
FILE_ATTRIBUTE_DIRECTORY = 0x10

# NTFS root directory always has FRN = 5
NTFS_ROOT_FRN = 5

# Output buffer per DeviceIoControl call.
# Larger = fewer syscalls = faster. 64KB is a safe default.
# Can be tuned up to 1MB on fast SSDs.
OUTPUT_BUFFER_SIZE = 65536


def _pack_mft_enum_data(start_frn: int) -> bytes:
    """
    Packs the MFT_ENUM_DATA_V0 input struct for DeviceIoControl.

    Fields:
        StartFileReferenceNumber: where to resume enumeration from
        LowUsn:  0  (we want all records regardless of USN)
        HighUsn: max int64 (upper bound, include everything)
    """
    return struct.pack("QQQ", start_frn, 0, 0x7FFFFFFFFFFFFFFF)


def _parse_usn_record(raw: bytes, offset: int) -> tuple:
    """
    Parses a single USN_RECORD_V2 from the raw output buffer at `offset`.

    USN_RECORD_V2 layout (offsets in bytes):
        0   DWORD  RecordLength
        8   DWORDLONG  FileReferenceNumber  (FRN)
        16  DWORDLONG  ParentFileReferenceNumber
        24  USN    Usn  (change journal sequence number, not needed here)
        52  DWORD  FileAttributes
        56  DWORDLONG  FileSize (only valid for files, 0 for directories)
        60  WORD   FileNameLength  (in bytes, not characters)
        62  WORD   FileNameOffset  (offset from record start)
        64+ WCHAR  FileName  (UTF-16LE, no null terminator)

    Returns: (rec_len, frn, parent_frn, file_size, file_attrs, name)
    """
    rec_len    = struct.unpack_from("I", raw, offset)[0]
    frn        = struct.unpack_from("Q", raw, offset + 8)[0]
    parent_frn = struct.unpack_from("Q", raw, offset + 16)[0]
    file_attrs = struct.unpack_from("I", raw, offset + 52)[0]
    file_size  = struct.unpack_from("Q", raw, offset + 56)[0]
    name_len   = struct.unpack_from("H", raw, offset + 60)[0]
    name_off   = struct.unpack_from("H", raw, offset + 62)[0]
    name       = raw[offset + name_off: offset + name_off + name_len].decode("utf-16-le")

    return rec_len, frn, parent_frn, file_size, file_attrs, name


def enum_mft_records(handle) -> Generator[tuple, None, None]:
    """
    Generator that yields one tuple per file/folder on the volume:
        (frn, parent_frn, file_size, file_attrs, name)

    Internally loops over DeviceIoControl(FSCTL_ENUM_USN_DATA) calls
    until Windows signals no more records (next_frn == 0).

    Each call fetches a batch of records. The first 8 bytes of each
    output buffer carry the next StartFRN so we know where to resume.
    """
    import win32file

    mft_enum_data = _pack_mft_enum_data(start_frn=0)

    while True:
        try:
            raw = win32file.DeviceIoControl(
                handle,
                FSCTL_ENUM_USN_DATA,
                mft_enum_data,
                OUTPUT_BUFFER_SIZE
            )
        except Exception:
            # Windows raises when there are no more records
            break

        # First 8 bytes = next StartFRN (continuation token)
        next_frn = struct.unpack_from("Q", raw, 0)[0]

        # Records start at byte 8
        offset = 8
        while offset < len(raw):
            rec_len = struct.unpack_from("I", raw, offset)[0]
            if rec_len == 0:
                break

            _, frn, parent_frn, file_size, file_attrs, name = _parse_usn_record(raw, offset)
            yield frn, parent_frn, file_size, file_attrs, name

            offset += rec_len

        if next_frn == 0:
            break

        mft_enum_data = _pack_mft_enum_data(start_frn=next_frn)