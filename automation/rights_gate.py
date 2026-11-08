"""Fail-closed documented licensing gate for OffTheRecord.aux."""
import argparse, datetime as dt, json
from pathlib import Path
from urllib.parse import urlsplit

PLATFORMS = {"instagram", "youtube"}
def https_url(value):
    p = urlsplit(value or "")
    return p.scheme == "https" and bool(p.hostname) and not p.username and not p.password

def validate(item, platform, today=None):
    today = today or dt.date.today()
    errors = []
    rights = item.get("rights", {})
    if not isinstance(rights, dict): rights = {}
    if item.get("status") != "ready": errors.append("status must be ready")
    if not https_url(item.get("source_url")): errors.append("public HTTPS source_url required")
    if platform not in PLATFORMS: errors.append("unsupported platform")
    if platform not in item.get("platforms", []): errors.append("platform not approved for this item")
    if rights.get("verification") != "documented": errors.append("documented verification required")
    if not rights.get("licensor") or not rights.get("license_id"): errors.append("licensor and license_id required")
    if not https_url(rights.get("evidence_url")): errors.append("HTTPS evidence_url required")
    if rights.get("commercial_use") is not True: errors.append("commercial use not expressly permitted")
    if rights.get("editing") is not True: errors.append("editing not expressly permitted")
    if rights.get("audio") is not True or rights.get("video") is not True: errors.append("both audio and video rights required")
    if rights.get("redistribution") is not True: errors.append("redistribution not expressly permitted")
    if platform not in rights.get("platforms", []): errors.append("license does not cover platform")
    try:
        if dt.date.fromisoformat(rights["expires_on"]) < today: errors.append("license expired")
    except (ValueError, KeyError, TypeError): errors.append("valid expires_on required")
    if item.get("do_not_repost"): errors.append("do_not_repost flag present")
    return errors

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--queue",default="automation/queue.json")
    p.add_argument("--platform",choices=sorted(PLATFORMS))
    p.add_argument("--id")
    args=p.parse_args()
    items=json.loads(Path(args.queue).read_text()).get("items",[])
    selected=[x for x in items if (not args.id or x.get("id")==args.id)]
    if args.id and len(selected)!=1: raise SystemExit("Item ID missing or duplicated")
    report=[]
    for item in selected:
        for platform in ([args.platform] if args.platform else item.get("platforms",[])):
            report.append({"id":item.get("id"),"platform":platform,"errors":validate(item,platform)})
    print(json.dumps(report,indent=2))
    if not report or any(r["errors"] for r in report): raise SystemExit("Rights gate BLOCKED")
if __name__=="__main__":main()
