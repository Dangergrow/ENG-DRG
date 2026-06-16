/* ═══════════════════════════════════
   Spring Animation Engine
   Физика: mass, stiffness, damping
   ═══════════════════════════════════ */
const Spring = {
  _running: new Map(),

  /**
   * Анимирует числовое значение с spring-физикой.
   * @param {object} opts — { from, to, stiffness (default 180), damping (default 12), mass (default 1) }
   * @param {function} onUpdate — (value) => {}
   * @param {function} onComplete — () => {}
   * @returns {object} { stop() }
   */
  animate(opts, onUpdate, onComplete) {
    const { from = 0, to = 1, stiffness = 180, damping = 12, mass = 1, precision = 0.001 } = opts;
    let x = from;
    let v = 0;
    const id = Symbol('spring');
    let raf;

    const step = () => {
      const force = -stiffness * (x - to);
      const damp = -damping * v;
      const accel = (force + damp) / mass;
      v += accel * 0.016;
      x += v * 0.016;

      onUpdate(x);

      if (Math.abs(x - to) < precision && Math.abs(v) < precision) {
        onUpdate(to);
        if (onComplete) onComplete();
        return;
      }
      raf = requestAnimationFrame(step);
    };

    raf = requestAnimationFrame(step);

    const handle = { id };
    this._running.set(id, handle);
    handle.stop = () => {
      cancelAnimationFrame(raf);
      this._running.delete(id);
    };
    return handle;
  },

  /** Преобразует DOM-элемент: scale spring */
  scale(el, from, to, opts = {}) {
    return this.animate(
      { from, to, stiffness: 200, damping: 14, mass: 0.8, ...opts },
      (v) => { el.style.transform = `scale(${v})`; }
    );
  },

  /** Легкий bounce на элементе */
  bounce(el, intensity = 1.08) {
    el.style.transition = 'none';
    el.style.transform = `scale(${intensity})`;
    requestAnimationFrame(() => {
      el.style.transition = 'transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
      el.style.transform = 'scale(1)';
    });
  },

  /** Shake элемента */
  shake(el) {
    el.classList.add('shake');
    el.addEventListener('animationend', () => el.classList.remove('shake'), { once: true });
  },

  /** Letter stagger: анимирует появление текста по буквам */
  staggerText(container, text, delay = 30) {
    container.innerHTML = '';
    container.classList.add('title-stagger');
    text.split('').forEach((char, i) => {
      const span = document.createElement('span');
      span.className = 'char';
      span.textContent = char === ' ' ? '\u00A0' : char;
      span.style.animationDelay = `${i * delay}ms`;
      container.appendChild(span);
    });
  },

  /** Числовой счётчик с анимацией */
  countUp(el, from, to, duration = 800) {
    const start = performance.now();
    const step = (now) => {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 4);
      const val = Math.round(from + (to - from) * eased);
      el.textContent = val;
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }
};

window.Spring = Spring;
