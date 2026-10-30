/* Tile Solve shared runtime, loaded by every page: players, per-player saves, music, and maths-for-a-hint.
   Everything is stored on this device (localStorage); there are no accounts. */
window.TS=(()=>{
const HOME=new URL("../index.html",document.currentScript.src).href;

function rngFrom(seed){let a=seed>>>0;return()=>{a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const store={get(k,d){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}},
             set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}},
             del(k){try{localStorage.removeItem(k)}catch(e){}}};

/* ---------- players ---------- */
const PKEY="tilesolve:players";
const data=Object.assign({list:[],current:null,music:true},store.get(PKEY,{}));
const persist=()=>store.set(PKEY,data);
const AVATARS=["🦊","🐼","🐯","🦁","🐸","🐙","🦄","🐢","🐧","🐨","🦖","🐬","🚀","🪐","👽","🌙"];
const COLORS=["#e2412e","#3b6fd9","#2a9d8f","#f08a24","#8f5bd6","#6bb34a","#e06aa6","#4fb3d9"];
const gradeName=g=>g<=0?"Kindergarten":g>=7?"Grade 7+":"Grade "+g;
/* Favourite things: the Little learners games draw their pictures from a player's favourite (kids learn more when it's about what they love). */
const FAVS={trains:{name:"Trains",icon:"🚂",em:[["🚂","trains"],["🚃","train cars"],["🚋","trams"],["🚆","trains"],["🚇","subway trains"],["🚄","fast trains"],["🚉","stations"],["🛤️","tracks"]]},
  trucks:{name:"Trucks",icon:"🚚",em:[["🚚","trucks"],["🚒","fire trucks"],["🚜","tractors"],["🚓","police cars"],["🚑","ambulances"],["🚛","big trucks"],["🏎️","race cars"],["🚌","buses"]]},
  dinos:{name:"Dinosaurs",icon:"🦖",em:[["🦖","T-rexes"],["🦕","dinosaurs"],["🥚","eggs"],["🦴","bones"],["🌋","volcanoes"],["🐊","crocodiles"],["🦎","lizards"],["🌿","leaves"]]},
  space:{name:"Space",icon:"🚀",em:[["🚀","rockets"],["🪐","planets"],["⭐","stars"],["🌙","moons"],["🛸","flying saucers"],["☄️","comets"],["🌍","Earths"],["👩‍🚀","astronauts"]]},
  animals:{name:"Animals",icon:"🐶",em:[["🐶","dogs"],["🐱","cats"],["🐰","bunnies"],["🐻","bears"],["🐸","frogs"],["🦊","foxes"],["🐷","pigs"],["🐮","cows"]]},
  unicorns:{name:"Unicorns",icon:"🦄",em:[["🦄","unicorns"],["🌈","rainbows"],["⭐","stars"],["🧚","fairies"],["🏰","castles"],["👑","crowns"],["💖","hearts"],["🦋","butterflies"]]},
  sports:{name:"Sports",icon:"⚽",em:[["⚽","soccer balls"],["🏀","basketballs"],["🏈","footballs"],["⚾","baseballs"],["🎾","tennis balls"],["🏒","hockey sticks"],["🥅","nets"],["🏆","trophies"]]}};
/* Grades are 0 (Kindergarten) to 7 (7 and up). */
const favOf=()=>{const p=players.current();return p&&FAVS[p.fav]||null};
const gnum=v=>{v=+v;return Number.isFinite(v)&&v>=0&&v<=7?Math.round(v):3};
function add(o){const p={id:Date.now().toString(36)+Math.random().toString(36).slice(2,6),
    name:String(o.name||"").trim().slice(0,16)||"Player",avatar:o.avatar||AVATARS[0],grade:gnum(o.grade),
    color:o.color||COLORS[data.list.length%COLORS.length],fav:FAVS[o.fav]?o.fav:""};
  data.list.push(p);persist();return p}
const players={
  list:()=>data.list.slice(),
  current:()=>data.list.find(p=>p.id===data.current)||null,
  use(id){data.current=id;persist()},
  add,
  update(id,patch){const p=data.list.find(p=>p.id===id);if(!p)return null;Object.assign(p,patch);
    p.name=String(p.name||"").trim().slice(0,16)||"Player";p.grade=gnum(p.grade);persist();return p},
  remove(id){data.list=data.list.filter(p=>p.id!==id);if(data.current===id)data.current=null;
    try{for(let k=localStorage.length-1;k>=0;k--){const key=localStorage.key(k);if(key&&key.startsWith("tilesolve:p:"+id+":"))localStorage.removeItem(key)}}catch(e){}
    persist()},
  AVATARS,COLORS,gradeName,gnum,FAVS,fav:()=>favOf()};

// Before players existed, Unblock the Car kept one save. Turn it into "Player 1" so nobody loses progress.
(()=>{const old=store.get("tilesolve:car",null);if(!old)return;
  if(!data.list.length&&old.grade){const p=add({name:"Player 1",avatar:AVATARS[0],grade:old.grade});data.current=p.id;
    store.set("tilesolve:p:"+p.id+":car",{grades:old.prog||{},all:!!old.all})}
  if(old.music===false)data.music=false;persist();store.del("tilesolve:car")})();
try{for(let k=localStorage.length-1;k>=0;k--){const key=localStorage.key(k);if(key&&key.startsWith("ubc:"))localStorage.removeItem(key)}}catch(e){}

/* A game page calls this first: no player picked means back to the home screen. */
function requirePlayer(){const p=players.current();if(!p){location.replace(HOME);throw new Error("No player selected")}return p}
/* Per-player, per-game save. Returns {data, save()}. */
function gameSave(game,def){const p=players.current(),key="tilesolve:p:"+(p?p.id:"none")+":"+game;
  const d=Object.assign(def,store.get(key,{}));return{data:d,save:()=>store.set(key,d)}}

/* ---------- music & sounds (generated live with Web Audio; nothing to download) ---------- */
const music=(()=>{
  let ctx=null,master=null,bus=null,timer=null,next=0,step=0,mel=[],held=false;
  const rng=rngFrom(20261025),E=60/84/2; // 84 bpm, eighth notes
  const CH=[[48,52,55],[45,48,52],[41,45,48],[43,47,50],[48,52,55],[40,43,47],[41,45,48],[43,47,50]]; // C Am F G C Em F G
  const PENT=[69,72,74,76,79,81,84,86]; // C major pentatonic, A4..D6
  const hz=m=>440*Math.pow(2,(m-69)/12);
  function init(){const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return false;
    ctx=new AC();master=ctx.createGain();master.gain.value=0;
    const lp=ctx.createBiquadFilter();lp.type="lowpass";lp.frequency.value=2600;
    const dl=ctx.createDelay(1);dl.delayTime.value=E*3;const fb=ctx.createGain();fb.gain.value=.28;const wet=ctx.createGain();wet.gain.value=.25;
    bus=ctx.createGain();bus.connect(lp);bus.connect(dl);dl.connect(fb);fb.connect(dl);dl.connect(wet);wet.connect(lp);
    lp.connect(master);master.connect(ctx.destination);return true}
  function tone(m,t,dur,type,vol,att){const o=ctx.createOscillator(),g=ctx.createGain();o.type=type;o.frequency.value=hz(m);
    g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(vol,t+att);g.gain.exponentialRampToValueAtTime(.0001,t+dur);
    o.connect(g);g.connect(bus);o.start(t);o.stop(t+dur+.05)}
  function compose(){mel=[];let ix=2+Math.floor(rng()*3);
    for(let bar=0;bar<8;bar++){const ct=CH[bar].map(n=>n%12);
      for(let e=0;e<8;e++){const strong=e%4===0;
        if(!(strong?rng()<.85:rng()<.42)||(bar%4===3&&e>4)){mel.push(null);continue}
        if(strong){let best=ix,bd=99;for(let k=0;k<PENT.length;k++)if(ct.includes(PENT[k]%12)&&Math.abs(k-ix)<bd){bd=Math.abs(k-ix);best=k}ix=best}
        else ix=Math.max(0,Math.min(PENT.length-1,ix+[-2,-1,-1,1,1,2][Math.floor(rng()*6)]));
        mel.push(PENT[ix])}}}
  function tick(){while(next<ctx.currentTime+.3){const s=step%64,bar=s>>3,e=s&7,t=next,ch=CH[bar];
      if(step%128===0)compose(); // a fresh tune every two times round the chords
      if(e===0){ch.forEach(n=>tone(n+12,t,E*8.6,"sine",.03,.4));tone(ch[0]-12,t,E*3,"triangle",.12,.02)}
      if(e===4)tone(ch[0]-5,t,E*2.5,"triangle",.07,.02);
      if(mel[s])tone(mel[s],t,E*2.4,"triangle",.055,.01);
      next+=E;step++}}
  const api={
    get on(){return data.music!==false},
    start(){if(!api.on||held||data.mute)return;if(!ctx&&!init())return;if(ctx.state==="suspended")ctx.resume();if(timer)return;
      next=ctx.currentTime+.08;master.gain.cancelScheduledValues(ctx.currentTime);master.gain.setTargetAtTime(.55,ctx.currentTime,.8);
      timer=setInterval(tick,60);tick()},
    stop(){if(!timer)return;clearInterval(timer);timer=null;master.gain.cancelScheduledValues(ctx.currentTime);master.gain.setTargetAtTime(0,ctx.currentTime,.12)},
    set(v){data.music=v;persist();v?api.start():api.stop()},
    /* A game that makes its own music (Tile Tunes) holds the background tune off while it plays. */
    hold(v){held=!!v;v?api.stop():api.start()},
    fx(kind){if(api.muted)return;if(!ctx&&!init())return;if(ctx.state==="suspended")ctx.resume();if(ctx.state!=="running")return;const t=ctx.currentTime+.02;
      if(timer===null){master.gain.cancelScheduledValues(t);master.gain.setValueAtTime(.55,t)}
      if(kind==="win")[72,76,79,84].forEach((m,i)=>tone(m,t+i*.11,.55,"triangle",.1,.005));
      else if(kind==="good")[76,84].forEach((m,i)=>tone(m,t+i*.1,.4,"triangle",.1,.005));
      else if(kind==="bad")tone(55,t,.3,"sine",.1,.01);
      else if(kind==="tap")tone(84,t,.12,"sine",.05,.004)},
    pause(){if(ctx&&ctx.state==="running")ctx.suspend()},
    resume(){if(ctx&&api.on&&timer)ctx.resume()},
    /* All sound off (music, tap sounds, the voice and the Tile Tunes piano). */
    get muted(){return data.mute===true},
    /* The sound button cycles: 🎵 everything on → music off (sounds and voice stay) → 🔇 all sound off. */
    button(el){const ST={all:["Music and sounds on",SND.all],sfx:["Music off · sounds on",SND.sfx],mute:["All sound off",SND.mute]};
      const state=()=>data.mute?"mute":api.on?"all":"sfx";
      const sync=()=>{const s=state();el.innerHTML=ST[s][1];el.dataset.snd=s;el.removeAttribute("aria-pressed");el.setAttribute("aria-label",ST[s][0]);el.title=ST[s][0]};
      el.addEventListener("click",()=>{const s=state(),next=s==="all"?"sfx":s==="sfx"?"mute":"all";
        data.mute=next==="mute";persist();if(next==="all")api.set(true);else api.set(false);if(next==="mute")try{speechSynthesis.cancel()}catch(e){}
        sync();toast(el,ST[next][0]);if(next!=="mute")api.fx("tap")});sync()}};
  function toast(el,text){let t=document.getElementById("tsSndToast");if(!t){t=document.createElement("div");t.id="tsSndToast";t.className="ts-toast";document.body.appendChild(t)}
    const r=el.getBoundingClientRect();t.textContent=text;t.style.left=Math.max(8,r.left)+"px";t.style.top=(r.bottom+8)+"px";t.classList.add("show");clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove("show"),1600)}
  // Browsers only allow sound after the player touches something.
  addEventListener("pointerdown",()=>api.start(),true);
  addEventListener("keydown",()=>api.start(),true);
  document.addEventListener("visibilitychange",()=>document.hidden?api.pause():api.resume());
  return api})();
