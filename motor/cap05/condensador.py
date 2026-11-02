# Dibujos del capítulo 5: el condensador (cámara con flash, condensadores por tipo,
# placas, carrera pila vs condensador, celular con MLCC, letreros).
import math
import random
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
from diagrams import L, label

CURR = D.CURR
WIRE = D.WIRE
GREEN = (61, 220, 132)
RED = (255, 80, 90)
ELEC = (110, 175, 255)       # electrones
PLUS = (255, 120, 120)       # cargas +
INSUL = (255, 214, 90)       # aislante
METAL = (200, 206, 216)

_cache = {}
def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


# ---------------- Cámara antigua con flash ----------------
CAM_W, CAM_H = 320, 220

def camera_img(ready=0.0, xray=0.0, charge=0.0, flash=0.0):
    key = ('cam', round(ready, 1), round(xray, 2), round(charge, 1), round(flash, 1))
    def mk():
        l = L(CAM_W, CAM_H)
        a = int(255 * (1 - 0.75 * xray))
        body = (46, 48, 56, a)
        # cuerpo
        l.rrect([10, 50, 310, 205], 22, fill=body, outline=(150, 156, 168, 255), width=5)
        l.rrect([10, 50, 310, 92], 22, fill=(186, 190, 198, a))
        l.rect([10, 72, 310, 92], fill=(186, 190, 198, a))
        # caja del flash arriba
        l.rrect([30, 16, 140, 60], 10, fill=(70, 72, 82, a), outline=(150, 156, 168, 255), width=4)
        fc = tuple(int(200 + 55 * flash) for _ in range(3))
        l.rrect([42, 24, 128, 52], 6, fill=(fc[0], fc[1], int(150 + 105 * flash), 255))
        # botón disparador
        l.rrect([240, 34, 286, 54], 6, fill=(200, 60, 60, 255))
        # lente
        lc = (190, 132)
        l.circle(lc, 64, fill=(30, 32, 38, a), outline=(160, 166, 178, 255), width=7)
        l.circle(lc, 42, fill=(20, 40, 70, a), outline=(90, 96, 110, 255), width=4)
        l.circle((lc[0] - 14, lc[1] - 16), 12, fill=(255, 255, 255, int(110 * (1 - xray))))
        # luz de "listo"
        lcol = (60, 255, 120) if ready > 0.5 else (120, 40, 40)
        l.circle((64, 120), 11, fill=lcol + (255,))
        if ready > 0.5:
            l.circle((64, 120), 20, fill=(60, 255, 120, 70))
        im = l.done()
        if xray > 0:
            # adentro: el condensador del flash brillando
            g = L(CAM_W, CAM_H)
            cx, cy = 92, 150
            gl = 0.4 + 0.6 * charge
            g.circle((cx, cy), 60, fill=(255, 220, 80, int(80 * xray * gl)))
            g.rrect([cx - 26, cy - 46, cx + 26, cy + 46], 12, fill=(70, 120, 230, int(255 * xray)), outline=(255, 240, 160, int(255 * xray)), width=4)
            g.rect([cx + 10, cy - 46, cx + 20, cy + 46], fill=(235, 240, 250, int(220 * xray)))
            g.line([(cx, cy - 46), (cx, cy - 70), (85, 52)], (255, 230, 120, int(255 * xray)), 4)
            im.alpha_composite(g.done())
        return im
    return cached(key, mk)


def flash_star(r=260):
    def mk():
        l = L(2 * r, 2 * r)
        c = (r, r)
        for k in range(12):
            a = k * math.pi / 6
            ln = r * (0.95 if k % 2 == 0 else 0.6)
            l.poly([(c[0] + math.cos(a - 0.08) * 30, c[1] + math.sin(a - 0.08) * 30),
                    (c[0] + math.cos(a) * ln, c[1] + math.sin(a) * ln),
                    (c[0] + math.cos(a + 0.08) * 30, c[1] + math.sin(a + 0.08) * 30)], fill=(255, 255, 230, 230))
        l.circle(c, 70, fill=(255, 255, 255, 255))
        return l.done().filter(ImageFilter.GaussianBlur(2))
    return cached(('star', r), mk)


