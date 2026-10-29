"""Shared helpers for the Tile Solve browser tests."""
import json, re, pathlib, http.server, threading, functools

ROOT = pathlib.Path(__file__).resolve().parent.parent

def _serve():
    """Serve the repo over http on a free local port, like GitHub Pages does (file:// pages lose storage on reload in headless Chrome)."""
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}"
BASE = _serve()
URL = lambda g: f"{BASE}/games/{g}/index.html"
HOME_URL = f"{BASE}/index.html"
PLAYERS = json.dumps({"list": [{"id": "k1", "name": "Mia", "avatar": "🐯", "grade": 3, "color": "#e2412e"}], "current": "k1", "music": True})
GAMES = ["car", "picture-drop", "picture-slide", "memory", "pattern", "flood", "blocks", "numbers", "words", "sudoku", "pipes", "lights", "pixels", "boxes", "wordsearch",
         "abc", "missletter", "case", "sound", "trace", "count", "numorder", "moreless", "missnum", "tenframe", "shapesort", "shapehunt", "colours", "sizeorder",
         "maketen", "times", "fractions", "money", "clock", "numberline", "patterns", "rhyme", "sentence", "spelling", "crossword",
         "animals", "oddone", "planets", "foodchain", "places", "robot", "tunes", "carols", "ballrun"]
# Test player starts with every "How to play" card already seen (tools/test_howto.py tests the cards themselves).
SEEN = json.dumps({g: 1 for g in GAMES})
INIT = (f"if(!localStorage.getItem('tilesolve:players'))localStorage.setItem('tilesolve:players', {json.dumps(PLAYERS)});"
        f"if(!localStorage.getItem('tilesolve:p:k1:seen'))localStorage.setItem('tilesolve:p:k1:seen', {json.dumps(SEEN)})")
INIT_FRESH = f"if(!localStorage.getItem('tilesolve:players'))localStorage.setItem('tilesolve:players', {json.dumps(PLAYERS)})"

class Checker:
    def __init__(self): self.fails = []
    def __call__(self, ok, msg):
        print(("PASS " if ok else "FAIL ") + msg)
        if not ok: self.fails.append(msg)
    def finish(self):
        print("\n" + ("ALL PASSED" if not self.fails else f"{len(self.fails)} FAILED"))
        return 1 if self.fails else 0

def question(pg):
    t = pg.inner_text(".prob").replace("\n", " "); n = list(map(int, re.findall(r"\d+", t)))
    if t.index("?") < t.index("="): return n[1] - n[0]
    op = re.search(r"[+−×÷]", t).group()
    return {"+": n[0]+n[1], "−": n[0]-n[1], "×": n[0]*n[1], "÷": n[0]//n[1]}[op]

def solve_math(pg):
    for ch in str(question(pg)): pg.click(f".keys button[data-k='{ch}']")
    pg.click(".keys .ok"); pg.wait_for_timeout(1200)

def unlock_all(pg, game, reload=False):
    """Turn on "open every level". With reload=True, reloads and makes sure the game sees it."""
    js = f"(()=>{{const k='tilesolve:p:k1:{game}',s=JSON.parse(localStorage.getItem(k)||'{{\"grades\":{{}}}}');s.all=true;localStorage.setItem(k,JSON.stringify(s))}})()"
    pg.evaluate(js)
    if not reload: return
    for _ in range(3):
        pg.wait_for_timeout(300); pg.reload(); pg.wait_for_timeout(250)
        if pg.evaluate("!!(window.__game && __game.K.save.all)"): return
        pg.evaluate(js)

def go_level(pg, n):
    pg.click("#kLevels"); pg.click(f"#kLevelGrid button:nth-child({n})"); pg.wait_for_timeout(200)

def watch_errors(pg, errors):
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: m.type == "error" and "Failed to load resource" not in m.text and errors.append(m.text))
    return pg

def mouse_drag(pg, x0, y0, x1, y1, steps=10):
    pg.mouse.move(x0, y0); pg.mouse.down()
    for s in range(1, steps + 1): pg.mouse.move(x0 + (x1-x0)*s/steps, y0 + (y1-y0)*s/steps)
    pg.mouse.up(); pg.wait_for_timeout(250)

def touch_drag(pg, x0, y0, x1, y1, steps=10):
    """A real finger drag (touch events), as on an iPad."""
    cdp = pg.context.new_cdp_session(pg)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y0}]})
    for s in range(1, steps + 1):
        cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x0 + (x1-x0)*s/steps, "y": y0 + (y1-y0)*s/steps}]})
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}); pg.wait_for_timeout(300)

def tap_center(pg, selector):
    bx = pg.locator(selector).bounding_box(); pg.touchscreen.tap(bx["x"] + bx["width"]/2, bx["y"] + bx["height"]/2); pg.wait_for_timeout(150)
