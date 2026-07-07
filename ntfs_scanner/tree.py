# ntfs_scanner/tree.py

from dataclasses import dataclass, field
from collections import defaultdict
from typing import Generator

from .mft import FILE_ATTRIBUTE_DIRECTORY, NTFS_ROOT_FRN


@dataclass
class FsNode:
    """Represents a single file or folder from the MFT."""
    name: str
    size: int           # raw file size in bytes (0 for directories)
    is_dir: bool
    total_size: int = 0 # size of this node + all descendants (filled by rollup)


def build_tree(
    records: Generator
) -> tuple[dict[int, FsNode], dict[int, list[int]]]:
    """
    Consumes the MFT record generator and builds two dicts in RAM:

        nodes:    frn → FsNode
        children: parent_frn → [child frn, child frn, ...]

    These two dicts together represent the entire volume's directory tree.
    No paths are stored here — paths are reconstructed on demand in navigator.py.
    """
    nodes: dict[int, FsNode] = {}
    children: dict[int, list[int]] = defaultdict(list)

    for frn, parent_frn, file_size, file_attrs, name in records:
        is_dir = bool(file_attrs & FILE_ATTRIBUTE_DIRECTORY)
        nodes[frn] = FsNode(name=name, size=file_size, is_dir=is_dir)
        children[parent_frn].append(frn)

    return nodes, children


def rollup_sizes(
    nodes: dict[int, FsNode],
    children: dict[int, list[int]],
    root_frn: int = NTFS_ROOT_FRN
) -> None:
    """
    Computes total_size for every node in the subtree rooted at root_frn.

    Uses an iterative post-order DFS (not recursive) to avoid Python's
    recursion limit on deep directory trees.

    Post-order means: children are fully processed before their parent,
    so each parent can safely sum its children's total_sizes.

    Modifies nodes in-place. Returns nothing.
    """
    # Stack entries: (frn, already_processed)
    # First visit  → push self again as processed=True, then push children
    # Second visit → children done, compute this node's total_size
    stack = [(root_frn, False)]

    while stack:
        frn, processed = stack.pop()

        if frn not in nodes:
            continue

        if not processed:
            stack.append((frn, True))
            for child_frn in children.get(frn, []):
                stack.append((child_frn, False))
        else:
            node = nodes[frn]
            child_total = sum(
                nodes[c].total_size
                for c in children.get(frn, [])
                if c in nodes
            )
            node.total_size = node.size + child_total