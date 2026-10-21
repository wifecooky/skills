#!/usr/bin/env python3
"""Word timings for onemin VO lines, so visual hits land on the spoken word.
usage: words.py <episode-dir> <key> [<key> ...]   prints  <key> word start-end  per word"""
import csv, pathlib, sys
import whisper

ep, keys = pathlib.Path(sys.argv[1]), sys.argv[2:]
lines = {r[0]: r[1] for r in csv.reader(open(ep / "assets/vo/xiaoman/lines.tsv", encoding="utf-8"), delimiter="\t")}
model = whisper.load_model("small")
for k in keys:
    r = model.transcribe(str(ep / f"assets/vo/{k}.wav"), language="zh", word_timestamps=True, initial_prompt=lines.get(k, ""))
    print(k, " ".join(f"{w['word'].strip()} {w['start']:.2f}-{w['end']:.2f}" for s in r["segments"] for w in s["words"]))
