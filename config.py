import os

# === AI Backend ===
AI_BACKEND = "openrouter"

def _read_key():
    # Ключ из файла apikey.txt (рядом с .exe или .py)
    import sys
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    keyfile = os.path.join(base, "apikey.txt")
    if os.path.exists(keyfile):
        with open(keyfile, "r") as f:
            return f.read().strip()
    return os.environ.get("OPENROUTER_API_KEY", "")

OPENROUTER_API_KEY = _read_key()
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "openai/gpt-oss-120b:free"

# DeepSeek (платный)
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# GigaChat (Сбер)
GIGACHAT_CLIENT_ID = os.environ.get("GIGACHAT_CLIENT_ID", "")
GIGACHAT_CLIENT_SECRET = os.environ.get("GIGACHAT_CLIENT_SECRET", "")
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"

DATABASE_PATH = "english_learn.db"
SECRET_KEY = os.environ.get("SECRET_KEY", "lingua-mate-default-key-change-in-production")
DEBUG = True
