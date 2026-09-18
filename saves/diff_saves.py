import sys, re, struct
from collections import defaultdict

def parse(path):
    data = open(path, 'rb').read()
    tag = b'PuzzleID\x00\x0c\x00\x00\x00StrProperty\x00'
    solved_tag = b'HasBeenSolved\x00\r\x00\x00\x00BoolProperty\x00'

    results = []
    for m in re.finditer(re.escape(tag), data):
        tag_pos = m.start()
        null_pos = tag_pos - 5
        i = null_pos - 1
        while i >= 0 and 32 <= data[i] <= 126:
            i -= 1
        str_start = i + 1
        path_str = data[str_start:null_pos].decode('ascii', errors='replace')

        search_region = data[tag_pos:tag_pos+4000]
        sm = search_region.find(solved_tag)
        solved = None
        if sm != -1:
            off = tag_pos + sm + len(solved_tag)
            boolval = data[off+8]
            solved = bool(boolval)
        results.append({'path': path_str, 'solved': solved})
    return results

def by_folder(entries):
    d = defaultdict(lambda: {'total': 0, 'solved': 0, 'paths': set()})
    for r in entries:
        parts = r['path'].split('/')
        folder = '/'.join(parts[1:4]) if len(parts) >= 5 else r['path']
        d[folder]['total'] += 1
        d[folder]['solved'] += 1 if r['solved'] else 0
        d[folder]['paths'].add(r['path'])
    return d

def diff(path_a, path_b, label_a=None, label_b=None):
    label_a = label_a or path_a
    label_b = label_b or path_b
    a = by_folder(parse(path_a))
    b = by_folder(parse(path_b))

    all_folders = sorted(set(a.keys()) | set(b.keys()))
    print(f"=== {label_a}  vs  {label_b} ===")
    for f in all_folders:
        av = a.get(f, {'total':0,'solved':0,'paths':set()})
        bv = b.get(f, {'total':0,'solved':0,'paths':set()})
        if av['total'] == bv['total'] and av['solved'] == bv['solved']:
            continue
        marker = " <-- NEW" if av['total'] == 0 and bv['total'] > 0 else ""
        print(f"{f}: {av['solved']}/{av['total']}  ->  {bv['solved']}/{bv['total']}{marker}")
        new_paths = bv['paths'] - av['paths']
        if new_paths and len(new_paths) <= 20:
            for p in sorted(new_paths):
                print(f"    + {p}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: diff_saves.py <old.sav> <new.sav> [label_old] [label_new]")
        sys.exit(1)
    la = sys.argv[3] if len(sys.argv) > 3 else None
    lb = sys.argv[4] if len(sys.argv) > 4 else None
    diff(sys.argv[1], sys.argv[2], la, lb)
