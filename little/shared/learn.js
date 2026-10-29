/* Tile Solve "Little learners" engine (Kindergarten to grade 2), built on the game kit (shared/kit.js).
   Each level is a short run of rounds. A game supplies make(level, roundIndex, rng, a) that returns one round.
   "a" is the CONTENT grade: the grade before the player's grade, matched to Alberta's K-6 outcomes
   (-1 = pre-K for Kindergarten players, 0 = Kindergarten for grade 1 players, 1 = grade 1 for grade 2 players...):
     pick  {type:"pick", say, prompt, options:[{key,html,aria?,say?}], answer, cols?}      tap the right answer
     order {type:"order", say, prompt, tiles:[{key,html,aria?,say?}], answer:[keys], size?} tap tiles in order
     sort  {type:"sort", say, prompt, bins:[{key,html,label?}], items:[{key,html,aria?}]}   item.key = its bin
     hunt  {type:"hunt", say, prompt, cells:[{html,ok,aria?}], cols}                      tap every match
     fill  {type:"fill", say, prompt, target, size:10|20}                                 fill a ten frame
     trace {type:"trace", say, prompt, ch}                                                trace a letter/number
     combo {type:"combo", say, prompt, cells:[{html,v}], target, solution:[indexes], fmt?}  tap tiles that add up to target
   Order tiles may carry a val (answer lists vals) so letters can repeat and extra tiles can be decoys.
   "say" is read aloud (🔊 repeats it). Stars: 0-1 oops = 3, 2-3 = 2, more = 1. */
