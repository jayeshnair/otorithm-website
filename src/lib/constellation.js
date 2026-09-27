/**
 * Constellation — particle field that assembles into brand formations.
 * Framework-agnostic: new Constellation(canvas, { formation, ambient, fill }).
 *
 * Formations are unions of axis-aligned rectangles in a 120×120 unit space
 * (the same space as the Ligature mark). Particles are placed on a regular
 * pixel grid inside those shapes, drawn as uniform 1px-outlined squares
 * snapped to the device pixel grid, so the formed mark reads crisp.
 */
export const FORMATIONS = {
  // Ligature mark: path "M104 48 H16 V96 H60 V48" + stem "M84 20 V102", stroke 12, miter joins.
  ligature: [
    [10, 42, 94, 12],
    [10, 42, 12, 60],
    [10, 90, 56, 12],
    [54, 42, 12, 60],
    [78, 20, 12, 82, 'amber'],
  ],
  // Engineering pods: 2×2 grid with the top-right block deployed.
  pods: [
    [20, 36, 28, 28],
    [20, 72, 28, 28],
    [56, 72, 28, 28],
    [72, 20, 28, 28, 'amber'],
  ],
  // AI transformation: a rising stepped line.
  ascent: [
    [14, 92, 30, 12],
    [32, 70, 12, 34],
    [32, 70, 36, 12],
    [56, 48, 12, 34],
    [56, 48, 36, 12],
    [80, 26, 12, 34, 'amber'],
    [80, 26, 26, 12, 'amber'],
  ],
  // Software consulting: stacked platform layers.
  layers: [
    [26, 26, 80, 16, 'amber'],
    [18, 52, 88, 16],
    [10, 78, 96, 16],
  ],
};

const STROKE_UNITS = 12; // the mark's stroke width in unit space
const PER_STROKE = 5; // particles across one stroke width
const PAPER = 'rgb(246,245,241)';
const AMBER = '#C27A2C';
const PAPER_ALPHA = 0.9;
const EASE = 0.06;
const REPEL_RADIUS = 90;
const REPEL_FORCE = 28;

function gridTargets(rects, scale) {
  const pitch = Math.min(11, Math.max(6, (scale * STROKE_UNITS) / PER_STROKE));
  const step = pitch / scale;
  const out = [];
  for (let uy = step / 2; uy < 120; uy += step) {
    for (let ux = step / 2; ux < 120; ux += step) {
      let hit = false;
      let amber = false;
      for (const [x, y, w, h, tag] of rects) {
        if (ux >= x && ux <= x + w && uy >= y && uy <= y + h) {
          hit = true;
          if (tag === 'amber') amber = true;
        }
      }
      if (hit) out.push({ ux, uy, amber });
    }
  }
  return { targets: out, pitch };
}

