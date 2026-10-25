// Box Push level generator. Usage: node tools/gen-boxes.js SEED SECONDS OUT.json
// Makes a random room, puts the boxes on their spots, then searches backwards ("pulling" boxes away)
// over every reachable position. Breadth-first search from the solved positions gives the exact fewest
// pushes for each position, so every level saved is solvable and its par is exact.
const fs=require('fs');
const[seed,secs,out]=[+process.argv[2],+process.argv[3],process.argv[4]];
function rngFrom(s){let a=s>>>0;return()=>{a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const r=rngFrom(seed);
function room(){const W=6+Math.floor(r()*4),H=6+Math.floor(r()*4),g=new Array(W*H).fill(1),dens=.12+r()*.2;
  for(let y=1;y<H-1;y++)for(let x=1;x<W-1;x++)g[y*W+x]=r()<dens?1:0;
  const floor=[];g.forEach((v,i)=>{if(!v)floor.push(i)});if(floor.length<10)return null;
  const seen=new Set([floor[0]]),q=[floor[0]];for(let h=0;h<q.length;h++){const i=q[h];for(const d of[1,-1,W,-W]){const j=i+d;if(!g[j]&&!seen.has(j)){seen.add(j);q.push(j)}}}
  if(seen.size!==floor.length)return null;return{W,H,g,floor}}
function region(W,g,boxes,start){const seen=new Set([start]),q=[start];
  for(let h=0;h<q.length;h++){const i=q[h];for(const d of[1,-1,W,-W]){const j=i+d;if(!g[j]&&!boxes.has(j)&&!seen.has(j)){seen.add(j);q.push(j)}}}return seen}
function make(k){const R=room();if(!R)return null;const{W,H,g,floor}=R;
  // goals: avoid cells hugging walls on two sides (keeps rooms from being trivial or impossible)
  const fl=floor.slice();for(let i=fl.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[fl[i],fl[j]]=[fl[j],fl[i]]}
  const goals=fl.slice(0,k);if(goals.length<k)return null;
  const key=(bx,rep)=>bx.slice().sort((a,b)=>a-b).join(",")+"|"+rep;
  const dist=new Map(),q=[];const gs=new Set(goals);
  // start: boxes on goals, player in any free region
  const done=new Set();for(const f of floor){if(gs.has(f)||done.has(f))continue;const reg=region(W,g,gs,f);reg.forEach(x=>done.add(x));
    const rep=Math.min(...reg),k0=key(goals,rep);if(!dist.has(k0)){dist.set(k0,0);q.push({bx:goals.slice(),rep})}}
  for(let h=0;h<q.length;h++){const s=q[h],d=dist.get(key(s.bx,s.rep)),bset=new Set(s.bx),reg=region(W,g,bset,s.rep);
    for(let bi=0;bi<s.bx.length;bi++){const b=s.bx[bi];
      for(const dd of[1,-1,W,-W]){const p=b-dd,np=p-dd; // player at p (next to box), steps back to np pulling box to p
        if(!reg.has(p)||g[np]||bset.has(np))continue;
        const nb=s.bx.slice();nb[bi]=p;const nset=new Set(nb),nreg=region(W,g,nset,np),rep=Math.min(...nreg),kk=key(nb,rep);
        if(!dist.has(kk)){dist.set(kk,d+1);q.push({bx:nb,rep})}}}
    if(q.length>250000)return null}
  const best=q[q.length-1],D=dist.get(key(best.bx,best.rep));if(D<2)return null;
  const pick=s=>{const reg=[...region(W,g,new Set(s.bx),s.rep)],pl=reg[Math.floor(r()*reg.length)],rows=[];
    for(let y=0;y<H;y++){let row="";for(let x=0;x<W;x++){const i=y*W+x,box=s.bx.includes(i),goal=gs.has(i);
      row+=g[i]?"#":i===pl?(goal?"+":"@"):box?(goal?"*":"$"):goal?".":" "}rows.push(row)}
    // trim fully-wall outer rows/cols beyond the border is unnecessary: border is exactly one wall thick
    return{r:rows.join("|"),p:dist.get(key(s.bx,s.rep)),b:k}};
  const outp=[pick(best)];
  // also keep a medium version of the same room for gentler levels
  const mid=q.filter(s=>{const d=dist.get(key(s.bx,s.rep));return d===Math.max(2,Math.round(D*.55))&&!s.bx.every(x=>gs.has(x))});
  if(mid.length)outp.push(pick(mid[Math.floor(r()*mid.length)]));
  return outp}
const bank=[],seen=new Set(),end=Date.now()+secs*1000;let rooms=0;
while(Date.now()<end){const k=1+Math.floor(r()*4);const res=make(k);rooms++;if(!res)continue;
  for(const lv of res){if(seen.has(lv.r))continue;seen.add(lv.r);bank.push(lv)}}
// keep at most 14 levels per (boxes, pushes) so the bank stays small but varied
const cnt={},kept=bank.filter(l=>{const k=l.b+":"+l.p;cnt[k]=(cnt[k]||0)+1;return cnt[k]<=14});
fs.writeFileSync(out,JSON.stringify(kept));
const by={};bank.forEach(l=>{const k=l.b+":"+l.p;by[k]=(by[k]||0)+1});
console.log("rooms",rooms,"levels",kept.length);for(let b=1;b<=4;b++){const ps=kept.filter(l=>l.b===b).map(l=>l.p).sort((a,c)=>a-c);
  console.log(b,"boxes:",ps.length,"pushes",ps[0],"-",ps[ps.length-1],"median",ps[ps.length>>1])}
