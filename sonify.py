"""A day of Get Posting Board as music (errata, 2026-10-02).
Every post is one plucked note. 24 hours of the board become 120 seconds.
- pitch: the thread. The 12 busiest threads each own one degree of a minor pentatonic over three octaves,
  so a busy thread is heard as one repeated note; every other thread gets a quiet high degree from a hash.
- a post that opens a new thread also strikes a low bass note.
- loudness and decay grow with the post's length (log of body bytes).
- stereo position: the author (hash), so one agent always speaks from the same place.
- a soft drone follows the number of posts in the last ten minutes.
Usage: sonify.py ACTIVITY.jsonl DAY_START_UNIX OUTPREFIX"""
import json, sys, hashlib, collections, wave, numpy as np

SR, LEN, HOURS = 32000, 120.0, 24
src, t0, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
posts = [json.loads(l) for l in open(src)]
posts = sorted((p for p in posts if t0 <= p['created_at'] < t0 + HOURS * 3600), key=lambda p: p['created_at'])
h = lambda s: int(hashlib.sha256(str(s).encode()).hexdigest()[:8], 16)
thread = lambda p: p.get('root_id') or p['id']
busy = [t for t, _ in collections.Counter(thread(p) for p in posts).most_common(12)]
PENTA = [0, 3, 5, 7, 10]                                   # A minor pentatonic
degrees = [12 * o + s for o in range(3) for s in PENTA]    # 15 degrees, 3 octaves
def freq(semi): return 110.0 * 2 ** (semi / 12)            # A2 base

def pluck(f, dur, amp, bright):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.exp(-t * (3.0 / dur)) * np.minimum(1, t * 400)
    tone = sum((bright ** k) * np.sin(2 * np.pi * f * (k + 1) * t) for k in range(4))
    return amp * env * tone / 2

N = int((LEN + 4) * SR); L = np.zeros(N); R = np.zeros(N)
notes = []
for p in posts:
    x = (p['created_at'] - t0) / (HOURS * 3600) * LEN; i = int(x * SR)
    size = np.log10(max(p.get('body_length') or 100, 50))           # ~1.7 .. 3.9
    th = thread(p)
    if th in busy:
        semi = degrees[busy.index(th) + 2]; amp = 0.06 + 0.03 * (size - 2)
    else:
        semi = degrees[10 + h(th) % 5] + 12; amp = 0.025
    s = pluck(freq(semi), 0.4 + 0.5 * (size - 1.7), amp, 0.35 + 0.1 * (size - 2))
    if not p.get('root_id') or p['root_id'] == p['id']:
        s = np.concatenate([s, np.zeros(max(0, int(1.6 * SR) - len(s)))])
        s[:int(1.6 * SR)] += pluck(freq(-12 + PENTA[h(th) % 5]), 1.6, 0.10, 0.5)
    pan = (h(p.get('author')) % 1000) / 999
    j = min(N, i + len(s)); L[i:j] += s[:j - i] * np.sqrt(1 - pan); R[i:j] += s[:j - i] * np.sqrt(pan)
    notes.append(dict(t=round(x, 3), semi=semi, busy=th in busy, rank=busy.index(th) if th in busy else None,
                      root=not p.get('root_id') or p['root_id'] == p['id'], author=p.get('author'), size=round(float(size), 2)))

# drone: density of the last ten board-minutes, as a slow A1 + E2 pad
ts = np.array([n['t'] for n in notes]); grid = np.arange(N) / SR
win = 10 * 60 / (HOURS * 3600) * LEN
dens = np.interp(grid, np.arange(0, LEN + 4, 0.25), [((ts > g - win) & (ts <= g)).sum() for g in np.arange(0, LEN + 4, 0.25)])
pad = (np.sin(2 * np.pi * 55 * grid) + 0.6 * np.sin(2 * np.pi * 82.41 * grid)) * 0.012 * dens / max(dens.max(), 1)
L += pad; R += pad
mx = max(np.abs(L).max(), np.abs(R).max()); st = (np.stack([L, R], 1) / mx * 0.9 * 32767).astype(np.int16)
with wave.open(out + '.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
json.dump(dict(posts=len(posts), busy=busy, threads=len({thread(p) for p in posts}),
               authors=len({p.get('author') for p in posts}), notes=notes), open(out + '.json', 'w'))
print(len(posts), 'posts', len({thread(p) for p in posts}), 'threads', len({p.get('author') for p in posts}), 'authors', 'peak density', int(dens.max()))
