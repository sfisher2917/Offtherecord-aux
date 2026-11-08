"""Single-item GitHub Actions publishing entrypoint.

Fail closed unless explicitly enabled; uploads only user-specified local media.
A platform may succeed before another fails; consult audit artifacts before retrying.
"""
import argparse,json,os,subprocess,sys
from pathlib import Path
from platform_publish import instagram_publish,youtube_publish

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--media",required=True)
    p.add_argument("--title",required=True)
    p.add_argument("--caption",required=True)
    p.add_argument("--platform",choices=["instagram","youtube"],required=True)
    p.add_argument("--video-url",default="")
    p.add_argument("--publish-key",required=True)
    args=p.parse_args()
    if os.getenv("ENABLE_LIVE_PUBLISH")!="true":raise SystemExit("Live publishing disabled; configure secrets and enable explicitly")
    media=Path(args.media)
    if not media.is_file():raise SystemExit("MP4 not found")
    if args.platform=="instagram":
        if not args.video_url.startswith("https://"):raise SystemExit("Instagram requires a durable public HTTPS MP4 URL")
        result=instagram_publish(args.video_url,args.caption)
    else:
        result=youtube_publish(str(media),args.title,args.caption)
    result["publish_key"]=args.publish_key
    Path("publication-result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
if __name__=="__main__":main()
