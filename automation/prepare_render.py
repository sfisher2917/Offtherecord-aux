"""Prepare a rights-cleared source from the repository manifest for rendering.

This is an authorization *record* check, not independent proof that evidence is genuine.
The manifest must be curated and evidence verified by a human before status=ready.
"""
import argparse, json, os, sys
from pathlib import Path
from rights_gate import validate

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--id",required=True)
    p.add_argument("--queue",default="automation/queue.json")
    p.add_argument("--output",default="render-metadata.json")
    args=p.parse_args()
    matches=[x for x in json.loads(Path(args.queue).read_text())["items"] if x.get("id")==args.id]
    if len(matches)!=1:raise SystemExit("Missing or duplicate content ID")
    item=matches[0]
    platforms=item.get("platforms",[])
    if not platforms or any(validate(item,platform) for platform in platforms):
        raise SystemExit("Rights gate BLOCKED for one or more destination platforms")
    for field in ("artist","title","event","source_url"):
        if not isinstance(item.get(field),str) or not item[field].strip():
            raise SystemExit("Missing required source metadata: "+field)
    start=item.get("start_seconds",0)
    duration=item.get("duration_seconds",59)
    if not isinstance(start,(int,float)) or not isinstance(duration,(int,float)) or start<0 or not 0<duration<=59.5:
        raise SystemExit("Invalid start/duration")
    payload={k:item[k] for k in ("id","artist","title","event","source_url")}
    payload.update(start_seconds=start,duration_seconds=duration,platforms=platforms,
                   license_id=item["rights"]["license_id"],evidence_url=item["rights"]["evidence_url"])
    Path(args.output).write_text(json.dumps(payload,indent=2)+"\n")
    print("Validated documented rights manifest for "+item["id"])
if __name__=="__main__":main()
