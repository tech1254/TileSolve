/* Tile Solve game kit: builds the standard game screen (top bar, stage, controls, level picker, win card)
   and handles per-player, per-grade progress and maths-gated hints. A game supplies only its puzzle:

   const K=TS_KIT({id:"memory",name:"Memory Match",levels:40,
     label:n=>"4×3",            // small text under each level in the picker
     start:n=>{...},            // build level n inside K.stage
     hint:()=>{...}});          // called after the maths question is answered (omit for no hint)
   K.win({stars,text}), K.fail({title,text}), K.stat(big,small), K.sub(text), K.tip(text), K.busy */
window.TS_KIT=function(o){
  const PLAYER=TS.requirePlayer(),GRADE=Math.max(1,Math.min(7,PLAYER.grade|0||3)),LEVELS=o.levels||40;
  const SAVE=TS.gameSave(o.id,{grades:{},all:false}),save=SAVE.data;
  const prog=()=>save.grades[GRADE]||(save.grades[GRADE]={unlocked:1,stars:{},last:1});
  const ICON={home:'<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/>',levels:'<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>'};
  const svg=p=>'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+p+"</svg>";
  document.body.insertAdjacentHTML("afterbegin",
    '<div class="app"><header class="top"><div class="left">'+
      '<a class="chip icon" id="kHome" href="../../index.html" aria-label="Home">'+svg(ICON.home)+'</a>'+
      '<button class="chip icon" id="kLevels" type="button" aria-label="Levels">'+svg(ICON.levels)+'</button>'+
      '<button class="chip icon" id="kMusic" type="button"></button></div>'+
      '<div class="lvl"><span class="lbl" id="kSub">'+o.name+'</span><div class="row1"><span class="lbl">Level</span><span class="num" id="kNum">1</span></div></div>'+
      '<div class="stat"><b id="kS1"></b><span class="lbl" id="kS2"></span></div></header>'+
    '<main class="stage" id="kStage"></main>'+
    '<nav class="controls"><button class="arrow" id="kPrev" type="button" aria-label="Previous level">‹</button>'+
      '<button id="kRestart" type="button">Restart</button><button id="kHint" type="button">Hint</button>'+
      '<button class="arrow" id="kNext" type="button" aria-label="Next level">›</button></nav>'+
    '<p class="tip" id="kTip"></p></div>'+
    '<div class="sheet" id="kSheetLevels" hidden><div class="card"><div class="row"><h2>'+o.name+'</h2><button class="close" id="kCloseLevels" type="button">Close</button></div>'+
      '<span class="toggle">Playing as&nbsp;<b id="kWho"></b></span><div class="levels" id="kLevelGrid"></div>'+
      '<label class="toggle"><input type="checkbox" id="kAll"> Open every level (for testing)</label></div></div>'+
    '<div class="sheet" id="kSheetWin" hidden><div class="card"><h2 id="kWinTitle"></h2><div class="stars" id="kWinStars"></div><p class="result" id="kWinText"></p>'+
      '<div class="btns"><button id="kReplay" type="button">Replay</button><button class="go" id="kWinNext" type="button">Next level</button></div></div></div>');
  const $=id=>document.getElementById(id);
  $("kMusic").innerHTML=TS.MUSIC_SVG;TS.music.button($("kMusic"));
  if(!o.hint)$("kHint").disabled=true;
  const K={grade:GRADE,player:PLAYER,levels:LEVELS,stage:$("kStage"),level:1,busy:false,save,persist:SAVE.save,
    tip:t=>{$("kTip").textContent=t||""},stat:(a,b)=>{$("kS1").textContent=a==null?"":a;$("kS2").textContent=b||""},sub:t=>{$("kSub").textContent=t||o.name},
    canPlay:n=>n>=1&&n<=LEVELS&&(save.all||n<=prog().unlocked),
    /* seeded random for level n, different per game and grade */
    rng:n=>TS.rngFrom((o.id.length*7919+o.id.charCodeAt(0)*131)*100003+GRADE*1009+n),
    load(n){n=Math.min(Math.max(1,n|0),LEVELS);
      if(TS.gate.pending(prog(),n)){$("kSheetWin").hidden=true;TS.gate.open(prog(),n,SAVE.save,K.load);return} // maths checkpoint first
      K.level=n;prog().last=n;SAVE.save();K.busy=false;
      $("kSheetWin").hidden=true;K.stage.innerHTML="";K.tip("");K.stat("","");K.sub();nav();o.start(n)},
    win({stars,text,title}){K.busy=true;TS.music.fx("win");const pr=prog();
      pr.stars[K.level]=Math.max(pr.stars[K.level]||0,stars);TS.gate.afterWin(pr,K.level,LEVELS);if(K.level+1>pr.unlocked)pr.unlocked=Math.min(LEVELS,K.level+1);SAVE.save();
      setTimeout(()=>{$("kWinTitle").textContent=title||(K.level===LEVELS?"All "+LEVELS+" levels done!":"Level "+K.level+" done!");
        $("kWinStars").hidden=false;$("kWinStars").innerHTML="★".repeat(stars)+'<span class="off">'+"★".repeat(3-stars)+"</span>";
        $("kWinText").textContent=text||"";$("kReplay").textContent="Replay";$("kWinNext").hidden=K.level>=LEVELS;$("kWinNext").textContent=TS.gate.pending(pr,K.level+1)?"Maths, then next level":"Next level";$("kWinNext").disabled=false;
        $("kSheetWin").hidden=false;nav()},700)},
    fail({title,text}){K.busy=true;TS.music.fx("bad");
      setTimeout(()=>{$("kWinTitle").textContent=title||"Nearly!";$("kWinStars").hidden=true;$("kWinText").textContent=text||"";
        $("kReplay").textContent="Try again";$("kWinNext").hidden=!K.canPlay(K.level+1);$("kSheetWin").hidden=false},500)}};
  function nav(){$("kNum").textContent=K.level;$("kPrev").disabled=K.level<=1;$("kNext").disabled=!K.canPlay(K.level+1)}
  $("kPrev").onclick=()=>{if(K.level>1)K.load(K.level-1)};
  $("kNext").onclick=()=>{if(K.canPlay(K.level+1))K.load(K.level+1)};
  $("kRestart").onclick=()=>K.load(K.level);
  $("kHint").onclick=()=>{if(!K.busy&&o.hint)TS.math.open(o.hint)};
  $("kReplay").onclick=()=>K.load(K.level);
  $("kWinNext").onclick=()=>K.load(K.level+1);
  function drawPicker(){const lg=$("kLevelGrid"),pr=prog();lg.innerHTML="";
    for(let n=1;n<=LEVELS;n++){const b=document.createElement("button");b.type="button";const st=pr.stars[n]||0;
      b.innerHTML="<b>"+n+"</b><span>"+(st?"★".repeat(st):K.canPlay(n)?(o.label?o.label(n):""):"🔒")+"</span>";
      if(n===K.level)b.className="cur";b.disabled=!K.canPlay(n);b.onclick=()=>{$("kSheetLevels").hidden=true;K.load(n)};lg.appendChild(b)}
    $("kAll").checked=!!save.all;$("kWho").textContent=PLAYER.avatar+" "+PLAYER.name+" · "+TS.players.gradeName(GRADE)}
  $("kLevels").onclick=()=>{drawPicker();$("kSheetLevels").hidden=false};
  $("kCloseLevels").onclick=()=>{$("kSheetLevels").hidden=true};
  $("kSheetLevels").addEventListener("click",e=>{if(e.target===$("kSheetLevels"))$("kSheetLevels").hidden=true});
  $("kAll").onchange=e=>{save.all=e.target.checked;SAVE.save();drawPicker();nav()};
  K.start=()=>K.load(prog().last||1);
  return K};
/* Colours for pattern and flood games, each with a shape so colour isn't the only clue. */
window.TS_KIT.COLORS=[{c:"#e2412e",s:"●",name:"red"},{c:"#f2c230",s:"▲",name:"yellow"},{c:"#3b6fd9",s:"■",name:"blue"},
  {c:"#6bb34a",s:"★",name:"green"},{c:"#8f5bd6",s:"◆",name:"purple"},{c:"#f08a24",s:"♥",name:"orange"}];
