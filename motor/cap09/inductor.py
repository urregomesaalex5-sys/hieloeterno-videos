# Dibujos del capítulo 8 (el inductor / la bobina), con aspecto realista:
# bobina de cobre sobre núcleo de hierro, líneas de campo, brújula, pila de 9 V, interruptor de cuchilla,
# lámpara de neón, bombillo, carrito pesado (analogía de la inercia), inductor de chip con corte,
# base de carga inalámbrica + celular en corte, gráfica de corriente y las dos bobinas del reto.
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
from caps_real import _shade_cols, cached

SS = 2
COPPER = np.array((214, 120, 54), np.float32)
COPPER_HI = np.array((255, 214, 160), np.float32)
IRON = (92, 96, 104)
LEAD = (196, 200, 210)
FIELD = (90, 200, 255)
WIRE = (232, 232, 232)


# ---------------- bobina (solenoide) ----------------
def coil(w=420, h=150, turns=14, core=True, hot=0.0, leads=True):
    """bobina horizontal: alambre de cobre enrollado (cada vuelta sombreada como cilindro)
    sobre un núcleo de hierro que asoma por los lados. w = largo del bobinado."""
    key = ('coil', w, h, turns, core, round(hot, 2), leads)
    def mk():
        W0, H0 = w * SS, h * SS
        core_ext = int(0.09 * W0) if core else 0
        lead_len = int(0.16 * W0) if leads else 0
        cw = W0 + 2 * core_ext + 2 * lead_len
        ch = int(H0 * 1.15)
        im = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cy = ch / 2
        x0 = lead_len + core_ext
        # núcleo de hierro (cilindro gris oscuro) que asoma por los dos lados
        if core:
            chh = int(H0 * 0.58)
            sh = _shade_cols(chh, spec=0.3)
            arr = np.ones((chh, W0 + 2 * core_ext, 3), np.float32) * np.array(IRON, np.float32)
            arr *= sh[:, None, None]
            cim = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
            m = Image.new('L', cim.size, 0)
            md = ImageDraw.Draw(m)
            md.rounded_rectangle([0, 0, cim.size[0] - 1, chh - 1], int(chh * 0.18), fill=255)
            cim.putalpha(m)
            im.alpha_composite(cim, (lead_len, int(cy - chh / 2)))
            # cara del núcleo (elipse más clara)
            for xe in (lead_len, lead_len + W0 + 2 * core_ext - int(chh * 0.25)):
                d.ellipse([xe, cy - chh / 2, xe + int(chh * 0.25), cy + chh / 2], fill=(130, 134, 142, 255),
                          outline=(70, 72, 80, 255), width=SS * 2)
        # bobinado: vueltas sombreadas
        pitch = W0 / turns
        xs = (np.arange(W0) + 0.5)
        ys = (np.arange(H0) + 0.5) / H0
        slant = 0.18 * pitch
        X = xs[None, :] + slant * (ys[:, None] - 0.5) * 2
        u = (X / pitch) % 1.0
        s_wire = np.clip(np.sin(np.pi * u), 0, 1) ** 0.5
        s_cyl = _shade_cols(H0, spec=0.25)[:, None]
        base = COPPER * (1 - hot) + np.array((255, 110, 40), np.float32) * hot
        arr = base[None, None, :] * (0.25 + 0.75 * s_wire[..., None]) * (0.55 + 0.45 * s_cyl[..., None] / s_cyl.max())
        spec = np.exp(-((u - 0.38) / 0.09) ** 2) * np.exp(-((ys[:, None] - 0.24) / 0.12) ** 2)
        arr += COPPER_HI[None, None, :] * spec[..., None] * 0.55
        wim = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
        m = Image.new('L', (W0, H0), 0)
        md = ImageDraw.Draw(m)
        md.rounded_rectangle([0, 0, W0 - 1, H0 - 1], int(H0 * 0.14), fill=255)
        wim.putalpha(m)
        im.alpha_composite(wim, (x0, int(cy - H0 / 2)))
        # patas de alambre (cobre) que salen de los extremos
        if leads:
            lw = max(4, int(6 * SS))
            ly = cy + H0 * 0.32
            d.line([(0, ly), (x0 + pitch * 0.4, ly)], fill=(214, 140, 70, 255), width=lw)
            d.line([(cw - 1, ly), (x0 + W0 - pitch * 0.4, ly)], fill=(214, 140, 70, 255), width=lw)
        return im.resize((cw // SS, ch // SS), Image.LANCZOS)
    return cached(key, mk)


def coil_size(w=420, h=150, core=True, leads=True):
    core_ext = int(0.09 * w) if core else 0
    lead_len = int(0.16 * w) if leads else 0
    return w + 2 * core_ext + 2 * lead_len, int(h * 1.15)


def coil_ends(cx, cy, w=420, h=150, sc=1.0, core=True, leads=True):
    """puntas de las patas (izquierda, derecha) en pantalla"""
    cw, ch = coil_size(w, h, core, leads)
    ly = cy + (h * 0.32) * sc
    return (cx - cw / 2 * sc, ly), (cx + cw / 2 * sc, ly)


def winding(k, w=420, h=150, turns=14):
    """alambre recto que se va enrollando (k = 0 recto, 1 bobina completa). Dibujo plano del alambre."""
    l = D.L(int(w * 1.6), int(h * 1.6))
    cx, cy = l.w / 2, l.h / 2
    n = 240
    pts = []
    L_straight = w * 1.45
    for i in range(n):
        s = i / (n - 1)
        # posición sobre el alambre recto
        xr = cx - L_straight / 2 + s * L_straight
        yr = cy
        # posición sobre la hélice (vista de frente: senoide de amplitud h/2)
        xh = cx - w / 2 + s * w
        yh = cy - (h / 2) * math.cos(s * turns * 2 * math.pi)
        x = xr + (xh - xr) * k
        y = yr + (yh - yr) * k
        pts.append((x, y))
    l.line(pts, (150, 80, 30, 255), 16)
    l.line(pts, (220, 130, 60, 255), 11)
    l.line([(x, y - 3) for x, y in pts], (255, 200, 140, 150), 3)
    return l.done()


# ---------------- líneas de campo magnético ----------------
def field_lines(t, k, w, h, n=5, flow=1.0, sign=1, col=FIELD, inside=True):
    """capa con las líneas de campo de un solenoide (centradas). k = 0..1 aparecen.
    Las rayitas avanzan por la línea (sentido = sign)."""
    if k <= 0.01:
        return None
    W2 = int(w * 2.4); H2 = int(h * 4.6)
    l = D.L(W2, H2)
    cx, cy = W2 / 2, H2 / 2
    al = int(220 * k)
    for i in range(n):
        f = (i + 1) / n
        b = h * (0.3 + 1.9 * f)          # semieje vertical
        a = w * 0.52 + h * (0.35 + 0.9 * f)  # semieje horizontal
        grow = S.clamp((k * 1.4 - f * 0.4) / 1.0)
        if grow <= 0:
            continue
        pts = []
        N = 120
        for j in range(N + 1):
            th = 2 * math.pi * j / N
            x = cx + a * math.cos(th)
            y = cy + b * math.sin(th) * (0.45 + 0.55 * abs(math.cos(th)) ** 0.25) if False else cy + b * math.sin(th)
            pts.append((x, y))
        # se dibuja solo la parte que ya "creció" (desde la derecha hacia los dos lados)
        m = int(N * grow)
        sub = pts[:m // 2 + 1] + [None] + pts[N - m // 2:]
        seg = []
        for p in sub:
            if p is None:
                if len(seg) > 1:
                    l.line(seg, col + (int(al * 0.75),), 5)
                seg = []
            else:
                seg.append(p)
        if len(seg) > 1:
            l.line(seg, col + (int(al * 0.75),), 5)
        # flechitas que avanzan
        if grow >= 0.99:
            for q in range(3):
                ph = ((t * 0.18 * flow * sign) + q / 3 + i * 0.13) % 1.0
                th = 2 * math.pi * ph
                x = cx + a * math.cos(th); y = cy + b * math.sin(th)
                dx = -a * math.sin(th) * sign; dy = b * math.cos(th) * sign
                ang = math.atan2(dy, dx)
                tip = (x + 14 * math.cos(ang), y + 14 * math.sin(ang))
                l1 = (x - 12 * math.cos(ang - 0.6), y - 12 * math.sin(ang - 0.6))
                l2 = (x - 12 * math.cos(ang + 0.6), y - 12 * math.sin(ang + 0.6))
                l.poly([tip, l1, l2], fill=(200, 240, 255, al))
    return l.done()


# ---------------- brújula ----------------
def compass(angle=0.0, size=170):
    """brújula vista desde arriba. angle = giro de la aguja (rad, 0 = apunta arriba)."""
    key = ('comp', round(angle, 2), size)
    def mk():
        l = D.L(size, size)
        c = (size / 2, size / 2)
        r = size / 2 - 6
        l.circle(c, r, fill=(186, 140, 60, 255), outline=(110, 80, 30, 255), width=4)
        l.circle(c, r * 0.84, fill=(244, 240, 228, 255), outline=(150, 120, 60, 255), width=3)
        for kk in range(12):
            a = kk / 12 * 2 * math.pi
            r0 = r * (0.7 if kk % 3 == 0 else 0.76)
            l.line([(c[0] + r0 * math.sin(a), c[1] - r0 * math.cos(a)), (c[0] + r * 0.82 * math.sin(a), c[1] - r * 0.82 * math.cos(a))],
                   (80, 70, 60, 255), 3)
        l.text((c[0], c[1] - r * 0.56), 'N', int(size * 0.13), fill=(200, 40, 40))
        # aguja: mitad roja (norte) y mitad blanca
        L = r * 0.62; wdt = r * 0.14
        ca, sa = math.cos(angle), math.sin(angle)
        def rot(dx, dy):
            return (c[0] + dx * ca - dy * sa, c[1] + dx * sa + dy * ca)
        l.poly([rot(0, -L), rot(wdt, 0), rot(-wdt, 0)], fill=(220, 40, 40, 255))
        l.poly([rot(0, L), rot(wdt, 0), rot(-wdt, 0)], fill=(235, 235, 240, 255), outline=(120, 120, 130, 255))
        l.circle(c, r * 0.07, fill=(60, 60, 64, 255))
        # brillo del vidrio
        l.circle((c[0] - r * 0.3, c[1] - r * 0.35), r * 0.18, fill=(255, 255, 255, 60))
        return l.done()
    return cached(key, mk)


# ---------------- pila AA de 1,5 V (genérica) ----------------
def battery_aa(h=230, vertical=True):
    key = ('aa', h)
    def mk():
        w = int(h * 0.36)
        l = D.L(w + 12, h + 24)
        cx = (w + 12) / 2
        l.rrect([cx - w * 0.18, 4, cx + w * 0.18, 22], 4, fill=(205, 208, 214, 255), outline=(120, 122, 130, 255), width=2)
        l.rrect([6, 18, w + 6, h + 18], 14, fill=(30, 30, 34, 255), outline=(12, 12, 14, 255), width=3)
        l.rrect([6, 18, w + 6, 18 + h * 0.34], 14, fill=(214, 168, 60, 255))
        l.rect([6, 18 + h * 0.2, w + 6, 18 + h * 0.34], fill=(214, 168, 60, 255))
        l.rect([12, 26, 20, h + 10], fill=(255, 255, 255, 45))
        l.text((cx, 18 + h * 0.13), '+', int(h * 0.12), fill=(60, 40, 10))
        l.text((cx, 18 + h * 0.62), '1,5V', int(h * 0.13), fill=(240, 240, 245))
        l.text((cx, h + 6), '−', int(h * 0.1), fill=(200, 200, 205))
        return l.done()
    return cached(key, mk)


# ---------------- pila de 9 V (genérica) ----------------
def battery9v(h=200):
    key = ('b9', h)
    def mk():
        w = int(h * 0.62)
        l = D.L(w + 10, h + 40)
        top = 34
        # broches (+ y −)
        l.circle((w * 0.32, 20), 15, fill=(205, 208, 214, 255), outline=(120, 122, 130, 255), width=3)
        l.rrect([w * 0.66 - 15, 6, w * 0.66 + 15, 34], 5, fill=(205, 208, 214, 255), outline=(120, 122, 130, 255), width=3)
        l.rect([w * 0.66 - 8, 2, w * 0.66 + 8, 12], fill=(190, 192, 198, 255))
        # cuerpo
        l.rrect([4, top, w + 4, h + 34], 12, fill=(30, 30, 34, 255), outline=(10, 10, 12, 255), width=3)
        l.rrect([4, top, w + 4, top + h * 0.30], 12, fill=(214, 168, 60, 255))
        l.rect([4, top + h * 0.22, w + 4, top + h * 0.30], fill=(214, 168, 60, 255))
        l.rect([12, top + 8, 22, h + 26], fill=(255, 255, 255, 40))
        l.text(((w + 8) / 2, top + h * 0.15), '+  −', int(h * 0.11), fill=(60, 40, 10))
        l.text(((w + 8) / 2, top + h * 0.6), '9V', int(h * 0.26), fill=(240, 240, 245))
        return l.done()
    return cached(key, mk)


# ---------------- interruptor de cuchilla ----------------
# Visto de lado. La bisagra queda a la DERECHA y el mango a la IZQUIERDA (hacia el personaje).
def _ksw_geom(open_k, w):
    CW = w + 70
    h = int(w * 0.9)
    by = h - 40
    hx, hy = 40, by - 26            # bisagra (antes de reflejar)
    cx_ = w - 46                    # contacto
    a = -math.radians(68) * open_k
    L = cx_ - hx
    tip = (hx + L * math.cos(a), hy + L * math.sin(a))
    ht = (tip[0] + 50 * math.cos(a), tip[1] + 50 * math.sin(a))
    return CW, h, by, hx, hy, cx_, a, tip, ht


def knife_switch(open_k=0.0, w=230):
    """open_k = 0 cerrado, 1 abierto (la cuchilla sube ~70°)."""
    key = ('ksw', round(open_k, 2), w)
    def mk():
        CW, h, by, hx, hy, cx_, a, tip, ht = _ksw_geom(open_k, w)
        l = D.L(CW, h)
        l.rrect([6, by, w - 6, h - 6], 8, fill=(150, 98, 52, 255), outline=(90, 56, 26, 255), width=3)
        l.rect([12, by + 6, w - 12, by + 12], fill=(190, 136, 80, 255))
        for x in (hx, cx_):
            l.rrect([x - 16, by - 40, x + 16, by + 2], 4, fill=(190, 150, 70, 255), outline=(110, 80, 30, 255), width=3)
        l.line([(hx, hy), tip], (120, 70, 30, 255), 16)
        l.line([(hx, hy), tip], (222, 150, 80, 255), 10)
        l.line([tip, ht], (24, 24, 28, 255), 22)
        l.circle(ht, 11, fill=(24, 24, 28, 255))
        l.circle((hx, hy), 8, fill=(80, 70, 50, 255))
        return l.done().transpose(Image.FLIP_LEFT_RIGHT)
    return cached(key, mk)


def knife_handle(open_k, w=230):
    """punta del mango, relativa al centro del dibujo"""
    CW, h, by, hx, hy, cx_, a, tip, ht = _ksw_geom(open_k, w)
    return -(ht[0] - CW / 2), ht[1] - h / 2


def knife_contact(w=230):
    CW, h, by, hx, hy, cx_, a, tip, ht = _ksw_geom(0, w)
    return -(cx_ - CW / 2), hy - h / 2


def knife_posts(w=230):
    """bases de los dos postes (para conectar cables): (contacto, bisagra), relativas al centro"""
    CW, h, by, hx, hy, cx_, a, tip, ht = _ksw_geom(0, w)
    return (-(cx_ - CW / 2), h / 2 - 8), (-(hx - CW / 2), h / 2 - 8)


# ---------------- lámpara de neón (tipo NE-2) ----------------
def neon(on=0.0, h=210):
    """foquito de neón vertical: cápsula de vidrio con dos electrodos paralelos; al prender brilla naranja
    alrededor de un electrodo."""
    key = ('neon', round(on, 2), h)
    def mk():
        H0 = h * SS
        w0 = int(H0 * 0.36)
        im = Image.new('RGBA', (w0, H0), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx = w0 / 2
        gw = w0 * 0.62
        gt, gb = H0 * 0.04, H0 * 0.58
        # patas
        lw = max(3, int(4 * SS))
        d.line([(cx - gw * 0.18, gb), (cx - gw * 0.18, H0)], fill=LEAD + (255,), width=lw)
        d.line([(cx + gw * 0.18, gb), (cx + gw * 0.18, H0)], fill=LEAD + (255,), width=lw)
        # resplandor naranja interior
        if on > 0.02:
            g = Image.new('RGBA', (w0, H0), (0, 0, 0, 0))
            gd = ImageDraw.Draw(g)
            gd.ellipse([cx - gw * 0.5, gt + gw * 0.1, cx + gw * 0.15, gb - gw * 0.1], fill=(255, 110, 30, int(200 * on)))
            g = g.filter(ImageFilter.GaussianBlur(12 * SS))
            im.alpha_composite(g)
        # vidrio
        d.rounded_rectangle([cx - gw / 2, gt, cx + gw / 2, gb], int(gw / 2), fill=(225, 235, 240, 70 if on < 0.5 else 40),
                            outline=(235, 245, 250, 210), width=int(3 * SS))
        # electrodos
        ecol = (150, 150, 155, 255) if on < 0.3 else (255, 170, 80, 255)
        d.line([(cx - gw * 0.18, gb), (cx - gw * 0.18, gt + gw * 0.55)], fill=ecol, width=int(6 * SS))
        d.line([(cx + gw * 0.18, gb), (cx + gw * 0.18, gt + gw * 0.55)], fill=(150, 150, 155, 255), width=int(6 * SS))
        if on > 0.02:
            d.line([(cx - gw * 0.18, gb - 4), (cx - gw * 0.18, gt + gw * 0.5)], fill=(255, 200, 120, int(255 * on)), width=int(10 * SS))
        # brillo del vidrio
        d.line([(cx - gw * 0.34, gt + gw * 0.35), (cx - gw * 0.34, gb - gw * 0.4)], fill=(255, 255, 255, 120), width=int(4 * SS))
        # base sellada
        d.rectangle([cx - gw * 0.46, gb - gw * 0.12, cx + gw * 0.46, gb], fill=(210, 220, 225, 160))
        return im.resize((w0 // SS, H0 // SS), Image.LANCZOS)
    return cached(key, mk)


# ---------------- bombillo pequeño ----------------
def bulb(on=0.0, h=200):
    key = ('bulb', round(on, 2), h)
    def mk():
        H0 = h * SS
        w0 = int(H0 * 0.7)
        im = Image.new('RGBA', (w0, H0), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx = w0 / 2
        r = w0 * 0.42
        cy = r + 4
        if on > 0.02:
            g = Image.new('RGBA', (w0, H0), (0, 0, 0, 0))
            ImageDraw.Draw(g).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 220, 120, int(220 * on)))
            g = g.filter(ImageFilter.GaussianBlur(10 * SS))
            im.alpha_composite(g)
        gcol = tuple(int(a + (b - a) * on) for a, b in zip((230, 238, 245), (255, 236, 160)))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=gcol + (60 + int(170 * on),), outline=(235, 242, 250, 220), width=int(3 * SS))
        # cuello y rosca
        d.polygon([(cx - r * 0.5, cy + r * 0.8), (cx + r * 0.5, cy + r * 0.8), (cx + r * 0.42, cy + r * 1.25), (cx - r * 0.42, cy + r * 1.25)],
                  fill=(230, 238, 245, 90))
        for k in range(4):
            y = cy + r * 1.25 + k * r * 0.16
            d.rounded_rectangle([cx - r * 0.44, y, cx + r * 0.44, y + r * 0.14], int(r * 0.05), fill=(196, 198, 206, 255), outline=(140, 142, 150, 255), width=SS)
        d.ellipse([cx - r * 0.18, cy + r * 1.9 - 4, cx + r * 0.18, cy + r * 2.05], fill=(60, 60, 66, 255))
        # filamento
        fc = tuple(int(a + (b - a) * on) for a, b in zip((90, 80, 70), (255, 250, 210)))
        d.line([(cx - r * 0.25, cy + r * 0.8), (cx - r * 0.25, cy), (cx + r * 0.25, cy), (cx + r * 0.25, cy + r * 0.8)],
               fill=(150, 150, 156, 255), width=int(2 * SS))
        pts = [(cx - r * 0.25 + k * r * 0.5 / 8, cy - (r * 0.08 if k % 2 else -r * 0.04)) for k in range(9)]
        d.line(pts, fill=fc + (255,), width=int(4 * SS))
        d.ellipse([cx - r * 0.6, cy - r * 0.65, cx - r * 0.25, cy - r * 0.2], fill=(255, 255, 255, 90))
        return im.resize((w0 // SS, H0 // SS), Image.LANCZOS)
    return cached(key, mk)


# ---------------- carrito pesado (analogía de la inercia) ----------------
def cart(w=300, label='MUY PESADO'):
    key = ('cart', w, label)
    def mk():
        h = int(w * 0.62)
        l = D.L(w, h)
        # caja de hierro remachada
        l.poly([(10, 20), (w - 10, 20), (w - 34, h - 48), (34, h - 48)], fill=(110, 114, 122, 255), outline=(60, 62, 70, 255), width=4)
        l.rect([10, 20, w - 10, 34], fill=(150, 154, 162, 255))
        for k in range(6):
            x = 40 + k * (w - 80) / 5
            l.circle((x, 50), 5, fill=(70, 72, 80, 255))
            l.circle((x + (w / 2 - x) * 0.08, h - 62), 5, fill=(70, 72, 80, 255))
        # carga: bloques de piedra
        for k, x in enumerate((60, 120, 180, 240)):
            if x > w - 40:
                continue
            l.rect([x - 26, -2 + 8 * (k % 2), x + 26, 22 + 8 * (k % 2)], fill=(128, 128, 134, 255), outline=(80, 80, 88, 255), width=3)
        l.text((w / 2, (20 + h - 48) / 2 + 6), label, 22, fill=(235, 235, 240))
        # ruedas
        for x in (w * 0.28, w * 0.72):
            l.circle((x, h - 30), 26, fill=(40, 40, 46, 255), outline=(150, 150, 160, 255), width=5)
            l.circle((x, h - 30), 7, fill=(150, 150, 160, 255))
        return l.done()
    return cached(key, mk)


def rails(w=900):
    key = ('rails', w)
    def mk():
        l = D.L(w, 40)
        for k in range(int(w / 50) + 1):
            l.rect([k * 50 + 6, 14, k * 50 + 36, 36], fill=(120, 80, 44, 255))
        l.line([(0, 12), (w, 12)], (170, 172, 180, 255), 6)
        return l.done()
    return cached(key, mk)


# ---------------- inductor de chip (montaje superficial) ----------------
def smd_inductor(w=300, cut=1.0):
    """inductor de potencia de chip: bloque gris oscuro con terminales plateados; con 'cut' se ve un corte
    con el bobinado de cobre por dentro."""
    key = ('smdL', w, round(cut, 2))
    def mk():
        h = int(w * 0.8)
        l = D.L(w + 20, h + 20)
        l.rrect([10, 10, w + 10, h + 10], 18, fill=(58, 60, 66, 255), outline=(30, 30, 34, 255), width=4)
        l.rrect([10, 10, 10 + w * 0.16, h + 10], 10, fill=(205, 210, 218, 255))
        l.rrect([w + 10 - w * 0.16, 10, w + 10, h + 10], 10, fill=(205, 210, 218, 255))
        if cut > 0.01:
            cx0, cy0 = 10 + w * 0.24, 10 + h * 0.18
            cx1, cy1 = 10 + w * 0.76, 10 + h * 0.82
            l.rrect([cx0, cy0, cx1, cy1], 10, fill=(34, 34, 38, int(255 * cut)))
            nt = 7
            for k in range(nt):
                x = cx0 + 14 + k * (cx1 - cx0 - 28) / (nt - 1)
                l.line([(x - 6, cy0 + 10), (x + 6, cy1 - 10)], (150, 80, 30, int(255 * cut)), 16)
                l.line([(x - 6, cy0 + 10), (x + 6, cy1 - 10)], (232, 140, 64, int(255 * cut)), 10)
                l.line([(x - 8, cy0 + 14), (x + 2, cy1 - 30)], (255, 210, 160, int(150 * cut)), 3)
        return l.done()
    return cached(key, mk)


def pcb_panel_L():
    """placa de celular con chips y pasivos diminutos, con varios inductores de potencia (bloques grises)"""
    def mk():
        rng = random.Random(11)
        PW, PH = 600, 470
        l = D.L(PW, PH)
        l.rrect([4, 4, PW - 4, PH - 4], 26, fill=(18, 92, 58, 255), outline=(10, 50, 30, 255), width=6)
        for k in range(14):
            y = rng.randint(30, PH - 30)
            l.line([(20, y), (PW - 20, y)], (196, 132, 58, 160), 4)
        for k in range(8):
            x = rng.randint(30, PW - 30)
            l.line([(x, 20), (x, PH - 20)], (196, 132, 58, 140), 4)
        for (x, y, w, h, lab) in ((60, 60, 170, 120, 'SoC'), (330, 280, 180, 120, 'PMIC')):
            l.rrect([x, y, x + w, y + h], 6, fill=(26, 26, 30, 255), outline=(60, 60, 66, 255), width=3)
            l.text((x + w / 2, y + h / 2), lab, 24, fill=(150, 150, 160))
        # inductores de potencia junto al PMIC
        for (x, y) in ((300, 220), (360, 220), (420, 220), (480, 220), (540, 300)):
            l.rrect([x - 22, y - 18, x + 22, y + 18], 5, fill=(70, 72, 80, 255), outline=(40, 40, 44, 255), width=2)
            l.rect([x - 22, y - 18, x - 15, y + 18], fill=(205, 210, 218, 255))
            l.rect([x + 15, y - 18, x + 22, y + 18], fill=(205, 210, 218, 255))
        for k in range(55):
            x = rng.randint(30, PW - 50); y = rng.randint(30, PH - 40)
            if 50 < x < 240 and 50 < y < 190 or 280 < x < 570 and 190 < y < 410:
                continue
            res = rng.random() < 0.5
            w, h = 22, 12
            if rng.random() < 0.5:
                w, h = h, w
            l.rect([x, y, x + w, y + h], fill=((30, 30, 32) if res else (200, 160, 110)) + (255,))
        return l.done()
    return cached('pcbL', mk)
PCB_L_SPOT = (420, 220)   # inductor que se ve en la lupa (coordenadas dentro del panel)


# ---------------- carga inalámbrica (vista de lado, en corte) ----------------
QI_W, QI_H = 640, 520
def qi_scene(t, on=1.0, k_phone=1.0, charge=0.0, flow=1.0):
    """base de carga (abajo) con su bobina plana y un celular encima con la suya, en corte lateral.
    on = la base está encendida (campo que cambia de sentido). charge = 0..1 nivel de batería."""
    l = D.L(QI_W, QI_H)
    cx = QI_W / 2
    # base (puck)
    by = QI_H - 120
    l.rrect([cx - 230, by, cx + 230, by + 92], 40, fill=(40, 42, 48, 255), outline=(90, 94, 104, 255), width=4)
    l.rrect([cx - 200, by + 16, cx + 200, by + 60], 16, fill=(26, 26, 30, 255))
    # bobina de la base: cortes del alambre (círculos de cobre) a los dos lados
    phase = math.sin(t * 2 * math.pi * 1.2)
    def coil_row(y, xs, glow):
        for x in xs:
            l.circle((x, y), 13, fill=(214, 120, 54, 255), outline=(120, 60, 20, 255), width=3)
            l.circle((x - 4, y - 4), 4, fill=(255, 210, 160, 200))
            if glow > 0:
                # punto (sale) o cruz (entra): sentido de la corriente que alterna
                s = 1 if (glow > 0) else -1
    xs_l = [cx - 170 + k * 26 for k in range(5)]
    xs_r = [cx + 66 + k * 26 for k in range(5)]
    coil_row(by + 38, xs_l + xs_r, 1)
    # corriente alterna en la base: puntos/cruces que cambian
    for x in xs_l:
        if phase > 0:
            l.circle((x, by + 38), 4, fill=(20, 20, 20, 255))
        else:
            l.line([(x - 5, by + 33), (x + 5, by + 43)], (20, 20, 20, 255), 3); l.line([(x + 5, by + 33), (x - 5, by + 43)], (20, 20, 20, 255), 3)
    for x in xs_r:
        if phase <= 0:
            l.circle((x, by + 38), 4, fill=(20, 20, 20, 255))
        else:
            l.line([(x - 5, by + 33), (x + 5, by + 43)], (20, 20, 20, 255), 3); l.line([(x + 5, by + 33), (x - 5, by + 43)], (20, 20, 20, 255), 3)
    # celular encima (en corte): carcasa, bobina receptora, batería, pantalla
    if k_phone > 0.01:
        py = by - 150 - 220 * (1 - k_phone)
        l.rrect([cx - 250, py, cx + 250, py + 110], 26, fill=(30, 32, 40, int(255 * k_phone)), outline=(150, 156, 170, int(255 * k_phone)), width=5)
        l.rect([cx - 236, py + 8, cx + 236, py + 22], fill=(60, 120, 200, int(255 * k_phone)))  # pantalla
        # batería
        l.rrect([cx - 220, py + 32, cx - 20, py + 70], 8, fill=(70, 74, 84, int(255 * k_phone)), outline=(140, 146, 160, int(255 * k_phone)), width=3)
        if charge > 0:
            l.rrect([cx - 214, py + 38, cx - 214 + 188 * charge, py + 64], 6, fill=(80, 220, 110, int(255 * k_phone)))
        # bobina receptora (abajo, cerca de la base)
        for x in [cx - 150 + k * 22 for k in range(4)] + [cx + 84 + k * 22 for k in range(4)]:
            l.circle((x, py + 92), 10, fill=(214, 120, 54, int(255 * k_phone)), outline=(120, 60, 20, int(255 * k_phone)), width=2)
        # corriente inducida: puntitos amarillos que corren hacia la batería
        if on > 0.3 and k_phone > 0.95:
            for q in range(6):
                u = (t * 0.9 * flow + q / 6) % 1.0
                x = cx + 120 - u * 260
                l.circle((x, py + 80 - 30 * u), 6, fill=D.CURR + (220,))
    # campo: lazos que suben por el centro y bajan por fuera (cambian de sentido con la fase)
    if on > 0.01:
        amp = abs(phase)
        for i in range(4):
            f = (i + 1) / 4
            a = 50 + 150 * f; b = 90 + 170 * f
            pts = []
            for j in range(61):
                th = math.pi * j / 60
                pts.append((cx + a * math.cos(th) * (1 if True else -1), by + 38 - b * math.sin(th)))
            al = int(170 * on * (0.35 + 0.65 * amp))
            l.line(pts, FIELD + (al,), 5)
            pts2 = [(2 * cx - x, y) for x, y in pts]
            l.line(pts2, FIELD + (al,), 5)
        # flecha central (sube o baja)
        s = 1 if phase > 0 else -1
        ya, yb_ = by + 10, by - 170
        if s < 0:
            ya, yb_ = yb_, ya
        D.arrow(l, (cx, ya), (cx, yb_), (150, 225, 255, int(230 * on * (0.3 + 0.7 * amp))), 8, 22)
    return l.done()


# ---------------- gráfica: corriente al conectar ----------------
def graph_rise(k, w=420, h=260, show_r=True, show_l=True, cut=None):
    """corriente vs tiempo: con resistencia sube de una (línea gris), con bobina sube poco a poco (naranja).
    k = 0..1 cuánto de la curva se ha dibujado. cut = punto (0..1) donde se abre el interruptor."""
    l = D.L(w, h)
    l.rrect([4, 4, w - 4, h - 4], 16, fill=(18, 20, 26, 225), outline=(200, 205, 215, 255), width=3)
    x0, y0, x1, y1 = 50, 30, w - 24, h - 48
    l.line([(x0, y1), (x1, y1)], (200, 205, 215, 255), 3)
    l.line([(x0, y1), (x0, y0)], (200, 205, 215, 255), 3)
    l.text((x0 - 26, (y0 + y1) / 2), 'I', 26, fill=(230, 230, 235))
    l.text(((x0 + x1) / 2, h - 22), 'tiempo →', 20, fill=(200, 205, 215))
    n = 80
    for which in ('r', 'l'):
        if (which == 'r' and not show_r) or (which == 'l' and not show_l):
            continue
        pts = []
        for j in range(n + 1):
            u = j / n
            if u > k:
                break
            ut = max(0.0, (u - 0.08) / 0.92)
            if u < 0.08:
                v = 0.0
            elif which == 'r':
                v = 1.0
            else:
                v = 1 - math.exp(-ut * 4.5)
            if cut is not None and u > cut:
                v = 0.0 if which == 'r' else v * 0.0
            pts.append((x0 + (x1 - x0) * u, y1 - (y1 - y0 - 10) * v))
        if len(pts) > 1:
            col = (170, 176, 190, 255) if which == 'r' else (255, 160, 60, 255)
            l.line(pts, col, 6)
    return l.done()


# ---------------- las dos bobinas del reto ----------------
def reto_pair(k=1.0):
    def mk():
        l = D.L(560, 300)
        a = coil(220, 90, 7, core=False, leads=False)
        b = coil(220, 90, 14, core=False, leads=False)
        l.im.alpha_composite(a.resize((a.size[0] * 2, a.size[1] * 2)), (20 * 2, 70 * 2))
        l.im.alpha_composite(b.resize((b.size[0] * 2, b.size[1] * 2)), (300 * 2, 70 * 2))
        l.text((140, 40), 'N VUELTAS', 26, fill=(255, 255, 255))
        l.text((420, 40), '2N VUELTAS', 26, fill=(255, 220, 120))
        l.text((140, 230), 'L', 40, fill=(255, 255, 255))
        l.text((420, 230), '¿×2 o ×4?', 40, fill=(255, 220, 120))
        return l.done()
    return cached('reto', mk)
