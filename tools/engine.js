// Shared Unblock-the-Car solver used by the offline tools (same logic as the game).
const P6=[];for(let i=0,v=1;i<16;i++,v*=6)P6.push(v);

/* ---------- seeded random ---------- */
function rngFrom(seed){let a=seed>>>0;return()=>{a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}

/* ---------- puzzle engine ---------- */
function encode(pos){let k=0;for(let i=0;i<pos.length;i++)k+=pos[i]*P6[i];return k}
function decode(k,n,out){for(let i=0;i<n;i++){out[i]=k%6;k=Math.floor(k/6)}return out}
function fillGrid(pos,cars,grid,skip){grid.fill(-1);
  for(let i=0;i<cars.length;i++){if(i===skip)continue;const c=cars[i],p=pos[i];
    for(let j=0;j<c.len;j++)grid[c.h?c.f*6+p+j:(p+j)*6+c.f]=i}}
function eachNext(key,pos,cars,grid,cb){
  fillGrid(pos,cars,grid,-1);
  for(let i=0;i<cars.length;i++){const c=cars[i],p=pos[i],w=P6[i];
    if(c.h){const b=c.f*6;
      for(let q=p-1;q>=0&&grid[b+q]<0;q--)cb(key+(q-p)*w,i,q);
      for(let e=p+c.len;e<6&&grid[b+e]<0;e++){const q=e-c.len+1;cb(key+(q-p)*w,i,q)}
    }else{
      for(let q=p-1;q>=0&&grid[q*6+c.f]<0;q--)cb(key+(q-p)*w,i,q);
      for(let e=p+c.len;e<6&&grid[e*6+c.f]<0;e++){const q=e-c.len+1;cb(key+(q-p)*w,i,q)}
    }}}
function explore(cars,start,limit){
  const n=cars.length,pos=new Array(n),grid=new Int8Array(36),seen=new Set([start]),q=[start],goals=[];
  for(let h=0;h<q.length;h++){const k=q[h];decode(k,n,pos);if(pos[0]===4)goals.push(k);
    eachNext(k,pos,cars,grid,nk=>{if(!seen.has(nk)){seen.add(nk);q.push(nk)}});
    if(q.length>limit)return null}
  return goals}
function distances(cars,goals){
  const n=cars.length,pos=new Array(n),grid=new Int8Array(36),dist=new Map(),q=goals.slice();
  for(const g of goals)dist.set(g,0);
  for(let h=0;h<q.length;h++){const k=q[h],d=dist.get(k)+1;decode(k,n,pos);
    eachNext(k,pos,cars,grid,nk=>{if(!dist.has(nk)){dist.set(nk,d);q.push(nk)}})}
  return{dist,q}}
function solveNext(cars,pos){
  const n=cars.length,tmp=new Array(n),grid=new Int8Array(36),start=encode(pos);
  if(pos[0]===4)return null;
  const prev=new Map([[start,null]]),q=[start];
  for(let h=0;h<q.length;h++){const k=q[h];decode(k,n,tmp);
    if(tmp[0]===4){let cur=k,step=prev.get(cur);while(step&&step.from!==start){cur=step.from;step=prev.get(cur)}return step}
    eachNext(k,tmp,cars,grid,(nk,i,to)=>{if(!prev.has(nk)){prev.set(nk,{from:k,i,to});q.push(nk)}});
    if(q.length>200000)return null}
  return null}
module.exports={P6,rngFrom,encode,decode,fillGrid,eachNext,explore,distances,solveNext};
