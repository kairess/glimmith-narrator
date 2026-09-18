import re, json, sys

path = sys.argv[1] if len(sys.argv) > 1 else 'resources/Glimmith_Editorial_v2.md'
with open(path, encoding='utf-8') as f:
    text = f.read()

# Split on "#### N<number>" headers
blocks = re.split(r'\n#### (N\d+)\n', text)
# blocks[0] is preamble; then alternating id, body
entries = {}
for i in range(1, len(blocks), 2):
    nid = blocks[i]
    body = blocks[i + 1]
    m_en = re.search(r'\*\*EN\*\*\s*\n(.+?)\n\n', body, re.S)
    if not m_en:
        m_en = re.search(r'\*\*EN\*\*\s*\n(.+)', body, re.S)
    en = m_en.group(1).strip().replace('\n', ' ') if m_en else None
    entries[nid] = en

for nid in sorted(entries, key=lambda x: int(x[1:])):
    print(nid, '|', entries[nid])
