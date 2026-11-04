import sys
import os 
import json
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QProgressBar, QMessageBox, 
                             QFileDialog, QRadioButton, QButtonGroup, QMenuBar,
                             QDialog, QCheckBox, QGroupBox)
from updater import UpdaterDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QFont, QAction, QPixmap, QPalette, QBrush
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import yt_dlp
from datetime import datetime


# ================= Translations =================
TRANSLATIONS = {
    'en': {
        'app_title': 'YUdl',
        'menu_file': 'File',
        'menu_settings': 'Settings',
        'menu_exit': 'Exit',
        'menu_help': 'Help',
        'menu_about': 'About',
        'menu_update': 'Check for Updates',
        'menu_update_en': 'Check for Updates',
        'menu_update_ru': 'Проверить обновления',
        'menu_update_uk': 'Перевірити оновлення',
        'url_label': 'URL:',
        'url_placeholder': 'https://youtube.com/watch?v=...',
        'video': 'Video',
        'audio': 'Audio',
        'quality_best': 'Best',
        'quality_medium': 'Medium (720p)',
        'quality_low': 'Low (480p)',
        'save_to': 'Save to:',
        'ready': 'Ready',
        'download_btn': 'DOWNLOAD',
        'stop_btn': 'STOP',
        'initializing': 'Initializing...',
        'converting': 'Converting...',
        'complete': 'Complete',
        'stopped': 'Stopped',
        'error': 'Error!',
        'error_empty_url': 'Enter YouTube URL!',
        'error_invalid_url': 'Invalid YouTube URL!',
        'done_title': 'Done',
        'error_title': 'Error',
        'settings_title': 'Settings',
        'audio_settings': 'Audio Settings',
        'enable_music': 'Enable Background Music',
        'language_settings': 'Language Settings',
        'language': 'Language:',
        'close_btn': 'Close',
        'about_title': 'About YUdl',
        'about_text': 'YUdl - YouTube Downloader\n\nVersion 1.0.1\n\n© 2026 msx. All rights reserved.\n\nDownload videos and audio from YouTube\nwith customizable settings!',
        'warning': 'Warning',
        'select_folder': 'Select Download Folder'
    },
    'ru': {
        'app_title': 'YUdl',
        'menu_file': 'Файл',
        'menu_settings': 'Настройки',
        'menu_exit': 'Выход',
        'menu_help': 'Справка',
        'menu_about': 'О программе',
        'url_label': 'URL:',
        'url_placeholder': 'https://youtube.com/watch?v=...',
        'video': 'Видео',
        'audio': 'Аудио',
        'quality_best': 'Лучшее',
        'quality_medium': 'Среднее (720p)',
        'quality_low': 'Низкое (480p)',
        'save_to': 'Сохранить в:',
        'ready': 'Готов',
        'download_btn': 'СКАЧАТЬ',
        'stop_btn': 'СТОП',
        'initializing': 'Инициализация...',
        'converting': 'Конвертация...',
        'complete': 'Завершено',
        'stopped': 'Остановлено',
        'error': 'Ошибка!',
        'error_empty_url': 'Введите URL YouTube!',
        'error_invalid_url': 'Неверный URL YouTube!',
        'done_title': 'Готово',
        'error_title': 'Ошибка',
        'settings_title': 'Настройки',
        'audio_settings': 'Настройки звука',
        'enable_music': 'Включить фоновую музыку',
        'language_settings': 'Настройки языка',
        'language': 'Язык:',
        'close_btn': 'Закрыть',
        'about_title': 'О программе YUdl',
        'about_text': 'YUdl - Загрузчик с YouTube\n\nВерсия 1.0.1\n\n© 2026 msx. Все права защищены.\n\nЗагружайте видео и аудио с YouTube\nс настраиваемыми параметрами!',
        'warning': 'Предупреждение',
        'select_folder': 'Выберите папку для загрузки'
    },
    'uk': {
        'app_title': 'YUdl',
        'menu_file': 'Файл',
        'menu_settings': 'Налаштування',
        'menu_exit': 'Вихід',
        'menu_help': 'Довідка',
        'menu_about': 'Про програму',
        'url_label': 'URL:',
        'url_placeholder': 'https://youtube.com/watch?v=...',
        'video': 'Відео',
        'audio': 'Аудіо',
        'quality_best': 'Найкраще',
        'quality_medium': 'Середнє (720p)',
        'quality_low': 'Низьке (480p)',
        'save_to': 'Зберегти в:',
        'ready': 'Готовий',
        'download_btn': 'ЗАВАНТАЖИТИ',
        'stop_btn': 'СТОП',
        'initializing': 'Ініціалізація...',
        'converting': 'Конвертація...',
        'complete': 'Завершено',
        'stopped': 'Зупинено',
        'error': 'Помилка!',
        'error_empty_url': 'Введіть URL YouTube!',
        'error_invalid_url': 'Невірний URL YouTube!',
        'done_title': 'Готово',
        'error_title': 'Помилка',
        'settings_title': 'Налаштування',
        'audio_settings': 'Налаштування звуку',
        'enable_music': 'Увімкнути фонову музику',
        'language_settings': 'Налаштування мови',
        'language': 'Мова:',
        'close_btn': 'Закрити',
        'about_title': 'Про програму YUdl',
        'about_text': 'YUdl - Завантажувач з YouTube\n\nВерсія 1.0.1\n\n© 2026 msx. Всі права захищені.\n\nЗавантажуйте відео та аудіо з YouTube\nз налаштуванням параметрів!',
        'warning': 'Попередження',
        'select_folder': 'Виберіть папку для завантаження'
    }
}


