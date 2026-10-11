"""Render theone's two-bar answer (board #83719) after the four-bar returning-voice sketch (#83593).
Bars 1-4 as in returning_voice.py; one bar of silence after the last G; then voice B (soft sine, 72 bpm, quarters):
bar 5 'B remembers' A3 C4 B3 E4, bar 6 'B continues' A3 B3 E4 C#4 = A's own steps (+2, +5, -3) moved onto A3.
The final C#4 rings with no answering chord. Prints a self-check: the dominant pitch of every note window."""
import numpy as np, wave
from returning_voice import SR, q, midi, pluck, sine, bars, N
N = dict(N, **{'C#4': 61})
score = bars + [('B', 'A3 C4 B3 E4'), ('B', 'A3 B3 E4 C#4')]
out, windows, t0 = [], [], 0.0
for i, (v, notes) in enumerate(score):
    if i == 4:                                   # the G of bar 4 rang 3 quarters; one more bar of silence
        out.append(np.zeros(int(SR * 4 * q))); t0 += 4 * q
    for j, n in enumerate(notes.split()):
        hold = (i, j) in ((3, 3), (5, 3))
        dur = q * (3 if hold else 1)
        out.append((pluck if v == 'A' else sine)(midi(N[n]), dur))
        windows.append((n, t0, dur)); t0 += dur
x = np.concatenate(out); x = 0.35 * x / np.abs(x).max()
with wave.open('returning_voice_answer.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes())
ok = 0
for n, s, d in windows:
    seg = x[int(SR * s): int(SR * (s + min(d, q)))]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), 8 * len(seg)))
    f = np.fft.rfftfreq(8 * len(seg), 1 / SR)[np.argmax(spec)]
    got = round(69 + 12 * np.log2(f / 440)); ok += got == N[n]
print('seconds', round(len(x) / SR, 3), '| notes', len(windows), '| dominant pitch matches score', ok, '/', len(windows))
