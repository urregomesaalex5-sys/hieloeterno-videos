# Efectos de sonido sintetizados estilo ASMR (sin música). 48 kHz estéreo.
import math
import numpy as np

SR = 48000
_rng = np.random.default_rng(11)

def _t(dur):
    return np.arange(int(SR * dur)) / SR

def _noise(n, seed=None):
    r = np.random.default_rng(seed) if seed is not None else _rng
    return r.standard_normal(n)

def lowpass(x, fc):
    a = math.exp(-2 * math.pi * fc / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y

def lp_fast(x, fc):
    # filtro de un polo vectorizado con scipy si está
    try:
        from scipy.signal import lfilter
        a = math.exp(-2 * math.pi * fc / SR)
        return lfilter([1 - a], [1, -a], x)
    except Exception:
        return lowpass(x, fc)

def hp_fast(x, fc):
    return x - lp_fast(x, fc)

def bandpass(x, f0, q=4.0):
    from scipy.signal import iirpeak, lfilter
    b, a = iirpeak(f0 / (SR / 2), q)
    return lfilter(b, a, x)

def env_exp(n, decay):
    return np.exp(-np.arange(n) / SR * decay)

def norm(x, peak=1.0):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak

# ---------- sonidos ----------
def step_wood(seed=0, heavy=1.0):
    n = int(SR * 0.16)
    t = _t(0.16)
    thump = np.sin(2 * np.pi * (95 + 40 * np.exp(-t * 40)) * t) * env_exp(n, 38) * heavy
    click = hp_fast(_noise(n, seed), 1500) * env_exp(n, 120) * 0.5
    body = bandpass(_noise(n, seed + 1), 420, 3) * env_exp(n, 30) * 0.9
    return norm(thump * 0.9 + click + body, 0.8)

def block_place(seed=0, pitch=1.0):
    n = int(SR * 0.22)
    t = _t(0.22)
    x = _noise(n, seed)
    a = bandpass(x, 900 * pitch, 6) * env_exp(n, 35)
    b = bandpass(x, 1900 * pitch, 8) * env_exp(n, 60) * 0.6
    thud = np.sin(2 * np.pi * 140 * pitch * t) * env_exp(n, 45) * 0.8
    click = hp_fast(x, 3000) * env_exp(n, 250) * 0.6
    return norm(a + b + thud + click, 0.85)

def whoosh(dur=0.45, f0=400, f1=1800, seed=0):
    n = int(SR * dur)
    x = _noise(n, seed)
    from scipy.signal import lfilter
    out = np.zeros(n)
    # barrido por bloques
    blk = 512
    for i in range(0, n, blk):
        k = i / n
        f = f0 + (f1 - f0) * k
        out[i:i + blk] = bandpass(x[i:i + blk + 0], f, 2.0)[:len(out[i:i + blk])]
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    return norm(lp_fast(out, 5000) * e, 0.6)

def snap(seed=0):
    n = int(SR * 0.09)
    x = _noise(n, seed)
    a = hp_fast(x, 2500) * env_exp(n, 160)
    b = bandpass(x, 1800, 10) * env_exp(n, 90) * 1.5
    return norm(a + b, 0.95)

def clap(seed=0):
    n = int(SR * 0.25)
    x = _noise(n, seed)
    e = np.zeros(n)
    for k, off in enumerate([0, 0.008, 0.016, 0.026]):
        i = int(off * SR)
        e[i:] += np.exp(-np.arange(n - i) / SR * (180 if k < 3 else 22)) * (0.7 if k < 3 else 1.0)
    y = bandpass(x, 1200, 1.2) * e
    return norm(y, 0.9)

def click(seed=0, f=2500):
    n = int(SR * 0.05)
    x = _noise(n, seed)
    return norm(bandpass(x, f, 6) * env_exp(n, 220) + hp_fast(x, 4000) * env_exp(n, 500) * 0.4, 0.7)

def switch(seed=0):
    a = click(seed, 2200); b = click(seed + 1, 3200)
    out = np.zeros(int(SR * 0.12))
    out[:len(a)] += a
    i = int(0.045 * SR); out[i:i + len(b)] += b * 0.8
    return out

def pop(f0=500, f1=1200, dur=0.12):
    t = _t(dur)
    f = f0 + (f1 - f0) * (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return norm(np.sin(ph) * env_exp(len(t), 25), 0.6)

def bell(f=1320, dur=1.6):
    t = _t(dur); n = len(t)
    y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * env_exp(n, 6)
         + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * env_exp(n, 12)) * env_exp(n, 3.2)
    return norm(y, 0.55)

def tink(f=3800, dur=0.35, seed=0):
    t = _t(dur); n = len(t)
    y = np.sin(2 * np.pi * f * t) * env_exp(n, 18) + 0.5 * np.sin(2 * np.pi * f * 1.51 * t) * env_exp(n, 30)
    y += hp_fast(_noise(n, seed), 5000) * env_exp(n, 400) * 0.3
    return norm(y, 0.5)

def roll(dur=0.5, seed=0):
    """bolita metálica rodando dentro de un tubito"""
    n = int(SR * dur)
    x = _noise(n, seed)
    r = bandpass(x, 2600, 3) * 0.25
    # traqueteo: microclicks
    out = r.copy()
    rng = np.random.default_rng(seed)
    k = 0.0
    while k < dur - 0.02:
        i = int(k * SR)
        c = tink(rng.uniform(3200, 5200), 0.04, seed + i)
        out[i:i + len(c)] += c[:len(out[i:i + len(c)])] * 0.35
        k += rng.uniform(0.018, 0.04)
    e = np.minimum(1, np.linspace(0, 6, n)) * np.minimum(1, np.linspace(6, 0, n))
    return norm(out * e, 0.5)

def thud(seed=0, f=70):
    n = int(SR * 0.35); t = _t(0.35)
    y = np.sin(2 * np.pi * (f + 60 * np.exp(-t * 30)) * t) * env_exp(n, 14)
    y += lp_fast(_noise(n, seed), 600) * env_exp(n, 25) * 1.2
    return norm(y, 0.9)

def crumble(seed=0, dur=0.6):
    n = int(SR * dur)
    out = np.zeros(n)
    rng = np.random.default_rng(seed)
    for k in range(9):
        i = int(rng.uniform(0, dur - 0.22) * SR)
        b = block_place(seed + k, rng.uniform(0.8, 1.4)) * rng.uniform(0.3, 0.7)
        out[i:i + len(b)] += b[:len(out[i:i + len(b)])]
    return norm(out, 0.8)

def tv_off():
    t = _t(0.6); n = len(t)
    f = 6000 * np.exp(-t * 7) + 200
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * env_exp(n, 6) * 0.4
    y += hp_fast(_noise(n, 3), 3000) * env_exp(n, 20) * 0.3
    c = click(5, 1800)
    y[:len(c)] += c
    return norm(y, 0.6)

def hum(dur=1.0, f=55):
    t = _t(dur)
    y = np.sin(2 * np.pi * f * t) * 0.5 + 0.2 * np.sin(2 * np.pi * f * 2 * t) + 0.1 * np.sin(2 * np.pi * f * 3 * t)
    e = np.minimum(1, t / 0.2) * np.minimum(1, (dur - t) / 0.3)
    return y * e * 0.25

def zap_on():
    """encendido de pantalla/LED: brillo suave"""
    t = _t(0.5); n = len(t)
    y = np.sin(2 * np.pi * 880 * t) * env_exp(n, 9) * 0.4 + np.sin(2 * np.pi * 1320 * t) * env_exp(n, 12) * 0.3
    y += hp_fast(_noise(n, 9), 6000) * env_exp(n, 30) * 0.15
    return norm(y, 0.5)

def float_drone(dur=3.0):
    """aire suave de 'sin gravedad'"""
    n = int(SR * dur); t = _t(dur)
    x = lp_fast(_noise(n, 21), 900)
    x = x / (np.max(np.abs(x)) + 1e-9)
    e = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.4)
    wob = 0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t)
    return x * e * wob * 0.25

