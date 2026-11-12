# Dibujos del capítulo 11 (el motor DC), con aspecto realista:
# motorcito de juguete (lata plateada, tapa de plástico, terminales y eje) con hélice, el motor por
# dentro visto de frente (imanes N y S con su campo, la bobina vista de punta con sus dos alambres
# ⊙ y ⊗, flechas de empujón), el conmutador de anillo partido con sus escobillas, la pila volteada,
# el control de videojuego con su motorcito de pesa a un lado, la manivela que lo vuelve generador,
# el molino del cap. 2 y la tarjeta del reto.
# Regla: cada rótulo sale de VERIFICACION.md (códigos M#).
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
from caps_real import _shade_cols, cached

SS = 2
RED_N = (214, 58, 58)
RED_HI = (255, 140, 130)
BLUE_S = (54, 104, 214)
BLUE_HI = (140, 180, 255)
COPPER = (214, 120, 54)
COPPER_HI = (255, 200, 140)
FIELD = (90, 200, 255)
PUSH = (255, 217, 61)
CURR = (255, 217, 61)
STEEL = (178, 184, 194)


def _cyl_img(w, h, rgb, spec=0.3, r=0):
    """rectángulo sombreado como cilindro (vertical)"""
    s = _shade_cols(w, spec)
    arr = np.ones((h, w, 3), np.float32) * np.array(rgb, np.float32) * s[None, :, None]
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    im = Image.fromarray(arr, 'RGB').convert('RGBA')
    if r:
        m = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
        im.putalpha(m)
    return im


