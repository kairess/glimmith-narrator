const fs = require('fs');
const path = require('path');

// Reads the game's UI language from Settings.sav, e.g. "ko" for Korean.
// Structure: "Language\0" + StrProperty type tag + Size:int64 + GUID-flag
// byte + FString value (length-prefixed ascii + null). Same tagged-property
// format as the puzzle save data (see saveParser.js).
const LANGUAGE_TAG = Buffer.from('Language\x00\x0c\x00\x00\x00StrProperty\x00', 'ascii');

function getLanguage(savesDir) {
  const settingsPath = path.join(savesDir, 'Settings.sav');
  let buf;
  try {
    buf = fs.readFileSync(settingsPath);
  } catch {
    return null;
  }

  const tagPos = buf.indexOf(LANGUAGE_TAG);
  if (tagPos === -1) return null;

  const strLenPos = tagPos + LANGUAGE_TAG.length + 8 + 1; // Size:int64 + GUID-flag byte
  if (strLenPos + 4 > buf.length) return null;
  const strLen = buf.readInt32LE(strLenPos); // includes the trailing null
  const strStart = strLenPos + 4;
  if (strLen <= 0 || strStart + strLen > buf.length) return null;

  return buf.toString('ascii', strStart, strStart + strLen - 1); // drop the null
}

module.exports = { getLanguage };