# ---------------- Condensadores ----------------
def elec_cap(h=300, swell=0.0, stripe_hl=0.0, top_off=0.0, q=False):
    """electrolítico: latica azul, franja blanca (−), pata larga (+), cruz arriba"""
    key = ('elec', h, round(swell, 2), round(stripe_hl, 1), round(top_off, 2), q)
    def mk():
        w = int(h * 0.62)
        cw = w + 120
        ch = h + 160
        l = L(cw, ch)
        cx = cw / 2
        top = 60; bot = top + h * 0.72
        bw = w * 0.5 * (1 + 0.18 * swell)
        # patas
        l.line([(cx - w * 0.2, bot), (cx - w * 0.2, ch - 8)], (205, 208, 216, 255), 7)
        l.line([(cx + w * 0.2, bot), (cx + w * 0.2, ch - 50)], (205, 208, 216, 255), 7)
        # cuerpo (se infla arriba)
        pts = []
        for k in range(21):
            u = k / 20
            y = top + (bot - top) * u
            bulge = 1 + 0.25 * swell * math.sin(min(1, (1 - u) * 1.6) * math.pi / 2)
            pts.append((cx + bw * bulge * (1 if u < 0.92 else 0.97), y))
        left = [(2 * cx - x, y) for x, y in reversed(pts)]
        l.poly(pts + left, fill=(52, 96, 205, 255), outline=(20, 40, 110, 255), width=4)
        # franja del negativo
        sx0 = cx + bw * 0.42; sx1 = cx + bw * 0.86
        sc = (240, 244, 255) if stripe_hl < 0.5 else (255, 240, 120)
        l.poly([(sx0, top + 14), (sx1 * (1 + 0.02 * swell), top + 14), (sx1, bot - 10), (sx0, bot - 10)], fill=sc + (255,))
        for k in range(4):
            yy = top + 40 + k * (bot - top - 70) / 3
            l.line([((sx0 + sx1) / 2 - 10, yy), ((sx0 + sx1) / 2 + 10, yy)], (40, 60, 120, 255), 5)
        # brillo
        l.rrect([cx - bw * 0.72, top + 20, cx - bw * 0.52, bot - 24], 8, fill=(255, 255, 255, 60))
        # tapa con cruz (válvula)
        ty = top - 26 * top_off * 4
        l.circle((cx, top + 2 - 120 * top_off), bw * (1 + 0.25 * swell), fill=(200, 206, 216, 255) if top_off == 0 else (200, 206, 216, int(255 * max(0, 1 - top_off * 1.5))))
        if top_off == 0:
            l.rect([cx - bw * (1 + 0.25 * swell), top - 2, cx + bw * (1 + 0.25 * swell), top + 6], fill=(52, 96, 205, 255))
            l.line([(cx - bw * 0.5, top - 6), (cx + bw * 0.5, top - 6)], (120, 126, 136, 255), 5)
            l.line([(cx, top - 6 - bw * 0.25), (cx, top - 6 + bw * 0.25)], (120, 126, 136, 255), 5)
        if q:
            l.text((cx, (top + bot) / 2), '?', int(h * 0.42), fill=(255, 255, 255), black=True, stroke=5, stroke_fill=(20, 30, 70))
        return l.done()
    return cached(key, mk)


def elec_top(hl=0.0, r=150):
    """tapa del electrolítico vista desde arriba: cruz de seguridad"""
    def mk():
        l = L(2 * r + 40, 2 * r + 40)
        c = (r + 20, r + 20)
        l.circle(c, r, fill=(52, 96, 205, 255), outline=(20, 40, 110, 255), width=5)
        l.circle(c, r * 0.86, fill=(200, 206, 216, 255), outline=(150, 156, 166, 255), width=4)
        col = (255, 210, 60, 255) if hl > 0.5 else (110, 116, 126, 255)
        w = 14 if hl > 0.5 else 9
        l.line([(c[0] - r * 0.6, c[1]), (c[0] + r * 0.6, c[1])], col, w)
        l.line([(c[0], c[1] - r * 0.6), (c[0], c[1] + r * 0.6)], col, w)
        l.circle((c[0] - r * 0.35, c[1] - r * 0.4), r * 0.12, fill=(255, 255, 255, 80))
        return l.done()
    return cached(('etop', round(hl), r), mk)


