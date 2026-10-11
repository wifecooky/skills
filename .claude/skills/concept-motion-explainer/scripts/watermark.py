# Moving faint watermark. Every P seconds the mark fades to a new spot; each spot is the
# emptiest box (fewest edges = least text/graphics) in that window, so it never covers reading.
# usage: python3 build/watermark.py DESIGN in.mp4 out.mp4            → full encode
#        python3 build/watermark.py DESIGN in.mp4 DIR 20,40,60       → preview PNGs
# DESIGN = seal | mark | vert (build/wm-DESIGN.png, made by build/wm_designs.py)
import json, math, subprocess, sys
import numpy as np
from PIL import Image

P, A, END, FPS = 20, 0.07, 407.09, 30     # window s, opacity, end card start, fps
SAFE = (60, 130, 1860, 860)               # x0,y0,x1,y1: below HUD, above captions
Q = 4                                     # analysis downscale
MIN_HOP = 500                             # px between consecutive spots

design, src, out = sys.argv[1:4]
at = sys.argv[4] if len(sys.argv) > 4 else None
png = f"build/wm-{design}.png"
w, h = Image.open(png).size


def edge_maps():
    # 1 fps grayscale frames at 1/Q size → per-frame edge masks
    W, H = 1920 // Q, 1080 // Q
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-t", str(END),
                          "-vf", f"fps=1,scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
    g = np.abs(np.diff(f, axis=1, prepend=0)) + np.abs(np.diff(f, axis=2, prepend=0))
    return (g > 14).astype(np.float32)


def plan():
    e = edge_maps()
    pad = 48 // Q                          # keep a margin around the mark too
    bw, bh = w // Q + 2 * pad, h // Q + 2 * pad
    spots, prev = [], None
    for k in range(math.ceil(END / P)):
        occ = e[k * P:(k + 1) * P].max(axis=0)          # anything drawn at any moment
        ii = np.pad(occ.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
        best = None
        for y in range(SAFE[1], SAFE[3] - h + 1, 20):
            for x in range(SAFE[0], SAFE[2] - w + 1, 20):
                y0, x0 = max(0, y // Q - pad), max(0, x // Q - pad)
                c = ii[y0 + bh, x0 + bw] - ii[y0, x0 + bw] - ii[y0 + bh, x0] + ii[y0, x0]
                if prev and math.dist((x, y), prev) < MIN_HOP:
                    c += 1e6
                if best is None or c < best[0]:
                    best = (c, x, y)
        prev = best[1:]
        spots.append(prev)
    return spots


def nest(vals):
    # if(lt(t,P),v0,if(lt(t,2P),v1,...))
    s = str(vals[-1])
    for k in range(len(vals) - 2, -1, -1):
        s = f"if(lt(t\\,{(k + 1) * P})\\,{vals[k]}\\,{s})"
    return s


spots = plan()
json.dump(spots, open(f"build/wm-plan-{design}.json", "w"))
fade = f"{A}*min(1\\,min(mod(T\\,{P})\\,{P}-mod(T\\,{P})))"


def graph(off):
    return (f"[1]format=rgba,setpts=PTS+{off}/TB,"
            f"geq=r='r(X\\,Y)':g='g(X\\,Y)':b='b(X\\,Y)':a='alpha(X\\,Y)*{fade}'[wm];"
            f"[0][wm]overlay=x='{nest([s[0] for s in spots])}':y='{nest([s[1] for s in spots])}'"
            f":enable='lt(t\\,{END})':shortest=1")


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args, check=True)


if at:
    import os
    os.makedirs(out, exist_ok=True)
    for t in at.split(","):
        ff(["-ss", t, "-copyts", "-i", src, "-loop", "1", "-framerate", str(FPS), "-i", png,
            "-filter_complex", graph(t), "-frames:v", "1", f"{out}/wm-{design}-{t}.png"])
else:
    ff(["-i", src, "-loop", "1", "-framerate", str(FPS), "-i", png, "-filter_complex", graph(0),
        "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "6M", "-bufsize", "12M",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
