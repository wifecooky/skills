#!/usr/bin/env python3
"""Generate continuous scene narration and independent, measured voice timelines."""
import argparse
from array import array
import asyncio
import http.client
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request

VOICES = {name: f"zh-CN-{full}Neural" for name, full in {
    "yunxi": "Yunxi", "xiaoyi": "Xiaoyi", "xiaoxiao": "Xiaoxiao",
    "yunxia": "Yunxia", "yunyang": "Yunyang", "yunjian": "Yunjian",
}.items()}

LISTENHUB_API = "https://api.marswave.ai/openapi/v1"
LISTENHUB_RATE = 32000
LISTENHUB_VOICES = {
    "houge": "doubao-official-zh_male_sunwukong_mars_bigtts",  # 猴哥，孙悟空腔
    "suzhe": "suzhe-45bbbe54",  # 苏哲，科普讲解男声
    "yuanye": "CN-Man-Beijing-V2",  # 原野，沉稳男声
    "gaoqing": "gaoqing3-bfb5c88a",  # 高晴，明快女声
    "xiaoman": "chat-girl-105-cn",  # 晓曼，温和女声
}
KOKORO_REPO = "hexgrad/Kokoro-82M-v1.1-zh"
KOKORO_RATE = 24000
SENTENCE_GAP = 0.5  # seconds of silence between sentences for engines that synthesize per sentence
# Heteronyms common in lesson scripts; pypinyin's full heteronym list is mostly obscure readings
HETERONYMS = set("长地得行重还都为数空角少分会和好当只没上处发干觉教强中应更便系"
                 "相血差传朝曾恶假降尽卷累露难宁省似弹挑调藏折着种乐率载兴给背薄扎切参")


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def duration(path):
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", str(path),
    ], capture_output=True, text=True, check=True)
    seconds = float(json.loads(result.stdout)["format"]["duration"])
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError(f"Invalid audio duration: {path}")
    return seconds