export class Constellation {
  constructor(canvas, opts = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.rects = FORMATIONS[opts.formation] || FORMATIONS.ligature;
    this.fill = opts.fill || 0.78;
    this.ambientCount = opts.ambient || 0;
    this.reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.pointer = null;
    this.raf = 0;
    this.w = 0;
    this.h = 0;
    this.scale = 1;
    this.ox = 0;
    this.oy = 0;
    this.size = 5;
    this.particles = [];
    this.ambient = [];

    this._tick = this._tick.bind(this);
    this._onMove = (e) => {
      const r = this.canvas.getBoundingClientRect();
      this.pointer = { x: e.clientX - r.left, y: e.clientY - r.top };
    };
    this._onLeave = () => {
      this.pointer = null;
    };

    this._layout();
    this._seedAmbient();

    this.ro = new ResizeObserver(() => {
      this._layout();
      if (this.reduce || !this.raf) this._draw();
    });
    this.ro.observe(canvas);

    this.io = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) this._start();
      else this._stop();
    });
    this.io.observe(canvas);

    if (!this.reduce) {
      window.addEventListener('pointermove', this._onMove, { passive: true });
      document.documentElement.addEventListener('pointerleave', this._onLeave);
      window.addEventListener('blur', this._onLeave);
    }
  }

  /** Size the canvas, then rebuild grid targets for the new scale. */
  _layout() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.w = this.canvas.clientWidth;
    this.h = this.canvas.clientHeight;
    this.canvas.width = Math.max(1, Math.round(this.w * dpr));
    this.canvas.height = Math.max(1, Math.round(this.h * dpr));
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.scale = (Math.min(this.w, this.h) * this.fill) / 120;
    this.ox = Math.round((this.w - 120 * this.scale) / 2);
    this.oy = Math.round((this.h - 120 * this.scale) / 2);

    const { targets, pitch } = gridTargets(this.rects, this.scale);
    this.size = pitch >= 8 ? 5 : 3;

    // Keep existing particles (so a resize reflows smoothly), add or trim to fit.
    while (this.particles.length < targets.length) {
      this.particles.push({ x: Math.random() * this.w, y: Math.random() * this.h });
    }
    this.particles.length = targets.length;
    targets.forEach((t, i) => Object.assign(this.particles[i], t));

    if (this.reduce) this._snap();
  }

  _seedAmbient() {
    this.ambient = Array.from({ length: this.ambientCount }, () => ({
      x: Math.random() * this.w,
      y: Math.random() * this.h,
      vx: (Math.random() - 0.5) * 0.25,
      vy: (Math.random() - 0.5) * 0.25,
      tick: Math.random() < 0.3,
      alpha: 0.06 + Math.random() * 0.08,
    }));
  }

  _snap() {
    for (const p of this.particles) {
      p.x = this.ox + p.ux * this.scale;
      p.y = this.oy + p.uy * this.scale;
    }
  }

  _start() {
    if (this.reduce) {
      this._draw();
      return;
    }
    if (!this.raf) this.raf = requestAnimationFrame(this._tick);
  }

  _stop() {
    if (this.raf) cancelAnimationFrame(this.raf);
    this.raf = 0;
  }

  _tick() {
    const ptr = this.pointer;
    for (const p of this.particles) {
      let tx = this.ox + p.ux * this.scale;
      let ty = this.oy + p.uy * this.scale;
      if (ptr) {
        const dx = tx - ptr.x;
        const dy = ty - ptr.y;
        const d = Math.hypot(dx, dy);
        if (d < REPEL_RADIUS && d > 0.01) {
          const push = (1 - d / REPEL_RADIUS) * REPEL_FORCE;
          tx += (dx / d) * push;
          ty += (dy / d) * push;
        }
      }
      p.x += (tx - p.x) * EASE;
      p.y += (ty - p.y) * EASE;
    }
    for (const a of this.ambient) {
      a.x += a.vx;
      a.y += a.vy;
      if (a.x < -10) a.x = this.w + 10;
      if (a.x > this.w + 10) a.x = -10;
      if (a.y < -10) a.y = this.h + 10;
      if (a.y > this.h + 10) a.y = -10;
    }
    this._draw();
    this.raf = requestAnimationFrame(this._tick);
  }

  _draw() {
    const ctx = this.ctx;
    const s = this.size;
    ctx.clearRect(0, 0, this.w, this.h);
    ctx.lineWidth = 1;

    // Ambient: dim, drifting, individually faded.
    ctx.strokeStyle = PAPER;
    ctx.fillStyle = PAPER;
    for (const a of this.ambient) {
      ctx.globalAlpha = a.alpha;
      const x = Math.round(a.x);
      const y = Math.round(a.y);
      if (a.tick) ctx.fillRect(x, y - 3, 1, 6);
      else ctx.strokeRect(x - 1.5, y - 1.5, 3, 3);
    }

    // Formation: uniform squares snapped to whole pixels, one stroke per colour.
    const batch = (amber, color, alpha) => {
      ctx.globalAlpha = alpha;
      ctx.strokeStyle = color;
      ctx.beginPath();
      for (const p of this.particles) {
        if (p.amber !== amber) continue;
        ctx.rect(Math.round(p.x - s / 2) + 0.5, Math.round(p.y - s / 2) + 0.5, s - 1, s - 1);
      }
      ctx.stroke();
    };
    batch(false, PAPER, PAPER_ALPHA);
    batch(true, AMBER, 1);
    ctx.globalAlpha = 1;
  }

  destroy() {
    this._stop();
    this.ro.disconnect();
    this.io.disconnect();
    window.removeEventListener('pointermove', this._onMove);
    document.documentElement.removeEventListener('pointerleave', this._onLeave);
    window.removeEventListener('blur', this._onLeave);
  }
}
