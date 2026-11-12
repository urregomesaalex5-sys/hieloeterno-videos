#!/usr/bin/env python3
# Inserta una frase nueva (archivo aparte) en la toma, después de la frase 'after'.
# Uso: python3 insert_phrase.py voice_orig.wav voice_cuts_orig.json frase.mp3 1  -> voice.wav + voice_cuts.json
import sys, json, subprocess, wave
import numpy as np
SR = 48000
def load(p):
    if not p.endswith('.wav'):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-ac', '1', '-ar', str(SR), '/tmp/_ins.wav'], check=True)
        p = '/tmp/_ins.wav'
    w = wave.open(p)
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() > 1:
        x = x.reshape(-1, w.getnchannels()).mean(axis=1)
    return x
main = load(sys.argv[1]); cuts = json.load(open(sys.argv[2])); fr = load(sys.argv[3]); after = int(sys.argv[4])
hop = SR // 100
m = len(fr) // hop
db = 20 * np.log10(np.sqrt(np.mean(fr[:m * hop].reshape(m, hop) ** 2, axis=1)) + 1e-9)
act = np.where(db > -40)[0]
fa, fb = max(0, act[0] - 4) * hop, min(len(fr), (act[-1] + 8) * hop)
seg = fr[fa:fb]
# igualar nivel con la toma
def lvl(x):
    r = np.sqrt(np.mean(x[:len(x) // hop * hop].reshape(-1, hop) ** 2, axis=1)); return np.median(r[r > 0.01])
seg = seg * (lvl(main) / (lvl(seg) + 1e-9))
gap = np.zeros(int(0.35 * SR))
pos = int(cuts[after]['b'] * SR)
ins = np.concatenate([gap, seg, gap])
y = np.concatenate([main[:pos], ins, main[pos:]])
shift = len(ins) / SR
new = dict(i=after + 1, a=round(cuts[after]['b'] + 0.35, 3), b=round(cuts[after]['b'] + 0.35 + len(seg) / SR, 3), anchors=[])
out = cuts[:after + 1] + [new] + [dict(c, a=round(c['a'] + shift, 3), b=round(c['b'] + shift, 3)) for c in cuts[after + 1:]]
for k, c in enumerate(out):
    c['i'] = k
w = wave.open('voice.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
json.dump(out, open('voice_cuts.json', 'w'), indent=1)
print('frase nueva', round(len(seg) / SR, 2), 's; toma total', round(len(y) / SR, 2), 's')
