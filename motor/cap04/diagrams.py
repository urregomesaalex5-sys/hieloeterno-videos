# Diagramas del capítulo 3: sensor de inclinación, circuito, usos y acelerómetro.
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S

SS = 2  # supermuestreo

GRAV = (255, 77, 109)
GLASS = (95, 168, 211)
GLASS_EDGE = (191, 215, 234)
COPPER = (217, 142, 58)
GOLD = (242, 201, 76)
SILVER = (217, 222, 228)
GREEN = (61, 220, 132)
CURR = (255, 217, 61)
WIRE = (232, 232, 232)
DARK = (30, 34, 42)


class L:
    """lienzo RGBA con supermuestreo"""
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def s(self, v):
        return [x * SS for x in v] if isinstance(v, (list, tuple)) else v * SS

    def rrect(self, box, r, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(self.s(box), r * SS, fill=fill, outline=outline, width=int(width * SS))

    def rect(self, box, fill=None, outline=None, width=1):
        self.d.rectangle(self.s(box), fill=fill, outline=outline, width=int(width * SS))

    def circle(self, c, r, fill=None, outline=None, width=1):
        self.d.ellipse(self.s([c[0] - r, c[1] - r, c[0] + r, c[1] + r]), fill=fill, outline=outline, width=int(width * SS))

    def line(self, pts, fill, width=1):
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=int(width * SS), joint='curve')

    def poly(self, pts, fill=None, outline=None, width=1):
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill, outline=outline, width=int(width * SS))

    def text(self, xy, txt, size, fill=(255, 255, 255), anchor='mm', stroke=0, stroke_fill=(0, 0, 0), black=False):
        self.d.text((xy[0] * SS, xy[1] * SS), txt, font=S.font(int(size * SS), black), fill=fill, anchor=anchor,
                    stroke_width=int(stroke * SS), stroke_fill=stroke_fill)

    def done(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def label(txt, size=30, fill=(255, 255, 255), bg=(20, 22, 28, 220), outline=None, pad=12):
    f = S.font(size)
    w, h, b = S.text_size(txt, f)
    lw, lh = w + 2 * pad, size + 2 * pad - 4
    l = L(lw + 8, lh + 8)
    l.rrect([4, 4, 4 + lw, 4 + lh], 10, fill=bg, outline=outline, width=3 if outline else 1)
    l.text((4 + lw / 2, 4 + lh / 2), txt, size, fill=fill)
    return l.done()


def arrow(l, p0, p1, color, width=10, head=26):
    l.line([p0, p1], color, width)
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    h1 = (p1[0] - head * math.cos(a - 0.45), p1[1] - head * math.sin(a - 0.45))
    h2 = (p1[0] - head * math.cos(a + 0.45), p1[1] - head * math.sin(a + 0.45))
    tip = (p1[0] + 6 * math.cos(a), p1[1] + 6 * math.sin(a))
    l.poly([tip, h1, h2], fill=color)


def gravity_arrow(length=220, grow=1.0, txt=True):
    """flecha roja hacia abajo con la palabra GRAVEDAD"""
    W_, H_ = 120, length + 70
    l = L(W_, H_)
    L_ = length * grow
    if L_ > 10:
        arrow(l, (W_ / 2, 10), (W_ / 2, 10 + L_), GRAV + (255,), width=14, head=34)
    im = l.done()
    if txt:
        t = label('GRAVEDAD', 26, fill=GRAV, bg=(20, 10, 14, 230))
        out = Image.new('RGBA', (max(W_, t.size[0]), H_ + t.size[1]), (0, 0, 0, 0))
        out.alpha_composite(t, ((out.size[0] - t.size[0]) // 2, 0))
        out.alpha_composite(im, ((out.size[0] - W_) // 2, t.size[1] - 8))
        return out
    return im


# ---------------- Diagrama A: sensor por dentro ----------------
TUBE_W, TUBE_H = 920, 280
TCX, TCY = 370, 140         # centro del tubo dentro de la capa (pivote de giro)
T_X0, T_X1 = 40, 700        # tubo exterior
T_Y0, T_Y1 = 75, 205
WALL = 15
CAP_X0 = 650
PRONG_X0, PRONG_X1 = 540, 660
PRONG_DY = 30
BALL_R = 40
BALL_REST = (T_X0 + WALL + BALL_R + 2, T_Y1 - WALL - BALL_R)   # abajo a la izquierda
BALL_TOUCH = (507, TCY)                                          # encajada en las púas
LEG_X0, LEG_X1 = 700, 850


def tube_layer(ball_x=None, ball_y=None, ball_rot=0.0, closed=0.0, parts=('tube', 'ball', 'cap'), legs_down=False,
               flash=0.0):
    """capa del sensor. closed 0..1 colorea las púas en verde."""
    l = L(TUBE_W, TUBE_H)
    if 'tube' in parts:
        # vidrio
        l.rrect([T_X0, T_Y0, T_X1, T_Y1], 30, fill=GLASS + (80,), outline=GLASS_EDGE + (255,), width=5)
        l.rrect([T_X0 + WALL, T_Y0 + WALL, T_X1 - 10, T_Y1 - WALL], 22, fill=(20, 40, 60, 90))
        # brillo del vidrio
        l.rrect([T_X0 + 30, T_Y0 + 8, T_X1 - 80, T_Y0 + 18], 5, fill=(255, 255, 255, 110))
    if 'cap' in parts:
        # púas (contactos)
        cg = tuple(int(GOLD[i] + (GREEN[i] - GOLD[i]) * closed) for i in range(3))
        for dy in (-PRONG_DY, PRONG_DY):
            l.rrect([PRONG_X0, TCY + dy - 7, PRONG_X1, TCY + dy + 7], 4, fill=cg + (255,), outline=(90, 70, 20, 255), width=2)
        # tapa de cobre
        l.rrect([CAP_X0, T_Y0 - 4, T_X1 + 6, T_Y1 + 4], 10, fill=COPPER + (255,), outline=(120, 70, 20, 255), width=4)
        l.rect([CAP_X0 + 8, T_Y0 + 8, CAP_X0 + 16, T_Y1 - 8], fill=(240, 180, 110, 255))
        # patitas
        for dy in (-PRONG_DY, PRONG_DY):
            if legs_down:
                l.line([(T_X1 + 6, TCY + dy), (T_X1 + 40 + (dy > 0) * 30, TCY + dy),
                        (T_X1 + 40 + (dy > 0) * 30, TCY + 130)], SILVER + (255,), 11)
            else:
                l.rrect([T_X1 + 6, TCY + dy - 6, LEG_X1, TCY + dy + 6], 4, fill=SILVER + (255,), outline=(120, 125, 130, 255), width=2)
    if 'ball' in parts and ball_x is not None:
        bx, by = ball_x, ball_y
        l.circle((bx, by), BALL_R, fill=(150, 156, 164, 255), outline=(90, 95, 100, 255), width=3)
        l.circle((bx - 4, by - 4), BALL_R - 9, fill=SILVER + (255,))
        # marca que gira
        mx = bx + math.cos(ball_rot) * 22; my = by + math.sin(ball_rot) * 22
        l.circle((mx, my), 6, fill=(170, 176, 184, 255))
        l.circle((bx - 15, by - 16), 9, fill=(255, 255, 255, 255))
        if flash > 0:
            for k in range(8):
                a = k * math.pi / 4 + 0.3
                r0, r1 = BALL_R + 8, BALL_R + 8 + 30 * flash
                cx, cy = bx + 34, by
                l.line([(cx + math.cos(a) * 12, cy + math.sin(a) * 12), (cx + math.cos(a) * (12 + 34 * flash), cy + math.sin(a) * (12 + 34 * flash))],
                       CURR + (int(255 * flash),), 5)
    return l.done()


def tube_path_points():
    """camino de la corriente (en coords de la capa): patita sup -> púa sup -> bolita -> púa inf -> patita inf"""
    return [(LEG_X1, TCY - PRONG_DY), (PRONG_X0 + 10, TCY - PRONG_DY), (BALL_TOUCH[0] + 18, TCY - 18),
            (BALL_TOUCH[0] + 18, TCY + 18), (PRONG_X0 + 10, TCY + PRONG_DY), (LEG_X1, TCY + PRONG_DY)]


def along(pts, u):
    """punto en una polilínea a fracción u (0..1)"""
    segs = []
    tot = 0
    for i in range(len(pts) - 1):
        d = math.dist(pts[i], pts[i + 1]); segs.append(d); tot += d
    u = (u % 1.0) * tot
    for i, d in enumerate(segs):
        if u <= d:
            k = u / d if d else 0
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k)
        u -= d
    return pts[-1]


def rotate_pt(p, c, ang):
    """rota p alrededor de c (ang en radianes, positivo = horario en pantalla)"""
    x, y = p[0] - c[0], p[1] - c[1]
    ca, sa = math.cos(ang), math.sin(ang)
    return (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)


# ---------------- Diagrama B: circuito ----------------
def battery_img():
    l = L(130, 250)
    l.rrect([20, 30, 110, 230], 14, fill=(43, 47, 54, 255), outline=(150, 155, 165, 255), width=4)
    l.rrect([20, 30, 110, 90], 14, fill=(230, 140, 40, 255))
    l.rect([20, 70, 110, 90], fill=(230, 140, 40, 255))
    l.rrect([50, 12, 80, 32], 5, fill=GOLD + (255,))
    l.text((65, 58), '+', 44, fill=(30, 30, 30))
    l.text((65, 205), '−', 44, fill=(220, 220, 220))
    l.text((65, 145), '3 V', 30, fill=(255, 255, 255))
    return l.done()


def led_img(on=0.0):
    l = L(260, 260)
    c = (130, 130)
    if on > 0:
        for r, a in ((125, 0.18), (90, 0.35)):
            l.circle(c, r * (0.8 + 0.2 * on), fill=(255, 60, 60, int(255 * a * on)))
        for k in range(8):
            ang = k * math.pi / 4
            l.line([(c[0] + math.cos(ang) * 68, c[1] + math.sin(ang) * 68),
                    (c[0] + math.cos(ang) * (68 + 40 * on), c[1] + math.sin(ang) * (68 + 40 * on))], CURR + (int(255 * on),), 7)
    col = tuple(int(90 + (255 - 90) * on) if i == 0 else int(30 + (59 - 30) * on) for i in range(3))
    l.circle(c, 55, fill=col + (255,), outline=(255, 200, 200, 255) if on > 0.5 else (140, 70, 70, 255), width=4)
    # símbolo: triángulo hacia abajo y barra
    l.poly([(c[0] - 26, c[1] - 20), (c[0] + 26, c[1] - 20), (c[0], c[1] + 18)], fill=(255, 255, 255, 230))
    l.line([(c[0] - 26, c[1] + 20), (c[0] + 26, c[1] + 20)], (255, 255, 255, 230), 6)
    return l.done()


def resistor_img():
    l = L(200, 80)
    l.rrect([25, 17, 175, 63], 20, fill=(232, 216, 176, 255), outline=(150, 130, 90, 255), width=3)
    for x, col in ((60, (200, 40, 40)), (85, (200, 40, 40)), (110, (110, 60, 20)), (148, (220, 180, 60))):
        l.rect([x - 6, 17, x + 6, 63], fill=col + (255,))
    return l.done()


# ---------------- Tarjetas de usos ----------------
CARD_W, CARD_H = 430, 250

def card_base(title):
    l = L(CARD_W, CARD_H)
    l.rrect([4, 4, CARD_W - 4, CARD_H - 4], 26, fill=(24, 28, 36, 235), outline=(255, 185, 70, 255), width=5)
    l.text((CARD_W / 2, CARD_H - 32), title, 30, fill=(255, 205, 110))
    return l


def card_alarm(t):
    l = card_base('ALARMAS')
    tilt = 0.25 * math.sin(t * 9) * min(1, t * 2)
    c = (CARD_W / 2, 100)
    box = [(-60, -50), (60, -50), (60, 55), (-60, 55)]
    l.poly([rotate_pt((c[0] + x, c[1] + y), c, tilt) for x, y in box], fill=(200, 60, 60, 255), outline=(255, 160, 160, 255), width=4)
    # campana
    bc = rotate_pt((c[0], c[1] - 5), c, tilt)
    l.circle(bc, 30, fill=GOLD + (255,))
    l.rect([bc[0] - 34, bc[1] + 10, bc[0] + 34, bc[1] + 30], fill=GOLD + (255,))
    l.circle((bc[0], bc[1] + 34), 7, fill=(160, 110, 20, 255))
    # ondas
    for k in range(3):
        ph = (t * 2.5 + k / 3) % 1
        a = int(255 * (1 - ph))
        r = 70 + ph * 50
        l.d.arc([(c[0] - r) * SS, (c[1] - r) * SS, (c[0] + r) * SS, (c[1] + r) * SS], -40, 40, fill=(255, 255, 255, a), width=5 * SS)
        l.d.arc([(c[0] - r) * SS, (c[1] - r) * SS, (c[0] + r) * SS, (c[1] + r) * SS], 140, 220, fill=(255, 255, 255, a), width=5 * SS)
    return l.done()


def card_toy(t):
    l = card_base('JUGUETES')
    tilt = -0.35 * max(0, math.sin(t * 4)) if t > 0.3 else 0
    c = (CARD_W / 2 - 20, 115)
    Y = (255, 214, 50, 255); O = (255, 140, 30, 255); K = (20, 20, 20, 255)
    blocks = [(-40, -10, 60, 50, Y), (0, -70, 50, 60, Y), (35, -50, 30, 16, O), (12, -55, 10, 10, K)]
    for x, y, w, h, col in blocks:
        pts = [(c[0] + x, c[1] + y), (c[0] + x + w, c[1] + y), (c[0] + x + w, c[1] + y + h), (c[0] + x, c[1] + y + h)]
        l.poly([rotate_pt(p, (c[0], c[1] + 50), tilt) for p in pts], fill=col)
    if tilt < -0.15:
        l.rrect([CARD_W - 175, 30, CARD_W - 30, 85], 20, fill=(255, 255, 255, 240))
        l.text((CARD_W - 102, 57), '¡cuac!', 30, fill=(30, 30, 30))
    return l.done()


def card_pinball(t):
    l = card_base('PINBALL')
    c = (CARD_W / 2, 100)
    l.poly([(c[0] - 70, c[1] - 70), (c[0] + 70, c[1] - 70), (c[0] + 95, c[1] + 70), (c[0] - 95, c[1] + 70)],
           fill=(40, 70, 160, 255), outline=(150, 190, 255, 255), width=4)
    bx = c[0] + 40 * math.sin(t * 5); by = c[1] - 20 + 30 * math.cos(t * 3.3)
    l.circle((bx, by), 12, fill=SILVER + (255,))
    l.line([(c[0] - 55, c[1] + 50), (c[0] - 15, c[1] + 60)], (255, 255, 255, 255), 8)
    l.line([(c[0] + 55, c[1] + 50), (c[0] + 15, c[1] + 60)], (255, 255, 255, 255), 8)
    if int(t * 4) % 2 == 0 and t > 0.4:
        l.rrect([c[0] - 80, c[1] - 30, c[0] + 80, c[1] + 25], 10, fill=(220, 30, 30, 245), outline=(255, 220, 220, 255), width=4)
        l.text((c[0], c[1] - 3), 'TILT', 46, fill=(255, 255, 255), black=True)
    return l.done()


def card_heater(t):
    l = card_base('CALENTADORES')
    k = S.ease_back(S.seg(t, 0.5, 1.0))
    ang = k * math.pi / 2
    c = (CARD_W / 2, 110)
    box = [(-45, -60), (45, -60), (45, 60), (-45, 60)]
    piv = (c[0] + 45, c[1] + 60)
    l.poly([rotate_pt((c[0] + x, c[1] + y), piv, ang) for x, y in box], fill=(240, 130, 40, 255), outline=(255, 210, 160, 255), width=4)
    for i in range(3):
        y0 = c[1] - 35 + i * 30
        pts = [rotate_pt((c[0] - 30 + j * 6, y0 + 5 * math.sin(j * 1.1)), piv, ang) for j in range(11)]
        l.line(pts, (120, 40, 10, 255), 5)
    if t < 0.5:
        for i in range(3):
            x = c[0] - 30 + i * 30
            pts = [(x + 6 * math.sin(j * 0.9 + t * 10), c[1] - 75 - j * 6) for j in range(8)]
            l.line(pts, (255, 120, 60, 200), 5)
    else:
        a = S.seg(t, 0.9, 1.1)
        if a > 0:
            l.rrect([c[0] - 150, c[1] - 70, c[0] - 50, c[1] - 20], 10, fill=(90, 90, 100, int(240 * a)))
            l.text((c[0] - 100, c[1] - 45), 'OFF', 32, fill=(255, 255, 255, int(255 * a)))
    return l.done()


# ---------------- Diagrama C: celular y acelerómetro ----------------
PH_W, PH_H = 300, 590

def phone_img(content_rot=0.0, chip_glow=0.0):
    pad = 40
    l = L(PH_W + 2 * pad, PH_H + 2 * pad)
    x0, y0 = pad, pad
    l.rrect([x0, y0, x0 + PH_W, y0 + PH_H], 44, fill=(30, 35, 43, 255), outline=(154, 165, 177, 255), width=6)
    # pantalla con degradado
    sx0, sy0, sx1, sy1 = x0 + 16, y0 + 26, x0 + PH_W - 16, y0 + PH_H - 26
    g = np.zeros(((sy1 - sy0) * SS, (sx1 - sx0) * SS, 4), np.uint8)
    for y in range(g.shape[0]):
        k = y / g.shape[0]
        g[y, :, :3] = [int(79 + (21 - 79) * k), int(195 + (101 - 195) * k), int(247 + (192 - 247) * k)]
        g[y, :, 3] = 255
    gi = Image.fromarray(g, 'RGBA')
    m = Image.new('L', gi.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, gi.size[0] - 1, gi.size[1] - 1], 30 * SS, fill=255)
    l.im.paste(gi, (sx0 * SS, sy0 * SS), m)
    # contenido: bloque de césped + flecha arriba, siempre derecho
    c = ((sx0 + sx1) / 2, (sy0 + sy1) / 2 + 15)
    def R(p):
        return rotate_pt(p, ((sx0 + sx1) / 2, (sy0 + sy1) / 2), content_rot)
    gb = [(-42, -15), (42, -15), (42, 65), (-42, 65)]
    l.poly([R((c[0] + x, c[1] + y)) for x, y in gb], fill=(134, 96, 67, 255))
    gt = [(-42, -15), (42, -15), (42, 8), (-42, 8)]
    l.poly([R((c[0] + x, c[1] + y)) for x, y in gt], fill=(106, 170, 64, 255))
    ar = [(0, -98), (30, -58), (10, -58), (10, -25), (-10, -25), (-10, -58), (-30, -58)]
    l.poly([R((c[0] + x, c[1] + y)) for x, y in ar], fill=(255, 255, 255, 255))
    # chip
    cc = ((sx0 + sx1) / 2, sy1 - 110)
    if chip_glow > 0:
        l.circle(cc, 45, fill=(255, 220, 80, int(120 * chip_glow)))
    l.rect([cc[0] - 22, cc[1] - 22, cc[0] + 22, cc[1] + 22], fill=(25, 25, 30, 255), outline=(200, 200, 210, 255), width=3)
    for i in range(4):
        for s in (-1, 1):
            l.line([(cc[0] - 15 + i * 10, cc[1] + s * 22), (cc[0] - 15 + i * 10, cc[1] + s * 30)], (200, 200, 210, 255), 3)
    return l.done(), (pad + (sx0 + sx1) / 2 - pad, pad + sy1 - 110 - pad)


def mems_img(shift=(0.0, 0.0), highlight=0.0):
    """vista interna: marco, masa naranja, 4 resortes y peines"""
    Wm = 400
    l = L(Wm, Wm)
    c = (Wm / 2, Wm / 2)
    l.rect([20, 20, Wm - 20, Wm - 20], fill=(18, 22, 30, 255), outline=(107, 118, 132, 255), width=6)
    mx, my = c[0] + shift[0], c[1] + shift[1]
    m = 65
    # resortes en zigzag a las 4 esquinas
    anchors = [(40, 40), (Wm - 40, 40), (Wm - 40, Wm - 40), (40, Wm - 40)]
    corners = [(mx - m, my - m), (mx + m, my - m), (mx + m, my + m), (mx - m, my + m)]
    for a, b in zip(anchors, corners):
        pts = []
        n = 9
        dx, dy = b[0] - a[0], b[1] - a[1]
        Ld = math.hypot(dx, dy); nx, ny = -dy / Ld, dx / Ld
        for i in range(n + 1):
            k = i / n
            o = (10 if i % 2 else -10) if 0 < i < n else 0
            pts.append((a[0] + dx * k + nx * o, a[1] + dy * k + ny * o))
        l.line(pts, (240, 240, 240, 255), 4)
    # peines fijos (azules) y móviles (naranja) a izquierda y derecha
    for side in (-1, 1):
        for i in range(5):
            y = c[1] - 48 + i * 24
            # fijo al marco
            fx0 = 20 if side < 0 else Wm - 20
            l.rect(sorted([fx0, c[0] + side * 105]) + [y - 4, y + 4], fill=(61, 139, 255, 255)) if False else None
            if side < 0:
                l.rect([22, y - 4, c[0] - m - 30, y + 4], fill=(61, 139, 255, 255))
                l.rect([mx - m - 40, y + 8, mx - m, y + 16], fill=(255, 159, 28, 255))
            else:
                l.rect([c[0] + m + 30, y - 4, Wm - 22, y + 4], fill=(61, 139, 255, 255))
                l.rect([mx + m, y + 8, mx + m + 40, y + 16], fill=(255, 159, 28, 255))
    l.rect([mx - m, my - m, mx + m, my + m], fill=(255, 159, 28, 255), outline=(255, 210, 140, 255), width=4)
    l.text((mx, my), 'MASA', 30, fill=(60, 30, 0))
    if highlight > 0:
        l.rect([mx - m - 6, my - m - 6, mx + m + 6, my + m + 6], outline=(255, 230, 80, int(255 * highlight)), width=5)
    return l.done()


def magnifier(content, r=190, ring=(255, 230, 140)):
    size = 2 * r + 120
    l = L(size, size)
    c = (r + 20, r + 20)
    # mango
    a = math.radians(45)
    p0 = (c[0] + math.cos(a) * r, c[1] + math.sin(a) * r)
    p1 = (c[0] + math.cos(a) * (r + 90), c[1] + math.sin(a) * (r + 90))
    l.line([p0, p1], (110, 70, 40, 255), 26)
    im = l.done()
    # contenido recortado en círculo
    ct = content.resize((2 * r, 2 * r), Image.LANCZOS)
    mask = Image.new('L', (2 * r * SS, 2 * r * SS), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 2 * r * SS - 1, 2 * r * SS - 1], fill=255)
    mask = mask.resize((2 * r, 2 * r), Image.LANCZOS)
    bg = Image.new('RGBA', (2 * r, 2 * r), (12, 14, 20, 255))
    bg.alpha_composite(ct)
    im.paste(bg, (c[0] - r, c[1] - r), mask)
    l2 = L(size, size)
    l2.circle(c, r, outline=ring + (255,), width=12)
    l2.circle((c[0] - r * 0.45, c[1] - r * 0.5), r * 0.18, fill=(255, 255, 255, 50))
    im.alpha_composite(l2.done())
    return im


def axis_bars(vals):
    """tres barras X Y Z con valores -1..1"""
    l = L(240, 230)
    cols = [(255, 80, 80), (80, 220, 120), (80, 150, 255)]
    for i, (n, v) in enumerate(zip('XYZ', vals)):
        x = 40 + i * 75
        l.rect([x - 22, 20, x + 22, 180], fill=(30, 34, 42, 230), outline=(120, 130, 140, 255), width=2)
        mid = 100
        h = v * 75
        l.rect([x - 18, min(mid, mid - h), x + 18, max(mid, mid - h)], fill=cols[i] + (255,))
        l.line([(x - 22, mid), (x + 22, mid)], (200, 200, 200, 255), 2)
        l.text((x, 205), n, 30, fill=cols[i])
    return l.done()


# ---------------- Burbuja de comentario ----------------
def avatar(size=64):
    l = L(size, size)
    l.circle((size / 2, size / 2), size / 2 - 1, fill=(222, 190, 140, 255))
    # personaje genérico de bloques
    s = size / 8
    l.rect([2.5 * s, 1.8 * s, 5.5 * s, 4.6 * s], fill=(120, 80, 50, 255))
    l.rect([3 * s, 2.8 * s, 5 * s, 4.4 * s], fill=(240, 200, 160, 255))
    l.rect([3.3 * s, 3.2 * s, 3.7 * s, 3.6 * s], fill=(40, 40, 60, 255))
    l.rect([4.3 * s, 3.2 * s, 4.7 * s, 3.6 * s], fill=(40, 40, 60, 255))
    l.rect([2.2 * s, 4.8 * s, 5.8 * s, 7.6 * s], fill=(70, 120, 200, 255))
    return l.done()


def comment_bubble(text, user='@teom074', width=600, heart=0.0, t=0.0):
    h = 150
    tw = S.text_size(text, S.font(38))[0]
    width = max(width, 132 + tw + 50 + (80 if heart > 0 else 0))
    l = L(width + 40, h + 50)
    l.rrect([10, 10, width + 10, h + 10], 30, fill=(250, 250, 250, 250), outline=(200, 200, 200, 255), width=3)
    l.poly([(80, h + 8), (120, h + 8), (70, h + 40)], fill=(250, 250, 250, 250))
    im = l.done()
    av = avatar(78)
    im.alpha_composite(av, (36, 32))
    d = ImageDraw.Draw(im)
    d.text((132, 50), user, font=S.font(30), fill=(70, 70, 80), anchor='lm')
    d.text((132, 102), text, font=S.font(38), fill=(15, 15, 20), anchor='lm')
    if heart > 0:
        pul = 1 + 0.12 * math.sin(t * 10)
        hs = int(70 * heart * pul)
        hl = L(hs + 10, hs + 10)
        r = hs / 4
        cx, cy = (hs + 10) / 2, (hs + 10) / 2 - r * 0.3
        hl.circle((cx - r, cy), r, fill=(230, 30, 60, 255))
        hl.circle((cx + r, cy), r, fill=(230, 30, 60, 255))
        hl.poly([(cx - 2 * r, cy + r * 0.3), (cx + 2 * r, cy + r * 0.3), (cx, cy + 2.2 * r)], fill=(230, 30, 60, 255))
        hh = hl.done()
        im.alpha_composite(hh, (width - hs // 2 - 30, 10 + h // 2 - hs // 2 - 10))
    return im


# ---------------- Botones finales ----------------
def end_button(kind, pressed=0.0):
    """kind: like, sub, follow"""
    cfg = {'like': ('Me gusta', '¡GRACIAS!', (40, 120, 255)),
           'sub': ('Suscríbete', 'SUSCRITO ✓', (230, 40, 40)),
           'follow': ('Sígueme', 'SIGUIENDO ✓', (200, 60, 220))}[kind]
    txt = cfg[1] if pressed > 0.5 else cfg[0]
    col = cfg[2] if pressed <= 0.5 else tuple(int(c * 0.75 + 255 * 0.25) for c in cfg[2])
    if kind == 'sub' and pressed > 0.5:
        col = (90, 90, 100)
    l = L(420, 110)
    l.rrect([8, 12, 412, 100], 44, fill=(0, 0, 0, 120))
    l.rrect([6, 6, 410, 92], 44, fill=col + (255,), outline=(255, 255, 255, 255), width=5)
    # icono
    ic = (60, 49)
    if kind == 'like':
        l.rrect([ic[0] - 18, ic[1] - 4, ic[0] + 16, ic[1] + 24], 6, fill=(255, 255, 255, 255))
        l.rrect([ic[0] - 6, ic[1] - 26, ic[0] + 8, ic[1] + 2], 6, fill=(255, 255, 255, 255))
        l.rect([ic[0] - 28, ic[1] - 2, ic[0] - 20, ic[1] + 24], fill=(255, 255, 255, 255))
    elif kind == 'sub':
        l.circle((ic[0], ic[1] - 2), 18, fill=(255, 255, 255, 255))
        l.rect([ic[0] - 22, ic[1] + 4, ic[0] + 22, ic[1] + 14], fill=(255, 255, 255, 255))
        l.circle((ic[0], ic[1] + 20), 6, fill=(255, 255, 255, 255))
    else:
        l.rect([ic[0] - 6, ic[1] - 22, ic[0] + 6, ic[1] + 22], fill=(255, 255, 255, 255))
        l.rect([ic[0] - 22, ic[1] - 6, ic[0] + 22, ic[1] + 6], fill=(255, 255, 255, 255))
    l.text((245, 49), txt, 34, fill=(255, 255, 255))
    return l.done()


# ---------------- Romper en bloquecitos ----------------
def shatter(canvas, layer, ox, oy, ts, seed=0, tile=54, push=(0.0, 0.0)):
    """dibuja 'layer' (pegado en ox,oy) roto en pedazos que caen; ts = segundos desde el golpe"""
    if ts <= 0:
        canvas.alpha_composite(layer, (ox, oy)) if ox >= 0 and oy >= 0 else S._paste(canvas, layer, ox, oy)
        return
    rnd = random.Random(seed)
    w, h = layer.size
    a = np.array(layer)
    cxl, cyl = w / 2, h / 2
    for ty in range(0, h, tile):
        for tx in range(0, w, tile):
            blk = a[ty:ty + tile, tx:tx + tile]
            if blk.shape[0] == 0 or blk[..., 3].max() < 10:
                continue
            cx, cy = tx + tile / 2, ty + tile / 2
            vx = (cx - cxl) * rnd.uniform(1.5, 3.5) + push[0] + rnd.uniform(-200, 200)
            vy = -rnd.uniform(300, 900) + push[1]
            spin = rnd.uniform(-8, 8)
            x = ox + cx + vx * ts
            y = oy + cy + vy * ts + 0.5 * 3200 * ts * ts
            al = max(0.0, 1 - ts / 0.9)
            S.paste_center(canvas, Image.fromarray(blk, 'RGBA'), x, y, angle=spin * ts, alpha=al)


# ---------------- Gravedad: planeta de bloques ----------------
_planet_cache = {}

def planet_img(r=170):
    if r in _planet_cache:
        return _planet_cache[r]
    n = 34
    rnd = random.Random(4)
    arr = np.zeros((n, n, 4), np.uint8)
    # continentes con ruido suavizado
    noise = np.array([[rnd.random() for _ in range(n)] for _ in range(n)])
    from scipy.ndimage import gaussian_filter
    noise = gaussian_filter(noise, 2.2)
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    for y in range(n):
        for x in range(n):
            dx, dy = (x + 0.5 - n / 2) / (n / 2), (y + 0.5 - n / 2) / (n / 2)
            d = math.hypot(dx, dy)
            if d > 1:
                continue
            if noise[y, x] > 0.55:
                col = (86, 170, 70) if noise[y, x] < 0.8 else (120, 95, 60)
            else:
                col = (50, 110, 210) if noise[y, x] > 0.3 else (40, 90, 190)
            sh = 1.0 - 0.35 * max(0, dx * 0.6 + dy * 0.6)
            if (dx + 0.35) ** 2 + (dy + 0.35) ** 2 < 0.08:
                sh *= 1.25
            arr[y, x, :3] = [min(255, int(c * sh)) for c in col]
            arr[y, x, 3] = 255
    im = Image.fromarray(arr, 'RGBA').resize((2 * r, 2 * r), Image.NEAREST)
    _planet_cache[r] = im
    return im


def mini_guy(h=60, col=(70, 120, 200)):
    """muñequito de bloques (de pie, mirando al frente)"""
    w = int(h * 0.55)
    l = L(w + 4, h + 4)
    u = h / 8
    l.rect([w / 2 - 1.5 * u + 2, 2, w / 2 + 1.5 * u + 2, 2 + 3 * u], fill=(240, 200, 160, 255))
    l.rect([w / 2 - 2 * u + 2, 2 + 3 * u, w / 2 + 2 * u + 2, 2 + 6 * u], fill=col + (255,))
    l.rect([w / 2 - 2 * u + 2, 2 + 6 * u, w / 2 + 2, 2 + 8 * u], fill=(60, 60, 90, 255))
    l.rect([w / 2 + 2, 2 + 6 * u, w / 2 + 2 * u + 2, 2 + 8 * u], fill=(60, 60, 90, 255))
    return l.done()


def gravity_planet(t, grow=1.0, arrows=1.0, guys=1.0, r=170):
    """planeta con muñequitos alrededor y flechas rojas hacia el centro."""
    size = 2 * r + 320
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    c = (size / 2, size / 2)
    if grow > 0:
        p = planet_img(r)
        rot = t * 0.15
        S.paste_center(out, p.rotate(math.degrees(rot), resample=Image.NEAREST), c[0], c[1], scale=grow)
    if guys > 0:
        cols = [(70, 120, 200), (220, 80, 80), (240, 180, 40), (120, 200, 120)]
        for i, ang in enumerate((-90, 20, 145, 230)):
            a = math.radians(ang)
            k = S.ease_back(S.clamp(guys * 4 - i))
            if k <= 0:
                continue
            g = mini_guy(64, cols[i])
            gx = c[0] + math.cos(a) * (r * grow + 32)
            gy = c[1] + math.sin(a) * (r * grow + 32)
            # de pie sobre la superficie: rotar para que los pies apunten al centro
            S.paste_center(out, g, gx, gy, scale=k, angle=-(a + math.pi / 2))
    if arrows > 0:
        l = L(size, size)
        for i, ang in enumerate((-45, 70, 185, 280)):
            a = math.radians(ang)
            k = S.ease_out(S.clamp(arrows * 4 - i))
            if k <= 0:
                continue
            r0 = r * grow + 100
            r1 = r0 - 75 * k
            pul = 6 * math.sin(t * 8 + i)
            p0 = (c[0] + math.cos(a) * (r0 + pul), c[1] + math.sin(a) * (r0 + pul))
            p1 = (c[0] + math.cos(a) * (r1 + pul), c[1] + math.sin(a) * (r1 + pul))
            arrow(l, p0, p1, GRAV + (255,), width=10, head=22)
        out.alpha_composite(l.done())
    return out


def stone_cube(size=110, col=(150, 150, 160)):
    l = L(size + 10, size + 10)
    l.rrect([5, 5, size + 5, size + 5], 8, fill=col + (255,), outline=(60, 60, 70, 255), width=4)
    l.rect([15, 15, size - 5, 30], fill=tuple(min(255, c + 40) for c in col) + (255,))
    return l.done()


def attraction(t, k=1.0):
    """dos bloques que se atraen con flechas"""
    Wd, Hd = 900, 300
    out = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0))
    gap = 300 - 140 * S.ease_in(S.clamp(t / 2.2))
    c1 = (Wd / 2 - gap, Hd / 2); c2 = (Wd / 2 + gap, Hd / 2)
    S.paste_center(out, stone_cube(130, (140, 150, 170)), c1[0], c1[1], scale=S.ease_back(k))
    S.paste_center(out, stone_cube(100, (190, 130, 90)), c2[0], c2[1], scale=S.ease_back(S.clamp(k * 1.3 - 0.3)))
    a = S.clamp(k * 2 - 1)
    if a > 0:
        l = L(Wd, Hd)
        arrow(l, (c1[0] + 80, c1[1]), (c1[0] + 80 + 90 * a, c1[1]), GRAV + (255,), 10, 22)
        arrow(l, (c2[0] - 70, c2[1]), (c2[0] - 70 - 90 * a, c2[1]), GRAV + (255,), 10, 22)
        out.alpha_composite(l.done())
    return out


PIV_PAD = 1100

def rotated_about(layer, piv, ang_deg, scale=1.0):
    """devuelve (img, offset) de 'layer' rotado ang_deg (positivo = horario) alrededor de piv (coords de la capa)"""
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.size[0] * scale)), max(1, int(layer.size[1] * scale))), Image.BICUBIC)
        piv = (piv[0] * scale, piv[1] * scale)
    w, h = layer.size
    R = int(math.ceil(max(math.hypot(piv[0], piv[1]), math.hypot(w - piv[0], piv[1]),
                          math.hypot(piv[0], h - piv[1]), math.hypot(w - piv[0], h - piv[1])))) + 4
    sq = Image.new('RGBA', (2 * R, 2 * R), (0, 0, 0, 0))
    sq.alpha_composite(layer, (int(R - piv[0]), int(R - piv[1])))
    if abs(ang_deg) > 0.01:
        sq = sq.rotate(-ang_deg, resample=Image.BICUBIC, center=(R, R))
    return sq, (-R, -R)
