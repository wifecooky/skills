// site-verify 的共用部分：本地静态服务、FEATURES.md 与测试对表、并发跑、截图、contact sheet。
// 每个站的 scripts/verify.mjs 只写自己的 TESTS / START / CTX / ready，然后：
//   const H = await import(path.join(os.homedir(), "Documents/git/skills/site-verify/harness.mjs"));
//   await H.verify({ root, title, tests, start, ctx, ready });
// 命令行：node scripts/verify.mjs [id ...]   不给 id 就全跑；出图在 <root>/.verify/index.html
// FEATURES.md 有而 tests 没有、或 tests 有而 FEATURES.md 没有的 id，都算失败。
// Playwright 用 desktop-to-mobile 那份钉了版本的（ui-check.mjs 同一份），别处的设 PLAYWRIGHT=…/playwright/index.mjs
import http from "node:http";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const PW = process.env.PLAYWRIGHT || path.join(os.homedir(), "Documents/git/skills/desktop-to-mobile/scripts/node_modules/playwright/index.mjs");

/* ── 测试里用的小工具 ── */
// 页面里等一个条件成立，不成立就带着说明失败
export const until = (p, fn, arg, msg, timeout = 5000) => p.waitForFunction(fn, arg, { timeout, polling: 50 }).catch(() => { throw new Error(msg); });
export const ok = (v, msg) => { if (!v) throw new Error(msg); };
export const val = (p, fn, arg) => p.evaluate(fn, arg);
export const hash = (p) => val(p, () => location.hash);
export const show = (p, sel) => p.locator(sel).first().scrollIntoViewIfNeeded();
// 截图前等翻页、淡入这类有限时长的动画走完（循环动画不等），最多 3 秒
const still = (p) => p.evaluate(() => Promise.race([new Promise((r) => setTimeout(r, 3000)),
  Promise.all(document.getAnimations().filter((a) => a.effect?.getComputedTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {})))]));
export const snap = async (p, tag) => { await still(p); await p.screenshot({ path: path.join(p._out, `${p._id}@${p._w}${tag ? "-" + tag : ""}.png`) }); };
// 换一个起点重新打开：先去 about:blank，只换 hash 不会重新加载
export const reopen = async (p, start = "") => { await p.goto("about:blank"); await p.goto(p._url(start)); await p._ready(p); };

/* ── 本地静态服务：目录给 index.html，/foo 找 foo.html（同 Cloudflare Pages），音视频支持 Range ── */
const TYPES = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json",
  ".svg": "image/svg+xml", ".webp": "image/webp", ".jpg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".avif": "image/avif", ".ico": "image/x-icon",
  ".woff2": "font/woff2", ".m4a": "audio/mp4", ".mp3": "audio/mpeg", ".mp4": "video/mp4", ".webm": "video/webm", ".vtt": "text/vtt",
  ".glb": "model/gltf-binary", ".wasm": "application/wasm", ".txt": "text/plain", ".xml": "application/xml", ".webmanifest": "application/manifest+json" };
function serve(dir) {
  const file = (u) => {
    const f = path.join(dir, decodeURIComponent(u.split("?")[0]));
    if (!f.startsWith(dir)) return null;
    for (const c of [f, path.join(f, "index.html"), f + ".html"]) if (fs.existsSync(c) && fs.statSync(c).isFile()) return c;
    return null;
  };
  return http.createServer((q, r) => {
    const f = file(q.url);
    if (!f) { r.writeHead(404).end(); return; }
    const type = TYPES[path.extname(f)] || "application/octet-stream", size = fs.statSync(f).size;
    const m = /bytes=(\d*)-(\d*)/.exec(q.headers.range || "");
    if (!m) { r.writeHead(200, { "content-type": type, "content-length": size, "accept-ranges": "bytes" }); fs.createReadStream(f).pipe(r); return; }
    const a = m[1] ? +m[1] : size - +m[2], b = m[1] && m[2] ? +m[2] : size - 1;
    r.writeHead(206, { "content-type": type, "content-length": b - a + 1, "content-range": `bytes ${a}-${b}/${size}`, "accept-ranges": "bytes" });
    fs.createReadStream(f, { start: a, end: b }).pipe(r);
  }).listen(0);
}

/*
 * root    站点仓库根（FEATURES.md 在这里，出图到 root/.verify）
 * serve   要服务的目录，默认 root；构建型站点给 dist
 * title   contact sheet 标题
 * tests   { id: async (page, width) => {} }，拿到一张已加载好的页，断言，最后那一屏自动截图
 * start   { id: "#hash" 或 "path/#hash" }，不写就开首页
 * ctx     { id: Playwright newContext 的额外选项 }
 * ready   async (page) => {}，开页后等站点自己的就绪信号；默认等字体
 * ignore  正则：可忽略的控制台报错（只放线上也有、与功能无关的外部资源报错）
 */
