"""Browser tests for Ball Run.  python3 tools/test_ballrun.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []

def player(grade, pid="br"):
    return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐸',grade:{grade},color:'#43a047'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(json.dumps({g: 1 for g in GAMES + ['ballrun']}))})")

# A careful driver: looks a little ahead, keeps to x positions that stay on the track and clear of walls.
AUTO = """(S)=>{const G=__game,sp=S.speed*S.slow,far=Math.min(4.5,sp*.5);let best=null,bl=-1,bd=1e9;
  for(let x=-1.6;x<=1.6001;x+=.05){let d=0;
    for(;d<=far;d+=.2){const z=S.z+d,t=S.t+d/sp,q=S.x+(x-S.x)*(1-Math.exp(-14*d/sp)); // where the ball really is by then
      const air=S.T.pads.some(p=>S.z>=p.z0-1&&S.z<=p.land);let ok=air||(S.y>.01)||(G.platAt(q-.1,z,t)&&G.platAt(q+.1,z,t));
      for(const w of S.T.walls){const dx=G.at(w,t);if(z+.45>=w.z0&&z-.45<=w.z1&&q+.45>=w.x0+dx&&q-.45<=w.x1+dx)ok=false}if(!ok)break}
    const dist=Math.abs(x-S.x);if(d>bl+1e-9||(Math.abs(d-bl)<1e-9&&dist<bd)){bl=d;bd=dist;best=x}}
  if(best!==null)S.target=best}"""
RUN = """((maxSteps)=>{const S=__game.S;S.auto=eval(%s);S.running=true;let i=0;
  for(;i<maxSteps&&!S.done;i++){__game.step(1/60);if(S.dying){__game.step(.7)}if(!S.running)S.running=true}
  return{done:S.done,falls:S.falls,z:+S.z.toFixed(1),len:S.T.finish,gems:S.gems,total:S.T.gems.length,steps:i}})""" % json.dumps(AUTO)

with sync_playwright() as p:
    b = p.chromium.launch()
    for grade in (1, 4, 7):
        ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(player(grade, f"g{grade}"))
        pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("ballrun")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
        res = []
        for lv in (1, 5, 10, 15, 20, 30, 40):
            pg.evaluate(f"__game.K.load({lv})"); pg.wait_for_timeout(80)
            if pg.is_visible(".prob"): solve_math(pg)
            res.append((lv, pg.evaluate(RUN + "(20000)")))
            pg.evaluate("__game.S.done=true")  # stop before the win card
        bad = [(lv, r) for lv, r in res if not r["done"] or r["falls"]]
        check(not bad, f"grade {grade}: levels 1-40 can be finished without falling (lengths {[r['len'] for _, r in res]}) {bad[:2]}")
        ctx.close()

    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(player(3))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("ballrun")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
    pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / "ballrun-start.png"))
    check(not pg.evaluate("__game.S.running") and "Tap to roll" in pg.text_content("#brMsg"), "waits for a tap to start")
    pg.click("#brCv"); pg.wait_for_timeout(600)
    check(pg.evaluate("__game.S.z") > 1, "tapping starts the ball rolling")
    pg.screenshot(path=str(OUT / "ballrun-play.png"))
    # hold ◀ until the ball rolls off the edge
    pg.dispatch_event("#brL", "pointerdown"); pg.wait_for_timeout(1500); pg.dispatch_event("#brL", "pointerup")
    pg.wait_for_timeout(900)
    check(pg.evaluate("__game.S.falls") == 1 and "Falls 1" in pg.text_content("#kSub"), "steering off the track is a fall")
    check(pg.evaluate("__game.S.y") == 0 and abs(pg.evaluate("__game.S.x")) < .1 and not pg.evaluate("__game.S.running"), "after a fall the ball waits back on the track")
    # level 12 has walls, gaps and moving parts: drive it to the finish for real (with the animation running)
    pg.evaluate("__game.K.load(12)"); pg.wait_for_timeout(200)
    if pg.is_visible(".prob"): solve_math(pg)
    pg.evaluate(f"void(__game.S.auto=eval({json.dumps(AUTO)}))"); pg.click("#brCv")
    for _ in range(60):
        if pg.is_visible("#kSheetWin"): break
        if not pg.evaluate("__game.S.running") and not pg.evaluate("__game.S.done"): pg.click("#brCv")
        pg.wait_for_timeout(1000)
        if _ == 3: pg.screenshot(path=str(OUT / "ballrun-l12.png"))
    check(pg.is_visible("#kSheetWin"), f"reaching the finish wins the level ({pg.text_content('#kWinText')})")
    ctx.close()

    # iPad: drag to steer
    tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(player(5, "t5"))
    tp = watch_errors(tctx.new_page(), errors); tp.goto(URL("ballrun")); tp.wait_for_function("window.__game && __game.S", timeout=10000)
    bx = tp.locator("#brCv").bounding_box(); x0 = bx["x"] + bx["width"]/2; y0 = bx["y"] + bx["height"]*.6
    cdp = tctx.new_cdp_session(tp)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y0}]}); tp.wait_for_timeout(100)
    for k in range(1, 8): cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x0 + k*12, "y": y0}]}); tp.wait_for_timeout(40)
    tp.wait_for_timeout(300)
    xr = tp.evaluate("__game.S.x")
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    check(tp.evaluate("__game.S.running") and xr > .3, f"touch: a finger drag starts the ball and steers it right (x={xr:.2f})")
    tp.screenshot(path=str(OUT / "ballrun-ipad.png"))
    tctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
