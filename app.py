from flask import Flask, render_template, request, jsonify, session, send_file, Response, stream_with_context, redirect, url_for
from database import *
from ai import *
from placement import PLACEMENT_QUESTIONS, LEVEL_THRESHOLDS, calculate_level
from lessons import get_lessons_for_level, LEVEL_NAMES, LEVEL_ORDER, get_next_level, get_all_lessons
from config import SECRET_KEY, DEBUG
from tts import get_tts_audio_path
import json
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY
init_db()


@app.context_processor
def inject_globals():
    u = get_user(uid()) if uid() else None
    return {
        "users": get_users() if uid() else [],
        "has_level": u.get("level") is not None if u else False,
    }


def uid():
    """Возвращает ID текущего пользователя из сессии."""
    return session.get("user_id", 0)


def require_user():
    if not uid():
        return None
    return get_user(uid())


@app.before_request
def check_user():
    if uid() and request.endpoint not in ("static", "login_page", "api_login", "api_register"):
        u = get_user(uid())
        if u:
            update_streak(uid())


# === АВТОРИЗАЦИЯ ===

@app.route("/api/save_key", methods=["POST"])
def api_save_key():
    data = request.get_json()
    key = data.get("key", "").strip()
    base_url = data.get("base_url", "").strip() or "https://openrouter.ai/api/v1"
    model = data.get("model", "").strip() or "openai/gpt-oss-120b:free"

    if not key:
        return jsonify({"ok": False, "error": "Введи API-ключ"}), 400

    # Проверка ключа
    try:
        from openai import OpenAI
        test_client = OpenAI(api_key=key, base_url=base_url)
        test_client.chat.completions.create(model=model, messages=[{"role":"user","content":"hi"}], max_tokens=5)
    except Exception as e:
        err = str(e)
        if "401" in err or "403" in err: return jsonify({"ok":False,"error":"Неверный API-ключ"})
        if "404" in err or "model" in err.lower(): return jsonify({"ok":False,"error":f"Модель '{model}' не найдена"})
        return jsonify({"ok":False,"error":f"Ошибка: {err[:120]}"})

    # Сохраняем в SaveDRG/settings.json
    import sys, json
    if getattr(sys, 'frozen', False): base = os.path.dirname(sys.executable)
    else: base = os.path.dirname(os.path.abspath(__file__))
    savedir = os.path.join(base, "SaveDRG"); os.makedirs(savedir, exist_ok=True)
    settings = {"apikey": key, "base_url": base_url, "model": model}
    with open(os.path.join(savedir, "settings.json"), "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

    import config
    config.OPENROUTER_API_KEY = key
    config.OPENROUTER_BASE_URL = base_url
    config.OPENROUTER_MODEL = model

    return jsonify({"ok": True})


@app.route("/api/get_key")
def api_get_key():
    import sys, json
    if getattr(sys, 'frozen', False): base = os.path.dirname(sys.executable)
    else: base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "SaveDRG", "settings.json")
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return jsonify(json.load(f))
    except: pass
    return jsonify({"apikey": "", "base_url": "", "model": ""})


@app.route("/login")
def login_page():
    users = get_users()
    return render_template("login.html", users=users)


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Введи имя"}), 400
    user = get_user_by_name(name)
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    session["user_id"] = user["id"]
    return jsonify({"ok": True, "user": user})


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name or len(name) < 2:
        return jsonify({"error": "Имя должно быть не короче 2 символов"}), 400
    user = create_user(name)
    if not user:
        return jsonify({"error": "Пользователь с таким именем уже есть"}), 409
    session["user_id"] = user["id"]
    return jsonify({"ok": True, "user": user})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("user_id", None)
    return jsonify({"ok": True})


@app.route("/api/switch_user", methods=["POST"])
def api_switch():
    data = request.get_json()
    uid_new = data.get("user_id")
    if get_user(uid_new):
        session["user_id"] = uid_new
        return jsonify({"ok": True})
    return jsonify({"error": "Пользователь не найден"}), 404


@app.route("/api/delete_account", methods=["POST"])
def api_delete():
    u = require_user()
    if not u:
        return jsonify({"error": "Не авторизован"}), 401
    delete_user(uid())
    session.pop("user_id", None)
    return jsonify({"ok": True})


# === ГЛАВНАЯ ===

