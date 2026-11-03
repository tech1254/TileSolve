"""Browser tests for Mine Cart.  python3 tools/test_mine.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
check = Checker(); errors = []
def player(grade, pid):
    return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐯',grade:{grade},color:'#3b6fd9'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(SEEN)})")
def to_station(pg):
    for _ in range(80):
        if pg.evaluate("__mine.mode") == "task": return True
        pg.evaluate("__mine.skip()"); pg.wait_for_timeout(250)
    return False
with sync_playwright() as p:
    b = p.chromium.launch()
    for grade, vp in ((0, (1024, 768)), (2, (1024, 768)), (4, (390, 844))):
        ctx = b.new_context(viewport={"width": vp[0], "height": vp[1]}, has_touch=vp[0] < 500); ctx.add_init_script(player(grade, f"m{grade}"))
        pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("mine")); pg.wait_for_function("window.__mine", timeout=10000)
        check(pg.evaluate("__mine.mode") == "start" and pg.is_visible("#mGo"), f"grade {grade}: starts with a Go card")
        pg.click("#mGo", force=True); pg.wait_for_timeout(1500)
        check(pg.evaluate("__mine.mode") == "ride" and pg.evaluate("__mine.cs") > 60 and pg.is_visible("#jump"), f"grade {grade}: the cart rides and the Jump button shows")
        if OUT: pg.screenshot(path=str(OUT / f"mine_ride_g{grade}.png"))
        # the track has drops, and loops show up
        ys = pg.evaluate("__mine.pts().map(p=>p.y)"); check(max(ys) - min(ys) > 150, f"grade {grade}: the track goes up and down ({max(ys)-min(ys):.0f})")
        pg.evaluate("__mine.jump()"); pg.wait_for_timeout(150)
        check(pg.evaluate("__mine.h") > 10, f"grade {grade}: tapping jumps the cart")
        # grab gems by riding through them: put a gem right on the cart's path
        g0 = pg.evaluate("__mine.save.gems")
        pg.evaluate("(()=>{const q=__mine.gems().find(q=>!q.got&&q.s>__mine.cs+50&&Math.abs(q.s-__mine.cs)<2500);return q})()")
        pg.wait_for_timeout(200)
        kinds = ["coal", "sort", "grab", "more" if grade < 2 else "add"]
        loops = 0
        for k in kinds:
            pg.evaluate(f"window.__mineNext='{k}'")
            if k == "grab": pg.evaluate("__mine.rideGems().length||__mine.rideGems().push(['red','#e8344a'],['blue','#2f7cf0'],['red','#e8344a'])")
            ok = to_station(pg)
            if not ok or pg.evaluate("__mine.task&&__mine.task.kind") != k: print("DEBUG", k, pg.evaluate("[__mine.mode,__mine.task&&__mine.task.kind,__mine.cs,__mine.stations().map(q=>[q.s,q.done])]"))
            check(ok and pg.evaluate("__mine.task.kind") == k, f"grade {grade}: the cart stops at a station with a {k} job")
            loops += pg.evaluate("__mine.pts().some(p=>p.loop)")
            pg.wait_for_timeout(300)
            if OUT: pg.screenshot(path=str(OUT / f"mine_{k}_g{grade}.png"))
            pg.evaluate("__mine.wrong()"); pg.wait_for_timeout(200)
            check(pg.evaluate("__mine.task.miss") == 1 and pg.evaluate("__mine.mode") == "task", f"grade {grade}: a wrong answer in {k} is caught and the cart waits")
            pg.evaluate("__mine.right()"); pg.wait_for_timeout(2700)
            if pg.evaluate("__mine.mode") not in ("ride","treasure"): print("DEBUG2", k, pg.evaluate("[__mine.mode,__mine.task&&__mine.task.kind,__mine.task&&__mine.task.miss,document.querySelector('.mcard')&&document.querySelector('.mcard').innerText]"))
            if pg.evaluate("__mine.mode") == "treasure":
                check(pg.is_visible("#mChest"), f"grade {grade}: every third station is a treasure room")
                nc = pg.evaluate("__mine.save.carts.length"); pg.click("#mChest", force=True); pg.wait_for_timeout(400)
                check(pg.evaluate("__mine.save.carts.length") == nc + 1, f"grade {grade}: the chest gives a new cart")
                if OUT: pg.screenshot(path=str(OUT / f"mine_treasure_g{grade}.png"))
                pg.click("#mRide", force=True); pg.wait_for_timeout(300)
            check(pg.evaluate("__mine.mode") == "ride", f"grade {grade}: after the {k} job the ride goes on (zone {pg.evaluate('__mine.zone')})")
        check(pg.evaluate("__mine.save.stations") == 4 and pg.evaluate("TS.notes.count()") >= 4, f"grade {grade}: stations count and earn 🎵")
        check(pg.evaluate("__mine.save.legs") == 4 and "Level 1" in pg.text_content("#prog") and pg.locator("#prog i.d").count() == 4, f"grade {grade}: the progress bar shows 4 of 6 stations")
        # magnet: costs 5 gems and stays on until the next station
        pg.evaluate("__mine.save.gems=7"); pg.click("#mag", force=True); pg.wait_for_timeout(200)
        check(pg.evaluate("__mine.magnetOn") and 2 <= pg.evaluate("__mine.save.gems") <= 6 and "ON" in pg.text_content("#mag"), f"grade {grade}: the magnet costs 5 gems and turns on")
        pg.evaluate("__mine.save.legs=5"); pg.evaluate("window.__mineNext='coal'"); to_station(pg)
        pg.evaluate("__mine.right()"); pg.wait_for_timeout(2400)
        check(pg.is_visible("#mVault"), f"grade {grade}: the 6th station leads to the treasure vault")
        nc = pg.evaluate("__mine.save.carts.length"); pg.click("#mVault", force=True); pg.wait_for_timeout(500)
        check(pg.evaluate("__mine.save.level") == 2 and pg.evaluate("__mine.save.trophies") == 1 and pg.evaluate("__mine.save.carts.length") == nc + 1 and "champion" in pg.text_content(".mcard"),
              f"grade {grade}: the vault gives a trophy and a new cart, and Level 2 begins")
        if OUT: pg.screenshot(path=str(OUT / f"mine_vault_g{grade}.png"))
        pg.click("#mRide", force=True); pg.wait_for_timeout(400)
        check(pg.evaluate("__mine.mode") == "ride" and pg.evaluate("__mine.save.legs") == 0 and not pg.evaluate("__mine.magnetOn") and pg.evaluate("__mine.zone") == "coal" and "Level 2" in pg.text_content("#prog"),
              f"grade {grade}: Level 2 starts back in the Coal Cave, and the magnet is off again")
        if OUT: pg.screenshot(path=str(OUT / f"mine_level2_g{grade}.png"))
        pg.reload(); pg.wait_for_function("window.__mine", timeout=10000)
        check(pg.evaluate("__mine.save.stations") == 5 and pg.evaluate("__mine.save.level") == 2 and len(pg.evaluate("__mine.save.carts")) == 3, f"grade {grade}: progress, level and carts are saved")
        pg.click("#mGo", force=True); pg.wait_for_timeout(300); pg.click("#cartBtn", force=True); pg.wait_for_timeout(300)
        check(pg.locator(".carts button[data-c]").count() == 3, f"grade {grade}: My carts shows the carts found")
        if OUT: pg.screenshot(path=str(OUT / f"mine_carts_g{grade}.png"))
        pg.click(".carts button[data-c='red']", force=True); pg.click("#mBack", force=True); pg.wait_for_timeout(200)
        check(pg.evaluate("__mine.save.cart") == "red" and pg.evaluate("__mine.mode") == "ride", f"grade {grade}: picking a cart and riding on")
        ctx.close()
    # a loop-the-loop: ride the track fast in simulated time and check the cart gets round
    ctx = b.new_context(viewport={"width": 1024, "height": 768}); ctx.add_init_script(player(0, "loop"))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("mine")); pg.wait_for_function("window.__mine", timeout=10000)
    pg.click("#mGo", force=True); pg.wait_for_timeout(200)
    cue = pg.evaluate("""()=>{window.__mineHold=true;let c=0;for(let i=0;i<30*120;i++){__mine.stations().forEach(q=>q.done=true);__mine.step(1/120);if(document.getElementById('jump').classList.contains('cue'))c++}window.__mineHold=false;return c}""")
    check(cue > 0, f"the Jump button glows when a high gem is coming ({cue} frames)")
    pg.evaluate("__mine.magnet()")
    r = pg.evaluate("""()=>{const g0=__mine.save.gems;window.__mineHold=true;let inLoop=0,maxv=0,maxPts=0;for(let i=0;i<60*120;i++){__mine.stations().forEach(q=>q.done=true);__mine.step(1/120);
      const c=__mine.cs,p=__mine.pts().find(p=>p.s>=c);if(p&&p.loop)inLoop++;maxv=Math.max(maxv,__mine.v);maxPts=Math.max(maxPts,__mine.pts().length)}
      window.__mineHold=false;return{inLoop,maxv,got:__mine.save.gems-g0,missed:__mine.gems().filter(q=>!q.got&&q.s<__mine.cs-60).length,cs:Math.round(__mine.cs),maxPts}}""")
    check(r["cs"] > 10000 and r["maxv"] > 400 and r["maxPts"] < 5000, f"a minute of riding goes far and fast, and old track is cleared away {r}")
    check(r["inLoop"] > 0, f"the ride has loop-the-loops, and the cart gets all the way round ({r['inLoop']} steps in loops)")
    check(r["got"] >= 10 and r["missed"] == 0, f"with the magnet on, riding without ever jumping collects every gem (got {r['got']}, missed {r['missed']})")
    ctx.close(); b.close()
check(not errors, f"no page errors {errors[:3]}")
check.finish()