def ceramic_cap(size=220, flip=False):
    """cerámico: lentejita naranja con '104'"""
    def mk():
        cw, ch = size + 40, int(size * 1.55)
        l = L(cw, ch)
        cx, cy = cw / 2, size * 0.5 + 10
        r = size * 0.42
        l.line([(cx - r * 0.35, cy + r * 0.6), (cx - r * 0.35, ch - 8)], (205, 208, 216, 255), 6)
        l.line([(cx + r * 0.35, cy + r * 0.6), (cx + r * 0.35, ch - 8)], (205, 208, 216, 255), 6)
        l.d.ellipse(l.s([cx - r, cy - r * 0.92, cx + r, cy + r * 0.92]), fill=(226, 120, 40, 255), outline=(140, 62, 12, 255), width=int(4 * D.SS))
        l.d.ellipse(l.s([cx - r * 0.62, cy - r * 0.6, cx - r * 0.2, cy - r * 0.25]), fill=(255, 190, 120, 120))
        l.text((cx, cy + 4), '104', int(size * 0.18), fill=(80, 34, 6), black=True)
        return l.done()
    return cached(('cer', size, flip), mk)


def supercap(h=430):
    def mk():
        w = int(h * 0.7)
        l = L(w + 40, h + 80)
        cx = (w + 40) / 2
        l.rrect([20, 40, w + 20, h + 20], 30, fill=(34, 36, 42, 255), outline=(140, 146, 158, 255), width=6)
        l.circle((cx, 46), w / 2 - 2, fill=(170, 176, 186, 255))
        l.rect([20, 40, w + 20, 52], fill=(34, 36, 42, 255))
        l.rrect([cx - 40, 8, cx - 10, 40], 6, fill=(220, 190, 70, 255))
        l.rrect([cx + 10, 8, cx + 40, 40], 6, fill=(200, 204, 214, 255))
        l.rrect([40, h * 0.35, w, h * 0.72], 16, fill=(50, 140, 255, 255))
        l.text((cx, h * 0.47), 'SUPER', int(h * 0.09), fill=(255, 255, 255), black=True)
        l.text((cx, h * 0.62), '2,7 V', int(h * 0.07), fill=(220, 236, 255))
        l.rrect([40, h * 0.1, 64, h * 0.92], 10, fill=(255, 255, 255, 40))
        return l.done()
    return cached(('super', h), mk)


def mini_cap_icon(kind, h=90):
    if kind == 'cer':
        return ceramic_cap(int(h * 0.8))
    if kind == 'elec':
        return elec_cap(int(h))
    return supercap(int(h * 1.1))


# ---------------- Pila / LED ----------------
def battery_rot(ang_deg):
    return cached(('bat', int(ang_deg)), lambda: D.battery_img().rotate(ang_deg, resample=Image.BICUBIC, expand=True))


def runner_battery(phase=0.0):
    """pila maratonista: con cinta en la frente y patitas"""
    key = ('runb', round(phase % 1.0, 2))
    def mk():
        l = L(200, 300)
        s = math.sin(phase * 2 * math.pi)
        l.line([(80, 230), (80 + 26 * s, 290)], (240, 240, 240, 255), 9)
        l.line([(120, 230), (120 - 26 * s, 290)], (240, 240, 240, 255), 9)
        im = l.done()
        b = D.battery_img().resize((110, 212))
        im.alpha_composite(b, (45, 30))
        l2 = L(200, 300)
        l2.rect([46, 70, 154, 86], fill=(230, 40, 60, 255))
        l2.line([(46, 78), (22, 98)], (230, 40, 60, 255), 8)
        l2.circle((160, 52), 7, fill=(140, 200, 255, 220))
        im.alpha_composite(l2.done())
        return im
    return cached(key, mk)


# ---------------- Celular con condensadores cerámicos (MLCC) ----------------
def phone_board(twinkle=0.0, n=230):
    key = ('board', round(twinkle % 1.0, 1))
    def mk():
        l = L(360, 600)
        l.rrect([6, 6, 354, 594], 44, fill=(26, 28, 34, 255), outline=(180, 186, 198, 255), width=8)
        l.rrect([30, 40, 330, 560], 18, fill=(28, 110, 70, 255))
        # chips grandes
        l.rrect([110, 150, 250, 270], 10, fill=(40, 42, 48, 255), outline=(120, 126, 136, 255), width=3)
        l.rrect([60, 360, 160, 430], 8, fill=(40, 42, 48, 255))
        l.rrect([200, 380, 300, 470], 8, fill=(40, 42, 48, 255))
        for k in range(12):
            l.line([(40, 300 + k * 6), (320, 300 + k * 6)], (60, 160, 100, 120), 1)
        rnd = random.Random(5)
        for i in range(n):
            x = rnd.uniform(40, 315); y = rnd.uniform(52, 545)
            if 105 < x < 255 and 145 < y < 275:
                continue
            w = rnd.choice((7, 9, 11)); h = w * 0.55
            bright = 0.5 + 0.5 * math.sin((twinkle + i * 0.137) * 2 * math.pi)
            col = (int(190 + 50 * bright), int(150 + 40 * bright), int(100 + 30 * bright), 255)
            l.rect([x, y, x + w, y + h], fill=col)
            l.rect([x, y, x + 2, y + h], fill=(220, 224, 230, 255)); l.rect([x + w - 2, y, x + w, y + h], fill=(220, 224, 230, 255))
        return l.done()
    return cached(key, mk)