def boing(f0=180, f1=420, dur=0.35):
    t = _t(dur)
    f = f0 + (f1 - f0) * np.sin(np.pi * t / dur) + 40 * np.sin(2 * np.pi * 18 * t) * np.exp(-t * 8)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return norm(np.sin(ph) * env_exp(len(t), 7), 0.5)

def marker(dur=0.4, seed=0):
    n = int(SR * dur)
    x = bandpass(_noise(n, seed), 3500, 1.5)
    e = 0.6 + 0.4 * np.abs(np.sin(np.linspace(0, 9, n)))
    e *= np.minimum(1, np.linspace(0, 10, n)) * np.minimum(1, np.linspace(10, 0, n))
    return norm(x * e, 0.25)


class Mixer:
    def __init__(self, dur):
        self.n = int(SR * dur) + SR
        self.L = np.zeros(self.n); self.R = np.zeros(self.n)

    def add(self, t, snd, gain=1.0, pan=0.0):
        """pan -1 izquierda .. 1 derecha"""
        if snd is None:
            return
        i = int(t * SR)
        if i < 0:
            snd = snd[-i:]; i = 0
        m = min(len(snd), self.n - i)
        if m <= 0:
            return
        a = (pan + 1) * math.pi / 4
        self.L[i:i + m] += snd[:m] * gain * math.cos(a)
        self.R[i:i + m] += snd[:m] * gain * math.sin(a)

    def stereo(self):
        return np.stack([self.L, self.R], axis=1)
