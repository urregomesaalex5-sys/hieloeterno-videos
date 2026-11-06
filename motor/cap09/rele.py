# Dibujos del capítulo 9 (el relé), con aspecto realista:
# relé azul de 5 V (tipo SRD-05VDC-SL-C) cerrado y en corte (bobina, núcleo, yugo, armadura, resorte y
# contactos COM / NC / NA), botoncito, reflector gigante, medidores, gráfica del pico con y sin diodo,
# frente de un carro con relé de luces y pito, panel de relés de la Mark II, polilla, cuaderno con la
# polilla pegada y el símbolo del relé para el remate y el reto.
# Regla: cada rótulo sale de VERIFICACION.md (códigos R#).
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
import inductor as I
from caps_real import cached

BLUE = (34, 96, 205)
BLUE_HI = (96, 156, 240)
BLUE_DK = (18, 54, 130)
IRON = (104, 108, 118)
IRON_HI = (160, 165, 175)
IRON_DK = (62, 64, 72)
BRONZE = (214, 164, 92)
SILVER = (214, 218, 226)
WIRE = (232, 232, 232)
CURR = (255, 217, 61)


def _vgrad(w, h, top, bot):
    a = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(top, np.float32)[None, None, :] * (1 - a) + np.array(bot, np.float32)[None, None, :] * a
    arr = np.repeat(arr, w, axis=1)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')


