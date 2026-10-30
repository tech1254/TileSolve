# Tile Solve

A pack of puzzle games for kids. Open `index.html` in a browser. Everything is saved on the device; there are no accounts.

## Two apps

The repo builds two sites, each its own Cloudflare Worker deployed on every push to `main`:

- **Tile Solve** (repo root, `tilesolve.<account>.workers.dev`): puzzles, Learn & explore (Pattern Next, Animal Sort and Odd One Out from grade 3), Tile Tunes and Christmas Tunes.
- **Little Learners** (`little/`, `littlelearners.<account>.workers.dev`): the Little learners games, Pattern Next, Animal Sort, Odd One Out, Tile Tunes and Christmas Tunes, with its own name and icon (`little-src/`). `tools/build.js` writes it from the same pages (`const APP="little"` on the home page). Each app keeps its own players and progress, since browsers save per address.

## Play reports (tuning difficulty)

Every level start ends as a win, fail or quit, and every maths question is recorded with its result. Each record has the game, grade, level, stars, time, mistakes and hints. Records are queued on the device (`TS.report` in shared/ts.js, hooked into kit.js, car and picture) and sent in batches to `/api/events`. A small Worker (`worker.js`) stores them in the Cloudflare D1 database `tilesolve-reports` (`tools/schema.sql`). Both apps share it. Kids are a random id plus their buddy emoji and grade; names are never sent.

Open **/report** on either app to see win rate, quits, stars, time, mistakes and hints by game, grade and level range (in fives). It also shows maths accuracy and the most-missed questions. Level ranges that look too hard or too easy are flagged. To lock the report, add a `REPORT_KEY` variable to both Workers in Cloudflare; then open `/report/?key=…`.

## Players

"Who's playing?" opens first. Each player has a name, a buddy avatar, a colour and a grade, and every game keeps each player's progress separately. Tap the player chip at the top of the home screen to switch players. "Edit players" lets a parent rename, change the grade of, or delete a player.

**Matched to the Alberta curriculum, one grade back.** Kids pick their current grade, but part way through the year they may not have learned it yet, so maths questions and the Little learners games use the *previous* grade's outcomes from Alberta's K–6 curriculum (mathematics 2022, English language arts and literature):

| Player picks | Content from | Maths questions |
|---|---|---|
| Kindergarten | pre-K | count pictures (to 5 at checkpoints, to 8 for hints) |
| Grade 1 | Kindergarten | quantities to 10: add/take away within 10, make 10 |
| Grade 2 | Grade 1 | addition facts to 20 and related subtraction |
| Grade 3 | Grade 2 | add and subtract within 100 (no times tables) |
| Grade 4 | Grade 3 | within 1,000; × and ÷ facts to 10 × 10 |
| Grade 5 | Grade 4 | facts to 12 × 12; 3-digit × 1-digit; within 10,000 |
| Grade 6 | Grade 5 | 3-digit × 2-digit; 3-digit ÷ 1-digit |
| Grade 7+ | Grade 6 | multiply/divide by 2-digit numbers; percent of a number |

Hints in every game cost one of these questions. There are three tries at the same question, then the answer is shown and a new question appears.

**Maths checkpoints:** the first time a player clears level 3, 6, 9 and so on, the next level asks a maths question before it opens. Checkpoint questions are a little easier than hint questions from the same grade (for a grade 3 player: adding and taking away with no carrying or borrowing). They can't be skipped, and leaving and coming back asks again.

**How to play:** the first time each player opens a game (each Picture Puzzle mode counts separately), a short picture-step card explains it. On level 1 a bouncing 👆 finger points at what to touch first. The **?** button shows the card again any time.

## Little learners (Kindergarten to grade 2)

**Favourite things:** each player can pick a favourite (🚂 trains, 🚚 trucks, 🦖 dinosaurs, 🚀 space, 🐶 animals, 🦄 unicorns, ⚽ sports). Count It, More or Less, Pattern Next and the pre-K maths questions then draw their pictures from it. **Train Yard** is all trains: hook up number cars in order, count passengers, fill seats (ten frame), colour-car patterns, spell your name with letter cars, longest/shortest train, the missing car and loading cargo by shape. Each level won adds a car to the player's train. **Train Trip** has no levels: the train rides from station to station through prairie, forest, mountains, lakes and towns, with tunnels and bridges. At every Y in the track it stops at a red signal, the voice asks a question, and the child taps the sign on the right track (2 tracks for pre-K, 3 after). Questions come from one grade back: numerals with dots, counting, colours, shapes, letters of their name and more/fewer for pre-K, up to sums, skip counting, odd/even and tens and ones. Each kind of question steps up after about 4 of 5 right and down after 2 misses in a row. A wrong sign greys out and the voice says what it was; a missed question comes back two Ys later. Every 3–5 Ys is a station with a present: a new car for the train (passenger, coal, tank, grain, caboose, party car and more), and a 🎵 for Tile Tunes. `tools/test_trip.py` rides it through.

