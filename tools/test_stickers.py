"""Sticker book in Train Yard (shared with Train Trip).  python3 tools/test_stickers.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
check = Checker(); errors = []
pid = "y1"
init = (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐯',grade:1,color:'#3b6fd9',fav:'trains'}}],current:'{pid}',music:true}}));"
        f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(SEEN)});"
        # an old-style save: stickers from the first, small book
        f"if(!sessionStorage.done){{sessionStorage.done=1;localStorage.setItem('tilesolve:p:{pid}:trip',JSON.stringify({{cars:[],stk:{{'🚂':3,'🦬':1,'🐿️':2,'🎉':1,'🦖':1}}}}))}}")
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1024, "height": 768}); ctx.add_init_script(init)
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("trains")); pg.wait_for_function("window.__yard", timeout=10000)
    check(pg.evaluate("TS_STICKERS.total(__yard.TD.stk)") == 5, "old stickers carry over into the new book")
    r = pg.evaluate("()=>{const S={n:1,total:5,miss:0};__yard.reward(S,__yard.K);return Object.keys(__yard.TD.stk).length}")
    check(r == 6, f"a first-time level win gives a new sticker ({r})")
    first = pg.evaluate("TS_STICKERS.order()[0].id")
    check(first == "trains", f"a train fan's book starts on the Trains page ({first})")
    t0 = pg.evaluate("__yard.K.save.tickets||0")
    pg.evaluate("TS_STICKERS.order()[0].items.slice(0,19).forEach(x=>__yard.TD.stk[x[0]]=__yard.TD.stk[x[0]]||1);"
                "const p=TS_STICKERS.order()[0];p.items.forEach(x=>{if(Object.keys(__yard.TD.stk).filter(k=>p.items.some(y=>y[0]===k)).length>19)return});")
    # make the trains page exactly one short
    pg.evaluate("const p=TS_STICKERS.order()[0],miss=p.items.filter(x=>!__yard.TD.stk[x[0]]);miss.slice(1).forEach(x=>__yard.TD.stk[x[0]]=1)")
    pg.evaluate("__yard.reward({n:2,total:5,miss:0},__yard.K)")
    t1 = pg.evaluate("__yard.K.save.tickets")
    check(t1 - t0 == 15, f"filling a page adds 10 bonus tickets on top of the level's tickets ({t1-t0})")
    pg.wait_for_timeout(800)
    check(pg.locator(".stb-new").count() == 1, "a full page gets a celebration")
    pg.wait_for_timeout(3000)
    pg.evaluate("__yard.myTrain()"); pg.wait_for_timeout(200)
    pg.click("#tyBook"); pg.wait_for_timeout(300)
    check(pg.is_visible(".stb-ov") and pg.locator(".stb-tab.done").count() >= 1, "My train opens the sticker book, with the full page starred")
    check(pg.locator(".stb-tab.on").get_attribute("data-i") == "1", "the book opens on the page being filled")
    pg.click(".stb-tab[data-i='0']"); pg.wait_for_timeout(200)
    check(pg.locator(".stb-sheet i.shiny").count() == 1, "a sticker found 3 times is shiny")
    if OUT: pg.screenshot(path=str(OUT / "stickers_trains.png"))
    pg.click(".stb-tab[data-i='3']"); pg.wait_for_timeout(200)
    if OUT: pg.screenshot(path=str(OUT / "stickers_page.png"))
    pg.click(".stb-x"); pg.wait_for_timeout(200)
    check(not pg.is_visible(".stb-ov") and pg.is_visible("#tyBook"), "Done goes back to My train")
    ctx.close()
    ph = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); ph.add_init_script(init)
    pg = watch_errors(ph.new_page(), errors); pg.goto(URL("trains")); pg.wait_for_function("window.__yard", timeout=10000)
    pg.evaluate("__yard.myTrain()"); pg.wait_for_timeout(200); pg.click("#tyBook"); pg.wait_for_timeout(300)
    box = pg.locator(".stb").bounding_box()
    check(box["width"] <= 390 and box["height"] <= 844, f"the book fits a phone ({box['width']:.0f}x{box['height']:.0f})")
    if OUT: pg.screenshot(path=str(OUT / "stickers_phone.png"))
    ph.close(); b.close()
check(not errors, f"no page errors {errors[:3]}")
check.finish()