@app.route("/")
def index():
    u = require_user()
    if not u:
        return redirect("/login")
    stats = get_stats(uid())
    has_level = u.get("level") is not None and u.get("level") != "A1"
    lessons_list = get_lessons_for_level(u.get("level", "A1"))
    new_ach = check_achievements(uid())
    return render_template("index.html", user=u, stats=stats, has_level=has_level,
                           lessons=lessons_list, level_names=LEVEL_NAMES,
                           level_order=LEVEL_ORDER, all_lessons=get_all_lessons(),
                           new_achievements=new_ach)


# === PLACEMENT ===

@app.route("/placement")
def placement_page():
    u = require_user()
    if not u:
        return redirect("/login")
    return render_template("placement.html", questions=PLACEMENT_QUESTIONS, user=u)


@app.route("/api/placement/submit", methods=["POST"])
def placement_submit():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    answers = data.get("answers", {})
    score, wrong_topics, correct_topics = 0, [], []
    for q in PLACEMENT_QUESTIONS:
        qid = str(q["id"])
        ua = int(answers.get(qid, -1))
        if ua == q["ans"]:
            score += 1
            correct_topics.append(q["topic"])
        else:
            wrong_topics.append(q["topic"])

    total = len(PLACEMENT_QUESTIONS)
    level = calculate_level(score, total)
    update_user(uid(), level=level)

    ai_analysis = evaluate_placement(score, total, list(set(wrong_topics)), list(set(correct_topics)))
    if "недоступен" in ai_analysis.lower() or "ошибка" in ai_analysis.lower():
        pct = round(score / total * 100)
        ai_analysis = f"Уровень: {level} — {LEVEL_NAMES.get(level, level)}\nПравильных: {score}/{total} ({pct}%)\nНачни с уроков уровня {level}."

    add_xp(uid(), score * 5)
    check_achievements(uid())

    return jsonify({"score": score, "total": total, "level": level,
                    "level_name": LEVEL_NAMES.get(level, level), "analysis": ai_analysis})


# === УРОКИ (стриминг) ===

@app.route("/api/lesson/<lesson_id>")
def api_lesson(lesson_id):
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    all_lessons = get_all_lessons()
    lesson = None
    for items in all_lessons.values():
        for item in items:
            if item["id"] == lesson_id:
                lesson = item
                break
    if not lesson:
        return jsonify({"error": "Not found"}), 404

    stream = request.args.get("stream", "0") == "1"
    if stream:
        def generate():
            prompt = LESSON_PROMPT.format(level=u.get("level", "A1"), topic=lesson["topic"])
            sys = SYSTEM_PROMPT.format(level=u.get("level", "A1"), name=u.get("name", ""))
            full = []
            for token in chat_stream([{"role":"system","content":sys},{"role":"user","content":prompt}], max_tokens=2000, temperature=0.5):
                full.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True, 'full': ''.join(full), 'id': lesson['id'], 'title': lesson['title']})}\n\n"
        return Response(stream_with_context(generate()), mimetype="text/event-stream")
    else:
        content = get_lesson(u.get("level", "A1"), lesson["topic"])
        return jsonify({"id": lesson["id"], "title": lesson["title"], "level": u.get("level"), "content": content})


@app.route("/api/lesson/complete", methods=["POST"])
def lesson_complete():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    log_lesson(uid(), data.get("lesson_id"), data.get("title", ""),
               u.get("level", "A1"), data.get("score", 8), data.get("max_score", 10))
    check_achievements(uid())
    return jsonify({"ok": True})


# === КВИЗ ПОСЛЕ УРОКА ===

@app.route("/api/quiz/<lesson_id>")
def api_quiz(lesson_id):
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    all_lessons = get_all_lessons()
    lesson = None
    for items in all_lessons.values():
        for item in items:
            if item["id"] == lesson_id:
                lesson = item
                break
    if not lesson:
        return jsonify({"error": "Not found"}), 404
    quiz_json = generate_quiz(lesson["topic"], u.get("level", "A1"), 5)
    return jsonify({"quiz": quiz_json, "lesson_id": lesson_id, "title": lesson["title"]})


@app.route("/api/quiz/submit", methods=["POST"])
def api_quiz_submit():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    lesson_id = data.get("lesson_id", "")
    title = data.get("title", "")
    answers = data.get("answers", {})
    correct = data.get("correct", {})

    score = 0
    total = len(correct)
    for i in range(total):
        if str(answers.get(str(i), -1)) == str(correct.get(str(i), -1)):
            score += 1
    passed = score >= max(1, total - 1)

    if passed:
        log_lesson(uid(), lesson_id, title, u.get("level", "A1"), score * 2, total * 2)
        check_achievements(uid())

    return jsonify({"score": score, "total": total, "passed": passed})


