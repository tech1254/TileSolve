"""Browser tests for Lights Out, Picture Logic and Box Push.  python3 tools/test_games4.py [screenshot_dir]"""
import sys, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []

def line_solvable(rows):
    """Can this nonogram be solved by simple row/column logic alone? (true means a unique, fair puzzle)"""
    N = len(rows); sol = [[1 if ch == "#" else 0 for ch in r] for r in rows]
    runs = lambda a: [len(x) for x in "".join("#" if v else "." for v in a).split(".") if x] or [0]
    rc = [runs(r) for r in sol]; cc = [runs([sol[r][c] for r in range(N)]) for c in range(N)]
    def fits(line, clue):
        out = []
        def gen(i, k, cur):
            if k == len(clue) or clue == [0]:
                full = cur + [0]*(N-len(cur))
                if all(line[j] in (-1, full[j]) for j in range(N)): out.append(full)
                return
            for s in range(i, N - clue[k] + 1):
                nxt = cur + [0]*(s-len(cur)) + [1]*clue[k]
                if len(nxt) < N: nxt = nxt + [0]
                if all(line[j] in (-1, nxt[j]) for j in range(min(len(nxt), N))): gen(len(nxt), k+1, nxt[:N] if len(nxt) > N else nxt)
        gen(0, 0, []); return out
    g = [[-1]*N for _ in range(N)]; changed = True
    while changed:
        changed = False
        for idx in range(2*N):
            line = g[idx] if idx < N else [g[r][idx-N] for r in range(N)]
            opts = fits(line, rc[idx] if idx < N else cc[idx-N])
            if not opts: return False
            for j in range(N):
                vals = {o[j] for o in opts}
                if len(vals) == 1 and line[j] == -1:
                    v = vals.pop()
                    if idx < N: g[idx][j] = v
                    else: g[j][idx-N] = v
                    changed = True
    return all(v != -1 for r in g for v in r)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(INIT)

    # ================= Lights Out =================
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("lights")); pg.wait_for_timeout(200)
    ramp = pg.evaluate("[1,7,19,33].map(n=>__game.spec(n).size)")
    check(ramp == [3, 4, 5, 5], f"Lights Out ramp: {ramp}")
    allok = pg.evaluate("(()=>{for(let n=1;n<=40;n++){__game.K.load(n);const S=__game.S;if(!S.par||S.par>__game.spec(n).presses)return n}__game.K.load(1);return 0})()")
    check(allok == 0, "every level solvable, par never more than the presses used to make it")
    pg.wait_for_timeout(200); pg.screenshot(path=str(OUT / "lights-1.png"))
    pg.click("#kHint"); solve_math(pg)
    check(pg.locator(".lb.hint").count() == 1, "maths hint rings a light")
    for i, v in enumerate(pg.evaluate("Array.from(__game.solve(__game.S.g,__game.S.N).x)")):
        if v: pg.click(f".lb[data-i='{i}']")
    pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and pg.locator("#kWinStars .off").inner_text() == "", "pressing the fewest-taps answer wins 3 stars")
    unlock_all(pg, "lights", reload=True); go_level(pg, 25); pg.screenshot(path=str(OUT / "lights-5.png"))
    pg.close()

    # ================= Picture Logic =================
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("pixels")); pg.wait_for_timeout(200)
    dims = pg.evaluate("__game.PICS.map(p=>[p.name,p.rows.length,p.rows.every(r=>r.length===p.rows.length&&/^[#.]+$/.test(r))])")
    check(all(d[2] for d in dims) and sorted({d[1] for d in dims}) == [5, 8, 10], f"all {len(dims)} pictures are square 5x5, 8x8 or 10x10")
    pics = pg.evaluate("__game.PICS.map(p=>[p.name,p.rows])")
    fair = [n for n, rows in pics if line_solvable(rows)]
    print(f"line-solvable pictures: {len(fair)}/{len(pics)}; not: {[n for n,_ in pics if n not in fair]}")
    check(len(fair) == len(pics), "every picture can be solved with row/column logic alone (unique answer)")
    S = pg.evaluate("({sol:__game.S.sol,N:__game.S.N})"); N = S["N"]
    # paint the first row's filled run by dragging across it
    row0 = [c for c in range(N) if S["sol"][c]]
    if row0:
        a = pg.locator(f".px[data-i='{row0[0]}']").bounding_box(); z = pg.locator(f".px[data-i='{row0[-1]}']").bounding_box()
        if all(S["sol"][c] for c in range(row0[0], row0[-1]+1)):
            mouse_drag(pg, a["x"]+a["width"]/2, a["y"]+a["height"]/2, z["x"]+z["width"]/2, z["y"]+z["height"]/2)
            check(all(pg.evaluate(f"__game.S.cur[{c}]") == 1 for c in row0), "dragging across squares fills them all")
    wrong = next(i for i, v in enumerate(S["sol"]) if not v)
    pg.click(f".px[data-i='{wrong}']")
    pg.click("#kHint"); solve_math(pg)
    check(pg.evaluate(f"__game.S.cur[{wrong}]") == 2, "maths hint fixes a wrongly filled square")
    pg.click("#mX"); empty2 = next(i for i, v in enumerate(S["sol"]) if not v and i != wrong); pg.click(f".px[data-i='{empty2}']")
    check(pg.evaluate(f"__game.S.cur[{empty2}]") == 2, "✕ mode marks a square as empty"); pg.click("#mFill")
    pg.screenshot(path=str(OUT / "pixels-mid.png"))
    for i, v in enumerate(S["sol"]):
        if v and pg.evaluate(f"__game.S.cur[{i}]") != 1: pg.click(f".px[data-i='{i}']")
    pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and "found the" in pg.text_content("#kWinTitle"), "matching every clue reveals the picture")
    pg.screenshot(path=str(OUT / "pixels-won.png"))
    unlock_all(pg, "pixels", reload=True); go_level(pg, 30); pg.wait_for_timeout(200); pg.screenshot(path=str(OUT / "pixels-10.png"))
    pg.close()

    # ================= Box Push =================
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("boxes")); pg.wait_for_timeout(300)
    plan = pg.evaluate("[1,6,7,16,17,24,25,33,40].map(n=>{const s=__game.spec(n);return s.crates+'/'+s.par})")
    print("box push grade 3 (crates/par):", plan)
    cr = [int(x.split("/")[0]) for x in plan]
    check(cr[0] == 1 and cr[2] == 2 and cr[6] == 3 and cr == sorted(cr), "Box Push ramp: 1 crate → 2 → 3")
    uniq = pg.evaluate("new Set(__game.plan().slice(1).map(l=>l.r)).size")
    check(uniq == 40, "all 40 levels are different")
    def cell_xy(i):
        return pg.evaluate(f"(()=>{{const r=__game.S.el.getBoundingClientRect(),W=__game.S.W,cs=r.width/W;return[r.left+({i}%W+.5)*cs,r.top+(({i}/W|0)+.5)*cs]}})()")
    def play_solution(pg, limit=80):
        for _ in range(limit):
            if pg.is_visible("#kSheetWin") or pg.evaluate("__game.K.busy"): return
            m = pg.evaluate("__game.solveFrom()")
            if not m: return
            if pg.evaluate("__game.S.me") != m["stand"]:
                x, y = cell_xy(m["stand"]); pg.mouse.click(x, y); pg.wait_for_function("!__game.S.walking", timeout=8000)
            pg.evaluate(f"__game.step({m['d']})"); pg.wait_for_timeout(40)
    pg.screenshot(path=str(OUT / "boxes-1.png"))
    me0 = pg.evaluate("__game.S.me"); W = pg.evaluate("__game.S.W")
    moved = pg.evaluate("[1,-1,__game.S.W,-__game.S.W].some(d=>__game.step(d))")
    pg.click("#undo")
    check(pg.evaluate("__game.S.me") == me0 and pg.evaluate("__game.S.moves") == 0, "Undo takes a move back")
    pg.click("#kHint"); solve_math(pg)
    check(pg.locator(".crate.hint").count() == 1 and pg.locator(".bb .arrow").count() == 1, "maths hint shows which crate to push and which way")
    par = pg.evaluate("__game.S.par"); play_solution(pg); pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and pg.evaluate("__game.S.pushes") == par, f"following the solver solves level 1 in par ({par} pushes)")
    unlock_all(pg, "boxes", reload=True); go_level(pg, 33); pg.wait_for_timeout(200)
    pg.screenshot(path=str(OUT / "boxes-33.png"))
    par = pg.evaluate("__game.S.par"); play_solution(pg, 200); pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and pg.evaluate("__game.S.pushes") == par, f"3-crate level 33 solved in par ({par} pushes)")
    pg.close()

    # ================= iPad touch =================
    tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(INIT)
    tp = watch_errors(tctx.new_page(), errors); tp.goto(URL("pixels")); tp.wait_for_timeout(300)
    a = tp.locator(".px[data-i='0']").bounding_box(); z = tp.locator(".px[data-i='4']").bounding_box()
    touch_drag(tp, a["x"]+5, a["y"]+a["height"]/2, z["x"]+z["width"]-5, z["y"]+z["height"]/2)
    check(tp.evaluate("[0,1,2,3,4].every(i=>__game.S.cur[i]===1)"), "touch: finger-dragging along a row fills it on iPad")
    tp.goto(URL("lights")); tp.wait_for_timeout(200)
    before = tp.evaluate("Array.from(__game.S.g).join('')"); tap_center(tp, ".lb[data-i='4']")
    check(tp.evaluate("Array.from(__game.S.g).join('')") != before, "touch: tapping a light flips it")
    tp.goto(URL("boxes")); tp.wait_for_timeout(300)
    m0 = tp.evaluate("__game.S.moves")
    for c in ["up", "down", "left", "right"]:
        tap_center(tp, f".dpad .{c}")
        if tp.evaluate("__game.S.moves") > m0: break
    check(tp.evaluate("__game.S.moves") > m0, "touch: arrow buttons move the player")
    r = tp.evaluate("(()=>{const S=__game.S,W=S.W;for(const d of[1,-1,W,-W]){const t=S.me+d;if(!S.wall[t]&&!S.boxes.includes(t))return d}return 0})()")
    if r:
        x, y = tp.evaluate("(()=>{const r=__game.S.el.getBoundingClientRect(),W=__game.S.W,cs=r.width/W,i=__game.S.me;return[r.left+(i%W+.5)*cs,r.top+((i/W|0)+.5)*cs]})()")
        dx, dy = (60 if r == 1 else -60 if r == -1 else 0), (60 if r == W else -60 if r == -W else 0)
        me = tp.evaluate("__game.S.me"); touch_drag(tp, x, y, x + dx, y + dy, 6)
        check(tp.evaluate("__game.S.me") == me + r, "touch: swiping moves the player")
    tp.screenshot(path=str(OUT / "ipad-boxes.png"))
    tctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
