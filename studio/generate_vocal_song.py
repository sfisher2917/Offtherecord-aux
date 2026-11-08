#!/usr/bin/env python3
"""Generate a full original sung track using an ACE-Step 1.5 REST server.
Requires a separately running ACE-Step API; never substitutes synthetic speech.
"""
import argparse,json,os,time,urllib.request,urllib.parse,pathlib,subprocess,sys
def request(base,route,payload,token,timeout=60):
    data=json.dumps(payload).encode()
    headers={"Content-Type":"application/json"}
    if token: headers["Authorization"]="Bearer "+token
    req=urllib.request.Request(base+route,data=data,headers=headers,method="POST")
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.load(r)
def check(obj):
    if obj.get("code")!=200: raise RuntimeError("ACE-Step API error: "+str(obj.get("error")))
    return obj["data"]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--song",default="studio/song.json")
    p.add_argument("--out",default="offtherecord-original-vocals-59s.mp3")
    p.add_argument("--api",default=os.environ.get("ACESTEP_API_URL",""))
    p.add_argument("--poll-seconds",type=int,default=15)
    p.add_argument("--timeout-seconds",type=int,default=900)
    a=p.parse_args()
    if not a.api.startswith("https://") and not (os.environ.get("ALLOW_LOCAL_ACESTEP")=="1" and a.api.startswith("http://127.0.0.1:")):
        sys.exit("ACE-Step API unavailable: set ACESTEP_API_URL to a trusted HTTPS endpoint (or local loopback with ALLOW_LOCAL_ACESTEP=1).")
    base=a.api.rstrip("/")
    token=os.environ.get("ACESTEP_API_KEY","")
    song=json.loads(pathlib.Path(a.song).read_text())
    duration=song["duration_seconds"]
    if duration!=59: raise ValueError("Studio requires exactly 59 seconds")
    payload={"prompt":song["prompt"],"lyrics":song["lyrics"],"vocal_language":"en","audio_duration":59,
             "bpm":song["bpm"],"key_scale":song["key_scale"],"time_signature":"4",
             "audio_format":"mp3","model":"acestep-v15-turbo","inference_steps":8,
             "batch_size":1,"thinking":False,"use_random_seed":True}
    job=check(request(base,"/release_task",payload,token))
    task=job["task_id"]
    deadline=time.monotonic()+a.timeout_seconds
    while time.monotonic()<deadline:
        data=check(request(base,"/query_result",{"task_id_list":[task]},token))
        if not data: raise RuntimeError("ACE-Step returned no task result")
        entry=data[0]
        status=int(entry["status"])
        if status==2: raise RuntimeError("ACE-Step generation failed: "+str(entry))
        if status==1:
            result=entry.get("result")
            result=json.loads(result) if isinstance(result,str) else result
            if not result: raise RuntimeError("No generated audio in result")
            path=result[0].get("file")
            if not path: raise RuntimeError("Missing generated audio file path")
            # Only accept paths served by the configured ACE-Step API, not arbitrary external URLs.
            parsed=urllib.parse.urlparse(path)
            if parsed.scheme or parsed.netloc or not path.startswith("/v1/audio?"):
                raise RuntimeError("Unexpected ACE-Step audio path")
            headers={}
            if token:headers["Authorization"]="Bearer "+token
            with urllib.request.urlopen(urllib.request.Request(base+path,headers=headers),timeout=120) as response:
                raw=response.read(100_000_001)
            if len(raw)>100_000_000 or len(raw)<10000:raise RuntimeError("Audio payload invalid")
            rawpath=pathlib.Path(a.out).with_suffix(".source.mp3");rawpath.write_bytes(raw)
            # Exact 59s deliverable with <=1.2s start/end fades; trim or pad if model drifts.
            subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(rawpath),
                "-af","apad,atrim=0:59,afade=t=in:st=0:d=1.2,afade=t=out:st=57.8:d=1.2",
                "-t","59","-codec:a","libmp3lame","-b:a","256k",a.out],check=True)
            rawpath.unlink()
            measured=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",a.out],text=True).strip())
            if abs(measured-59)>0.2:raise RuntimeError("Audio duration is not 59 seconds: "+str(measured))
            print("Generated original full-vocal song:",a.out)
            return
        time.sleep(a.poll_seconds)
    raise TimeoutError("ACE-Step did not finish within allotted time")
if __name__=="__main__":main()
