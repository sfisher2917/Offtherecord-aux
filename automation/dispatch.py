"""Fail-closed scheduler: validates queue and prints planned jobs; no platform uploads yet."""
import datetime,hashlib,json,os
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent
queue=json.loads((ROOT/"queue.json").read_text())
ledger=json.loads((ROOT/"published.json").read_text())
assert queue["timezone"]=="America/New_York"
now=datetime.datetime.now(ZoneInfo(queue["timezone"]))
slot=now.strftime("%Y-%m-%dT%H:%M")
seen={p["key"] for p in ledger["posts"]}
eligible=[]
for item in queue["items"]:
    if item.get("status")!="approved" or item.get("scheduled_local")!=slot:continue
    if not item.get("rights_evidence_url") or not item.get("video_url"):continue
    for platform in item.get("platforms",[]):
        if platform not in ("youtube","instagram"):continue
        key=hashlib.sha256((item["id"]+"|"+platform).encode()).hexdigest()
        if key not in seen:eligible.append({"id":item["id"],"platform":platform,"key":key})
print(json.dumps({"time":slot,"eligible":eligible,"mode":"DRY_RUN_ONLY"},indent=2))