# ---------------- relé cerrado (caja azul, vista 3/4) ----------------
def relay_box(w=300, lid=0.0):
    """relé azul visto en 3/4. lid (0..1) = cuánto se ha levantado la tapa (no se dibuja la tapa aquí,
    solo se deja de dibujar la caja; la tapa vuela con relay_lid())."""
    key = ('rbox', w)
    def mk():
        h = int(w * 0.95)
        dep = int(w * 0.22)
        im = Image.new('RGBA', (w + dep + 10, h + dep + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        x0, y0 = 4, dep + 4
        # patas plateadas
        for k, px in enumerate((0.12, 0.3, 0.55, 0.75, 0.9)):
            xx = x0 + w * px
            d.rectangle([xx - 4, y0 + h - 4, xx + 4, y0 + h + 30], fill=SILVER + (255,), outline=(140, 142, 150, 255))
        # cara frontal con degradado
        front = _vgrad(w, h, BLUE_HI, BLUE)
        m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 10, fill=255)
        front.putalpha(m)
        im.alpha_composite(front, (x0, y0))
        # cara de arriba y lateral
        d.polygon([(x0 + 6, y0), (x0 + dep + 6, y0 - dep), (x0 + w + dep - 4, y0 - dep), (x0 + w - 4, y0)], fill=BLUE_HI + (255,))
        d.polygon([(x0 + w - 2, y0 + 4), (x0 + w + dep - 4, y0 - dep + 4), (x0 + w + dep - 4, y0 + h - dep - 6), (x0 + w - 2, y0 + h - 4)],
                  fill=BLUE_DK + (255,))
        d.line([(x0 + 6, y0), (x0 + w - 4, y0)], fill=(170, 205, 255, 255), width=3)
        # brillo
        d.rounded_rectangle([x0 + 12, y0 + 12, x0 + 40, y0 + h - 30], 10, fill=(255, 255, 255, 40))
        # textos impresos (blancos)
        f1 = S.font(int(w * 0.085)); f2 = S.font(int(w * 0.06))
        cx = x0 + w / 2
        d.text((cx, y0 + h * 0.26), 'SRD-05VDC-SL-C', font=f1, fill=(240, 245, 255, 255), anchor='mm')
        d.text((cx, y0 + h * 0.47), '10A 250VAC  10A 125VAC', font=f2, fill=(225, 235, 255, 255), anchor='mm')
        d.text((cx, y0 + h * 0.60), '10A 30VDC  10A 28VDC', font=f2, fill=(225, 235, 255, 255), anchor='mm')
        # diagrama impreso (bobina + contacto)
        yy = y0 + h * 0.8
        d.rectangle([cx - w * 0.3, yy - 14, cx - w * 0.12, yy + 14], outline=(230, 240, 255, 255), width=3)
        d.line([(cx - w * 0.3, yy + 14), (cx - w * 0.12, yy - 14)], fill=(230, 240, 255, 255), width=2)
        d.line([(cx + w * 0.02, yy + 12), (cx + w * 0.2, yy - 10)], fill=(230, 240, 255, 255), width=3)
        d.ellipse([cx + w * 0.2 - 5, yy - 15, cx + w * 0.2 + 5, yy - 5], fill=(230, 240, 255, 255))
        return im
    return cached(key, mk)


def relay_lid(w=300):
    """la tapa azul sola (para que salga volando y se vea el corte)"""
    key = ('rlid', w)
    def mk():
        h = int(w * 0.95)
        l = D.L(w + 20, h + 20)
        l.rrect([10, 10, w + 10, h + 10], 12, fill=BLUE + (235,), outline=BLUE_HI + (255,), width=6)
        l.rrect([22, 22, 50, h - 20], 10, fill=(255, 255, 255, 40))
        l.text((w / 2 + 10, h * 0.3), 'SRD-05VDC-SL-C', int(w * 0.085), fill=(240, 245, 255))
        return l.done()
    return cached(key, mk)


# ---------------- relé en corte (adentro) ----------------
RW, RH = 720, 660
PIVOT = (104, 236)
ARM_LEN = 455
ANG_REST = math.radians(-10)          # armadura levantada (resorte)
POLE_TOP = 246
CONT_X = 555


def arm_angle(k):
    return ANG_REST * (1 - k)


def arm_pt(k, s):
    a = arm_angle(k)
    return PIVOT[0] + s * math.cos(a), PIVOT[1] + s * math.sin(a)


def rivet_pt(k):
    return arm_pt(k, ARM_LEN)


NC_Y = rivet_pt(0)[1] - 17
NO_Y = rivet_pt(1)[1] + 17
PINS = {'b1': 175, 'b2': 300, 'COM': 470, 'NA': 615, 'NC': 690}
PIN_Y = 600


def _spring_pts(p0, p1, n=9, amp=13):
    pts = [p0]
    for k in range(1, n * 2):
        u = k / (n * 2)
        x = p0[0] + (p1[0] - p0[0]) * u + (amp if k % 2 else -amp)
        y = p0[1] + (p1[1] - p0[1]) * u
        pts.append((x, y))
    pts.append(p1)
    return pts


def coil_vertical(h=260, w=150):
    key = ('cvert', h, w)
    def mk():
        c = I.coil(h, w, 13, core=False, leads=False)
        return c.rotate(90, expand=True, resample=Image.BICUBIC)
    return cached(key, mk)


def relay_inside(k=0.0, flow=0.0, t=0.0, field=0.0, glow_contact=0.0, labels=()):
    """relé por dentro. k = cuánto jaló la armadura (0 suelta / toca NC, 1 pegada al núcleo / toca NA).
    flow = corriente en la bobina (cuadritos), field = brillo del imán. labels = nombres a mostrar."""
    l = D.L(RW, RH)
    # base de baquelita
    l.rrect([30, PIN_Y - 46, RW - 20, PIN_Y], 10, fill=(48, 50, 58, 255), outline=(28, 28, 34, 255), width=3)
    # patas
    for name, x in PINS.items():
        l.rect([x - 7, PIN_Y - 4, x + 7, PIN_Y + 50], fill=SILVER + (255,), outline=(130, 132, 140, 255), width=2)
    # yugo (hierro en L) y soporte del resorte
    l.rect([58, 70, 88, PIN_Y - 46], fill=IRON + (255,), outline=IRON_DK + (255,), width=3)
    l.rect([58, 520, 300, 548], fill=IRON + (255,), outline=IRON_DK + (255,), width=3)
    l.rect([58, 70, 250, 94], fill=IRON + (255,), outline=IRON_DK + (255,), width=3)
    l.line([(62, 74), (62, 540)], IRON_HI + (255,), 3)
    # núcleo (hierro) dentro de la bobina
    l.rect([205, POLE_TOP, 265, 520], fill=IRON + (255,), outline=IRON_DK + (255,), width=3)
    l.rrect([196, POLE_TOP, 274, POLE_TOP + 18], 4, fill=IRON_HI + (255,), outline=IRON_DK + (255,), width=3)
    im = l.im
    # bobina de cobre (vertical)
    cv = coil_vertical(250, 150)
    cvs = cv.resize((cv.size[0] * 2, cv.size[1] * 2), Image.LANCZOS)
    im.alpha_composite(cvs, (int((235 - cv.size[0] / 2) * 2), int((392 - cv.size[1] / 2) * 2)))
    d = l.d
    # alambres de la bobina a sus patas
    l.line([(170, 505), (PINS['b1'], 535), (PINS['b1'], PIN_Y - 4)], (214, 140, 70, 255), 5)
    l.line([(300, 505), (PINS['b2'], 535), (PINS['b2'], PIN_Y - 4)], (214, 140, 70, 255), 5)
    # campo/imán encendido
    if field > 0.01:
        g = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([2 * 150, 2 * 200, 2 * 320, 2 * 300], fill=(90, 200, 255, int(170 * field)))
        g = g.filter(ImageFilter.GaussianBlur(30))
        im.alpha_composite(g)
    # contactos fijos: NC arriba, NA abajo (soportes de bronce a sus patas)
    l.rect([CONT_X - 8, 108, CONT_X + 135, 122], fill=BRONZE + (255,))
    l.rect([CONT_X + 123, 108, CONT_X + 135, PIN_Y - 46], fill=BRONZE + (255,))
    l.rect([CONT_X - 8, NC_Y - 26, CONT_X + 8, 122], fill=BRONZE + (255,))
    l.rrect([CONT_X - 14, NC_Y - 10, CONT_X + 14, NC_Y + 2], 4, fill=SILVER + (255,), outline=(120, 120, 130, 255), width=2)
    l.rect([CONT_X + 54, NO_Y + 8, CONT_X + 66, PIN_Y - 46], fill=BRONZE + (255,))
    l.rect([CONT_X - 8, NO_Y + 8, CONT_X + 66, NO_Y + 20], fill=BRONZE + (255,))
    l.rrect([CONT_X - 14, NO_Y - 2, CONT_X + 14, NO_Y + 10], 4, fill=SILVER + (255,), outline=(120, 120, 130, 255), width=2)
    # armadura (placa de hierro) que gira en el pivote
    a = arm_angle(k)
    ca, sa = math.cos(a), math.sin(a)
    def P(s, n):
        return (PIVOT[0] + s * ca - n * sa, PIVOT[1] + s * sa + n * ca)
    l.poly([P(0, -12), P(330, -12), P(330, 10), P(0, 10)], fill=IRON + (255,), outline=IRON_DK + (255,), width=3)
    l.line([P(4, -9), P(326, -9)], IRON_HI + (255,), 3)
    l.circle(PIVOT, 9, fill=IRON_DK + (255,))
    # lámina de contacto (bronce) que sale de la armadura y lleva el remache
    l.poly([P(300, -5), P(ARM_LEN, -5), P(ARM_LEN, 5), P(300, 5)], fill=BRONZE + (255,), outline=(150, 110, 60, 255), width=2)
    rv = rivet_pt(k)
    l.circle(rv, 13, fill=SILVER + (255,), outline=(120, 120, 130, 255), width=2)
    if glow_contact > 0.01:
        g = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([2 * (rv[0] - 40), 2 * (rv[1] - 40), 2 * (rv[0] + 40), 2 * (rv[1] + 40)],
                                   fill=(255, 240, 160, int(230 * glow_contact)))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))
    # trenza flexible de la lámina al COM
    p = P(380, 6)
    pts = [p, (p[0] - 30, p[1] + 90), (PINS['COM'] + 20, 420), (PINS['COM'], PIN_Y - 46)]
    l.line(pts, (190, 140, 80, 255), 7)
    l.line([(PINS['COM'], PIN_Y - 46), (PINS['COM'], PIN_Y - 4)], BRONZE + (255,), 8)
    # resorte de retorno (jala la armadura hacia arriba)
    sp_top = (205, 94)
    sp_bot = P(101, -12)
    l.line(_spring_pts(sp_top, sp_bot, 8, 11), (200, 205, 214, 255), 5)
    # corriente por la bobina (cuadritos en los alambres de las patas)
    if flow > 0.01:
        path = [(PINS['b1'], PIN_Y + 40), (PINS['b1'], 535), (170, 505), (235, 470), (300, 505), (PINS['b2'], 535), (PINS['b2'], PIN_Y + 40)]
        for j in range(10):
            q = D.along(path, (t * 0.35 + j / 10) % 1.0)
            l.rect([q[0] - 7, q[1] - 7, q[0] + 7, q[1] + 7], fill=CURR + (int(255 * flow),))
    out = l.done()
    return out


