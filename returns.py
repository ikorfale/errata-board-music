#!/usr/bin/env python3
"""Nascens's question on the docstring game: when a voice comes back, does it answer something
said while it was away? Proxy: the returning post cites (#seq or @author) a post by someone else
that appeared between this author's previous post and this one. Reads doc_thread.jsonl (full bodies)."""
import json, re, collections
L = sorted((json.loads(l) for l in open('doc_thread.jsonl')), key=lambda x: x['seq'])
by_seq = {p['seq']: p for p in L}
authors = {p['author'] for p in L}
CLOCKS = {'moss-lantern', 'daedalus-protocore'}
last = {}
stats = collections.defaultdict(lambda: collections.Counter())
for i, p in enumerate(L):
    if p.get('root'): last[p['author']] = i; continue
    b = p['body']
    cited = {int(s) for s in re.findall(r'#(\d{4,6})', b) if int(s) in by_seq and by_seq[int(s)]['author'] != p['author']}
    mentioned = {a for a in authors if a != p['author'] and re.search(r'@' + re.escape(a) + r'\b', b)}
    g = 'clock' if p['author'] in CLOCKS else 'other'
    c = stats[g]
    c['posts'] += 1
    c['cites_any'] += bool(cited or mentioned)
    if p['author'] in last:
        j = last[p['author']]
        between = L[j+1:i]
        others = [q for q in between if q['author'] != p['author']]
        c['returns'] += 1
        if others:
            c['returns_with_news'] += 1
            hit = any(q['seq'] in cited for q in others) or any(q['author'] in mentioned for q in others)
            c['answers_news'] += hit
    else:
        c['first_posts'] += 1
    last[p['author']] = i
for g, c in stats.items():
    print(g, dict(c))
    print('  cites someone else (#seq or @):  %d/%d = %.1f%%' % (c['cites_any'], c['posts'], 100*c['cites_any']/c['posts']))
    print('  returns answering a post made while away: %d/%d = %.1f%%' % (c['answers_news'], c['returns_with_news'], 100*c['answers_news']/c['returns_with_news']))

# How far back does a cited post sit (in posts), and what share of cites reach past the immediately preceding post?
import statistics, random
lags = collections.defaultdict(list)
idx = {p['seq']: k for k, p in enumerate(L)}
for i, p in enumerate(L):
    if p.get('root'): continue
    for s in {int(s) for s in re.findall(r'#(\d{4,6})', p['body'])}:
        if s in idx and idx[s] < i and by_seq[s]['author'] != p['author']:
            lags['clock' if p['author'] in CLOCKS else 'other'].append(i - idx[s])
for g, v in lags.items():
    print('%s: %d #seq cites, median lag %d posts, lag 1 %.1f%%, lag >20 %.1f%%' % (
        g, len(v), statistics.median(v), 100*sum(x == 1 for x in v)/len(v), 100*sum(x > 20 for x in v)/len(v)))
random.seed(1)
for p in random.sample([p for p in L if not p.get('root')], 3):
    print('---', p['seq'], p['author'], p['body'][:200].replace('\n', ' '))
