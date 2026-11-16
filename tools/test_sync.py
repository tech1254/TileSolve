"""Cloud sync between two devices, and the update checker. Runs worker.js locally with SQLite (tools/devserver.mjs).
   python3 tools/test_sync.py [screenshot_dir]"""
import sys, json, pathlib, subprocess, time
from playwright.sync_api import sync_playwright
from tsutil import Checker, SEEN

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
check = Checker(); errors = []
ROOT = pathlib.Path(__file__).resolve().parent.parent
srv = subprocess.Popen(["node", str(ROOT / "tools" / "devserver.mjs"), "8799"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL); time.sleep(1.2)
B = "http://localhost:8799"
def device(kids, cur):
    js = f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:{json.dumps(kids)},current:'{cur}',music:true}}));"
    js += "".join(f"localStorage.setItem('tilesolve:p:{k['id']}:seen',{json.dumps(SEEN)});" for k in kids)
    return f"if(!localStorage.getItem('tilesolve:players')){{{js}}}"
def get(pg, k): return pg.evaluate(f"JSON.parse(localStorage.getItem({json.dumps(k)}))")
def put(pg, k, v): pg.evaluate(f"localStorage.setItem({json.dumps(k)},JSON.stringify({json.dumps(v)}))")
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        A = b.new_context(viewport={"width": 1024, "height": 768}); A.add_init_script(device([{"id": "a1", "name": "Ava", "avatar": "🦊", "grade": 2, "color": "#e2412e"}], "a1"))
        Bc = b.new_context(viewport={"width": 1024, "height": 768}); Bc.add_init_script(device([{"id": "b7", "name": "ava", "avatar": "🦊", "grade": 2, "color": "#e2412e"},
                                                                                                  {"id": "b8", "name": "Ben", "avatar": "🐸", "grade": 0, "color": "#43a047"}], "b8"))
        pa = A.new_page(); pb = Bc.new_page()
        for pg in (pa, pb): pg.on("pageerror", lambda e: errors.append(str(e)))
        pa.goto(B + "/index.html"); pb.goto(B + "/index.html"); pa.wait_for_timeout(500)
        # some progress on each device before they're linked
        put(pa, "tilesolve:p:a1:blocks", {"grades": {"1": {"stars": {"1": 3, "2": 2}, "last": 3}}})
        put(pa, "tilesolve:p:a1:trip", {"stk": {"🚂": 2}, "carts": ["wood"], "cars": ["passenger"]})
        put(pb, "tilesolve:p:b7:blocks", {"grades": {"1": {"stars": {"2": 3, "3": 1}, "last": 4}}})
        put(pb, "tilesolve:p:b7:trip", {"stk": {"🚂": 1, "🦬": 1}, "carts": ["red"], "cars": ["coal", "tank"]})
        # A: start
        pa.click("#btnSync"); pa.wait_for_timeout(200)
        if OUT: pa.screenshot(path=str(OUT / "sync_start.png"))
        pa.click("#syStart"); pa.wait_for_timeout(1200)
        code = pa.evaluate("TS.sync.code")
        check(len(code) == 10 and code.replace(" ", "") in pa.text_content("#syCode").replace(" ", ""), f"the first device makes a family code and shows it ({code})")
        if OUT: pa.screenshot(path=str(OUT / "sync_on.png"))
        # B: join
        pb.click("#btnSync"); pb.fill("#syIn", code[:5] + " " + code[5:]); pb.click("#syJoin"); pb.wait_for_timeout(1500)
        names = sorted(x["name"].lower() for x in pb.evaluate("TS.players.list()"))
        check(names == ["ava", "ben"], f"joining: the same kid on both devices becomes one, the other kid is added ({names})")
        bl = get(pb, "tilesolve:p:a1:blocks") or get(pb, "tilesolve:p:b7:blocks")
        check(bl and bl["grades"]["1"]["stars"] == {"1": 3, "2": 3, "3": 1} and bl["grades"]["1"]["last"] == 4, f"keep the best of both: every level keeps its best stars ({bl})")
        tr = get(pb, "tilesolve:p:a1:trip") or get(pb, "tilesolve:p:b7:trip")
        check(tr and tr["stk"] == {"🚂": 2, "🦬": 1} and sorted(tr["carts"]) == ["red", "wood"], f"sticker counts keep the most, carts found on either device are kept ({tr})")
        check(pb.evaluate("TS.players.current()&&TS.players.current().name") == "Ben", "this device keeps its own player")
        # A pulls B's extra kid and the merged progress
        pa.evaluate("TS.sync.push()"); pa.wait_for_timeout(1200)
        check(sorted(x["name"] for x in pa.evaluate("TS.players.list()")) == ["Ava", "Ben"] and pa.evaluate("TS.players.current().name") == "Ava",
              "the first device gets the new kid, and keeps its own player")
        bl = get(pa, "tilesolve:p:a1:blocks")
        check(bl and bl["grades"]["1"]["stars"] == {"1": 3, "2": 3, "3": 1}, f"...and the combined progress ({bl})")
        pa.click("#syX"); pa.click("#btnMe"); pa.wait_for_timeout(300)
        check(pa.locator("#playerGrid").filter(has_text="Ben").count() >= 1, "the home screen shows the synced kids")
        # later changes flow both ways
        put(pb, "tilesolve:p:a1:blocks", {"grades": {"1": {"stars": {"1": 3, "2": 3, "3": 3, "4": 2}, "last": 5}}}); pb.wait_for_timeout(3800)
        pa.evaluate("TS.sync.push()"); pa.wait_for_timeout(1000)
        check(get(pa, "tilesolve:p:a1:blocks")["grades"]["1"]["stars"].get("4") == 2, "a level won on one iPad shows up on the other")
        pa.evaluate("TS.players.remove(TS.players.list().find(p=>p.name==='Ben').id)"); pa.wait_for_timeout(3800)
        pb.evaluate("TS.sync.push()"); pb.wait_for_timeout(1000)
        check([x["name"] for x in pb.evaluate("TS.players.list()")] == ["ava"] or [x["name"] for x in pb.evaluate("TS.players.list()")] == ["Ava"], "removing a kid on one device removes them on the other")
        check(pb.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('tilesolve:p:b8:')).length") == 0, "...along with their saves")
        check(pb.evaluate("TS.sync.pending") == 0 and pb.evaluate("TS.sync.error") == "", "nothing left waiting, no errors")
        # a wrong code
        C = b.new_context(); pc = C.new_page(); pc.goto(B + "/index.html"); pc.wait_for_timeout(300)
        check(pc.is_visible("#formJoin"), "a brand-new device can join from the first-run screen (no duplicate player needed)")
        pc.click("#formJoin"); pc.fill("#syIn", "ABC"); pc.click("#syJoin"); pc.wait_for_timeout(300)
        check("10 letters" in pc.text_content("#sySt") and not pc.evaluate("TS.sync.code"), "a code that's too short is caught")
        C.close()
        # ---- updates ----
        U = b.new_context(viewport={"width": 1024, "height": 768}); U.add_init_script(device([{"id": "u1", "name": "Ula", "avatar": "🦊", "grade": 3, "color": "#e2412e"}], "u1") + "window.__loads=(+sessionStorage.loads||0)+1;sessionStorage.loads=window.__loads")
        state = {"new": False}
        def ver(route):
            real = json.loads((ROOT / "version.json").read_text())
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"v": "zz-new"} if state["new"] else real))
        U.route("**/version.json*", ver)
        pu = U.new_page(); pu.on("pageerror", lambda e: errors.append(str(e)))
        pu.goto(B + "/games/blocks/index.html"); pu.wait_for_timeout(3200)
        check(pu.locator(".ts-update").count() == 0, "no update note when the version is current")
        state["new"] = True; pu.wait_for_timeout(5200); pu.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); pu.wait_for_timeout(1500)
        check(pu.locator(".ts-update").count() == 1, "in a game, a new version shows a 'tap to update' note (no surprise reload mid-level)")
        if OUT: pu.screenshot(path=str(OUT / "update_note.png"))
        n0 = pu.evaluate("window.__loads"); pu.click(".ts-update"); pu.wait_for_timeout(1500)
        check(pu.evaluate("window.__loads") == n0 + 1, "tapping it loads the new version")
        pu.goto(B + "/index.html"); pu.wait_for_timeout(500); n0 = pu.evaluate("window.__loads"); pu.wait_for_timeout(4500)
        n1 = pu.evaluate("window.__loads"); pu.wait_for_timeout(5000)
        check(n1 == n0 + 1 and pu.evaluate("window.__loads") == n1, f"on the home screen a new version loads by itself, once (never a reload loop) ({n0}->{n1}->{pu.evaluate('window.__loads')})")
        b.close()
finally:
    srv.terminate()
check(not errors, f"no page errors {errors[:3]}")
check.finish()
