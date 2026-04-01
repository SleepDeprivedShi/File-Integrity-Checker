import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel,
    QFileDialog, QLineEdit, QRadioButton, QMessageBox, QDialog,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QCursor, QColor

from core import scan_directory, save_scan, compare_scans


class ScanWorker(QThread):
    progress = pyqtSignal(int, str)  # percent, filename
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, folder, mode):
        super().__init__()
        self.folder = folder
        self.mode = mode

    def run(self):
        try:
            def update(p, file):
                self.progress.emit(p, file)

            data = scan_directory(self.folder, self.mode, update)
            self.finished.emit(data)

        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Integrity Checker")
        self.setGeometry(400, 200, 800, 550)

        self.scan_data = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.apply_dark_theme()
        self.show_main_menu()

    # THEME
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: Segoe UI;
            }

            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 6px;
                font-size: 16px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #888;
            }

            QPushButton#primary {
                background-color: #0078d4;
                border: none;
            }

            QPushButton#primary:hover {
                background-color: #0090ff;
            }

            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 8px;
            }

            QRadioButton {
                font-size: 15px;
                spacing: 8px;
            }

            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #888;
                background: transparent;
            }

            QRadioButton::indicator:checked {
                background-color: #0078d4;
                border: 2px solid #0078d4;
            }

            QProgressBar {
                border: 1px solid #444;
                border-radius: 5px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #0078d4;
            }
        """)

    # HELPERS
    def update_progress(self, percent, filename):
        self.progress.setValue(percent)

        if len(filename) > 50:
            filename = "..." + filename[-50:]

        self.scan_label.setText(f"Scanning: {filename}")

    def create_container(self):
        container = QWidget()
        container.setMinimumWidth(550)
        container.setMaximumWidth(650)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        container.setLayout(layout)

        self.layout.addStretch()
        self.layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addStretch()

        return layout

    def create_button(self, text, func, primary=False):
        btn = QPushButton(text)
        btn.setMinimumHeight(50)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.clicked.connect(func)

        if primary:
            btn.setObjectName("primary")

        return btn

    def create_back_bar(self):
        top_bar = QHBoxLayout()

        back_btn = QPushButton("Back")
        back_btn.setObjectName("back") 
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setFixedHeight(35)
        back_btn.setFixedWidth(90)
        back_btn.clicked.connect(self.show_main_menu)

        top_bar.addWidget(back_btn)
        top_bar.addStretch()

        self.layout.addLayout(top_bar)

    def show_message(self, title, text, icon=QMessageBox.Icon.Information):
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("QPushButton { min-width: 80px; padding: 5px; }")
        msg.exec()

    # FILE PICKERS 
    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self.folder_input.setText(path)

    def select_file1(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "JSON (*.json)")
        if path:
            self.file1_input.setText(path)

    def select_file2(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "JSON (*.json)")
        if path:
            self.file2_input.setText(path)

    # MAIN MENU
    def show_main_menu(self):
        self.clear_layout()

        container = self.create_container()

        title = QLabel("SELECT MODE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: bold;")

        scan_btn = self.create_button("Scan Folder", self.show_scan_ui, primary=True)
        compare_btn = self.create_button("Compare Scans", self.show_compare_ui)

        container.addWidget(title)
        container.addWidget(scan_btn)
        container.addWidget(compare_btn)

    # SCAN UI
    def show_scan_ui(self):
        self.clear_layout()

        self.create_back_bar()
        container = self.create_container()

        title = QLabel("Scan Folder")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")

        self.size_radio = QRadioButton("Size (Fast)")
        self.md5_radio = QRadioButton("MD5 (Accurate)")
        self.size_radio.setChecked(True)

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select folder...")

        browse_btn = self.create_button("Browse Folder", self.select_folder)
        scan_btn = self.create_button("Scan", self.start_scan, primary=True)

        self.progress = QProgressBar()
        self.progress.setVisible(False)

        container.addWidget(title)

        self.scan_label = QLabel("")
        self.scan_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.size_radio)
        radio_layout.addWidget(self.md5_radio)

        container.addLayout(radio_layout)
        container.addWidget(self.folder_input)
        container.addWidget(browse_btn)
        container.addWidget(scan_btn)

        container.addWidget(self.progress)
        container.addWidget(self.scan_label)

    # SCAN FUNCTION
    def start_scan(self):
        folder = self.folder_input.text()
        mode = "md5" if self.md5_radio.isChecked() else "size"

        if not folder:
            self.show_message("Error", "Select a folder first", QMessageBox.Icon.Critical)
            return

        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.scan_label.setText("Starting...")

        self.worker = ScanWorker(folder, mode)

        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.scan_finished)
        self.worker.error.connect(self.scan_error)

        self.worker.start()

    def scan_finished(self, data):
        self.progress.setVisible(False)
        self.scan_data = data

        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON (*.json)")
        if file_path:
            save_scan(self.scan_data, file_path)
            self.show_message("Success", "Scan + Export completed")

    def scan_error(self, err):
        self.progress.setVisible(False)
        self.show_message("Error", err, QMessageBox.Icon.Critical)

    # COMPARE UI
    def show_compare_ui(self):
        self.clear_layout()

        self.create_back_bar()
        container = self.create_container()

        title = QLabel("Compare Scans")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")

        self.file1_input = QLineEdit()
        self.file1_input.setPlaceholderText("Select first scan file...")

        self.file2_input = QLineEdit()
        self.file2_input.setPlaceholderText("Select second scan file...")

        btn1 = self.create_button("Select File 1", self.select_file1)
        btn2 = self.create_button("Select File 2", self.select_file2)
        compare_btn = self.create_button("Compare", self.compare_files, primary=True)

        container.addWidget(title)
        container.addWidget(self.file1_input)
        container.addWidget(btn1)
        container.addWidget(self.file2_input)
        container.addWidget(btn2)
        container.addWidget(compare_btn)

    # COMPARE FUNCTION
    def compare_files(self):
        file1 = self.file1_input.text()
        file2 = self.file2_input.text()

        if not file1 or not file2:
            self.show_message("Error", "Select both files", QMessageBox.Icon.Critical)
            return

        try:
            missing, extra, mismatch = compare_scans(file1, file2)
            self.show_results_table(missing, extra, mismatch)
        except Exception as e:
            self.show_message("Error", str(e), QMessageBox.Icon.Critical)

    # RESULTS
    def show_results_table(self, missing, extra, mismatch):
        dialog = QDialog(self)
        dialog.setWindowTitle("Results")
        dialog.resize(800, 500)

        layout = QVBoxLayout()
        table = QTableWidget()

        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["File", "Type", "Details"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSortingEnabled(True)

        rows = len(missing) + len(extra) + len(mismatch)
        table.setRowCount(rows)

        row = 0

        def add_row(file, type_, detail, color):
            nonlocal row
            table.setItem(row, 0, QTableWidgetItem(file))
            table.setItem(row, 1, QTableWidgetItem(type_))
            table.setItem(row, 2, QTableWidgetItem(detail))

            for col in range(3):
                table.item(row, col).setBackground(color)

            row += 1

        for f, size in missing:
            add_row(f, "Missing", f"{size} bytes", QColor(120, 0, 0))

        for f, size in extra:
            add_row(f, "Extra", f"{size} bytes", QColor(120, 80, 0))

        for f, reason in mismatch:
            add_row(f, "Mismatch", reason, QColor(0, 100, 0))

        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec()

    # CLEAR
    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

            elif item.layout():
                sub_layout = item.layout()
                while sub_layout.count():
                    sub_item = sub_layout.takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
