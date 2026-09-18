const path = require('path');
const { pathToFileURL } = require('url');
const { app, BrowserWindow, screen, ipcMain } = require('electron');

const { getSavesDir, getVoicesDir } = require('./config');
const { SaveWatcher } = require('./saveWatcher');
const { getLanguage } = require('./languageReader');
const LINES = require('./lines');

// All sizes below are "design pixels", tuned by eye on a 2560x1440 screen.
// At runtime everything is multiplied by a scale factor derived from the
// actual screen size, so the overlay looks the same relative size on any
// player's monitor instead of a fixed pixel size that would look huge on a
// small screen or tiny on a large one.
const BASE_CONTENT_WIDTH = 1280;
const BASE_CONTENT_HEIGHT = 280;
const BASE_SHADOW_MARGIN = 40; // transparent breathing room so the drop-shadow isn't clipped
const BASE_BOTTOM_MARGIN = 90;
const REFERENCE_SCREEN_WIDTH = 2560;
const MIN_SCALE = 0.6;
const MAX_SCALE = 1.5;

// Small always-on corner icon confirming the app is running/watching, so the
// player doesn't have to guess whether the narrator is active.
const BASE_ICON_SIZE = 56;
const BASE_ICON_MARGIN = 8;

let overlayWindow = null;
let statusWindow = null;
let hideTimer = null;

function computeScale(screenWidth) {
  const raw = screenWidth / REFERENCE_SCREEN_WIDTH;
  return Math.min(MAX_SCALE, Math.max(MIN_SCALE, raw));
}

function createOverlayWindow() {
  const { workArea } = screen.getPrimaryDisplay();
  const scale = computeScale(workArea.width);

  const windowWidth = Math.round((BASE_CONTENT_WIDTH + BASE_SHADOW_MARGIN * 2) * scale);
  const windowHeight = Math.round((BASE_CONTENT_HEIGHT + BASE_SHADOW_MARGIN * 2) * scale);
  const bottomMargin = Math.round((BASE_BOTTOM_MARGIN - BASE_SHADOW_MARGIN) * scale);

  const x = Math.round(workArea.x + (workArea.width - windowWidth) / 2);
  const y = Math.round(workArea.y + workArea.height - windowHeight - bottomMargin);

  overlayWindow = new BrowserWindow({
    x,
    y,
    width: windowWidth,
    height: windowHeight,
    frame: false,
    transparent: true,
    hasShadow: false,
    resizable: false,
    movable: false,
    minimizable: false,
    maximizable: false,
    fullscreenable: false,
    focusable: false,
    skipTaskbar: true,
    alwaysOnTop: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  overlayWindow.setAlwaysOnTop(true, 'screen-saver');
  overlayWindow.setIgnoreMouseEvents(true, { forward: true });
  overlayWindow.loadFile(path.join(__dirname, 'overlay.html'), { search: `scale=${scale}` });
}

function createStatusWindow() {
  const { workArea } = screen.getPrimaryDisplay();
  const scale = computeScale(workArea.width);

  const size = Math.round(BASE_ICON_SIZE * scale);
  const margin = Math.round(BASE_ICON_MARGIN * scale);

  const x = Math.round(workArea.x + margin);
  const y = Math.round(workArea.y + workArea.height - size - margin);

  statusWindow = new BrowserWindow({
    x,
    y,
    width: size,
    height: size,
    frame: false,
    transparent: true,
    hasShadow: false,
    resizable: false,
    movable: false,
    minimizable: false,
    maximizable: false,
    fullscreenable: false,
    focusable: false,
    skipTaskbar: true,
    alwaysOnTop: true,
  });

  statusWindow.setAlwaysOnTop(true, 'screen-saver');
  statusWindow.setIgnoreMouseEvents(true, { forward: true });
  statusWindow.loadFile(path.join(__dirname, 'statusIndicator.html'));
}

function playLine(line, savesDir) {
  if (!overlayWindow) return;
  if (hideTimer) {
    clearTimeout(hideTimer);
    hideTimer = null;
  }

  // Korean if the game's UI language is set to Korean, English for anything else.
  const language = getLanguage(savesDir);
  const text = language === 'ko' && line.textKo ? line.textKo : line.textEn;

  const audioPath = path.join(getVoicesDir(), line.voiceFile);
  overlayWindow.webContents.send('play-line', {
    text,
    lang: language,
    audioUrl: pathToFileURL(audioPath).href,
  });
  overlayWindow.showInactive();
}

function startWatcher() {
  const savesDir = getSavesDir();
  const statePath = path.join(app.getPath('userData'), 'flag-state.json');

  const watcher = new SaveWatcher({
    savesDir,
    lines: LINES,
    statePath,
  });

  watcher.on('triggered', ({ puzzlePath, flagName, sourceFile }) => {
    const line = LINES[puzzlePath];
    if (!line) return;
    console.log(`[glimmith-narrator] ${puzzlePath} ${flagName} (via ${sourceFile}) -> playing ${line.id}`);
    playLine(line, savesDir);
  });

  watcher.on('error', (err) => {
    console.error('[glimmith-narrator] watcher error:', err.message);
  });

  watcher.start();
  console.log(`[glimmith-narrator] watching ${savesDir}`);
  return watcher;
}

app.whenReady().then(() => {
  createOverlayWindow();
  createStatusWindow();
  startWatcher();
});

ipcMain.on('line-finished', () => {
  if (!overlayWindow) return;
  overlayWindow.hide();
});

app.on('window-all-closed', () => {
  // Keep running in the background even with the overlay hidden; the app
  // only quits via explicit quit (tray/quit menu can be added later).
});
