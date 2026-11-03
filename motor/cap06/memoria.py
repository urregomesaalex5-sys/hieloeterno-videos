# Dibujos del capítulo 6: la memoria del celular.
# Todo sale de la tabla de verificación (VERIFICACION.md): los rótulos solo dicen lo que está ahí.
import math
import random
from PIL import Image, ImageDraw
import scene as S
import diagrams as D
from diagrams import L

_cache = {}
def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]

ELEC = (70, 150, 255)
ELEC_EDGE = (200, 230, 255)
OXIDE = (150, 205, 235)
TRAP = (226, 168, 84)
GATE = (150, 156, 168)
SILI = (110, 100, 140)
NPLUS = (80, 70, 120)


# ---------------- celular gigante (intro) ----------------
PH_W, PH_H = 400, 780

def phone_big(on=0.0, flip=0.0):
    key = ('ph', round(on, 2))
    def mk():
        l = L(PH_W + 40, PH_H + 20)
        l.rrect([24, 6, PH_W + 24, PH_H + 6], 58, fill=(22, 24, 30, 255), outline=(90, 96, 110, 255), width=6)
        # botón de encendido (lado derecho)
        l.rrect([PH_W + 22, 190, PH_W + 36, 280], 6, fill=(120, 126, 140, 255))
        # pantalla
        sx0, sy0, sx1, sy1 = 46, 40, PH_W + 2, PH_H - 30
        if on <= 0.01:
            l.rrect([sx0, sy0, sx1, sy1], 40, fill=(8, 9, 12, 255))
        else:
            k = on
            l.rrect([sx0, sy0, sx1, sy1], 40, fill=(int(25 + 30 * k), int(28 + 34 * k), int(40 + 50 * k), 255))
            # galería: cuadrícula de fotos de colores
            rng = random.Random(7)
            cols = [(255, 170, 90), (110, 200, 255), (130, 220, 140), (255, 120, 150), (200, 160, 255), (255, 220, 110)]
            gw = (sx1 - sx0 - 40) / 3
            for r in range(6):
                for c in range(3):
                    x = sx0 + 16 + c * (gw + 4); y = sy0 + 70 + r * (gw + 4)
                    if y + gw > sy1 - 20:
                        continue
                    col = cols[rng.randrange(len(cols))]
                    a = int(255 * k)
                    l.rect([x, y, x + gw, y + gw], fill=col + (a,))
                    l.poly([(x, y + gw), (x + gw * 0.45, y + gw * 0.45), (x + gw * 0.8, y + gw)], fill=(40, 90, 60, a))
                    l.circle((x + gw * 0.75, y + gw * 0.28), gw * 0.1, fill=(255, 250, 220, a))
            l.text(((sx0 + sx1) / 2, sy0 + 36), 'Galería', 30, fill=(255, 255, 255, int(255 * k)))
        # puerto de carga (abajo)
        l.rrect([PH_W / 2 + 24 - 34, PH_H - 4, PH_W / 2 + 24 + 34, PH_H + 8], 6, fill=(5, 5, 8, 255), outline=(120, 126, 140, 255), width=3)
        return l.done()
    return cached(key, mk)


def photo_card(back=False, size=210):
    key = ('photo', back, size)
    def mk():
        l = L(size + 20, size + 40)
        if not back:
            l.rrect([10, 10, size + 10, size + 30], 10, fill=(255, 255, 255, 255))
            l.rect([22, 22, size - 2, size - 2], fill=(110, 190, 250, 255))
            l.poly([(22, size - 2), (size * 0.45, size * 0.45), (size * 0.8, size - 2)], fill=(60, 150, 90, 255))
            l.poly([(size * 0.5, size - 2), (size * 0.72, size * 0.6), (size - 2, size - 2)], fill=(40, 120, 70, 255))
            l.circle((size * 0.75, size * 0.3), size * 0.08, fill=(255, 240, 150, 255))
        else:
            l.rrect([10, 10, size + 10, size + 30], 10, fill=(225, 225, 230, 255))
            l.text((size / 2 + 10, size / 2 + 20), '?', 110, fill=(150, 150, 160, 255), black=True)
        return l.done()
    return cached(key, mk)


