"""Browser tests for "How to play" cards, the 👆 finger and the ? button in every game.  python3 tools/test_howto.py [screenshot_dir]"""
import sys, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []
KIT = ["memory", "pattern", "flood", "blocks", "numbers", "words", "sudoku", "pipes", "lights", "pixels", "boxes", "wordsearch",
       "abc", "count", "shapesort", "trace", "tenframe"]

def card(pg): return pg.locator(".ts-howto").is_visible()
def finger(pg):
    f = pg.locator(".ts-finger")
    if not f.count(): return None
    b = f.bounding_box(); vp = pg.viewport_size
    return b if 0 <= b["x"] <= vp["width"] and 0 <= b["y"] <= vp["height"] else None

with sync_playwright() as p:
    b = p.chromium.launch()
    for game in ["car"] + KIT:
        ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(INIT_FRESH)
        pg = watch_errors(ctx.new_page(), errors); pg.goto(URL(game)); pg.wait_for_timeout(500)
        steps = pg.locator(".ts-steps li").count()
        check(card(pg) and steps >= 3 and pg.text_content("#tsHowT").startswith("How to play"), f"{game}: 'How to play' card shows the first time ({steps} steps)")
        if game in ("car", "boxes"): pg.screenshot(path=str(OUT / f"howto-{game}.png"))
        pg.click(".ts-howto .bigbtn"); pg.wait_for_timeout(2400 if game == "memory" else 600)
        if game == "pattern":
            check(not card(pg), f"{game}: Let's play closes it")
        else:
            f = finger(pg)
            check(not card(pg) and f is not None, f"{game}: closing it shows the 👆 finger on level 1")
            if game in ("car", "blocks"): pg.screenshot(path=str(OUT / f"finger-{game}.png"))
            pg.mouse.click(5, 300); pg.wait_for_timeout(200)
            check(pg.locator(".ts-finger").count() == 0, f"{game}: touching anything hides the finger")
        pg.reload(); pg.wait_for_timeout(600)
        check(not card(pg), f"{game}: the card doesn't come back on its own")
        pg.click("#btnHelp" if game == "car" else "#kHelp"); pg.wait_for_timeout(300)
        check(card(pg), f"{game}: the ? button shows it again")
        pg.click(".ts-howto .bigbtn"); ctx.close()

    # Picture Puzzle: one card per mode, after choosing the mode
    ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(INIT_FRESH)
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("picture")); pg.wait_for_timeout(400)
    check(pg.is_visible("#sheetMode") and not card(pg), "picture: mode chooser comes first")
    pg.click(".modes button[data-mode='drop']"); pg.wait_for_timeout(700)
    check(card(pg) and "Drop-in" in pg.text_content("#tsHowT"), "picture: Drop-in card after choosing Drop-in")
    pg.click(".ts-howto .bigbtn"); pg.wait_for_timeout(600)
    check(finger(pg) is not None, "picture: finger points at a piece")
    pg.mouse.click(5, 300)
    pg.click("#btnMode"); pg.click(".modes button[data-mode='slide']"); pg.wait_for_timeout(900)
    check(card(pg) and "Slider" in pg.text_content("#tsHowT"), "picture: Slider has its own card")
    pg.click(".ts-howto .bigbtn"); pg.wait_for_timeout(600)
    check(finger(pg) is not None, "picture: finger points at the tile to slide")
    pg.mouse.click(5, 300); pg.click("#btnHelp"); pg.wait_for_timeout(300)
    check(card(pg) and "Slider" in pg.text_content("#tsHowT"), "picture: ? shows the card for the current mode")
    ctx.close()

    # Each player sees the cards once for themselves
    ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(INIT_FRESH)
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("lights")); pg.wait_for_timeout(400); pg.click(".ts-howto .bigbtn")
    pg.evaluate("(()=>{const d=JSON.parse(localStorage.getItem('tilesolve:players'));d.list.push({id:'k2',name:'Sam',avatar:'🦄',grade:1,color:'#3b6fd9'});d.current='k2';localStorage.setItem('tilesolve:players',JSON.stringify(d))})()")
    pg.reload(); pg.wait_for_timeout(400)
    check(card(pg), "a second player gets their own first-time card")
    ctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
