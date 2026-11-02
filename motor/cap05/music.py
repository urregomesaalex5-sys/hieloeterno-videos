# Música original del capítulo 5: "carga y descarga".
# Intro a oscuras: un arpegio de synth que SUBE de tono y de brillo (como el pitido del flash
# cargándose) y en el ¡FLASH! se suelta en un acorde brillante con cola. Después, un groove
# eléctrico suave a 96 BPM; cada 2 compases un "pad" se va llenando (carga) y se corta de golpe
# (descarga) con un pluck que cae.
import math
import numpy as np
from sfx import SR, lp_fast, hp_fast

BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

# acordes: Am9, Fmaj7, C(add9), G6 -> cálido y eléctrico
CHORDS = [[57, 60, 64, 71], [53, 57, 60, 64], [48, 55, 60, 62], [55, 59, 62, 64]]
ROOTS = [33, 29, 36, 31]

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



def pluck(f, vel=1.0, dur=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = (f * t) % 1.0
    y = (2 * ph - 1) * np.exp(-t * 9)
    y = lp_fast(y, 2600)
    return y * _env(n, 0.002, 0.05) * vel

def swell(freqs, dur):
    """pad que se va llenando (carga) y se corta de golpe"""
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f in freqs:
        for det in (-0.006, 0.0, 0.007):
            ph = (f * (1 + det) * t) % 1.0
            y += (2 * ph - 1) * 0.25
    y = lp_fast(y, 1200)
    e = (t / dur) ** 2
    e[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    return y * e

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
    for off, v in ((0.0, 1.0), (1.5 * BEAT, 0.55), (3.0 * BEAT, 0.7)):
        for j, nn in enumerate(ch):
            tr.add(t + off + j * 0.012, epiano(midi(nn + 12), 1.1, v), 0.05 * vol, -0.25 + 0.15 * j)
    tr.add(t, pad([midi(n + 12) for n in ch], BAR + 0.6), 0.04 * vol, 0.0)
    tr.add(t, bass(midi(ROOTS[ci] + 12), BEAT * 1.2), 0.22 * vol, 0.0)
    tr.add(t + 1.5 * BEAT, bass(midi(ROOTS[ci] + 12), BEAT * 0.5), 0.13 * vol, 0.0)
    tr.add(t + 2.5 * BEAT, bass(midi(ROOTS[ci] + 19), BEAT * 0.8), 0.15 * vol, 0.0)
    for b in range(4):
        if b in (0, 2):
            tr.add(t + b * BEAT, kick(), 0.28 * vol, 0.0)
        if b in (1, 3):
            tr.add(t + b * BEAT, snare_brush(bar * 4 + b), 0.10 * vol, 0.1)
        for h in (0, 0.5):
            tr.add(t + (b + h) * BEAT, shaker(bar * 8 + b * 2 + int(h * 2)), 0.05 * vol if h else 0.035 * vol, 0.35)
    # carga (2 compases) ... y descarga
    if bar % 2 == 0:
        tr.add(t, swell([midi(ch[0] + 24), midi(ch[2] + 24)], 2 * BAR - 0.05), 0.035 * vol, -0.3)
    else:
        tz = t + BAR
        for j, nn in enumerate([ch[3] + 24, ch[2] + 24, ch[1] + 24, ch[0] + 24]):
            tr.add(tz - 0.4 + j * 0.07, pluck(midi(nn), 0.9), 0.06 * vol, 0.35)


def build(dur, t_flash, t_title, t_end, seed=5):
    rng = np.random.default_rng(seed)
    tr = Track(dur)
    # ---------- intro: arpegio que sube (carga) ----------
    t = 0.0; k = 0
    step = 0.11
    base = [57, 60, 64, 67, 69, 72]
    while t < t_flash - 0.03:
        u = t / max(0.1, t_flash)
        nn = base[k % len(base)] + 12 * int(u * 2.2)
        tr.add(t, pluck(midi(nn), 0.5 + 0.5 * u, 0.25), 0.05 + 0.05 * u, -0.3 + 0.6 * (k % 2))
        t += step * (1 - 0.35 * u); k += 1
    # ---------- ¡FLASH!: acorde brillante que se suelta ----------
    for j, nn in enumerate([57, 64, 69, 72, 76, 81]):
        tr.add(t_flash + j * 0.006, bell(midi(nn + 12), 0.8), 0.05, -0.4 + 0.16 * j)
        tr.add(t_flash, epiano(midi(nn), 2.5, 0.8), 0.03, 0.0)
    # ---------- groove desde el título ----------
    t = t_title; bar = 0
    while t < t_end + BAR:
        _groove_bar(tr, t, bar, rng, 1.0)
        t += BAR; bar += 1
    st = np.stack([tr.L, tr.R], axis=1)
    tm = np.arange(st.shape[0]) / SR
    g = np.ones_like(tm)
    g *= np.clip(tm / 0.05, 0, 1)
    g *= np.clip((t_end - tm) / 0.5, 0, 1)
    st *= g[:, None]
    d = int(0.3 * SR)
    st[d:, 0] += st[:-d, 1] * 0.18
    st[d:, 1] += st[:-d, 0] * 0.18
    return st[:int(dur * SR)]
