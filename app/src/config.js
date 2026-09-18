const path = require('path');
const os = require('os');
const { app } = require('electron');

// Directory containing SaveFile*.sav. Override with GLIMMITH_SAVES_DIR for local testing
// (e.g. pointing at the repo's saves/ folder instead of the live game save).
function getSavesDir() {
  if (process.env.GLIMMITH_SAVES_DIR) {
    return process.env.GLIMMITH_SAVES_DIR;
  }
  if (process.platform === 'win32') {
    const localAppData = process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local');
    return path.join(localAppData, 'Geri', 'Saved', 'SaveGames');
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
