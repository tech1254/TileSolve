"""Writes the science and social studies games built on shared/learn.js: Animal Sort, Planet Order, Food Chain,
Flags & Places, Odd One Out (src/<id>.html). make(level, round, rng, a) gets a = player's grade - 1 (one grade back).
Run: python3 tools/mk_science.py  (then node tools/build.js)"""
import pathlib, json
SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
G = {}

G["animals"] = ("Animal Sort", [["🐾","Every animal belongs in one home."],["👆","Drag an animal to its home, or tap it and then tap the home."],["🐳","Careful: some are tricky! A whale is not a fish."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){
  // emoji, name, where (land/water/sky), covering, group, food
  const A=[["🐶","dog","land","fur","mammal","both"],["🐱","cat","land","fur","mammal","meat"],["🐮","cow","land","fur","mammal","plant"],["🐴","horse","land","fur","mammal","plant"],
    ["🐰","rabbit","land","fur","mammal","plant"],["🐻","bear","land","fur","mammal","both"],["🦁","lion","land","fur","mammal","meat"],["🐺","wolf","land","fur","mammal","meat"],
    ["🦌","deer","land","fur","mammal","plant"],["🐭","mouse","land","fur","mammal","both"],["🐳","whale","water","skin","mammal","meat"],["🐬","dolphin","water","skin","mammal","meat"],
    ["🦅","eagle","sky","feathers","bird","meat"],["🦉","owl","sky","feathers","bird","meat"],["🦜","parrot","sky","feathers","bird","plant"],["🐔","chicken","land","feathers","bird","both"],
    ["🐧","penguin","water","feathers","bird","meat"],["🦆","duck","water","feathers","bird","both"],["🐟","fish","water","scales","fish","both"],["🦈","shark","water","scales","fish","meat"],
    ["🐠","clownfish","water","scales","fish","both"],["🐍","snake","land","scales","reptile","meat"],["🐢","turtle","water","scales","reptile","both"],["🦎","lizard","land","scales","reptile","meat"],
    ["🐊","crocodile","water","scales","reptile","meat"],["🐸","frog","water","skin","amphibian","meat"],["🐝","bee","sky","none","insect","plant"],["🦋","butterfly","sky","none","insect","plant"],
    ["🐞","ladybug","sky","none","insect","meat"],["🐜","ant","land","none","insect","both"],["🦗","cricket","land","none","insect","both"]];
  const BIN={land:["🌳","Land"],water:["🌊","Water"],sky:["☁️","Sky"],fur:["🧶","Fur"],feathers:["🪶","Feathers"],scales:["🐉","Scales"],mammal:["🍼","Mammal"],bird:["🥚","Bird"],
    fish:["🫧","Fish"],insect:["6️⃣","Insect (6 legs)"],reptile:["☀️","Reptile"],amphibian:["💧","Amphibian"],plant:["🥬","Plant eater"],meat:["🍖","Meat eater"],both:["🍽️","Eats both"]};
  let f,bins,count,say;
  if(a<0){f=2;bins=["land","water"];count=4;say="Does it live on land or in water?"}
  else if(a===0){f=2;bins=["land","water","sky"];count=5;say="Where does it live: land, water or sky? Sky is for animals that fly."}
  else if(a===1){f=3;bins=["fur","feathers","scales"];count=6;say="What covers its body: fur, feathers or scales?"}
  else if(a===2||i%2===0){f=4;bins=a===2?["mammal","bird","fish","insect"]:U.sample(r,["mammal","bird","fish","insect","reptile","amphibian"],4);count=6;say="Sort the animals into their groups."}
  else{f=5;bins=["plant","meat","both"];count=6;say="What does it eat: plants, meat, or both?"}
  const tricky=a<=0?["duck","frog","crocodile","turtle","penguin"]:f===3?["turtle"]:[],pool=A.filter(x=>bins.includes(x[f])&&!tricky.includes(x[1])),items=[];
  // at least one in every home, then fill up
  for(const bk of U.shuffle(r,bins))items.push(U.pick(r,pool.filter(x=>x[f]===bk&&!items.includes(x))));
  for(const x of U.shuffle(r,pool))if(items.length<count&&!items.includes(x))items.push(x);
  return{type:"sort",say,prompt:'<span class="ask">'+say.split("?")[0]+(say.includes("?")?"?":"")+"</span>",
    bins:bins.map(k=>({key:k,html:BIN[k][0],label:BIN[k][1]})),items:U.shuffle(r,items).map(x=>({key:x[f],html:'<span class="lr-em">'+x[0]+"</span>",aria:x[1]}))}}''', [0,5])

G["planets"] = ("Planet Order", [["☀️","Eight planets travel around the Sun."],["👆","Tap the planets in order: closest to the Sun first."],["❓","Some rounds ask a question about space."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){
  const P=[["Mercury","#a8a29a",8],["Venus","#e3bb6f",12],["Earth","#3f86d9",12.5],["Mars","#d1583a",10],["Jupiter","#d6a06a",24],["Saturn","#e6cb83",21],["Uranus","#93dbe3",16],["Neptune","#4466e0",15.5]];
  const pic=(p,big)=>{const[nm,c,s]=p,R=big?s:Math.max(8,s*.9);let x='<circle cx="30" cy="30" r="'+R+'" fill="'+c+'"/>';
    if(nm==="Earth")x+='<path d="M22 22q6-4 10 1t-2 9q-6 2-8-4zM34 36q5-2 7 3t-5 5q-4-3-2-8z" fill="#5bb04a"/>';
    if(nm==="Jupiter")x+='<path d="M7 26h46M8 33h44M11 40h38" stroke="#a8683a" stroke-width="3" opacity=".7"/><circle cx="38" cy="36" r="3" fill="#b9512d"/>';
    if(nm==="Saturn")x='<ellipse cx="30" cy="30" rx="29" ry="8" fill="none" stroke="#b9a165" stroke-width="3"/>'+x+'<path d="M2 30a28 8 0 0 0 56 0" fill="none" stroke="#b9a165" stroke-width="3"/>';
    return'<span class="lr-planet"><svg viewBox="0 0 60 60" aria-hidden="true">'+x+"</svg><small>"+nm+"</small></span>"};
  const tile=p=>({key:p[0],html:pic(p,true),say:p[0],aria:p[0]});
  const facts=[ // [question, answer, wrong answers, from content grade]
    ["Which planet do we live on?","Earth",["Mars","Jupiter","Venus"],-1],["Which planet has big rings?","Saturn",["Earth","Mars","Mercury"],-1],
    ["Which is the red planet?","Mars",["Neptune","Earth","Uranus"],0],["Which is the biggest planet?","Jupiter",["Mercury","Earth","Mars"],0],
    ["Which planet is closest to the Sun?","Mercury",["Neptune","Earth","Saturn"],1],["Which planet is the farthest from the Sun?","Neptune",["Mercury","Mars","Earth"],1],
    ["Which planet is the hottest? Its thick clouds trap the heat.","Venus",["Mercury","Earth","Jupiter"],2],["Which planet is closest to Earth's size?","Venus",["Jupiter","Saturn","Mercury"],3],
    ["Which planet spins on its side?","Uranus",["Earth","Mars","Venus"],3]];
  const words=[["What is the Sun?","a star",["a planet","a moon","a cloud"],-1],["What goes around the Earth?","the Moon",["the Sun","Mars","Jupiter"],0],
    ["What makes day and night?","Earth spinning",["clouds","the Moon","Earth stopping"],1],["How long does Earth take to go around the Sun?","1 year",["1 day","1 week","1 month"],1],
    ["How long does Earth take to spin around once?","1 day",["1 year","1 hour","1 month"],2],["What keeps the planets going around the Sun?","gravity",["wind","magnets","rockets"],2]];
  if(i%3===2){const all=facts.filter(f=>f[3]<=a).map(f=>[f,1]).concat(words.filter(f=>f[3]<=a).map(f=>[f,0])),[[q,ans,wr],isP]=U.pick(r,all),k=a<1?3:4;
    const opts=U.shuffle(r,[ans].concat(U.sample(r,wr,k-1)));
    return{type:"pick",cols:2,say:q,prompt:'<span class="ask">'+q+"</span>",
      options:opts.map(x=>isP?{key:x,html:pic(P.find(p=>p[0]===x),true),say:x,aria:x}:{key:x,html:'<span style="font-size:22px">'+x+"</span>"}),answer:ans}}
  // order from the Sun: a few neighbours at first, all eight later
  if(a>=3&&i%3===1){const set=U.sample(r,[0,3,2,6,5,4],Math.min(6,3+Math.floor(n/10))).sort((x,y)=>P[x][2]-P[y][2]).map(k=>P[k]);
    return{type:"order",say:"Put the planets in order from smallest to biggest.",prompt:'<span class="ask">Smallest to biggest</span>',tiles:U.mix(r,set.map(tile)),answer:set.map(p=>p[0])}}
  const len=Math.min(8,(a<=0?3:a===1?4:5)+Math.floor(n/12)),s=U.ri(r,0,8-len),set=P.slice(s,s+len);
  return{type:"order",say:"Put the planets in order, starting closest to the Sun.",prompt:'<span class="ask">☀️ Closest to the Sun first</span>',tiles:U.mix(r,set.map(tile)),answer:set.map(p=>p[0])}}''', [2,7])

G["foodchain"] = ("Food Chain", [["🌱","Every food chain starts with a plant."],["➡️","Then comes the animal that eats it, then the animal that eats that."],["👆","Tap them in order, plant first."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){
  const C=[[["🌱","grass"],["🐛","caterpillar"],["🐦","bird"],["🦅","eagle"]],[["🌾","grain"],["🐭","mouse"],["🐍","snake"],["🦅","eagle"]],[["🥕","carrot"],["🐰","rabbit"],["🦊","fox"]],
    [["🍃","leaves"],["🦗","grasshopper"],["🐸","frog"],["🐍","snake"]],[["🌿","plants"],["🦌","deer"],["🐺","wolf"]],[["🌰","acorn"],["🐿️","squirrel"],["🦉","owl"]],
    [["🦠","plankton"],["🐟","fish"],["🦭","seal"],["🐻‍❄️","polar bear"]],[["🌸","flower"],["🐝","bee"],["🐦","bird"]],[["🍓","berries"],["🐭","mouse"],["🦉","owl"]],
    [["🌿","seaweed"],["🐟","fish"],["🦈","shark"]],[["🍂","leaves"],["🪱","worm"],["🐦","robin"],["🦊","fox"]],[["🌾","grass"],["🦗","cricket"],["🦎","lizard"],["🦅","hawk"]]];
  const tile=x=>({key:x[1],html:'<span class="lr-word"><b>'+x[0]+"</b>"+x[1]+"</span>",say:x[1],aria:x[1]});
  if(a>=3&&i%3===2){ // producers and consumers
    const plants=[...new Map(C.map(c=>c[0]).map(x=>[x[1],x])).values()],eaters=[...new Map(C.flatMap(c=>c.slice(1)).map(x=>[x[1],x])).values()];
    const items=U.sample(r,plants,3).concat(U.sample(r,eaters,3));
    return{type:"sort",say:"Producers make their own food from sunlight. Consumers eat other living things. Sort them!",prompt:'<span class="ask">Producer or consumer?</span>',
      bins:[{key:"p",html:"☀️",label:"Producer"},{key:"c",html:"🍽️",label:"Consumer"}],items:U.shuffle(r,items.map(x=>({key:plants.includes(x)?"p":"c",html:'<span class="lr-em">'+x[0]+"</span>",aria:x[1]})))}}
  if(i%3===1){ // what does it eat?
    const c=U.pick(r,C),k=U.ri(r,1,c.length-1),eater=c[k],food=c[k-1];
    // wrong answers can't be something it really eats: plant eaters get animals, meat eaters get plants
    const wrong=U.shuffle(r,(k===1?C.flatMap(d=>d.slice(1)):C.map(d=>d[0])).filter(x=>x[1]!==eater[1]&&!C.some(d=>d.some((y,j)=>y[1]===eater[1]&&j>0&&d[j-1][1]===x[1]))));
    const opts=[food];for(const x of wrong)if(opts.length<(a<1?3:4)&&!opts.some(o=>o[1]===x[1]))opts.push(x);
    return{type:"pick",cols:2,say:"What does the "+eater[1]+" eat?",prompt:'<span class="ask">What does it eat?</span><span class="lr-word big1"><b>'+eater[0]+"</b>"+eater[1]+"</span>",
      options:U.shuffle(r,opts).map(tile),answer:food[1]}}
  const c=U.pick(r,C.filter(c=>a>=2||c.length===3||n>15)),chain=a<=1&&c.length>3?c.slice(0,3):c;
  return{type:"order",wide:true,say:"Make the food chain. Start with the plant!",prompt:'<span class="ask">🌱 Plant first, then who eats it</span>',
    tiles:U.mix(r,chain.map(tile)),answer:chain.map(x=>x[1])}}''', [2,7])

G["places"] = ("Flags & Places", [["🇨🇦","Questions about Canada, Alberta and the world."],["👀","Look at the flag, map word or picture."],["👆","Tap the right answer."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){const opt=x=>({key:x,html:/^\p{RI}/u.test(x)?'<span style="font-size:52px;line-height:1">'+x+"</span>":'<span style="font-size:20px">'+x+"</span>",aria:x});
  const Q=[ // [question, extra picture, answer, wrong answers, from content grade]
    ["Which is Canada's flag?","","🇨🇦",["🇺🇸","🇲🇽","🇬🇧"],-1],["Which leaf is on Canada's flag?","🇨🇦","maple leaf",["clover","palm leaf","oak leaf"],-1],
    ["Which animal is a symbol of Canada?","","beaver 🦫",["kangaroo 🦘","panda 🐼","lion 🦁"],-1],["What colours are on Canada's flag?","","red and white",["blue and white","green and yellow","red and blue"],-1],
    ["Which coin has a loon on it?","","loonie",["dime","nickel","quarter"],0],["What is Canada's capital city?","","Ottawa",["Calgary","Toronto","New York"],0],
    ["Which country is Canada's neighbour?","","United States",["Australia","Japan","Brazil"],0],["Which one is a province of Canada?","","Alberta",["Texas","Paris","China"],0],
    ["Which ocean is NOT next to Canada?","","Indian Ocean",["Pacific Ocean","Atlantic Ocean","Arctic Ocean"],1],["What are Canada's two official languages?","","English and French",["English and Spanish","French and German","English and Chinese"],1],
    ["Which mountains are in Alberta?","🏔️","Rocky Mountains",["Andes","Alps","Himalayas"],1],["What is the capital city of Alberta?","","Edmonton",["Calgary","Red Deer","Banff"],2],
    ["Which city is in Alberta?","","Red Deer",["Regina","Vancouver","Winnipeg"],2],["Which province is west of Alberta?","","British Columbia",["Saskatchewan","Manitoba","Ontario"],2],
    ["Which province is east of Alberta?","","Saskatchewan",["British Columbia","Quebec","Nova Scotia"],2],["What is Alberta's flower?","🌹","wild rose",["tulip","sunflower","daisy"],2],
    ["Which national park is in Alberta?","","Banff",["Yellowstone","Gros Morne","Pacific Rim"],2],["How many provinces does Canada have?","","10",["3","5","13"],3],["How many territories does Canada have?","","3",["1","10","5"],3],
    ["Which one is a territory?","","Yukon",["Alberta","Manitoba","Ontario"],3]];
  const CAP=[["British Columbia","Victoria"],["Alberta","Edmonton"],["Saskatchewan","Regina"],["Manitoba","Winnipeg"],["Ontario","Toronto"],["Quebec","Quebec City"],["New Brunswick","Fredericton"],
    ["Nova Scotia","Halifax"],["Prince Edward Island","Charlottetown"],["Newfoundland and Labrador","St. John's"],["Yukon","Whitehorse"],["Northwest Territories","Yellowknife"],["Nunavut","Iqaluit"]];
  const FL=[["🇨🇦","Canada","North America"],["🇺🇸","United States","North America"],["🇲🇽","Mexico","North America"],["🇬🇧","United Kingdom","Europe"],["🇫🇷","France","Europe"],["🇩🇪","Germany","Europe"],
    ["🇮🇹","Italy","Europe"],["🇺🇦","Ukraine","Europe"],["🇯🇵","Japan","Asia"],["🇨🇳","China","Asia"],["🇮🇳","India","Asia"],["🇵🇭","Philippines","Asia"],["🇧🇷","Brazil","South America"],
    ["🇦🇷","Argentina","South America"],["🇰🇪","Kenya","Africa"],["🇪🇬","Egypt","Africa"],["🇿🇦","South Africa","Africa"],["🇦🇺","Australia","Oceania"],["🇳🇿","New Zealand","Oceania"]];
  const kind=a>=4?i%3:a>=3?(i%2?0:3):0;
  if(kind===1){const[c,ans]=U.pick(r,CAP),o=new Set([ans]);while(o.size<4)o.add(U.pick(r,CAP)[1]);
    return{type:"pick",cols:2,say:"What is the capital city of "+c+"?",prompt:'<span class="ask">Capital city of</span><span class="lr-sent">'+c+"</span>",options:U.shuffle(r,[...o]).map(opt),answer:ans}}
  if(kind===2){const f=U.pick(r,FL),byFlag=i%2===0,o=new Set([byFlag?f[1]:f[2]]);
    while(o.size<4)o.add(byFlag?U.pick(r,FL)[1]:U.pick(r,["North America","South America","Europe","Asia","Africa","Oceania"]));
    return byFlag?{type:"pick",cols:2,say:"Which country has this flag?",prompt:'<span class="ask">Which country has this flag?</span><span class="lr-emo">'+f[0]+"</span>",options:U.shuffle(r,[...o]).map(opt),answer:f[1]}
      :{type:"pick",cols:2,say:"Which continent is "+f[1]+" in?",prompt:'<span class="ask">Which continent is '+f[1]+" in?</span><span class=\"lr-emo\">"+f[0]+"</span>",options:U.shuffle(r,[...o]).map(opt),answer:f[2]}}
  if(kind===3){const f=U.pick(r,FL.slice(0,10)),o=new Set([f[0]]);while(o.size<4)o.add(U.pick(r,FL.slice(0,12))[0]);
    return{type:"pick",cols:2,say:"Which flag belongs to "+f[1]+"?",prompt:'<span class="ask">Which is the flag of '+f[1]+"?</span>",options:U.shuffle(r,[...o]).map(opt),answer:f[0]}}
  const pool=Q.filter(q=>q[4]<=a&&q[4]>=Math.min(a,3)-2),[q,pic,ans,wr]=U.pick(r,pool),k=a<1?3:4;
  return{type:"pick",cols:2,say:q.replace("NOT","not"),prompt:'<span class="ask">'+q+"</span>"+(pic?'<span class="lr-emo">'+pic+"</span>":""),
    options:U.shuffle(r,[ans].concat(U.sample(r,wr,k-1))).map(opt),answer:ans}}''', [2,7])

G["oddone"] = ("Odd One Out", [["🔍","Look at all the pictures."],["🤔","Three belong together. One doesn't!"],["👆","Tap the one that doesn't belong."],["🔊","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){
  const C=[["fruit","🍎🍌🍇🍓🍊🍐🍉🍒"],["vegetables","🥕🥦🌽🥔🥒🍆"],["animals","🐶🐱🐭🐰🐻🦊🐮🐷"],["vehicles","🚗🚌🚲🚂🚜🚒🚓"],["clothes","👕👖🧦🧢👟🧤🧣"],
    ["sea animals","🐟🐙🦀🐳🐬🦈"],["things that fly","✈️🚁🎈🪁🚀🛸"],["weather","☀️🌧️❄️⛈️🌈🌪️"],["sports balls","⚽🏀🏈⚾🎾🏐"],["music","🎸🥁🎺🎹🎻🪇"],
    ["treats","🍰🍩🍪🍦🍫🧁"],["tools","🔨🪛🪚🔧🪓"]].map(([n,s])=>[n,[...new Intl.Segmenter().segment(s)].map(x=>x.segment)]);
  const near={fruit:"vegetables",vegetables:"fruit",animals:"sea animals","sea animals":"animals","things that fly":"vehicles",treats:"fruit",clothes:"sports balls",tools:"music"};
  const k=a<0?3:4;
  if(a>=2&&i%2===1){ // numbers
    let set,odd,why;const t=a>=4?U.ri(r,0,3):U.ri(r,0,2);
    if(t===0){const ev=U.sample(r,Array.from({length:a>=3?45:15},(_,j)=>2*j+2),3);set=ev;odd=2*U.ri(r,1,a>=3?45:15)+1;why="even numbers"}
    else if(t===1){set=U.sample(r,Array.from({length:a>=3?20:10},(_,j)=>5*j+5),3);do odd=U.ri(r,6,a>=3?99:49);while(odd%5===0);why="counting by 5s"}
    else if(t===2){set=U.sample(r,Array.from({length:9},(_,j)=>10*j+10),3);do odd=U.ri(r,11,99);while(odd%10===0);why="tens"}
    else{set=U.sample(r,Array.from({length:12},(_,j)=>3*j+3),3);do odd=U.ri(r,4,36);while(odd%3===0);why="the 3 times table"}
    return{type:"pick",cols:2,say:"Which number does not belong?",prompt:'<span class="ask">Which number does not belong?</span>',
      options:U.shuffle(r,set.concat([odd])).map(v=>({key:v,html:String(v),say:v===odd?"Yes! The others are "+why+".":String(v)})),answer:odd}}
  if(a>=3&&i%3===2){ // words
    const W=[["big","huge","giant","tiny"],["happy","glad","cheerful","sad"],["run","jump","skip","apple"],["red","blue","green","chair"],["cold","icy","frozen","hot"],
      ["quick","fast","speedy","slow"],["Monday","Friday","Sunday","March"],["circle","square","triangle","seven"],["cat","dog","horse","carrot"],["shout","yell","scream","whisper"]];
    const w=U.pick(r,W);return{type:"pick",cols:2,say:"Which word does not belong? "+U.shuffle(r,w).join(", "),prompt:'<span class="ask">Which word does not belong?</span>',
      options:U.shuffle(r,w).map(x=>({key:x,html:'<span style="font-size:24px">'+x+"</span>"})),answer:w[3]}}
  const[g,list]=U.pick(r,C),oddFrom=a>=1&&near[g]&&r()<.6?C.find(c=>c[0]===near[g]):U.pick(r,C.filter(c=>c[0]!==g&&c[0]!==near[g]&&near[c[0]]!==g));
  const same=U.sample(r,list,k-1),odd=U.pick(r,oddFrom[1].filter(x=>!list.includes(x)));
  return{type:"pick",cols:2,say:"Which one does not belong?",prompt:'<span class="ask">Which one does not belong?</span>',
    options:U.shuffle(r,same.concat([odd])).map(x=>({key:x,html:'<span style="font-size:56px;line-height:1">'+x+"</span>",say:x===odd?"Yes! The others are all "+g+".":""})),answer:odd}}''', [0,5])

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
print(len(G), "games written:", ", ".join(G))
