"""Browser tests for the Little Learners app (built into little/).  python3 tools/test_little.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []
LBASE = BASE + "/little"
LITTLE = ["trains", "abc", "syllables", "blend", "missletter", "case", "sound", "trace", "count", "numorder", "moreless", "missnum", "tenframe", "shapesort", "shapehunt", "colours", "sizeorder", "rhyme", "position", "shapes3d"]
EXTRAS = ["patterns", "animals", "oddone"]; MUSIC = ["tunes", "carols"]

def player(grade, pid):
    seen = json.dumps({g: 1 for g in GAMES})
    return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐸',grade:{grade},color:'#43a047'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(seen)})")

check((ROOT / "little/wrangler.jsonc").exists() and '"littlelearners"' in (ROOT / "little/wrangler.jsonc").read_text(), "little/ has its own Worker config (littlelearners)")
check((ROOT / "little/icon-180.png").read_bytes() != (ROOT / "icon-180.png").read_bytes(), "Little Learners has its own icon")
check(sorted(d.name for d in (ROOT / "little/games").iterdir()) == sorted(LITTLE + EXTRAS + MUSIC), "little/ has exactly its 25 games")

with sync_playwright() as p:
    b = p.chromium.launch()
    # first launch: new player, Kindergarten by default, only K-3 grades
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    pg = watch_errors(ctx.new_page(), errors); pg.goto(LBASE + "/index.html"); pg.wait_for_timeout(300)
    check(pg.title() == "Little Learners" and "LITTLE" in pg.text_content(".brand") and "LEARNERS" in pg.text_content(".brand"), "home says Little Learners")
    check(pg.locator("meta[name='apple-mobile-web-app-title']").get_attribute("content") == "Little Learners", "the home-screen name is Little Learners")
    check(pg.is_visible("#sheetPlayer") and pg.locator("#fGrades button").count() == 4 and "K" in pg.text_content("#fGrades .cur"), "new player: grades K to 3, Kindergarten picked")
    pg.screenshot(path=str(OUT / "little-newplayer.png"))
    check(pg.locator("#fFavs button").count() == 8, "the player form offers favourite things (none + 7)")
    pg.click("#fFavs button[data-fav='trains']")
    pg.fill("#fName", "Lily"); pg.click("#formSave"); pg.wait_for_timeout(300)
    check(pg.evaluate("JSON.parse(localStorage.getItem('tilesolve:players')).list[0].fav") == "trains", "picking 🚂 Trains saves it on the player")
    heads = pg.locator(".gsec h2").all_text_contents()
    check([h.split(" ")[0] for h in heads] == ["Little", "More", "Music"], f"sections: Little learners, More to explore, Music ({heads})")
    got = lambda grp: sorted(pg.evaluate(f"[...document.querySelectorAll(\".games[data-group='{grp}'] .game\")].map(e=>e.dataset.game)"))
    check(got("little") == sorted(LITTLE) and got("explore") == sorted(EXTRAS) and got("puzzles") == sorted(MUSIC), "all 25 games are listed")
    pg.screenshot(path=str(OUT / "little-home.png"), full_page=True)
    check(not pg.is_visible("#otherApp"), "no cross-app link on a test address")
    ctx.close()

    # every game opens inside the little app and Home goes back to the little home
    ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(player(1, "lg"))
    for g in LITTLE + EXTRAS + MUSIC:
        gp = watch_errors(ctx.new_page(), errors); gp.goto(f"{LBASE}/games/{g}/index.html"); gp.wait_for_timeout(500)
        ok = gp.evaluate("!!document.getElementById('kStage')") and "Little Learners" in gp.title()
        gp.click("#kHome"); gp.wait_for_timeout(300)
        check(ok and gp.url.endswith("/little/index.html"), f"{g}: opens in Little Learners and Home comes back to it")
        gp.close()
    # a train-loving player counts trains, and Train Yard adds cars to his train
    ctx.add_init_script("(()=>{const d=JSON.parse(localStorage.getItem('tilesolve:players'));d.list[0].fav='trains';localStorage.setItem('tilesolve:players',JSON.stringify(d))})()")
    gp = watch_errors(ctx.new_page(), errors); gp.goto(f"{LBASE}/games/count/index.html"); gp.wait_for_function("window.__learn && __learn.R", timeout=10000)
    pics = gp.evaluate("[...new Set([...document.getElementById('lrPrompt').textContent.replace(/[A-Za-z?: ]/g,'')])].join('')")
    check(any(t in pics for t in "🚂🚃🚋🚆🚇🚄🚉"), f"favourite trains show up in Count It ({pics[:6]})")
    gp.goto(f"{LBASE}/games/trains/index.html"); gp.wait_for_function("window.__learn && __learn.R", timeout=10000)
    for _ in range(10):
        if gp.is_visible("#kSheetWin"): break
        gp.evaluate("__learn.R && !__learn.R.done && __learn.solve()"); gp.wait_for_timeout(950)
    check("Your train has 1 car" in gp.text_content("#kWinText"), f"winning Train Yard adds a car to his train ({gp.text_content('#kWinText')[-40:]})")
    gp.close()
    # earning 🎵 inside the little app opens songs
    gp = watch_errors(ctx.new_page(), errors); gp.goto(f"{LBASE}/games/count/index.html"); gp.wait_for_function("window.__learn && __learn.R", timeout=10000)
    for _ in range(12):
        if gp.is_visible("#kSheetWin"): break
        gp.evaluate("__learn.R && !__learn.R.done && __learn.solve()"); gp.wait_for_timeout(900)
    check(gp.evaluate("TS.notes.count()") >= 1, "finishing a Little learners level earns a 🎵 here too")
    ctx.close()

    # the main app's link logic (pretend addresses)
    ctx = b.new_context(viewport={"width": 390, "height": 844})
    pg = ctx.new_page(); pg.goto(LBASE + "/index.html")
    html = (ROOT / "index.html").read_text()
    check("littlelearners." in html and "tilesolve." in (ROOT / "little/index.html").read_text(), "each app links to the other on the workers.dev addresses")
    ctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
