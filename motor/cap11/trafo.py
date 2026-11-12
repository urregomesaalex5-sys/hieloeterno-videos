# Dibujos del capítulo 10 (el transformador), con aspecto realista:
# núcleo de hierro laminado en forma de marco con dos bobinas de cobre (primaria y secundaria),
# flujo magnético que da la vuelta por el hierro, enchufe y tomacorriente de 120 V, gráfica de la
# corriente alterna, voltímetros, pila con su pulsito, transformador de poste con cables, láminas
# del núcleo que se estiran (zumbido), símbolo del transformador para el remate y el reto.
# Regla: cada rótulo sale de VERIFICACION.md (códigos T#).
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
from caps_real import _shade_cols, cached

SS = 2
COPPER = np.array((214, 120, 54), np.float32)
COPPER_HI = np.array((255, 214, 160), np.float32)
COPPER2 = np.array((196, 96, 60), np.float32)          # secundaria un poco más rojiza
IRON = (98, 102, 112)
IRON_HI = (150, 156, 168)
IRON_DK = (58, 60, 68)
FIELD = (90, 200, 255)
WIRE = (232, 232, 232)
CURR = (255, 217, 61)


# ---------------- bobina vertical (vueltas horizontales) ----------------
def vcoil(cw, ch, turns, base=COPPER):
    """bobina vertical sombreada como cilindro: cada vuelta es una banda horizontal de alambre"""
    key = ('vcoil', cw, ch, turns, tuple(base.tolist()))
    def mk():
        W0, H0 = cw * SS, ch * SS
        pitch = H0 / turns
        ys = np.arange(H0) + 0.5
        xs = (np.arange(W0) + 0.5) / W0
        Y = ys[:, None] + 0.25 * pitch * (xs[None, :] - 0.5) * 2
        u = (Y / pitch) % 1.0
        s_wire = np.clip(np.sin(np.pi * u), 0, 1) ** 0.5
        s_cyl = _shade_cols(W0, spec=0.3)[None, :]
        arr = base[None, None, :] * (0.25 + 0.75 * s_wire[..., None]) * (0.5 + 0.5 * s_cyl[..., None] / s_cyl.max())
        spec = np.exp(-((u - 0.38) / 0.1) ** 2) * np.exp(-((xs[None, :] - 0.3) / 0.1) ** 2)
        arr += COPPER_HI[None, None, :] * spec[..., None] * 0.6
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
        m = Image.new('L', (W0, H0), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, W0 - 1, H0 - 1], int(W0 * 0.12), fill=255)
        im.putalpha(m)
        return im.resize((cw, ch), Image.LANCZOS)
    return cached(key, mk)


# ---------------- transformador (núcleo en marco + 2 bobinas) ----------------
def geom(w):
    """medidas del transformador de ancho w (coordenadas dentro de la imagen)"""
    h = int(w * 0.78)
    th = int(w * 0.17)                     # grosor de las patas del núcleo
    pad = int(w * 0.16)                    # margen para las patas de alambre
    W_, H_ = w + 2 * pad, h + 20
    x0, y0 = pad, 10
    cw = int(th * 1.75); ch = int(h * 0.56)
    lc = (x0 + th / 2, y0 + h / 2)         # centro bobina izquierda (primaria)
    rc = (x0 + w - th / 2, y0 + h / 2)     # centro bobina derecha (secundaria)
    return dict(w=w, h=h, th=th, pad=pad, W=W_, H=H_, x0=x0, y0=y0, cw=cw, ch=ch, lc=lc, rc=rc)


def lead_points(w):
    """puntas de las patas: (izq_arriba, izq_abajo, der_arriba, der_abajo) dentro de la imagen"""
    g = geom(w)
    ya = g['lc'][1] - g['ch'] * 0.32; yb = g['lc'][1] + g['ch'] * 0.32
    return (2, ya), (2, yb), (g['W'] - 2, ya), (g['W'] - 2, yb)


def flux_path(w, inset=0.5):
    """recorrido del flujo por el centro del hierro (rectángulo), en sentido horario"""
    g = geom(w)
    x0, y0, th = g['x0'], g['y0'], g['th']
    a = x0 + th * inset; b = y0 + th * inset
    c = x0 + g['w'] - th * inset; d = y0 + g['h'] - th * inset
    return [(a, d), (a, b), (c, b), (c, d), (a, d)]


