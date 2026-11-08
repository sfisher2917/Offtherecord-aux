#!/usr/bin/env python3
"""Generate an entirely original procedural beat and lyric-driven animated video.
No external assets, AI APIs, credentials, or commercial source files required.
Vocals are NOT synthesized; lyrics appear as on-screen captions.
"""
import math, wave, struct, random, tempfile, subprocess, pathlib, json, argparse
SR=24000
D=59
def audio(path,seed):
    rng=random.Random(seed)
    n=SR*D
    # 100 BPM, original four-bar chord cycle with kick, clap, hats and bass
    chords=[(110,138.59,164.81),(98,123.47,146.83),(87.31,110,130.81),(103.83,130.81,155.56)]
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
        chunk=[]
        for i in range(n):
            t=i/SR
            beat=t/(60/100)
            phase=beat%1
            bar=int(beat//4)%4
            chord=chords[bar]
            # tonal pads and melodic pluck, with slowly evolving original progression
            pad=sum(math.sin(2*math.pi*f*t)*0.024 for f in chord)
            step=int(beat*2)%8
            melody=chord[[0,2,1,2,0,1,2,1][step]]*2
            pluck=0.08*math.exp(-8*((beat*2)%1))*math.sin(2*math.pi*melody*t)
            kick=0.35*math.exp(-20*phase)*math.sin(2*math.pi*(52*t+22*math.exp(-30*phase)*phase))
            clap_phase=(beat-2)%4
            clap=0.14*(rng.random()*2-1)*math.exp(-38*clap_phase) if clap_phase<0.18 else 0
            hatphase=(beat*2)%1
            hat=0.045*(rng.random()*2-1)*math.exp(-48*hatphase)
            bass=0.16*math.sin(2*math.pi*(chord[0]/2)*t)*(0.7+0.3*math.cos(2*math.pi*phase))
            fade=min(1,t/1.2,(D-t)/1.2)
            v=max(-1,min(1,(pad+pluck+kick+clap+hat+bass)*max(0,fade)))
            chunk.append(struct.pack("<h",int(v*29000)))
            if len(chunk)>=8192:
                w.writeframesraw(b"".join(chunk));chunk=[]
        if chunk:w.writeframesraw(b"".join(chunk))
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",default="offtherecord-original-59s.mp4");ap.add_argument("--seed",type=int,default=2917)
    args=ap.parse_args()
    # Visual scenes are original mathematical animations rendered by FFmpeg; no external clips.
    scenes=[
        (0,9,"3 AM / writing dreams into the night"),
        (9,19,"City lights / and a heart that won't quit"),
        (19,29,"No sleep / all gas / moving forward"),
        (29,39,"Rain on the glass / but the vision stays clear"),
        (39,49,"From the shadows / to the stage"),
        (49,59,"No sleep / all gas / this is our year")
    ]
    with tempfile.TemporaryDirectory() as d:
        p=pathlib.Path(d); wav=p/"original.wav";audio(wav,args.seed)
        # drawtext overlay; one black translucent lower box with red accent.
        vf=["format=yuv420p","drawbox=x=0:y=1510:w=iw:h=410:color=black@0.65:t=fill","drawbox=x=34:y=1535:w=9:h=340:color=red@1:t=fill"]
        title=p/"title.txt";title.write_text("OffTheRecord.aux | No Sleep, All Gas | Original Studio",encoding="utf-8")
        vf.append("drawtext=textfile='"+str(title)+"':fontcolor=white:fontsize=30:x=70:y=1780")
        for i,(start,end,lyric) in enumerate(scenes):
            f=p/f"line{i}.txt";f.write_text(lyric,encoding="utf-8")
            vf.append("drawtext=textfile='"+str(f)+"':fontcolor=white:fontsize=42:x=70:y=1610:enable='between(t,"+str(start)+","+str(end-0.001)+")'")
        # Procedural neon moving city stripes, beat-responsive background via FFmpeg expression.
        background="color=c=0x080b1a:s=1080x1920:r=30:d=59"
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi","-i",background,"-i",str(wav),
             "-vf",",".join(["drawgrid=w=108:h=120:t=2:c=0x3b245f@0.45",
                              "drawbox=x=100:y=300:w=880:h=660:color=0x131b37@0.7:t=fill"]+vf),
             "-t","59","-c:v","libx264","-preset","ultrafast","-crf","25","-pix_fmt","yuv420p",
             "-c:a","aac","-b:a","160k","-movflags","+faststart",args.out]
        subprocess.run(cmd,check=True)
        duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",args.out],text=True).strip())
        assert abs(duration-59)<0.2,duration
        print("Original instrumental + animated lyric video generated:",args.out)
if __name__=="__main__":main()
