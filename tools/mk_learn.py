import pathlib, json
SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
G = {}

G["abc"] = ("My ABCs", [["🔤","Each level is a new letter. The letters in YOUR name come first!"],["👂","Meet the letter: hear its name and its sound."],["🔍","Then find it, match big and little, trace it, and hear it in words."],["🎵","Finish by singing the ABC song: tap the glowing letters."]],
r"""rounds:()=>6,adapt:false,
label:n=>{const q=ABC.seq();return n<=26?q[n-1]:"⭐"},
make(n,i,r,a){
  /* Built on research about how young children learn the alphabet:
     letters of the child's own name first, then the rest; one new letter per level with review of earlier ones;
     letter names linked to their sounds and a keyword picture; many kinds of practice; the alphabet song for order. */
  const UP=ABC.UP,SEQ=ABC.seq(),pr=TS.rngFrom(n*7919+(a+2)*104729),review=n>26;
  const L=review?U.pick(r,ABC.HARD):SEQ[n-1],known=review?SEQ:SEQ.slice(0,n-1);
  // the plan for this level: meet (new letters only), then a mix, then the song
  const mix=["find","hunt","sound","match","trace"].concat(a>=0?["next"]:[]).filter(k=>!(k==="match"&&a<0&&n<6)&&!(k==="sound"&&L==="X"));
  const pickN=(arr,k)=>{const c=arr.slice(),o=[];while(o.length<k&&c.length)o.push(c.splice(Math.floor(pr()*c.length),1)[0]);return o};
  // four practice rounds in a different mix and order each level (always including "find")
  const mid=["find"].concat(pickN(mix.filter(k=>k!=="find"),3));for(let k=mid.length-1;k>0;k--){const j=Math.floor(pr()*(k+1));[mid[k],mid[j]]=[mid[j],mid[k]]}
  const plan=review?pickN(["find","hunt","match","sound","trace"].concat(a>=0?["next"]:[]),5).concat(["sing"]):["meet"].concat(mid,["sing"]);
  while(plan.length<6)plan.splice(plan.length-1,0,"find");
  const kind=plan[i];
  // a review round now and then: practise a letter learned earlier
  const T=(kind==="find"||kind==="hunt")&&i>=3&&known.length>=2?U.pick(r,known.slice(-4)):L;
  const t=T.toLowerCase(),[word,pic]=ABC.word(T,r),snd=ABC.SND[T],lowCase=a>=0&&r()<.5;
  const others=(k,avoid)=>{const pool=(known.length>=k?known:UP.split("")).filter(c=>c!==T&&!(avoid||[]).includes(c));
    const extra=a>=1?ABC.CONF[T]||[]:[];const out=U.shuffle(r,extra.filter(c=>c!==T)).slice(0,1);
    for(const c of U.shuffle(r,pool.concat(UP.split("").filter(c=>!pool.includes(c)))))if(out.length<k&&c!==T&&!out.includes(c))out.push(c);return out};
  const big=(c,low)=>'<span style="font-family:var(--font-kid)">'+(low?c.toLowerCase():c)+"</span>";
  if(kind==="meet")return{type:"meet",up:T,low:t,pic,word,say:"This is the letter "+T+". "+T+" says "+snd+", like "+word+"! Tap it.",tapSay:T+". "+snd+". "+word+"!",
    prompt:'<span class="ask">Meet the letter '+T+"!</span>",text:"Tap the big letter to hear it."};
  if(kind==="find"){const k=a<0?3:4,opts=[T].concat(others(k-1));
    return{type:"pick",cols:k,say:"Which one is "+(lowCase?"little ":"")+T+"?",prompt:'<span class="ask">Which one is '+(lowCase?"little ":"")+T+"?</span>",
      options:U.shuffle(r,opts).map(c=>({key:c,html:big(c,lowCase),say:c})),answer:T}}
  if(kind==="hunt"){const cols=4,cnt=a<0?8:12,hits=a<0?3:4,dis=others(3);const cells=[];
    for(let k=0;k<hits;k++)cells.push({html:big(T,a>=0&&k%2===1),ok:true,aria:T});
    while(cells.length<cnt){const c=U.pick(r,dis);cells.push({html:big(c,a>=0&&r()<.5),ok:false,aria:c})}
    return{type:"hunt",cols,say:"Find every "+T+(a>=0?", big and little":"")+"!",prompt:'<span class="ask">Find every '+T+(a>=0?" and "+t:"")+"!</span>",cells:U.shuffle(r,cells)}}
  if(kind==="sound"){const k=a<0?3:4,opts=[[word,pic]];for(const c of others(k+2,["X"]))if(opts.length<k){const w=ABC.word(c,r);if(!opts.some(o=>o[0][0]===w[0][0]))opts.push(w)}
    return{type:"pick",cols:2,say:"Which one starts with "+T+"? "+T+" says "+snd+".",prompt:'<span class="ask">Which starts with '+big(T)+"?</span>",
      options:U.shuffle(r,opts).map(([w,e])=>({key:w,html:'<span class="lr-word"><b>'+e+"</b>"+w+"</span>",say:w,aria:w})),answer:word}}
  if(kind==="match"){const k=a<0?3:4,opts=[T].concat(others(k-1));
    return{type:"pick",cols:k,say:"Find little "+T+". It goes with big "+T+".",prompt:'<span class="ask">Which is little '+T+"?</span>"+'<span class="big l">'+T+"</span>",
      options:U.shuffle(r,opts).map(c=>({key:c,html:big(c,true),say:c})),answer:T}}
  if(kind==="trace")return{type:"trace",ch:T,say:"Trace the letter "+T+". Start at the green dot.",prompt:'<span class="ask">Trace the letter '+T+"</span>"};
  if(kind==="next"){const ix=UP.indexOf(T),after=ix<25&&(ix===0||r()<.6),ans=after?UP[ix+1]:UP[ix-1],opts=[ans].concat(U.shuffle(r,UP.split("").filter(c=>c!==ans&&c!==T)).slice(0,3));
    return{type:"pick",cols:4,say:"What comes "+(after?"after ":"before ")+T+"? Sing the ABCs if you need to!",prompt:'<span class="ask">What comes '+(after?"after":"before")+'</span><span class="big l">'+T+"</span>",
      options:U.shuffle(r,opts).map(c=>({key:c,html:big(c),say:c})),answer:ans}}
  // sing: the part of the alphabet song with this letter in it (the whole song for bigger kids and review levels)
  const seg=a>=1||review?[0,26]:ABC.SEGS.find(([s,e])=>UP.indexOf(L)>=s&&UP.indexOf(L)<e),letters=UP.slice(seg[0],seg[1]).split("");
  return{type:"sing",letters,notes:letters.map(c=>ABC.NOTE[UP.indexOf(c)]),say:"Let's sing the ABCs! Tap the glowing letters.",prompt:'<span class="ask">🎵 Sing the ABCs! Tap the glowing letter.</span>'}}
""")