def transformer(w=520, n1=8, n2=8, glow2=0.0, labels=False):
    """transformador clásico: marco de hierro laminado y dos bobinas (izq. primaria, der. secundaria)"""
    key = ('trafo', w, n1, n2, round(glow2, 2), labels)
    def mk():
        g = geom(w)
        l = D.L(g['W'], g['H'])
        x0, y0, th, h = g['x0'], g['y0'], g['th'], g['h']
        # sombra
        l.rrect([x0 + 10, y0 + 14, x0 + w + 10, y0 + h + 14], 10, fill=(0, 0, 0, 70))
        # marco de hierro
        l.rrect([x0, y0, x0 + w, y0 + h], 8, fill=IRON + (255,), outline=IRON_DK + (255,), width=4)
        l.rect([x0 + th, y0 + th, x0 + w - th, y0 + h - th], fill=(0, 0, 0, 0))
        im = l.im
        # hueco (transparente)
        ImageDraw.Draw(im).rectangle([(x0 + th) * SS, (y0 + th) * SS, (x0 + w - th) * SS, (y0 + h - th) * SS], fill=(0, 0, 0, 0))
        l.rect([x0 + th, y0 + th, x0 + w - th, y0 + h - th], outline=IRON_DK + (255,), width=4)
        # láminas: rayitas finas a lo largo
        for k in range(1, 6):
            f = k / 6
            yy = y0 + th * f
            l.line([(x0 + th * f, yy), (x0 + w - th * f, yy)], (78, 82, 92, 255), 1.5)
            yy = y0 + h - th * f
            l.line([(x0 + th * f, yy), (x0 + w - th * f, yy)], (78, 82, 92, 255), 1.5)
            xx = x0 + th * f
            l.line([(xx, y0 + th * f), (xx, y0 + h - th * f)], (78, 82, 92, 255), 1.5)
            xx = x0 + w - th * f
            l.line([(xx, y0 + th * f), (xx, y0 + h - th * f)], (78, 82, 92, 255), 1.5)
        # brillo arriba
        l.line([(x0 + 10, y0 + 5), (x0 + w - 10, y0 + 5)], IRON_HI + (255,), 3)
        img = l.done()
        # patas de alambre (por detrás de la bobina)
        d = ImageDraw.Draw(img)
        la, lb, ra, rb = lead_points(w)
        for (px, py), cx in ((la, g['lc'][0]), (lb, g['lc'][0]), (ra, g['rc'][0]), (rb, g['rc'][0])):
            d.line([(px, py), (cx, py)], fill=(150, 80, 30, 255), width=9)
            d.line([(px, py), (cx, py)], fill=(222, 140, 70, 255), width=5)
        # bobinas
        for (cx, cy), n, base in ((g['lc'], n1, COPPER), (g['rc'], n2, COPPER2)):
            c = vcoil(g['cw'], g['ch'], n, base)
            img.alpha_composite(c, (int(cx - g['cw'] / 2), int(cy - g['ch'] / 2)))
        if glow2 > 0.01:
            gl = Image.new('RGBA', img.size, (0, 0, 0, 0))
            cx, cy = g['rc']
            ImageDraw.Draw(gl).rounded_rectangle([cx - g['cw'] * 0.6, cy - g['ch'] * 0.55, cx + g['cw'] * 0.6, cy + g['ch'] * 0.55], 20,
                                                 fill=(255, 220, 120, int(120 * glow2)))
            img = Image.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14)), img)
        return img
    return cached(key, mk)


