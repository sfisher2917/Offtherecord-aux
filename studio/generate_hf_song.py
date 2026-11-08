#!/usr/bin/env python3
"""Use an existing Hugging Face Gradio music Space with user-provided endpoint mapping.
Do not assume all ACE-Step demos expose the same API schema.
"""
import argparse,os,json,subprocess,pathlib,sys
from gradio_client import Client
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--song",default="studio/song.json")
 p.add_argument("--out",default="offtherecord-original-vocals-59s.mp3")
 a=p.parse_args()
 space=os.getenv("HF_MUSIC_SPACE","ACE-Step/Ace-Step-v1.5").strip()
 endpoint=os.getenv("HF_MUSIC_ENDPOINT","").strip()
 if not space:
  sys.exit("Set HF_MUSIC_SPACE and HF_MUSIC_ENDPOINT repository secrets after inspecting the selected Space's 'Use via API' page.")
 token=os.getenv("HF_TOKEN") or None
 client=Client(space,token=token)
 if os.getenv("HF_INSPECT_API")=="1":
  print(client.view_api());return
 if not endpoint:
  sys.exit("Set HF_MUSIC_ENDPOINT after inspecting the Space API.")
 song=json.loads(pathlib.Path(a.song).read_text())
 # Explicit mapping is required because community Spaces have varying input signatures.
 # Configure HF_MUSIC_INPUTS_JSON as JSON list of supported input keys in positional order.
 keys=json.loads(os.getenv("HF_MUSIC_INPUTS_JSON","[]"))
 values={"prompt":song["prompt"],"lyrics":song["lyrics"],"duration":59,"bpm":song["bpm"],"key_scale":song["key_scale"]}
 if not keys or any(k not in values for k in keys):
  sys.exit("Set HF_MUSIC_INPUTS_JSON to a JSON array of supported keys: prompt, lyrics, duration, bpm, key_scale")
 result=client.predict(*(values[k] for k in keys),api_name=endpoint)
 def find_file(obj):
  if isinstance(obj,dict):
   for key in ("path","audio","file","name"):
    if isinstance(obj.get(key),str) and pathlib.Path(obj[key]).is_file():return obj[key]
   for v in obj.values():
    f=find_file(v)
    if f:return f
  if isinstance(obj,(list,tuple)):
   for v in obj:
    f=find_file(v)
    if f:return f
  if isinstance(obj,str) and pathlib.Path(obj).is_file():return obj
  return None
 file=find_file(result)
 if not file:raise RuntimeError("Space returned no locally downloadable audio file. Inspect its API response and update adapter.")
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",file,
  "-af","apad,atrim=0:59,afade=t=in:st=0:d=1.2,afade=t=out:st=57.8:d=1.2",
  "-t","59","-codec:a","libmp3lame","-b:a","256k",a.out],check=True)
 print("Cloud-generated vocal song:",a.out)
if __name__=="__main__":main()