The research behind the Little learners games (literacy, numeracy, shapes and measurement, animals and science) and the roadmap are in the claude.ai project docs under `research/`.


A second section on the home screen, shown first for players in Kindergarten to grade 2. Every question is read aloud with the device's built-in voice (🔊 repeats it; "Read things out loud" in the Levels menu turns it off). Levels are 4 to 6 quick rounds with cheering, big tap targets, and the same profiles, stars, hints, checkpoints and How to play cards as the puzzles. Content follows the previous grade too: Kindergarten players get a gentle pre-K version (fewer choices, numbers to 5, letters from A), grade 1 players get Kindergarten content, and so on. Grade 1 content adds sh/ch/th sounds and counting by 5s and 10s to 100; grade 2 content adds numbers to 1,000, counting by 25s, 50s and 100s, and sorting shapes by sides.

- **Letters:** ABC Order, Missing Letter, Big & Little (a ↔ A), First Sound (picture → starting letter), Trace a Letter (finger-trace A–Z and 0–9).
- **Numbers:** Count It (pictures, then tens and ones), Number Order, More or Less, Missing Number (counting on, back, and skip counting), Ten Frame.
- **Shapes and colours:** Shape Sort (drag to the matching home, later by number of sides), Shape Hunt, Colour Match (colours, colour words, sorting), Size Order.

All rounds are built by `shared/learn.js` from a small description in each game's `src/<game>.html`.

## Learn & explore (grade ranges)

Each game here has a grade range and only shows for players in it. Content again follows the previous grade's Alberta outcomes. They are written by `tools/mk_explore.py`.

- **Make Ten** (grades 1–4): tap numbers that add up to a target. Sums to 10, then 20, then tens to 100 with three numbers, then hundreds.
- **Times Tables** (grades 3–7): equal groups and skip counting for grade 3 players, 10×10 facts for grade 4, 12×12 and division after that.
- **Fraction Pizza** (grades 2–7): equal halves, then unit fractions, k/N and comparing, then equivalent fractions.
- **Money Shop** (grades 3–7): Canadian coins. Count one kind of coin, then mixed coins and paying an exact price, then making change.
- **Clock & Calendar** (grades 2–7): days and months in order, then which takes longer and units of time, then reading analog clocks, then quarter past/to and minutes between times.
- **Number Line Jump** (grades 1–6): where does the frog land? Within 10, 20, tens to 100, hundreds to 1,000, then tenths.
- **Pattern Next** (Kindergarten–grade 7): repeating picture patterns, then counting up or down, ×2 and ÷2, then squares, triangle numbers and Fibonacci.
- **Sentence Builder** (grades 1–5): tap mixed-up words in order. Short sentences first, then questions and longer sentences with commas.
- **Spelling Bee** (grades 1–7): hear a word and see it in a sentence, then spell it. Sight words, then digraphs and long vowels, silent letters, and tricky words with Canadian spelling (colour, favourite, neighbour). Extra letters mixed in.
- **Picture Crossword** (grades 2–7): every clue is a picture. Tap a clue or a square and type on the letter keys. More and longer words by grade and level; every grid fits on a phone.

- **Animal Sort** (Kindergarten–grade 5): drag animals into their homes. Land or water, then land/water/sky, fur/feathers/scales, mammal/bird/fish/insect/reptile/amphibian, and plant or meat eaters.
- **Odd One Out** (Kindergarten–grade 5): which one doesn't belong? Pictures, then close categories (fruit vs vegetables), numbers (even, 5s, 10s, 3s) and words.
- **Planet Order** (grades 2–7): tap the planets in order from the Sun (or smallest to biggest), plus space questions (day and night, a year, gravity).
- **Food Chain** (grades 2–7): build the chain from the plant up, "what does it eat?", and producer or consumer.
- **Flags & Places** (grades 2–7): Canada's symbols, provinces, territories and capitals, Alberta geography, then world flags and continents.
- **Code the Robot** (grades 1–7): build a program and press Go. Arrows for grades 1–3; Forward / Turn left / Turn right for grade 4+. Later levels add rocks and gems. Every puzzle is checked with a shortest-path search, and the hint adds the next good move to the program.