def flux_overlay(w, t, amp, speed=0.6, n=12, col=FIELD, alpha=1.0):
    """flechitas que dan la vuelta por el hierro. amp en [-1, 1]: tamaño y sentido del flujo."""
    g = geom(w)
    l = D.L(g['W'], g['H'])
    pts = flux_path(w)
    a = abs(amp)
    if a < 0.04 or alpha < 0.02:
        return l.done()
    sgn = 1 if amp > 0 else -1
    phase = (t * speed * sgn) % 1.0
    for k in range(n):
        u = (k / n + phase) % 1.0
        p = D.along(pts, u)
        q = D.along(pts, (u + 0.012 * sgn) % 1.0)
        ang = math.atan2(q[1] - p[1], q[0] - p[0])
        s = 9 + 9 * a
        tip = (p[0] + math.cos(ang) * s, p[1] + math.sin(ang) * s)
        b1 = (p[0] + math.cos(ang + 2.5) * s, p[1] + math.sin(ang + 2.5) * s)
        b2 = (p[0] + math.cos(ang - 2.5) * s, p[1] + math.sin(ang - 2.5) * s)
        l.poly([tip, b1, b2], fill=col + (int(255 * alpha * (0.35 + 0.65 * a)),))
    return l.done()


# ---------------- tomacorriente y enchufe ----------------
def outlet(w=170):
    key = ('outlet', w)
    def mk():
        h = int(w * 1.35)
        l = D.L(w, h)
        l.rrect([4, 4, w - 4, h - 4], 16, fill=(240, 238, 230, 255), outline=(150, 148, 140, 255), width=4)
        l.rrect([w * 0.18, h * 0.2, w * 0.82, h * 0.8], 22, fill=(226, 224, 214, 255), outline=(190, 188, 180, 255), width=3)
        cx = w / 2
        for dx in (-0.16, 0.16):
            l.rrect([cx + dx * w - 6, h * 0.36, cx + dx * w + 6, h * 0.52], 3, fill=(40, 40, 44, 255))
        l.circle((cx, h * 0.65), 9, fill=(40, 40, 44, 255))
        l.circle((cx, h * 0.1), 5, fill=(170, 168, 160, 255))
        l.circle((cx, h * 0.9), 5, fill=(170, 168, 160, 255))
        return l.done()
    return cached(key, mk)


def plug(w=120):
    """enchufe visto de lado con dos patas planas (hacia arriba) y el cable saliendo por abajo"""
    key = ('plug', w)
    def mk():
        h = int(w * 1.7)
        l = D.L(w, h)
        for dx in (-0.16, 0.16):
            l.rect([w / 2 + dx * w - 5, 4, w / 2 + dx * w + 5, h * 0.3], fill=(214, 218, 226, 255), outline=(140, 142, 150, 255), width=2)
        l.rrect([w * 0.12, h * 0.28, w * 0.88, h * 0.72], 16, fill=(40, 42, 48, 255), outline=(16, 16, 20, 255), width=3)
        l.rect([w * 0.2, h * 0.34, w * 0.3, h * 0.66], fill=(70, 72, 80, 255))
        l.rrect([w * 0.4, h * 0.7, w * 0.6, h * 0.86], 6, fill=(34, 36, 40, 255))
        l.line([(w / 2, h * 0.85), (w / 2, h - 2)], (34, 36, 40, 255), 12)
        return l.done()
    return cached(key, mk)


# ---------------- gráfica de la corriente alterna ----------------
def ac_graph(k=1.0, cursor=None, w=560, h=300, cycles=3):
    """onda que sube y baja: arriba "→", abajo "←". k = cuánto se ha dibujado; cursor = posición del punto (0..1)"""
    key = ('ac', round(k, 2), None if cursor is None else round(cursor, 3), w, h)
    def mk():
        l = D.L(w, h)
        l.rrect([2, 2, w - 2, h - 2], 16, fill=(18, 22, 30, 230), outline=(90, 100, 120, 255), width=3)
        x0, x1 = 60, w - 24
        yc, amp = h * 0.5, h * 0.33
        l.line([(x0, 20), (x0, h - 20)], (160, 170, 190, 255), 3)
        l.line([(x0, yc), (x1, yc)], (160, 170, 190, 255), 3)
        l.text((x1 - 4, h - 22), 'tiempo', 18, fill=(160, 170, 190), anchor='rm')
        l.text((x0 - 34, yc - amp * 0.75), '→', 30, fill=(255, 217, 61))
        l.text((x0 - 34, yc + amp * 0.75), '←', 30, fill=(120, 200, 255))
        pts = []
        n = 200
        for i in range(n + 1):
            u = i / n
            if u > k:
                break
            pts.append((x0 + (x1 - x0) * u, yc - amp * math.sin(u * cycles * 2 * math.pi)))
        if len(pts) > 1:
            l.line(pts, (255, 217, 61, 255), 6)
        if cursor is not None:
            u = cursor
            v = math.sin(u * cycles * 2 * math.pi)
            p = (x0 + (x1 - x0) * u, yc - amp * v)
            l.circle(p, 13, fill=(255, 255, 255, 255), outline=(255, 140, 40, 255), width=4)
        return l.done()
    return cached(key, mk)


