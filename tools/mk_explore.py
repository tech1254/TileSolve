"""Writes the "Learn & explore" games (src/<id>.html). Each game only describes its rounds; shared/learn.js runs them.
Content is calibrated to Alberta's K-6 curriculum one grade back: make(level, round, rng, a) gets a = player's grade - 1.
Run: python3 tools/mk_explore.py  (then node tools/build.js)"""
import pathlib, json
SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
G = {}

# ---------------------------------------------------------------- maths
G["maketen"] = ("Make Ten", [["🔟","Each round has a target number."],["👆","Tap numbers that add up to it. Tap again to take one back."],["➕","Later you'll need three numbers!"],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){let target,unit,parts;
  // research + Alberta K: "ways to make 5 and 10" (with dots), then grade 1 bridging through 10 to 20, then 3+ numbers to 100
  if(a<=0){target=n<=12?5:10;unit=1;parts=2}
  else if(a===1){target=n<=10?10:U.pick(r,[11,12,13,14,15,16,17,18]);unit=1;parts=n>25?3:2}
  else if(a===2){target=10*U.ri(r,5,10);unit=10;parts=n>20?3:2}                        // grade 2: within 100, several addends
  else{target=50*U.ri(r,10,20);unit=50;parts=3}                                          // grade 3: within 1000
  const sol=[];let left=target;for(let j=0;j<parts-1;j++){const v=unit*U.ri(r,1,left/unit-(parts-1-j));sol.push(v);left-=v}sol.push(left);
  const extra=Array.from({length:a<=0?3:4},()=>unit*U.ri(r,1,Math.max(1,target/unit-1)));
  const cells=U.shuffle(r,sol.map(v=>({v,sol:true})).concat(extra.map(v=>({v,sol:false}))));
  return{type:"combo",target,say:"Tap numbers that add up to "+target+".",prompt:'<span class="ask">Make</span><span class="big l">'+target+"</span>",
    cells:cells.map(c=>({v:c.v,html:a<=0?U.numdots(c.v):String(c.v)})),solution:cells.map((c,k)=>c.sol?k:-1).filter(k=>k>=0)}}''', [1,4])

G["times"] = ("Times Tables", [["✖️","Answer the times table questions."],["🍪","Equal groups: count how many altogether."],["🧗","Every right answer climbs the ladder!"],["🔊","Tap the speaker to hear it again."]],
r'''rounds:()=>8,
make(n,i,r,a){
  if(a<=2){ // grade 2: skip counting with equal groups (multiplication starts in Alberta grade 3)
    const g=U.ri(r,2,n<=20?4:5),per=U.pick(r,n<=20?[2,5,10]:[2,3,4,5,10]),em=U.pick(r,["🍪","🍎","⭐","🐞","🌸"]),t=g*per,o=new Set([t]);
    for(const d of U.shuffle(r,[per,-per,1,-1,2*per]))if(o.size<4&&t+d>0)o.add(t+d);
    return{type:"pick",say:"There are "+g+" groups of "+per+". How many altogether?",prompt:'<span class="ask">'+g+" groups of "+per+": how many?</span>"+
      '<span class="lr-groups">'+Array.from({length:g},()=>'<span class="grp">'+U.cluster(em,per,per>5?5:per)+"</span>").join("")+"</span>",
      options:U.shuffle(r,[...o]).map(v=>({key:v,html:String(v)})),answer:t}}
  const mx=a===3?10:12,x=U.ri(r,2,n<=10?5:mx),y=U.ri(r,2,mx),div=a>=4&&i%3===2,ans=div?x:x*y,o=new Set([ans]);  // grade 3: to 10x10; grade 4+: to 12x12
  for(const d of U.shuffle(r,div?[1,-1,2,-2,y]:[x,-x,y,-y,1,-1,10]))if(o.size<4&&ans+d>0)o.add(ans+d);
  return{type:"pick",say:div?"What is "+x*y+" divided by "+y+"?":"What is "+x+" times "+y+"?",
    prompt:'<span class="seq"><b class="w">'+(div?x*y+" ÷ "+y:x+" × "+y)+'</b><b class="q">?</b></span>',options:U.shuffle(r,[...o]).map(v=>({key:v,html:String(v)})),answer:ans}}''', [3,7])

G["fractions"] = ("Fraction Pizza", [["🍕","Pizzas are cut into equal slices."],["👀","Look at how many slices there are, and how many are coloured."],["👆","Tap the right fraction or pizza."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const F=(x,y)=>U.frac(x,y),key=(x,y)=>x+"/"+y;
  if(a<=1){ // grade 1: one-half means two EQUAL parts
    if(i%2===0){const opts=U.shuffle(r,[{key:"half",html:U.pizza(2,1)},{key:"uneven",html:U.pie([120,240],[0])},{key:"third",html:U.pizza(3,1)},{key:"quarter",html:U.pizza(4,1)}]).slice(0,a<=0?3:4);
      if(!opts.some(o=>o.key==="half"))opts[0]={key:"half",html:U.pizza(2,1)};
      return{type:"pick",cols:2,say:"Which pizza shows one half? Two equal parts!",prompt:'<span class="ask">Which shows one half?</span>',options:U.shuffle(r,opts),answer:"half"}}
    return{type:"pick",cols:2,say:"Which pizza is cut into two equal halves?",prompt:'<span class="ask">Which is cut into equal halves?</span>',
      options:U.shuffle(r,[{key:"eq",html:U.pizza(2,0)},{key:"no",html:U.pie([100,260],[])},{key:"no2",html:U.pie([150,210],[])}]),answer:"eq"}}
  if(a===2){ // grade 2: unit fractions, 10 or fewer parts
    const N=U.ri(r,2,n<=20?4:8),o=new Set([N]);while(o.size<4)o.add(U.ri(r,2,10));
    return{type:"pick",say:"The pizza has "+N+" equal slices and 1 is coloured. What fraction is coloured?",prompt:'<span class="ask">What fraction is coloured?</span>'+U.pizza(N,1),
      options:U.shuffle(r,[...o]).map(d=>({key:key(1,d),html:F(1,d)})),answer:key(1,N)}}
  if(a===3){ // grade 3: fractions as unit fractions put together, denominators up to 12
    const N=U.pick(r,[2,3,4,5,6,8,10,12]),K=U.ri(r,1,N-1);
    if(i%3===2){const d1=U.pick(r,[2,3,4,5,6,8]),d2=U.pick(r,[2,3,4,5,6,8].filter(d=>d!==d1)),big=Math.min(d1,d2);
      return{type:"pick",cols:2,say:"Which is bigger: one "+d1+"th or one "+d2+"th? Look at the slices!",prompt:'<span class="ask">Which is bigger?</span>',
        options:[{key:key(1,d1),html:U.pizza(d1,1)+F(1,d1)},{key:key(1,d2),html:U.pizza(d2,1)+F(1,d2)}],answer:key(1,big)}}
    const o=new Map([[key(K,N),F(K,N)]]);for(const[x,y]of U.shuffle(r,[[N-K,N],[K,N+1],[K+1,N],[1,N],[K,N*2]]))if(o.size<4&&x>0&&x<y&&!o.has(key(x,y)))o.set(key(x,y),F(x,y));
    return{type:"pick",say:"What fraction of the pizza is coloured?",prompt:'<span class="ask">What fraction is coloured?</span>'+U.pizza(N,K),
      options:U.shuffle(r,[...o].map(([k,h])=>({key:k,html:h}))),answer:key(K,N)}}
  // grade 4+: equivalent fractions
  const[x,y]=U.pick(r,[[1,2],[1,3],[2,3],[1,4],[3,4],[2,5]]),m=U.ri(r,2,4),o=new Map([[key(x*m,y*m),F(x*m,y*m)]]);
  for(const[p,q]of U.shuffle(r,[[x*m+1,y*m],[x+m,y+m],[x*m,y*m+1],[y,x*m+y],[x*m-1,y*m]]))if(o.size<4&&p>0&&p<q&&p*y!==q*x&&!o.has(key(p,q)))o.set(key(p,q),F(p,q));
  return{type:"pick",say:"Which fraction is the same as "+x+" over "+y+"?",prompt:'<span class="ask">Which is the same as</span>'+F(x,y)+U.pizza(y,x),
    options:U.shuffle(r,[...o].map(([k,h])=>({key:k,html:h}))),answer:key(x*m,y*m)}}''', [2,7])

