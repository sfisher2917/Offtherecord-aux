#!/usr/bin/env python3
"""Optional local Whisper transcription to SRT. Installs only when requested."""
import argparse,pathlib,sys
def main():
 p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--output",required=True);p.add_argument("--model",default="tiny");a=p.parse_args()
 try:import whisper
 except ImportError:sys.exit("Install optional dependency: pip install openai-whisper")
 if a.model not in ("tiny","base","small"):sys.exit("Only tiny/base/small supported")
 model=whisper.load_model(a.model);result=model.transcribe(a.source,fp16=False)
 def stamp(t):
  n=round(t*1000);return f"{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}"
 blocks=[]
 for i,s in enumerate(result["segments"],1):
  text=s["text"].strip()
  if text:blocks.append(f'{i}\n{stamp(s["start"])} --> {stamp(s["end"])}\n{text}\n')
 path=pathlib.Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text("\n".join(blocks))
 print(f"Created {len(blocks)} caption segments: {path}")
if __name__=="__main__":main()