# ================= FFmpeg finder =================
import shutil

def find_ffmpeg():
    """Ищет FFmpeg в нескольких возможных местах"""
    base = os.path.dirname(os.path.abspath(__file__))
    
    is_windows = sys.platform.startswith('win')
    ext = '.exe' if is_windows else ''
    
    # Возможные пути
    paths = [
        os.path.join(base, "ffmpeg", "bin"),
        os.path.join(base, "ffmpeg"),
        os.path.join(base, "bin"),
        "/usr/local/bin",
        "/usr/bin",
    ]
    
    if is_windows:
        paths.extend([
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
            r"C:\Program Files (x86)\ffmpeg\bin",
        ])
    
    for p in paths:
        ffmpeg_exe = os.path.join(p, f"ffmpeg{ext}")
        ffprobe_exe = os.path.join(p, f"ffprobe{ext}")
        
        if os.path.isfile(ffmpeg_exe) and os.path.isfile(ffprobe_exe):
            return p
    
    # Пробуем найти через shutil.which
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return os.path.dirname(ffmpeg_path)
    
    return None


class DownloadThread(QThread):
    progress = pyqtSignal(dict)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, url, quality, format_type, output_path, audio_format='mp3'):
        super().__init__()
        self.url = url
        self.quality = quality
        self.format_type = format_type
        self.output_path = output_path
        self.audio_format = audio_format
        self.current_percent = 0
        self.should_stop = False
        
    def stop(self):
        """Остановка загрузки"""
        self.should_stop = True
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                if total:
                    percent = int(d.get('downloaded_bytes', 0) / total * 100)
                    if percent != self.current_percent:
                        self.current_percent = percent
                        self.progress.emit({
                            'percent': percent,
                            'downloaded': d.get('downloaded_bytes', 0),
                            'total': total,
                            'speed': d.get('speed', 0)
                        })
            except Exception as e:
                print(f"Progress error: {e}")
        elif d['status'] == 'finished':
            # Когда загрузка завершена, но еще идет конвертация
            self.progress.emit({
                'percent': 95,
                'downloaded': 0,
                'total': 0,
                'speed': 0
            })
                
    def run(self):
        try:
            if self.should_stop:
                return
                
            # Находим FFmpeg
            ffmpeg_path = find_ffmpeg()
            
            if not ffmpeg_path:
                raise Exception(
                    "FFmpeg not found!\n"
                    "Put ffmpeg in ffmpeg/bin next to the program."
                )    
            ydl_opts = {
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'ffmpeg_location': ffmpeg_path,
                'ignoreerrors': False,
                'socket_timeout': 30,
                'retries': 15,
                'fragment_retries': 15,
                'extractor_retries': 5,
                'http_chunk_size': 10485760,
                'concurrent_fragment_downloads': 1,

                # ✅ Новый формат js runtime
                'js_runtimes': {
                    'node': {}
                },
                'remote_components': ['ejs:github'],
            }            

            # ---------- AUDIO ----------
            if self.format_type == 'audio':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.audio_format,
                        'preferredquality': '320' if self.audio_format == 'mp3' else '0',
                    }],
                })
            
            # ---------- VIDEO (БЕЗ ЛИШНЕЙ КОНВЕРТАЦИИ!) ----------
            else:
                if self.quality == 'best':
                    # Ищем готовые MP4 файлы с AAC аудио
                    ydl_opts['format'] = (
                        'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                    )
                elif self.quality == 'medium':
                    ydl_opts['format'] = (
                        'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/'
                        'best[height<=720][ext=mp4]/best[height<=720]'
                    )
                else:  # low
                    ydl_opts['format'] = (
                        'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/'
                        'best[height<=480][ext=mp4]/best[height<=480]'
                    )
                
                # Просто объединяем потоки БЕЗ конвертации
                ydl_opts['merge_output_format'] = 'mp4'
            
            if self.should_stop:
                return
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                
                if self.should_stop:
                    return
                    
                title = info.get('title', 'Video')
                self.finished.emit(title)
                
        except Exception as e:
            if not self.should_stop:
                self.error.emit(str(e))


class SettingsDialog(QDialog):
    """Диалоговое окно настроек"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle(self.tr('settings_title'))
        self.setFixedSize(400, 250)
        self.init_ui()
        
    def tr(self, key):
        """Получает перевод для текущего языка"""
        return TRANSLATIONS[self.parent_window.current_language].get(key, key)
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # === МУЗЫКА ===
        music_group = QGroupBox(self.tr('audio_settings'))
        music_layout = QVBoxLayout()
        
        self.music_checkbox = QCheckBox(self.tr('enable_music'))
        self.music_checkbox.setChecked(self.parent_window.music_enabled)
        self.music_checkbox.toggled.connect(self.toggle_music)
        music_layout.addWidget(self.music_checkbox)
        
        music_group.setLayout(music_layout)
        layout.addWidget(music_group)
        
        # === ЯЗЫК ===
        language_group = QGroupBox(self.tr('language_settings'))
        language_layout = QVBoxLayout()
        
        lang_label = QLabel(self.tr('language'))
        language_layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(['English', 'Русский', 'Українська'])
        
        # Устанавливаем текущий язык
        lang_index = {'en': 0, 'ru': 1, 'uk': 2}.get(self.parent_window.current_language, 0)
        self.language_combo.setCurrentIndex(lang_index)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        language_layout.addWidget(self.language_combo)
        
        language_group.setLayout(language_layout)
        layout.addWidget(language_group)
        
        # === КНОПКИ ===
        btn_layout = QHBoxLayout()
        
        close_btn = QPushButton(self.tr('close_btn'))
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.apply_dialog_style()
        
    def toggle_music(self, checked):
        self.parent_window.music_enabled = checked
        self.parent_window.save_settings()
        
        if checked:
            self.parent_window.play_background_music()
        else:
            self.parent_window.music_player.stop()
            
    def change_language(self, index):
        """Изменяет язык приложения"""
        lang_map = {0: 'en', 1: 'ru', 2: 'uk'}
        new_lang = lang_map.get(index, 'en')
        
        if new_lang != self.parent_window.current_language:
            self.parent_window.current_language = new_lang
            self.parent_window.save_settings()
            
            QMessageBox.information(
                self,
                self.tr('done_title'),
                "Please restart the application to apply language changes.\n"
                "Пожалуйста, перезапустите приложение для применения изменений.\n"
                "Будь ласка, перезапустіть програму для застосування змін."
            )
            
    def apply_dialog_style(self):
        self.setStyleSheet("""
            QDialog {
                background: #0A0A0A;
                color: #00FF00;
            }
            
            QGroupBox {
                color: #00FF00;
                border: 2px solid #3A3A3A;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            QLabel {
                color: #00FF00;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3A3A3A, stop:1 #1A1A1A);
                color: #00FF00;
                border: 2px outset #4A4A4A;
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A4A4A, stop:1 #2A2A2A);
            }
            
            QPushButton:pressed {
                border: 2px inset #4A4A4A;
            }
            
            QCheckBox {
                color: #00FF00;
                spacing: 5px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            
            QCheckBox::indicator::unchecked {
                background: #1A1A1A;
                border: 2px solid #3A3A3A;
            }
            
            QCheckBox::indicator::checked {
                background: #00FF00;
                border: 2px solid #00AA00;
            }
            
            QComboBox {
                background: #1A1A1A;
                color: #00FF00;
                border: 2px outset #3A3A3A;
                padding: 4px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #00FF00;
                margin-right: 5px;
            }
            
            QComboBox QAbstractItemView {
                background: #1A1A1A;
                color: #00FF00;
                selection-background-color: #00AA00;
            }
        """)


class YUdlDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.download_thread = None
        
        # Кроссплатформенный путь к Downloads
        home = os.path.expanduser('~')
        if sys.platform.startswith('win'):
            self.output_path = os.path.join(home, 'Downloads')
        else:
            # Linux может иметь Downloads или Загрузки
            download_path = os.path.join(home, 'Downloads')
            if not os.path.exists(download_path):
                download_path = os.path.join(home, 'Загрузки')
            self.output_path = download_path
        
        self.settings_file = os.path.join(home, '.yudl_settings.json')
        self.current_language = 'en'  # По умолчанию английский
        
        # Настройки музыки
        self.music_enabled = True
        self.music_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.music_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.15)  # Негромкая музыка
        self.music_player.setLoops(QMediaPlayer.Loops.Infinite)  # Зацикливание
        
        self.load_settings()
        self.init_ui()
        self.apply_style()
        self.play_background_music()
        
    def tr(self, key):
        """Получает перевод для текущего языка"""
        return TRANSLATIONS[self.current_language].get(key, key)
        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.music_enabled = settings.get('music', True)
                    self.output_path = settings.get('output_path', self.output_path)
                    self.current_language = settings.get('language', 'en')
        except:
            pass
    
    def save_settings(self):
        try:
            settings = {
                'music': self.music_enabled,
                'output_path': self.output_path,
                'language': self.current_language
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except:
            pass
        
    def init_ui(self):
        self.setWindowTitle(self.tr('app_title'))
        self.setFixedSize(500, 350)
        
        # === МЕНЮ ===
        menubar = self.menuBar()
        
        # Меню File
        file_menu = menubar.addMenu(self.tr('menu_file'))
        
        settings_action = QAction(self.tr('menu_settings'), self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(self.tr('menu_exit'), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Help
        help_menu = menubar.addMenu(self.tr('menu_help'))
        
        update_action = QAction(self.tr('menu_update'), self)
        update_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(update_action)
        
        help_menu.addSeparator()
        
        about_action = QAction(self.tr('menu_about'), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Основной виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Заголовок
        header = QLabel(self.tr('app_title'))
        header.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(30)
        header.setObjectName("header")
        layout.addWidget(header)
        
        # URL
        url_label = QLabel(self.tr('url_label'))
        layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(self.tr('url_placeholder'))
        self.url_input.setFixedHeight(28)
        layout.addWidget(self.url_input)
        
        # Формат
        format_layout = QHBoxLayout()
        
        self.video_radio = QRadioButton(self.tr('video'))
        self.video_radio.setChecked(True)
        self.video_radio.toggled.connect(self.on_format_changed)
        
        self.audio_radio = QRadioButton(self.tr('audio'))
        
        format_layout.addWidget(self.video_radio)
        format_layout.addWidget(self.audio_radio)
        format_layout.addStretch()
        
        layout.addLayout(format_layout)
        
        # Качество видео
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            self.tr('quality_best'),
            self.tr('quality_medium'),
            self.tr('quality_low')
        ])
        self.quality_combo.setFixedHeight(28)
        layout.addWidget(self.quality_combo)
        
        # Формат аудио
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems([
            'MP3',
            'WAV',
            'FLAC',
            'M4A'
        ])
        self.audio_format_combo.setFixedHeight(28)
        self.audio_format_combo.hide()  # Скрыто по умолчанию
        layout.addWidget(self.audio_format_combo)
        
        # Папка сохранения
        folder_layout = QHBoxLayout()
        
        folder_label = QLabel(self.tr('save_to'))
        folder_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        folder_layout.addWidget(folder_label)
        
        self.folder_display = QLabel(self.output_path)
        self.folder_display.setWordWrap(True)
        self.folder_display.setStyleSheet("color: #00FF00; font-size: 10px;")
        folder_layout.addWidget(self.folder_display, 1)
        
        self.folder_btn = QPushButton('...')
        self.folder_btn.setFixedSize(30, 24)
        self.folder_btn.clicked.connect(self.choose_folder)
        folder_layout.addWidget(self.folder_btn)
        
        layout.addLayout(folder_layout)
        
        # Дисплей
        self.display = QLabel(self.tr('ready'))
        self.display.setFont(QFont('Courier New', 10, QFont.Weight.Bold))
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display.setFixedHeight(35)
        self.display.setObjectName("display")
        layout.addWidget(self.display)
        
        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat('%p%')
        layout.addWidget(self.progress_bar)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.download_btn = QPushButton(self.tr('download_btn'))
        self.download_btn.setFixedHeight(32)
        self.download_btn.clicked.connect(self.start_download)
        buttons_layout.addWidget(self.download_btn)
        
        self.stop_btn = QPushButton(self.tr('stop_btn'))
        self.stop_btn.setFixedHeight(32)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_download)
        buttons_layout.addWidget(self.stop_btn)
        
        layout.addLayout(buttons_layout)
        
        main_widget.setLayout(layout)
        
    def open_settings(self):
        """Открывает окно настроек"""
        dialog = SettingsDialog(self)
        dialog.exec()
        
    def show_about(self):
        """Показывает информацию о программе"""
        QMessageBox.about(
            self,
            self.tr('about_title'),
            self.tr('about_text')
        )
    
    def check_for_updates(self):
        """Проверка обновлений"""
        dialog = UpdaterDialog(self)
        dialog.exec()
    
    def choose_folder(self):
        """Выбор папки для сохранения"""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.tr('select_folder'),
            self.output_path
        )
        
        if folder:
            self.output_path = folder
            self.folder_display.setText(folder)
            self.save_settings()
        
    def play_background_music(self):
        """Играет фоновую музыку из файла 1.wav"""
        if not self.music_enabled:
            return
            
        music_file = '1.wav'
        
        if os.path.exists(music_file):
            self.music_player.setSource(QUrl.fromLocalFile(os.path.abspath(music_file)))
            self.music_player.play()
        
    def on_format_changed(self):
        # Переключаем между видео и аудио
        if self.audio_radio.isChecked():
            self.quality_combo.hide()
            self.audio_format_combo.show()
        else:
            self.quality_combo.show()
            self.audio_format_combo.hide()
            
    def start_download(self):
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, self.tr('error_title'), self.tr('error_empty_url'))
            return
            
        if 'youtube.com' not in url and 'youtu.be' not in url:
            QMessageBox.warning(self, self.tr('error_title'), self.tr('error_invalid_url'))
            return
                
        format_type = 'audio' if self.audio_radio.isChecked() else 'video'
        
        # Получаем формат аудио или качество видео
        if format_type == 'audio':
            audio_format = self.audio_format_combo.currentText().lower()
            quality = 'best'
        else:
            audio_format = 'mp3'  # По умолчанию для видео
            quality_text = self.quality_combo.currentText()
            
            # Преобразуем текст в качество
            if 'Medium' in quality_text or 'Среднее' in quality_text or 'Середнє' in quality_text:
                quality = 'medium'
            elif 'Low' in quality_text or 'Низкое' in quality_text or 'Низьке' in quality_text:
                quality = 'low'
            else:
                quality = 'best'
        
        if not os.path.exists(self.output_path):
            try:
                os.makedirs(self.output_path)
            except:
                pass
        
        self.download_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.display.setText(self.tr('initializing'))
        
        self.download_thread = DownloadThread(url, quality, format_type, self.output_path, audio_format)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.error.connect(self.download_error)
        self.download_thread.start()
    
    def stop_download(self):
        """Остановка текущей загрузки"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait(2000)  # Ждем 2 секунды
            self.download_thread.terminate()  # Принудительная остановка
            
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.display.setText(self.tr('stopped'))
        self.progress_bar.setValue(0)
        
        QTimer.singleShot(2000, lambda: self.display.setText(self.tr('ready')))
        
    def update_progress(self, data):
        percent = data['percent']
        self.progress_bar.setValue(percent)
        
        if percent >= 95 and data['downloaded'] == 0:
            # Идет конвертация
            self.display.setText(self.tr('converting'))
        else:
            downloaded = data['downloaded'] / (1024 * 1024)
            self.display.setText(f'{downloaded:.1f} MB')
        
    def download_finished(self, title):
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.display.setText(self.tr('complete'))
        self.progress_bar.setValue(100)
        
        QMessageBox.information(self, self.tr('done_title'), title)
        
        QTimer.singleShot(2000, lambda: self.display.setText(self.tr('ready')))
        
    def download_error(self, error):
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.display.setText(self.tr('error'))
        
        QMessageBox.critical(self, self.tr('error_title'), error)
        
        QTimer.singleShot(2000, lambda: self.display.setText(self.tr('ready')))
        
    def apply_style(self):
        """Применяет стандартный стиль"""
        self.setStyleSheet("""
            QMainWindow {
                background: #0A0A0A;
            }
            
            QMenuBar {
                background: #1A1A1A;
                color: #00FF00;
                border-bottom: 1px solid #3A3A3A;
            }
            
            QMenuBar::item {
                background: transparent;
                padding: 4px 8px;
            }
            
            QMenuBar::item:selected {
                background: #2A2A2A;
            }
            
            QMenu {
                background: #1A1A1A;
                color: #00FF00;
                border: 1px solid #3A3A3A;
            }
            
            QMenu::item:selected {
                background: #00AA00;
            }
            
            QWidget {
                background: #0A0A0A;
                color: #00FF00;
            }
            
            #header {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3A3A3A, stop:0.5 #2A2A2A, stop:1 #1A1A1A);
                color: #00FF00;
                border: 2px outset #4A4A4A;
                border-radius: 3px;
            }
            
            QLabel {
                color: #00FF00;
            }
            
            QLineEdit {
                background: #1A1A1A;
                color: #00FF00;
                border: 2px inset #3A3A3A;
                padding: 4px;
            }
            
            QComboBox {
                background: #1A1A1A;
                color: #00FF00;
                border: 2px outset #3A3A3A;
                padding: 4px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #00FF00;
                margin-right: 5px;
            }
            
            QComboBox QAbstractItemView {
                background: #1A1A1A;
                color: #00FF00;
                selection-background-color: #00AA00;
            }
            
            QRadioButton {
                color: #00FF00;
            }
            
            QRadioButton::indicator {
                width: 13px;
                height: 13px;
            }
            
            QRadioButton::indicator::unchecked {
                background: #1A1A1A;
                border: 2px solid #3A3A3A;
                border-radius: 7px;
            }
            
            QRadioButton::indicator::checked {
                background: #00FF00;
                border: 2px solid #00AA00;
                border-radius: 7px;
            }
            
            #display {
                background: #000000;
                color: #00FF00;
                border: 3px inset #2A2A2A;
            }
            
            QProgressBar {
                background: #1A1A1A;
                border: 2px inset #2A2A2A;
                text-align: center;
                color: #00FF00;
                font-weight: bold;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #003300, stop:0.5 #00AA00, stop:1 #00FF00);
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3A3A3A, stop:1 #1A1A1A);
                color: #00FF00;
                border: 2px outset #4A4A4A;
                border-radius: 3px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A4A4A, stop:1 #2A2A2A);
            }
            
            QPushButton:pressed {
                border: 2px inset #4A4A4A;
            }
            
            QPushButton:disabled {
                background: #1A1A1A;
                color: #003300;
            }
        """)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YUdlDownloader()
    window.show()
    sys.exit(app.exec())