def stamp(seconds):
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def read_scenes(path):
    scenes = json.loads(path.read_text(encoding="utf-8")).get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("Input must contain a nonempty scenes array")
    seen = set()
    for scene in scenes:
        if not isinstance(scene, dict):
            raise ValueError("Each scene must be an object")
        sid, text = scene.get("id"), scene.get("text")
        if not isinstance(sid, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", sid):
            raise ValueError("Scene IDs must use 1–64 letters, digits, underscores or hyphens")
        if sid in seen:
            raise ValueError(f"Duplicate scene ID: {sid}")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Scene {sid} needs nonempty text")
        pause = scene.get("pauseAfter", 0)
        if isinstance(pause, bool) or not isinstance(pause, (int, float)) \
                or not math.isfinite(pause) or pause < 0:
            raise ValueError(f"Scene {sid}: pauseAfter must be a nonnegative number of seconds")
        seen.add(sid)
    return scenes


async def stream_to(edge_tts, text, voice, rate, temporary):
    events = []
    with temporary.open("wb") as stream:
        async for event in edge_tts.Communicate(
            text, voice, rate=rate, boundary="SentenceBoundary"
        ).stream():
            if event["type"] == "audio":
                stream.write(event["data"])
            elif event["type"] == "SentenceBoundary":
                events.append(event)
    return events


async def synthesize(edge_tts, text, voice, rate, target, timeout, attempts=3):
    """Edge TTS is an unofficial endpoint; transient NoAudioReceived and hangs happen."""
    temporary = target.with_suffix(".partial.mp3")
    for attempt in range(attempts):
        try:
            events = await asyncio.wait_for(
                stream_to(edge_tts, text, voice, rate, temporary), timeout)
            seconds = duration(temporary)
            if not events:
                raise ValueError("Service returned audio without sentence boundaries")
            temporary.replace(target)
            return seconds, events
        except Exception as exc:
            temporary.unlink(missing_ok=True)
            if attempt + 1 == attempts:
                raise RuntimeError(
                    f"{voice}/{target.stem}: synthesis failed after {attempts} attempts "
                    f"({type(exc).__name__}: {exc})") from exc
            print(f"Retrying {voice}/{target.stem} ({type(exc).__name__})", flush=True)
            await asyncio.sleep(2 ** attempt)


async def edge_engine(args, scenes):
    try:
        import edge_tts
    except ImportError as exc:
        raise RuntimeError("Install edge-tts in your task's Python environment first") from exc
    available = await edge_tts.list_voices()
    if args.list_voices:
        print(json.dumps([v for v in available if v["Locale"].startswith("zh-")],
                         ensure_ascii=False, indent=2))
        return None
    voice_ids = list(dict.fromkeys(VOICES.get(v, v) for v in (args.voice or ["yunxi"])))
    known = {v["ShortName"] for v in available}
    for voice in voice_ids:
        if voice not in known:
            raise ValueError(f"Voice unavailable: {voice}; use --list-voices")

    async def synth(text, voice, target):
        return await synthesize(edge_tts, text, voice, args.rate, target, args.timeout)
    return voice_ids, synth, {}


def kokoro_voices():
    from huggingface_hub import snapshot_download
    try:
        folder = snapshot_download(KOKORO_REPO, allow_patterns="voices/*", local_files_only=True)
    except OSError:
        folder = snapshot_download(KOKORO_REPO, allow_patterns="voices/*")
    return sorted(p.stem for p in (Path(folder) / "voices").glob("*.pt"))


def load_lexicon(path):
    lexicon = json.loads(path.read_text(encoding="utf-8"))
    for word, reading in lexicon.items():
        if not word or not isinstance(reading, str) or len(reading.split()) != len(word):
            raise ValueError(f"Lexicon entry {word!r} needs one pinyin (e.g. chang2) per character")
    return lexicon


def english_phonemes():
    """misaki's Chinese frontend has no English G2P; its English dictionary covers letters, sin, cos."""
    import misaki
    gold = json.loads((Path(misaki.__file__).with_name("data") / "us_gold.json")
                      .read_text(encoding="utf-8"))

    def lookup(key):
        entry = gold.get(key)
        return entry.get("DEFAULT") if isinstance(entry, dict) else entry

    def phonemes(text):
        # Whole word first (sin, cos, pi); otherwise spell it letter by letter: AB -> ˈA bˈi
        return lookup(text) or lookup(text.lower()) or " ".join(lookup(c.upper()) or c for c in text)
    return phonemes


def apply_lexicon(frontend, lexicon):
    """misaki picks heteronym readings by dictionary, then forces neutral tone on 的/地/得 word endings."""
    import jieba
    from pypinyin import load_phrases_dict
    for word in lexicon:
        jieba.add_word(word)
    load_phrases_dict({w: [[p] for p in r.split()] for w, r in lexicon.items()})
    frontend.tone_modifier.must_not_neural_tone_words.update(lexicon)


def heteronyms(frontend, text):
    """Readings misaki will actually use for common heteronyms, so wrong ones can go into the lexicon."""
    import cn2an
    from difflib import get_close_matches
    from jieba import posseg
    from pypinyin import Style, pinyin
    found = []
    for word, pos in frontend.tone_modifier.pre_merge_for_modify(
            posseg.lcut(cn2an.transform(text, "an2cn"))):
        if not re.fullmatch(r"[\u4e00-\u9fff]+", word):
            continue
        initials, finals = frontend._get_initials_finals(word)
        finals = frontend.tone_modifier.modified_tone(word, pos, finals)
        for char, initial, final in zip(word, initials, finals):
            options = pinyin(char, style=Style.TONE3, heteronym=True, neutral_tone_with_five=True)[0]
            if char not in HETERONYMS or len(options) < 2:
                continue
            # misaki spells finals PaddleSpeech-style (uei2, zhiii3); show the matching pypinyin spelling
            same_tone = [o for o in options if o[-1] == final[-1]]
            chosen = get_close_matches(initial + final, same_tone, n=1, cutoff=0) or [initial + final]
            found.append((char, word, chosen[0], " ".join(options)))
    return found


def trim(audio, rate, threshold=0.01, keep=0.08):
    """Engines pad sentences with silence of varying length; cut it so SENTENCE_GAP sets the pauses."""
    first = next((i for i, v in enumerate(audio) if abs(v) > threshold), None)
    if first is None:
        return audio
    last = next(i for i in range(len(audio) - 1, -1, -1) if abs(audio[i]) > threshold)
    pad = int(rate * keep)
    return audio[max(0, first - pad):last + pad]


def assemble(text, render, rate, target):
    """Synthesize sentence by sentence (render gives mono float32 samples) and join with fixed gaps,
    so every sentence gets a boundary measured in samples."""
    audio, events = array("f"), []
    for sentence in re.findall(r"[^。！？]+[。！？]*", text):
        sentence = sentence.strip()
        if not sentence:
            continue
        if events:
            audio.extend(array("f", bytes(4 * int(rate * SENTENCE_GAP))))
        chunk = trim(render(sentence), rate)
        events.append({"type": "SentenceBoundary", "text": sentence,
                       "offset": round(len(audio) / rate * 1e7),
                       "duration": round(len(chunk) / rate * 1e7)})
        audio.extend(chunk)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(rate), "-ac", "1",
        "-i", "pipe:", "-b:a", "128k", str(target),
    ], input=audio.tobytes(), check=True)
    return duration(target), events