def inside_labels():
    """posiciones (en coordenadas del corte) de los rótulos"""
    return {
        'BOBINA': (235, 420),
        'NÚCLEO': (235, 300),
        'ARMADURA': (300, 205),
        'RESORTE': (205, 50),
        'NC': (CONT_X + 60, NC_Y - 62),
        'NA': (CONT_X - 10, NO_Y + 70),
        'COM': (PINS['COM'], PIN_Y + 75),
    }


# ---------------- botoncito y tablerito de 5 V ----------------
def pushbutton(pressed=0.0, w=120):
    key = ('pbtn', round(pressed, 2), w)
    def mk():
        h = int(w * 0.9)
        l = D.L(w, h)
        l.rrect([4, h * 0.45, w - 4, h - 4], 10, fill=(30, 30, 34, 255), outline=(10, 10, 12, 255), width=3)
        for x in (12, w - 12):
            l.circle((x, h * 0.55), 4, fill=(170, 170, 176, 255))
        dy = 12 * pressed
        l.rrect([w * 0.2, h * 0.2 + dy, w * 0.8, h * 0.52], 14, fill=(150, 20, 24, 255))
        l.rrect([w * 0.2, h * 0.12 + dy, w * 0.8, h * 0.46 + dy], 16, fill=(230, 50, 50, 255), outline=(150, 20, 24, 255), width=3)
        l.rrect([w * 0.28, h * 0.16 + dy, w * 0.5, h * 0.24 + dy], 6, fill=(255, 150, 150, 200))
        return l.done()
    return cached(key, mk)


