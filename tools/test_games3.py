"""Browser tests for Sudoku Light and Pipe Connect.  python3 tools/test_games3.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(INIT)

    # ================= Sudoku Light =================
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("sudoku")); pg.wait_for_timeout(300)
    ramp = pg.evaluate("[1,9,17,31,40].map(n=>{const s=__game.spec(n);return (s.animals?'A':'')+s.N+'/'+s.clues})")
    print("sudoku grade 3:", ramp)
    check(ramp[0].startswith("A4") and ramp[1].startswith("4/") and ramp[2].startswith("6/") and ramp[4].startswith("6/"), "Sudoku ramp: 4x4 animals → numbers → 6x6")
    uniq = pg.evaluate("(()=>{const bad=[];for(const n of [1,5,9,14,17,24,31,40]){__game.K.load(n);const S=__game.S;if(__game.count(S.given,S.sp,2)!==1)bad.push(n)}__game.K.load(1);return bad})()")
    check(uniq == [], "every puzzle checked has exactly one answer")
    pg.wait_for_timeout(200); pg.screenshot(path=str(OUT / "sudoku-1.png"))
    S = pg.evaluate("({sol:__game.S.sol,given:__game.S.given})")
    empties = [i for i, v in enumerate(S["given"]) if v < 0]
    # a clash: put a value already in that row
    i0 = empties[0]; N = 4; row = [S["given"][(i0//N)*N+k] for k in range(N)]; clash = next(v for v in row if v >= 0)
    pg.click(f".sc[data-i='{i0}']"); pg.click(f"#sp button[data-v='{clash}']")
    check("Mistakes 1" in pg.text_content("#kSub") and pg.locator(".sc.bad").count() >= 1, "a clash turns red and counts a mistake")
    pg.screenshot(path=str(OUT / "sudoku-clash.png"))
    pg.click(f".sc[data-i='{i0}']"); pg.click(f"#sp button[data-v='{S['sol'][i0]}']")
    # pen mode: pick a symbol, then tap squares
    v = S["sol"][empties[1]]; pg.click(f"#sp button[data-v='{v}']")
    for i in empties[1:]:
        if S["sol"][i] == v: pg.click(f".sc[data-i='{i}']")
    pg.click(f"#sp button[data-v='{v}']")  # put the pen down
    check(all(pg.evaluate(f"__game.S.cur[{i}]") == v for i in empties[1:] if S["sol"][i] == v), "pick a symbol first, then tap squares")
    pg.click("#kHint"); solve_math(pg)
    check(pg.locator(".sc.flash").count() == 1, "maths hint fills a square")
    for i in empties:
        if pg.evaluate(f"__game.S.cur[{i}]") < 0:
            pg.click(f".sc[data-i='{i}']"); pg.click(f"#sp button[data-v='{S['sol'][i]}']")
    pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and pg.locator("#kWinStars .off").inner_text() == "", "solving with 1 mistake wins 3 stars")
    unlock_all(pg, "sudoku", reload=True); go_level(pg, 20); pg.wait_for_timeout(200)
    pg.screenshot(path=str(OUT / "sudoku-6.png"))
    pg.close()
    # older player gets 9x9, made quickly
    c5 = b.new_context(viewport={"width": 1024, "height": 1366})
    c5.add_init_script("localStorage.setItem('tilesolve:players',JSON.stringify({list:[{id:'k5',name:'Ben',avatar:'🦁',grade:5,color:'#3b6fd9'}],current:'k5',music:true}));"
                       "localStorage.setItem('tilesolve:p:k5:sudoku',JSON.stringify({grades:{5:{unlocked:40,stars:{},last:30}},all:true}))")
    p5 = watch_errors(c5.new_page(), errors); p5.goto(URL("sudoku")); p5.wait_for_timeout(300)
    t = p5.evaluate("(()=>{const t=performance.now();__game.K.load(40);return [performance.now()-t,__game.S.sp.N,__game.S.given.filter(v=>v>=0).length,__game.count(__game.S.given,__game.S.sp,2)]})()")
    check(t[1] == 9 and t[3] == 1 and t[0] < 3000, f"grade 5 level 40: unique 9x9 with {t[2]} clues, made in {t[0]:.0f} ms")
    p5.screenshot(path=str(OUT / "sudoku-9.png")); c5.close()

    # ================= Pipe Connect =================
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("pipes")); pg.wait_for_timeout(300)
    ramp = pg.evaluate("[1,6,15,25,35].map(n=>__game.spec(n).size)")
    check(ramp == [3, 4, 5, 6, 7], f"Pipe Connect ramp: {ramp}")
    def taps_needed(pg):
        return pg.evaluate("__game.S.sol.map((m,i)=>{let k=0;while(__game.cur(i)!==m&&k<4){__game.S.turns[i]++;k++}__game.S.turns[i]-=k;return k})")
    need = taps_needed(pg)
    check(sum(need) == pg.evaluate("__game.S.par"), f"par is the fewest taps ({sum(need)})")
    pg.screenshot(path=str(OUT / "pipes-1.png"))
    pg.click("#kHint"); solve_math(pg)
    check(pg.locator(".pc.flash").count() == 1, "maths hint turns a pipe the right way")
    for i, k in enumerate(taps_needed(pg)):
        for _ in range(k): pg.click(f".pc[data-i='{i}']")
    pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and pg.locator("#kWinStars .off").inner_text() == "", "connecting every pipe wins 3 stars")
    pg.click("#kWinNext"); pg.wait_for_timeout(200)
    check(pg.locator(".pc.wet").count() < pg.locator(".pc").count(), "a fresh level starts with some pipes dry")
    unlock_all(pg, "pipes", reload=True); go_level(pg, 25)
    for i, k in enumerate(taps_needed(pg)):
        for _ in range(k): pg.click(f".pc[data-i='{i}']")
    pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / "pipes-won.png"))
    check(pg.locator(".pc.wet").count() == 36, "6x6 board: all pipes full of water when solved")
    pg.close()

    # ================= iPad touch =================
    tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(INIT)
    tp = watch_errors(tctx.new_page(), errors); tp.goto(URL("pipes")); tp.wait_for_timeout(300)
    t0 = tp.evaluate("__game.S.turns[0]"); tap_center(tp, ".pc[data-i='0']")
    check(tp.evaluate("__game.S.turns[0]") == t0 + 1, "touch: tapping a pipe turns it")
    tp.goto(URL("sudoku")); tp.wait_for_timeout(300)
    i = tp.evaluate("__game.S.given.findIndex(v=>v<0)"); v = tp.evaluate(f"__game.S.sol[{i}]")
    tap_center(tp, f".sc[data-i='{i}']"); tap_center(tp, f"#sp button[data-v='{v}']")
    check(tp.evaluate(f"__game.S.cur[{i}]") == v, "touch: tap a square then an animal fills it")
    tctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
