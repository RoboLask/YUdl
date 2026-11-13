"""Пошук і автоматичне завантаження FFmpeg.

Якщо FFmpeg немає поруч із програмою, він качається автоматично
(як у Go-версії yudl-tui-v1).

Джерела пробуються по порядку, поки одне з них не спрацює:

    Windows: yt-dlp/FFmpeg-Builds (GitHub), потім BtbN/FFmpeg-Builds
    Linux:   BtbN/FFmpeg-Builds (GitHub), потім johnvansickle.com
    macOS:   osxexperts.net
"""

import os
import sys
import shutil
import tarfile
import tempfile
import platform
import urllib.request
import zipfile


IS_WINDOWS = sys.platform.startswith('win')
IS_MAC = sys.platform == 'darwin'
EXE = '.exe' if IS_WINDOWS else ''
BINARIES = ('ffmpeg', 'ffprobe')


# ================= Шляхи =================

def app_dir():
    """Папка програми: поруч з .exe (PyInstaller) або з main.py."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def data_dir():
    """Папка для вбудованих ресурсів (1.wav) — _MEIPASS у onefile-збірці."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def ffmpeg_dir():
    return os.path.join(app_dir(), 'ffmpeg')


def resource_path(name):
    """Шлях до resource файлу поруч із програмою або розпакованого PyInstaller-ом."""
    local = os.path.join(app_dir(), name)
    if os.path.exists(local):
        return local
    return os.path.join(data_dir(), name)


def has_ffmpeg(folder):
    if not folder:
        return False
    return all(
        os.path.isfile(os.path.join(folder, name + EXE)) for name in BINARIES
    )


# ================= Пошук =================

def find_ffmpeg():
    """Шукає FFmpeg у кількох можливих місцях. Повертає папку або None."""
    base = app_dir()

    candidates = [
        os.path.join(base, 'ffmpeg', 'bin'),
        os.path.join(base, 'ffmpeg'),
        os.path.join(base, 'bin'),
        os.path.join(base),
    ]

    if IS_WINDOWS:
        candidates += [
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
            r"C:\Program Files (x86)\ffmpeg\bin",
        ]
    else:
        candidates += [
            '/usr/local/bin',
            '/usr/bin',
            '/opt/homebrew/bin',
            '/opt/local/bin',
        ]

    for folder in candidates:
        if has_ffmpeg(folder):
            return folder

    found = shutil.which('ffmpeg')
    if found:
        return os.path.dirname(os.path.abspath(found))

    return None


# ================= Джерела =================

def _arch():
    machine = platform.machine().lower()
    if machine in ('arm64', 'aarch64'):
        return 'arm64'
    return 'x86_64'


def sources():
    """Список (url, тип) — пробуються по порядку."""
    arm = _arch() == 'arm64'

    if IS_WINDOWS:
        suffix = 'winarm64' if arm else 'win64'
        return [
            (f"https://github.com/yt-dlp/FFmpeg-Builds/releases/latest/download/"
             f"ffmpeg-master-latest-{suffix}-gpl.zip", 'zip'),
            (f"https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/"
             f"ffmpeg-master-latest-{suffix}-gpl.zip", 'zip'),
        ]

    if IS_MAC:
        if arm:
            return [("https://www.osxexperts.net/ffmpeg71arm.zip", 'zip')]
        return [("https://www.osxexperts.net/ffmpeg71intel.zip", 'zip')]

    suffix = 'linuxarm64' if arm else 'linux64'
    static = 'arm64' if arm else 'amd64'
    return [
        (f"https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/"
         f"ffmpeg-master-latest-{suffix}-gpl.tar.xz", 'tar.xz'),
        (f"https://johnvansickle.com/ffmpeg/releases/"
         f"ffmpeg-release-{static}-static.tar.xz", 'tar.xz'),
    ]


# ================= Завантаження =================

def download_ffmpeg(progress=None):
    """Качає FFmpeg і кладе ffmpeg/ffprobe у папку ffmpeg/.

    progress(percent: int) викликається під час завантаження.
    Повертає папку з бінарниками.
    """
    target = ffmpeg_dir()
    os.makedirs(target, exist_ok=True)

    last_error = None
    for url, kind in sources():
        try:
            if progress:
                progress(0)
            tmp = _fetch(url, progress)
            try:
                if kind == 'zip':
                    _extract_zip(tmp, target)
                else:
                    _extract_tar_xz(tmp, target)
            finally:
                try:
                    os.remove(tmp)
                except OSError:
                    pass

            if has_ffmpeg(target):
                for name in BINARIES:
                    path = os.path.join(target, name + EXE)
                    if not IS_WINDOWS:
                        os.chmod(path, 0o755)
                return target

            last_error = f"{url}: у архіві немає ffmpeg/ffprobe"
        except Exception as exc:  # noqa: BLE001 — пробуємо наступне джерело
            last_error = f"{url}: {exc}"

    raise RuntimeError(f"Не вдалося завантажити FFmpeg.\n{last_error}")


def _fetch(url, progress=None):
    """Завантажує URL у тимчасовий файл, повідомляючи прогрес у відсотках."""
    request = urllib.request.Request(url, headers={'User-Agent': 'YUdl'})
    handle, path = tempfile.mkstemp(prefix='yudl-ffmpeg-')
    os.close(handle)

    with urllib.request.urlopen(request, timeout=60) as response, \
            open(path, 'wb') as out:
        total = int(response.headers.get('Content-Length') or 0)
        done = 0
        while True:
            chunk = response.read(262144)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)
            if progress and total:
                progress(min(int(done * 100 / total), 99))

    if progress:
        progress(100)
    return path


def _wanted(name):
    return os.path.basename(name) in {n + EXE for n in BINARIES}


def _extract_zip(archive, target):
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            if member.is_dir() or not _wanted(member.filename):
                continue
            name = os.path.basename(member.filename)
            with zf.open(member) as src, open(os.path.join(target, name), 'wb') as dst:
                shutil.copyfileobj(src, dst)


def _extract_tar_xz(archive, target):
    with tarfile.open(archive, 'r:xz') as tf:
        for member in tf:
            if not member.isfile() or not _wanted(member.name):
                continue
            name = os.path.basename(member.name)
            src = tf.extractfile(member)
            if src is None:
                continue
            with src, open(os.path.join(target, name), 'wb') as dst:
                shutil.copyfileobj(src, dst)


def ensure_ffmpeg(progress=None):
    """Повертає папку з FFmpeg, качаючи його за потреби."""
    folder = find_ffmpeg()
    if folder:
        return folder
    return download_ffmpeg(progress)
