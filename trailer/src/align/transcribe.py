import mlx_whisper, json, glob, os, sys
out = {}
files = sorted(glob.glob('/Users/brad/Development/glimmith-narrator/voices/*.mp3'))
for f in files:
    k = os.path.basename(f)[:-4]
    r = mlx_whisper.transcribe(f, path_or_hf_repo='mlx-community/whisper-large-v3-turbo', language='en', word_timestamps=True)
    words = [dict(w=w['word'], s=round(w['start'],3), e=round(w['end'],3)) for seg in r['segments'] for w in seg.get('words', [])]
    out[k] = dict(text=r['text'], words=words)
    print(k, r['text'], flush=True)
json.dump(out, open('align/words.json','w'), ensure_ascii=False, indent=1)
print('DONE')