def comment_shot(path, width=900):
    """captura real del comentario, en un marco redondeado"""
    key = ('shot', path, width)
    def mk():
        im = Image.open(path).convert('RGBA')
        k = (width - 40) / im.size[0]
        im = im.resize((int(im.size[0] * k), int(im.size[1] * k)), Image.LANCZOS)
        w, h = im.size
        l = L(w + 40, h + 40)
        l.rrect([4, 4, w + 36, h + 36], 24, fill=(15, 15, 15, 255), outline=(255, 255, 255, 230), width=4)
        out = l.done()
        out.alpha_composite(im, (20, 20))
        return out
    return cached(key, mk)


# ---------------- escritorio (RAM) y archivero (almacenamiento) ----------------
def desk_img(papers=1.0):
    key = ('desk', round(papers, 1))
    def mk():
        l = L(330, 260)
        l.rect([20, 90, 310, 116], fill=(170, 110, 60, 255), outline=(110, 68, 34, 255), width=4)
        l.rect([36, 116, 62, 250], fill=(140, 88, 46, 255))
        l.rect([268, 116, 294, 250], fill=(140, 88, 46, 255))
        rng = random.Random(3)
        n = int(round(5 * papers))
        for k in range(n):
            x = 50 + k * 48 + rng.uniform(-6, 6); y = 50 + rng.uniform(-8, 8)
            l.poly([(x, y), (x + 58, y - 6), (x + 64, y + 38), (x + 6, y + 44)], fill=(250, 250, 245, 255), outline=(160, 160, 170, 255), width=2)
            l.line([(x + 12, y + 12), (x + 50, y + 8)], (120, 140, 200, 255), 3)
            l.line([(x + 14, y + 24), (x + 52, y + 20)], (120, 140, 200, 255), 3)
        return l.done()
    return cached(key, mk)


def cabinet_img():
    def mk():
        l = L(230, 330)
        l.rrect([20, 10, 210, 320], 10, fill=(120, 128, 140, 255), outline=(70, 76, 88, 255), width=5)
        for k in range(4):
            y = 24 + k * 73
            l.rrect([34, y, 196, y + 62], 6, fill=(150, 158, 170, 255), outline=(90, 96, 108, 255), width=3)
            l.rrect([90, y + 24, 140, y + 36], 4, fill=(70, 76, 88, 255))
            l.rect([60, y + 8, 110, y + 18], fill=(250, 250, 245, 255))
        return l.done()
    return cached('cab', mk)


# ---------------- chip con cuadrícula de celdas ----------------
def chip_grid(hi=0.0, n=12):
    key = ('grid', round(hi, 2), n)
    def mk():
        sz = 470
        l = L(sz + 40, sz + 40)
        for x in range(40, sz, 30):
            l.rect([x, 2, x + 12, 22], fill=(200, 205, 212, 255))
            l.rect([x, sz + 18, x + 12, sz + 38], fill=(200, 205, 212, 255))
            l.rect([2, x, 22, x + 12], fill=(200, 205, 212, 255))
            l.rect([sz + 18, x, sz + 38, x + 12], fill=(200, 205, 212, 255))
        l.rrect([20, 20, sz + 20, sz + 20], 12, fill=(26, 26, 32, 255), outline=(70, 70, 80, 255), width=4)
        g = (sz - 40) / n
        for i in range(n):
            for j in range(n):
                x = 40 + i * g; y = 40 + j * g
                c = (60, 120, 90, 255) if (i + j) % 3 else (70, 140, 105, 255)
                if i == n // 2 and j == n // 2 and hi > 0:
                    c = (int(60 + 195 * hi), int(120 + 110 * hi), int(90 - 20 * hi), 255)
                l.rect([x + 2, y + 2, x + g - 2, y + g - 2], fill=c)
        return l.done()
    return cached(key, mk)


# ---------------- celda flash en corte ----------------
CW, CH_ = 560, 400
BANDS = [  # (y0, y1, color, texto)
    ('gate', 20, 95, GATE, 'COMPUERTA'),
    ('box', 95, 160, OXIDE, 'AISLANTE'),
    ('trap', 160, 210, TRAP, 'AQUÍ SE GUARDA LA CARGA'),
    ('tox', 210, 226, OXIDE, ''),
    ('si', 226, 340, SILI, 'SILICIO'),
]
CELL_X0, CELL_X1 = 30, 530

