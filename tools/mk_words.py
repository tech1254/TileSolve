"""Writes the word games built on shared/learn.js: Rhyme Time, Sentence Builder, Spelling Bee (src/<id>.html).
Content follows Alberta English language arts one grade back: make(level, round, rng, a) gets a = player's grade - 1.
Run: python3 tools/mk_words.py  (then node tools/build.js)"""
import pathlib, json
SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
G = {}

G["rhyme"] = ("Rhyme Time", [["👂","Rhyming words sound the same at the end: cat, hat, bat."],["🔊","Listen to the word."],["👆","Tap the picture or word that rhymes."],["🔁","Tap the speaker to hear it again."]],
r'''make(n,i,r,a){
  // word families: words in a family rhyme. Families with different spellings (light/kite) come later.
  const F=[["cat🐱","hat🎩","bat🦇","rat🐀","mat🧘"],["dog🐶","frog🐸","log🪵"],["bee🐝","tree🌳","key🔑","knee🦵"],["car🚗","star⭐","jar🫙"],["cake🎂","snake🐍","rake🧹"],
    ["moon🌙","spoon🥄","balloon🎈"],["fish🐟","dish🍽️"],["bear🐻","pear🍐","chair🪑","hair💇"],["mouse🐭","house🏠"],["boat⛵","goat🐐","coat🧥"],["king🤴","ring💍","swing🛝"],
    ["sock🧦","clock🕰️","rock🪨","lock🔒"],["bug🐛","mug☕","rug🧶"],["fox🦊","box📦","socks🧦"],["pig🐷","wig💇","dig⛏️"],["train🚆","rain🌧️","chain⛓️","plane✈️"],["snail🐌","whale🐋","mail📬"],
    ["light💡","kite🪁","night🌃","bite🦷"],["nose👃","rose🌹","toes🦶"],["bed🛏️","bread🍞","red🟥"],["sun☀️","bun🍔","run🏃"],["hen🐔","pen🖊️","ten🔟"],["ship🚢","lip👄","zip🤐"],
    ["bell🔔","shell🐚","well🪣"],["shoe👟","two2️⃣","glue🧴","zoo🦁"],["ball⚽","wall🧱","fall🍂"],["corn🌽","horn📯","unicorn🦄"]].map(f=>f.map(s=>{const m=s.match(/^([a-z]+)(.+)$/u);return{w:m[1],e:m[2]}}));
  const fam=U.pick(r,F.filter(f=>a>=1||f.length>=3)),[q,ans]=U.sample(r,fam,2),others=U.shuffle(r,F.filter(f=>f!==fam)),k=a<0?2:a===0?3:4;
  const tile=(x,pic)=>({key:x.w,html:pic?'<span class="lr-word"><b>'+x.e+"</b>"+x.w+"</span>":'<span class="lr-word">'+x.w+"</span>",say:x.w,aria:x.w});
  const pic=a<2;
  if(a>=1&&i%3===2){ // which one does NOT rhyme?
    const three=U.sample(r,fam.length>=3?fam:fam.concat(fam),3).filter((x,j,s)=>s.findIndex(y=>y.w===x.w)===j);const odd=U.pick(r,others[0]);
    if(three.length>=2){const opts=U.shuffle(r,three.concat([odd]));
      return{type:"pick",cols:2,say:"Which word does not rhyme? "+opts.map(x=>x.w).join(", "),prompt:'<span class="ask">Which one does NOT rhyme?</span>',options:opts.map(x=>tile(x,pic)),answer:odd.w}}}
  // research: wrong choices start out sharing nothing with the answer, then share its first sound (cat/cup), then its vowel (cat/cap)
  const V=x=>(x.w.match(/[aeiou]/)||[""])[0],near=a<=0?(x=>x.w[0]!==ans.w[0]&&V(x)!==V(ans)):a===1?(x=>x.w[0]===ans.w[0]):(x=>V(x)===V(ans)||x.w[0]===ans.w[0]);
  const flat=others.flat().filter(x=>!fam.includes(x)),pref=U.shuffle(r,flat.filter(near)),rest=U.shuffle(r,flat.filter(x=>!near(x)&&(a>0||(x.w[0]!==ans.w[0]))));
  const opts=[ans];for(const x of pref.concat(rest))if(opts.length<k&&!opts.some(o=>o.w===x.w))opts.push(x);
  return{type:"pick",cols:2,say:"What rhymes with "+q.w+"?",prompt:'<span class="ask">What rhymes with</span><span class="lr-word big1"><b>'+q.e+"</b>"+q.w+"</span>",
    options:U.shuffle(r,opts).map(x=>tile(x,pic)),answer:ans.w}}''', None)

