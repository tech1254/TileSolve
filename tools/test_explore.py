"""Browser tests for the "Learn & explore" games.  python3 tools/test_explore.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []
# game -> grade range shown on the home screen
EXPLORE = {"maketen": (1, 4), "times": (3, 7), "fractions": (2, 7), "money": (3, 7), "clock": (2, 7), "numberline": (1, 6), "patterns": (0, 7),
           "sentence": (1, 5), "spelling": (1, 7), "rhyme": (0, 3),
           "animals": (0, 5), "oddone": (0, 5), "planets": (2, 7), "foodchain": (2, 7), "places": (2, 7)}
LITTLE = {"rhyme"}  # in the Little learners section, not Learn & explore
HOME_EXPLORE = dict(EXPLORE, crossword=(2, 7), robot=(1, 7))

def player(grade, pid="ex"):
    seen = json.dumps({g: 1 for g in list(EXPLORE) + GAMES})
    return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐸',grade:{grade},color:'#43a047'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(seen)})")

VALIDATE = """((lo,hi)=>{const bad=[];let rounds=0;
  for(let a=lo;a<=hi;a++)for(let n=1;n<=40;n++){const r=TS.rngFrom(n*977+a*31+7);for(let i=0;i<8;i++){let R;
    try{R=__learn.make(n,i,r,a)}catch(e){bad.push(a+':'+n+':'+i+' threw '+e.message);continue}rounds++;const id=a+':'+n+':'+i+' '+R.type;
    if(!R.say||/undefined|NaN/.test(R.say+R.prompt))bad.push(id+' bad text '+R.say);
    if(R.type==='pick'){const ks=R.options.map(o=>String(o.key));if(new Set(ks).size!==ks.length)bad.push(id+' dup options '+ks);
      if(!ks.includes(String(R.answer)))bad.push(id+' answer missing '+R.answer+' in '+ks);if(ks.length<2)bad.push(id+' too few');
      if(R.options.some(o=>/NaN|undefined/.test(o.html)))bad.push(id+' bad option html')}
    else if(R.type==='order'){const ks=R.tiles.map(t=>String(t.val!==undefined?t.val:t.key));const left=ks.slice();for(const v of R.answer.map(String)){const j=left.indexOf(v);if(j<0){bad.push(id+' answer not in tiles '+v);break}left.splice(j,1)}
      if(new Set(R.tiles.map(t=>t.key)).size!==R.tiles.length)bad.push(id+' dup keys');
      if(ks.length>1&&ks.slice(0,R.answer.length).join()===R.answer.join())bad.push(id+' already in order')}
    else if(R.type==='combo'){const s=R.solution.reduce((t,k)=>t+R.cells[k].v,0);if(s!==R.target)bad.push(id+' solution '+s+' != '+R.target);
      if(R.cells.some(c=>!(c.v>0)))bad.push(id+' bad cell');if(R.solution.length<2)bad.push(id+' trivial')}
    else if(R.type==='sort'){const bk=R.bins.map(b=>b.key);if(R.items.some(x=>!bk.includes(x.key)))bad.push(id+' item without bin');if(R.items.length<2)bad.push(id+' few items');
      if(bk.some(k=>!R.items.some(x=>x.key===k)))bad.push(id+' empty bin');if(R.items.some(x=>!x||!x.html))bad.push(id+' bad item')}
    else bad.push(id+' unexpected type')}}
  return{bad:bad.slice(0,6),n:bad.length,rounds}})"""

def win_level(pg, limit=14):
    for _ in range(limit):
        if pg.is_visible("#kSheetWin"): return True
        pg.evaluate("__learn.R && !__learn.R.done && __learn.solve()"); pg.wait_for_timeout(1000)
    return pg.is_visible("#kSheetWin")

with sync_playwright() as p:
    b = p.chromium.launch()
    for g, (g0, g1) in EXPLORE.items():
        for grade in sorted({g0, g1, min(g1, 3)}):
            ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(player(grade))
            pg = watch_errors(ctx.new_page(), errors); pg.goto(URL(g)); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
            if grade == g0:
                v = pg.evaluate(VALIDATE + f"({max(-1, g0-1)},{g1-1})")
                check(v["n"] == 0, f"{g}: all {v['rounds']} rounds (content grades {g0-1} to {g1-1}, 40 levels) are well formed {v['bad']}")
            shown = pg.evaluate("({p:document.getElementById('lrPrompt').textContent.trim().length,d:document.querySelectorAll('#lrDots i').length})")
            check(shown["p"] > 0 and shown["d"] >= 3, f"{g} grade {grade}: question and progress dots are shown")
            pg.screenshot(path=str(OUT / f"explore-{g}-g{grade}.png"))
            R = pg.evaluate("({type:__learn.R.type,options:(__learn.R.options||[]).map(o=>String(o.key)),answer:String(__learn.R.answer)})")
            if R["type"] == "pick":
                wrong = next(k for k in R["options"] if k != R["answer"])
                pg.click(f".lr-opt[data-key=\"{wrong}\"]"); pg.wait_for_timeout(150)
                check("Oops 1" in pg.text_content("#kSub"), f"{g} grade {grade}: a wrong answer counts an oops")
            check(win_level(pg), f"{g} grade {grade}: playing every round wins the level")
            if grade == g0:
                pg.evaluate("__learn.K.load(30)"); pg.wait_for_timeout(400)
                check(win_level(pg), f"{g} grade {grade}: level 30 can be won")
            ctx.close()

    # ---------- combo rounds by touch: Make Ten and Money Shop ----------
    for g, grade in (("maketen", 3), ("money", 4)):
        tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(player(grade, f"t{grade}"))
        tp = watch_errors(tctx.new_page(), errors)
        tp.goto(URL(g)); tp.wait_for_function("window.__learn && __learn.R", timeout=10000)
        for _ in range(4):
            if tp.evaluate("__learn.R.type") == "combo": break
            tp.evaluate("__learn.solve()"); tp.wait_for_timeout(1000)
        check(tp.evaluate("__learn.R.type") == "combo", f"{g}: has a tap-to-add round")
        cells = tp.evaluate("__learn.R.cells.map(c=>c.v)"); sol = tp.evaluate("__learn.R.solution"); target = tp.evaluate("__learn.R.target")
        over = [k for k in range(len(cells)) if k not in sol and cells[k] > target - sum(cells[s] for s in sol[:-1])]
        for k in sol[:-1]: tap_center(tp, f".lr-cbt >> nth={k}")
        sub = tp.text_content("#lrSum")
        check(sub != "0" and sub != "0¢", f"{g}: total goes up when tapping ({sub})")
        if over:
            tap_center(tp, f".lr-cbt >> nth={over[0]}"); tp.wait_for_timeout(800)
            check("Oops 1" in tp.text_content("#kSub") and tp.locator(".lr-cbt.on").count() == len(sol) - 1, f"{g}: going over the target is an oops and is taken back")
        i0 = tp.evaluate("__learn.S.i")
        tap_center(tp, f".lr-cbt >> nth={sol[-1]}"); tp.wait_for_timeout(900)
        check(tp.evaluate("__learn.S.i") == i0 + 1 or tp.evaluate("__learn.R.done"), f"{g}: hitting the target exactly finishes the round")
        tp.screenshot(path=str(OUT / f"explore-ipad-{g}.png"))
        tctx.close()

    # ---------- home screen: grade ranges ----------
    for grade in range(0, 8):
        cg = b.new_context(viewport={"width": 390, "height": 844}); cg.add_init_script(player(grade, f"h{grade}"))
        hp = watch_errors(cg.new_page(), errors); hp.goto(HOME_URL); hp.wait_for_timeout(300)
        got = sorted(hp.evaluate("[...document.querySelectorAll(\".games[data-group='explore'] .game\")].map(e=>e.dataset.game)"))
        # Pattern Next, Animal Sort and Odd One Out are in the Little Learners app for K-2; the main app shows them from grade 3
        want = sorted(g for g, (a, z) in HOME_EXPLORE.items() if (max(a, 3) if g in ("patterns", "animals", "oddone") else a) <= grade <= z and g not in LITTLE)
        check(got == want, f"grade {grade}: Learn & explore shows {want}")
        if grade in (1, 5): hp.screenshot(path=str(OUT / f"home-explore-g{grade}.png"), full_page=True)
        cg.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
