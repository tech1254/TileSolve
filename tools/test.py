"""Browser tests for Tile Solve.  python3 tools/test.py [screenshot_dir]
Covers: players (add, switch, separate progress, delete), migration of the old single-player save,
Unblock the Car (difficulty curve, drag without bounce, maths-for-a-hint, music), and no JS errors."""
import sys, re, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
import tsutil
HOME = tsutil.HOME_URL
CAR = tsutil.URL("car")
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
fails = []
def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)

def movable(cars, pos):
    occ = set()
    for i, c in enumerate(cars):
        for j in range(c["len"]):
            occ.add((c["f"]*6 + pos[i] + j) if c["h"] else ((pos[i]+j)*6 + c["f"]))
    for i, c in enumerate(cars):
        cell = (lambda q, c=c: c["f"]*6 + q) if c["h"] else (lambda q, c=c: q*6 + c["f"])
        hi = pos[i]
        while hi + c["len"] < 6 and cell(hi + c["len"]) not in occ: hi += 1
        if hi > pos[i]: return i, hi - pos[i], 1
        lo = pos[i]
        while lo > 0 and cell(lo - 1) not in occ: lo -= 1
        if lo < pos[i]: return i, pos[i] - lo, -1

def add_player(pg, name, avatar_ix, grade):
    pg.fill("#fName", name)
    pg.click(f"#fAvatars button:nth-child({avatar_ix})")
    pg.click(f"#fGrades button:nth-child({grade + 1})")  # K is first
    pg.click("#formSave")

