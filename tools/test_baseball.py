"""Browser tests for Baseball.  python3 tools/test_baseball.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []
def player(grade, pid):
    return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐯',grade:{grade},color:'#3b6fd9'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(json.dumps({g: 1 for g in GAMES}))})")
# plays the level in fast simulated time. mode "perfect": swing right on time at strikes, let balls go; "never": never swing
PLAY = """((mode,max)=>{const G=__game,S=G.S;S.manual=true;let i=0,hits={};
  for(;i<max&&!S.done;i++){const p=S.pitch;if(S.phase==="intro")G.swing();
    if(mode==="perfect"&&S.phase==="pitch"&&p&&p.strike&&!S.swing&&S.t+1/240>=p.ta-.1)G.swing();
    if(S.hit&&!S.hit.counted){S.hit.counted=1;hits[S.hit.res]=(hits[S.hit.res]||0)+1}
    G.step(1/240)}
  return{done:S.done,runs:S.runs,outs:S.outs,target:S.C.target,hits,secs:Math.round(S.t)}})"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for grade in (1, 4, 7):
        ctx = b.new_context(viewport={"width": 1024, "height": 768}); ctx.add_init_script(player(grade, f"g{grade}"))
        pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("baseball")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
        res = []
        for lv in (1, 6, 12, 20, 30, 40):
            pg.evaluate(f"__game.K.load({lv})"); pg.wait_for_timeout(60)
            if pg.is_visible(".prob"): solve_math(pg)
            res.append((lv, pg.evaluate(PLAY + "('perfect',400000)")))
        bad = [(lv, r) for lv, r in res if not r["done"] or r["outs"] or r["runs"] < r["target"]]
        check(not bad, f"grade {grade}: perfect swings win every level with no outs (targets {[r['target'] for _, r in res]}) {bad[:2]}")
        allhits = {}
        for _, r in res:
            for k, v in r["hits"].items(): allhits[k] = allhits.get(k, 0) + v
        check(set(allhits) <= {"hr", "triple", "double"} and allhits.get("hr"), f"grade {grade}: perfect timing gives big hits {allhits}")
        pg.evaluate("__game.K.load(1)"); pg.wait_for_timeout(60)
        if pg.is_visible(".prob"): solve_math(pg)
        r = pg.evaluate(PLAY + "('never',400000)")
        check(r["done"] and r["outs"] == 3 and r["runs"] == 0, f"grade {grade}: never swinging strikes out 3 times {r}")
        pg.wait_for_timeout(2200)
        check(pg.is_visible("#kSheetWin") and "Three outs" in pg.text_content("#kWinTitle"), f"grade {grade}: three outs shows Try again")
        ctx.close()

    # pitch speed goes up with level and grade; changeups and curves come later
    ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(player(1, "c1"))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("baseball")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
    c1, c40 = pg.evaluate("[__game.cfg(1),__game.cfg(40)]")
    check(c40["tp"] < c1["tp"] and c1["ball"] == 0 and c1["curve"] == 0 and c40["curve"] > 0 and c40["target"] > c1["target"], "harder pitches and more runs needed at higher levels")
    # a real tap: SWING during a pitch counts as a swing; win sheet after a real perfect level
    pg.evaluate("__game.S.phase='windup';__game.S.pt=__game.S.t"); pg.wait_for_function("__game.S.phase==='pitch'", timeout=8000)
    pg.click("#bbSwing")
    check(pg.evaluate("!!__game.S.swing"), "tapping SWING during a pitch swings the bat")
    pg.screenshot(path=str(OUT / "baseball_phone.png"))
    # hint: slow pitch down the middle with a guide ring
    pg.evaluate("__game.K.load(2)"); pg.wait_for_timeout(100); pg.click("#kHint"); solve_math(pg); pg.wait_for_timeout(200)
    pg.evaluate("__game.S.phase='windup';__game.S.pt=__game.S.t"); pg.wait_for_function("__game.S.phase==='pitch'", timeout=8000)
    check(pg.evaluate("__game.S.pitch.guide && __game.S.pitch.strike && __game.S.pitch.kind==='fast'"), "the hint pitch is a slow strike with a guide ring")
    pg.evaluate(PLAY + "('perfect',400000)"); pg.wait_for_timeout(2400)
    check(pg.is_visible("#kSheetWin") and "done" in pg.text_content("#kWinTitle"), "winning shows the level-done card")
    ctx.close()
    check(not errors, f"no page errors {errors[:3]}")
sys.exit(check.finish())