G["missletter"] = ("Missing Letter", [["🔤","Some letters are in ABC order."],["❓","One letter is missing."],["👆","Tap the letter that goes in the box."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const UP="ABCDEFGHIJKLMNOPQRSTUVWXYZ",len=a<0?3:a===0?4:a===1?5:6,lower=(a===1&&n>20)||(a>=2&&n>8),back=a>=2&&n>20&&i%2===1;
  const start=a<0?U.ri(r,0,n<=20?3:8):a===0&&n<=10?U.ri(r,0,6):U.ri(r,0,26-len);let seq=UP.slice(start,start+len).split("");if(back)seq.reverse();
  const hole=a<0||(a===0&&n<=10)?len-1:U.ri(r,1,len-1),ans=seq[hole],idx=UP.indexOf(ans),count=a<0?(n<=15?2:3):a===0?3:4,opts=new Set([ans]);
  for(const d of U.shuffle(r,[-1,1,-2,2,-3,3,4,-4]))if(opts.size<count&&UP[idx+d]&&idx+d>=0)opts.add(UP[idx+d]);
  const c=x=>lower?x.toLowerCase():x;
  return{type:"pick",say:"Which letter is missing?"+(back?" These go backwards!":""),
    prompt:'<span class="ask">Which letter is missing?</span><span class="seq">'+seq.map((x,k)=>k===hole?'<b class="q">?</b>':"<b>"+c(x)+"</b>").join("")+"</span>",
    options:U.shuffle(r,[...opts]).map(x=>({key:c(x),html:c(x),say:c(x)})),answer:c(ans)}}''')

G["case"] = ("Big & Little", [["🅰️","Every big letter has a little letter."],["👀","Look at the letter at the top."],["👆","Tap its matching big or little letter."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const AB="abcdefghijklmnopqrstuvwxyz",EASY="cosuvwxzpk";
  const CONF={b:"dpq",d:"bpq",p:"qbd",q:"pdb",m:"nwu",n:"mhu",u:"nvw",w:"mvu",i:"ljt",l:"ijt",j:"igy",f:"tl",t:"fl",h:"nk",a:"oed",e:"aoc",c:"oe",o:"ce",g:"qy",y:"gv",v:"wy",s:"z",z:"s",k:"hx",r:"nm",x:"kz"};
  const l=U.pick(r,(a<0||(a===0&&n<=10)?EASY:AB).split("")),toLower=a<0?true:a===0?(n<=20||i%2===0):i%2===0,count=a<0?(n<=15?2:3):a===0?3:a===1?4:5,opts=new Set([l]);
  if(a>=2||n>25)for(const c of U.shuffle(r,(CONF[l]||"").split("")))if(opts.size<count)opts.add(c);
  while(opts.size<count)opts.add(U.pick(r,AB.split("")));
  const show=toLower?l.toUpperCase():l,f=x=>toLower?x:x.toUpperCase();
  return{type:"pick",say:toLower?"Find the little letter that matches big "+l.toUpperCase()+".":"Find the big letter that matches little "+l+".",
    prompt:'<span class="ask">'+(toLower?"Find the little letter":"Find the big letter")+'</span><span class="big l">'+show+"</span>",
    options:U.shuffle(r,[...opts]).map(x=>({key:f(x),html:f(x)})),answer:f(l)}}''')

G["sound"] = ("First Sound", [["🖼️","Look at the picture and listen to the word."],["👂","What sound does it start with?"],["👆","Tap the letter it starts with."],["🔊","Tap the speaker to hear the word again."]],
r'''make(n,i,r,a){const W=("apple🍎 ant🐜 alligator🐊|ball⚽ bee🐝 bear🐻 banana🍌 bus🚌|cat🐱 car🚗 cake🎂 cow🐮 cup☕ carrot🥕|dog🐶 duck🦆 drum🥁 dinosaur🦕 door🚪|"+
    "egg🥚 elephant🐘 elf🧝|fish🐟 fox🦊 frog🐸 fire🔥 feather🪶|goat🐐 gift🎁 guitar🎸 grapes🍇 gorilla🦍|hat🎩 horse🐴 house🏠 heart❤️ hen🐔|iguana🦎 insect🐞|"+
    "juice🧃 jellyfish🪼 jet✈️ jeans👖|kite🪁 key🔑 koala🐨 kangaroo🦘 king🤴|lion🦁 leaf🍃 lemon🍋 lamp💡 ladybug🐞|moon🌙 mouse🐭 monkey🐵 milk🥛 map🗺️|"+
    "nest🪺 nose👃 nut🥜 net🥅|octopus🐙 otter🦦 ox🐂|pig🐷 pizza🍕 panda🐼 pear🍐 penguin🐧|queen👸|rabbit🐰 rocket🚀 rainbow🌈 robot🤖 ring💍|"+
    "sun☀️ snake🐍 sock🧦 star⭐ seal🦭|tiger🐯 tree🌳 turtle🐢 train🚆 tooth🦷|umbrella☂️ up⬆️|van🚐 violin🎻 volcano🌋|whale🐳 watermelon🍉 web🕸️ worm🪱 watch⌚|"+
    "yo-yo🪀 yarn🧶|zebra🦓 zero0️⃣").split("|").map(g=>g.split(" ").map(s=>{const m=s.match(/^([a-z-]+)(.+)$/);return{w:m[1],e:m[2]}}));
  const DG=[["sh","sheep🐑 shell🐚 shoe👟 ship🚢 shark🦈"],["ch","chick🐤 cheese🧀 cherry🍒 chair🪑"],["th","thumb👍 three3️⃣ thread🧵"]];
  if(a>=1&&n>20&&i%2===1){const[d,ws]=U.pick(r,DG),word=U.pick(r,ws.split(" ")).match(/^([a-z]+)(.+)$/),opts=[d,...DG.map(x=>x[0]).filter(x=>x!==d),d[0]];
    return{type:"pick",say:word[1]+". What sound does "+word[1]+" start with?",prompt:'<span class="big">'+word[2]+"</span>",options:U.shuffle(r,opts).map(x=>({key:x,html:x})),answer:d}}
  // research: for pre-K/K avoid words whose first sound isn't the letter's usual sound and words starting with two consonants (blends)
  const easy="smtapbcdfln",young=a<=0,okWord=x=>!young||(/^[a-z][aeiouy]/.test(x.w)&&!["circle","giraffe","eagle","ocean","ox","iguana"].includes(x.w));
  const pool=W.map(g=>g.filter(okWord)).filter(g=>g.length&&(a>0||(a===0&&n>15)||easy.includes(g[0].w[0]))),word=U.pick(r,U.pick(r,pool)),l=word.w[0];
  const count=a<0?(n<=15?2:3):a===0?3:4,lower=a>=2||(a===1&&n>20),letters="abcdefghijklmnopqrstuvwyz".split("").filter(x=>x!==l&&!(l==="c"&&x==="k")&&!(l==="k"&&x==="c")),opts=[l,...U.sample(r,letters,count-1)];
  const f=x=>lower?x:x.toUpperCase(),blank=a>=2||(a===1&&n>25);
  return{type:"pick",say:word.w.replace("-"," ")+". What sound does "+word.w.replace("-"," ")+" start with?",
    prompt:'<span class="big">'+word.e+"</span>"+(blank?'<span class="word">_'+word.w.slice(1)+"</span>":""),
    options:U.shuffle(r,opts).map(x=>({key:f(x),html:f(x)})),answer:f(l)}}''')

G["trace"] = ("Trace a Letter", [["👀","First watch how the letter is made."],["🟢","Put your finger on the green dot and follow the line."],["🌫️","Then the line fades... and then you write it from memory!"],["🔢","Some letters have more than one line: follow the numbers."]],
r'''rounds:()=>3,label:n=>{const c=TRACE_ORDER(n);return c},
make(n,i,r,a){
  /* Research (Zemlock et al.; handwriting studies): writing a letter by hand helps recognise it more than looking at it. Each level is ONE
     letter (so b and d are never mixed in one session): watch + trace, trace a faded line, then write it from memory. */
  const ch=TRACE_ORDER(n,a),num=/\d/.test(ch),mode=["guided","fade","memory"][i]||"memory",w=num?"number":"letter";
  const say=mode==="guided"?"Watch, then trace the "+w+" "+ch+". Start at the green dot.":mode==="fade"?"Now the line is faint. Trace "+ch+" again.":"Now write "+ch+" from memory! Start at the green dot.";
  return{type:"trace",ch,mode,say,prompt:'<span class="ask">'+(mode==="memory"?"Write "+ch+" from memory":mode==="fade"?"Trace "+ch+" again":"Watch, then trace "+ch)+"</span>"}}''')

G["count"] = ("Count It", [["🍎","Look at the pictures."],["☝️","Count them one at a time."],["👆","Tap the number that says how many. Then we count them together!"],["🧺","Some rounds ask you to put a number of things in the basket."]],
r'''make(n,i,r,a){
  /* Research (Clements & Sarama counting trajectory): a line of 1-5, then scattered 1-5, then 6-10; count along after each answer
     so the last number counted = how many (cardinality); "make N" rounds count out a set. Pre-K numerals come with dots. */
  const EM=[["🍎","apples"],["⭐","stars"],["🐟","fish"],["🎈","balloons"],["🐞","ladybugs"],["🍪","cookies"],["🌸","flowers"],["🚗","cars"],["🦆","ducks"],["🍓","strawberries"],["🐸","frogs"],["⚽","balls"]];
  const[em,name]=U.pick(r,U.fav(EM));let N,pic,opts;
  if((a<0&&n>8&&i%3===2)||(a===0&&i%3===2)){const t=a<0?U.ri(r,2,5):U.ri(r,4,10);
    return{type:"fill",size:a<0?5:10,target:t,em,say:"Put "+t+" "+name+" in the basket. Count as you tap!",prompt:'<span class="ask">🧺 Put <b>'+t+"</b> "+name+" in the basket</span>"}}
  if(a<0){const max=n<=10?3:5;N=U.ri(r,1,max);pic=n<=6?U.cluster(em,N,N):U.scatter(r,em,N);opts=U.near(r,N,n<=10?2:3,1,Math.max(max,3),2)}
  else if(a===0){const max=n<=10?5:n<=25?8:10;N=U.ri(r,1,max);pic=n<=5?U.cluster(em,N,Math.min(N,5)):U.scatter(r,em,N);opts=U.near(r,N,3,1,Math.max(max,4),2)}
  else if(a===1&&n<=25){const max=n<=10?12:20;N=U.ri(r,n<=10?3:6,max);pic=U.cluster(em,N,N>10?10:5,true);opts=U.near(r,N,4,1,25,3)}
  else{N=a===1?U.ri(r,20,59):U.ri(r,n<=10?10:21,n<=10?49:99);pic=U.tens(N);const s=new Set([N]);for(const d of U.shuffle(r,[10,-10,1,-1,11,-9]))if(s.size<4&&N+d>0)s.add(N+d);opts=U.shuffle(r,[...s])}
  return{type:"pick",countAlong:a<=0&&N<=10,say:a<=0?"Count the "+name+". How many are there?":N<=20?"How many "+name+" are there?":"Count the tens and ones. How many blocks?",
    prompt:'<span class="ask">'+(N>20?"Tens and ones: how many?":"How many?")+"</span>"+pic,
    options:opts.map(v=>({key:v,html:a<0?U.numdots(v):String(v),say:String(v)})),answer:N}}''')

G["numorder"] = ("Number Order", [["🔢","Numbers are mixed up."],["👆","Tap them in order, smallest first."],["⬇️","Later, some rounds go from biggest to smallest. Listen!"],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const range=(s,len,step)=>Array.from({length:len},(_,k)=>s+k*step);let nums,desc=false;
  if(a<0){const len=n<=15?3:n<=30?4:5;nums=range(1,len,1)}
  else if(a===0){const len=n<=10?3:n<=20?5:U.ri(r,4,5);nums=range(n<=20?1:U.ri(r,1,11-len),len,1)}
  else if(a===1){if(n<=15){const len=U.ri(r,5,6);nums=range(U.ri(r,1,21-len),len,1)}else if(n<=25)nums=range(2*U.ri(r,1,5),5,2);else{const st=U.pick(r,[5,10]);nums=range(st*U.ri(r,1,st===5?14:5),5,st)}}
  else{if(n<=12){const step=U.pick(r,[2,10,25,50]);nums=range(step*U.ri(r,1,step>=25?8:step===10?4:20),6,step)}else nums=U.sample(r,range(n>25?100:1,n>25?999:99,1),U.ri(r,5,6));desc=n>15&&i%2===1}
  const ans=nums.slice().sort((x,y)=>desc?y-x:x-y).map(String);
  return{type:"order",say:desc?"Put the numbers in order from biggest to smallest.":"Put the numbers in order from smallest to biggest.",
    prompt:'<span class="ask">'+(desc?"Biggest to smallest ⬇️":"Smallest to biggest ⬆️")+"</span>",tiles:U.mix(r,ans).map(v=>({key:v,html:v,say:v})),answer:ans}}''')

G["moreless"] = ("More or Less", [["⚖️","Look at the groups."],["👂","Listen: is it asking for the MOST, or the LEAST?"],["🐘","Careful: big pictures don't mean more! Count them."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){
  if(a<=0){ /* Research: big differences first, then close ones; then break the size cue (3 elephants vs 5 mice) and spread-out vs bunched rows;
     K content adds "same" and "enough / not enough" (Alberta KN1.4). */
    const EM=["🍎","⭐","🐟","🎈","🐞","🍪","🦆","🍓"],em=U.pick(r,U.fav(EM));
    if(a===0&&i%4===3){const k=U.ri(r,2,6),h=U.pick(r,[k,k,k-1,k+1].filter(x=>x>=1)),PAIR=U.pick(r,[["🧒","🎩","hats","kids"],["🐶","🦴","bones","dogs"],["🐰","🥕","carrots","bunnies"],["🐝","🌸","flowers","bees"]]);
      const ok=h>=k;return{type:"pick",cols:2,say:"Are there enough "+PAIR[2]+" for all the "+PAIR[3]+"? Match them up!",prompt:'<span class="ask">Enough '+PAIR[2]+" for every one?</span>"+'<span class="lr-rows"><span>'+PAIR[0].repeat(k)+"</span><span>"+PAIR[1].repeat(h)+"</span></span>",
        options:[{key:"yes",html:"👍 Yes",say:"yes"},{key:"no",html:"👎 No",say:"no"}],answer:ok?"yes":"no"}}
    const k=a<0?(n<=4?2:3):(n<=10?3:4),gap=a<0&&n<=10?3:a<0||n<=15?2:1,hi=a<0?7:9;
    let xs;do{xs=Array.from({length:k},()=>U.ri(r,1,hi))}while(xs.some((x,j)=>xs.some((y,m)=>m!==j&&Math.abs(x-y)<gap)));
    const same=a===0&&n>10&&i%5===4;if(same){const v=U.ri(r,2,6);xs=[v,v]}
    const least=(a<0?n>3&&i%3===2:i%2===1),trick=!least&&((a<0&&n>12&&i%3===1)||(a===0&&n>8&&i%3===1)),best=least?Math.min(...xs):Math.max(...xs),two=xs.length===2,w=least?(two?"less":"the least"):(two?"more":"the most");
    // the size trick: the group with fewer things gets the bigger pictures
    const sizeOf=x=>trick?(x===Math.min(...xs)?1.5:.75):1,BIG=["🐘","🐳","🦒","🐻"],SM=["🐭","🐞","🐜","🐣"],tb=U.pick(r,BIG),ts=U.pick(r,SM);
    const pic=(x,j)=>{const e=trick?(x===Math.min(...xs)?tb:ts):em;return'<span style="font-size:'+sizeOf(x)+'em">'+(j%2&&a===0&&n>15?U.scatter(r,e,x):U.cluster(e,x,x>4&&j%2?2:3))+"</span>"};
    const opts=xs.map((x,j)=>({key:"g"+j,html:pic(x,j),aria:x+" pictures"}));if(a===0)opts.push({key:"same",html:"🟰 Same",say:"the same"});
    const ans=same?"same":"g"+xs.indexOf(best);
    return{type:"pick",cols:2,say:(same||a===0&&opts.length>2&&!least?"Which group has "+w+"? Or are they the same?":"Which group has "+w+"?")+(trick?" Count carefully!":""),
      prompt:'<span class="ask">Which group has <b>'+w.replace("the ","")+"</b>"+(two?"":" of all")+"?</span>",options:opts,answer:ans}}
  const k=n>20?3:2,big=i%2===0;let nums;
  if(a===1){const s=new Set(),hi=n>25?100:20;while(s.size<k)s.add(U.ri(r,1,hi));nums=[...s]}
  else if(a>=2&&n>25){const s=new Set(),b=U.ri(r,100,989);s.add(b);while(s.size<k)s.add(Math.max(100,Math.min(999,b+U.pick(r,[-100,100,-10,10,-1,1,90,-90]))));nums=[...s]}
  else{const s=new Set();const b=U.ri(r,12,98);s.add(b);const sw=+(String(b%10)+String(Math.floor(b/10)));if(b%10&&sw!==b&&sw>9)s.add(sw);
    while(s.size<k)s.add(Math.max(10,Math.min(99,b+U.ri(r,-9,9))));nums=[...s].slice(0,k)}
  const ans=big?Math.max(...nums):Math.min(...nums),w=a===1?(big?"bigger":"smaller"):(big?"greater":"less");
  return{type:"pick",cols:k,say:"Which number is "+w+"?",prompt:'<span class="ask">Which number is '+w+"?</span>",
    options:U.shuffle(r,nums).map(v=>({key:v,html:String(v)})),answer:ans}}''')

G["missnum"] = ("Missing Number", [["🔢","The numbers are counting along."],["❓","One number is missing."],["👆","Tap the number that goes in the box."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){let len,step,s,hole,count;
  // research: a gap in the middle is easiest, then "what comes after?", then "what comes before?"
  if(a<0){len=3;step=1;s=U.ri(r,1,3);hole=n<=12?1:n<=25?2:0;count=n<=15?2:3}
  else if(a===0){len=4;step=1;s=U.ri(r,1,7);hole=n<=8?U.ri(r,1,2):n<=18?3:U.ri(r,0,3);count=3}
  else if(a===1){len=5;count=4;if(n<=15){step=1;s=U.ri(r,1,16)}else if(n<=25){step=-1;s=U.ri(r,6,20)}else if(n<=32){step=2;s=2*U.ri(r,0,6)}else{step=U.pick(r,[5,10]);s=step*U.ri(r,1,step===5?15:5)}hole=U.ri(r,1,4)}
  else{len=5;count=4;step=U.pick(r,n<=12?[2,10]:n<=25?[2,10,25,50]:[10,25,50,100]);s=step*U.ri(r,1,step>=100?5:step>=25?10:step===10?40:200);if(n>25&&i%2===1){s+=step*4;step=-step}hole=U.ri(r,1,4)}
  const seq=Array.from({length:len},(_,k)=>s+k*step),ans=seq[hole],m=Math.abs(step),opts=new Set([ans]);
  for(const d of U.shuffle(r,[m,-m,1,-1,2*m,-2*m,2,-2]))if(opts.size<count&&ans+d>=0)opts.add(ans+d);
  return{type:"pick",say:"What number is missing?"+(step<0?" These count backwards!":""),
    prompt:'<span class="ask">What number is missing?</span><span class="seq">'+seq.map((v,k)=>k===hole?'<b class="q">?</b>':"<b"+(String(v).length>2?' class="sm"':"")+">"+v+"</b>").join("")+"</span>",
    options:U.shuffle(r,[...opts]).map(v=>({key:v,html:a<0?U.numdots(v):String(v),say:String(v)})),answer:ans}}''')

G["tenframe"] = ("Ten Frame", [["🔟","A ten frame has 10 boxes."],["👆","Tap boxes to put in dots. Tap again to take one out."],["🧮","Some rounds ask how many dots, or how many more make 10."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const size=a>=2?20:a<0?5:10; // pre-K starts on a five-frame (research: keep the five-structure, fill top row first)
  if(i%2===0){const t=a<0?U.ri(r,1,n<=20?3:5):a===0?(n<=15?U.ri(r,1,5):U.ri(r,3,10)):a===1?U.ri(r,3,10):U.ri(r,11,20);
    return{type:"fill",size,target:t,say:"Show "+t+". Tap the boxes to put in "+t+" dots.",prompt:'<span class="ask">Put in this many dots</span><span class="big l">'+t+"</span>"}}
  if(a<=0){const k=a<0?U.ri(r,1,5):U.ri(r,1,n<=15?6:10);return{type:"pick",say:"How many dots?",prompt:'<span class="ask">How many dots?</span>'+U.frame(k,a<0?5:10),
    options:U.near(r,k,a<0?2:3,a<0?1:0,10,2).map(v=>({key:v,html:a<0?U.numdots(v):String(v),say:String(v)})),answer:k}}
  if(a===1){const k=U.ri(r,1,9);return{type:"pick",say:"How many more dots make 10?",prompt:'<span class="ask">How many more make 10?</span>'+U.frame(k),
    options:U.near(r,10-k,4,0,10,2).map(v=>({key:v,html:String(v)})),answer:10-k}}
  const k=U.ri(r,11,19),more=i%4===1;
  return{type:"pick",say:more?"How many more dots make 20?":"How many dots?",prompt:'<span class="ask">'+(more?"How many more make 20?":"How many dots?")+"</span>"+U.frame(k,20),
    options:U.near(r,more?20-k:k,4,0,20,2).map(v=>({key:v,html:String(v)})),answer:more?20-k:k}}''')

G["shapesort"] = ("Shape Sort", [["🔺","Each shape has a home with its outline."],["👆","Drag a shape to its home, or tap the shape then tap its home."],["🔄","Shapes can be any colour, size, or turned around!"],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const C=U.SHAPE_COLS,NM={circle:"circle",oval:"oval",square:"square",rectangle:"rectangle",triangle:"triangle",star:"star",heart:"heart",diamond:"rhombus",pentagon:"pentagon",hexagon:"hexagon"};
  let kinds,bySides=false;
  if(a<0)kinds=n<=20?["circle","square"]:["circle","square","triangle"];
  else if(a===0)kinds=n<=10?["circle","square"]:n<=25?["circle","square","triangle"]:U.sample(r,["circle","square","triangle","star","heart"],3);
  else if(a===1)kinds=n<=15?U.sample(r,["circle","square","triangle","star","heart"],3):(()=>{const p=U.pick(r,[["square","rectangle"],["circle","oval"]]);
    return p.concat(U.sample(r,["triangle","star","heart"],n>30?2:1))})();
  else if(n<=12)kinds=U.sample(r,["triangle","square","pentagon","hexagon","diamond","rectangle"],4);
  else{bySides=true;kinds=["triangle","square","rectangle","diamond","pentagon","hexagon"]}
  const cnt=a<0?3:a===0?4:a===1?6:7,items=[];
  // research: shapes turned and in different forms from K up (a tilted square is still a square), and colours that don't give the answer away
  const rot=k=>a<0?0:k==="square"||k==="rectangle"?U.pick(r,[0,45,90,30]):U.ri(r,0,359);
  const bkey=k=>bySides?"s"+U.SIDES[k]:k;
  const binsK=bySides?[3,4,5,6].map(s=>"s"+s):kinds;
  // at least one item for each home, then random ones
  const pickKinds=bySides?[...[3,4,5,6].map(s=>U.pick(r,kinds.filter(k=>U.SIDES[k]===s)))]:kinds.slice();
  while(pickKinds.length<cnt)pickKinds.push(U.pick(r,kinds));
  const VAR={triangle:["triangle","tri_tall","tri_right","tri_wide"],rectangle:["rectangle","rect_long"]};
  U.shuffle(r,pickKinds).forEach(k=>items.push({key:bkey(k),html:U.shape(a<0?k:U.pick(r,VAR[k]||[k]),U.pick(r,C),rot(k),.7+.3*r()),aria:NM[k]}));
  const bins=binsK.map(b=>bySides?{key:b,html:'<b class="sides">'+b.slice(1)+"</b>",label:b.slice(1)+" sides"}:{key:b,html:U.shape(b,"#cfd6dd",0,1,true),label:NM[b]});
  return{type:"sort",say:bySides?"Sort the shapes by how many sides they have.":"Put each shape in its home.",
    prompt:'<span class="ask">'+(bySides?"Sort by number of sides":"Put each shape in its home")+"</span>",bins,items}}''')

G["shapehunt"] = ("Shape Hunt", [["🔍","Lots of shapes are mixed up."],["👂","Listen for which shape to find."],["📐","Triangles can be tall, skinny, tipped over or tiny. Careful: some shapes are only ALMOST right!"],["👆","Tap every one of them!"]],
r'''make(n,i,r,a){
  /* Research (Clements & Sarama; shape prototype studies): only 30% of 5-6 year olds accept all kinds of triangles, and few reject "almost" shapes.
     So targets come in many forms and orientations, and from K content up some decoys are near-misses (open, curved sides, a cut corner). */
  const C=U.SHAPE_COLS,PL={circle:"circles",square:"squares",rectangle:"rectangles",triangle:"triangles",star:"stars",heart:"hearts",pentagon:"pentagons",hexagon:"hexagons"};
  const VAR={triangle:["triangle","tri_tall","tri_right","tri_wide"],square:["square"],circle:["circle"],rectangle:["rectangle","rect_long"],star:["star"],heart:["heart"],pentagon:["pentagon"],hexagon:["hexagon"]};
  const NEAR={triangle:[["open_tri","not a triangle: it's open"],["curvy_tri","not a triangle: its sides are curved"],["cut_tri","not a triangle: it has 4 sides"]],
    square:[["rectangle","a rectangle: its sides aren't all the same"],["rhombus","not a square: its corners aren't square"]],circle:[["oval","an oval, not a circle"]],rectangle:[["square","a square"]]};
  let cols,rows,kinds,bySides=false;
  if(a<0){cols=3;rows=2;kinds=["circle","square","triangle"]}
  else if(a===0){cols=3;rows=n<=15?3:4;kinds=n<=15?["circle","square","triangle"]:["circle","square","triangle","star","heart"]}
  else if(a===1){cols=4;rows=4;kinds=["circle","square","triangle","rectangle","star","heart"]}
  else{cols=4;rows=5;kinds=["triangle","square","rectangle","pentagon","hexagon","circle"];bySides=n>15}
  const N=cols*rows,turn=()=>a<0?U.pick(r,[0,0,180]):U.ri(r,0,359);
  const BASE={tri_tall:"triangle",tri_right:"triangle",tri_wide:"triangle",rect_long:"rectangle"};
  const cell=(k,ok,why)=>({html:U.shape(k,U.pick(r,C),turn(),.6+.4*r()),ok,aria:ok||!/_|rhombus/.test(k)?BASE[k]||k:"shape",why});let cells=[],say,ask;
  if(bySides){const s=U.pick(r,[3,4,5,6]),T=U.ri(r,3,6),yes=kinds.filter(k=>U.SIDES[k]===s),no=kinds.filter(k=>U.SIDES[k]!==s);
    for(let k=0;k<N;k++){const ok=k<T;const kk=U.pick(r,ok?yes:no);cells.push(cell(ok?U.pick(r,VAR[kk]||[kk]):kk,ok,ok?"":"a shape with "+(U.SIDES[kk]||"no")+" sides"))}
    say="Tap all the shapes with "+s+" sides.";ask="Tap all shapes with "+s+" sides"}
  else{const t=a<0?U.pick(r,kinds):U.pick(r,kinds.filter(k=>NEAR[k]||r()<.3)),T=a<0?2:U.ri(r,2,Math.min(5,Math.floor(N/3))),others=kinds.filter(k=>k!==t);
    const near=a<0?[]:(NEAR[t]||[]),nNear=Math.min(near.length,a===0?1:2);
    for(let k=0;k<N;k++){if(k<T)cells.push(cell(a<0?t:U.pick(r,VAR[t]||[t]),true));
      else if(k<T+nNear){const[nk,why]=near[k-T];cells.push(cell(nk,false,why))}
      else{const o=U.pick(r,others);cells.push(cell(o,false,"a "+o))}}
    say="Tap all the "+PL[t]+"."+(nNear?" Careful, some are only almost "+PL[t]+"!":"");ask="Tap all the "+PL[t]+" "+U.shape(t,"#9aa3ad").replace('class="lr-shp"','class="lr-shp ic"')}
  return{type:"hunt",cols,say,prompt:'<span class="ask">'+ask+"</span>",cells:U.shuffle(r,cells)}}''')

G["colours"] = ("Colour Match", [["🎨","Each round is about colours."],["👆","Tap the right colour, or sort shapes into the basket of the same colour."],["📖","Later you read the colour word yourself!"],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const COL=U.COLOURS,K=["circle","square","triangle","star","heart","diamond"];
  // research: colour words come slowly and brown, grey, pink and purple come last, so they get extra turns once they're in
  const LATE=["brown","grey","pink","purple"],base=a<0?["red","blue","yellow","green"].slice(0,n<=15?3:4):a===0?(n<=12?["red","blue","green","yellow"]:["red","blue","green","yellow","orange","pink","purple"]):a===1?["red","blue","green","yellow","orange","purple","pink","brown","grey"]:Object.keys(COL);
  const NAMES=base.concat(base.filter(c=>LATE.includes(c)));
  if(a<0||(a===0&&n<=15)||i%2===0){const cs=U.sample(r,[...new Set(U.shuffle(r,NAMES))],a<0?(n<=15?2:3):a===0?3:4),t=cs[0],stroop=a>=2&&n>20,ink=stroop?U.pick(r,cs.slice(1)):null;
    const prompt=a<=0?'<span class="ask">Tap the '+t+" one</span>":'<span class="ask">'+(stroop?"Tap the colour the word SAYS":"Read the word. Tap that colour.")+'</span><span class="word" style="color:'+(stroop?COL[ink]:"#e9edf1")+'">'+t.toUpperCase()+"</span>";
    return{type:"pick",say:a<=0?"Tap the "+t+" one.":stroop?"Tap the colour the word says, not the colour of the letters.":"Read the colour word, then tap that colour.",prompt,
      options:U.shuffle(r,cs).map(c=>({key:c,html:U.shape(U.pick(r,K),COL[c]),aria:c,say:c})),answer:t}}
  const bins=U.sample(r,[...new Set(U.shuffle(r,NAMES))],a<=0?2:a===1?3:4),cnt=a<=0?4:6,items=[];
  const order=bins.slice();while(order.length<cnt)order.push(U.pick(r,bins));
  U.shuffle(r,order).forEach(c=>items.push({key:c,html:U.shape(U.pick(r,K),COL[c],0,.75+.25*r()),aria:c}));
  return{type:"sort",say:"Put each shape in the basket with the same colour.",prompt:'<span class="ask">Match the colours</span>',
    bins:bins.map(c=>({key:c,html:'<span class="swatch" style="background:'+COL[c]+'"></span>',label:c})),items}}''')

G["sizeorder"] = ("Size Order", [["📏","Things come in different sizes."],["👂","Listen to the question: biggest? smallest? heavier?"],["🐘","Some rounds ask about REAL life: is a mouse bigger than an elephant?"],["👆","Tap the answer, or tap things in order."]],
r'''rounds:a=>a<=0?5:6,
make(n,i,r,a){
  /* Many kinds of size thinking, mixed differently each level: comparing (biggest/smallest), ordering (both directions),
     real-world size (pictures drawn the same size), heavier/lighter, and for older kids "which one is out of order?". */
  const pr=TS.rngFrom(n*131+(a+3)*7);
  const pool=a<0?["compare","order","compare","real"].concat(n>8?["order"]:[]):a===0?["compare","order","real","realorder","heavy"]:["order","realorder","heavy","wrong","compare","real"];
  for(let k=pool.length-1;k>0;k--){const j=Math.floor(pr()*(k+1));[pool[k],pool[j]]=[pool[j],pool[k]]}
  const kind=pool[(i+n)%pool.length];
  const REAL=[["ant","🐜",1],["ladybug","🐞",1],["strawberry","🍓",1.5],["mouse","🐭",2],["apple","🍎",2],["frog","🐸",2],["cat","🐱",3],["watermelon","🍉",3.5],["dog","🐶",4],
    ["bike","🚲",5],["horse","🐴",6],["car","🚗",6.5],["giraffe","🦒",7],["elephant","🐘",7.5],["bus","🚌",8],["house","🏠",8.5],["airplane","✈️",9],["whale","🐋",9.5]];
  const HEAVY=[["feather","🪶",.1],["leaf","🍃",.2],["balloon","🎈",.3],["sock","🧦",.5],["banana","🍌",1],["book","📖",2],["rock","🪨",4],["bowling ball","🎳",6],["watermelon","🍉",5],
    ["cat","🐱",7],["dog","🐶",8],["car","🚗",9],["elephant","🐘",10]];
  const card=(x)=>({key:x[0],html:'<span class="lr-word"><b>'+x[1]+"</b>"+x[0]+"</span>",say:x[0],aria:x[0]});
  const pickSpread=(L,k,gap)=>{let s;do s=U.sample(r,L,k);while(s.some((x,j)=>s.some((y,m)=>m!==j&&Math.abs(x[2]-y[2])<gap)));return s};
  if(kind==="real"){const k=a<0?2:3,s=pickSpread(REAL,k,a<0?3:1.5),big=a<0||r()<.6,ans=s.reduce((p,q)=>(big?q[2]>p[2]:q[2]<p[2])?q:p);
    const w=k===2?(big?"bigger":"smaller"):(big?"the biggest":"the smallest");
    return{type:"pick",cols:k,say:"Which is "+w+" in real life?",prompt:'<span class="ask">Which is '+w+" in <b>real life</b>?</span>",options:U.shuffle(r,s).map(card),answer:ans[0]}}
  if(kind==="realorder"){const k=a<=0?3:4,s=pickSpread(REAL,k,1.5).sort((x,y)=>x[2]-y[2]),desc=r()<.4;if(desc)s.reverse();
    const w=desc?"biggest to smallest":"smallest to biggest";
    return{type:"order",wide:true,say:"Put them in order from "+w+", in real life.",prompt:'<span class="ask">Real life: '+w+"</span>",tiles:U.mix(r,s.map(card)),answer:s.map(x=>x[0])}}
  if(kind==="heavy"){const k=a<=0?2:3,s=pickSpread(HEAVY,k,1.5),hv=r()<.6,ans=s.reduce((p,q)=>(hv?q[2]>p[2]:q[2]<p[2])?q:p);
    const w=k===2?(hv?"heavier":"lighter"):(hv?"the heaviest":"the lightest");
    return{type:"pick",cols:k,say:"Which is "+w+"?",prompt:'<span class="ask">⚖️ Which is '+w+"?</span>",options:U.shuffle(r,s).map(card),answer:ans[0]}}
  // drawn sizes: emoji, long bars or tall bars
  const mode=a<=0?"emoji":U.pick(r,["emoji","bar","vbar"]),em=U.pick(r,["🐘","🍎","⭐","🐻","🌳","🎈","🐟","🏠","🐢","🌻","🚗","🧸"]),col=U.pick(r,U.SHAPE_COLS);
  const html=v=>mode==="emoji"?'<span class="sz" style="font-size:calc(var(--ts) * '+(v*.78).toFixed(2)+')">'+em+"</span>":mode==="bar"?'<span class="sz"><i class="bar" style="width:'+Math.round(v*92)+"%;--c:"+col+'"></i></span>':
    '<span class="sz" style="display:flex;justify-content:center"><i class="vbar" style="height:'+Math.round(v*84)+"%;--c:"+col+'"></i></span>';
  const words=mode==="emoji"?["smallest","biggest"]:mode==="bar"?["shortest","longest"]:["shortest","tallest"];
  const step=a<0?.3:a===0?.2:a===1?.13:.09,grid=[];for(let v=.3;v<=1.0001;v+=step)grid.push(+v.toFixed(3));
  if(kind==="compare"){const k=Math.min(grid.length,a<0?3:4),vals=U.sample(r,grid,k),big=r()<.5,ans=vals.indexOf(big?Math.max(...vals):Math.min(...vals));
    return{type:"pick",cols:k,say:"Which one is the "+(big?words[1]:words[0])+"?",prompt:'<span class="ask">Which is the '+(big?words[1]:words[0])+"?</span>",
      options:vals.map((v,j)=>({key:"v"+j,html:html(v),aria:"size "+Math.round(v*10)})),answer:"v"+ans}}
  const k=Math.min(grid.length,a<0?(n<=15?3:3):a===0?(n<=20?3:4):a===1?(n<=15?4:5):(n<=15?5:6));
  if(kind==="wrong"){const vals=U.sample(r,grid,Math.max(4,k)).sort((x,y)=>x-y);let from,to;do{from=U.ri(r,0,vals.length-1);to=U.ri(r,0,vals.length-1)}while(Math.abs(from-to)<2);
    const row=vals.slice();const [mv]=row.splice(from,1);row.splice(to,0,mv);
    return{type:"pick",cols:row.length,say:"These go from "+words[0]+" to "+words[1]+", but one is in the wrong place. Which one?",prompt:'<span class="ask">'+words[0][0].toUpperCase()+words[0].slice(1)+" → "+words[1]+": which one is in the wrong place?</span>",
      options:row.map((v,j)=>({key:"w"+j,html:html(v),aria:"size "+Math.round(v*10)})),answer:"w"+to}}
  const vals=U.sample(r,grid,k),desc=a<0?n>8&&r()<.4:r()<.5;
  const sorted=vals.map((v,j)=>({key:"v"+j,v,html:html(v)})).sort((x,y)=>desc?y.v-x.v:x.v-y.v),w=desc?words[1]+" to "+words[0]:words[0]+" to "+words[1];
  return{type:"order",size:86,say:"Put them in order from "+w+".",prompt:'<span class="ask">'+w[0].toUpperCase()+w.slice(1)+"</span>",tiles:U.mix(r,sorted),answer:sorted.map(t=>t.key)}}''')


G["trains"] = ("Train Yard", [["🚂","All aboard! Every level has train jobs to do."],["🔢","Hook up the cars in number order, count the passengers, and load the train."],["🎨","Finish the colour pattern and spell your name with letter cars."],["🚃","Every level you finish adds a car to YOUR train!"]],
r'''rounds:a=>a<=0?5:6,
winText:(S,K)=>{const pr=K.save.grades[K.age]||{stars:{}},cars=Math.max(1,Object.keys(pr.stars||{}).length);
  return "🚂"+"🚃".repeat(Math.min(cars,12))+(cars>12?"+":"")+" Your train has "+cars+" car"+(cars>1?"s":"")+"!"},
make(n,i,r,a){
  /* Train-themed practice for a child who loves trains: number order, counting, ten-frame seats, patterns, letters of his name,
     comparing train lengths, missing numbers and sorting cargo. Content one grade back (pre-K for Kindergarten). */
  const COL=["#e2412e","#3b6fd9","#f2b705","#43a047","#8f5bd6","#f08a24","#1e9e8a","#e06aa6"],CN={"#e2412e":"red","#3b6fd9":"blue","#f2b705":"yellow","#43a047":"green","#8f5bd6":"purple","#f08a24":"orange","#1e9e8a":"teal","#e06aa6":"pink"};
  const pr=TS.rngFrom(n*977+(a+3)*31),pool=["couple","passengers","board","pattern","longest","name","missing","cargo"].filter(k=>!(k==="missing"&&a<0&&n<6)&&!(k==="cargo"&&a<0&&n<4));
  for(let k=pool.length-1;k>0;k--){const j=Math.floor(pr()*(k+1));[pool[k],pool[j]]=[pool[j],pool[k]]}
  const kind=i===0?"couple":pool[(i-1)%pool.length]==="couple"?pool[i%pool.length]:pool[(i-1)%pool.length];
  const eng=U.car("#2b2f36","",true),num=v=>a<0?U.numdots(v):String(v);
  if(kind==="couple"){ // hook up the cars in order behind the engine
    let seq;if(a<0){const k=n<=8?3:n<=20?4:5;seq=Array.from({length:k},(_,j)=>j+1)}
    else if(a===0){const k=n<=10?4:5,s=U.ri(r,1,10-k+1);seq=Array.from({length:k},(_,j)=>s+j);if(n>15&&r()<.4)seq.reverse()}
    else{const st=U.pick(r,n<=10?[1,2]:[2,5,10]),k=5,s=st*U.ri(r,0,st===1?15:st===2?5:st===5?6:5);seq=Array.from({length:k},(_,j)=>s+st*j);if(n>12&&r()<.4)seq.reverse()}
    const down=seq.length>1&&seq[0]>seq[1];
    return{type:"order",wide:true,cls:"trains",say:down?"Count down! Hook up the cars from "+seq[0]+" to "+seq[seq.length-1]+".":"Hook up the train cars in number order: "+seq.join(", ")+"!",
      prompt:'<span class="ask">🚂 Hook up the cars: '+(down?"count down!":"in number order")+"</span>",
      tiles:U.mix(r,seq.map((v,j)=>({key:"c"+v,val:v,html:U.car(COL[j%COL.length],v),say:String(v),aria:"car "+v}))),answer:seq}}
  if(kind==="passengers"){ // count the passengers in the car
    const max=a<0?(n<=10?4:6):a===0?10:20,N=U.ri(r,1,max),opts=U.near(r,N,a<0?3:4,1,Math.max(max,4),a<0?2:1);
    const ppl=Array.from({length:N},(_,k)=>["🧑","👧","👦","👩","👴","👶"][k%6]).join("");
    return{type:"pick",say:"How many passengers are on the train?",prompt:'<span class="ask">How many passengers?</span><span class="lr-coach">'+ppl+"</span>",
      options:opts.map(v=>({key:v,html:num(v),say:String(v)})),answer:N}}
  if(kind==="board"){const N=a<0?U.ri(r,1,5):a===0?U.ri(r,3,10):U.ri(r,6,10);
    return{type:"fill",target:N,size:10,say:"Put "+N+" passengers on the train. Tap a seat for each one.",prompt:'<span class="ask">🚃 Put <b>'+N+"</b> passengers on the train</span>"}}
  if(kind==="pattern"){ // colour pattern of cars: what comes next?
    const core=a<0?"AB":a===0?U.pick(r,["AB","ABC","AAB"]):U.pick(r,["ABC","AABB","ABB","ABCD"]),cols=U.sample(r,COL,4),L=core.length,len=Math.max(L*2,4)+(a<0?0:U.ri(r,0,1));
    const at=k=>cols["ABCD".indexOf(core[k%L])],ans=at(len),used=[...new Set(core)].map(c=>cols["ABCD".indexOf(c)]),opts=new Set([ans]);for(const c of U.shuffle(r,used.concat(cols)))if(opts.size<(a<0?2:3))opts.add(c);
    return{type:"pick",cols:3,say:"What colour car comes next?",prompt:'<span class="ask">Which car comes next?</span><span class="lr-train">'+eng+Array.from({length:len},(_,k)=>U.car(at(k),"")).join("")+U.car("#9aa3ad","?")+"</span>",
      options:[...opts].map(c=>({key:c,html:U.car(c,""),say:CN[c],aria:CN[c]})),answer:ans}}
  if(kind==="longest"){ // which train is longest / shortest?
    const k=a<0?2:3;let lens;do lens=Array.from({length:k},()=>U.ri(r,1,a<0?4:6));while(new Set(lens).size<k||(a<0&&Math.abs(lens[0]-lens[1])<2));
    const long=a<0||r()<.6,ans=lens.indexOf(long?Math.max(...lens):Math.min(...lens)),w=long?"longest":"shortest";
    return{type:"pick",cols:1,say:"Which train is the "+w+"? It has the "+(long?"most":"fewest")+" cars.",prompt:'<span class="ask">Which train is the '+w+"?</span>",
      options:lens.map((l,j)=>({key:"t"+j,html:'<span class="lr-train">'+eng+Array.from({length:l},(_,q)=>U.car(COL[(j*2+q)%COL.length],"")).join("")+"</span>",aria:l+" cars"})),answer:"t"+ans}}
  if(kind==="name"){ // spell your name with letter cars (or an ABC run)
    const nm=((TS.players.current()||{}).name||"").toUpperCase().replace(/[^A-Z]/g,"").slice(0,7);
    const run=nm.length>=2&&a<=0?nm.split(""):(()=>{const s=U.ri(r,0,26-5);return"ABCDEFGHIJKLMNOPQRSTUVWXYZ".slice(s,s+5).split("")})();
    const own=nm.length>=2&&a<=0;
    return{type:"order",wide:true,cls:"trains",say:own?"Spell your name with the letter cars: "+run.join(", ")+"!":"Hook up the letter cars in ABC order!",
      prompt:'<span class="ask">'+(own?"🚂 Spell your name: <b>"+nm+"</b>":"🚂 Letter cars in ABC order")+"</span>",
      tiles:U.mix(r,run.map((c,j)=>({key:"l"+j,val:c,html:U.car(COL[j%COL.length],c),say:c,aria:c}))),answer:run}}
  if(kind==="missing"){ // which number car is missing?
    const k=5,s=a<0?1:U.ri(r,1,a===0?6:15),seq=Array.from({length:k},(_,j)=>s+j),hole=a<0?2:U.ri(r,1,k-2),ans=seq[hole],opts=U.near(r,ans,3,1,Math.max(s+k+2,6),1);
    return{type:"pick",say:"One train car is missing. Which number goes in the gap?",prompt:'<span class="ask">Which car is missing?</span><span class="lr-train">'+eng+seq.map((v,j)=>j===hole?U.car("#9aa3ad","?"):U.car(COL[j%COL.length],v)).join("")+"</span>",
      options:opts.map(v=>({key:v,html:num(v),say:String(v)})),answer:ans}}
  // cargo: sort shapes (or colours for pre-K) into the right freight car
  const shapes=a<0?U.sample(r,["circle","square","triangle"],2):U.sample(r,["circle","square","triangle","star","heart"],3);
  const items=[];for(const sh of shapes)for(let k=0;k<(a<0?2:2);k++)items.push(sh);while(items.length<(a<0?4:6))items.push(U.pick(r,shapes));
  return{type:"sort",say:"Load the cargo! Put each shape in its train car.",prompt:'<span class="ask">🚃 Load the cargo into the right car</span>',
    bins:shapes.map((sh,j)=>({key:sh,html:U.car(COL[j],"")+'<span style="display:block;margin-top:-6px">'+U.shape(sh,"#ffffff",0,.55)+"</span>",label:sh+"s"})),
    items:U.shuffle(r,items).map(sh=>({key:sh,html:U.shape(sh,U.pick(r,U.SHAPE_COLS)),aria:sh}))}}''')



G["syllables"] = ("Clap the Syllables", [["👏","Words have beats. Clap them: but-ter-fly has 3!"],["🔊","Listen to the word in beats."],["👆","Tap how many claps."],["🔁","Tap the speaker to hear it again."]],
r"""make(n,i,r,a){
  /* Phonological awareness goes from big parts to small ones (Reading Rockets / NELP): syllables come before single sounds.
     Alberta K ELAL: count syllables in spoken words. Pre-K: 1-2 beats; K: 1-3; grade 1: up to 4 and "which word has 2 claps?". */
  const W=[["cat","🐱",["cat"]],["dog","🐶",["dog"]],["sun","☀️",["sun"]],["bee","🐝",["bee"]],["fish","🐟",["fish"]],["ball","⚽",["ball"]],["frog","🐸",["frog"]],["cake","🎂",["cake"]],["train","🚆",["train"]],
    ["apple","🍎",["ap","ple"]],["monkey","🐵",["mon","key"]],["rabbit","🐰",["rab","bit"]],["pencil","✏️",["pen","cil"]],["rainbow","🌈",["rain","bow"]],["tiger","🐯",["ti","ger"]],["pizza","🍕",["piz","za"]],
    ["robot","🤖",["ro","bot"]],["zebra","🦓",["ze","bra"]],["rocket","🚀",["rock","et"]],["turtle","🐢",["tur","tle"]],["cookie","🍪",["cook","ie"]],["snowman","⛄",["snow","man"]],
    ["banana","🍌",["ba","na","na"]],["butterfly","🦋",["but","ter","fly"]],["dinosaur","🦕",["di","no","saur"]],["elephant","🐘",["el","e","phant"]],["octopus","🐙",["oc","to","pus"]],
    ["kangaroo","🦘",["kan","ga","roo"]],["tomato","🍅",["to","ma","to"]],["umbrella","☂️",["um","brel","la"]],["bicycle","🚲",["bi","cy","cle"]],["strawberry","🍓",["straw","ber","ry"]],
    ["watermelon","🍉",["wa","ter","mel","on"]],["caterpillar","🐛",["cat","er","pil","lar"]],["alligator","🐊",["al","li","ga","tor"]],["helicopter","🚁",["hel","i","cop","ter"]],["avocado","🥑",["av","o","ca","do"]]];
  const max=a<0?2:a===0?3:4,pool=W.filter(w=>w[2].length<=max),claps=k=>"👏".repeat(k);
  if(a>=1&&i%3===2){const k=U.ri(r,1,max),hit=U.pick(r,pool.filter(w=>w[2].length===k)),others=U.sample(r,pool.filter(w=>w[2].length!==k),2);
    return{type:"pick",cols:3,say:"Which word has "+k+" claps?",prompt:'<span class="ask">Which word has '+claps(k)+" ("+k+")?</span>",
      options:U.shuffle(r,[hit].concat(others)).map(w=>({key:w[0],html:'<span class="lr-word"><b>'+w[1]+"</b>"+w[0]+"</span>",say:w[2].join(" - ")})),answer:hit[0]}}
  const w=U.pick(r,pool),k=w[2].length,opts=Array.from({length:max},(_,j)=>j+1);
  return{type:"pick",cols:Math.min(max,4),say:w[0]+". Clap it: "+w[2].join(" - ")+". How many claps?",prompt:'<span class="ask">How many claps?</span><span class="lr-word big1"><b>'+w[1]+"</b>"+w[2].join("·")+"</span>",
    options:opts.map(v=>({key:v,html:'<span style="font-size:.5em;line-height:1.1">'+claps(v)+"</span><br>"+v,say:String(v)})),answer:k}}""")

G["blend"] = ("Robot Talk", [["🤖","The robot talks in little pieces: c... at."],["👂","Put the pieces together to make a word."],["👆","Tap the picture of the word the robot said."],["🔊","Tap the speaker to hear the robot again."]],
r"""make(n,i,r,a){
  /* Blending: big parts first (pre-K: two words -> sun... flower), then onset-rime (K: c... at), then every sound (grade 1: c-a-t),
     then 4 sounds with blends (grade 2: f-r-o-g). Alberta K ELAL: blend onset and rime; grade 1: blend up to 5 sounds. */
  const SND={b:"buh",c:"kuh",d:"duh",f:"fff",g:"guh",h:"huh",j:"juh",k:"kuh",l:"lll",m:"mmm",n:"nnn",p:"puh",r:"rrr",s:"sss",t:"tuh",v:"vvv",w:"wuh",x:"ks",y:"yuh",z:"zzz",a:"aah",e:"eh",i:"ih",o:"aw",u:"uh"};
  const COMP=[["sunflower","🌻",["sun","flower"]],["cupcake","🧁",["cup","cake"]],["rainbow","🌈",["rain","bow"]],["popcorn","🍿",["pop","corn"]],["snowman","⛄",["snow","man"]],
    ["football","🏈",["foot","ball"]],["starfish","⭐",["star","fish"]],["pancake","🥞",["pan","cake"]],["toothbrush","🪥",["tooth","brush"]],["doghouse","🏠",["dog","house"]],["butterfly","🦋",["butter","fly"]],["seashell","🐚",["sea","shell"]]];
  const CVC=[["cat","🐱"],["dog","🐶"],["sun","☀️"],["pig","🐷"],["bus","🚌"],["hat","🎩"],["bed","🛏️"],["fox","🦊"],["cup","☕"],["bug","🐛"],["map","🗺️"],["net","🥅"],["hen","🐔"],
    ["jet","✈️"],["van","🚐"],["web","🕸️"],["pen","🖊️"],["box","📦"],["rat","🐀"],["bat","🦇"],["log","🪵"],["fan","🪭"],["pot","🍲"],["mop","🧹"],["leg","🦵"],["bib","👶"]];
  const CCVC=[["frog","🐸"],["crab","🦀"],["drum","🥁"],["flag","🚩"],["sled","🛷"],["star","⭐"],["snail","🐌"],["plant","🪴"],["swim","🏊"],["clock","🕰️"],["truck","🚚"],["glove","🧤"]];
  const lvl=a<0?0:a===0?1:a===1?2:3,list=lvl===0?COMP:lvl===3?CCVC.concat(CVC):CVC,w=U.pick(r,list),k=a<0?3:4;
  const parts=lvl===0?w[2]:lvl===1?[w[0][0],w[0].slice(1)]:w[0].split("");
  const spoken=lvl===0?parts.join("... "):lvl===1?SND[parts[0]]+"... "+parts[1]:parts.map(c=>SND[c]||c).join("... ");
  const opts=[w].concat(U.sample(r,list.filter(x=>x!==w&&(lvl===0||x[0][0]!==w[0][0]||r()<.3)),k-1));
  return{type:"pick",cols:2,say:"The robot says: "+spoken+". What word is it?",prompt:'<span class="ask">🤖 The robot says:</span><span class="lr-sent">'+parts.join(" · ")+"</span>",
    options:U.shuffle(r,opts).map(x=>({key:x[0],html:'<span class="lr-word"><b>'+x[1]+"</b>"+x[0]+"</span>",say:x[0]})),answer:w[0]}}""")


G["position"] = ("Where's the Cat?", [["🐱","The cat likes to hide!"],["👂","Listen: is it ON, UNDER, IN, NEXT TO, BEHIND, IN FRONT OF, or BETWEEN?"],["👆","Tap the picture that matches."],["🔊","Tap the speaker to hear it again."]],
r"""make(n,i,r,a){
  /* Position words, in the order children learn them (research: in, on, under first; then next to, behind, in front of; then between). */
  const WORDS=a<0?["on","under","in"]:a===0?["on","under","in","next to","behind","in front of"]:["on","under","in","next to","behind","in front of","between"];
  const PETS=U.fav([["🐱","cat"],["🐶","dog"],["🐰","bunny"],["🐻","bear"],["🐸","frog"]]),[pet,name]=U.pick(r,PETS);
  const scene=w=>'<span class="lr-pos p-'+w.replace(/ /g,"-")+'">'+(w==="in"?'<i class="pet">'+pet+'</i><i class="box"></i>':w==="between"?'<i class="tree l">🌳</i><i class="pet">'+pet+'</i><i class="tree r">🌳</i>':'<i class="table"></i><i class="pet">'+pet+"</i>")+"</span>";
  const t=U.pick(r,WORDS),k=a<0?3:4,opts=[t].concat(U.sample(r,WORDS.filter(x=>x!==t),k-1)),obj=t==="in"?"box":t==="between"?"trees":"table";
  return{type:"pick",cols:2,say:"Find the "+name+" "+t+" the "+obj+".",
    prompt:'<span class="ask">The '+name+" is <b>"+t.toUpperCase()+"</b> the "+obj+"</span>",options:U.shuffle(r,opts).map(w=>({key:w,html:scene(w),say:w,aria:name+" "+w})),answer:t}}""")

G["shapes3d"] = ("3D Shapes", [["⚽","Things around us have 3D shapes: balls are spheres, cans are cylinders."],["👀","Look at the real thing."],["👆","Sort it, or tap the one that matches."],["🔊","Tap the speaker to hear it again."]],
r"""make(n,i,r,a){
  /* Alberta K/1 geometry: describe and sort 3D objects; grade 1 names sphere, cube, cylinder, cone; then "which ones roll?" (properties). */
  const OBJ={sphere:[["⚽","soccer ball"],["🏀","basketball"],["🌍","globe"],["🍊","orange"],["🎾","tennis ball"],["🔮","crystal ball"]],cube:[["🎲","dice"],["🧊","ice cube"],["🎁","gift box"],["📦","box"]],
    cylinder:[["🥫","can"],["🔋","battery"],["🧻","paper roll"],["🪵","log"],["🕯️","candle"]],cone:[["🍦","ice cream cone"],["🥕","carrot"],["🎄","tree"]]};
  const NAME={sphere:"sphere (ball shape)",cube:"cube (box shape)",cylinder:"cylinder (can shape)",cone:"cone"},kinds=a<0?["sphere","cube"]:a===0?["sphere","cube","cylinder"]:["sphere","cube","cylinder","cone"];
  const bin=k=>({key:k,html:U.solid(k),label:a<0?(k==="sphere"?"ball shape":"box shape"):k});
  if(a>=1&&i%3===2){const roll=new Set(["sphere","cylinder","cone"]),cells=[];for(let k=0;k<8;k++){const kk=U.pick(r,kinds),o=U.pick(r,OBJ[kk]);cells.push({html:'<span style="font-size:2.2em">'+o[0]+"</span>",ok:roll.has(kk),aria:o[1],why:"a "+kk+": it doesn't roll"})}
    if(!cells.some(c=>c.ok))cells[0]={html:'<span style="font-size:2.2em">⚽</span>',ok:true,aria:"ball"};if(cells.every(c=>c.ok))cells[1]={html:'<span style="font-size:2.2em">🎲</span>',ok:false,aria:"dice",why:"a cube: it doesn't roll"};
    return{type:"hunt",cols:4,say:"Tap everything that can roll.",prompt:'<span class="ask">Tap everything that can <b>roll</b></span>',cells}}
  if(i%2===1){const t=U.pick(r,kinds),o=U.pick(r,OBJ[t]),opts=U.shuffle(r,kinds).slice(0,a<0?2:3);if(!opts.includes(t))opts[0]=t;
    return{type:"pick",cols:opts.length,say:"What shape is the "+o[1]+"?",prompt:'<span class="ask">What shape is it?</span><span class="lr-emo">'+o[0]+"</span>",
      options:U.shuffle(r,opts).map(k=>({key:k,html:U.solid(k)+'<span style="display:block;font-size:15px">'+(a<0?(k==="sphere"?"ball":"box"):k)+"</span>",say:NAME[k]})),answer:t}}
  const items=[];for(const k of kinds)items.push(k);while(items.length<(a<0?4:6))items.push(U.pick(r,kinds));
  return{type:"sort",say:"Sort the things by their shape.",prompt:'<span class="ask">Sort them by shape</span>',bins:kinds.map(bin),
    items:U.shuffle(r,items).map(k=>{const o=U.pick(r,OBJ[k]);return{key:k,html:'<span class="lr-em">'+o[0]+"</span>",aria:o[1]}})}}""")


# helper used by the new number games: k distinct choices near v, inside lo..hi (pre-K keeps them apart)
NEAR_JS = r"""const choices=(r,v,k,lo,hi,step=1,spread=3)=>{const c=[];for(let x=lo;x<=hi;x+=step)if(x!==v&&Math.abs(x-v)<=spread*step)c.push(x);const o=U.sample(r,c,Math.min(k-1,c.length));
  for(let x=lo;o.length<k-1&&x<=hi;x+=step)if(x!==v&&!o.includes(x))o.push(x);return U.shuffle(r,o.concat([v]))};"""

G["quicklook"] = ("Quick Look", [["👀","Some dots flash on the screen for a moment."],["⚡","Don't count them one by one. Just look!"],["👆","Tap how many you saw."],["🔁","You can look again once."]],
r"""make(n,i,r,a){
  /* Subitizing (Clements & Sarama): see a small amount at a glance. Pre-K 1-4 then 5 on dice, then lines;
     K 1-5 any layout, then 6-7 as two groups; grade 1 6-10 on ten frames and dice pairs; grade 2 10-20 on double frames. Short looks so there's no time to count. */
  let v,kind,split=0,ms=2000,k=a<0?3:4,lo=1,hi=a<0?5:a===0?7:a===1?10:20;
  if(a<0){v=U.ri(r,1,n<=8?4:5);kind=n<=15?"dice":U.pick(r,["dice","line"])}
  else if(a===0){ms=1500;if(n<=12||i%2===0){v=U.ri(r,1,5);kind=U.pick(r,["dice","line","scatter"])}else{v=U.ri(r,6,7);kind="pair";split=U.ri(r,v-5,5)}}
  else if(a===1){ms=1500;v=U.ri(r,6,10);kind=U.pick(r,["frame","pair"]);if(kind==="pair")split=U.ri(r,Math.max(1,v-6),Math.min(6,v-1))}
  else{v=U.ri(r,10,20);kind="frame";lo=8}
  const opts=choices(r,v,k,lo,hi,1,a<0?4:2);
  return{type:"pick",cols:a<0?3:2,flash:ms,say:"Quick look! How many dots?",prompt:'<span class="ask">Quick look! How many?</span><span class="lr-flash">'+U.dotpic(v,kind,r,split)+"</span>",
    options:opts.map(x=>({key:x,html:a<0?U.numdots(x):String(x),say:String(x)})),answer:v}}""")

G["hidebugs"] = ("Hiding Bugs", [["🐞","Some bugs are hiding under a leaf!"],["👀","You know how many bugs there are in all."],["🤔","Count the ones you can see. How many are hiding?"],["👆","Tap the number that's hiding."]],
r"""make(n,i,r,a){
  /* Hidden partner (number bonds: part-part-whole). Pre-K wholes of 3-5 with the whole shown as dots; K wholes of 5-10 ("5 is 3 and 2");
     grade 1 to 20 as an equation (_ + 7 = 12); grade 2 with tens (60 = 40 + _). */
  const BUG=U.pick(r,["🐞","🐛","🐜","🐝","🦋"]),k=a<0?3:4;let w,h;
  if(a<0)w=U.ri(r,3,n<=12?4:5);else if(a===0)w=n<=12?5:U.ri(r,5,10);else if(a===1)w=U.ri(r,8,20);else w=10*U.ri(r,3,10);
  if(a>=2)h=10*U.ri(r,1,w/10-1);else h=U.ri(r,1,w-1);
  const s=w-h,pics=s<=12?'<span class="lr-hide">'+("<i>"+BUG+"</i>").repeat(s)+'<i class="leaf"><b>?</b></i></span>':"";
  let ask,say;
  if(a<0){ask="There are "+w+" bugs. How many are hiding?";say="There are "+w+" bugs in all. I can see "+s+". How many are hiding under the leaf?"}
  else if(a===0){ask=w+" is "+s+" and <b>?</b>";say=w+" bugs in all. "+s+" you can see. How many are hiding? "+w+" is "+s+" and how many?"}
  else if(a===1){ask=s+" + <b>?</b> = "+w;say=s+" plus what makes "+w+"?"}
  else{ask=w+" = "+s+" + <b>?</b>";say=w+" is "+s+" plus what?"}
  const whole=a<0?'<span class="lr-hide" style="font-size:16px;gap:8px">All the bugs: '+U.numdots(w)+"</span>":"";
  const opts=a>=2?choices(r,h,k,10,w-10,10,2):choices(r,h,k,1,Math.max(w-1,k),1,a<0?4:3);
  return{type:"pick",cols:a<0?3:2,say,prompt:'<span class="ask">'+ask+"</span>"+whole+pics,
    options:opts.map(x=>({key:x,html:a<0?U.numdots(x):String(x),say:x===h?"Yes! "+s+" and "+h+" make "+w+".":String(x)})),answer:h}}""")

G["dotmatch"] = ("Dot Match", [["🎲","The same number can look different."],["👀","Look at the card at the top."],["👆","Find the card that shows the same number."],["🔊","Tap the speaker to hear it again."]],
r"""make(n,i,r,a){
  /* Same number, different look; then dots and numerals; then numerals and number words. The main numeral-learning game for pre-readers. */
  const W=["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen","twenty"];
  const k=a<0?3:4,LOOKS=v=>v<=6?["dice","line","scatter"]:v<=10?["frame","line","scatter"]:["frame"];
  let v,mode;
  if(a<0){v=U.ri(r,1,n<=12?4:5);mode=n<=12||i%2===0?"dots":"num"}
  else if(a===0){v=U.ri(r,1,n<=12?6:10);mode=["dots","num","fromnum"][i%3]}
  else{v=U.ri(r,a===1?1:10,20);mode=i%2?"word":"fromnum"}
  const opts=choices(r,v,k,a>=1&&v>=10?10:1,a<0?5:a===0?10:20,1,a<0?4:2);
  const look=LOOKS(v),shown=U.pick(r,look);
  const pic=(x,not)=>{const l=LOOKS(x).filter(y=>y!==not);return U.dotpic(x,U.pick(r,l.length?l:LOOKS(x)),r)};
  let top,html,ask;
  if(mode==="dots"){top=U.dotpic(v,shown,r);html=x=>pic(x,shown);ask="Find the same number of dots"}
  else if(mode==="num"){top=U.dotpic(v,shown,r);html=x=>a<0?U.numdots(x):String(x);ask="Which number is this?"}
  else if(mode==="fromnum"){top='<b style="font-size:clamp(56px,16vw,80px)">'+v+"</b>";html=x=>pic(x);ask="Find "+v+" dots"}
  else{top='<b style="font-size:clamp(34px,10vw,48px)">'+W[v]+"</b>";html=x=>String(x);ask="Which number is "+W[v]+"?"}
  return{type:"pick",cols:2,say:ask+".",prompt:'<span class="ask">'+ask+'</span><span class="lr-flash" style="min-height:0">'+top+"</span>",
    options:opts.map(x=>({key:x,html:html(x),say:String(x)})),answer:v}}""")

G["counton"] = ("Count On", [["🐸","Some frogs are already in the pond. More hop in!"],["🧠","Start at the number in the pond, then count on."],["👆","Tap how many there are now."],["🔊","Tap the speaker to hear it again."]],
r"""make(n,i,r,a){
  /* Counting on (and back) from a hidden group: K start to 5, add 1-3; grade 1 start to 20, add 1-4, some count back; grade 2 to 100 by tens.
     Train fans see passengers getting on a train. */
  const tr=(TS.players.current()||{}).fav==="trains",who=tr?["🧍","people","on the train","get on","get off"]:["🐸","frogs","in the pond","hop in","hop out"];
  let s,add,back=false,step=1;
  if(a<0){s=U.ri(r,1,3);add=1}else if(a===0){s=U.ri(r,2,5);add=U.ri(r,1,3)}
  else if(a===1){s=U.ri(r,5,20);add=U.ri(r,1,4);back=i%3===2&&s-add>=2}
  else{step=10;s=U.ri(r,2,8)*10+U.ri(r,0,9);add=10*U.ri(r,1,3);back=i%3===2&&s-add>=5}
  const tot=back?s-add:s+add,seq=[];for(let x=s;back?x>=tot:x<=tot;x+=back?-step:step)seq.push(x);
  const movers=step===10?Array.from({length:add/10},()=>'<i class="ten">10 '+who[0]+"</i>").join(""):("<i>"+who[0]+"</i>").repeat(add);
  const home='<span class="home'+(tr?" train":"")+'">'+(tr?"🚃 ":"")+s+"<small>"+who[1]+"</small></span>";
  const verb=v=>add===1?v.replace(/^(\w+)/,m=>m==="hop"?"hops":m+"s"):v;
  const say="There are "+s+" "+who[1]+" "+who[2]+". "+add+(back?" ":" more ")+verb(back?who[4]:who[3])+". How many are "+(back?"left":"there now")+"?";
  const opts=choices(r,tot,a<0?3:4,step===10?10:1,step===10?100:a===1?24:10,step,2);
  return{type:"pick",cols:a<0?3:2,say,prompt:'<span class="ask">'+s+" "+(back?"−":"+")+" "+add+" = <b>?</b></span>"+'<span class="lr-hop">'+home+'<span class="in">'+(back?"⬅️ ":"")+movers+(back?"":" ⬅️")+"</span></span>",
    options:opts.map(x=>({key:x,html:a<0?U.numdots(x):String(x),say:x===tot?seq.join("… ")+"! "+tot+".":String(x)})),answer:tot}}""")

# Extra script a game needs before TS_LEARN runs.
PRE = {"trace": r"""const TRACE_ORDER=(n,a)=>{const ORDER="LTIEFHVXWAKMNYZOCQGSJUDPBR",DIG="0123456789";
  if(a!==undefined&&a>=1&&n%3===0)return DIG[(n/3)%10];return n>26&&a!==undefined&&a<0?DIG[(n-27)%10]:ORDER[(n-1)%26]};""","abc": r"""const ABC={UP:"ABCDEFGHIJKLMNOPQRSTUVWXYZ",
  // letters of the player's own name come first (children learn their name letters most easily), then the rest A to Z
  seq(){const nm=((TS.players.current()||{}).name||"").toUpperCase().replace(/[^A-Z]/g,""),first=[...new Set(nm.split(""))].slice(0,6);
    return first.concat(this.UP.split("").filter(c=>!first.includes(c)))},
  HARD:"BDPQEIOUHWYCGMNVX".split(""), // the letters young children find hardest, for review levels
  SND:{A:"ah",B:"buh",C:"kuh",D:"duh",E:"eh",F:"fff",G:"guh",H:"huh",I:"ih",J:"juh",K:"kuh",L:"lll",M:"mmm",N:"nnn",O:"aw",P:"puh",Q:"kwuh",R:"rrr",S:"sss",T:"tuh",U:"uh",V:"vvv",W:"wuh",X:"ks",Y:"yuh",Z:"zzz"},
  W:{A:[["apple","🍎"],["ant","🐜"],["alligator","🐊"]],B:[["ball","⚽"],["bear","🐻"],["banana","🍌"],["bus","🚌"]],C:[["cat","🐱"],["car","🚗"],["cake","🎂"]],D:[["dog","🐶"],["duck","🦆"],["drum","🥁"]],
    E:[["egg","🥚"],["elephant","🐘"]],F:[["fish","🐟"],["frog","🐸"],["fox","🦊"]],G:[["goat","🐐"],["grapes","🍇"],["gift","🎁"]],H:[["hat","🎩"],["horse","🐴"],["house","🏠"]],
    I:[["iguana","🦎"],["igloo","🧊"]],J:[["jellyfish","🪼"],["juice","🧃"],["jeans","👖"]],K:[["kite","🪁"],["key","🔑"],["kangaroo","🦘"]],L:[["lion","🦁"],["leaf","🍃"],["lemon","🍋"]],
    M:[["moon","🌙"],["mouse","🐭"],["monkey","🐵"]],N:[["nest","🪺"],["nose","👃"],["nut","🥜"]],O:[["octopus","🐙"],["otter","🦦"]],P:[["pig","🐷"],["pizza","🍕"],["panda","🐼"]],
    Q:[["queen","👸"]],R:[["rabbit","🐰"],["rainbow","🌈"],["robot","🤖"]],S:[["sun","☀️"],["snake","🐍"],["sock","🧦"]],T:[["tiger","🐯"],["tree","🌳"],["train","🚆"]],
    U:[["umbrella","☂️"],["up","⬆️"]],V:[["van","🚐"],["violin","🎻"],["volcano","🌋"]],W:[["whale","🐳"],["watermelon","🍉"],["worm","🪱"]],X:[["fox","🦊"],["box","📦"]],
    Y:[["yo-yo","🪀"],["yak","🐃"],["yarn","🧶"]],Z:[["zebra","🦓"],["zipper","🤐"],["zero","0️⃣"]]},
  word(c,r){const l=this.W[c];return l[Math.floor(r()*l.length)]},
  CONF:{B:["D","P"],D:["B"],P:["Q","B"],Q:["P","O"],M:["N","W"],N:["M"],W:["M"],E:["F"],F:["E"],O:["Q","C"],C:["O","G"],G:["C"],I:["L","J"],L:["I"],U:["V"],V:["U"]},
  // the alphabet song: A-G, H-P, Q-V, W-Z, and the note each letter is sung on
  SEGS:[[0,7],[7,16],[16,22],[22,26]],
  NOTE:[60,60,67,67,69,69,67,65,65,64,64,62,62,62,62,60,67,67,65,64,64,62,67,65,64,60]};
"""}

for _g in ["quicklook", "hidebugs", "dotmatch", "counton"]: PRE[_g] = NEAR_JS

for gid,(name,howto,body) in G.items():
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<!--HEAD:{name}-->
</head>
<body>
<!--KIT-->
<!--LEARN-->
<script>
(()=>{{const U=TS_LEARN.util;
{PRE.get(gid,'')}
TS_LEARN({{id:{json.dumps(gid)},name:{json.dumps(name)},howto:{json.dumps(howto,ensure_ascii=False)},
{body}}});
}})();
</script>
</body>
</html>
'''
    (SRC / f"{gid}.html").write_text(html)
print(len(G), "games written")