def question(pg):
    t = pg.inner_text(".prob").replace("\n", " ")
    n = list(map(int, re.findall(r"\d+", t)))
    if t.index("?") < t.index("="): return t, n[1] - n[0]          # a + ? = c
    op = re.search(r"[+−×÷]", t).group()
    return t, {"+": n[0]+n[1], "−": n[0]-n[1], "×": n[0]*n[1], "÷": n[0]//max(1, n[1])}[op]

def answer(pg, v):
    for ch in str(v): pg.click(f".keys button[data-k='{ch}']")
    pg.click(".keys .ok")

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: m.type == "error" and "Failed to load resource" not in m.text and errors.append(m.text))

    # ---- Home: first launch asks for a player ----
    pg.goto(HOME)
    check(pg.is_visible("#sheetPlayer"), "first launch opens New player")
    pg.screenshot(path=str(OUT / "shot-newplayer.png"))
    pg.click("#formSave")
    check(pg.is_visible("#sheetPlayer"), "can't save a player without a name")
    add_player(pg, "Mia", 3, 3)
    check(pg.is_visible("#viewGames") and "Hi Mia!" in pg.text_content("#hello"), "saving a player goes to the game grid")
    live = len([d for d in (ROOT / "games").iterdir() if (d / "index.html").exists()])
    check(pg.locator(".game:not(.soon)").count() == live and pg.locator(".game").count() == 28, f"{live} games playable, the rest say coming soon")
    pg.screenshot(path=str(OUT / "shot-games.png"))

    # ---- Car game ----
    pg.click(".game[data-game='car']")
    pg.wait_for_url("**/games/car/index.html"); pg.wait_for_timeout(200)
    if pg.locator(".ts-howto").is_visible(): pg.click(".ts-howto .bigbtn"); pg.wait_for_timeout(300)
    check(pg.text_content("#lvlNum") == "1", "Car opens at level 1 for the new player")
    curve = pg.evaluate("[1,5,10,20,30,50,100,200,500,1000].map(n=>[n,window.__tilesolve.getLevel(3,n).par])")
    print("grade 3 par by level:", curve)
    d = dict(curve)
    check(d[1] <= 5 and 17 <= d[30] <= 22 and d[100] > d[30] and all(curve[i][1] <= curve[i+1][1] for i in range(len(curve)-1)),
          "grade 3 curve: easy start, ~20 by level 30, rising after")
    g1, g7 = pg.evaluate("[window.__tilesolve.getLevel(1,30).par, window.__tilesolve.getLevel(7,30).par]")
    check(g1 < d[30] < g7, f"older grades harder at level 30 (g1={g1}, g3={d[30]}, g7={g7})")
    check(pg.text_content("#par") == str(d[1]), "board uses the player's grade")
    pg.screenshot(path=str(OUT / "shot-board.png"))

    L = pg.evaluate("window.__tilesolve.getLevel(3,1)")
    i, steps, sign = movable(L["cars"], L["pos"])
    horiz = L["cars"][i]["h"]
    box = pg.locator(f".car[data-i='{i}']").bounding_box()
    cell = pg.evaluate("document.getElementById('grid').clientWidth/6")
    x0, y0 = box["x"] + box["width"]/2, box["y"] + box["height"]/2
    dist = sign * (steps - 0.35) * cell
    pg.mouse.move(x0, y0); pg.mouse.down()
    for k in range(1, 11):
        pg.mouse.move(x0 + (dist*k/10 if horiz else 0), y0 + (0 if horiz else dist*k/10))
    pg.evaluate("""i=>{const el=document.querySelector(`.car[data-i='${i}']`);window.__trace=[];const t0=performance.now();
      (function f(){const r=el.getBoundingClientRect();window.__trace.push([r.left,r.top]);if(performance.now()-t0<450)requestAnimationFrame(f)})()}""", i)
    pg.mouse.up(); pg.wait_for_timeout(500)
    vals = [t[0 if horiz else 1] for t in pg.evaluate("window.__trace")]
    worst = max(abs(v - vals[-1]) - abs(vals[0] - vals[-1]) for v in vals)
    back = max(0, *(sign*(vals[k-1]-vals[k]) for k in range(1, len(vals))))
    check(worst <= 1.5 and back <= 1.5, f"released car settles without bouncing (overshoot {worst:.1f}px, backstep {back:.1f}px)")
    check(pg.text_content("#moves") == "1", "drag counted as one move")

    pg.click("#btnHint")
    check(pg.locator(".prob").is_visible(), "hint opens a maths question")
    q1, a1 = question(pg); print("grade 3 player's question:", q1, "->", a1)
    check(re.search(r"[×÷]", q1) is None and all(int(v) <= 100 for v in re.findall(r"\d+", q1)), "grade 3 player gets grade 2 maths (+/− within 100)")
    pg.screenshot(path=str(OUT / "shot-math.png"))
    answer(pg, a1 + 1); pg.wait_for_timeout(600)
    check("2 tries left" in pg.text_content(".fb") and question(pg)[0] == q1, "1st miss: same question, 2 tries left")
    answer(pg, a1 + 1); pg.wait_for_timeout(600)
    check("Last try" in pg.text_content(".fb"), "2nd miss: last try")
    pg.click(".sheet:not([hidden]) .close"); pg.click("#btnHint")
    check(question(pg)[0] == q1 and "Last try" in pg.text_content(".fb"), "closing and reopening keeps the question and tries")
    answer(pg, a1 + 1); pg.wait_for_timeout(300)
    check(f"The answer was {a1}" in pg.text_content(".fb"), "3rd miss shows the answer")
    pg.wait_for_timeout(2600)
    check(pg.locator(".tries i:not(.used)").count() == 3, "then a new question with 3 fresh tries")
    q2, a2 = question(pg); answer(pg, a2); pg.wait_for_timeout(1200)
    check(pg.locator(".ghost").count() == 1 and pg.text_content("#tip").startswith("Hint:"), "correct answer shows the hint")

    pg.click("#btnMusic"); off = pg.get_attribute("#btnMusic", "aria-pressed")
    pg.click("#btnMusic"); on = pg.get_attribute("#btnMusic", "aria-pressed")
    check(off == "false" and on == "true", "music button toggles")
    ms = pg.evaluate("(()=>{const T=window.__tilesolve,L=T.getLevel(7,1000),t=performance.now(),s=T.solveNext(L.cars,L.pos);return [L.par,s?1:0,performance.now()-t]})()")
    check(ms[1] == 1 and ms[2] < 3000, f"hint works on hardest level (par {ms[0]}, {ms[2]:.0f} ms)")
    pg.click("#btnLevels")
    check("Mia" in pg.text_content("#whoLbl") and "Grade 3" in pg.text_content("#whoLbl"), "level picker shows who is playing")
    pg.click("#closeLevels")

    # ---- Second player has separate progress and grade-appropriate everything ----
    pg.click("#btnHome"); pg.wait_for_url("**/index.html")
    check(pg.is_visible("#viewGames"), "Home button returns to the game grid")
    pg.click("#btnMe")
    check(pg.is_visible("#viewPlayers") and pg.locator(".player:not(.addp)").count() == 1, "player chip goes back to Who's playing")
    pg.click("#btnAdd"); add_player(pg, "Sam", 7, 1)
    pg.click(".game[data-game='car']"); pg.wait_for_url("**/games/car/index.html"); pg.wait_for_timeout(200)
    if pg.locator(".ts-howto").is_visible(): pg.click(".ts-howto .bigbtn"); pg.wait_for_timeout(300)
    sam_par = pg.text_content("#par")
    check(pg.text_content("#moves") == "0" and sam_par == str(pg.evaluate("window.__tilesolve.getLevel(1,1).par")), "Sam starts fresh with grade 1 puzzles")
    pg.click("#btnHint"); qs, _ = question(pg)
    check(all(int(v) <= 20 for v in re.findall(r"\d+", qs)), f"grade 1 player gets grade 1 maths ({qs})")
    pg.goto(HOME)
    pg.click("#btnMe")
    pg.screenshot(path=str(OUT / "shot-players.png"))
    keys = pg.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('tilesolve:p:')&&k.endsWith(':car')).length")
    check(keys == 2, "each player has their own Car save")

    # ---- Back to games, and getting in and out of editing ----
    check(pg.is_visible("#btnBack") and "Back to games" in pg.text_content("#btnBack"), "Who's playing has a Back to games button")
    pg.click("#btnBack")
    check(pg.is_visible("#viewGames") and "Sam" in pg.text_content("#meName"), "Back returns to the same player's games")
    pg.click("#btnMe"); pg.click("#btnEdit")
    check(pg.text_content("#whoTitle") == "Edit players" and pg.is_visible("#btnDone") and pg.is_visible("#editNote") and pg.is_hidden("#btnEdit"),
          "edit mode is obvious: title, explanation and a Done button at the top")
    pg.screenshot(path=str(OUT / "shot-editing.png"))
    pg.click(".player:has-text('Mia')"); pg.fill("#fName", "Mia Rose"); pg.click("#formSave")
    check(pg.text_content("#whoTitle") == "Edit players" and pg.locator(".player:has-text('Mia Rose')").count() == 1, "saving a change keeps you in edit mode")
    pg.click("#btnDone")
    check(pg.text_content("#whoTitle") == "Who's playing?" and pg.is_hidden("#btnDone"), "Done leaves edit mode")
    pg.click(".player:has-text('Mia Rose')")
    check(pg.is_visible("#viewGames") and "Mia Rose" in pg.text_content("#meName"), "after Done, tapping a player picks them again")
    pg.click("#btnMe"); pg.click("#btnEdit"); pg.click("#btnBack")
    check(pg.text_content("#whoTitle") == "Who's playing?", "Back also leaves edit mode")

    # ---- Edit and delete ----
    pg.click("#btnEdit"); pg.click(".player:has-text('Sam')")
    check(pg.text_content("#formTitle") == "Edit Sam", "edit mode opens a player's details")
    pg.click("#btnDelete")
    check(pg.locator(".player:has-text('Sam')").count() == 1, "first delete tap only asks to confirm")
    pg.click("#btnDelete")
    check(pg.locator(".player:not(.addp)").count() == 1 and pg.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('tilesolve:p:')&&k.endsWith(':car')).length") == 1,
          "second tap deletes the player and their progress")

    # ---- Old single-player save becomes "Player 1" ----
    ctx2 = b.new_context(viewport={"width": 390, "height": 844})
    p2 = ctx2.new_page()
    p2.goto(HOME)
    p2.evaluate("""localStorage.clear();localStorage.setItem('tilesolve:car',JSON.stringify({grade:3,music:false,all:false,prog:{3:{unlocked:12,stars:{1:3,2:2},last:11}}}));
                   localStorage.setItem('ubc:L5','{}')""")
    p2.goto(CAR)
    check(p2.text_content("#lvlNum") == "11", "old save migrates: same level")
    check(p2.get_attribute("#btnMusic", "aria-pressed") == "false", "old save migrates: music setting")
    check(p2.evaluate("localStorage.getItem('tilesolve:car')===null && localStorage.getItem('ubc:L5')===null"), "old keys removed")
    p2.goto(HOME)
    check("Player 1" in p2.text_content("#meName"), "migrated player is called Player 1")
    p3 = ctx2.new_page(); p3.goto(HOME); p3.evaluate("localStorage.clear()"); p3.goto(CAR)
    check(p3.url.endswith("/index.html") and "/games/" not in p3.url, "opening a game with no player goes home")
    ctx2.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()

print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