# ---------------- motorcito de juguete (de pie, eje hacia arriba) ----------------
def toy_motor(w=150):
    """lata plateada con tapa de plástico, dos terminales y el eje; mira hacia arriba"""
    key = ('toymotor', w)
    def mk():
        h = int(w * 1.25)
        W_, H_ = w + 40, h + 60
        im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        x0 = 20
        # eje
        sh = _cyl_img(max(6, int(w * 0.07)), int(w * 0.32), (200, 204, 210), 0.35)
        im.alpha_composite(sh, (W_ // 2 - sh.width // 2, 2))
        # lata
        can = _cyl_img(w, int(h * 0.78), STEEL, 0.28, r=int(w * 0.08))
        im.alpha_composite(can, (x0, int(w * 0.3)))
        # tapa de abajo (plástico blanco) y terminales
        cap = _cyl_img(int(w * 0.9), int(h * 0.16), (236, 232, 222), 0.3, r=int(w * 0.06))
        cy = int(w * 0.3) + int(h * 0.78) - 4
        im.alpha_composite(cap, (x0 + int(w * 0.05), cy))
        d = ImageDraw.Draw(im)
        for k, sx in enumerate((0.28, 0.72)):
            tx = x0 + int(w * sx)
            d.rectangle([tx - 5, cy + int(h * 0.12), tx + 5, cy + int(h * 0.16) + 18], fill=(200, 150, 70), outline=(110, 70, 20))
            d.ellipse([tx - 4, cy + int(h * 0.16) + 6, tx + 4, cy + int(h * 0.16) + 14], fill=(90, 50, 10))
        # ranuras y brillo
        top = int(w * 0.3)
        d.rounded_rectangle([x0 + w * 0.2, top + 10, x0 + w * 0.8, top + 22], 5, fill=(140, 146, 156))
        d.ellipse([W_ // 2 - 14, top - 6, W_ // 2 + 14, top + 10], fill=(150, 154, 162), outline=(110, 114, 122))
        d.text((W_ // 2, top + h * 0.42), 'DC', font=S.font(int(w * 0.18), True), fill=(110, 116, 128), anchor='mm')
        return im
    return cached(key, mk)


def toy_motor_terms(cx, cy, w=150):
    """posición en pantalla de las dos terminales (para los cables)"""
    im = toy_motor(w)
    h = int(w * 1.25)
    top = cy - im.height / 2
    yy = top + int(w * 0.3) + int(h * 0.78) - 4 + int(h * 0.16) + 16
    xs = [cx - im.width / 2 + 20 + int(w * sx) for sx in (0.28, 0.72)]
    return (xs[0], yy), (xs[1], yy)


def propeller(ang, speed, w=260):
    """hélice vista de lado: dos aspas que se ven más anchas o angostas al girar; con velocidad, disco borroso"""
    l = D.L(w + 20, int(w * 0.36) + 20)
    cx, cy = (w + 20) / 2, (w * 0.36 + 20) / 2
    blur = min(1.0, max(0.0, (speed - 4) / 10))
    if blur > 0.02:
        l.d.ellipse(l.s([cx - w / 2, cy - w * 0.07, cx + w / 2, cy + w * 0.07]), fill=(230, 80, 60, int(120 * blur)))
        l.d.ellipse(l.s([cx - w / 2, cy - w * 0.03, cx + w / 2, cy + w * 0.03]), fill=(255, 255, 255, int(70 * blur)))
    a = 1 - blur
    if a > 0.02:
        c = math.cos(ang)
        for sgn in (1, -1):
            ex = cx + sgn * c * w / 2
            th = w * 0.06 * (0.5 + 0.5 * abs(math.sin(ang)))
            col = (225, 70, 55, int(255 * a)) if sgn * c > 0 else (180, 50, 40, int(255 * a))
            l.poly([(cx, cy - th * 0.6), (ex, cy - th), (ex, cy + th), (cx, cy + th * 0.6)], fill=col)
    l.circle((cx, cy), w * 0.05, fill=(240, 240, 245, 255), outline=(120, 120, 130, 255), width=2)
    return l.done()


# ---------------- el motor por dentro (vista de frente) ----------------
MW, MH = 620, 440
def _magnet_block(w, h, col, hi, letter, flip=False):
    key = ('mag', w, h, col, letter, flip)
    def mk():
        arr = np.ones((h, w, 3), np.float32) * np.array(col, np.float32)
        v = (np.arange(h) + 0.5) / h
        s = 0.55 + 0.6 * np.sin(np.pi * v) ** 0.6 + 0.35 * np.exp(-((v - 0.25) / 0.06) ** 2)
        arr = np.clip(arr * s[:, None, None], 0, 255).astype(np.uint8)
        im = Image.fromarray(arr, 'RGB').convert('RGBA')
        m = Image.new('L', (w, h), 0)
        md = ImageDraw.Draw(m)
        # cara curva hacia la bobina
        rr = h * 0.62
        if not flip:
            md.rectangle([0, 0, w - 1, h - 1], fill=255)
            md.ellipse([w - rr * 0.5, h / 2 - rr, w - rr * 0.5 + 2 * rr, h / 2 + rr], fill=0)
        else:
            md.rectangle([0, 0, w - 1, h - 1], fill=255)
            md.ellipse([-2 * rr + rr * 0.5, h / 2 - rr, rr * 0.5, h / 2 + rr], fill=0)
        im.putalpha(m)
        d = ImageDraw.Draw(im)
        d.text((w * (0.26 if not flip else 0.76), h / 2), letter, font=S.font(int(h * 0.3), True), fill=(255, 255, 255), anchor='mm',
               stroke_width=4, stroke_fill=tuple(int(c * 0.5) for c in col))
        return im
    return cached(key, mk)


def motor_inside(theta, cur=1, show_cur=1.0, push=0.0, field=1.0, t=0.0, swap=False, highlight_one=False, w=MW):
    """theta: ángulo de la bobina (0 = acostada). cur: +1/-1 = sentido de la corriente en el extremo A.
    push: 0..1 muestra las flechas de empujón. swap: imanes al revés (S a la izquierda)."""
    h = int(w * MH / MW)
    sc = w / MW
    l = D.L(w, h)
    # campo entre imanes (líneas que corren de N a S)
    mw, mh = int(150 * sc), int(300 * sc)
    gap_l, gap_r = mw * 0.75, w - mw * 0.75
    if field > 0.02:
        for k in range(5):
            y = h / 2 + (k - 2) * 52 * sc
            for j in range(9):
                u = ((j / 9) + t * 0.35 * (-1 if swap else 1)) % 1.0
                x = gap_l + (gap_r - gap_l) * u
                a = int(150 * field * math.sin(math.pi * u))
                xx = x + (8 if not swap else -8) * sc
                l.line([(x - 8 * sc, y), (x + 8 * sc, y)], FIELD + (a,), 3 * sc)
                l.poly([(xx + (6 if not swap else -6) * sc, y), (xx - (2 if not swap else -2) * sc, y - 6 * sc), (xx - (2 if not swap else -2) * sc, y + 6 * sc)], fill=FIELD + (a,))
    im = l.done()
    # imanes
    lm = _magnet_block(mw, mh, BLUE_S if swap else RED_N, None, 'S' if swap else 'N')
    rm = _magnet_block(mw, mh, RED_N if swap else BLUE_S, None, 'N' if swap else 'S', flip=True)
    im.alpha_composite(lm, (0, int(h / 2 - mh / 2)))
    im.alpha_composite(rm, (w - mw, int(h / 2 - mh / 2)))
    # bobina vista de punta: barra que gira con dos alambres en los extremos
    l2 = D.L(w, h)
    cx, cy = w / 2, h / 2
    R_ = 120 * sc
    ax, ay = cx + R_ * math.cos(theta), cy - R_ * math.sin(theta)
    bx, by = cx - R_ * math.cos(theta), cy + R_ * math.sin(theta)
    l2.line([(ax, ay), (bx, by)], (120, 70, 30, 255), 22 * sc)
    l2.line([(ax, ay), (bx, by)], COPPER + (255,), 14 * sc)
    l2.circle((cx, cy), 16 * sc, fill=(200, 204, 212, 255), outline=(90, 94, 104, 255), width=3 * sc)
    rr = 30 * sc
    for k, (px, py) in enumerate(((ax, ay), (bx, by))):
        if highlight_one and k == 1:
            continue
        l2.circle((px, py), rr, fill=COPPER + (255,), outline=(110, 60, 20, 255), width=4 * sc)
        l2.circle((px - rr * 0.3, py - rr * 0.3), rr * 0.3, fill=COPPER_HI + (200,))
        sgn = cur if k == 0 else -cur
        if show_cur > 0.02:
            ca = int(255 * show_cur)
            if sgn > 0:   # ⊙ sale hacia ti
                l2.circle((px, py), rr * 0.55, fill=(255, 255, 255, ca))
                l2.circle((px, py), rr * 0.2, fill=(30, 30, 36, ca))
            else:         # ⊗ entra
                l2.circle((px, py), rr * 0.55, fill=(255, 255, 255, ca))
                q = rr * 0.33
                l2.line([(px - q, py - q), (px + q, py + q)], (30, 30, 36, ca), 5 * sc)
                l2.line([(px - q, py + q), (px + q, py - q)], (30, 30, 36, ca), 5 * sc)
        if push > 0.02:
            # fuerza: con campo de izquierda a derecha, ⊙ empuja hacia arriba y ⊗ hacia abajo (al revés con swap)
            up = (sgn > 0) != swap
            L_ = 95 * sc * push
            y1 = py - (rr + 8 * sc) if up else py + (rr + 8 * sc)
            y2 = y1 - L_ if up else y1 + L_
            D.arrow(l2, (px, y1), (px, y2), PUSH + (int(255 * min(1, push * 1.5)),), width=10 * sc, head=24 * sc)
    im.alpha_composite(l2.done())
    return im


def coil_end_pos(theta, which=0, w=MW):
    sc = w / MW
    h = int(w * MH / MW)
    R_ = 120 * sc
    s = 1 if which == 0 else -1
    return w / 2 + s * R_ * math.cos(theta) - w / 2, h / 2 - s * R_ * math.sin(theta) - h / 2


# ---------------- conmutador de anillo partido con escobillas ----------------
def commutator(theta, w=360, plus_left=True, flow=0.0, t=0.0):
    """dos medias lunas de cobre que giran con la bobina; escobillas fijas de carbón a izquierda y derecha.
    La mitad A (dorada) se conecta a la escobilla con la que está en contacto."""
    h = int(w * 0.8)
    l = D.L(w, h)
    cx, cy = w / 2, h / 2
    r = w * 0.22
    gap = 0.16
    # mitades: A centrada en theta + 90° (arriba cuando theta = 0)… usamos theta directamente
    for k, col in enumerate(((236, 176, 70), (196, 110, 50))):
        a0 = theta + k * math.pi + gap / 2
        a1 = theta + (k + 1) * math.pi - gap / 2
        pts = [(cx + r * math.cos(a0 + (a1 - a0) * j / 24), cy - r * math.sin(a0 + (a1 - a0) * j / 24)) for j in range(25)]
        pts += [(cx + r * 0.55 * math.cos(a1 - (a1 - a0) * j / 24), cy - r * 0.55 * math.sin(a1 - (a1 - a0) * j / 24)) for j in range(25)]
        l.poly(pts, fill=col + (255,), outline=(90, 50, 15, 255), width=3)
        am = (a0 + a1) / 2
        l.text((cx + r * 0.78 * math.cos(am), cy - r * 0.78 * math.sin(am)), 'A' if k == 0 else 'B', int(w * 0.07), fill=(60, 30, 5))
    l.circle((cx, cy), r * 0.3, fill=(200, 204, 212, 255), outline=(90, 94, 104, 255), width=3)
    # escobillas (bloques de carbón con resorte)
    bw, bh = w * 0.1, w * 0.1
    for side in (-1, 1):
        x_in = cx + side * (r + 2)
        x_out = x_in + side * bw
        l.rrect([min(x_in, x_out), cy - bh / 2, max(x_in, x_out), cy + bh / 2], 4, fill=(48, 48, 54, 255), outline=(20, 20, 24, 255), width=2)
        xe = x_out + side * w * 0.05
        l.line([(x_out, cy), (xe, cy)], (210, 210, 216, 255), 6)
        pos = (side < 0) == plus_left
        l.circle((xe + side * 16, cy), 16, fill=(230, 60, 60, 255) if pos else (60, 90, 220, 255))
        l.text((xe + side * 16, cy), '+' if pos else '−', 24, fill=(255, 255, 255))
    return l.done()


def contact_half(theta):
    """qué mitad (0 = A, 1 = B) toca la escobilla izquierda"""
    a = (math.pi - theta) % (2 * math.pi)
    return 0 if a < math.pi else 1


# ---------------- pila AA acostada (con + a un lado) ----------------
def battery_h(w=260, flipped=False):
    key = ('bath', w, flipped)
    def mk():
        h = int(w * 0.36)
        l = D.L(w + 30, h + 12)
        x0, y0 = 6, 6
        l.rrect([x0, y0, x0 + w, y0 + h], 14, fill=(30, 30, 34, 255), outline=(12, 12, 14, 255), width=3)
        if not flipped:
            l.rrect([x0 + w * 0.66, y0, x0 + w, y0 + h], 14, fill=(214, 168, 60, 255))
            l.rect([x0 + w * 0.66, y0, x0 + w * 0.8, y0 + h], fill=(214, 168, 60, 255))
            l.rrect([x0 + w, y0 + h * 0.32, x0 + w + 18, y0 + h * 0.68], 4, fill=(205, 208, 214, 255))
            l.text((x0 + w * 0.83, y0 + h / 2), '+', int(h * 0.5), fill=(60, 40, 10))
            l.text((x0 + w * 0.12, y0 + h / 2), '−', int(h * 0.45), fill=(220, 220, 225))
        else:
            l.rrect([x0, y0, x0 + w * 0.34, y0 + h], 14, fill=(214, 168, 60, 255))
            l.rect([x0 + w * 0.2, y0, x0 + w * 0.34, y0 + h], fill=(214, 168, 60, 255))
            l.text((x0 + w * 0.17, y0 + h / 2), '+', int(h * 0.5), fill=(60, 40, 10))
            l.text((x0 + w * 0.88, y0 + h / 2), '−', int(h * 0.45), fill=(220, 220, 225))
        l.text((x0 + w * 0.45, y0 + h / 2), '1,5V', int(h * 0.36), fill=(240, 240, 245))
        l.rect([x0 + 10, y0 + 6, x0 + w - 10, y0 + 12], fill=(255, 255, 255, 40))
        return l.done()
    return cached(key, mk)


# ---------------- control de videojuego con el motorcito de pesa ----------------
def gamepad(w=560, see_inside=0.0, ang=0.0):
    l = D.L(w, int(w * 0.62))
    h = l.h
    body = (58, 60, 70)
    # agarraderas y cuerpo
    for sx in (0.2, 0.8):
        l.circle((w * sx, h * 0.62), w * 0.17, fill=body + (255,), outline=(25, 26, 30, 255), width=4)
    l.rrect([w * 0.1, h * 0.12, w * 0.9, h * 0.68], int(w * 0.12), fill=body + (255,), outline=(25, 26, 30, 255), width=4)
    l.rrect([w * 0.12, h * 0.14, w * 0.88, h * 0.3], int(w * 0.08), fill=(255, 255, 255, 18))
    # cruceta
    cx, cy = w * 0.27, h * 0.36
    l.rect([cx - 30, cy - 10, cx + 30, cy + 10], fill=(30, 30, 34, 255)); l.rect([cx - 10, cy - 30, cx + 10, cy + 30], fill=(30, 30, 34, 255))
    # botones
    for (dx, dy, col) in ((0, -32, (90, 200, 120)), (32, 0, (230, 70, 70)), (-32, 0, (80, 140, 230)), (0, 32, (240, 200, 70))):
        l.circle((w * 0.73 + dx, h * 0.36 + dy), 15, fill=col + (255,), outline=(30, 30, 34, 255), width=2)
    for sx in (0.4, 0.6):
        l.circle((w * sx, h * 0.52), 30, fill=(36, 36, 40, 255), outline=(20, 20, 24, 255), width=3)
        l.circle((w * sx, h * 0.52), 18, fill=(70, 72, 80, 255))
    im = l.done()
    if see_inside > 0.02:
        # ventana en la agarradera izquierda con el motorcito y su pesa
        win = vib_motor(int(w * 0.26), ang)
        mask = Image.new('L', im.size, 0)
        r = w * 0.15
        ImageDraw.Draw(mask).ellipse([w * 0.2 - r, h * 0.62 - r, w * 0.2 + r, h * 0.62 + r], fill=int(255 * see_inside))
        inner = Image.new('RGBA', im.size, (18, 20, 26, 255))
        S.paste_center(inner, win, w * 0.2, h * 0.62)
        im.paste(inner, (0, 0), mask)
        ImageDraw.Draw(im).ellipse([w * 0.2 - r, h * 0.62 - r, w * 0.2 + r, h * 0.62 + r], outline=(255, 230, 140, int(255 * see_inside)), width=4)
    return im


def vib_motor(w=150, ang=0.0):
    """motorcito acostado (lata) con la pesa de media luna en el eje, vista de frente desde la punta del eje"""
    l = D.L(w, w)
    c = (w / 2, w / 2)
    l.circle(c, w * 0.3, fill=STEEL + (255,), outline=(90, 94, 104, 255), width=3)
    l.circle((c[0] - w * 0.08, c[1] - w * 0.08), w * 0.1, fill=(230, 232, 236, 150))
    # pesa de media luna (descentrada) que gira con el eje
    r = w * 0.42
    pts = [c]
    for j in range(21):
        a = ang - math.pi / 2 + math.pi * j / 20
        pts.append((c[0] + r * math.cos(a), c[1] - r * math.sin(a)))
    l.poly(pts, fill=(150, 154, 166, 255), outline=(60, 62, 70, 255), width=3)
    am = ang
    l.circle((c[0] + r * 0.45 * math.cos(am), c[1] - r * 0.45 * math.sin(am)), w * 0.05, fill=(255, 255, 255, 90))
    l.circle(c, w * 0.06, fill=(220, 222, 228, 255), outline=(90, 94, 104, 255), width=2)
    return l.done()


# ---------------- manivela (el motor como generador) ----------------
def crank(ang, w=200):
    l = D.L(w, w)
    c = (w / 2, w / 2)
    r = w * 0.36
    p = (c[0] + r * math.cos(ang), c[1] - r * math.sin(ang))
    l.line([c, p], (150, 100, 50, 255), 18)
    l.line([c, p], (200, 140, 70, 255), 10)
    l.circle(c, w * 0.09, fill=(200, 204, 212, 255), outline=(90, 94, 104, 255), width=3)
    l.circle(p, w * 0.1, fill=(230, 60, 50, 255), outline=(120, 20, 20, 255), width=3)
    return l.done()


def windmill(w=160, ang=0.0):
    l = D.L(w, int(w * 1.3))
    c = (w / 2, w * 0.45)
    l.poly([(c[0] - 8, c[1]), (c[0] + 8, c[1]), (c[0] + 14, l.h - 4), (c[0] - 14, l.h - 4)], fill=(230, 232, 236, 255), outline=(120, 122, 130, 255), width=2)
    for k in range(3):
        a = ang + k * 2 * math.pi / 3
        tip = (c[0] + w * 0.44 * math.cos(a), c[1] - w * 0.44 * math.sin(a))
        sd = (c[0] + w * 0.1 * math.cos(a + 0.5), c[1] - w * 0.1 * math.sin(a + 0.5))
        l.poly([c, sd, tip], fill=(245, 245, 250, 255), outline=(130, 132, 140, 255), width=2)
    l.circle(c, 9, fill=(200, 60, 50, 255))
    return l.done()


# ---------------- tarjeta del reto ----------------
def reto_card(w=440, hide=1.0):
    l = D.L(w, int(w * 0.95))
    l.rrect([4, 4, w - 4, l.h - 4], 24, fill=(18, 20, 28, 235), outline=(255, 220, 120, 255), width=5)
    im = l.done()
    mi = motor_inside(0.6, cur=-1, show_cur=0.0, push=0.0, field=0.8, swap=True, w=int(w * 0.86))
    S.paste_center(im, mi, w / 2, im.height * 0.42)
    S.paste_center(im, battery_h(int(w * 0.42), flipped=True), w / 2, im.height * 0.83)
    if hide > 0.02:
        q = S.fancy_text('?', 120)
        S.paste_center(im, q, w / 2, im.height * 0.42, scale=hide)
    return im
