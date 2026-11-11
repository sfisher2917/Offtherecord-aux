const json=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{"content-type":"application/json","cache-control":"no-store","x-content-type-options":"nosniff"}});
const models={
 groq:{url:"https://api.groq.com/openai/v1/chat/completions",model:"openai/gpt-oss-20b",key:"GROQ_API_KEY"},
 openrouter:{url:"https://openrouter.ai/api/v1/chat/completions",model:"openrouter/free",key:"OPENROUTER_API_KEY"},
 gemini:{url:"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",model:"gemini-2.5-flash",key:"GEMINI_API_KEY"}
};
async function ask(name,prompt,env){
 const cfg=models[name],key=env[cfg.key];if(!key)return {provider:name,status:"unavailable"};
 const gemini=name==="gemini";
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),12000);
 try{
 const response=await fetch(cfg.url,{method:"POST",signal:controller.signal,headers:gemini?{"content-type":"application/json","x-goog-api-key":key}:{"content-type":"application/json",authorization:"Bearer "+key},body:JSON.stringify(gemini?{contents:[{parts:[{text:prompt}]}],generationConfig:{maxOutputTokens:512}}:{model:cfg.model,messages:[{role:"user",content:prompt}],max_tokens:512})});
 if(!response.ok)return {provider:name,status:"failed",http_status:response.status};
 const data=await response.json();const answer=gemini?data.candidates?.[0]?.content?.parts?.map(p=>p.text||"").join("\n"):data.choices?.[0]?.message?.content;
 return {provider:name,status:answer?"ok":"empty",model:cfg.model,answer:String(answer||"").slice(0,4000)};
 }catch{return {provider:name,status:"failed"};}finally{clearTimeout(timeout);}
}
export default {async fetch(request,env){
 const url=new URL(request.url);
 if(url.pathname==="/health"&&request.method==="GET")return json({status:"configured",active:env.ENABLED==="true"});
 if(url.pathname!=="/review")return json({error:"not found"},404);
 if(request.method!=="POST")return json({error:"method not allowed"},405);
 if(!env.GATEWAY_TOKEN||request.headers.get("authorization")!=="Bearer "+env.GATEWAY_TOKEN)return json({error:"unauthorized"},401);
 if(env.ENABLED!=="true"||env.ZERO_COST_VERIFIED!=="true")return json({error:"disabled pending billing verification"},503);
 if(request.headers.get("content-type")?.split(";")[0]!=="application/json")return json({error:"JSON required"},415);
 const length=Number(request.headers.get("content-length")||0);if(length>8192)return json({error:"too large"},413);
 let body;try{body=await request.json();}catch{return json({error:"invalid JSON"},400);}
 const prompt=body?.prompt;
 if(typeof prompt!=="string"||prompt.trim().length<1||prompt.length>1000)return json({error:"prompt must be 1-1000 characters"},400);
 if(!["groq","openrouter","gemini"].every(k=>env[models[k].key]))return json({error:"provider key missing"},503);
 const results=await Promise.all(["groq","gemini","openrouter"].map(name=>ask(name,prompt,env)));
 return json({results,notice:"Independent AI outputs; ChatGPT should verify and synthesize. No paid fallback."});
}};