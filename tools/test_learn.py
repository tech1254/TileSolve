"""Browser tests for the Little learners (K-2) games and Kindergarten support.  python3 tools/test_learn.py [screenshot_dir]"""
import sys, json, re, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
check = Checker(); errors = []
LEARN = ["trains", "abc", "syllables", "blend", "missletter", "case", "sound", "trace", "count", "numorder", "moreless", "missnum", "tenframe", "shapesort", "shapehunt", "colours", "sizeorder", "position", "shapes3d", "quicklook", "hidebugs", "dotmatch", "counton", "animals", "senses", "seasons"]

def player(grade, pid="kk"):
    seen = json.dumps({g: 1 for g in LEARN + GAMES})
    return (f"localStorage.setItem('tilesolve:players',JSON.stringify({{list:[{{id:'{pid}',name:'Kid',avatar:'🐸',grade:{grade},color:'#43a047'}}],current:'{pid}',music:true}}));"
            f"localStorage.setItem('tilesolve:p:{pid}:seen',{json.dumps(seen)})")

VALIDATE = """(()=>{const bad=[],TR=TS_LEARN.TRACE;let rounds=0;
  for(const a of [-1,0,1,2,3])for(let n=1;n<=40;n++){const r=TS.rngFrom(n*977+a*31+7);for(let i=0;i<6;i++){let R;
    try{R=__learn.make(n,i,r,a)}catch(e){bad.push(a+':'+n+':'+i+' threw '+e.message);continue}rounds++;const id=a+':'+n+':'+i+' '+R.type;
    if(!R.say)bad.push(id+' no say');
    if(R.type==='pick'){const ks=R.options.map(o=>o.key);if(new Set(ks).size!==ks.length)bad.push(id+' dup options '+ks);if(!ks.includes(R.answer))bad.push(id+' answer missing');if(ks.length<2)bad.push(id+' too few')}
    else if(R.type==='order'){const keys=R.tiles.map(t=>t.key),ks=R.tiles.map(t=>String(t.val!==undefined?t.val:t.key));if(new Set(keys).size!==keys.length)bad.push(id+' dup tiles');
      if(ks.slice().sort().join()!==R.answer.map(String).sort().join())bad.push(id+' answer not tiles');
      if(ks.length>1&&ks.join()===R.answer.map(String).join())bad.push(id+' already in order')}
    else if(R.type==='sort'){const bk=R.bins.map(b=>b.key);if(R.items.some(x=>!bk.includes(x.key)))bad.push(id+' item without bin');if(R.items.length<2)bad.push(id+' few items')}
    else if(R.type==='hunt'){if(!R.cells.some(c=>c.ok))bad.push(id+' nothing to find');if(R.cells.every(c=>c.ok))bad.push(id+' all targets')}
    else if(R.type==='fill'){if(!(R.target>=1&&R.target<=(R.size||10)))bad.push(id+' bad target')}
    else if(R.type==='trace'){if(!TR[R.ch])bad.push(id+' no strokes for '+R.ch)}
    else if(R.type==='meet'){if(!R.up||!R.pic||!R.word)bad.push(id+' meet missing letter/picture')}
    else if(R.type==='sing'){if(!R.letters.length||R.letters.length!==R.notes.length||R.notes.some(m=>!(m>=48&&m<=84)))bad.push(id+' bad song')}
    else bad.push(id+' unknown type')}}
  return{bad:bad.slice(0,8),n:bad.length,rounds}})()"""

