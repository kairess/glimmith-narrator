# Glimmith Narrator

Watches the save-game directory for *The Artisan of Glimmith* and, the moment a
tracked puzzle path is observed with its trigger flag (`HasBeenSolved`, usually)
newly true, shows a subtitle box at the bottom-center of the screen and plays
the matching voice-over from `../voices/`. All 87 lines (`N01`–`N87`, see
`src/lines.js`) are wired up, from the tutorial letter through the endgame.

Read-only: this never writes to your save file.

## How it works

- `src/saveParser.js` — reads the relevant slice of the game's GVAS `.sav`
  format directly (same byte offsets as `saves/diff_saves.py` /
  `saves/set_solved.py`), no game mod required.
- `src/saveWatcher.js` — watches every `SaveFile*.sav` in the saves directory
  (covers all save slots), debounces rapid writes, and fires a `triggered`
  event the first time each tracked puzzle path's flag flips to true.
  Already-fired flags are remembered per save file in
  `<userData>/flag-state.json` so they never replay after a restart. A
  handful of "welcome" lines (e.g. the tutorial letter) are written in one
  shot already-solved rather than opened-then-solved, so they're allowed to
  fire the first time this app observes them already true, not just on a
  false→true transition.
- `src/main.js` — a frameless, click-through, always-on-top overlay window
  that shows the line (Korean or English, following the game's UI language)
  and plays its audio file; also owns the system tray icon and its menu
  (open log file, open the watched saves folder, **Reset progress** — forgets
  this app's own playback bookkeeping without touching the game save — and
  Quit).

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
and delete the app's `flag-state.json` (its path is printed by Electron's
`app.getPath('userData')`; on Windows that's normally
`%APPDATA%\glimmith-narrator\flag-state.json`) — or, with the app running,
use the tray menu's **Reset progress** instead of deleting the file by hand.

**Never point `GLIMMITH_SAVES_DIR` (or run without it) at your real, live
save while the game is running** unless you intend to test against real
progress — this app only reads the file, but the game itself may be writing
to it at the same time.

## Building the Windows .exe

```
npm run dist:win
```

This uses `electron-builder` with the `portable` target (a single self-contained
`.exe`, no installer) and bundles `../voices/` into the packaged app's
`resources/voices` folder (see `getVoicesDir()` in `src/config.js`). Run it on
Windows (or in CI).

To also code-sign the build, set `CSC_LINK` (path to a `.pfx`) and
`CSC_KEY_PASSWORD` before running the command; `electron-builder` picks them up
automatically. Without a certificate from a trusted CA, the result is only
self-signed and Windows SmartScreen may still warn on first run.