# ---------------- gráfica del pulsito con pila ----------------
def pulse_graph(k=1.0, w=520, h=280):
    key = ('pulse', round(k, 2), w, h)
    def mk():
        l = D.L(w, h)
        l.rrect([2, 2, w - 2, h - 2], 16, fill=(18, 22, 30, 230), outline=(90, 100, 120, 255), width=3)
        x0, x1 = 40, w - 20
        yb, top = h * 0.74, 40
        l.line([(x0, 20), (x0, h - 20)], (160, 170, 190, 255), 3)
        l.line([(x0, yb), (x1, yb)], (160, 170, 190, 255), 3)
        l.text((x0 + 8, 32), 'voltaje que sale', 18, fill=(160, 170, 190), anchor='lm')
        l.text((x1 - 4, h - 22), 'tiempo', 18, fill=(160, 170, 190), anchor='rm')
        xo = x0 + (x1 - x0) * 0.25
        pts = []
        n = 160
        for i in range(n + 1):
            u = i / n
            if u > k:
                break
            x = x0 + (x1 - x0) * u
            y = yb if x < xo else yb - (yb - top) * math.exp(-(x - xo) / 14)
            pts.append((x, y))
        if len(pts) > 1:
            l.line(pts, (255, 140, 60, 255), 6)
        l.line([(xo, yb - 6), (xo, yb + 6)], (200, 200, 210, 255), 3)
        l.text((xo, h - 22), 'conecta', 18, fill=(200, 200, 210))
        if k > 0.35:
            l.text((xo + 60, top + 60), 'PULSITO', 22, fill=(255, 170, 100), anchor='lm')
        if k > 0.8:
            l.text((x0 + (x1 - x0) * 0.75, yb - 30), 'NADA', 26, fill=(255, 110, 110))
        return l.done()
    return cached(key, mk)


# ---------------- pila grande (D) ----------------
def battery_d(h=220):
    key = ('bd', h)
    def mk():
        w = int(h * 0.55)
        l = D.L(w + 12, h + 24)
        cx = (w + 12) / 2
        l.rrect([cx - w * 0.16, 4, cx + w * 0.16, 22], 4, fill=(205, 208, 214, 255), outline=(120, 122, 130, 255), width=2)
        l.rrect([6, 18, w + 6, h + 18], 16, fill=(30, 30, 34, 255), outline=(12, 12, 14, 255), width=3)
        l.rrect([6, 18, w + 6, 18 + h * 0.4], 16, fill=(214, 168, 60, 255))
        l.rect([6, 18 + h * 0.25, w + 6, 18 + h * 0.4], fill=(214, 168, 60, 255))
        l.rect([14, 26, 24, h + 10], fill=(255, 255, 255, 45))
        l.text((cx, 18 + h * 0.15), '+', int(h * 0.13), fill=(60, 40, 10))
        l.text((cx, 18 + h * 0.66), 'PILA', int(h * 0.11), fill=(240, 240, 245))
        return l.done()
    return cached(key, mk)


# ---------------- medidor digital (voltímetro) ----------------
def meter(txt, w=210, col=(120, 240, 150), sub='VOLTIOS'):
    key = ('meter', txt, w, col, sub)
    def mk():
        h = int(w * 0.72)
        l = D.L(w, h)
        l.rrect([4, 4, w - 4, h - 4], 18, fill=(250, 196, 40, 255), outline=(90, 70, 10, 255), width=5)
        l.rrect([w * 0.12, h * 0.14, w * 0.88, h * 0.6], 8, fill=(26, 34, 30, 255), outline=(10, 10, 10, 255), width=3)
        l.text((w / 2, h * 0.37), txt, int(w * 0.17), fill=col)
        l.text((w / 2, h * 0.78), sub, int(w * 0.085), fill=(60, 44, 6))
        return l.done()
    return cached(key, mk)


