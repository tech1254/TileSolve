"""Writes the science and social studies games built on shared/learn.js: Animal Sort, Planet Order, Food Chain,
Flags & Places, Odd One Out (src/<id>.html). make(level, round, rng, a) gets a = player's grade - 1 (one grade back).
Run: python3 tools/mk_science.py  (then node tools/build.js)"""
import pathlib, json
SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
G = {}

G["animals"] = ("Animal Sort", [["🐾","Lots of ways to learn about animals: how they move, what they eat, their babies, and what they do in winter."],["👆","Drag an animal to its home, or tap it and then tap the home. Some rounds you tap the right answer."],["🐳","Careful: some are tricky! A whale is not a fish."],["🔊","Tap the speaker to hear it again."]],
r"""make(n,i,r,a){const unsort=(t,ans)=>{let s;do s=U.shuffle(r,t);while(s.map(x=>x.key).join()===ans.join());return s};
  /* Research plan (research/animals-science.md): one feature per question for pre-K and K, typical animals first, then tricky ones
     that explain themselves (a whale is a mammal, a bat isn't a bird, a penguin is a bird, a spider isn't an insect).
     Pre-K: fly or walk, sounds, babies and parents, wings. K: fly/walk/swim, why animals move (Alberta K), is it an animal, alive or not.
     Grade 1: + hop and slither, Alberta winter (sleep, fly south, stay active), animal groups, habitats, legs, "both" (Venn).
     Grade 2: life cycles, more groups, insects vs spiders, what they eat. */
  const it=(key,x)=>({key,html:'<span class="lr-em">'+x[0]+"</span>",aria:x[1],say:x[2]||"",why:x[3]||""});
  const bin=(key,em,label)=>({key,html:em,label});
  // at least one animal in every home, one tricky one when given, then fill up
  const fill=(pools,cnt,tricky)=>{const keys=Object.keys(pools),out=[],used=new Set();
    for(const k of U.shuffle(r,keys)){const x=U.pick(r,pools[k]);out.push(it(k,x));used.add(x[1])}
    const tr=(tricky||[]).filter(t=>pools[t[0]]&&!used.has(t[2]));if(tr.length){const t=U.pick(r,tr);out.push(it(t[0],t.slice(1)));used.add(t[2])}
    for(const[k,x] of U.shuffle(r,keys.flatMap(k=>pools[k].map(x=>[k,x])))){if(out.length>=cnt)break;if(!used.has(x[1])){out.push(it(k,x));used.add(x[1])}}return U.shuffle(r,out)};
  const sort=(say,bins,items)=>({type:"sort",say,prompt:'<span class="ask">'+say+"</span>",bins,items});
  const big=h=>'<span style="font-size:clamp(40px,12vw,56px);line-height:1">'+h+"</span>";
  const MOVE={fly:[["🦅","eagle"],["🦉","owl"],["🐝","bee"],["🦋","butterfly"],["🐦","bird"],["🦜","parrot"]],walk:[["🐄","cow"],["🐕","dog"],["🐘","elephant"],["🐎","horse"],["🦒","giraffe"],["🐖","pig"],["🐑","sheep"]],
    swim:[["🐟","fish"],["🐋","whale"],["🐙","octopus"],["🦈","shark"],["🐬","dolphin"],["🐠","tropical fish"]],hop:[["🐇","rabbit"],["🐸","frog"],["🦘","kangaroo"],["🦗","cricket"]],
    slither:[["🐍","snake"],["🪱","worm"],["🐌","snail","Yes! A snail slides along on its foot."]]};
  const MB={fly:["🪽","Fly"],walk:["🦶","Walk"],swim:["🌊","Swim"],hop:["🐾","Hop"],slither:["〰️","Slither"]};
  const MTRICK=[["walk","🐔","hen","Yes! A hen has wings, but it mostly walks.","~A hen has wings, but it mostly walks."],["swim","🐧","penguin","Yes! A penguin is a bird that can't fly. It swims!","~A penguin is a bird, but it can't fly. It swims!"],
    ["fly","🦇","bat","Yes! A bat flies, but it isn't a bird.","~A bat flies at night!"]];
  const moveRound=(keys,cnt,trick)=>{const P={};keys.forEach(k=>P[k]=MOVE[k]);return sort(keys.length===2?"Does it fly or walk?":"How does it mostly get around?",keys.map(k=>bin(k,MB[k][0],MB[k][1])),fill(P,cnt,trick?MTRICK:null))};
  const GROUP={mammal:[["🐕","dog"],["🐄","cow"],["🐎","horse"],["🐻","bear"],["🦁","lion"],["🐇","rabbit"]],bird:[["🦅","eagle"],["🦉","owl"],["🦜","parrot"],["🐔","hen"],["🦆","duck"]],
    fish:[["🐟","fish"],["🦈","shark"],["🐠","clownfish"]],insect:[["🐝","bee"],["🐞","ladybug"],["🐜","ant"],["🦗","cricket"]],reptile:[["🐍","snake"],["🦎","lizard"],["🐊","crocodile"],["🐢","turtle"]],
    amphibian:[["🐸","frog","Yes! A frog starts life in the water, then lives on land."],["🦎","salamander"]]};
  const GB={mammal:["🍼","Mammal"],bird:["🥚","Bird"],fish:["🫧","Fish"],insect:["6️⃣","Insect (6 legs)"],reptile:["☀️","Reptile"],amphibian:["💧","Amphibian"]};
  const GTRICK=[["mammal","🐋","whale","Yes! A whale breathes air and feeds its baby milk. It's a mammal.","~A whale lives in water, but it breathes air and feeds its baby milk. It's a mammal, not a fish!"],
    ["mammal","🦇","bat","Yes! A bat has fur and feeds its baby milk. It's a mammal.","~A bat flies, but it has fur and feeds its baby milk. It's a mammal, not a bird!"],
    ["bird","🐧","penguin","Yes! A penguin can't fly, but it has feathers. It's a bird.","~A penguin can't fly, but it has feathers and lays eggs. It's a bird!"],
    ["insect","🦋","butterfly","Yes! A butterfly has 6 legs. It's an insect.","~A butterfly has wings, but it isn't a bird. It has 6 legs, so it's an insect!"],
    ["mammal","🐬","dolphin","Yes! A dolphin breathes air. It's a mammal.","~A dolphin swims, but it breathes air and feeds its baby milk. It's a mammal, not a fish!"]];
  const groupRound=keys=>{const P={};keys.forEach(k=>P[k]=GROUP[k].filter(x=>!(k==="amphibian"&&x[1]==="salamander"&&keys.includes("reptile"))));
    return sort("Which group does it belong to?",keys.map(k=>bin(k,GB[k][0],GB[k][1])),fill(P,6,GTRICK))};
  const WINTER={sleep:[["🐻","bear","Yes! Bears sleep in a den all winter."],["🦇","little brown bat","Yes! Bats sleep through the winter in caves."],["🐸","wood frog","Yes! Wood frogs sleep under the leaves. They even freeze solid!"],["🐍","garter snake","Yes! Garter snakes sleep together in big dens."]],
    away:[["🦢","trumpeter swan"],["🦆","duck"],["🐦","robin"],["🦋","monarch butterfly","Yes! Monarch butterflies fly all the way to Mexico."],["🪿","Canada goose","Yes! Geese fly south in a V."]],
    stay:[["🫎","moose","Yes! Moose eat twigs all winter."],["🦬","bison","Yes! Bison push the snow with their heads to find grass."],["🐺","wolf"],["🦊","fox"],["🦉","owl"],["🐿️","red squirrel","Yes! Red squirrels store cones to eat."],["🦫","beaver","Yes! Beavers keep branches under the ice to eat."],["🐇","snowshoe hare","Yes! Snowshoe hares turn white for winter."],["🦌","deer"]]};
  const HAB={forest:[["🫎","moose"],["🐻","black bear"],["🦉","owl"],["🐿️","red squirrel"]],prairie:[["🦬","bison"],["🦡","badger"],["🦗","grasshopper"]],mountains:[["🐐","mountain goat"],["🐏","bighorn sheep"]],pond:[["🦫","beaver"],["🐸","frog"],["🦆","duck"],["🐟","trout"]]};
  const HB={forest:["🌲","Forest"],prairie:["🌾","Prairie"],mountains:["⛰️","Mountains"],pond:["💧","Pond and lake"]};
  const FOOD={plant:[["🐄","cow"],["🐎","horse"],["🐇","rabbit"],["🦌","deer"],["🐑","sheep"],["🦒","giraffe"],["🐘","elephant"]],meat:[["🦁","lion"],["🐺","wolf"],["🦈","shark"],["🦅","eagle"],["🦉","owl"],["🐍","snake"]],
    both:[["🐻","bear","Yes! Bears eat berries and fish."],["🐔","hen"],["🐕","dog"],["🐭","mouse"],["🦝","raccoon"]]};
  let kinds;
  if(a<0)kinds=["move","sound","baby","wings","where"];
  else if(a===0)kinds=["move","why","animal","baby","alive","diet","where"];
  else if(a===1)kinds=["move","winter","group","venn","habitat","legs","baby","covering"];
  else if(a===2)kinds=["life","group","diet","winter","insects","venn","habitat"];
  else kinds=["group","diet","life","winter","venn"];
  const K=kinds[(i+(n-1)*3)%kinds.length];
  if(K==="move")return a<0?moveRound(["fly","walk"],4):a===0?moveRound(["fly","walk","swim"],5,true):moveRound(U.sample(r,["fly","walk","swim","hop","slither"],4),6,true);
  if(K==="where"){const W={land:[["🐕","dog"],["🐈","cat"],["🐄","cow"],["🐎","horse"],["🐇","rabbit"],["🐻","bear"]],water:[["🐟","fish"],["🦈","shark"],["🐙","octopus"],["🐬","dolphin"],["🦀","crab"]],sky:[["🦅","eagle"],["🦉","owl"],["🐝","bee"],["🦋","butterfly"],["🦜","parrot"]]};
    const keys=a<0?["land","water"]:["land","water","sky"],P={};keys.forEach(k=>P[k]=W[k]);
    return sort(a<0?"Does it live on land or in water?":"Where does it live: land, water or sky?",keys.map(k=>bin(k,{land:"🌳",water:"🌊",sky:"☁️"}[k],{land:"Land",water:"Water",sky:"Sky"}[k])),fill(P,a<0?4:5))}
  if(K==="sound"){const S=[["moo","🐄","cow"],["oink","🐖","pig"],["baa","🐑","sheep"],["neigh","🐎","horse"],["woof","🐕","dog"],["meow","🐈","cat"],["quack","🦆","duck"],["cluck","🐔","hen"],["hoot","🦉","owl"],["buzz","🐝","bee"],["ribbit","🐸","frog"],["howl","🐺","wolf"]];
    const t=U.pick(r,S),opts=[t].concat(U.sample(r,S.filter(x=>x!==t),2));
    return{type:"pick",cols:3,say:"Who says "+t[0]+"?",prompt:'<span class="ask">Who says <b>'+t[0]+"</b>?</span>",options:U.shuffle(r,opts).map(x=>({key:x[2],html:big(x[1]),say:x===t?"Yes! The "+x[2]+" says "+x[0]+"!":"a "+x[2]})),answer:t[2]}}
  if(K==="baby"){const FARM=[["calf","🐄","cow"],["lamb","🐑","sheep"],["foal","🐎","horse"],["piglet","🐖","pig"],["puppy","🐕","dog"],["kitten","🐈","cat"],["chick","🐔","hen","🐣"],["duckling","🦆","duck"]],
      WILD=[["cub","🐻","bear"],["fawn","🦌","deer"],["kit","🦊","fox"],["joey","🦘","kangaroo"],["elephant calf","🐘","elephant"]],
      TRICK=[["caterpillar","🦋","butterfly","🐛","Yes! A caterpillar grows up to be a butterfly."],["tadpole","🐸","frog",U.stage("tadpole"),"Yes! A tadpole grows up to be a frog."]];
    const pool=a<0?FARM:a===0?FARM.concat(WILD):FARM.concat(WILD,TRICK,TRICK),t=U.pick(r,pool),others=U.sample(r,FARM.concat(WILD).filter(x=>x[2]!==t[2]),a<0?2:3);
    return{type:"pick",cols:a<0?3:2,say:"Who is the "+t[0]+"'s mom?",prompt:'<span class="ask">Who is the <b>'+t[0]+"</b>'s mom?</span><span class=\"lr-emo\">"+(t[3]||U.baby(t[1]))+"</span>",
      options:U.shuffle(r,[t].concat(others)).map(x=>({key:x[2],html:big(x[1]),say:x===t?(t[4]||"Yes! A "+t[0]+" grows up to be a "+t[2]+"."):"a "+x[2]})),answer:t[2]}}
  if(K==="wings"||K==="animal"||K==="insects"){
    const SETS={wings:[[["🦅","eagle"],["🦉","owl"],["🐝","bee"],["🦋","butterfly"],["🐔","hen"],["🦆","duck"],["🐦","bird"]],[["🐄","a cow, with no wings"],["🐕","a dog, with no wings"],["🐟","a fish, with no wings"],["🐍","a snake, with no wings"],["🐇","a rabbit, with no wings"],["🐘","a elephant, with no wings"]],"Tap all the animals with wings."],
      animal:[[["🐜","ant"],["🐟","fish"],["🐦","bird"],["🧒","child"],["🐞","ladybug"],["🐍","snake"],["🐄","cow"]],[["🌳","~A tree is alive, but it's a plant, not an animal."],["🪨","a rock. It isn't alive"],["🚗","a car. It isn't alive"],["🧸","a teddy bear. It's a toy"],["🌻","~A sunflower is alive, but it's a plant, not an animal."],["🤖","a robot. It's a machine"]],"Tap all the animals. People are animals too!"],
      insects:[[["🐝","bee"],["🐞","ladybug"],["🐜","ant"],["🦋","butterfly"],["🦗","cricket"],["🪲","beetle"]],[["🕷️","~A spider has 8 legs. It isn't an insect!"],["🪱","~A worm has no legs. It isn't an insect."],["🐌","a snail. It has no legs"],["🐦","a bird. It has 2 legs"]],"Tap all the insects. Insects have 6 legs."]};
    const[yes,no,say]=SETS[K],T=K==="wings"&&a<0?3:4,N=Math.min(K==="wings"&&a<0?6:9,T+no.length),cells=[];
    const ys=U.sample(r,yes,T);if(K==="animal"&&!ys.some(x=>x[1]==="child")&&r()<.6)ys[0]=yes[3];
    ys.forEach(x=>cells.push({html:big(x[0]),ok:true,aria:x[1]}));
    const nos=U.shuffle(r,no);while(cells.length<N){const x=nos[(cells.length-T)%nos.length];cells.push({html:big(x[0]),ok:false,aria:"picture",why:x[1]})}
    return{type:"hunt",cols:3,say,prompt:'<span class="ask">'+say+"</span>",cells:U.shuffle(r,cells)}}
  if(K==="why"){const SC=[["🦉","🐁","The owl flies after a mouse.","food"],["🐻","🐟","The bear goes to the river to catch a fish.","food"],["🐝","🌸","The bee flies to a flower.","food"],["🐇","🦊","The rabbit runs away from the fox.","danger"],
      ["🐿️","🦅","The squirrel runs up a tree, away from the eagle.","danger"],["🐟","🦈","The little fish swims away from the shark.","danger"],["🐕","⚽","The puppy runs after a ball.","play"],["🐬","🐬","The dolphins jump and splash together.","play"],
      ["🐈","🧶","The kitten chases the yarn.","play"],["🦌","💧","The deer walks to the lake for a drink.","water"],["🐘","💧","The elephant walks to the water hole for a drink.","water"]];
    const REA={food:["🍎","to find food"],water:["💧","to get a drink"],play:["⚽","to play"],danger:["🏃","to get away from danger"]},t=U.pick(r,SC);
    return{type:"pick",cols:2,say:t[2]+" Why is it moving?",prompt:'<span class="ask">Why is it moving?</span><span class="lr-scene">'+t[0]+'<span class="why">💨</span>'+t[1]+"</span>",
      options:Object.keys(REA).map(k=>({key:k,html:big(REA[k][0])+'<span style="display:block;font-size:15px">'+REA[k][1]+"</span>",say:k===t[3]?"Yes! "+REA[k][1].replace(/^to/,"It wants to")+".":REA[k][1]})),answer:t[3]}}
  if(K==="alive")return sort("Is it alive?",[bin("yes","💚","Alive"),bin("no","⛔","Not alive")],fill({
      yes:[["🐶","dog"],["🐦","bird"],["🐟","fish"],["🌻","sunflower","Yes! Plants are alive too. They grow and need water.","~A sunflower is alive! Plants grow and need water."],["🌳","tree","Yes! Trees are alive. They grow.","~A tree is alive! It grows and needs water."],["🧒","child"],["🐞","ladybug"]],
      no:[["🧸","teddy bear"],["🤖","robot","","~A robot moves, but it isn't alive."],["🚗","car","","~A car moves, but it isn't alive."],["☁️","cloud"],["🔥","fire","Right! Fire moves, but it isn't alive.","~Fire moves, but it isn't alive."],["🪨","rock"],["⚽","ball"]]},6));
  if(K==="diet"){const keys=a<=0?["plant","meat"]:["plant","meat","both"],P={};keys.forEach(k=>P[k]=FOOD[k]);
    return sort(keys.length===2?"Does it eat plants or meat?":"What does it eat: plants, meat, or both?",keys.map(k=>bin(k,{plant:"🥬",meat:"🍖",both:"🍽️"}[k],{plant:"Plants",meat:"Meat",both:"Both"}[k])),fill(P,6))}
  if(K==="winter")return sort("What do these Alberta animals do in winter?",[bin("sleep","😴","Sleep all winter"),bin("away","✈️","Fly south"),bin("stay","❄️","Stay active")],fill(WINTER,6));
  if(K==="habitat"){const keys=U.sample(r,Object.keys(HAB),a===1?3:4),P={};keys.forEach(k=>P[k]=HAB[k]);return sort("Where does it live in Alberta?",keys.map(k=>bin(k,HB[k][0],HB[k][1])),fill(P,6))}
  if(K==="group")return groupRound(a===1?["mammal","bird","fish","insect"]:U.sample(r,Object.keys(GROUP),4));
  if(K==="covering"){const C={fur:[["🐕","dog"],["🐻","bear"],["🐇","rabbit"],["🦊","fox"]],feathers:[["🦅","eagle"],["🦉","owl"],["🐔","hen"],["🐧","penguin"]],scales:[["🐟","fish"],["🐍","snake"],["🦎","lizard"],["🦈","shark"]]};
    return sort("What covers its body?",[bin("fur","🧶","Fur"),bin("feathers","🪶","Feathers"),bin("scales","🐉","Scales")],fill(C,6))}
  if(K==="legs"){const L=[["🐔","hen",2],["🦆","duck",2],["🐧","penguin",2],["🐕","dog",4],["🐄","cow",4],["🦎","lizard",4],["🐞","ladybug",6],["🐜","ant",6],["🐝","bee",6],["🕷️","spider",8],["🐍","snake",0],["🐟","fish",0],["🪱","worm",0]];
    const t=U.pick(r,L),opts=U.shuffle(r,[t[2]].concat(U.sample(r,[0,2,4,6,8].filter(x=>x!==t[2]),3)));
    return{type:"pick",cols:2,say:"How many legs does the "+t[1]+" have?",prompt:'<span class="ask">How many legs?</span><span class="lr-emo">'+t[0]+"</span>",
      options:opts.map(x=>({key:x,html:String(x),say:x===t[2]?"Yes! A "+t[1]+" has "+(x||"no")+" legs.":String(x)})),answer:t[2]}}
  if(K==="venn"){if(a===1)return sort("Can it fly? Can it swim?",[bin("both","🪽🌊","Flies and swims"),bin("fly","🪽","Only flies"),bin("swim","🌊","Only swims"),bin("none","🚫","Neither")],fill({
      both:[["🦆","duck","Yes! Ducks fly and swim."],["🦢","swan","Yes! Swans fly and swim."]],fly:[["🦅","eagle"],["🐝","bee"],["🦋","butterfly"]],swim:[["🐟","fish"],["🐋","whale"],["🐙","octopus"]],none:[["🐌","snail"],["🐜","ant"],["🦔","hedgehog"]]},6));
    return sort("Where does it live, and how does it breathe?",[bin("air","🐋","In water, breathes air"),bin("gills","🐟","In water, breathes with gills"),bin("land","🌳","On land")],fill({
      air:[["🐋","whale","Yes! Whales come up to breathe air."],["🐬","dolphin","Yes! Dolphins breathe air through a blowhole."],["🦭","seal"],["🐢","sea turtle"]],gills:[["🐟","fish"],["🦈","shark"],["🐠","clownfish"]],land:[["🐄","cow"],["🐕","dog"],["🦒","giraffe"]]},6))}
  if(K==="life"){const CY={butterfly:[["🥚","egg"],["🐛","caterpillar"],[U.stage("chrysalis"),"chrysalis"],["🦋","butterfly"]],frog:[[U.stage("frogspawn"),"eggs"],[U.stage("tadpole"),"tadpole"],[U.stage("froglet"),"froglet"],["🐸","frog"]],
      hen:[["🥚","egg"],["🐣","hatching chick"],["🐤","chick"],["🐔","hen"]],bean:[["🫘","seed"],["🌱","sprout"],["🪴","young plant"],["🫛","plant with bean pods"]]};
    // pair a big change (butterfly, frog) with a simple one (hen, bean) so it's clear every living thing has a life cycle
    const nm=i%2?U.pick(r,["hen","bean"]):U.pick(r,["butterfly","frog"]),st=CY[nm];
    return{type:"order",size:72,say:"Put the "+nm+"'s life cycle in order. Start at the beginning.",prompt:'<span class="ask">The '+nm+"'s life cycle: put it in order</span>",
      tiles:unsort(st.map(x=>({key:x[1],html:(x[0][0]==="<"?x[0]:'<span class="lr-em">'+x[0]+"</span>")+'<small style="display:block;font-size:11px">'+x[1]+"</small>",say:x[1],aria:x[1]})),st.map(x=>x[1])),answer:st.map(x=>x[1])}}
  return moveRound(["fly","walk"],4)}""", [0,5])