# === ТЕСТ НА ПОВЫШЕНИЕ УРОВНЯ ===

@app.route("/api/levelup/test/<level>")
def api_levelup_test(level):
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    if level not in LEVEL_ORDER:
        return jsonify({"error": "Invalid level"}), 400
    quiz_json = generate_level_test(level)
    return jsonify({"quiz": quiz_json, "level": level, "level_name": LEVEL_NAMES.get(level, level)})


@app.route("/api/levelup/submit", methods=["POST"])
def api_levelup_submit():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    target_level = data.get("level", "")
    answers = data.get("answers", {})
    correct = data.get("correct", {})

    score = 0
    total = len(correct)
    for i in range(total):
        if str(answers.get(str(i), -1)) == str(correct.get(str(i), -1)):
            score += 1

    pct = (score / total * 100) if total > 0 else 0
    passed = pct >= 70

    if passed and target_level in LEVEL_ORDER:
        update_user(uid(), level=target_level)
        add_xp(uid(), 200)
        check_achievements(uid())

    return jsonify({"score": score, "total": total, "pct": round(pct),
                    "passed": passed, "level": target_level})


# === ИГРЫ ===

@app.route("/api/game/xp", methods=["POST"])
def api_game_xp():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    amount = data.get("amount", 0)
    add_xp(uid(), amount)
    check_achievements(uid())
    return jsonify({"ok": True, "xp": get_user(uid())["xp"]})


@app.route("/api/game/hangman")
def api_hangman():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    import random
    words = [
        {"word": "elephant", "hint": "Большое серое животное с хоботом"},
        {"word": "beautiful", "hint": "Очень красивый, привлекательный"},
        {"word": "adventure", "hint": "Захватывающее путешествие или опыт"},
        {"word": "chocolate", "hint": "Сладкое лакомство из какао"},
        {"word": "umbrella", "hint": "Предмет, который берут в дождь"},
        {"word": "computer", "hint": "Электронное устройство для работы и игр"},
        {"word": "mountain", "hint": "Очень высокий холм"},
        {"word": "sandwich", "hint": "Еда из двух кусков хлеба с начинкой"},
        {"word": "breakfast", "hint": "Первый приём пищи за день"},
        {"word": "hospital", "hint": "Место, куда едут лечиться"},
        {"word": "language", "hint": "Средство общения между людьми"},
        {"word": "kitchen", "hint": "Комната для приготовления еды"},
        {"word": "bicycle", "hint": "Двухколёсный транспорт без мотора"},
        {"word": "weather", "hint": "То, что показывают в прогнозе: дождь, солнце, снег"},
        {"word": "diamond", "hint": "Драгоценный камень, самый твёрдый минерал"},
        {"word": "penguin", "hint": "Птица, которая не летает, живёт в холоде"},
        {"word": "rainbow", "hint": "Семь цветов в небе после дождя"},
        {"word": "holiday", "hint": "Отпуск, каникулы, выходной"},
        {"word": "problem", "hint": "Трудность, задача, которую нужно решить"},
        {"word": "student", "hint": "Тот, кто учится в школе или университете"},
    ]
    w = random.choice(words)
    return jsonify({"word": w["word"], "hint": w["hint"], "length": len(w["word"])})


@app.route("/api/game/wordmatch")
def api_wordmatch():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    words = get_all_words(uid())
    if len(words) < 5:
        import random
        default = [
            {"word": "apple", "translation": "яблоко"},
            {"word": "house", "translation": "дом"},
            {"word": "water", "translation": "вода"},
            {"word": "school", "translation": "школа"},
            {"word": "friend", "translation": "друг"},
            {"word": "book", "translation": "книга"},
            {"word": "sun", "translation": "солнце"},
            {"word": "city", "translation": "город"},
        ]
        selected = random.sample(default, min(5, len(default)))
    else:
        import random
        selected = random.sample(words, min(8, len(words)))
        selected = [{"word": w["word"], "translation": w["translation"]} for w in selected]
    return jsonify({"pairs": selected})


# === ЧАТ (стриминг) ===

