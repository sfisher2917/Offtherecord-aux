import test from 'node:test';
import assert from 'node:assert/strict';
import {createHandler} from './server.js';
import {Readable} from 'node:stream';
const env={GATEWAY_TOKEN:'test',ENABLED:'true',ZERO_COST_VERIFIED:'true',GROQ_API_KEY:'x',GEMINI_API_KEY:'y',OPENROUTER_API_KEY:'z'};
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
 let count=0;const fetcher=async()=>{count++;return {ok:true,json:async()=>({choices:[{message:{content:'ok'}}],candidates:[{content:{parts:[{text:'ok'}]}}]})};};
 const handler=createHandler({...env,MAX_REQUESTS_PER_PROCESS:'1'},fetcher);
 const first=await invoke(handler);assert.equal(first.status,200);assert.equal(first.body.results.length,3);assert.equal(count,3);
 assert.equal((await invoke(handler)).status,429);
});