const SV=p=>'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+p+"</svg>";
const SND={all:SV('<path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>'),
  sfx:SV('<path d="M11 5L6 9H3v6h3l5 4z"/><path d="M15.5 9.5a4 4 0 0 1 0 5"/>'),
  mute:SV('<path d="M11 5L6 9H3v6h3l5 4z"/><path d="M16 9l6 6M22 9l-6 6"/>')};
const MUSIC_SVG='<svg class="on" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/></svg>'+
  '<svg class="off" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/><path d="M3 3l18 18"/></svg>';

/* ---------- play reports (to tune difficulty) ----------
   Level results and maths answers are queued on the device and sent in batches to /api/events (worker.js),
   so offline play still counts. Players are sent as their random id, buddy emoji and grade, never their name. */
const report=(()=>{const QK="tilesolve:events",DK="tilesolve:device";let timer=null,busy=false;
  const dev=()=>{let d=store.get(DK,null);if(!d){d=Math.random().toString(36).slice(2,10)+Date.now().toString(36);store.set(DK,d)}return d};
  const little=()=>/^littlelearners\./.test(location.hostname)||/\/little\//.test(location.pathname);
  const on=()=>/^https?:$/.test(location.protocol)&&(!/^(localhost|127\.0\.0\.1)$/.test(location.hostname)||window.TS_REPORT_TEST===true);
  // the endpoint is at the site root (in local tests the little app lives under /little/)
  const ep=()=>(/\/little\//.test(location.pathname)&&!/^littlelearners\./.test(location.hostname)?location.pathname.slice(0,location.pathname.indexOf("/little/")+7):"")+"/api/events";
  function log(ev){const p=players.current();ev.ts=Date.now();ev.id=Math.random().toString(36).slice(2,10)+ev.ts.toString(36);if(p){ev.player=p.id;ev.avatar=p.avatar;ev.grade=p.grade}
    const q=store.get(QK,[]);q.push(ev);while(q.length>500)q.shift();store.set(QK,q);clearTimeout(timer);timer=setTimeout(flush,4000)}
  async function flush(beacon){if(!on()||busy)return;const q=store.get(QK,[]);if(!q.length)return;const batch=q.slice(0,200),n=batch.length;
    const body=JSON.stringify({app:little()?"little":"main",device:dev(),events:batch});
    // page closing: send without waiting, but keep the queue (it may not arrive); the next send repeats it and the server ignores duplicates
    if(beacon===true&&navigator.sendBeacon){try{navigator.sendBeacon(ep(),new Blob([body],{type:"application/json"}))}catch(e){}return}
    busy=true;try{const r=await fetch(ep(),{method:"POST",headers:{"content-type":"application/json"},body,keepalive:true});
      if(r.ok){store.set(QK,store.get(QK,[]).slice(n));busy=false;if(store.get(QK,[]).length)flush();return}}catch(e){}busy=false}
  addEventListener("pagehide",()=>flush(true));
  setTimeout(flush,2500); // anything left over from last time
  return{log,flush,pending:()=>store.get(QK,[]).length}})();

/* ---------- maths: hint questions and level checkpoints ----------
   Calibrated to the Alberta K-6 mathematics curriculum (2022). Kids pick their CURRENT grade, but part way through
   the year they may not have learned it yet, so questions come from the PREVIOUS grade's outcomes:
     Kindergarten player -> pre-K: count pictures (checkpoint 1-5, hint 2-8)
     Grade 1 -> Kindergarten: quantities to 10 (add/take away within 10, make 10)
     Grade 2 -> Grade 1: addition facts to 20 and related subtraction
     Grade 3 -> Grade 2: add and subtract within 100
     Grade 4 -> Grade 3: add/subtract within 1000, multiplication facts to 10 x 10 and related division
     Grade 5 -> Grade 4: facts to 12 x 12, 3-digit x 1-digit, add/subtract within 10 000
     Grade 6 -> Grade 5: 3-digit x 2-digit, 3-digit / 1-digit, larger sums
     Grade 7+ -> Grade 6: multiply/divide by 2-digit numbers, percent of a number
   Checkpoints (before every 3rd new level) use an easier set from the same grade. Three tries at the same question;
   after the third miss the answer is shown and a new question appears. Closing a hint question keeps it, so it
   can't be skipped for an easier one. */
function problem(level,easy){const ri=(a,b)=>a+Math.floor(Math.random()*(b-a+1)),pick=a=>a[Math.floor(Math.random()*a.length)];
  if(level<0){const n=easy?ri(1,5):ri(2,8),em=favOf()?pick(favOf().em)[0]:pick(["🍎","⭐","🐟","🎈","🐞","🍪","🌸","🚗","🦆","🍓"]);return{slot:"n",em,n,ans:n}} // pre-K: count the pictures
  const op=(a,o,b,ans)=>({a,op:o,b,ans,slot:"c"}),add=(a,b)=>op(a,"+",b,a+b),sub=(a,b)=>op(a,"−",b,a-b),
    mul=(a,b)=>op(a,"×",b,a*b),div=(q,b)=>op(q*b,"÷",b,q),miss=(a,c)=>({a,op:"+",c,ans:c-a,slot:"b"}),pct=(p,of)=>op(p+"%","of",of,p*of/100);
  // two-digit ± one-digit with no carrying/borrowing (e.g. 43 + 5, 68 − 3)
  const noCarryAdd=()=>{const t=10*ri(1,8),u=ri(0,8),b=ri(1,9-u);return add(t+u,b)},noBorrowSub=()=>{const t=10*ri(1,9),u=ri(1,9),b=ri(1,u);return sub(t+u,b)};
  const T={
    0:[()=>{const a=ri(1,9);return add(a,ri(1,10-a))},()=>{const a=ri(2,10);return sub(a,ri(1,a-1))},()=>{const a=ri(1,9);return miss(a,10)},()=>{const a=ri(1,5);return miss(a,ri(a+1,10))}],
    1:[()=>add(ri(1,10),ri(1,10)),()=>{const a=ri(5,20);return sub(a,ri(1,Math.min(10,a)))},()=>{const a=ri(1,9);return miss(a,ri(a+1,Math.min(20,a+10)))},()=>{const a=ri(2,9);return add(a,a)}],
    2:[()=>{const b=ri(3,9);return add(ri(11,99-b),b)},()=>{const a=ri(10,79);return add(a,ri(10,99-a))},()=>sub(ri(12,99),ri(3,9)),
       ()=>{const a=ri(25,99);return sub(a,ri(10,a-5))},()=>{const a=ri(3,9);return miss(a,ri(a+3,a+9))},()=>{const a=10*ri(1,7);return miss(a,10*ri(a/10+1,9))}],
    3:[()=>mul(ri(2,10),ri(2,10)),()=>div(ri(2,10),ri(2,10)),()=>{const a=ri(100,800);return add(a,ri(10,999-a))},()=>{const a=ri(200,999);return sub(a,ri(10,a-50))},
       ()=>{const a=10*ri(2,40);return miss(a,a+10*ri(5,50))}],
    4:[()=>mul(ri(2,12),ri(2,12)),()=>div(ri(2,12),ri(2,12)),()=>mul(ri(100,999),ri(2,9)),()=>{const a=ri(1000,8999);return add(a,ri(100,9999-a))},
       ()=>{const a=ri(2000,9999);return sub(a,ri(500,a-100))},()=>mul(ri(11,99),pick([10,100]))],
    5:[()=>mul(ri(100,999),ri(11,99)),()=>div(ri(12,199),ri(2,9)),()=>mul(ri(12,99),ri(3,9)),()=>{const a=ri(10000,899999);return add(a,ri(1000,999999-a))},
       ()=>mul(ri(2,12),ri(2,12))],
    6:[()=>mul(ri(100,999),ri(11,99)),()=>div(ri(11,99),ri(11,40)),()=>pct(pick([10,20,25,50,75]),20*ri(1,20)),()=>{const a=ri(20000,999999);return sub(a,ri(1000,a-1000))}]};
  const E={ // a little easier than the hint questions at the same level
    0:[()=>{const a=ri(1,4);return add(a,ri(1,5-a))},()=>{const a=ri(2,5);return sub(a,ri(1,a-1))},()=>{const a=ri(1,9);return add(a,1)}],
    1:[()=>{const a=ri(1,9);return add(a,ri(1,10-a))},()=>{const a=ri(3,10);return sub(a,ri(1,a-1))},()=>{const a=ri(1,5);return miss(a,ri(a+1,10))},()=>add(10,ri(1,10))],
    2:[noCarryAdd,noBorrowSub,()=>{const a=10*ri(1,8);return add(a,10*ri(1,9-a/10))},()=>{const a=10*ri(3,9);return sub(a,10*ri(1,a/10-1))},()=>{const a=ri(2,9);return add(a,a)},
       ()=>{const a=ri(2,9);return miss(a,ri(a+2,Math.min(20,a+9)))}],
    3:[()=>mul(pick([2,5,10]),ri(1,10)),()=>{const a=100*ri(1,8);return add(a,100*ri(1,9-a/100))},()=>{const a=10*ri(1,7)+ri(0,4),b=10*ri(1,8-Math.floor(a/10))+ri(0,5);return add(a,b)},()=>div(ri(1,10),pick([2,5,10]))],
    4:[()=>mul(ri(2,10),ri(2,10)),()=>div(ri(2,10),ri(2,10)),()=>mul(ri(11,99),10),()=>{const a=100*ri(10,80);return add(a,100*ri(1,19))}],
    5:[()=>mul(ri(2,12),ri(2,12)),()=>div(ri(2,12),ri(2,12)),()=>mul(ri(12,99),ri(2,5))],
    6:[()=>mul(ri(2,12),ri(2,12)),()=>mul(ri(12,99),ri(2,9)),()=>pct(pick([10,50]),10*ri(1,20))]};
  // Weight the first kinds a little more so the gentlest question type comes up often.
  const list=(easy?E:T)[Math.max(0,Math.min(6,level))];return pick(list.concat([list[0]]))()}
// Questions come from the grade BEFORE the player's grade (Kindergarten players get pre-K counting: level -1).
const mathLevel=()=>{const p=players.current(),g=p?gnum(p.grade):3;return Math.max(-1,Math.min(6,g-1))};

const math=(()=>{
  const blank=()=>({q:null,lvl:0,tries:3,entry:"",lock:false,mark:"",done:null}),Ms={hint:blank(),check:blank()};let M=Ms.hint,kind="hint",el=null;
  function build(){el=document.createElement("div");el.className="sheet";el.hidden=true;el.innerHTML=
    '<div class="card" role="dialog" aria-labelledby="tsMathT"><div class="row"><h2 id="tsMathT">Solve it for a hint!</h2><button class="close" type="button">Not now</button></div>'+
    '<p class="result ts-sub" hidden></p><div class="prob" aria-live="polite"></div><div class="tries" aria-label="Tries left"></div><p class="fb" aria-live="polite"></p><div class="keys"></div><div class="ts-pick" hidden></div></div>';
    document.body.appendChild(el);el.querySelector(".close").onclick=close;
    const keys=el.querySelector(".keys");
    ["1","2","3","4","5","6","7","8","9","del","0","ok"].forEach(k=>{const b=document.createElement("button");b.type="button";
      b.textContent=k==="del"?"⌫":k==="ok"?"✓":k;b.dataset.k=k;
      if(k==="del"){b.className="del";b.setAttribute("aria-label","Delete")}
      if(k==="ok"){b.className="ok";b.setAttribute("aria-label","Check answer")}
      b.onclick=()=>press(k);keys.appendChild(b)});
    addEventListener("keydown",e=>{if(el.hidden)return;
      if(/^[0-9]$/.test(e.key))press(e.key);else if(e.key==="Backspace")press("del");else if(e.key==="Enter")press("ok");else if(e.key==="Escape"&&kind==="hint")close()})}
  function newQ(){M.lvl=mathLevel();M.q=problem(M.lvl,kind==="check");M.tries=3;M.entry="";M.mark="";M.opts=null;M.t0=Date.now()}
  const qText=q=>q.slot==="n"?"count "+q.n:q.slot==="b"?q.a+" "+q.op+" ? = "+q.c:q.a+" "+q.op+" "+q.b;
  const logQ=(correct,tries)=>{try{report.log({t:"math",game:report.game||"home",kind,mlevel:M.lvl,q:qText(M.q),correct:correct?1:0,tries,ms:Date.now()-(M.t0||Date.now())})}catch(e){}};
  const left=()=>M.tries<3?(M.tries===1?"Last try!":M.tries+" tries left"):"";
  function render(){const q=M.q,txt=M.entry||(M.mark==="show"?String(q.ans):"?");
    const slot='<span class="slot'+(M.entry||M.mark==="show"?"":" empty")+(M.mark?" "+M.mark:"")+'">'+txt+"</span>",s=x=>"<span>"+x+"</span>";
    const isN=q.slot==="n";el.querySelector(".keys").hidden=isN;el.querySelector(".tries").hidden=isN;el.querySelector(".ts-pick").hidden=!isN;if(isN)drawPick();
    el.querySelector(".prob").innerHTML=isN?'<span class="ts-count" aria-label="'+q.n+' pictures">'+Array.from({length:q.n},(_,i)=>'<span data-i="'+i+'">'+q.em+"</span>").join("")+"</span>"+s("=")+slot
      :q.slot==="b"?s(q.a)+s(q.op)+slot+s("=")+s(q.c):s(q.a)+s(q.op)+s(q.b)+s("=")+slot;
    el.querySelector(".tries").innerHTML=[0,1,2].map(k=>'<i class="'+(k<M.tries?"":"used")+'"></i>').join("")}
  /* Pre-K counting: no keypad. Three big answer buttons each show the numeral AND that many dots, and say the number,
     so a child who can count but can't read numbers yet can answer, and sees and hears the numeral as they do. */
  const WORDS=["zero","one","two","three","four","five","six","seven","eight","nine","ten"];
  function choices(n){if(M.opts&&M.opts.n===n)return M.opts.v;const o=new Set([n]),near=[n-1,n+1,n-2,n+2].filter(v=>v>=1&&v<=10);
    for(const v of near.sort(()=>Math.random()-.5))if(o.size<3)o.add(v);const v=[...o].sort((a,b)=>a-b);M.opts={n,v,off:new Set()};return v}
  const dots=v=>'<span class="ts-dots">'+Array.from({length:v},(_,i)=>"<i"+(i===5?' class="br"':"")+"></i>").join("")+"</span>";
  function drawPick(){const P=el.querySelector(".ts-pick"),q=M.q;P.innerHTML="";
    choices(q.n).forEach(v=>{const b=document.createElement("button");b.type="button";b.dataset.v=v;b.disabled=M.opts.off.has(v)||M.lock;
      b.setAttribute("aria-label",WORDS[v]);b.innerHTML="<b>"+v+"</b>"+dots(v);b.onclick=()=>pickN(v);P.appendChild(b)})}
  function countAlong(n,then){const sp=[...el.querySelectorAll(".ts-count span")];talk.say(Array.from({length:n},(_,i)=>i+1).join(", ")+". "+WORDS[n]+"!");
    sp.forEach((x,i)=>setTimeout(()=>{x.classList.add("lit");x.dataset.n=i+1},i*520));setTimeout(then,n*520+600)}
  function pickN(v){if(M.lock)return;talk.say(WORDS[v]);M.entry=String(v);
    if(v===M.q.ans){logQ(true,M.opts.off.size+1);M.lock=true;notes.addMath();M.mark="good";render();fb("Yes! Let's count them!","good");music.fx("good");const m=M;
      countAlong(v,()=>{m.q=null;m.opts=null;m.lock=false;close();m.done&&m.done()});return}
    // not quite: count together, then try again (that answer is greyed out); no tries are used up
    M.lock=true;M.opts.off.add(v);M.mark="bad";render();music.fx("bad");fb("Not "+v+". Let's count together!","bad");
    setTimeout(()=>countAlong(M.q.n,()=>{M.lock=false;M.entry="";M.mark="";render();el.querySelectorAll(".ts-count span").forEach(x=>x.classList.add("lit"));fb("Now tap the right number!")}),700)}
  function fb(t,cls){const f=el.querySelector(".fb");f.textContent=t||"";f.className="fb"+(cls?" "+cls:"")}
  /* open(onSolved) asks a hint question; open(onSolved,{checkpoint:true}) asks an easier checkpoint question that can't be closed. */
  function open(onSolved,opts){if(!el)build();kind=opts&&opts.checkpoint?"check":"hint";M=Ms[kind];
    el.dataset.kind=kind;el.querySelector("#tsMathT").textContent=kind==="check"?"Maths checkpoint!":"Solve it for a hint!";
    const sub=el.querySelector(".ts-sub");sub.hidden=kind!=="check";sub.textContent="Answer this to unlock the next level.";
    el.querySelector(".close").hidden=kind==="check";
    if(!M.q||M.lvl!==mathLevel())newQ();M.done=onSolved;M.entry="";M.mark="";M.lock=false;render();fb(left());el.hidden=false;
    if(M.q.slot==="n"){talk.say("How many are there? Count them, then tap the number.");fb("Count them, then tap the number!")}}
  function close(){if(el)el.hidden=true}
  function check(){if(M.lock||!M.entry)return;
    if(+M.entry===M.q.ans){logQ(true,4-M.tries);M.lock=true;notes.addMath();M.mark="good";render();fb(kind==="check"?"Correct! On to the next level.":"Correct! Here's your hint.","good");music.fx("good");
      const m=M;setTimeout(()=>{m.q=null;m.lock=false;close();m.done&&m.done()},900);return}
    M.tries--;music.fx("bad");
    if(M.tries>0){M.mark="bad";render();M.entry="";M.mark="";
      fb(M.tries===1?"Not quite. Last try!":"Not quite. Try again! "+M.tries+" tries left","bad");
      setTimeout(()=>{if(!M.lock&&!M.entry)render()},500);return}
    logQ(false,3);M.lock=true;M.entry="";M.mark="show";render();fb("The answer was "+M.q.ans+". Here's a new one!","bad");
    setTimeout(()=>{newQ();M.lock=false;render();fb("");if(M.q.slot==="n")talk.say("How many are there?")},2400)}
  function press(k){if(M.lock)return;
    if(k==="ok")return check();
    if(k==="del")M.entry=M.entry.slice(0,-1);else if(M.entry.length<6)M.entry=(M.entry+k).replace(/^0+(?=\d)/,"");
    M.mark="";render();if(M.entry)fb(left())}
  return{open,close,get isOpen(){return !!el&&!el.hidden},get kind(){return kind}}})();

/* ---------- maths checkpoints every 3 levels ----------
   The first time a player clears level 3, 6, 9…, the next level is "gated": opening it asks a checkpoint question first.
   Games call gate.afterWin(progress, level, totalLevels) when a level is won (before unlocking the next one),
   and gate.open(progress, level, save, go) at the top of loading a level; it returns true if it took over. */
const gate={
  afterWin(pr,level,total){if(level%3===0&&level<total&&level+1>(pr.unlocked|0))pr.gate=level+1},
  pending:(pr,level)=>pr.gate===level,
  open(pr,level,save,go){if(pr.gate!==level)return false;math.open(()=>{delete pr.gate;save();go(level)},{checkpoint:true});return true}};

/* ---------- talking ----------
   TS.say(text) reads text aloud with the device's built-in voice (no downloads). Browsers only allow speech after
   the player has touched the screen, so anything said before the first touch is held and spoken on that touch.
   TS.talk.on / TS.talk.set(bool) is a shared on/off setting. */
const talk=(()=>{let unlocked=false,pending=null,voice=null;
  const ok=()=>"speechSynthesis" in window&&"SpeechSynthesisUtterance" in window;
  /* Voices differ by device. Rank English voices so the most natural-sounding one is used:
     neural/natural/enhanced/premium voices first, then Siri and Google voices, Canadian English preferred;
     joke voices (Zarvox, Bubbles...) are never picked. A parent can choose a different one in the Levels menu. */
  const JOKE=/albert|bad news|bahh|bells|boing|bubbles|cellos|good news|jester|organ|superstar|trinoids|whisper|wobble|zarvox|fred|junior|ralph|kathy|grandpa|grandma|rocko|shelley|eddy|flo|reed|sandy/i;
  function score(v){let s=0;const n=v.name||"",l=(v.lang||"").replace("_","-");
    if(/^en-CA/i.test(l))s+=4;else if(/^en-(US|GB|AU|NZ|IE)/i.test(l))s+=2;else if(/^en/i.test(l))s+=1;else return -99;
    if(/natural|neural|online/i.test(n))s+=8;if(/premium/i.test(n))s+=7;if(/enhanced/i.test(n))s+=6;if(/siri/i.test(n))s+=5;
    if(/google/i.test(n))s+=4;if(/samantha|ava|allison|susan|zoe|nicky|karen|moira|tessa|serena/i.test(n))s+=2;if(JOKE.test(n))s-=50;return s}
  function list(){if(!ok())return[];try{return speechSynthesis.getVoices().filter(v=>score(v)>-50).sort((a,b)=>score(b)-score(a))}catch(e){return[]}}
  function pickVoice(){if(voice)return voice;const vs=list();voice=(data.voice&&vs.find(v=>v.voiceURI===data.voice))||vs[0]||null;return voice}
  if(ok())try{speechSynthesis.addEventListener("voiceschanged",()=>{voice=null})}catch(e){}
  function speak(t){try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t),v=pickVoice();if(v){u.voice=v;u.lang=v.lang}else u.lang="en-CA";
    u.rate=.92;u.pitch=1;speechSynthesis.speak(u)}catch(e){}}
  const api={get on(){return data.talk!==false},
    set(on){data.talk=!!on;persist();if(!on)try{speechSynthesis.cancel()}catch(e){}},
    say(t){api.last=t;if(!t||!api.on||!ok()||music.muted)return;if(!unlocked){pending=t;return}speak(t)},last:"",
    voices:()=>list().map(v=>({uri:v.voiceURI,name:v.name,lang:v.lang})),
    get voice(){const v=pickVoice();return v?v.voiceURI:""},
    setVoice(uri){data.voice=uri||null;persist();voice=null},
    test(){unlocked=true;speak("Hi! I'll read the questions to you. Let's play!")}};
  const unlock=()=>{if(unlocked)return;unlocked=true;if(pending){const t=pending;pending=null;if(api.on&&ok())speak(t)}};
  addEventListener("pointerup",unlock,true);addEventListener("keydown",unlock,true);
  return api})();

