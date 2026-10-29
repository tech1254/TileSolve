"""Browser tests for play reports: what the games send to /api/events, and the /report page.  python3 tools/test_report.py [screenshot_dir]"""
import sys, json, pathlib, time
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []
SENT = []

def player(grade, pid="rp"):
    return ("window.TS_REPORT_TEST=true;"
            f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Secret Name',avatar:'🐸',grade:{grade},color:'#43a047'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(json.dumps({g: 1 for g in GAMES}))})")

def capture(route):
    try: SENT.append((route.request.url, json.loads(route.request.post_data or "{}")))
    except Exception: SENT.append((route.request.url, {}))
    route.fulfill(status=200, content_type="application/json", body='{"ok":true}')

def events(kind=None):
    out = [e for _, b in SENT for e in b.get("events", [])]
    return [e for e in out if kind is None or e.get("t") == kind]

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(player(0)); ctx.route("**/api/events", capture)
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("count")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    # a hint (pre-K counting question), then win the level
    pg.click("#kHint"); pg.wait_for_timeout(300); solve_math(pg)
    for _ in range(8):
        if pg.is_visible("#kSheetWin"): break
        pg.evaluate("__learn.R && !__learn.R.done && __learn.solve()"); pg.wait_for_timeout(950)
    # start level 2 and leave it unfinished by loading level 3
    pg.evaluate("__learn.K.load(2)"); pg.wait_for_timeout(200); pg.evaluate("__learn.K.load(3)"); pg.wait_for_timeout(200)
    pg.evaluate("TS.report.flush()"); pg.wait_for_timeout(600)
    plays = events("play"); maths = events("math")
    win = next((e for e in plays if e["result"] == "win" and e["level"] == 1), None)
    check(win and win["game"] == "count" and win["stars"] >= 1 and win["hints"] == 1 and win["ms"] > 0, f"a won level is reported with stars, time and hints ({win})")
    check(any(e["result"] == "quit" and e["level"] == 2 for e in plays), "leaving a level unfinished is reported as a quit")
    m = maths[0] if maths else None
    check(m and m["kind"] == "hint" and m["q"].startswith("count ") and m["correct"] == 1 and m["mlevel"] == -1, f"maths answers are reported ({m})")
    body = SENT[-1][1] if SENT else {}
    check(body.get("app") == "main" and body.get("device") and all(e.get("avatar") == "🐸" and e.get("grade") == 0 for e in body.get("events", [])), "each batch says which app and device, with buddy and grade")
    check("Secret Name" not in json.dumps([s[1] for s in SENT]), "names are never sent")
    check(pg.evaluate("TS.report.pending()") == 0, "the device queue empties once sent")
    ctx.close()

    # offline: events wait on the device and go out later
    SENT.clear()
    ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(player(3, "off"))
    ctx.route("**/api/events", lambda r: r.abort())
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("car")); pg.wait_for_timeout(600)
    if pg.locator(".ts-howto").is_visible(): pg.click(".ts-howto .bigbtn")
    pg.evaluate("dispatchEvent(new Event('pagehide'))"); pg.wait_for_timeout(300)
    pg.evaluate("TS.report.flush()"); pg.wait_for_timeout(500)
    queued = pg.evaluate("TS.report.pending()")
    check(queued >= 1, f"without a connection, events wait on the device ({queued} queued)")
    ctx.unroute("**/api/events"); ctx.route("**/api/events", capture)
    pg.evaluate("TS.report.flush()"); pg.wait_for_timeout(800)
    check(pg.evaluate("TS.report.pending()") == 0 and any(e["game"] == "car" for e in events("play")), "they are sent once the connection is back (Unblock the Car reports too)")
    ctx.close()

    # Little Learners posts to its own site root
    SENT.clear()
    ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(player(0, "lt")); ctx.route("**/api/events", capture)
    pg = watch_errors(ctx.new_page(), errors); pg.goto(BASE + "/little/games/trains/index.html"); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    pg.evaluate("__learn.K.load(2)"); pg.wait_for_timeout(200); pg.evaluate("TS.report.flush()"); pg.wait_for_timeout(600)
    check(SENT and SENT[-1][0].endswith("/little/api/events") and SENT[-1][1].get("app") == "little", f"the little app reports as 'little' ({SENT[-1][0] if SENT else 'nothing sent'})")
    ctx.close()

    # the /report page draws what /api/report returns
    ctx = b.new_context(viewport={"width": 1100, "height": 900})
    now = int(time.time() * 1000)
    fake = {"ok": True, "days": 30, "players": [{"player": "p1", "avatar": "🐸", "grade": 0, "app": "little", "n": 12, "last": now}],
            "games": [{"game": "count", "n": 12, "wins": 6, "minutes": 9.5, "last": now}],
            "levels": [{"game": "count", "grade": 0, "band": 1, "n": 8, "wins": 3, "fails": 2, "quits": 3, "stars": 2.1, "ms": 52000, "oops": 2.4, "hinted": .6, "top": 5},
                       {"game": "trains", "grade": 0, "band": 1, "n": 6, "wins": 6, "fails": 0, "quits": 0, "stars": 3, "ms": 30000, "oops": 0, "hinted": 0, "top": 5}],
            "maths": [{"grade": 0, "mlevel": -1, "kind": "hint", "n": 10, "acc": .5, "tries": 1.8, "ms": 9000}],
            "misses": [{"q": "count 7", "grade": 0, "n": 4}]}
    ctx.route("**/api/report*", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(fake)))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(BASE + "/report/index.html"); pg.wait_for_timeout(500)
    flags = pg.text_content("#flags")
    check("Count It" in flags and "Too hard" in flags and "Train Yard" in flags and "Too easy" in flags, "the report flags too-hard and too-easy level ranges")
    check("count 7" in pg.text_content("#misses") and "🐸" in pg.text_content("#who"), "it lists missed maths questions and each kid by buddy")
    pg.screenshot(path=str(OUT / "report.png"), full_page=True)
    ctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