# ---------------- poste con transformador ----------------
def pole(w=420, hum=0.0, t=0.0):
    """poste de concreto con cruceta, 3 aisladores, cables y un transformador cilíndrico gris colgado"""
    key = ('pole', w, round(hum, 2), round(t * 30) % 4 if hum > 0 else 0)
    def mk():
        h = int(w * 1.7)
        l = D.L(w, h)
        cx = w * 0.5
        # cables de arriba (media tensión)
        for k, xx in enumerate((0.12, 0.5, 0.88)):
            yy = h * 0.11
            l.line([(0, yy + 8), (w, yy + 8)], (30, 30, 34, 255), 3)
        # poste
        l.poly([(cx - 22, h * 0.05), (cx + 22, h * 0.05), (cx + 34, h), (cx - 34, h)], fill=(176, 172, 164, 255), outline=(120, 118, 112, 255), width=2)
        l.line([(cx - 10, h * 0.06), (cx - 16, h)], (200, 196, 188, 255), 4)
        # cruceta
        l.rect([w * 0.06, h * 0.12, w * 0.94, h * 0.12 + 16], fill=(120, 118, 112, 255))
        for xx in (0.12, 0.5, 0.88):
            x = w * xx
            for j in range(3):
                l.rrect([x - 13 + j * 2, h * 0.09 - j * 12, x + 13 - j * 2, h * 0.09 - j * 12 + 10], 4, fill=(170, 110, 70, 255))
        # bajante al transformador
        l.line([(w * 0.12, h * 0.1), (w * 0.2, h * 0.3)], (30, 30, 34, 255), 3)
        # transformador (tanque gris)
        tx0, tx1 = w * 0.08, w * 0.4
        ty0, ty1 = h * 0.3, h * 0.55
        wob = (2 if hum > 0 and (round(t * 30) % 2) else 0) * hum
        arr = np.ones((int(ty1 - ty0) * SS, int(tx1 - tx0) * SS, 3), np.float32) * np.array((150, 156, 160), np.float32)
        arr *= _shade_cols(arr.shape[1], 0.3)[None, :, None] * 0.85
        tank = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
        l.im.alpha_composite(tank, (int((tx0 + wob) * SS), int(ty0 * SS)))
        l.rrect([tx0 + wob - 4, ty0 - 12, tx1 + wob + 4, ty0 + 6], 6, fill=(120, 126, 132, 255))
        for k in range(4):
            yy = ty0 + 30 + k * (ty1 - ty0 - 50) / 3
            l.line([(tx0 + wob + 2, yy), (tx1 + wob - 2, yy)], (110, 116, 122, 255), 3)
        l.rrect([tx0 + wob + 14, ty0 + 40, tx1 + wob - 14, ty0 + 80], 4, fill=(230, 230, 220, 255))
        l.text(((tx0 + tx1) / 2 + wob, ty0 + 60), 'kVA', 16, fill=(40, 40, 44))
        # soporte al poste
        l.rect([tx1 + wob, ty0 + 30, max(tx1 + wob + 2, cx - 20), ty0 + 44], fill=(90, 90, 96, 255))
        # cables de baja (a la casa)
        l.line([((tx0 + tx1) / 2, ty1), ((tx0 + tx1) / 2, ty1 + 50), (w, ty1 + 120)], (30, 30, 34, 255), 4)
        return l.done()
    return cached(key, mk)


def house(w=230, lit=0.0):
    key = ('house', w, round(lit, 2))
    def mk():
        h = int(w * 0.95)
        l = D.L(w, h)
        l.poly([(w * 0.05, h * 0.42), (w * 0.5, h * 0.05), (w * 0.95, h * 0.42)], fill=(170, 60, 50, 255), outline=(90, 30, 25, 255), width=3)
        l.rect([w * 0.13, h * 0.4, w * 0.87, h - 4], fill=(236, 220, 186, 255), outline=(140, 120, 90, 255), width=3)
        win = tuple(int(a + (b - a) * lit) for a, b in zip((60, 70, 90), (255, 225, 130)))
        l.rect([w * 0.22, h * 0.52, w * 0.45, h * 0.72], fill=win + (255,), outline=(90, 80, 60, 255), width=3)
        l.rect([w * 0.56, h * 0.55, w * 0.76, h - 4], fill=(120, 80, 50, 255), outline=(80, 50, 30, 255), width=3)
        return l.done()
    return cached(key, mk)


