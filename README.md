# Tile Solve

Puzzle games for kids. Open `index.html` in a browser; it works offline after the first load.

## Unblock the Car

Slide cars along their lanes until the red car can drive out of the exit.

- **Grade picker:** puzzles ramp faster for older players. For grade 3, they get properly challenging by about level 30. Each grade keeps its own progress.
- **1,000 levels** drawn from a bank of pre-generated, verified puzzles. A level's par is its exact shortest solution.
- **Hints cost a maths question:** grade 2 adding or taking away within 100. She gets three tries at the same question, then sees the answer and gets a new one.
- **Music:** a gentle tune generated in the browser, with a mute button.

## Working on it

- Edit `src/index.template.html`, then run `node tools/build.js` to produce `index.html` with the puzzle bank baked in.
- To make more puzzles, run `node tools/gen-bank.js SEED SECONDS out.json`, then `node tools/build.js out.json` to merge, verify and rebuild.
- `python3 tools/test.py` runs the browser tests (needs Playwright).
