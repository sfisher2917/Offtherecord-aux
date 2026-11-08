# Direct Instagram and YouTube publishing

## Current state
Direct API publishing code is installed, but **not authorized or live**. This workflow intentionally requires a repository variable `ENABLE_LIVE_PUBLISH=true` and credentials in encrypted GitHub Actions secrets. No secrets are committed to the repository.

## YouTube
1. Configure a Google Cloud project with YouTube Data API v3 enabled.
2. Complete OAuth consent and obtain a refresh token with `youtube.upload` scope for the correct channel. API quota and Google verification rules may apply.
3. Add Actions secrets `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`.
4. Validate the channel identity and use a permitted test upload before production.

## Instagram
1. Use an eligible Instagram professional account and official Meta Graph API access with the necessary publishing permissions.
2. Add Actions secrets `META_ACCESS_TOKEN` and `INSTAGRAM_ACCOUNT_ID`.
3. Supply a durable publicly accessible HTTPS MP4 URL. GitHub Actions artifact links are not suitable media hosting.
4. Test container creation, processing, publishing and permalink verification.

## Enabling
After tests and rights verification, set GitHub repository Actions variable `ENABLE_LIVE_PUBLISH` to `true`. Manually dispatch **Direct platform publishing (manual gated)** from Actions. It targets **one platform per run** to limit ambiguous partial failures. Verify each platform independently.

## Safety and limitations
- User-supplied permission must cover the underlying music and footage, not merely editorial approval.
- Duplicate prevention is not fully transactional: GitHub concurrency helps only with simultaneous runs using the same key. Always reconcile existing public posts and audit artifacts before retries.
- Direct uploads do not yet include automatic token refresh for Meta, durable hosting, analytics collection or robust publish scheduling.
- No personal Facebook posting is involved, although Meta developer/account setup may be necessary for Instagram's API.
- Do not enable the workflow until credentials, platform eligibility and video hosting are configured and tested.
