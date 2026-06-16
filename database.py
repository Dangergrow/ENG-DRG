import sqlite3
from datetime import datetime, date
from config import DATABASE_PATH


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            level TEXT DEFAULT NULL,
            xp INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            last_active TEXT DEFAULT (date('now')),
            total_minutes INTEGER DEFAULT 0,
            words_learned INTEGER DEFAULT 0,
            lessons_done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS placement_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            level TEXT NOT NULL,
            details TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            translation TEXT NOT NULL,
            example TEXT DEFAULT '',
            level TEXT DEFAULT 'A1',
            status TEXT DEFAULT 'new',
            ease_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 0,
            next_review TEXT DEFAULT (date('now')),
            correct_count INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, word)
        );

        CREATE TABLE IF NOT EXISTS lessons_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_id TEXT NOT NULL,
            lesson_title TEXT NOT NULL,
            level TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            max_score INTEGER DEFAULT 10,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            mode TEXT DEFAULT 'free',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            minutes_studied INTEGER DEFAULT 0,
            words_reviewed INTEGER DEFAULT 0,
            lessons_completed INTEGER DEFAULT 0,
            xp_earned INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, date)
        );

        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_id TEXT NOT NULL,
            unlocked_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, achievement_id)
        );

        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            tts_enabled INTEGER DEFAULT 1,
            tts_voice_en TEXT DEFAULT 'en-US-AriaNeural',
            tts_voice_ru TEXT DEFAULT 'ru-RU-SvetlanaNeural',
            daily_goal_minutes INTEGER DEFAULT 15,
            daily_goal_words INTEGER DEFAULT 10,
            theme TEXT DEFAULT 'dark',
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


# === ПОЛЬЗОВАТЕЛИ ===

def get_users():
    conn = get_db()
    rows = conn.execute("SELECT id, name, level, xp, streak FROM users ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_name(name):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE name=?", (name,)).fetchone()
    conn.close()
    return dict(user) if user else None


def create_user(name):
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE name=?", (name,)).fetchone()
        uid = user['id']
        conn.execute("INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)", (uid,))
        conn.commit()
        conn.close()
        return dict(user)
    except sqlite3.IntegrityError:
        conn.close()
        return None


def update_user(user_id, **kwargs):
    conn = get_db()
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    conn.execute(f"UPDATE users SET {fields} WHERE id=?", values)
    conn.commit()
    conn.close()


