#!/usr/bin/env python3
"""VICEWIRE offline review renderer. No network access or publishing."""
import argparse,json,pathlib,re,subprocess,sys,shutil,math
def cmd(args): return subprocess.run(args,check=True,text=True,capture_output=True).stdout
def probe(path):
 return json.loads(cmd(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,width,height","-of","json",str(path)]))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--manifest",required=True);p.add_argument("--demo",action="store_true")
 a=p.parse_args(); m=json.loads(pathlib.Path(a.manifest).read_text())
 if m.get("publish") is not False:sys.exit("Publishing must explicitly be false")
 if m.get("rights_status")!="approved" or not str(m.get("rights_evidence","")).strip():sys.exit("BLOCKED: rights approval and evidence required")
 if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):sys.exit("FFmpeg required")
 src=pathlib.Path(m["source"]).resolve();out=pathlib.Path(m["output"]).resolve()
 if not src.is_file() or src==out:sys.exit("Invalid source or output")
 info=probe(src);length=float(info["format"]["duration"]);duration=float(m.get("duration",15));start=float(m.get("start",0))
 if not (1<=duration<=60 and 0<=start and start+duration<=length+0.1):sys.exit("Invalid clip bounds")
 title=str(m.get("title","VICEWIRE")).strip()[:75]
 if not re.fullmatch(r"[A-Za-z0-9 .,!?:'-]{1,75}",title):sys.exit("Title must use simple printable ASCII")
 out.parent.mkdir(parents=True,exist_ok=True)
 # Escape special characters for ffmpeg drawtext, using a UTF-8 text file rather than interpolating.
 titlefile=out.with_suffix(".title.txt");titlefile.write_text(title,encoding="utf-8")
 vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,drawbox=x=0:y=1570:w=1080:h=240:color=black@0.75:t=fill,drawbox=x=44:y=1590:w=12:h=175:color=0xff315e:t=fill"
 vf+=",drawtext=textfile='"+str(titlefile).replace("\\","/").replace(":","\\:").replace("'","\\'")+"':fontcolor=white:fontsize=53:x=83:y=1640"
 srt=m.get("subtitles")
 if srt:
  sp=pathlib.Path(srt).resolve()
  if not sp.is_file() or sp.suffix.lower()!=".srt":sys.exit("Invalid subtitle file")
  vf+=",subtitles='"+str(sp).replace("\\","/").replace(":","\\:").replace("'","\\'")+"'"
 has_audio=any(s.get("codec_type")=="audio" for s in info["streams"])
 args=["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(start),"-i",str(src)]
 if not has_audio:args+=["-f","lavfi","-i","anullsrc=r=48000:cl=stereo"]
 args+=["-t",str(duration),"-vf",vf,"-af",f"afade=t=in:st=0:d=0.8,afade=t=out:st={max(0,duration-0.8)}:d=0.8","-c:v","libx264","-preset","fast","-crf","20","-r","30","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",str(out)]
 try:cmd(args)
 finally:titlefile.unlink(missing_ok=True)
 rendered=probe(out);v=next((s for s in rendered["streams"] if s.get("codec_type")=="video"),{})
 if v.get("width")!=1080 or v.get("height")!=1920 or out.stat().st_size<10000:sys.exit("Output validation failed")
 meta={"status":"review_only","output":str(out),"duration_seconds":round(float(rendered["format"]["duration"]),2),"resolution":"1080x1920","rights_evidence":m["rights_evidence"],"published":False}
 out.with_suffix(".json").write_text(json.dumps(meta,indent=2))
 print(json.dumps(meta))
if __name__=="__main__":main()