G["senses"] = ("Five Senses", [["👀","We learn about the world with our five senses: see, hear, smell, taste and touch."],["👆","Tap the right body part, or sort things by the sense you'd use."],["🦉","Later: which animals have super senses?"],["🔊","Tap the speaker to hear it again."]],
r"""make(n,i,r,a){
  /* Alberta K: environments and objects are explored with the five senses. Pre-K: which body part? K: sort by sense, soft/loud hunts. Grade 1+: animals' super senses. */
  const SN={see:["👀","eyes","see"],hear:["👂","ears","hear"],smell:["👃","nose","smell"],taste:["👅","tongue","taste"],touch:["✋","hands","feel"]};
  const TH={see:[["🌈","the rainbow"],["🎆","the fireworks"],["⭐","the stars"]],hear:[["🔔","the bell"],["🥁","the drum"],["🎺","the trumpet"]],smell:[["🌸","the flower"],["🧄","the garlic"],["🍞","fresh bread"]],
    taste:[["🍋","the lemon"],["🍦","the ice cream"],["🍯","the honey"]],touch:[["🧸","the soft teddy"],["🧊","the cold ice"],["🌵","the prickly cactus"]]};
  const big=h=>'<span style="font-size:clamp(40px,12vw,56px);line-height:1">'+h+"</span>",k=a<0?3:4;
  const part=()=>{const s=U.pick(r,Object.keys(SN)),t=U.pick(r,TH[s]),opts=U.shuffle(r,[s].concat(U.sample(r,Object.keys(SN).filter(x=>x!==s),k-1)));
    return{type:"pick",cols:a<0?3:2,say:"What do you use to "+SN[s][2]+" "+t[1]+"?",prompt:'<span class="ask">What do you use to <b>'+SN[s][2]+"</b> "+t[1]+"?</span><span class=\"lr-emo\">"+t[0]+"</span>",
      options:opts.map(x=>({key:x,html:big(SN[x][0])+'<span style="display:block;font-size:15px">'+SN[x][1]+"</span>",say:x===s?"Yes! You "+SN[s][2]+" with your "+SN[s][1]+".":"your "+SN[x][1]})),answer:s}};
  if(a<0)return part();
  const K=a===0?["part","sort","hunt"][i%3]:["animal","sort","hunt","animal"][i%4];
  if(K==="part")return part();
  if(K==="sort"){const keys=U.sample(r,Object.keys(SN),a===0?3:4),items=[];
    for(const s of keys)for(const t of U.sample(r,TH[s],keys.length===3?2:1))items.push({key:s,html:'<span class="lr-em">'+t[0]+"</span>",aria:t[1].replace(/^the /,"")});
    while(items.length<6){const s=U.pick(r,keys),t=U.pick(r,TH[s]);if(!items.some(x=>x.aria===t[1].replace(/^the /,"")))items.push({key:s,html:'<span class="lr-em">'+t[0]+"</span>",aria:t[1].replace(/^the /,"")})}
    return{type:"sort",say:"Which sense would you use most?",prompt:'<span class="ask">Which sense would you use?</span>',bins:keys.map(s=>({key:s,html:SN[s][0],label:SN[s][2]})),items:U.shuffle(r,items)}}
  if(K==="hunt"){const H=U.pick(r,[["soft",[["🧸","teddy"],["🪶","feather"],["🧶","yarn"],["🐑","sheep's wool"],["🧦","sock"]],[["🪨","rock: it's hard"],["🔨","hammer: it's hard"],["🧱","brick: it's hard"],["🥥","coconut: it's hard"]]],
      ["loud",[["🥁","drum"],["🚒","fire truck"],["🎺","trumpet"],["📯","horn"],["🦁","lion's roar"]],[["🪶","feather: it's quiet"],["🐌","snail: it's quiet"],["🦋","butterfly: it's quiet"],["📖","book: it's quiet"]]],
      ["sweet",[["🍦","ice cream"],["🍯","honey"],["🍓","strawberry"],["🍬","candy"]],[["🍋","lemon: it's sour"],["🧂","salt: it's salty"],["🥨","pretzel: it's salty"],["🧄","garlic"]]]]);
    const cells=U.sample(r,H[1],4).map(x=>({html:big(x[0]),ok:true,aria:x[1]})).concat(U.sample(r,H[2],4).map(x=>({html:big(x[0]),ok:false,aria:x[1].split(":")[0],why:x[1]})));
    return{type:"hunt",cols:4,say:"Tap all the "+H[0]+" things.",prompt:'<span class="ask">Tap all the <b>'+H[0]+"</b> things</span>",cells:U.shuffle(r,cells)}}
  const A=[["🦉","owl","spot a mouse at night with its huge eyes"],["🐕","dog","smell things far away"],["🦅","eagle","see a mouse from high in the sky"],["🐍","snake","smell with its tongue"],["🦇","bat","find its way in the dark by listening to echoes"]];
  const t=U.pick(r,A),opts=U.shuffle(r,[t].concat(U.sample(r,A.filter(x=>x!==t),3)));
  return{type:"pick",cols:2,say:"Which animal can "+t[2]+"?",prompt:'<span class="ask">Which animal can '+t[2]+"?</span>",
    options:opts.map(x=>({key:x[1],html:big(x[0]),say:x===t?"Yes! The "+x[1]+" can "+x[2]+".":"the "+x[1]})),answer:t[1]}}""", [0,3])

