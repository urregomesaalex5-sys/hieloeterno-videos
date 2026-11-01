# Dibujos del capítulo 4: el diodo (puerta de un solo sentido, componente, unión P-N,
# circuito con bombillo, cargador con puente de diodos y tarjetas de tipos).
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
from diagrams import L, label, arrow

P_COL = (255, 120, 120)      # zona P (le faltan electrones)
N_COL = (110, 170, 255)      # zona N (electrones de sobra)
BAR_COL = (170, 150, 200)    # barrera
GREEN = (61, 220, 132)
RED = (255, 80, 90)
CURR = D.CURR
WIRE = D.WIRE

_cache = {}
def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


# ---------------- Intro: la puerta-diodo gigante ----------------
DOOR_H = 520
TRI_W = 300
FLAP_W = 46

def door_triangle(glow=1.0):
    def mk():
        pad = 30
        l = L(TRI_W + 2 * pad, DOOR_H + 2 * pad)
        pts = [(pad, pad), (pad + TRI_W, pad + DOOR_H / 2), (pad, pad + DOOR_H)]
        l.poly(pts, fill=GREEN + (70,))
        l.line(pts + [pts[0]], GREEN + (255,), 16)
        l.line(pts + [pts[0]], (210, 255, 225, 255), 5)
        # bloques decorativos dentro (como de Minecraft)
        for k in range(5):
            y = pad + 70 + k * 80
            xm = pad + TRI_W * (1 - abs((y - pad - DOOR_H / 2) / (DOOR_H / 2))) - 40
            for x in range(pad + 28, int(xm), 64):
                l.rrect([x, y, x + 46, y + 46], 6, fill=(61, 220, 132, 50), outline=(61, 220, 132, 120), width=2)
        im = l.done()
        g = im.filter(ImageFilter.GaussianBlur(14))
        out = Image.new('RGBA', im.size, (0, 0, 0, 0))
        out.alpha_composite(g); out.alpha_composite(im)
        return out
    return cached('tri', mk)


def door_flap():
    """la rayita convertida en puerta de gato: bisagra arriba (en el centro de la parte de arriba)"""
    def mk():
        l = L(FLAP_W + 20, DOOR_H + 30)
        l.rrect([10, 14, 10 + FLAP_W, 14 + DOOR_H], 10, fill=(236, 238, 244, 255), outline=(60, 64, 76, 255), width=5)
        for y in range(40, DOOR_H, 70):
            l.line([(18, 14 + y), (2 + FLAP_W, 14 + y)], (190, 194, 205, 255), 3)
        l.circle((10 + FLAP_W / 2, 18), 12, fill=(120, 124, 136, 255), outline=(50, 52, 60, 255), width=3)
        return l.done()
    return cached('flap', mk)


def stopper():
    """tope que no deja abrir la puerta hacia la izquierda"""
    def mk():
        l = L(70, 60)
        l.rrect([6, 10, 64, 50], 8, fill=(255, 80, 90, 255), outline=(90, 20, 30, 255), width=4)
        l.text((35, 30), '✕', 26, fill=(255, 255, 255))
        return l.done()
    return cached('stop', mk)


def one_way_sign():
    def mk():
        l = L(300, 110)
        l.rrect([6, 6, 294, 104], 16, fill=(250, 250, 250, 255), outline=(30, 30, 30, 255), width=6)
        arrow(l, (40, 56), (250, 56), (25, 25, 25, 255), 18, 40)
        l.text((128, 56), 'SOLO', 30, fill=(255, 255, 255), black=True)
        return l.done()
    return cached('sign', mk)


def bonk_text():
    return cached('bonk', lambda: S.fancy_text('¡BONK!', 96, top=(255, 255, 140), bot=(255, 120, 30)))


