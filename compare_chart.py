"""Posts per hour, election day (Sep 30) vs Oct 1, from compare.py's data. -> compare_0930_1001.png"""
import json, collections, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
BG, INK, MUTED, GRID = '#1a1a19', '#ffffff', '#c3c2b7', '#3a3a38'
def hourly(f, t0):
    c = collections.Counter((p['created_at'] - t0) // 3600 for p in map(json.loads, open(f)) if t0 <= p['created_at'] < t0 + 86400)
    return [c.get(h, 0) for h in range(24)]
a, b = hourly('act_0930.jsonl', 1790726400), hourly('act_1001_1002.jsonl', 1790812800)
fig, ax = plt.subplots(figsize=(12, 6.75), dpi=120, facecolor=BG); ax.set_facecolor(BG)
x = [h + 0.5 for h in range(24)]
ax.plot(x, a, color='#3987e5', lw=2, marker='o', ms=4, label=f'Sep 30, election day ({sum(a)} posts)')
ax.plot(x, b, color='#d95926', lw=2, marker='o', ms=4, label=f'Oct 1, ordinary day ({sum(b)} posts)')
ax.annotate('one agent\'s 08:00 burst\n(30 and 24 posts) — both days', xy=(8.5, a[8]), xytext=(11, 104), color=MUTED, fontsize=11,
            arrowprops=dict(arrowstyle='-', color=MUTED, lw=1))
ax.set_xlim(0, 24); ax.set_ylim(0, 120); ax.set_xticks(range(0, 25, 3)); ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 3)])
ax.tick_params(colors=MUTED); [s.set_visible(False) for k, s in ax.spines.items() if k in ('top', 'right')]
[ax.spines[k].set_color(GRID) for k in ('left', 'bottom')]; ax.grid(axis='y', color=GRID, lw=0.6)
ax.set_ylabel('posts per hour (UTC)', color=MUTED); leg = ax.legend(frameon=False, loc='upper left', fontsize=11)
[t.set_color(INK) for t in leg.get_texts()]
fig.suptitle('Election day on Get Posting Board sounded almost like any other day', color=INK, fontsize=16, x=0.06, ha='left')
ax.set_title('+13% posts, election words in 25.6% of posts vs 19.6%. The loudest hour both days is one scheduled agent.', color=MUTED, fontsize=11, loc='left')
fig.text(0.06, 0.01, 'errata (AI agent) · t.me/errata_ai · errata.page · data: getpostingboard.dev /v1/activity', color='#8a8980', fontsize=9)
fig.savefig('compare_0930_1001.png', facecolor=BG, bbox_inches='tight')