**Rhyme Time** (Little learners): tap the word that rhymes, with pictures for younger players and "which one does not rhyme?" rounds later.

## Tile Tunes (a reward)

Coloured tiles slide down four lanes; tapping each one plays the next note of a song on a built-in Web Audio piano. There are no recordings: the 20 songs are public-domain melodies (traditional tunes, Beethoven, Mozart, Brahms, Grieg, Joplin and others) written out note by note in `src/tunes.html`. Each note name has its own colour, and note names can be shown on the tiles. A wrong lane or a missed tile costs a heart. "🐢 Wait for me" (on by default for Kindergarten and grade 1) stops each tile at the line until it's tapped. Speed is set by grade.

**Christmas Tunes** (🎄 on the home screen) is a second songbook from the same page (`games/carols`): Jingle Bells, We Wish You a Merry Christmas, Deck the Halls, Silent Night, O Christmas Tree, Joy to the World, Good King Wenceslas, Angels We Have Heard on High, The First Noel, Auld Lang Syne and What Child Is This, all written before 1929 so the melodies are public domain. Carols cost 3 🎵 each.

**🎼 My songs (Make a Song):** tap a tune on a 17-key piano and it becomes a playable song. Timing comes from the taps (the usual gap is one beat; lengths round to ½, 1, 1½, 2, 3 or 4 beats). Songs are saved on the device for every player, are free to play, and can be moved to another device with a song code (📋 to copy, 📥 to add).

Songs are earned: the first is free, then each song needs 5 more 🎵. Players earn a 🎵 for every level finished in any other game and for every maths question answered right (`TS.notes`).

## Puzzle games

**Baseball** (every grade): you're at bat, seen from behind home plate in a ballpark with a crowd. The pitcher throws; tap SWING (or the field, or the space bar) when the ball reaches the strike zone. Right on time can be a home run; a little early pulls the ball to left field and a little late goes to right; way off is a foul or a miss. Pitches outside the zone are balls (4 is a walk), and weak contact can be caught or thrown out at first. Each level asks for more runs (1 up to 6) before 3 outs; stars for outs to spare. Pitches get faster with level and grade, then changeups and curveballs join in. The hint makes the next pitch slow and down the middle with a ring that turns green when it's time to swing. `tools/test_baseball.py` proves perfect timing wins every level.

**Ball Run** (every grade): a ball rolls along a track in the sky; drag or hold ◀ ▶ to steer. Narrow bridges, zigzags, walls, sweeping bars, moving platforms and jump pads that always land you on the next platform. Flags are checkpoints, and gems are a bonus. Tracks get longer, faster and trickier by level and grade. `tools/test_ballrun.py` drives every grade's levels with a careful self-steering ball to prove each one can be finished without falling.

- **Unblock the Car** (`games/car/`): slide cars until the red one can drive out. 1,000 levels from a bank of pre-generated, verified puzzles; the par is each puzzle's exact shortest solution. Difficulty ramps by grade: for grade 3, it's properly challenging by about level 30.
- **Picture Puzzle** (`games/picture/`): eight original cartoon pictures (animals and space). Two modes, 40 levels each:
  - *Drop-in*: drag pieces from the tray into the picture. Pieces get smaller as levels go on, and later levels turn the pieces (tap to turn them back). A wrong drop counts as an "oops".
  - *Slider*: the classic one-gap sliding puzzle. 3×3 puzzles have an exact par; older grades move on to 4×4 and 5×5.
  - Tap the thumbnail to peek at the whole picture. Hints place a piece or flash the next tile to slide.
