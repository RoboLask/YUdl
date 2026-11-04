import sys
import os
import json
import urllib.request
import zipfile
import shutil
import tempfile
import stat
import subprocess
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QMessageBox, QApplication
from PyQt6.QtCore import Qt, QThread, pyqtSignal


CURRENT_VERSION = "1.0.1"
REPO_OWNER = "RoboLask"
REPO_NAME = "YUdl"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"


class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, output_path):
        super().__init__()
        self.url = url
        self.output_path = output_path

    def run(self):
        try:
            def report_progress(block_num, block_size, total_size):
                if total_size > 0:
                    percent = int(block_num * block_size / total_size * 100)
                    self.progress.emit(percent)

            urllib.request.urlretrieve(self.url, self.output_path, reporthook=report_progress)
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))


class UpdaterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update")
        self.setFixedSize(400, 150)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.status_label = QLabel("Checking for updates...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        self.apply_style()
        self.check_for_updates()

    def apply_style(self):
        self.setStyleSheet("""
            QDialog {
                background: #0A0A0A;
                color: #00FF00;
            }
            QLabel {
                color: #00FF00;
            }
            QProgressBar {
                background: #1A1A1A;
                border: 2px inset #2A2A2A;
                text-align: center;
                color: #00FF00;
            }
            QProgressBar::chunk {
                background: #00AA00;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3A3A3A, stop:1 #1A1A1A);
                color: #00FF00;
                border: 2px outset #4A4A4A;
                border-radius: 3px;
                padding: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A4A4A, stop:1 #2A2A2A);
            }
        """)

    def check_for_updates(self):
        self.status_label.setText("Checking for updates...")
        self.info_label.setText("")
        self.close_btn.setEnabled(False)

        try:
            req = urllib.request.Request(
                API_URL,
                headers={"User-Agent": "YUdl-Updater"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

            latest_version = data.get("tag_name", "").lstrip("v")

            if latest_version > CURRENT_VERSION:
                self.status_label.setText(f"New version available: {latest_version}")

                for asset in data.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        self.download_url = asset["browser_download_url"]
                        self.info_label.setText(
                            f"Current: v{CURRENT_VERSION}\nLatest: v{latest_version}"
                        )
                        self.close_btn.setEnabled(True)
                        self.download_update()
                        return

                self.info_label.setText("No exe found in release")
            else:
                self.status_label.setText("You have the latest version")
                self.info_label.setText(f"Version: v{CURRENT_VERSION}")

        except Exception as e:
            self.status_label.setText("Failed to check for updates")
            self.info_label.setText(str(e))

        self.close_btn.setEnabled(True)

    def download_update(self):
        self.status_label.setText("Downloading update...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.close_btn.setEnabled(False)

        temp_dir = tempfile.gettempdir()
        self.output_path = os.path.join(temp_dir, "YUdl_update.exe")

        self.worker = DownloadWorker(self.download_url, self.output_path)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.error.connect(self.on_download_error)
        self.worker.start()

    def on_progress(self, percent):
        self.progress_bar.setValue(percent)

    def on_download_finished(self, path):
        self.progress_bar.setVisible(False)
        self.status_label.setText("Update downloaded!")

        reply = QMessageBox.question(
            self,
            "Update Ready",
            "Update downloaded. The application will now restart to apply the update.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.apply_update(path)

        self.close_btn.setEnabled(True)

    def on_download_error(self, error):
        self.progress_bar.setVisible(False)
        self.status_label.setText("Download failed")
        self.info_label.setText(error)
        self.close_btn.setEnabled(True)

    def apply_update(self, update_path):
        current_exe = sys.executable
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        is_windows = sys.platform.startswith('win')
        
        if is_windows:
            batch_path = os.path.join(tempfile.gettempdir(), "yudl_update.bat")
            with open(batch_path, "w", encoding='utf-8') as f:
                f.write('@echo off\n')
                f.write(f'taskkill /F /IM "{os.path.basename(current_exe)}" >nul 2>&1\n')
                f.write(f'ping localhost -n 2 >nul\n')
                f.write(f'copy /Y "{update_path}" "{os.path.join(current_dir, "YUdl.exe")}"\n')
                f.write(f'start "" "{os.path.join(current_dir, "YUdl.exe")}"\n')
                f.write(f'del "{batch_path}"\n')
            os.startfile(batch_path)
        else:
            import stat
            target_path = os.path.join(current_dir, "YUdl")
            shutil.copy2(update_path, target_path)
            os.chmod(target_path, os.stat(target_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            subprocess.Popen([target_path], detached=True, start_new_session=True)
        
        app = QApplication.instance()
        if app:
            app.quit()
