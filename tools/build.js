// Builds the published pages from src/ (home -> index.html, car -> games/car/index.html), baking in the puzzle bank.
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
console.log(total,'puzzles;',Object.keys(bank).map(p=>p+':'+bank[p].length).join(' '));

// Pages: src template -> published path. __V__ is a content hash of the shared files, so Safari
// fetches fresh copies after every update instead of reusing a cached old one.
const crypto=require('crypto'),h=crypto.createHash('sha1');
for(const f of fs.readdirSync(path.join(ROOT,'shared')).sort())h.update(fs.readFileSync(path.join(ROOT,'shared',f)));
const V=h.digest('hex').slice(0,8);
// Pages built with the game kit: every src/<game>.html that isn't listed above becomes games/<game>/index.html.
const PAGES=[['src/home.html','index.html'],['src/car.html','games/car/index.html'],['src/picture.html','games/picture/index.html'],['src/tunes.html','games/carols/index.html']];
for(const f of fs.readdirSync(path.join(ROOT,'src')).sort()){const g=f.replace(/\.html$/,'');
  if(f.endsWith('.html')&&!['home','car','picture'].includes(g))PAGES.push(['src/'+f,'games/'+g+'/index.html'])}
// <!--HEAD:Title--> expands to the standard game-page head; <!--KIT--> to the shared scripts.
const HEAD=t=>`<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#161b21">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);box-sizing:border-box;height:100%}body{margin:0}[hidden]{display:none!important}</style>
<title>${t} · Tile Solve</title>
<meta name="apple-mobile-web-app-title" content="Tile Solve">
<link rel="apple-touch-icon" href="../../icon-180.png">
<link rel="icon" type="image/png" href="../../icon-512.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bungee&family=Barlow:wght@400;600;700&display=swap">
<link rel="stylesheet" href="../../shared/ts.css?v=__V__">
<link rel="stylesheet" href="../../shared/game.css?v=__V__">`;
const KIT=`<script src="../../shared/ts.js?v=__V__"></script>
<script src="../../shared/kit.js?v=__V__"></script>`;
// <!--LEARN--> adds the Little learners engine (shared/learn.js + learn.css) after the kit.
const LEARN=`<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Andika:wght@400;700&display=swap">
<link rel="stylesheet" href="../../shared/learn.css?v=__V__">
<script src="../../shared/learn.js?v=__V__"></script>`;
for(const[src,out]of PAGES){
  let html=fs.readFileSync(path.join(ROOT,src),'utf8').replace(/<!--HEAD:([^>]*)-->/,(_,t)=>HEAD(t)).replace('<!--KIT-->',KIT).replace('<!--LEARN-->',LEARN)
    .replace(/__V__/g,V).replace('"__BANK__"','"'+b64+'"')
    .replace('__BOXBANK__',()=>fs.existsSync(path.join(__dirname,'box-bank.json'))?fs.readFileSync(path.join(__dirname,'box-bank.json'),'utf8'):'[]');
  fs.mkdirSync(path.dirname(path.join(ROOT,out)),{recursive:true});fs.writeFileSync(path.join(ROOT,out),html);
  console.log(out,(html.length/1024).toFixed(1)+'KB','v='+V)}

/* ---------- Little Learners: a second app (its own Cloudflare Worker) built into little/ ----------
   Same pages as Tile Solve, a different home screen (APP="little"), name and icon. */
{const LROOT=path.join(ROOT,'little'),home=fs.readFileSync(path.join(ROOT,'src/home.html'),'utf8');
  fs.rmSync(LROOT,{recursive:true,force:true});fs.mkdirSync(path.join(LROOT,'games'),{recursive:true});
  const ids=[...home.matchAll(/\{id:"([a-z]+)"[^}]*group:"little"/g)].map(m=>m[1]).concat(['patterns','animals','oddone','tunes','carols']);
  const rename=h=>h.replace(/ · Tile Solve<\/title>/g,' · Little Learners</title>').replace(/content="Tile Solve"/g,'content="Little Learners"');
  fs.cpSync(path.join(ROOT,'shared'),path.join(LROOT,'shared'),{recursive:true});
  for(const n of [180,512])fs.copyFileSync(path.join(ROOT,'little-src','icon-'+n+'.png'),path.join(LROOT,'icon-'+n+'.png'));
  let idx=rename(fs.readFileSync(path.join(ROOT,'index.html'),'utf8')).replace('const APP="main";','const APP="little";')
    .replace('<title>Tile Solve</title>','<title>Little Learners</title>').replace('<p class="brand">TILE<span>SOLVE</span></p>','<p class="brand">LITTLE<span>LEARNERS</span></p>');
  if(!idx.includes('const APP="little"'))throw new Error('little home: APP marker missing');
  fs.writeFileSync(path.join(LROOT,'index.html'),idx);
  for(const id of ids){const src=path.join(ROOT,'games',id,'index.html');if(!fs.existsSync(src))throw new Error('little app: no game '+id);
    fs.mkdirSync(path.join(LROOT,'games',id),{recursive:true});fs.writeFileSync(path.join(LROOT,'games',id,'index.html'),rename(fs.readFileSync(src,'utf8')))}
  fs.writeFileSync(path.join(LROOT,'wrangler.jsonc'),JSON.stringify({name:'littlelearners',compatibility_date:'2026-10-01',assets:{directory:'.'}},null,2)+'\n');
  fs.writeFileSync(path.join(LROOT,'.assetsignore'),'wrangler.jsonc\n.assetsignore\n');
  console.log('little/ ('+ids.length+' games)')}
