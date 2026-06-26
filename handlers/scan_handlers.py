import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidgetItem

from workers import ScanWorker


class ScanHandlersMixin:
    """Mixin providing scan-related event handlers for FileOrganizerApp."""

    def handle_scan_click(self):
        if self.worker and self.worker.isRunning():
            self.stop_scan()
        else:
            self.start_scan()

    def start_scan(self):
        target_dir = self.path_input.text()
        if not target_dir or not os.path.exists(target_dir):
            self.top_stats_label.setText("INVALID PATH")
            return

        # Reset states for a fresh scan
        self.first_search_done = False
        self.solidified_selections = set()
        self._last_search_was_empty = True

        self.loading_widget.show()
        self.tree_view.clear()
        self.filter_list.clear()
        self.search_input.clear()
        self.file_search_input.clear()

        self.scan_btn.setText("Stop Scan")
        self.scan_btn.setObjectName("StopButton")
        self.scan_btn.setStyleSheet("")
        self.apply_styles()

        self.progress_bar.setRange(0, 0)

        self.worker = ScanWorker(target_dir)
        self.worker.status.connect(self.handle_worker_status)
        self.worker.progress.connect(self.handle_worker_progress)
        self.worker.finished.connect(self.handle_scan_results)
        self.worker.start()

    def stop_scan(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        self.loading_widget.hide()
        self.reset_scan_button()
        self.top_stats_label.setText("SCAN CANCELED")

    def reset_scan_button(self):
        self.scan_btn.setText("Scan & Group")
        self.scan_btn.setObjectName("ScanButton")
        self.apply_styles()

    def handle_worker_status(self, text):
        self.top_stats_label.setText(text)

    def handle_worker_progress(self, current, total):
        if self.progress_bar.maximum() == 0:
            self.progress_bar.setRange(0, 100)

        percent = int((current / total) * 100)
        self.progress_bar.setValue(percent)
        self.top_stats_label.setText(f"SCANNING: {percent}%  ({current}/{total})")

    def handle_scan_results(self, groups):
        if not groups and self.top_stats_label.text() == "SCAN CANCELED":
            return

        self.all_data = groups
        self.loading_widget.hide()
        self.reset_scan_button()

        self.filter_list.blockSignals(True)
        for ext, files in sorted(groups.items()):
            item = QListWidgetItem(f" {ext}  ({len(files)})")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.filter_list.addItem(item)
        self.filter_list.blockSignals(False)

        self.populate_tree_view()

        total_files = sum(len(v) for v in groups.values())
        self.top_stats_label.setText(f"{total_files} TOTAL FILES MAPPED")

    def refresh_filter_counts(self):
        """Update filter list item counts to reflect current all_data state.

        Removes filter entries whose extension groups no longer exist.
        """
        self.filter_list.blockSignals(True)

        items_to_remove = []
        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)
            ext_name = item.text().strip().split("  (")[0]

            if ext_name in self.all_data:
                new_count = len(self.all_data[ext_name])
                item.setText(f" {ext_name}  ({new_count})")
            else:
                items_to_remove.append(i)

        # Remove from bottom to top so indices stay valid
        for idx in reversed(items_to_remove):
            self.filter_list.takeItem(idx)

        self.filter_list.blockSignals(False)