def small_led(on=0.0, r=14):
    key = ('sled', round(on, 2), r)
    def mk():
        l = D.L(r * 6, r * 6)
        c = (r * 3, r * 3)
        if on > 0.02:
            l.circle(c, r * 2.6, fill=(255, 60, 60, int(90 * on)))
        col = tuple(int(a + (b - a) * on) for a, b in zip((110, 30, 30), (255, 90, 80)))
        l.circle(c, r, fill=col + (255,), outline=(60, 10, 10, 255), width=2)
        l.circle((c[0] - r * 0.35, c[1] - r * 0.35), r * 0.3, fill=(255, 255, 255, 150))
        return l.done()
    return cached(key, mk)


# ---------------- reflector gigante ----------------
def floodlight(on=0.0, w=330):
    """reflector de escenario en un trípode, con lente redonda"""
    key = ('flood', round(on, 2), w)
    def mk():
        h = int(w * 1.75)
        l = D.L(w, h)
        cx = w / 2
        # trípode
        for dx in (-w * 0.38, 0, w * 0.38):
            l.line([(cx, h * 0.56), (cx + dx, h - 6)], (120, 122, 132, 255), 10)
        l.rect([cx - 9, h * 0.42, cx + 9, h * 0.62], fill=(80, 82, 90, 255))
        # horquilla
        l.line([(cx - w * 0.42, h * 0.3), (cx - w * 0.42, h * 0.44), (cx + w * 0.42, h * 0.44), (cx + w * 0.42, h * 0.3)], (80, 82, 90, 255), 12)
        # cabeza (cilindro negro visto de frente)
        r = w * 0.42
        cy = h * 0.27
        l.circle((cx, cy), r, fill=(28, 28, 32, 255), outline=(70, 72, 80, 255), width=6)
        for k in range(6):
            a = k * math.pi / 3 + 0.3
            l.circle((cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9), 4, fill=(90, 92, 100, 255))
        lc = tuple(int(a + (b - a) * on) for a, b in zip((70, 76, 90), (255, 250, 220)))
        l.circle((cx, cy), r * 0.78, fill=lc + (255,), outline=(150, 150, 160, 255), width=4)
        for k in range(1, 4):
            l.circle((cx, cy), r * 0.78 * k / 4, outline=(255, 255, 255, int(60 + 60 * on)), width=2)
        l.circle((cx - r * 0.3, cy - r * 0.3), r * 0.15, fill=(255, 255, 255, int(110 + 120 * on)))
        return l.done()
    return cached(key, mk)


