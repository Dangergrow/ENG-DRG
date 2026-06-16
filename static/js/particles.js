/* ═══════════════════════════════════
   Particle System (Canvas)
   Конфетти, искры, celebration bursts
   ═══════════════════════════════════ */
const Particles = {
  canvas: null,
  ctx: null,
  particles: [],
  running: false,

  init() {
    if (this.canvas) return;
    this.canvas = document.createElement('canvas');
    this.canvas.id = 'particles-canvas';
    this.ctx = this.canvas.getContext('2d');
    document.body.appendChild(this.canvas);
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.loop();
  },

  resize() {
    if (!this.canvas) return;
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  },

  /** Запускает burst частиц из точки (x, y) */
  burst(x, y, count = 40, colors = null) {
    this.init();
    const palette = colors || [
      '#a78bfa', '#00e6b0', '#ffb347', '#ff4d6a', '#4da6ff',
      '#c4b5fd', '#33ffcc', '#ffffff',
    ];
    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5) * 0.5;
      const speed = 2 + Math.random() * 6;
      this.particles.push({
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 2,
        life: 1,
        decay: 0.015 + Math.random() * 0.03,
        size: 2 + Math.random() * 5,
        color: palette[Math.floor(Math.random() * palette.length)],
        gravity: 0.08,
      });
    }
  },

  /** Конфетти по центру экрана */
  confetti(count = 80) {
    this.init();
    const w = window.innerWidth;
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: w / 2 + (Math.random() - 0.5) * 400,
        y: -20 - Math.random() * 200,
        vx: (Math.random() - 0.5) * 3,
        vy: 2 + Math.random() * 4,
        life: 1,
        decay: 0.004 + Math.random() * 0.008,
        size: 4 + Math.random() * 8,
        color: ['#ffb347', '#ff4d6a', '#4da6ff', '#a78bfa', '#00e6b0'][Math.floor(Math.random() * 5)],
        gravity: 0.05,
        shape: Math.random() > 0.5 ? 'rect' : 'circle',
        rotation: Math.random() * Math.PI * 2,
        rotSpeed: (Math.random() - 0.5) * 0.2,
      });
    }
  },

  loop() {
    if (!this.ctx || !this.canvas) return;
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.particles = this.particles.filter(p => p.life > 0);
    for (const p of this.particles) {
      p.vy += p.gravity;
      p.x += p.vx;
      p.y += p.vy;
      p.life -= p.decay;

      ctx.save();
      ctx.globalAlpha = p.life;
      ctx.fillStyle = p.color;

      if (p.shape === 'rect') {
        p.rotation = (p.rotation || 0) + (p.rotSpeed || 0);
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rotation);
        ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
      } else {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }

    requestAnimationFrame(() => this.loop());
  }
};

window.Particles = Particles;
