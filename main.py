import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,QFileDialog, QLineEdit, QRadioButton, QTextEdit,QMessageBox, QDialog)
from PyQt6.QtCore import Qt

# from core import scan_directory, save_scan, compare_scans

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Integrity Checker")
        self.setGeometry(400, 200, 700, 500)

        self.scan_data = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.show_main_menu()
 
    def show_main_menu(self):
        self.clear_layout()

        container = self.create_container(350)

        title = QLabel("SELECT MODE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        scan_btn = self.create_button("Scan Folder", self.show_scan_ui)
        compare_btn = self.create_button("Compare Scans", self.show_compare_ui)

        container.addWidget(title)
        container.addWidget(scan_btn)
        container.addWidget(compare_btn)

 
    def show_scan_ui(self):
        self.clear_layout()

        container = self.create_container(400)

        title = QLabel("Scan Folder")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.size_radio = QRadioButton("Size (Fast)")
        self.md5_radio = QRadioButton("MD5 (Accurate)")
        self.size_radio.setChecked(True)

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select folder...")

        browse_btn = self.create_button("Browse Folder", self.select_folder)
        scan_btn = self.create_button("Scan", self.scan_folder)
        export_btn = self.create_button("Export JSON", self.export_scan)
        back_btn = self.create_button("Back", self.show_main_menu)

        container.addWidget(title)
        container.addWidget(self.size_radio)
        container.addWidget(self.md5_radio)
        container.addWidget(self.folder_input)
        container.addWidget(browse_btn)
        container.addWidget(scan_btn)
        container.addWidget(export_btn)
        container.addWidget(back_btn)

 
    def show_compare_ui(self):
        self.clear_layout()

        container = self.create_container(400)

        title = QLabel("Compare Scans")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.file1_input = QLineEdit()
        self.file1_input.setPlaceholderText("Select first scan file...")

        self.file2_input = QLineEdit()
        self.file2_input.setPlaceholderText("Select second scan file...")

        btn1 = self.create_button("Select File 1", self.select_file1)
        btn2 = self.create_button("Select File 2", self.select_file2)
        compare_btn = self.create_button("Compare", self.compare_files)
        back_btn = self.create_button("Back", self.show_main_menu)

        container.addWidget(title)
        container.addWidget(self.file1_input)
        container.addWidget(btn1)
        container.addWidget(self.file2_input)
        container.addWidget(btn2)
        container.addWidget(compare_btn)
        container.addWidget(back_btn)

 
    def create_container(self, width):
        outer = self.layout

        container_widget = QWidget()
        container_widget.setFixedWidth(width)

        container_layout = QVBoxLayout()
        container_layout.setSpacing(12)
        container_widget.setLayout(container_layout)

        outer.addStretch()
        outer.addWidget(container_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        outer.addStretch()

        return container_layout

    def create_button(self, text, func):
        btn = QPushButton(text)
        btn.setMinimumHeight(45)
        btn.setStyleSheet("font-size: 15px; padding: 8px;")
        btn.clicked.connect(func)
        return btn

 
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

 
    def scan_folder(self):
        folder = self.folder_input.text()
        mode = "md5" if self.md5_radio.isChecked() else "size"

        if not folder:
            QMessageBox.critical(self, "Error", "Select a folder first")
            return

        try:
            self.setWindowTitle("Scanning... please wait")
            self.scan_data = scan_directory(folder, mode)
            self.setWindowTitle("File Integrity Checker")
            QMessageBox.information(self, "Success", "Scan completed!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def export_scan(self):
        if not self.scan_data:
            QMessageBox.critical(self, "Error", "No scan data available")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON (*.json)")

        if file_path:
            try:
                save_scan(self.scan_data, file_path)
                QMessageBox.information(self, "Saved", "Scan saved successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def compare_files(self):
        file1 = self.file1_input.text()
        file2 = self.file2_input.text()

        if not file1 or not file2:
            QMessageBox.critical(self, "Error", "Select both files")
            return

        try:
            missing, extra, mismatch = compare_scans(file1, file2)
            self.show_results(missing, extra, mismatch)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def show_results(self, missing, extra, mismatch):
        dialog = QDialog(self)
        dialog.setWindowTitle("Results")
        dialog.resize(600, 400)

        layout = QVBoxLayout()
        text = QTextEdit()
        text.setReadOnly(True)

        text.append("=== Missing Files ===")
        for f, size in missing:
            text.append(f"{f} ({size} bytes)")

        text.append("\n=== Extra Files ===")
        for f, size in extra:
            text.append(f"{f} ({size} bytes)")

        text.append("\n=== Mismatched Files ===")
        for f, reason in mismatch:
            text.append(f"{f} ({reason})")

        layout.addWidget(text)
        dialog.setLayout(layout)
        dialog.exec()


    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())