# Free Unified Clipper — OffTheRecord.aux

This workflow combines **FFmpeg** with GitHub Actions into a zero-subscription clip-rendering system. It preserves the single black translucent information box with red accent bar, artist/song/live location, 1080×1920 vertical framing, and <=1.5-second audio fades.

## Phone-only operation
1. Open **Actions → Free Unified Clipper → Run workflow**.
2. Supply a **direct HTTPS MP4 URL** for footage you own or are licensed to redistribute. A YouTube watch URL does not work. File must be <=300 MB.
3. Set start (seconds), duration (59 for Instagram, up to 60 for YouTube), artist, song, and live location.
4. Check the rights-confirmed box and run.
5. Open the completed run → **Artifacts** → download the ZIP containing both MP4s. Upload them manually.

## Important limitations
- This is an actual working baseline clipper, **not** automatic viral-moment detection. Choose the best start time manually. No scraping or bypassing copyright controls.
- Whisper transcription, Chopify, and QMM AutoEdit are **not installed or executed** by this baseline. Their quality, licenses, resource needs, and CLI interfaces require validation before integrating. They are optional future stages, not claimed capabilities.
- Standard GitHub-hosted Actions usage and artifact storage have free-tier limits; this is not unlimited free compute.
- Long videos and private upload links may exceed size or access limits.
- The crop is centered; review subjects before publishing. No automatic face tracking.
- Never paste account passwords, cookies, or private API tokens into workflow inputs.
- The workflow does not post to any social account.

## Architecture
Rights-cleared source → safe download → FFmpeg crop / lower-third / fades → two 1080p MP4s → downloadable Actions artifact.

## Troubleshooting
- **403/404:** direct file URL is inaccessible or expired.
- **Unsupported input:** use an MP4 with H.264 video and AAC audio.
- **Download too large:** trim or compress the source first.
- **No sound:** source may lack an audio track.
- **No artifact:** inspect the failed Actions step logs.

This is isolated on a feature branch for review and does not modify your existing scheduled posting pipeline.
