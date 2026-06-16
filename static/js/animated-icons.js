/* ═══════════════════════════════════
   Animated SVG Icons — 5 icons × 4 states
   Каждая иконка: static → hover → active → celebrating
   ═══════════════════════════════════ */
const AnimatedIcons = {
  /** home — дом с breathing-дымоходом */
  home(className = '') {
    return `<svg class="icon-wrap ${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 10l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2V10z"/>
      <path d="M9 21V12h6v9"/>
      <line x1="10" y1="7" x2="14" y2="7" class="chimney-smoke" opacity="0.6">
        <animate attributeName="y1" values="7;5;7" dur="3s" repeatCount="indefinite"/>
        <animate attributeName="y2" values="7;5;7" dur="3s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.6;0.2;0.6" dur="3s" repeatCount="indefinite"/>
      </line>
    </svg>`;
  },

  /** lessons — книга с перелистывающейся страницей */
  lessons(className = '') {
    return `<svg class="icon-wrap ${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/>
      <path d="M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15z"/>
      <path d="M12 6v10" class="page-curl" style="transform-origin:12px 11px">
        <animateTransform attributeName="transform" type="rotate" values="0 12 11;-8 12 11;0 12 11" dur="4s" repeatCount="indefinite"/>
      </path>
    </svg>`;
  },

  /** streak — пламя с 3 уровнями интенсивности */
  streak(className = '', intensity = 1) {
    const scales = {1: '0.8', 2: '1.0', 3: '1.15'};
    const scale = scales[intensity] || '1.0';
    return `<svg class="icon-wrap ${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <g transform="scale(${scale})" style="transform-origin:12px 14px">
        <path d="M12 2c-1 3-3 6-3 9a3 3 0 006 0c0-3-2-6-3-9z" fill="color-mix(in oklch, currentColor 20%, transparent)">
          <animate attributeName="d" values="M12 2c-1 3-3 6-3 9a3 3 0 006 0c0-3-2-6-3-9z;M12 1.5c-0.8 3-3.2 6.5-3.2 9.5a3.2 3.2 0 006.4 0c0-3-2.4-6.5-3.2-9.5z;M12 2c-1 3-3 6-3 9a3 3 0 006 0c0-3-2-6-3-9z" dur="2s" repeatCount="indefinite"/>
        </path>
        <path d="M9 14c0 1.5 1.5 3 3 3s3-1.5 3-3"/>
      </g>
      <circle cx="12" cy="18" r="0.8" opacity="0.5">
        <animate attributeName="opacity" values="0.5;1;0.5" dur="1.5s" repeatCount="indefinite"/>
        <animate attributeName="r" values="0.8;1.2;0.8" dur="1.5s" repeatCount="indefinite"/>
      </circle>
      <circle cx="14" cy="19.5" r="0.5" opacity="0.3">
        <animate attributeName="opacity" values="0.3;0.7;0.3" dur="1.8s" repeatCount="indefinite"/>
      </circle>
    </svg>`;
  },

  /** check — галочка с stroke-animation */
  check(className = '') {
    return `<svg class="icon-wrap ${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10" stroke-dasharray="63" stroke-dashoffset="63">
        <animate attributeName="stroke-dashoffset" from="63" to="0" dur="0.5s" begin="icon-celebrate" fill="freeze"/>
      </circle>
      <path d="M8 12l2.5 2.5L16 9" stroke-dasharray="16" stroke-dashoffset="16">
        <animate attributeName="stroke-dashoffset" from="16" to="0" dur="0.3s" begin="icon-celebrate+0.3s" fill="freeze"/>
      </path>
    </svg>`;
  },

  /** play — треугольник с orbiting-частицами */
  play(className = '') {
    return `<svg class="icon-wrap ${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <path d="M10 8l6 4-6 4V8z" fill="currentColor" fill-opacity="0.15"/>
      <!-- Orbiting particle 1 -->
      <circle cx="12" cy="2" r="2" fill="currentColor" opacity="0.6">
        <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="3s" repeatCount="indefinite"/>
      </circle>
      <!-- Orbiting particle 2 (offset) -->
      <circle cx="12" cy="2" r="1.5" fill="currentColor" opacity="0.4">
        <animateTransform attributeName="transform" type="rotate" from="120 12 12" to="480 12 12" dur="3s" repeatCount="indefinite"/>
      </circle>
      <!-- Orbiting particle 3 (offset) -->
      <circle cx="12" cy="2" r="1" fill="currentColor" opacity="0.3">
        <animateTransform attributeName="transform" type="rotate" from="240 12 12" to="600 12 12" dur="3s" repeatCount="indefinite"/>
      </circle>
    </svg>`;
  },

  /** Враппер для interactive icon с 4 состояниями */
  create(el, type, opts = {}) {
    const wrapper = document.createElement('span');
    wrapper.className = 'interactive-icon';
    wrapper.innerHTML = this[type] ? this[type]() : '';

    // Hover: squish + bounce
    wrapper.addEventListener('mouseenter', () => {
      wrapper.style.transition = 'transform 0.3s cubic-bezier(0.34,1.56,0.64,1)';
      wrapper.style.transform = 'scale(1.15)';
    });
    wrapper.addEventListener('mouseleave', () => {
      wrapper.style.transform = 'scale(1)';
    });

    // Active: press
    wrapper.addEventListener('mousedown', () => {
      wrapper.style.transition = 'transform 0.1s ease-out';
      wrapper.style.transform = 'scale(0.88)';
    });
    wrapper.addEventListener('mouseup', () => {
      wrapper.style.transition = 'transform 0.3s cubic-bezier(0.34,1.56,0.64,1)';
      wrapper.style.transform = 'scale(1)';
    });

    // Celebrating
    if (opts.onCelebrate) {
      wrapper.addEventListener('celebrate', () => {
        wrapper.style.transition = 'transform 0.5s cubic-bezier(0.34,1.56,0.64,1)';
        wrapper.style.transform = 'scale(1.25)';
        setTimeout(() => { wrapper.style.transform = 'scale(1)'; }, 500);
        opts.onCelebrate();
      });
    }

    if (el) el.appendChild(wrapper);
    return wrapper;
  }
};

window.AnimatedIcons = AnimatedIcons;