def win_level(pg, limit=40):
    for _ in range(limit):
        if pg.is_visible("#kSheetWin"): return True
        pg.evaluate("__learn.R && !__learn.R.done && __learn.solve()"); pg.wait_for_timeout(1000)
    return pg.is_visible("#kSheetWin")

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2); ctx.add_init_script(player(0))
    for g in LEARN:
        pg = watch_errors(ctx.new_page(), errors); pg.goto(URL(g)); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
        v = pg.evaluate(VALIDATE)
        check(v["n"] == 0, f"{g}: all {v['rounds']} rounds (pre-K to grade 3 content, 40 levels) are well formed {v['bad']}")
        pg.screenshot(path=str(OUT / f"learn-{g}.png"))
        shown = pg.evaluate("({p:document.getElementById('lrPrompt').textContent.trim().length,d:document.querySelectorAll('#lrDots i').length,t:document.getElementById('kTip').textContent.length})")
        check(shown["p"] > 0 and shown["d"] >= 3 and shown["t"] > 0, f"{g}: question, progress dots and tip are shown {shown}")
        R = pg.evaluate("({type:__learn.R.type,options:(__learn.R.options||[]).map(o=>o.key),answer:__learn.R.answer})")
        if R["type"] == "pick":
            wrong = next(k for k in R["options"] if k != R["answer"])
            pg.click(f".lr-opt[data-key='{wrong}']"); pg.wait_for_timeout(150)
            check("Oops 1" in pg.text_content("#kSub"), f"{g}: a wrong answer counts an oops")
        check(win_level(pg), f"{g}: playing every round wins the level")
        pg.close()

    # Support after mistakes (research): say what was picked, take away a wrong choice, then show the answer; missed rounds come back
    sctx = b.new_context(viewport={"width": 390, "height": 844}); sctx.add_init_script(player(1, "sp"))
    pg = watch_errors(sctx.new_page(), errors)
    pg.add_init_script("window.__said=[];const S=window.speechSynthesis;if(S){S.speak=u=>window.__said.push(u.text);S.cancel=()=>{}}")
    pg.goto(URL("moreless")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000); pg.mouse.click(5, 5); pg.wait_for_timeout(200)
    for _ in range(6):
        if pg.evaluate("__learn.R.type==='pick'&&__learn.R.options.length>=3"): break
        pg.evaluate("__learn.solve()"); pg.wait_for_timeout(1000)
    keys = pg.evaluate("__learn.R.options.map(o=>o.key)"); ans = pg.evaluate("__learn.R.answer"); wrong = [k for k in keys if k != ans]
    i0 = pg.evaluate("__learn.S.i")
    tapk = lambda k: pg.evaluate(f"document.querySelector(\".lr-opt[data-key='{k}']\").click()")
    tapk(wrong[0]); pg.wait_for_timeout(200)
    check(pg.locator(f".lr-opt[data-key='{wrong[0]}']").is_disabled(), "a wrong pick is greyed out so it can't be picked again")
    tapk(wrong[1]); pg.wait_for_timeout(200)
    check(pg.locator(".lr-opt[disabled]").count() == (3 if len(keys) >= 5 else 2), f"a second mistake takes away another wrong choice when 2+ are left ({len(keys)} choices)")
    tapk(ans); pg.wait_for_timeout(1100)
    due = pg.evaluate("__learn.S.retry.map(x=>x.due)")
    check(due == [i0 + 3], f"the missed round is queued to come back 3 rounds later ({due})")
    check(pg.evaluate("__learn.S.adj") < 0, "two mistakes in a round makes the next rounds a little easier")
    pg.close(); sctx.close()

    # Reading research rules
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("trace")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    tr = pg.evaluate("(()=>{const out=[];for(let n=1;n<=26;n++){const r=TS.rngFrom(n);out.push([0,1,2].map(i=>{const R=__learn.make(n,i,r,-1);return R.ch+':'+R.mode}))}return out})()")
    check(all(len({x.split(':')[0] for x in lv}) == 1 and [x.split(':')[1] for x in lv] == ["guided", "fade", "memory"] for lv in tr),
          f"Trace: one letter per level (never b and d together): watch + trace, faded line, then from memory ({tr[0]})")
    pg.goto(URL("sound")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    bad = pg.evaluate("(()=>{const bad=[];for(let n=1;n<=40;n++){const r=TS.rngFrom(n);for(let i=0;i<4;i++){for(const a of[-1,0]){const R=__learn.make(n,i,r,a);const w=String(R.say).split('.')[0].toLowerCase();if(!/^[a-z][aeiouy]/.test(w))bad.push(w)}}}return bad})()")
    check(not bad, f"First Sound: no blends or tricky first sounds for pre-K and K content {bad[:5]}")
    pg.goto(URL("blend")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    parts = pg.evaluate("[-1,0,1,2].map(a=>__learn.make(5,0,TS.rngFrom(a+9),a).prompt.replace(/<[^>]+>/g,'|').split('|').filter(Boolean).pop())")
    check(" · " in parts[0] and len(parts[1].split(" · ")) == 2 and len(parts[2].split(" · ")) == 3, f"Robot Talk: word parts, then onset-rime, then every sound ({parts})")

    # Shapes and space research rules
    pg.goto(URL("shapehunt")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    sh = pg.evaluate("""(()=>{let near=0,whys=0,forms=new Set();for(let n=1;n<=40;n++){const r=TS.rngFrom(n);for(let i=0;i<5;i++){const R=__learn.make(n,i,r,0);
      if(/almost/.test(R.say)){near++;if(R.cells.some(c=>!c.ok&&/^not a|^an oval|^a rectangle|^a square/.test(c.why||"")))whys++}
      if(/triangles/.test(R.say))R.cells.filter(c=>c.ok).forEach(c=>forms.add(c.html.replace(/.*<polygon points="([^"]+)".*/,"$1")))}}return{near,whys,forms:forms.size}})()""")
    check(sh["near"] >= 5 and sh["whys"] == sh["near"] and sh["forms"] >= 3, f"Shape Hunt: many kinds of triangles, plus 'almost' shapes that explain why they're not ({sh})")
    pg.goto(URL("shapesort")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    ss = pg.evaluate("(()=>{let t=0,s='';for(let n=1;n<=40;n++){const r=TS.rngFrom(n);for(let a=-1;a<=2;a++){const R=__learn.make(n,0,r,a);s+=R.say+JSON.stringify(R.bins.map(b=>b.label))+R.items.map(x=>x.aria).join()}}return /diamond/i.test(s)})()")
    check(not ss, "Shape Sort never calls a shape a diamond")
    pg.goto(URL("colours")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    cc = pg.evaluate("(()=>{const c={};for(let n=1;n<=60;n++){const r=TS.rngFrom(n);const R=__learn.make(n,0,r,1);if(R.type==='pick')c[R.answer]=(c[R.answer]||0)+1}return c})()")
    late = sum(cc.get(k, 0) for k in ("brown", "grey", "pink", "purple")) / 4; early = sum(cc.get(k, 0) for k in ("red", "blue", "green", "yellow", "orange")) / 5
    check(late > early, f"Colour Match: brown, grey, pink and purple come up more often ({cc})")
    pg.goto(URL("position")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    pw = pg.evaluate("[-1,0,1].map(a=>{const s=new Set();for(let n=1;n<=30;n++){const R=__learn.make(n,0,TS.rngFrom(n),a);R.options.forEach(o=>s.add(o.key))}return[...s].sort()})")
    check(pw[0] == ["in", "on", "under"] and "between" not in pw[1] and "between" in pw[2], f"Where's the Cat: in/on/under first, then next to/behind/in front of, then between ({pw})")
    # Number and science research rules (batch 4)
    pg.goto(URL("quicklook")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    ql = pg.evaluate("[-1,0,1,2].map(a=>{const v=[];for(let n=1;n<=30;n++){const R=__learn.make(n,n%5,TS.rngFrom(n),a);v.push(R.answer);if(!R.flash||!/lr-flash/.test(R.prompt))return 'no flash'}return[Math.min(...v),Math.max(...v)]})")
    check(ql == [[1, 5], [1, 7], [6, 10], [10, 20]], f"Quick Look: dots flash briefly; pre-K 1-5, K to 7, grade 1 6-10, grade 2 10-20 ({ql})")
    pg.wait_for_timeout(2300)
    check(pg.evaluate("document.querySelector('#lrPrompt .lr-flash').classList.contains('hid')") and pg.is_visible(".lr-again"), "the dots hide after a moment and 👀 Look again shows them once more")
    pg.goto(URL("hidebugs")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    hb = pg.evaluate("[-1,0,1,2].map(a=>{let ok=true;for(let n=1;n<=30;n++){const R=__learn.make(n,0,TS.rngFrom(n),a);if(!R.options.some(o=>o.key===R.answer))ok=false}return ok})")
    check(all(hb), "Hiding Bugs: the hidden number is always one of the choices")
    pg.goto(URL("counton")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    co = pg.evaluate("(()=>{const R=__learn.make(5,0,TS.rngFrom(3),0);return R.options.find(o=>o.key===R.answer).say})()")
    check("…" in co, f"Count On: the answer is counted on out loud ({co})")
    pg.goto(URL("animals")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    an = pg.evaluate("""[-1,0,1,2].map(a=>{const ks=new Set();let bad=0;for(let n=1;n<=12;n++)for(let i=0;i<5;i++){const R=__learn.make(n,i,TS.rngFrom(n*7+i),a);
      ks.add(R.type==='sort'?R.bins.map(b=>b.key).sort().join('/'):R.type+':'+R.prompt.replace(/<[^>]+>/g,'').split(' ').slice(0,3).join(' '));
      if(R.type==='sort'&&(R.items.length>6||R.bins.length>4||R.items.some(x=>!R.bins.some(b=>b.key===x.key))))bad++}return{n:ks.size,ks:[...ks],bad}})""")
    check(all(x["bad"] == 0 for x in an), "Animal Sort: at most 6 cards and 4 homes, and every card has a home")
    check("fly/walk" in an[0]["ks"] and not any("mammal" in k for k in an[0]["ks"]) and an[0]["n"] >= 4, f"Animal Sort pre-K: fly or walk, sounds, babies, wings; no 'mammal' words ({an[0]['ks']})")
    check(any("Why is" in k for k in an[1]["ks"]) and "no/yes" in an[1]["ks"], f"Animal Sort K: why animals move and alive / not alive ({an[1]['ks']})")
    check("away/sleep/stay" in an[2]["ks"] and any(k.count("/") == 3 and "both" in k for k in an[2]["ks"]), f"Animal Sort grade 1: Alberta winter and fly/swim 'both' rounds ({an[2]['ks']})")
    check(any(k.startswith("order") for k in an[3]["ks"]), f"Animal Sort grade 2: life cycles ({an[3]['ks']})")
    tr = pg.evaluate("(()=>{for(let n=1;n<=60;n++)for(let i=0;i<5;i++){const R=__learn.make(n,i,TS.rngFrom(n+i),1);if(R.type==='sort'){const w=R.items.find(x=>x.aria==='whale'&&x.why);if(w)return w.why}}return ''})()")
    check("mammal" in tr, f"tricky animals explain themselves ({tr[:60]})")
    pg.goto(URL("shapes3d")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    s3 = pg.evaluate("[-1,1].map(a=>{const t=new Set();for(let i=0;i<6;i++){const R=__learn.make(4,i,TS.rngFrom(i),a);t.add(R.type+(R.type==='sort'?R.bins.length:''))}return[...t].sort()})")
    check("sort2" in s3[0] and "hunt" in s3[1] and "sort4" in s3[1], f"3D Shapes: ball and box shapes first, then four solids and 'what rolls?' ({s3})")
    pg.close()

    # My ABCs: the child's name letters first, a new letter each level, many kinds of rounds, ending with the song
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("abc")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    seq = pg.evaluate("Array.from({length:26},(_,k)=>__learn.K&&1).length") and pg.evaluate("(()=>{const out=[];for(let n=1;n<=26;n++){const R=__learn.make(n,0,TS.rngFrom(n),-1);out.push(R.up)}return out})()")
    check(seq[:2] == ["K", "I"] and sorted(seq) == sorted("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), f"levels 1-26 teach every letter once, the player's name (Kid) first: {''.join(seq)}")
    kinds = pg.evaluate("(()=>{const ks=new Set(),per=[];for(let n=1;n<=26;n++){const r=TS.rngFrom(n*3),t=[];for(let i=0;i<6;i++){const R=__learn.make(n,i,r,-1);t.push(R.type==='pick'?R.prompt.replace(/<[^>]+>/g,'').split(' ').slice(0,2).join(' '):R.type);ks.add(t[i])}per.push(t)}return{ks:[...ks],first:per.map(t=>t[0]),last:per.map(t=>t[5]),distinct:new Set(per.map(t=>t.join())).size}})()")
    check(set(kinds["first"]) == {"meet"} and set(kinds["last"]) == {"sing"} and len(kinds["ks"]) >= 6 and kinds["distinct"] >= 12,
          f"every level starts by meeting the letter and ends with the ABC song, with varied rounds between ({len(kinds['ks'])} kinds, {kinds['distinct']} different level plans)")
    pg.screenshot(path=str(OUT / "abc-meet.png"))
    pg.close()

    # A level for each grade plays through
    for grade in (1, 2):
        c = b.new_context(viewport={"width": 390, "height": 844}); c.add_init_script(player(grade, f"g{grade}"))
        for g in ["abc", "count", "shapesort", "tenframe", "trace"]:
            pg = watch_errors(c.new_page(), errors); pg.goto(URL(g)); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
            check(win_level(pg), f"grade {grade} {g}: level 1 can be won"); pg.close()
        c.close()

    # Maths questions match the PREVIOUS grade's Alberta outcomes
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("count")); pg.wait_for_timeout(300)
    res = pg.evaluate("""(()=>{const out={};const num=x=>typeof x==='number'?x:parseFloat(x);
      const rules={'-1':q=>q.slot==='n',0:q=>q.slot!=='n'&&!/[×÷%]/.test(q.op)&&Math.max(num(q.a),num(q.b||0),num(q.c||0),q.ans)<=10,
        1:q=>!/[×÷%]/.test(q.op)&&Math.max(num(q.a),num(q.b||0),num(q.c||0),q.ans)<=20,
        2:q=>!/[×÷%]/.test(q.op)&&Math.max(num(q.a),num(q.b||0),num(q.c||0),q.ans)<=100,
        3:q=>(q.op==='×'?num(q.a)<=10&&num(q.b)<=10:q.op==='÷'?num(q.b)<=10&&q.ans<=10:true)&&Math.max(num(q.a),num(q.b||0),num(q.c||0),q.ans)<=1000,
        4:q=>(q.op==='÷'?num(q.b)<=12&&q.ans<=12:true)&&Math.max(num(q.a),num(q.b||0),num(q.c||0),q.ans)<=10000};
      for(const L of [-1,0,1,2,3,4])for(const easy of [false,true]){let bad=0,ex='';for(let k=0;k<3000;k++){const q=TS.problem(L,easy);
        if(easy&&L===-1&&q.n>5)bad++;else if(!easy&&L===-1&&q.n>8)bad++;else if(!rules[L](q)){bad++;ex=JSON.stringify(q)}}out[L+(easy?' checkpoint':' hint')]=[bad,ex]}
      return out})()""")
    for k, (bad, ex) in res.items():
        check(bad == 0, f"Alberta maths for content grade {k}: 3000 questions in range {ex}")
    pg.close()

    # Hints, pointer, talking
    pg = watch_errors(ctx.new_page(), errors)
    pg.add_init_script("window.__said=[];const S=window.speechSynthesis;if(S){S.speak=u=>window.__said.push(u.text);S.cancel=()=>{}}")
    pg.goto(URL("count")); pg.wait_for_timeout(500)
    pg.mouse.click(5, 5); pg.wait_for_timeout(300)
    check(any("How many" in s for s in pg.evaluate("window.__said")), "questions are read aloud after the first touch")
    pg.click("#lrSay"); pg.wait_for_timeout(100)
    check(len(pg.evaluate("window.__said")) >= 2, "🔊 reads the question again")
    pg.click("#kHint"); pg.wait_for_timeout(300)
    t = pg.inner_text(".prob")
    check("?" in t and len(re.findall(r"\d", t)) == 0, f"Kindergarten hint question is counting pictures ({t.strip()[:30]})")
    cnt = pg.locator(".ts-count span").count()
    opts = pg.evaluate("[...document.querySelectorAll('.ts-pick button')].map(b=>+b.dataset.v)")
    check(not pg.is_visible(".keys") and len(opts) == 3 and cnt in opts, f"pre-K: no keypad, three number buttons to pick from {opts}")
    check(pg.locator(f".ts-pick button[data-v='{cnt}'] .ts-dots i").count() == cnt and pg.text_content(f".ts-pick button[data-v='{cnt}'] b") == str(cnt), "each button shows the numeral and that many dots")
    wrong = next(v for v in opts if v != cnt)
    n0 = len(pg.evaluate("window.__said"))
    pg.click(f".ts-pick button[data-v='{wrong}']"); pg.wait_for_timeout(700 + cnt * 520 + 900)
    said = pg.evaluate("window.__said")[n0:]
    check(said and said[0] in ("one","two","three","four","five","six","seven","eight","nine","ten") and any(", " in x or x.startswith("1") for x in said), f"tapping a number says it, and a wrong one counts along ({said[:2]})")
    check(pg.locator(f".ts-pick button[data-v='{wrong}']").is_disabled() and pg.evaluate("TS.math.isOpen"), "the wrong number is greyed out and he can try again")
    pg.screenshot(path=str(OUT / "prek-count.png"))
    pg.click(f".ts-pick button[data-v='{cnt}']"); pg.wait_for_timeout(cnt * 520 + 1100)
    check(pg.locator(".lr-hint").count() >= 1, "the right number (after counting along) unlocks a hint that highlights the answer")
    pg.click("#kLevels")
    check(pg.locator("#lrTalk").is_checked(), "Read things out loud is on by default")
    pg.click("#lrTalk"); pg.click("#kCloseLevels")
    check(pg.evaluate("JSON.parse(localStorage.getItem('tilesolve:players')).talk") is False, "talking can be turned off")
    pg.close()

    # ---------- iPad touch ----------
    tctx = b.new_context(**p.devices["iPad Mini"]); tctx.add_init_script(player(0))
    tp = watch_errors(tctx.new_page(), errors)
    tp.goto(URL("count")); tp.wait_for_timeout(400)
    tap_center(tp, f".lr-opt[data-key='{tp.evaluate('__learn.R.answer')}']"); tp.wait_for_timeout(200)
    check(tp.evaluate("__learn.S.i") == 1 or tp.evaluate("__learn.R.done"), "touch: tapping the right answer finishes the round")
    tp.goto(URL("abc")); tp.wait_for_timeout(400)
    tap_center(tp, ".lr-meet"); tp.wait_for_timeout(2700)
    check(tp.evaluate("__learn.S.i") == 1, "touch: tapping the big letter card meets the letter")
    for _ in range(4):
        if tp.evaluate("__learn.R.type") == "sing": break
        tp.evaluate("__learn.solve()"); tp.wait_for_timeout(1000)
    n = tp.evaluate("__learn.R.letters.length")
    for k in range(n): tap_center(tp, ".lr-sl.glow"); tp.wait_for_timeout(60)
    tp.wait_for_timeout(700)
    check(tp.evaluate("__learn.S.i") == 6 or tp.is_visible("#kSheetWin"), f"touch: singing the ABCs by tapping the glowing letters ({n} letters)")
    tp.goto(URL("shapesort")); tp.wait_for_timeout(400)
    left0 = tp.evaluate("__learn.R.left")
    item = tp.locator(".lr-tray .lr-item").first; key = tp.evaluate("__learn.R.items[+document.querySelector('.lr-tray .lr-item').dataset.k].key")
    a = item.bounding_box(); z = tp.locator(f".lr-bin[data-bin='{key}']").bounding_box()
    touch_drag(tp, a["x"]+a["width"]/2, a["y"]+a["height"]/2, z["x"]+z["width"]/2, z["y"]+z["height"]/2, 12)
    check(tp.evaluate("__learn.R.left") == left0 - 1, "touch: dragging a shape into its home")
    key = tp.evaluate("__learn.R.items[+document.querySelector('.lr-tray .lr-item').dataset.k].key")
    tap_center(tp, ".lr-tray .lr-item >> nth=0"); tap_center(tp, f".lr-bin[data-bin='{key}']")
    check(tp.evaluate("__learn.R.left") == left0 - 2, "touch: tap a shape, then tap its home")
    tp.screenshot(path=str(OUT / "learn-ipad-sort.png"))
    tp.goto(URL("trace")); tp.wait_for_timeout(400)
    ch = tp.evaluate("__learn.R.ch")
    strokes = tp.evaluate("__learn.R.strokes")
    box = tp.locator(".lr-tsvg").bounding_box()
    to = lambda q: (box["x"] + q[0]/100*box["width"], box["y"] + q[1]/100*box["height"])
    cdp = tctx.new_cdp_session(tp)
    for st in strokes:
        x, y = to(st[0]); cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x, "y": y}]})
        for q in st[1::2] + [st[-1]]:
            x, y = to(q); cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x, "y": y}]})
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}); tp.wait_for_timeout(120)
    tp.wait_for_timeout(300)
    check(tp.evaluate("__learn.R.done") or tp.evaluate("__learn.S.i") == 1, f"touch: tracing the letter {ch} with a finger completes it")
    tp.goto(URL("tenframe")); tp.wait_for_timeout(400)
    t = tp.evaluate("__learn.R.target")
    for k in range(t): tap_center(tp, f".lr-fc[data-i='{k}']")
    tp.wait_for_timeout(800)
    check(tp.evaluate("__learn.S.i") == 1, "touch: filling the ten frame finishes the round")
    tctx.close()

    # ---------- lowercase letters really look lowercase; voice chooser; grade filter ----------
    c3 = b.new_context(viewport={"width": 390, "height": 844}); c3.add_init_script(player(3, "g3"))
    c3.add_init_script("window.__said=[];const S=window.speechSynthesis;if(S){S.speak=u=>window.__said.push(u.text);S.cancel=()=>{}}")
    pg = watch_errors(c3.new_page(), errors); pg.goto(URL("case")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    fam = pg.evaluate("getComputedStyle(document.querySelector('.lr-opt')).fontFamily")
    texts = pg.evaluate("[...document.querySelectorAll('.lr-opt'),document.querySelector('.lr-prompt .big')].map(e=>e.textContent)")
    check("Andika" in fam and "Bungee" not in fam, f"letter tiles use a font with real lowercase ({fam.split(',')[0]})")
    check(any(t.islower() for t in texts) and any(t.isupper() for t in texts), f"Big & Little shows both big and little letters {texts}")
    pg.screenshot(path=str(OUT / "learn-case-font.png"))
    pg.click("#kLevels")
    check(pg.locator("#lrVoice").is_visible() and pg.locator("#lrTest").is_visible(), "Levels menu has a voice chooser and Test button")
    pg.click("#lrTest"); pg.wait_for_timeout(100)
    check(any("read the questions" in x for x in pg.evaluate("window.__said")), "Test reads a sample sentence")
    pg.close(); c3.close()
    # Little learners moved to the Little Learners app (tools/test_little.py); the main app no longer lists them
    for grade, shows in ((3, False), (4, False), (7, False)):
        cg = b.new_context(viewport={"width": 390, "height": 844}); cg.add_init_script(player(grade, f"h{grade}"))
        hp = watch_errors(cg.new_page(), errors); hp.goto(HOME_URL); hp.wait_for_timeout(300)
        n = hp.locator(".games[data-group='little'] .game").count()
        check((n == 15) == shows and hp.locator(".games[data-group='puzzles'] .game").count() == 18,
              f"grade {grade}: Little learners {'shown' if shows else 'hidden'} ({n}), puzzles shown")
        cg.close()

    hc = b.new_context(viewport={"width": 390, "height": 844})
    hp = watch_errors(hc.new_page(), errors); hp.goto(HOME_URL); hp.wait_for_timeout(300)
    hp.fill("#fName", "Lily"); hp.click("#fGrades button:nth-child(1)"); hp.click("#formSave"); hp.wait_for_timeout(300)
    check(hp.evaluate("JSON.parse(localStorage.getItem('tilesolve:players')).list[0].grade") == 0, "Kindergarten can be picked for a player")
    heads = hp.locator(".gsec h2").all_text_contents()
    check(not any(h.startswith("Little learners") for h in heads) and hp.locator(".games[data-group='little'] .game").count() == 0, "the main app no longer lists Little learners (they're in the Little Learners app)")
    hp.screenshot(path=str(OUT / "home-little.png"), full_page=True)
    hp.click("#btnMe"); hp.click("#btnEdit")
    check("Kindergarten" in hp.text_content(".player"), "player card says Kindergarten")
    hp.click("#btnDone"); hp.click(".player:has-text('Lily')"); hp.wait_for_timeout(200)
    hp.goto(URL("car")); hp.wait_for_timeout(500)
    if hp.locator(".ts-howto").is_visible(): hp.click(".ts-howto .bigbtn")
    check(hp.text_content("#par") == str(hp.evaluate("window.__tilesolve.getLevel(1,1).par")), "Unblock the Car gives a Kindergarten player grade 1 puzzles")
    hc.close()

    check(not errors, "no JavaScript errors" + ("" if not errors else ": " + "; ".join(errors[:3])))
    b.close()
sys.exit(check.finish())
