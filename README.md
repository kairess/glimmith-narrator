# Glimmith Narrator

A companion overlay for **The Artisan of Glimmith** that watches your save file and plays Elias's narration — as a subtitle + voice line — the moment you actually reach that point in the game. No mods, no save edits: it only reads your `.sav` files.

[![Demo video](https://img.youtube.com/vi/frVgAVe1fgA/hqdefault.jpg)](https://www.youtube.com/watch?v=frVgAVe1fgA)

## Features

- **Live narration overlay** — a frameless, click-through subtitle box appears at the bottom of the screen with matching voice-over (87 lines, `N01`–`N87`) as you solve puzzles and progress through the game.
- **Korean & English** — narration language follows the game's own UI language setting automatically.
- **Zero setup** — auto-detects your save folder (`%LOCALAPPDATA%\Geri\Saved\SaveGames`) on launch. Portable `.exe`, nothing to install.
- **Read-only & safe** — never writes to your save file; watches it, nothing more.
- **Tray menu** — open the log file, open the watched saves folder, **Reset progress** (forgets which lines this app has already played, without touching your game save), and Quit.

## Download

Grab the latest portable `.exe` from [Releases](https://github.com/kairess/glimmith-narrator/releases/latest) and run it — no installer. It sits in the system tray while you play.

> The build is self-signed (not yet a trusted CA), so Windows SmartScreen may show an "unknown publisher" warning on first run.

## Voice

Narration is generated with [ElevenLabs](https://elevenlabs.io) using the **Cornelius (British)** voice (`eleven_multilingual_v2` model).

## Development

See [`app/README.md`](app/README.md) for running from source, testing against a sample save, and building the Windows executable.
