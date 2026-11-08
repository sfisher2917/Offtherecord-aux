import argparse,json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser()
for k in ("source","artist","title"):p.add_argument("--"+k,required=True)
p.add_argument("--duration",type=float,default=42)
a=p.parse_args()
if not 0<a.duration<=60:raise ValueError("Duration must be 1-60 seconds")
out=Path("output");out.mkdir(exist_ok=True)
im=Image.new("RGBA",(1080,1920),(0,0,0,0));d=ImageDraw.Draw(im)
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=ImageFont.truetype(font,40)
d.rounded_rectangle((40,1520,1040,1730),radius=22,fill=(0,0,0,195))
d.rectangle((40,1520,52,1730),fill="#dc3434")
d.text((80,1545),a.artist[:35],font=f,fill="white")
d.text((80,1620),a.title[:40],font=f,fill="#f4e7d2")
d.text((65,125),"OFFTHERECORD.AUX",font=f,fill="white")
im.save(out/"overlay.png")
cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-t",str(a.duration),"-i",a.source,"-loop","1","-i",str(out/"overlay.png"),"-filter_complex","[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg];[bg][1:v]overlay=0:0,format=yuv420p[v]","-map","[v]","-map","0:a:0","-c:v","libx264","-preset","medium","-crf","19","-r","30","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(out/"offtherecord-short.mp4")]
subprocess.run(cmd,check=True)
meta=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(out/"offtherecord-short.mp4")]))
assert float(meta["format"]["duration"])<=60.3
assert any(x.get("codec_name")=="aac" for x in meta["streams"])
assert any(x.get("width")==1080 and x.get("height")==1920 for x in meta["streams"])
print("Rendered and validated",out/"offtherecord-short.mp4")
