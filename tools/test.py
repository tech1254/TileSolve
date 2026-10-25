"""Browser test for Unblock the Car.  python3 tools/test.py [path/to/index.html]
Checks: grade picker, difficulty curve, drag release has no bounce, maths-for-a-hint flow, music toggle, no JS errors."""
import sys, re, json, pathlib
from playwright.sync_api import sync_playwright

FILE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent.parent / "index.html").resolve()
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(".")
fails = []
def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)

def movable(cars, pos):
    occ = {}
    for i, c in enumerate(cars):
        for j in range(c["len"]):
            occ[(c["f"]*6 + pos[i] + j) if c["h"] else ((pos[i]+j)*6 + c["f"])] = i
    for i, c in enumerate(cars):
        cell = (lambda q: c["f"]*6 + q) if c["h"] else (lambda q: q*6 + c["f"])
        hi = pos[i]
        while hi + c["len"] < 6 and cell(hi + c["len"]) not in occ: hi += 1
        if hi > pos[i]: return i, hi - pos[i], 1
        lo = pos[i]
        while lo > 0 and cell(lo - 1) not in occ: lo -= 1
        if lo < pos[i]: return i, pos[i] - lo, -1
    return None

with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, has_touch=False)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: m.type == "error" and "Failed to load resource" not in m.text and errors.append(m.text))
    pg.goto(FILE.as_uri())

    # Grade picker on first launch
    check(pg.is_visible("#sheetGrade"), "grade picker shows on first launch")
    pg.screenshot(path=str(OUT / "shot-grade.png"))
    pg.click("#gradeGrid button:nth-child(3)")
    check(pg.is_hidden("#sheetGrade") and pg.text_content("#lvlNum") == "1", "picking grade 3 starts level 1")
    saved = pg.evaluate("JSON.parse(localStorage.getItem('tilesolve:car'))")
    check(saved["grade"] == 3, "grade is saved")

    # Difficulty curve
    curve = pg.evaluate("[1,5,10,20,30,50,100,200,500,1000].map(n=>[n,window.__tilesolve.getLevel(3,n).par])")
    print("grade 3 par by level:", curve)
    d = dict(curve)
    check(d[1] <= 5 and 17 <= d[30] <= 22 and d[100] > d[30] and all(curve[i][1] <= curve[i+1][1] for i in range(len(curve)-1)),
          "grade 3 curve: easy start, ~20 by level 30, rising after")
    g1, g7 = pg.evaluate("[window.__tilesolve.getLevel(1,30).par, window.__tilesolve.getLevel(7,30).par]")
    check(g1 < d[30] < g7, f"older grades harder at level 30 (g1={g1}, g3={d[30]}, g7={g7})")
    distinct = pg.evaluate("new Set(Array.from({length:200},(_,k)=>JSON.stringify(window.__tilesolve.getLevel(3,k+1).pos)+window.__tilesolve.getLevel(3,k+1).cars.length)).size")
    check(distinct >= 195, f"first 200 grade-3 levels are (nearly) all different ({distinct}/200)")
    pg.screenshot(path=str(OUT / "shot-board.png"))

    # Drag release: car must glide to its cell without first moving back toward where it started
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
    tr = pg.evaluate("window.__trace")
    axis = 0 if horiz else 1
    vals = [t[axis] for t in tr]
    final, rel = vals[-1], vals[0]
    worst = max(abs(v - final) - abs(rel - final) for v in vals)
    back = max(0, *(sign*(vals[k-1]-vals[k]) for k in range(1, len(vals))))
    print(f"drag trace (px along axis): {[round(v) for v in vals[:12]]} ... {round(final)}")
    check(worst <= 1.5 and back <= 1.5, f"released car settles without bouncing (overshoot {worst:.1f}px, backstep {back:.1f}px)")
    check(pg.text_content("#moves") == "1", "drag counted as one move")

    # Maths for a hint
    pg.click("#btnHint")
    check(pg.is_visible("#sheetMath"), "hint opens a maths question")
    def question():
        t = pg.inner_text("#mathQ").replace("\n", " ")
        nums = list(map(int, re.findall(r"\d+", t)))
        if "?" in t and t.index("?") < t.index("="):  # a + ? = c
            return t, nums[1] - nums[0]
        return t, (nums[0] + nums[1]) if "+" in t else (nums[0] - nums[1])
    def answer(n):
        for ch in str(n): pg.click(f"#mathKeys button:text-is('{ch}')")
        pg.click("#mathKeys .ok")
    q1, a1 = question(); print("question:", q1, "->", a1)
    check(all(0 <= v <= 100 for v in map(int, re.findall(r"\d+", q1))) and 0 <= a1 <= 100, "question is grade-2 range (within 100)")
    pg.screenshot(path=str(OUT / "shot-math.png"))
    wrong = a1 + 1
    answer(wrong); pg.wait_for_timeout(600)
    check("2 tries left" in pg.text_content("#mathFb") and question()[0] == q1, "1st wrong answer: same question, 2 tries left")
    answer(wrong); pg.wait_for_timeout(600)
    check("Last try" in pg.text_content("#mathFb") and question()[0] == q1, "2nd wrong answer: same question, last try")
    pg.click("#closeMath"); pg.click("#btnHint")
    check(question()[0] == q1 and "Last try" in pg.text_content("#mathFb"), "closing and reopening keeps the question and tries")
    answer(wrong); pg.wait_for_timeout(300)
    check(f"The answer was {a1}" in pg.text_content("#mathFb"), "3rd wrong answer shows the answer")
    pg.wait_for_timeout(2600)
    tries = pg.locator("#mathTries i:not(.used)").count()
    check(tries == 3, "then a new question with 3 fresh tries")
    q2, a2 = question(); answer(a2); pg.wait_for_timeout(1200)
    check(pg.is_hidden("#sheetMath") and pg.locator(".ghost").count() == 1 and pg.text_content("#tip").startswith("Hint:"), "correct answer closes sheet and shows the hint")
    pg.screenshot(path=str(OUT / "shot-hint.png"))

    # Music toggle
    st = pg.evaluate("window.AudioContext ? 'yes' : 'no'")
    pg.click("#btnMusic")
    off = pg.get_attribute("#btnMusic", "aria-pressed")
    pg.click("#btnMusic")
    on = pg.get_attribute("#btnMusic", "aria-pressed")
    check(off == "false" and on == "true" and pg.evaluate("JSON.parse(localStorage.getItem('tilesolve:car')).music") is True, "music button toggles and is remembered")

    # Hardest level: hint solver must still answer quickly
    ms = pg.evaluate("(()=>{const T=window.__tilesolve,L=T.getLevel(7,1000),t=performance.now(),s=T.solveNext(L.cars,L.pos);return [L.par,s?1:0,performance.now()-t]})()")
    check(ms[1] == 1 and ms[2] < 3000, f"hint works on hardest level (par {ms[0]}, {ms[2]:.0f} ms)")

    # Reload keeps grade, level and progress
    pg.reload()
    check(pg.is_hidden("#sheetGrade") and pg.text_content("#lvlNum") == "1", "reload keeps grade and level")
    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()

print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
