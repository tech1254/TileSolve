"""Smash Chess: rules (perft), every lesson solvable, puzzles generate, bots play legal games, coach warnings.  python3 tools/test_chess.py [screenshot_dir]"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []
def player(grade, pid):
    return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Sam',avatar:'🦊',grade:{grade},color:'#3b6fd9'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(json.dumps({g: 1 for g in GAMES}))})")
def go(pg, n):
    pg.evaluate(f"__chess.K.load({n})"); pg.wait_for_timeout(150)
    if pg.is_visible(".prob"): solve_math(pg); pg.wait_for_timeout(150)
def wait_idle(pg):
    pg.wait_for_function("(__chess.G&&!__chess.G.busy&&!__chess.G.anim)||!document.getElementById('kSheetWin').hidden", timeout=20000)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1024, "height": 768}); ctx.add_init_script(player(4, "c4"))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("chess")); pg.wait_for_function("window.__chess && __chess.G", timeout=10000)
    pg.evaluate("__chess.K.save.all=true")
    # rules: perft counts from standard test positions
    bad = pg.evaluate("""(()=>{const C=__chess;function perft(s,d){if(d===0)return 1;let n=0;for(const m of C.legal(s))n+=perft(C.make(s,m),d-1);return n}
      const P=[[C.START,[20,400,8902]],["r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -",[48,2039]],["8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -",[14,191,2812]],
        ["r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq -",[6,264,9467]],["rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ -",[44,1486]]];
      const out=[];for(const[f,exp]of P){const s=C.fromFEN(f);exp.forEach((e,i)=>{const g=perft(s,i+1);if(g!==e)out.push(f.slice(0,10)+" d"+(i+1)+":"+g)})}return out})()""")
    check(not bad, f"chess rules match the standard move counts (castling, en passant, promotion, checks) {bad}")
    # lessons 1-6: solve each star board by following the hint, in the fewest moves
    for n in range(1, 7):
        go(pg, n); wait_idle(pg)
        par = pg.evaluate("__chess.G.par")
        for _ in range(30):
            if pg.is_visible("#kSheetWin"): break
            wait_idle(pg)
            m = pg.evaluate("""(()=>{const G=__chess.G,C=__chess;const t=G.piece;let best=null,bd=1e9;for(const x of C.pseudo(G.s).filter(x=>!x.promo||x.promo==="Q")){const n=C.make(G.s,x);n.turn="w";const d=C.solveStars(n,t);if(d>=0&&d<bd){bd=d;best=x}}return best&&[best.from,best.to]})()""")
            if pg.is_visible("#kSheetWin") or not m: break
            pg.evaluate(f"__chess.tapSq({m[0]})"); pg.evaluate(f"__chess.tapSq({m[1]})"); pg.wait_for_timeout(600)
        pg.wait_for_timeout(1200)
        check(par > 0 and pg.is_visible("#kSheetWin") and pg.locator("#kWinStars").inner_text().startswith("★★★"), f"lesson {n} ({pg.evaluate('__chess.G.kind')}): stars can all be smashed, in {par} moves for 3 stars")
        if n == 1: pg.screenshot(path=str(OUT / "chess-lesson.png"))
    # puzzles: each generates quickly and can be solved with the hint's move
    for n in (8, 10, 12, 14, 16, 20):
        go(pg, n); wait_idle(pg); kind = pg.evaluate("__chess.G.kind"); ok = True
        for r in range(4):
            if pg.is_visible("#kSheetWin"): break
            wait_idle(pg)
            m = pg.evaluate("""(()=>{const G=__chess.G,C=__chess;let m=null;if(G.goal==="capture")m=G.start.capv.reduce((a,x)=>x.v>a.v?x:a).m;else if(G.goal==="castle")m=C.legal(G.s).find(x=>x.castle);
              else if(G.goal==="check")m=C.legal(G.s).find(x=>C.inCheck(C.make(G.s,x),"b"));else if(G.goal==="mate")m=C.mateIn1(G.s);else m=C.legal(G.s)[0];return m&&[m.from,m.to]})()""")
            if pg.is_visible("#kSheetWin"): break
            if not m: ok = False; break
            pg.evaluate(f"__chess.tapSq({m[0]})"); pg.evaluate(f"__chess.tapSq({m[1]})"); pg.wait_for_timeout(2400)
        pg.wait_for_timeout(800)
        check(ok and pg.is_visible("#kSheetWin"), f"level {n} ({kind}): every puzzle round has a solution and the level can be won")
        if n == 12: pass
    # a wrong capture in the capture lesson: the bot takes back and the coach explains
    go(pg, 8); wait_idle(pg)
    m = pg.evaluate("""(()=>{const G=__chess.G;const w=G.start.capv.filter(x=>x.v<G.start.base-50)[0];return w&&[w.m.from,w.m.to]})()""")
    pg.evaluate(f"__chess.tapSq({m[0]})"); pg.evaluate(f"__chess.tapSq({m[1]})"); pg.wait_for_timeout(1700)
    check("guarded" in pg.text_content("#chSay") or "best" in pg.text_content("#chSay"), f"a capture of a guarded piece is shown and explained ({pg.text_content('#chSay')[:70]})")
    pg.screenshot(path=str(OUT / "chess-trap.png"))
    # matches: a careful player (2 moves ahead) against each bot strength; games finish legally
    pg.evaluate("window.__chessFast=true")
    for n, kind in ((7, "first"), (21, "mid"), (39, "last")):
        go(pg, n); wait_idle(pg)
        res = pg.evaluate("""(async()=>{const C=__chess,G=C.G;for(let ply=0;ply<400;ply++){if(G.busy||G.anim){await new Promise(r=>setTimeout(r,20));continue}
            if(C.status(G.s)||document.getElementById("kSheetWin").hidden===false||G.done)break;if(G.s.turn!=="w"){await new Promise(r=>setTimeout(r,20));continue}
            const m=C.bestMove(G.s,2);G.coachOn=false;C.tryMove(m)}return{st:C.status(G.s),turn:G.s.turn,skill:G.skill,caps:G.caps.w.length+G.caps.b.length}})()""")
        pg.wait_for_timeout(2600)
        check(res["st"] in ("mate", "stalemate", "fifty", "material", None) and pg.is_visible("#kSheetWin"), f"match level {n} (bot skill {res['skill']}): a whole game plays out and ends ({res})")
        if n == 7: check(res["st"] == "mate" and res["turn"] == "b", f"the first bot is gentle enough to lose to a beginner-level player ({res})")
    pg.evaluate("window.__chessFast=false")
    # coach: warns before hanging the queen
    go(pg, 7); wait_idle(pg)
    pg.evaluate("""(()=>{const C=__chess,G=C.G;G.coachOn=true;G.s=C.fromFEN("rnbqkb1r/pppp1ppp/5n2/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -")})()""")
    w = pg.evaluate("""(()=>{const C=__chess,G=C.G;const m=C.legal(G.s).find(x=>x.from===59&&x.to===31);return C.warnFor(m)})()""")
    check(w and "queen" in w, f"the coach warns before a move that hangs the queen ({w})")
    pg.evaluate("__chess.tapSq(59)"); pg.evaluate("__chess.tapSq(31)"); pg.wait_for_timeout(300)
    check(pg.is_visible("#chAsk button") and "sure" in pg.text_content("#chSay"), "the warning asks 'are you sure?' with Move anyway / Think again")
    pg.screenshot(path=str(OUT / "chess-warn.png"))
    # saving: a match in progress saves after every move; reopening offers Continue or New game
    pg.evaluate("window.__chessFast=true"); go(pg, 7); wait_idle(pg)
    if pg.is_visible("#chAsk button"): pg.click("#chAsk button:first-child"); wait_idle(pg)
    for k in range(3):
        pg.evaluate("(()=>{const C=__chess,G=C.G;G.coachOn=false;C.tryMove(C.bestMove(G.s,1))})()"); pg.wait_for_timeout(400); wait_idle(pg)
    saved = pg.evaluate("__chess.K.save.game"); pos = pg.evaluate("__chess.G.s.b.join(',')")
    check(saved and saved["n"] == 7 and saved["s"]["turn"] == "w" and ",".join(x or "" for x in saved["s"]["b"]) == pos.replace("null",""), "a match saves itself after each move (white to move)")
    pg.reload(); pg.wait_for_function("window.__chess && __chess.G", timeout=10000); go(pg, 7); pg.wait_for_timeout(300)
    check(pg.is_visible("#chAsk button") and "saved game" in pg.text_content("#chSay"), f"reopening the match offers the saved game ({pg.text_content('#chSay')[:60]})")
    pg.screenshot(path=str(OUT / "chess-saved.png"))
    pg.click("#chAsk button.go"); pg.wait_for_timeout(300)
    check(pg.evaluate("__chess.G.s.b.join(',')") == pos and not pg.evaluate("__chess.G.busy") and "Welcome back" in pg.text_content("#chSay"), "Continue puts every piece back where it was")
    pg.evaluate("(()=>{const C=__chess,G=C.G;C.tryMove(C.bestMove(G.s,1))})()"); pg.wait_for_timeout(500); wait_idle(pg)
    check(pg.evaluate("__chess.G.s.b.join(',')") != pos, "and the game carries on")
    pg.evaluate("__chess.K.load(7)"); pg.wait_for_timeout(300); pg.click("#chAsk button:first-child"); pg.wait_for_timeout(300)
    check(pg.evaluate("__chess.G.hist.length") == 0 and not pg.evaluate("__chess.K.save.game"), "New game starts fresh and clears the save")
    pg.evaluate("window.__chessFast=false")
    ctx.close()
    # phone layout
    ctx = b.new_context(viewport={"width": 390, "height": 844}); ctx.add_init_script(player(3, "c3"))
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("chess")); pg.wait_for_function("window.__chess && __chess.G", timeout=10000)
    pg.evaluate("__chess.K.save.all=true"); go(pg, 7); wait_idle(pg)
    box = pg.evaluate("(()=>{const r=document.getElementById('chCv').getBoundingClientRect();return[r.left,r.right,r.width]})()")
    check(box[0] >= 0 and box[1] <= 390 and box[2] >= 300, f"the board fits a phone screen ({box})")
    pg.screenshot(path=str(OUT / "chess-phone.png"))
    ctx.close()
    check(not errors, f"no page errors {errors[:3]}")
sys.exit(check.finish())
