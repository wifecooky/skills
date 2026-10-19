# Verify a watermarked encode: python3 wm_check.py PROJECT_DIR → per-window |diff| inside the seal box vs whole frame
# (re-encode noise ≈1–2; seal ≈5+), and the end card must show ≈0 in every spot box.
import sys,subprocess,numpy as np,json
d=sys.argv[1]; P=20
def fr(f,t):
    b=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",f,"-frames:v","1","-f","rawvideo","-pix_fmt","gray","-"],capture_output=True).stdout
    return np.frombuffer(b,np.uint8).reshape(1080,1920).astype(float)
spots=json.load(open(f"{d}/build/wm-plan-seal.json")); end=json.load(open(f"{d}/build/timing.json"))["endcard_at"]
a,b=f"{d}/renders/video-web.mp4",f"{d}/renders/video-web-wm.mp4"
out=[]
for k,(x,y) in enumerate(spots):
    t=k*P+10
    if t>=end: t=(k*P+end)/2
    df=np.abs(fr(a,t)-fr(b,t)); s=df[y:y+92,x:x+92].mean(); r=df.mean()
    out.append(f"{t:.0f}s spot {s:.2f}/rest {r:.2f}")
df=np.abs(fr(a,end+2.5)-fr(b,end+2.5)); out.append(f"EC max-box {max(df[y:y+92,x:x+92].mean() for x,y in spots):.2f}/rest {df.mean():.2f}")
print(d+": "+" | ".join(out))
