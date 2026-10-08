# Design system (from the LLM piece)

Palette, fonts, background layers, HUD. Copy and re-theme; keep 3-color discipline.

## Tokens + background
```css
      :root {
        --ink: #14110e;
        --cream: #efe6d6;
        --dim: rgba(239, 230, 214, 0.66);
        --accent: #ff5b3a;
        --serif: "Noto Serif SC", serif;
        --mono: "JetBrains Mono", "Noto Serif SC", monospace;
      }
      * {
        position: absolute;
        left: -120px;
        top: -120px;
        width: 2160px;
        height: 1320px;
        background-image: radial-gradient(rgba(239, 230, 214, 0.22) 1.6px, transparent 1.8px);
        background-size: 60px 60px;
        opacity: 0.55;
      }
      #moon {
        position: absolute;
        left: 0;
        top: 0;
        width: 560px;
        height: 560px;
      }
      #moon-glow {
        position: absolute;
        inset: -320px;
        border-radius: 50%;
        background: radial-gradient(
          circle,
          rgba(255, 140, 90, 0.2) 0%,
          rgba(255, 110, 70, 0.08) 35%,
          rgba(255, 91, 58, 0) 68%
        );
      }
      #moon-disk {
        position: absolute;
        inset: 0;
        border-radius: 50%;
        background: radial-gradient(
          circle at 38% 34%,
          rgba(239, 230, 214, 0.2) 0%,
          rgba(239, 230, 214, 0.08) 55%,
          rgba(239, 230, 214, 0.03) 100%
        );
        border: 2px solid rgba(239, 230, 214, 0.18);
      }
      #moon-ring {
        position: absolute;
        inset: -46px;
        border-radius: 50%;
        border: 2px dashed rgba(239, 230, 214, 0.14);
      }
      #vignette {
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse at 50% 45%, rgba(0, 0, 0, 0) 45%, rgba(0, 0, 0, 0.6) 100%);
      }
      #grain {
        position: absolute;
        left: -160px;
        top: -160px;
        width: 2240px;
        height: 1400px;
        opacity: 0.09;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='320' height='320'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1.4 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
      }

      /* ---------- camera ---------- */
      #cam,
      #world {
        position: absolute;
        inset: 0;
      }

      /* ---------- tokens ---------- */
      .tok {
        position: absolute;
        top: 430px;
        height: 150px;
      }
      .tok-frame {
```

## HUD (brand, step label, timecode)
```css
        width: 920px;
        height: 150px;
        overflow: visible;
      }

      /* ---------- HUD ---------- */
      #hud-brand {
        position: absolute;
        left: 80px;
        top: 58px;
        display: flex;
        align-items: baseline;
        gap: 18px;
        white-space: nowrap;
      }
      #hud-brand .k {
        font-family: var(--mono);
        font-size: 24px;
        font-weight: 700;
        color: var(--accent);
        letter-spacing: 0.12em;
      }
      #hud-brand .t {
        font-size: 26px;
        color: var(--dim);
      }
      .step {
        position: absolute;
        right: 80px;
        top: 54px;
        display: flex;
        align-items: baseline;
        gap: 16px;
        white-space: nowrap;
      }
      .step .n {
        font-family: var(--mono);
        font-size: 24px;
        color: var(--dim);
      }
      .step .n b {
        color: var(--accent);
      }
      .step .z {
        font-size: 32px;
        font-weight: 600;
        color: var(--cream);
      }
      .step .e {
        font-family: var(--mono);
        font-size: 22px;
        letter-spacing: 0.16em;
        color: var(--dim);
      }
      .cap {
        position: absolute;
        left: 80px;
        top: 872px;
        white-space: nowrap;
      }
      .cap .c {
        font-size: 46px;
        font-weight: 600;
        color: var(--cream);
        line-height: 1.1;
      }
      .cap .r {
        margin-top: 14px;
        font-family: var(--mono);
        font-size: 22px;
        color: var(--dim);
        letter-spacing: 0.04em;
      }
      .cap .r b {
        color: var(--accent);
        font-weight: 700;
      }
      .rail {
        position: absolute;
        top: 1006px;
        height: 4px;
        background: rgba(239, 230, 214, 0.16);
      }
      .rail i {
        display: block;
        width: 100%;
        height: 4px;
        background: var(--accent);
        transform-origin: 0 50%;
      }
      #tc {
        position: absolute;
        right: 80px;
        top: 968px;
        font-family: var(--mono);
        font-size: 22px;
        color: var(--dim);
        letter-spacing: 0.06em;
      }
    </style>
  </head>
  <body>
    <div data-hf-id="hf-kbh8" id="root" data-composition-id="main" data-start="0" data-duration="122.8" data-width="1920" data-height="1080">
```

## JS helpers
```js
        const mk = (tag, cls, parent, html) => {
          const el = document.createElement(tag);
          if (cls) el.className = cls;
          if (html != null) el.innerHTML = html;
          parent.appendChild(el);
          return el;
        };
        const hash = (a, b, c) => {
          const x = Math.sin(a * 127.1 + b * 311.7 + c * 74.7) * 43758.5453;
          return x - Math.floor(x);
        };
        const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
        const lerp = (a, b, p) => a + (b - a) * p;

```

Copy the full working composition from `~/Downloads/videos/llm-next-token-detailed/index.html` as the structural template (camera, morph chain, clock driver, step rail).
