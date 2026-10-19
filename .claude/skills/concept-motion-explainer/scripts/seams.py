# Seam check: python3 seams.py VIDEO OUT_PREFIX ENDCARD_AT → luma curve (10 fps), max frame jump, loudness (0.25 s)
# and a 0.5 s frame strip for the open (0–4 s) and the end-card join (EC−3 … EC+5). Writes OUT_PREFIX-{open,ec}.png.
import sys, subprocess, numpy as np
from PIL import Image
v, out, EC = sys.argv[1], sys.argv[2], float(sys.argv[3])
def frames(t0, t1, fps, w=320):
    h = w * 9 // 16
    raw = subprocess.run(["ffmpeg","-v","error","-ss",str(t0),"-t",str(t1-t0),"-i",v,"-vf",f"fps={fps},scale={w}:{h}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,h,w,3)
def loud(t0, t1, step=0.25):
    raw = subprocess.run(["ffmpeg","-v","error","-ss",str(t0),"-t",str(t1-t0),"-i",v,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
    a = np.frombuffer(raw,np.float32); n=int(16000*step)
    return [round(20*np.log10(np.sqrt(np.mean(a[i:i+n]**2))+1e-9)) for i in range(0,len(a)-n+1,n)]
for name, t0, t1 in (("open", 0, 4), ("ec", EC-3, EC+5)):
    f = frames(t0, t1, 10)
    lum = f.mean(axis=(1,2,3))
    jumps = np.abs(np.diff(lum))
    print(f"{name} {t0:.1f}-{t1:.1f}s luma@10fps:", [round(x) for x in lum])
    print(f"  max frame-to-frame luma jump {jumps.max():.1f} at {t0+0.1*(jumps.argmax()+1):.1f}s")
    print(f"  loudness@0.25s:", loud(t0, t1))
    pick = f[::5]  # every 0.5 s
    strip = Image.new("RGB", (320*len(pick), 180))
    for i, fr in enumerate(pick): strip.paste(Image.fromarray(fr), (320*i, 0))
    strip.save(f"{out}-{name}.png")
