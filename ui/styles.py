"""Nord-themed QSS stylesheet for the Orcafile application."""

NORD_STYLESHEET = """
    QMainWindow { background-color: #2E3440; }
    QLabel { color: #ECEFF4; font-size: 12px; font-family: 'Segoe UI', system-ui, sans-serif; }

    QLineEdit {
        background-color: #3B4252; border: 1px solid #4C566A;
        border-radius: 6px; padding: 0px 12px; color: #ECEFF4; font-size: 13px;
    }
    QLineEdit:focus { border: 1px solid #88C0D0; background-color: #434C5E; }

    QPushButton {
        background-color: #4C566A; border: 1px solid #434C5E;
        border-radius: 6px; padding: 0px 16px; color: #ECEFF4; font-size: 12px;
        font-weight: 600;
    }
    QPushButton:hover { background-color: #434C5E; border-color: #81A1C1; }
    QPushButton:pressed { background-color: #3B4252; }

    QPushButton#BrowseButton { border-color: #81A1C1; color: #88C0D0; }
    QPushButton#BrowseButton:hover { background-color: #81A1C1; color: #2E3440; }

    QPushButton#ScanButton { background-color: #88C0D0; color: #2E3440; border: none; font-weight: bold; }
    QPushButton#ScanButton:hover { background-color: #8FBCBB; }

    QPushButton#StopButton { background-color: #BF616A; color: #ECEFF4; border: none; font-weight: bold; }
    QPushButton#StopButton:hover { background-color: #D08770; }

    QTreeWidget, QListWidget {
        background-color: #3B4252; border: 1px solid #4C566A;
        border-radius: 8px; color: #D8DEE9; font-size: 13px; padding: 6px;
        outline: 0;
    }
    QTreeWidget::item, QListWidget::item { padding: 6px; border-radius: 4px; margin-bottom: 2px; }
    QTreeWidget::item:hover, QListWidget::item:hover { background-color: #434C5E; color: #ECEFF4; }
    QTreeWidget::item:selected, QListWidget::item:selected { background-color: #81A1C1; color: #2E3440; font-weight: bold; }

    QHeaderView::section {
        background-color: #3B4252; color: #88C0D0;
        padding: 8px; border: none; border-bottom: 1px solid #4C566A;
        font-weight: bold; font-size: 12px;
    }

    QProgressBar { background-color: #3B4252; border: none; border-radius: 3px; }
    QProgressBar::chunk { background-color: #A3BE8C; border-radius: 3px; }

    QLabel#TopStats {
        background-color: #3B4252;
        color: #A3BE8C;
        font-weight: bold;
        font-size: 12px;
        letter-spacing: 0.5px;
        border: 1px solid #4C566A;
        border-radius: 6px;
        padding: 0px;
    }

    QSplitter::handle {
        background-color: transparent;
    }
"""
