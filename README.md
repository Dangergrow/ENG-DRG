# DRG ENG — Изучение английского языка с ИИ

Персональный ИИ-репетитор английского языка от A0 до C2. Desktop-приложение для Windows 10/11.

## Возможности

- **112 уроков** от алфавита до профессионального уровня (C2)
- **Разговорный клуб** с голосовым вводом и озвучкой (SpeechSynthesis)
- **11 обучающих игр**: Виселица, Пары слов, Блиц-квиз, Memory, Скоростной набор, Грам. защита, Word Rain, Собери предложение, Диктант, Охота на ошибки и др.
- **Тестирование** после каждого урока + экзамены на повышение уровня
- **Словарь** с интервальным повторением (алгоритм SM-2)
- **22 достижения** + система XP
- **Мульти-профили** для всей семьи
- **ИИ-учитель** через OpenRouter (бесплатные модели)
- **Нативное Windows-окно** (PyWebView + Edge WebView2)

## Установка

Скачай `DRGENG.exe` из [Releases](https://github.com/Dangergrow/ENG-DRG/releases).

Запусти — приложение откроется в собственном окне. Ни Python, ни браузер не нужны.

Данные сохраняются в папке `SaveDRG` рядом с `.exe`.

## Разработка

```bash
# Клонирование
git clone https://github.com/Dangergrow/ENG-DRG.git
cd ENG-DRG

# Установка зависимостей
pip install flask openai edge-tts pywebview pyinstaller

# Запуск в режиме разработки (браузер)
python main.py

# Запуск в режиме desktop (нативное окно)
python server.py

# Сборка в .exe
python make_icon.py   # Сгенерировать иконку
pyinstaller --clean --noconfirm DRGENG.spec
# Готовый .exe: dist/DRGENG.exe
```

## Структура проекта

```
├── server.py          # Точка входа (Flask + PyWebView)
├── main.py            # Точка входа (Flask + браузер)
├── app.py             # Flask-роуты
├── ai.py              # ИИ-интеграция (OpenRouter)
├── database.py        # SQLite + ORM
├── lessons.py         # 112 уроков
├── placement.py       # Placement test (30 вопросов)
├── prompts.py         # ИИ-промпты
├── config.py          # Конфигурация
├── tts.py             # Edge-TTS (резервный)
├── DRGENG.spec        # PyInstaller-спек
├── make_icon.py       # Генератор иконки
├── static/
│   ├── css/design-system.css
│   └── js/ (spring.js, particles.js, adaptive-theme.js, animated-icons.js, main.js)
├── templates/         # Jinja2-шаблоны
└── SaveDRG/           # Данные пользователя (создаётся автоматически)
```

## Автор

**Dangergrow** — [GitHub](https://github.com/Dangergrow)

## Лицензия

MIT
