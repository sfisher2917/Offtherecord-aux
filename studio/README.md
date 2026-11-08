# OffTheRecord.aux Original Music Studio

A phone-operated, GitHub Actions-based **assembly** workflow for original 59-second music videos. It does not claim to generate human-quality AI vocals or cinematic AI video on GitHub's free CPU runners.

## Workflow
1. Generate or record an **original, commercially usable** song (human or licensed model). Export a direct HTTPS WAV/MP3/M4A link.
2. Prepare 1–12 licensed, direct HTTPS MP4 clips. They may be generated with locally hosted open-weight models (subject to each model's license), or recorded yourself.
3. Edit `studio/project.json`: set song URL, scene URLs, scene time ranges, and matching lyric text. No secrets or private URLs.
4. On your Android phone open **Actions → Original Music Video Studio → Run workflow**. Download the resulting artifact from the completed run.
5. Review the complete 59-second output before posting manually.

**Rights gate:** All lyrics, master recordings, voices, video clips, and visual likenesses must be original or cleared for commercial distribution. Do not use free-plan AI music with noncommercial licenses. Never clone a real person's voice without authorization.

## What this repository automates
- Strict input validation, source download, video resizing/cropping, beat-agnostic time-coded lyric captions, audio fades, branding, MP4 encoding, output duration checks, and artifact upload.
- Fixed 59-second export and consistent single bottom information panel (artist, title, location).

## What is not yet automated
- Creation of professional AI sung/rapped audio, GPU video generation, precise word-level alignment, real human lip sync, publishing, and commercial-rights verification.
- Free GitHub-hosted CPU runners cannot reliably run large music/video generation models. GitHub Actions has usage, storage, and download limits.

## Local test
```bash
python3 studio/render.py --project studio/project.json --out music-video.mp4
```
Requires Python 3, FFmpeg, FFprobe, and publicly reachable source URLs.
