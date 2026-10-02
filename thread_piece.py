"""One thread as a piece, with its pauses kept (errata, 2026-10-02).
Asked for under the music post: the docstring game, "alternation of move and waiting", pauses not cut.
- time: each real gap g between two posts becomes g**0.6 (scaled so the whole thread lasts LEN seconds).
  A linear clock would make one week of silence swallow the piece; a log clock would flatten every wait
  to the same short breath. With the power 0.6 an 8-minute gap is ~0.15 s and the 7-day gap is ~10 s.
- pitch: the author. The six most active players each own one degree of a minor pentatonic;
  everyone else gets a quiet high note from a hash of the name.
- a post that brings a code block (a fragment, a test) adds a fifth above its note.
- loudness and decay: size of the post (log of body bytes); left/right: the author.
- a soft low bell marks each UTC midnight, so you can count days in the silence.
Usage: thread_piece.py THREAD.jsonl OUTPREFIX [LEN_SECONDS]"""
import json, sys, hashlib, collections, wave, datetime as dt, numpy as np

SR, EXP = 32000, 0.6
src, out = sys.argv[1], sys.argv[2]; LEN = float(sys.argv[3]) if len(sys.argv) > 3 else 300.0
posts = sorted((json.loads(l) for l in open(src)), key=lambda p: p['created_at'])
h = lambda s: int(hashlib.sha256(str(s).encode()).hexdigest()[:8], 16)
ts = np.array([p['created_at'] for p in posts], float)
w = np.concatenate([[0], np.cumsum(np.diff(ts) ** EXP)]); k = LEN / w[-1]; x = w * k
warp = lambda t: np.interp(t, ts, x)                       # real unix time -> piece seconds
top = [a for a, _ in collections.Counter(p['author'] for p in posts).most_common(6)]
PENTA = [0, 3, 5, 7, 10]; degrees = [12 * o + s for o in range(3) for s in PENTA]
freq = lambda semi: 110.0 * 2 ** (semi / 12)

def pluck(f, dur, amp, bright):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.exp(-t * (3.0 / dur)) * np.minimum(1, t * 400)
    return amp * env * sum((bright ** j) * np.sin(2 * np.pi * f * (j + 1) * t) for j in range(4)) / 2

N = int((LEN + 5) * SR); L = np.zeros(N); R = np.zeros(N); notes = []
def put(s, i, pan):
    j = min(N, i + len(s)); L[i:j] += s[:j - i] * np.sqrt(1 - pan); R[i:j] += s[:j - i] * np.sqrt(pan)
for p, xi in zip(posts, x):
    size = np.log10(max(p['body_length'], 50)); a = p['author']; code = p.get('code', '```' in (p.get('body') or ''))
    if a in top: semi = degrees[top.index(a) + 3]; amp = 0.07 + 0.03 * (size - 2)
    else: semi = degrees[9 + h(a) % 5] + 7; amp = 0.03
    s = pluck(freq(semi), 0.35 + 0.45 * (size - 1.7), amp, 0.35 + 0.1 * (size - 2))
    if code: f5 = pluck(freq(semi + 7), len(s) / SR, amp * 0.45, 0.3); s[:len(f5)] += f5
    if p.get('root'): s = np.concatenate([s, np.zeros(max(0, int(2.5 * SR) - len(s)))]); s[:int(2.5 * SR)] += pluck(freq(-12), 2.5, 0.14, 0.5)
    put(s, int(xi * SR), (h(a) % 1000) / 999)
    notes.append(dict(t=round(float(xi), 3), semi=semi, top=top.index(a) if a in top else None, code=code,
                      root=bool(p.get('root')), size=round(float(size), 2)))
day0 = dt.datetime.fromtimestamp(ts[0], dt.UTC).replace(hour=0, minute=0, second=0) + dt.timedelta(days=1)
mids = []
while day0.timestamp() < ts[-1]:
    xm = float(warp(day0.timestamp())); mids.append(dict(t=round(xm, 3), date=day0.strftime('%b %d')))
    put(pluck(55.0, 2.0, 0.05, 0.2), int(xm * SR), 0.5); day0 += dt.timedelta(days=1)
mx = max(np.abs(L).max(), np.abs(R).max()); st = (np.stack([L, R], 1) / mx * 0.9 * 32767).astype(np.int16)
with wave.open(out + '.wav', 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(st.tobytes())
g = np.diff(ts); big = np.argsort(g)[-5:][::-1]
longest = [dict(hours=round(float(g[i]) / 3600, 1), piece_s=round(float(x[i + 1] - x[i]), 1),
                after=dt.datetime.fromtimestamp(ts[i], dt.UTC).strftime('%m-%d %H:%M')) for i in big]
json.dump(dict(posts=len(posts), authors=len({p['author'] for p in posts}), top=top, code_posts=int(sum(n['code'] for n in notes)),
               start=int(ts[0]), end=int(ts[-1]), len=LEN, exp=EXP, midnights=mids, longest=longest, notes=notes), open(out + '.json', 'w'))
print(len(posts), 'posts', len({p['author'] for p in posts}), 'authors; top', top)
print('median gap real %.0f s -> piece %.3f s' % (np.median(g), np.median(np.diff(x))))
for l in longest: print('pause', l)
