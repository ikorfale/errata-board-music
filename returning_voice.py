"""Render theone's four-bar sketch for the returning-voice idea (board #83593) as audio.
Voice A: soft plucked tone; voice B: soft sine with slow attack. All quarter notes, equal loudness, 72 bpm.
Bar 4 keeps A's timbre but borrows B's intervals (+3, -1, +5 semitones) starting from C4; the last G is left hanging."""
import numpy as np, wave, sys
SR, BPM = 44100, 72
q = 60 / BPM
def midi(n): return 440 * 2 ** ((n - 69) / 12)
N = {'A3': 57, 'B3': 59, 'C4': 60, 'D4': 62, 'Eb4': 63, 'E4': 64, 'G4': 67}
bars = [('A', 'C4 D4 G4 E4'), ('B', 'A3 C4 B3 E4'), ('A', 'C4 D4 G4 E4'), ('A', 'C4 Eb4 D4 G4')]
def pluck(f, dur):
    t = np.arange(int(SR * dur)) / SR
    return (np.sin(2*np.pi*f*t) + 0.3*np.sin(4*np.pi*f*t) + 0.1*np.sin(6*np.pi*f*t)) * np.exp(-3.0 * t)
def sine(f, dur):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 0.12) * np.exp(-1.2 * t)
    return np.sin(2*np.pi*f*t) * env * 1.15
out = []
for i, (v, notes) in enumerate(bars):
    for j, n in enumerate(notes.split()):
        last = i == 3 and j == 3
        dur = q * (3 if last else 1)            # let the final G ring out instead of resolving
        tone = (pluck if v == 'A' else sine)(midi(N[n]), dur)
        out.append(tone)
x = np.concatenate(out); x = 0.35 * x / np.abs(x).max()
with wave.open('returning_voice.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes())
print('seconds', round(len(x) / SR, 2))
