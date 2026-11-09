#!/usr/bin/env python3
"""Pick a lively section using FFmpeg audio energy; does not understand song meaning."""
import argparse, json, math, re, subprocess

def duration(path):
    p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",path],capture_output=True,text=True,check=True)
    return float(json.loads(p.stdout)["format"]["duration"])

def select(path, length=59, step=8):
    total=duration(path)
    if total<=length: return 0, total
    # Decode audio once into a low-resolution mono PCM stream.
    p=subprocess.run(["ffmpeg","-nostdin","-v","error","-i",path,"-vn","-ac","1","-ar","1000","-f","s16le","-"],capture_output=True,check=True)
    import array
    audio=array.array("h");audio.frombytes(p.stdout)
    samples=[]
    for i in range(0,len(audio),step*1000):
        block=audio[i:i+step*1000]
        if not block: break
        rms=math.sqrt(sum(v*v for v in block)/len(block))
        samples.append(20*math.log10(max(rms,1)/32768))
    best=(-1e9,0)
    for start in range(0,max(1,int(total-length)+1),step):
        chunk=samples[start//step:max(start//step+1,math.ceil((start+length)/step))]
        score=sum(chunk)/len(chunk)+0.4*min(chunk)
        if score>best[0]: best=(score,start)
    return float(best[1]),length

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("source");a.add_argument("--length",type=float,default=59);a.add_argument("--output",default="selection.json");args=a.parse_args()
    start,length=select(args.source,args.length)
    with open(args.output,"w") as f:json.dump({"start":start,"duration":length,"method":"audio energy heuristic"},f)
    print(f"Selected {start:.1f}s through {start+length:.1f}s")
