#!/usr/bin/env python3
# Corte de frases por programación dinámica: elige los silencios que mejor reparten
# el texto a velocidad pareja (sirve cuando [long pause] sale casi igual que las pausas internas).
import sys, json, re, math
import numpy as np
from segment import load, SR
from timeline import PHRASES

x = load(sys.argv[1])
hop = SR // 100
n = len(x) // hop
rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1))
db = 20 * np.log10(rms + 1e-9)
thr = float(sys.argv[2]) if len(sys.argv) > 2 else -38
sil = db < thr
gaps = []
i = 0
while i < n:
    if sil[i]:
        j = i
        while j < n and sil[j]:
            j += 1
        if (j - i) >= 18:
            gaps.append((i / 100, j / 100))
        i = j
    else:
        i += 1
first = next(k for k in range(n) if not sil[k]) / 100
last = (n - next(k for k in range(n) if not sil[n - 1 - k])) / 100
gaps = [g for g in gaps if g[0] > first + 0.3 and g[1] < last - 0.3]
L = [len(re.sub(r'\[[^\]]*\]', '', p[0]).strip()) for p in PHRASES]
speech = (last - first) - 0.45 * (len(PHRASES) - 1)
rate = sum(L) / speech
K = len(PHRASES); G = len(gaps)
INF = 1e18
# estado: (frase k terminada en el gap g)
pts = [first] + [None] * 0
best = [[INF] * (G + 1) for _ in range(K)]
prev = [[-1] * (G + 1) for _ in range(K)]
def start_of(g):
    return first if g < 0 else gaps[g][1]
def cost(k, a, b, glen):
    d = b - a
    exp = L[k] / rate
    return (math.log(max(0.05, d) / exp)) ** 2 * 10 - 2.5 * glen
for g in range(G):
    best[0][g] = cost(0, first, gaps[g][0], gaps[g][1] - gaps[g][0])
for k in range(1, K - 1):
    for g in range(G):
        for h in range(g):
            if best[k - 1][h] >= INF:
                continue
            c = best[k - 1][h] + cost(k, gaps[h][1], gaps[g][0], gaps[g][1] - gaps[g][0])
            if c < best[k][g]:
                best[k][g] = c; prev[k][g] = h
tot = INF; gl = -1
for h in range(G):
    if best[K - 2][h] < INF:
        c = best[K - 2][h] + cost(K - 1, gaps[h][1], last, 0.6)
        if c < tot:
            tot = c; gl = h
sel = [gl]
for k in range(K - 2, 0, -1):
    sel.append(prev[k][sel[-1]])
sel = sel[::-1]
bounds = [first] + [v for g in sel for v in gaps[g]] + [last]
cuts = []
for k in range(K):
    a, b = bounds[2 * k], bounds[2 * k + 1]
    a = max(0, a - 0.04); b = b + 0.08
    sub_ = PHRASES[k][1].replace(' / ', ' ')
    marks = [m.end() for m in re.finditer(r'(\.\.\.|[.!?,:](?= ))', sub_)]
    strong = [m for m in marks if 3 < m < len(sub_) - 3 and sub_[m - 1] in '.!?:']
    ins = [g for g in [(i0 / 100, i1 / 100) for i0, i1 in []]]
    # pausas internas para anclar
    inner = []
    i = int(a * 100)
    while i < int(b * 100):
        if sil[i]:
            j = i
            while j < int(b * 100) and sil[j]:
                j += 1
            if (j - i) >= 12 and i / 100 > a + 0.1 and j / 100 < b - 0.1:
                inner.append((i / 100, j / 100))
            i = j
        else:
            i += 1
    pick = sorted(sorted(inner, key=lambda g: -(g[1] - g[0]))[:len(strong)])
    anchors = []
    if len(pick) == len(strong):
        for m, g in zip(strong, pick):
            anchors.append([m / len(sub_), (g[0] - a) / (b - a), (g[1] - a) / (b - a)])
    cuts.append(dict(i=k, a=round(a, 3), b=round(b, 3), anchors=anchors))
    print(f'{k:2d} {a:7.2f}-{b:7.2f} ({b - a:5.2f}s, {L[k] / (b - a):4.1f} car/s) {sub_[:55]}')
json.dump(cuts, open('voice_cuts.json', 'w'), indent=1)
print('rate', round(rate, 1), 'gaps', G)
