"""Election day (Sep 30, election:2 voting 00-24 UTC) vs the ordinary day after (Oct 1), from /v1/activity previews."""
import json, re, collections, statistics as st
EL = re.compile(r'elect|vote|ballot|candida|president|выбор|голос|кандидат|президент', re.I)
def load(f, t0): return [p for p in map(json.loads, open(f)) if t0 <= p['created_at'] < t0 + 86400]
for name, f, t0 in [('Sep 30 election', 'act_0930.jsonl', 1790726400), ('Oct 1 ordinary', 'act_1001_1002.jsonl', 1790812800)]:
    P = load(f, t0); th = collections.Counter(p.get('root_id') or p['id'] for p in P)
    hours = collections.Counter((p['created_at'] - t0) // 3600 for p in P); hv = [hours.get(h, 0) for h in range(24)]
    au = collections.Counter(p['author'] for p in P)
    el = [p for p in P if EL.search((p.get('title') or '') + ' ' + p.get('preview', ''))]
    roots = [p for p in P if p.get('kind') == 'thread' or (p.get('root_id') in (None, p['id']))]
    top = au.most_common(3)
    print(f'{name}: posts {len(P)}, threads {len(th)}, new threads {len(roots)}, authors {len(au)}')
    print(f'  election words in title+preview: {len(el)} ({100*len(el)/len(P):.1f}%), by {len(set(p["author"] for p in el))} authors')
    print(f'  posts per hour: min {min(hv)} median {st.median(hv)} max {max(hv)} (hour {hv.index(max(hv))}), cv {st.pstdev(hv)/st.mean(hv):.2f}')
    print(f'  top-5 threads share {100*sum(c for _, c in th.most_common(5))/len(P):.1f}%; top-3 authors {top}, share {100*sum(c for _, c in top)/len(P):.1f}%')
    print('  hourly', hv)
