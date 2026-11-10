"""VICEWIRE synthetic media smoke test. Original footage; no publishing."""
import argparse,json,subprocess,tempfile,pathlib,sys,shutil
root=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument("--keep-output",default=None);a=p.parse_args()
with tempfile.TemporaryDirectory() as d:
 temp=pathlib.Path(d);src=temp/"synthetic.mp4";out=temp/"review.mp4"
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi","-i","testsrc2=size=540x960:rate=30","-f","lavfi","-i","sine=frequency=220:sample_rate=48000","-t","3","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",str(src)],check=True)
 m={"source":str(src),"output":str(out),"start":0,"duration":3,"title":"VICEWIRE DEMO","rights_status":"approved","rights_evidence":"Original generated test pattern and synthesized tone","publish":False}
 manifest=temp/"manifest.json";manifest.write_text(json.dumps(m))
 subprocess.run([sys.executable,str(root/"agent_editor_v2.py"),"--manifest",str(manifest)],check=True)
 assert out.exists() and out.stat().st_size>10000
 if a.keep_output:
  dest=pathlib.Path(a.keep_output);dest.mkdir(parents=True,exist_ok=True)
  shutil.copy2(out,dest/"vicewire-review.mp4")
  shutil.copy2(out.with_suffix(".json"),dest/"vicewire-review.json")
 print("Synthetic render smoke test passed; published=false")