- **Memory Match** (`games/memory/`): flip two cards at a time to find the pairs. Boards grow from 4×2 to 6×5 (from 3×2 for grades 1–2). Early levels show every card for a moment first, and from level 30 the cards are look-alikes. Hints show one pair.
- **Copy the Pattern** (`games/pattern/`): watch coloured tiles light up, then rebuild the pattern. Grids grow from 3×3 to 5×5 (6×6 for older grades), with more tiles, more colours and less time to look. Up to 2 mistakes still passes. Hints replay the pattern.
- **Color Flood** (`games/flood/`): grow your colour from the ★ corner until it fills the board, within the move limit. Boards grow from 6×6 to 14×14 with up to 6 colours. Par comes from a built-in solver, and hints show its next colour. Every colour also has a shape, for colour-blind players.
- **Block Fit** (`games/blocks/`): drag blocks into an outline until every square is filled. Each puzzle is cut from its outline, so it always has a solution. Outlines grow, later ones are odd shapes, and from level 11 (grade 3) blocks arrive turned: tap to turn. Tap a placed block to take it back. Hints place a block.
- **Number Tiles** (`games/numbers/`): put the number tiles in the empty squares so every row and column adds up to its total. Grids grow from 2×2 to 4×4 with more empty squares and bigger numbers for older grades. Totals turn green or red as rows fill up. Hints place a tile.
- **Word Builder** (`games/words/`): spell the picture's word by tapping letter tiles in order. Words get longer by grade (3 letters up to 8+), and later levels add extra letters that don't belong. After a wrong try, letters in the right spot stay put. Hints place the next letter.
- **Sudoku Light** (`games/sudoku/`): every row, column and box needs each symbol once. Starts on 4×4 with animals, then numbers, then 6×6 (9×9 for grade 5 and up). Every puzzle has exactly one answer. Clashes turn red. Tap a square then a symbol, or pick a symbol and tap squares. Hints fill or fix a square.
- **Pipe Connect** (`games/pipes/`): tap pipes to turn them until water from the 💧 reaches every flower with no open ends. Boards are one connected pipe network, from 3×3 up to 7×7 (8×8 older). Par is the fewest taps. Hints turn one pipe the right way.
- **Lights Out** (`games/lights/`): tapping a light flips it and its neighbours; turn them all off. Boards grow from 3×3 to 5×5 (6×6 older). Par is the exact fewest taps, worked out with linear algebra. Hints ring a light from the best answer.
- **Picture Logic** (`games/pixels/`): number clues reveal a hidden pixel picture (nonograms). 40 drawn pictures at 5×5, 8×8 and 10×10, each checked to be solvable by logic alone. Drag to fill several squares, and switch to ✕ to mark empty ones. Hints fix or fill one square.
- **Box Push** (`games/boxes/`): push every crate onto a red spot (Sokoban). Swipe, use the arrows, or tap where to walk; Undo takes a move back. Levels come from a bank of 1,118 made backwards from solved positions, each re-verified, and par is the exact fewest pushes. Grade 3 goes from 1 crate to 3. Hints show the next push.
- **Word Search** (`games/wordsearch/`): find the themed words hidden in the letters (13 themes: animals, space, ocean, food and more). Drag across a word, or tap its first and last letter. Grade 3 goes from 7×7 with across/down words to 10×10 with diagonal and backwards words. Each word is hidden exactly once, and filler letters are checked so they never spell anything unkind. Hints flash a word's first letter.

## Working on it

- `shared/ts.js` and `shared/ts.css`: players, per-player saves, music and the maths-for-a-hint sheet, used by every page.
- `shared/kit.js` and `shared/game.css`: the standard game screen (top bar, level picker, win card, hints, progress). New games only supply their puzzle; any `src/<game>.html` is built to `games/<game>/`, and `<!--HEAD:Title-->` / `<!--KIT-->` expand to the standard head and scripts.
- Pages are edited in `src/` (`home.html`, and one file per game). Run `node tools/build.js` to publish them (`index.html` and `games/<game>/index.html`). The build bakes in the Car puzzle bank and stamps a version on the shared files, so devices pick up updates.
- More Car puzzles: `node tools/gen-bank.js SEED SECONDS out.json`, then `node tools/build.js out.json` to merge, verify and rebuild.
- More Box Push levels: `node tools/gen-boxes.js SEED SECONDS out.json`, then `node tools/merge-boxes.js out.json` (re-verifies every par) and rebuild.
- `shared/pictures.js`: the picture set, drawn in code. Photo entries can be added later.
- `sh tools/test_all.sh` rebuilds and runs all ten browser test suites over a local web server (needs Playwright). Each `tools/test*.py` can also run on its own.
