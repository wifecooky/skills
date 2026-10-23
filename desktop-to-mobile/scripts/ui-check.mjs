// UI floor that every page must pass, at 320/390/768/1440 px. Exits 1 on any ✗; ⚠ lines only warn.
//   node ui-check.mjs [--strict] <site-dir | http-url> [page ...]    pages default to index.html
//   --strict turns every ⚠ into ✗: new projects start strict; sites shipped before 2026-10-24 run without it.
//   e.g. node ui-check.mjs ~/Documents/git/sanguo   node ui-check.mjs http://localhost:3000 / /cart
// First run: cd this dir && npm install
//
// 1. No sideways scroll (WCAG 1.4.10).
// 2. No visible text under 12px. ⚠ <p>/<li> prose and inputs under 16px at ≤ 768px (inputs under 16px also zoom iOS).
// 3. Tap targets at least 24×24px or spaced apart (WCAG 2.5.8). ⚠ under 44×44px at ≤ 768px (Apple HIG). Links in running text are exempt.
// 4. Tap targets do not overlap each other.
// 5. No `user-scalable=no` / `maximum-scale=1`, no page errors, no console errors.
// A project's own check script adds its page-specific rules on top; this file keeps only the shared floor.
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const WIDTHS = [320, 390, 768, 1440];
const STRICT = process.argv.includes("--strict");
const [target, ...pages] = process.argv.slice(2).filter((a) => a !== "--strict");
if (!target) { console.error("usage: node ui-check.mjs [--strict] <site-dir | http-url> [page ...]"); process.exit(2); }

const TYPES = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".woff2": "font/woff2", ".m4a": "audio/mp4" };
let server, base = target;
if (!/^https?:/.test(target)) {
  const root = path.resolve(target);
  server = http.createServer((q, r) => {
    let f = path.join(root, decodeURIComponent(q.url.split("?")[0]));
    if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, "index.html");
    if (!f.startsWith(root) || !fs.existsSync(f)) { r.writeHead(404).end(); return; }
    r.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream" }).end(fs.readFileSync(f));
  }).listen(0);
  base = `http://localhost:${server.address().port}`;
}

// runs in the page
function audit(w) {
  const out = [], warn = [];
  const seen = (e) => {
    const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.opacity !== "0" && r.right > 0 && r.left < innerWidth;
  };
  const name = (e) => (e.textContent || e.getAttribute("aria-label") || e.getAttribute("title") || e.tagName).trim().replace(/\s+/g, " ").slice(0, 24);

  const sw = document.documentElement.scrollWidth;
  if (sw > innerWidth) out.push(`page is ${sw}px wide, viewport ${innerWidth}px`);

  const vp = document.querySelector('meta[name="viewport"]')?.content || "";
  if (/user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b/.test(vp)) out.push(`viewport blocks zoom: ${vp}`);

  const small = new Map();
  for (const e of document.body.querySelectorAll("*")) {
    if (["SCRIPT", "STYLE", "NOSCRIPT", "SVG"].includes(e.tagName) || e.closest("svg")) continue;
    const text = [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    const field = e.matches("input:not([type=hidden],[type=checkbox],[type=radio],[type=range]), textarea, select");
    if (!(text || field) || !seen(e)) continue;
    const px = parseFloat(getComputedStyle(e).fontSize);
    const floor = px < 12 ? 12 : w <= 768 && px < 16 && (field || e.matches("p, li") && e.textContent.trim().length > 40) ? 16 : 0;
    if (floor) {
      const k = `${px}px < ${floor}px`;
      small.set(k, [...(small.get(k) || []), name(e) || e.tagName]);
    }
  }
  for (const [k, l] of small) (k.endsWith("< 12px") ? out : warn).push(`text ${k}: ${l.length}× e.g. 「${l.slice(0, 3).join("」「")}」`);

  const taps = [...document.querySelectorAll("a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button], [onclick]")]
    .filter((e) => seen(e) && !e.parentElement.closest("a[href], button, summary, [role=button]"));
  const under = (n) => taps.filter((e) => {
    const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    const inline = e.matches("a") && s.display === "inline" && e.parentElement.closest("p, li, dd, td, figcaption, blockquote");
    return !inline && (r.width < n || r.height < n);
  });
  const list = (l) => l.slice(0, 4).map((e) => { const r = e.getBoundingClientRect(); return `「${name(e)}」 ${Math.round(r.width)}×${Math.round(r.height)}`; }).join(", ");
  // WCAG 2.5.8 spacing exception: a small target passes when a 24px circle on its centre touches no other target
  const near = (e) => {
    const r = e.getBoundingClientRect(), cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2;
    return taps.some((o) => {
      if (o === e) return false;
      const q = o.getBoundingClientRect();
      return Math.hypot(Math.max(q.left - cx, 0, cx - q.right), Math.max(q.top - cy, 0, cy - q.bottom)) < 12;
    });
  };
  const t24 = under(24).filter(near), t44 = w <= 768 ? under(44).filter((e) => !t24.includes(e)) : [];
  if (t24.length) out.push(`${t24.length} tap targets under 24×24px, e.g. ${list(t24)}`);
  if (t44.length) warn.push(`${t44.length} tap targets under 44×44px, e.g. ${list(t44)}`);
  const rects = taps.map((e) => [e, e.getBoundingClientRect()]);
  const hits = [];
  for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
    const [a, p] = rects[i], [b, q] = rects[j];
    if (a.contains(b) || b.contains(a)) continue;
    const x = Math.min(p.right, q.right) - Math.max(p.left, q.left), y = Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top);
    if (x > 2 && y > 2) hits.push(`「${name(a)}」/「${name(b)}」`);
  }
  if (hits.length) out.push(`${hits.length} overlapping tap targets, e.g. ${hits.slice(0, 3).join(", ")}`);
  return { out, warn };
}

const browser = await chromium.launch();
let bad = 0, warned = 0;
for (const page of pages.length ? pages : ["/"]) {
  const url = new URL(page.replace(/^(?!\/)/, "/"), base).href;
  for (const w of WIDTHS) {
    const ctx = await browser.newContext({ viewport: { width: w, height: w <= 768 ? 844 : 900 }, isMobile: w <= 768, hasTouch: w <= 768 });
    const p = await ctx.newPage(), errs = [];
    p.on("pageerror", (e) => errs.push(`page error: ${e.message}`));
    p.on("console", (m) => m.type() === "error" && errs.push(`console: ${m.text()}`));
    try {
      // a slow font CDN must not fail the check: wait for the DOM, then at most 10 s for the rest
      await p.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
      await p.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => {});
      await p.evaluate(() => Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 3000))]));
      const { out, warn } = await p.evaluate(audit, w);
      for (const m of [...out, ...errs, ...(STRICT ? warn : [])]) { console.error(`✗ ${page} @${w}: ${m}`); bad++; }
      if (!STRICT) for (const m of warn) { console.error(`⚠ ${page} @${w}: ${m}`); warned++; }
    } catch (e) { console.error(`✗ ${page} @${w}: does not load: ${e.message.split("\n")[0]}`); bad++; }
    await ctx.close();
  }
}
await browser.close();
server?.close();
console.log(`ui-check: ${bad} problems, ${warned} warnings${STRICT ? " (strict)" : ""}`);
process.exit(bad ? 1 : 0);
