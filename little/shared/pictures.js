/* Tile Solve picture set: original cartoon scenes drawn in code (no downloads, no licences needed).
   Each scene is a 400x400 SVG with texture everywhere, so every puzzle piece looks different.
   Later, photo entries can be added as {id, name, theme, src, credit}. */
window.TS_PICTURES=(()=>{
function rng(seed){let a=seed>>>0;return()=>{a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const svg=b=>'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="1024" height="1024">'+b+"</svg>";
const lin=(id,stops,x2=0,y2=1)=>'<linearGradient id="'+id+'" x1="0" y1="0" x2="'+x2+'" y2="'+y2+'">'+stops.map((c,i)=>'<stop offset="'+(i/(stops.length-1))+'" stop-color="'+c+'"/>').join("")+"</linearGradient>";
const rad=(id,stops,cx=.5,cy=.5,r=.5)=>'<radialGradient id="'+id+'" cx="'+cx+'" cy="'+cy+'" r="'+r+'">'+stops.map((c,i)=>'<stop offset="'+(i/(stops.length-1))+'" stop-color="'+c+'"/>').join("")+"</radialGradient>";
function stars(r,n,y0=0,y1=400,col="#fff"){let s="";for(let i=0;i<n;i++){const x=r()*400,y=y0+r()*(y1-y0),z=.6+r()*1.8;
  s+=r()<.12?'<path d="M'+x+" "+(y-z*3)+"L"+(x+z)+" "+(y-z)+"L"+(x+z*3)+" "+y+"L"+(x+z)+" "+(y+z)+"L"+x+" "+(y+z*3)+"L"+(x-z)+" "+(y+z)+"L"+(x-z*3)+" "+y+"L"+(x-z)+" "+(y-z)+'Z" fill="'+col+'"/>'
   :'<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+z.toFixed(2)+'" fill="'+col+'" opacity="'+(.5+r()*.5).toFixed(2)+'"/>'}return s}
function grass(r,y,h,n,cols){let s="";for(let i=0;i<n;i++){const x=r()*400,hh=h*(.5+r()),c=cols[Math.floor(r()*cols.length)],w=2+r()*3;
  s+='<path d="M'+x+" "+(y+6)+"Q"+(x+(r()-.5)*14)+" "+(y-hh/2)+" "+(x+(r()-.5)*10)+" "+(y-hh)+"Q"+(x+w)+" "+(y-hh/2)+" "+(x+w)+" "+(y+6)+'Z" fill="'+c+'"/>'}return s}
function flowers(r,y0,y1,n,cols){let s="";for(let i=0;i<n;i++){const x=r()*400,y=y0+r()*(y1-y0),c=cols[Math.floor(r()*cols.length)],z=3+r()*4;
  for(let k=0;k<5;k++){const a=k*1.2566;s+='<circle cx="'+(x+Math.cos(a)*z).toFixed(1)+'" cy="'+(y+Math.sin(a)*z).toFixed(1)+'" r="'+(z*.7).toFixed(1)+'" fill="'+c+'"/>'}
  s+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+(z*.55).toFixed(1)+'" fill="#ffd84a"/>'}return s}
function bubbles(r,n,y0,y1){let s="";for(let i=0;i<n;i++){const x=r()*400,y=y0+r()*(y1-y0),z=2+r()*7;
  s+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+z.toFixed(1)+'" fill="#ffffff" fill-opacity=".12" stroke="#e8fbff" stroke-opacity=".7" stroke-width="1.2"/><circle cx="'+(x-z*.35).toFixed(1)+'" cy="'+(y-z*.35).toFixed(1)+'" r="'+(z*.25).toFixed(1)+'" fill="#fff" opacity=".8"/>'}return s}
function cloud(x,y,s,c="#fff",o=1){return'<g fill="'+c+'" opacity="'+o+'"><ellipse cx="'+x+'" cy="'+y+'" rx="'+34*s+'" ry="'+16*s+'"/><circle cx="'+(x-14*s)+'" cy="'+(y-10*s)+'" r="'+15*s+'"/><circle cx="'+(x+10*s)+'" cy="'+(y-15*s)+'" r="'+19*s+'"/></g>'}
const eye=(x,y,r=6)=>'<circle cx="'+x+'" cy="'+y+'" r="'+r+'" fill="#1d1d2b"/><circle cx="'+(x+r*.35)+'" cy="'+(y-r*.35)+'" r="'+(r*.35)+'" fill="#fff"/>';

const P=[];
/* 1. Fox at sunset */
P.push({id:"fox",name:"Fox at Sunset",theme:"animals",svg:(()=>{const r=rng(11);return svg(
  "<defs>"+lin("s1",["#3d2a6e","#b04a7c","#f47d4a","#ffc857"])+lin("h1",["#5a3c74","#3b2a58"])+"</defs>"+
  '<rect width="400" height="400" fill="url(#s1)"/>'+stars(r,26,0,110,"#ffe9b8")+
  '<circle cx="300" cy="215" r="58" fill="#ffe07a"/><circle cx="300" cy="215" r="76" fill="#ffe07a" opacity=".25"/>'+
  cloud(90,95,1.1,"#ffb6a0",.7)+cloud(250,70,.8,"#ffc9a8",.6)+
  '<path d="M0 250 Q60 200 120 230 T240 220 T400 230 V400 H0Z" fill="#7a4a86"/>'+
  '<path d="M0 275 Q80 240 160 265 T320 255 T400 262 V400 H0Z" fill="url(#h1)"/>'+
  [20,55,345,380,90,310].map((x,i)=>{const h=60+((i*37)%40),y=268-(i%3)*6;return'<path d="M'+x+" "+(y-h)+"L"+(x+16)+" "+y+"H"+(x-16)+'Z" fill="#2b1d45"/><path d="M'+x+" "+(y-h*.65)+"L"+(x+20)+" "+(y+8)+"H"+(x-20)+'Z" fill="#2b1d45"/>'}).join("")+
  '<path d="M0 300 Q100 285 200 300 T400 298 V400 H0Z" fill="#3f8a4a"/><path d="M0 330 Q120 318 220 332 T400 328 V400 H0Z" fill="#2f6e3a"/>'+
  grass(r,320,26,70,["#4fa65a","#357a40","#5cb866"])+flowers(r,335,395,26,["#ff7ab6","#ffffff","#b48cff","#ffb347"])+
  /* fox */
  '<path d="M250 330 C320 320 340 250 300 230 C330 270 300 300 250 305Z" fill="#e8742a"/><path d="M300 230 C318 240 326 258 322 272 C312 252 304 244 300 230Z" fill="#fff6ea"/>'+
  '<ellipse cx="205" cy="300" rx="62" ry="46" fill="#ee7d2e"/><ellipse cx="190" cy="318" rx="30" ry="26" fill="#fff6ea"/>'+
  '<rect x="160" y="320" width="18" height="40" rx="8" fill="#d8641f"/><rect x="215" y="322" width="18" height="38" rx="8" fill="#d8641f"/><ellipse cx="169" cy="360" rx="12" ry="7" fill="#3a2418"/><ellipse cx="224" cy="360" rx="12" ry="7" fill="#3a2418"/>'+
  '<path d="M140 228 L120 170 L168 205Z" fill="#ee7d2e"/><path d="M135 215 L127 186 L152 205Z" fill="#3a2418"/><path d="M220 228 L238 170 L196 205Z" fill="#ee7d2e"/><path d="M224 215 L232 186 L208 205Z" fill="#3a2418"/>'+
  '<path d="M180 200 C140 200 120 230 128 255 C135 278 160 292 180 292 C200 292 225 278 232 255 C240 230 220 200 180 200Z" fill="#f08a36"/>'+
  '<path d="M128 255 C140 262 160 262 180 292 C200 262 220 262 232 255 C226 280 205 296 180 300 C155 296 134 280 128 255Z" fill="#fff6ea"/>'+
  eye(160,245,7)+eye(200,245,7)+'<ellipse cx="180" cy="272" rx="9" ry="7" fill="#2a1a12"/><path d="M172 283 Q180 290 188 283" stroke="#2a1a12" stroke-width="2.5" fill="none" stroke-linecap="round"/>'+
  '<circle cx="146" cy="265" r="7" fill="#ff9aa8" opacity=".6"/><circle cx="214" cy="265" r="7" fill="#ff9aa8" opacity=".6"/>'+
  '<g fill="#ffe9b8"><path d="M60 140 q6 -6 12 0 q6 -6 12 0" stroke="#3b2a58" stroke-width="2.5" fill="none"/><path d="M95 120 q5 -5 10 0 q5 -5 10 0" stroke="#3b2a58" stroke-width="2" fill="none"/></g>')})()});

/* 2. Rocket launch */
P.push({id:"rocket",name:"Rocket Launch",theme:"space",svg:(()=>{const r=rng(22);return svg(
  "<defs>"+lin("s2",["#0b1030","#24206b","#5a2f8e","#c0508a"])+lin("rb",["#ffffff","#d7dde8"],1,0)+rad("fl",["#fff7c2","#ffd23f","#ff8a2a","#ff4d2a"],.5,.2,.8)+"</defs>"+
  '<rect width="400" height="400" fill="url(#s2)"/>'+stars(r,120,0,330)+
  '<circle cx="78" cy="78" r="44" fill="#f3f0dc"/><circle cx="96" cy="66" r="44" fill="#0e1336"/><circle cx="58" cy="92" r="5" fill="#d6d1b6"/><circle cx="70" cy="60" r="3.5" fill="#d6d1b6"/>'+
  '<circle cx="338" cy="96" r="26" fill="#ff9e5e"/><ellipse cx="338" cy="96" rx="44" ry="9" fill="none" stroke="#ffd2a8" stroke-width="4" transform="rotate(-18 338 96)"/>'+
  '<circle cx="300" cy="190" r="10" fill="#5fd3c4"/><circle cx="296" cy="187" r="3" fill="#a8f0e6"/>'+
  '<path d="M150 330 Q150 300 175 305 Q185 280 210 292 Q235 278 248 302 Q275 296 270 330Z" fill="#cfc6e6" opacity=".9"/>'+
  '<path d="M60 400 Q50 345 100 350 Q115 320 150 336 Q170 310 200 330 Q235 305 255 335 Q290 318 305 350 Q350 340 345 400Z" fill="#e9e3f6"/>'+
  '<path d="M0 400 Q10 370 45 375 Q70 350 100 372 Q110 360 130 400Z" fill="#d7cfee"/><path d="M290 400 Q300 365 340 372 Q360 350 400 368 V400Z" fill="#d7cfee"/>'+
  '<path d="M180 262 Q200 330 220 262Z" fill="url(#fl)"/><path d="M188 262 Q200 300 212 262Z" fill="#fff7c2"/>'+
  '<path d="M200 70 C232 100 240 160 236 230 H164 C160 160 168 100 200 70Z" fill="url(#rb)"/>'+
  '<path d="M200 70 C214 82 224 98 230 118 H170 C176 98 186 82 200 70Z" fill="#e2412e"/>'+
  '<path d="M164 190 L132 246 L166 236Z" fill="#e2412e"/><path d="M236 190 L268 246 L234 236Z" fill="#e2412e"/><rect x="190" y="200" width="20" height="44" rx="6" fill="#b8301f"/>'+
  '<rect x="160" y="226" width="80" height="14" rx="5" fill="#7a8396"/>'+
  '<circle cx="200" cy="150" r="22" fill="#7a8396"/><circle cx="200" cy="150" r="16" fill="#3b6fd9"/><path d="M190 142 a12 12 0 0 1 14 -4" stroke="#bfe0ff" stroke-width="4" fill="none" stroke-linecap="round"/>'+
  '<circle cx="182" cy="196" r="3" fill="#9aa3b5"/><circle cx="218" cy="196" r="3" fill="#9aa3b5"/>'+
  '<path d="M30 220 L70 200" stroke="#fff" stroke-width="2" opacity=".6"/><circle cx="72" cy="199" r="3" fill="#fff"/>')})()});

/* 3. Saturn */
P.push({id:"saturn",name:"Ringed Planet",theme:"space",svg:(()=>{const r=rng(33);return svg(
  "<defs>"+rad("sp",["#2a1b5e","#120c33","#05040f"],.3,.3,.9)+lin("pl",["#ffe2a6","#f2b866","#e08e3c","#f7cf86","#d98a3a"],0,1)+rad("neb",["#ff7ad8","#7a4fe0","#120c3300"],.5,.5,.5)+"</defs>"+
  '<rect width="400" height="400" fill="url(#sp)"/><ellipse cx="90" cy="300" rx="150" ry="90" fill="url(#neb)" opacity=".45"/><ellipse cx="330" cy="70" rx="110" ry="60" fill="url(#neb)" opacity=".3"/>'+
  stars(r,170,0,400)+
  '<g transform="rotate(-16 210 205)"><ellipse cx="210" cy="205" rx="168" ry="44" fill="none" stroke="#c9a46e" stroke-width="14" opacity=".9"/><ellipse cx="210" cy="205" rx="146" ry="36" fill="none" stroke="#f0d6a2" stroke-width="7"/></g>'+
  '<circle cx="210" cy="205" r="92" fill="url(#pl)"/>'+
  '<path d="M126 170 Q210 150 296 176" stroke="#c4752e" stroke-width="7" fill="none" opacity=".6"/><path d="M120 214 Q210 198 300 222" stroke="#fbe3b5" stroke-width="9" fill="none" opacity=".7"/><path d="M130 252 Q210 240 290 258" stroke="#b9692a" stroke-width="6" fill="none" opacity=".55"/>'+
  '<ellipse cx="240" cy="230" rx="16" ry="9" fill="#c4612a" opacity=".7"/>'+
  '<circle cx="180" cy="160" r="40" fill="#fff" opacity=".12"/>'+
  '<g transform="rotate(-16 210 205)"><path d="M42 205 A168 44 0 0 0 378 205" fill="none" stroke="#c9a46e" stroke-width="14" opacity=".95"/><path d="M64 205 A146 36 0 0 0 356 205" fill="none" stroke="#f0d6a2" stroke-width="7"/></g>'+
  '<circle cx="62" cy="88" r="18" fill="#9fd3ff"/><circle cx="56" cy="82" r="5" fill="#d8eeff"/><circle cx="70" cy="96" r="3" fill="#6fa8d8"/>'+
  '<circle cx="350" cy="320" r="12" fill="#ff8aa0"/><circle cx="346" cy="316" r="4" fill="#ffc2cd"/>'+
  '<path d="M290 360 L360 300" stroke="#bfe8ff" stroke-width="3" stroke-linecap="round" opacity=".8"/><circle cx="362" cy="298" r="6" fill="#e8f7ff"/>'+
  '<circle cx="310" cy="120" r="6" fill="#d9d2ff"/>')})()});

/* 4. Octopus reef */
P.push({id:"octopus",name:"Octopus Reef",theme:"animals",svg:(()=>{const r=rng(44);let ten="";
  for(let k=0;k<6;k++){const x=150+k*20,dx=(k-2.5)*22,c=k%2?"#9b5fd6":"#a86be0";
    ten+='<path d="M'+x+" 230 C"+(x+dx*.4)+" 280 "+(x+dx)+" 290 "+(x+dx*1.2)+" 320 C"+(x+dx*1.4)+" 340 "+(x+dx*1.8+8)+" 336 "+(x+dx*1.7+4)+" 326 C"+(x+dx*1.5+12)+" 300 "+(x+dx*.8+14)+" 280 "+(x+16)+' 230Z" fill="'+c+'"/>';
    for(let j=0;j<3;j++)ten+='<circle cx="'+(x+8+dx*(.35+j*.3)).toFixed(1)+'" cy="'+(250+j*22)+'" r="3" fill="#e2c4ff"/>'}
  return svg("<defs>"+lin("w4",["#4fd1d9","#1b8fb8","#155f9a","#0d3b6e"])+lin("sd",["#f5d99a","#e2b96a"])+"</defs>"+
  '<rect width="400" height="400" fill="url(#w4)"/>'+
  '<g fill="#ffffff" opacity=".1"><path d="M40 0 L90 0 L170 400 L110 400Z"/><path d="M170 0 L200 0 L260 400 L220 400Z"/><path d="M290 0 L340 0 L360 400 L320 400Z"/></g>'+
  '<path d="M0 330 Q100 312 200 330 T400 326 V400 H0Z" fill="url(#sd)"/>'+
  Array.from({length:40},()=>'<circle cx="'+(r()*400).toFixed(1)+'" cy="'+(340+r()*58).toFixed(1)+'" r="'+(1+r()*2).toFixed(1)+'" fill="#c99a50" opacity=".6"/>').join("")+
  '<path d="M20 340 C10 300 30 270 25 240 M25 300 C40 290 50 270 48 250 M22 280 C8 270 2 255 6 240" stroke="#ff7a8a" stroke-width="9" fill="none" stroke-linecap="round"/>'+
  '<path d="M355 345 C350 300 370 280 362 250 M360 300 C380 295 388 275 384 256 M358 318 C340 310 334 290 338 272" stroke="#ffa24a" stroke-width="10" fill="none" stroke-linecap="round"/>'+
  [60,95,300,330,385].map((x,i)=>'<path d="M'+x+" 335 C"+(x-14)+" "+(300-i*6)+" "+(x+14)+" "+(260-i*8)+" "+(x-4)+" "+(210-i*10)+'" stroke="#2f9e5a" stroke-width="7" fill="none" stroke-linecap="round"/>').join("")+
  '<ellipse cx="300" cy="352" rx="18" ry="10" fill="#ffd0e0"/><path d="M282 352 Q300 332 318 352" fill="#ffb3cc"/>'+
  '<path d="M90 365 l6 -14 l6 14 l14 2 l-11 9 l4 14 l-13 -8 l-13 8 l4 -14 l-11 -9Z" fill="#ff8a3d"/>'+
  ten+'<ellipse cx="200" cy="190" rx="70" ry="64" fill="#b07ae6"/><ellipse cx="180" cy="160" rx="22" ry="14" fill="#c99bf0"/>'+
  eye(178,200,11)+eye(222,200,11)+'<path d="M188 226 Q200 236 212 226" stroke="#4a2275" stroke-width="3" fill="none" stroke-linecap="round"/>'+
  '<circle cx="158" cy="222" r="9" fill="#ff9acb" opacity=".55"/><circle cx="242" cy="222" r="9" fill="#ff9acb" opacity=".55"/>'+
  '<g><path d="M300 110 q30 -22 54 0 q-24 22 -54 0Z" fill="#ffd23f"/><path d="M300 110 l-16 -12 v24Z" fill="#ffd23f"/><circle cx="342" cy="106" r="3" fill="#1d1d2b"/><path d="M318 98 v24 M330 99 v22" stroke="#f08a24" stroke-width="4"/></g>'+
  '<g><path d="M60 140 q24 -18 44 0 q-20 18 -44 0Z" fill="#ff7a3d"/><path d="M104 140 l14 -10 v20Z" fill="#ff7a3d"/><circle cx="70" cy="137" r="3" fill="#1d1d2b"/><path d="M80 126 v28" stroke="#fff" stroke-width="4"/></g>'+
  '<g><path d="M250 290 q18 -14 34 0 q-16 14 -34 0Z" fill="#5fe0c8"/><path d="M284 290 l10 -8 v16Z" fill="#5fe0c8"/><circle cx="258" cy="288" r="2.5" fill="#1d1d2b"/></g>'+
  bubbles(r,26,10,320))})()});

/* 5. Panda and bamboo */
P.push({id:"panda",name:"Bamboo Panda",theme:"animals",svg:(()=>{const r=rng(55);let bam="";
  [30,75,330,372,120,285].forEach((x,i)=>{const c=i<4?"#5aa84a":"#8fd16f",w=i<4?16:11;
    for(let y=-10;y<330;y+=46+((i*13)%14))bam+='<rect x="'+(x-w/2)+'" y="'+y+'" width="'+w+'" height="'+(40+((i*13)%14))+'" rx="4" fill="'+c+'"/><rect x="'+(x-w/2-2)+'" y="'+(y-3)+'" width="'+(w+4)+'" height="6" rx="3" fill="#3f7d3a"/>';
    for(let k=0;k<3;k++){const y=40+k*90+i*15,s=k%2?1:-1;bam+='<path d="M'+x+" "+y+" q"+(s*30)+" -14 "+(s*52)+" 4 q"+(s*-26)+" 6 "+(s*-52)+' -4Z" fill="#6fc25a"/>'}});
  return svg("<defs>"+lin("s5",["#e9f7d9","#c8ecb0","#a6d98a"])+"</defs>"+
  '<rect width="400" height="400" fill="url(#s5)"/>'+cloud(200,60,1.2,"#fff",.8)+cloud(90,120,.7,"#fff",.6)+bam+
  '<path d="M0 320 Q100 300 200 318 T400 312 V400 H0Z" fill="#7cc25e"/>'+grass(r,322,22,80,["#5aa84a","#8fd16f","#3f8f3a"])+flowers(r,345,395,20,["#ffffff","#ffd84a","#ff9acb"])+
  '<ellipse cx="200" cy="290" rx="86" ry="70" fill="#fdfdfb"/>'+
  '<ellipse cx="140" cy="335" rx="32" ry="24" fill="#24242c"/><ellipse cx="260" cy="335" rx="32" ry="24" fill="#24242c"/><ellipse cx="140" cy="338" rx="14" ry="10" fill="#4a4a55"/><ellipse cx="260" cy="338" rx="14" ry="10" fill="#4a4a55"/>'+
  '<path d="M128 250 C108 270 110 300 132 306 C150 300 150 270 150 250Z" fill="#24242c"/>'+
  '<rect x="246" y="150" width="12" height="160" rx="5" fill="#5aa84a" transform="rotate(12 252 230)"/><path d="M262 160 q30 -20 50 -2 q-26 8 -50 2Z" fill="#6fc25a"/>'+
  '<path d="M272 250 C292 270 290 300 268 306 C250 300 250 270 250 250Z" fill="#24242c"/>'+
  '<circle cx="148" cy="148" r="24" fill="#24242c"/><circle cx="252" cy="148" r="24" fill="#24242c"/>'+
  '<ellipse cx="200" cy="190" rx="70" ry="60" fill="#fdfdfb"/>'+
  '<ellipse cx="172" cy="188" rx="17" ry="22" fill="#24242c" transform="rotate(-20 172 188)"/><ellipse cx="228" cy="188" rx="17" ry="22" fill="#24242c" transform="rotate(20 228 188)"/>'+
  eye(174,188,6)+eye(226,188,6)+'<ellipse cx="200" cy="214" rx="10" ry="7" fill="#24242c"/><path d="M190 226 Q200 234 210 226" stroke="#24242c" stroke-width="3" fill="none" stroke-linecap="round"/>'+
  '<circle cx="152" cy="214" r="9" fill="#ffb0c4" opacity=".6"/><circle cx="248" cy="214" r="9" fill="#ffb0c4" opacity=".6"/>'+
  '<g><path d="M330 220 q-14 -16 0 -22 q14 6 0 22Z" fill="#ff9acb"/><path d="M330 220 q14 -16 0 -22 q-14 6 0 22Z" fill="#ffd84a" transform="rotate(60 330 210)"/></g>'+
  '<g transform="translate(80 230)"><path d="M0 0 q-16 -14 -10 -24 q12 0 10 24Z" fill="#7ad0ff"/><path d="M0 0 q16 -14 10 -24 q-12 0 -10 24Z" fill="#b48cff"/></g>')})()});

/* 6. Turtle beach */
P.push({id:"turtle",name:"Turtle Beach",theme:"animals",svg:(()=>{const r=rng(66);let shell="";
  [[200,262],[176,250],[224,250],[188,282],[212,282],[164,274],[236,274]].forEach(([x,y],i)=>shell+='<path d="M'+x+" "+(y-13)+"l12 7v13l-12 7l-12 -7v-13Z\" fill=\""+(i%2?"#4f9a3e":"#5fb04a")+'" stroke="#2f6e2a" stroke-width="2"/>');
  return svg("<defs>"+lin("s6",["#5fc3ff","#a8e2ff","#e6f7ff"])+lin("sea",["#1fa8d8","#127aa8"])+lin("sd6",["#ffe6a8","#f4cf7c"])+"</defs>"+
  '<rect width="400" height="400" fill="url(#s6)"/><circle cx="320" cy="62" r="36" fill="#ffe14d"/>'+
  Array.from({length:12},(_,k)=>{const a=k*Math.PI/6;return'<path d="M'+(320+Math.cos(a)*44)+" "+(62+Math.sin(a)*44)+"L"+(320+Math.cos(a)*60)+" "+(62+Math.sin(a)*60)+'" stroke="#ffe14d" stroke-width="5" stroke-linecap="round"/>'}).join("")+
  cloud(80,60,1,"#fff")+cloud(190,100,.7,"#fff",.9)+
  '<path d="M0 150 H400 V230 H0Z" fill="url(#sea)"/>'+
  Array.from({length:5},(_,k)=>'<path d="M0 '+(162+k*14)+" "+Array.from({length:10},(_,j)=>"q10 -6 20 0 t20 0").join(" ")+'" stroke="#d8f6ff" stroke-width="2" fill="none" opacity="'+(.7-k*.1)+'"/>').join("")+
  '<path d="M300 160 l14 -24 l4 24Z" fill="#fff"/><path d="M290 162 h40 l-8 8 h-26Z" fill="#e2412e"/>'+
  '<path d="M0 222 Q100 236 200 224 T400 228 V400 H0Z" fill="url(#sd6)"/><path d="M0 224 Q100 238 200 226 T400 230" stroke="#fff" stroke-width="5" fill="none" opacity=".8"/>'+
  Array.from({length:60},()=>'<circle cx="'+(r()*400).toFixed(1)+'" cy="'+(240+r()*160).toFixed(1)+'" r="'+(1+r()*1.6).toFixed(1)+'" fill="#d9ae5c" opacity=".7"/>').join("")+
  '<path d="M350 240 C346 190 352 140 342 100" stroke="#8a5a2b" stroke-width="12" fill="none" stroke-linecap="round"/>'+
  [[-70,10],[-40,-25],[0,-35],[40,-15],[60,20]].map(([dx,dy])=>'<path d="M342 100 q'+dx*.5+" "+(dy-20)+" "+dx+" "+dy+" q"+(-dx*.4)+" "+(-dy*.2-6)+" "+(-dx)+" "+(-dy)+'Z" fill="#3f9a3a"/>').join("")+
  '<circle cx="336" cy="108" r="7" fill="#7a4a1e"/><circle cx="348" cy="110" r="7" fill="#7a4a1e"/>'+
  '<ellipse cx="150" cy="296" rx="16" ry="9" fill="#6fae52" transform="rotate(-30 150 296)"/><ellipse cx="252" cy="298" rx="16" ry="9" fill="#6fae52" transform="rotate(30 252 298)"/>'+
  '<ellipse cx="160" cy="238" rx="15" ry="9" fill="#6fae52" transform="rotate(30 160 238)"/><ellipse cx="244" cy="238" rx="15" ry="9" fill="#6fae52" transform="rotate(-30 244 238)"/>'+
  '<ellipse cx="200" cy="268" rx="58" ry="44" fill="#3f8a34"/>'+shell+
  '<ellipse cx="200" cy="206" rx="22" ry="20" fill="#7cc25e"/>'+eye(192,202,4.5)+eye(208,202,4.5)+'<path d="M193 214 Q200 219 207 214" stroke="#2f6e2a" stroke-width="2.5" fill="none" stroke-linecap="round"/>'+
  '<path d="M70 340 l7 -16 l7 16 l17 1 l-13 11 l5 16 l-16 -9 l-16 9 l5 -16 l-13 -11Z" fill="#ff7a5a"/>'+
  '<path d="M300 340 q14 -24 28 0Z" fill="#ffc9d9"/><path d="M304 340 q10 -16 20 0" stroke="#e892ad" stroke-width="2" fill="none"/>'+
  '<circle cx="110" cy="372" r="6" fill="#fff4d6"/><circle cx="270" cy="378" r="5" fill="#ffe2ef"/>')})()});

/* 7. Astronaut */
P.push({id:"astronaut",name:"Space Walk",theme:"space",svg:(()=>{const r=rng(77);return svg(
  "<defs>"+rad("sp7",["#1b2a6b","#0b1236","#03040c"],.2,.2,1)+rad("ea",["#7fd0ff","#2f7fe0","#1b4fa8"],.35,.3,.8)+lin("vi",["#ffe28a","#f2a73b","#c46a1e"],1,1)+"</defs>"+
  '<rect width="400" height="400" fill="url(#sp7)"/>'+stars(r,150,0,400)+
  '<circle cx="330" cy="350" r="150" fill="url(#ea)"/>'+
  '<path d="M220 300 q30 -30 60 -10 q20 20 50 0 q14 30 -10 50 q-40 20 -60 0 q-30 -10 -40 -40Z" fill="#5fbf5a"/><path d="M330 230 q30 -10 50 10 q-10 30 -40 20 q-20 -10 -10 -30Z" fill="#6fcf5f"/><path d="M200 380 q20 -20 50 -10 q10 20 -20 30Z" fill="#5fbf5a"/>'+
  '<path d="M240 260 q40 -14 70 0" stroke="#fff" stroke-width="8" fill="none" opacity=".7" stroke-linecap="round"/><path d="M260 330 q30 -10 60 4" stroke="#fff" stroke-width="7" fill="none" opacity=".6" stroke-linecap="round"/>'+
  '<g transform="rotate(-14 150 170)">'+
  '<rect x="96" y="120" width="44" height="80" rx="12" fill="#c9cfdb"/>'+
  '<path d="M150 236 q-26 40 -10 66" stroke="#eef1f7" stroke-width="24" fill="none" stroke-linecap="round"/><path d="M178 236 q20 40 40 56" stroke="#eef1f7" stroke-width="24" fill="none" stroke-linecap="round"/>'+
  '<ellipse cx="140" cy="306" rx="16" ry="12" fill="#9aa3b5"/><ellipse cx="222" cy="296" rx="16" ry="12" fill="#9aa3b5"/>'+
  '<rect x="116" y="140" width="96" height="104" rx="34" fill="#f4f6fa"/>'+
  '<path d="M124 170 q-40 -10 -54 -40" stroke="#eef1f7" stroke-width="22" fill="none" stroke-linecap="round"/><path d="M206 172 q40 10 52 -26" stroke="#eef1f7" stroke-width="22" fill="none" stroke-linecap="round"/>'+
  '<circle cx="68" cy="126" r="13" fill="#9aa3b5"/><circle cx="260" cy="142" r="13" fill="#9aa3b5"/>'+
  '<rect x="140" y="196" width="48" height="30" rx="6" fill="#d7dde8"/><circle cx="152" cy="211" r="5" fill="#e2412e"/><circle cx="166" cy="211" r="5" fill="#3b6fd9"/><rect x="176" y="205" width="8" height="12" rx="2" fill="#6bb34a"/>'+
  '<circle cx="164" cy="116" r="50" fill="#f4f6fa"/><circle cx="164" cy="118" r="38" fill="url(#vi)"/><path d="M142 104 a26 26 0 0 1 26 -14" stroke="#fff6d6" stroke-width="7" fill="none" stroke-linecap="round" opacity=".9"/>'+
  '<rect x="154" y="62" width="20" height="10" rx="4" fill="#c9cfdb"/></g>'+
  '<g transform="translate(320 70) rotate(20)"><rect x="-12" y="-8" width="24" height="16" rx="3" fill="#d7dde8"/><rect x="-52" y="-6" width="34" height="12" fill="#3b6fd9"/><rect x="18" y="-6" width="34" height="12" fill="#3b6fd9"/>'+
  '<path d="M-52 0h34M18 0h34M-41 -6v12M-29 -6v12M29 -6v12M41 -6v12" stroke="#8fc3ff" stroke-width="1.5"/><circle cx="0" cy="-14" r="4" fill="#ffd23f"/></g>'+
  '<circle cx="40" cy="340" r="14" fill="#d6d1b6"/><circle cx="35" cy="335" r="4" fill="#b7b195"/><circle cx="46" cy="346" r="3" fill="#b7b195"/>')})()});

/* 8. Lion on the savanna */
P.push({id:"lion",name:"Savanna Lion",theme:"animals",svg:(()=>{const r=rng(88);let mane="";
  for(let k=0;k<18;k++){const a=k*Math.PI/9,x=200+Math.cos(a)*62,y=210+Math.sin(a)*58;mane+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="30" fill="'+(k%2?"#b8541c":"#cf6a22")+'"/>'}
  return svg("<defs>"+lin("s8",["#ff9b4a","#ffc463","#ffe3a0"])+lin("g8",["#e8b04a","#c98a2e"])+"</defs>"+
  '<rect width="400" height="400" fill="url(#s8)"/><circle cx="200" cy="150" r="110" fill="#fff0b8" opacity=".55"/><circle cx="200" cy="150" r="70" fill="#fff4c9"/>'+
  '<g fill="#7a3f1e" opacity=".7"><path d="M60 80 q8 -8 16 0 q8 -8 16 0" stroke="#7a3f1e" stroke-width="3" fill="none"/><path d="M300 60 q6 -6 12 0 q6 -6 12 0" stroke="#7a3f1e" stroke-width="2.5" fill="none"/><path d="M330 100 q5 -5 10 0 q5 -5 10 0" stroke="#7a3f1e" stroke-width="2" fill="none"/></g>'+
  '<path d="M0 250 Q100 236 200 246 T400 240 V400 H0Z" fill="#d99a3c"/>'+
  '<path d="M48 250 C52 210 46 180 58 150" stroke="#4a2a14" stroke-width="9" fill="none"/><path d="M58 150 L20 140 M58 150 L100 136 M54 175 L28 168" stroke="#4a2a14" stroke-width="5"/>'+
  '<ellipse cx="60" cy="134" rx="62" ry="16" fill="#4f6a2a"/><ellipse cx="40" cy="146" rx="34" ry="10" fill="#5f7d34"/>'+
  '<path d="M340 252 C344 220 340 200 348 180" stroke="#4a2a14" stroke-width="7" fill="none"/><ellipse cx="348" cy="170" rx="44" ry="12" fill="#4f6a2a"/>'+
  '<path d="M0 290 Q100 276 200 288 T400 282 V400 H0Z" fill="url(#g8)"/>'+grass(r,300,40,110,["#c98a2e","#e8b04a","#a86e22","#f2c264"])+
  mane+'<ellipse cx="200" cy="330" rx="74" ry="50" fill="#e89a3a"/>'+
  '<ellipse cx="150" cy="368" rx="22" ry="14" fill="#f0a848"/><ellipse cx="250" cy="368" rx="22" ry="14" fill="#f0a848"/>'+
  '<circle cx="158" cy="166" r="16" fill="#e89a3a"/><circle cx="242" cy="166" r="16" fill="#e89a3a"/><circle cx="158" cy="166" r="8" fill="#c76a2a"/><circle cx="242" cy="166" r="8" fill="#c76a2a"/>'+
  '<ellipse cx="200" cy="212" rx="56" ry="52" fill="#f2aa48"/>'+
  eye(180,200,7)+eye(220,200,7)+'<ellipse cx="200" cy="236" rx="26" ry="18" fill="#ffe2b0"/><path d="M190 226 L210 226 L200 238Z" fill="#6a3418"/>'+
  '<path d="M200 238 v6 M188 248 Q200 256 212 248" stroke="#6a3418" stroke-width="3" fill="none" stroke-linecap="round"/>'+
  '<g fill="#6a3418"><circle cx="184" cy="240" r="1.6"/><circle cx="178" cy="234" r="1.6"/><circle cx="216" cy="240" r="1.6"/><circle cx="222" cy="234" r="1.6"/></g>'+
  '<circle cx="164" cy="228" r="8" fill="#ff9a80" opacity=".5"/><circle cx="236" cy="228" r="8" fill="#ff9a80" opacity=".5"/>'+
  flowers(r,360,396,10,["#ffffff","#ff7a5a"]))})()});

return P})();
