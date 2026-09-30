import json, re
W = json.load(open('align/words.json'))
def sentences(k):
    ws = W[k]['words']; out=[]; cur=[]
    for w in ws:
        cur.append(w)
        if re.search(r'[.?!]["”]?$', w['w'].strip()):
            out.append(cur); cur=[]
    if cur: out.append(cur)
    return [(round(s[0]['s'],2), round(s[-1]['e'],2), ''.join(x['w'] for x in s).strip()) for s in out]
if __name__ == '__main__':
    import sys
    for k in sys.argv[1:]:
        for i,(a,b,t) in enumerate(sentences(k)):
            print(f'{k}[{i}] {a:6.2f}-{b:6.2f} {t}')
