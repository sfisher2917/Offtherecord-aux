#!/usr/bin/env python3
"""Select high-motion, scene-diverse segments from locally supplied footage; no downloads."""
import argparse,json,pathlib,subprocess,statistics
def call(args):return subprocess.run(args,check=True,text=True,capture_output=True).stdout
def main():
 p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--output",required=True);p.add_argument("--duration",type=float,default=15);p.add_argument("--rights-evidence",required=True);p.add_argument("--title",default="VICEWIRE | Highlights");a=p.parse_args()
 src=pathlib.Path(a.source).resolve()
 if not src.is_file() or not a.rights_evidence.strip():raise SystemExit("Authorized local source and rights evidence required")
 duration=float(json.loads(call(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(src)]))["format"]["duration"])
 if duration<a.duration:raise SystemExit("Source shorter than requested highlight")
 # Analyze sampled scene-change frames, then choose the highest change-density window.
 raw=call(["ffmpeg","-hide_banner","-i",str(src),"-vf","fps=2,scale=160:-1,select='gt(scene,0.12)',showinfo","-an","-f","null","-"]) if False else ""
 # FFmpeg scene metadata is printed to stderr; low-resolution sampling avoids expensive full decode.
 proc=subprocess.run(["ffmpeg","-hide_banner","-loglevel","info","-i",str(src),"-vf","fps=2,scale=160:-1,select=gt(scene\\,0.12),showinfo","-an","-f","null","-"],text=True,capture_output=True)
 import re
 stamps=[float(x) for x in re.findall(r"pts_time:([0-9.]+)",proc.stderr)]
 if proc.returncode!=0:raise SystemExit("Scene analysis failed: "+proc.stderr[-500:])
 candidates=[min(float(i),duration-a.duration) for i in range(0,max(1,int(duration-a.duration)+1),max(1,int(a.duration//2)))]
 start=max(candidates,key=lambda t:(sum(t<=x<t+a.duration for x in stamps),-t))
 manifest={"source":str(src),"output":str(pathlib.Path(a.output).resolve()),"start":start,"duration":a.duration,"title":a.title,"rights_status":"approved","rights_evidence":a.rights_evidence,"publish":False}
 path=pathlib.Path(a.output).with_suffix(".manifest.json");path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(manifest,indent=2))
 print(json.dumps({"manifest":str(path),"selected_start":start,"scene_changes":len(stamps)}))
if __name__=="__main__":main()