def cell_layer(build=1.0, labels=True, crack=0.0):
    key = ('cell', round(build, 2), labels, round(crack, 1))
    def mk():
        l = L(CW, CH_)
        nb = len(BANDS)
        for k, (name, y0, y1, col, txt) in enumerate(reversed(BANDS)):
            a = S.clamp(build * nb - k)
            if a <= 0:
                continue
            al = int(255 * a)
            l.rect([CELL_X0, y0, CELL_X1, y1], fill=col + (al,), outline=(20, 22, 28, al), width=3)
            if name == 'si':
                l.rect([CELL_X0, y0, CELL_X0 + 110, y0 + 52], fill=NPLUS + (al,))
                l.rect([CELL_X1 - 110, y0, CELL_X1, y0 + 52], fill=NPLUS + (al,))
            if labels and txt:
                if name == 'trap':
                    l.text((CELL_X0 + 14, (y0 + y1) / 2), 'CARGA', 22, fill=(20, 22, 30, al), anchor='lm')
                else:
                    l.text(((CELL_X0 + CELL_X1) / 2, (y0 + y1) / 2), txt, 26,
                           fill=(20, 22, 30, al) if name != 'si' else (240, 240, 250, al))
        if crack > 0:
            rnd = random.Random(2)
            for k in range(int(6 * crack)):
                x = rnd.uniform(CELL_X0 + 40, CELL_X1 - 40)
                l.line([(x, 211), (x + 8, 218), (x - 4, 225)], (40, 30, 30, 255), 3)
        return l.done()
    return cached(key, mk)

def band_y(name):
    for b in BANDS:
        if b[0] == name:
            return b[1], b[2]


def electron(r=15):
    def mk():
        l = L(2 * r + 6, 2 * r + 6)
        l.circle((r + 3, r + 3), r, fill=ELEC + (255,), outline=ELEC_EDGE + (255,), width=3)
        l.line([(r + 3 - r * 0.45, r + 3), (r + 3 + r * 0.45, r + 3)], (255, 255, 255, 255), 4)
        return l.done()
    return cached(('e', r), mk)


# ---------------- bomba de carga y voltímetro ----------------
def volt_meter(v):
    key = ('vm', int(round(v)))
    def mk():
        l = L(230, 130)
        l.rrect([6, 6, 224, 124], 16, fill=(30, 34, 42, 255), outline=(200, 205, 212, 255), width=4)
        l.rrect([24, 24, 206, 90], 8, fill=(140, 190, 120, 255))
        l.text((115, 58), f'{int(round(v))} V', 44, fill=(20, 40, 20, 255), black=True)
        l.text((115, 106), 'VOLTÍMETRO', 18, fill=(200, 205, 212, 255))
        return l.done()
    return cached(key, mk)

def pump_img(level=1.0):
    """escalera de condensadores (bomba de carga) que se va 'llenando' escalón por escalón"""
    key = ('pump', round(level, 2))
    def mk():
        l = L(250, 330)
        for k in range(5):
            x = 20 + k * 38; y = 280 - k * 58
            on = S.clamp(level * 5 - k)
            col = (int(90 + 165 * on), int(90 + 140 * on), int(110 - 30 * on), 255)
            l.rect([x, y, x + 70, y + 14], fill=col)
            l.rect([x, y + 24, x + 70, y + 38], fill=col)
            if k < 4:
                l.line([(x + 70, y + 31), (x + 70 + 18, y - 20)], (220, 220, 230, 255), 4)
        l.text((125, 316), 'BOMBA DE CARGA', 20, fill=(255, 230, 140, 255))
        return l.done()
    return cached(key, mk)


