"""Colour by Number: built-in pictures, painting, fill, saving progress, and making a picture from a photo.  python3 tools/test_paint.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []
PHOTO = str(ROOT / "icon-512.png")  # any picture will do as a "photo"
def player(grade, pid):
    return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Sam',avatar:'🦊',grade:{grade},color:'#3b6fd9'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(json.dumps({g: 1 for g in GAMES}))})")
def go(pg, n):
    pg.evaluate(f"__game.K.load({n})"); pg.wait_for_timeout(250)
    if pg.is_visible(".prob"): solve_math(pg); pg.wait_for_timeout(250)
PAINT_ALL = "(()=>{const S=__game.S;S.pic.cells.forEach((c,i)=>{if(!S.filled[i]){S.sel=c;__game.paintAt(i,true)}})})()"

with sync_playwright() as p:
    b = p.chromium.launch()
    for grade, vp in ((0, {"width": 1024, "height": 768}), (3, {"width": 768, "height": 1024}), (6, {"width": 390, "height": 844})):
        ctx = b.new_context(viewport=vp); ctx.add_init_script(player(grade, f"p{grade}"))
        pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("paint")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
        pg.evaluate("__game.K.save.all=true")
        sizes = []
        for n in (1, 15, 30):
            go(pg, n); s = pg.evaluate("[__game.S.pic.w,__game.S.pic.pal.length,__game.S.tool]"); sizes.append(s)
        check(sizes[0][0] <= sizes[2][0] and sizes[0][1] < sizes[2][1], f"grade {grade}: pictures get bigger and more colourful ({sizes})")
        check((sizes[0][2] == "fill") == (grade <= 0), f"grade {grade}: the youngest start with the fill-a-patch bucket ({sizes[0][2]})")
        box = pg.evaluate("(()=>{const r=document.getElementById('pbCv').getBoundingClientRect();return[r.left,r.right,r.top,r.bottom]})()")
        check(box[0] >= 0 and box[1] <= vp["width"] and pg.evaluate("document.getElementById('pbCv').getBoundingClientRect().width") >= 200, f"grade {grade}: the picture fits the screen ({box})")
        if grade == 3: pg.screenshot(path=str(OUT / "paint-ipad.png"))
        if grade == 6: pg.screenshot(path=str(OUT / "paint-phone.png"))
        ctx.close()

    ctx = b.new_context(viewport={"width": 1024, "height": 768}); ctx.add_init_script(player(3, "q3"))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("paint")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
    go(pg, 1)
    # a square with another number doesn't get painted
    r = pg.evaluate("(()=>{const S=__game.S,i=S.pic.cells.findIndex(c=>c!==S.sel);__game.paintAt(i,true);return S.filled[i]})()")
    check(r == 0, "tapping a square with a different number doesn't paint it")
    # fill a patch paints the whole connected patch
    r = pg.evaluate("(()=>{const S=__game.S;S.tool='fill';const i=S.pic.cells.findIndex(c=>c===S.sel);__game.paintAt(i,true);return S.filled.filter(Boolean).length})()")
    check(r > 5, f"fill a patch paints a whole patch at once ({r} squares)")
    # progress is kept
    pg.evaluate("document.getElementById('pbCv').dispatchEvent(new PointerEvent('pointerup'))"); pg.reload(); pg.wait_for_function("window.__game && __game.S", timeout=10000)
    if pg.is_visible(".prob"): solve_math(pg)
    check(pg.evaluate("__game.S.filled.filter(Boolean).length") == r, "a half-finished picture is still half-finished after leaving")
    pg.evaluate(PAINT_ALL); pg.wait_for_timeout(2700)
    check(pg.is_visible("#kSheetWin") and pg.locator("#kWinStars").inner_text().startswith("★★★"), "colouring every square finishes the picture with 3 stars")
    # photo → picture
    pg.click("#kReplay"); pg.wait_for_timeout(300); pg.click("#pbMine"); pg.wait_for_timeout(200)
    with pg.expect_file_chooser() as fc: pg.click("#mNew")
    fc.value.set_files(PHOTO); pg.wait_for_function("document.getElementById('mPrev')", timeout=5000); pg.wait_for_timeout(300)
    pg.click("[data-k='6']"); pg.wait_for_timeout(150); pg.screenshot(path=str(OUT / "paint-photo.png"))
    pg.fill("#mName", "Our icon"); pg.click("#mMake"); pg.wait_for_timeout(300)
    info = pg.evaluate("[__game.S.pic.name,__game.S.pic.pal.length,__game.S.n,__game.MINE.all().length]")
    check(info[0] == "Our icon" and 2 <= info[1] <= 6 and info[2] is None and info[3] == 1, f"a photo becomes a named picture with the chosen number of colours ({info})")
    stored = pg.evaluate("localStorage.getItem('tilesolve:mypics')")
    check(len(stored) < 4000 and "data:image" not in stored, f"only the small numbered grid is kept, not the photo ({len(stored)} characters)")
    pg.evaluate(PAINT_ALL); pg.wait_for_timeout(2000)
    check(pg.is_visible("#pbOv") and "finished" in pg.text_content("#pbOv"), "finishing a photo picture shows it as finished in My pictures")
    pg.screenshot(path=str(OUT / "paint-mine.png"))
    ctx.close()
    check(not errors, f"no page errors {errors[:3]}")
sys.exit(check.finish())
