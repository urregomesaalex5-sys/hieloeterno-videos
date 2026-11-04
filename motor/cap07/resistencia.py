# Dibujos del capítulo 7 (la resistencia), con aspecto realista: resistencia con franjas,
# LED rojo de 5 mm (prendido, apagado o quemado), fuente de laboratorio, multímetros,
# barras de corriente/voltaje, red de átomos (modelo simplificado), termómetro y tostadora.
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
from caps_real import _shade_cols, _cyl, cached

SS = 2
# colores del código (IEC 60062)
BAND = {
    'negro': (22, 22, 24), 'marron': (120, 66, 28), 'rojo': (205, 30, 32), 'naranja': (240, 120, 20),
    'amarillo': (245, 210, 30), 'verde': (30, 150, 60), 'azul': (40, 80, 200), 'violeta': (140, 60, 170),
    'gris': (130, 130, 135), 'blanco': (240, 240, 240), 'dorado': (212, 170, 60), 'plata': (200, 204, 210),
}
B330 = ('naranja', 'naranja', 'marron', 'dorado')
B1K = ('marron', 'negro', 'rojo', 'dorado')
BODY = (226, 204, 160)   # beige típico de resistencia de carbón
LEAD = (196, 200, 210)


# ---------------- resistencia ----------------
def resistor(w=320, bands=B330, glow=0.0, leads=True, hl=None, q=False):
    """resistencia horizontal con aspecto realista. w = ancho del cuerpo (sin patas).
    hl = índice de franja resaltada (o None). glow = 0..1 (se pone naranja de calor)."""
    key = ('res', w, bands, round(glow, 2), leads, hl, q)
    def mk():
        bw = w * SS
        bh = int(bw * 0.30)
        lead_len = int(bw * 0.45) if leads else 0
        cw = bw + 2 * lead_len
        ch = int(bh * 1.25)
        im = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        cy = ch // 2
        d = ImageDraw.Draw(im)
        if leads:
            lw = max(3, int(bh * 0.10))
            d.line([(0, cy), (lead_len + bw * 0.1, cy)], fill=LEAD + (255,), width=lw)
            d.line([(cw - lead_len - bw * 0.1, cy), (cw, cy)], fill=LEAD + (255,), width=lw)
            d.line([(0, cy - lw * 0.25), (lead_len, cy - lw * 0.25)], fill=(240, 242, 248, 255), width=max(1, lw // 3))
            d.line([(cw - lead_len, cy - lw * 0.25), (cw, cy - lw * 0.25)], fill=(240, 242, 248, 255), width=max(1, lw // 3))
        # cuerpo: hueso de perro (extremos más gruesos), sombreado como cilindro (vertical)
        u = (np.arange(bw) + 0.5) / bw
        prof = 0.78 + 0.22 * (np.exp(-((u - 0.1) / 0.08) ** 2) + np.exp(-((u - 0.9) / 0.08) ** 2))
        prof = np.clip(prof, 0.78, 1.0)
        base = np.array(BODY, np.float32)
        if glow > 0:
            base = base * (1 - glow) + np.array((255, 120, 40), np.float32) * glow
        sh = _shade_cols(bh, spec=0.3)  # sombreado a lo alto
        arr = np.ones((bh, bw, 3), np.float32) * base[None, None, :]
        # franjas
        xs = [0.25, 0.37, 0.49, 0.74]
        for k, (bx, nm) in enumerate(zip(xs, bands)):
            col = np.array(BAND[nm], np.float32)
            if q:
                col = col * 0.92
            m = np.abs(u - bx) < 0.045
            arr[:, m] = col
        arr = arr * sh[:, None, None]
        # brillo metálico del dorado
        mgold = np.abs(u - xs[3]) < 0.045
        if bands[3] in ('dorado', 'plata'):
            arr[:, mgold] += (40 * np.exp(-((np.arange(bh) / bh - 0.3) / 0.08) ** 2))[:, None, None]
        body = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
        mask = Image.new('L', (bw, bh), 0)
        md = ImageDraw.Draw(mask)
        rc = 0.07
        for x in range(bw):
            hh = bh * prof[x]
            e = min(u[x], 1 - u[x])
            if e < rc:
                hh *= math.sqrt(max(0.0, 1 - ((rc - e) / rc) ** 2))
            md.line([(x, (bh - hh) / 2), (x, (bh + hh) / 2)], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(0.6 * SS))
        body.putalpha(mask)
        im.alpha_composite(body, (lead_len, cy - bh // 2))
        if hl is not None:
            bx = lead_len + xs[hl] * bw
            d.rounded_rectangle([bx - 0.07 * bw, cy - bh * 0.62, bx + 0.07 * bw, cy + bh * 0.62], 8 * SS,
                                outline=(255, 240, 120, 255), width=int(5 * SS))
        out = im.resize((cw // SS, ch // SS), Image.LANCZOS)
        if q:
            l = D.L(out.size[0], out.size[1])
            l.text((out.size[0] / 2, out.size[1] / 2), '?', out.size[1] * 0.7, fill=(255, 255, 255), stroke=4, stroke_fill=(40, 30, 10))
            out.alpha_composite(l.done())
        return out
    return cached(key, mk)


def band_x(w, k):
    """posición x (relativa al centro) de la franja k de resistor(w)"""
    xs = [0.25, 0.37, 0.49, 0.74]
    return (xs[k] - 0.5) * w


# ---------------- LED rojo de 5 mm ----------------
def led(on=0.0, burnt=0.0, h=200):
    """LED rojo vertical: domo arriba, patas abajo. on 0..1 (o >1 = sobrecarga), burnt 0..1"""
    key = ('led', round(on, 2), round(burnt, 2), h)
    def mk():
        H0 = h * SS
        w0 = int(H0 * 0.42)
        cw = int(w0 * 1.1)
        im = Image.new('RGBA', (cw, H0), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx = cw / 2
        rad = w0 * 0.36
        top = rad * 0.2
        body_b = top + rad + w0 * 0.55
        rim_b = body_b + w0 * 0.10
        # patas
        lw = max(3, int(5 * SS))
        d.line([(cx - rad * 0.4, rim_b), (cx - rad * 0.4, H0)], fill=LEAD + (255,), width=lw)
        d.line([(cx + rad * 0.4, rim_b), (cx + rad * 0.4, H0 - w0 * 0.25)], fill=LEAD + (255,), width=lw)
        # color del epoxy
        lit = min(on, 1.0)
        dark = (110, 18, 22)
        bright = (255, 90, 80)
        if on > 1.0:
            bright = (255, 235, 220)
        col = tuple(int(dark[i] + (bright[i] - dark[i]) * min(1, on)) for i in range(3))
        if burnt > 0:
            col = tuple(int(c * (1 - burnt) + b * burnt) for c, b in zip(col, (34, 22, 20)))
        sh = _shade_cols(int(2 * rad), spec=0.3)
        bw = int(2 * rad)
        bh = int(body_b - top)
        arr = np.ones((bh, bw, 3), np.float32) * np.array(col, np.float32)
        arr *= (0.55 + 0.45 * sh)[None, :, None] if lit < 0.5 else (0.85 + 0.15 * sh)[None, :, None]
        body = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
        m = Image.new('L', (bw, bh), 0)
        md = ImageDraw.Draw(m)
        md.ellipse([0, 0, bw, 2 * rad], fill=255)
        md.rectangle([0, rad, bw, bh], fill=255)
        body.putalpha(m.point(lambda v: int(v * (0.92 if burnt < 0.5 else 1.0))))
        im.alpha_composite(body, (int(cx - rad), int(top)))
        # aro de abajo
        d.rectangle([cx - rad * 1.12, body_b, cx + rad * 1.12, rim_b], fill=tuple(int(c * 0.8) for c in col) + (255,))
        # brillito del domo
        if burnt < 0.5:
            d.ellipse([cx - rad * 0.55, top + rad * 0.25, cx - rad * 0.15, top + rad * 0.9], fill=(255, 255, 255, 120 if lit < 0.5 else 200))
        # dentro: yunque y poste
        d.line([(cx - rad * 0.4, body_b), (cx - rad * 0.4, top + rad * 1.2)], fill=(80, 70, 70, 140), width=int(6 * SS))
        d.line([(cx + rad * 0.4, body_b), (cx + rad * 0.4, top + rad * 1.0)], fill=(80, 70, 70, 140), width=int(4 * SS))
        # quemado: grietas
        if burnt > 0.3:
            a = int(255 * min(1, (burnt - 0.3) / 0.4))
            rr = random.Random(7)
            for _ in range(4):
                x0 = cx + rr.uniform(-rad * 0.5, rad * 0.5); y0 = top + rr.uniform(rad * 0.3, rad * 1.4)
                pts = [(x0, y0)]
                for _j in range(3):
                    x0 += rr.uniform(-rad * 0.35, rad * 0.35); y0 += rr.uniform(rad * 0.1, rad * 0.4)
                    pts.append((x0, y0))
                d.line(pts, fill=(200, 190, 170, a), width=int(3 * SS))
            d.ellipse([cx - rad * 0.3, top + rad * 0.2, cx + rad * 0.1, top + rad * 0.6], fill=(15, 10, 10, a))
        return im.resize((cw // SS, H0 // SS), Image.LANCZOS)
    return cached(key, mk)


# ---------------- fuente de laboratorio ----------------
SUP_W, SUP_H = 280, 190
def supply(volts='5,00', amps='0.00', pressed=0.0, on=True):
    key = ('sup', volts, amps, round(pressed, 1), on)
    def mk():
        l = D.L(SUP_W, SUP_H + 30)
        y0 = 30
        # terminales arriba
        for x, col in ((90, (30, 30, 34)), (190, (210, 40, 40))):
            l.rrect([x - 16, 6, x + 16, y0 + 8], 6, fill=col + (255,), outline=(255, 255, 255, 120), width=2)
            l.rect([x - 6, 0, x + 6, 14], fill=(200, 200, 205, 255))
        l.text((50, y0 - 12), '−', 26, fill=(230, 230, 230))
        l.text((230, y0 - 12), '+', 26, fill=(255, 120, 120))
        # caja
        l.rrect([4, y0, SUP_W - 4, SUP_H + 26], 14, fill=(150, 156, 166, 255), outline=(90, 96, 106, 255), width=4)
        l.rect([4, y0 + 8, SUP_W - 4, y0 + 22], fill=(175, 180, 190, 255))
        l.rrect([18, y0 + 30, SUP_W - 18, SUP_H + 10], 10, fill=(38, 42, 50, 255))
        # pantalla
        l.rrect([30, y0 + 42, 190, y0 + 108], 6, fill=(8, 22, 12, 255), outline=(70, 80, 90, 255), width=3)
        if on:
            l.text((110, y0 + 66), volts + ' V', 34, fill=(90, 255, 120))
            l.text((110, y0 + 96), amps + ' A', 20, fill=(90, 220, 120))
        # perilla
        l.circle((236, y0 + 72), 28, fill=(60, 64, 72, 255), outline=(180, 186, 196, 255), width=4)
        l.line([(236, y0 + 72), (236 + 18, y0 + 56)], (230, 230, 235, 255), 5)
        # botón de encendido
        py = 6 * pressed
        l.rrect([40, y0 + 122 + py, 120, y0 + 152 + py], 8, fill=(210, 60, 40, 255) if not on else (60, 200, 90, 255),
                outline=(255, 255, 255, 160), width=2)
        l.text((80, y0 + 137 + py), 'ON', 20, fill=(255, 255, 255))
        l.text((200, y0 + 140), 'FUENTE DC', 18, fill=(170, 176, 186))
        return l.done()
    return cached(key, mk)


# ---------------- multímetro ----------------
def meter(txt, kind='V', w=200):
    key = ('met', txt, kind, w)
    def mk():
        h = int(w * 0.62)
        l = D.L(w, h)
        body = (250, 200, 30) if kind == 'V' else (60, 170, 240)
        l.rrect([4, 4, w - 4, h - 4], 16, fill=body + (255,), outline=(60, 50, 10, 255), width=4)
        l.rrect([16, 14, w - 16, h - 40], 8, fill=(190, 210, 180, 255), outline=(40, 40, 40, 255), width=3)
        l.text((w / 2, (14 + h - 40) / 2 + 2), txt, int(h * 0.30), fill=(20, 30, 20))
        l.text((w / 2, h - 22), 'VOLTÍMETRO' if kind == 'V' else 'AMPERÍMETRO', int(h * 0.13), fill=(40, 30, 10))
        return l.done()
    return cached(key, mk)


# ---------------- barra de corriente (mA) ----------------
def current_bar(ma, top=30.0, line=20.0, h=360, w=110):
    key = ('cbar', round(ma, 1), top, line, h, w)
    def mk():
        l = D.L(w + 10, h + 70)
        x0, x1 = 30, w - 10
        y0, y1 = 10, h
        l.rrect([x0, y0, x1, y1], 10, fill=(20, 22, 28, 220), outline=(220, 220, 230, 255), width=3)
        fr = min(1.0, ma / top)
        col = (90, 220, 120) if ma <= line else (255, 70, 60)
        if fr > 0:
            l.rrect([x0 + 6, y1 - 6 - (y1 - y0 - 12) * fr, x1 - 6, y1 - 6], 6, fill=col + (255,))
        yl = y1 - 6 - (y1 - y0 - 12) * (line / top)
        l.line([(x0 - 14, yl), (x1 + 14, yl)], (255, 60, 60, 255), 5)
        l.text(((x0 + x1) / 2, y1 + 30), f'{ma:.0f} mA', 26, fill=(255, 255, 255))
        return l.done()
    return cached(key, mk)


def volt_stack(k_led=1.0, k_res=1.0, h=360, w=120):
    """barra apilada: 5 V = 2 V (LED) + 3 V (resistencia)"""
    key = ('vstack', round(k_led, 2), round(k_res, 2), h, w)
    def mk():
        l = D.L(w + 10, h + 70)
        x0, x1 = 20, w - 10
        y0, y1 = 10, h
        l.rrect([x0, y0, x1, y1], 10, fill=(20, 22, 28, 220), outline=(220, 220, 230, 255), width=3)
        inner = y1 - y0 - 12
        hl = inner * 2 / 5 * k_led
        hr = inner * 3 / 5 * k_res
        if hl > 1:
            l.rect([x0 + 6, y1 - 6 - hl, x1 - 6, y1 - 6], fill=(255, 80, 70, 255))
            l.text(((x0 + x1) / 2, y1 - 6 - hl / 2), '2 V', 26, fill=(255, 255, 255))
        if hr > 1:
            l.rect([x0 + 6, y1 - 6 - hl - hr, x1 - 6, y1 - 6 - hl], fill=(240, 160, 40, 255))
            l.text(((x0 + x1) / 2, y1 - 6 - hl - hr / 2), '3 V', 26, fill=(255, 255, 255))
        l.text(((x0 + x1) / 2, y1 + 30), '= 5 V', 26, fill=(255, 255, 255))
        return l.done()
    return cached(key, mk)


# ---------------- red de átomos (modelo simplificado) ----------------
LAT_W, LAT_H = 600, 470
def lattice(t, heat, flow=1.0, seed=3):
    """panel con átomos que vibran (más y más naranjas con 'heat') y electrones que pasan chocando"""
    l = D.L(LAT_W, LAT_H)
    l.rrect([4, 4, LAT_W - 4, LAT_H - 4], 26, fill=(28, 24, 22, 235), outline=(226, 204, 160, 255), width=6)
    nx, ny = 5, 3
    gx = (LAT_W - 160) / (nx - 1); gy = (LAT_H - 170) / (ny - 1)
    amp = 3 + 12 * heat
    cold = np.array((150, 156, 170)); hot = np.array((255, 130, 40))
    col = tuple(int(v) for v in cold * (1 - heat) + hot * heat)
    atoms = []
    for j in range(ny):
        for i in range(nx):
            ph = i * 1.7 + j * 2.3
            x = 80 + i * gx + amp * math.sin(t * 23 + ph)
            y = 85 + j * gy + amp * math.cos(t * 19 + ph * 1.3)
            atoms.append((x, y))
            if heat > 0.3:
                l.circle((x, y), 34, fill=(255, 140, 40, int(70 * (heat - 0.3))))
            l.circle((x, y), 25, fill=col + (255,), outline=(255, 255, 255, 160), width=3)
            l.text((x, y - 1), '+', 26, fill=(40, 30, 20))
    # electrones: van de izquierda a derecha en zigzag (rebotan en los átomos)
    rr = random.Random(seed)
    for k in range(9):
        y_lane = 85 + gy * rr.randint(0, ny - 2)
        sp = rr.uniform(0.18, 0.28)
        u = (t * sp * flow + k / 9) % 1.0
        x = 10 + u * (LAT_W - 20)
        # desviación cuando pasa cerca de un átomo
        y = y_lane + gy * 0.5 + 34 * math.sin(u * 19 + k)
        # choque: destello chiquito si está muy cerca de un átomo
        for ax, ay in atoms:
            if (ax - x) ** 2 + (ay - y) ** 2 < 36 ** 2 and flow > 0.2:
                l.circle(((ax + x) / 2, (ay + y) / 2), 10, fill=(255, 240, 150, 200))
                break
        l.circle((x, y), 17, fill=(70, 140, 255, 255), outline=(230, 240, 255, 255), width=3)
        l.text((x, y - 1), '−', 26, fill=(255, 255, 255))
    return l.done()


def thermometer(level, h=380):
    key = ('thermo', round(level, 2), h)
    def mk():
        w = 90
        l = D.L(w, h + 20)
        cx = w / 2
        l.rrect([cx - 18, 10, cx + 18, h - 50], 18, fill=(240, 244, 250, 255), outline=(120, 126, 138, 255), width=3)
        l.circle((cx, h - 40), 34, fill=(220, 40, 40, 255), outline=(120, 30, 30, 255), width=3)
        top = (h - 60) - (h - 90) * level
        l.rect([cx - 9, top, cx + 9, h - 50], fill=(220, 40, 40, 255))
        for k in range(6):
            y = 30 + k * (h - 100) / 5
            l.line([(cx + 18, y), (cx + 30, y)], (90, 96, 108, 255), 3)
        return l.done()
    return cached(key, mk)


# ---------------- tostadora (corte lateral) ----------------
TOA_W, TOA_H = 470, 360
def toaster(glow=0.0, toast=0.0):
    key = ('toast', round(glow, 2), round(toast, 2))
    def mk():
        l = D.L(TOA_W, TOA_H)
        # pan que asoma (se tuesta)
        bread = np.array((236, 200, 140)) * (1 - toast) + np.array((168, 104, 46)) * toast
        bc = tuple(int(v) for v in bread)
        for x in (150, 300):
            l.rrect([x - 62, 6, x + 62, 150], 30, fill=bc + (255,), outline=(120, 80, 40, 255), width=4)
        # carcasa cromada
        l.rrect([20, 70, TOA_W - 20, TOA_H - 26], 50, fill=(200, 206, 216, 255), outline=(110, 116, 128, 255), width=5)
        l.rrect([36, 84, 120, TOA_H - 50], 30, fill=(240, 244, 250, 120))
        # corte: ventana al interior
        l.rrect([70, 120, TOA_W - 70, TOA_H - 70], 20, fill=(30, 26, 26, 255), outline=(80, 80, 88, 255), width=4)
        # alambre en zigzag (nicromo) a los dos lados de cada pan
        hot = (60 + 195 * glow, 50 + 70 * glow, 50 - 20 * glow)
        hc = tuple(int(max(0, min(255, v))) for v in hot)
        for x in (110, 190, 260, 340):
            pts = []
            for k in range(11):
                y = 135 + k * (TOA_H - 220) / 10
                pts.append((x + (14 if k % 2 else -14), y))
            if glow > 0.2:
                l.line(pts, (255, 120, 30, int(120 * glow)), 16)
            l.line(pts, hc + (255,), 6)
        # pan dentro (sombra)
        for x in (150, 300):
            l.rrect([x - 22, 130, x + 22, TOA_H - 80], 8, fill=bc + (200,))
        # palanca
        l.rrect([TOA_W - 40, 150, TOA_W - 6, 180], 8, fill=(40, 40, 46, 255))
        # patas
        for x in (70, TOA_W - 70):
            l.rrect([x - 26, TOA_H - 30, x + 26, TOA_H - 6], 6, fill=(40, 40, 46, 255))
        return l.done()
    return cached(key, mk)


# ---------------- humo y chispa ----------------
def smoke(cv, x, y, u, a=1.0):
    """hilo de humo que sube (u = segundos desde el ¡pop!)"""
    if a <= 0.01:
        return
    l = Image.new('RGBA', (240, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    for k in range(14):
        v = k / 13
        yy = 400 - v * 380 * min(1, 0.4 + u)
        xx = 120 + 26 * math.sin(v * 5 + u * 3) * v
        r = 8 + 22 * v
        al = int(130 * a * (1 - v) * min(1, u * 4))
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(190, 190, 195, al))
    l = l.filter(ImageFilter.GaussianBlur(6))
    S._paste(cv, l, int(x - 120), int(y - 400))


def spark(cv, x, y, u):
    if not (0 <= u < 0.35):
        return
    k = 1 - u / 0.35
    l = D.L(260, 260)
    rr = random.Random(int(u * 60))
    for j in range(10):
        a = rr.uniform(0, 2 * math.pi)
        r0 = 10 + 60 * (1 - k); r1 = r0 + 40 + 50 * k
        l.line([(130 + r0 * math.cos(a), 130 + r0 * math.sin(a)), (130 + r1 * math.cos(a), 130 + r1 * math.sin(a))],
               (255, 230, 120, int(255 * k)), 6)
    S.paste_center(cv, l.done(), x, y)
    S.glow_fast(cv, x, y, 160, (255, 220, 120), 0.9 * k)


# ---------------- sello ----------------
def stamp(txt, size=40, col=(230, 40, 40)):
    key = ('stamp', txt, size, col)
    def mk():
        f = S.font(size)
        w, h, b = S.text_size(txt, f)
        l = D.L(w + 60, size + 50)
        l.rrect([8, 8, w + 52, size + 42], 10, fill=(255, 255, 255, 40), outline=col + (255,), width=6)
        l.text(((w + 60) / 2, (size + 50) / 2), txt, size, fill=col)
        return l.done()
    return cached(key, mk)


def strike(txt, size=30):
    """texto tachado ('consume corriente')"""
    f = S.font(size)
    w, h, b = S.text_size(txt, f)
    l = D.L(w + 30, size + 30)
    l.text(((w + 30) / 2, (size + 30) / 2), txt, size, fill=(220, 220, 230))
    l.line([(6, (size + 30) / 2), (w + 24, (size + 30) / 2)], (255, 60, 60, 255), 6)
    return l.done()


# ---------------- celular por dentro con resistencias de chip ----------------
PCB_W, PCB_H = 600, 470
def pcb_panel(t):
    def mk():
        rng = random.Random(9)
        l = D.L(PCB_W, PCB_H)
        l.rrect([4, 4, PCB_W - 4, PCB_H - 4], 26, fill=(18, 92, 58, 255), outline=(10, 50, 30, 255), width=6)
        for k in range(14):
            y = rng.randint(30, PCB_H - 30)
            l.line([(20, y), (PCB_W - 20, y)], (196, 132, 58, 160), 4)
        for k in range(8):
            x = rng.randint(30, PCB_W - 30)
            l.line([(x, 20), (x, PCB_H - 20)], (196, 132, 58, 140), 4)
        # chips grandes
        for (x, y, w, h, lab) in ((60, 60, 170, 120, 'SoC'), (330, 280, 180, 120, 'PMIC')):
            l.rrect([x, y, x + w, y + h], 6, fill=(26, 26, 30, 255), outline=(60, 60, 66, 255), width=3)
            l.text((x + w / 2, y + h / 2), lab, 24, fill=(150, 150, 160))
        # pasivos diminutos (resistencias negras con tapas plateadas y condensadores beige)
        pts = []
        for k in range(60):
            x = rng.randint(30, PCB_W - 50); y = rng.randint(30, PCB_H - 40)
            if 50 < x < 240 and 50 < y < 190 or 320 < x < 520 and 270 < y < 410:
                continue
            res = rng.random() < 0.5
            w, h = 22, 12
            if rng.random() < 0.5:
                w, h = h, w
            l.rect([x, y, x + w, y + h], fill=((30, 30, 32) if res else (200, 160, 110)) + (255,))
            if w > h:
                l.rect([x, y, x + 5, y + h], fill=(215, 218, 224, 255)); l.rect([x + w - 5, y, x + w, y + h], fill=(215, 218, 224, 255))
            else:
                l.rect([x, y, x + w, y + 5], fill=(215, 218, 224, 255)); l.rect([x, y + h - 5, x + w, y + h], fill=(215, 218, 224, 255))
        return l.done()
    return cached('pcb', mk)


def smd_resistor(w=300):
    """resistencia de chip vista de cerca (cuerpo negro, tapas plateadas, código impreso)"""
    def mk():
        h = int(w * 0.5)
        l = D.L(w + 20, h + 40)
        l.rrect([10, 20, w + 10, h + 20], 8, fill=(22, 22, 24, 255))
        l.rrect([10, 20, 10 + w * 0.2, h + 20], 8, fill=(205, 210, 218, 255))
        l.rrect([w + 10 - w * 0.2, 20, w + 10, h + 20], 8, fill=(205, 210, 218, 255))
        l.rect([10 + w * 0.2, 20, w + 10 - w * 0.2, 30], fill=(60, 60, 64, 255))
        return l.done()
    return cached(('smd', w), mk)