# ---------------- comparación: saltar vs atravesar ----------------
def tunnel_panel(ok, u):
    """ok=False: el electrón intenta saltar por encima (no puede). ok=True: pasa A TRAVÉS de la pared intacta."""
    l = L(300, 300)
    l.rrect([4, 4, 296, 296], 18, fill=(20, 22, 30, 220), outline=(255, 255, 255, 120), width=3)
    l.rect([140, 60 if not ok else 70, 160 if not ok else 150, 250], fill=OXIDE + (255,))
    ex = 40 + 220 * u
    if not ok:
        ey = 200 - 110 * math.sin(min(1, u * 2) * math.pi) if u < 0.5 else 200
        ex = 40 + 180 * min(u, 0.42)
        if u >= 0.5:
            ex = 115 - 70 * (u - 0.5)
    else:
        ey = 200
    a = 120 if (ok and 140 < ex < 160) else 255
    l.circle((ex, ey), 16, fill=ELEC + (a,), outline=ELEC_EDGE + (a,), width=3)
    l.text((150, 278), 'ATRAVIESA ✓' if ok else 'SALTA ✗', 28, fill=(130, 240, 150, 255) if ok else (255, 120, 120, 255))
    l.text((150, 34), 'PARED INTACTA' if ok else 'NO PUEDE', 22, fill=(230, 230, 240, 255))
    return l.done()


# ---------------- lectura: voltaje umbral ----------------
def mini_cell(charged, bit_alpha=1.0):
    key = ('mc', charged, round(bit_alpha, 1))
    def mk():
        l = L(220, 260)
        l.rect([20, 30, 200, 70], fill=GATE + (255,))
        l.rect([20, 70, 200, 92], fill=OXIDE + (255,))
        l.rect([20, 92, 200, 116], fill=TRAP + (255,))
        l.rect([20, 116, 200, 122], fill=OXIDE + (255,))
        l.rect([20, 122, 200, 170], fill=SILI + (255,))
        if charged:
            for k in range(5):
                x = 40 + k * 34
                l.circle((x, 104), 9, fill=ELEC + (255,), outline=ELEC_EDGE + (255,), width=2)
        a = int(255 * bit_alpha)
        l.text((110, 220), '0' if charged else '1', 64, fill=(255, 230, 120, a), black=True, stroke=3, stroke_fill=(60, 30, 0, a))
        return l.done()
    return cached(key, mk)

def gauge(v):
    """medidor: a qué voltaje empieza a conducir (aguja de 0 a 1)"""
    l = L(260, 160)
    l.rrect([6, 6, 254, 154], 16, fill=(30, 34, 42, 255), outline=(200, 205, 212, 255), width=3)
    cx, cy, r = 130, 130, 92
    for k in range(11):
        a = math.pi * (1 - k / 10)
        l.line([(cx + (r - 14) * math.cos(a), cy - (r - 14) * math.sin(a)), (cx + r * math.cos(a), cy - r * math.sin(a))], (220, 220, 230, 255), 3)
    a = math.pi * (1 - v)
    l.line([(cx, cy), (cx + (r - 8) * math.cos(a), cy - (r - 8) * math.sin(a))], (255, 90, 90, 255), 6)
    l.circle((cx, cy), 9, fill=(255, 90, 90, 255))
    l.text((130, 24), 'VOLTAJE UMBRAL', 18, fill=(255, 230, 140, 255))
    return l.done()


# ---------------- vaso con 8 niveles ----------------
def glass(level):
    """level: 0..7 (8 niveles = 3 bits). Llenado por escalones."""
    key = ('glass', round(level, 2))
    def mk():
        l = L(300, 470)
        x0, x1, y0, y1 = 60, 220, 30, 430
        hh = (y1 - y0 - 20) / 7
        top = y1 - 10 - level * hh
        l.rect([x0 + 6, top, x1 - 6, y1 - 6], fill=(80, 150, 255, 170))
        for k in range(8):
            y = y1 - 10 - k * hh
            l.line([(x1 - 40, y), (x1 + 4, y)], (255, 255, 255, 255), 3)
            bits = format(k, '03b')
            l.text((x1 + 44, y), bits, 20, fill=(255, 230, 140, 255) if abs(level - k) < 0.3 else (210, 210, 220, 200))
        l.line([(x0, y0), (x0, y1), (x1, y1), (x1, y0)], (230, 240, 255, 255), 6)
        return l.done()
    return cached(key, mk)