# ---------------- láminas que se estiran (zumbido) ----------------
def lamination(k=0.0, w=520, h=200):
    """paquete de láminas de hierro vistas de cerca; k en [-1,1] = cuánto se estiran (exagerado)"""
    l = D.L(w + 80, h + 20)
    n = 7
    st = 1 + 0.06 * k
    lw = w * st
    x0 = (w + 80 - lw) / 2
    for i in range(n):
        y = 10 + i * h / n
        c = 120 + (i % 2) * 18
        l.rrect([x0, y, x0 + lw, y + h / n - 5], 4, fill=(c, c + 4, c + 12, 255), outline=(60, 62, 70, 255), width=2)
        l.line([(x0 + 6, y + 3), (x0 + lw - 6, y + 3)], (190, 196, 206, 200), 2)
    return l.done()


# ---------------- símbolo del transformador ----------------
def trafo_symbol(w=430, n_lab=None, hide=False, vin='', vout=''):
    """dos bobinas (arcos) con dos rayas de núcleo en medio; textos opcionales"""
    key = ('tsym', w, n_lab, hide, vin, vout)
    def mk():
        h = int(w * 0.8)
        l = D.L(w, h)
        l.rrect([2, 2, w - 2, h - 2], 20, fill=(18, 22, 30, 225), outline=(110, 120, 140, 255), width=3)
        col = (235, 240, 250, 255)
        cx, cy = w / 2, h * 0.5
        r = h * 0.07
        for side in (-1, 1):
            x = cx + side * w * 0.12
            for j in range(4):
                yc = cy - 3 * r + j * 2 * r
                box = [x - r, yc - r, x + r, yc + r]
                if side < 0:
                    l.d.arc([v * SS for v in box], 90, 270, fill=(255, 200, 120, 255), width=5 * SS)
                else:
                    l.d.arc([v * SS for v in box], -90, 90, fill=(150, 220, 255, 255), width=5 * SS)
            l.line([(x, cy - 4 * r), (x, cy - 4 * r - 40), (x + side * w * 0.26, cy - 4 * r - 40)], col, 4)
            l.line([(x, cy + 4 * r), (x, cy + 4 * r + 40), (x + side * w * 0.26, cy + 4 * r + 40)], col, 4)
        for dx in (-7, 7):
            l.line([(cx + dx, cy - 4.4 * r), (cx + dx, cy + 4.4 * r)], (200, 205, 215, 255), 5)
        if vin:
            l.text((w * 0.16, cy), vin, 30, fill=(255, 200, 120))
        if vout:
            if hide:
                l.rrect([w * 0.72, cy - 40, w * 0.95, cy + 40], 10, fill=(60, 66, 80, 255), outline=(255, 217, 61, 255), width=3)
                l.text((w * 0.835, cy - 4), '?', 54, fill=(255, 217, 61))
            else:
                l.text((w * 0.84, cy), vout, 30, fill=(150, 220, 255))
        if n_lab:
            l.text((cx - w * 0.12, h * 0.08 + 10), n_lab[0], 22, fill=(255, 200, 120))
            l.text((cx + w * 0.12, h * 0.08 + 10), n_lab[1], 22, fill=(150, 220, 255))
        return l.done()
    return cached(key, mk)


def plug_front(w=80):
    """enchufe visto de frente (cuerpo negro) para ponerlo encima del tomacorriente"""
    key = ('plugf', w)
    def mk():
        h = int(w * 1.1)
        l = D.L(w, h)
        l.rrect([4, 4, w - 4, h - 4], 14, fill=(36, 38, 44, 255), outline=(12, 12, 16, 255), width=3)
        l.rrect([w * 0.18, h * 0.16, w * 0.4, h * 0.84], 6, fill=(60, 62, 70, 255))
        l.line([(w * 0.62, h * 0.2), (w * 0.62, h * 0.8)], (70, 72, 80, 255), 4)
        return l.done()
    return cached(key, mk)
