/* Tile Solve / Little Learners backend: the static pages are served as before (env.ASSETS); this Worker only adds
     POST /api/events   a batch of play and maths records from a device (queued on the device, sent in batches)
     GET  /api/report   totals for the /report page, to tune difficulty
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
        .bind(S(e.id, 40), ts, ...who, S(e.game, 24), e.kind === "check" ? "check" : "hint", I(e.mlevel, -1, 9), S(e.q, 40), e.correct ? 1 : 0, I(e.tries, 0, 9), I(e.ms, 0, 36e5)));
  }
  if (stmts.length) await env.DB.batch(stmts);
  return json({ ok: true, saved: stmts.length });
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
  async fetch(req, env) {
    const url = new URL(req.url);
    try {
      if (url.pathname === "/api/events" && req.method === "POST") return await events(req, env);
      if (url.pathname === "/api/report") return await report(url, env);
    } catch (e) { return json({ ok: false, error: String(e && e.message || e) }, 500); }
    if (url.pathname === "/report") return Response.redirect(url.origin + "/report/", 302);
    return env.ASSETS.fetch(req);
  },
};
