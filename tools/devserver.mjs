// Local stand-in for Cloudflare: serves the built site and runs worker.js for /api/* with a real SQLite database
// (node:sqlite, wrapped to look like D1). Used by tools/test_sync.py.   node tools/devserver.mjs [port] [dbfile]
import http from "node:http"; import fs from "node:fs"; import path from "node:path"; import { DatabaseSync } from "node:sqlite";
import worker from "../worker.js";
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), ".."), PORT = +process.argv[2] || 8799;
const db = new DatabaseSync(process.argv[3] || ":memory:");
const stmt = (sql, args = []) => ({
  bind: (...a) => stmt(sql, a),
  first: async () => db.prepare(sql).get(...args) ?? null,
  all: async () => ({ results: db.prepare(sql).all(...args) }),
  run: async () => { const r = db.prepare(sql).run(...args); return { meta: { changes: r.changes } }; },
});
const env = { DB: { prepare: (sql) => stmt(sql), batch: async (list) => { const out = []; for (const s of list) out.push(await s.run()); return out; } } };
globalThis.caches = globalThis.caches || { default: { match: async () => undefined, put: async () => {} } };
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".png": "image/png", ".mp3": "audio/mpeg", ".svg": "image/svg+xml" };
http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost:" + PORT);
  if (/^\/(little\/)?api\//.test(url.pathname)) {
    const body = req.method === "POST" ? await new Promise((ok) => { let b = ""; req.on("data", (c) => (b += c)); req.on("end", () => ok(b)); }) : undefined;
    const r = await worker.fetch(new Request(url, { method: req.method, headers: { "content-type": req.headers["content-type"] || "" }, body }), env, { waitUntil() {} });
    res.writeHead(r.status, Object.fromEntries(r.headers)); res.end(Buffer.from(await r.arrayBuffer())); return;
  }
  let f = path.join(ROOT, decodeURIComponent(url.pathname));
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, "index.html");
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); res.end("not found"); return; }
  res.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream", "cache-control": "no-cache" }); fs.createReadStream(f).pipe(res);
}).listen(PORT, () => console.log("devserver on http://localhost:" + PORT));