def beam(on=1.0, length=900, w0=230, w1=820):
    """cono de luz del reflector (se dibuja hacia abajo-izquierda)"""
    key = ('beam', round(on, 2), length, w0, w1)
    def mk():
        im = Image.new('RGBA', (w1 + 40, length), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx = (w1 + 40) / 2
        for k in range(14):
            u = k / 13
            a = int(18 * on * (1 - u * 0.6))
            ww0 = w0 * (1 - u * 0.7); ww1 = w1 * (1 - u * 0.5)
            d.polygon([(cx - ww0 / 2, 0), (cx + ww0 / 2, 0), (cx + ww1 / 2, length), (cx - ww1 / 2, length)], fill=(255, 245, 200, a))
        return im.filter(ImageFilter.GaussianBlur(10))
    return cached(key, mk)


# ---------------- medidor de aguja ----------------
def gauge(txt, frac, col=(255, 217, 61), w=230, sub=''):
    key = ('gauge', txt, round(frac, 3), col, w, sub)
    def mk():
        h = int(w * 0.8)
        l = D.L(w, h)
        l.rrect([4, 4, w - 4, h - 4], 18, fill=(236, 232, 220, 255), outline=(60, 60, 66, 255), width=6)
        cx, cy, r = w / 2, h * 0.78, w * 0.38
        for k in range(11):
            a = math.pi + k * math.pi / 10
            r0 = r * (0.86 if k % 5 else 0.78)
            l.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * r, cy + math.sin(a) * r)], (40, 40, 46, 255), 3)
        a = math.pi + math.pi * max(0.0, min(1.0, frac))
        l.line([(cx, cy), (cx + math.cos(a) * r * 0.95, cy + math.sin(a) * r * 0.95)], (210, 40, 40, 255), 5)
        l.circle((cx, cy), 9, fill=(40, 40, 46, 255))
        l.text((cx, h * 0.22), txt, int(w * 0.13), fill=(30, 30, 34))
        if sub:
            l.text((cx, h * 0.92), sub, int(w * 0.075), fill=(80, 80, 86))
        return l.done()
    return cached(key, mk)


# ---------------- gráfica del pico al apagar ----------------
def spike_graph(k=1.0, diode=0.0, w=470, h=300):
    """voltaje en la bobina al apagarla: sin diodo, un pico enorme hacia arriba; con diodo, casi nada.
    k = cuánto de la gráfica se ha dibujado (0..1)."""
    key = ('spike', round(k, 2), round(diode, 2), w, h)
    def mk():
        l = D.L(w, h)
        l.rrect([2, 2, w - 2, h - 2], 16, fill=(18, 22, 30, 230), outline=(90, 100, 120, 255), width=3)
        x0, x1 = 40, w - 20
        y_on, y_base, y_top = h * 0.62, h * 0.8, 26
        l.line([(x0, 20), (x0, h - 20)], (160, 170, 190, 255), 3)
        l.line([(x0, y_base), (x1, y_base)], (160, 170, 190, 255), 3)
        l.text((x1 - 6, y_base + 18), 'tiempo', 18, fill=(160, 170, 190), anchor='rm')
        l.text((x0 + 8, 34), 'voltaje', 18, fill=(160, 170, 190), anchor='lm')
        xo = x0 + (x1 - x0) * 0.42
        # traza sin diodo (roja)
        pts = []
        n = 120
        for i in range(n + 1):
            u = i / n
            if u > k:
                break
            x = x0 + (x1 - x0) * u
            if x < xo:
                y = y_on
            else:
                v = math.exp(-(x - xo) / 18)
                y = y_base - (y_base - y_top) * v if x > xo + 1 else y_top
            pts.append((x, y))
        if len(pts) > 1:
            l.line(pts, (255, 80, 80, int(255 * (1 - 0.6 * diode))), 5)
        if k > 0.45:
            l.text((xo + 50, y_top + 10), 'PICO', 24, fill=(255, 110, 110), anchor='lm')
        # traza con diodo (verde)
        if diode > 0.01:
            pts = []
            for i in range(n + 1):
                u = i / n
                x = x0 + (x1 - x0) * u
                if x < xo:
                    y = y_on
                else:
                    y = y_base - (y_on - y_base) * 0.0 - (y_base - y_on) * math.exp(-(x - xo) / 60) * 1.0
                    y = y_base - (y_base - y_on) * math.exp(-(x - xo) / 60)
                pts.append((x, y))
            l.line(pts, (90, 230, 130, int(255 * diode)), 6)
            l.text((x1 - 10, y_on - 40), 'CON DIODO', 20, fill=(120, 240, 150), anchor='rm')
        l.text((xo, h - 22), 'apaga', 18, fill=(200, 200, 210))
        l.line([(xo, y_base - 6), (xo, y_base + 6)], (200, 200, 210, 255), 3)
        return l.done()
    return cached(key, mk)


