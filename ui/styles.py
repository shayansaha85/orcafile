"""Theme stylesheets for the Orcafile application."""

import os

# Compute absolute path to SVG icons (project root, alongside logo.ico).
# Use forward slashes for QSS url() compatibility on all platforms.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
_CHECK_ICON = f"{_PROJECT_ROOT}/check.svg"
_DASH_ICON = f"{_PROJECT_ROOT}/dash.svg"

# ──────────────────────────────────────────────────────────────
# DARK THEME  (Nord palette – original)
# ──────────────────────────────────────────────────────────────
NORD_STYLESHEET = f"""
    QMainWindow {{ background-color: #2E3440; }}
    QLabel {{ color: #ECEFF4; font-size: 12px; font-family: 'Segoe UI', system-ui, sans-serif; }}

    QLineEdit {{
        background-color: #3B4252; border: 1px solid #4C566A;
        border-radius: 6px; padding: 0px 12px; color: #ECEFF4; font-size: 13px;
    }}
    QLineEdit:focus {{ border: 1px solid #88C0D0; background-color: #434C5E; }}

    QPushButton {{
        background-color: #4C566A; border: 1px solid #434C5E;
        border-radius: 6px; padding: 0px 16px; color: #ECEFF4; font-size: 12px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background-color: #434C5E; border-color: #81A1C1; }}
    QPushButton:pressed {{ background-color: #3B4252; }}

    QPushButton#BrowseButton {{ border-color: #81A1C1; color: #88C0D0; }}
    QPushButton#BrowseButton:hover {{ background-color: #81A1C1; color: #2E3440; }}

    QPushButton#ScanButton {{ background-color: #88C0D0; color: #2E3440; border: none; font-weight: bold; }}
    QPushButton#ScanButton:hover {{ background-color: #8FBCBB; }}

    QPushButton#StopButton {{ background-color: #BF616A; color: #ECEFF4; border: none; font-weight: bold; }}
    QPushButton#StopButton:hover {{ background-color: #D08770; }}

    QPushButton#ThemeToggleButton {{
        background-color: #434C5E; border: 1px solid #4C566A;
        border-radius: 6px; padding: 0px 10px; color: #EBCB8B; font-size: 14px;
        font-weight: bold; min-width: 36px; max-width: 36px;
    }}
    QPushButton#ThemeToggleButton:hover {{ background-color: #4C566A; border-color: #EBCB8B; }}

    QPushButton#DeleteButton {{
        background-color: #4C566A; border: 1px solid #434C5E;
        border-radius: 6px; padding: 0px 14px; color: #BF616A; font-size: 12px;
        font-weight: 600;
    }}
    QPushButton#DeleteButton:hover {{ background-color: #BF616A; color: #ECEFF4; border-color: #BF616A; }}
    QPushButton#DeleteButton:disabled {{ background-color: #3B4252; color: #4C566A; border-color: #3B4252; }}

    QTreeWidget, QListWidget {{
        background-color: #3B4252; border: 1px solid #4C566A;
        border-radius: 8px; color: #D8DEE9; font-size: 13px; padding: 6px;
        outline: 0;
    }}
    QTreeWidget::item, QListWidget::item {{ padding: 6px; border-radius: 4px; margin-bottom: 2px; }}
    QTreeWidget::item:hover, QListWidget::item:hover {{ background-color: #434C5E; color: #ECEFF4; }}
    QTreeWidget::item:selected, QListWidget::item:selected {{ background-color: #81A1C1; color: #2E3440; font-weight: bold; }}

    QTreeWidget::indicator:unchecked {{
        width: 16px; height: 16px;
        border: 2px solid #4C566A; border-radius: 3px; background-color: #3B4252;
    }}
    QTreeWidget::indicator:checked {{
        width: 16px; height: 16px;
        border: 2px solid #88C0D0; border-radius: 3px; background-color: #88C0D0;
        image: url("{_CHECK_ICON}");
    }}
    QTreeWidget::indicator:indeterminate {{
        width: 16px; height: 16px;
        border: 2px solid #EBCB8B; border-radius: 3px; background-color: #EBCB8B;
        image: url("{_DASH_ICON}");
    }}

    QHeaderView::section {{
        background-color: #3B4252; color: #88C0D0;
        padding: 8px; border: none; border-bottom: 1px solid #4C566A;
        font-weight: bold; font-size: 12px;
    }}

    QProgressBar {{ background-color: #3B4252; border: none; border-radius: 3px; }}
    QProgressBar::chunk {{ background-color: #A3BE8C; border-radius: 3px; }}

    QLabel#TopStats {{
        background-color: #3B4252;
        color: #A3BE8C;
        font-weight: bold;
        font-size: 12px;
        letter-spacing: 0.5px;
        border: 1px solid #4C566A;
        border-radius: 6px;
        padding: 0px;
    }}

    QLabel#FilterTitle {{
        color: #D8DEE9; font-size: 13px; font-weight: bold;
    }}

    QSplitter::handle {{
        background-color: transparent;
    }}

    QCheckBox {{ color: #D8DEE9; font-size: 12px; spacing: 6px; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px;
        border: 2px solid #4C566A; border-radius: 3px; background-color: #3B4252;
    }}
    QCheckBox::indicator:checked {{
        border: 2px solid #88C0D0; background-color: #88C0D0;
        image: url("{_CHECK_ICON}");
    }}
    QCheckBox::indicator:indeterminate {{
        border: 2px solid #EBCB8B; background-color: #EBCB8B;
        image: url("{_DASH_ICON}");
    }}

    QMessageBox {{ background-color: #2E3440; }}
    QMessageBox QLabel {{ color: #ECEFF4; font-size: 13px; }}
    QMessageBox QPushButton {{
        background-color: #4C566A; border: 1px solid #434C5E;
        border-radius: 6px; padding: 6px 20px; color: #ECEFF4; font-size: 12px;
        font-weight: 600; min-width: 70px;
    }}
    QMessageBox QPushButton:hover {{ background-color: #434C5E; border-color: #81A1C1; }}

    QLabel#ToastLabel {{
        background-color: #3B4252; color: #A3BE8C;
        font-size: 12px; font-weight: bold; padding: 10px 20px;
        border: 1px solid #4C566A; border-radius: 8px;
    }}
    QLabel#ToastError {{
        background-color: #3B4252; color: #BF616A;
        font-size: 12px; font-weight: bold; padding: 10px 20px;
        border: 1px solid #BF616A; border-radius: 8px;
    }}
"""

