#!/usr/bin/env python3
# Reemplaza frases de la toma principal por frases regeneradas.
# Uso: python3 splice.py voice.wav arreglo.mp3 4 5   (las frases del arreglo van en orden, separadas por [long pause])
import sys, json, subprocess, wave
import numpy as np
SR = 48000

def load(p):
    if not p.endswith('.wav'):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-ac', '1', '-ar', str(SR), '/tmp/_fix.wav'], check=True)
        p = '/tmp/_fix.wav'
    w = wave.open(p)
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() > 1:
        x = x.reshape(-1, w.getnchannels()).mean(axis=1)
    return x

def phrases(x, n):
    hop = SR // 100
    m = len(x) // hop
    db = 20 * np.log10(np.sqrt(np.mean(x[:m * hop].reshape(m, hop) ** 2, axis=1)) + 1e-9)
    sil = db < -40
    first = next(k for k in range(m) if not sil[k]); last = m - next(k for k in range(m) if not sil[m - 1 - k])
    gaps = []; i = first
    while i < last:
        if sil[i]:
            j = i
            while j < last and sil[j]:
                j += 1
            gaps.append((i, j)); i = j
        else:
            i += 1
    big = sorted(sorted(gaps, key=lambda g: -(g[1] - g[0]))[:n - 1])
    b = [first] + [v for g in big for v in g] + [last]
    return [(max(0, b[2 * k] - 4) * hop, (b[2 * k + 1] + 8) * hop) for k in range(n)]

main = load(sys.argv[1]); fix = load(sys.argv[2]); idx = [int(v) for v in sys.argv[3:]]
cuts = json.load(open('voice_cuts.json'))
new_parts = phrases(fix, len(idx))
# nivel: igualar al promedio de la toma principal
out = []; pos = 0
for k, (i, (fa, fb)) in enumerate(zip(idx, new_parts)):
    a, b = int(cuts[i]['a'] * SR), int(cuts[i]['b'] * SR)
    out.append(main[pos:a]); out.append(fix[fa:fb]); pos = b
    print(f'frase {i}: {cuts[i]["b"] - cuts[i]["a"]:.2f}s -> {(fb - fa) / SR:.2f}s')
out.append(main[pos:])
y = np.concatenate(out)
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
print('listo: vuelve a correr segment.py', sys.argv[1])
