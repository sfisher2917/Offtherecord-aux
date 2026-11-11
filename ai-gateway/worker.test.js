import test from 'node:test';
import assert from 'node:assert/strict';
import worker from './worker.js';

const url='https://example.workers.dev/review';
const req=(body,token='test-token')=>new Request(url,{method:'POST',headers:{'content-type':'application/json','authorization':'Bearer '+token},body:JSON.stringify(body)});
const env={GATEWAY_TOKEN:'test-token',ENABLED:'true',ZERO_COST_VERIFIED:'true',GROQ_API_KEY:'fake',GEMINI_API_KEY:'fake',OPENROUTER_API_KEY:'fake'};

test('rejects unauthenticated request',async()=>{
 const res=await worker.fetch(req({prompt:'hello'},'wrong'),env);
 assert.equal(res.status,401);
});
test('fails closed when billing is not verified',async()=>{
 const res=await worker.fetch(req({prompt:'hello'}),{...env,ZERO_COST_VERIFIED:'false'});
 assert.equal(res.status,503);
});
test('rejects missing provider credentials before any calls',async()=>{
 const res=await worker.fetch(req({prompt:'hello'}),{...env,GROQ_API_KEY:''});
 assert.equal(res.status,503);
});
test('rejects invalid prompt',async()=>{
 const res=await worker.fetch(req({prompt:'x'.repeat(1001)}),env);
 assert.equal(res.status,400);
});
test('health endpoint reveals no secrets',async()=>{
 const res=await worker.fetch(new Request('https://example.workers.dev/health'),env);
 const data=await res.text();
 assert.equal(res.status,200);
 assert.equal(data.includes('test-token'),false);
});
