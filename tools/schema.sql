-- D1 database "tilesolve-reports" (id 48c6bcec-7336-4d1c-a942-8f72262c2241), used by worker.js
CREATE TABLE IF NOT EXISTS plays (id INTEGER PRIMARY KEY AUTOINCREMENT, eid TEXT, ts INTEGER NOT NULL, app TEXT, device TEXT, player TEXT, avatar TEXT, grade INTEGER,
  game TEXT NOT NULL, level INTEGER, result TEXT, stars INTEGER, ms INTEGER, oops INTEGER, hints INTEGER);
CREATE TABLE IF NOT EXISTS maths (id INTEGER PRIMARY KEY AUTOINCREMENT, eid TEXT, ts INTEGER NOT NULL, app TEXT, device TEXT, player TEXT, avatar TEXT, grade INTEGER,
  game TEXT, kind TEXT, mlevel INTEGER, q TEXT, correct INTEGER, tries INTEGER, ms INTEGER);
CREATE INDEX IF NOT EXISTS plays_game ON plays(game, grade, level);
CREATE INDEX IF NOT EXISTS plays_ts ON plays(ts);
CREATE INDEX IF NOT EXISTS maths_ts ON maths(ts);
-- each event has a random id from the device, so a batch sent twice (page closing, then a retry) is only stored once
CREATE UNIQUE INDEX IF NOT EXISTS plays_eid ON plays(eid);
CREATE UNIQUE INDEX IF NOT EXISTS maths_eid ON maths(eid);
