"""Browser tests for Word Search.  python3 tools/test_games5.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []

def center(pg, i):
    return pg.evaluate(f"(()=>{{const r=__game.S.el.querySelector('.wc[data-i=\"{i}\"]').getBoundingClientRect();return[r.left+r.width/2,r.top+r.height/2]}})()")

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(INIT)
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("wordsearch")); pg.wait_for_timeout(300)

    ramp = pg.evaluate("[1,6,11,21,29,36].map(n=>{const s=__game.spec(n);return s.size+'/'+s.count+'/'+s.set})")
    print("word search grade 3 (size/words/directions):", ramp)
    check(ramp == ["7/4/RD", "8/5/RD", "8/6/RDX", "9/7/RDX", "10/8/RDXB", "10/9/ALL"], "ramp: bigger grids, more words, diagonal from 11, backwards from 29")
    # every level for every grade: words placed once, the right directions, no blocked words in the grid
    res = pg.evaluate("""(()=>{const bad=[],K=__game.K,DIRS={RD:['R','D'],RDX:['R','D','DR','UR'],RDXB:['R','D','DR','UR','L','U']};let worst=0;
      for(const g of [1,3,7]){K.grade=g;for(let n=1;n<=40;n++){const t=performance.now();K.load(n);worst=Math.max(worst,performance.now()-t);
        const S=__game.S,sp=__game.spec(n);if(S.words.length<Math.max(2,sp.count-1))bad.push(g+':'+n+' few words');
        for(const w of S.words){if(__game.occurrences(S.grid,S.N,w.w)!==1)bad.push(g+':'+n+' '+w.w+' not unique');
          if(sp.set!=='ALL'&&!DIRS[sp.set].includes(w.dir))bad.push(g+':'+n+' '+w.w+' dir '+w.dir)}
        for(const x of __game.BLOCK)if(__game.occurrences(S.grid,S.N,x))bad.push(g+':'+n+' contains blocked word')}}
      K.grade=3;K.load(1);return {bad,worst}})()""")
    check(res["bad"] == [], f"all 120 levels checked (grades 1, 3, 7): every word hidden exactly once, right directions, clean filler {res['bad'][:3]}")
    check(res["worst"] < 2500, f"levels build quickly (slowest {res['worst']:.0f} ms)")
    pg.reload(); pg.wait_for_timeout(300)
    pg.screenshot(path=str(OUT / "ws-1.png"))
    W = pg.evaluate("__game.S.words.map(w=>({w:w.w,cells:w.cells}))")
    # drag across the first word
    a, z = center(pg, W[0]["cells"][0]), center(pg, W[0]["cells"][-1])
    mouse_drag(pg, a[0], a[1], z[0], z[1], 8)
    check(pg.evaluate("__game.S.words[0].found"), f"dragging across {W[0]['w']} finds it")
    check(pg.locator(f".wchip.found[data-w='{W[0]['w']}']").count() == 1, "found word is crossed off the list")
    # drag backwards across the second word also counts
    a, z = center(pg, W[1]["cells"][-1]), center(pg, W[1]["cells"][0])
    mouse_drag(pg, a[0], a[1], z[0], z[1], 8)
    check(pg.evaluate("__game.S.words[1].found"), "dragging a word from its last letter to its first also works")
    # a wrong line counts a miss
    N = pg.evaluate("__game.S.N"); used = set(c for w in W for c in w["cells"])
    row = next(r for r in range(N) if all(r*N+c not in used for c in range(3)) ) if any(all(r*N+c not in used for c in range(3)) for r in range(N)) else None
    if row is not None:
        a, z = center(pg, row*N), center(pg, row*N+2); mouse_drag(pg, a[0], a[1], z[0], z[1], 6)
        check("Misses 1" in pg.text_content("#kSub"), "a line that isn't a word counts a miss")
    # tap first letter, then last letter
    pg.mouse.click(*center(pg, W[2]["cells"][0])); pg.wait_for_timeout(150)
    check(pg.locator(".wc.anchor").count() == 1, "tapping a letter marks it as the start")
    pg.mouse.click(*center(pg, W[2]["cells"][-1])); pg.wait_for_timeout(200)
    check(pg.evaluate("__game.S.words[2].found") and pg.locator(".wc.anchor").count() == 0, "tapping the last letter finds the word")
    pg.screenshot(path=str(OUT / "ws-found.png"))
    pg.click("#kHint"); solve_math(pg)
    check(pg.locator(".wc.hint").count() == 1 and "Look for" in pg.text_content("#kTip"), "maths hint flashes the first letter of a word")
    for w in W[3:]:
        a, z = center(pg, w["cells"][0]), center(pg, w["cells"][-1]); mouse_drag(pg, a[0], a[1], z[0], z[1], 8)
    pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin") and pg.locator("#kWinStars .off").inner_text() == "", "finding every word wins (1 miss = 3 stars)")
    unlock_all(pg, "wordsearch", reload=True); go_level(pg, 36); pg.wait_for_timeout(300)
    pg.screenshot(path=str(OUT / "ws-36.png"))
    check(pg.evaluate("__game.S.N") == 10, "level 36 is a 10×10 grid")
    pg.close()

    # Older grade gets the big grid
    c7 = b.new_context(viewport={"width": 1024, "height": 1366})
    c7.add_init_script("localStorage.setItem('tilesolve:players',JSON.stringify({list:[{id:'k7',name:'Ben',avatar:'🦁',grade:7,color:'#3b6fd9'}],current:'k7',music:true}));"
                       "localStorage.setItem('tilesolve:p:k7:seen',JSON.stringify({wordsearch:1}));"
                       "localStorage.setItem('tilesolve:p:k7:wordsearch',JSON.stringify({grades:{7:{unlocked:40,stars:{},last:40}},all:true}))")
    p7 = watch_errors(c7.new_page(), errors); p7.goto(URL("wordsearch")); p7.wait_for_timeout(500)
    check(p7.evaluate("__game.S.N") == 14 and p7.evaluate("__game.S.words.length") >= 12, f"grade 7 level 40: 14×14 with {p7.evaluate('__game.S.words.length')} words")
    p7.screenshot(path=str(OUT / "ws-grade7.png")); c7.close()

    # iPad touch: finger drag
    tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(INIT)
    tp = watch_errors(tctx.new_page(), errors); tp.goto(URL("wordsearch")); tp.wait_for_timeout(400)
    w = tp.evaluate("__game.S.words[0].cells"); a = center(tp, w[0]); z = center(tp, w[-1])
    touch_drag(tp, a[0], a[1], z[0], z[1], 8)
    check(tp.evaluate("__game.S.words[0].found"), "touch: finger-dragging across a word finds it on iPad")
    w = tp.evaluate("__game.S.words[1].cells")
    tap_center(tp, f".wc[data-i='{w[0]}']"); tap_center(tp, f".wc[data-i='{w[-1]}']")
    check(tp.evaluate("__game.S.words[1].found"), "touch: tap first letter then last letter finds it")
    tctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
