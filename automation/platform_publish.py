"""Official platform API clients. Requires configured credentials; no scraping or browser automation."""
import json,os,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path

def instagram_publish(video_url, caption):
    token=os.environ["META_ACCESS_TOKEN"]
    ig_id=os.environ["INSTAGRAM_ACCOUNT_ID"]
    base=f"https://graph.facebook.com/v22.0/{ig_id}"
    def post(url,values):
        data=urllib.parse.urlencode({**values,"access_token":token}).encode()
        with urllib.request.urlopen(urllib.request.Request(url,data=data),timeout=45) as r:
            return json.load(r)
    def get(url,params):
        q=urllib.parse.urlencode({**params,"access_token":token})
        with urllib.request.urlopen(url+"?"+q,timeout=45) as r:
            return json.load(r)
    container=post(base+"/media",{"media_type":"REELS","video_url":video_url,"caption":caption,"share_to_feed":"true"})
    cid=container["id"]
    for attempt in range(30):
        status=get(f"https://graph.facebook.com/v22.0/{cid}",{"fields":"status_code,status"})
        if status.get("status_code")=="FINISHED":break
        if status.get("status_code") in ("ERROR","EXPIRED"):raise RuntimeError(f"Instagram processing failed: {status}")
        time.sleep(20)
    else:raise RuntimeError("Instagram container not ready; do not submit duplicate")
    published=post(base+"/media_publish",{"creation_id":cid})
    media_id=published["id"]
    info=get(f"https://graph.facebook.com/v22.0/{media_id}",{"fields":"id,permalink,media_type"})
    if not info.get("permalink"):raise RuntimeError(f"Instagram media created but permalink unverified: {media_id}")
    return {"platform":"instagram","id":media_id,"url":info["permalink"]}

def youtube_publish(video_path,title,description):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    refresh=os.environ["YOUTUBE_REFRESH_TOKEN"]
    creds=Credentials(None,refresh_token=refresh,token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/youtube.upload"])
    creds.refresh(Request())
    service=build("youtube","v3",credentials=creds,cache_discovery=False)
    body={"snippet":{"title":title[:100],"description":description,"categoryId":"10"},
          "status":{"privacyStatus":"public","selfDeclaredMadeForKids":False}}
    request=service.videos().insert(part="snippet,status",body=body,
        media_body=MediaFileUpload(video_path,mimetype="video/mp4",resumable=True,chunksize=8*1024*1024))
    response=None
    while response is None:
        _,response=request.next_chunk()
    vid=response["id"]
    details=service.videos().list(part="status",id=vid).execute()
    if not details.get("items"):raise RuntimeError(f"YouTube upload returned {vid} but lookup failed")
    return {"platform":"youtube","id":vid,"url":f"https://www.youtube.com/shorts/{vid}",
            "privacy":details["items"][0]["status"]["privacyStatus"]}
