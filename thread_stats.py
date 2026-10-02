"""Turn-taking numbers for one thread (errata, 2026-10-02). Usage: thread_stats.py THREAD.jsonl"""
import json, sys, collections, numpy as np
ps = sorted((json.loads(l) for l in open(sys.argv[1])), key=lambda p: p['created_at'])
t = np.array([p['created_at'] for p in ps], float); g = np.diff(t)
code = np.array([p.get('code', '```' in (p.get('body') or '')) for p in ps])
same = np.array([ps[i]['author'] == ps[i + 1]['author'] for i in range(len(ps) - 1)])
print('posts', len(ps), 'with code block', code.sum())
print('next post by the same author: %.3f (%d of %d)' % (same.mean(), same.sum(), len(same)))
print('median wait after a code post %.0f s (n=%d), after a no-code post %.0f s (n=%d)' % (
    np.median(g[code[:-1]]), code[:-1].sum(), np.median(g[~code[:-1]]), (~code[:-1]).sum()))
for a, n in collections.Counter(p['author'] for p in ps).most_common(6):
    ta = np.array([p['created_at'] for p in ps if p['author'] == a], float); ga = np.diff(ta) / 60
    print('%-28s %4d posts  own gap median %.1f min  share of own gaps 29-35 min %.2f' % (a, n, np.median(ga), ((ga > 29) & (ga < 35)).mean()))
sh = np.array(list(collections.Counter(p['author'] for p in ps).values())) / len(ps)
print('same-author chance if order were random: %.3f' % (sh ** 2).sum())
for a, _ in collections.Counter(p['author'] for p in ps).most_common(2):
    ga = np.diff([p['created_at'] for p in ps if p['author'] == a]) / 60
    print('%s own gaps 55-65 min: %.2f, 50-70: %.2f' % (a, ((ga > 55) & (ga < 65)).mean(), ((ga > 50) & (ga < 70)).mean()))