/* ---------- how to play ----------
   howto.show(game, title, steps, onClose) shows a "How to play" card: steps are [icon, text] pairs.
   howto.first(game, ...) shows it only the first time this player opens that game.
   point(el) bounces a 👆 finger over an element until the player touches anything. */
const howto=(()=>{let el=null,done=null;
  const key=()=>{const p=players.current();return"tilesolve:p:"+(p?p.id:"none")+":seen"};
  function build(){el=document.createElement("div");el.className="sheet";el.hidden=true;el.innerHTML='<div class="card ts-howto" role="dialog" aria-labelledby="tsHowT"><h2 id="tsHowT"></h2><ol class="ts-steps"></ol><button class="bigbtn" type="button">Let\'s play!</button></div>';
    document.body.appendChild(el);el.querySelector(".bigbtn").onclick=close;el.addEventListener("click",e=>{if(e.target===el)close()})}
  function show(game,title,steps,onClose){if(!el)build();el.querySelector("#tsHowT").textContent="How to play "+title;
    el.querySelector(".ts-steps").innerHTML=steps.map(([i,t])=>'<li><span class="ts-ico" aria-hidden="true">'+i+"</span><span>"+t+"</span></li>").join("");
    done=onClose;el.hidden=false;const seen=store.get(key(),{});seen[game]=1;store.set(key(),seen)}
  function close(){if(el)el.hidden=true;const d=done;done=null;if(d)setTimeout(d,150)}
  const seen=game=>!!store.get(key(),{})[game];
  return{show,first(game,title,steps,onClose){if(seen(game))return false;show(game,title,steps,onClose);return true},seen,get isOpen(){return!!el&&!el.hidden}}})();
