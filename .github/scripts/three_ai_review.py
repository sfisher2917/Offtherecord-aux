"""Three-provider concurrent review. Manual, read-only, fail-closed."""
import concurrent.futures
import json
import os
import sys
from free_ai_review import PROVIDERS, REQUEST_TIMEOUT_SECONDS
import urllib.request
import urllib.error

def ask(name, prompt):
    secret, url, model = PROVIDERS[name]
    key = os.environ.get(secret, "").strip()
    if not key:
        return {"provider": name, "status": "unavailable", "reason": "Missing key"}
    if name == "gemini":
        body = {"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"maxOutputTokens":512}}
        headers = {"x-goog-api-key":key}
    else:
        body = {"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":512}
        headers = {"Authorization":"Bearer "+key}
    headers["Content-Type"]="application/json"
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers=headers,method="POST")
    try:
        with urllib.request.urlopen(req,timeout=min(REQUEST_TIMEOUT_SECONDS,75)) as response:
            data=json.load(response)
        if name=="gemini":
            answer="\n".join(p.get("text","") for c in data.get("candidates",[]) for p in c.get("content",{}).get("parts",[]))
        else:
            answer=(data.get("choices") or [{}])[0].get("message",{}).get("content","")
        return {"provider":name,"status":"ok","answer":str(answer)[:3500]} if answer else {"provider":name,"status":"empty"}
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,OSError) as error:
        return {"provider":name,"status":"failed","error_type":type(error).__name__}

def main():
    prompt=os.environ.get("PROMPT","").strip()
    if not 1<=len(prompt)<=1000:
        sys.exit("Prompt must be 1-1000 characters")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(lambda name:ask(name,prompt),("groq","gemini","openrouter")))
    # Responses are not executed or fed to other tools.
    for result in results:
        print("###",result["provider"],result["status"])
        if result["status"]=="ok":
            print(result["answer"].replace("::","[colon-colon]"))
        else:
            print(result.get("reason",result.get("error_type","No response")))
    print("Compare results manually; disagreement is not evidence of correctness.")
if __name__=="__main__":
    main()
