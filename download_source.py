"""Download a permitted public video link to a local MP4 for rendering.

Does not use cookies, credentials, DRM bypass or access-control workarounds.
"""
import argparse
import ipaddress
import socket
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

MAX_BYTES = 500 * 1024 * 1024

def validate_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("An ordinary public HTTPS video URL is required")
    hostname = parsed.hostname.lower()
    if hostname in ("localhost",) or hostname.endswith((".local", ".internal")):
        raise ValueError("Private hosts are not supported")
    for item in socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM):
        address = ipaddress.ip_address(item[4][0])
        if not address.is_global:
            raise ValueError("Private or reserved addresses are not supported")
    return parsed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", default="source-video.mp4")
    args = parser.parse_args()
    parsed = validate_url(args.url)
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    # yt-dlp handles direct MP4/WebM URLs and compatible public video pages.
    # Limit size and duration; never request private sessions or bypass DRM.
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-playlist", "--no-warnings", "--no-progress",
        "--max-filesize", "500M",
        "--match-filter", "duration <= 3600 | duration = NA",
        "--format", "bv*[height<=1080]+ba/b[height<=1080]/b",
        "--merge-output-format", "mp4",
        "--recode-video", "mp4",
        "--output", str(dest.with_suffix("")) + ".%(ext)s",
        args.url,
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if completed.returncode:
        message = (completed.stderr + "\n" + completed.stdout).lower()
        if "sign in to confirm" in message or "not a bot" in message:
            raise SystemExit(
                "::error title=YouTube source access blocked::"
                "YouTube requires sign-in/bot verification on this runner. "
                "Supply a rights-holder-provided direct HTTPS MP4 URL and rerun. "
                "No cookies or access-control bypass will be attempted."
            )
        raise SystemExit(
            f"::error title=Source download failed::yt-dlp exit code {completed.returncode}. "
            "Check the URL is publicly downloadable.\n" + completed.stderr[-3000:]
        )
    result = dest.with_suffix(".mp4")
    if not result.is_file() or result.stat().st_size > MAX_BYTES:
        raise RuntimeError("Expected MP4 not found or exceeds size limit")
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type", "-of", "csv=p=0", str(result)],
        capture_output=True, text=True, check=True,
    )
    streams = probe.stdout.splitlines()
    if "video" not in streams or "audio" not in streams:
        raise RuntimeError("Source must contain both video and audio")
    print("Source media ready:", result)

if __name__ == "__main__":
    main()