# ---------------- Símbolos ----------------
def symbol(kind='normal', size=120, col=(255, 255, 255), leads=True, lw=8):
    """símbolo del diodo apuntando a la derecha. kind: normal, led, zener, schottky, foto"""
    key = ('sym', kind, size, col, leads, lw)
    def mk():
        s = size
        Wd = int(s * 2.4); Hd = int(s * 1.5)
        l = L(Wd, Hd)
        cx, cy = Wd / 2, Hd / 2 + (s * 0.12 if kind in ('led', 'foto') else 0)
        x0 = cx - s * 0.45; x1 = cx + s * 0.45
        c = col + (255,)
        if leads:
            l.line([(8, cy), (x0, cy)], c, lw)
            l.line([(x1, cy), (Wd - 8, cy)], c, lw)
        l.poly([(x0, cy - s * 0.5), (x1, cy), (x0, cy + s * 0.5)], fill=c)
        bx = x1
        l.line([(bx, cy - s * 0.52), (bx, cy + s * 0.52)], c, lw + 2)
        hook = s * 0.16
        if kind == 'zener':
            l.line([(bx, cy - s * 0.52), (bx - hook, cy - s * 0.52 - hook * 0.6)], c, lw)
            l.line([(bx, cy + s * 0.52), (bx + hook, cy + s * 0.52 + hook * 0.6)], c, lw)
        if kind == 'schottky':
            l.line([(bx, cy - s * 0.52), (bx + hook, cy - s * 0.52), (bx + hook, cy - s * 0.52 + hook)], c, lw)
            l.line([(bx, cy + s * 0.52), (bx - hook, cy + s * 0.52), (bx - hook, cy + s * 0.52 - hook)], c, lw)
        if kind in ('led', 'foto'):
            for k in range(2):
                ox = cx - s * 0.05 + k * s * 0.32
                if kind == 'led':
                    p0 = (ox, cy - s * 0.55); p1 = (ox + s * 0.32, cy - s * 0.95)
                else:
                    p1 = (ox, cy - s * 0.58); p0 = (ox + s * 0.32, cy - s * 0.98)
                arrow(l, p0, p1, c, max(4, lw - 3), s * 0.18)
        return l.done()
    return cached(key, mk)


# ---------------- El componente real ----------------
PART_W, PART_H = 760, 160
BODY = (250, 40, 510, 120)       # cuerpo negro (x0, y0, x1, y1)
STRIPE = (448, 476)              # franja plateada (cátodo)

def diode_part(glow=0.0, stripe_hl=0.0):
    key = ('part', round(glow, 2), round(stripe_hl, 2))
    def mk():
        l = L(PART_W, PART_H)
        cy = PART_H / 2
        # patitas
        l.line([(10, cy), (BODY[0] + 10, cy)], (200, 204, 212, 255), 12)
        l.line([(BODY[2] - 10, cy), (PART_W - 10, cy)], (200, 204, 212, 255), 12)
        l.line([(10, cy - 3), (BODY[0] + 10, cy - 3)], (245, 247, 250, 255), 3)
        l.line([(BODY[2] - 10, cy - 3), (PART_W - 10, cy - 3)], (245, 247, 250, 255), 3)
        # cuerpo
        l.rrect(list(BODY), 36, fill=(32, 34, 40, 255), outline=(10, 10, 12, 255), width=4)
        l.rrect([BODY[0] + 20, BODY[1] + 10, BODY[2] - 20, BODY[1] + 24], 7, fill=(80, 84, 94, 255))
        # franja (cátodo)
        sc = tuple(int(200 + 55 * stripe_hl) for _ in range(3))
        l.rect([STRIPE[0], BODY[1] + 2, STRIPE[1], BODY[3] - 2], fill=sc + (255,))
        l.text((350, cy + 4), '1N4007', 26, fill=(150, 154, 165))
        im = l.done()
        if glow > 0:
            g = Image.new('RGBA', im.size, (0, 0, 0, 0))
            gg = L(PART_W, PART_H)
            gg.rrect(list(BODY), 36, fill=GREEN + (int(160 * glow),))
            g = gg.done().filter(ImageFilter.GaussianBlur(16))
            out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(im)
            return out
        return im
    return cached(key, mk)


# ---------------- Unión P-N ----------------
PN_X0, PN_X1 = 150, 930
PN_Y0, PN_Y1 = 350, 610
PN_MID = 540

def carriers(seed, n, side):
    r = random.Random(seed)
    out = []
    for k in range(n):
        if side == 'p':
            x = r.uniform(PN_X0 + 30, PN_MID - 20)
        else:
            x = r.uniform(PN_MID + 20, PN_X1 - 30)
        y = r.uniform(PN_Y0 + 32, PN_Y1 - 32)
        out.append(dict(x=x, y=y, ph=r.uniform(0, 6.28), w=r.uniform(1.5, 3.0), pop=r.uniform(0, 0.6)))
    return out

