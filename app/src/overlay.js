const frame = document.getElementById('frame');
const content = document.getElementById('content');
const frameSvg = document.getElementById('frameSvg');
const textLayer = document.getElementById('textLayer');
const text = document.getElementById('text');
const audio = document.getElementById('audio');

// Must match BASE_CONTENT_WIDTH/HEIGHT in main.js. `scale` is passed in via
// the loaded URL's query string so this design scales with the player's
// actual screen size instead of always being a fixed pixel size.
const BASE_CONTENT_WIDTH = 1280;
const BASE_CONTENT_HEIGHT = 280;
const BASE_FONT_SIZE = 34;
const BASE_PADDING_V = 46;
const BASE_PADDING_H = 130;
const BASE_SHADOW_OFFSET_Y = 12;
const BASE_SHADOW_BLUR = 22;

const scale = parseFloat(new URLSearchParams(window.location.search).get('scale')) || 1;
content.style.width = `${BASE_CONTENT_WIDTH * scale}px`;
content.style.height = `${BASE_CONTENT_HEIGHT * scale}px`;
text.style.fontSize = `${BASE_FONT_SIZE * scale}px`;
textLayer.style.padding = `${BASE_PADDING_V * scale}px ${BASE_PADDING_H * scale}px`;
frameSvg.style.filter = `drop-shadow(0 ${BASE_SHADOW_OFFSET_Y * scale}px ${BASE_SHADOW_BLUR * scale}px rgba(0, 0, 0, 0.4))`;

// Extra time to keep the subtitle on screen after the audio finishes, so
// slower readers have a chance to finish reading the line.
const POST_AUDIO_READ_DELAY_MS = 3000;

window.glimmith.onPlayLine(({ text: lineText, lang, audioUrl }) => {
  text.textContent = lineText;
  text.classList.toggle('lang-ko', lang === 'ko');
  frame.classList.add('visible');
  audio.src = audioUrl;
  audio.currentTime = 0;
  audio.play().catch(() => {
    // Autoplay can fail if the window isn't focused; fall back to a fixed
    // display duration so the subtitle still shows and hides itself.
    setTimeout(scheduleHide, 6000);
  });
});

function scheduleHide() {
  setTimeout(hide, POST_AUDIO_READ_DELAY_MS);
}

function hide() {
  frame.classList.remove('visible');
  setTimeout(() => window.glimmith.notifyFinished(), 400);
}

audio.addEventListener('ended', scheduleHide);
audio.addEventListener('error', scheduleHide);
