from PyQt6.QtCore import Qt


class FilterHandlersMixin:
    """Mixin providing extension filter event handlers for FileOrganizerApp."""

    def filter_extension_list(self, text):
        search_query = text.lower().strip()

        # If user clears the search bar
        if not search_query:
            for i in range(self.filter_list.count()):
                self.filter_list.item(i).setHidden(False)
            self._last_search_was_empty = True
            return

        self.filter_list.blockSignals(True)

        # When typing begins (transition from empty to active search)
        if self._last_search_was_empty:
            self.solidified_selections = set()
            if not self.first_search_done:
                # First ever search clears the board to isolate the result
                self.first_search_done = True
            else:
                # Subsequent searches remember what was already checked
                for i in range(self.filter_list.count()):
                    item = self.filter_list.item(i)
                    if item.checkState() == Qt.CheckState.Checked:
                        self.solidified_selections.add(item.text())

            self._last_search_was_empty = False

        # Apply visibility and auto-selection logic
        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)
            item_text = item.text()
            is_match = search_query in item_text.lower()

            item.setHidden(not is_match)

            # Keep it checked if it matches the current typing OR was saved previously
            if is_match or (item_text in self.solidified_selections):
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

        self.filter_list.blockSignals(False)
        self.populate_tree_view()

    def toggle_all_filters(self, state):
        self.filter_list.blockSignals(True)
        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)
            if not item.isHidden():
                item.setCheckState(state)

        # Reset search isolation logic if user manually alters everything via buttons
        if state == Qt.CheckState.Checked:
            self.first_search_done = False
        else:
            self.first_search_done = True

        self.filter_list.blockSignals(False)
        self.populate_tree_view()

    def update_tree_filters(self, item):
        self.populate_tree_view()
