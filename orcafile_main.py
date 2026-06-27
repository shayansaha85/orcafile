import sys
import platform

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from ui import FileOrganizerApp


if __name__ == "__main__":
    if platform.system() == "Windows":
        import ctypes
        myappid = 'shayansaha85.orcafile.fileorganizer.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("orcafile_logo.ico"))

    window = FileOrganizerApp()
    window.show()
    sys.exit(app.exec())