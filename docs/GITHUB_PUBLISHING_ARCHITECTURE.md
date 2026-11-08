# OffTheRecord.aux GitHub-first publishing architecture

## Goal
GitHub Actions orchestrates rendering, scheduling, direct API publishing, audit logs and analytics. Metricool remains a fallback until end-to-end publishing is verified.

## Phase 1 — installed
- Queue file, published ledger and timezone-aware dry-run scheduler.
- **No separate editorial approval step**: items marked `ready` may qualify automatically.
- Before any public upload, the queue still requires a media URL and evidence that the footage and underlying audio may be reused.
- SHA-256 idempotency key based on source item and platform.
- No external publishing or API credentials in this phase.

## Phase 2 — after technical verification
- Render and quality-assure authorized source footage.
- Add official YouTube Data API OAuth upload and Meta Instagram Graph API Reels publishing.
- Use durable HTTPS MP4 hosting for Instagram ingestion.
- Store OAuth credentials as encrypted GitHub secrets with least privilege.
- Record publication with concurrency controls and reconciliation; a JSON ledger alone is not a transactional lock.
- Verify public post IDs/playback, alert on failures and report analytics.

## Constraints
- Scheduled Actions can be delayed or skipped.
- YouTube uploads require OAuth, quotas and compliance with API policy.
- Instagram publishing requires eligible professional account and Meta permissions.
- GitHub Actions and platform APIs have limits; no unlimited-free guarantee.
- This scheduler is **dry run only** and cannot publish.
