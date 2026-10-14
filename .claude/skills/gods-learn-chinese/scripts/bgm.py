# Local BGM with MusicGen (facebook/musicgen-small, ~28s per track) -> assets/bgm/<name>.wav
# Run in the project dir:  python3 bgm.py   (takes a few minutes on Apple MPS; run in background)
# build.py loops a track automatically when a scene run is longer than the file.
import json, os
import torch, soundfile as sf
from transformers import AutoProcessor, MusicgenForConditionalGeneration

S = json.load(open("script.json"))
dev = "mps" if torch.backends.mps.is_available() else "cpu"
p = AutoProcessor.from_pretrained("facebook/musicgen-small")
m = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to(dev)
os.makedirs("assets/bgm", exist_ok=True)
for name, cfg in S.get("bgm", {}).items():
    out = f"assets/bgm/{name}.wav"
    if os.path.exists(out):
        continue
    inp = p(text=[cfg["prompt"]], padding=True, return_tensors="pt").to(dev)
    audio = m.generate(**inp, do_sample=True, guidance_scale=3.0, max_new_tokens=int(cfg.get("sec", 28) * 50))  # ~50 tokens per second
    sf.write(out, audio[0, 0].cpu().numpy(), m.config.audio_encoder.sampling_rate)
    print(name, "ok", flush=True)
