# VICEWIRE source-to-review pipeline
All stages are offline and review-only. Do not publish or change existing schedules.

1. Obtain footage you own or have written permission to edit; keep rights evidence.
2. Supply the file locally as `vicewire/input/authorized_source.mp4`. GitHub Actions runners cannot see your local file automatically; use a secure upload mechanism, not public Git history, for actual production footage.
3. Optional highlight selection: `python3 vicewire/highlights.py --source vicewire/input/authorized_source.mp4 --output vicewire/output/review.mp4 --duration 15 --rights-evidence "permission reference"`. This scores scene-change density, not semantic excitement.
4. Optional caption generation: `pip install openai-whisper`, then `python3 vicewire/captions.py --source vicewire/input/authorized_source.mp4 --output vicewire/input/captions.srt`. Whisper model download requires internet on first use. For trimmed clips, adjust caption timecodes to the selected start before embedding.
5. Render: `python3 vicewire/agent_editor_v2.py --manifest vicewire/output/review.manifest.json`. To burn supplied captions, set the `subtitles` field to an existing SRT path.
6. Inspect the MP4 and JSON validation metadata; obtain explicit approval before any publishing.

The review-artifact workflow will intentionally fail until a source file and rights-approved manifest are available on the runner. The smoke test is the only ready-to-run workflow without source footage. Automated downloading of arbitrary copyrighted GTA footage and AI video generation are not included.
