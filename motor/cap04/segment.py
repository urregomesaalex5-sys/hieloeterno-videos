#!/usr/bin/env python3
# Corta la toma de voz en frases buscando los silencios largos ([long pause]).
import sys
import json
import numpy as np
import wave
from timeline import PHRASES

SR = 48000

def load(p):
    w = wave.open(p)
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() > 1:
        x = x.reshape(-1, w.getnchannels()).mean(axis=1)
    return x

def main():
    x = load(sys.argv[1])
    hop = SR // 100
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1))
    db = 20 * np.log10(rms + 1e-9)
    thr = np.percentile(db[db > -80], 30) if (db > -80).any() else -40
    thr = max(min(thr, -32), -50)
    silent = db < thr
    # tramos de silencio
    gaps = []
    i = 0
    while i < n:
        if silent[i]:
            j = i
            while j < n and silent[j]:
                j += 1
            gaps.append((i / 100, j / 100))
            i = j
        else:
            i += 1
    first = next(k for k in range(n) if not silent[k]) / 100
    last = (n - next(k for k in range(n) if not silent[n - 1 - k])) / 100
    inner = [g for g in gaps if g[0] > first + 0.05 and g[1] < last - 0.05]
    need = len(PHRASES) - 1
    big = sorted(inner, key=lambda g: -(g[1] - g[0]))[:need]
    big.sort()
    print('umbral dB', round(thr, 1), 'silencios internos', len(inner), 'duración', round(len(x) / SR, 2))
    print('silencios elegidos (los más largos):', [round(g[1] - g[0], 2) for g in big])
    rest = sorted([g[1] - g[0] for g in inner if g not in big], reverse=True)[:6]
    print('siguientes silencios más largos (no usados):', [round(r, 2) for r in rest])
    bounds = [first] + [v for g in big for v in g] + [last]
    cuts = []
    for k in range(len(PHRASES)):
        a, b = bounds[2 * k], bounds[2 * k + 1]
        a = max(0, a - 0.04); b = b + 0.08
        sub_ = PHRASES[k][1].replace(' / ', ' ')
        import re as _re
        marks = [m.end() for m in _re.finditer(r'(\.\.\.|[.!?,:](?= ))', sub_)]
        marks = [m for m in marks if 3 < m < len(sub_) - 3]
        ins = [g for g in gaps if g[0] > a + 0.1 and g[1] < b - 0.1 and g[1] - g[0] >= 0.12]
        # usar solo las pausas más claras (máximo una por marca fuerte)
        strong = [m for m in marks if sub_[m - 1] in '.!?:']
        pick = sorted(sorted(ins, key=lambda g: -(g[1] - g[0]))[:len(strong)])
        anchors = []
        if len(pick) == len(strong):
            for m, g in zip(strong, pick):
                anchors.append([m / len(sub_), (g[0] - a) / (b - a), (g[1] - a) / (b - a)])
        cuts.append(dict(i=k, a=round(a, 3), b=round(b, 3), anchors=anchors))
        sub = PHRASES[k][1].replace(' / ', ' ')
        print(f'{k:2d} {a:7.2f}-{b:7.2f} ({b - a:5.2f}s, {len(sub) / (b - a):4.1f} car/s) {sub[:60]}')
    json.dump(cuts, open('voice_cuts.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