HOLES = carriers(11, 16, 'p')
ELECS = carriers(22, 16, 'n')

def hole_img():
    def mk():
        l = L(48, 48)
        l.circle((24, 24), 15, fill=(0, 0, 0, 0), outline=(255, 255, 255, 255), width=5)
        l.circle((24, 24), 15, outline=P_COL + (255,), width=2)
        return l.done()
    return cached('hole', mk)

def elec_img():
    def mk():
        l = L(48, 48)
        l.circle((24, 24), 15, fill=(60, 220, 255, 255), outline=(255, 255, 255, 255), width=3)
        l.line([(16, 24), (32, 24)], (10, 30, 60, 255), 5)
        return l.done()
    return cached('elec', mk)


def pn_frame(p_a=1.0, n_a=1.0):
    """bloque de silicio con zonas P y N (sin portadores)"""
    key = ('pn', round(p_a, 2), round(n_a, 2))
    def mk():
        l = L(W_, H_)
        ox, oy = PN_X0 - 20, PN_Y0 - 20
        if p_a > 0:
            l.rrect([20, 20, PN_MID - ox, PN_Y1 - oy], 22, fill=P_COL[:3] + (int(70 * p_a),), outline=P_COL + (int(255 * p_a),), width=6)
            l.text((60, 60), 'P', 56, fill=(255, 200, 200, int(255 * p_a)), black=True)
        if n_a > 0:
            l.rrect([PN_MID - ox, 20, PN_X1 - ox, PN_Y1 - oy], 22, fill=N_COL[:3] + (int(70 * n_a),), outline=N_COL + (int(255 * n_a),), width=6)
            l.text((PN_X1 - ox - 40, 60), 'N', 56, fill=(200, 220, 255, int(255 * n_a)), black=True)
        return l.done()
    W_, H_ = PN_X1 - PN_X0 + 40, PN_Y1 - PN_Y0 + 40
    return cached(key, mk)


