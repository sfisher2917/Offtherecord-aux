"""Scheduled intake and readiness audit. NEVER publishes automatically."""
import datetime as dt
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from rights_gate import validate

root = Path(__file__).resolve().parent
queue = json.loads((root / "queue.json").read_text())
ledger = json.loads((root / "published.json").read_text())
assert queue["timezone"] == "America/New_York"
now = dt.datetime.now(ZoneInfo(queue["timezone"]))
seen = {post["key"] for post in ledger["posts"]}
eligible, held = [], []
for item in queue["items"]:
    if item.get("scheduled_local") != now.strftime("%Y-%m-%dT%H:%M"):
        continue
    for platform in item.get("platforms", []):
        if platform not in ("youtube", "instagram"):
            continue
        errors = validate(item, platform, now.date())
        if not item.get("video_url") or not item["video_url"].startswith("https://"):
            errors.append("durable HTTPS finished-video URL required")
        key = hashlib.sha256((item["id"] + "|" + platform).encode()).hexdigest()
        if key in seen: errors.append("already published in ledger")
        if errors: held.append({"id": item.get("id"), "platform": platform, "reasons": errors})
        else: eligible.append({"id": item["id"], "platform": platform, "key": key})
print(json.dumps({"time":now.isoformat(),"eligible_for_future_integration":eligible,"held":held,"mode":"DRY_RUN_NO_PUBLICATION"},indent=2))