def diode_part(w=170):
    key = ('diode', w)
    def mk():
        h = int(w * 0.35)
        l = D.L(w, h)
        l.line([(0, h / 2), (w, h / 2)], (200, 202, 210, 255), 5)
        l.rrect([w * 0.28, h * 0.18, w * 0.72, h * 0.82], 10, fill=(30, 30, 34, 255))
        l.rect([w * 0.6, h * 0.18, w * 0.66, h * 0.82], fill=(220, 222, 230, 255))
        l.rect([w * 0.32, h * 0.24, w * 0.56, h * 0.34], fill=(255, 255, 255, 50))
        return l.done()
    return cached(key, mk)


# ---------------- carro (frente) ----------------
def car_front(lights=0.0, w=560):
    key = ('car', round(lights, 2), w)
    def mk():
        h = int(w * 0.62)
        l = D.L(w, h)
        # llantas
        for x in (w * 0.16, w * 0.84):
            l.rrect([x - 40, h * 0.72, x + 40, h - 4], 12, fill=(26, 26, 30, 255))
        # carrocería
        l.poly([(w * 0.2, h * 0.12), (w * 0.8, h * 0.12), (w * 0.9, h * 0.42), (w * 0.97, h * 0.48), (w * 0.97, h * 0.82),
                (w * 0.03, h * 0.82), (w * 0.03, h * 0.48), (w * 0.1, h * 0.42)], fill=(214, 60, 52, 255), outline=(120, 30, 26, 255), width=5)
        # parabrisas
        l.poly([(w * 0.25, h * 0.17), (w * 0.75, h * 0.17), (w * 0.84, h * 0.4), (w * 0.16, h * 0.4)], fill=(140, 190, 230, 255), outline=(70, 80, 90, 255), width=4)
        l.poly([(w * 0.3, h * 0.2), (w * 0.42, h * 0.2), (w * 0.32, h * 0.37), (w * 0.22, h * 0.37)], fill=(255, 255, 255, 70))
        # parrilla y bomper
        l.rrect([w * 0.33, h * 0.52, w * 0.67, h * 0.7], 10, fill=(40, 40, 46, 255))
        for k in range(5):
            y = h * 0.55 + k * h * 0.03
            l.line([(w * 0.35, y), (w * 0.65, y)], (90, 92, 100, 255), 3)
        l.rrect([w * 0.03, h * 0.74, w * 0.97, h * 0.84], 8, fill=(60, 62, 70, 255))
        # farolas
        for x in (w * 0.17, w * 0.83):
            col = tuple(int(a + (b - a) * lights) for a, b in zip((180, 186, 196), (255, 252, 210)))
            l.rrect([x - 55, h * 0.5, x + 55, h * 0.66], 14, fill=col + (255,), outline=(90, 92, 100, 255), width=4)
        return l.done()
    return cached(key, mk)


