// Final SRT for one voice: TTS sentence boundaries shifted by the title card, formulas in display form.
// usage: node scripts/make-srt.mjs OUT.srt [VOICE]
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const manifest = JSON.parse(readFileSync(join(root, "public/narration/manifest.json"), "utf8"));
const config = JSON.parse(readFileSync(join(root, "video.config.json"), "utf8"));
const display = JSON.parse(readFileSync(join(root, "src/captions-display.json"), "utf8"));
const [out, voice] = process.argv.slice(2);
if (!out) {
  console.error("usage: node scripts/make-srt.mjs OUT.srt [VOICE]");
  process.exit(2);
}
const track = voice ? manifest.tracks.find((t) => t.voice === voice) : manifest.tracks[0];
if (!track) {
  console.error(`Error: no track ${voice ?? ""} in manifest (${manifest.tracks.map((t) => t.voice).join(", ")})`);
  process.exit(1);
}
const fps = manifest.fps;
const offset = Math.round(config.titleSeconds * fps) / fps;
const stamp = (s) => {
  const ms = Math.round(s * 1000);
  const p = (n, w = 2) => String(n).padStart(w, "0");
  return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`;
};
const cues = [];
for (const scene of track.scenes) {
  const base = offset + scene.audioStartFrame / fps;
  scene.boundaries.forEach((b, k) => {
    const next = scene.boundaries[k + 1];
    const end = next ? next.startSeconds : b.endSeconds;
    cues.push(`${cues.length + 1}\n${stamp(base + b.startSeconds)} --> ${stamp(base + end)}\n${display[b.text] ?? b.text}`);
  });
}
writeFileSync(out, cues.join("\n\n") + "\n", "utf8");
console.log(`${out}: ${cues.length} cues, ${track.voice}`);