G["sentence"] = ("Sentence Builder", [["📝","The words got mixed up!"],["👆","Tap the words in order to make a sentence."],["🔠","Sentences start with a capital letter and end with . ? or !"],["🔊","Tap the speaker to hear the sentence."]],
r'''make(n,i,r,a){
  const B=[ // [emoji, sentence]; each has only one sensible order
    [["🐱","I see a cat."],["🐶","The dog can run."],["☀️","Look at the sun."],["🚗","I like my car."],["🐸","The frog is green."],["🍎","I can eat it."],["🎈","We see a red ball."],["🏠","This is my home."],
     ["🐝","Look at the bee."],["🐟","The fish can swim."],["🦆","The duck is wet."],["🚌","We go on the bus."]],                                                                    // K content
    [["🐸","The frog jumps in the pond."],["🌧️","It is raining on my hat."],["🐶","My dog likes to play ball."],["🍪","Can I have a cookie?"],["🚲","She rides her bike to school."],
     ["🐻","The bear is in the cave."],["🌳","A bird sat in the tree."],["🍕","We had pizza for lunch."],["⛄","Look at the big snowman!"],["🐢","The turtle is very slow."],["🎂","Today is my birthday!"],["📖","Will you read me a book?"]], // grade 1
    [["🦊","The little fox ran into the forest."],["🧁","My sister made cupcakes for the party."],["🚀","The rocket flew up to the moon."],["🐧","Where do penguins like to swim?"],
     ["🏒","We play hockey on the frozen pond."],["🦋","A butterfly landed on my nose!"],["🍁","The leaves turn orange in the fall."],["🐳","Did you see the giant whale?"],
     ["🧤","Wear your mittens when it is cold."],["🚂","The long train went over the bridge."]],                                                                                  // grade 2
    [["🌋","The volcano rumbled and smoke filled the sky."],["🐿️","After school, we watched a squirrel hide acorns."],["🏕️","When it got dark, we told stories by the campfire."],
     ["🦉","Why do owls stay awake all night long?"],["🎨","My brother painted a beautiful picture of the mountains."],["🏔️","Our family drove to Banff to see the mountains."],
     ["⛸️","On Saturday, my friends and I went skating."],["📚","The library has thousands of books to borrow."],["🦖","Dinosaurs lived on Earth millions of years ago."],["🌦️","If it rains tomorrow, we will play inside."]]]; // grade 3+
  const lv=Math.max(0,Math.min(3,a));let pool=B[lv];if(a>=1&&n<=8)pool=B[lv-1].concat(pool);
  const[e,s]=U.pick(r,pool),words=s.split(" "),tiles=words.map((w,k)=>({key:"w"+k,val:w,html:w,say:w.replace(/[.?!,]/g,"")}));
  return{type:"order",wide:true,say:"Make a sentence: "+s,text:"Tap the words in order. Start with the capital letter!",
    prompt:'<span class="ask">Put the words in order</span><span class="lr-emo">'+e+"</span>",tiles:U.mix(r,tiles),answer:words}}''', [1,5])

