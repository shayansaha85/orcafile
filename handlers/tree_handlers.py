import os
import platform
import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTreeWidgetItem, QMessageBox
from send2trash import send2trash
from send2trash.exceptions import TrashPermissionError


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


class TreeHandlersMixin:
    """Mixin providing tree view event handlers for FileOrganizerApp."""

    def populate_tree_view(self):
        self.tree_view.clear()

        enabled_extensions = set()
        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                ext_name = item.text().strip().split("  (")[0]
                enabled_extensions.add(ext_name)

        self._block_tree_signals = True

        # Sorted by total size, same convention as ntfs_scanner.navigator.list_folder
        # (TreeSize-style view) — direction toggled via self._sort_ascending.
        descending = not self._sort_ascending
        groups_by_size = sorted(
            self.all_data.items(),
            key=lambda kv: sum(s for _, _, s in kv[1]),
            reverse=descending
        )

        for ext, file_list in groups_by_size:
            if ext not in enabled_extensions:
                continue

            group_size = sum(s for _, _, s in file_list)
            parent_node = QTreeWidgetItem(self.tree_view, [f" {ext.upper()} Group ({len(file_list)} items)", "", format_size(group_size)])
            parent_node.setFlags(parent_node.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            parent_node.setCheckState(0, Qt.CheckState.Unchecked)

            for name, path, size in sorted(file_list, key=lambda f: f[2], reverse=descending):
                child = QTreeWidgetItem(parent_node, [name, path, format_size(size)])
                child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                child.setCheckState(0, Qt.CheckState.Unchecked)

        self._block_tree_signals = False

        self.tree_view.expandAll()

        if self.file_search_input.text():
            self.filter_file_tree(self.file_search_input.text())

        self.update_delete_button_state()

    def toggle_sort_order(self):
        """Flip the size sort direction and re-render the tree."""
        self._sort_ascending = not self._sort_ascending
        self.sort_order_btn.setText("Size ▲" if self._sort_ascending else "Size ▼")
        self.populate_tree_view()

    def handle_tree_item_changed(self, item, column):
        """Handle checkbox changes — propagate group ↔ child states."""
        if self._block_tree_signals:
            return

        self._block_tree_signals = True

        # If a group (top-level) item was toggled, propagate to children
        if item.parent() is None:
            state = item.checkState(0)
            # Only propagate Checked / Unchecked — not PartiallyChecked
            if state != Qt.CheckState.PartiallyChecked:
                for i in range(item.childCount()):
                    item.child(i).setCheckState(0, state)
        else:
            # A child was toggled — update parent tri-state
            parent = item.parent()
            if parent is not None:
                self._update_parent_check_state(parent)

        self._block_tree_signals = False
        self.update_delete_button_state()
        self._sync_select_all_checkbox()

    def _update_parent_check_state(self, parent):
        """Set parent to Checked, Unchecked, or PartiallyChecked based on children."""
        total = parent.childCount()
        checked_count = 0
        for i in range(total):
            if parent.child(i).checkState(0) == Qt.CheckState.Checked:
                checked_count += 1

        if checked_count == 0:
            parent.setCheckState(0, Qt.CheckState.Unchecked)
        elif checked_count == total:
            parent.setCheckState(0, Qt.CheckState.Checked)
        else:
            parent.setCheckState(0, Qt.CheckState.PartiallyChecked)

    def _sync_select_all_checkbox(self):
        """Keep the Select All checkbox in sync with tree state."""
        total = 0
        checked = 0
        for i in range(self.tree_view.topLevelItemCount()):
            group = self.tree_view.topLevelItem(i)
            for j in range(group.childCount()):
                total += 1
                if group.child(j).checkState(0) == Qt.CheckState.Checked:
                    checked += 1

        self.select_all_checkbox.blockSignals(True)
        if total == 0 or checked == 0:
            self.select_all_checkbox.setCheckState(Qt.CheckState.Unchecked)
        elif checked == total:
            self.select_all_checkbox.setCheckState(Qt.CheckState.Checked)
        else:
            self.select_all_checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
        self.select_all_checkbox.blockSignals(False)

    def toggle_select_all_files(self, state):
        """Toggle all file checkboxes in the tree."""
        # Qt sends 1 for PartiallyChecked from user click — treat as Checked
        target = Qt.CheckState.Checked if state != 0 else Qt.CheckState.Unchecked

        self._block_tree_signals = True
        for i in range(self.tree_view.topLevelItemCount()):
            group = self.tree_view.topLevelItem(i)
            if group.isHidden():
                continue
            group.setCheckState(0, target)
            for j in range(group.childCount()):
                child = group.child(j)
                if not child.isHidden():
                    child.setCheckState(0, target)
        self._block_tree_signals = False

        self.update_delete_button_state()

    def update_delete_button_state(self):
        """Enable/disable the Delete button based on whether any files are selected."""
        has_selection = len(self.get_selected_files()) > 0
        self.delete_btn.setEnabled(has_selection)

    def get_selected_files(self):
        """Return list of (extension, filename, full_path) for all checked file-level items."""
        selected = []
        for i in range(self.tree_view.topLevelItemCount()):
            group = self.tree_view.topLevelItem(i)
            # Extract extension from group label like " .PDF Group (5 items)"
            group_text = group.text(0).strip()
            ext = group_text.split(" Group")[0].strip().lower()

            for j in range(group.childCount()):
                child = group.child(j)
                if child.checkState(0) == Qt.CheckState.Checked:
                    selected.append((ext, child.text(0), child.text(1)))
        return selected

    def confirm_and_delete_selected(self):
        """Ask the user whether to recycle or permanently delete the selection."""
        selected = self.get_selected_files()
        if not selected:
            return

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("Confirm Deletion")
        msg_box.setText(f"Delete {len(selected)} selected file(s)?")

        recycle_btn = msg_box.addButton("Move to Recycle Bin", QMessageBox.ButtonRole.AcceptRole)
        permanent_btn = msg_box.addButton("Delete Permanently", QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg_box.setDefaultButton(recycle_btn)
        msg_box.setEscapeButton(cancel_btn)

        msg_box.exec()
        clicked = msg_box.clickedButton()

        if clicked is recycle_btn:
            self.delete_selected_files(selected, permanent=False)
        elif clicked is permanent_btn:
            self.delete_selected_files(selected, permanent=True)
        # Cancel — do nothing

    def delete_selected_files(self, selected, permanent=False):
        """Remove files from disk (recycled or permanent) and update internal data structures."""
        deleted_count = 0
        error_count = 0

        for ext, filename, full_path in selected:
            try:
                if os.path.exists(full_path):
                    if permanent:
                        os.remove(full_path)
                    else:
                        send2trash(full_path)
                    deleted_count += 1
                else:
                    # File already gone — still remove from data
                    deleted_count += 1

                # Remove from self.all_data
                if ext in self.all_data:
                    self.all_data[ext] = [
                        (n, p, s) for n, p, s in self.all_data[ext]
                        if p != full_path
                    ]
                    # Remove the extension group entirely if empty
                    if not self.all_data[ext]:
                        del self.all_data[ext]

            except (PermissionError, TrashPermissionError, OSError):
                error_count += 1

        # Refresh filter counts and tree
        self.refresh_filter_counts()
        self.populate_tree_view()

        # Update top stats
        total_files = sum(len(v) for v in self.all_data.values())
        self.top_stats_label.setText(f"{total_files} TOTAL FILES MAPPED")

        # Show result toast
        action_done = "permanently deleted" if permanent else "moved to Recycle Bin"
        action_failed = "delete" if permanent else "move"
        if error_count == 0:
            self.show_toast(f"✓  {deleted_count} file(s) {action_done}")
        else:
            self.show_toast(
                f"{action_done.capitalize()}: {deleted_count}, failed to {action_failed}: {error_count} (permission denied)",
                is_error=True
            )

    def filter_file_tree(self, text):
        search_query = text.lower().strip()

        for i in range(self.tree_view.topLevelItemCount()):
            group_item = self.tree_view.topLevelItem(i)
            group_has_match = False

            for j in range(group_item.childCount()):
                file_item = group_item.child(j)
                file_name = file_item.text(0).lower()

                if search_query in file_name:
                    file_item.setHidden(False)
                    group_has_match = True
                else:
                    file_item.setHidden(True)

            if not group_has_match and search_query != "":
                group_item.setHidden(True)
            else:
                group_item.setHidden(False)
                if search_query:
                    group_item.setExpanded(True)

    def open_file_location(self, item, column):
        file_path = item.text(1)
        if not file_path or not os.path.exists(file_path):
            return

        current_os = platform.system()
        try:
            if current_os == "Windows":
                subprocess.run(["explorer", "/select,", os.path.normpath(file_path)])
            elif current_os == "Darwin":
                subprocess.run(["open", "-R", file_path])
            else:
                subprocess.run(["xdg-open", os.path.dirname(file_path)])
        except Exception:
            self.top_stats_label.setText("EXPLORER ERROR")
