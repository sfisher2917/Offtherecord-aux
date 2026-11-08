import argparse, json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

p = argparse.ArgumentParser()
for name in ("source", "artist", "title", "event"):
    p.add_argument("--" + name, required=True)
p.add_argument("--duration", type=float, default=59)
p.add_argument("--start", type=float, default=0)
p.add_argument("--crop-x", type=float, default=0.5)
a = p.parse_args()
if not 0 < a.duration <= 59.5 or a.start < 0 or not 0 <= a.crop_x <= 1:
    p.error("Duration must be (0,59.5], start >= 0, crop-x between 0 and 1")
if any(not getattr(a, k).strip() for k in ("artist", "title", "event")):
    p.error("Verified artist, title and event are required")
source = Path(a.source)
if not source.is_file():
    p.error("Source does not exist")
probe = json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(source)]))
length = float(probe["format"].get("duration", 0))
if length < a.start + a.duration - 0.15:
    p.error(f"Source too short: {length:.2f}s for start {a.start}s and duration {a.duration}s")
if not any(s.get("codec_type") == "audio" for s in probe["streams"]):
    p.error("Source has no audio")
out = Path("output")
out.mkdir(exist_ok=True)
im = Image.new("RGBA", (1080,1920), (0,0,0,0))
d = ImageDraw.Draw(im)
fontpath = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
boldpath = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
small = ImageFont.truetype(fontpath, 32)
large = ImageFont.truetype(boldpath, 43)
def fitted(text, y, color, maxwidth=880):
    size = 43 if y < 1690 else 31
    while size >= 22:
        f = ImageFont.truetype(boldpath if y < 1690 else fontpath, size)
        if d.textbbox((0,0),text,font=f)[2] <= maxwidth:
            break
        size -= 1
    d.text((91,y), text, font=f, fill=color)
d.text((55,100), "OFFTHERECORD.AUX", font=large, fill="white", stroke_width=2, stroke_fill="black")
d.rounded_rectangle((40,1510,1040,1760), radius=24, fill=(0,0,0,195))
d.rectangle((40,1510,54,1760), fill="#dc3434")
fitted(a.artist, 1535, "white")
fitted(a.title, 1610, "#f4e7d2")
fitted(a.event, 1695, "white")
im.save(out/"overlay.png")
fade = min(1.5, a.duration / 3)
fade_out = max(0, a.duration - fade)
# Crop position: 0=left, 0.5=center, 1=right.
filtergraph = (
    f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
    f"crop=1080:1920:(iw-1080)*{a.crop_x}:((ih-1920)/2),setsar=1[bg];"
    "[bg][1:v]overlay=0:0,format=yuv420p[v];"
    f"[0:a]afade=t=in:st=0:d={fade},afade=t=out:st={fade_out}:d={fade}[aud]"
)
cmd = ["ffmpeg","-hide_banner","-loglevel","error","-y",
       "-ss",str(a.start),"-t",str(a.duration),"-i",str(source),
       "-loop","1","-i",str(out/"overlay.png"),
       "-filter_complex",filtergraph,"-map","[v]","-map","[aud]",
       "-c:v","libx264","-preset","fast","-crf","20","-r","30",
       "-c:a","aac","-b:a","192k","-t",str(a.duration),
       "-movflags","+faststart",str(out/"offtherecord-short.mp4")]
subprocess.run(cmd, check=True, timeout=1200)
final = out/"offtherecord-short.mp4"
meta = json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(final)]))
streams = meta["streams"]
duration = float(meta["format"]["duration"])
assert 0 < duration <= 60 and abs(duration-a.duration) < 0.6, f"Unexpected duration: {duration}"
assert any(s.get("codec_name") == "aac" for s in streams)
assert any(s.get("codec_name") == "h264" and s.get("width") == 1080 and s.get("height") == 1920 for s in streams)
assert final.stat().st_size > 10000
print(f"Rendered and verified {final} ({duration:.2f}s, {final.stat().st_size} bytes)")