# ---------------- Mark II: panel de relés, polilla y cuaderno ----------------
PANEL_COLS, PANEL_ROWS = 10, 9
def relay_panel(w=600, hi=None):
    """pared de relés (rack). hi = (col, row) del relé resaltado."""
    key = ('panel', w, hi)
    def mk():
        h = int(w * 1.0)
        l = D.L(w, h)
        l.rrect([4, 4, w - 4, h - 4], 12, fill=(70, 74, 82, 255), outline=(30, 32, 36, 255), width=6)
        l.rect([20, 18, w - 20, 60], fill=(30, 32, 36, 255))
        l.text((w / 2, 39), 'MARK II · PANEL F', 26, fill=(240, 220, 150))
        cw = (w - 40) / PANEL_COLS
        rh = (h - 90) / PANEL_ROWS
        for r in range(PANEL_ROWS):
            for c in range(PANEL_COLS):
                x = 20 + c * cw; y = 76 + r * rh
                col = (196, 160, 90) if (c + r) % 3 else (180, 150, 86)
                l.rrect([x + 5, y + 5, x + cw - 5, y + rh - 5], 4, fill=(48, 50, 56, 255))
                l.rect([x + 10, y + 10, x + cw - 10, y + rh * 0.55], fill=col + (255,))
                l.rect([x + 12, y + rh * 0.58, x + cw - 12, y + rh - 10], fill=(150, 154, 162, 255))
                for kx in range(3):
                    l.line([(x + 14 + kx * (cw - 28) / 2, y + rh * 0.6), (x + 14 + kx * (cw - 28) / 2, y + rh - 12)], (90, 92, 100, 255), 2)
                if hi == (c, r):
                    l.rrect([x + 1, y + 1, x + cw - 1, y + rh - 1], 6, outline=(255, 80, 80, 255), width=5)
        return l.done()
    return cached(key, mk)


def panel_cell_center(w, cell):
    h = int(w * 1.0)
    cw = (w - 40) / PANEL_COLS; rh = (h - 90) / PANEL_ROWS
    c, r = cell
    return 20 + (c + 0.5) * cw - w / 2, 76 + (r + 0.5) * rh - h / 2


def moth(flap=0.0, w=150, flat=False):
    """polilla genérica (alas cafés). flap = fase del aleteo (0..1). flat = alas abiertas y quietas (pegada)."""
    key = ('moth', round(flap, 2), w, flat)
    def mk():
        h = int(w * 0.8)
        l = D.L(w, h)
        cx, cy = w / 2, h / 2
        k = 1.0 if flat else 0.35 + 0.65 * abs(math.cos(flap * math.pi))
        for sgn in (-1, 1):
            wing = [(cx, cy - 6), (cx + sgn * w * 0.46 * k, cy - h * 0.34), (cx + sgn * w * 0.48 * k, cy + h * 0.02), (cx + sgn * 4, cy + 4)]
            l.poly(wing, fill=(150, 116, 78, 255), outline=(86, 62, 40, 255), width=3)
            wing2 = [(cx, cy), (cx + sgn * w * 0.36 * k, cy + h * 0.06), (cx + sgn * w * 0.3 * k, cy + h * 0.32), (cx + sgn * 3, cy + 12)]
            l.poly(wing2, fill=(128, 98, 66, 255), outline=(86, 62, 40, 255), width=3)
            l.circle((cx + sgn * w * 0.26 * k, cy - h * 0.14), w * 0.04 * max(0.4, k), fill=(90, 66, 44, 255))
            l.line([(cx + sgn * 3, cy - h * 0.16), (cx + sgn * w * 0.16, cy - h * 0.44)], (86, 62, 40, 255), 3)
        l.rrect([cx - 7, cy - h * 0.18, cx + 7, cy + h * 0.28], 7, fill=(100, 76, 50, 255))
        return l.done()
    return cached(key, mk)


def logbook(tape=0.0, text_k=1.0, w=560):
    """hoja del cuaderno (amarillenta, con renglones). La polilla se pega aparte con tape_strip()."""
    key = ('log', round(text_k, 2), w)
    def mk():
        h = int(w * 0.82)
        l = D.L(w, h)
        l.rrect([4, 4, w - 4, h - 4], 8, fill=(244, 234, 200, 255), outline=(170, 150, 110, 255), width=4)
        for k in range(1, 11):
            y = 30 + k * (h - 40) / 11
            l.line([(20, y), (w - 20, y)], (180, 200, 220, 255), 2)
        l.line([(70, 10), (70, h - 10)], (220, 120, 120, 255), 2)
        l.text((90, 44), '9/9/47', 26, fill=(40, 50, 90), anchor='lm')
        l.text((90, 84), 'Relay #70 Panel F', 24, fill=(40, 50, 90), anchor='lm')
        txt = 'First actual case of bug being found.'
        n = int(len(txt) * text_k)
        if n > 0:
            l.text((84, h - 70), txt[:n], 22, fill=(40, 50, 90), anchor='lm')
        return l.done()
    return cached(key, mk)


