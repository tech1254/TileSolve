// Merge Box Push generator output into tools/box-bank.json, re-verifying every level with an
// independent forward search (fewest pushes must equal the stored par). Usage: node tools/merge-boxes.js a.json b.json ...
const fs=require('fs'),path=require('path'),BANK=path.join(__dirname,'box-bank.json'),CAP=14;
function solve(rows){const H=rows.length,W=rows[0].length,wall=[],goal=new Set(),bx=[];let me=0;
  rows.forEach((row,y)=>[...row].forEach((ch,x)=>{const i=y*W+x;wall[i]=ch==="#";if(".*+".includes(ch))goal.add(i);if("$*".includes(ch))bx.push(i);if("@+".includes(ch))me=i}));
  const reach=(b,from)=>{const bs=new Set(b),seen=new Set([from]),q=[from];for(let h=0;h<q.length;h++){const i=q[h];for(const d of[1,-1,W,-W]){const j=i+d;if(!wall[j]&&!bs.has(j)&&!seen.has(j)){seen.add(j);q.push(j)}}}return seen};
  const key=(b,reg)=>b.slice().sort((a,c)=>a-c).join(",")+"|"+Math.min(...reg);
  let layer=[{bx,reg:reach(bx,me)}];const seen=new Set([key(bx,layer[0].reg)]);
  for(let d=0;d<200&&layer.length;d++){const next=[];
    for(const s of layer){if(s.bx.every(b=>goal.has(b)))return d;
      for(let k=0;k<s.bx.length;k++){const b=s.bx[k];for(const dd of[1,-1,W,-W]){if(!s.reg.has(b-dd)||wall[b+dd]||s.bx.includes(b+dd))continue;
        const nb=s.bx.slice();nb[k]=b+dd;const reg=reach(nb,b),kk=key(nb,reg);if(!seen.has(kk)){seen.add(kk);next.push({bx:nb,reg})}}}}
    layer=next}
  return -1}
const bank=fs.existsSync(BANK)?JSON.parse(fs.readFileSync(BANK,'utf8')):[],have=new Set(bank.map(l=>l.r)),cnt={};
bank.forEach(l=>{const k=l.b+":"+l.p;cnt[k]=(cnt[k]||0)+1});
let added=0,bad=0;
for(const f of process.argv.slice(2))for(const l of JSON.parse(fs.readFileSync(f,'utf8'))){
  const k=l.b+":"+l.p;if(have.has(l.r)||(cnt[k]||0)>=CAP)continue;
  const p=solve(l.r.split("|"));if(p!==l.p){bad++;continue}
  bank.push(l);have.add(l.r);cnt[k]=(cnt[k]||0)+1;added++}
bank.sort((a,b)=>a.b-b.b||a.p-b.p);
fs.writeFileSync(BANK,JSON.stringify(bank));
console.log("added",added,"rejected",bad,"total",bank.length);
for(let b=1;b<=4;b++){const ps=bank.filter(l=>l.b===b).map(l=>l.p);console.log(b,"crates:",ps.length,"levels, pushes",Math.min(...ps),"-",Math.max(...ps))}
