# OffTheRecord.aux — video production

An initial free GitHub Actions + FFmpeg pipeline for **authorized** music performance clips.

## Render a clip on Android
1. Open [Actions](https://github.com/sfisher2917/Offtherecord-aux/actions).
2. Select **Render OffTheRecord Short** and tap **Run workflow**.
3. Provide a **direct HTTPS MP4/WebM video file URL**, performer, title and duration (maximum 60 seconds).
4. Confirm reuse rights for **both the recording and the music**.
5. After a successful run, open its **Artifacts** section and download `offtherecord-short` (ZIP containing an MP4).

The renderer targets **1080 × 1920 H.264 video with AAC audio**, adds OffTheRecord.aux text branding, and checks the output streams and duration.

## Automated test
The **Smoke test renderer** workflow generates a synthetic test pattern and synthetic audio, renders a short, and uploads a sample artifact. This is only a technical test, not publishable music content.

## Current limitations
- A real performance-source render has **not** been verified yet.
- GitHub workflow artifacts are temporary downloads, **not permanent public video URLs** accepted by Metricool.
- No automatic Instagram/YouTube publishing has been implemented or verified.
- Do not put passwords, API tokens or confidential media links in workflow inputs. GitHub Actions usage and storage remain subject to GitHub's plan limits.
- Verify source license and attribution requirements before distributing or publishing.

## Roadmap
1. Validate the synthetic smoke-test render and audio.
2. Render a genuinely licensed performance.
3. Establish compatible public hosting for finished MP4s.
4. Integrate Metricool with idempotent duplicate prevention and independently verified publication.
