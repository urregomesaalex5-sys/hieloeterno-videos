# Música original del capítulo 3: suave, de fondo, con tema de "gravedad".
# Intro flotante (sin ritmo) mientras no hay gravedad; al chasquido todo "cae"
# y entra un groove lo-fi tranquilo a 92 BPM con acordes descendentes y una
# marimba que rebota como una bolita.
import math
import numpy as np
from sfx import SR, lp_fast, hp_fast

BPM = 92
BEAT = 60 / BPM
BAR = 4 * BEAT

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

# acordes (notas MIDI): Fmaj7, Em7, Dm7, Cmaj7 -> bajan como algo que cae
CHORDS = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
ROOTS = [41, 40, 38, 36]

def _env(n, a, r):
    e = np.ones(n)
    na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    if nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e

def epiano(f, dur, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3) \
        + 0.12 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 6)
    y *= np.exp(-t * 1.6) * (1 + 0.06 * np.sin(2 * np.pi * 4.5 * t))
    return y * _env(n, 0.005, 0.15) * vel

def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f in freqs:
        for det in (-0.004, 0.0, 0.005):
            ph = (f * (1 + det) * t) % 1.0
            y += (2 * ph - 1) * 0.3
    y = lp_fast(lp_fast(y, 700), 900)
    return y * _env(n, min(1.2, dur * 0.4), min(1.2, dur * 0.4))

def bass(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 2 * f * t)
    return y * np.exp(-t * 2.2) * _env(n, 0.01, 0.08)

def marimba(f, vel=1.0):
    dur = 0.6; n = int(dur * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.4 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 22)
    return y * _env(n, 0.002, 0.05) * vel

def bell(f, vel=1.0):
    dur = 2.5; n = int(dur * SR); t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t * 3)) * np.exp(-t * 1.4)
    return y * _env(n, 0.003, 0.3) * vel

def kick():
    n = int(0.25 * SR); t = np.arange(n) / SR
    f = 48 + 70 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)

def shaker(seed):
    n = int(0.06 * SR)
    x = np.random.default_rng(seed).standard_normal(n)
    return hp_fast(x, 6000) * np.exp(-np.arange(n) / SR * 70) * 0.5

def snare_brush(seed):
    n = int(0.18 * SR)
    x = np.random.default_rng(seed).standard_normal(n)
    return lp_fast(hp_fast(x, 1500), 6000) * np.exp(-np.arange(n) / SR * 22) * 0.5


class Track:
    def __init__(self, dur):
        self.n = int(dur * SR) + SR * 3
        self.L = np.zeros(self.n); self.R = np.zeros(self.n)

    def add(self, t, y, g=1.0, pan=0.0):
        i = int(t * SR)
        if i >= self.n or i + len(y) <= 0:
            return
        if i < 0:
            y = y[-i:]; i = 0
        m = min(len(y), self.n - i)
        a = (pan + 1) * math.pi / 4
        self.L[i:i + m] += y[:m] * g * math.cos(a)
        self.R[i:i + m] += y[:m] * g * math.sin(a)


def build(dur, t_snap, t_groove, t_end, seed=3):
    rng = np.random.default_rng(seed)
    tr = Track(dur)
    # ---------- intro flotante: pad lento + campanitas que flotan ----------
    t = 0.0; k = 0
    while t < t_snap:
        ch = CHORDS[[0, 3][k % 2]]
        d = min(4.0, t_snap - t + 1.5)
        tr.add(t, pad([midi(n + 12) for n in ch], d), 0.22, 0.0)
        t += 3.2; k += 1
    penta = [72, 74, 76, 79, 81, 84]
    t = 0.4
    while t < t_snap - 0.3:
        tr.add(t, bell(midi(int(rng.choice(penta)))), 0.09, float(rng.uniform(-0.6, 0.6)))
        t += float(rng.uniform(0.6, 1.3))
    # ---------- el chasquido: todo cae (barrido descendente) ----------
    n = int(0.9 * SR); tt = np.arange(n) / SR
    f = 880 * np.exp(-tt * 2.6)
    fall = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3) * 0.5
    tr.add(t_snap, fall, 0.12, 0.0)
    # ---------- groove ----------
    bar = 0
    t = t_groove
    motif_falls = [84, 81, 79, 76, 74, 72]      # bolita que cae
    while t < t_end + BAR:
        ci = bar % 4
        ch = CHORDS[ci]
        # acordes de piano eléctrico: en 1 y en el "y" del 3
        for off, v in ((0.0, 1.0), (2.5 * BEAT, 0.7)):
            for j, nn in enumerate(ch):
                tr.add(t + off + j * 0.012, epiano(midi(nn + 12), 1.6, v), 0.06, -0.25 + 0.15 * j)
        # pad suave de fondo
        tr.add(t, pad([midi(n + 12) for n in ch], BAR + 0.6), 0.06, 0.0)
        # bajo
        tr.add(t, bass(midi(ROOTS[ci]), BEAT * 1.5), 0.22, 0.0)
        tr.add(t + 2 * BEAT, bass(midi(ROOTS[ci] + (7 if ci % 2 == 0 else 12)), BEAT), 0.16, 0.0)
        # batería muy suave
        for b in range(4):
            if b in (0, 2):
                tr.add(t + b * BEAT, kick(), 0.30, 0.0)
            if b in (1, 3):
                tr.add(t + b * BEAT, snare_brush(bar * 4 + b), 0.10, 0.1)
            for h in (0, 0.5):
                tr.add(t + (b + h) * BEAT, shaker(bar * 8 + b * 2 + int(h * 2)), 0.06 if h else 0.04, 0.35)
        # marimba: cada 2 compases una bolita que cae y rebota
        if bar % 2 == 1:
            base = t + 0.5 * BEAT
            for j, nn in enumerate(motif_falls[:4]):
                tr.add(base + j * BEAT / 2, marimba(midi(nn - (ci == 3) * 0)), 0.11, 0.3)
            # rebotes: misma nota con intervalos cada vez más cortos
            b0 = base + 2.2 * BEAT; gap = 0.32
            for j in range(5):
                tr.add(b0, marimba(midi(ch[0] + 24), 0.8 * (0.75 ** j)), 0.10, 0.3)
                b0 += gap; gap *= 0.62
        t += BAR; bar += 1
    st = np.stack([tr.L, tr.R], axis=1)
    # entrada suave del groove y salida en el chasquido final
    tm = np.arange(st.shape[0]) / SR
    g = np.ones_like(tm)
    g *= np.clip((tm - t_groove + 0.2) / 1.5, 0, 1) * (tm >= t_groove - 0.2) + (tm < t_snap + 0.9) * 1.0
    g = np.clip(g, 0, 1)
    g *= np.clip((t_end - tm) / 0.5, 0, 1)
    st *= g[:, None]
    # un poco de "aire": eco simple
    d = int(0.33 * SR)
    st[d:, 0] += st[:-d, 1] * 0.18
    st[d:, 1] += st[:-d, 0] * 0.18
    return st[:int(dur * SR)]
