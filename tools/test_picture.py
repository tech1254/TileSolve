"""Browser tests for Picture Puzzle.  python3 tools/test_picture.py [screenshot_dir]"""
import sys, json, re, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
import tsutil
PAGE = tsutil.URL("picture")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
fails = []
def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)

PLAYERS = json.dumps({"list": [{"id": "k1", "name": "Mia", "avatar": "🐯", "grade": 3, "color": "#e2412e"}], "current": "k1", "music": True})

def question(pg):
    t = pg.inner_text(".prob").replace("\n", " ")
    n = list(map(int, re.findall(r"\d+", t)))
    if t.index("?") < t.index("="): return n[1] - n[0]
    op = re.search(r"[+−×÷]", t).group()
    return {"+": n[0]+n[1], "−": n[0]-n[1], "×": n[0]*n[1], "÷": n[0]//n[1]}[op]

def solve_math(pg):
    for ch in str(question(pg)): pg.click(f".keys button[data-k='{ch}']")
    pg.click(".keys .ok"); pg.wait_for_timeout(1300)

def cell_center(pg, k, n):
    b = pg.locator("#board").bounding_box(); cs = b["width"] / n
    return b["x"] + (k % n + .5) * cs, b["y"] + (k // n + .5) * cs

def drag_piece(pg, k, to_cell, n):
    el = pg.locator(f".tp[data-k='{k}']"); el.scroll_into_view_if_needed()
    bb = el.bounding_box(); x0, y0 = bb["x"] + bb["width"]/2, bb["y"] + bb["height"]/2
    x1, y1 = cell_center(pg, to_cell, n)
    pg.mouse.move(x0, y0); pg.mouse.down()
    for s in range(1, 9): pg.mouse.move(x0 + (x1-x0)*s/8, y0 + (y1-y0)*s/8)
    pg.mouse.up(); pg.wait_for_timeout(320)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    ctx.add_init_script(f"if(!localStorage.getItem('tilesolve:players'))localStorage.setItem('tilesolve:players', {json.dumps(PLAYERS)})")
    ctx.add_init_script(tsutil.INIT)
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: m.type == "error" and "Failed to load resource" not in m.text and errors.append(m.text))
    pg.goto(PAGE)

    check(pg.is_visible("#sheetMode"), "first visit asks Drop-in or Slider")
    pg.screenshot(path=str(OUT / "pic-mode.png"))

    sizes = pg.evaluate("[1,9,17,25,40].map(n=>__picture.spec('drop',n).size)")
    rot = pg.evaluate("[12,13].map(n=>__picture.spec('drop',n).rotate)")
    ssz = pg.evaluate("[1,16,17,40].map(n=>__picture.spec('slide',n).size)")
    print("grade 3 drop sizes", sizes, "rotate@12/13", rot, "slide sizes", ssz)
    check(sizes == [3, 4, 5, 6, 6] and rot == [False, True] and ssz == [3, 3, 4, 4], "grade 3 level ramp (pieces shrink, turning from level 13, slider 3x3 then 4x4)")

    # ---- Drop-in ----
    pg.click(".modes button[data-mode='drop']"); pg.wait_for_function("__picture.S && !__picture.busy")
    n = pg.evaluate("__picture.L.size")
    check(n == 3 and pg.locator(".tp").count() == 9, "Drop-in level 1: 3x3, nine pieces in the tray")
    pg.click("#btnLook")
    check(pg.is_visible("#peek") and pg.get_attribute("#peekImg", "src"), "👀 button shows the finished picture")
    pg.wait_for_timeout(3000)
    check(pg.is_visible("#peek"), "it stays up until you tap")
    pg.click("#peek"); check(pg.is_hidden("#peek"), "tapping closes it")
    check(pg.locator(".ghostimg").count() == 0 and "off" in pg.text_content("#btnGhost"), "faint picture starts off for grade 3")
    pg.click("#btnGhost")
    check(pg.locator(".ghostimg").count() == 1 and "on" in pg.text_content("#btnGhost"), "Faint picture button shows it on the board")
    pg.reload(); pg.wait_for_function("__picture.S && !__picture.busy")
    check(pg.locator(".ghostimg").count() == 1, "faint picture setting is remembered")
    pg.click("#btnGhost"); check(pg.locator(".ghostimg").count() == 0, "and can be turned off again")
    ks = pg.evaluate("__picture.S.pieces.map(p=>p.k)")
    k = ks[0]; wrong = (k + 1) % 9
    drag_piece(pg, k, wrong, n)
    check(pg.text_content("#stat2") == "Oops 1" and pg.locator(f".tp[data-k='{k}']").count() == 1, "wrong drop counts an oops and the piece goes back")
    drag_piece(pg, k, k, n)
    check(pg.text_content("#stat1") == "1/9" and pg.locator(".pc").count() == 1, "right drop locks the piece into the picture")
    pg.screenshot(path=str(OUT / "pic-drop.png"))
    pg.click("#btnHint"); solve_math(pg)
    check(pg.text_content("#stat1") == "2/9", "maths hint places a piece")
    for k in pg.evaluate("__picture.S.pieces.filter(p=>!p.done).map(p=>p.k)"):
        drag_piece(pg, k, k, n)
    pg.wait_for_timeout(900)
    check(pg.is_visible("#sheetWin") and "You made" in pg.text_content("#winTitle"), "finishing the picture shows the win card")
    check(pg.locator("#winStars .off").inner_text() == "", "one oops still earns 3 stars")
    pg.screenshot(path=str(OUT / "pic-win.png"))
    pg.click("#btnWinNext"); pg.wait_for_function("__picture.S && !__picture.busy && __picture.L.n===2")
    check(pg.text_content("#lvlNum") == "2", "Next level goes to level 2")

    # ---- Turning pieces (level 13) ----
    pg.evaluate("(()=>{const k='tilesolve:p:k1:picture',s=JSON.parse(localStorage.getItem(k));s.all=true;localStorage.setItem(k,JSON.stringify(s))})()")
    pg.reload(); pg.wait_for_function("__picture.S && !__picture.busy")
    pg.click("#btnLevels"); pg.click("#levelGrid button:nth-child(13)"); pg.wait_for_function("__picture.S && !__picture.busy && __picture.L.n===13")
    n = pg.evaluate("__picture.L.size"); p0 = pg.evaluate("__picture.S.pieces[0]")
    check(p0["rot"] in (90, 180, 270), f"level 13 pieces start turned ({p0['rot']}°), board {n}x{n}")
    drag_piece(pg, p0["k"], p0["k"], n)
    check("Tap the piece to turn it" in pg.text_content("#tip"), "a turned piece in the right spot is rejected with a turn-it tip")
    for _ in range((360 - p0["rot"]) // 90):
        pg.locator(f".tp[data-k='{p0['k']}']").click(); pg.wait_for_timeout(260)
    check(pg.evaluate(f"__picture.S.pieces.find(p=>p.k==={p0['k']}).rot") == 0, "tapping turns the piece")
    drag_piece(pg, p0["k"], p0["k"], n)
    check(pg.locator(".pc").count() == 1, "turned-right piece locks in")
    pg.screenshot(path=str(OUT / "pic-rotate.png"))

    # ---- Slider ----
    pg.click("#btnMode"); pg.click(".modes button[data-mode='slide']")
    pg.wait_for_function("__picture.S && !__picture.busy && __picture.S.cells")
    check(pg.is_hidden("#btnGhost") and pg.is_visible("#btnLook"), "slider shows 👀 but not the faint-picture switch")
    par = pg.evaluate("__picture.S.par")
    check(pg.evaluate("__picture.L.size") == 3 and pg.locator(".tile").count() == 8 and "Par" in pg.text_content("#stat2"), f"Slider level 1: 3x3 with par {par}")
    pg.screenshot(path=str(OUT / "pic-slide.png"))
    pg.click("#btnHint"); solve_math(pg)
    check(pg.locator(".tile.hint").count() == 1, "maths hint flashes the tile to slide")
    for _ in range(40):
        t = pg.evaluate("__picture.busy ? -1 : __picture.nextMove()")
        if t < 0: break
        v = pg.evaluate(f"__picture.S.cells[{t}]")
        pg.locator(f".tile[data-v='{v}']").click(); pg.wait_for_timeout(160)
    pg.wait_for_timeout(900)
    check(pg.is_visible("#sheetWin") and pg.evaluate("__picture.S.moves") == par, f"following hints solves it in exactly par ({par}) moves")
    tap_row = None
    # Sliding a whole row with one tap
    pg.click("#btnReplay"); pg.wait_for_function("__picture.S && !__picture.busy && __picture.S.cells")
    z = pg.evaluate("__picture.S.cells.indexOf(0)"); far = (z // 3) * 3 + (0 if z % 3 == 2 else 2)
    if z % 3 != 1:
        v = pg.evaluate(f"__picture.S.cells[{far}]"); pg.locator(f".tile[data-v='{v}']").click(); pg.wait_for_timeout(200)
        check(pg.evaluate("__picture.S.moves") == 2, "tapping the far tile in the gap's row slides two tiles")

    # Dragging a tile toward the gap: a short nudge snaps back, a longer drag moves it
    def adj():
        c = pg.evaluate("__picture.S.cells"); z = c.index(0)
        t = z - 1 if z % 3 else z + 1
        return c[t], (z % 3) - (t % 3)
    def drag_tile(frac):
        v, dirx = adj(); bb = pg.locator(f".tile[data-v='{v}']").bounding_box()
        x0, y0 = bb["x"] + bb["width"]/2, bb["y"] + bb["height"]/2
        pg.mouse.move(x0, y0); pg.mouse.down()
        for s in range(1, 7): pg.mouse.move(x0 + dirx*bb["width"]*frac*s/6, y0)
        pg.mouse.up(); pg.wait_for_timeout(250)
    m0 = pg.evaluate("__picture.S.moves"); drag_tile(.15)
    check(pg.evaluate("__picture.S.moves") == m0, "a small nudge snaps the tile back")
    drag_tile(.7)
    check(pg.evaluate("__picture.S.moves") == m0 + 1, "dragging a tile toward the gap slides it")

    pg.click("#btnLevels"); pg.click("#levelGrid button:nth-child(17)")
    pg.wait_for_function("__picture.S && !__picture.busy && __picture.S.cells && __picture.L.n===17")
    ms = pg.evaluate("(()=>{const t=performance.now(),m=__picture.nextMove(),S=__picture.S,z=S.cells.indexOf(0),n=S.n;"
                     "const ok=[z-n,z+n,(z%n)?z-1:-9,(z%n<n-1)?z+1:-9].includes(m);return [ok,performance.now()-t]})()")
    check(pg.evaluate("__picture.L.size") == 4 and ms[0] and ms[1] < 2500, f"4x4 slider hint finds a legal move ({ms[1]:.0f} ms)")
    pg.screenshot(path=str(OUT / "pic-slide4.png"))

    # Touch screen (iPad emulation): tapping a tile slides it
    tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(tsutil.INIT)
    tctx.add_init_script(f"localStorage.setItem('tilesolve:players', {json.dumps(PLAYERS)});"
                         "localStorage.setItem('tilesolve:p:k1:picture',JSON.stringify({mode:'slide',drop:{},slide:{},numbers:false,all:false}))")
    tp = tctx.new_page(); tp.on("pageerror", lambda e: errors.append(str(e))); tp.goto(PAGE)
    tp.wait_for_function("__picture.S && __picture.S.cells && !__picture.busy")
    c = tp.evaluate("__picture.S.cells"); z = c.index(0); t = z - 1 if z % 3 else z + 1
    bb = tp.locator(f".tile[data-v='{c[t]}']").bounding_box()
    tp.touchscreen.tap(bb["x"] + bb["width"]/2, bb["y"] + bb["height"]/2); tp.wait_for_timeout(300)
    check(tp.evaluate("__picture.S.moves") == 1 and tp.evaluate(f"__picture.S.cells[{z}]") == c[t], "touch tap slides a tile on a tablet")
    tctx.close()

    # Landscape iPad layout keeps tray beside the board
    ip = ctx.new_page(); ip.set_viewport_size({"width": 1180, "height": 820}); ip.goto(PAGE)
    ip.click("#btnMode"); ip.click(".modes button[data-mode='drop']"); ip.wait_for_function("__picture.S && !__picture.busy")
    bb, tb = ip.locator("#board").bounding_box(), ip.locator("#tray").bounding_box()
    check(tb["x"] > bb["x"] + bb["width"] - 1, "iPad landscape: tray sits beside the board")
    ip.screenshot(path=str(OUT / "pic-ipad.png"))

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()

print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
