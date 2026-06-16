"""
DRG ENG v1.0.0 — Desktop приложение для изучения английского языка
Автор: Dangergrow
Запуск: python server.py
"""
import sys, os, threading, time, json, shutil, logging, traceback
from datetime import datetime

# ═══ Сохранения в папке SaveDRG рядом с .exe ═══
def save_dir():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(base, 'SaveDRG')
    os.makedirs(d, exist_ok=True)
    return d

def save_json(filename, data):
    path = os.path.join(save_dir(), filename)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"Save failed: {filename} — {e}")
        return False

def load_json(filename, default=None):
    path = os.path.join(save_dir(), filename)
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Load failed: {filename} — {e}")
        return default

# ═══ Логирование ═══
logging.basicConfig(
    filename=os.path.join(save_dir(), 'error.log'),
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# ═══ Flask-сервер ═══
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.serving import make_server

flask_app = Flask(__name__, static_folder='static', template_folder='templates')

# Импорт модулей приложения
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Подменяем путь к БД — всегда в SaveDRG
import config
config.DATABASE_PATH = os.path.join(save_dir(), 'linguamate.db')

# Также переопределяем для прямого импорта
import database as db_mod
db_mod.DATABASE_PATH = config.DATABASE_PATH

# Инициализация БД
db_mod.init_db()

# Импорт приложения ПОСЛЕ установки пути БД
from app import app as main_app
flask_app = main_app

# ═══ API для JSON-сохранений ═══
@flask_app.route('/api/save', methods=['POST'])
def api_save():
    data = request.get_json()
    filename = request.args.get('file', 'profile')
    if not filename.endswith('.json'):
        filename += '.json'
    success = save_json(filename, data)
    return jsonify({'ok': success})

@flask_app.route('/api/load')
def api_load():
    filename = request.args.get('file', 'profile')
    if not filename.endswith('.json'):
        filename += '.json'
    data = load_json(filename, {})
    return jsonify(data)

@flask_app.route('/api/backup', methods=['POST'])
def api_backup():
    """Создаёт резервную копию БД в SaveDRG"""
    import shutil
    src = _get_db_path()
    if os.path.exists(src):
        dst = os.path.join(save_dir(), f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        shutil.copy2(src, dst)
        return jsonify({'ok': True, 'path': dst})
    return jsonify({'ok': False, 'error': 'DB not found'})

# ═══ Запуск сервера и окна ═══
def find_free_port(start=8080, end=8090):
    import socket
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return 8080

def run_flask(port):
    server = make_server('127.0.0.1', port, flask_app)
    server.serve_forever()

def main():
    port = find_free_port()
    url = f'http://127.0.0.1:{port}'

    # Запускаем Flask в фоне
    flask_thread = threading.Thread(target=run_flask, args=(port,), daemon=True)
    flask_thread.start()
    time.sleep(0.5)

    # ═══ PyWebView — нативное окно ═══
    try:
        import webview
        # Генерируем простую иконку если её нет
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.ico')

        def on_closing():
            """Подтверждение закрытия + автосохранение"""
            try:
                import requests
                requests.post(f'{url}/api/backup', timeout=2)
            except:
                pass
            return True  # Разрешаем закрыть

        window = webview.create_window(
            title='DRG ENG v1.0.0 — Изучение английского',
            url=url,
            width=1280,
            height=820,
            min_size=(360, 600),
            resizable=True,
            fullscreen=False,
            frameless=False,
            easy_drag=True,
            confirm_close=True,
            background_color='#050814',
        )

        # Привязываем событие закрытия
        window.events.closing += on_closing

        webview.start(gui='edgechromium' if os.name == 'nt' else 'gtk', debug=False)

    except Exception as e:
        logging.error(f"WebView failed: {e}")
        print(f"\n{'='*50}")
        print("⚠️  Не удалось открыть окно приложения.")
        print(f"   Ошибка: {e}")
        print(f"   Открываю в браузере: {url}")
        print(f"{'='*50}\n")
        import webbrowser
        webbrowser.open(url)
        flask_thread.join()

if __name__ == '__main__':
    main()
