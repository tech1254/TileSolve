/* Tile Solve / Little Learners backend: the static pages are served as before (env.ASSETS); this Worker only adds
     POST /api/events   a batch of play and maths records from a device (queued on the device, sent in batches)
     GET  /api/report   totals for the /report page, to tune difficulty
     GET  /api/sync?fam=CODE         all of a family's saved progress (cloud sync between devices)
     POST /api/sync {fam, items}     merge changed saves: for each key the newer time wins; returns everything newer than "since"
     GET  /api/tts?t=   the games' voice: text to speech with Workers AI (MeloTTS), cached at the edge and on the device.
                        New clips are capped per day (TTS_CAP) so this never uses much of the account's shared AI allowance;
                        over the cap (or on any error) the games fall back to the device's own voice.
   Data goes into the D1 database "tilesolve-reports" (tables in tools/schema.sql). No names are stored:
   a player is a random id plus their buddy emoji and grade. If a REPORT_KEY variable is set, /api/report needs ?key=. */
const S = (v, n) => (v == null ? null : String(v).slice(0, n));
const I = (v, lo, hi) => { v = Math.round(+v); return Number.isFinite(v) ? Math.max(lo, Math.min(hi, v)) : null; };
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });

export async function events(req, env) {
  let b;
  try { b = await req.json(); } catch (e) { return json({ ok: false, error: "bad json" }, 400); }
  if (!b || !Array.isArray(b.events)) return json({ ok: false, error: "no events" }, 400);
  const app = S(b.app, 12), device = S(b.device, 24), player = S(b.player, 24), avatar = S(b.avatar, 16), grade = I(b.grade, 0, 7);
  const now = Date.now(), stmts = [];
  for (const e of b.events.slice(0, 200)) {
    const ts = I(e.ts, now - 90 * 864e5, now + 864e5) || now, who = [app, device, S(e.player, 24) || player, S(e.avatar, 16) || avatar, e.grade != null ? I(e.grade, 0, 7) : grade];
    if (e.t === "play" && e.game)
      stmts.push(env.DB.prepare("INSERT OR IGNORE INTO plays (eid,ts,app,device,player,avatar,grade,game,level,result,stars,ms,oops,hints) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
        .bind(S(e.id, 40), ts, ...who, S(e.game, 24), I(e.level, 0, 1000), ["win", "fail", "quit"].includes(e.result) ? e.result : "quit", I(e.stars, 0, 3), I(e.ms, 0, 36e5), I(e.oops, 0, 999), I(e.hints, 0, 99)));
    else if (e.t === "math")
      stmts.push(env.DB.prepare("INSERT OR IGNORE INTO maths (eid,ts,app,device,player,avatar,grade,game,kind,mlevel,q,correct,tries,ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
        .bind(S(e.id, 40), ts, ...who, S(e.game, 24), ["check", "mission"].includes(e.kind) ? e.kind : "hint", I(e.mlevel, -1, 9), S(e.q, 40), e.correct ? 1 : 0, I(e.tries, 0, 9), I(e.ms, 0, 36e5)));
  }
  if (stmts.length) await env.DB.batch(stmts);
  return json({ ok: true, saved: stmts.length });
}

const TTS_MODEL = "@cf/myshell-ai/melotts", TTS_CAP = 2000; // new clips per day, both apps together (~15-20% of the free allowance)
let ttsTable = false;
export async function tts(url, env, ctx) {
  const t = (url.searchParams.get("t") || "").replace(/\s+/g, " ").trim().slice(0, 600);
  if (!t) return json({ ok: false, error: "no text" }, 400);
  if (!env.AI) return json({ ok: false, error: "no AI binding" }, 503);
  const key = new Request(url.origin + "/api/tts?v=1&t=" + encodeURIComponent(t)), cache = caches.default;
  const hit = await cache.match(key);
  if (hit) return hit;
  const day = new Date().toISOString().slice(0, 10);
  if (env.DB) {
    if (!ttsTable) { await env.DB.prepare("CREATE TABLE IF NOT EXISTS tts_usage (day TEXT PRIMARY KEY, n INTEGER NOT NULL DEFAULT 0, chars INTEGER NOT NULL DEFAULT 0)").run(); ttsTable = true; }
    const r = await env.DB.prepare("SELECT n FROM tts_usage WHERE day=?").bind(day).first();
    if (r && r.n >= TTS_CAP) return json({ ok: false, error: "daily voice limit reached" }, 429);
  }
  const out = await env.AI.run(TTS_MODEL, { prompt: t, lang: "en" });
  let body;
  if (out && typeof out === "object" && typeof out.audio === "string") body = Uint8Array.from(atob(out.audio), (c) => c.charCodeAt(0));
  else if (out instanceof ReadableStream) body = await new Response(out).arrayBuffer();
  else if (out instanceof ArrayBuffer || ArrayBuffer.isView(out)) body = out;
  else return json({ ok: false, error: "unexpected voice output" }, 502);
  const res = new Response(body, { headers: { "content-type": "audio/mpeg", "cache-control": "public, max-age=31536000, immutable" } });
  ctx.waitUntil(cache.put(key, res.clone()));
  if (env.DB) ctx.waitUntil(env.DB.prepare("INSERT INTO tts_usage (day,n,chars) VALUES (?,1,?) ON CONFLICT(day) DO UPDATE SET n=n+1, chars=chars+excluded.chars").bind(day, t.length).run());
  return res;
}

/* ---------- cloud sync ----------
   A family's saves live in the sync table, one row per localStorage key ("tilesolve:..."), with the time it was last changed
   on a device. The family code is the only key: 10 letters/digits (about 50 bits), made on a device and typed into the others.
   Deleted saves are kept as v=null so deletions reach the other devices. */
const FAM = /^[A-HJ-NP-Z2-9]{10}$/, MAXV = 300000, MAXKEYS = 3000;
let syncTable = false;
async function syncDB(env) {
  if (!syncTable) {
    await env.DB.prepare("CREATE TABLE IF NOT EXISTS sync (fam TEXT NOT NULL, k TEXT NOT NULL, v TEXT, t INTEGER NOT NULL, up INTEGER NOT NULL, PRIMARY KEY (fam, k))").run();
    syncTable = true;
  }
}
export async function sync(req, url, env) {
  if (!env.DB) return json({ ok: false, error: "no database" }, 503);
  await syncDB(env);
  let fam, items = {}, since = 0;
  if (req.method === "POST") {
    const body = await req.json().catch(() => null);
    if (!body) return json({ ok: false, error: "bad json" }, 400);
    fam = String(body.fam || ""); items = body.items && typeof body.items === "object" ? body.items : {}; since = Number(body.since) || 0;
  } else { fam = url.searchParams.get("fam") || ""; since = Number(url.searchParams.get("since")) || 0; }
  fam = fam.toUpperCase().replace(/[^A-Z0-9]/g, "");
  if (!FAM.test(fam)) return json({ ok: false, error: "bad family code" }, 400);
  const now = Date.now(), keys = Object.keys(items).filter((k) => k.startsWith("tilesolve:") && k.length < 200).slice(0, MAXKEYS);
  if (keys.length) {
    const have = await env.DB.prepare("SELECT COUNT(*) n FROM sync WHERE fam=?").bind(fam).first();
    if ((have?.n || 0) + keys.length > MAXKEYS * 2) return json({ ok: false, error: "too many saves" }, 413);
    const st = [];
    for (const k of keys) {
      const it = items[k] || {}, v = it.v == null ? null : String(it.v), t = Math.min(Number(it.t) || 0, now + 60000);
      if (v && v.length > MAXV) continue;
      // newer time wins; "up" is when the server got it, so other devices can ask for "everything since my last sync"
      st.push(env.DB.prepare("INSERT INTO sync (fam,k,v,t,up) VALUES (?,?,?,?,?) ON CONFLICT(fam,k) DO UPDATE SET v=excluded.v, t=excluded.t, up=excluded.up WHERE excluded.t > sync.t")
        .bind(fam, k, v, t, now));
    }
    for (let i = 0; i < st.length; i += 50) await env.DB.batch(st.slice(i, i + 50));
  }
  const rows = (await env.DB.prepare("SELECT k, v, t FROM sync WHERE fam=? AND up>=?").bind(fam, since).all()).results || [];
  // and the server's copy of every key just sent, in case the server already had a newer one
  for (let i = 0; i < keys.length; i += 90) {
    const part = keys.slice(i, i + 90);
    const r2 = await env.DB.prepare("SELECT k, v, t FROM sync WHERE fam=? AND k IN (" + part.map(() => "?").join(",") + ")").bind(fam, ...part).all();
    rows.push(...(r2.results || []));
  }
  const out = {};
  for (const r of rows) out[r.k] = { v: r.v, t: r.t };
  return json({ ok: true, now, items: out });
}

export async function report(url, env) {
  if (env.REPORT_KEY && url.searchParams.get("key") !== env.REPORT_KEY) return json({ ok: false, error: "key needed" }, 403);
  const days = I(url.searchParams.get("days") || 30, 1, 3650), since = Date.now() - days * 864e5;
  const player = url.searchParams.get("player") || "", app = url.searchParams.get("app") || "";
  const where = (t) => "WHERE " + t + ".ts>=?" + (player ? " AND " + t + ".player=?" : "") + (app ? " AND " + t + ".app=?" : "");
  const args = [since].concat(player ? [player] : [], app ? [app] : []);
  const q = (sql) => env.DB.prepare(sql).bind(...args).all().then((r) => r.results);
  const [levels, maths, misses, players, games] = await Promise.all([
    q(`SELECT game, grade, ((level-1)/5)*5+1 AS band, COUNT(*) AS n, SUM(result='win') AS wins, SUM(result='fail') AS fails, SUM(result='quit') AS quits,
        ROUND(AVG(CASE WHEN result='win' THEN stars END),2) AS stars, ROUND(AVG(CASE WHEN result='win' THEN ms END)) AS ms,
        ROUND(AVG(oops),2) AS oops, ROUND(AVG(hints>0),2) AS hinted, MAX(level) AS top
       FROM plays p ${where("p")} GROUP BY game, grade, band ORDER BY game, grade, band`),
    q(`SELECT grade, mlevel, kind, COUNT(*) AS n, ROUND(AVG(correct),2) AS acc, ROUND(AVG(tries),2) AS tries, ROUND(AVG(ms)) AS ms
       FROM maths m ${where("m")} GROUP BY grade, mlevel, kind ORDER BY grade, kind`),
    q(`SELECT q, grade, COUNT(*) AS n FROM maths m ${where("m")} AND correct=0 GROUP BY q, grade ORDER BY n DESC LIMIT 15`),
    env.DB.prepare(`SELECT player, avatar, grade, app, COUNT(*) AS n, MAX(ts) AS last FROM plays WHERE ts>=? GROUP BY player ORDER BY last DESC`).bind(since).all().then((r) => r.results),
    q(`SELECT game, COUNT(*) AS n, SUM(result='win') AS wins, ROUND(SUM(ms)/60000.0,1) AS minutes, MAX(ts) AS last FROM plays p ${where("p")} GROUP BY game ORDER BY n DESC`),
  ]);
  return json({ ok: true, days, levels, maths, misses, players, games });
}

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    if (url.pathname.startsWith("/little/api/")) url.pathname = url.pathname.slice(7); // the Little Learners pages inside Tile Solve use /little/api/...
    try {
      if (url.pathname === "/api/events" && req.method === "POST") return await events(req, env);
      if (url.pathname === "/api/report") return await report(url, env);
      if (url.pathname === "/api/tts" && req.method === "GET") return await tts(url, env, ctx);
      if (url.pathname === "/api/sync") return await sync(req, url, env);
    } catch (e) { return json({ ok: false, error: String(e && e.message || e) }, 500); }
    if (url.pathname === "/report") return Response.redirect(url.origin + "/report/", 302);
    return env.ASSETS.fetch(req);
  },
};
