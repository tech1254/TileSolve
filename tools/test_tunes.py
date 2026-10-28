"""Browser tests for Tile Tunes.  python3 tools/test_tunes.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []

def player(grade, pid="tt"):
    return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐸',grade:{grade},color:'#43a047'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(json.dumps({g: 1 for g in GAMES + ['tunes']}))})")

def play_through(pg, gap=40):
    """Taps every tile in the right lane."""
    while True:
        lane = pg.evaluate("(()=>{const S=__game.S,n=S.notes[S.next];return n?n.lane:-1})()")
        if lane < 0: break
        pg.evaluate(f"__game.hitLane({lane})"); pg.wait_for_timeout(gap)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(player(3))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("tunes")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
    info = pg.evaluate("""__game.LIST.map(s=>({t:s.title,n:s.notes.length,lo:Math.min(...s.notes.map(x=>x.m)),hi:Math.max(...s.notes.map(x=>x.m)),
        lanes:[...new Set(s.notes.map(x=>x.lane))].length,ok:s.notes.every(x=>x.lane>=0&&x.lane<4&&x.d>0)}))""")
    check(len(info) >= 20, f"{len(info)} songs")
    bad = [s["t"] for s in info if not (s["ok"] and s["n"] >= 10 and 48 <= s["lo"] and s["hi"] <= 96 and s["lanes"] >= 3)]
    check(not bad, f"every song has 10+ notes in piano range spread over 3+ lanes {bad}")
    check(pg.evaluate("__game.relaxed()") is False, "grade 3 starts with tiles that keep moving")
    pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / "tunes-start.png"))
    # wrong lane before starting does nothing; first tile starts the song
    first = pg.evaluate("__game.S.notes[0].lane")
    pg.evaluate(f"__game.hitLane({(first+1)%4})")
    check(pg.evaluate("__game.S.oops") == 0 and not pg.evaluate("__game.S.running"), "tapping a wrong lane before starting is ignored")
    pg.evaluate(f"__game.hitLane({first})")
    check(pg.evaluate("__game.S.running") and pg.evaluate("__game.S.next") == 1, "tapping the first tile starts the song")
    pg.wait_for_timeout(400); pg.screenshot(path=str(OUT / "tunes-play.png"))
    pos0 = pg.evaluate("__game.S.pos"); pg.wait_for_timeout(500)
    check(pg.evaluate("__game.S.pos") > pos0, "tiles slide down while playing")
    nxt = pg.evaluate("__game.S.notes[__game.S.next].lane")
    pg.evaluate(f"__game.hitLane({(nxt+2)%4})")
    check(pg.evaluate("__game.S.oops") == 1 and pg.evaluate("__game.S.hearts") == 2, "a wrong lane costs a heart")
    pg.wait_for_timeout(4000)
    check(pg.evaluate("__game.S.oops") >= 2 and pg.evaluate("__game.S.waiting"), "a tile that slides past is a miss, and the song waits for it")
    pg.click("#ttRelax")
    check(pg.evaluate("__game.relaxed()"), "🐢 Wait for me can be switched on")
    play_through(pg)
    pg.wait_for_timeout(1500)
    check(pg.is_visible("#kSheetWin") and "done" in pg.text_content("#kWinTitle"), "playing every tile wins the song")
    pg.evaluate("localStorage.setItem('tilesolve:p:tt:tunes-options',JSON.stringify({relaxed:false}))")
    check(not pg.is_visible("#kWinNext") and "more 🎵" in pg.text_content("#kWinText"), "with no 🎵 yet, song 2 stays locked after song 1")
    pg.click("#kReplay"); pg.wait_for_timeout(200); pg.click("#kLevels")
    check("🎵5" in pg.text_content("#kLevelGrid button:nth-child(2)") and pg.locator("#kLevelGrid button:nth-child(2)").is_disabled(), "the song list shows what each locked song needs")
    pg.click("#kCloseLevels")
    # earn notes: a maths question and a few finished levels in another game
    pg.evaluate("localStorage.setItem('tilesolve:p:tt:memory',JSON.stringify({grades:{3:{unlocked:5,stars:{1:3,2:2,3:1,4:3},last:4}},all:false}))")
    check(pg.evaluate("TS.notes.count()") == 4, "finished levels in other games count as 🎵")
    pg.click("#kHint"); pg.wait_for_timeout(400); solve_math(pg)
    check(pg.evaluate("TS.notes.count()") == 5, "a maths question answered right counts as a 🎵")
    pg.evaluate("__game.K.load(2)"); pg.wait_for_timeout(300)
    check(pg.evaluate("__game.K.level") == 2 and pg.evaluate("__game.K.canPlay(2)") and not pg.evaluate("__game.K.canPlay(3)"), "with 5 🎵, song 2 opens (song 3 still needs 10)")

    # out of hearts
    pg.evaluate("__game.K.load(2)"); pg.wait_for_timeout(300)
    if pg.evaluate("__game.relaxed()"): pg.click("#ttRelax")
    pg.evaluate("__game.hitLane(__game.S.notes[0].lane)")
    for _ in range(3): pg.evaluate("__game.hitLane((__game.S.notes[__game.S.next].lane+1)%4)")
    pg.wait_for_timeout(1600)
    check(pg.is_visible("#kSheetWin") and "hearts" in pg.text_content("#kSheetWin").lower(), "running out of hearts ends the song with a Try again " + str(pg.evaluate("({lv:__game.K.level,h:__game.S.hearts,o:__game.S.oops,n:__game.S.next,r:__game.relaxed(),t:document.getElementById('kWinTitle').textContent,m:TS.math.isOpen})")))
    ctx.close()

    # Kindergarten: tiles wait, five hearts; every song can be finished
    ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(player(0, "tk"))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("tunes")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
    check(pg.evaluate("__game.relaxed()") and pg.evaluate("__game.S.hearts") == 5, "Kindergarten: Wait for me is on and there are 5 hearts")
    pg.evaluate("__game.hitLane(__game.S.notes[0].lane)"); pg.wait_for_timeout(5000)
    check(pg.evaluate("__game.S.oops") == 0 and pg.evaluate("__game.S.waiting"), "Wait for me: tiles stop at the line instead of being missed")
    pg.evaluate("(()=>{const k='tilesolve:p:tk:tunes',s=JSON.parse(localStorage.getItem(k)||'{\"grades\":{}}');s.all=true;localStorage.setItem(k,JSON.stringify(s))})()")
    wins = []
    for lv in range(1, pg.evaluate("__game.LIST.length") + 1):
        pg.evaluate(f"__game.K.load({lv})"); pg.wait_for_timeout(150)
        if pg.is_visible(".prob"):
            if pg.locator(".ts-count").count():
                for ch in pg.locator(".ts-count").get_attribute("aria-label").split()[0]: pg.click(f".keys button[data-k='{ch}']")
                pg.click(".keys .ok"); pg.wait_for_timeout(1300)
            else: solve_math(pg)
        pg.evaluate("(()=>{const S=__game.S;while(S.next<S.notes.length&&!S.done){S.pos=Math.max(S.pos,S.notes[S.next].b-1);__game.hitLane(S.notes[S.next].lane)}})()"); pg.wait_for_timeout(1600)
        wins.append(pg.is_visible("#kSheetWin"))
    check(all(wins), f"every song can be played to the end ({sum(wins)}/{len(wins)})")
    pg.click("#kReplay"); pg.wait_for_timeout(300)
    check("Eine kleine" in pg.text_content(".tt-song") and "Mozart" in pg.text_content(".tt-song"), "each song shows its name and composer")
    ctx.close()

    # iPad touch on the canvas
    tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(player(4, "t4"))
    tp = watch_errors(tctx.new_page(), errors); tp.goto(URL("tunes")); tp.wait_for_function("window.__game && __game.S", timeout=10000)
    bx = tp.locator("#ttCv").bounding_box()
    for k in range(3):
        lane = tp.evaluate("__game.S.notes[__game.S.next].lane")
        tp.touchscreen.tap(bx["x"] + bx["width"] * (lane + .5) / 4, bx["y"] + bx["height"] * .7); tp.wait_for_timeout(120)
    check(tp.evaluate("__game.S.next") == 3 and tp.evaluate("__game.S.oops") == 0, "touch: tapping the right lanes plays the notes")
    tp.screenshot(path=str(OUT / "tunes-ipad.png"))
    tctx.close()

    # ---------- Christmas Tunes: its own songbook, progress and cheaper 🎵 ----------
    cctx = b.new_context(viewport={"width": 390, "height": 844}); cctx.add_init_script(player(2, "cc"))
    cp = watch_errors(cctx.new_page(), errors); cp.goto(URL("carols")); cp.wait_for_function("window.__game && __game.S", timeout=10000)
    titles = cp.evaluate("__game.LIST.map(s=>s.title)")
    check(cp.evaluate("__game.BOOK") == "carols" and "Silent Night" in titles and "Deck the Halls" in titles and len(titles) >= 10, f"Christmas Tunes has {len(titles)} carols")
    bad = cp.evaluate("__game.LIST.filter(s=>!(s.notes.length>=10&&s.notes.every(x=>x.m>=48&&x.m<=96&&x.d>0))).map(s=>s.title)")
    check(not bad, f"every carol is well formed {bad}")
    check(cp.evaluate("__game.PER") == 3 and cp.evaluate("__game.cost(2)") == 3, "carols cost 3 🎵 each")
    cp.evaluate("localStorage.setItem('tilesolve:p:cc:carols',JSON.stringify({grades:{2:{unlocked:9,stars:{1:3,2:3,3:3,4:3,5:3,6:3,7:3,8:3},last:1}},all:false}))")
    check(cp.evaluate("TS.notes.count()") == 0, "playing carols doesn't earn 🎵 (only other games do)")
    cp.evaluate("(()=>{const k='tilesolve:p:cc:carols',s=JSON.parse(localStorage.getItem(k));s.all=true;localStorage.setItem(k,JSON.stringify(s))})()")
    wins = []
    for lv in range(1, len(titles) + 1):
        cp.evaluate(f"__game.K.load({lv})"); cp.wait_for_timeout(150)
        if cp.is_visible(".prob"): solve_math(cp)
        cp.evaluate("(()=>{const S=__game.S;while(S.next<S.notes.length&&!S.done){S.pos=Math.max(S.pos,S.notes[S.next].b-1);__game.hitLane(S.notes[S.next].lane)}})()"); cp.wait_for_timeout(1600)
        wins.append(cp.is_visible("#kSheetWin"))
    check(all(wins), f"every carol can be played to the end ({sum(wins)}/{len(wins)})")
    cp.goto(HOME_URL); cp.wait_for_timeout(300)
    check(cp.locator(".game[data-game='carols']").count() == 1, "Christmas Tunes is on the home screen")
    cctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