G["spelling"] = ("Spelling Bee", [["🐝","Listen to the word."],["📝","The sentence shows how it's used."],["👆","Tap the letters in order to spell it."],["⚠️","Some letters are extra. Tap 🔊 to hear the word again."]],
r'''rounds:()=>5,
make(n,i,r,a){
  const L=[ // [word, sentence with ___] from each grade's high-frequency and phonics words (Canadian spelling)
    [["see","I ___ a bird."],["can","I ___ jump."],["the","Look at ___ cat."],["and","Mom ___ Dad."],["big","A ___ dog."],["red","A ___ apple."],["up","Go ___ the hill."],["go","Let's ___ home."],
     ["me","Come with ___."],["we","___ like to play."],["run","I can ___ fast."],["sun","The ___ is hot."],["yes","___, please!"],["not","It is ___ cold."],["look","___ at me!"],["my","This is ___ hat."]],
    [["ship","A ___ on the sea."],["fish","The ___ can swim."],["chin","Food on my ___."],["that","Is ___ your cat?"],["this","___ is my bike."],["with","Come ___ me."],["they","___ are my friends."],
     ["said","Mom ___ yes."],["have","I ___ a dog."],["like","I ___ pizza."],["make","Let's ___ a cake."],["home","Time to go ___."],["play","Can you ___ outside?"],["went","We ___ to the park."],
     ["from","A card ___ Grandma."],["what","___ is your name?"],["when","___ is lunch?"],["much","Thank you very ___."]],
    [["green","Grass is ___."],["train","The ___ goes choo choo."],["light","Turn on the ___."],["night","Stars come out at ___."],["know","I ___ the answer."],["write","I can ___ my name."],
     ["friend","She is my best ___."],["school","We learn at ___."],["could","___ you help me?"],["would","I ___ like that."],["there","Put it over ___."],["where","___ is my hat?"],
     ["after","We play ___ lunch."],["again","Read it ___!"],["every","I brush my teeth ___ day."],["because","I smiled ___ I was happy."],["snake","The ___ says hiss."],["knee","I fell and hurt my ___."]],
    [["beautiful","What a ___ sunset!"],["different","Every snowflake is ___."],["favourite","Blue is my ___ colour."],["colour","What ___ is the sky?"],["neighbour","Our ___ has a dog."],
     ["through","We walked ___ the forest."],["answer","I know the ___!"],["believe","I ___ in you."],["enough","Do we have ___ cookies?"],["special","Today is a ___ day."],
     ["surprise","The party was a ___!"],["library","We borrow books at the ___."],["question","Can I ask a ___?"],["important","Sleep is ___."],["remember","I ___ your birthday."],["laugh","Jokes make me ___."]],
    [["necessary","Is that really ___?"],["separate","Keep the colours ___."],["rhythm","Clap to the ___."],["knowledge","Books give us ___."],["temperature","The ___ dropped below zero."],
     ["restaurant","We ate at a ___."],["exercise","___ keeps you healthy."],["definitely","I will ___ be there."],["environment","Take care of the ___."],["calendar","Mark it on the ___."],
     ["government","The ___ makes laws."],["Wednesday","Art class is on ___."],["February","My birthday is in ___."],["vacuum","Please ___ the rug."],["mischief","The kitten got into ___."]]];
  const lv=Math.max(0,Math.min(4,a));let pool=L[lv];if(lv>0&&n<=6)pool=L[lv-1].concat(pool);
  const[w,s]=U.pick(r,pool.filter(x=>x[0].length<=(lv>=3?11:8))),letters=w.split(""),dec=lv===0?(n>15?1:0):lv===1?1:lv===2?2:3;
  const alpha="abcdefghijklmnopqrstuvwxyz",extra=[];while(extra.length<dec){const c=U.pick(r,alpha.split(""));if(!w.toLowerCase().includes(c)&&!extra.includes(c))extra.push(c)}
  const tiles=letters.concat(extra).map((c,k)=>({key:"l"+k,val:c,html:c,say:null}));
  return{type:"order",say:"Spell "+w+". "+s.replace("___",w)+" Spell "+w+".",text:"Listen, then spell the word. Tap 🔊 to hear it again.",
    prompt:'<span class="ask">🐝 Spell the word</span><span class="lr-sent">'+s.replace("___",'<u>'+"&nbsp;".repeat(Math.max(4,w.length))+"</u>")+"</span>",
    tiles:U.mix(r,tiles,letters.length),answer:letters}}''', [1,7])

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
