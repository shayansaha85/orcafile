"""Theme persistence manager using QSettings for Orcafile."""

from PyQt6.QtCore import QSettings

_SETTINGS = QSettings("OrcaFile", "Preferences")
_THEME_KEY = "appearance/theme"
_DEFAULT_THEME = "dark"


def load_theme() -> str:
    """Return the stored theme name ('dark' or 'light'). Defaults to 'dark'."""
    return _SETTINGS.value(_THEME_KEY, _DEFAULT_THEME)


def save_theme(theme: str) -> None:
    """Persist the selected theme name."""
    _SETTINGS.setValue(_THEME_KEY, theme)
    _SETTINGS.sync()
