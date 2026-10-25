// Builds index.html from src/index.template.html with the puzzle bank baked in.
//   node tools/build.js                 rebuild from tools/car-bank.json
//   node tools/build.js new1.json ...   merge generator output into the bank first
// Every puzzle is re-verified: legal layout, and par equals its true shortest solution.
const fs=require('fs'),path=require('path');
const{encode,decode,eachNext}=require('./engine.js');
const ROOT=path.join(__dirname,'..'),BANKFILE=path.join(__dirname,'car-bank.json'),CAP=150;

const unpack=b=>({h:!!(b&1),len:b&2?3:2,f:(b>>2)&7,p:b>>5});
function shortest(cars,pos){const n=cars.length,tmp=new Array(n),grid=new Int8Array(36),start=encode(pos),d=new Map([[start,0]]),q=[start];
  for(let h=0;h<q.length;h++){const k=q[h];decode(k,n,tmp);if(tmp[0]===4)return d.get(k);
    eachNext(k,tmp,cars,grid,nk=>{if(!d.has(nk)){d.set(nk,d.get(k)+1);q.push(nk)}})}
  return -1}
function verify(bytes,par){const cs=bytes.map(unpack),occ=new Array(36).fill(false);
  if(!(cs[0].h&&cs[0].len===2&&cs[0].f===2))return'red car wrong';
  for(const c of cs){if(c.f>5||c.p+c.len>6)return'out of bounds';if(c.h&&c.f===2&&c!==cs[0])return'blocks exit row';
    for(let j=0;j<c.len;j++){const x=c.h?c.f*6+c.p+j:(c.p+j)*6+c.f;if(occ[x])return'overlap';occ[x]=true}}
  const s=shortest(cs.map(({h,len,f})=>({h,len,f})),cs.map(c=>c.p));
  return s===par?null:'par '+par+' but shortest is '+s}

const bank=fs.existsSync(BANKFILE)?JSON.parse(fs.readFileSync(BANKFILE,'utf8')):{};
const sig=b=>b.slice(1).slice().sort((x,y)=>x-y).join(',')+'|'+b[0];
const seen=new Set();for(const p in bank)for(const b of bank[p])seen.add(sig(b));
for(const f of process.argv.slice(2)){const add=JSON.parse(fs.readFileSync(f,'utf8'));let n=0;
  for(const p in add)for(const e of add[p]){const s=sig(e.c);if(seen.has(s))continue;
    (bank[p]=bank[p]||[]);if(bank[p].length>=CAP)continue;const err=verify(e.c,+p);
    if(err){console.warn('skip',p,err);continue}seen.add(s);bank[p].push(e.c);n++}
  console.log('merged',n,'from',f)}

let bytes=[],total=0;
for(const p of Object.keys(bank).map(Number).sort((a,b)=>a-b))for(const b of bank[p]){
  const err=verify(b,p);if(err)throw new Error('bad puzzle at par '+p+': '+err);
  bytes.push(p,b.length,...b);total++}
fs.writeFileSync(BANKFILE,JSON.stringify(bank));
const b64=Buffer.from(bytes).toString('base64');
const html=fs.readFileSync(path.join(ROOT,'src/index.template.html'),'utf8').replace('"__BANK__"','"'+b64+'"');
fs.writeFileSync(path.join(ROOT,'index.html'),html);
console.log(total,'puzzles;',Object.keys(bank).map(p=>p+':'+bank[p].length).join(' '));
console.log('index.html',(html.length/1024).toFixed(1)+'KB');
