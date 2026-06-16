"""Edge-TTS: быстрая озвучка с автоопределением языка."""
import asyncio, tempfile, os, concurrent.futures, re, hashlib

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

VOICE_EN_DEFAULT = "en-US-AriaNeural"
VOICE_RU = "ru-RU-SvetlanaNeural"

_cache_dir = os.path.join(tempfile.gettempdir(), "linguamate_tts")
os.makedirs(_cache_dir, exist_ok=True)


def _detect_lang(text):
    cyrillic = len(re.findall(r'[а-яёА-ЯЁ]', text))
    latin = len(re.findall(r'[a-zA-Z]', text))
    return 'ru' if cyrillic > latin else 'en'


def _gen_tts(text, voice, output_path):
    async def _run():
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
    asyncio.run(_run())


def speak(text, voice_en=None):
    lang = _detect_lang(text)
    if lang == 'ru':
        voice = VOICE_RU
    else:
        voice = voice_en or VOICE_EN_DEFAULT

    key = hashlib.md5((text + voice).encode()).hexdigest()
    cache_path = os.path.join(_cache_dir, key + ".mp3")

    if os.path.exists(cache_path):
        return cache_path

    fd, temp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    _executor.submit(_gen_tts, text, voice, temp_path).result(timeout=25)

    try:
        os.replace(temp_path, cache_path)
    except OSError:
        pass
    return cache_path


def get_tts_audio_path(text, voice_en=None):
    return speak(text, voice_en)