@app.route("/api/chat", methods=["POST"])
def api_chat():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    message = data.get("message", "")
    mode = data.get("mode", "free")
    stream = data.get("stream", False)

    save_chat(uid(), "user", message, mode)
    history = get_chat_history(uid(), 20)

    if stream:
        def generate():
            full = []
            if mode == "grammar":
                gen = chat_stream([{"role":"system","content":SYSTEM_PROMPT.format(level=u.get('level','A1'),name=u.get('name',''))},
                                   {"role":"user","content":WRITING_PROMPT.format(text=message,level=u.get('level','A1'),task="грамматика")}],
                                  max_tokens=1000, temperature=0.4)
            elif mode == "roleplay":
                gen = chat_stream([{"role":"system","content":SYSTEM_PROMPT.format(level=u.get('level','A1'),name=u.get('name','')) +
                                    "\n"+ROLEPLAY_PROMPT.format(level=u.get('level','A1'),scenario=data.get('scenario','restaurant'))}],
                                  max_tokens=800, temperature=0.8)
            else:
                gen = free_chat_stream(u.get("level", "A1"), message, history)
            for token in gen:
                full.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"
            reply = "".join(full)
            save_chat(uid(), "assistant", reply, mode)
            add_xp(uid(), 5)
            yield f"data: {json.dumps({'done': True, 'full': reply})}\n\n"
        return Response(stream_with_context(generate()), mimetype="text/event-stream")
    else:
        if mode == "grammar":
            reply = check_grammar(message, u.get("level", "A1"))
        elif mode == "topic":
            reply = chat_conversation(u.get("level", "A1"), data.get("topic", "everyday"), history)
        elif mode == "roleplay":
            reply = roleplay_chat(u.get("level", "A1"), data.get("scenario", "restaurant"), history)
        else:
            reply = free_chat(u.get("level", "A1"), message, history)

        save_chat(uid(), "assistant", reply, mode)
        add_xp(uid(), 5)
        check_achievements(uid())
        return jsonify({"reply": reply})


@app.route("/api/chat/history")
def chat_history():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    return jsonify({"history": get_chat_history(uid(), 50)})


@app.route("/api/chat/clear", methods=["POST"])
def chat_clear():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    clear_chat(uid())
    return jsonify({"ok": True})


# === ПЕРЕВОДЧИК ===

@app.route("/api/translate", methods=["POST"])
def api_translate():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    result = translate_text(data.get("text", ""), u.get("level", "A1"), data.get("direction", "ru-en"))
    add_xp(uid(), 3)
    return jsonify({"result": result})


# === ПРОИЗНОШЕНИЕ ===

@app.route("/api/pronounce", methods=["POST"])
def api_pronounce():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    result = pronounce_help(data.get("text", ""), u.get("level", "A1"))
    return jsonify({"result": result})


# === ПИСЬМО ===

@app.route("/api/writing", methods=["POST"])
def api_writing():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    result = check_writing(data.get("text", ""), u.get("level", "A1"), data.get("task", "свободная тема"))
    add_xp(uid(), 5)
    return jsonify({"result": result})


# === DAILY CHALLENGE ===

@app.route("/api/daily_challenge")
def api_daily():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    challenge = daily_challenge(u.get("level", "A1"))
    return jsonify({"challenge": challenge})


# === TTS (GET + POST) ===

