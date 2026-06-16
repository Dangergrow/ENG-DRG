import os

# === AI Backend (настраивается через страницу входа) ===

def _read_key():
    key = _read_setting("apikey")
    return key or os.environ.get("OPENROUTER_API_KEY", "")

def _read_setting(name):
    import sys, json
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "SaveDRG", "settings.json")
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get(name, "")
    except:
        pass
    return ""

OPENROUTER_API_KEY = _read_key()
OPENROUTER_BASE_URL = _read_setting("base_url") or "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = _read_setting("model") or "openai/gpt-oss-120b:free"

# Устаревшие — оставлены для совместимости
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"
GIGACHAT_CLIENT_ID = os.environ.get("GIGACHAT_CLIENT_ID", "")
GIGACHAT_CLIENT_SECRET = os.environ.get("GIGACHAT_CLIENT_SECRET", "")
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"

DATABASE_PATH = "english_learn.db"
SECRET_KEY = os.environ.get("SECRET_KEY", "lingua-mate-default-key-change-in-production")
DEBUG = True
