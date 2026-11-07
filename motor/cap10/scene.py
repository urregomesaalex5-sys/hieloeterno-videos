# Escenario: cuarto de bloques, lámpara, luz, textos y utilidades de animación.
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H = 1080, 1920
FPS = 30
ROOM_T = 200          # arriba del cuarto (debajo queda la franja negra con la lámpara)
FLOOR_Y = 1392        # donde pisan los pies
FLOOR_T = 1380        # borde superior del piso de madera
FLOOR_B = 1470        # borde inferior del piso
BLK = 72              # tamaño de bloque en pantalla
NCOL = W // BLK + 1
SUB_Y = 1560          # subtítulos
LAMP_X, LAMP_Y = 540, 150
SCALE = 17            # px por unidad de skin

FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_BLACK = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'

_fonts = {}
def font(size, black=False):
    key = (size, black)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_BLACK if black else FONT_B, size)
    return _fonts[key]

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def ease_out(t):
    t = clamp(t); return 1 - (1 - t) ** 3

def ease_in(t):
    t = clamp(t); return t ** 3

def ease_io(t):
    t = clamp(t); return t * t * (3 - 2 * t)

def ease_back(t, s=1.7):
    t = clamp(t) - 1; return 1 + t * t * ((s + 1) * t + s)

def elastic(t):
    t = clamp(t)
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t - 0.075) * (2 * math.pi) / 0.3) + 1

def bounce_out(t):
    t = clamp(t)
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1; return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1; return n1 * t * t + 0.9375
    t -= 2.625 / d1; return n1 * t * t + 0.984375

def seg(t, a, b):
    """progreso 0..1 de t entre a y b"""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))

def jelly(t, freq=3.0, decay=4.0):
    """rebote gelatinoso amortiguado (empieza en 1, termina en 0)"""
    if t < 0:
        return 0.0
    return math.exp(-decay * t) * math.cos(2 * math.pi * freq * t)

# ---------- texturas de bloques ----------
def _noise_block(rng, base, var, n=16, px=BLK, edge=0.75, crack=True):
    tp = px / n
    arr = np.zeros((n, n, 3), np.float32)
    for y in range(n):
        for x in range(n):
            v = base + rng.uniform(-var, var)
            arr[y, x] = v
    if crack:
        arr[0, :] *= 1.08; arr[:, 0] *= 1.06
        arr[n - 1, :] *= edge; arr[:, n - 1] *= edge
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').resize((px, px), Image.NEAREST)
    return im

def make_stone(rng):
    # piedra azul-grisácea como en los capítulos anteriores
    base = np.array([74, 80, 92])
    b = _noise_block(rng, base, 14)
    return b

def make_wood(rng):
    n = 16
    arr = np.zeros((n, n, 3), np.float32)
    base = np.array([150, 98, 52], np.float32)
    for y in range(n):
        row = 1.0 + rng.uniform(-0.05, 0.05)
        for x in range(n):
            arr[y, x] = base * row * (1 + rng.uniform(-0.07, 0.07))
        if y % 4 == 3:
            arr[y, :] *= 0.72
    for k in range(3):
        y = rng.randrange(n); x = rng.randrange(n)
        arr[y, x] *= 0.6
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').resize((BLK, BLK), Image.NEAREST)

_rng = random.Random(7)
STONES = [make_stone(_rng) for _ in range(8)]
WOODS = [make_wood(_rng) for _ in range(5)]

# rejilla del cuarto: columnas y filas de bloques de pared
X0 = (W - NCOL * BLK) // 2
WALL_ROWS = list(range(ROOM_T, FLOOR_T, BLK))  # y de cada fila

def wall_tiles():
    """lista de (img, x, y) de la pared"""
    tiles = []
    r = random.Random(3)
    for ri, y in enumerate(WALL_ROWS):
        for c in range(NCOL):
            tiles.append((STONES[r.randrange(len(STONES))], X0 + c * BLK, y))
    return tiles

def floor_tiles():
    tiles = []
    r = random.Random(5)
    for c in range(NCOL):
        tiles.append((WOODS[r.randrange(len(WOODS))], X0 + c * BLK, FLOOR_T))
    return tiles

WALL = wall_tiles()
FLOOR = floor_tiles()

def room_raw():
    im = Image.new('RGB', (W, H), (0, 0, 0))
    for t, x, y in WALL:
        im.paste(t, (x, y))
    for t, x, y in FLOOR:
        im.paste(t.crop((0, 0, BLK, FLOOR_B - FLOOR_T)), (x, y))
    # recortar arriba (franja negra)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, ROOM_T - 1], fill=(0, 0, 0))
    d.rectangle([0, FLOOR_B, W, H], fill=(0, 0, 0))
    return im

