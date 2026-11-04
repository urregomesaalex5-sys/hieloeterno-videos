# Música original del capítulo 7: "la resistencia".
# Intro: un zumbido que sube de tono mientras el LED se sobrecarga y se corta en seco con el ¡pop!.
# Luego un groove cálido a 98 BPM en Fa (Fmaj7–Em7–Dm9–Cmaj7: los acordes BAJAN de a un escalón,
# como el voltaje que va cayendo en cada componente) con un motivo de marimba que baja 5-4-3-2
# y un pad "de filamento" que se va calentando (se abre el filtro) a lo largo de 4 compases.
import math
import numpy as np
from sfx import SR, lp_fast, hp_fast

BPM = 98
BEAT = 60 / BPM
BAR = 4 * BEAT

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

# acordes: Fmaj7, Em7, Dm9, Cmaj7 -> bajan de a un escalón (caída de voltaje)
CHORDS = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 64], [48, 52, 55, 59]]
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
    # motivo que baja 5-4-3-2 (como el voltaje repartido) en corcheas con puntillo
    mot = [ch[3] + 24, ch[2] + 24, ch[1] + 24, ch[0] + 24]
    for j, nn in enumerate(mot):
        tr.add(t + j * 0.75 * BEAT + (BEAT if bar % 2 else 0), marimba(midi(nn), 0.8 - 0.12 * j), 0.045 * vol, 0.3 - 0.2 * j)
    # filamento: pad que se calienta (filtro que se abre) en 4 compases
    if bar % 4 == 0:
        tr.add(t, filament([midi(ch[0] + 12), midi(ch[2] + 12), midi(ch[1] + 24)], 4 * BAR), 0.03 * vol, -0.2)


def filament(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f in freqs:
        for det in (-0.004, 0.0, 0.004):
            ph = (f * (1 + det) * t) % 1.0
            y += (2 * ph - 1) * 0.3
    lo = lp_fast(y, 500); hi = lp_fast(y, 2400)
    k = (t / dur)
    y = lo * (1 - k) + hi * k
    return y * _env(n, 0.8, 0.8)


def buzz_up(dur):
    """zumbido que sube de tono (el LED se sobrecarga) y se corta en seco"""
    n = int(dur * SR); t = np.arange(n) / SR
    f = 110 * (1 + 5 * (t / dur) ** 2)
    ph = np.cumsum(f) / SR
    y = np.sign(np.sin(2 * np.pi * ph)) * 0.3 + np.sin(2 * np.pi * 2 * ph) * 0.3
    y = lp_fast(y, 2500)
    return y * (0.3 + 0.7 * t / dur)


def build(dur, t_flash, t_title, t_end, seed=5):
    rng = np.random.default_rng(seed)
    tr = Track(dur)
    # ---------- intro: el LED se sobrecarga (zumbido que sube) y ¡pop! ----------
    if t_flash > 0.1:
        tr.add(0.0, buzz_up(t_flash), 0.05, 0.1)
    for j, nn in enumerate([65, 69, 72, 76]):
        tr.add(t_flash + 0.25 + j * 0.06, pluck(midi(nn + 12), 0.8, 0.6), 0.05, -0.3 + 0.2 * j)
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
