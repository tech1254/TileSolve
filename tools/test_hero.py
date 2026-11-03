"""Browser tests for Hero Rush.  python3 tools/test_hero.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
check = Checker(); errors = []
def player(grade, pid, hero=None, allopen=False):
    js = (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐯',grade:{grade},color:'#3b6fd9'}}],current:'{pid}',music:true}}));"
          f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(SEEN)});")
    if hero or allopen:
        js += f"if(!sessionStorage.h){{sessionStorage.h=1;localStorage.setItem('tilesolve:p:{pid}:hero',JSON.stringify({{grades:{{}},all:{str(allopen).lower()},hero:{json.dumps(hero) if hero else 'undefined'}}}))}}"
    return js
# a bot that only presses the buttons: hold right, jump at pits, baddies and spikes; on boss levels wait for the dizzy boss and jump on it
BOT = """((n,secs)=>{const G=__game,K=G.K;window.__heroHold=true;K.load(n);const S0=G.S;const IN=G.IN;IN.r=1;let t=0,res=null;
  const solid=x=>G.S.L.gy[Math.floor(x/20)]!=null&&G.S.L.gy[Math.floor(x/20)+1]!=null;
  for(;t<secs;t+=1/120){const S=G.S;if(S!==S0)break;if(S.done){res=S.hearts>0?"win":"fail";break}
    if(S.boss){const B=S.boss;IN.l=0;IN.r=0;const d=B.x-S.x;
      const wv=S.waves&&S.waves.some(w=>Math.abs(w.x-S.x)<110&&(Math.sign(S.x-w.x)===w.d||Math.abs(w.x-S.x)<30));
      if(B.st==="dizzy"){const want=S.on&&Math.abs(d)<170&&Math.abs(S.vx)>200?0:Math.sign(d);IN.r=want>0&&Math.abs(d)>6?1:0;IN.l=want<0&&Math.abs(d)>6?1:0;if(((Math.abs(d)<110&&Math.abs(S.vx)<=260)||wv)&&S.on)IN.jp=1;IN.j=1}
      else{IN.j=0;const tx=B.st==="hop"?B.tx:B.x,dd=tx-S.x;if(Math.abs(dd)<260){const away=dd>0?-1:1,edge=(away<0&&S.x<200)||(away>0&&S.x>S.L.end-200);const go=edge?-away:away;IN.l=go<0?1:0;IN.r=go>0?1:0}if(S.waves&&S.waves.some(w=>Math.abs(w.x-S.x)<90&&Math.sign(S.x-w.x)===w.d)&&S.on){IN.jp=1;IN.j=1}}}
    else{IN.r=1;IN.l=0;let jump=false;const v=Math.max(S.vx,150),la=40+v*.18;
      if(S.on){for(let x=S.x+10;x<S.x+la;x+=10)if(!solid(x))jump=true;
        for(const f of S.L.foes)if(f.alive&&f.t!=='bird'&&f.x>S.x&&f.x-S.x<70+v*.12)jump=true;
        for(const k of S.L.spikes)if(k.x>S.x&&k.x-S.x<30+v*.15)jump=true}
      if(jump){IN.jp=1;IN.j=1}else if(S.on)IN.j=0}
    G.step(1/120)}
  IN.r=IN.l=IN.j=0;window.__heroHold=false;const S=G.S;return{res:res||"timeout",t:Math.round(t),lost:S.lost,got:S.got,total:S.total,x:Math.round(S.x),end:S.L.end}})"""
HERO = {"name": "Zap", "animal": "dog", "body": "#3b6fd9", "shoes": "#f2c230", "cape": "#e2412e", "emblem": "letter", "power": "double"}
with sync_playwright() as p:
    b = p.chromium.launch()
    # 1. the hero maker on first play
    ctx = b.new_context(viewport={"width": 1024, "height": 768}); ctx.add_init_script(player(4, "h1"))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("hero")); pg.wait_for_function("window.__game&&__game.S", timeout=10000); pg.wait_for_timeout(500)
    check(pg.is_visible(".hm") and pg.locator(".hm-chips[data-k='animal'] button").count() == 12, "first play opens the hero maker with 12 animals")
    pg.click(".hm-chips[data-k='animal'] button[data-v='dragon']"); pg.click(".hm-chips[data-k='body'] .sw[data-v='#43a047']")
    pg.click(".hm-chips[data-k='cape'] .sw[data-v='#8f5bd6']"); pg.click(".hm-chips[data-k='power'] button[data-v='turbo']"); pg.click(".hm-chips[data-k='emblem'] button[data-v='letter']")
    pg.fill("#hmName", "Captain Blaze")
    if OUT: pg.screenshot(path=str(OUT / "hero_maker.png"))
    pg.click("#hmGo"); pg.wait_for_timeout(500)
    h = pg.evaluate("__game.K.save.hero")
    check(not pg.is_visible(".hm") and h["animal"] == "dragon" and h["name"] == "Captain Blaze" and h["power"] == "turbo", f"the hero is saved ({h['name']}, {h['animal']}, {h['power']})")
    check("Captain Blaze" in pg.text_content("#kSub"), "the hero's name shows at the top")
    pg.wait_for_timeout(300)
    # 2. controls: holding right runs, jump jumps
    pg.dispatch_event("#hrR", "pointerdown", {"pointerId": 1}); pg.wait_for_timeout(900)
    x1 = pg.evaluate("__game.S.x"); check(x1 > 300 and pg.evaluate("__game.S.vx") > 300, f"holding ▶ runs fast ({x1:.0f})")
    if OUT: pg.screenshot(path=str(OUT / "hero_run.png"))
    pg.dispatch_event("#hrJ", "pointerdown", {"pointerId": 2}); pg.wait_for_timeout(150)
    check(not pg.evaluate("__game.S.on") and pg.evaluate("__game.S.vy") < 0, "tapping JUMP jumps")
    pg.dispatch_event("#hrJ", "pointerup", {"pointerId": 2}); pg.dispatch_event("#hrR", "pointerup", {"pointerId": 1}); pg.wait_for_timeout(800)
    pg.dispatch_event("#hrP", "pointerdown", {"pointerId": 3}); pg.wait_for_timeout(60); pg.dispatch_event("#hrP", "pointerup", {"pointerId": 3})
    check(pg.evaluate("__game.S.dash") > 0 and abs(pg.evaluate("__game.S.vx")) > 700, "the Turbo Dash power zooms")
    # 3. stomping, getting hurt, falling in a pit, checkpoints, sparks
    pg.evaluate("__game.K.load(1)"); pg.wait_for_timeout(300)
    SETUP = "const G=__game;G.K.load(1);const S=G.S;window.__heroHold=true;S.L.foes.length=0;S.x=500;S.y=S.L.gy[25];S.on=1;S.vx=0;S.vy=0;S.inv=0;S.dash=0;"
    r = pg.evaluate("()=>{"+SETUP+"""const f={t:'slime',x:520,x0:400,x1:700,y:S.y,fy:S.y,dir:-1,alive:1,ph:0};S.L.foes.push(f);S.y-=120;S.on=0;S.vy=100;
      for(let i=0;i<120&&f.alive;i++)G.step(1/120);window.__heroHold=false;return{stomped:!f.alive,hearts:G.S.hearts}}""")
    check(r["stomped"] and r["hearts"] == 3, f"jumping on a baddy bops it {r}")
    r = pg.evaluate("()=>{"+SETUP+"""const f={t:'slime',x:530,x0:400,x1:700,y:S.y,fy:S.y,dir:-1,alive:1,ph:0};S.L.foes.push(f);
      for(let i=0;i<60;i++)G.step(1/120);window.__heroHold=false;return{hearts:G.S.hearts,alive:f.alive}}""")
    check(r["hearts"] == 2 and r["alive"], f"running into a baddy costs a heart {r}")
    r = pg.evaluate("()=>{"+SETUP+"""const sp={x:S.x+5,y:S.y-28,got:0};S.L.sparks.push(sp);S.total++;G.step(1/120);window.__heroHold=false;return sp.got===1}""")
    check(r, "touching a spark collects it")
    r = pg.evaluate("()=>{"+SETUP+"""const f=S.L.flags[0];S.x=f.x-30;S.y=f.y;S.vx=500;for(let i=0;i<60;i++)G.step(1/120);const cp=S.cp.x===f.x&&f.on===1;
      let pi=S.L.gy.findIndex((y,i)=>i*20>f.x&&y==null);S.x=pi*20+30;S.y=600;S.on=0;S.vx=0;S.vy=0;S.inv=0;const h0=S.hearts;for(let i=0;i<300;i++)G.step(1/120);
      window.__heroHold=false;return{cp,fell:S.hearts===h0-1,back:Math.abs(S.x-S.cp.x)<40&&S.cp.x>=f.x,x:Math.round(S.x),fx:S.cp.x}}""")
    check(r["cp"], f"passing a flag sets a checkpoint {r}")
    check(r["fell"] and r["back"], f"falling in a pit costs a heart and goes back to the checkpoint {r}")
    ctx.close()
    # 4. the bot plays every level using only the buttons
    ctx = b.new_context(viewport={"width": 1024, "height": 768}); ctx.add_init_script(player(4, "h2", HERO, True))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("hero")); pg.wait_for_function("window.__game&&__game.S", timeout=10000); pg.wait_for_timeout(300)
    check(not pg.is_visible(".hm"), "a saved hero skips the maker")
    pg.evaluate("window.__heroNoMission=true")
    loops = 0; results = {}
    for n in range(1, 25):
        r = pg.evaluate(BOT + f"({n},150)"); results[n] = r
        loops += len(pg.evaluate("__game.S.L.loops"))
        if n in (2, 4, 10, 15, 22) and OUT:
            pg.evaluate(f"__game.K.load({n})"); pg.wait_for_timeout(200)
            pg.evaluate("(()=>{const S=__game.S;window.__heroHold=true;const lp=S.L.loops[0];if(lp){S.x=lp.x-260;S.y=lp.y}else if(S.boss){S.x=900}for(let i=0;i<60;i++)__game.step(1/120);window.__heroHold=false})()")
            pg.wait_for_timeout(250); pg.screenshot(path=str(OUT / f"hero_l{n}.png"))
    bad = {n: r for n, r in results.items() if r["res"] != "win"}
    check(not bad, f"a simple button-pressing bot finishes all 24 levels {bad}")
    check(loops >= 8, f"there are loop-the-loops to zoom round ({loops})")
    print("  bot:", {n: (r["t"], r["lost"], f"{r['got']}/{r['total']}") for n, r in results.items()})
    ctx.close()
    # 5. story missions: maths to fix the Number Engines
    for grade in (1, 3, 5):
        ctx = b.new_context(viewport={"width": 1024, "height": 768}); ctx.add_init_script(player(grade, f"ms{grade}", HERO, True))
        pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("hero")); pg.wait_for_function("window.__game&&__game.S", timeout=10000); pg.wait_for_timeout(300)
        bad = pg.evaluate("""()=>{const out=[];for(let age=0;age<=5;age++)for(let w=0;w<6;w++)for(let i=0;i<150;i++){const q=__game.mathQ(age,w,Math.random);
          if(!(Number.isInteger(q.ans)&&q.ans>=0&&q.ans<100000&&q.eq.includes('?')&&q.text&&q.how))out.push([age,w,q])}return out.slice(0,3)}""")
        if grade == 1: check(not bad, f"5400 maths problems for every grade and world have whole-number answers and a how-to {bad}")
        pg.evaluate("(()=>{const S=__game.S;S.x=S.L.end+2;S.on=1;S.y=S.L.gy[Math.floor(S.x/20)]})()"); pg.wait_for_timeout(2000)
        check(pg.is_visible(".ms") and "Professor Muddle" in pg.text_content(".ms-story") and not pg.is_visible("#kSheetWin"), f"grade {grade}: winning level 1 opens the first story mission before the next level")
        if OUT: pg.screenshot(path=str(OUT / f"hero_mission_g{grade}.png"))
        q = pg.evaluate("__mission.q"); pg.evaluate(f"__mission.answer({q['ans']+1})"); pg.wait_for_timeout(300)
        check("Not quite" in pg.text_content("#msHelp") and str(q["ans"]) in pg.text_content("#msHelp"), f"grade {grade}: a wrong answer shows the answer and how to work it out")
        pg.wait_for_timeout(4000)
        check(pg.evaluate("__mission.q.text") != q["text"] or pg.evaluate("__mission.q.eq") != q["eq"], f"grade {grade}: then a fresh problem")
        for k in range(3):
            pg.evaluate("__mission.answer(__mission.q.ans)"); pg.wait_for_timeout(1100)
        check("done" in pg.text_content("#msQ") and pg.evaluate("__game.K.save.eng[0]") == 1, f"grade {grade}: 3 right answers fix part 1 of the Meadow engine")
        pg.click(".ms-btn"); pg.wait_for_timeout(1200)
        check(pg.is_visible("#kSheetWin") and not pg.is_visible(".ms"), f"grade {grade}: then the level-done card shows")
        # replaying a level already won: no mission
        pg.evaluate("__game.K.load(1)"); pg.wait_for_timeout(300)
        pg.evaluate("(()=>{const S=__game.S;S.x=S.L.end+2;S.on=1;S.y=S.L.gy[Math.floor(S.x/20)]})()"); pg.wait_for_timeout(2400)
        check(pg.is_visible("#kSheetWin") and not pg.is_visible(".ms"), f"grade {grade}: replaying a won level skips the mission")
        if grade == 3:
            # level 3 win: the usual maths checkpoint is replaced by the missions
            for n in (2, 3):
                pg.evaluate(f"__game.K.load({n})"); pg.wait_for_timeout(300)
                pg.evaluate("(()=>{const S=__game.S;S.x=S.L.end+2;S.on=1;S.y=S.L.gy[Math.floor(S.x/20)]})()"); pg.wait_for_timeout(1700)
                for k in range(3): pg.evaluate("__mission.answer(__mission.q.ans)"); pg.wait_for_timeout(1100)
                pg.click(".ms-btn"); pg.wait_for_timeout(1200)
            check(pg.text_content("#kWinNext") == "Next level" and not pg.evaluate("(__game.K.save.grades[__game.K.age]||{}).gate"), f"grade {grade}: no extra maths checkpoint after level 3 ({pg.text_content('#kWinNext')})")
            pg.evaluate("__game.K.load(4)"); pg.wait_for_timeout(300)
            pg.evaluate("(()=>{const S=__game.S;S.boss.hp=0;})()"); pg.wait_for_timeout(2600)
            check(pg.is_visible(".ms") and "Restart" in pg.text_content(".ms-main h2"), "beating the boss leads to the Restart the engine mission")
            for k in range(3): pg.evaluate("__mission.answer(__mission.q.ans)"); pg.wait_for_timeout(1100)
            check("is saved" in pg.text_content("#msQ") and pg.evaluate("__game.K.save.eng[0]") == 4, "restarting the engine saves Meadow Run")
            if OUT: pg.screenshot(path=str(OUT / "hero_saved.png"))
        ctx.close()
    b.close()
check(not errors, f"no page errors {errors[:3]}")
check.finish()
