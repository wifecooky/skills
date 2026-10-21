# Pipeline reference

## Voiceover (ListenHub)

Credential: never print or write the key. Load inline per command:
`export LISTENHUB_API_KEY=$(grep -ohE "lh_sk_[A-Za-z0-9_-]{8,}" ~/.claude/projects/*/*.jsonl | head -1)`
(or rely on `listenhub auth login` OAuth).

```bash
# one clip per scene
listenhub openapi tts --text "<line>" --voice zh-male-guchuan-9d6a4666 --format mp3 --output assets/vo/vo0.mp3
# Japanese: --voice minimax-official-japanese-optimisticyouth-b70b8e2a53 --speed 1.2 ; pass hard readings as kana
ffprobe -v error -show_entries format=duration -of csv=p=0 assets/vo/vo0.mp3
```
- Voices used: 晓曼 (ListenHub `--speaker 晓曼`, onemin + kids videos). 谷川 `zh-male-guchuan-9d6a4666` is lively but drops volume mid-clip (next rule). 驷码难追 from Handwired on: 解说小明 2.0 `doubao-official-zh_male_jieshuoxiaoming_uranus_bigtts`.
- **Audition the hook before voicing the episode.** Cause: the user heard Handwired vo0 (谷川) as 「很平淡，没有抑扬顿挫」. The API has no emotion/style field (text, voice, speed only), so the levers are the voice and the text. Fix: voice vo0 with 3–4 voices (prefer the doubao `*_uranus_bigtts` 2.0 voices), plus one text variant with spoken punctuation (short clauses, `！` on the surprising fact, `？` on the question). Measure pitch range (librosa pyin, p10–p90 in semitones, octave errors dropped) and let the user pick by ear. Handwired result: 谷川 8.7 st, 解说小明 2.0 10.9 st, and 11.8 st with punctuation (user's pick). Punctuation barely helped 谷川 (+1.2 st) and made it 6 s slower. **Bracket instructions don't pass through ListenHub:** 「[用惊讶的语气]」 and 「（惊讶地）」 were read aloud (tested 2026-10-20). Verify: the user picked the voice from the samples before the full TTS run.
- **谷川 drops 8–10 dB mid-clip; kids/general videos use 晓曼.** Cause: the user heard 「音色声音突然变轻」 in the toilet video (and had flagged the same in another project). Measured: 谷川 `zh-male-guchuan-9d6a4666` vo3 fell 8 dB at 9.2 s, vo2 9.6 dB at the end, clip median −22.8 dBFS. Fix: voice with onemin's chain, `listenhub tts create --text "$T" --mode direct --speaker 晓曼 --lang zh --json`, trim, +7 dB, `alimiter=limit=0.84`, shortest of N takes (`~/.claude/skills/onemin-episode/scripts/vo.sh` does all of it; for another project, copy its steps and convert to mp3 192k if `audio.py` expects mp3). 晓曼 came out ≈ −17 LUFS, about 4–5 dB louder, so re-check VO vs BGM (toilet: BGM 0.2 → 0.28 to stay ~7 dB under). An existing cut is retimed through § Re-voice. Verify: `python3 ~/.claude/skills/concept-motion-explainer/scripts/vo_levels.py assets/vo/vo*.mp3` exits 0 (no mid-clip phrase > 6 dB under the clip median; the last phrase may fall off and is only marked `~`). Run it on every new TTS batch, whatever the voice.
- English: Host Sam `hostsam-dab52696` at `--speed 1.08` (user picked it from a 4-voice audition: `listenhub speakers list --lang en`, one 20 s clip each, concatenated into one file to compare).
- `--speed` validation bug: 1.1 / 1.10 / 1.12 / 1.15 are rejected ("at most two decimals", float rounding). 1.08, 1.2, 1.25 work.
- ListenHub English clips come out ~2 dB quieter than the Chinese ones. Match them (`-af volume=2dB`) before mixing, or the BGM level from the other version drowns the VO.
- Script tone: conversational, a little cheeky ("其实这家伙只会一件事"), short sentences, one idea per clip.

## Writing pass: draft with /ljg-plain, gate with /human-writing (before § Script check)

Cause: scripts were drafted from habit with no writing skill. Handwired v1's VO ended on 「GPU 快，不是因为它聪明，恰恰因为它笨」 and opened 「GPU 更聪明吗？其实，它更笨」: an invented misconception set up only to be knocked down (翻案腔), plus colon-led lines and 「不是…而是」 in the brief. The user asked whether a writing skill existed.

Fix, in order:
1. **Draft** against `/ljg-plain` § 红线 and § 工具箱 (口语检验 first, 零术语, 一句一事, 具体, 诚实). Use its rules only; skip its Org/Denote file output. Everything is 口播, written for the ear.
2. **Gate** with `/human-writing`. Read `references/formats.md` § 口播 and `references/reality.md` (every episode explains a real project with real numbers). Read `references/revision.md` only after the draft exists. Its bans apply to VO **and** on-screen captions.
3. **Hook vs 翻案腔.** The struck-through hook (§1.5) is allowed only when the audience really holds that misconception. If the hook would invent a belief just to strike it out, open on a surprising real fact instead. Either way the VO states things positively: no 不是…而是 / 其实 / 恰恰 / 说到底 moves.
4. **Colons and dashes.** No `：` except before a quoted line, no `—`/`——`. Code and machine fields in captions are exempt.
5. **Hook line with `/dbs-hook`** (its 话题 + Hook + 可信度, diagnosis only). The episode's surprising claim must be spoken within 5 s of the video start, intro breath included. Exception: when the sentences before it only name the scene and narrate the motion on screen right then (next rule), the claim may land as the third sentence, ≤ 9 s (Handwired v2 vo0 A: 「神经网络」 at 8.2 s, user-approved). Cause: Handwired v2 vo0 opened 「这是一个能拖动的小桌面，三个窗口，一个程序坞」, so 「神经网络」 landed at 9.5 s into the video; the setup the picture already shows was spoken first. Fix: lead with the claim, leave what the visuals show to the visuals (re-voiced vo0 → 「这个小桌面背后的程序，整个是一个神经网络」, 14.9 s → 9.9 s). Verify: after TTS, whisper vo0 and check INTRO + the start time of the claim's key word ≤ 5 s.
   - **Open on what is moving on screen right then.** Cause: Handwired v2 vo0 opened 「有个神经网络，里面九千九百多个数，一个都没训练过」. It passed ljg-plain, dbs-hook and check_prose, and the user still said 「开头再形象些」: a count and an abstract noun gave no picture. Fix: make the first sentence point at the thing the first shot is doing (s0 drags `#w-notes` with an elastic spring at 1.4 s → 「你看这个窗口，是一个神经网络在推着它走，拖过去还会弹一下」), let the claim ride on it, and move the numbers to the second sentence. Verify: grep index.html for what animates in the first 3 s of s0. The first sentence's noun and verb name that motion, and the claim still lands ≤ 5 s.
   - **Name the thing before pointing at it.** Cause: the fix above, 「你看这个窗口」, was heard as 「突兀」. A bare deictic (你看 / 这个) was the very first sound, and at that moment (0.74 s into the video) the desktop was still fading in and no window had moved, so 「这个」 pointed at nothing. Fix: sentence 1 names the scene in plain words (「这是一个网页里的小桌面。」), sentence 2 narrates the motion as it happens (「窗口拖过去，松手还会弹一下。」), sentence 3 is the claim (「推着它走的，是一个神经网络！」). In the visuals, the referent is on screen and the motion starts on the spoken verb, never after it. Verify: the TTS input of vo0 doesn't open with 你看 / 这个 / 那个 / 这里; whisper vo0 and check each motion verb's time (+ INTRO) ≥ the start of the tween it names (拖 → drag tween, 弹 → spring) and ≤ that tween's start + 0.3 s.

6. **Every revision re-runs the whole pass, not just the checker.** Cause: Handwired v2 script revision (after 「开头突兀、用词要一般 engineer 能懂、Cheng Lou 发音不对」) ran only check_prose.py and the cold listener. The user asked whether a skill checks the draft, and the skipped steps then found more: 权重 used before it was explained (ljg-plain 零术语), no credibility in the hook (dbs-hook 可信度), a 「……的，是……」 sentence (revision.md 第四遍). Fix: for each revision, run steps 1–5 again plus revision.md 第四/五遍 and § Script check 1–11, and list each one with its result before showing the user. `/dbs-hook` is disabled for model invocation, so Read `~/.claude/skills/dbs-hook/SKILL.md` and apply Phase 3 by hand. Verify: the message to the user has one line per pass with its result, and none is marked skipped.
7. **Names the TTS can't say.** A foreign personal name in the VO (Cheng Lou) came out mispronounced, and dropped in cold it felt abrupt. Fix: keep the name on screen and say who the person is in words (「一位参与过 React 开发的工程师」). Introduce them once, as the hook's credibility, before any 「作者」. Verify: grep the TTS input for Latin-script personal names; each one must be a deliberate choice, auditioned before the full TTS run.

Verify: `python3 ~/.claude/skills/human-writing/scripts/check_prose.py SCRIPT.md` exits clean (the VO lines; strip code blocks and the source table first if they trip it). Then run § Script check.

## Script check: logic and expression (before showing the script, before TTS)

Cause: the unit-test video said 「这本书最警惕的是误报」 and 「书的答案是」, but no book was ever introduced (the source only appears in the end-card credit). The user caught it after the render. The same pass found three more: 漏报/误报 → 四根柱子 had no bridge, 柱子 → 设计 had no bridge, and 「起火」 and 「坏了」 were mixed for the same idea. Every one of these cost a re-TTS, a retime, and a re-render.

Fix: run these checks on the whole script and fix what fails *before* the user sees it:
1. **Every reference is defined.** Each 这本书 / 它 / 这个 / 书里 / 作者 points to something the viewer has already heard in the VO. The on-screen credit does not count. If it is undefined, introduce it once or cut the reference.
2. **Clip-to-clip bridge.** Read only the first sentence of each clip in order. Together they should form one argument. Each clip opens by saying how it relates to the last one: cause, contrast (反过来), question (怎么做到？), or mapping (不漏报，叫防止回归). When a new concept (四根柱子) arrives, tie it to one already explained.
3. **One metaphor, one vocabulary.** State the mapping the first time it comes up (测试 = 报警器, 代码坏了 = 该响). Then use the same words every time, and make the on-screen captions match the VO.
4. **Every claim has its reason.** 「它就响了」 needs the why (调用次数变了). 「测试却不响」 needs the mechanism (照抄实现，跟着一起错).
5. **Pay off the hook.** If the hook promises something (「只做一件事」), deliver the answer within about 20 s and close it again at the end. Don't hold it open for the whole video. The closing line closes it in the hook's own concrete words, not a maxim. Cause: onemin ep02 ended 「之后…几乎都斜十三度半。」 → 「好设计，是让手自己知道该停。」: a jump from a number to an abstract moral, no connective, no reference back, and 「自己知道」 contradicted line 07 (the prompt text was changed to tell people to touch). The user heard it as 牵强 in the preview; the cold listener could restate the facts but dropped the moral. Fix: open the last line with the connective and a pointer to the previous line's key noun, and end on the hook's promise (「所以这十三度半，就是为了让手停住零点二秒。」). Verify: the last line has 所以/这 pointing at the line before, reuses the hook's noun and verb, and the cold listener's one-line summary (check 8) contains it. Run the cold listener on every draft, revisions included: it also caught 「只改了形状」 vs 「提示语也改了」, which checks 1–7 had passed.
6. **Expression.** One idea per sentence. No 书面语 inside spoken lines. Read each line aloud: if it needs a second read to parse, rewrite it.
7. **Dropped subjects (Chinese).** Write out the omitted subject of every sentence. Where the topic changes (AI 写测试 → 「一千块一件」), the dropped subject can't be recovered by ear. Name it (「比如一段算订单的代码：…」). The same goes for the head noun behind a measure word: 「一千块一件」 is stall talk, where the item is in front of you, and in a video the ear fills in the default noun for 件 (衣服). Write 「一件商品一千块」. The same applies when the referent silently switches: 「这个测试」 in a later scene must be the same test the viewer already met, or say 「有的测试」.
8. **Cold listener (the author can't do 1–7 on their own script).** The author always knows the missing subject, so the gap stays invisible to them (user caught 「一千块一件」 after checks 1–6 passed). Spawn a fresh `general-purpose` agent, not a fork. Give it the VO lines in order, the audience profile (e.g. "Chinese developers who know 单元测试/重构/覆盖率"), and a one-line on-screen summary per clip. Don't give it the source article. Ask it, sentence by sentence: explicit subject, link to the previous sentence, and a flag wherever it had to guess. Without the audience profile it flags every term (22 flags, about half of them noise). Triage its table yourself: keep the flags that would hold for the real audience, and drop the rest with a reason.

9. **Sentence-to-sentence connectives (Chinese).** Check 2 covers clips; this covers adjacent sentences inside a line. For every pair, name the relation (contrast, cause, progression, sequence) and check that a word in the second sentence carries it: 却/但/可 for contrast, 因为/所以 for cause, 也/还/连…都 for progression, 后来/又 for sequence. A comma, a dash or a pause is rhythm, not logic, and the ear doesn't recover the relation from it. Cause: onemin ep01 had 「有一排小刻痕。护发素上，没有。」. The contrast was carried only by a pause, and the user caught it after TTS and render: 「护发素上却没有」 reads smoothly. Write the connective into the on-screen title as well, so caption and VO match (check 3).
10. **Numbers as the voice will say them (Chinese).** The TTS input is not the caption. Years are read digit by digit: 「一九九一年」, never 「一千九百九十一年」. In the TTS text, write years out in Chinese numerals (use 零, not 〇, which some engines skip or misread). Keep digits in the on-screen captions. Counts stay cardinal (「六成」「八条」). Standard and model numbers (JIS S 0021) are usually better said by name (「日本工业标准」) than read out. Cause: onemin ep01 sent 「1990 年」「1991 年」 to ListenHub as written, and the user heard the year read as a cardinal number after the full mix. Re-recorded with Chinese numerals, line 04 got 0.68 s shorter and line 09 0.44 s shorter. A re-recorded line moves every phrase inside it, so re-measure with silencedetect and retime anything synced to a word (see § Story beats). Verify: before generating, grep the TTS input for `[0-9]`; every hit must be a deliberate reading.
    - **Decide each reading from context, then spell it in characters.** The point is the reading, not a digit ban: year → digit by digit, count → cardinal, code literal (x 大于四) → cardinal, version/phone → digit by digit. **Pinyin can't carry it.** ListenHub has no phoneme/SSML option (`listenhub openapi tts --help`: text, voice, format, speed only). Tested 2026-10-19: 「重(chong2)新」 came out as 「总二新」, and 「行[háng]」 added a spoken extra syllable. For a 多音字 with a wrong default reading, swap in an unambiguous word (重新 → 再), then audition the clip. Whisper prints digits back as digits, so it can't check a number's reading. Listen to it.
11. **The ear gets the spine; details go to the screen or a closing 补充.** Checks 1–10 catch broken sentences, not too many correct ones. Cause: Handwired v2 vo2/vo3 spoke the relu arithmetic step by step (x 减四、x 减五各过 relu 再相减, 乘一加负四) and the integer caveat in the middle of the mechanism. Every check and the cold listener passed, and the user still said 「vo2 vo3 的表述会不会过于复杂」. Fix: tag every sentence spine or detail. A sentence is spine only if the next one stops making sense without it (samber/technical-video-script's load-bearing test). Formulas and step values go on screen only, and the VO says what they do (「拿两个 relu 一减，就能做出一个开关」); never read on-screen text aloud. Boundary cases and caveats (x 是四点五) leave the mechanism clip and go to the first clip after it where the condition is enforced (Handwired: vo4, where the window inputs are snapped to the 1/64 px grid), answering the flag the claim left (「前提是 x 是整数」 → 「为什么得是整数？」). Not a 补充 clip before the landing: the engineer-viewer loop (L4) scored it 6/7, because a caveat paid two minutes later reads like 先吹后找补 and a 「补充」 label right before the landing tells viewers they can leave. Verify: list each clip's detail sentences; each one is cut, already on screen, or in the clip right after its claim. Re-run check 8 and confirm the cold listener can still say the message after the mechanism clips.

12. **Each claimed benefit stands on what the video shows; don't retract it in the next breath.** Cause: Handwired L3–L5 said 「写出来的网络能训练」 and used the gallery demo as proof, but the gallery trains from scratch and the README says of re-training written weights 「what does that even do? Let's find out!」. Both engineer viewers caught the swap (这不就是普通训练吗). The fix that followed ended every benefit on a hedge (还没试 / 有赢有输 / 早就有), and the frontend viewer dropped to 6: 「收回的话太多……说不清所以呢」. Fix: phrase the benefit as the property the demo really exercises (能求导, shown by a concrete weight nudge: −4 → −4.1, 10 → 10.2, while the if stays at 10), state the unverified extension once in the middle, then close on what is shown (「能求导这件事，项目里已经用上了」). For a speed comparison, concede the known prior art (Go/RE2 don't backtrack) and then say what is new. Verify: for each benefit, name the demo or on-screen number that proves it; its last sentence is a shown fact, not a hedge.
13. **Engineer-viewer loop for technical explainers.** Checks 1–12 and the cold listener catch broken sentences and gaps, but not 「我会在这里划走」 or 「这在懂行的人眼里站不住」. Cause: the Handwired script passed every check, and two simulated engineer viewers still found the 4.5 contradiction, the RE2 straw man, and the demo/claim mismatch. Fix: spawn two fresh `general-purpose` agents in one message, with different stacks (e.g. backend Go/Java 6 years, frontend React/TS 4 years), each reading the VO plus a per-clip screen summary, no web. Per clip they report 听懂了什么 / 卡住 / 太细 / 怀疑 / 会不会划走; at the end, a one-line message, a 1–10 score (10 = 会转给同事), and their top 3 fixes. Check every fix they propose against the source before using it, since viewers invent facts too. Stop when both score ≥ 8 with no 会划走, or after 5 major versions, then hand the user the version log. Verify: the log shows each version's two scores and which complaint each change answered.

Verify: show the user a table of each failing line → its fix, with the check number, next to the script. They approve both before any TTS.

## Word timestamps (sync visual hits to words)

```bash
HF_HUB_OFFLINE=1 mlx_whisper assets/vo/vo3.mp3 --model mlx-community/whisper-small-mlx \
  --language zh --word-timestamps True --output-format json --output-dir /tmp/vot
```
large-v3-turbo download can hang at 0% CPU — use cached small model offline.
Never pass the script as `--initial-prompt`: whisper loops/hallucinates (unit-test-alarm v2: 4 of 8 clips garbage). For simplified output use a short neutral prompt + `--condition-on-previous-text False`: `--initial-prompt "以下是普通话的句子。"`. Homophones (响→想) don't matter for timing; check char count vs the txt.

## Re-voice an existing cut (new VO, same visuals) — time warp, not hand retiming

Cause (unit-test-alarm v2): script fixes changed every clip length; hand-shifting ~200 tween times is error-prone. Fix:
- Keep all authored times in the v1 timebase. `build/warp.py` builds a piecewise-linear map W(v1→v2) from anchors = scene boundaries (same lead/tail around each VO as v1) + characters both VO transcripts share (difflib on per-char whisper times). Don't anchor VO starts if v2 prepends words to a clip. Hand-pin hits on reworded words (`MANUAL`).
- In index.html: real timeline `TL`; `tl = {to,set,fromTo}` wrappers map position `p → W(p)` (durations unchanged); render reads `Wi(clock.t)`; clock/end card/shiftChildren/registration on `TL` with `END = W(S.end)`. Rail fills: `duration: W(out) - W(STEP_AT[i])`. sfx.py maps cues through the same warp.json.
- Verify: print where key beats land vs the new whisper word times (each within ~0.2 s), and `grep -n 'data-duration="<old total>"' index.html` → nothing left (v2 missed `#scene` → everything black after 100 s). Captions authored back-to-back can collide when W compresses the gap — check `content_overlap` info lines.
- Prepended words stretch: when a new clip starts with words v1 never had (v3 「比如一段算订单金额的代码：」), v1 events 0.02 s apart can end up 0.26 s apart. One element shows before the other hides, and they overlap (test card over the chip grid). Fix: pin each event of such a swap to the same word (`(9.84, first(1, "代")), (9.86, first(1, "代") + 0.03)`). Also pin anything that must sit on a sentence that is now new (vo6 card on 「真实的代码里」, not on the later 「测试」).
- A pin drops char anchors within 0.3 s, never scene boundaries. Keep them in a separate `struct` list (v3 lost `(9.6, 9.6)`, so scene 1 started 1.7 s late). The chain step must be 0.01, not 0.02: `9.86 - 9.84` is `0.0199…` in floats, so a 0.02 test silently drops the second pin. Verify: print W at every scene start (it must equal `S`) and at every pin.

## Other-language variant (English cut of the 7-min LLM lecture)

- **Carrier**: pick a line whose tokenization keeps the same number of tokens as the original, so every N-column layout survives. "To be or not to be, that is the ___" is exactly 10 real cl100k tokens (no "for this demo" caveat). Look up real IDs and neighbours with `tiktoken` instead of inventing them.
- **Ribbon pitch**: English words are wider than one CJK glyph. The 80 px pitch / 60 px font became 128 px / 52 px (x = 256 + 128·i), with the slot widening to 256 when the long answer lands. Measure widths with PIL on the subset font first.
- **Subtitles**: one sentence per line if ≤ 72 chars, else pack clauses split at `, ; :` up to 64 chars, and as a last resort split at the space nearest the middle. Sentence split must also handle `."` (period inside a closing quote).
- **BGM** is length-bound: a longer VO needs the bed extended (`acrossfade=d=6` with a mid-track section of itself), then check the mean dB around the seam.
- Agents: give each one the whole seamless chain (ch01–ch04 to one agent), so no boundary spans two agents. Hand over the old-language cue sheet as well, so they map beats instead of guessing.

## BGM (ListenHub music)

```bash
listenhub music instrumental --prompt "<mood: warm minimal ambient electronic, soft pulse, no vocals>" --json
# "unreachable / failover" error → just retry
ffmpeg -i full.mp3 -t <duration+1> -c copy assets/bgm/bgm.mp3
```

## Audio tracks

| track | content | volume | notes |
|---|---|---|---|
| 1 | VO clips | 1 | data-duration ≤ real media length (`clip_media_fit` lint) |
| 2 | BGM | 0.2–0.22 | data-fade-in 1.5, data-fade-out 2.5–3 |
| 3–4 | SFX | 0.15–0.55 | alternate tracks so no same-track overlap |

SFX vocabulary (Pixabay, keep CREDITS.md): whoosh-cinematic (opening), whoosh-short (scene transitions), key-press/typing (text typing), glitch (scramble/ID flicker), pop (element appears), click/click-soft (selection), sparkle (reveal), chime (insight), impact-bass (big statement), riser (build-up).
Generate SFX `<audio>` tags from a list `[time, file, vol]` with a script that assigns track 3/4 greedily to avoid overlap.
Verify mix: `ffmpeg -i renders/video.mp4 -af volumedetect -f null -` → max_volume between -1.5 and -5 dB.

**Loudness-normalize SFX before mixing** (user heard "开头好多噪音"): the library files differ by >15 dB in mean loudness, so the same `vol` is inaudible for one and louder than the VO for another (impact-bass was +8 dB over VO; glitch-2 is a 3.5 s noise bed that sits under speech). Fix:
- `gain = min(1, 10**((-35 - mean_dB)/20) * vol/0.3)` with `mean_dB` from `volumedetect` per file, cap `vol` at 0.5.
- Never put long glitch/noise files under VO — swap glitch-* for `click`.
- Target result: VO ≥ 6 dB over BGM (BGM ~0.13 for a −23 dB VO), integrated ≈ −18 LUFS, peak ≈ −4 dBFS.

## Fonts (CJK subset — full fonts are huge)

```bash
# collect every non-ASCII char in index.html + base set
python3 - <<'PY' > /tmp/chars.txt
import re;s=open('index.html',encoding='utf-8').read()
print(''.join(sorted(set(c for c in s if ord(c)>127)))+'0123456789')
PY
for w in Regular SemiBold Black; do
  pyftsubset NotoSerifSC-$w.otf --text-file=/tmp/chars.txt --flavor=woff2 --output-file=assets/fonts/NotoSerifSC-$w.woff2
done
```
Re-run after any text change, or new glyphs fall back to system fonts.

## HyperFrames gotchas hit in practice

- One paused root timeline `window.__timelines["main"]`; one clock-driver tween for per-frame counters/timecode.
- Same-track `<audio>` overlap = lint error.
- Intentional overflow (scrolling corpus, glyph overhang) → `data-layout-allow-overflow`.
- `content_overlap` warnings are real — move the element, don't ignore.
- Panels over the background need opaque backgrounds or the grid/moon bleeds through.
- `check` "Navigation timeout" under load is transient → retry.
- Vendor GSAP locally (`assets/vendor/gsap.min.js`); a CDN fetch can fail mid-render on a long piece.
- Two `fromTo` on the same element + property: the later one's from-state wins at seek 0 (immediateRender). Any fromTo that is not the first on that property needs `immediateRender: false`, or the opening frame shows the wrong state.
- A layer built for a later scene but drawn at the same spot as an earlier one (e.g. the font 木 that takes over from the morphing glyph at the family chapter) must be hidden at t=0 and shown only at its handover. If it isn't, it sits on top of the earlier scene the whole time, and the viewer sees the "answer" before it is revealed. Verify by snapshotting the early scenes and checking that only that scene's element is visible. Snapshotting only the scene you just built won't catch it.
- Progress rails/timelines: give each stop three distinct states. Future: a faint skeleton (hollow dot, labels at about 0.22 alpha, no content). Current: bright labels, an accent dot at 1.5×, full content. Past: content at 0.4, labels at 0.45. Add an accent fill line that grows with the transition. Never show future content up front.
- Morph sequences (A→B→C): keep the state you just left as a ghost behind the new one, at about 0.16 opacity. Keep only one ghost at a time and fade out the older one, so viewers can compare before and after without clutter. This was user feedback on the hanzi evolution.
- An exiting scene must be gone before the next one fades in. For example, the ring zoom-out ending 0.15s before 沐 starts. If the two overlap at half opacity the frame turns to mud. Check by snapshotting the 0.3s around every hand-off.

## Layout polish: four traps `check` passes (onemin ep01, 2026-10-18)

`hyperframes check` returned 0 errors on all four of these. Only snapshots caught them. The ep01 generator (`onemin-japan/episodes/ep01-shampoo/.hyperframes/gen_comps.py`) already contains every fix, so later episodes that copy it inherit them.

- **An element that fades in later shows from frame 0.**
  - Cause: a `fromTo(..., {immediateRender:false})` doesn't apply its from-state until the tween starts. Before that the element sits at its CSS opacity. Moving the tween later only made the flash last longer: the legend was on screen 2 s before the people it explains.
  - Fix: every element whose entrance comes from a tween gets `opacity:0` in CSS. A key, legend or label enters at or after the thing it labels, never before.
  - Verify: snapshot each scene at its first frame. Only that beat's first elements may be visible.
- **Rising title lines paint over the caption below them.**
  - Cause: a line reveal that animates `y` up from below has no edge. While it travels, it draws across whatever sits under the title block.
  - Fix: clip the title block at its own bottom edge, leaving the top and sides open for overhang: `.h1{clip-path:inset(-40px -40px 0 -40px)}`. The lines then come up from behind that edge.
  - Verify: snapshot mid-reveal (about 0.2 s into each title) and check the caption is untouched.
- **Annotations drift off their target during a zoom.**
  - Cause: the tick marks pointing at the bottle's notches were siblings of the Ken Burns wrapper. The footage scaled 1.15× but the marks didn't, so they ended 50 px off.
  - Fix: anything that points at something in the media lives inside the wrapper that zooms or pans, so it shares the transform. Position it in the media's coordinates, not the stage's.
  - Verify: snapshot the start and end of the move. The mark must sit on the same feature in both.
- **CJK captions break badly.**
  - Cause: the browser wraps at the box edge. It left 「过。」 alone on a line and split 「全行/业」.
  - Fix: in the generator, measure each caption as CJK = 1 and ASCII ≈ 0.55. If it is over one line (box width ÷ font size; 834/38 ≈ 21.9), break with `<br>` at the `，：；` closest to the middle. Never leave a line of 1–3 characters. If there is no punctuation to break at, rewrite the line rather than let the browser break it.
    ```python
    def brk(s, cap=21.9):
        w = lambda t: sum(.55 if c.isascii() else 1 for c in t)
        cuts = [i + 1 for i, c in enumerate(s[:-1]) if c in "，：；"]
        if w(s) <= cap or not cuts or "<br>" in s:  # a hand-broken caption stays as written
            return s
        i = min(cuts, key=lambda i: abs(w(s[:i]) - w(s) / 2))
        return s[:i] + "<br>" + s[i:]
    ```
  - Verify: list every caption over one line together with where its break falls, and snapshot the longest one.

## Story beats: three traps a design critique caught (onemin ep01, 2026-10-18)

`check` passed on all three. The critique found them; before/after snapshots proved the fixes (`ep01-shampoo/.hyperframes/crit-compare/`).

- **The stat appears before the voice says it, and the caption spoils it.**
  - Cause: the six red people started at 10.0 s and 「约六成」 landed at 10.9 s. The voice says 「约六成」 at 11.3 s. The full-sentence caption had already printed the answer at 8.8 s. The stagger was 0.12 s, so six people went red in 0.7 s: that reads as "most", not as "six".
  - Fix:
    - Measure where the stat's word is spoken: `ffmpeg -i vo.wav -af silencedetect=noise=-28dB:d=0.05 -f null -`. The gaps are phrase breaks.
    - The count runs in the pause before the word. Use ≥ 0.2 s per unit so it can be counted, and rebuild any per-unit SFX at the same spacing.
    - The number lands on the word.
    - Split the caption at the colon. The half that holds the answer appears with the number.
    - No legend. The title already says what red means (data-in-motion.md: "No legends").
  - Verify: snapshot just before, at, and just after the spoken word. The number and the answer half of the caption must be absent before it.
- **The emotional peak is the smallest type on screen.**
  - Cause: in the twist, the struck-out 「实用新型专利」 was 64 px 900 weight. The payoff 「主动撤回 → 全行业都能用」 was a 34 px note, and it was the only beat with no title.
  - Fix: the beat's payoff line becomes its title (96 px, second line in the accent colour, same bottom anchor as every other beat). Remove the note that repeats it. The title stays up while the rest of that section plays.
  - Verify: in the peak beat's snapshot, the payoff line must be the largest text in the frame.
- **A drawn hand or arm ends in mid-air.**
  - Cause: the hand SVG stopped at x≈985, so the wrist was cut off inside the frame.
  - Fix: any limb that comes from off-screen extends past the frame edge (bleed). Widen the viewBox; do not scale up the hand.
  - Verify: snapshot with the limb at rest. Its cut end must lie outside 0–1080.

Also: CJK titles get `font-feature-settings:"halt" 1` so 「，」 doesn't leave a 100 px hole at 96 px. The font subset must keep that feature: `pyftsubset … --layout-features+=halt`.

## Machine cutaways: every joint must work (toilet video, 2026-10-16)

- Cause: the user asked to check 「各个部件，管子连接处」. At 4× the toilet cutaway was physically wrong in 13 places: a gap and a step where the bowl met the trap, wall thickness jumping 2→4 px, a solid floor flange blocking the drain, a solid overflow "pipe", a refill line drawn as a bare stroke, a lift rod that shortened as it moved, a hinge and a tank floating in the air, a seal water level 6 px below the weir, and bowl water 32 px above the trap water during the flush (breaks communicating vessels).
- Fix: build each part as it is made, not as a shape. Pipes are hollow, with walls of one thickness, and joins run along the tangent with no shoulder. Every moving link is fixed length and hangs on a pin. Every part sits on or is bolted to something, with a gasket where a pipe passes a wall. Water obeys physics in every frame: one level in connected vessels, the seal level at the weir, and flow only through an open path.
- Verify: before the first render, list every joint and moving part, then snapshot each at 4× in every state (rest, mid-action, refill; the toilet took 12 joints × 3 states = 28 crops) and look at each one. Afterwards, check about 16 keyframes from open to end card for regressions.

## Body parts: adapt an open-licensed drawing, don't freehand (onemin ep02, 2026-10-20)

- Cause: the hand holding the Suica card was drawn freehand as one path. At full size it read as a flat paddle with a single long finger and no thumb, and the user called it 「离谱」.
- Fix: search Iconify (`https://api.iconify.design/search?query=palm%20down`, plus `hand card`, `hand holding`), render the candidates on one contact sheet (`rsvg-convert` + `magick montage`), and read each set's licence from `/collections?prefixes=…`. Prefer MIT / Apache 2.0 (noto, fluent, iconoir, tabler, ph). CC BY needs a credit, and CC BY-SA (openmoji) would put the derived work under the same licence. Take the outline only, restyle it to the design system (paper fill, ink stroke, no shading), and pose it by transforming its points. ep02 used noto `palm-down-hand`, rotated 31° so that the thumb tip and the index tip both rest on the card, with a forearm added where the wrist was cut. Record the source, licence and changes in a code comment and in the episode BRIEF.
- Verify: snapshot every scene that uses the drawing at full size. A stranger should be able to name the part and its grip (thumb, fingers, what it is holding). Nothing should pierce the surface it rests on.

## Long form: chapter sub-compositions and seamless boundaries

For anything over ~2 min, split into one sub-composition per chapter (`compositions/chNN-*.html`, ids prefixed `chNN-`, hosts alternate tracks 2/3). Shared bg/HUD/subtitles/audio stay in root. Hand each chapter to an agent with a written contract (geometry of shared elements, local cue times, safe area, verification steps).

**Boundary rule** (user saw "同一帧闪了一下" at 1:48 and 2:13):
- *Scene change* (different content on both sides): each chapter fades its content out over its last 0.5 s and in over its first 0.5 s. That is fine.
- *Continuous element across the cut* (the carrier ribbon, vector columns): **no exit fade in chapter N and no enter fade in chapter N+1.** Chapter N+1's frame 0 must equal chapter N's last frame. Fading both makes the same picture dip to black and come back, which reads as a flash.
  - **Same data**: one constant for IDs/values across all chapters. ch03 used different token IDs from ch02, so the numbers visibly jumped.
  - **Same geometry**: same box model, font, letter-spacing, line-height, color.
  - If chapter N+1's style differs, start it in chapter N's style and tween to its own over ~0.5 s (e.g. border 0.55→0.22, accent "?" crossfades to a dashed slot).
  - Remove only chapter-N-only labels with a short local fade before the cut.
  - No yoyo or breathe tweens on the shared elements in the last ~1.5 s: a residual offset of a few px shows as a jump.
  - Verify with a pixel diff, not by eye: snapshot `boundary−0.04` and `boundary+0.04`, crop out the HUD (y 130–860), then run `ImageChops.difference`. Max ≲ 20/255 = seamless.

```bash
npx hyperframes snapshot . --at "108.9,108.97" --describe false
python3 -c "from PIL import Image,ImageChops as C;import glob;f=sorted(glob.glob('snapshots/frame-*.png'));print(C.difference(*(Image.open(x).convert('L').crop((80,130,1840,860)) for x in f[:2])).getextrema())"
```

## Intro & end card

Scene times `S` stay VO-derived (0 = first scene). Intro and outro are pure offsets on top:

```js
const INTRO = 1.5, OUTRO = 5.0;                   // 5s: the CTA row needs reading time
const clock = { t: -INTRO };                       // render() sees negative t during intro
// ... build all scene tweens at S times ...
tl.shiftChildren(INTRO, false, 0);                 // push every scene tween back by INTRO
tl.fromTo("#fade", { opacity: 1 }, { opacity: 0, duration: 1.4, ease: "power2.inOut" }, 0);
tl.fromTo("#hud-brand", { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.8, ease: "power3.out", immediateRender: false }, 0.5);
tl.fromTo(clock, { t: -INTRO }, { t: S.end, duration: S.end + INTRO, ease: "none", onUpdate: render }, 0);

const EC = S.end + INTRO;                          // end card starts after the final fade
tl.set(["#cam", "#title", "#hud" /* ...everything on screen */], { opacity: 0 }, EC);
tl.to("#endcard", { opacity: 1, duration: 0.7, ease: "power2.out" }, EC);
tl.to("#ec-k", { opacity: 1, duration: 0.6 }, EC + 0.3);
tl.to("#ec-name span", { opacity: 1, y: 0, duration: 0.7, ease: "expo.out", stagger: 0.09 }, EC + 0.45);
tl.to("#ec-rule", { scaleX: 1, duration: 0.6, ease: "power3.inOut" }, EC + 1.0);
tl.to("#ec-sub", { opacity: 1, duration: 0.6 }, EC + 1.25);
tl.fromTo(".ec-c", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out", stagger: 0.15 }, EC + 1.7);  // CTA row
tl.to("#endcard", { opacity: 0, duration: 0.8, ease: "power2.in" }, EC + OUTRO - 0.9);
```

```html
<div id="endcard">  <!-- inset:0, flex column centered, radial ink→black bg, last child of the scene -->
  <div id="ec-k">关注视频号</div>                <!-- serif 30px, letter-spacing .5em, dim -->
  <div id="ec-name"><span>双</span><span>言</span><span>两</span><span>语</span></div>  <!-- Noto Serif SC 900, 168px -->
  <div id="ec-rule"></div>                       <!-- 300×3 accent -->
  <div id="ec-sub">WECHAT CHANNELS</div>         <!-- mono, dim -->
</div>
```

- Every `<audio>` `data-start` += INTRO (vo0 at 0.6 → 2.1); root, scene and BGM `data-duration` = `S.end + INTRO + OUTRO`.
- Timecode must count from the real frame: `f = round((t + INTRO) * FPS)`.

### Seam check: open and end card (user asked "开头结尾衔接处有没有违和感，顺不顺滑，有没有情绪")

Run `python3 scripts/seams.py renders/video.mp4 snapshots/seam ENDCARD_AT` on every render, and look at both strips. Pass when:
- **Open:** luma rises from 0 over ~1.2 s, and the first VO starts at ≥ 2.0 s with only BGM before it. The 2026-10-08 TCP cut spoke at 0.5 s over the fade-in. It had no `INTRO`.
- **End join:** fade to black reaches 0, and the end card starts fading in within 0.1–0.2 s (no dead black, no hard cut). Max frame-to-frame luma jump is under ~8/255.
- **Music runs under the whole end card** and decays to under −45 dB at the last frame. Cause hit 2026-10-18: lengthening OUTRO (4 → 5 s) or adding an end card to an old cut makes the video longer than `bgm.mp3`. The music stops and the end card sits in silence, so the mood drops.
  - Fix: `ffmpeg -i bgm.mp3 -af atempo=<bgm_len/needed_len> bgm-NN.mp3`. Stretch the whole track; under −15 dB of VO, a ≤ 7% slowdown is inaudible. Don't loop or crossfade a section: the beats don't line up (a flam), and the track's own intro leaves a −34 dB hole mid end card.
- **Climax hit vs VO:** a title-slam SFX overlapping the last VO words must stay within ~4 dB of the VO. The TCP `impact-bass-2` at 0.5 volume was 11 dB over the VO tail; 0.25 kept the hit and the words.
- **Adding an intro to an old cut:** put `tl.shiftChildren(INTRO, false, 0)` after every scene tween. Delete the old `#fade` fade-in at 0 and re-add it after the shift. Clock: `fromTo(clock, {t: -INTRO}, {t: S.end, duration: S.end + INTRO}, 0)`. Add +INTRO to every non-BGM `<audio>`. render() must tolerate t < 0.

## Check, snapshot, render

```bash
npx hyperframes check .
npx hyperframes snapshot . --at 3,12,25,40 --describe false   # read the contact sheets yourself
npx hyperframes render . -q high -o ./renders/video.mp4
# web copy — use bitrate cap; crf barely compresses because of the grain layer
ffmpeg -i renders/video.mp4 -c:v libx264 -preset slow -b:v 7M -maxrate 9M -bufsize 14M \
  -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders/video-web.mp4
```
≈ 0.9 MB per second at 7M (58s → 49MB, 123s → 108MB).
For long pieces (> 3 min) use `-crf 20 -maxrate 6M -bufsize 12M` instead of `-b:v 7M`: 7-min LLM lecture went 272 MB → 76 MB with no visible loss.

## Anti-piracy watermark (post-process, never in the composition)

The user wanted a faint moving mark that "不影响阅读". The first try used fixed spots at 12% plain text. They said it was too strong, and the fixed spots sat next to content. What shipped:
- **Design**: the 印章 seal (双言/两语 2×2 in a thin rounded frame, 92 px, cream). Make it with `scripts/wm_designs.py`, which needs `build/wm-font.otf`.
  - To get the font: `fontTools` → load the woff2 → `flavor=None` → save as .otf. ffmpeg can't read woff2.
- **Opacity 7%**. It hops every 20 s with a 1 s fade in and out, and is off from the end card on.
- **Auto-placement**: for each 20 s window, sample frames at 1 fps and build an edge map, taking the max over the window. Pick the box with the fewest edges inside the safe area (below the HUD, above the captions), with a 48 px margin and at least 500 px from the previous spot. So it never covers text, and it can't be cropped away in one place.
- The end-card start comes from `build/timing.json` `endcard_at` (no hard-coded END). Run `python3 scripts/watermark.py seal renders/video.mp4 snapshots/wm 50,130` to get previews, then `... seal renders/video.mp4 renders/video-web-wm.mp4` for the full encode. On a 7-minute video that takes about 1.5 min, and it does the web encode in the same pass.
- Feed the **web copy** (`renders/video-web.mp4`), not the `-q high` master, to both preview and full encode. The ~540 MB master's decode made a 100 s preview run past 10 min; the web copy did a 115 s preview in 7 s. The placement only reads 1 fps edge maps, and the full encode re-encodes to web bitrate anyway, so the result is the same.
- ffmpeg notes:
  - The fade is `geq` on a looped PNG: `a='alpha(X,Y)*A*fade(T)'`.
  - Preview frames use `-ss T -copyts`, plus `setpts=PTS+T/TB` on the PNG stream so `T` stays absolute.
- Verify:
  - Diff the frame against the unwatermarked web copy at a spot. Expect a max of about 17/255 mid-window, about 5 at 0.3 s into a window, and 0 on the end card.
  - When the input is `video-web.mp4`, the wm file is a second encode, so the whole-frame max diff is about 30 everywhere (encoder noise). Compare means instead. For each window k, take the 100 px box at `build/wm-plan-seal.json[k]` (spot) and the whole frame (rest). v3 got spot about 4.5–5.3 vs rest about 1.5–2.1 at every window, and about 0.1 for both on the end card. Pass `-y` to ffmpeg when grabbing frames to a reused temp file, or it silently re-reads the stale frame.
  - Always keep the unwatermarked `video-web.mp4` too.