def sand_vs_mlcc():
    def mk():
        l = L(380, 380)
        l.rect([0, 0, 380, 380], fill=(28, 110, 70, 255))
        # MLCC chiquito
        l.rect([70, 160, 170, 215], fill=(200, 160, 110, 255))
        l.rect([70, 160, 92, 215], fill=(225, 228, 234, 255)); l.rect([148, 160, 170, 215], fill=(225, 228, 234, 255))
        # grano de arena
        pts = [(230, 150), (285, 135), (320, 170), (310, 225), (260, 240), (222, 205)]
        l.poly(pts, fill=(222, 196, 140, 255), outline=(160, 130, 80, 255), width=3)
        l.circle((262, 175), 9, fill=(250, 235, 200, 200))
        l.text((120, 262), 'MLCC', 30, fill=(255, 255, 255))
        l.text((270, 280), 'arena', 30, fill=(255, 235, 190))
        return l.done()
    return cached('sand', mk)


# ---------------- Letreros ----------------
def warning_sign():
    def mk():
        l = L(300, 300)
        l.poly([(150, 20), (285, 260), (15, 260)], fill=(255, 205, 40, 255), outline=(40, 30, 10, 255), width=10)
        l.text((150, 175), '!', 140, fill=(30, 22, 6), black=True)
        return l.done()
    return cached('warn', mk)


def big_farad():
    return cached('farad', lambda: S.fancy_text('1 FARADIO', 110, top=(255, 245, 140), bot=(255, 150, 40)))


def micro_f():
    return cached('uf', lambda: S.fancy_text('µF', 120, top=(170, 230, 255), bot=(60, 140, 255), outline=(10, 30, 70)))


def energy_bar(level=0.0, h=360, col=CURR):
    key = ('ebar', round(level, 2), h)
    def mk():
        l = L(110, h + 60)
        l.rrect([20, 30, 90, h + 30], 18, fill=(22, 24, 30, 230), outline=(230, 230, 240, 255), width=5)
        fh = (h - 16) * max(0.0, min(1.0, level))
        if fh > 2:
            l.rrect([28, h + 22 - fh, 82, h + 22], 12, fill=col + (255,))
        l.rrect([42, 12, 68, 32], 6, fill=(230, 230, 240, 255))
        return l.done()
    return cached(key, mk)


def volt_meter(v):
    key = ('vm', int(v))
    def mk():
        l = L(300, 170)
        l.rrect([6, 6, 294, 164], 22, fill=(22, 24, 30, 235), outline=(255, 200, 80, 255), width=5)
        k = v / 300
        l.rrect([26, 110, 274, 140], 10, fill=(50, 52, 60, 255))
        if k > 0.01:
            l.rrect([26, 110, 26 + 248 * k, 140], 10, fill=(255, int(220 - 140 * k), 60, 255))
        l.text((150, 62), f'{int(v)} V', 54, fill=(255, 255, 255), black=True)
        return l.done()
    return cached(key, mk)


def smoke(k=1.0, seed=3):
    key = ('smoke', round(k, 2), seed)
    def mk():
        l = L(360, 360)
        rnd = random.Random(seed)
        for i in range(9):
            a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(20, 120) * (0.5 + k)
            r = rnd.uniform(40, 70) * (0.6 + 0.6 * k)
            g = rnd.randint(90, 140)
            l.circle((180 + math.cos(a) * d, 180 + math.sin(a) * d * 0.7), r, fill=(g, g, g + 6, int(200 * max(0, 1 - k * 0.7))))
        return l.done()
    return cached(key, mk)


def pum_text():
    return cached('pum', lambda: S.fancy_text('¡PUM!', 120, top=(255, 250, 160), bot=(255, 90, 30), outline=(80, 20, 0)))


def spark(r=46):
    def mk():
        l = L(2 * r, 2 * r)
        c = (r, r)
        pts = []
        for k in range(8):
            a = k * math.pi / 4
            rr = r if k % 2 == 0 else r * 0.38
            pts.append((c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr))
        l.poly(pts, fill=(255, 240, 120, 255))
        return l.done()
    return cached(('spark', r), mk)
