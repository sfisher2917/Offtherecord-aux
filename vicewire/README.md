# VICEWIRE Agentic Editor — isolated development
This is a manual-trigger, review-only FFmpeg editor. It does not download media, post to any platform, change automations, or alter the existing production pipeline.

## Usage
1. Supply your own authorized MP4 at `vicewire/input/authorized_source.mp4` (do not commit private footage).
2. Set `rights_status` to `approved` and record evidence of permission in `example_manifest.json`.
3. Run `python3 vicewire/agent_editor.py --manifest vicewire/example_manifest.json`.
4. Review `vicewire/output/review.mp4` manually. Never publish without approval.

The workflow is manual-only and intentionally fails until a rights-approved input exists in its runner. GitHub-hosted runners do not automatically contain your local media. This is an initial processing foundation, not a complete automatic highlight selector, transcription engine, or AI video generator.