# ---------- luz de la lámpara ----------
def light_mask():
    """multiplicador de luz (H,W) float: cono de luz desde la lámpara."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dy = np.maximum(yy - LAMP_Y, 1)
    half = 60 + (dy) * 0.36   # ancho del cono
    dx = np.abs(xx - LAMP_X)
    inside = np.clip(1.0 - (dx - half) / 140.0, 0, 1)
    fall = np.clip(1.15 - dy / 2600.0, 0, 1)
    m = 0.30 + 0.75 * inside * fall
    # un poco de viñeta
    vx = (xx - W / 2) / (W / 2)
    m *= 1.0 - 0.18 * vx ** 2
    return np.clip(m, 0, 1.15)

LIGHT = light_mask()

def lit_room():
    raw = np.array(room_raw(), np.float32)
    out = raw * LIGHT[..., None]
    # el cono también ilumina un poco el aire (haz)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dy = np.maximum(yy - LAMP_Y, 1)
    half = 60 + dy * 0.36
    beam = np.clip(1.0 - np.abs(xx - LAMP_X) / half, 0, 1) ** 1.5 * np.clip(1 - dy / 1600, 0, 1) * 18
    beam[yy < ROOM_T] *= 0.0
    out += beam[..., None] * np.array([1.0, 0.95, 0.8])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGB')

def draw_lamp(img, on=1.0, swing=0.0, y_off=0.0, cord=True, x=None):
    """lámpara colgante. swing en radianes."""
    d = ImageDraw.Draw(img)
    lx = LAMP_X if x is None else x
    ly = LAMP_Y + y_off
    ex = lx + math.sin(swing) * (ly)
    ey = math.cos(swing) * ly
    if cord:
        d.line([(lx, 0), (ex, ey)], fill=(70, 70, 70), width=3)
    # pantalla (trapecio)
    ang = swing
    def R(px, py):
        return (ex + px * math.cos(ang) - py * math.sin(ang), ey + px * math.sin(ang) + py * math.cos(ang))
    shade = [R(-16, 0), R(16, 0), R(26, 18), R(-26, 18)]
    d.polygon(shade, fill=(55, 55, 58))
    d.line([R(-16, 0), R(16, 0)], fill=(90, 90, 92), width=2)
    bulb = R(0, 22)
    if on > 0.01:
        c = (int(150 + 105 * on), int(140 + 100 * on), int(90 + 70 * on))
        d.ellipse([bulb[0] - 9, bulb[1] - 7, bulb[0] + 9, bulb[1] + 7], fill=c)
    else:
        d.ellipse([bulb[0] - 9, bulb[1] - 7, bulb[0] + 9, bulb[1] + 7], fill=(80, 78, 70))
    return (ex, ey)

# ---------- texto ----------
def text_size(txt, f):
    b = f.getbbox(txt)
    return b[2] - b[0], b[3] - b[1], b

def draw_outlined(img, xy, txt, f, fill=(255, 255, 255), outline=(0, 0, 0), ow=5, anchor='mm', shadow=True):
    d = ImageDraw.Draw(img)
    if shadow:
        d.text((xy[0] + 4, xy[1] + 6), txt, font=f, fill=(0, 0, 0, 160), anchor=anchor, stroke_width=ow, stroke_fill=(0, 0, 0, 160))
    d.text(xy, txt, font=f, fill=fill, anchor=anchor, stroke_width=ow, stroke_fill=outline)

def fancy_text(txt, size, top=(255, 214, 80), bot=(255, 120, 30), outline=(70, 25, 5), ow=8, black=True):
    """Letras decoradas con degradado, contorno y sombra. Devuelve RGBA recortada."""
    f = font(size, black)
    w, h, b = text_size(txt, f)
    pad = ow + 24
    Wt, Ht = w + 2 * pad, h + 2 * pad + 10
    base = Image.new('RGBA', (Wt, Ht), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    org = (pad - b[0], pad - b[1])
    # sombra
    sh = Image.new('RGBA', (Wt, Ht), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((org[0] + 5, org[1] + 9), txt, font=f, fill=(0, 0, 0, 200), stroke_width=ow, stroke_fill=(0, 0, 0, 200))
    sh = sh.filter(ImageFilter.GaussianBlur(3))
    base.alpha_composite(sh)
    d.text(org, txt, font=f, fill=outline + (255,), stroke_width=ow, stroke_fill=outline + (255,))
    # relleno con degradado
    mask = Image.new('L', (Wt, Ht), 0)
    ImageDraw.Draw(mask).text(org, txt, font=f, fill=255)
    grad = np.zeros((Ht, Wt, 4), np.uint8)
    y0, y1 = pad, pad + h
    for y in range(Ht):
        k = clamp((y - y0) / max(1, (y1 - y0)))
        grad[y, :, :3] = [int(top[i] + (bot[i] - top[i]) * k) for i in range(3)]
        grad[y, :, 3] = 255
    g = Image.fromarray(grad, 'RGBA')
    base.paste(g, (0, 0), mask)
    # brillo arriba
    hl = Image.new('L', (Wt, Ht), 0)
    ImageDraw.Draw(hl).text((org[0], org[1] - 3), txt, font=f, fill=90)
    hl = ImageChops.multiply(hl, mask)
    hlm = np.array(hl, np.float32)
    hlm[int(pad + h * 0.45):, :] = 0
    white = Image.new('RGBA', (Wt, Ht), (255, 255, 255, 255))
    base.paste(white, (0, 0), Image.fromarray(hlm.astype(np.uint8)))
    return base

def wrap_lines(txt, f, maxw):
    words = txt.split()
    lines = []; cur = ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if text_size(t, f)[0] <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def draw_subtitle(img, txt, alpha=1.0, y=SUB_Y, size=48):
    if not txt or alpha <= 0:
        return
    f = font(size)
    lines = wrap_lines(txt, f, 960)
    layer = Image.new('RGBA', (W, 300), (0, 0, 0, 0))
    lh = size + 14
    for i, ln in enumerate(lines):
        draw_outlined(layer, (W // 2, 40 + i * lh), ln, f, ow=6)
    if alpha < 1:
        a = np.array(layer); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); layer = Image.fromarray(a)
    img.alpha_composite(layer, (0, y - 40))

def draw_label(img, txt, alpha=1.0):
    f = font(30)
    layer = Image.new('RGBA', (W, 80), (0, 0, 0, 0))
    draw_outlined(layer, (W // 2, 40), txt, f, fill=(255, 185, 70), outline=(60, 25, 0), ow=4, shadow=False)
    if alpha < 1:
        a = np.array(layer); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); layer = Image.fromarray(a)
    img.alpha_composite(layer, (0, ROOM_T + 6))

# ---------- utilidades de imagen ----------
def with_alpha(im, a):
    if a >= 0.999:
        return im
    arr = np.array(im)
    arr[..., 3] = (arr[..., 3].astype(np.float32) * max(0.0, a)).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')

def paste_center(canvas, im, cx, cy, scale=1.0, sx=None, sy=None, angle=0.0, alpha=1.0):
    if im is None or alpha <= 0.003:
        return
    sx = scale if sx is None else sx * scale
    sy = scale if sy is None else sy * scale
    w, h = im.size
    nw, nh = max(1, int(w * sx)), max(1, int(h * sy))
    t = im if (nw, nh) == (w, h) else im.resize((nw, nh), Image.BICUBIC)
    if abs(angle) > 0.001:
        t = t.rotate(math.degrees(angle), resample=Image.BICUBIC, expand=True)
    t = with_alpha(t, alpha)
    x = int(round(cx - t.size[0] / 2)); y = int(round(cy - t.size[1] / 2))
    _paste(canvas, t, x, y)

def _paste(canvas, img, x, y):
    Wc, Hc = canvas.size
    cx0 = max(0, -x); cy0 = max(0, -y)
    cx1 = min(img.size[0], Wc - x); cy1 = min(img.size[1], Hc - y)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    if (cx0, cy0, cx1, cy1) == (0, 0) + img.size:
        canvas.alpha_composite(img, (x, y))
    else:
        canvas.alpha_composite(img.crop((cx0, cy0, cx1, cy1)), (x + cx0, y + cy0))

def glow(canvas, cx, cy, r, color, strength=1.0):
    """brillo aditivo radial"""
    if strength <= 0.01:
        return
    r = int(r)
    size = 2 * r
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    dd = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r
    g = np.clip(1 - dd, 0, 1) ** 2 * strength
    x0, y0 = int(cx - r), int(cy - r)
    arr = np.array(canvas)
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(W, x0 + size), min(arr.shape[0], y0 + size)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    gg = g[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0]
    reg = arr[sy0:sy1, sx0:sx1, :3].astype(np.float32)
    reg += gg[..., None] * np.array(color, np.float32)
    arr[sy0:sy1, sx0:sx1, :3] = np.clip(reg, 0, 255).astype(np.uint8)
    canvas.paste(Image.fromarray(arr, 'RGBA'))

def glow_fast(canvas, cx, cy, r, color, strength=1.0):
    """versión con recorte (no copia el lienzo entero)"""
    if strength <= 0.01:
        return
    r = int(r); size = 2 * r
    x0, y0 = int(cx - r), int(cy - r)
    Wc, Hc = canvas.size
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(Wc, x0 + size), min(Hc, y0 + size)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    yy, xx = np.mgrid[sy0:sy1, sx0:sx1].astype(np.float32)
    dd = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    g = np.clip(1 - dd, 0, 1) ** 2 * strength
    reg = np.array(canvas.crop((sx0, sy0, sx1, sy1))).astype(np.float32)
    reg[..., :3] += g[..., None] * np.array(color, np.float32)
    canvas.paste(Image.fromarray(np.clip(reg, 0, 255).astype(np.uint8), 'RGBA'), (sx0, sy0))

def speed_lines(canvas, x0, y0, x1, y1, n=4, color=(255, 255, 255, 150), width=4, spread=30, seed=0):
    d = ImageDraw.Draw(canvas)
    r = random.Random(seed)
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    for i in range(n):
        o = (i - (n - 1) / 2) * spread / max(1, n - 1) * 2 + r.uniform(-6, 6)
        s = r.uniform(0.0, 0.3)
        d.line([(x0 + dx * s + nx * o, y0 + dy * s + ny * o), (x1 + nx * o * 0.6, y1 + ny * o * 0.6)], fill=color, width=width)
