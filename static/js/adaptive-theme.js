/* ═══════════════════════════════════
   Adaptive Theme System
   Время суток + эмоциональный контекст + ручной выбор
   ═══════════════════════════════════ */
const AdaptiveTheme = {
  _period: null,
  _emotion: 'neutral', // neutral | success | fail
  _manual: null,
  _emotionTimer: null,

  /** Инициализация */
  init() {
    this.setByTime();
    this._startTimeInterval();
    this._listenClicks();
  },

  /** Определяет период суток и выставляет accent */
  setByTime() {
    const h = new Date().getHours();
    let period;
    if (h >= 6 && h < 12) period = 'morning';
    else if (h >= 12 && h < 17) period = 'day';
    else if (h >= 17 && h < 22) period = 'evening';
    else period = 'night';

    if (period === this._period && !this._manual) return;
    this._period = period;
    this._applyPeriod(period);
  },

  _startTimeInterval() {
    setInterval(() => {
      if (!this._manual) this.setByTime();
    }, 60000);
  },

  /** Цветовые схемы периодов */
  _applyPeriod(period) {
    const palettes = {
      morning: { h: 288, c: 0.22, l: 0.65 },
      day:     { h: 280, c: 0.24, l: 0.63 },
      evening: { h: 35,  c: 0.2,  l: 0.68 },
      night:   { h: 270, c: 0.22, l: 0.58 },
    };
    const p = palettes[period] || palettes.day;
    this._setAccent(p.h, p.l, p.c);
  },

  /** Применяет accent через CSS переменные с плавным переходом */
  _setAccent(h, l, c) {
    const root = document.documentElement;
    root.style.setProperty('--accent', `oklch(${l} ${c} ${h})`);
    root.style.setProperty('--accent-2', `oklch(${Math.min(l + 0.08, 0.85)} ${Math.max(c - 0.04, 0.12)} ${h + 10})`);
    root.style.setProperty('--accent-glass', `oklch(${l} ${c} ${h} / 0.15)`);
  },

  /** Эмоциональный контекст */
  onSuccess() {
    this._emotion = 'success';
    // Смещаем accent к warm для celebration vibe
    this._setAccent(45, 0.7, 0.18);
    clearTimeout(this._emotionTimer);
    this._emotionTimer = setTimeout(() => this._resetEmotion(), 4000);
  },

  onFail() {
    this._emotion = 'fail';
    // Успокаивающий teal
    this._setAccent(170, 0.68, 0.16);
    clearTimeout(this._emotionTimer);
    this._emotionTimer = setTimeout(() => this._resetEmotion(), 4000);
  },

  _resetEmotion() {
    this._emotion = 'neutral';
    if (!this._manual) this.setByTime();
  },

  /** Ручное переключение темы (светлая/тёмная) */
  toggleLightDark() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const next = current === 'light' ? null : 'light';
    if (next) html.setAttribute('data-theme', next);
    else html.removeAttribute('data-theme');
    this._manual = next;
    localStorage.setItem('linguamate-theme', next || 'dark');
  },

  /** Загрузка сохранённой темы */
  loadSaved() {
    const saved = localStorage.getItem('linguamate-theme');
    if (saved === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
      this._manual = 'light';
    }
  },

  /** Закрыть клик вне меню */
  _listenClicks() {
    // Placeholder для закрытия дропдаунов
  }
};

window.AdaptiveTheme = AdaptiveTheme;