async def kokoro_engine(args, scenes):
    if args.list_voices:
        print("\n".join(kokoro_voices()))
        return None
    try:
        from kokoro import KModel, KPipeline
    except ImportError as exc:
        raise RuntimeError("Install kokoro and misaki[zh] in your task's Python environment first") from exc
    lexicon = load_lexicon(Path(__file__).with_name("kokoro_lexicon.json"))
    if args.lexicon:
        lexicon.update(load_lexicon(args.lexicon))
    pipeline = KPipeline(lang_code="z", repo_id=KOKORO_REPO,
                         model=KModel(repo_id=KOKORO_REPO).eval(), en_callable=english_phonemes())
    apply_lexicon(pipeline.g2p.frontend, lexicon)
    for scene in scenes:
        for char, word, chosen, options in heteronyms(pipeline.g2p.frontend, scene["text"]):
            print(f"{scene['id']}\t{char}\t{word}\t{chosen}\t备选 {options}", flush=True)
    if args.check:
        return None
    voice_ids = list(dict.fromkeys(args.voice or ["zm_066"]))
    speed = 1 + int(args.rate[:-1]) / 100

    async def synth(text, voice, target):
        def render(sentence):
            audio = array("f")
            for result in pipeline(sentence, voice=voice, speed=speed):
                if result.audio is not None:
                    audio.frombytes(result.audio.numpy().astype("float32").tobytes())
            return audio
        return assemble(text, render, KOKORO_RATE, target)
    return voice_ids, synth, {"model": KOKORO_REPO, "lexicon": lexicon}


def listenhub_request(path, body, timeout, attempts=3):
    """ListenHub OpenAPI: Bearer key from LISTENHUB_API_KEY; JSON in, JSON or raw audio out."""
    key = os.environ.get("LISTENHUB_API_KEY")
    if not key:
        raise RuntimeError("Set LISTENHUB_API_KEY (ListenHub API key), or use --engine edge-tts / kokoro")
    request = urllib.request.Request(
        LISTENHUB_API + path, method="POST" if body is not None else "GET",
        data=None if body is None else json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read()
                if response.headers.get_content_type().startswith("audio/"):
                    return payload
                reply = json.loads(payload)
                if reply.get("code") != 0:
                    raise RuntimeError(f"ListenHub {path}: {reply.get('message') or reply}")
                return reply["data"]
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            if exc.code in (401, 402, 403) or attempt + 1 == attempts:
                raise RuntimeError(f"ListenHub {path}: HTTP {exc.code} {detail}") from exc
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError) as exc:
            if attempt + 1 == attempts:
                raise RuntimeError(f"ListenHub {path}: {type(exc).__name__}: {exc}") from exc
        print(f"Retrying ListenHub {path}", flush=True)
        time.sleep(2 ** attempt)


async def listenhub_engine(args, scenes):
    speakers = listenhub_request("/speakers/list?language=zh", None, args.timeout)["items"]
    if args.list_voices:
        for speaker in speakers:
            profile = speaker.get("profile") or {}
            print(f"{speaker['speakerId']}\t{speaker['name']}\t{speaker['gender']}\t"
                  f"{profile.get('descriptionLocalized', {}).get('zh', '')}")
        return None
    voice_ids = list(dict.fromkeys(LISTENHUB_VOICES.get(v, v) for v in (args.voice or ["houge"])))
    known = {s["speakerId"] for s in speakers}
    for voice in voice_ids:
        if voice not in known:
            raise ValueError(f"Voice unavailable: {voice}; use --list-voices")
    speed = round(1 + int(args.rate[:-1]) / 100, 2)

    async def synth(text, voice, target):
        def render(sentence):
            mp3 = listenhub_request("/tts", {"input": sentence, "voice": voice, "speed": speed,
                                             "response_format": "mp3"}, args.timeout)
            audio = array("f")
            audio.frombytes(subprocess.run([
                "ffmpeg", "-v", "error", "-i", "pipe:", "-f", "f32le",
                "-ar", str(LISTENHUB_RATE), "-ac", "1", "pipe:",
            ], input=mp3, capture_output=True, check=True).stdout)
            return audio
        return assemble(text, render, LISTENHUB_RATE, target)
    return voice_ids, synth, {"api": LISTENHUB_API}


ENGINES = {"listenhub": listenhub_engine, "edge-tts": edge_engine, "kokoro": kokoro_engine}


