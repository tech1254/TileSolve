import pathlib, json
SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
G = {}

G["abc"] = ("ABC Order", [["🔤","Letters are mixed up."],["👆","Tap the letters in ABC order: A, then B, then C..."],["✅","Fill every box to finish the round."],["🔊","Tap the speaker to hear it again."]],
r'''label:n=>"",
make(n,i,r,a){const UP="ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  if(a>=2&&n>15){ // putting words in ABC order
    const W=[["ant","🐜"],["apple","🍎"],["bat","🦇"],["bear","🐻"],["bed","🛏️"],["bus","🚌"],["cat","🐱"],["cake","🎂"],["cup","☕"],["dog","🐶"],["duck","🦆"],["egg","🥚"],
      ["fish","🐟"],["fox","🦊"],["frog","🐸"],["goat","🐐"],["gift","🎁"],["hat","🎩"],["hen","🐔"],["jet","✈️"],["kite","🪁"],["key","🔑"],["lamp","💡"],["lion","🦁"],
      ["map","🗺️"],["moon","🌙"],["nest","🪺"],["nut","🥜"],["owl","🦉"],["pig","🐷"],["pear","🍐"],["queen","👸"],["rain","🌧️"],["ring","💍"],["sun","☀️"],["sock","🧦"],
      ["tree","🌳"],["tent","⛺"],["van","🚐"],["web","🕸️"],["yarn","🧶"],["zebra","🦓"]];
    const k=U.ramp(n,16,40,3,5),same=n>30;let ws;
    for(let t=0;t<50;t++){ws=U.sample(r,W,k);if(same||new Set(ws.map(w=>w[0][0])).size===k)break}
    ws.sort((x,y)=>x[0]<y[0]?-1:1);const ans=ws.map(w=>w[0]);   // mix() shuffles away from the sorted order
    return{type:"order",wide:true,say:"Put the words in A B C order.",prompt:'<span class="ask">Put the words in ABC order</span>',
      tiles:U.mix(r,ws).map(w=>({key:w[0],html:w[1]+" "+w[0],say:w[0]})),answer:ans}}
  let len,start,lower;
  if(a<0){len=n<=20?3:n<=32?4:5;start=0;lower=false}
  else if(a===0){len=Math.min(7,3+Math.floor((n-1)/8));start=n<=12?0:U.ri(r,0,26-len);lower=false}
  else if(a===1){len=Math.min(10,5+Math.floor((n-1)/8));start=U.ri(r,0,26-len);lower=n>20}
  else{len=U.ri(r,8,10);start=U.ri(r,0,26-len);lower=n>8}
  const seq=UP.slice(start,start+len).split("").map(c=>lower?c.toLowerCase():c);
  return{type:"order",say:"Put the letters in A B C order."+(start===0?" Start with A.":""),prompt:'<span class="ask">Put the letters in ABC order</span>',
    tiles:U.mix(r,seq).map(c=>({key:c,html:c,say:c})),answer:seq}}''')

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
  const easy="smtapbcdfln",pool=W.filter(g=>a>0||(a===0&&n>15)||easy.includes(g[0].w[0])),word=U.pick(r,U.pick(r,pool)),l=word.w[0];
  const count=a<0?(n<=15?2:3):a===0?3:4,lower=a>=2||(a===1&&n>20),letters="abcdefghijklmnopqrstuvwyz".split("").filter(x=>x!==l),opts=[l,...U.sample(r,letters,count-1)];
  const f=x=>lower?x:x.toUpperCase(),blank=a>=2||(a===1&&n>25);
  return{type:"pick",say:word.w.replace("-"," ")+". What sound does "+word.w.replace("-"," ")+" start with?",
    prompt:'<span class="big">'+word.e+"</span>"+(blank?'<span class="word">_'+word.w.slice(1)+"</span>":""),
    options:U.shuffle(r,opts).map(x=>({key:f(x),html:f(x)})),answer:f(l)}}''')

G["trace"] = ("Trace a Letter", [["🟢","Put your finger on the green dot."],["✍️","Slide along the grey line to draw it."],["🔢","Some letters have more than one line: follow the numbers."],["🔊","Tap the speaker to hear it again."]],
r'''rounds:()=>3,label:n=>"",
make(n,i,r,a){const ORDER="LTIEFHVXWAKMNYZOCQGSJUDPBR",DIG="0123456789";let ch;
  if(a<0)ch=i===2&&n>12?DIG[1+(n%5)]:ORDER[((n-1)*2+i)%12];
  else if(a===0)ch=ORDER[((n-1)*3+i)%26];
  else if(a===1)ch=n<=15?ORDER[((n-1)*3+i)%26]:(i===1?DIG[(n+i)%10]:U.pick(r,ORDER.split("")));
  else ch=i%2===1?DIG[U.ri(r,0,9)]:U.pick(r,ORDER.split(""));
  const num=/\d/.test(ch);
  return{type:"trace",ch,say:"Trace the "+(num?"number ":"letter ")+ch+". Start at the green dot.",prompt:'<span class="ask">Trace the '+(num?"number":"letter")+" "+ch+"</span>"}}''')

G["count"] = ("Count It", [["🍎","Look at the pictures."],["☝️","Count them one at a time."],["👆","Tap the number that says how many."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const EM=[["🍎","apples"],["⭐","stars"],["🐟","fish"],["🎈","balloons"],["🐞","ladybugs"],["🍪","cookies"],["🌸","flowers"],["🚗","cars"],["🦆","ducks"],["🍓","strawberries"],["🐸","frogs"],["⚽","balls"]];
  const[em,name]=U.pick(r,EM);let N,pic,opts;
  if(a<0){const max=n<=10?3:5;N=U.ri(r,1,max);pic=U.scatter(r,em,N);opts=U.near(r,N,n<=10?2:3,1,Math.max(max,3),2)}
  else if(a===0){const max=n<=10?5:n<=25?8:10;N=U.ri(r,1,max);pic=U.scatter(r,em,N);opts=U.near(r,N,3,1,Math.max(max,4),2)}
  else if(a===1&&n<=25){const max=n<=10?12:20;N=U.ri(r,n<=10?3:6,max);pic=U.cluster(em,N,N>10?10:5,true);opts=U.near(r,N,4,1,25,3)}
  else{N=a===1?U.ri(r,20,59):U.ri(r,n<=10?10:21,n<=10?49:99);pic=U.tens(N);const s=new Set([N]);for(const d of U.shuffle(r,[10,-10,1,-1,11,-9]))if(s.size<4&&N+d>0)s.add(N+d);opts=U.shuffle(r,[...s])}
  return{type:"pick",say:a<=0?"Count the "+name+". How many are there?":N<=20?"How many "+name+" are there?":"Count the tens and ones. How many blocks?",
    prompt:'<span class="ask">'+(N>20?"Tens and ones: how many?":"How many?")+"</span>"+pic,
    options:opts.map(v=>({key:v,html:String(v),say:String(v)})),answer:N}}''')

