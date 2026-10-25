"""Browser tests for Block Fit, Number Tiles and Word Builder.  python3 tools/test_games2.py [screenshot_dir]"""
import sys, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []

def piece_points(pg, pid):
    """Pointer start (on the piece's first square) and the board point that puts the piece at its solution."""
    info = pg.evaluate(f"""(()=>{{const S=__game.S,p=S.pieces.find(q=>q.id==={pid}),sh=__game.shape(p),el=p.el.getBoundingClientRect(),
        b=S.bw.getBoundingClientRect(),s=p.at?S.cs:S.tc,[r,c]=sh[0];
        return{{x0:el.left+(c+.5)*s,y0:el.top+(r+.5)*s,x1:b.left+(p.sol[1]+c+.5)*S.cs,y1:b.top+(p.sol[0]+r+.5)*S.cs,rot:p.rot}}}})()""")
    return info

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(INIT)

    # ================= Block Fit =================
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("blocks")); pg.wait_for_timeout(200)
    ramp = pg.evaluate("[1,6,11,19,29].map(n=>{const s=__game.spec(n);return s.w+'x'+s.h+(s.rotate?'R':'')+(s.shaped?'S':'')})")
    print("blocks grade 3:", ramp)
    check(ramp == ["3x3", "4x4", "5x4R", "5x5RS", "6x6RS"], "Block Fit ramp: bigger outlines, turning from 11, odd shapes from 19")
    ok = pg.evaluate("(()=>{for(let n=1;n<=40;n++){__game.K.load(n);const S=__game.S;let cells=0;S.pieces.forEach(p=>cells+=p.cells.length);"
                     "if(cells!==S.inside.size||S.pieces.some(p=>p.cells.length<2))return n}__game.K.load(1);return 0})()")
    check(ok == 0, "every level's blocks exactly cover its outline")
    pg.wait_for_timeout(200)
    ids = pg.evaluate("__game.S.pieces.map(p=>p.id)")
    pt = piece_points(pg, ids[0]); mouse_drag(pg, pt["x0"], pt["y0"], pt["x1"], pt["y1"])
    check(pg.evaluate(f"!!__game.S.pieces.find(p=>p.id==={ids[0]}).at"), "dragging a block to its spot places it")
    pg.screenshot(path=str(OUT / "blocks-1.png"))
    pt2 = piece_points(pg, ids[1]); mouse_drag(pg, pt2["x0"], pt2["y0"], pt["x1"], pt["y1"])
    check(pg.evaluate("__game.S.oops") == 1 and pg.evaluate(f"!__game.S.pieces.find(p=>p.id==={ids[1]}).at"), "dropping on top of another block is an oops")
    bx = pg.evaluate(f"(()=>{{const r=__game.S.pieces.find(p=>p.id==={ids[0]}).el.querySelector('i').getBoundingClientRect();return[r.left+r.width/2,r.top+r.height/2]}})()")
    pg.mouse.click(bx[0], bx[1]); pg.wait_for_timeout(200)
    check(pg.evaluate(f"!__game.S.pieces.find(p=>p.id==={ids[0]}).at"), "tapping a placed block sends it back")
    pg.click("#kHint"); solve_math(pg)
    check(pg.evaluate("__game.S.pieces.filter(p=>p.at).length") == 1, "maths hint places a block")
    for pid in pg.evaluate("__game.S.pieces.filter(p=>!p.at).map(p=>p.id)"):
        pt = piece_points(pg, pid); mouse_drag(pg, pt["x0"], pt["y0"], pt["x1"], pt["y1"])
    pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin"), "filling the outline wins")
    unlock_all(pg, "blocks", reload=True); go_level(pg, 19)
    p0 = pg.evaluate("__game.S.pieces[0]"); r0 = p0["rot"]
    pt = piece_points(pg, p0["id"]); pg.mouse.click(pt["x0"], pt["y0"]); pg.wait_for_timeout(200)
    check(pg.evaluate("__game.S.pieces[0].rot") == (r0 + 1) % 4, "tapping a tray block turns it")
    pg.screenshot(path=str(OUT / "blocks-19.png"))
    pg.close()

    # ================= Number Tiles =================
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("numbers")); pg.wait_for_timeout(200)
    ramp = pg.evaluate("[1,5,21,33].map(n=>{const s=__game.spec(n);return [s.size,s.max,s.blanks]})")
    print("numbers grade 3 [size,max,empty]:", ramp)
    check([r[0] for r in ramp] == [2, 3, 3, 4] and ramp[2][1] == 20, "Number Tiles ramp: 2x2 → 4x4, bigger numbers")
    def fill_solution(pg):
        S = pg.evaluate("({sol:__game.S.sol,blanks:[...__game.S.blanks]})")
        for i in S["blanks"]:
            tid = pg.evaluate(f"__game.S.tiles.find(t=>t.at<0&&t.v===__game.S.sol[{i}]).id")
            pg.click(f".nt[data-id='{tid}']"); pg.click(f".nc[data-i='{i}']")
    fill_solution(pg); pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and pg.locator("#kWinStars .off").inner_text() == "", "filling the right tiles wins with 3 stars")
    unlock_all(pg, "numbers", reload=True); go_level(pg, 12)
    S = pg.evaluate("({sol:__game.S.sol,blanks:[...__game.S.blanks],tiles:__game.S.tiles})")
    bl = S["blanks"]; vals = [S["sol"][i] for i in bl]
    # put tiles in a rotated (wrong) order
    order = sorted(S["tiles"], key=lambda t: t["v"]); wrong = None
    for i, t in zip(bl, order[1:] + order[:1]): pg.click(f".nt[data-id='{t['id']}']"); pg.click(f".nc[data-i='{i}']")
    if pg.is_visible("#kSheetWin"): print("(rotated order happened to also work)")
    else:
        check(pg.locator(".sum.bad").count() > 0 and "don't match" in pg.text_content("#kTip"), "wrong tiles show red totals")
        pg.screenshot(path=str(OUT / "numbers-wrong.png"))
        pg.click("#kHint"); solve_math(pg)
        check(pg.locator(".nc.flash").count() == 1, "maths hint fixes one square")
        cells = pg.evaluate("[...__game.S.blanks].filter(i=>{const t=__game.S.tiles.find(x=>x.at===i);return !t||t.v!==__game.S.sol[i]})")
        for i in cells:
            pg.click(f".nc[data-i='{i}']")  # send back whatever is there
        for i in cells:
            if pg.evaluate(f"__game.S.tiles.find(x=>x.at==={i})") is None:
                tid = pg.evaluate(f"__game.S.tiles.find(t=>t.at<0&&t.v===__game.S.sol[{i}]).id")
                pg.click(f".nt[data-id='{tid}']"); pg.click(f".nc[data-i='{i}']")
        pg.wait_for_timeout(900)
        check(pg.is_visible("#kSheetWin"), "fixing the tiles wins")
    pg.close()

    # ================= Word Builder =================
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("words")); pg.wait_for_timeout(200)
    ramp = pg.evaluate("[1,11,16,26,30].map(n=>{const s=__game.spec(n);return [s.band,s.decoys]})")
    print("words grade 3 [length,extra letters]:", ramp)
    check(ramp == [[4, 0], [5, 0], [5, 1], [6, 1], [6, 2]], "Word Builder ramp: 4 → 6 letters, extra letters from 16")
    lens = pg.evaluate("Object.entries(__game.LIST).map(([k,l])=>l.every(x=>k==='8'?x.w.length>=8:x.w.length===+k))")
    check(all(lens), "every word list has the right word lengths")
    def spell(pg, word):
        used = set()
        for ch in word:
            t = pg.evaluate(f"__game.S.tiles.find(t=>t.at<0&&t.ch==='{ch}').i"); pg.click(f".letters .lt[data-t='{t}']")
    w = pg.evaluate("__game.S.word"); print("level 1 word:", w)
    pg.screenshot(path=str(OUT / "words-1.png"))
    spell(pg, w); pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and pg.locator("#kWinStars .off").inner_text() == "", "spelling it first try: 3 stars")
    pg.click("#kWinNext"); pg.wait_for_timeout(200)
    w = pg.evaluate("__game.S.word"); spell(pg, w[1:] + w[0]) if len(set(w)) > 1 else None
    pg.wait_for_timeout(900)
    check(pg.evaluate("__game.S.oops") == 1 and not pg.is_visible("#kSheetWin"), "a wrong spelling counts an oops and lets you try again")
    pg.click("#kHint"); solve_math(pg)
    check(pg.evaluate("__game.S.fixed.size") >= 1, "maths hint places a letter")
    rest = pg.evaluate("__game.S.slots.map((t,k)=>t<0?__game.S.word[k]:'').join('')")
    spell(pg, rest); pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin"), "finishing the word wins")
    unlock_all(pg, "words", reload=True); go_level(pg, 30)
    check(pg.locator(".letters .lt").count() == pg.evaluate("__game.S.word.length") + 2, "level 30 has two extra letters")
    pg.screenshot(path=str(OUT / "words-30.png"))
    pg.close()

    # ================= iPad touch =================
    tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(INIT)
    tp = watch_errors(tctx.new_page(), errors); tp.goto(URL("blocks")); tp.wait_for_timeout(300)
    pid = tp.evaluate("__game.S.pieces[0].id"); pt = piece_points(tp, pid)
    touch_drag(tp, pt["x0"], pt["y0"], pt["x1"], pt["y1"])
    check(tp.evaluate(f"!!__game.S.pieces.find(p=>p.id==={pid}).at"), "touch: dragging a block with a finger on iPad places it")
    tp.screenshot(path=str(OUT / "ipad-blocks.png"))
    tp.goto(URL("numbers")); tp.wait_for_timeout(200)
    i = tp.evaluate("[...__game.S.blanks][0]"); tid = tp.evaluate(f"__game.S.tiles.find(t=>t.v===__game.S.sol[{i}]).id")
    tap_center(tp, f".nt[data-id='{tid}']"); tap_center(tp, f".nc[data-i='{i}']")
    check(tp.evaluate(f"__game.S.tiles.find(t=>t.id==={tid}).at") == i, "touch: tap a tile then a square places it")
    tp.goto(URL("words")); tp.wait_for_timeout(200)
    ch = tp.evaluate("__game.S.word[0]"); t = tp.evaluate(f"__game.S.tiles.find(t=>t.ch==='{ch}').i")
    tap_center(tp, f".letters .lt[data-t='{t}']")
    check(tp.evaluate("__game.S.slots[0]") == t, "touch: tapping a letter places it")
    tctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
