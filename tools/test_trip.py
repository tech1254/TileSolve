"""Train Trip: ride from station to station, answer at every Y, get a present at each station."""
import sys, json
from playwright.sync_api import sync_playwright
from tsutil import URL, Checker

check = Checker()
def player(grade, pid):
    pl = json.dumps({"list": [{"id": pid, "name": "Max", "avatar": "🦖", "grade": grade, "color": "#3b6fd9"}], "current": pid, "music": True})
    return (f"if(!localStorage.getItem('tilesolve:players'))localStorage.setItem('tilesolve:players',{json.dumps(pl)});"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',JSON.stringify({{trip:1}}))")
def errs(pg, out):
    pg.on("pageerror", lambda e: out.append(str(e)))
    return pg

with sync_playwright() as p:
    b = p.chromium.launch()
    for grade, nsigns, dev in ((0, 2, {"width": 1024, "height": 768}), (2, 3, {"width": 390, "height": 760}), (4, 3, {"width": 768, "height": 1024})):
        E = []; ctx = b.new_context(viewport=dev); ctx.add_init_script(player(grade, f"t{grade}"))
        pg = errs(ctx.new_page(), E); pg.goto(URL("trip")); pg.wait_for_timeout(600)
        check(pg.is_visible("#go") and pg.evaluate("__trip.mode") == "start", f"grade {grade}: starts at a station with a Go button")
        pg.click("#go", force=True)
        pg.wait_for_function("__trip.mode==='ask'", timeout=40000)
        check(pg.locator(".sign:not(.gone)").count() == nsigns and pg.is_visible("#ask"), f"grade {grade}: the train stops at a Y with {nsigns} signs and a question")
        x0 = pg.evaluate("__trip.tx")
        pg.evaluate("__trip.wrong()"); pg.wait_for_timeout(300)
        check(pg.locator(".sign.no").count() == 1 and pg.evaluate("__trip.mode") == "ask", f"grade {grade}: a wrong sign greys out and the train waits")
        if nsigns == 2: check(pg.locator(".sign.glow").count() == 1, f"grade {grade}: with one sign left it glows")
        # tap the right sign like a child would
        k = pg.evaluate("__trip.fork.q.opts.findIndex(o=>o.key===__trip.fork.q.ans)")
        pg.locator("#signs .sign:not(.gone)").nth(k).click(force=True)
        pg.wait_for_timeout(2500)
        check(pg.evaluate("__trip.tx") > x0 + 20 and pg.evaluate("__trip.save.forks") == 1, f"grade {grade}: tapping the right sign sends the train down that track")
        # ride on to the station
        for _ in range(8):
            pg.wait_for_function("__trip.mode==='ask'||__trip.mode==='station'||__trip.mode==='run'", timeout=40000)
            m = pg.evaluate("__trip.mode")
            if m == "station": break
            if m == "ask": pg.evaluate("__trip.fork.miss||__trip.stickerNext();__trip.right()"); pg.wait_for_function("__trip.mode!=='go'", timeout=10000)
            pg.evaluate("__trip.skip()"); pg.wait_for_timeout(300)
            pg.wait_for_function("__trip.mode!=='run'", timeout=40000)
        pg.wait_for_timeout(2300)
        nst = pg.evaluate("Object.keys(__trip.save.stk).length")
        check(nst >= 1 and pg.text_content("#bookN") == str(nst), f"grade {grade}: right answers sometimes give a sticker, counted on the 📒 ({nst})")
        check(pg.evaluate("__trip.mode") == "station" and 3 <= pg.evaluate("__trip.save.forks") <= 5, f"grade {grade}: a station comes after 3-5 Ys ({pg.evaluate('__trip.save.forks')})")
        want = pg.evaluate("__trip.gives(__trip.station.name)[0]")
        pg.click("#gift", force=True); pg.wait_for_timeout(300); pg.click("#hook", force=True); pg.wait_for_timeout(300)
        check(pg.evaluate("__trip.save.cars[0].k") == want, f"grade {grade}: the station gives its own kind of car ({want})")
        check(pg.is_visible("#go") and pg.is_visible("#yard"), f"grade {grade}: after hooking it on, Go and My train are offered")
        check(pg.evaluate("__trip.save.cars.length") == 1 and "🚃 1" in pg.text_content("#score"), f"grade {grade}: the present is a new car on the train")
        check(pg.evaluate("TS.notes.count()") >= 1, f"grade {grade}: a station earns a 🎵")
        pg.reload(); pg.wait_for_timeout(600)
        check(pg.evaluate("__trip.save.cars.length") == 1 and pg.evaluate("__trip.save.stations") == 1, f"grade {grade}: the train and stations are saved")
        pg.click("#book", force=True); pg.wait_for_timeout(200)
        check(pg.is_visible("#bookov") and pg.locator("#sbook i:not(.no)").count() == pg.evaluate("Object.keys(__trip.save.stk).length") and pg.locator("#sbook i").count() == pg.evaluate("__trip.STK.length"),
              f"grade {grade}: the sticker book shows the stickers found and spaces for the rest")
        pg.click("#bookX", force=True); pg.wait_for_timeout(200)
        check(not pg.is_visible("#bookov"), f"grade {grade}: the sticker book closes")
        pg.click("#yard", force=True); pg.wait_for_timeout(300)
        check(pg.locator(".ycar").count() == 1, f"grade {grade}: My train shows every car")
        pg.click(".ycar button", force=True); pg.wait_for_timeout(300)
        check(pg.locator(".ycar").count() == 0 and pg.evaluate("__trip.save.cars.length") == 0 and "🚃 0" in pg.text_content("#score"), f"grade {grade}: tapping ✖ leaves the car at the station")
        pg.click("#done", force=True); pg.wait_for_timeout(200)
        check(pg.is_visible("#go") and not pg.is_visible("#yard"), f"grade {grade}: Done goes back to the Go card")
        pg.reload(); pg.wait_for_timeout(500)
        check(pg.evaluate("__trip.save.cars.length") == 0, f"grade {grade}: the removed car stays removed")
        check(not E, f"grade {grade}: no page errors {E[:2]}")
        ctx.close()
sys.exit(check.finish())
