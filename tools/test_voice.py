"""The games' voice: cloud clips from /api/tts (faked here with shared/horn.mp3), device clip cache, and falling back to the device voice.
   python3 tools/test_voice.py"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright
from tsutil import *

check = Checker(); errors = []
MP3 = (pathlib.Path(__file__).resolve().parent.parent / "shared" / "horn.mp3").read_bytes()
init = ("localStorage.setItem('tilesolve:players',JSON.stringify({list:[{id:'v',name:'Kid',avatar:'🐯',grade:1,color:'#3b6fd9'}],current:'v',music:true}));"
        f"localStorage.setItem('tilesolve:p:v:seen',{json.dumps(SEEN)});"
        # watch the device voice and the sounds started
        "window.__dev=[];window.__plays=0;addEventListener('DOMContentLoaded',()=>{try{const o=speechSynthesis.speak.bind(speechSynthesis);speechSynthesis.speak=u=>{__dev.push(u.text);};}catch(e){}"
        "const C=window.AudioContext||window.webkitAudioContext;const st=AudioBufferSourceNode.prototype.start;AudioBufferSourceNode.prototype.start=function(){if(this.buffer&&this.buffer.length>1)__plays++;return st.apply(this,arguments)}});")
REQ = []; MODE = {"v": "ok"}
def tts(route):
    REQ.append(route.request.url)
    if MODE["v"] == "ok": route.fulfill(status=200, content_type="audio/mpeg", body=MP3)
    else: route.fulfill(status=429, content_type="application/json", body='{"ok":false}')
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(); ctx.add_init_script(init); ctx.route("**/api/tts*", tts)
    pg = watch_errors(ctx.new_page(), errors); pg.goto(URL("count")); pg.wait_for_function("window.__learn && __learn.R", timeout=10000)
    pg.mouse.click(5, 5); pg.wait_for_timeout(1500); REQ.clear()
    check(pg.evaluate("TS.talk.voice") == "cloud", "the cloud voice is the default")
    pg.evaluate("TS.say('Count by 2s and pay $1.05!')"); pg.wait_for_timeout(1200)
    check(len(REQ) == 1 and "count%20by%20twos" in REQ[0].lower().replace("+", "%20") and "1%20dollar%20and%205%20cents" in REQ[0], f"a line is fetched from /api/tts, already tidied for speaking ({REQ[-1][-70:] if REQ else None})")
    check(pg.evaluate("__plays") >= 1 and pg.evaluate("__dev.length") == 0, "the cloud clip plays (not the device voice)")
    n = len(REQ); pg.evaluate("TS.say('Count by 2s and pay $1.05!')"); pg.wait_for_timeout(600)
    check(len(REQ) == n and pg.evaluate("__plays") >= 2, "saying it again plays from the device, no new request")
    pg.reload(); pg.wait_for_function("window.__learn && __learn.R", timeout=10000); pg.mouse.click(5, 5); pg.wait_for_timeout(800); REQ.clear()
    pg.evaluate("TS.say('Count by 2s and pay $1.05!')"); pg.wait_for_timeout(800)
    check(len(REQ) == 0, "after a reload the clip comes from the device's clip cache")
    MODE["v"] = "limit"
    pg.evaluate("TS.say('A brand new line')"); pg.wait_for_timeout(1000)
    check(pg.evaluate("__dev") == ["A brand new line"], f"when the cloud can't help (daily limit), the device voice says it ({pg.evaluate('__dev')})")
    for t in ("Two", "Three"): pg.evaluate(f"TS.say('{t}')"); pg.wait_for_timeout(500)
    n = len(REQ); pg.evaluate("TS.say('Four')"); pg.wait_for_timeout(400)
    check(len(REQ) == n and "Four" in pg.evaluate("__dev"), "after 3 misses the cloud voice rests (no waiting), the device voice carries on")
    pg.evaluate("TS.talk.setVoice(TS.talk.voices().find(v=>v.uri!=='cloud')?.uri||'x-device')"); MODE["v"] = "ok"; n = len(REQ)
    pg.evaluate("TS.say('Device please')"); pg.wait_for_timeout(500)
    check(len(REQ) == n and pg.evaluate("TS.talk.voice") != "cloud", "a parent can pick a device voice instead")
    pg.evaluate("TS.talk.setVoice('cloud')"); check(pg.evaluate("TS.talk.voice") == "cloud", "and switch back to the Tile Solve voice")
    # the little app asks its own path's /api
    pg.goto(f"{BASE}/little/games/count/index.html"); pg.wait_for_timeout(800); pg.mouse.click(5, 5); pg.wait_for_timeout(300); REQ.clear()
    pg.evaluate("TS.say('Hello little learner')"); pg.wait_for_timeout(800)
    check(REQ and "/little/api/tts" in REQ[0], f"inside /little/, the voice asks /little/api/tts ({REQ[:1]})")
    b.close()
check(not errors, f"no page errors {errors[:3]}")
check.finish()
