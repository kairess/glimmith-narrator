const fs = require('fs');
const path = require('path');
const { EventEmitter } = require('events');
const { getFlagValues } = require('./saveParser');

const DEBOUNCE_MS = 400;
const READ_RETRIES = 3;
const READ_RETRY_DELAY_MS = 150;

// Only the live save slots, e.g. SaveFile1.sav / SaveFile2.sav. Backup/rotation
// copies (SaveFile1_backup_3.sav, ...) are excluded: they're historical
// snapshots and can disagree with the current slot, which would make flag
// transitions look like they happened when they didn't.
const SAVE_FILE_RE = /^SaveFile\d+\.sav$/i;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Reads the file with a couple of retries, since the game may briefly hold/lock
// the .sav file while writing it.
async function readFileWithRetry(filePath) {
  let lastErr;
  for (let attempt = 0; attempt < READ_RETRIES; attempt++) {
    try {
      return await fs.promises.readFile(filePath);
    } catch (err) {
      lastErr = err;
      await sleep(READ_RETRY_DELAY_MS);
    }
  }
  throw lastErr;
}

// Watches a SaveGames directory and emits 'triggered' the moment a tracked
// puzzle path's trigger flag (e.g. HasBeenSolved) is observed to flip from
// false to true *within a given save file*. State is tracked per save file
// (not globally per puzzle path), because two save slots are independent
// playthroughs that can legitimately disagree on the same puzzle — treating
// them as one shared truth made the directory's (unordered) scan order able
// to produce a bogus transition. The very first observation of each flag
// (e.g. at app startup) only records a baseline and never fires by itself —
// otherwise an already-solved puzzle would fire the instant the app is first
// launched. Baselines are persisted across restarts via statePath.
class SaveWatcher extends EventEmitter {
  constructor({ savesDir, lines, statePath }) {
    super();
    this.savesDir = savesDir;
    this.requests = Object.entries(lines).map(([path, line]) => ({
      path,
      flagName: line.trigger,
      fireOnFirstBaseline: !!line.fireOnFirstBaseline,
    }));
    this.statePath = statePath;
    // A handful of "welcome" lines (e.g. the tutorial) are for puzzles/letters
    // whose save entry is written in one shot already-solved (no earlier
    // "opened but not solved" state to observe first), so the normal
    // baseline-and-ignore behaviour below would mean they never play for a
    // save that already has them true the first time this watcher looks at
    // it -- e.g. a player who finished the tutorial before ever installing
    // this app, or a fresh save reached after a reset. `duringInitialScan`
    // only exists to stop the burst of duplicate fires that would otherwise
    // happen if several save slots already have the same line solved at
    // startup; it does not gate firing after startup.
    this.duringInitialScan = true;
    this.firedFirstBaselineLines = new Set();
    this.lastKnownValues = this._loadState(); // Map: `${filename}::${path}::${flagName}` -> boolean
    this.timers = new Map();
    this.watcher = null;
  }

  _loadState() {
    try {
      const raw = fs.readFileSync(this.statePath, 'utf8');
      return new Map(Object.entries(JSON.parse(raw)));
    } catch {
      return new Map();
    }
  }

  _saveState() {
    try {
      fs.mkdirSync(path.dirname(this.statePath), { recursive: true });
      fs.writeFileSync(this.statePath, JSON.stringify(Object.fromEntries(this.lastKnownValues), null, 2));
    } catch (err) {
      this.emit('error', err);
    }
  }

  start() {
    if (!fs.existsSync(this.savesDir)) {
      this.emit('error', new Error(`Saves directory not found: ${this.savesDir}`));
      return;
    }

    // Establish a baseline from current state before watching for changes, so
    // a puzzle already solved before this app ever ran doesn't fire on launch
    // (except the fireOnFirstBaseline lines, which are meant to fire here).
    this._scanDirectory().finally(() => {
      this.duringInitialScan = false;
    });

    this.watcher = fs.watch(this.savesDir, (eventType, filename) => {
      if (!filename || !SAVE_FILE_RE.test(filename)) return;
      this._scheduleCheck(filename);
    });
  }