G["money"] = ("Money Shop", [["🪙","Canadian coins: nickel 5¢, dime 10¢, quarter 25¢, loonie $1, toonie $2."],["🧮","Count the coins to find how much money."],["🛒","Some rounds: tap coins to pay exactly the price."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const NM={5:"nickels",10:"dimes",25:"quarters",100:"loonies",200:"toonies"},row=vs=>'<span class="lr-coins">'+vs.map(U.coin).join("")+"</span>";
  const opts=(t,step)=>{const o=new Set([t]);for(const d of U.shuffle(r,[step,-step,5,-5,10,2*step]))if(o.size<4&&t+d>0)o.add(t+d);return U.shuffle(r,[...o]).map(v=>({key:v,html:U.cents(v)}))};
  if(a<=2){ // grade 2: skip counting with coins of one kind
    const k=U.pick(r,n<=15?[10,5]:[10,5,25]),c=U.ri(r,2,k===25?4:n<=15?6:9);
    return{type:"pick",say:"Count the "+NM[k]+". How much money?",prompt:'<span class="ask">How much money?</span>'+row(Array(c).fill(k)),options:opts(k*c,k),answer:k*c}}
  if(a===3){ // grade 3: counting mixed coins, paying exact amounts
    if(i%2===0){const vs=Array.from({length:U.ri(r,3,6)},()=>U.pick(r,n>20?[100,25,25,10,10,5]:[25,25,10,10,5])).sort((x,y)=>y-x),t=vs.reduce((x,y)=>x+y,0);
      return{type:"pick",say:"How much money is there? Start with the biggest coins.",prompt:'<span class="ask">How much money?</span>'+row(vs),options:opts(t,5),answer:t}}
    const sol=Array.from({length:U.ri(r,2,4)},()=>U.pick(r,n>20?[100,25,10,5]:[25,10,5])),price=sol.reduce((x,y)=>x+y,0),extra=U.sample(r,[25,10,5,25,10,100],3);
    const cells=U.shuffle(r,sol.map(v=>({v,s:1})).concat(extra.map(v=>({v,s:0}))));
    return{type:"combo",target:price,fmt:U.cents,say:"Tap coins to pay exactly "+U.cents(price).replace("¢"," cents")+".",prompt:'<span class="ask">Pay exactly</span><span class="big l">'+U.cents(price)+"</span>",
      cells:cells.map(c=>({v:c.v,html:U.coin(c.v),aria:U.cents(c.v)})),solution:cells.map((c,k)=>c.s?k:-1).filter(k=>k>=0)}}
  // grade 4+: making change
  const paid=U.pick(r,[100,200,500,1000]),cost=5*U.ri(r,3,paid/5-1),ch=paid-cost,o=new Set([ch]);
  for(const d of U.shuffle(r,[5,-5,10,-10,25,-25,100]))if(o.size<4&&ch+d>0)o.add(ch+d);
  return{type:"pick",say:"A toy costs "+U.cents(cost)+". You pay "+U.cents(paid)+". How much change do you get?",
    prompt:'<span class="ask">🧸 costs '+U.cents(cost)+". You pay "+U.cents(paid)+". Change?</span>",options:U.shuffle(r,[...o]).map(v=>({key:v,html:U.cents(v)})),answer:ch}}''', [3,7])

G["clock"] = ("Clock & Calendar", [["📅","Days, months, and how long things take."],["🕒","Later: read the clock. The short hand shows the hour, the long red hand shows minutes."],["👆","Tap the right answer, or tap things in order."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const D=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],M=["January","February","March","April","May","June","July","August","September","October","November","December"];
  if(a<=1){ // grade 1: days of the week and months of the year
    if(i%2===0){const L=n>20&&i%4===2?M:D,len=L===M?U.ri(r,4,6):(n<=12?7:U.ri(r,4,5)),s=L===D&&n<=12?0:U.ri(r,0,L.length-1),seq=Array.from({length:len},(_,k)=>L[(s+k)%L.length]);
      return{type:"order",wide:true,say:"Put the "+(L===M?"months":"days")+" in order.",prompt:'<span class="ask">Put the '+(L===M?"months":"days")+" in order</span>",
        tiles:U.mix(r,seq).map(x=>({key:x,html:x,say:x})),answer:seq}}
    const L=n>20?U.pick(r,[D,M]):D,k=U.ri(r,0,L.length-1),before=n>15&&i%3===1,ans=L[(k+(before?-1:1)+L.length)%L.length];
    const o=new Set([ans]);while(o.size<4)o.add(U.pick(r,L.filter(x=>x!==L[k])));
    return{type:"pick",cols:2,say:"What "+(L===M?"month":"day")+" comes "+(before?"before ":"after ")+L[k]+"?",prompt:'<span class="ask">What comes '+(before?"before":"after")+'</span><span class="word">'+L[k]+"</span>",
      options:U.shuffle(r,[...o]).map(x=>({key:x,html:'<span style="font-size:22px">'+x+"</span>"})),answer:ans}}
  if(a===2){ // grade 2: duration (longer/shorter) and units of time
    const A=[["Blink","👁️",.2],["Sneeze","🤧",.5],["Tie your shoes","👟",30],["Brush your teeth","🪥",120],["Eat lunch","🥪",1200],["Walk around the block","🚶",900],
      ["Watch a movie","🎬",6000],["A school day","🏫",21600],["Sleep at night","😴",36000],["Summer holidays","🏖️",5e6],["Grow a tree","🌳",3e8],["Bake cookies","🍪",1800]];
    if(i%2===0){let x,y;do{[x,y]=U.sample(r,A,2)}while(Math.max(x[2],y[2])/Math.min(x[2],y[2])<(n>20?4:20));const ans=x[2]>y[2]?x[0]:y[0];
      return{type:"pick",cols:2,say:"Which takes longer?",prompt:'<span class="ask">Which takes longer?</span>',options:[x,y].map(v=>({key:v[0],html:'<span class="act"><b>'+v[1]+"</b>"+v[0]+"</span>"})),answer:ans}}
    const v=U.pick(r,A),u=v[2]<60?"seconds":v[2]<3600?"minutes":v[2]<172800?"hours":"days";
    return{type:"pick",cols:2,say:"How would you measure how long it takes to "+v[0].toLowerCase()+"?",prompt:'<span class="ask">How long? Pick the best unit</span><span class="act"><b>'+v[1]+"</b>"+v[0]+"</span>",
      options:["seconds","minutes","hours","days"].map(x=>({key:x,html:'<span style="font-size:22px">'+x+"</span>"})),answer:u}}
  const t=(h,m)=>h+":"+String(m).padStart(2,"0");
  if(a===3){ // grade 3: read analog and digital clocks
    const h=U.ri(r,1,12),m=n<=12?U.pick(r,[0,30]):5*U.ri(r,0,11),ans=t(h,m),o=new Set([ans]);
    for(const c of U.shuffle(r,[t(m===0?12:Math.max(1,m/5),h*5%60),t(h%12+1,m),t(h,(m+30)%60),t(h===1?12:h-1,m),t(h,(m+5)%60)]))if(o.size<4)o.add(c);
    if(i%3===2){const arr=[...o];return{type:"pick",cols:2,say:"Which clock shows "+ans+"?",prompt:'<span class="ask">Which clock shows</span><span class="big l">'+ans+"</span>",
      options:U.shuffle(r,arr).map(x=>{const[hh,mm]=x.split(":").map(Number);return{key:x,html:U.clock(hh,mm),aria:x}}),answer:ans}}
    return{type:"pick",cols:2,say:"What time is it?",prompt:'<span class="ask">What time is it?</span>'+U.clock(h,m),options:U.shuffle(r,[...o]).map(x=>({key:x,html:x})),answer:ans}}
  // grade 4+: quarter past / to, and how long between times
  if(i%2===0){const h=U.ri(r,1,12),m=U.pick(r,[0,15,30,45]),nx=h%12+1,W={0:h+" o'clock",15:"quarter past "+h,30:"half past "+h,45:"quarter to "+nx},ans=W[m];
    return{type:"pick",cols:2,say:"What time is it? Use words.",prompt:'<span class="ask">What time is it?</span>'+U.clock(h,m),
      options:U.shuffle(r,[0,15,30,45].map(k=>({key:W[k],html:'<span style="font-size:20px">'+W[k]+"</span>"}))),answer:ans}}
  const h=U.ri(r,1,10),m=5*U.ri(r,0,9),d=5*U.ri(r,2,n>20?20:11),e=h*60+m+d,o=new Set([d]);for(const x of U.shuffle(r,[d+5,d-5,d+10,d+15,60-d]))if(o.size<4&&x>0)o.add(x);
  return{type:"pick",say:"How many minutes from "+t(h,m)+" to "+t(Math.floor(e/60),e%60)+"?",prompt:'<span class="ask">How many minutes from '+t(h,m)+" to "+t(Math.floor(e/60),e%60)+"?</span>",
    options:U.shuffle(r,[...o]).map(v=>({key:v,html:String(v)})),answer:d}}''', [2,7])

G["numberline"] = ("Number Line Jump", [["🐸","The frog starts at the green dot."],["↪️","It jumps forward (+) or back (−)."],["👆","Tap where the frog lands."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){let lo=0,hi,tick,label,unit,fmt=v=>String(v),s,j;
  if(a<=0){ // research (Siegler & Ramani): a 1-10 number TRACK and a dot die build number sense before number lines
    const s0=U.ri(r,1,n<=12?4:6),roll=U.ri(r,1,Math.min(4,10-s0)),e0=s0+roll,o=U.near(r,e0,3,1,10,1);
    const track='<span class="lr-track">'+Array.from({length:10},(_,k)=>'<i class="'+(k+1===s0?"me":"")+'">'+(k+1===s0?"🐸":k+1)+"</i>").join("")+"</span>";
    return{type:"pick",say:"The frog is on "+s0+". It rolls "+roll+". Hop "+roll+" squares. Where does it land?",
      prompt:'<span class="ask">🐸 is on '+s0+". Roll: </span>"+U.numdots(roll).replace("<b>"+roll+"</b>","")+track,options:o.map(v=>({key:v,html:String(v),say:String(v)})),answer:e0}}
  else if(a===1){hi=20;tick=1;label=5;s=U.ri(r,0,15);j=U.ri(r,1,Math.min(9,20-s));if(n>10&&i%2===1){s=U.ri(r,6,20);j=-U.ri(r,1,Math.min(9,s))}} // grade 1: within 20
  else if(a===2){hi=100;tick=10;label=20;s=10*U.ri(r,0,7);j=10*U.ri(r,1,10-s/10);if(n>12&&i%2===1){s=10*U.ri(r,3,10);j=-10*U.ri(r,1,s/10)}} // grade 2: tens to 100
  else if(a===3){hi=1000;tick=100;label=200;s=100*U.ri(r,0,7);j=100*U.ri(r,1,10-s/100);if(i%2===1){s=100*U.ri(r,3,10);j=-100*U.ri(r,1,s/100)}} // grade 3: hundreds to 1000
  else{hi=20;tick=1;label=5;fmt=v=>(v/10).toFixed(1).replace(/\.0$/,"");s=U.ri(r,0,12);j=U.ri(r,1,8);if(i%2===1){s=U.ri(r,8,20);j=-U.ri(r,1,8)}}       // grade 4+: tenths
  const e=s+j,o=new Set([e]);for(const d of U.shuffle(r,[tick,-tick,2*tick,-2*tick,-2*j]))if(o.size<4&&e+d>=lo&&e+d<=hi)o.add(e+d);
  const js=(j>0?"+":"−")+fmt(Math.abs(j));
  return{type:"pick",say:"Start at "+fmt(s)+". Jump "+(j>0?"forward ":"back ")+fmt(Math.abs(j))+". Where do you land?",
    prompt:'<span class="ask">Start at '+fmt(s)+", jump "+js+". Where do you land?</span>"+U.numberline(lo,hi,tick,label,s,e,fmt),
    options:U.shuffle(r,[...o]).map(v=>({key:v,html:fmt(v)})),answer:e}}''', [1,6])

G["patterns"] = ("Pattern Next", [["🔁","Patterns repeat or grow in a special way."],["👀","Look for the part that repeats."],["👆","Copy it, finish it, or find the part that repeats."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const SETS=[["🔴","🔵","🟡","🟢"],["🐶","🐱","🐭","🐰"],["⭐","🌙","☀️","☁️"],["🍎","🍌","🍇","🍓"],["🔺","🟦","🟣","🔶"]].concat(U.fav([]).length?[U.fav([]).slice(0,4),U.fav([]).slice(4,8)]:[]);
  const seqHtml=(xs,q)=>'<span class="ask">'+(q||"What comes next?")+'</span><span class="seq">'+xs.map(x=>"<b"+(String(x).length>2?' class="sm"':"")+">"+x+"</b>").join("")+(q?"":'<b class="q">?</b>')+"</span>";
  if(a<=1){ /* Research (Vanderbilt patterning study): copy is easiest, then extend, then rebuild with new things, then "which part repeats?" (hardest).
       Always show at least 2 full repeats; pre-K uses AB only. */
    const cores=a<0?["AB"]:a===0?["AB","AAB","ABC","ABB"]:["ABC","AABB","ABCD","ABBC","AAB"],core=U.pick(r,cores),set=U.shuffle(r,U.pick(r,SETS)),L=core.length;
    const len=Math.max(L*2,a<0?4:6)+U.ri(r,0,L-1),xs=Array.from({length:len},(_,k)=>set["ABCD".indexOf(core[k%L])]),ans=set["ABCD".indexOf(core[len%L])];
    const kinds=a<0?(n<=6?["copy","copy","next"]:["copy","next","next"]):a===0?["copy","next","next","rebuild"]:["next","rebuild","unit","next"],kind=kinds[i%kinds.length];
    if(kind==="copy"){const row=xs.slice(0,Math.min(len,L*2));
      return{type:"order",say:"Copy the pattern! Tap the pictures in the same order.",prompt:seqHtml(row,"Copy the pattern"),tiles:U.mix(r,row.map((x,k)=>({key:"c"+k,val:x,html:x}))),answer:row}}
    if(kind==="rebuild"){const other=U.shuffle(r,U.pick(r,SETS.filter(s=>!s.includes(set[0]))));
      const mk=c=>Array.from({length:L*2},(_,k)=>other["ABCD".indexOf(c[k%c.length])]).join(" "),wrong=U.shuffle(r,["AB","AAB","ABB","ABC","AABB"].filter(c=>c!==core)).slice(0,2);
      return{type:"pick",cols:1,say:"Which row has the same pattern, made with different things?",prompt:seqHtml(xs.slice(0,L*2),"Which row has the same pattern?"),
        options:U.shuffle(r,[core].concat(wrong)).map(c=>({key:c,html:'<span style="font-size:.6em;letter-spacing:4px">'+mk(c)+"</span>"})),answer:core}}
    if(kind==="unit"){const unit=core.split("").map(c=>set["ABCD".indexOf(c)]).join(""),wrongs=new Set();
      for(const c of U.shuffle(r,[core.slice(0,-1),core+core[0],core.split("").reverse().join(""),core.slice(1)+core[0]])){const w=c.split("").map(x=>set["ABCD".indexOf(x)]).join("");if(c.length>=2&&w!==unit&&wrongs.size<2)wrongs.add(w)}
      return{type:"pick",cols:1,say:"Which part repeats over and over?",prompt:seqHtml(xs,"Which part repeats?"),options:U.shuffle(r,[unit].concat([...wrongs])).map(u=>({key:u,html:'<span style="letter-spacing:4px">'+u+"</span>"})),answer:unit}}
    const used=[...new Set(core)].map(c=>set["ABCD".indexOf(c)]),o=new Set([ans]);for(const x of U.shuffle(r,used.concat(set)))if(o.size<(a<0?2:3))o.add(x);
    return{type:"pick",say:"What comes next in the pattern?",prompt:seqHtml(xs),options:U.shuffle(r,[...o]).map(x=>({key:x,html:x})),answer:ans}}
  let xs,ans;
  if(a===2){const st=U.pick(r,[2,5,10,3,4]),down=n>15&&i%2===1,s=down?U.ri(r,st*5,60):U.ri(r,0,20);xs=Array.from({length:5},(_,k)=>s+(down?-1:1)*st*k);ans=s+(down?-1:1)*st*5}  // grade 2: increasing/decreasing
  else if(a===3){const kind=i%3;if(kind===0){const s=U.ri(r,1,5);xs=[s,s*2,s*4,s*8];ans=s*16}else if(kind===1){const st=U.pick(r,[25,50,100]);const s=st*U.ri(r,0,4);xs=[0,1,2,3,4].map(k=>s+st*k);ans=s+st*5}
    else{const s=U.pick(r,[1000,2000,5000]);xs=[s,s/2,s/4];ans=s/8}}                                                                  // grade 3: x2, /2, skip counting
  else{const kind=U.ri(r,0,3);if(kind===0){xs=[1,4,9,16];ans=25}else if(kind===1){xs=[1,3,6,10];ans=15}else if(kind===2){const s=U.ri(r,1,3);xs=[s,s,2*s,3*s,5*s];ans=8*s}
    else{const s=U.ri(r,1,10);xs=[s,s+1,s+3,s+6];ans=s+10}}                                                                          // grade 4+: squares, triangular, Fibonacci, growing
  const o=new Set([ans]);for(const d of U.shuffle(r,[1,-1,2,-2,5,10,-10]))if(o.size<4&&ans+d>=0)o.add(ans+d);
  return{type:"pick",say:"What number comes next?",prompt:seqHtml(xs),options:U.shuffle(r,[...o]).map(v=>({key:v,html:String(v)})),answer:ans}}''', [0,7])

for gid,(name,howto,body,grades) in G.items():
    (SRC / f"{gid}.html").write_text(f'''<!DOCTYPE html>
<html lang="en">
<head>
<!--HEAD:{name}-->
</head>
<body>
<!--KIT-->
<!--LEARN-->
<script>
(()=>{{const U=TS_LEARN.util;
TS_LEARN({{id:{json.dumps(gid)},name:{json.dumps(name)},howto:{json.dumps(howto,ensure_ascii=False)},
{body}}});
}})();
</script>
</body>
</html>
''')
print(len(G), "games written:", ", ".join(f"{k} (grades {v[3][0]}-{v[3][1]})" for k,v in G.items()))
