"""Browser tests for Picture Crossword.  python3 tools/test_crossword.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []

def player(grade, pid="cw"):
    return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐸',grade:{grade},color:'#43a047'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(json.dumps({g: 1 for g in GAMES + ['crossword']}))})")

VALIDATE = """(()=>{const bad=[];let n=0,maxR=0,maxC=0;
  for(let lv=1;lv<=40;lv++){const P=__game.build(lv);if(!P){bad.push(lv+' no grid');continue}n++;maxR=Math.max(maxR,P.rows);maxC=Math.max(maxC,P.cols);
    const sp=__game.spec(lv);if(P.words.length!==sp.count)bad.push(lv+' has '+P.words.length+' words');
    if(new Set(P.words.map(w=>w.w)).size!==P.words.length)bad.push(lv+' repeats a word');
    const owner=new Map();P.words.forEach((w,i)=>{if(w.w.length<sp.lo||w.w.length>sp.hi)bad.push(lv+' length '+w.w);
      w.cells.forEach((k,j)=>{if(P.cells.get(k)!==w.w[j])bad.push(lv+' letter clash '+w.w);owner.set(k,(owner.get(k)||[]).concat(i))})});
    if(owner.size!==P.cells.size)bad.push(lv+' stray cells');
    // squares side by side must be part of the same word
    for(const k of P.cells.keys()){const[r,c]=k.split(',').map(Number);for(const[dr,dc]of[[0,1],[1,0]]){const k2=(r+dr)+','+(c+dc);
      if(P.cells.has(k2)&&!owner.get(k).some(i=>owner.get(k2).includes(i)&&P.words[i].d===dr))bad.push(lv+' touching words at '+k)}}
    // all words joined up
    const seen=new Set([0]),todo=[0];while(todo.length){const i=todo.pop();P.words[i].cells.forEach(k=>owner.get(k).forEach(j=>{if(!seen.has(j)){seen.add(j);todo.push(j)}}))}
    if(seen.size!==P.words.length)bad.push(lv+' not connected');
    if(P.rows>10||P.cols>9)bad.push(lv+' too big');
    const nums=P.words.map(w=>w.num);if(nums[0]!==1)bad.push(lv+' numbering')}
  return{bad:bad.slice(0,6),nb:bad.length,n,maxR,maxC}})()"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for grade in range(2, 8):
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(player(grade))
        pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("crossword")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
        v = pg.evaluate(VALIDATE)
        check(v["nb"] == 0 and v["n"] == 40, f"grade {grade}: 40 crosswords build, all words cross and fit on a phone (up to {v['maxR']}x{v['maxC']}) {v['bad']}")
        if grade in (2, 7): pg.screenshot(path=str(OUT / f"crossword-g{grade}.png"))
        ctx.close()

    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(player(3))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("crossword")); pg.wait_for_function("window.__game && __game.S", timeout=10000)
    w = pg.evaluate("__game.S.words[__game.S.sel].w")
    wrong = "".join("q" if ch != "q" else "z" for ch in w)
    for ch in wrong: pg.click(f".cw-keys button[data-ch='{ch}']")
    pg.wait_for_timeout(900)
    check("Oops 1" in pg.text_content("#kSub") and pg.evaluate("__game.S.done.size") == 0, "a wrong word counts an oops")
    check(pg.evaluate("[...__game.S.words[__game.S.sel].cells].filter(k=>__game.S.fill.has(k)).length") == 0, "wrong letters are taken away")
    for ch in w[:-1]: pg.click(f".cw-keys button[data-ch='{ch}']")
    pg.click(".cw-keys .del")
    check(pg.evaluate("[...__game.S.words[__game.S.sel].cells].filter(k=>__game.S.fill.has(k)).length") == len(w) - 2, "⌫ removes the last letter")
    for ch in w[-2:]: pg.click(f".cw-keys button[data-ch='{ch}']")
    pg.wait_for_timeout(300)
    check(pg.evaluate("__game.S.done.size") >= 1 and pg.locator(".cw-c.ok").count() >= len(w), "a right word turns green")
    sel = pg.evaluate("__game.S.sel")
    check(sel != 0 and not pg.evaluate(f"__game.S.done.has({sel})"), "the next unfinished word is picked automatically")
    l0 = pg.evaluate("__game.S.lock.size")
    pg.click("#kHint"); pg.wait_for_timeout(400)
    if pg.is_visible(".prob"): solve_math(pg)
    check(pg.evaluate("__game.S.lock.size") == l0 + 1, "a hint (after a maths question) fills in the next letter")
    pg.click(f".cw-q[data-i='{pg.evaluate('__game.S.words.length-1')}']"); pg.wait_for_timeout(100)
    check(pg.evaluate("__game.S.sel") == pg.evaluate("__game.S.words.length-1"), "tapping a picture clue picks that word")
    pg.screenshot(path=str(OUT / "crossword-play.png"))
    for _ in range(12):
        if pg.is_visible("#kSheetWin"): break
        pg.evaluate("__game.solveWord()"); pg.wait_for_timeout(250)
    pg.wait_for_timeout(900)
    check(pg.is_visible("#kSheetWin"), "filling every word wins the level")
    ctx.close()

    # ---------- iPad touch ----------
    tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(player(4, "t4"))
    tp = watch_errors(tctx.new_page(), errors); tp.goto(URL("crossword")); tp.wait_for_function("window.__game && __game.S", timeout=10000)
    k = tp.evaluate("__game.S.words[1].cells[0]")
    tap_center(tp, f".cw-c[data-k='{k}']")
    check(1 in tp.evaluate(f"__game.S.words.map((w,i)=>w.cells.includes('{k}')?i:-1)") and tp.evaluate(f"__game.S.words[__game.S.sel].cells.includes('{k}')"), "touch: tapping a square picks its word")
    w = tp.evaluate("__game.S.words[__game.S.sel]")
    for j, ch in enumerate(w["w"]):
        if not tp.evaluate(f"__game.S.fill.has('{w['cells'][j]}')"): tap_center(tp, f".cw-keys button[data-ch='{ch}']")
    tp.wait_for_timeout(300)
    check(tp.evaluate("__game.S.done.size") >= 1, "touch: typing on the letter keys fills a word")
    tp.screenshot(path=str(OUT / "crossword-ipad.png"))
    tctx.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
