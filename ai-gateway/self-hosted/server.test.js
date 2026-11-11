import test from 'node:test';
import assert from 'node:assert/strict';
import {createHandler} from './server.js';
import {Readable} from 'node:stream';
const env={GATEWAY_TOKEN:'test',ENABLED:'true',ZERO_COST_VERIFIED:'true',GROQ_API_KEY:'x',OPENROUTER_API_KEY:'z'};
async function invoke(handler,path='/review',token='Bearer test',payload={prompt:'hello'}){
 const req=Readable.from([JSON.stringify(payload)]);req.url=path;req.method='POST';req.headers={authorization:token,'content-type':'application/json'};
 let status,body='';const res={writeHead(s){status=s;},end(s){body=s;}};
 await handler(req,res);return {status,body:JSON.parse(body)};
}
test('unauthorized denied',async()=>assert.equal((await invoke(createHandler(env,async()=>{throw Error('should not fetch')}),'/review','Bearer wrong')).status,401));
test('billing guard',async()=>assert.equal((await invoke(createHandler({...env,ZERO_COST_VERIFIED:'false'}))).status,503));
test('missing key',async()=>assert.equal((await invoke(createHandler({...env,GROQ_API_KEY:''}))).status,503));
test('invalid prompt',async()=>assert.equal((await invoke(createHandler(env),'/review','Bearer test',{prompt:'x'.repeat(1001)})).status,400));
test('parallel calls and capped budget',async()=>{
 let count=0;const urls=[];const fetcher=async(url)=>{urls.push(url);count++;return {ok:true,json:async()=>({choices:[{message:{content:'ok'}}]})};};
 const handler=createHandler({...env,MAX_REQUESTS_PER_PROCESS:'1'},fetcher);
 const first=await invoke(handler);assert.equal(first.status,200);assert.equal(first.body.results.length,2);assert.equal(count,2);assert.deepEqual(first.body.results.map(x=>x.provider),['groq','openrouter']);assert.deepEqual(urls.map(u=>new URL(u).hostname),['api.groq.com','openrouter.ai']);
 assert.equal((await invoke(handler)).status,429);
});
test('provider failures do not retry or use a paid fallback',async()=>{
 const calls=[];const fetcher=async(url)=>{calls.push(url);return {ok:false,status:429};};
 const result=await invoke(createHandler(env,fetcher));
 assert.deepEqual(result.body.results.map(x=>[x.provider,x.http_status]),[['groq',429],['openrouter',429]]);
 assert.equal(calls.length,2);
});
test('health lists only the supported providers without credentials',async()=>{
 const handler=createHandler({});let result;
 await handler({url:'/health',method:'GET'},{writeHead(){},end(body){result=JSON.parse(body);}});
 assert.deepEqual(result,{status:'ready',providers:['groq','openrouter'],enabled:false});
});