window.TS_LEARN=function(o){
  const $=id=>document.getElementById(id),U=TS_LEARN.util;let K,R=null,S=null;
  const cssq=v=>(window.CSS&&CSS.escape)?CSS.escape(String(v)):String(v).replace(/"/g,'\\"');
  const roundsFor=age=>o.rounds?o.rounds(age):age<=0?4:age===1?5:6;
  /* Research-based support (see the project's research docs):
     - after a wrong answer: say what was picked, replay the question, then take away a wrong choice, then show the answer to tap
     - a round with mistakes comes back once, 2-3 rounds later
     - difficulty steps up after 3 clean rounds in a row and down after a round with 2+ mistakes (o.adapt:false turns this off)
     - numerals shown with dots fade their dots as the child gets each number right */
  function start(n){S={n,i:0,total:roundsFor(K.age),miss:0,rng:K.rng(n),adj:0,streak:0,retry:[]};
    K.stage.insertAdjacentHTML("beforeend",'<div class="lr-dots" id="lrDots"></div><div class="lr-head"><button class="lr-say" id="lrSay" type="button" aria-label="Say it again">🔊</button>'+
      '<div class="lr-prompt" id="lrPrompt"></div></div><div class="lr-body" id="lrBody"></div>');
    $("lrSay").onclick=()=>{TS.talk.on?TS.say(R&&R.say):K.tip("Talking is off. Turn it on in the Levels menu.")};next()}
  function next(){if(!S)return;
    if(S.i>=S.total){const st=S.miss<=1?3:S.miss<=3?2:1;
      K.win({stars:st,text:S.total+" rounds · "+(S.miss?S.miss+" oops":"no oops")+(st===3?" · superstar!":"")+(o.winText?" "+o.winText(S,K):"")});TS.say(st===3?"Great job, superstar!":"Well done!");return}
    // content comes from the grade BEFORE the player's grade (Kindergarten -> pre-K = -1)
    const due=S.retry.findIndex(x=>x.due<=S.i);
    if(due>=0&&S.i<S.total-1){R=JSON.parse(S.retry.splice(due,1)[0].data);R.isRetry=true}
    else{const nEff=o.adapt===false?S.n:Math.max(1,Math.min(40,S.n+S.adj));R=o.make(nEff,S.i,S.rng,K.age-1)}
    R.done=false;R.miss=0;dots();$("lrPrompt").innerHTML=R.prompt||"";K.tip(R.isRetry?"Let's try this one again!":R.text||R.say||"");
    const b=$("lrBody");b.innerHTML="";b.className="lr-body lr-"+R.type;b.removeAttribute("style");TYPES[R.type].draw(b);TS.say(R.say);stats()}
  function dots(){$("lrDots").innerHTML=Array.from({length:S.total},(_,k)=>'<i class="'+(k<S.i?"done":k===S.i?"cur":"")+'"></i>').join("")}
  function stats(){K.stat(Math.min(S.i+1,S.total)+"/"+S.total,"Round");K.sub("Oops "+S.miss)}
  function oops(el,picked){S.miss++;R.miss=(R.miss||0)+1;stats();TS.music.fx("bad");if(el){el.classList.remove("lr-no");void el.offsetWidth;el.classList.add("lr-no")}
    const m=R.miss,b=body();
    // 1st: say what was picked and ask again; 2nd: take away a wrong choice (or point at the answer); 3rd+: show the answer to tap
    if(m===1)TS.say((picked?"That's "+picked+". ":"Not quite. ")+(R.say||""));
    else if(m===2){TS.say(picked?"That's "+picked+". Try again!":"Try again!");if(R.type==="pick")dropOne(b);else flash(TYPES[R.type].target(b))}
    else{TS.say("Tap the one that's glowing!");K.tip("Tap the one that's glowing!");const t=TYPES[R.type].target(b);flash(t);if(t)t.classList.add("lr-show")}
    if(b)b.classList.add("peek")} // numerals that had faded their dots show them again
  function dropOne(b){const left=[...b.querySelectorAll(".lr-opt:not([disabled])")].filter(x=>x.dataset.key!==String(R.answer));if(left.length>1){const x=left[Math.floor(Math.random()*left.length)];x.disabled=true;x.classList.add("lr-off")}}
  function roundDone(){if(R.done)return;R.done=true;TS.music.fx("good");
    // missed rounds come back once; clean rounds in a row step the difficulty up, rough ones step it down
    if(R.miss&&!R.isRetry&&!["meet","sing","trace"].includes(R.type)){const c=JSON.parse(JSON.stringify(R));for(const k of["done","miss","pos","sel","left","on","t","strokes","si","pi"])delete c[k];S.retry.push({due:S.i+3,data:JSON.stringify(c)})}
    if(!R.miss){if(++S.streak>=3){S.adj=Math.min(S.adj+3,8);S.streak=0}}else{S.streak=0;if(R.miss>=2)S.adj=Math.max(S.adj-4,-10)}
    if(R.type==="pick"&&typeof R.answer==="number"&&body().querySelector(".lr-nd"))numeralRight(R.answer);
    const c=document.createElement("div");c.className="lr-cheer";c.textContent=["⭐","🎉","👏","🌟","💫","🥳"][Math.floor(Math.random()*6)];document.body.appendChild(c);setTimeout(()=>c.remove(),900);
    S.i++;dots();setTimeout(next,900)}
  const body=()=>$("lrBody");

  /* ---------- round types ---------- */
  const TYPES={
    pick:{draw(b){const n=R.options.length;b.style.setProperty("--cols",R.cols||(n<=4?n:Math.ceil(n/2)));
        R.options.forEach(op=>{const x=document.createElement("button");x.type="button";x.className="lr-opt";x.innerHTML=op.html;x.dataset.key=op.key;
          x.setAttribute("aria-label",op.aria||String(op.key));
          x.onclick=()=>{if(R.done||K.busy||x.disabled)return;
            if(op.key===R.answer){x.classList.add("lr-yes");if(R.countAlong)countAlong(op.say||String(op.key));else{if(op.say)TS.say(op.say);roundDone()}}
            else{x.disabled=true;x.classList.add("lr-off");oops(x,op.say||(typeof op.key==="number"?String(op.key):""))}};b.appendChild(x)})},
      target:b=>b.querySelector('.lr-opt[data-key="'+cssq(R.answer)+'"]'),
      hint(b){flash(this.target(b))},solve(b){this.target(b).click()}},
    order:{draw(b){R.pos=0;b.innerHTML='<div class="lr-slots"></div><div class="lr-tray"></div>';const sl=b.firstChild,tr=b.lastChild;
        if(R.size)b.style.setProperty("--ts",R.size+"px");if(R.wide)b.classList.add("wide");if(R.cls)b.classList.add(R.cls);
        R.answer.forEach((_,k)=>{const s=document.createElement("div");s.className="lr-slot";s.dataset.n=k+1;sl.appendChild(s)});
        R.tiles.forEach(t=>{const x=document.createElement("button");x.type="button";x.className="lr-tile";x.innerHTML=t.html;x.dataset.key=t.key;x.dataset.val=String(t.val!==undefined?t.val:t.key);x.setAttribute("aria-label",t.aria||String(t.key));
          x.onclick=()=>{if(R.done||K.busy||x.classList.contains("used"))return;
            if(String(t.val!==undefined?t.val:t.key)===String(R.answer[R.pos])){const s=sl.children[R.pos];s.innerHTML=t.html;s.classList.add("full");x.classList.add("used");R.pos++;TS.music.fx("tap");
              if(t.say)TS.say(t.say);if(R.pos>=R.answer.length)roundDone()}else oops(x)};tr.appendChild(x)})},
      target:b=>b.querySelector('.lr-tile:not(.used)[data-val="'+cssq(R.answer[R.pos])+'"]'),
      hint(b){flash(this.target(b))},solve(b){while(!R.done)this.target(b).click()}},
    sort:{draw(b){R.left=R.items.length;R.sel=null;b.innerHTML='<div class="lr-bins"></div><div class="lr-tray"></div>';const bins=b.firstChild,tr=b.lastChild;
        R.bins.forEach(bn=>{const d=document.createElement("button");d.type="button";d.className="lr-bin";d.dataset.bin=bn.key;d.setAttribute("aria-label",bn.label||bn.key);
          d.innerHTML='<div class="lr-binhead">'+bn.html+"</div>"+(bn.label?'<span class="lr-binlbl">'+bn.label+"</span>":"")+'<div class="lr-binin"></div>';
          d.onclick=()=>{if(R.sel!=null)drop(R.sel,d)};bins.appendChild(d)});
        R.items.forEach((it,k)=>{const x=document.createElement("div");x.className="lr-item";x.innerHTML=it.html;x.dataset.k=k;x.setAttribute("role","button");
          x.setAttribute("aria-label",it.aria||"item");tr.appendChild(x)})},
      target:b=>b.querySelector(".lr-tray .lr-item"),
      hint(b){const x=this.target(b);if(!x)return;flash(x);flash(b.querySelector('.lr-bin[data-bin="'+cssq(R.items[+x.dataset.k].key)+'"]'))},
      solve(b){let x;while((x=this.target(b)))drop(x,b.querySelector('.lr-bin[data-bin="'+cssq(R.items[+x.dataset.k].key)+'"]'))}},
    hunt:{draw(b){b.style.setProperty("--cols",R.cols);R.left=R.cells.filter(c=>c.ok).length;
        R.cells.forEach((c,k)=>{const x=document.createElement("button");x.type="button";x.className="lr-cell";x.innerHTML=c.html;x.dataset.k=k;x.setAttribute("aria-label",c.aria||"picture");
          x.onclick=()=>{if(R.done||K.busy||x.classList.contains("found"))return;if(c.ok){x.classList.add("found");TS.music.fx("tap");if(--R.left===0)roundDone()}else oops(x)};b.appendChild(x)})},
      target(b){const k=R.cells.findIndex((c,i)=>c.ok&&!b.children[i].classList.contains("found"));return k<0?null:b.children[k]},
      hint(b){flash(this.target(b))},solve(b){let t;while(!R.done&&(t=this.target(b)))t.click()}},
    /* meet {type:"meet", up, low, pic, word, say, tapSay}: a big letter card; tapping it says its name and sound */
    meet:{draw(b){const x=document.createElement("button");x.type="button";x.className="lr-mcard";x.setAttribute("aria-label",R.up);
        const w=R.word||"";x.innerHTML='<span class="lr-mbig">'+R.up+'<i>'+R.low+'</i></span><span class="lr-mpic">'+(R.pic||"")+'</span><span class="lr-mword"><b>'+w.slice(0,1)+"</b>"+w.slice(1)+'</span><span class="lr-mtap">👆 Tap me!</span>';
        x.onclick=()=>{if(R.done||K.busy)return;TS.say(R.tapSay||R.say);TS.music.fx("tap");x.classList.add("on");clearTimeout(R.t);R.t=setTimeout(()=>roundDone(),1600)};b.appendChild(x)},
      target:b=>b.querySelector(".lr-mcard"),hint(b){flash(this.target(b))},solve(b){this.target(b).click();clearTimeout(R.t);roundDone()}},
    /* sing {type:"sing", letters:[...], notes:[midi...]}: tap the glowing letters in order; each tap plays the next note of the alphabet song */
    sing:{draw(b){R.pos=0;b.style.setProperty("--cols",Math.min(7,R.letters.length));
        R.letters.forEach((l,k)=>{const x=document.createElement("button");x.type="button";x.className="lr-sl"+(k===0?" glow":"");x.textContent=l;x.dataset.k=k;x.setAttribute("aria-label",l);
          x.onclick=()=>{if(R.done||K.busy)return;if(k!==R.pos){x.classList.remove("lr-no");void x.offsetWidth;x.classList.add("lr-no");return}
            note(R.notes[k],k===R.letters.length-1?.9:.45);TS.say(l);x.classList.remove("glow");x.classList.add("sung");R.pos++;
            const nx=b.children[R.pos];if(nx)nx.classList.add("glow");else setTimeout(roundDone,500)};b.appendChild(x)})},
      target:b=>b.querySelector(".lr-sl.glow"),hint(b){flash(this.target(b))},solve(b){let t;while(!R.done&&(t=this.target(b)))t.click()}},
    /* fill {type:"fill", target, size (5, 10 or 20), em?}: tap to fill the frame in order, top row first (research: keep the five-structure);
       tapping a filled box takes the last one out. Each tap says the new count. */
    fill:{draw(b){const n=R.size||10,per=n===5?5:10;R.count=0;
        b.innerHTML='<div class="lr-frames"></div><div class="lr-count"><b id="lrCount">0</b> / '+R.target+"</div>";const fr=b.firstChild;
        const show=()=>{b.querySelectorAll(".lr-fc").forEach((c,k)=>{const on=k<R.count;c.classList.toggle("on",on);c.classList.toggle("em",on&&!!R.em);c.textContent=on&&R.em?R.em:""});$("lrCount").textContent=R.count};
        for(let f=0;f<Math.ceil(n/per);f++){const g=document.createElement("div");g.className="lr-frame"+(per===5?" five":"");
          for(let k=0;k<per;k++){const i=f*per+k,c=document.createElement("button");c.type="button";c.className="lr-fc";c.dataset.i=i;c.setAttribute("aria-label","Box "+(i+1));
            c.onclick=()=>{if(R.done||K.busy)return;if(i<R.count)R.count--;else if(R.count<n)R.count++;show();TS.music.fx("tap");if(R.count)TS.say(String(R.count));
              clearTimeout(R.t);if(R.count===R.target)R.t=setTimeout(()=>{if(!R.done&&R.count===R.target){TS.say(R.target+"!");roundDone()}},650)};g.appendChild(c)}
          fr.appendChild(g)}
        R.on={get size(){return R.count}}},
      target(b){const cs=[...b.querySelectorAll(".lr-fc")];return R.count<R.target?cs[R.count]:cs[R.count-1]},
      hint(b){flash(this.target(b))},
      solve(b){const cs=[...b.querySelectorAll(".lr-fc")];let g=0;while(R.count!==R.target&&g++<40)(R.count<R.target?cs[R.count]:cs[R.count-1]).click()}},
    combo:{draw(b){R.sel=new Set();const fmt=R.fmt||(v=>String(v));
        b.innerHTML='<div class="lr-combo"></div><div class="lr-count">Total: <b id="lrSum">'+fmt(0)+"</b> / "+fmt(R.target)+"</div>";const g=b.firstChild;
        const sum=()=>[...R.sel].reduce((a,k)=>a+R.cells[k].v,0);
        R.cells.forEach((c,k)=>{const x=document.createElement("button");x.type="button";x.className="lr-cbt";x.innerHTML=c.html;x.dataset.k=k;x.setAttribute("aria-label",c.aria||String(c.v));
          x.onclick=()=>{if(R.done||K.busy)return;if(R.sel.has(k)){R.sel.delete(k);x.classList.remove("on")}else{R.sel.add(k);x.classList.add("on")}TS.music.fx("tap");
            const t=sum();$("lrSum").textContent=fmt(t);clearTimeout(R.t);
            if(t===R.target)R.t=setTimeout(()=>{if(!R.done&&sum()===R.target)roundDone()},450);
            else if(t>R.target){oops(x);K.tip("Too much! Take one away.");setTimeout(()=>{if(R.sel.has(k)){R.sel.delete(k);x.classList.remove("on");$("lrSum").textContent=fmt(sum())}},450)}};g.appendChild(x)})},
      target(b){const k=R.solution.find(i=>!R.sel.has(i));return k===undefined?null:b.querySelector('.lr-cbt[data-k="'+k+'"]')},
      hint(b){R.solution.forEach(i=>flash(b.querySelector('.lr-cbt[data-k="'+i+'"]')))},
      solve(b){[...R.sel].filter(i=>!R.solution.includes(i)).forEach(i=>b.querySelector('.lr-cbt[data-k="'+i+'"]').click());
        R.solution.forEach(i=>{if(!R.sel.has(i))b.querySelector('.lr-cbt[data-k="'+i+'"]').click()})}},
    trace:{draw(b){R.strokes=(TS_LEARN.TRACE[R.ch]||TS_LEARN.TRACE.O).map(U.sampleLine);R.si=0;R.pi=0;
        const P=R.strokes;b.innerHTML='<svg class="lr-tsvg'+(R.mode&&R.mode!=="guided"?" "+R.mode:"")+'" viewBox="0 0 100 100" role="img" aria-label="Trace '+R.ch+'"><line x1="0" y1="10" x2="100" y2="10" class="lr-ln"/><line x1="0" y1="50" x2="100" y2="50" class="lr-ln mid"/><line x1="0" y1="90" x2="100" y2="90" class="lr-ln"/>'+
          P.map(p=>'<polyline class="lr-guide" points="'+U.pts(p)+'"/>').join("")+P.map((p,k)=>'<polyline class="lr-ink" data-s="'+k+'" points=""/>').join("")+
          '<circle class="lr-start" r="6.5"/><text class="lr-num" text-anchor="middle" dominant-baseline="central"></text><circle class="lr-demo" r="4.5" hidden/></svg>';
        this.mark(b);if(R.mode==="guided")setTimeout(()=>{if(!R.done&&R.si===0&&R.pi===0)this.hint(b)},700)}, // watch first
      mark(b){const P=R.strokes[R.si];if(!P)return;const s=b.querySelector(".lr-start"),t=b.querySelector(".lr-num"),[x,y]=P[R.pi];
        s.setAttribute("cx",x);s.setAttribute("cy",y);t.setAttribute("x",x);t.setAttribute("y",y);t.textContent=R.si+1;
        b.querySelectorAll(".lr-guide").forEach((g,k)=>g.classList.toggle("now",k===R.si))},
      ink(b){const P=R.strokes[R.si];b.querySelector('.lr-ink[data-s="'+R.si+'"]').setAttribute("points",U.pts(P.slice(0,R.pi+1)))},
      target:b=>b.querySelector(".lr-start"),
      hint(b){const P=R.strokes[R.si],d=b.querySelector(".lr-demo");if(!P)return;d.hidden=false;let k=R.pi,rep=0;
        const step=()=>{if(R.done||!d.isConnected){d.hidden=true;return}k+=1;if(k>=P.length){if(++rep>=2){d.hidden=true;return}k=R.pi}
          d.setAttribute("cx",P[k][0]);d.setAttribute("cy",P[k][1]);setTimeout(step,28)};step();K.tip("Follow the moving dot!")},
      solve(b){while(R.si<R.strokes.length){R.pi=R.strokes[R.si].length-1;this.ink(b);R.si++;R.pi=0}roundDone()}}};
  /* a soft piano note for the alphabet song (quiet when all sound is off) */
  let AC=null;function note(m,sec){if(TS.music.muted)return;try{AC=AC||new(window.AudioContext||window.webkitAudioContext)();if(AC.state==="suspended")AC.resume();
    const t=AC.currentTime+.01,o=AC.createOscillator(),g=AC.createGain();o.type="triangle";o.frequency.value=440*Math.pow(2,(m-69)/12);
    g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(.25,t+.01);g.gain.exponentialRampToValueAtTime(.0001,t+sec+.3);o.connect(g);g.connect(AC.destination);o.start(t);o.stop(t+sec+.35)}catch(e){}}
  /* count along: light each picture in the question one by one while saying the numbers, then the total */
  function countAlong(total){R.done=true;const items=[...$("lrPrompt").querySelectorAll(".lr-cl i,.lr-sc i")];
    items.sort((a,b)=>(+getComputedStyle(a).getPropertyValue("--y")||0)-(+getComputedStyle(b).getPropertyValue("--y")||0)||(+getComputedStyle(a).getPropertyValue("--x")||0)-(+getComputedStyle(b).getPropertyValue("--x")||0));
    TS.say(items.map((_,k)=>k+1).join(", ")+". "+total+"!");items.forEach((x,k)=>setTimeout(()=>{x.classList.add("lr-lit");x.dataset.n=k+1},k*380));
    setTimeout(()=>{R.done=false;roundDone()},items.length*380+600)}
  /* numeral learning: how many times each numeral has been picked right (per player) */
  const NK=()=>"tilesolve:p:"+((TS.players.current()||{}).id||"none")+":numerals";
  function numeralRight(v){const d=TS.store.get(NK(),{});d[v]=(d[v]||0)+1;TS.store.set(NK(),d)}
  function flash(el){if(!el)return;el.classList.remove("lr-hint");void el.offsetWidth;el.classList.add("lr-hint")}

  /* ---------- sorting: drag an item onto a bin, or tap the item then the bin ---------- */
  function drop(x,bin){const it=R.items[+x.dataset.k];setSel(null);
    if(it.key===bin.dataset.bin){bin.querySelector(".lr-binin").appendChild(x);x.classList.add("in");TS.music.fx("tap");if(--R.left===0)roundDone()}else oops(bin)}
  function setSel(x){document.querySelectorAll(".lr-item.sel").forEach(e=>e.classList.remove("sel"));R.sel=x;if(x)x.classList.add("sel")}
  let D=null;
  document.addEventListener("pointerdown",e=>{if(!R||R.done||K.busy)return;
    const x=e.target.closest(".lr-tray .lr-item");if(x&&R.type==="sort"){e.preventDefault();D={x,id:e.pointerId,sx:e.clientX,sy:e.clientY,moved:false};return}
    const svg=e.target.closest(".lr-tsvg");if(svg&&R.type==="trace"){e.preventDefault();const p=svgPt(svg,e),P=R.strokes[R.si];
      if(P&&U.dist(p,P[R.pi])<16){D={svg,id:e.pointerId,trace:true};try{svg.setPointerCapture(e.pointerId)}catch(_){}}}});
  document.addEventListener("pointermove",e=>{if(!D||e.pointerId!==D.id)return;
    if(D.trace){traceTo(D.svg,svgPt(D.svg,e));return}
    if(!D.moved&&Math.hypot(e.clientX-D.sx,e.clientY-D.sy)>8){D.moved=true;const r=D.x.getBoundingClientRect(),f=D.x.cloneNode(true);f.classList.add("lr-fly");
      f.style.width=r.width+"px";f.style.height=r.height+"px";document.body.appendChild(f);D.f=f;D.ox=e.clientX-r.left;D.oy=e.clientY-r.top;D.x.classList.add("lift")}
    if(D.moved)D.f.style.transform="translate("+(e.clientX-D.ox)+"px,"+(e.clientY-D.oy)+"px)"});
  function endD(e){if(!D||e.pointerId!==D.id)return;const d=D;D=null;if(d.trace)return;
    if(!d.moved){setSel(R.sel===d.x?null:d.x);TS.music.fx("tap");return}
    d.f.hidden=true;const under=document.elementFromPoint(e.clientX,e.clientY),bin=under&&under.closest(".lr-bin");d.f.remove();d.x.classList.remove("lift");
    if(bin)drop(d.x,bin)}
  document.addEventListener("pointerup",endD);document.addEventListener("pointercancel",endD);
  function svgPt(svg,e){const r=svg.getBoundingClientRect();return[(e.clientX-r.left)/r.width*100,(e.clientY-r.top)/r.height*100]}
  /* Tracing: the finger must stay near the line; progress moves forward as it reaches the next points. Lifting keeps progress. */
  function traceTo(svg,p){const b=body(),P=R.strokes[R.si];if(!P||R.done)return;let moved=false;
    for(let guard=0;guard<200;guard++){let best=-1;for(let j=R.pi+1;j<=Math.min(P.length-1,R.pi+5);j++)if(U.dist(p,P[j])<13)best=j;if(best<0)break;R.pi=best;moved=true}
    if(!moved)return;TYPES.trace.ink(b);TYPES.trace.mark(b);
    if(R.pi>=P.length-2){R.pi=P.length-1;TYPES.trace.ink(b);R.si++;R.pi=0;D=null;TS.music.fx("tap");
      if(R.si>=R.strokes.length){b.querySelector(".lr-start").setAttribute("r",0);b.querySelector(".lr-num").textContent="";TS.say(R.done?"":R.ch);roundDone()}else TYPES.trace.mark(b)}}

  function hint(){if(!R||R.done)return;TYPES[R.type].hint(body())}
  K=TS_KIT({id:o.id,name:o.name,levels:40,howto:o.howto,start,hint,label:o.label||(()=>""),point:()=>R&&TYPES[R.type].target(body())});
  // Talking on/off lives in the Levels menu.
  const all=document.getElementById("kAll").closest("label");
  all.insertAdjacentHTML("beforebegin",'<label class="toggle"><input type="checkbox" id="lrTalk"> 🗣️ Read things out loud</label>'+
    '<div class="lr-voice"><label for="lrVoice">Voice</label><select id="lrVoice"></select><button class="chip" type="button" id="lrTest">▶ Test</button></div>'+
    '<p class="lr-vtip">Voices come from this device. For a more natural voice: on iPad/iPhone, Settings › Accessibility › Spoken Content › Voices › English, and download an \"Enhanced\" or \"Premium\" voice. On Android, Settings › Text-to-speech › Google, and install voice data.</p>');
  const tk=document.getElementById("lrTalk");tk.checked=TS.talk.on;tk.onchange=()=>{TS.talk.set(tk.checked)};
  const vs=document.getElementById("lrVoice");
  function fillVoices(){const list=TS.talk.voices(),cur=TS.talk.voice;vs.innerHTML=list.length?list.map((v,k)=>'<option value="'+v.uri.replace(/"/g,"&quot;")+'"'+(v.uri===cur?" selected":"")+">"+(k===0?"⭐ ":"")+v.name+" ("+v.lang+")</option>").join(""):"<option>No voices on this device</option>"}
  fillVoices();try{speechSynthesis.addEventListener("voiceschanged",fillVoices)}catch(e){}
  document.getElementById("kLevels").addEventListener("click",fillVoices);
  vs.onchange=()=>{TS.talk.setVoice(vs.value);TS.talk.test()};document.getElementById("lrTest").onclick=()=>TS.talk.test();
  window.__learn={get R(){return R},get S(){return S},K,make:o.make,solve(){TYPES[R.type].solve(body())},target:()=>TYPES[R.type].target(body())};// for tools/test_learn.py
  K.start();return K};

/* ---------- helpers shared by the games ---------- */
TS_LEARN.util=(()=>{
  const ri=(r,a,b)=>a+Math.floor(r()*(b-a+1)),pick=(r,a)=>a[Math.floor(r()*a.length)];
  const shuffle=(r,a)=>{a=a.slice();for(let k=a.length-1;k>0;k--){const j=Math.floor(r()*(k+1));[a[k],a[j]]=[a[j],a[k]]}return a};
  const sample=(r,a,k)=>shuffle(r,a).slice(0,k);
  // shuffle that is never the same as the original order (when possible)
  // shuffle so the result isn't already in order (tiles compare by what they show, so two "e" tiles count as the same); n = how much of the front must differ
  const mix=(r,a,n)=>{if(a.length<2)return a.slice();const sv=x=>x&&typeof x==="object"&&("val" in x||"key" in x)?String(x.val!==undefined?x.val:x.key):x;n=Math.min(n||a.length,a.length);let b,t=0;
    do b=shuffle(r,a);while(b.slice(0,n).every((v,i)=>sv(v)===sv(a[i]))&&++t<50);return b};
  const ramp=(n,from,to,a,b)=>Math.round(a+(b-a)*Math.max(0,Math.min(1,(n-from)/Math.max(1,to-from))));
  // numeric options around an answer, all different, within [lo,hi]
  function near(r,ans,count,lo,hi,spread){const s=new Set([ans]);let guard=0;
    while(s.size<count&&guard++<400){const v=ans+ri(r,-spread,spread);if(v>=lo&&v<=hi)s.add(v)}
    for(let v=lo;s.size<count&&v<=hi;v++)s.add(v);return shuffle(r,[...s])}
  /* ---------- shapes ---------- */
  const poly=(n,rad,rot)=>Array.from({length:n},(_,k)=>{const a=(rot+k*360/n)*Math.PI/180;return(50+rad*Math.cos(a)).toFixed(1)+","+(50+rad*Math.sin(a)).toFixed(1)}).join(" ");
  const star=()=>Array.from({length:10},(_,k)=>{const a=(-90+k*36)*Math.PI/180,rr=k%2?20:44;return(50+rr*Math.cos(a)).toFixed(1)+","+(52+rr*Math.sin(a)).toFixed(1)}).join(" ");
  const SHAPES={circle:'<circle cx="50" cy="50" r="40"/>',oval:'<ellipse cx="50" cy="50" rx="45" ry="27"/>',square:'<rect x="13" y="13" width="74" height="74" rx="4"/>',
    rectangle:'<rect x="5" y="27" width="90" height="46" rx="4"/>',triangle:'<polygon points="50,9 93,87 7,87"/>',star:'<polygon points="'+star()+'"/>',
    heart:'<path d="M50 88C20 66 6 50 6 33 6 19 17 9 30 9c9 0 16 5 20 13 4-8 11-13 20-13 13 0 24 10 24 24 0 17-14 33-44 55z"/>',
    diamond:'<polygon points="50,5 88,50 50,95 12,50"/>',pentagon:'<polygon points="'+poly(5,44,-90)+'"/>',hexagon:'<polygon points="'+poly(6,44,0)+'"/>'};
  const SIDES={triangle:3,square:4,rectangle:4,diamond:4,pentagon:5,hexagon:6,circle:0,oval:0,star:10,heart:0};
  const shape=(kind,col,rot=0,sc=1,outline=false)=>'<svg class="lr-shp" viewBox="0 0 100 100" aria-hidden="true"><g transform="translate(50 50) rotate('+rot+') scale('+sc+') translate(-50 -50)" '+
    (outline?'fill="none" stroke="'+col+'" stroke-width="5" stroke-dasharray="9 7" stroke-linejoin="round"':'fill="'+col+'" stroke="rgba(0,0,0,.28)" stroke-width="3" stroke-linejoin="round"')+">"+SHAPES[kind]+"</g></svg>";
  const COLOURS={red:"#e2412e",blue:"#3b6fd9",green:"#43a047",yellow:"#f5c518",orange:"#f08a24",purple:"#8f5bd6",pink:"#f06fb0",brown:"#8b5a2b",black:"#262626",white:"#fafafa",grey:"#9aa3ad"};
  const SHAPE_COLS=["#e2412e","#3b6fd9","#43a047","#f5c518","#f08a24","#8f5bd6","#f06fb0"];
  /* ---------- pictures of numbers ---------- */
  // n copies of an emoji, arranged in tidy rows (groups of 5 when grouped)
  const cluster=(em,n,cols,grouped)=>'<span class="lr-cl'+(grouped?" grp":"")+'" style="--c:'+(cols||Math.min(5,Math.max(3,Math.ceil(Math.sqrt(n)))))+'">'+Array.from({length:n},()=>"<i>"+em+"</i>").join("")+"</span>";
  const scatter=(r,em,n)=>{const cells=sample(r,[...Array(16).keys()],n);return'<span class="lr-sc">'+cells.map(c=>'<i style="--x:'+(c%4)+';--y:'+((c/4)|0)+'">'+em+"</i>").join("")+"</span>"};
  const tens=(n,em)=>'<span class="lr-tens">'+Array.from({length:Math.floor(n/10)},()=>'<i class="rod" aria-hidden="true">'+"<b></b>".repeat(10)+"</i>").join("")+
    Array.from({length:n%10},()=>'<i class="one"></i>').join("")+"</span>";
  const frame=(n,size=10)=>{const per=size===5?5:10;return'<span class="lr-mini">'+Array.from({length:Math.ceil(size/per)},(_,f)=>'<span class="lr-frame sm'+(per===5?" five":"")+'">'+Array.from({length:per},(_,k)=>'<i class="'+(f*per+k<n?"on":"")+'"></i>').join("")+"</span>").join("")+"</span>"};
  /* ---------- tracing ---------- */
  const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]),pts=p=>p.map(q=>q[0].toFixed(1)+","+q[1].toFixed(1)).join(" ");
  function sampleLine(poly){const out=[poly[0]];for(let k=1;k<poly.length;k++){const a=poly[k-1],b=poly[k],d=dist(a,b),n=Math.max(1,Math.round(d/3));
      for(let j=1;j<=n;j++)out.push([a[0]+(b[0]-a[0])*j/n,a[1]+(b[1]-a[1])*j/n])}return out}
  /* ---------- fractions, coins, clocks, number lines ---------- */
  const frac=(a,b)=>'<span class="lr-frac" aria-label="'+a+' over '+b+'"><i>'+a+"</i><i>"+b+"</i></span>";
  // a pie split into slices with the given angles (degrees); slices listed in "fill" are shaded
  function pie(angles,fill){let a0=-90,out="";angles.forEach((ang,k)=>{const a1=a0+ang,r=44,x0=50+r*Math.cos(a0*Math.PI/180),y0=50+r*Math.sin(a0*Math.PI/180),
      x1=50+r*Math.cos(a1*Math.PI/180),y1=50+r*Math.sin(a1*Math.PI/180);
      out+='<path d="M50 50L'+x0.toFixed(2)+" "+y0.toFixed(2)+"A44 44 0 "+(ang>180?1:0)+" 1 "+x1.toFixed(2)+" "+y1.toFixed(2)+'Z" fill="'+(fill.includes(k)?"#e8833a":"#ffe9a8")+'" stroke="#8a5a1e" stroke-width="2.2" stroke-linejoin="round"/>';a0=a1});
    return'<svg class="lr-pic" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="48" fill="#d9a35a"/>'+out+"</svg>"}
  const pizza=(N,K)=>pie(Array(N).fill(360/N),[...Array(K).keys()]);
  const COIN={5:["#c9ced6","5¢",36],10:["#c9ced6","10¢",31],25:["#c9ced6","25¢",42],100:["#e3b341","$1",44],200:["#e3b341","$2",46]};
  function coin(v){const[c,l,r]=COIN[v];let body;
    if(v===100){const pts=Array.from({length:11},(_,k)=>{const a=(k*360/11-90)*Math.PI/180;return(50+r*Math.cos(a)).toFixed(1)+","+(50+r*Math.sin(a)).toFixed(1)}).join(" ");body='<polygon points="'+pts+'" fill="'+c+'" stroke="#9c7a1e" stroke-width="3"/>'}
    else if(v===200)body='<circle cx="50" cy="50" r="'+r+'" fill="#c9ced6" stroke="#8e96a1" stroke-width="3"/><circle cx="50" cy="50" r="28" fill="#e3b341" stroke="#9c7a1e" stroke-width="2"/>';
    else body='<circle cx="50" cy="50" r="'+r+'" fill="'+c+'" stroke="#8e96a1" stroke-width="3"/><circle cx="50" cy="50" r="'+(r-6)+'" fill="none" stroke="#e8ebef" stroke-width="2"/>';
    return'<svg class="coin" viewBox="0 0 100 100" aria-hidden="true">'+body+'<text x="50" y="52" text-anchor="middle" dominant-baseline="central" font-family="Verdana,sans-serif" font-weight="700" font-size="'+(v>=100?24:Math.max(15,r*.55))+'" fill="#2b2f36">'+l+"</text></svg>"}
  const cents=v=>v<100?v+"¢":"$"+(v/100).toFixed(2);
  function clock(h,m){let t="";for(let k=0;k<60;k++){const a=k*6*Math.PI/180,r1=k%5?42:38;t+='<line x1="'+(50+r1*Math.sin(a)).toFixed(1)+'" y1="'+(50-r1*Math.cos(a)).toFixed(1)+'" x2="'+(50+45*Math.sin(a)).toFixed(1)+'" y2="'+(50-45*Math.cos(a)).toFixed(1)+'" stroke="#2b2f36" stroke-width="'+(k%5?.8:2)+'"/>'}
    for(let k=1;k<=12;k++){const a=k*30*Math.PI/180;t+='<text x="'+(50+31*Math.sin(a)).toFixed(1)+'" y="'+(50-31*Math.cos(a)).toFixed(1)+'" text-anchor="middle" dominant-baseline="central" font-family="Verdana,sans-serif" font-weight="700" font-size="9" fill="#2b2f36">'+k+"</text>"}
    const ha=((h%12)+m/60)*30,ma=m*6;
    return'<svg class="lr-pic" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="47" fill="#fff" stroke="#3b6fd9" stroke-width="4"/>'+t+
      '<line x1="50" y1="50" x2="'+(50+21*Math.sin(ha*Math.PI/180)).toFixed(1)+'" y2="'+(50-21*Math.cos(ha*Math.PI/180)).toFixed(1)+'" stroke="#2b2f36" stroke-width="4.5" stroke-linecap="round"/>'+
      '<line x1="50" y1="50" x2="'+(50+34*Math.sin(ma*Math.PI/180)).toFixed(1)+'" y2="'+(50-34*Math.cos(ma*Math.PI/180)).toFixed(1)+'" stroke="#e2412e" stroke-width="2.6" stroke-linecap="round"/><circle cx="50" cy="50" r="3" fill="#2b2f36"/></svg>'}
  // number line from lo to hi (in "units"), a jump from s to e; fmt turns a unit into a label
  function numberline(lo,hi,tick,label,s,e,fmt){const W=440,x=v=>30+(v-lo)/(hi-lo)*(W-60);let t='<line x1="20" y1="80" x2="'+(W-20)+'" y2="80" stroke="#e9edf1" stroke-width="3"/>';
    for(let v=lo;v<=hi+1e-9;v+=tick){const big=Math.abs(Math.round(v/label)*label-v)<1e-9;t+='<line x1="'+x(v)+'" y1="'+(big?68:73)+'" x2="'+x(v)+'" y2="'+(big?92:87)+'" stroke="#e9edf1" stroke-width="'+(big?3:1.5)+'"/>';
      if(big)t+='<text x="'+x(v)+'" y="116" text-anchor="middle" font-family="Verdana,sans-serif" font-size="22" font-weight="700" fill="#e9edf1">'+fmt(v)+"</text>"}
    const xs=x(s),xe=x(e),mid=(xs+xe)/2;
    t+='<path d="M'+xs+' 76 Q'+mid+" "+(76-Math.min(70,Math.abs(xe-xs)*.6+20))+" "+xe+' 76" fill="none" stroke="#f2c230" stroke-width="3.5" stroke-dasharray="7 5" marker-end="url(#ah)"/>'+
      '<circle cx="'+xs+'" cy="80" r="9" fill="#43a047" stroke="#fff" stroke-width="2"/><text x="'+xe+'" y="62" text-anchor="middle" font-family="Verdana,sans-serif" font-size="26" font-weight="700" fill="#f2c230">?</text>';
    return'<svg class="lr-line" viewBox="0 0 '+W+' 124" aria-hidden="true"><defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#f2c230"/></marker></defs>'+t+"</svg>"}
  /* fav(list): the player's favourite things in the same shape as list ([emoji,name] pairs or plain emoji), or list itself */
  function fav(list){const f=TS.players.fav&&TS.players.fav();if(!f)return list;return Array.isArray(list[0])?f.em:f.em.map(x=>x[0])}
  /* numeral with its dot pattern underneath (dice layout to 6, five-frame rows above), for children still learning to read numbers */
  function numdots(v){const DICE={1:[[50,50]],2:[[28,28],[72,72]],3:[[25,25],[50,50],[75,75]],4:[[28,28],[72,28],[28,72],[72,72]],5:[[25,25],[75,25],[50,50],[25,75],[75,75]],6:[[28,22],[72,22],[28,50],[72,50],[28,78],[72,78]]};
    let d;if(DICE[v])d='<svg class="lr-dice" viewBox="0 0 100 100" aria-hidden="true">'+DICE[v].map(([x,y])=>'<circle cx="'+x+'" cy="'+y+'" r="13"/>').join("")+"</svg>";
    else d='<svg class="lr-dice wide" viewBox="0 0 110 46" aria-hidden="true">'+Array.from({length:Math.min(v,10)},(_,k)=>'<circle cx="'+(11+(k%5)*22)+'" cy="'+(k<5?12:34)+'" r="8.5"/>').join("")+"</svg>";
    const m=(TS.store.get("tilesolve:p:"+((TS.players.current()||{}).id||"none")+":numerals",{})[v])||0;
    return'<span class="lr-nd'+(m>=6?" gone":m>=3?" fade":"")+'"><b>'+v+"</b>"+d+"</span>"}
  /* a train car (or engine) drawn as SVG; label goes on the side */
  function car(col,label,engine){const L=label==null?"":String(label);
    const body=engine?'<path d="M8 20h34v-12h16v12h8a6 6 0 0 1 6 6v18H8z" fill="'+col+'"/><rect x="46" y="11" width="9" height="9" rx="2" fill="#cfe9ff"/><rect x="14" y="2" width="8" height="18" fill="#3a3a3a"/><path d="M72 44l8 6H72z" fill="#555"/>'
      :'<rect x="6" y="10" width="68" height="34" rx="6" fill="'+col+'"/><rect x="12" y="15" width="16" height="11" rx="2" fill="#e8f6ff"/><rect x="52" y="15" width="16" height="11" rx="2" fill="#e8f6ff"/><rect x="2" y="36" width="5" height="4" fill="#555"/><rect x="73" y="36" width="5" height="4" fill="#555"/>';
    return'<svg class="lr-car" viewBox="0 0 80 56" aria-hidden="true">'+body+'<circle cx="22" cy="47" r="7" fill="#2b2f36"/><circle cx="58" cy="47" r="7" fill="#2b2f36"/><circle cx="22" cy="47" r="2.5" fill="#bbb"/><circle cx="58" cy="47" r="2.5" fill="#bbb"/>'+
      (L?'<text x="40" y="'+(engine?35:40)+'" text-anchor="middle" font-family="Andika,Verdana,sans-serif" font-weight="700" font-size="'+(L.length>2?17:26)+'" fill="#fff" stroke="rgba(0,0,0,.35)" stroke-width="1">'+L+"</text>":"")+"</svg>"}
  return{ri,pick,shuffle,sample,mix,ramp,near,shape,SHAPES,SIDES,COLOURS,SHAPE_COLS,cluster,scatter,tens,frame,dist,pts,sampleLine,frac,pie,pizza,coin,cents,clock,numberline,fav,numdots,car}})();

/* Letter and number shapes for tracing, drawn in a 100x100 box (top line y=10, middle y=50, bottom y=90).
   Each character is a list of strokes in writing order; each stroke is a list of points. */
TS_LEARN.TRACE=(()=>{
  const Ln=(x1,y1,x2,y2)=>[[x1,y1],[x2,y2]];
  const Ar=(cx,cy,rx,ry,a0,a1)=>{const n=Math.max(8,Math.round(Math.abs(a1-a0)/10)),o=[];for(let k=0;k<=n;k++){const a=(a0+(a1-a0)*k/n)*Math.PI/180;o.push([cx+rx*Math.cos(a),cy+ry*Math.sin(a)])}return o};
  const J=(...ps)=>ps.reduce((a,p)=>a.concat(a.length&&Math.hypot(a[a.length-1][0]-p[0][0],a[a.length-1][1]-p[0][1])<1.5?p.slice(1):p),[]);
  const bowlTop=J(Ln(25,10,52,10),Ar(52,30,20,20,-90,90),Ln(52,50,25,50)),bowlP=bowlTop;
  return{
    A:[Ln(50,10,20,90),Ln(50,10,80,90),Ln(33,62,67,62)],
    B:[Ln(25,10,25,90),bowlTop,J(Ln(25,50,56,50),Ar(56,70,22,20,-90,90),Ln(56,90,25,90))],
    C:[Ar(55,50,32,40,-45,-315)],
    D:[Ln(25,10,25,90),J(Ln(25,10,42,10),Ar(42,50,36,40,-90,90),Ln(42,90,25,90))],
    E:[Ln(25,10,25,90),Ln(25,10,72,10),Ln(25,50,64,50),Ln(25,90,72,90)],
    F:[Ln(25,10,25,90),Ln(25,10,72,10),Ln(25,50,64,50)],
    G:[J(Ar(55,50,32,40,-45,-360),Ln(87,50,62,50))],
    H:[Ln(25,10,25,90),Ln(75,10,75,90),Ln(25,50,75,50)],
    I:[Ln(50,10,50,90),Ln(32,10,68,10),Ln(32,90,68,90)],
    J:[J(Ln(65,10,65,66),Ar(45,66,20,24,0,180))],
    K:[Ln(28,10,28,90),Ln(72,10,28,56),Ln(42,44,74,90)],
    L:[J(Ln(28,10,28,90),Ln(28,90,72,90))],
    M:[J(Ln(20,90,20,10),Ln(20,10,50,62),Ln(50,62,80,10),Ln(80,10,80,90))],
    N:[J(Ln(25,90,25,10),Ln(25,10,75,90),Ln(75,90,75,10))],
    O:[Ar(50,50,30,40,-90,-450)],
    P:[Ln(25,10,25,90),bowlP],
    Q:[Ar(50,50,30,40,-90,-450),Ln(56,68,80,93)],
    R:[Ln(25,10,25,90),bowlP,Ln(46,50,75,90)],
    S:[J(Ar(50,30,23,20,-25,-270),Ar(50,70,25,20,-90,155))],
    T:[Ln(22,10,78,10),Ln(50,10,50,90)],
    U:[J(Ln(25,10,25,62),Ar(50,62,25,28,180,0),Ln(75,62,75,10))],
    V:[J(Ln(22,10,50,90),Ln(50,90,78,10))],
    W:[J(Ln(14,10,31,90),Ln(31,90,50,36),Ln(50,36,69,90),Ln(69,90,86,10))],
    X:[Ln(25,10,75,90),Ln(75,10,25,90)],
    Y:[Ln(25,10,50,50),J(Ln(75,10,50,50),Ln(50,50,50,90))],
    Z:[J(Ln(25,10,75,10),Ln(75,10,25,90),Ln(25,90,75,90))],
    "0":[Ar(50,50,24,40,-90,-450)],
    "1":[J(Ln(36,24,52,10),Ln(52,10,52,90))],
    "2":[J(Ar(50,32,23,22,-165,30),Ln(70,43,26,90),Ln(26,90,76,90))],
    "3":[J(Ar(48,30,22,20,-150,90),Ar(48,70,25,20,-90,150))],
    "4":[J(Ln(60,10,22,64),Ln(22,64,80,64)),Ln(62,32,62,90)],
    "5":[J(Ln(70,10,33,10),Ln(33,10,31,46),Ar(48,65,25,25,-130,150))],
    "6":[J(Ar(56,56,30,44,-62,-180),Ar(50,68,24,22,180,-180))],
    "7":[J(Ln(25,10,75,10),Ln(75,10,40,90))],
    "8":[Ar(50,30,20,20,-90,-450),Ar(50,70,25,20,-90,-450)],
    "9":[J(Ar(48,32,22,22,0,-360),Ln(70,32,66,90))]}})();
