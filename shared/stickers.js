/* Sticker book shared by Train Trip and Train Yard. Both games keep stickers in the Train Trip save (stk: {emoji: count}).
   New stickers fill one themed page at a time; a full page earns a bonus; a sticker found 3+ times turns shiny. */
const TS_STICKERS=(()=>{
const P=(id,title,icon,list)=>({id,title,icon,items:list.trim().split(/\s*\|\s*/).map(s=>{const i=s.indexOf(" ");return[s.slice(0,i),s.slice(i+1)]})});
const PAGES=[
P("trains","Trains & tracks","🚂","🚂 steam train|🚃 train car|🚄 fast train|🚅 bullet train|🚆 train|🚇 subway train|🚈 light rail train|🚉 station|🚊 tram|🚝 monorail|🚞 mountain train|🚋 tram car|🛤️ railway tracks|🚦 signal light|🎫 ticket|🧳 suitcase|🕰️ station clock|🌉 bridge|🛎️ bell|🏮 lantern"),
P("go","Things that go","🚗","🚗 car|🚕 taxi|🚙 jeep|🚌 bus|🚎 trolley bus|🏎️ race car|🚓 police car|🚑 ambulance|🚒 fire truck|🚐 van|🛻 pickup truck|🚚 truck|🚛 big truck|🚜 tractor|🏍️ motorbike|🛵 scooter|🚲 bike|🛴 kick scooter|✈️ airplane|🚁 helicopter"),
P("wild","Alberta wildlife","🦬","🦬 bison|🫎 moose|🦌 deer|🐻 bear|🦫 beaver|🦉 owl|🦅 eagle|🐿️ squirrel|🐺 wolf|🦊 fox|🐇 bunny|🦆 duck|🐸 frog|🦝 raccoon|🦨 skunk|🐻‍❄️ polar bear|🦢 swan|🦡 badger|🐟 fish|🦇 bat"),
P("farm","On the farm","🐄","🐄 cow|🐷 pig|🐑 sheep|🐐 goat|🐔 chicken|🐣 baby chick|🐓 rooster|🐴 horse|🦃 turkey|🐮 cow face|🐶 puppy|🐱 kitty|🐰 bunny face|🐭 mouse|🌽 corn|🌾 wheat|🥕 carrot|🏡 farmhouse|🥛 milk|🐎 racing horse"),
P("dino","Dino land","🦖","🦖 T-rex|🦕 long-neck dinosaur|🥚 egg|🦴 bone|🌋 volcano|🐊 crocodile|🦎 lizard|🌿 leaf|🌴 palm tree|🪨 rock|🐉 dragon|🐲 dragon face|🦤 dodo bird|🪶 feather|🌵 cactus|🥥 coconut|🪺 nest|🦣 mammoth|🌳 tree|🌱 sprout"),
P("space","Outer space","🚀","🚀 rocket|🪐 planet|⭐ star|🌙 moon|🛸 flying saucer|☄️ comet|🌍 Earth|👩‍🚀 astronaut|🌟 glowing star|🌠 shooting star|🌌 galaxy|🔭 telescope|🛰️ satellite|🌕 full moon|🌑 new moon|👽 alien|👾 space monster|🤖 robot|🌛 moon face|💫 dizzy star"),
P("sea","Boats & sea","⛵","⛵ sailboat|🚤 speedboat|🛥️ motor boat|🛳️ cruise ship|⛴️ ferry|🚢 ship|🛶 canoe|⚓ anchor|🏝️ island|🌊 wave|🐳 whale|🐬 dolphin|🐙 octopus|🦀 crab|🐠 tropical fish|🐡 puffer fish|🦈 shark|🐢 turtle|🦭 seal|🐚 shell"),
P("zoo","Zoo & jungle","🦁","🦁 lion|🐯 tiger|🐘 elephant|🦒 giraffe|🦓 zebra|🦛 hippo|🦏 rhino|🐒 monkey|🦍 gorilla|🦧 orangutan|🐼 panda|🐨 koala|🦘 kangaroo|🐪 camel|🦩 flamingo|🦜 parrot|🐧 penguin|🦥 sloth|🐍 snake|🦚 peacock"),
P("weather","Weather & sky","🌈","🌞 sunshine|☀️ sun|⛅ sun and cloud|☁️ cloud|🌧️ rain|⛈️ thunderstorm|🌩️ lightning|⚡ zap|🌈 rainbow|❄️ snowflake|☃️ snowman|🌨️ snow cloud|🌪️ tornado|🌫️ fog|💨 wind|☂️ umbrella|💧 raindrop|🌡️ thermometer|🌅 sunrise|🌄 mountain sunrise"),
P("bugs","Bugs & flowers","🐞","🐛 caterpillar|🦋 butterfly|🐌 snail|🐞 ladybug|🐜 ant|🐝 bee|🪲 beetle|🦗 cricket|🕷️ spider|🕸️ spider web|🦂 scorpion|🪱 worm|🦟 mosquito|🐾 paw prints|🌸 blossom|🌷 tulip|🌻 sunflower|🌼 daisy|🍄 mushroom|🌹 rose"),
P("food","Yummy food","🍦","🍎 apple|🍌 banana|🍓 strawberry|🍇 grapes|🍉 watermelon|🍊 orange|🍒 cherries|🍍 pineapple|🥝 kiwi|🍕 pizza|🍔 burger|🌭 hot dog|🍟 fries|🥞 pancakes|🧇 waffle|🍪 cookie|🧁 cupcake|🍩 donut|🍦 ice cream|🍿 popcorn"),
P("sports","Sports & games","⚽","⚽ soccer ball|🏀 basketball|🏈 football|⚾ baseball|🎾 tennis ball|🏒 hockey stick|🥅 net|🏆 trophy|🥇 gold medal|🏐 volleyball|🏓 ping pong|🏸 badminton|⛳ golf|🎳 bowling|🛹 skateboard|⛸️ ice skate|🎿 skis|🛷 sled|🪁 kite|🏉 rugby ball"),
P("party","Music & party","🎉","🎉 party|🎈 balloon|🎂 birthday cake|🎁 present|🎊 confetti|🥳 party face|🎵 music note|🎶 music notes|🎸 guitar|🥁 drum|🎹 piano|🎺 trumpet|🎷 saxophone|🎻 violin|🎤 microphone|🪅 piñata|🎆 fireworks|🎇 sparkler|🪩 disco ball|🍭 lollipop"),
P("toys","Toys & treasure","🧸","🧸 teddy bear|🪀 yo-yo|🧩 puzzle|🎲 dice|🎨 paints|🖍️ crayon|🎮 video game|🪄 magic wand|🔮 crystal ball|👑 crown|💎 gem|💰 money bag|🪙 coin|🗝️ old key|🏴‍☠️ pirate flag|🗺️ treasure map|🧭 compass|🎯 target|🪆 nesting doll|🎠 carousel"),
P("magic","Magic & holidays","🦄","🦄 unicorn|🧚 fairy|🏰 castle|💖 sparkly heart|🍁 maple leaf|🍂 fall leaves|🎃 pumpkin|👻 ghost|🧙 wizard|🎄 Christmas tree|🎅 Santa|🤶 Mrs. Claus|🔔 bell|🕯️ candle|🍬 candy|🍫 chocolate|🧦 stocking|🧝 elf|🍀 lucky clover|🕊️ dove"),
P("faces","Faces & friends","😀","😀 smile|😂 laughing|😎 cool|🤩 star eyes|😜 silly face|🥰 love|🤠 cowboy|🤡 clown|😺 happy cat|🙈 see no evil monkey|🙉 hear no evil monkey|🙊 speak no evil monkey|👍 thumbs up|👋 wave|🤗 hug|😴 sleepy|🤓 smarty pants|💪 strong|🙌 hooray|👏 clapping")];
const ALL=[].concat(...PAGES.map(p=>p.items.map(x=>({em:x[0],name:x[1],page:p})))),BY={};ALL.forEach(x=>{BY[x.em]=x});
const PER=PAGES[0].items.length,SHINY=3;
const strip=e=>e.replace(/️/g,"");
const find=e=>BY[e]||ALL.find(x=>strip(x.em)===strip(e));
/* The player's favourite topic's page comes first (Trains for train fans). */
function order(){const f=window.TS&&TS.players.fav&&TS.players.fav(),ic=f&&f.icon;const first=PAGES.find(p=>p.icon===ic||p.items.some(x=>x[0]===ic));
  return first?[first].concat(PAGES.filter(p=>p!==first)):PAGES.slice()}
const have=(stk,p)=>p.items.filter(x=>stk[x[0]]).length;
const total=stk=>ALL.filter(x=>stk[x.em]).length;
/* Pick the next sticker: a new one from the first page that isn't full; once every page is full, a random repeat (they turn shiny). */
function next(stk,rng){rng=rng||Math.random;const pg=order().find(p=>have(stk,p)<p.items.length);
  const pool=pg?pg.items.filter(x=>!stk[x[0]]):ALL.map(x=>[x.em,x.name]),x=pool[Math.floor(rng()*pool.length)];
  stk[x[0]]=(stk[x[0]]||0)+1;const s=find(x[0]);
  return{em:x[0],name:x[1],page:s.page,pageDone:!!pg&&have(stk,pg)===pg.items.length,shiny:stk[x[0]]===SHINY,count:stk[x[0]],book:total(stk)>=ALL.length}}

let css=false,ov=null;
function addCSS(){if(css)return;css=true;const st=document.createElement("style");st.textContent=
`.stb-ov{position:fixed;inset:0;z-index:60;display:grid;place-items:center;background:rgba(10,20,40,.55);padding:10px}
.stb-ov[hidden]{display:none}
.stb{box-sizing:border-box;width:min(520px,96vw);max-height:94vh;display:flex;flex-direction:column;gap:8px;background:#fff8e8;border-radius:22px;padding:12px 12px 14px;box-shadow:0 10px 0 #c99a4a,0 18px 40px rgba(0,0,0,.35);color:#4a3418;font-family:var(--font-body,system-ui)}
.stb-top{display:flex;align-items:center;gap:8px}
.stb-top h2{flex:1;margin:0;font:700 22px var(--font-sign,var(--font-body,system-ui));text-align:center}
.stb-x{border:0;border-radius:14px;background:#4a3418;color:#fff;font:700 18px var(--font-body,system-ui);padding:8px 14px;cursor:pointer}
.stb-tabs{display:flex;gap:5px;overflow-x:auto;padding:2px 2px 6px;scrollbar-width:thin}
.stb-tab{flex:0 0 auto;position:relative;width:46px;height:46px;border:0;border-radius:12px;background:#f0dfbd;font-size:26px;cursor:pointer;opacity:.8}
.stb-tab.on{background:#ffcf4a;opacity:1;box-shadow:0 0 0 3px #e08a00}
.stb-tab.done::after{content:"⭐";position:absolute;right:-4px;top:-6px;font-size:14px}
.stb-tab.lock{filter:grayscale(1);opacity:.45}
.stb-page{display:flex;align-items:center;gap:6px}
.stb-arr{flex:0 0 auto;border:0;width:clamp(28px,8vw,40px);padding:0;height:64px;border-radius:14px;background:#f0dfbd;font:700 26px var(--font-body,system-ui);color:#4a3418;cursor:pointer}
.stb-arr:disabled{opacity:.3}
.stb-sheet{flex:1;min-width:0;display:grid;grid-template-columns:repeat(5,1fr);gap:clamp(4px,1.6vw,8px);padding:clamp(6px,2vw,10px);border-radius:16px;background:repeating-linear-gradient(#fffdf6 0 28px,#f3e7cc 28px 29px);box-shadow:inset 0 0 0 3px #e8d3a6}
.stb-sheet i{position:relative;font-style:normal;aspect-ratio:1;border-radius:50%;display:grid;place-items:center;font-size:clamp(24px,7vw,36px);background:#fff;box-shadow:0 0 0 3px #f2c94c,0 3px 0 3px #d9a730;cursor:pointer;user-select:none}
.stb-sheet i.no{background:rgba(120,90,40,.08);box-shadow:inset 0 0 0 2px rgba(120,90,40,.25);cursor:default}
.stb-sheet i.no span{filter:brightness(0);opacity:.12}
.stb-sheet i b{position:absolute;right:-5px;bottom:-5px;background:#e2412e;color:#fff;font:700 12px var(--font-body,system-ui);border-radius:10px;padding:1px 5px}
.stb-sheet i.shiny{background:radial-gradient(circle at 35% 30%,#fff,#fff3b0 60%,#ffd94a);box-shadow:0 0 0 3px #ffb300,0 0 14px 4px rgba(255,200,0,.75);animation:stbGlow 1.6s ease-in-out infinite}
.stb-sheet i.shiny::before{content:"✨";position:absolute;left:-6px;top:-8px;font-size:16px}
.stb-sheet i.pop{animation:stbPop .5s ease}
@keyframes stbGlow{50%{box-shadow:0 0 0 3px #ffb300,0 0 22px 8px rgba(255,220,60,.9)}}
@keyframes stbPop{50%{transform:scale(1.3)}}
.stb-foot{display:flex;justify-content:space-between;align-items:center;font:700 15px var(--font-body,system-ui);padding:0 4px}
.stb-bar{flex:1;height:12px;margin:0 10px;border-radius:8px;background:#f0dfbd;overflow:hidden}
.stb-bar span{display:block;height:100%;background:linear-gradient(90deg,#ffcf4a,#ff8a00)}
.stb-new{position:fixed;left:50%;top:40%;z-index:70;transform:translate(-50%,-50%);background:#fff8e8;border-radius:22px;padding:16px 22px;text-align:center;box-shadow:0 8px 0 #c99a4a,0 18px 40px rgba(0,0,0,.35);font:700 20px var(--font-body,system-ui);color:#4a3418;animation:stbPop .6s ease;pointer-events:none}
.stb-new big{display:block;font-size:54px}`;
document.head.appendChild(st)}

/* Open the book. o: {onClose, page(id to show)} */
function open(stk,o){o=o||{};addCSS();const pages=order();
  if(!ov){ov=document.createElement("div");ov.className="stb-ov";document.body.appendChild(ov)}
  const firstOpen=pages.findIndex(p=>have(stk,p)<p.items.length);
  let at=o.page?Math.max(0,pages.findIndex(p=>p.id===o.page)):Math.max(0,firstOpen<0?0:firstOpen);
  const unlocked=i=>i<=Math.max(firstOpen<0?pages.length-1:firstOpen,0)||have(stk,pages[i])>0;
  function draw(){const p=pages[at],h=have(stk,p),n=total(stk);
    ov.innerHTML='<div class="stb" role="dialog" aria-label="My sticker book"><div class="stb-top"><h2>📒 My stickers</h2><button class="stb-x" type="button">Done</button></div>'+
      '<div class="stb-tabs">'+pages.map((q,i)=>'<button type="button" class="stb-tab'+(i===at?" on":"")+(have(stk,q)===q.items.length?" done":"")+(unlocked(i)?"":" lock")+'" data-i="'+i+'" aria-label="'+q.title+'">'+q.icon+"</button>").join("")+"</div>"+
      '<div class="stb-top"><h2 style="font-size:20px">'+p.title+(h===p.items.length?" ⭐":"")+"</h2></div>"+
      '<div class="stb-page"><button class="stb-arr" type="button" data-d="-1" '+(at?"":"disabled")+' aria-label="Back">‹</button><div class="stb-sheet">'+
      p.items.map(x=>{const c=stk[x[0]]||0;return c?'<i data-e="'+x[0]+'" class="'+(c>=SHINY?"shiny":"")+'" title="'+x[1]+'">'+x[0]+(c>1?"<b>×"+c+"</b>":"")+"</i>":'<i class="no"><span>'+x[0]+"</span></i>"}).join("")+
      '</div><button class="stb-arr" type="button" data-d="1" '+(at<pages.length-1?"":"disabled")+' aria-label="Next">›</button></div>'+
      '<div class="stb-foot"><span>'+h+" / "+p.items.length+'</span><span class="stb-bar"><span style="width:'+Math.round(100*h/p.items.length)+'%"></span></span><span>'+n+" of "+ALL.length+"</span></div></div>";}
  draw();ov.hidden=false;
  ov.onclick=e=>{const t=e.target;
    if(t===ov||t.closest(".stb-x")){ov.hidden=true;o.onClose&&o.onClose();return}
    const tab=t.closest(".stb-tab");if(tab){at=+tab.dataset.i;draw();const p=pages[at];TS.say(p.title+". "+(have(stk,p)?"You have "+have(stk,p)+" of "+p.items.length+".":"Keep going to find these stickers!"));return}
    const ar=t.closest(".stb-arr");if(ar&&!ar.disabled){at=Math.min(pages.length-1,Math.max(0,at+(+ar.dataset.d)));draw();TS.say(pages[at].title);return}
    const i=t.closest("i[data-e]");if(i){const s=find(i.dataset.e);i.classList.remove("pop");void i.offsetWidth;i.classList.add("pop");if(s)TS.say((stk[s.em]>=SHINY?"Shiny ":"")+s.name)}};
  const p=pages[at],n=total(stk);
  TS.say(n?"You have "+n+" stickers! This page is "+p.title+".":"No stickers yet. Right answers can win stickers!")}
const isOpen=()=>!!ov&&!ov.hidden;
function close(){if(ov)ov.hidden=true}
/* A short "page full" celebration card. */
function celebrate(page,bonus){addCSS();const el=document.createElement("div");el.className="stb-new";
  el.innerHTML="<big>"+page.icon+"⭐</big>"+page.title+" page is full!"+(bonus?"<br>🎟️ +"+bonus+" tickets":"");document.body.appendChild(el);
  setTimeout(()=>el.remove(),3200)}
return{PAGES,ALL,PER,SHINY,next,open,close,isOpen,total,have,find,celebrate,order}})();