export async function verify({ root, serve: dir = root, title, tests, start = {}, ctx = {}, ready = (p) => p.evaluate(() => document.fonts.ready), ignore = null, widths = [390, 1440] }) {
  if (!fs.existsSync(PW)) { console.error(`✗ no Playwright at ${PW}: cd ~/Documents/git/skills/desktop-to-mobile/scripts && npm install`); process.exit(2); }
  const { chromium } = await import(PW);
  const OUT = path.join(root, ".verify");
  dir = path.resolve(root, dir);

  /* 功能地图和测试对表 */
  const md = fs.readFileSync(path.join(root, "FEATURES.md"), "utf8");
  const rows = Object.fromEntries([...md.matchAll(/^\| `([a-z0-9-]+)` \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$/gm)].map((m) => [m[1], { area: m[2].trim(), act: m[3].trim(), want: m[4].trim() }]));
  let bad = 0;
  const fail = (m) => { console.error(`✗ ${m}`); bad++; };
  for (const id of Object.keys(rows)) if (!tests[id]) fail(`FEATURES.md has ${id}, scripts/verify.mjs has no test for it`);
  for (const id of Object.keys(tests)) if (!rows[id]) fail(`scripts/verify.mjs tests ${id}, FEATURES.md has no row for it`);
  const pick = process.argv.slice(2);
  for (const id of pick) if (!tests[id]) fail(`no test ${id}`);
  const ids = (pick.length ? pick : Object.keys(rows)).filter((id) => tests[id]);

  /* 起服务，逐条跑：每条每个宽度一个新的浏览器上下文，4 条并行 */
  const server = serve(dir);
  const url = (s = "") => `http://localhost:${server.address().port}/${s.replace(/^\//, "")}`;
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.mkdirSync(OUT);
  const browser = await chromium.launch();
  const results = [];
  // 外网资源（字体 CDN、统计、验证码等）一律回空的 200：验收只看本站，外网慢或断不该让它红；字体退回系统字体
  const offsite = (route) => route.fulfill({ status: 200, body: "" });
  const run = async ([id, w]) => {
    const c = await browser.newContext({ viewport: { width: w, height: w <= 768 ? 844 : 900 }, isMobile: w <= 768, hasTouch: w <= 768, ...ctx[id] });
    await c.route((u) => u.hostname !== "localhost", offsite);
    const p = await c.newPage(), errs = [];
    Object.assign(p, { _id: id, _w: w, _out: OUT, _url: url, _ready: ready });
    p.on("pageerror", (e) => errs.push(`page error: ${e.message}`));
    p.on("console", (m) => m.type() === "error" && !(ignore && ignore.test(m.text() + " " + (m.location().url || ""))) && errs.push(`console: ${m.text()}`));
    let err = null;
    try {
      await p.goto(url(start[id]), { waitUntil: "domcontentloaded" });
      await ready(p);
      await tests[id](p, w);
    } catch (e) { err = e.message.split("\n")[0]; }
    if (!err && errs.length) err = errs[0];
    await snap(p).catch(() => {});
    await c.close();
    results.push({ id, w, err });
    if (err) fail(`${id} @${w}: ${err}`);
  };
  const queue = ids.flatMap((id) => widths.map((w) => [id, w]));
  await Promise.all(Array.from({ length: 4 }, async () => { while (queue.length) await run(queue.shift()); }));
  await browser.close();
  server.close();

  /* contact sheet：一行一条功能，两种宽度并排，过程截图跟在后面 */
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const pngs = fs.readdirSync(OUT).filter((f) => f.endsWith(".png"));
  const cells = (id) => pngs.filter((f) => f.startsWith(id + "@")).sort().map((f) => `<a href="${f}"><img src="${f}" loading="lazy" alt="${esc(f)}"><span>${esc(f.replace(id + "@", ""))}</span></a>`).join("");
  const sheet = ids.map((id) => {
    const rs = results.filter((r) => r.id === id), errs = rs.filter((r) => r.err);
    return `<section class="${errs.length ? "bad" : ""}"><h2>${errs.length ? "✗" : "✓"} <code>${id}</code> ${esc(rows[id].area)}</h2>` +
      `<p><b>操作</b> ${esc(rows[id].act)}　<b>期望</b> ${esc(rows[id].want)}</p>` +
      errs.map((r) => `<p class="err">@${r.w}: ${esc(r.err)}</p>`).join("") + `<div class="row">${cells(id)}</div></section>`;
  }).join("\n");
  const passed = results.filter((r) => !r.err).length;
  fs.writeFileSync(path.join(OUT, "index.html"), `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} · 功能验收</title>
<style>body{font:16px/1.5 system-ui,sans-serif;margin:24px;background:#f6f4ef;color:#222}section{border-top:1px solid #ccc;padding:12px 0}h2{font-size:17px;margin:0 0 4px}
.bad h2,.err{color:#b00}.row{display:flex;gap:12px;overflow-x:auto;align-items:flex-start}.row a{flex:none;text-decoration:none;color:#555;font-size:12px}
.row img{display:block;height:320px;border:1px solid #bbb;background:#fff}</style>
<h1>${esc(title)} · 功能验收</h1><p>${passed} / ${results.length} 通过 · ${new Date().toLocaleString("zh-CN")} · 截图是每条测试结束时那一屏，带 -a 的是中途那一屏</p>
${sheet}`);
  console.log(`verify: ${bad} problems, ${passed}/${results.length} passed · open .verify/index.html`);
  process.exit(bad ? 1 : 0);
}
