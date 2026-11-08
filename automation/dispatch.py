"""Dry-run scheduling inspection; no uploads or publishing performed."""
import datetime, hashlib, json
from pathlib import Path
from zoneinfo import ZoneInfo

root = Path(__file__).resolve().parent
queue = json.loads((root / "queue.json").read_text())
ledger = json.loads((root / "published.json").read_text())
assert queue["timezone"] == "America/New_York"
now = datetime.datetime.now(ZoneInfo(queue["timezone"]))
slot = now.strftime("%Y-%m-%dT%H:%M")
seen = {post["key"] for post in ledger["posts"]}
eligible = []
held = []
for item in queue["items"]:
    if item.get("scheduled_local") != slot or item.get("status") not in ("ready", "approved"):
        continue
    # No separate editorial approval is required. Rights must be established before public upload.
    if not item.get("video_url") or not item.get("rights_evidence_url"):
        held.append({"id": item.get("id"), "reason": "missing media URL or pre-publication rights evidence"})
        continue
    for platform in item.get("platforms", []):
        if platform not in ("youtube", "instagram"):
            continue
        key = hashlib.sha256((item["id"] + "|" + platform).encode()).hexdigest()
        if key not in seen:
            eligible.append({"id": item["id"], "platform": platform, "key": key})
print(json.dumps({"time": slot, "eligible": eligible, "held": held, "mode": "DRY_RUN_ONLY"}, indent=2))
