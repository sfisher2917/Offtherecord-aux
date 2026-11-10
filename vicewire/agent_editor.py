#!/usr/bin/env python3
"""VICEWIRE rights-gated, offline vertical video editor. No publishing."""
import argparse,json,pathlib,subprocess,shutil,sys
def run(cmd): subprocess.run(cmd,check=True)
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--manifest",required=True)
 a=p.parse_args()
 m=json.loads(pathlib.Path(a.manifest).read_text())
 if m.get("rights_status")!="approved" or not m.get("rights_evidence"):
  sys.exit("BLOCKED: explicit approved rights_status and rights_evidence required")
 if m.get("publish",False):sys.exit("BLOCKED: publishing prohibited")
 src=pathlib.Path(m["source"]).resolve()
 if not src.is_file():sys.exit("Missing input footage: "+str(src))
 if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):sys.exit("ffmpeg and ffprobe required")
 out=pathlib.Path(m.get("output","vicewire/output.mp4")).resolve()
 if out==src:sys.exit("Input/output must differ")
 out.parent.mkdir(parents=True,exist_ok=True)
 duration=float(m.get("duration",15)); start=float(m.get("start",0))
 if not (0<=start and 1<=duration<=60):sys.exit("Invalid start/duration")
 # Safe font-independent lower third, with pink accent. Avoid arbitrary filter injection.
 vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,drawbox=x=0:y=1570:w=1080:h=225:color=black@0.72:t=fill,drawbox=x=45:y=1600:w=12:h=155:color=0xff315e:t=fill"
 cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(start),"-i",str(src),"-t",str(duration),"-vf",vf,"-af","afade=t=in:st=0:d=1,afade=t=out:st="+str(max(0,duration-1))+":d=1","-c:v","libx264","-preset","fast","-crf","20","-r","30","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",str(out)]
 run(cmd)
 print(json.dumps({"status":"rendered_for_review_only","output":str(out),"bytes":out.stat().st_size}))
if __name__=="__main__":main()
