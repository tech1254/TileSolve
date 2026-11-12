"""Block Fit hints: solve from where the player is.  python3 tools/test_blocks_hint.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
check = Checker(); errors = []
def player(grade, pid): return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐯',grade:{grade},color:'#3b6fd9'}}],current:'{pid}',music:true}}));"
                                f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(SEEN)});localStorage.setItem('tilesolve:p:{pid}:blocks',JSON.stringify({{grades:{{}},all:true}}))")
placed = "__game.S.pieces.filter(p=>p.at).length"
def hint(pg): pg.evaluate("__game.hint()"); pg.wait_for_timeout(1150)
with sync_playwright() as p:
    b = p.chromium.launch()
    for grade in (1, 3, 5):
        ctx = b.new_context(viewport={"width": 820, "height": 1180}); ctx.add_init_script(player(grade, f"b{grade}"))
        pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("blocks")); pg.wait_for_function("window.__game&&__game.S", timeout=10000)
        for n in (3, 15, 32):
            pg.evaluate(f"__game.K.load({n})"); pg.wait_for_timeout(300)
            hint(pg)
            check(pg.evaluate(placed) == 1 and pg.evaluate("!!__game.solveFrom(__game.S.pieces.filter(p=>p.at))"), f"grade {grade} level {n}: a hint slides one block into a spot that works")
            if OUT and n == 15 and grade == 3:
                pg.evaluate("__game.hint()"); pg.wait_for_timeout(450); pg.screenshot(path=str(OUT / "blocks_hint_fly.png")); pg.wait_for_timeout(700)
            # a symmetric block turned around but in the right place stays; the hint adds a new one
            r = pg.evaluate("""()=>{const G=__game,S=G.S;S.pieces.forEach(p=>p.at=null);const sol=G.solveFrom([]);
              const sym=sol.find(m=>{const a=JSON.stringify(G.shape({...m.p,rot:m.rot})),k=[1,2,3].find(k=>JSON.stringify(G.shape({...m.p,rot:(m.rot+k)%4}))===a);m.alt=k;return k});
              if(!sym||!S.sp.rotate)return{skip:true};sym.p.rot=(sym.rot+sym.alt)%4;sym.p.at=sym.at.slice();return{skip:false,id:sym.p.id,at:sym.at}}""")
            if not r["skip"]:
                pg.evaluate("__game.K.stat&&0"); hint(pg)
                check(pg.evaluate(placed) == 2 and pg.evaluate(f"__game.S.pieces.find(p=>p.id==={r['id']}).at.join()") == ",".join(map(str, r["at"])),
                      f"grade {grade} level {n}: a block turned a different way but in a right spot is kept, and a new block is added")
            # a block in a spot that makes the puzzle impossible is taken out
            r = pg.evaluate("""()=>{const G=__game,S=G.S;S.pieces.forEach(p=>p.at=null);const {w,h}=S.sp;
              for(const p of S.pieces)for(let r0=0;r0<h;r0++)for(let c0=0;c0<w;c0++){if(!G.fits(p,r0,c0))continue;p.at=[r0,c0];if(!G.solveFrom([p]))return{id:p.id};p.at=null}return null}""")
            if r:
                hint(pg)
                check(pg.evaluate(f"__game.S.pieces.find(p=>p.id==={r['id']}).at") is None and "won't work" in pg.text_content("#kTip"),
                      f"grade {grade} level {n}: a block in a spot that can't work goes back to the tray, with a note")
            # hint again and again finishes the puzzle
            for k in range(30):
                if pg.is_visible("#kSheetWin"): break
                hint(pg)
            check(pg.is_visible("#kSheetWin"), f"grade {grade} level {n}: pressing Hint over and over finishes the puzzle")
        ctx.close()
    b.close()
check(not errors, f"no page errors {errors[:3]}")
check.finish()