def delete_user(user_id):
    conn = get_db()
    conn.execute("DELETE FROM chat_history WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM vocabulary WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM lessons_log WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM daily_stats WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM achievements WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM user_settings WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM placement_results WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def add_xp(user_id, amount):
    conn = get_db()
    conn.execute("UPDATE users SET xp = xp + ? WHERE id=?", (amount, user_id))
    conn.commit()
    conn.close()


def get_user_settings(user_id):
    conn = get_db()
    s = conn.execute("SELECT * FROM user_settings WHERE user_id=?", (user_id,)).fetchone()
    if not s:
        conn.execute("INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)", (user_id,))
        conn.commit()
        s = conn.execute("SELECT * FROM user_settings WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(s) if s else {}


def update_settings(user_id, **kwargs):
    conn = get_db()
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    conn.execute(f"UPDATE user_settings SET {fields} WHERE user_id=?", values)
    conn.commit()
    conn.close()


# === СЛОВАРЬ ===

def add_word(user_id, word, translation, example="", level="A1"):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO vocabulary (user_id, word, translation, example, level) VALUES (?,?,?,?,?)",
            (user_id, word, translation, example, level)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()


def update_word(word_id, user_id, **kwargs):
    conn = get_db()
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [word_id, user_id]
    conn.execute(f"UPDATE vocabulary SET {fields} WHERE id=? AND user_id=?", values)
    conn.commit()
    conn.close()


def delete_word(word_id, user_id):
    conn = get_db()
    conn.execute("DELETE FROM vocabulary WHERE id=? AND user_id=?", (word_id, user_id))
    conn.commit()
    conn.close()


def get_words_due(user_id, limit=20):
    conn = get_db()
    today = date.today().isoformat()
    words = conn.execute(
        "SELECT * FROM vocabulary WHERE user_id=? AND next_review <= ? ORDER BY next_review ASC LIMIT ?",
        (user_id, today, limit)
    ).fetchall()
    conn.close()
    return [dict(w) for w in words]


def get_all_words(user_id):
    conn = get_db()
    words = conn.execute(
        "SELECT * FROM vocabulary WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(w) for w in words]


def update_word_review(word_id, quality):
    conn = get_db()
    word = conn.execute("SELECT * FROM vocabulary WHERE id=?", (word_id,)).fetchone()
    if not word:
        conn.close()
        return
    w = dict(word)
    ease, interval, correct, wrong = w['ease_factor'], w['interval_days'], w['correct_count'], w['wrong_count']

    if quality >= 3:
        interval = 1 if interval == 0 else (6 if interval == 1 else round(interval * ease))
        correct += 1
    else:
        interval, wrong = 1, wrong + 1

    ease = max(1.3, ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    next_review = date.today().isoformat() if interval == 0 else (
        date.today().replace(day=date.today().day + interval).isoformat()
    )
    status = 'mastered' if interval >= 21 else 'learning'

    conn.execute(
        "UPDATE vocabulary SET ease_factor=?, interval_days=?, next_review=?, correct_count=?, wrong_count=?, status=? WHERE id=?",
        (ease, interval, next_review, correct, wrong, status, word_id)
    )
    conn.commit()
    conn.close()


# === УРОКИ ===

def log_lesson(user_id, lesson_id, title, level, score=0, max_score=10, completed=1):
    conn = get_db()
    conn.execute(
        "INSERT INTO lessons_log (user_id, lesson_id, lesson_title, level, score, max_score, completed) VALUES (?,?,?,?,?,?,?)",
        (user_id, lesson_id, title, level, score, max_score, completed)
    )
    conn.commit()
    done = conn.execute("SELECT COUNT(*) FROM lessons_log WHERE user_id=? AND completed=1", (user_id,)).fetchone()[0]
    update_user(user_id, lessons_done=done)
    add_xp(user_id, score * 2)
    conn.close()


# === ЧАТ ===

def save_chat(user_id, role, content, mode="free"):
    conn = get_db()
    conn.execute(
        "INSERT INTO chat_history (user_id, role, content, mode) VALUES (?,?,?,?)",
        (user_id, role, content, mode)
    )
    conn.commit()
    conn.close()


def get_chat_history(user_id, limit=30):
    conn = get_db()
    rows = conn.execute(
        "SELECT role, content FROM chat_history WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def clear_chat(user_id):
    conn = get_db()
    conn.execute("DELETE FROM chat_history WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


# === СТАТИСТИКА ===

def get_stats(user_id):
    conn = get_db()
    user = get_user(user_id)
    total = conn.execute("SELECT COUNT(*) FROM vocabulary WHERE user_id=?", (user_id,)).fetchone()[0]
    mastered = conn.execute("SELECT COUNT(*) FROM vocabulary WHERE user_id=? AND status='mastered'", (user_id,)).fetchone()[0]
    lessons = conn.execute("SELECT COUNT(*) FROM lessons_log WHERE user_id=? AND completed=1", (user_id,)).fetchone()[0]
    chats = conn.execute("SELECT COUNT(*) FROM chat_history WHERE user_id=? AND role='user'", (user_id,)).fetchone()[0]
    conn.close()
    return {
        "words_total": total, "words_mastered": mastered,
        "lessons_completed": lessons, "total_messages": chats,
        "streak": user['streak'], "total_minutes": user['total_minutes'],
        "level": user['level'] or 'Not set', "xp": user['xp'] or 0,
    }


def get_lesson_progress(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT lesson_id, score, max_score FROM lessons_log WHERE user_id=? AND completed=1", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_streak(user_id):
    user = get_user(user_id)
    if not user:
        return 0
    today = date.today().isoformat()
    last = user['last_active']
    if last == today:
        return user['streak']
    yesterday = date.today().replace(day=date.today().day - 1).isoformat()
    new_streak = user['streak'] + 1 if last == yesterday else 1
    update_user(user_id, streak=new_streak, last_active=today)
    return new_streak


def check_achievements(user_id):
    s = get_stats(user_id)
    u = get_user(user_id)
    achieved = []
    checks = [
        ("streak_3", s['streak'] >= 3),
        ("streak_7", s['streak'] >= 7),
        ("streak_14", s['streak'] >= 14),
        ("streak_30", s['streak'] >= 30),
        ("words_10", s['words_total'] >= 10),
        ("words_50", s['words_total'] >= 50),
        ("words_100", s['words_total'] >= 100),
        ("mastered_10", s['words_mastered'] >= 10),
        ("mastered_30", s['words_mastered'] >= 30),
        ("mastered_100", s['words_mastered'] >= 100),
        ("lessons_1", s['lessons_completed'] >= 1),
        ("lessons_5", s['lessons_completed'] >= 5),
        ("lessons_10", s['lessons_completed'] >= 10),
        ("lessons_25", s['lessons_completed'] >= 25),
        ("chats_10", s['total_messages'] >= 10),
        ("chats_50", s['total_messages'] >= 50),
        ("chats_100", s['total_messages'] >= 100),
        ("xp_100", s['xp'] >= 100),
        ("xp_500", s['xp'] >= 500),
        ("xp_2000", s['xp'] >= 2000),
        ("level_b1", u['level'] in ('B1','B2','C1','C2') if u else False),
        ("level_c1", u['level'] in ('C1','C2') if u else False),
    ]
    conn = get_db()
    for aid, cond in checks:
        if cond:
            try:
                conn.execute("INSERT OR IGNORE INTO achievements (user_id, achievement_id) VALUES (?,?)", (user_id, aid))
                if conn.changes: achieved.append(aid)
            except: pass
    conn.commit()
    conn.close()
    if achieved: add_xp(user_id, len(achieved) * 50)
    return achieved