# ---------------- bloque y borrador ----------------
def block_grid(erased=0.0, sweep=None, n=8):
    key = ('blk', round(erased, 2), None if sweep is None else round(sweep, 2), n)
    def mk():
        sz = 420
        l = L(sz + 20, sz + 20)
        l.rrect([4, 4, sz + 16, sz + 16], 14, fill=(26, 26, 32, 230), outline=(255, 210, 120, 255), width=4)
        g = (sz - 30) / n
        for i in range(n):
            for j in range(n):
                x = 25 + i * g; y = 25 + j * g
                cleared = sweep is not None and x < 25 + sweep * (sz - 30)
                rnd = (i * 7 + j * 3) % 4
                if cleared or erased >= 1:
                    c = (60, 70, 80, 255)
                else:
                    c = [(70, 150, 255, 255), (60, 120, 210, 255), (90, 170, 255, 255), (50, 100, 190, 255)][rnd]
                l.rect([x + 3, y + 3, x + g - 3, y + g - 3], fill=c)
        return l.done()
    return cached(key, mk)

def eraser(size=1.0):
    key = ('er', round(size, 2))
    def mk():
        w, h = int(120 * size), int(60 * size)
        l = L(w + 20, h + 20)
        l.rrect([10, 10, w * 0.62 + 10, h + 10], 8, fill=(240, 120, 150, 255), outline=(150, 60, 80, 255), width=3)
        l.rrect([w * 0.62 + 10, 10, w + 10, h + 10], 8, fill=(80, 120, 220, 255), outline=(40, 60, 140, 255), width=3)
        return l.done()
    return cached(key, mk)


# ---------------- RAM: transistor + condensador ----------------
def dram_cell(q=1.0, bit=True):
    key = ('dc', round(q, 2), bit)
    def mk():
        l = L(480, 330)
        # transistor (interruptor)
        l.rrect([20, 120, 170, 210], 14, fill=(60, 64, 76, 255), outline=(200, 205, 212, 255), width=4)
        l.text((95, 165), 'TRANSISTOR', 22, fill=(255, 255, 255, 255))
        l.line([(170, 165), (250, 165)], (220, 220, 230, 255), 6)
        # condensador: dos placas con aislante; la carga se ve como electrones en una placa
        l.rect([250, 70, 270, 260], fill=(200, 205, 212, 255))
        l.rect([330, 70, 350, 260], fill=(200, 205, 212, 255))
        l.rect([270, 70, 330, 260], fill=OXIDE + (140,))
        n = int(round(q * 7))
        for k in range(n):
            l.circle((260, 82 + k * 25), 10, fill=ELEC + (255,), outline=ELEC_EDGE + (255,), width=2)
        l.text((300, 290), 'CONDENSADOR', 22, fill=(255, 230, 140, 255))
        l.text((300, 40), 'unos pocos fF', 20, fill=(210, 210, 220, 255))
        if bit:
            l.text((420, 165), '1' if q > 0.5 else '0', 72, fill=(255, 230, 120, 255), black=True, stroke=3, stroke_fill=(60, 30, 0, 255))
        return l.done()
    return cached(key, mk)

def cap_cell(q, size=56):
    """mini condensador para la cuadrícula de RAM: barra que se llena"""
    key = ('cc', round(q, 2), size)
    def mk():
        l = L(size, size + 6)
        l.rrect([4, 4, size - 4, size + 2], 8, fill=(30, 34, 42, 255), outline=(150, 156, 170, 255), width=3)
        h = (size - 14) * q
        l.rect([12, size - 4 - h, size - 12, size - 4], fill=(int(70 + 150 * (1 - q)), int(150 + 60 * q), 255, 255))
        return l.done()
    return cached(key, mk)


def race_bar(label, frac, col, txt):
    l = L(620, 110)
    l.text((10, 26), label, 30, fill=(255, 255, 255, 255), anchor='lm')
    l.rrect([10, 52, 610, 96], 12, fill=(30, 34, 42, 230), outline=(200, 205, 212, 255), width=3)
    if frac > 0:
        l.rrect([14, 56, 14 + 592 * frac, 92], 10, fill=col + (255,))
    l.text((600, 26), txt, 24, fill=(255, 230, 140, 255), anchor='rm')
    return l.done()


def mystery_box(t=0.0):
    l = L(240, 240)
    l.rrect([20, 20, 220, 220], 22, fill=(60, 50, 110, 255), outline=(255, 220, 120, 255), width=6)
    l.text((120, 120), '?', 130, fill=(255, 230, 120, 255), black=True)
    return l.done()
