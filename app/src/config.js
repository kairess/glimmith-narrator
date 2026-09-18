const fs = require('fs');
const path = require('path');
const os = require('os');
const { app } = require('electron');

const SAVE_FILE_MARKER_RE = /^(SaveFile\d*|Settings)\.sav$/i;

// True if `dir` exists and actually contains the game's save files, rather
// than just being a plausible-looking path. Used to tell an empty/wrong
// guess apart from the real SaveGames folder.
function looksLikeSavesDir(dir) {
  try {
    return fs.readdirSync(dir).some((f) => SAVE_FILE_MARKER_RE.test(f));
  } catch {
    return false;
  }
}

// Root folders Unreal Engine games commonly put their `<Project>/Saved/SaveGames`
// folder under, across different install/launcher setups.
function candidateRoots() {
  const home = os.homedir();
  const roots = [
    process.env.LOCALAPPDATA,
    process.env.APPDATA,
    path.join(home, 'AppData', 'Local'),
    path.join(home, 'AppData', 'LocalLow'),
    path.join(home, 'Documents', 'My Games'),
    path.join(home, 'Documents'),
  ].filter(Boolean);
  return [...new Set(roots)];
}

// Scans the candidate roots for any `<something>/Saved/SaveGames` folder that
// actually holds save files, in case the project folder isn't named exactly
// "Geri" (different build, launcher, or casing) so the fixed guess below misses it.
function findSavesDirByScanning() {
  for (const root of candidateRoots()) {
    let entries;
    try {
      entries = fs.readdirSync(root, { withFileTypes: true });
    } catch {
      continue;
    }

    const dirs = entries.filter((e) => e.isDirectory());
    // Try folders that look related to this game first, then everything else.
    dirs.sort((a, b) => Number(/geri|glimmith|artisan/i.test(b.name)) - Number(/geri|glimmith|artisan/i.test(a.name)));

    for (const dir of dirs) {
      const savesDir = path.join(root, dir.name, 'Saved', 'SaveGames');
      if (looksLikeSavesDir(savesDir)) return savesDir;
    }
  }
  return null;
}

// Directory containing SaveFile*.sav. Override with GLIMMITH_SAVES_DIR for local testing
// (e.g. pointing at the repo's saves/ folder instead of the live game save).
function getSavesDir() {
  if (process.env.GLIMMITH_SAVES_DIR) {
    return process.env.GLIMMITH_SAVES_DIR;
  }

  if (process.platform === 'win32') {
    const localAppData = process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local');
    const expected = path.join(localAppData, 'Geri', 'Saved', 'SaveGames');
    if (looksLikeSavesDir(expected)) return expected;

    const found = findSavesDirByScanning();
    if (found) return found;

    // Nothing found yet (game may never have been launched/saved). Return the
    // expected path anyway so the watcher's error message points somewhere useful.
    return expected;
  }

  // No sane default off Windows; caller must set GLIMMITH_SAVES_DIR for dev/testing.
  return path.join(os.homedir(), 'Geri', 'Saved', 'SaveGames');
}

// Directory containing the voice-over mp3 files.
function getVoicesDir() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'voices');
  }
  return path.join(__dirname, '..', '..', 'voices');
}

module.exports = { getSavesDir, getVoicesDir };
