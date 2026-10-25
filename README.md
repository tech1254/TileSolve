# Tile Solve

A pack of puzzle games for kids. Open `index.html` in a browser. Everything is saved on the device; there are no accounts.

## Players

"Who's playing?" opens first. Each player has a name, a buddy avatar, a colour and a grade, and every game keeps each player's progress separately. Tap the player chip at the top of the home screen to switch players. "Edit players" lets a parent rename, change the grade of, or delete a player.

Hints in every game cost a maths question one grade below the player's grade (grade 3 gets grade 2 maths). There are three tries at the same question, then the answer is shown and a new question appears.

## Games

- **Unblock the Car** (`games/car/`): slide cars until the red one can drive out. 1,000 levels from a bank of pre-generated, verified puzzles; the par is each puzzle's exact shortest solution. Difficulty ramps by grade: for grade 3, it's properly challenging by about level 30.
- Coming soon: Picture Puzzle, Memory Match, Copy the Pattern, Color Flood, Block Fit, Number Tiles, Word Builder, Sudoku Light, Pipe Connect, Lights Out, Picture Logic, Box Push.

## Working on it

- `shared/ts.js` and `shared/ts.css`: players, per-player saves, music and the maths-for-a-hint sheet, used by every page.
- Pages are edited in `src/` (`home.html`, `car.html`). Run `node tools/build.js` to publish them (`index.html`, `games/car/index.html`). The build bakes in the Car puzzle bank and stamps a version on the shared files, so devices pick up updates.
- More Car puzzles: `node tools/gen-bank.js SEED SECONDS out.json`, then `node tools/build.js out.json` to merge, verify and rebuild.
- `python3 tools/test.py` runs the browser tests (needs Playwright).
