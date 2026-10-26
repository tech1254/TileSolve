"""Browser tests for Code the Robot.  python3 tools/test_robot.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []

def player(grade, pid="rb"):
    return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐸',grade:{grade},color:'#43a047'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(json.dumps({g: 1 for g in GAMES + ['robot']}))})")

VALIDATE = """(()=>{const bad=[];let pars=[];
  for(let lv=1;lv<=40;lv++){const L=__game.build(lv),sp=__game.spec(lv);if(!L){bad.push(lv+' no puzzle');continue}
    const sol=__game.bfs(L,{r:L.start[0],c:L.start[1],d:L.d0,g:0});if(!sol||sol.length!==L.par)bad.push(lv+' par');
    if(L.par<sp.lo||L.par>sp.hi)bad.push(lv+' par '+L.par+' out of range');if(L.rock.size!==sp.rocks||L.gems.length!==sp.gems)bad.push(lv+' contents');
    // following the solution really ends on the star with every gem
    let s={r:L.start[0],c:L.start[1],d:L.d0,g:0};for(const cm of sol)s=__game.step(L,s,cm);
    if(s.crash||s.r!==L.goal[0]||s.c!==L.goal[1]||s.g!==(1<<L.gems.length)-1)bad.push(lv+' solution fails');pars.push(L.par)}
  return{bad:bad.slice(0,6),nb:bad.length,pars:pars.filter((_,i)=>i%5===0)}})()"""

def wait_idle(pg, ms=15000):
    pg.wait_for_function("!__game.S.running", timeout=ms)

with sync_playwright() as p:
    b = p.chromium.launch()
    for grade in range(1, 8):
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(player(grade))
        pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("robot")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
        v = pg.evaluate(VALIDATE)
        check(v["nb"] == 0, f"grade {grade}: 40 puzzles, each solvable with the right number of moves (shortest every 5 levels: {v['pars']}) {v['bad']}")
        mode = pg.evaluate("[...document.querySelectorAll('.rb-cmds [data-cmd]')].map(b=>b.dataset.cmd)")
        check(mode == (["F", "L", "R"] if grade >= 4 else ["3", "0", "2", "1"]), f"grade {grade}: {'Forward/Turn' if grade >= 4 else 'arrow'} buttons")
        if grade in (1, 4, 7):
            pg.evaluate("__game.K.load(30)"); pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / f"robot-g{grade}.png"))
            pg.evaluate("__game.solve()"); pg.wait_for_timeout(9000)
            check(pg.is_visible("#kSheetWin"), f"grade {grade}: level 30 shortest program wins")
        ctx.close()

    ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(player(2))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("robot")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
    sol = pg.evaluate("__game.bfs(__game.S.L,{r:__game.S.L.start[0],c:__game.S.L.start[1],d:__game.S.L.d0,g:0})")
    # too short a program stops before the star
    pg.click(f".rb-cmds [data-cmd='{sol[0]}']"); pg.click("#rbGo"); pg.wait_for_timeout(600); wait_idle(pg)
    check("Oops 1" in pg.text_content("#kSub") and not pg.is_visible("#kSheetWin"), "stopping before the star counts an oops")
    check(pg.locator(".rb-chip").count() == 1, "the program is kept so it can be fixed")
    # walking off the edge bumps
    pg.click(".rb-cmds .ed >> nth=1")
    L = pg.evaluate("({r:__game.S.L.start[0],c:__game.S.L.start[1],rows:__game.S.L.rows,cols:__game.S.L.cols})")
    edge = 0 if L["r"] == 0 else 2 if L["r"] == L["rows"]-1 else 3 if L["c"] == 0 else 1
    steps = {0: L["r"]+1, 2: L["rows"]-L["r"], 3: L["c"]+1, 1: L["cols"]-L["c"]}[edge]
    for _ in range(steps): pg.click(f".rb-cmds [data-cmd='{edge}']")
    pg.click("#rbGo"); pg.wait_for_timeout(400); wait_idle(pg)
    check("Oops 2" in pg.text_content("#kSub"), "bumping into the edge or a rock counts an oops")
    pg.click(".rb-cmds .ed >> nth=1")
    check(pg.locator(".rb-chip").count() == 0, "🗑️ clears the program")
    pg.click("#kHint"); pg.wait_for_timeout(400)
    if pg.is_visible(".prob"): solve_math(pg)
    check(pg.evaluate("__game.S.prog") == sol[:1], "a hint (after a maths question) adds the next good move")
    for cm in sol[1:]: pg.click(f".rb-cmds [data-cmd='{cm}']")
    pg.click(".rb-chip >> nth=0"); check(pg.locator(".rb-chip").count() == len(sol) - 1, "tapping a step removes it")
    pg.click(".rb-cmds .ed >> nth=0"); pg.click(".rb-cmds .ed >> nth=1")
    for cm in sol: pg.click(f".rb-cmds [data-cmd='{cm}']")
    pg.click("#rbGo"); pg.wait_for_timeout(len(sol) * 340 + 1500)
    check(pg.is_visible("#kSheetWin"), "the right program wins the level")
    ctx.close()

    # ---------- iPad touch, turn mode ----------
    tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(player(5, "t5"))
    tp = watch_errors(tctx.new_page(), errors); tp.goto(URL("robot")); tp.wait_for_function("window.__game && __game.S", timeout=10000)
    sol = tp.evaluate("__game.bfs(__game.S.L,{r:__game.S.L.start[0],c:__game.S.L.start[1],d:__game.S.L.d0,g:0})")
    for cm in sol: tap_center(tp, f".rb-cmds [data-cmd='{cm}']")
    tp.screenshot(path=str(OUT / "robot-ipad.png"))
    tap_center(tp, "#rbGo"); tp.wait_for_timeout(len(sol) * 340 + 1500)
    check(tp.is_visible("#kSheetWin"), f"touch: building a Forward/Turn program ({''.join(sol)}) and pressing Go wins")
    tctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
