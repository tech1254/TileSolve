// Offline puzzle generator: hill-climbs random car layouts towards deeper (harder) puzzles and
// keeps one puzzle per par value per climb. Usage: node gen-bank.js SEED SECONDS OUTFILE.json
const fs=require('fs');
const{rngFrom,encode,decode,explore,distances}=require('./engine.js');
const [seed,secs,out]=[+process.argv[2],+process.argv[3],process.argv[4]];
const rng=rngFrom(seed);
const CAP=160; // max puzzles kept per par
const bank={},seen=new Set();
function cells(c,p){const r=[];for(let j=0;j<c.len;j++)r.push(c.h?c.f*6+p+j:(p+j)*6+c.f);return r}
function occOf(cars,pos){const o=new Array(36).fill(false);cars.forEach((c,i)=>cells(c,pos[i]).forEach(x=>o[x]=true));return o}
function tryAdd(cars,pos){const o=occOf(cars,pos);
  for(let t=0;t<60;t++){const h=rng()<0.45,len=rng()<0.3?3:2,f=Math.floor(rng()*6),p=Math.floor(rng()*(7-len));
    if(h&&f===2)continue;const cs=cells({h,len,f},p);if(cs.some(x=>o[x]))continue;
    return{cars:[...cars,{h,len,f}],pos:[...pos,p]}}
  return null}
function remove(cars,pos){if(cars.length<=3)return null;const i=1+Math.floor(rng()*(cars.length-1));
  return{cars:cars.filter((_,k)=>k!==i),pos:pos.filter((_,k)=>k!==i)}}
function evaluate(cfg){const g=explore(cfg.cars,encode(cfg.pos),300000);if(!g||!g.length)return null;
  const{dist,q}=distances(cfg.cars,g);const D=dist.get(q[q.length-1]);
  const far=[];for(let k=q.length-1;k>=0&&dist.get(q[k])===D;k--)far.push(q[k]);
  return{D,far}}
function harvest(cfg,ev,got){const D=ev.D;if(D<3||got.has(D))return;bank[D]=bank[D]||[];if(bank[D].length>=CAP)return;
  const k=ev.far[Math.floor(rng()*ev.far.length)],pos=decode(k,cfg.cars.length,new Array(cfg.cars.length));
  const sig=cfg.cars.map((c,i)=>(c.h?1:0)+(c.len===3?2:0)+c.f*4+pos[i]*32).sort((a,b)=>a-b).join(',');
  if(seen.has(sig))return;seen.add(sig);got.add(D);
  bank[D].push({c:cfg.cars.map((c,i)=>(c.h?1:0)|(c.len===3?2:0)|(c.f<<2)|(pos[i]<<5)),p:D})}
const end=Date.now()+secs*1000;let climbs=0;
while(Date.now()<end){climbs++;
  let cur=null,ev=null;
  for(let t=0;t<50&&!ev;t++){let c={cars:[{h:true,len:2,f:2}],pos:[Math.floor(rng()*3)]};
    const want=5+Math.floor(rng()*8);for(let k=0;k<want;k++){const n=tryAdd(c.cars,c.pos);if(n)c=n}
    const e=evaluate(c);if(e){cur=c;ev=e}}
  if(!ev)continue;const got=new Set();harvest(cur,ev,got);
  let stale=0;
  for(let it=0;it<400&&stale<70&&Date.now()<end;it++){
    const r=rng();let nxt=null;
    if(r<0.4){const a=remove(cur.cars,cur.pos);if(a)nxt=tryAdd(a.cars,a.pos)}
    else if(r<0.75)nxt=tryAdd(cur.cars,cur.pos);else nxt=remove(cur.cars,cur.pos);
    if(!nxt)continue;const e=evaluate(nxt);if(!e){stale++;continue}
    if(e.D>=ev.D){if(e.D>ev.D)stale=0;else stale++;cur=nxt;ev=e;harvest(cur,ev,got)}else stale++}
}
fs.writeFileSync(out,JSON.stringify(bank));
console.log('climbs',climbs,Object.keys(bank).map(k=>k+':'+bank[k].length).join(' '));
