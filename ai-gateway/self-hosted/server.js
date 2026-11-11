import http from 'node:http';
import { timingSafeEqual } from 'node:crypto';

const models={
 groq:{url:'https://api.groq.com/openai/v1/chat/completions',model:'openai/gpt-oss-20b',secret:'GROQ_API_KEY'},
 openrouter:{url:'https://openrouter.ai/api/v1/chat/completions',model:'openrouter/free',secret:'OPENROUTER_API_KEY'},
 gemini:{url:'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent',model:'gemini-2.5-flash',secret:'GEMINI_API_KEY'}
};
const send=(res,status,obj)=>{res.writeHead(status,{'content-type':'application/json','cache-control':'no-store','x-content-type-options':'nosniff'});res.end(JSON.stringify(obj));};
const equal=(a,b)=>{const x=Buffer.from(a||''),y=Buffer.from(b||'');return x.length===y.length&&timingSafeEqual(x,y);};
async function ask(name,prompt,env,fetcher){
 const m=models[name],gemini=name==='gemini';
 const headers=gemini?{'x-goog-api-key':env[m.secret]}:{authorization:'Bearer '+env[m.secret]};
 const body=gemini?{contents:[{parts:[{text:prompt}]}],generationConfig:{maxOutputTokens:512}}:{model:m.model,messages:[{role:'user',content:prompt}],max_tokens:512};
 try{
  const response=await fetcher(m.url,{method:'POST',headers:{...headers,'content-type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(12000)});
  if(!response.ok)return {provider:name,status:'failed',http_status:response.status};
  const data=await response.json();
  const answer=gemini?data.candidates?.[0]?.content?.parts?.map(p=>p.text||'').join('\n'):data.choices?.[0]?.message?.content;
  return {provider:name,status:answer?'ok':'empty',model:m.model,answer:String(answer||'').slice(0,4000)};
 }catch{return {provider:name,status:'failed'};}
}
export function createHandler(env=process.env,fetcher=fetch){
 let used=0;
 return async(req,res)=>{
  if(req.url==='/health'&&req.method==='GET')return send(res,200,{status:'ready',enabled:env.ENABLED==='true'&&env.ZERO_COST_VERIFIED==='true'});
  if(req.url!=='/review')return send(res,404,{error:'not found'});
  if(req.method!=='POST')return send(res,405,{error:'method not allowed'});
  if(!env.GATEWAY_TOKEN||!equal(req.headers.authorization,'Bearer '+env.GATEWAY_TOKEN))return send(res,401,{error:'unauthorized'});
  if(env.ENABLED!=='true'||env.ZERO_COST_VERIFIED!=='true')return send(res,503,{error:'disabled until billing verified'});
  if(!Object.values(models).every(m=>env[m.secret]))return send(res,503,{error:'provider credentials missing'});
  if(used>=Number(env.MAX_REQUESTS_PER_PROCESS||10))return send(res,429,{error:'request budget exhausted'});
  if(!req.headers['content-type']?.startsWith('application/json'))return send(res,415,{error:'JSON required'});
  let raw='';for await(const chunk of req){raw+=chunk;if(raw.length>4096)return send(res,413,{error:'request too large'});}
  let data;try{data=JSON.parse(raw);}catch{return send(res,400,{error:'invalid JSON'});}
  if(typeof data.prompt!=='string'||data.prompt.trim().length<1||data.prompt.length>1000)return send(res,400,{error:'prompt must be 1-1000 characters'});
  used++;
  const results=await Promise.all(['groq','gemini','openrouter'].map(name=>ask(name,data.prompt,env,fetcher)));
  return send(res,200,{results,notice:'Unverified independent model responses; verify before using.'});
 };
}
if(process.argv[1]&&import.meta.url===new URL('file://'+process.argv[1]).href){
 const port=Number(process.env.PORT||8787);
 const host=process.env.HOST||'127.0.0.1';
 http.createServer(createHandler()).listen(port,host,()=>console.log('Gateway listening on '+host+':'+port));
}