def barrier_img(bw, a=1.0):
    bw = max(8, int(bw))
    key = ('bar', bw // 4, round(a, 1))
    def mk():
        h = PN_Y1 - PN_Y0 - 8
        l = L(bw + 20, h + 20)
        l.rect([10, 10, 10 + bw, 10 + h], fill=BAR_COL + (int(150 * a),))
        for y in range(-bw, h, 26):
            l.line([(10, 10 + y + bw), (10 + bw, 10 + y)], (230, 220, 255, int(140 * a)), 4)
        l.line([(10, 10), (10, 10 + h)], (240, 235, 255, int(255 * a)), 4)
        l.line([(10 + bw, 10), (10 + bw, 10 + h)], (240, 235, 255, int(255 * a)), 4)
        return l.done()
    return cached(key, mk)


# ---------------- Circuito ----------------
def bulb_img(on=0.0):
    key = ('bulb', round(on, 2))
    def mk():
        l = L(240, 300)
        c = (120, 110)
        if on > 0:
            for r, a in ((115, 0.16), (85, 0.3)):
                l.circle(c, r, fill=(255, 220, 90, int(255 * a * on)))
            for k in range(10):
                ang = k * math.pi / 5
                l.line([(c[0] + math.cos(ang) * 82, c[1] + math.sin(ang) * 82),
                        (c[0] + math.cos(ang) * (82 + 30 * on), c[1] + math.sin(ang) * (82 + 30 * on))], CURR + (int(255 * on),), 7)
        glass = tuple(int(70 + (255 - 70) * on * (1, 0.93, 0.6)[i]) for i in range(3))
        l.circle(c, 62, fill=glass + (235,), outline=(230, 230, 240, 255), width=4)
        l.rect([c[0] - 32, c[1] + 48, c[0] + 32, c[1] + 70], fill=glass + (235,))
        # filamento
        fc = (255, 240, 160, 255) if on > 0.5 else (90, 80, 70, 255)
        l.line([(c[0] - 18, c[1] + 50), (c[0] - 18, c[1] + 6), (c[0] - 9, c[1] - 10), (c[0], c[1] + 4), (c[0] + 9, c[1] - 10), (c[0] + 18, c[1] + 6), (c[0] + 18, c[1] + 50)], fc, 4)
        # rosca
        for k in range(4):
            y = c[1] + 72 + k * 16
            l.rrect([c[0] - 36, y, c[0] + 36, y + 14], 6, fill=(185, 188, 196, 255), outline=(110, 112, 120, 255), width=2)
        l.rrect([c[0] - 20, c[1] + 136, c[0] + 20, c[1] + 152], 6, fill=(60, 60, 66, 255))
        return l.done()
    return cached(key, mk)


def battery_rot(ang_deg):
    """pila acostada/girada (ang en grados, 0 = + arriba)"""
    key = ('bat', int(ang_deg))
    return cached(key, lambda: D.battery_img().rotate(ang_deg, resample=Image.BICUBIC, expand=True))


# ---------------- Cargador ----------------
def outlet_img():
    def mk():
        l = L(170, 220)
        l.rrect([8, 8, 162, 212], 22, fill=(238, 236, 228, 255), outline=(120, 118, 110, 255), width=5)
        l.rrect([30, 34, 140, 186], 18, fill=(250, 249, 244, 255), outline=(170, 168, 160, 255), width=3)
        l.rrect([56, 72, 68, 118], 4, fill=(40, 40, 44, 255))
        l.rrect([102, 72, 114, 118], 4, fill=(40, 40, 44, 255))
        l.circle((85, 150), 11, fill=(40, 40, 44, 255))
        return l.done()
    return cached('outlet', mk)


def wave_img(kind, phase=0.0, w=220, h=150, col=CURR, draw=1.0):
    l = L(w, h)
    pts = []
    n = 80
    for k in range(int(n * draw) + 1):
        x = 8 + (w - 16) * k / n
        v = math.sin(2 * math.pi * (k / n * 2.0) - phase)
        if kind == 'dc':
            v = abs(v)
            y = h - 22 - (h - 44) * v
        else:
            y = h / 2 - (h / 2 - 20) * v
        pts.append((x, y))
    if kind != 'dc':
        l.line([(8, h / 2), (w - 8, h / 2)], (255, 255, 255, 70), 2)
    else:
        l.line([(8, h - 22), (w - 8, h - 22)], (255, 255, 255, 70), 2)
    if len(pts) > 1:
        l.line(pts, col + (255,), 8)
    return l.done()


def bridge_img(glow=0.0):
    """puente de 4 diodos: entra alterna por arriba y abajo; sale directa (+ a la derecha, - a la izquierda)"""
    key = ('bridge', round(glow, 2))
    def mk():
        s = 250
        l = L(s, s)
        c = s / 2
        top, right, bot, left = (c, 22), (s - 22, c), (c, s - 22), (22, c)
        col = (255, 255, 255, 150)
        l.poly([top, right, bot, left], outline=col, width=4)
        for p in (top, right, bot, left):
            l.circle(p, 9, fill=(255, 255, 255, 255))
        l.text((right[0] - 2, right[1] - 30), '+', 30, fill=(120, 255, 170))
        l.text((left[0] + 4, left[1] - 30), '−', 30, fill=(255, 160, 160))
        im = l.done()
        scol = (255, 255, 255) if glow < 0.5 else (170, 255, 200)
        sym = symbol('normal', 44, scol, leads=False, lw=6)
        for a, b in ((left, top), (top, right), (left, bot), (bot, right)):
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            rot = sym.rotate(-ang, resample=Image.BICUBIC, expand=True)
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            im.alpha_composite(rot, (int(mx - rot.size[0] / 2), int(my - rot.size[1] / 2)))
        if glow > 0:
            g = im.filter(ImageFilter.GaussianBlur(10))
            out = Image.new('RGBA', im.size, (0, 0, 0, 0))
            for _ in range(2):
                out.alpha_composite(g)
            out.alpha_composite(im)
            return out
        return im
    return cached(key, mk)


def phone_img(level=0.2, charging=0.0):
    key = ('ph', round(level, 2), round(charging, 1))
    def mk():
        l = L(170, 300)
        l.rrect([8, 8, 162, 292], 26, fill=(28, 30, 36, 255), outline=(150, 154, 165, 255), width=5)
        l.rrect([20, 30, 150, 270], 14, fill=(18, 40, 52, 255))
        # pila
        l.rrect([52, 90, 118, 220], 10, outline=(255, 255, 255, 255), width=5)
        l.rrect([72, 78, 98, 92], 4, fill=(255, 255, 255, 255))
        hh = int(118 * level)
        col = GREEN if level > 0.5 else (255, 200, 60)
        if hh > 0:
            l.rrect([60, 214 - hh, 110, 214], 6, fill=col + (255,))
        if charging > 0:
            l.poly([(90, 118), (70, 160), (86, 160), (78, 196), (102, 150), (86, 150)], fill=(255, 255, 255, int(255 * charging)))
        return l.done()
    return cached(key, mk)


# ---------------- Tarjetas de los tipos ----------------
CW, CH_ = D.CARD_W, D.CARD_H

def _card(title, border):
    l = L(CW, CH_)
    l.rrect([4, 4, CW - 4, CH_ - 4], 26, fill=(24, 28, 36, 238), outline=border + (255,), width=5)
    l.rrect([CW / 2 - 130, CH_ - 56, CW / 2 + 130, CH_ - 12], 14, fill=border[:3] + (60,))
    l.text((CW / 2, CH_ - 34), title, 30, fill=(255, 255, 255), black=True)
    return l


def card_led(t, color_k=0.0, light=1.0):
    l = _card('LED', (255, 120, 120))
    im = l.done()
    cols = [(255, 60, 60), (60, 230, 90), (70, 130, 255), (255, 210, 60)]
    i = int(color_k) % 4; f = color_k - int(color_k)
    c = tuple(int(cols[i][j] * (1 - f) + cols[(i + 1) % 4][j] * f) for j in range(3))
    sym = symbol('led', 70, (255, 255, 255), leads=True, lw=6)
    im.alpha_composite(sym, (30, 40))
    # LED que brilla
    g = L(200, 200)
    if light > 0:
        g.circle((100, 100), 80, fill=c + (int(70 * light),))
        g.circle((100, 100), 56, fill=c + (int(120 * light),))
    g.rrect([70, 60, 130, 130], 26, fill=tuple(int(v * (0.35 + 0.65 * light)) for v in c) + (255,), outline=(255, 255, 255, 200), width=3)
    g.rect([70, 105, 130, 130], fill=tuple(int(v * (0.35 + 0.65 * light)) for v in c) + (255,))
    g.line([(85, 130), (85, 185)], (200, 204, 212, 255), 5); g.line([(115, 130), (115, 175)], (200, 204, 212, 255), 5)
    gi = g.done()
    im.alpha_composite(gi, (CW - 215, 0))
    return im


def card_zener(t, k=0.0):
    """k 0..1: el voltaje sube y se queda fijo"""
    l = _card('ZENER', (255, 200, 80))
    sym = symbol('zener', 60, (255, 255, 255), leads=True, lw=6)
    # gráfica
    gx0, gy0, gx1, gy1 = 230, 30, 410, 170
    l.line([(gx0, gy1), (gx1, gy1)], (255, 255, 255, 160), 3)
    l.line([(gx0, gy0), (gx0, gy1)], (255, 255, 255, 160), 3)
    vz = gy0 + 50
    for x in range(gx0 + 6, gx1, 18):
        l.line([(x, vz), (x + 9, vz)], (255, 200, 80, 200), 3)
    pts = []
    n = 40
    for j in range(int(n * k) + 1):
        u = j / n
        x = gx0 + (gx1 - gx0) * u
        y = gy1 - (gy1 - vz) * min(1.0, u / 0.45) * (1 if u < 0.45 else 1)
        if u >= 0.45:
            y = vz + 2 * math.sin(u * 40)
        pts.append((x, y))
    if len(pts) > 1:
        l.line(pts, (120, 255, 160, 255), 6)
    l.text((gx1 - 8, vz - 18), '5,1 V', 22, fill=(255, 210, 110), anchor='rm')
    im = l.done()
    im.alpha_composite(sym, (14, 50))
    return im


def card_schottky(t, k=0.0, fast=0.0):
    """k: carrera de encendido (0..1). fast: líneas de velocidad"""
    l = _card('SCHOTTKY', (120, 200, 255))
    x0, x1 = 210, 414
    for row, (name, vth, col) in enumerate((('S', 0.3, (120, 200, 255)), ('normal', 0.7, (200, 200, 210)))):
        y = 52 + row * 76
        v = 0.8 * k
        on = v >= vth
        l.rrect([x0, y - 18, x1, y + 18], 10, outline=(255, 255, 255, 150), width=3)
        fw = (x1 - x0 - 6) * min(1.0, v / 0.8)
        l.rrect([x0 + 3, y - 15, x0 + 3 + max(6, fw), y + 15], 8, fill=(GREEN if on else col) + (255,))
        tx = x0 + (x1 - x0) * vth / 0.8
        l.line([(tx, y - 24), (tx, y + 24)], (255, 255, 255, 230), 4)
        l.text((tx, y + 38), '0,3 V' if row == 0 else '0,7 V', 24, fill=(255, 255, 255), black=True)
        if on:
            l.text((x0 + 10, y), '¡ON!', 22, fill=(10, 40, 20), anchor='lm', black=True)
    if fast > 0:
        bx, by = 168, 12
        l.poly([(bx + 14, by), (bx, by + 34), (bx + 12, by + 34), (bx + 4, by + 62), (bx + 26, by + 24), (bx + 14, by + 24)],
               fill=(255, 230, 80, int(255 * fast)))
    im = l.done()
    sym = symbol('schottky', 46, (255, 255, 255), leads=True, lw=6)
    im.alpha_composite(sym, (12, 36))
    nrm = symbol('normal', 30, (200, 200, 210), leads=True, lw=5)
    im.alpha_composite(nrm, (40, 110))
    return im


def card_foto(t, light=0.0, current=0.0, tv=0.0, dark=0.0):
    l = _card('FOTODIODO', (190, 140, 255))
    # control remoto
    l.rrect([30, 60, 78, 170], 14, fill=(50, 52, 60, 255), outline=(150, 150, 160, 255), width=3)
    l.circle((54, 82), 8, fill=(255, 80, 80, 255))
    for r in range(3):
        for c in range(2):
            l.circle((44 + c * 20, 112 + r * 18), 5, fill=(170, 170, 180, 255))
    # ondas de luz infrarroja
    if light > 0:
        for j in range(3):
            rr = 30 + j * 26 + 20 * ((t * 2.5) % 1.0)
            l.d.arc([(84 - rr) * 2, (95 - rr) * 2, (84 + rr) * 2, (95 + rr) * 2], -35, 35, fill=(255, 120, 200, int(220 * light)), width=8)
    # tele
    l.rrect([268, 40, 412, 140], 10, fill=(20, 22, 26, 255), outline=(150, 150, 160, 255), width=4)
    if tv > 0:
        l.rrect([278, 50, 402, 130], 6, fill=(int(60 + 120 * tv), int(130 + 100 * tv), int(200 + 50 * tv), 255))
        l.text((340, 90), '▶', 34, fill=(255, 255, 255, int(255 * tv)))
    l.rect([326, 140, 354, 156], fill=(120, 120, 130, 255))
    im = l.done()
    sym = symbol('foto', 50, (255, 255, 255) if dark < 0.5 else (140, 140, 150), leads=True, lw=5)
    im.alpha_composite(sym, (138, 70))
    if current > 0:
        c = L(CW, CH_)
        for j in range(4):
            u = (t * 1.6 + j / 4) % 1.0
            x = 150 + 110 * u
            c.rect([x - 6, 128, x + 6, 140], fill=CURR + (int(255 * current),))
        im.alpha_composite(c.done())
    return im


def superpoderes():
    return cached('sp', lambda: S.fancy_text('¡SUPERPODERES!', 84, top=(255, 245, 120), bot=(255, 140, 30)))


def mystery_door():
    def mk():
        l = L(220, 300)
        l.rrect([10, 10, 210, 290], 30, fill=(150, 100, 60, 255), outline=(70, 40, 20, 255), width=8)
        l.rrect([34, 36, 186, 150], 14, fill=(120, 76, 44, 255))
        l.rrect([34, 166, 186, 268], 14, fill=(120, 76, 44, 255))
        l.circle((178, 160), 10, fill=(255, 210, 80, 255))
        l.text((110, 150), '?', 150, fill=(255, 255, 255), black=True, stroke=6, stroke_fill=(40, 20, 10))
        return l.done()
    return cached('myst', mk)
