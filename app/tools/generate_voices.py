"""Generates missing N-number narration voice lines via the ElevenLabs API.

Usage:
  ELEVENLABS_API_KEY=... python3 generate_voices.py [--only N21,N22] [--dry-run]

Reads app/tools/lines_to_voice.json (id -> English text) and writes
voices/N<id>.mp3 for any id not already present, using the voice/model/
settings the user specified.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

VOICE_ID = "6sFKzaJr574YWVu4UuJF"  # Cornelius (British)
MODEL_ID = "eleven_multilingual_v2"
VOICE_SETTINGS = {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": True,
    "speed": 1.0,
}
OUTPUT_FORMAT = "mp3_44100_128"  # matches existing N01-N20 files (128kbps/44.1kHz)

ROOT = Path(__file__).resolve().parent.parent.parent
LINES_PATH = Path(__file__).resolve().parent / "lines_to_voice.json"
VOICES_DIR = ROOT / "voices"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="comma-separated list of ids to generate, e.g. N21,N22")
    parser.add_argument("--dry-run", action="store_true", help="print what would be generated without calling the API")
    parser.add_argument("--force", action="store_true", help="regenerate even if the mp3 already exists")
    args = parser.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key and not args.dry_run:
        sys.exit("ELEVENLABS_API_KEY environment variable is not set")

    with open(LINES_PATH, encoding="utf-8") as f:
        lines = json.load(f)

    ids = sorted(lines, key=lambda x: int(x[1:]))
    if args.only:
        wanted = set(args.only.split(","))
        ids = [i for i in ids if i in wanted]

    VOICES_DIR.mkdir(exist_ok=True)

    for nid in ids:
        out_path = VOICES_DIR / f"{nid}.mp3"
        if out_path.exists() and not args.force:
            print(f"skip {nid}: already exists")
            continue

        text = lines[nid]
        print(f"generating {nid} ({len(text)} chars): {text[:60]}...")
        if args.dry_run:
            continue

        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
            params={"output_format": OUTPUT_FORMAT},
            json={
                "text": text,
                "model_id": MODEL_ID,
                "voice_settings": VOICE_SETTINGS,
            },
            timeout=60,
        )
        if resp.status_code != 200:
            print(f"  FAILED {nid}: {resp.status_code} {resp.text[:300]}")
            continue

        out_path.write_bytes(resp.content)
        print(f"  wrote {out_path} ({len(resp.content)} bytes)")
        time.sleep(0.3)  # be polite to the API


if __name__ == "__main__":
    main()
