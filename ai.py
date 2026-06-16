from openai import OpenAI
from config import (
    AI_BACKEND, OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
)
from prompts import *

_clients = {}


def _get_client():
    if AI_BACKEND in _clients:
        return _clients[AI_BACKEND]
    if AI_BACKEND == "openrouter":
        client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
        _clients["openrouter"] = (client, OPENROUTER_MODEL)
    elif AI_BACKEND == "deepseek":
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        _clients["deepseek"] = (client, DEEPSEEK_MODEL)
    else:
        client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
        _clients["openrouter"] = (client, OPENROUTER_MODEL)
    return _clients.get(AI_BACKEND) or _clients.get("openrouter")


def chat(messages, max_tokens=1024, temperature=0.6):
    try:
        client, model = _get_client()
        resp = client.chat.completions.create(
            model=model, messages=messages,
            max_tokens=max_tokens, temperature=temperature,
        )
        return resp.choices[0].message.content
    except Exception as e:
        err = str(e)
        if "401" in err or "403" in err:
            return "Ошибка авторизации API. Проверь ключ в config.py."
        if "402" in err or "balance" in err.lower():
            return "Недостаточно средств."
        if "429" in err:
            return "Слишком много запросов. Подожди 30 секунд."
        return "ИИ временно недоступен. Попробуй через минуту."


