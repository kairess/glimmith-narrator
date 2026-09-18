# Glimmith Narrator

Watches the save-game directory for *The Artisan of Glimmith* and, the first time
`AGeri/Puzzles/Data/Tutorial-1` is observed with `HasBeenSolved = true`, shows a
subtitle box at the bottom-center of the screen and plays the matching voice-over
from `../voices/`. Currently wired up for **N01** only
(see `resources/Glimmith_Editorial_v2.md`); add more entries to `src/lines.js`
to cover additional N-numbers.

Read-only: this never writes to your save file.

## How it works

- `src/saveParser.js` — reads the relevant slice of the game's GVAS `.sav`
  format directly (same byte offsets as `saves/diff_saves.py` /
  `saves/set_solved.py`), no game mod required.
- `src/saveWatcher.js` — watches every `*.sav` in the saves directory
  (covers both save slots), debounces rapid writes, and fires a `solved`
  event the first time each tracked puzzle path flips to solved. Already-
  fired puzzles are remembered in `<userData>/played-lines.json` so they
  never replay after a restart.
- `src/main.js` — a frameless, click-through, always-on-top overlay window
  that shows the English line and plays its audio file.

## Run it (dev)

```
npm install
npm start
```

By default it watches `%LOCALAPPDATA%\Geri\Saved\SaveGames` (the real game
save location on Windows). To point it at a different folder — e.g. a safe
test copy instead of your live save — set `GLIMMITH_SAVES_DIR`:

```
GLIMMITH_SAVES_DIR=/path/to/test/saves npm start
```

## Testing without touching your real save

A copy of the save with `Tutorial-1` set to **not solved** lives at
`../saves/test/SaveFile1.sav`. Run the app against it:

```
GLIMMITH_SAVES_DIR=../saves/test npm start
```

Then, in another terminal, flip the flag to simulate finishing the tutorial:

```
cd ../saves
python3 toggle_puzzle_flag.py test/SaveFile1.sav test/SaveFile1.sav AGeri/Puzzles/Data/Tutorial-1 true
```

The overlay should appear at the bottom-center of the screen and play
`voices/N01.mp3`. To test again from scratch, flip the flag back to `false`
and delete the app's `played-lines.json` (its path is printed by Electron's
`app.getPath('userData')`; on Linux that's normally
`~/.config/glimmith-narrator/played-lines.json`).

**Never point `GLIMMITH_SAVES_DIR` (or run without it) at your real, live
save while the game is running** unless you intend to test against real
progress — this app only reads the file, but the game itself may be writing
to it at the same time.

## Building the Windows .exe

```
npm run dist:win
```

This uses `electron-builder` with the `nsis` target and bundles `../voices/`
into the packaged app's `resources/voices` folder (see `getVoicesDir()` in
`src/config.js`). Building an NSIS installer for Windows from Linux requires
Wine; it's simplest to run this command on Windows, or in CI.