G["numorder"] = ("Number Order", [["🔢","Numbers are mixed up."],["👆","Tap them in order, smallest first."],["⬇️","Later, some rounds go from biggest to smallest. Listen!"],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const range=(s,len,step)=>Array.from({length:len},(_,k)=>s+k*step);let nums,desc=false;
  if(a<0){const len=n<=15?3:n<=30?4:5;nums=range(1,len,1)}
  else if(a===0){const len=n<=10?3:n<=20?5:U.ri(r,4,5);nums=range(n<=20?1:U.ri(r,1,11-len),len,1)}
  else if(a===1){if(n<=15){const len=U.ri(r,5,6);nums=range(U.ri(r,1,21-len),len,1)}else if(n<=25)nums=range(2*U.ri(r,1,5),5,2);else{const st=U.pick(r,[5,10]);nums=range(st*U.ri(r,1,st===5?14:5),5,st)}}
  else{if(n<=12){const step=U.pick(r,[2,10,25,50]);nums=range(step*U.ri(r,1,step>=25?8:step===10?4:20),6,step)}else nums=U.sample(r,range(n>25?100:1,n>25?999:99,1),U.ri(r,5,6));desc=n>15&&i%2===1}
  const ans=nums.slice().sort((x,y)=>desc?y-x:x-y).map(String);
  return{type:"order",say:desc?"Put the numbers in order from biggest to smallest.":"Put the numbers in order from smallest to biggest.",
    prompt:'<span class="ask">'+(desc?"Biggest to smallest ⬇️":"Smallest to biggest ⬆️")+"</span>",tiles:U.mix(r,ans).map(v=>({key:v,html:v,say:v})),answer:ans}}''')

G["moreless"] = ("More or Less", [["⚖️","Look at both sides."],["👂","Listen: is it asking for more, or fewer?"],["👆","Tap the right one."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){
  if(a<=0){const EM=["🍎","⭐","🐟","🎈","🐞","🍪","🦆","🍓"],em=U.pick(r,EM),gap=a<0||n<=15?2:1,hi=a<0?5:7;let x,y;do{x=U.ri(r,1,hi);y=U.ri(r,1,hi)}while(Math.abs(x-y)<gap);
    const fewer=a===0&&n>20&&i%2===1,ans=(fewer?x<y:x>y)?"L":"R";
    return{type:"pick",cols:2,say:fewer?"Which group has fewer?":"Which group has more?",prompt:'<span class="ask">Which has '+(fewer?"fewer":"more")+"?</span>",
      options:[{key:"L",html:U.cluster(em,x,3),aria:x+" pictures"},{key:"R",html:U.cluster(em,y,3),aria:y+" pictures"}],answer:ans}}
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
  if(a<0){len=3;step=1;s=U.ri(r,1,3);hole=2;count=n<=15?2:3}
  else if(a===0){len=4;step=1;s=U.ri(r,1,7);hole=n<=10?3:U.ri(r,0,3);count=3}
  else if(a===1){len=5;count=4;if(n<=15){step=1;s=U.ri(r,1,16)}else if(n<=25){step=-1;s=U.ri(r,6,20)}else if(n<=32){step=2;s=2*U.ri(r,0,6)}else{step=U.pick(r,[5,10]);s=step*U.ri(r,1,step===5?15:5)}hole=U.ri(r,1,4)}
  else{len=5;count=4;step=U.pick(r,n<=12?[2,10]:n<=25?[2,10,25,50]:[10,25,50,100]);s=step*U.ri(r,1,step>=100?5:step>=25?10:step===10?40:200);if(n>25&&i%2===1){s+=step*4;step=-step}hole=U.ri(r,1,4)}
  const seq=Array.from({length:len},(_,k)=>s+k*step),ans=seq[hole],m=Math.abs(step),opts=new Set([ans]);
  for(const d of U.shuffle(r,[m,-m,1,-1,2*m,-2*m,2,-2]))if(opts.size<count&&ans+d>=0)opts.add(ans+d);
  return{type:"pick",say:"What number is missing?"+(step<0?" These count backwards!":""),
    prompt:'<span class="ask">What number is missing?</span><span class="seq">'+seq.map((v,k)=>k===hole?'<b class="q">?</b>':"<b>"+v+"</b>").join("")+"</span>",
    options:U.shuffle(r,[...opts]).map(v=>({key:v,html:String(v),say:String(v)})),answer:ans}}''')

