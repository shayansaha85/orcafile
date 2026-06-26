import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter
from ui import FileOrganizerApp

def run():
    app = QApplication(sys.argv)
    window = FileOrganizerApp()
    
    # Ensure it starts in dark mode
    if window._current_theme != "dark":
        window.toggle_theme()
        
    window.resize(1100, 720)

    # Populate some dummy data to make it look realistic
    window.all_data = {
        '.pdf': [('report_2026.pdf', 'C:/Documents/report_2026.pdf'), ('invoice_001.pdf', 'C:/Documents/invoice_001.pdf')],
        '.py': [('script.py', 'C:/Code/script.py'), ('main.py', 'C:/Code/main.py'), ('utils.py', 'C:/Code/utils.py')],
        '.jpg': [('photo1.jpg', 'C:/Photos/photo1.jpg')]
    }
    
    from PyQt6.QtWidgets import QListWidgetItem
    for ext, files in window.all_data.items():
        item = QListWidgetItem(f" {ext}  ({len(files)})")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked)
        window.filter_list.addItem(item)
        
    window.populate_tree_view()
    
    # Select something to show the delete button activated
    group = window.tree_view.topLevelItem(0)
    if group:
        group.child(0).setCheckState(0, Qt.CheckState.Checked)
        window.handle_tree_item_changed(group.child(0), 0)

    window.top_stats_label.setText("6 TOTAL FILES MAPPED")
    window.path_input.setText("C:/Documents/Work")

    window.show()

    def capture():
        app.processEvents()
        # Capture dark mode
        pixmap_dark = window.grab()
        
        # Toggle to light mode
        window.toggle_theme()
        app.processEvents()
        
        # Capture light mode
        pixmap_light = window.grab()
        
        # Combine side by side
        combined = QPixmap(pixmap_dark.width() * 2, pixmap_dark.height())
        painter = QPainter(combined)
        painter.drawPixmap(0, 0, pixmap_dark)
        painter.drawPixmap(pixmap_dark.width(), 0, pixmap_light)
        painter.end()
        
        out_path = r"C:\Users\shaya\.gemini\antigravity\brain\d7a938aa-b68e-4b8b-a00e-c20e37b9e8de\actual_screenshot.png"
        combined.save(out_path)
        print(f"Saved to {out_path}")
        app.quit()

    QTimer.singleShot(1000, capture)
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