# ──────────────────────────────────────────────────────────────
# LIGHT THEME  (Snow Storm palette)
# ──────────────────────────────────────────────────────────────
LIGHT_STYLESHEET = f"""
    QMainWindow {{ background-color: #F0F1F5; }}
    QLabel {{ color: #2E3440; font-size: 12px; font-family: 'Segoe UI', system-ui, sans-serif; }}

    QLineEdit {{
        background-color: #FFFFFF; border: 1px solid #D8DEE9;
        border-radius: 6px; padding: 0px 12px; color: #2E3440; font-size: 13px;
    }}
    QLineEdit:focus {{ border: 1px solid #5E81AC; background-color: #FFFFFF; }}

    QPushButton {{
        background-color: #E5E9F0; border: 1px solid #D8DEE9;
        border-radius: 6px; padding: 0px 16px; color: #2E3440; font-size: 12px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background-color: #D8DEE9; border-color: #5E81AC; }}
    QPushButton:pressed {{ background-color: #CDD3DE; }}

    QPushButton#BrowseButton {{ border-color: #5E81AC; color: #5E81AC; }}
    QPushButton#BrowseButton:hover {{ background-color: #5E81AC; color: #FFFFFF; }}

    QPushButton#ScanButton {{ background-color: #5E81AC; color: #FFFFFF; border: none; font-weight: bold; }}
    QPushButton#ScanButton:hover {{ background-color: #4C6B8A; }}

    QPushButton#StopButton {{ background-color: #BF616A; color: #FFFFFF; border: none; font-weight: bold; }}
    QPushButton#StopButton:hover {{ background-color: #A5444D; }}

    QPushButton#ThemeToggleButton {{
        background-color: #E5E9F0; border: 1px solid #D8DEE9;
        border-radius: 6px; padding: 0px 10px; color: #5E81AC; font-size: 14px;
        font-weight: bold; min-width: 36px; max-width: 36px;
    }}
    QPushButton#ThemeToggleButton:hover {{ background-color: #D8DEE9; border-color: #5E81AC; }}

    QPushButton#DeleteButton {{
        background-color: #E5E9F0; border: 1px solid #D8DEE9;
        border-radius: 6px; padding: 0px 14px; color: #BF616A; font-size: 12px;
        font-weight: 600;
    }}
    QPushButton#DeleteButton:hover {{ background-color: #BF616A; color: #FFFFFF; border-color: #BF616A; }}
    QPushButton#DeleteButton:disabled {{ background-color: #F0F1F5; color: #C0C5CE; border-color: #E5E9F0; }}

    QTreeWidget, QListWidget {{
        background-color: #FFFFFF; border: 1px solid #D8DEE9;
        border-radius: 8px; color: #2E3440; font-size: 13px; padding: 6px;
        outline: 0;
    }}
    QTreeWidget::item, QListWidget::item {{ padding: 6px; border-radius: 4px; margin-bottom: 2px; }}
    QTreeWidget::item:hover, QListWidget::item:hover {{ background-color: #E5E9F0; color: #2E3440; }}
    QTreeWidget::item:selected, QListWidget::item:selected {{ background-color: #5E81AC; color: #FFFFFF; font-weight: bold; }}

    QTreeWidget::indicator:unchecked {{
        width: 16px; height: 16px;
        border: 2px solid #C0C5CE; border-radius: 3px; background-color: #FFFFFF;
    }}
    QTreeWidget::indicator:checked {{
        width: 16px; height: 16px;
        border: 2px solid #5E81AC; border-radius: 3px; background-color: #5E81AC;
        image: url("{_CHECK_ICON}");
    }}
    QTreeWidget::indicator:indeterminate {{
        width: 16px; height: 16px;
        border: 2px solid #D08770; border-radius: 3px; background-color: #D08770;
        image: url("{_DASH_ICON}");
    }}

    QHeaderView::section {{
        background-color: #F0F1F5; color: #5E81AC;
        padding: 8px; border: none; border-bottom: 1px solid #D8DEE9;
        font-weight: bold; font-size: 12px;
    }}

    QProgressBar {{ background-color: #E5E9F0; border: none; border-radius: 3px; }}
    QProgressBar::chunk {{ background-color: #A3BE8C; border-radius: 3px; }}

    QLabel#TopStats {{
        background-color: #FFFFFF;
        color: #5E81AC;
        font-weight: bold;
        font-size: 12px;
        letter-spacing: 0.5px;
        border: 1px solid #D8DEE9;
        border-radius: 6px;
        padding: 0px;
    }}

    QLabel#FilterTitle {{
        color: #2E3440; font-size: 13px; font-weight: bold;
    }}

    QSplitter::handle {{
        background-color: transparent;
    }}

    QCheckBox {{ color: #2E3440; font-size: 12px; spacing: 6px; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px;
        border: 2px solid #C0C5CE; border-radius: 3px; background-color: #FFFFFF;
    }}
    QCheckBox::indicator:checked {{
        border: 2px solid #5E81AC; background-color: #5E81AC;
        image: url("{_CHECK_ICON}");
    }}
    QCheckBox::indicator:indeterminate {{
        border: 2px solid #D08770; background-color: #D08770;
        image: url("{_DASH_ICON}");
    }}

    QMessageBox {{ background-color: #F0F1F5; }}
    QMessageBox QLabel {{ color: #2E3440; font-size: 13px; }}
    QMessageBox QPushButton {{
        background-color: #E5E9F0; border: 1px solid #D8DEE9;
        border-radius: 6px; padding: 6px 20px; color: #2E3440; font-size: 12px;
        font-weight: 600; min-width: 70px;
    }}
    QMessageBox QPushButton:hover {{ background-color: #D8DEE9; border-color: #5E81AC; }}

    QLabel#ToastLabel {{
        background-color: #FFFFFF; color: #4C8C5E;
        font-size: 12px; font-weight: bold; padding: 10px 20px;
        border: 1px solid #A3BE8C; border-radius: 8px;
    }}
    QLabel#ToastError {{
        background-color: #FFFFFF; color: #BF616A;
        font-size: 12px; font-weight: bold; padding: 10px 20px;
        border: 1px solid #BF616A; border-radius: 8px;
    }}
"""


def get_stylesheet(theme: str) -> str:
    """Return the QSS stylesheet string for the given theme name."""
    if theme == "light":
        return LIGHT_STYLESHEET
    return NORD_STYLESHEET
