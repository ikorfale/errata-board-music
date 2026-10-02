#!/usr/bin/env python3
"""Embed every post of the docstring-game thread (text-embedding-3-small) -> doc_emb.npy (rows in seq order)."""
import json, os, urllib.request, numpy as np
L = sorted((json.loads(l) for l in open('doc_thread.jsonl')), key=lambda x: x['seq'])
KEY = open(os.path.expanduser('~/.config/agent-accounts/openai.key')).read().strip()
out = []
for i in range(0, len(L), 100):
    req = urllib.request.Request('https://api.openai.com/v1/embeddings', method='POST',
        headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'},
        data=json.dumps({'model': 'text-embedding-3-small', 'input': [p['body'][:7000] or '.' for p in L[i:i+100]]}).encode())
    d = json.load(urllib.request.urlopen(req, timeout=120))
    out += [e['embedding'] for e in sorted(d['data'], key=lambda e: e['index'])]
    print(i, d['usage'])
np.save('doc_emb.npy', np.array(out, dtype=np.float32))
