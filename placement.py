PLACEMENT_QUESTIONS = [
    # A0 (6 вопросов)
    {"id": 1, "topic": "Лексика", "level": "A0", "q": "What is the English word for 'кошка'?", "opts": ["Dog", "Cat", "Bird", "Fish"], "ans": 1},
    {"id": 2, "topic": "Лексика", "level": "A0", "q": "How do you say 'Привет' in English?", "opts": ["Goodbye", "Hello", "Sorry", "Please"], "ans": 1},
    {"id": 3, "topic": "Числа", "level": "A0", "q": "What number is 'seven'?", "opts": ["5", "6", "7", "8"], "ans": 2},
    {"id": 4, "topic": "Лексика", "level": "A0", "q": "What colour is the sky on a clear day?", "opts": ["Red", "Green", "Blue", "Yellow"], "ans": 2},
    {"id": 5, "topic": "Лексика", "level": "A0", "q": "'Dog' — это ...", "opts": ["Кошка", "Собака", "Птица", "Рыба"], "ans": 1},
    {"id": 6, "topic": "Лексика", "level": "A0", "q": "Как переводится 'water'?", "opts": ["Хлеб", "Молоко", "Вода", "Сок"], "ans": 2},

    # A1 (7 вопросов)
    {"id": 7, "topic": "Грамматика", "level": "A1", "q": "___ am a student.", "opts": ["He", "I", "They", "We"], "ans": 1},
    {"id": 8, "topic": "Грамматика", "level": "A1", "q": "She ___ a doctor.", "opts": ["am", "is", "are", "be"], "ans": 1},
    {"id": 9, "topic": "Грамматика", "level": "A1", "q": "He ___ to school every day.", "opts": ["go", "goes", "going", "went"], "ans": 1},
    {"id": 10, "topic": "Грамматика", "level": "A1", "q": "___ you like coffee?", "opts": ["Does", "Do", "Is", "Are"], "ans": 1},
    {"id": 11, "topic": "Предлоги", "level": "A1", "q": "The book is ___ the table.", "opts": ["at", "in", "on", "by"], "ans": 2},
    {"id": 12, "topic": "Лексика", "level": "A1", "q": "I ___ a new car. (у меня есть)", "opts": ["have", "has", "am", "is"], "ans": 0},
    {"id": 13, "topic": "Грамматика", "level": "A1", "q": "There ___ two cats in the room.", "opts": ["is", "are", "am", "be"], "ans": 1},

    # A2 (6 вопросов)
    {"id": 14, "topic": "Грамматика", "level": "A2", "q": "Yesterday I ___ to the cinema.", "opts": ["go", "goes", "went", "gone"], "ans": 2},
    {"id": 15, "topic": "Грамматика", "level": "A2", "q": "She ___ her homework last night.", "opts": ["do", "does", "did", "done"], "ans": 2},
    {"id": 16, "topic": "Грамматика", "level": "A2", "q": "Tomorrow we ___ visit our grandma.", "opts": ["go", "will", "are", "have"], "ans": 1},
    {"id": 17, "topic": "Грамматика", "level": "A2", "q": "This car is ___ than that one.", "opts": ["fast", "faster", "fastest", "more fast"], "ans": 1},
    {"id": 18, "topic": "Модальные", "level": "A2", "q": "You ___ smoke here. It's forbidden.", "opts": ["can", "must", "mustn't", "should"], "ans": 2},
    {"id": 19, "topic": "Грамматика", "level": "A2", "q": "Look! It ___ outside.", "opts": ["rains", "rained", "is raining", "will rain"], "ans": 2},

    # B1 (6 вопросов)
    {"id": 20, "topic": "Грамматика", "level": "B1", "q": "I ___ never been to London.", "opts": ["has", "have", "had", "having"], "ans": 1},
    {"id": 21, "topic": "Грамматика", "level": "B1", "q": "If it rains, I ___ at home.", "opts": ["stay", "stayed", "will stay", "would stay"], "ans": 2},
    {"id": 22, "topic": "Лексика", "level": "B1", "q": "I need to ___ up smoking.", "opts": ["take", "give", "put", "get"], "ans": 1},
    {"id": 23, "topic": "Грамматика", "level": "B1", "q": "The letter ___ yesterday.", "opts": ["sent", "was sent", "is sent", "sends"], "ans": 1},
    {"id": 24, "topic": "Грамматика", "level": "B1", "q": "She ___ in London since 2020.", "opts": ["lives", "lived", "has lived", "living"], "ans": 2},
    {"id": 25, "topic": "Грамматика", "level": "B1", "q": "You like pizza, ___ you?", "opts": ["don't", "do", "aren't", "isn't"], "ans": 0},

    # B2 (3 вопроса)
    {"id": 26, "topic": "Грамматика", "level": "B2", "q": "You ___ have told me earlier!", "opts": ["must", "should", "could", "would"], "ans": 1},
    {"id": 27, "topic": "Грамматика", "level": "B2", "q": "If I ___ rich, I would travel the world.", "opts": ["am", "was", "were", "be"], "ans": 2},
    {"id": 28, "topic": "Грамматика", "level": "B2", "q": "I wish I ___ harder at school.", "opts": ["study", "studied", "had studied", "would study"], "ans": 2},

    # C1-C2 (2 вопроса)
    {"id": 29, "topic": "Грамматика", "level": "C1", "q": "Not only ___ the exam, but he also got the highest score.", "opts": ["he passed", "passed he", "did he pass", "he did pass"], "ans": 2},
    {"id": 30, "topic": "Лексика", "level": "C2", "q": "His argument was ___ — completely convincing and well-reasoned.", "opts": ["cogent", "coherent", "cohesive", "complacent"], "ans": 0},
]

LEVEL_THRESHOLDS = [
    (0, "A0", "Absolute Beginner"), (7, "A1", "Beginner"), (14, "A2", "Elementary"),
    (20, "B1", "Intermediate"), (25, "B2", "Upper-Intermediate"), (28, "C1", "Advanced"), (30, "C2", "Proficient"),
]


def calculate_level(score, total):
    pct = (score / total) * 100 if total > 0 else 0
    if pct >= 97: return "C2"
    elif pct >= 87: return "C1"
    elif pct >= 72: return "B2"
    elif pct >= 52: return "B1"
    elif pct >= 32: return "A2"
    elif pct >= 14: return "A1"
    else: return "A0"