  stop() {
    if (this.watcher) {
      this.watcher.close();
      this.watcher = null;
    }
    for (const timer of this.timers.values()) clearTimeout(timer);
    this.timers.clear();
  }

  _scheduleCheck(filename) {
    if (this.timers.has(filename)) clearTimeout(this.timers.get(filename));
    const timer = setTimeout(() => {
      this.timers.delete(filename);
      this._checkFile(filename).catch((err) => this.emit('error', err));
    }, DEBOUNCE_MS);
    this.timers.set(filename, timer);
  }

  // Forgets every baseline this watcher has recorded (in memory and on disk)
  // and re-scans immediately. Unlike the real startup scan, this never fires
  // a welcome-style line for a flag that's already true -- it only resets
  // this app's bookkeeping. A flag that's genuinely re-solved afterwards
  // (in the save, live) still narrates normally either way. Used by the
  // tray's "Reset progress" menu item.
  async resetState() {
    this.lastKnownValues.clear();
    try {
      fs.unlinkSync(this.statePath);
    } catch (err) {
      if (err.code !== 'ENOENT') throw err;
    }
    this.firedFirstBaselineLines.clear();
    await this._scanDirectory({ silent: true });
  }

  async _scanDirectory({ silent = false } = {}) {
    let files;
    try {
      files = fs.readdirSync(this.savesDir).filter((f) => SAVE_FILE_RE.test(f));
    } catch (err) {
      this.emit('error', err);
      return;
    }
    await Promise.all(
      files.map((filename) => this._checkFile(filename, { silent }).catch((err) => this.emit('error', err)))
    );
  }

  async _checkFile(filename, { silent = false } = {}) {
    const filePath = path.join(this.savesDir, filename);
    let buf;
    try {
      buf = await readFileWithRetry(filePath);
    } catch (err) {
      this.emit('error', err);
      return;
    }

    const values = getFlagValues(buf, this.requests);
    for (const { path: puzzlePath, flagName, fireOnFirstBaseline } of this.requests) {
      const valueKey = `${puzzlePath}::${flagName}`;
      const value = values.get(valueKey);
      const key = `${filename}::${valueKey}`;

      if (value === null || value === undefined) {
        // Not present in this save. Also drop any cached value: if this key
        // was cached from an earlier playthrough that reused this filename
        // (a deleted/replaced save), leaving a stale "already true" baseline
        // in place would silently swallow the next genuine occurrence.
        if (this.lastKnownValues.has(key)) {
          this.lastKnownValues.delete(key);
          this._saveState();
        }
        continue;
      }

      const previous = this.lastKnownValues.get(key);
      if (previous === undefined) {
        // First time we've ever seen this flag: record the baseline silently,
        // unless this line is flagged to play anyway even when already true
        // (see the comment in the constructor). During the initial startup
        // scan, only let one save file fire it, so having e.g. 3 slots that
        // already solved it doesn't play the line 3 times in a row.
        this.lastKnownValues.set(key, value);
        this._saveState();
        if (
          !silent &&
          fireOnFirstBaseline &&
          value === true &&
          !(this.duringInitialScan && this.firedFirstBaselineLines.has(puzzlePath))
        ) {
          this.firedFirstBaselineLines.add(puzzlePath);
          this.emit('triggered', { puzzlePath, flagName, sourceFile: filename });
        }
        continue;
      }

      if (previous === false && value === true) {
        this.lastKnownValues.set(key, value);
        this._saveState();
        this.emit('triggered', { puzzlePath, flagName, sourceFile: filename });
      } else if (previous !== value) {
        this.lastKnownValues.set(key, value);
        this._saveState();
      }
    }
  }
}

module.exports = { SaveWatcher };
