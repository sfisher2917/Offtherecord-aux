# VICEWIRE Agentic Studio — review only
The v2 renderer supports vertical cropping, pink-accent lower third, custom title, optional supplied SRT captions, audio fades, silent-video support, MP4 export, and ffprobe validation.

Run: `python3 vicewire/agent_editor_v2.py --manifest vicewire/review_manifest.json`.

The sample manifest is deliberately blocked: rights must be approved with evidence and the authorized MP4 must exist on the runner. Never label AI-generated concepts as real GTA 6 gameplay. Avoid copyrighted music, unauthorized creator footage, or unverified news.

A separate manual GitHub Actions workflow runs a synthetic render smoke test without external media. It does not post, upload, schedule, or modify the main branch. The existing review-only workflow remains unchanged. The studio does not yet perform speech transcription, scene scoring, automatic sourcing, or generative video; these need additional source media and validated services.

The agent's review checklist: inspect actual source and permissions; prepare manifest and optional SRT; render; inspect MP4 and metadata; approve before any separate publication action.
