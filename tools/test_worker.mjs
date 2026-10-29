// Tests worker.js against a real SQLite database (node:sqlite) standing in for D1.  node tools/test_worker.mjs
import { DatabaseSync } from "node:sqlite";
import { readFileSync } from "node:fs";
import worker, { events, report } from "../worker.js";
const db = new DatabaseSync(":memory:");
db.exec(readFileSync(new URL("./schema.sql", import.meta.url), "utf8"));
const stmt = (sql) => ({ args: [], bind(...a) { return { ...this, args: a }; }, async all() { return { results: db.prepare(sql).all(...this.args) }; }, async run() { db.prepare(sql).run(...this.args); return {}; } });
const env = { DB: { prepare: stmt, async batch(list) { for (const s of list) await s.run(); return []; } }, ASSETS: { fetch: () => new Response("asset") } };
let fails = 0; const check = (ok, msg) => { console.log((ok ? "PASS " : "FAIL ") + msg); if (!ok) fails++; };
const post = (body) => worker.fetch(new Request("https://x/api/events", { method: "POST", body: JSON.stringify(body) }), env).then((r) => r.json());
const now = Date.now();
let r = await post({ app: "little", device: "d1", player: "p1", avatar: "🐸", grade: 0, events: [
  { t: "play", ts: now, game: "count", level: 3, result: "win", stars: 3, ms: 41000, oops: 0, hints: 0 },
  { t: "play", ts: now, game: "count", level: 4, result: "fail", stars: 0, ms: 60000, oops: 4, hints: 1 },
  { t: "play", ts: now, game: "count", level: 12, result: "quit", ms: 9000, oops: 1, hints: 0 },
  { t: "math", ts: now, game: "count", kind: "hint", mlevel: -1, q: "count 4", correct: 1, tries: 2, ms: 8000 },
  { t: "math", ts: now, game: "count", kind: "check", mlevel: -1, q: "count 7", correct: 0, tries: 3, ms: 12000 },
  { t: "bogus" }, { t: "play" } ] });
check(r.ok && r.saved === 5, "events: saves 5 good records and skips bad ones (" + JSON.stringify(r) + ")");
r = await post({ app: "main", device: "d2", player: "p2", avatar: "🐯", grade: 3, events: [{ t: "play", ts: now - 40 * 864e5, game: "car", level: 1, result: "win", stars: 2, ms: 1000 }] });
check(r.saved === 1, "old records are kept");
await post({ app: "main", device: "d2", player: "p2", avatar: "🐯", grade: 3, events: [{ t: "play", id: "dup1", ts: now, game: "memory", level: 1, result: "win", stars: 3, ms: 1 }] });
await post({ app: "main", device: "d2", player: "p2", avatar: "🐯", grade: 3, events: [{ t: "play", id: "dup1", ts: now, game: "memory", level: 1, result: "win", stars: 3, ms: 1 }] });
check(db.prepare("SELECT COUNT(*) AS c FROM plays WHERE game='memory'").get().c === 1, "the same event sent twice is stored once");
const rep = await worker.fetch(new Request("https://x/api/report?days=30"), env).then((r) => r.json());
const band = rep.levels.find((l) => l.game === "count" && l.band === 1);
check(band && band.n === 2 && band.wins === 1 && band.fails === 1 && band.stars === 3, "report groups levels 1-5 per game and grade " + JSON.stringify(band));
check(rep.levels.some((l) => l.game === "count" && l.band === 11 && l.quits === 1), "quits are counted (level 12 → band 11-15)");
check(!rep.levels.some((l) => l.game === "car"), "the days filter leaves out older plays");
check(rep.maths.length === 2 && rep.misses[0].q === "count 7", "maths accuracy and most-missed questions");
check(rep.players.some((p) => p.avatar === "🐸" && p.grade === 0) && rep.players.every((p) => !("name" in p)), "players show buddy and grade, no names");
const one = await worker.fetch(new Request("https://x/api/report?days=30&player=nobody"), env).then((r) => r.json());
check(one.levels.length === 0, "filter by player");
const bad = await worker.fetch(new Request("https://x/api/events", { method: "POST", body: "nope" }), env);
check(bad.status === 400, "bad JSON is refused");
const locked = await worker.fetch(new Request("https://x/api/report"), { ...env, REPORT_KEY: "secret" });
check(locked.status === 403, "REPORT_KEY protects the report when set");
const asset = await worker.fetch(new Request("https://x/index.html"), env).then((r) => r.text());
check(asset === "asset", "everything else is served from the static files");
console.log(fails ? fails + " FAILED" : "\nALL PASSED"); process.exit(fails ? 1 : 0);
