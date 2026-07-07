# ntfs_scanner/navigator.py

from dataclasses import dataclass
from .tree import FsNode
from .mft import NTFS_ROOT_FRN


@dataclass
class FolderEntry:
    """A single item shown when browsing a folder's contents."""
    name: str
    total_size: int
    is_dir: bool
    frn: int

    @property
    def size_mb(self) -> float:
        return self.total_size / (1024 ** 2)

    @property
    def size_gb(self) -> float:
        return self.total_size / (1024 ** 3)


def find_frn_by_path(
    target_path: str,
    nodes: dict[int, FsNode],
    children: dict[int, list[int]],
    root_frn: int = NTFS_ROOT_FRN
) -> int | None:
    """
    Resolves a relative path to an FRN by walking the in-memory tree.

    target_path: path relative to drive root, e.g. "Projects\\backend"
                 forward slashes are also accepted.

    Returns the FRN of the target folder, or None if not found.

    This is purely an in-memory operation — no disk access.
    """
    segments = [s for s in target_path.replace("/", "\\").split("\\") if s]

    if not segments:
        return root_frn  # empty path = drive root

    current_frn = root_frn

    for segment in segments:
        segment_lower = segment.lower()
        found_frn = None

        for child_frn in children.get(current_frn, []):
            child = nodes.get(child_frn)
            if child and child.name.lower() == segment_lower:
                found_frn = child_frn
                break

        if found_frn is None:
            return None  # segment not found

        current_frn = found_frn

    return current_frn


def list_folder(
    frn: int,
    nodes: dict[int, FsNode],
    children: dict[int, list[int]]
) -> list[FolderEntry]:
    """
    Returns the direct children of a folder, sorted by total_size descending.
    Equivalent to the main panel in TreeSize when you click a folder.
    """
    results = []

    for child_frn in children.get(frn, []):
        child = nodes.get(child_frn)
        if not child:
            continue
        results.append(FolderEntry(
            name=child.name,
            total_size=child.total_size,
            is_dir=child.is_dir,
            frn=child_frn
        ))

    results.sort(key=lambda e: e.total_size, reverse=True)
    return results


def build_full_paths(
    nodes: dict[int, FsNode],
    children: dict[int, list[int]],
    root_frn: int = NTFS_ROOT_FRN
) -> dict[int, str]:
    """
    Builds a complete frn → full_path mapping for every node in the tree.
    Uses top-down BFS so parent paths are always known before children.

    Returns dict: frn → "\\Windows\\System32\\drivers" (no drive letter prefix)
    """
    paths: dict[int, str] = {root_frn: "\\"}
    stack = [root_frn]

    while stack:
        frn = stack.pop()
        parent_path = paths[frn]

        for child_frn in children.get(frn, []):
            if child_frn not in nodes:
                continue
            child_name = nodes[child_frn].name
            sep = "" if parent_path == "\\" else "\\"
            paths[child_frn] = parent_path + sep + child_name
            stack.append(child_frn)

    return paths