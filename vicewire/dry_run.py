#!/usr/bin/env python3
"""VICEWIRE local-only dry-run renderer. Never publishes or downloads footage."""
import argparse, pathlib, shutil, subprocess, sys
p=argparse.ArgumentParser()
p.add_argument("--out",default="vicewire_preview.mp4")
p.add_argument("--seconds",type=int,default=8)
args=p.parse_args()
if not 1 <= args.seconds <= 60: p.error("seconds must be 1..60")
if not shutil.which("ffmpeg"): sys.exit("ffmpeg not installed")
out=pathlib.Path(args.out)
out.parent.mkdir(parents=True,exist_ok=True)
# Synthetic visual, silent soundtrack, no copyrighted media.
cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
"-f","lavfi","-i","color=c=0x0b0b12:s=1080x1920:r=30",
"-f","lavfi","-i","anullsrc=r=48000:cl=stereo",
"-t",str(args.seconds),"-vf","drawbox=x=0:y=1560:w=1080:h=240:color=black@0.8:t=fill,drawbox=x=45:y=1590:w=14:h=170:color=0xff315e:t=fill,drawtext=text='VICEWIRE  |  GTA 6':fontcolor=white:fontsize=72:x=90:y=1610,drawtext=text='TEST ONLY - NOT FOR PUBLICATION':fontcolor=0xff315e:fontsize=36:x=90:y=1700",
"-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(out)]
subprocess.run(cmd,check=True)
print(f"DRY RUN ONLY: {out} ({out.stat().st_size} bytes)")
