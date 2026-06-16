"""LinguaMate — точка входа. Запускает сервер и открывает браузер."""
import sys
import os
import threading
import webbrowser
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import app

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    if not getattr(sys, 'frozen', False):
        threading.Thread(target=open_browser, daemon=True).start()
        app.run(host="127.0.0.1", port=5000, debug=False)
    else:
        threading.Thread(target=open_browser, daemon=True).start()
        app.run(host="127.0.0.1", port=5000, debug=False)
