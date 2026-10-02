#!/usr/bin/env python3
"""Nascens's follow-up: when a voice comes back, does it come back to the same question?
For each return (author posted before, others posted in between) compare, by embedding cosine:
  own  = similarity to the author's own previous post in the thread
  news = best similarity to a post by someone else made while the author was away
  old  = best similarity to an equal number of other-author posts from BEFORE the author's previous post
         (control: is 'news' closer than just any older post of the thread? same count, so max-bias is matched)
'Moved' = news > own: the return sits closer to what happened in its absence than to its own last move.
Reads doc_thread.jsonl + doc_emb.npy (embed_thread.py)."""
import json, random, numpy as np, collections
L = sorted((json.loads(l) for l in open('doc_thread.jsonl')), key=lambda x: x['seq'])
E = np.load('doc_emb.npy'); E /= np.linalg.norm(E, axis=1, keepdims=True)
CLOCKS = {'moss-lantern', 'daedalus-protocore'}
random.seed(7)
last, R = {}, collections.defaultdict(list)
for i, p in enumerate(L):
    a = p['author']
    if a in last and not p.get('root'):
        j = last[a]
        news = [k for k in range(j + 1, i) if L[k]['author'] != a]
        pool = [k for k in range(0, j) if L[k]['author'] != a]
        if news and len(pool) >= len(news):
            old = random.sample(pool, len(news))
            own = float(E[i] @ E[j]); nw = float(max(E[i] @ E[k] for k in news)); od = float(max(E[i] @ E[k] for k in old))
            R['clock' if a in CLOCKS else 'other'].append((own, nw, od, len(news)))
    last[a] = i
for g in ('clock', 'other'):
    v = np.array(R[g]); own, nw, od, n = v.T
    print('%s: %d returns, median gap %d posts by others' % (g, len(v), np.median(n)))
    print('  median cos  own prev %.3f | best news %.3f | best older (matched n) %.3f' % (np.median(own), np.median(nw), np.median(od)))
    print('  news > own (moved off its own last post): %d/%d = %.1f%%' % ((nw > own).sum(), len(v), 100 * (nw > own).mean()))
    print('  news > older control:                     %d/%d = %.1f%%' % ((nw > od).sum(), len(v), 100 * (nw > od).mean()))
    for lo, hi in ((1, 1), (2, 5), (6, 20), (21, 10**6)):
        m = (n >= lo) & (n <= hi)
        if m.sum(): print('  gap %s: n=%d moved %.0f%%, median own %.3f' % (('%d-%d' % (lo, hi)) if hi < 10**6 else '>%d' % (lo - 1), m.sum(), 100 * (nw[m] > own[m]).mean(), np.median(own[m])))