async def run(args):
    scenes = None if args.list_voices else read_scenes(args.input)
    engine = await ENGINES[args.engine](args, scenes)
    if engine is None:
        return
    voice_ids, synth, extra = engine
    if not shutil.which("ffprobe"):
        raise RuntimeError("ffprobe must be available on PATH")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    # A fresh directory prevents stale manifests from describing partially replaced audio.
    if any(out.iterdir()):
        raise ValueError(f"Output directory must be empty: {out}")
    manifest = {"engine": args.engine, "aiGenerated": True, "fps": args.fps,
                "rate": args.rate, **extra, "tracks": []}
    lead = math.ceil(args.lead * args.fps)
    tail = math.ceil(args.tail * args.fps)
    for voice in voice_ids:
        folder = out / voice
        folder.mkdir()
        try:
            manifest["tracks"].append(await synthesize_track(scenes, voice, folder, out, args, lead, tail, synth))
        except BaseException:
            # Keep finished scenes for inspection; an empty folder would only block a rerun.
            if not any(folder.iterdir()):
                folder.rmdir()
            raise
    save_json(out / "manifest.json", manifest)
    print(f"Manifest: {out / 'manifest.json'}")


async def synthesize_track(scenes, voice, folder, out, args, lead, tail, synth):
    track = {"voice": voice, "scenes": []}
    cursor, subtitles = 0, []
    for scene in scenes:
        target = folder / (scene["id"] + ".mp3")
        seconds, events = await synth(scene["text"], voice, target)
        save_json(target.with_suffix(".boundaries.json"), events)
        audio_start = cursor + lead
        pause = math.ceil(scene.get("pauseAfter", 0) * args.fps)
        length = lead + math.ceil(seconds * args.fps) + tail + pause
        boundaries = []
        for index, event in enumerate(events):
            start = max(0, event["offset"] / 1e7)
            end = min(seconds, (event["offset"] + event["duration"]) / 1e7)
            if index + 1 < len(events):
                end = min(end, events[index + 1]["offset"] / 1e7)
            if end <= start:
                raise ValueError(f"Invalid sentence boundary in {voice}/{scene['id']}")
            boundaries.append({"text": event["text"], "startSeconds": start, "endSeconds": end})
            subtitles.append((audio_start / args.fps + start,
                              audio_start / args.fps + end, event["text"]))
        track["scenes"].append({
            "id": scene["id"], "text": scene["text"],
            "file": target.relative_to(out).as_posix(), "durationSeconds": seconds,
            "startFrame": cursor, "durationFrames": length, "pauseAfterFrames": pause,
            "audioStartFrame": audio_start, "boundaries": boundaries,
        })
        cursor += length
        print(f"Generated {voice}/{scene['id']}: {seconds:.2f}s", flush=True)
    srt = folder / "captions.srt"
    srt.write_text("\n\n".join(
        f"{i}\n{stamp(start)} --> {stamp(end)}\n{text}"
        for i, (start, end, text) in enumerate(subtitles, 1)
    ) + "\n", encoding="utf-8")
    track.update(durationFrames=cursor, captions=srt.relative_to(out).as_posix())
    return track


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=list(ENGINES), default="listenhub")
    parser.add_argument("--list-voices", action="store_true")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--out", type=Path, help="New or empty output directory")
    parser.add_argument("--voice", action="append", help="Alias or full ID; repeat to compare voices")
    parser.add_argument("--rate", default="-3%")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--lead", type=float, default=0.25, help="Seconds before each scene's audio")
    parser.add_argument("--tail", type=float, default=0.25, help="Seconds after each scene's audio")
    parser.add_argument("--timeout", type=float, default=60,
                        help="Seconds allowed per synthesis attempt before retrying")
    parser.add_argument("--lexicon", type=Path,
                        help='Kokoro: JSON {"word": "pin1 yin1"} added to scripts/kokoro_lexicon.json')
    parser.add_argument("--check", action="store_true",
                        help="Kokoro: print heteronym readings for --input and exit")
    args = parser.parse_args()
    if (args.check or args.lexicon) and args.engine != "kokoro":
        parser.error("--check and --lexicon apply to --engine kokoro")
    if not args.list_voices and (args.input is None or (args.out is None and not args.check)):
        parser.error("--input and --out are required for synthesis")
    if args.fps <= 0 or not all(math.isfinite(v) and v >= 0 for v in (args.lead, args.tail)):
        parser.error("fps must be positive; lead and tail must be finite and nonnegative")
    if not (math.isfinite(args.timeout) and args.timeout > 0):
        parser.error("timeout must be a positive number of seconds")
    if not re.fullmatch(r"[+-]\d+%", args.rate):
        parser.error("rate must look like --rate=-3% or --rate=+0%")
    try:
        asyncio.run(run(args))
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