let finger=null;
function point(target){unpoint();if(!target)return;const r=target.getBoundingClientRect();if(!r.width)return;
  finger=document.createElement("div");finger.className="ts-finger";finger.textContent="👆";finger.setAttribute("aria-hidden","true");
  finger.style.left=(r.left+r.width/2)+"px";finger.style.top=(r.top+r.height*.55)+"px";document.body.appendChild(finger);
  const off=()=>{unpoint();removeEventListener("pointerdown",off,true)};addEventListener("pointerdown",off,true);setTimeout(unpoint,12000)}
function unpoint(){if(finger){finger.remove();finger=null}}
addEventListener("resize",unpoint);

/* ---------- the train horn: a real recording (a wooden train whistle), shared/horn.mp3, for the train games ----------
   horn.load() fetches it early; horn.play() returns false if it isn't ready (or sound is off) so a game can fall back. */
const HORN_URL=new URL("horn.mp3",document.currentScript.src).href;
const horn=(()=>{let ctx=null,buf=null,loading=null;
  const wake=()=>{if(ctx&&ctx.state==="suspended")ctx.resume()};
  function load(){if(loading)return loading;const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return loading=Promise.resolve(null);
    try{ctx=new AC()}catch(e){return loading=Promise.resolve(null)}addEventListener("pointerdown",wake,true);addEventListener("keydown",wake,true);
    loading=fetch(HORN_URL).then(r=>r.arrayBuffer()).then(a=>new Promise((res,rej)=>ctx.decodeAudioData(a,res,rej))).then(b=>(buf=b)).catch(()=>null);return loading}
  function play(vol){if(music.muted)return true;load();if(!ctx||!buf)return false;wake();
    try{const s=ctx.createBufferSource(),g=ctx.createGain();g.gain.value=vol==null?1:vol;s.buffer=buf;s.connect(g);g.connect(ctx.destination);s.start();return true}catch(e){return false}}
  return{load,play}})();

/* ---------- 🎵 music notes: earned by finishing levels and answering maths, spent... well, counted, to open Tile Tunes songs ---------- */
const notes={
  addMath(){const p=players.current();if(!p)return;const k="tilesolve:p:"+p.id+":notes",d=store.get(k,{math:0});d.math=(d.math||0)+1;store.set(k,d)},
  /* one per level finished (any grade) in every game except Tile Tunes, plus one per maths question answered right */
  count(){const p=players.current();if(!p)return 0;const pre="tilesolve:p:"+p.id+":";let n=(store.get(pre+"notes",{math:0}).math)||0;
    try{for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(!k||!k.startsWith(pre))continue;const g=k.slice(pre.length);
      if(/^(tunes|carols|tunes-options|notes|seen)$/.test(g))continue;const d=store.get(k,null);
      if(d&&d.grades)for(const a in d.grades){const st=d.grades[a]&&d.grades[a].stars;if(st)n+=Object.keys(st).length}}}catch(e){}
    return n}};
return{HOME,rngFrom,store,players,requirePlayer,gameSave,music,horn,notes,report,MUSIC_SVG,math,problem,gate,howto,point,talk,say:t=>talk.say(t)}})();