G["seasons"] = ("Seasons in Alberta", [["🍂","Winter, spring, summer and fall: Alberta has all four!"],["👆","Tap the right season, sort things, or put them in order."],["🌬️","Later: chinooks, and why winter is cold."],["🔊","Tap the speaker to hear it again."]],
r"""make(n,i,r,a){const unsort=(t,ans)=>{let s;do s=U.shuffle(r,t);while(s.map(x=>x.key).join()===ans.join());return s};
  /* Alberta grade 1 Earth Systems (seasonal changes and how they affect plants and animals), K "environments change over time",
     grade 2 Earth and Sun. Pre-K names the season; K dresses for the weather and orders the seasons; grade 1 signs of fall and winter, chinooks;
     grade 2 why winter is colder and the parts of a day. */
  const SE={winter:["❄️","winter",["☃️","⛸️","🛷","🧣"]],spring:["🌷","spring",["🌧️","🐣","🌱","🌈"]],summer:["☀️","summer",["🏖️","🍉","🏊","🍦"]],fall:["🍂","fall",["🎃","🍁","🍎","🌰"]]};
  const big=h=>'<span style="font-size:clamp(38px,11vw,52px);line-height:1">'+h+"</span>",L=["winter","spring","summer","fall"];
  const which=()=>{const s=U.pick(r,L),pics=U.sample(r,SE[s][2],2).join(" "),opts=a<0?U.shuffle(r,[s].concat(U.sample(r,L.filter(x=>x!==s),2))):L;
    return{type:"pick",cols:2,say:"Which season is it?",prompt:'<span class="ask">Which season is it?</span><span class="lr-emo">'+pics+"</span>",
      options:opts.map(x=>({key:x,html:big(SE[x][0])+'<span style="display:block;font-size:15px">'+x+"</span>",say:x===s?"Yes! It's "+s+".":x})),answer:s}};
  if(a<0)return which();
  const K=a===0?["which","clothes","loop"][i%3]:a===1?["signs","chinook","loop","signs","clothes"][i%5]:["why","day","signs","chinook"][i%4];
  if(K==="which")return which();
  if(K==="clothes")return{type:"sort",say:"What would you wear? Sort them: cold day or hot day.",prompt:'<span class="ask">Cold day or hot day?</span>',bins:[{key:"cold",html:"🥶",label:"Cold day"},{key:"hot",html:"🥵",label:"Hot day"}],
    items:U.shuffle(r,U.sample(r,[["🧤","mittens"],["🧣","scarf"],["🥾","boots"],["🧥","coat"]],3).map(x=>({key:"cold",html:'<span class="lr-em">'+x[0]+"</span>",aria:x[1]})).concat(
      U.sample(r,[["🩳","shorts"],["🕶️","sunglasses"],["👒","sun hat"],["🩴","flip flops"]],3).map(x=>({key:"hot",html:'<span class="lr-em">'+x[0]+"</span>",aria:x[1]}))))};
  if(K==="loop"){const st=U.ri(r,0,3),seq=[0,1,2,3].map(k=>L[(st+k)%4]);
    return{type:"order",size:72,say:"Start with "+seq[0]+". Put the seasons in order.",prompt:'<span class="ask">Start with '+seq[0]+": what comes next?</span>",
      tiles:unsort(L.map(x=>({key:x,html:'<span class="lr-em">'+SE[x][0]+'</span><small style="display:block;font-size:11px">'+x+"</small>",say:x})),seq),answer:seq}}
  if(K==="signs"){const s=U.pick(r,["fall","winter","spring"]),SG={fall:[["🍂","leaves change colour and fall"],["🦆","ducks fly south"],["🎃","pumpkins are ready"],["🐿️","squirrels store food"],["🍎","apples are picked"]],
      winter:[["❄️","snow falls"],["⛸️","ponds freeze for skating"],["🦊","foxes grow thick fur"],["🌑","it gets dark early"],["⛄","snowmen"]],spring:[["🌷","flowers come up"],["🐣","baby animals are born"],["🌧️","rain showers"],["🦆","ducks come back"],["🌱","seeds sprout"]]};
    const other=L.filter(x=>x!==s).flatMap(x=>(SG[x]||SE[x][2].map(e=>[e,""])).map(y=>[y[0],x])).filter(y=>!SG[s].some(z=>z[0]===y[0]));
    const cells=U.sample(r,SG[s],4).map(x=>({html:big(x[0]),ok:true,aria:x[1]})).concat(U.sample(r,other,4).map(x=>({html:big(x[0]),ok:false,aria:"picture",why:"a sign of "+x[1]})));
    return{type:"hunt",cols:4,say:"Tap all the signs of "+s+".",prompt:'<span class="ask">Tap all the signs of <b>'+s+"</b></span>",cells:U.shuffle(r,cells)}}
  const Q={chinook:["In winter, a warm wind can blow over the Rocky Mountains and melt the snow. What is it called?","a chinook",["a chinook","a blizzard","a rainbow"],"⛰️🌬️☀️"],
    why:["Why is winter colder than summer?","less sunlight",["less sunlight","the Sun turns off","the clouds eat the heat"],"🌍☀️"],
    day:["What comes after the evening?","night",["night","morning","lunch"],"🌇"]};
  if(K==="day"&&i%2){const D=[["🌅","morning"],["☀️","noon"],["🌇","evening"],["🌙","night"]];
    return{type:"order",size:72,say:"Put the parts of the day in order.",prompt:'<span class="ask">Put the day in order</span>',tiles:unsort(D.map(x=>({key:x[1],html:'<span class="lr-em">'+x[0]+'</span><small style="display:block;font-size:11px">'+x[1]+"</small>",say:x[1]})),D.map(x=>x[1])),answer:D.map(x=>x[1])}}
  const q=Q[K]||Q.chinook;
  return{type:"pick",cols:1,say:q[0],prompt:'<span class="ask">'+q[0]+'</span><span class="lr-emo">'+q[3]+"</span>",
    options:U.shuffle(r,q[2]).map(x=>({key:x,html:'<span style="font-size:20px">'+x+"</span>",say:x===q[1]?(K==="why"?"Yes! In winter the days are short and the sunlight is weaker.":K==="chinook"?"Yes! A chinook can melt the snow in a day.":"Yes! Night comes after evening."):x})),answer:q[1]}}""", [0,3])

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
