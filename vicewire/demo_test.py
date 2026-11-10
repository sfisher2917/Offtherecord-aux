"""Local smoke test with generated footage; never publish."""
import json,subprocess,tempfile,pathlib,sys
root=pathlib.Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d);src=p/"synthetic.mp4";out=p/"review.mp4"
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi","-i","testsrc2=size=540x960:rate=30","-t","3","-c:v","libx264","-pix_fmt","yuv420p",str(src)],check=True)
 m={"source":str(src),"output":str(out),"start":0,"duration":3,"title":"VICEWIRE DEMO","rights_status":"approved","rights_evidence":"synthetic generated test pattern","publish":False}
 manifest=p/"manifest.json";manifest.write_text(json.dumps(m))
 subprocess.run([sys.executable,str(root/"agent_editor_v2.py"),"--manifest",str(manifest)],check=True)
 assert out.exists() and out.stat().st_size>10000
 print("Synthetic render smoke test passed")
