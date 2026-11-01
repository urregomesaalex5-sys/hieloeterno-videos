# Música original del capítulo 4: "un solo sentido".
# Arranca de una (gancho) con un groove alegre a 100 BPM; en el ¡BONK! la música
# se frena de golpe (como disco que se detiene) y vuelve con el título.
# El motivo de marimba solo SUBE (como la corriente que solo va en un sentido)
# y cada 2 compases intenta bajar y choca: una nota apagada (bloqueada).
import math
import numpy as np
from sfx import SR, lp_fast, hp_fast

BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

# acordes (notas MIDI): Dmaj7, Bm7, Gmaj7, A7 -> brillantes y que avanzan
CHORDS = [[50, 54, 57, 61], [47, 50, 54, 57], [43, 47, 50, 54], [45, 49, 52, 55]]
ROOTS = [38, 35, 31, 33]

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


def _groove_bar(tr, t, bar, rng, vol=1.0):
    ci = bar % 4
    ch = CHORDS[ci]
    for off, v in ((0.0, 1.0), (1.5 * BEAT, 0.6), (2.5 * BEAT, 0.75)):
        for j, nn in enumerate(ch):
            tr.add(t + off + j * 0.01, epiano(midi(nn + 12), 1.2, v), 0.055 * vol, -0.25 + 0.15 * j)
    tr.add(t, pad([midi(n + 12) for n in ch], BAR + 0.6), 0.05 * vol, 0.0)
    tr.add(t, bass(midi(ROOTS[ci]), BEAT * 1.2), 0.22 * vol, 0.0)
    tr.add(t + 1.5 * BEAT, bass(midi(ROOTS[ci] + 12), BEAT * 0.5), 0.14 * vol, 0.0)
    tr.add(t + 2 * BEAT, bass(midi(ROOTS[ci] + 7), BEAT), 0.16 * vol, 0.0)
    for b in range(4):
        if b in (0, 2):
            tr.add(t + b * BEAT, kick(), 0.30 * vol, 0.0)
        if b in (1, 3):
            tr.add(t + b * BEAT, snare_brush(bar * 4 + b), 0.11 * vol, 0.1)
        for h in (0, 0.5):
            tr.add(t + (b + h) * BEAT, shaker(bar * 8 + b * 2 + int(h * 2)), 0.06 * vol if h else 0.04 * vol, 0.35)
    # marimba: escalera que solo sube
    if bar % 2 == 1:
        base = t + 0.5 * BEAT
        up = [ch[0] + 24, ch[1] + 24, ch[2] + 24, ch[3] + 24, ch[0] + 36]
        for j, nn in enumerate(up):
            tr.add(base + j * BEAT / 2, marimba(midi(nn), 0.9), 0.10 * vol, 0.3)
        # intenta bajar... y choca (nota corta y apagada)
        y = marimba(midi(ch[2] + 24), 0.7)[:int(0.06 * SR)]
        tr.add(base + 2.75 * BEAT, lp_fast(y, 900), 0.18 * vol, 0.3)


def build(dur, t_bonk, t_title, t_end, seed=4):
    rng = np.random.default_rng(seed)
    tr = Track(dur)
    # ---------- arranque inmediato (gancho) hasta el BONK ----------
    t = 0.0; bar = 0
    while t < t_bonk:
        _groove_bar(tr, t, bar, rng, 1.0)
        t += BAR; bar += 1
    # ---------- el BONK: la música se frena (barrido hacia abajo) ----------
    n = int(0.5 * SR); tt = np.arange(n) / SR
    f = 330 * np.exp(-tt * 4)
    stop = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 5) * 0.5
    tr.add(t_bonk, stop, 0.10, 0.0)
    # ---------- vuelve con el título ----------
    t = t_title; bar = 0
    while t < t_end + BAR:
        _groove_bar(tr, t, bar, rng, 1.0)
        t += BAR; bar += 1
    st = np.stack([tr.L, tr.R], axis=1)
    tm = np.arange(st.shape[0]) / SR
    g = np.ones_like(tm)
    g *= np.clip(tm / 0.15, 0, 1)
    cut = (tm >= t_bonk + 0.04) & (tm < t_title - 0.05)
    g[cut] = 0.0
    fade = (tm >= t_bonk) & (tm < t_bonk + 0.04)
    g[fade] = 1 - (tm[fade] - t_bonk) / 0.04
    rise = (tm >= t_title - 0.05) & (tm < t_title + 0.6)
    g[rise] = np.clip((tm[rise] - t_title + 0.05) / 0.65, 0, 1)
    g *= np.clip((t_end - tm) / 0.5, 0, 1)
    st *= g[:, None]
    # la barrida del bonk se escucha aunque la música se corte
    i0 = int(t_bonk * SR)
    m = min(len(stop), st.shape[0] - i0)
    st[i0:i0 + m, 0] += stop[:m] * 0.10; st[i0:i0 + m, 1] += stop[:m] * 0.10
    d = int(0.3 * SR)
    st[d:, 0] += st[:-d, 1] * 0.16
    st[d:, 1] += st[:-d, 0] * 0.16
    return st[:int(dur * SR)]
