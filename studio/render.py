#!/usr/bin/env python3
"""59-second lyric-to-scene assembly; requires authorized external source media."""
import argparse, json, pathlib, re, subprocess, tempfile, urllib.parse, urllib.request

DURATION=59
def run(*args):
    subprocess.run(args,check=True)
def textfile(p,s):
    pathlib.Path(p).write_text(s,encoding="utf-8")
def download(url,path):
    u=urllib.parse.urlparse(url)
    if u.scheme!="https" or not u.hostname or u.username or u.password:
        raise ValueError("Media URL must be public HTTPS without embedded credentials")
    # Do not permit user-supplied local paths. Github runner is not a secure URL fetch sandbox.
    if u.hostname in ("localhost","127.0.0.1","::1") or u.hostname.endswith((".local",".internal")):
        raise ValueError("Local URL rejected")
    req=urllib.request.Request(url,headers={"User-Agent":"OffTheRecordStudio/1.0"})
    with urllib.request.urlopen(req,timeout=40) as response, open(path,"wb") as f:
        if urllib.parse.urlparse(response.geturl()).scheme!="https":
            raise ValueError("Non-HTTPS redirect rejected")
        max_bytes=300*1024*1024
        size=0
        while True:
            b=response.read(1024*1024)
            if not b: break
            size+=len(b)
            if size>max_bytes: raise ValueError("Source exceeds 300 MB")
            f.write(b)
def esc(s):
    return s.replace("\\","\\\\").replace(":","\\:").replace("'","\\'").replace("%","\\%").replace("\n"," ")
def validate(p):
    if p.get("rights_confirmed") is not True: raise ValueError("Confirm commercial rights first")
    if not p.get("song_url"): raise ValueError("Set song_url")
    scenes=p.get("scenes",[])
    if not 1<=len(scenes)<=12: raise ValueError("Supply 1-12 scenes")
    cursor=0
    for s in scenes:
        if s.get("start")!=cursor or not isinstance(s.get("end"),int) or s["end"]<=cursor or not s.get("video_url"):
            raise ValueError("Scene ranges must be contiguous integer seconds with video_url")
        if s["end"]>DURATION: raise ValueError("Scene exceeds 59 seconds")
        cursor=s["end"]
    if cursor!=DURATION: raise ValueError("Scenes must cover exactly 59 seconds")
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--project",default="studio/project.json")
    a.add_argument("--out",default="music-video.mp4")
    args=a.parse_args()
    p=json.loads(pathlib.Path(args.project).read_text(encoding="utf-8"))
    validate(p)
    with tempfile.TemporaryDirectory() as td:
        t=pathlib.Path(td)
        download(p["song_url"],t/"song")
        segments=[]
        for i,s in enumerate(p["scenes"]):
            source=t/f"source{i}.mp4"
            segment=t/f"segment{i}.mp4"
            download(s["video_url"],source)
            length=s["end"]-s["start"]
            # drawtext uses separate UTF-8 textfiles to avoid escaping user lyrics
            lyric=t/f"lyric{i}.txt"
            textfile(lyric,str(s.get("lyric",""))[:220])
            filters=(
                "scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,fps=30,setsar=1,"
                "drawbox=x=0:y=1600:w=iw:h=320:color=black@0.65:t=fill,"
                "drawbox=x=32:y=1625:w=8:h=255:color=red@0.95:t=fill,"
                "drawtext=textfile='"+str(lyric)+"':fontcolor=white:fontsize=49:"
                "x=65:y=1660:box=0:fix_bounds=1"
            )
            run("ffmpeg","-hide_banner","-loglevel","error","-y",
                "-stream_loop","-1","-i",str(source),"-t",str(length),
                "-vf",filters,"-an","-c:v","libx264","-preset","veryfast",
                "-crf","21","-pix_fmt","yuv420p","-r","30",str(segment))
            segments.append(segment)
        concat=t/"concat.txt"
        textfile(concat,"".join("file '"+str(s)+"'\n" for s in segments))
        visual=t/"visual.mp4"
        run("ffmpeg","-hide_banner","-loglevel","error","-y",
            "-f","concat","-safe","0","-i",str(concat),
            "-c","copy",str(visual))
        # Single bottom box includes artist/title/location as metadata and lyric.
        # Use a compact metadata line at the top of the existing bottom panel.
        metadata=t/"metadata.txt"
        textfile(metadata," | ".join(str(p.get(k,""))[:60] for k in ("artist","title","location")))
        vf="drawtext=textfile='"+str(metadata)+"':fontcolor=white:fontsize=29:x=65:y=1810:fix_bounds=1"
        run("ffmpeg","-hide_banner","-loglevel","error","-y",
            "-i",str(visual),"-i",str(t/"song"),
            "-map","0:v:0","-map","1:a:0","-t","59",
            "-vf",vf,"-af","afade=t=in:st=0:d=1.2,afade=t=out:st=57.8:d=1.2",
            "-c:v","libx264","-preset","veryfast","-crf","20",
            "-c:a","aac","-b:a","192k","-ar","48000",
            "-movflags","+faststart","-pix_fmt","yuv420p",args.out)
        probe=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",args.out],text=True)
        if abs(float(probe.strip())-59)>0.15: raise RuntimeError("Output duration mismatch")
        print("Created:",args.out)
if __name__=="__main__": main()