G["tenframe"] = ("Ten Frame", [["🔟","A ten frame has 10 boxes."],["👆","Tap boxes to put in dots. Tap again to take one out."],["🧮","Some rounds ask how many dots, or how many more make 10."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const size=a>=2?20:10;
  if(i%2===0){const t=a<0?U.ri(r,1,n<=20?3:5):a===0?(n<=15?U.ri(r,1,5):U.ri(r,3,10)):a===1?U.ri(r,3,10):U.ri(r,11,20);
    return{type:"fill",size,target:t,say:"Show "+t+". Tap the boxes to put in "+t+" dots.",prompt:'<span class="ask">Put in this many dots</span><span class="big l">'+t+"</span>"}}
  if(a<=0){const k=a<0?U.ri(r,1,5):U.ri(r,1,n<=15?6:10);return{type:"pick",say:"How many dots?",prompt:'<span class="ask">How many dots?</span>'+U.frame(k),
    options:U.near(r,k,a<0?2:3,0,10,2).map(v=>({key:v,html:String(v)})),answer:k}}
  if(a===1){const k=U.ri(r,1,9);return{type:"pick",say:"How many more dots make 10?",prompt:'<span class="ask">How many more make 10?</span>'+U.frame(k),
    options:U.near(r,10-k,4,0,10,2).map(v=>({key:v,html:String(v)})),answer:10-k}}
  const k=U.ri(r,11,19),more=i%4===1;
  return{type:"pick",say:more?"How many more dots make 20?":"How many dots?",prompt:'<span class="ask">'+(more?"How many more make 20?":"How many dots?")+"</span>"+U.frame(k,20),
    options:U.near(r,more?20-k:k,4,0,20,2).map(v=>({key:v,html:String(v)})),answer:more?20-k:k}}''')

G["shapesort"] = ("Shape Sort", [["🔺","Each shape has a home with its outline."],["👆","Drag a shape to its home, or tap the shape then tap its home."],["🔄","Shapes can be any colour, size, or turned around!"],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const C=U.SHAPE_COLS,NM={circle:"circle",oval:"oval",square:"square",rectangle:"rectangle",triangle:"triangle",star:"star",heart:"heart",diamond:"diamond",pentagon:"pentagon",hexagon:"hexagon"};
  let kinds,bySides=false;
  if(a<0)kinds=n<=20?["circle","square"]:["circle","square","triangle"];
  else if(a===0)kinds=n<=10?["circle","square"]:n<=25?["circle","square","triangle"]:U.sample(r,["circle","square","triangle","star","heart"],3);
  else if(a===1)kinds=n<=15?U.sample(r,["circle","square","triangle","star","heart"],3):(()=>{const p=U.pick(r,[["square","rectangle"],["circle","oval"]]);
    return p.concat(U.sample(r,["triangle","star","heart"],n>30?2:1))})();
  else if(n<=12)kinds=U.sample(r,["triangle","square","pentagon","hexagon","diamond","rectangle"],4);
  else{bySides=true;kinds=["triangle","square","rectangle","diamond","pentagon","hexagon"]}
  const cnt=a<0?3:a===0?4:a===1?6:7,items=[];
  const rot=k=>a<=0?0:k==="square"||k==="diamond"||k==="rectangle"?U.pick(r,[0,90,180]):U.ri(r,0,359);
  const bkey=k=>bySides?"s"+U.SIDES[k]:k;
  const binsK=bySides?[3,4,5,6].map(s=>"s"+s):kinds;
  // at least one item for each home, then random ones
  const pickKinds=bySides?[...[3,4,5,6].map(s=>U.pick(r,kinds.filter(k=>U.SIDES[k]===s)))]:kinds.slice();
  while(pickKinds.length<cnt)pickKinds.push(U.pick(r,kinds));
  U.shuffle(r,pickKinds).forEach(k=>items.push({key:bkey(k),html:U.shape(k,U.pick(r,C),rot(k),.7+.3*r()),aria:NM[k]}));
  const bins=binsK.map(b=>bySides?{key:b,html:'<b class="sides">'+b.slice(1)+"</b>",label:b.slice(1)+" sides"}:{key:b,html:U.shape(b,"#cfd6dd",0,1,true),label:NM[b]});
  return{type:"sort",say:bySides?"Sort the shapes by how many sides they have.":"Put each shape in its home.",
    prompt:'<span class="ask">'+(bySides?"Sort by number of sides":"Put each shape in its home")+"</span>",bins,items}}''')

G["shapehunt"] = ("Shape Hunt", [["🔍","Lots of shapes are mixed up."],["👂","Listen for which shape to find."],["👆","Tap every one of them!"],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const C=U.SHAPE_COLS,PL={circle:"circles",oval:"ovals",square:"squares",rectangle:"rectangles",triangle:"triangles",star:"stars",heart:"hearts",diamond:"diamonds",pentagon:"pentagons",hexagon:"hexagons"};
  let cols,rows,kinds,bySides=false;
  if(a<0){cols=3;rows=2;kinds=["circle","square","triangle"]}
  else if(a===0){cols=3;rows=n<=15?3:4;kinds=n<=15?["circle","square","triangle"]:["circle","square","triangle","star","heart"]}
  else if(a===1){cols=4;rows=4;kinds=["circle","square","triangle","rectangle","oval","star","heart"]}
  else{cols=4;rows=5;kinds=["triangle","square","rectangle","diamond","pentagon","hexagon","circle","oval"];bySides=n>15}
  const N=cols*rows,rot=k=>a<=0?0:k==="square"||k==="diamond"||k==="rectangle"?U.pick(r,[0,90]):U.ri(r,0,359);
  const cell=(k,ok)=>({html:U.shape(k,U.pick(r,C),rot(k),.65+.35*r()),ok,aria:k});let cells=[],say,ask;
  if(bySides){const s=U.pick(r,[3,4,5,6]),T=U.ri(r,3,6);const yes=kinds.filter(k=>U.SIDES[k]===s),no=kinds.filter(k=>U.SIDES[k]!==s);
    for(let k=0;k<N;k++){const ok=k<T;cells.push(cell(U.pick(r,ok?yes:no),ok))}say="Tap all the shapes with "+s+" sides.";ask="Tap all shapes with "+s+" sides"}
  else{const t=U.pick(r,kinds),T=a<0?2:U.ri(r,2,Math.min(5,Math.floor(N/3))),LIKE={square:"rectangle",rectangle:"square",circle:"oval",oval:"circle"};
    const others=kinds.filter(k=>k!==t);for(let k=0;k<N;k++){const ok=k<T;cells.push(cell(ok?t:(a>=1&&LIKE[t]&&others.includes(LIKE[t])&&r()<.45?LIKE[t]:U.pick(r,others)),ok))}
    say="Tap all the "+PL[t]+".";ask="Tap all the "+PL[t]+" "+U.shape(t,"#9aa3ad").replace('class="lr-shp"','class="lr-shp ic"')}
  return{type:"hunt",cols,say,prompt:'<span class="ask">'+ask+"</span>",cells:U.shuffle(r,cells)}}''')

G["colours"] = ("Colour Match", [["🎨","Each round is about colours."],["👆","Tap the right colour, or sort shapes into the basket of the same colour."],["📖","Later you read the colour word yourself!"],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const COL=U.COLOURS,K=["circle","square","triangle","star","heart","diamond"];
  const NAMES=a<0?["red","blue","yellow","green"].slice(0,n<=15?3:4):a===0?["red","blue","green","yellow"]:a===1?["red","blue","green","yellow","orange","purple","pink","brown"]:Object.keys(COL);
  if(a<0||(a===0&&n<=15)||i%2===0){const cs=U.sample(r,NAMES,a<0?(n<=15?2:3):a===0?3:4),t=cs[0],stroop=a>=2&&n>20,ink=stroop?U.pick(r,cs.slice(1)):null;
    const prompt=a<=0?'<span class="ask">Tap the '+t+" one</span>":'<span class="ask">'+(stroop?"Tap the colour the word SAYS":"Read the word. Tap that colour.")+'</span><span class="word" style="color:'+(stroop?COL[ink]:"#e9edf1")+'">'+t.toUpperCase()+"</span>";
    return{type:"pick",say:a<=0?"Tap the "+t+" one.":stroop?"Tap the colour the word says, not the colour of the letters.":"Read the colour word, then tap that colour.",prompt,
      options:U.shuffle(r,cs).map(c=>({key:c,html:U.shape(U.pick(r,K),COL[c]),aria:c,say:c})),answer:t}}
  const bins=U.sample(r,NAMES,a<=0?2:a===1?3:4),cnt=a<=0?4:6,items=[];
  const order=bins.slice();while(order.length<cnt)order.push(U.pick(r,bins));
  U.shuffle(r,order).forEach(c=>items.push({key:c,html:U.shape(U.pick(r,K),COL[c],0,.75+.25*r()),aria:c}));
  return{type:"sort",say:"Put each shape in the basket with the same colour.",prompt:'<span class="ask">Match the colours</span>',
    bins:bins.map(c=>({key:c,html:'<span class="swatch" style="background:'+COL[c]+'"></span>',label:c})),items}}''')

G["sizeorder"] = ("Size Order", [["📏","The pictures are different sizes."],["👂","Listen: smallest first, or biggest first?"],["👆","Tap them in that order."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const k=a<0?(n<=15?2:3):a===0?(n<=20?3:4):a===1?(n<=15?4:5):(n<=15?5:6),desc=((a<=0&&n>25)||(a>=1&&n>10))&&i%2===1;
  const step=a<0?.32:a===0?.22:a===1?.13:.09,grid=[];for(let v=.3;v<=1.0001;v+=step)grid.push(+v.toFixed(3));
  const vals=U.sample(r,grid,Math.min(k,grid.length)),mode=a<=0?"emoji":a===1?(i%2===0?"emoji":"bar"):(i%2===0?"bar":"vbar");
  const em=U.pick(r,["🐘","🍎","⭐","🐻","🌳","🎈","🐟","🏠"]),col=U.pick(r,U.SHAPE_COLS);
  const html=v=>mode==="emoji"?'<span class="sz" style="font-size:calc(var(--ts) * '+(v*.78).toFixed(2)+')">'+em+"</span>":mode==="bar"?'<span class="sz"><i class="bar" style="width:'+Math.round(v*92)+"%;--c:"+col+'"></i></span>':
    '<span class="sz" style="display:flex;justify-content:center"><i class="vbar" style="height:'+Math.round(v*84)+"%;--c:"+col+'"></i></span>';
  const sorted=vals.map((v,j)=>({key:"v"+j,v,html:html(v)})).sort((x,y)=>desc?y.v-x.v:x.v-y.v),ans=sorted.map(t=>t.key),tiles=sorted; // mixed below
  const words=mode==="emoji"?["smallest","biggest"]:mode==="bar"?["shortest","longest"]:["shortest","tallest"],w=desc?words[1]+" to "+words[0]:words[0]+" to "+words[1];
  return{type:"order",size:86,say:"Put them in order from "+w+".",prompt:'<span class="ask">'+w[0].toUpperCase()+w.slice(1)+"</span>",tiles:U.mix(r,tiles),answer:ans}}''')

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
TS_LEARN({{id:{json.dumps(gid)},name:{json.dumps(name)},howto:{json.dumps(howto,ensure_ascii=False)},
{body}}});
}})();
</script>
</body>
</html>
'''
    (SRC / f"{gid}.html").write_text(html)
print(len(G), "games written")
