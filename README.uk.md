# YUdl

[English](README.md) | **Українська**

![Version](https://img.shields.io/badge/version-1.0.1-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt-6-41CD52?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

**Завантажувач YouTube із графічним інтерфейсом.** Python + PyQt6 + yt-dlp.
Вставив посилання, вибрав формат, натиснув «Завантажити» — усе.

Версія **1.0.1** · автор **msx** · © 2026

## Можливості

- Просте вікно: посилання → Відео / Аудіо → якість або формат → прогрес.
- **Відео** — MP4 у якості Best, 720p або 480p.
- **Аудіо** — MP3 320 кбіт/с, WAV, FLAC або M4A.
- Смуга прогресу та кнопка **STOP**.
- Мови інтерфейсу: **English**, **Русский**, **Українська**.
- Перемикач фонової музики.
- FFmpeg уже лежить у папці `ffmpeg/` — нічого встановлювати вручну не треба.
- Вбудована перевірка оновлень із GitHub.
- Папку завантажень можна вибрати — програма її запам'ятовує.

## Вимоги

- Windows 10 / 11 (також працює на Linux і macOS)
- Python **3.8+**
- Підключення до інтернету

## Встановлення

### 1. Клонувати репозиторій

```bash
git clone https://github.com/RoboLask/YUdl
cd YUdl
```

### 2. Перевірити Python

```bash
python --version
```

Якщо Python немає — встанови з [python.org](https://www.python.org/downloads/)
і під час встановлення постав галочку **Add Python to PATH**.

### 3. Встановити залежності

```bash
pip install -r requirements.txt
```

Якщо `pip` не знайдено:

```bash
python -m pip install -r requirements.txt
```

### 4. Запустити

```bash
python main.py
```

На Windows можна просто двічі клікнути `main.py`.

На Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./run.sh
```

## Використання

1. Встав посилання YouTube у поле **URL**.
2. Вибери **Відео** або **Аудіо**.
3. Вибери якість (Best / 720p / 480p) або формат аудіо.
4. За потреби вибери папку — за замовчуванням це **Завантаження**.
5. Натисни **DOWNLOAD** і дочекайся завершення прогресу.

## Формати

| Тип | Варіанти | Примітки |
|---|---|---|
| Відео | Best, 720p, 480p | MP4, склеюється через FFmpeg |
| Аудіо | MP3 | 320 кбіт/с, грає всюди |
| Аудіо | WAV | без стиснення, великі файли |
| Аудіо | FLAC | без втрат |
| Аудіо | M4A | добре для iPhone / iTunes |

## Налаштування

Відкрий **File → Settings**:

- **Background music** — увімкнути або вимкнути вбудовану музику.
- **Language** — English, Русский або Українська.

Налаштування зберігаються у `~/.yudl_settings.json`:

```json
{
  "music": true,
  "output_path": "C:/Users/me/Downloads",
  "language": "en"
}
```

| Поле | Що задає | Варіанти |
|---|---|---|
| `music` | фонова музика | `true`, `false` |
| `output_path` | папка завантажень | будь-яка папка |
| `language` | мова інтерфейсу | `en`, `ru`, `uk` |

## Структура проєкту

```
main.py           вікно, логіка завантаження і переклади
updater.py        перевірка оновлень із GitHub
requirements.txt  залежності Python
run.sh            запуск на Linux / macOS (через venv)
1.wav             фонова музика
ffmpeg/           вбудовані бінарники FFmpeg
```

## Якщо щось не працює

**`python` не розпізнається**

Python не додано в `PATH`. Перевстанови з галочкою **Add Python to PATH**
або спробуй:

```bash
py main.py
```

**`pip` не розпізнається**

```bash
python -m pip install -r requirements.txt
```

**FFmpeg not found**

Перевір, що в папці `ffmpeg/bin/` є `ffmpeg.exe` і `ffprobe.exe`.

**Завантаження ніби застрягло на 95%**

Це нормально — FFmpeg конвертує файл. Зачекай хвилину-дві.

**Невірний URL YouTube**

Використовуй посилання виду `https://youtube.com/watch?v=...` або
`https://youtu.be/...`.

## Правове застереження

Програма призначена **лише для особистого використання**. Поважай умови
YouTube та авторське право. Ти відповідаєш за те, що завантажуєш.

---

© 2026 msx
