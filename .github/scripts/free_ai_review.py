import json, os, sys, urllib.request, urllib.error
provider=os.environ["PROVIDER"]
prompt=os.environ["PROMPT"].strip()
if not prompt or len(prompt)>1000: sys.exit("Prompt must be 1-1000 characters")
cfg={
 "groq":("GROQ_API_KEY","https://api.groq.com/openai/v1/chat/completions","openai/gpt-oss-20b"),
 "openrouter":("OPENROUTER_API_KEY","https://openrouter.ai/api/v1/chat/completions","openrouter/free"),
 "gemini":("GEMINI_API_KEY","https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent","gemini-3.8-flash")
}
if provider not in cfg: sys.exit("Provider not allowed")
secret,url,model=cfg[provider]
key=os.environ.get(secret,"")
if not key: sys.exit("Missing secret: "+secret)
if provider=="gemini":
 body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"maxOutputTokens":512}}
 headers={"x-goog-api-key":key}
else:
 body={"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":512}
 headers={"Authorization":"Bearer "+key}
req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={**headers,"Content-Type":"application/json"},method="POST")
try:
 with urllib.request.urlopen(req,timeout=40) as r: response=json.load(r)
except urllib.error.HTTPError as e:
 print("Provider request failed with HTTP",e.code,"(no paid fallback)")
 sys.exit(1)
if provider=="gemini":
 result="\n".join(p.get("text","") for c in response.get("candidates",[]) for p in c.get("content",{}).get("parts",[]))
else: result=response["choices"][0]["message"].get("content","")
print("Provider:",provider,"Model:",model)
print(str(result)[:5000])
