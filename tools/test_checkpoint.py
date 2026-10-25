"""Browser tests for the maths checkpoint every 3 levels.  python3 tools/test_checkpoint.py"""
import sys, re, json
from playwright.sync_api import sync_playwright
from tsutil import *

check = Checker(); errors = []

def solve_lights(pg):
    for i, v in enumerate(pg.evaluate("Array.from(__game.solve(__game.S.g,__game.S.N).x)")):
        if v: pg.click(f".lb[data-i='{i}']")
    pg.wait_for_timeout(900)

def checkpoint_open(pg):
    return pg.evaluate("TS.math.isOpen && TS.math.kind==='check'")

def answer(pg, v):
    for ch in str(v): pg.click(f".keys button[data-k='{ch}']")
    pg.click(".keys .ok")

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(INIT)
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("lights")); pg.wait_for_timeout(200)

    for n in (1, 2):
        solve_lights(pg); check(pg.text_content("#kWinNext") == "Next level", f"no checkpoint after level {n}")
        pg.click("#kWinNext"); pg.wait_for_timeout(200)
        check(not checkpoint_open(pg) and pg.text_content("#kNum") == str(n + 1), f"level {n+1} opens straight away")
    solve_lights(pg)
    check(pg.text_content("#kWinNext") == "Maths, then next level", "after level 3 the button says maths comes first")
    pg.click("#kWinNext"); pg.wait_for_timeout(200)
    check(checkpoint_open(pg) and pg.text_content("#tsMathT") == "Maths checkpoint!", "a maths checkpoint opens before level 4")
    check(not pg.locator(".sheet:not([hidden]) .close").is_visible(), "the checkpoint can't be skipped (no Not now)")
    qs = []
    for _ in range(25):
        t = pg.inner_text(".prob").replace("\n", " "); qs.append(t)
        pg.evaluate("(()=>{})()")
        break
    t = qs[0]; nums = list(map(int, re.findall(r"\d+", t)))
    print("grade 3 checkpoint question:", t)
    easy = all(v <= 99 for v in nums)
    if "+" in t and "?" not in t.split("=")[0] and nums[1] < 10 and nums[0] >= 10: easy = easy and (nums[0] % 10 + nums[1] < 10)
    if "−" in t and nums[1] < 10 and nums[0] >= 10: easy = easy and (nums[0] % 10 >= nums[1])
    check(easy, "checkpoint question is easier: within 100, no carrying or borrowing")
    # leaving and coming back still asks
    pg.reload(); pg.wait_for_function("window.__game && __game.S", timeout=10000); pg.wait_for_timeout(300)
    num = pg.text_content("#kNum")
    check(num == "3" and not checkpoint_open(pg), f"reloading goes back to level 3 (shows level {num})")
    pg.click("#kNext"); pg.wait_for_timeout(200)
    check(checkpoint_open(pg), "the › button also asks the checkpoint")
    a = question(pg); answer(pg, a + 1); pg.wait_for_timeout(600); answer(pg, a + 1); pg.wait_for_timeout(600); answer(pg, a + 1); pg.wait_for_timeout(300)
    check(f"The answer was {a}" in pg.text_content(".fb"), "three misses show the answer")
    pg.wait_for_timeout(2600)
    answer(pg, question(pg)); pg.wait_for_timeout(1300)
    check(not checkpoint_open(pg) and pg.text_content("#kNum") == "4", "right answer opens level 4")
    pg.click("#kPrev"); pg.wait_for_timeout(200); pg.click("#kNext"); pg.wait_for_timeout(200)
    check(not checkpoint_open(pg) and pg.text_content("#kNum") == "4", "once passed, level 4 opens freely")
    for n in (4, 5):
        solve_lights(pg); pg.click("#kWinNext"); pg.wait_for_timeout(200)
    check(not checkpoint_open(pg) and pg.text_content("#kNum") == "6", "no checkpoint after levels 4 and 5")
    solve_lights(pg); pg.click("#kWinNext"); pg.wait_for_timeout(200)
    check(checkpoint_open(pg), "next checkpoint comes after level 6")
    answer(pg, question(pg)); pg.wait_for_timeout(1300)
    check(pg.text_content("#kNum") == "7", "then level 7")
    # hint questions are still the harder kind and closable
    pg.click("#kHint"); pg.wait_for_timeout(200)
    check(pg.evaluate("TS.math.kind") == "hint" and pg.locator(".sheet:not([hidden]) .close").is_visible(), "hint questions still have Not now")
    pg.close()

    # ---- Unblock the Car and Picture Puzzle use the same checkpoint ----
    for game, key, data, nxt in [
        ("car", "car", {"grades": {"3": {"unlocked": 4, "stars": {}, "last": 3, "gate": 4}}, "all": False}, "#btnNext"),
        ("picture", "picture", {"mode": "drop", "drop": {"3": {"unlocked": 4, "stars": {}, "last": 3, "gate": 4}}, "slide": {}, "numbers": False, "all": False}, "#btnNext")]:
        c2 = b.new_context(viewport={"width": 390, "height": 844}); c2.add_init_script(INIT)
        c2.add_init_script(f"if(!sessionStorage.getItem('seeded')){{localStorage.setItem('tilesolve:p:k1:{key}',{json.dumps(json.dumps(data))});sessionStorage.setItem('seeded','1')}}")
        q = watch_errors(c2.new_page(), errors); q.goto(URL(game)); q.wait_for_timeout(500)
        q.click(nxt); q.wait_for_timeout(300)
        check(checkpoint_open(q), f"{game}: checkpoint before level 4")
        answer(q, question(q)); q.wait_for_timeout(1500)
        lv = q.text_content("#lvlNum")
        check(not checkpoint_open(q) and lv == "4", f"{game}: answering opens level 4")
        c2.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
