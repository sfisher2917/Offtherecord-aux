# OffTheRecord.aux — editorial and publishing SOP

## Brand and format
- Cross-genre music moments: live vocals, unexpected collaborations, standout musicianship and compelling stories.
- Vertical 9:16, 1080x1920 target, H.264/AAC, readable safe-area typography, consistent OffTheRecord.aux brand.
- Source-led captions: name performer, track and original source, with attribution required by the license.
- No fabricated quotes, invented performance facts, misleading titles, or deceptive AI edits.

## Source gate — required before rendering
1. Verify permission to reuse **video and the underlying audio/composition** on both Instagram and YouTube, including any license restrictions and attribution.
2. Save source URL and proof/terms of permission. A public video link or credit alone is not permission.
3. Check source-register.json and both platform accounts for previous use.
4. Verify factual details and select a strong, context-preserving moment.
5. Avoid personal/private footage and sensitive content without appropriate authorization.

## Production QA
- Confirm portrait frame, 1080x1920, H.264, AAC, no black frames, no missing audio, correct crop and captions.
- Listen to beginning/end; avoid clipping and awkward cuts.
- Review spelling, branding, mobile safe areas, and any required credit.
- Check the exported MP4, not just the renderer log.

## Publishing gate
- Require a stable public HTTPS video file URL compatible with the destination or an officially supported upload route.
- Check for existing posts before submitting. Use a unique source fingerprint + platform + scheduled slot to prevent duplicates.
- Submit once; verify resulting post IDs/URLs and actual public playback on Instagram and YouTube.
- Mark as published only after verification; if status is unknown, investigate rather than repost.
- Send a notification with verified links and performance notes.

## Operating targets
- Editorial radar: 8 AM ET.
- Publishing targets: 10 AM, 4 PM, 7 PM ET **only when all gates pass**.
- If permissions, source availability, rendering, hosting, or publishing verification fail, hold the slot rather than post placeholder content or claim success.

## Current technical status
- GitHub write integration works.
- Initial renderer and smoke-test workflow committed.
- Local FFmpeg core processing test passed; GitHub-hosted run and complete branded export still need verification.
- No durable video hosting or verified Metricool auto-publishing pipeline yet.
- Use free tools where feasible, while monitoring GitHub Actions usage limits.
