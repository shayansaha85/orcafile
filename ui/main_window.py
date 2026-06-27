from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QFileDialog, QTreeWidget,
    QListWidget, QLabel, QSplitter, QProgressBar,
    QCheckBox, QGraphicsOpacityEffect
)

from handlers import ScanHandlersMixin, FilterHandlersMixin, TreeHandlersMixin
from ui.styles import get_stylesheet
from ui.theme_manager import load_theme, save_theme


class FileOrganizerApp(ScanHandlersMixin, FilterHandlersMixin, TreeHandlersMixin, QMainWindow):
    """Main application window for Orcafile — a file extension organizer."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orcafile")
        self.setWindowIcon(QIcon("logo.ico"))
        self.setGeometry(100, 100, 1100, 720)

        self.all_data = {}
        self.worker = None

        # State variables for Accumulative Search Logic
        self.first_search_done = False
        self.solidified_selections = set()
        self._last_search_was_empty = True

        # Theme state
        self._current_theme = load_theme()

        # Prevent recursive checkbox signals
        self._block_tree_signals = False

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- TOP CONTROL DECK ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select a folder or local drive to index...")
        self.path_input.setFixedHeight(30)

        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("BrowseButton")
        browse_btn.setFixedHeight(30)
        browse_btn.clicked.connect(self.browse_folder)

        self.scan_btn = QPushButton("Scan & Group")
        self.scan_btn.setObjectName("ScanButton")
        self.scan_btn.setFixedHeight(30)
        self.scan_btn.clicked.connect(self.handle_scan_click)

        self.top_stats_label = QLabel("SYSTEM IDLE")
        self.top_stats_label.setObjectName("TopStats")
        self.top_stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.top_stats_label.setFixedHeight(30)

        self.theme_btn = QPushButton("☀️" if self._current_theme == "dark" else "🌙")
        self.theme_btn.setObjectName("ThemeToggleButton")
        self.theme_btn.setFixedHeight(30)
        self.theme_btn.setToolTip("Toggle Light / Dark theme")
        self.theme_btn.clicked.connect(self.toggle_theme)

        top_layout.addWidget(self.path_input, stretch=5)
        top_layout.addWidget(browse_btn)
        top_layout.addWidget(self.scan_btn)
        top_layout.addWidget(self.top_stats_label, stretch=3)
        top_layout.addWidget(self.theme_btn)
        main_layout.addLayout(top_layout)

        # --- PROGRESS ANIMATION ---
        self.loading_widget = QWidget()
        loading_layout = QHBoxLayout(self.loading_widget)
        loading_layout.setContentsMargins(0, 2, 0, 2)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)

        loading_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.loading_widget)
        self.loading_widget.hide()

        # --- MAIN DIVISION SPLITTER ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(12)

        # Left Workspace: Sidebar / Filter Deck
        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(10)

        self.filter_title_label = QLabel("FILTER CHANNELS")
        self.filter_title_label.setObjectName("FilterTitle")
        sidebar_layout.addWidget(self.filter_title_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search extensions (e.g. .pdf)...")
        self.search_input.setFixedHeight(28)
        self.search_input.textChanged.connect(self.filter_extension_list)
        sidebar_layout.addWidget(self.search_input)

        filter_ctrl_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        deselect_all_btn = QPushButton("Clear All")
        select_all_btn.setFixedHeight(26)
        deselect_all_btn.setFixedHeight(26)

        select_all_btn.clicked.connect(lambda: self.toggle_all_filters(Qt.CheckState.Checked))
        deselect_all_btn.clicked.connect(lambda: self.toggle_all_filters(Qt.CheckState.Unchecked))
        filter_ctrl_layout.addWidget(select_all_btn)
        filter_ctrl_layout.addWidget(deselect_all_btn)
        sidebar_layout.addLayout(filter_ctrl_layout)

        self.filter_list = QListWidget()
        self.filter_list.itemChanged.connect(self.update_tree_filters)
        sidebar_layout.addWidget(self.filter_list)

        # Right Workspace: Main File Tree
        main_content_container = QWidget()
        main_content_layout = QVBoxLayout(main_content_container)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(10)

        # --- FILE SEARCH DECK ---
        file_ctrl_layout = QHBoxLayout()

        self.file_search_input = QLineEdit()
        self.file_search_input.setPlaceholderText("Search for specific files...")
        self.file_search_input.setFixedHeight(28)
        self.file_search_input.textChanged.connect(self.filter_file_tree)

        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.setFixedHeight(26)
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all_files)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("DeleteButton")
        self.delete_btn.setFixedHeight(26)
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.confirm_and_delete_selected)

        expand_btn = QPushButton("Expand All")
        collapse_btn = QPushButton("Collapse All")
        expand_btn.setFixedHeight(26)
        collapse_btn.setFixedHeight(26)

        expand_btn.clicked.connect(lambda: self.tree_view.expandAll())
        collapse_btn.clicked.connect(lambda: self.tree_view.collapseAll())

        file_ctrl_layout.addWidget(self.file_search_input, stretch=3)
        file_ctrl_layout.addWidget(self.select_all_checkbox)
        file_ctrl_layout.addWidget(self.delete_btn)
        file_ctrl_layout.addWidget(expand_btn)
        file_ctrl_layout.addWidget(collapse_btn)
        main_content_layout.addLayout(file_ctrl_layout)

        self.tree_view = QTreeWidget()
        self.tree_view.setHeaderLabels(["Extension Tree Directory", "Target Destination Path"])
        self.tree_view.setColumnWidth(0, 400)
        self.tree_view.itemDoubleClicked.connect(self.open_file_location)
        self.tree_view.itemChanged.connect(self.handle_tree_item_changed)
        main_content_layout.addWidget(self.tree_view)

        splitter.addWidget(sidebar_container)
        splitter.addWidget(main_content_container)
        splitter.setSizes([260, 840])
        main_layout.addWidget(splitter)

    def browse_folder(self):
        selected_dir = QFileDialog.getExistingDirectory(self, "Open Folder Location")
        if selected_dir:
            self.path_input.setText(selected_dir)

    def apply_styles(self):
        self.setStyleSheet(get_stylesheet(self._current_theme))

    def toggle_theme(self):
        """Switch between dark and light themes and persist the choice."""
        if self._current_theme == "dark":
            self._current_theme = "light"
            self.theme_btn.setText("🌙")
        else:
            self._current_theme = "dark"
            self.theme_btn.setText("☀️")

        save_theme(self._current_theme)
        self.apply_styles()

    # ── Toast notification ──────────────────────────────────

    def show_toast(self, message: str, is_error: bool = False, duration_ms: int = 3000):
        """Show a temporary toast notification at the bottom of the window."""
        toast = QLabel(message, self)
        toast.setObjectName("ToastError" if is_error else "ToastLabel")
        toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toast.setStyleSheet(get_stylesheet(self._current_theme))
        toast.adjustSize()

        # Position at bottom-center
        toast_width = max(toast.sizeHint().width() + 40, 280)
        toast_height = toast.sizeHint().height() + 12
        x = (self.width() - toast_width) // 2
        y = self.height() - toast_height - 30
        toast.setFixedSize(toast_width, toast_height)
        toast.move(x, y)
        toast.show()
        toast.raise_()

        # Fade-out animation
        opacity_effect = QGraphicsOpacityEffect(toast)
        toast.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(1.0)

        fade_anim = QPropertyAnimation(opacity_effect, b"opacity", toast)
        fade_anim.setDuration(500)
        fade_anim.setStartValue(1.0)
        fade_anim.setEndValue(0.0)
        fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        fade_anim.finished.connect(toast.deleteLater)

        # Start fading after the visible duration
        QTimer.singleShot(duration_ms, fade_anim.start)
