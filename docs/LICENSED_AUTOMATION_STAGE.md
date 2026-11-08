# Licensed-source automation: safe staging

## Current operation
The new **Licensed content render (artifact only)** GitHub Action takes an exact content ID from `automation/queue.json`. It checks the license record **before downloading**, downloads the approved source, renders the vertical MP4, and saves the MP4 plus an audit manifest as an Actions artifact. It never posts.

## Required queue fields
```json
{
  "id": "unique-content-id",
  "status": "ready",
  "artist": "Artist",
  "title": "Performance",
  "event": "Verified venue or event",
  "source_url": "https://licensed-provider.example/video.mp4",
  "platforms": ["instagram", "youtube"],
  "start_seconds": 0,
  "duration_seconds": 59,
  "rights": {
    "verification": "documented",
    "licensor": "Actual rights holder",
    "license_id": "traceable-license-number",
    "evidence_url": "https://secure-evidence.example/license-document",
    "commercial_use": true,
    "editing": true,
    "audio": true,
    "video": true,
    "redistribution": true,
    "platforms": ["instagram", "youtube"],
    "expires_on": "2099-12-31"
  }
}
```
**Never mark a source ready based only on a video being public, a credit line, a Creative Commons label without verifying the actual license, or a self-asserted permission.** Check who owns the master video, sound recording, composition, and any third-party performance rights; verify territory, term, commercial use, derivative edits, and platform scope. Store a durable copy of the evidence securely. This gate checks fields and dates, **not authenticity of documents**.

## Publishing is not enabled
The resulting GitHub artifact is not public video hosting. Instagram needs a durable, publicly accessible HTTPS video URL; YouTube needs valid OAuth credentials. Do not set `ENABLE_LIVE_PUBLISH=true` until a licensed test item, verified credentials, hosting, duplicate reconciliation, and a controlled test publication all pass. No scheduled public posts are created by this workflow.

## Operational limitation
Existing `render-short.yml` and `direct-publish.yml` are manual workflows; the latter now checks manifest rights, while the former still relies on a manual rights checkbox. The new licensed workflow should be preferred for any production render. Repository write access to the manifest must be restricted to trusted maintainers.