@app.route("/api/tts", methods=["GET", "POST"])
def api_tts():
    if request.method == "POST":
        data = request.get_json() or {}
        text = data.get("text", "")
        voice = data.get("voice")
    else:
        text = request.args.get("text", "")
        voice = request.args.get("voice")
    if not text:
        return jsonify({"error": "no text"}), 400
    try:
        mp3_path = get_tts_audio_path(text, voice)
        return send_file(mp3_path, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === СЛОВАРЬ (CRUD) ===

@app.route("/api/vocab/add", methods=["POST"])
def vocab_add():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    add_word(uid(), data.get("word"), data.get("translation"),
             data.get("example", ""), data.get("level", u.get("level", "A1")))
    return jsonify({"ok": True})


@app.route("/api/vocab/update", methods=["POST"])
def vocab_update():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    update_word(data.get("id"), uid(), **{k: v for k, v in data.items() if k != "id" and v})
    return jsonify({"ok": True})


@app.route("/api/vocab/delete", methods=["POST"])
def vocab_delete():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    delete_word(data.get("id"), uid())
    return jsonify({"ok": True})


@app.route("/api/vocab/due")
def vocab_due():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    return jsonify({"words": get_words_due(uid(), 20)})


@app.route("/api/vocab/all")
def vocab_all():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    return jsonify({"words": get_all_words(uid())})


@app.route("/api/vocab/review", methods=["POST"])
def vocab_review():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    update_word_review(data.get("word_id"), data.get("quality", 0))
    add_xp(uid(), 2)
    return jsonify({"ok": True})


@app.route("/api/vocab/generate", methods=["POST"])
def vocab_generate():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    exercise = get_vocab_exercise(u.get("level", "A1"), data.get("topic", "general"))
    return jsonify({"exercise": exercise})


# === СТАТИСТИКА ===

@app.route("/api/profile/history")
def api_profile_history():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    conn = get_db()
    recent_lessons = conn.execute(
        "SELECT lesson_title, level, score, max_score, created_at FROM lessons_log WHERE user_id=? AND completed=1 ORDER BY created_at DESC LIMIT 10"
    , (uid(),)).fetchall()
    recent_chats = conn.execute(
        "SELECT COUNT(*) as cnt, mode FROM chat_history WHERE user_id=? AND role='user' GROUP BY mode ORDER BY cnt DESC"
    , (uid(),)).fetchall()
    achievements_list = conn.execute(
        "SELECT achievement_id, unlocked_at FROM achievements WHERE user_id=? ORDER BY unlocked_at DESC"
    , (uid(),)).fetchall()
    xp_total = u.get('xp', 0)
    level = u.get('level')
    conn.close()
    return jsonify({
        "lessons": [dict(r) for r in recent_lessons],
        "chat_modes": [dict(r) for r in recent_chats],
        "achievements": [dict(r) for r in achievements_list],
        "xp": xp_total,
        "level": level,
        "name": u['name'],
        "streak": u['streak'],
        "words": get_stats(uid())['words_total'],
        "mastered": get_stats(uid())['words_mastered'],
    })
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    return jsonify({"stats": get_stats(uid()), "progress": get_lesson_progress(uid())})


@app.route("/api/user/set_level", methods=["POST"])
def set_level():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    level = data.get("level")
    if level in LEVEL_ORDER:
        update_user(uid(), level=level)
        return jsonify({"ok": True})
    return jsonify({"error": "Invalid level"}), 400


@app.route("/api/user/rename", methods=["POST"])
def rename_user():
    u = require_user()
    if not u:
        return jsonify({"error": "Auth"}), 401
    data = request.get_json()
    new_name = data.get("name", "").strip()
    if not new_name or len(new_name) < 2:
        return jsonify({"error": "Имя слишком короткое"}), 400
    existing = get_user_by_name(new_name)
    if existing and existing["id"] != uid():
        return jsonify({"error": "Имя занято"}), 409
    update_user(uid(), name=new_name)
    return jsonify({"ok": True})


# === СТРАНИЦЫ ===

@app.route("/lessons")
def lessons_page():
    u = require_user()
    if not u:
        return redirect("/login")
    return render_template("lessons.html", user=u, lessons=get_lessons_for_level(u.get("level", "A1")),
                           level=u.get("level", "A1"), level_names=LEVEL_NAMES,
                           level_order=LEVEL_ORDER, all_lessons=get_all_lessons())


@app.route("/chat")
def chat_page():
    u = require_user()
    if not u:
        return redirect("/login")
    return render_template("chat.html", user=u, fullpage_mode=True)


@app.route("/translate")
def translate_page():
    u = require_user()
    if not u:
        return redirect("/login")
    return render_template("translate.html", user=u)


@app.route("/pronounce")
def pronounce_page():
    u = require_user()
    if not u:
        return redirect("/login")
    return render_template("pronounce.html", user=u)


@app.route("/writing")
def writing_page():
    u = require_user()
    if not u:
        return redirect("/login")
    return render_template("writing.html", user=u)


@app.route("/vocab")
def vocab_page():
    u = require_user()
    if not u:
        return redirect("/login")
    words = get_all_words(uid())
    tab = request.args.get("tab", "active")
    return render_template("vocab.html", user=u, words=words, tab=tab)


@app.route("/stats")
def stats_page():
    u = require_user()
    if not u:
        return redirect("/login")
    return render_template("stats.html", user=u, stats=get_stats(uid()))


@app.route("/levelup")
def levelup_page():
    u = require_user()
    if not u:
        return redirect("/login")
    return render_template("levelup.html", user=u, level_order=LEVEL_ORDER,
                           level_names=LEVEL_NAMES, current_level=u.get("level", "A1"))


@app.route("/games")
def games_page():
    u = require_user()
    if not u:
        return redirect("/login")
    return render_template("games.html", user=u)


@app.route("/about")
def about_page():
    u = require_user()
    if not u:
        return redirect("/login")
    return render_template("about.html", user=u)


if __name__ == "__main__":
    app.run(debug=DEBUG, host="127.0.0.1", port=5000)
