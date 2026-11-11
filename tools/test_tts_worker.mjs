// The voice route in worker.js (/api/tts) with a fake Workers AI and D1.  node tools/test_tts_worker.mjs
const store=new Map();globalThis.caches={default:{match:async r=>{const v=store.get(r.url);return v?v.clone():undefined},put:async(r,res)=>{store.set(r.url,res)}}};
const {tts}=await import("../worker.js");
let usage={},runs=0,mode="b64";
const DB={prepare(sql){return{bind(...a){this.a=a;return this},async first(){return usage[this.a[0]]?{n:usage[this.a[0]]}:null},async run(){if(/INSERT/.test(sql))usage[this.a[0]]=(usage[this.a[0]]||0)+1;return{}}}}};
const AI={async run(m,inp){runs++;if(m!=="@cf/myshell-ai/melotts"||!inp.prompt)throw new Error("bad");const bytes=new Uint8Array([0xFF,0xF3,1,2,3]);
  if(mode==="b64")return{audio:btoa(String.fromCharCode(...bytes))};return new Response(bytes).body}};
const waits=[];const ctx={waitUntil:p=>waits.push(p)};
const call=async t=>{const r=await tts(new URL("https://x.dev/api/tts?v=1&t="+encodeURIComponent(t)),{AI,DB},ctx);await Promise.all(waits.splice(0));return r};
const ok=(c,m)=>{console.log((c?"PASS ":"FAIL ")+m);if(!c)process.exitCode=1};
let r=await call("Hello there!");ok(r.status===200&&r.headers.get("content-type")==="audio/mpeg"&&(await r.arrayBuffer()).byteLength===5,"a new line is made into an mp3");
r=await call("Hello there!");ok(r.status===200&&runs===1,"the same line again comes from the cache (no new AI call)");
mode="stream";r=await call("Stream me");ok(r.status===200&&(await r.arrayBuffer()).byteLength===5&&runs===2,"a streamed answer from the model works too");
const day=new Date().toISOString().slice(0,10);ok(usage[day]===2,"each new clip is counted for the day ("+usage[day]+")");
usage[day]=2000;r=await call("Over the limit");ok(r.status===429&&runs===2,"over the daily limit: no AI call, the game uses the device voice");
r=await call("Hello there!");ok(r.status===200,"cached lines still play after the limit");
r=await tts(new URL("https://x.dev/api/tts?t="),{AI,DB},ctx);ok(r.status===400,"empty text is refused");
r=await tts(new URL("https://x.dev/api/tts?t=hi"),{DB},ctx);ok(r.status===503,"no AI binding: the device voice is used");