def chat_stream(messages, max_tokens=1024, temperature=0.6):
    """Генератор: возвращает токены по мере генерации."""
    try:
        client, model = _get_client()
        stream = client.chat.completions.create(
            model=model, messages=messages,
            max_tokens=max_tokens, temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"\n[Ошибка: {str(e)[:100]}]"


def get_lesson(level, topic):
    prompt = LESSON_PROMPT.format(level=level, topic=topic)
    sys = SYSTEM_PROMPT.format(level=level, name="Student")
    return chat([{"role": "system", "content": sys}, {"role": "user", "content": prompt}], max_tokens=2000, temperature=0.5)


def chat_conversation(level, topic, history):
    sys = SYSTEM_PROMPT.format(level=level, name="Student")
    prompt = CHAT_PROMPT.format(level=level, topic=topic)
    messages = [{"role": "system", "content": sys + "\n\n" + prompt}]
    for h in history[-15:]:
        messages.append(h)
    return chat(messages, max_tokens=800, temperature=0.75)


def free_chat(level, message, history):
    sys = SYSTEM_PROMPT.format(level=level, name="Student")
    sys += "\nТы дружелюбный ИИ-собеседник. Общайся естественно. Исправляй ошибки мягко."
    messages = [{"role": "system", "content": sys}]
    for h in history[-15:]:
        messages.append(h)
    messages.append({"role": "user", "content": message})
    return chat(messages, max_tokens=800, temperature=0.75)


def free_chat_stream(level, message, history):
    sys = SYSTEM_PROMPT.format(level=level, name="Student")
    sys += "\nТы дружелюбный ИИ-собеседник. Общайся естественно. Исправляй ошибки мягко."
    messages = [{"role": "system", "content": sys}]
    for h in history[-15:]:
        messages.append(h)
    messages.append({"role": "user", "content": message})
    yield from chat_stream(messages, max_tokens=800, temperature=0.75)


def check_grammar(text, level):
    prompt = WRITING_PROMPT.format(text=text, level=level, task="грамматика")
    sys = SYSTEM_PROMPT.format(level=level, name="Student")
    return chat([{"role": "system", "content": sys}, {"role": "user", "content": prompt}], max_tokens=1000, temperature=0.4)


def evaluate_placement(score, total, wrong_topics, correct_topics):
    prompt = PLACEMENT_EVAL_PROMPT.format(
        score=score, total=total,
        wrong_topics=", ".join(wrong_topics) if wrong_topics else "нет",
        correct_topics=", ".join(correct_topics) if correct_topics else "нет"
    )
    return chat([
        {"role": "system", "content": "Ты эксперт CEFR. Отвечай на русском."},
        {"role": "user", "content": prompt}
    ], max_tokens=800, temperature=0.4)


def translate_text(text, level, direction="ru-en"):
    prompt = TRANSLATE_PROMPT.format(text=text, level=level, direction=direction)
    sys = SYSTEM_PROMPT.format(level=level, name="Student")
    return chat([{"role": "system", "content": sys}, {"role": "user", "content": prompt}], max_tokens=800, temperature=0.4)


def pronounce_help(text, level):
    prompt = PRONOUNCE_PROMPT.format(text=text, level=level)
    sys = SYSTEM_PROMPT.format(level=level, name="Student")
    return chat([{"role": "system", "content": sys}, {"role": "user", "content": prompt}], max_tokens=800, temperature=0.4)


def check_writing(text, level, task="свободная тема"):
    prompt = WRITING_PROMPT.format(text=text, level=level, task=task)
    sys = SYSTEM_PROMPT.format(level=level, name="Student")
    return chat([{"role": "system", "content": sys}, {"role": "user", "content": prompt}], max_tokens=1000, temperature=0.4)


def roleplay_chat(level, scenario, history):
    sys = SYSTEM_PROMPT.format(level=level, name="Student")
    prompt = ROLEPLAY_PROMPT.format(level=level, scenario=scenario)
    messages = [{"role": "system", "content": sys + "\n\n" + prompt}]
    for h in history[-10:]:
        messages.append(h)
    return chat(messages, max_tokens=800, temperature=0.8)


def get_vocab_exercise(level, topic="general"):
    prompt = f"""Создай упражнение на лексику для уровня {level}. Тема: {topic}.
Дай ровно 5 слов с английским словом [транскрипция], переводом, примером.
Затем 3 вопроса студенту."""
    sys = SYSTEM_PROMPT.format(level=level, name="Student")
    return chat([{"role": "system", "content": sys}, {"role": "user", "content": prompt}], max_tokens=800, temperature=0.6)


def daily_challenge(level):
    prompt = f"""Придумай ежедневное задание по английскому для студента уровня {level}.
Одно интересное задание на сегодня: может быть мини-тест, загадка, перевод фразы, исправление ошибок.
Сделай его увлекательным и полезным. Дай задание, подсказку и правильный ответ (скрытый)."""
    sys = SYSTEM_PROMPT.format(level=level, name="Student")
    return chat([{"role": "system", "content": sys}, {"role": "user", "content": prompt}], max_tokens=600, temperature=0.7)


def generate_quiz(topic, level, count=5):
    prompt = f"""Сгенерируй {count} вопросов теста по теме "{topic}" для студента уровня {level}.
Формат: ТОЛЬКО JSON массив объектов. Каждый объект: q (вопрос на русском), opts (массив из 4 вариантов ответа, один правильный), ans (индекс правильного ответа 0-3).
Не добавляй текст вне JSON. Пример:
[{{"q":"Как переводится слово 'cat'?","opts":["Собака","Кошка","Птица","Рыба"],"ans":1}}]"""
    sys = "Ты генерируешь тесты. Отвечай ТОЛЬКО JSON массивом. Без пояснений."
    return chat([{"role": "system", "content": sys}, {"role": "user", "content": prompt}], max_tokens=800, temperature=0.5)


def generate_level_test(level):
    prompt = f"""Сгенерируй 15 вопросов для проверки знания английского на уровне {level}.
Вопросы должны покрывать: грамматику уровня {level}, лексику уровня {level}, понимание прочитанного.
Формат: ТОЛЬКО JSON массив. Каждый объект: q (вопрос), opts (4 варианта), ans (индекс правильного 0-3).
Разнообразь вопросы: перевод слов, грамматика, понимание фраз, предлоги, времена.
Не добавляй текст вне JSON."""
    sys = "Ты генерируешь тесты CEFR. Отвечай ТОЛЬКО JSON. Без пояснений."
    return chat([{"role": "system", "content": sys}, {"role": "user", "content": prompt}], max_tokens=1500, temperature=0.5)
