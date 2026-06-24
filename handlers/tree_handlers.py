import os
import platform
import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTreeWidgetItem


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

        for ext, file_list in sorted(self.all_data.items()):
            if ext not in enabled_extensions:
                continue

            parent_node = QTreeWidgetItem(self.tree_view, [f" {ext.upper()} Group ({len(file_list)} items)"])
            for name, path in file_list:
                QTreeWidgetItem(parent_node, [name, path])

        self.tree_view.expandAll()

        if self.file_search_input.text():
            self.filter_file_tree(self.file_search_input.text())

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
