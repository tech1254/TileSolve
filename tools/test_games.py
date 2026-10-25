"""Browser tests for Memory Match, Copy the Pattern and Color Flood.  python3 tools/test_games.py [screenshot_dir]"""
import sys, json, re, pathlib
from playwright.sync_api import sync_playwright
import tsutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = tsutil.URL
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
fails = []
def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)
PLAYERS = json.dumps({"list": [{"id": "k1", "name": "Mia", "avatar": "🐯", "grade": 3, "color": "#e2412e"}], "current": "k1", "music": True})
INIT = f"if(!localStorage.getItem('tilesolve:players'))localStorage.setItem('tilesolve:players', {json.dumps(PLAYERS)})"

def question(pg):
    t = pg.inner_text(".prob").replace("\n", " "); n = list(map(int, re.findall(r"\d+", t)))
    if t.index("?") < t.index("="): return n[1] - n[0]
    op = re.search(r"[+−×÷]", t).group()
    return {"+": n[0]+n[1], "−": n[0]-n[1], "×": n[0]*n[1], "÷": n[0]//n[1]}[op]
def solve_math(pg):
    for ch in str(question(pg)): pg.click(f".keys button[data-k='{ch}']")
    pg.click(".keys .ok"); pg.wait_for_timeout(1200)
def unlock_all(pg, game):
    pg.evaluate(f"(()=>{{const k='tilesolve:p:k1:{game}',s=JSON.parse(localStorage.getItem(k)||'{{\"grades\":{{}}}}');s.all=true;localStorage.setItem(k,JSON.stringify(s))}})()")
def go_level(pg, n):
    pg.click("#kLevels"); pg.click(f"#kLevelGrid button:nth-child({n})"); pg.wait_for_timeout(150)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(INIT); ctx.add_init_script(tsutil.INIT)
    errors = []
    def page():
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and "Failed to load resource" not in m.text and errors.append(m.text))
        return pg

    # ================= Memory Match =================
    pg = page(); pg.goto(URL("memory"))
    ramp = pg.evaluate("[1,7,13,19,25,31].map(n=>{const s=__game.spec(n);return s.cols+'x'+s.rows})")
    print("memory grade 3 boards:", ramp)
    check(ramp == ["4x2", "4x3", "4x4", "5x4", "6x4", "6x5"], "Memory: boards grow 4x2 → 6x5 for grade 3")
    check(pg.locator(".cardbtn").count() == 8, "Memory level 1 has 8 cards")
    pg.wait_for_timeout(300)
    check(pg.locator(".cardbtn.peek").count() == 8, "early levels show every card first")
    pg.screenshot(path=str(OUT / "mem-peek.png"))
    pg.wait_for_timeout(2000)
    deck = pg.evaluate("__game.S.deck")
    a = 0; bb = next(i for i, f in enumerate(deck) if f != deck[0])
    pg.click(f".cardbtn[data-i='{a}']"); pg.click(f".cardbtn[data-i='{bb}']")
    check("Misses 1" in pg.text_content("#kSub"), "a wrong pair counts a miss")
    pg.wait_for_timeout(1000)
    check(pg.locator(".cardbtn.up").count() == 0, "wrong pair flips back over")
    pg.click("#kHint"); solve_math(pg)
    check(pg.locator(".cardbtn.peek").count() == 2, "maths hint shows a matching pair")
    pg.wait_for_timeout(1600)
    seen = set()
    for i, f in enumerate(deck):
        if f in seen: continue
        seen.add(f); j = next(k for k in range(len(deck)) if k != i and deck[k] == f)
        pg.click(f".cardbtn[data-i='{i}']"); pg.click(f".cardbtn[data-i='{j}']"); pg.wait_for_timeout(120)
    pg.wait_for_timeout(1000)
    check(pg.is_visible("#kSheetWin") and pg.locator("#kWinStars .off").inner_text() == "", "finding all pairs wins (1 miss = 3 stars)")
    pg.screenshot(path=str(OUT / "mem-win.png"))
    tsutil.unlock_all(pg, "memory", reload=True)
    go_level(pg, 31)
    check(pg.locator(".cardbtn").count() == 30, "level 31 is a 30-card board (look-alikes)")
    pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / "mem-big.png"))
    bx = pg.locator(".cardbtn").first.bounding_box()
    check(bx["width"] >= 44, f"30 cards still fit a phone with big enough cards ({bx['width']:.0f}px)")
    pg.close()

    # ================= Copy the Pattern =================
    pg = page(); pg.goto(URL("pattern"))
    ramp = pg.evaluate("[1,6,11,16,21,40].map(n=>{const s=__game.spec(n);return [s.size,s.count,s.colors]})")
    print("pattern grade 3 [size,tiles,colours]:", ramp)
    check(ramp[0][0] == 3 and ramp[1][0] == 4 and ramp[3][0] == 5 and ramp[2][2] == 2 and ramp[4][2] == 3 and ramp[5][1] > ramp[0][1],
          "Pattern: grid, tile count and colours ramp up")
    pg.wait_for_timeout(600)
    check(pg.locator(".pt.show").count() == pg.evaluate("__game.S.sp.count"), "pattern is shown first")
    pg.screenshot(path=str(OUT / "pat-watch.png"))
    pg.wait_for_function("__game.S.phase==='build'", timeout=15000)
    check(pg.locator(".pt.show").count() == 0 and pg.is_visible("#done"), "then hidden: your turn")
    for i, v in enumerate(pg.evaluate("__game.S.target")):
        if v >= 0: pg.click(f"#pgrid .pt:nth-child({i+1})")
    pg.screenshot(path=str(OUT / "pat-build.png"))
    pg.click("#done"); pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and pg.locator("#kWinStars .off").inner_text() == "", "copying it exactly gives 3 stars")
    pg.click("#kWinNext"); pg.wait_for_function("__game.S.phase==='build'", timeout=15000)
    tgt = pg.evaluate("__game.S.target"); empties = [i for i, v in enumerate(tgt) if v < 0][:3]
    for i in empties: pg.click(f"#pgrid .pt:nth-child({i+1})")
    pg.click("#done"); pg.wait_for_timeout(700)
    check(pg.is_visible("#kSheetWin") and "Nearly" in pg.text_content("#kWinTitle") and pg.text_content("#kReplay") == "Try again", "too many mistakes: try again")
    pg.screenshot(path=str(OUT / "pat-fail.png"))
    tsutil.unlock_all(pg, "pattern", reload=True)
    go_level(pg, 12); pg.wait_for_function("__game.S && __game.S.phase==='build'", timeout=15000)
    check(pg.locator("#pal button").count() == 2, "level 12 has a two-colour palette")
    pg.click("#kHint"); solve_math(pg)
    check(pg.evaluate("__game.S.phase") == "watch", "maths hint replays the pattern")
    pg.wait_for_function("__game.S.phase==='build'", timeout=8000)
    for i, v in enumerate(pg.evaluate("__game.S.target")):
        if v >= 0:
            pg.click(f"#pal button:nth-child({v+1})"); pg.click(f"#pgrid .pt:nth-child({i+1})")
    pg.click("#done"); pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and "done" in pg.text_content("#kWinTitle"), "two-colour pattern copied with the palette")
    pg.close()

    # ================= Color Flood =================
    pg = page(); pg.goto(URL("flood"))
    ramp = pg.evaluate("[1,5,7,15,25,35].map(n=>{const s=__game.spec(n);return s.size+'x'+s.size+'/'+s.colors})")
    print("flood grade 3 size/colours:", ramp)
    check(ramp == ["6x6/3", "6x6/4", "8x8/4", "10x10/5", "12x12/6", "14x14/6"], "Flood: boards and colours ramp up")
    S = pg.evaluate("({par:__game.S.par,limit:__game.S.limit})")
    check(S["limit"] == S["par"] + 4, f"level 1: par {S['par']}, limit {S['limit']}")
    pg.screenshot(path=str(OUT / "flood-start.png"))
    pg.click("#kHint"); solve_math(pg)
    check(pg.locator("#pal button.hint").count() == 1, "maths hint flashes the best colour")
    for c in pg.evaluate("__game.solve(__game.S.g,__game.S.N,__game.S.sp.colors)"):
        pg.click(f"#pal button[data-c='{c}']"); pg.wait_for_timeout(60)
    pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and pg.locator("#kWinStars .off").inner_text() == "", "playing the solver's moves wins with 3 stars")
    pg.screenshot(path=str(OUT / "flood-win.png"))
    pg.click("#kWinNext"); pg.wait_for_timeout(300)
    for _ in range(60):
        if pg.is_visible("#kSheetWin"): break
        cur = pg.evaluate("__game.S.g[0]"); pg.click(f"#pal button[data-c='{(cur+1)%2}']"); pg.wait_for_timeout(40)
    pg.wait_for_timeout(700)
    check(pg.is_visible("#kSheetWin") and "Out of moves" in pg.text_content("#kWinTitle"), "running out of moves: try again")
    t = pg.evaluate("(()=>{let worst=0,bad=0;for(let n=1;n<=40;n++){const s=__game.spec(n),r=__game.K.rng(n),N=s.size;"
                    "const g=Int8Array.from({length:N*N},()=>Math.floor(r()*s.colors));const t0=performance.now(),sol=__game.solve(g,N,s.colors);"
                    "worst=Math.max(worst,performance.now()-t0);if(!sol)bad++}return [worst,bad]})()")
    check(t[1] == 0 and t[0] < 1500, f"solver handles every level (slowest {t[0]:.0f} ms)")
    tsutil.unlock_all(pg, "flood", reload=True); go_level(pg, 35); pg.wait_for_timeout(300)
    pg.screenshot(path=str(OUT / "flood-big.png"))
    pg.close()

    # ================= iPad touch =================
    tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(INIT); tctx.add_init_script(tsutil.INIT)
    tp = tctx.new_page(); tp.on("pageerror", lambda e: errors.append(str(e)))
    tp.goto(URL("memory")); tp.wait_for_timeout(2400)
    deck = tp.evaluate("__game.S.deck"); j = next(k for k in range(1, len(deck)) if deck[k] == deck[0])
    for i in (0, j):
        bx = tp.locator(f".cardbtn[data-i='{i}']").bounding_box(); tp.touchscreen.tap(bx["x"]+bx["width"]/2, bx["y"]+bx["height"]/2)
    tp.wait_for_timeout(300)
    check(tp.evaluate("__game.S.found") == 1, "touch: tapping cards on iPad flips them")
    tp.goto(URL("flood")); tp.wait_for_timeout(200)
    g = tp.evaluate("__game.S.g"); N = tp.evaluate("__game.S.N"); k = next(i for i, v in enumerate(g) if v != g[0])
    bx = tp.locator(f".fc:nth-child({k+1})").bounding_box(); tp.touchscreen.tap(bx["x"]+bx["width"]/2, bx["y"]+bx["height"]/2); tp.wait_for_timeout(200)
    check(tp.evaluate("__game.S.moves") == 1, "touch: tapping a flood tile picks its colour")
    tp.goto(URL("pattern")); tp.wait_for_function("__game.S.phase==='build'", timeout=15000)
    i = next(i for i, v in enumerate(tp.evaluate("__game.S.target")) if v >= 0)
    bx = tp.locator(f"#pgrid .pt:nth-child({i+1})").bounding_box(); tp.touchscreen.tap(bx["x"]+bx["width"]/2, bx["y"]+bx["height"]/2); tp.wait_for_timeout(200)
    check(tp.evaluate(f"__game.S.mine[{i}]") == 0, "touch: tapping a pattern tile colours it")
    tp.screenshot(path=str(OUT / "ipad-pattern.png"))
    tctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
