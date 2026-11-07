# Música original del capítulo 10: "el transformador".
# Intro: zumbido de 120 Hz que crece cuando se mete el enchufe y se abre en un acorde grande.
# Luego groove a 100 BPM en La menor (Am9–Fmaj7–Cmaj7–G6) con dos ideas de "transformador":
#  - ECO INDUCIDO: cada frase del piano (la bobina 1) la repite una campanita una octava arriba,
#    una corchea después y del otro lado del estéreo (la bobina 2 "copia" lo que pasa en la 1);
#  - bajo ALTERNO: salta entre la nota de abajo y su octava, ida y vuelta, como la corriente alterna.
import math
import numpy as np
from sfx import SR, lp_fast, hp_fast

BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

# acordes: Em9, Cmaj7, G6, D6sus
CHORDS = [[57, 60, 64, 71], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 64]]
ROOTS = [45, 41, 36, 43]
GATE = [1, 1, 0, 1, 1, 0, 1, 0]     # patrón de conmutación del pad (corcheas): contactos cerrados / abiertos

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


def slow_pad(freqs, dur, attack=0.9, tail=0.9):
    """pad que entra despacio y se queda sonando después (la 'inercia' de la bobina)"""
    n = int((dur + tail) * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f in freqs:
        for det in (-0.005, 0.0, 0.006):
            y += np.sin(2 * np.pi * f * (1 + det) * t) * 0.3 + 0.12 * np.sin(4 * np.pi * f * (1 + det) * t)
    e = 1 - np.exp(-t / (attack / 3))
    rel = np.clip((dur + tail - t) / tail, 0, 1) ** 1.5
    return lp_fast(y, 1800) * e * np.minimum(1, rel)


def glide_bass(f0, f1, dur, glide=0.18):
    n = int(dur * SR); t = np.arange(n) / SR
    k = np.clip(t / glide, 0, 1)
    f = f0 * (f1 / f0) ** (k * k * (3 - 2 * k))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.25 * np.sin(2 * ph)
    return y * _env(n, 0.01, 0.1) * (0.8 + 0.2 * np.exp(-t * 3))


def gated_pad(freqs, dur, gate, step):
    """pad que se conmuta todo-o-nada (relé): cada corchea está ON u OFF, con bordes de 4 ms"""
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f in freqs:
        for det in (-0.004, 0.0, 0.005):
            ph = (f * (1 + det) * t) % 1.0
            y += (2 * ph - 1) * 0.25
    y = lp_fast(lp_fast(y, 1500), 1900)
    g = np.zeros(n)
    ns = int(step * SR); edge = int(0.004 * SR)
    for k in range(int(math.ceil(dur / step))):
        if gate[k % len(gate)]:
            i0 = k * ns; i1 = min(n, i0 + int(ns * 0.82))
            if i0 >= n:
                break
            seg = np.ones(i1 - i0)
            e = min(edge, len(seg) // 2)
            if e > 0:
                seg[:e] = np.linspace(0, 1, e); seg[-e:] = np.linspace(1, 0, e)
            g[i0:i1] = seg
    return y * g


_RC = {}
def relay_tick(seed, off=False):
    from sfx import relay_click
    k = (seed % 6, off)
    if k not in _RC:
        _RC[k] = relay_click(seed % 6, off)
    return _RC[k]


def _groove_bar(tr, t, bar, rng, vol=1.0):
    ci = bar % 4
    ch = CHORDS[ci]
    # piano eléctrico en el 1 y en el "y" del 2
    for off, v in ((0.0, 0.7), (1.5 * BEAT, 0.5)):
        for j, nn in enumerate(ch):
            tr.add(t + off + j * 0.008, epiano(midi(nn), 0.8, v), 0.040 * vol, -0.25 + 0.15 * j)
    tr.add(t, slow_pad([midi(n + 12) for n in ch[:3]], BAR, attack=0.6, tail=0.3), 0.030 * vol, 0.0)
    # bajo alterno (corriente alterna): abajo-arriba-abajo-arriba
    for b in range(4):
        nn = ROOTS[ci] + (12 if b % 2 else 0)
        tr.add(t + b * BEAT, bass(midi(nn), BEAT * 0.7), (0.20 if b % 2 == 0 else 0.14) * vol, 0.0)
        if b in (0, 2):
            tr.add(t + b * BEAT, kick(), 0.26 * vol, 0.0)
        if b in (1, 3):
            tr.add(t + b * BEAT, snare_brush(bar * 4 + b), 0.10 * vol, 0.1)
        tr.add(t + (b + 0.5) * BEAT, shaker(bar * 4 + b), 0.05 * vol, 0.3)
    # motivo de marimba (bobina 1, izquierda) y su eco inducido en campanita (bobina 2, derecha)
    if bar % 2 == 1:
        mot = [ch[3] + 12, ch[2] + 12, ch[1] + 12, ch[2] + 12]
        for j, nn in enumerate(mot):
            t0 = t + 2 * BEAT + j * 0.5 * BEAT
            tr.add(t0, marimba(midi(nn), 0.55), 0.034 * vol, -0.45)
            tr.add(t0 + 0.5 * BEAT, bell(midi(nn + 12), 0.5), 0.018 * vol, 0.45)


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


def zing():
    """destello del neón: chispa brillante + nota que cae"""
    n = int(0.9 * SR); t = np.arange(n) / SR
    f = 2600 * np.exp(-t * 2.5) + 600
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 0.5
    nz = np.random.default_rng(3).standard_normal(n)
    y += hp_fast(nz, 5000) * np.exp(-t * 25) * 0.4
    return y


def coil_hum(dur, f0=120):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f0 * t) + 0.3 * np.sin(2 * np.pi * 2 * f0 * t) + 0.1 * np.sin(2 * np.pi * 3 * f0 * t)
    return y * np.minimum(1, t * 8)


def build(dur, t_click, t_title, t_end, seed=10):
    rng = np.random.default_rng(seed)
    tr = Track(dur)
    # zumbido de 120 Hz que crece con el enchufe y se abre en un acorde grande
    tr.add(t_click, coil_hum(1.6) * np.linspace(1, 0, int(1.6 * SR)), 0.05, 0.0)
    for j, nn in enumerate([45, 52, 57, 60, 64, 71]):
        tr.add(t_click + 0.05 + j * 0.012, epiano(midi(nn + 12), 1.8, 0.9), 0.045, -0.3 + 0.12 * j)
    tr.add(t_click + 0.05, pad([midi(n + 12) for n in (45, 52, 57)], 2.0), 0.05, 0.0)
    t = t_title + 0.3; bar = 0
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
