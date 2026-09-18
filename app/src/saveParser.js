// Minimal reader for the relevant slice of Unreal Engine GVAS SaveGame binary format
// used by Glimmith's PuzzleData TMap<FString, FPuzzleSaveData>.
// Ported from the byte-offset logic in saves/diff_saves.py and saves/set_solved.py.

const PUZZLE_ID_TAG = Buffer.from('PuzzleID\x00\x0c\x00\x00\x00StrProperty\x00', 'ascii');
const SEARCH_WINDOW = 4000;

function boolPropertyTag(flagName) {
  // [flagName]\x00 + [len(BoolProperty)+1 : int32LE] + "BoolProperty\x00"
  const typeName = 'BoolProperty';
  const lenPrefix = Buffer.alloc(4);
  lenPrefix.writeInt32LE(typeName.length + 1, 0);
  return Buffer.concat([Buffer.from(flagName + '\x00', 'ascii'), lenPrefix, Buffer.from(typeName + '\x00', 'ascii')]);
}

function findPuzzleEntries(buf) {
  const entries = [];
  let searchFrom = 0;
  while (true) {
    const tagPos = buf.indexOf(PUZZLE_ID_TAG, searchFrom);
    if (tagPos === -1) break;

    // The FString key (puzzle path) sits right before this tag: [len:int32][ascii][\x00].
    const nullPos = tagPos - 5;
    let i = nullPos - 1;
    while (i >= 0 && buf[i] >= 32 && buf[i] <= 126) i--;
    const strStart = i + 1;

    if (strStart >= 0 && strStart < nullPos) {
      const path = buf.toString('ascii', strStart, nullPos);
      entries.push({ path, tagPos });
    }
    searchFrom = tagPos + 1;
  }
  return entries;
}

function readBoolFlag(buf, tagPos, flagName) {
  const tag = boolPropertyTag(flagName);
  const regionEnd = Math.min(buf.length, tagPos + SEARCH_WINDOW);
  const sm = buf.indexOf(tag, tagPos);
  if (sm === -1 || sm >= regionEnd) return null;
  const boolBytePos = sm + tag.length + 8;
  if (boolBytePos >= buf.length) return null;
  return buf[boolBytePos] !== 0;
}

// requests: [{ path, flagName }]. Returns a Map keyed by `${path}::${flagName}` -> boolean|null.
function getFlagValues(buf, requests) {
  const wantedPaths = new Set(requests.map((r) => r.path));
  const tagPosByPath = new Map();
  for (const { path, tagPos } of findPuzzleEntries(buf)) {
    if (wantedPaths.has(path) && !tagPosByPath.has(path)) {
      tagPosByPath.set(path, tagPos);
    }
  }

  const result = new Map();
  for (const { path, flagName } of requests) {
    const tagPos = tagPosByPath.get(path);
    const value = tagPos === undefined ? null : readBoolFlag(buf, tagPos, flagName);
    result.set(`${path}::${flagName}`, value);
  }
  return result;
}

module.exports = { getFlagValues };
