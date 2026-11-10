#!/usr/bin/env python3
"""Authorized footage -> original narrated 60-second vertical commentary video.
Does not post to any social platform. Requires ffmpeg, yt-dlp and edge-tts.
"""
import asyncio, json, os, pathlib, subprocess, textwrap
import edge_tts

ROOT=pathlib.Path("vicewire/output")
ROOT.mkdir(parents=True,exist_ok=True)
SOURCE=os.environ.get("SOURCE_URL","https://www.youtube.com/watch?v=tJbzMqJGH4k")
subprocess.run(["yt-dlp","--no-playlist","-f","bv*[height<=1080]+ba/b[height<=1080]/best","--merge-output-format","mp4","-o",str(ROOT/"source.%(ext)s"),SOURCE],check=True)
src=next(ROOT.glob("source.*"))
def probe(p):
 return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-of","json",str(p)]))["format"]
duration=float(probe(src)["duration"])
if duration < 60: raise RuntimeError("Source shorter than 60 seconds")
lines=[
 "Rockstar's latest look at Grand Theft Auto Six reveals a world built for chaos.",
 "Vice City is back, but this time the surrounding state of Leonida is part of the story.",
 "From packed beaches to neon streets, every scene feels full of movement.",
 "Jason and Lucia are at the center of the action, navigating a criminal world where trust matters.",
 "Look closely at the crowds, traffic, and tiny background details. That's where the world comes alive.",
 "High-speed escapes, unforgettable locations, and a new take on the GTA formula.",
 "This is VICEWIRE. Follow for more Grand Theft Auto Six breakdowns."
]
script=" ".join(lines)
(ROOT/"narration.txt").write_text(script)
async def speak():
 await edge_tts.Communicate(script,voice="en-US-GuyNeural",rate="+5%").save(str(ROOT/"voice.mp3"))
asyncio.run(speak())
voice_duration=float(probe(ROOT/"voice.mp3")["duration"])
if voice_duration > 59:
 raise RuntimeError(f"Narration too long: {voice_duration:.1f} seconds")
words=script.split()
def timestamp(t):
 h=int(t//3600); m=int(t%3600//60); sec=int(t%60); ms=int((t%1)*1000)
 return f"{h:02}:{m:02}:{sec:02},{ms:03}"
cues=[]
for i in range(0,len(words),7):
 start=voice_duration*i/len(words)
 end=voice_duration*min(i+7,len(words))/len(words)
 cues.append(f"{len(cues)+1}\n{timestamp(start)} --> {timestamp(end)}\n{' '.join(words[i:i+7])}\n")
(ROOT/"captions.srt").write_text("\n".join(cues),encoding="utf-8")
# Build eight varied scene extracts from across the source, retaining original footage.
segments=8
clip_length=7.5
max_start=duration-clip_length
for i in range(segments):
 start=max_start*(i+0.5)/segments
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(start),"-i",str(src),"-t",str(clip_length),
  "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30",
  "-an","-c:v","libx264","-preset","veryfast","-crf","23",str(ROOT/f"scene_{i:02d}.mp4")],check=True)
concat=ROOT/"concat.txt"
concat.write_text("".join(f"file 'scene_{i:02d}.mp4'\n" for i in range(segments)))
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(concat),
 "-i",str(ROOT/"voice.mp3"),"-filter_complex",
 "[0:v]drawbox=x=0:y=1600:w=1080:h=230:color=black@0.7:t=fill,drawbox=x=40:y=1620:w=12:h=175:color=red:t=fill,drawtext=text='VICEWIRE | GTA 6':fontcolor=white:fontsize=56:x=80:y=1660[v];[1:a]apad=pad_dur=60,atrim=duration=60,afade=t=out:st=58:d=2[a]",
 "-map","[v]","-map","[a]","-t","60","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",
 "-c:a","aac","-b:a","192k","-movflags","+faststart",str(ROOT/"VICEWIRE_GTA6_YouTube_Shorts.mp4")],check=True)
import shutil
shutil.copyfile(ROOT/"VICEWIRE_GTA6_YouTube_Shorts.mp4",ROOT/"VICEWIRE_GTA6_Instagram_Reel.mp4")
(ROOT/"POSTING.txt").write_text("YouTube title: Rockstar's GTA 6 World Looks INSANE | VICEWIRE #Shorts\nInstagram caption: Vice City is calling. Here's our GTA 6 breakdown. #GTA6 #ViceCity #RockstarGames #VICEWIRE\nSource: "+SOURCE+"\nNOTE: Voiceover is AI-generated. Review visual accuracy, pacing and rights before uploading.\n")
# Do not redistribute the full-length source video in the deliverable.
src.unlink()\nfor clip in ROOT.glob("scene_*.mp4"): clip.unlink()
