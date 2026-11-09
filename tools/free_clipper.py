#!/usr/bin/env python3
"""Free vertical clipper: FFmpeg, single translucent lower third, audio fades."""
import os, subprocess, pathlib, math, json, textwrap

def number(name, default):
    try: value=float(os.getenv(name,default))
    except ValueError: raise SystemExit(f"Invalid {name}")
    if not math.isfinite(value): raise SystemExit(f"Invalid {name}")
    return value

start=number("START",0)
duration=number("DURATION",59)
if start<0 or not 1<=duration<=60: raise SystemExit("Start must be nonnegative; duration 1..60 seconds")
artist=os.getenv("ARTIST","Artist").strip()[:90]
song=os.getenv("SONG","Song").strip()[:90]
location=os.getenv("LOCATION","Live performance").strip()[:90]
if not all((artist,song,location)): raise SystemExit("Artist, song and location required")
pathlib.Path("output").mkdir(exist_ok=True)
def esc(s):
    return s.replace("\\","\\\\").replace(":","\\:").replace("'","\\'").replace("%","\\%").replace(",","\\,").replace("[","\\[").replace("]","\\]")
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# One dark translucent information panel and a red accent bar; no secondary label.
# Escape FFmpeg drawtext expressions and keep metadata length bounded.
for name, length in (("instagram",min(duration,59)),("youtube",duration)):
    fade=max(0.1,min(1.5,length/4))
    y=1535
    filters=[
      "scale=1080:1920:force_original_aspect_ratio=increase",
      "crop=1080:1920",
      "setsar=1",
      f"drawbox=x=35:y={y}:w=1010:h=260:color=black@0.62:t=fill",
      f"drawbox=x=35:y={y}:w=9:h=260:color=0xC8192E:t=fill",
    ]
    for i,line in enumerate([artist,song,location]):
        # Long labels truncated to avoid spilling off the panel.
        line=line[:42]
        filters.append(f"drawtext=fontfile={font}:text='{esc(line)}':x=70:y={y+28+i*73}:fontsize={42 if i==0 else 36}:fontcolor=white")
    cmd=["ffmpeg","-hide_banner","-y","-ss",str(start),"-i","source.mp4",
         "-t",str(length),"-vf",",".join(filters),
         "-af",f"afade=t=in:st=0:d={fade},afade=t=out:st={max(0,length-fade)}:d={fade}",
         "-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",
         f"output/{name}_vertical.mp4"]
    subprocess.run(cmd,check=True)
print("Rendered both platform-ready files.")
