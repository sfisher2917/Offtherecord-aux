# OffTheRecord.aux GitHub-first publishing architecture

## Goal
GitHub Actions orchestrates discovery, rights checks, FFmpeg renders, approvals, scheduling, direct API publishing, audit logs and analytics. Metricool stays connected as fallback until end-to-end publishing is verified.

## Phase 1 — installed
- Queue file, published ledger and timezone-aware dry-run scheduler.
- Fail closed: only `approved` queue entries with evidence of rights and a media URL qualify.
- SHA-256 idempotency key based on source item and platform.
- No external publishing, API credentials or GitHub secrets needed for this phase.

## Phase 2 — after technical verification
- Render and quality-assure source footage with permission for both audiovisual and musical works.
- Add official YouTube Data API OAuth upload and Meta Instagram Graph API Reels publishing.
- Use a durable HTTPS MP4 URL for Instagram container ingestion.
- Store OAuth credentials only as GitHub encrypted secrets, with least-privilege scopes and rotation.
- Commit/record publication ledger using concurrency controls and idempotent reconciliation. **A JSON ledger in the repository alone is not a transactional lock**.
- Verify public post IDs and playback before marking as published.
- Add alerts, retries with backoff, quota monitoring and analytics reporting.

## Constraints
- GitHub Actions scheduled workflows may start late or be skipped; five-minute polling does not guarantee exact publishing times.
- YouTube API uploads require Google OAuth authorization and are subject to quota, project verification and API policy.
- Instagram API publishing requires a supported professional account and Meta permissions; it is not equivalent to using a personal Instagram login.
- APIs, GitHub Actions and free plans may impose limits; avoid promises of unlimited free posting.
- The dry-run scheduler does **not** publish anything.