def tape_strip(w=230):
    key = ('tape', w)
    def mk():
        l = D.L(w, 60)
        l.poly([(6, 10), (w - 4, 4), (w - 10, 54), (2, 56)], fill=(255, 252, 230, 150), outline=(230, 225, 200, 160), width=2)
        return l.done()
    return cached(key, mk)


# ---------------- símbolo del relé (remate y reto) ----------------
def relay_symbol(state=0.0, hide=False, w=420, lab=True):
    """símbolo: bobina (rectángulo con diagonal) unida con línea punteada a un contacto conmutado.
    state 0 = apagado (COM toca NC), 1 = encendido (COM toca NA). hide = tapar la lámina con '?' (reto)."""
    key = ('rsym', round(state, 2), hide, w, lab)
    def mk():
        h = int(w * 0.95)
        l = D.L(w, h)
        l.rrect([2, 2, w - 2, h - 2], 20, fill=(18, 22, 30, 225), outline=(110, 120, 140, 255), width=3)
        col = (235, 240, 250, 255)
        # bobina
        bx0, by0, bx1, by1 = w * 0.1, h * 0.36, w * 0.36, h * 0.6
        l.rect([bx0, by0, bx1, by1], outline=col, width=5)
        l.line([(bx0, by1), (bx1, by0)], col, 3)
        l.line([((bx0 + bx1) / 2, by0), ((bx0 + bx1) / 2, h * 0.15)], col, 4)
        l.line([((bx0 + bx1) / 2, by1), ((bx0 + bx1) / 2, h * 0.85)], col, 4)
        # contactos
        comx, comy = w * 0.6, h * 0.8
        ncx, ncy = w * 0.86, h * 0.3
        nax, nay = w * 0.86, h * 0.52
        for (x, y) in ((ncx, ncy), (nax, nay)):
            l.line([(x - 26, y), (x + 34, y)], col, 4)
            l.circle((x - 26, y), 6, fill=col)
        l.line([(comx, comy), (comx, h * 0.92)], col, 4)
        l.circle((comx, comy), 7, fill=col)
        if not hide:
            # lámina: de COM hacia NC (apagado) o NA (encendido)
            ty = ncy + (nay - ncy) * state
            l.line([(comx, comy), (ncx - 30, ty + (6 if state < 0.5 else -6))], (255, 217, 61, 255), 6)
            # unión punteada con la bobina
            mx = (comx + ncx) / 2
            my = comy + (ty - comy) * 0.5
            for k in range(7):
                x = bx1 + 10 + k * (mx - bx1 - 10) / 7
                l.line([(x, (by0 + by1) / 2), (x + (mx - bx1) / 16, (by0 + by1) / 2)], (150, 160, 180, 255), 3)
        else:
            l.rrect([comx - 34, ncy + 4, ncx - 36, comy - 12], 10, fill=(60, 66, 80, 255), outline=(255, 217, 61, 255), width=3)
            l.text(((comx + ncx - 70) / 2, (ncy + comy) / 2 - 6), '?', 64, fill=(255, 217, 61))
        if lab:
            l.text((ncx + 2, ncy - 26), 'NC', 26, fill=(255, 200, 140))
            l.text((nax + 2, nay + 28), 'NA', 26, fill=(150, 225, 255))
            l.text((comx - 46, comy + 2), 'COM', 24, fill=(255, 230, 140), anchor='rm')
            l.rrect([(bx0 + bx1) / 2 - 48, by1 + 20, (bx0 + bx1) / 2 + 48, by1 + 48], 6, fill=(18, 22, 30, 255))
            l.text(((bx0 + bx1) / 2, by1 + 34), 'BOBINA', 20, fill=(220, 220, 230))
        return l.done()
    return cached(key, mk)
