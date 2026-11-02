# Laboratorio estilo Minecraft para el capítulo 5: azulejos, piso de cuadros, estantes con frascos,
# mesón con vasos de colores, osciloscopio y bola de plasma. Capas separadas para animar el cambio.
import math
import random
import numpy as np
from PIL import Image, ImageDraw
import scene as S

W, H, BLK = S.W, S.H, S.BLK
CTOP = 1150          # tapa del mesón
_r = random.Random(11)


def _pix_block(base, var, n=16, grout=None, gcol=None, edge=0.85, seed=0):
    rng = random.Random(seed)
    arr = np.zeros((n, n, 3), np.float32)
    for y in range(n):
        for x in range(n):
            arr[y, x] = np.array(base, np.float32) * (1 + rng.uniform(-var, var))
    if grout:
        for k in grout:
            arr[k, :] = gcol; arr[:, k] = gcol
    arr[n - 1, :] *= edge; arr[:, n - 1] *= edge
    arr[0, :] *= 1.06; arr[:, 0] *= 1.04
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').resize((BLK, BLK), Image.NEAREST)

# azulejo de laboratorio: verde azulado oscuro con juntas claras (4 azulejitos por bloque)
TILES = [_pix_block((52, 94, 104), 0.05, grout=(0, 8), gcol=(104, 142, 150), seed=s) for s in range(6)]
TILES_LOW = [_pix_block((40, 70, 80), 0.05, grout=(0, 8), gcol=(84, 118, 126), seed=20 + s) for s in range(4)]
FLOOR_W = _pix_block((196, 200, 206), 0.04, seed=40)
FLOOR_B = _pix_block((58, 62, 72), 0.06, seed=41)


def bare_raw():
    im = Image.new('RGB', (W, H), (0, 0, 0))
    r = random.Random(3)
    for ri, y in enumerate(S.WALL_ROWS):
        for c in range(S.NCOL):
            pool = TILES_LOW if y >= CTOP - 2 * BLK else TILES
            im.paste(pool[r.randrange(len(pool))], (S.X0 + c * BLK, y))
    # franja de advertencia (amarillo/negro) a media pared
    d = ImageDraw.Draw(im)
    yb = CTOP - 2 * BLK - 14
    for x in range(-40, W + 40, 40):
        d.polygon([(x, yb), (x + 20, yb), (x + 34, yb + 14), (x + 14, yb + 14)], fill=(235, 190, 40))
        d.polygon([(x + 20, yb), (x + 40, yb), (x + 54, yb + 14), (x + 34, yb + 14)], fill=(30, 30, 30))
    for c in range(S.NCOL):
        im.paste((FLOOR_W if c % 2 == 0 else FLOOR_B).crop((0, 0, BLK, S.FLOOR_B - S.FLOOR_T)), (S.X0 + c * BLK, S.FLOOR_T))
    d.rectangle([0, 0, W, S.ROOM_T - 1], fill=(0, 0, 0))
    d.rectangle([0, S.FLOOR_B, W, H], fill=(0, 0, 0))
    return im


# ---------------- muebles (capas RGBA del tamaño del cuadro) ----------------
def _px(d, x, y, w, h, col):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=col)

def counter_layer():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # gabinetes blancos con puertas
    _px(d, 0, CTOP + 26, W, S.FLOOR_T - CTOP - 26, (206, 210, 216, 255))
    for x in range(0, W, 180):
        d.rectangle([x + 10, CTOP + 40, x + 170, S.FLOOR_T - 12], outline=(150, 156, 166, 255), width=4)
        _px(d, x + 74, CTOP + 70, 32, 10, (110, 116, 126, 255))
    _px(d, 0, S.FLOOR_T - 12, W, 12, (60, 62, 70, 255))
    # tapa de granito negro
    _px(d, 0, CTOP, W, 28, (34, 36, 42, 255))
    _px(d, 0, CTOP, W, 5, (90, 94, 104, 255))
    rr = random.Random(5)
    for k in range(160):
        _px(d, rr.randrange(W), CTOP + 6 + rr.randrange(20), 3, 2, (70, 72, 80, 255))
    return im

def shelf_layer():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in (430, 640):
        _px(d, 16, y, 360, 16, (170, 176, 186, 255))
        _px(d, 16, y + 16, 360, 5, (90, 94, 104, 255))
        for bx in (40, 336):
            d.polygon([(bx, y + 16), (bx + 16, y + 16), (bx + 16, y + 50)], fill=(120, 124, 134, 255))
    # frascos y cosas en los estantes
    def flask(x, ybase, col, h=86):
        w = h * 0.7
        d.polygon([(x - 10, ybase - h), (x + 10, ybase - h), (x + 10, ybase - h * 0.6), (x + w / 2, ybase), (x - w / 2, ybase), (x - 10, ybase - h * 0.6)],
                  fill=(200, 225, 235, 150), outline=(230, 245, 250, 230), width=3)
        d.polygon([(x - w * 0.36, ybase - h * 0.28), (x + w * 0.36, ybase - h * 0.28), (x + w / 2 - 3, ybase - 3), (x - w / 2 + 3, ybase - 3)], fill=col + (235,))
        _px(d, x - 12, ybase - h - 6, 24, 8, (140, 100, 70, 255))
    def jar(x, ybase, col, h=70):
        d.rectangle([x - 22, ybase - h, x + 22, ybase], fill=(200, 225, 235, 140), outline=(230, 245, 250, 230), width=3)
        d.rectangle([x - 19, ybase - h * 0.6, x + 19, ybase - 3], fill=col + (230,))
        _px(d, x - 24, ybase - h - 10, 48, 12, (70, 74, 84, 255))
    flask(70, 430, (80, 220, 120)); jar(140, 430, (230, 90, 200)); flask(215, 430, (90, 160, 255), 74)
    for k, col in enumerate([(200, 60, 60), (60, 120, 200), (230, 180, 40), (80, 170, 90), (150, 80, 180)]):
        _px(d, 270 + k * 18, 430 - 70 + (k % 2) * 8, 15, 70 - (k % 2) * 8, col + (255,))
    jar(60, 640, (255, 170, 60), 60); flask(135, 640, (250, 90, 90), 90)
    # microscopio
    mx = 250
    _px(d, mx - 40, 628, 80, 12, (60, 62, 70, 255))
    _px(d, mx + 10, 560, 16, 70, (220, 224, 232, 255))
    d.polygon([(mx - 26, 540), (mx - 6, 530), (mx + 20, 590), (mx, 600)], fill=(230, 234, 240, 255), outline=(120, 126, 136, 255))
    _px(d, mx - 34, 596, 50, 8, (60, 62, 70, 255))
    _px(d, mx - 30, 524, 18, 12, (40, 42, 48, 255))
    jar(330, 640, (120, 240, 230), 56)
    return im

def items_layer():
    """cosas del mesón (sin las partes animadas)"""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # vasos de precipitado
    for x, col, h in ((500, (80, 230, 120), 90), (575, (90, 160, 255), 120), (650, (240, 90, 180), 80)):
        d.rectangle([x - 28, CTOP - h, x + 28, CTOP], fill=(200, 225, 235, 120), outline=(235, 248, 252, 230), width=3)
        d.rectangle([x - 25, CTOP - h * 0.55, x + 25, CTOP - 3], fill=col + (220,))
        for k in range(3):
            _px(d, x + 10, CTOP - h + 18 + k * 18, 14, 3, (235, 248, 252, 200))
    # osciloscopio
    ox0, oy0 = 790, 990
    d.rectangle([ox0, oy0, ox0 + 240, CTOP], fill=(70, 74, 84, 255), outline=(150, 156, 166, 255), width=4)
    d.rectangle([ox0 + 16, oy0 + 16, ox0 + 160, oy0 + 130], fill=(12, 30, 20, 255), outline=(40, 44, 50, 255), width=3)
    for k in range(5):
        d.ellipse([ox0 + 178, oy0 + 18 + k * 26, ox0 + 198, oy0 + 38 + k * 26], fill=(200, 204, 214, 255))
        _px(d, ox0 + 208, oy0 + 22 + k * 26, 18, 12, (230, 90, 60, 255) if k == 0 else (60, 64, 72, 255))
    # base de la bola de plasma
    px_ = 400
    d.polygon([(px_ - 40, CTOP), (px_ + 40, CTOP), (px_ + 26, CTOP - 40), (px_ - 26, CTOP - 40)], fill=(30, 32, 38, 255))
    # protoboard con LEDs
    d.rectangle([690, CTOP - 22, 770, CTOP], fill=(236, 236, 230, 255), outline=(170, 170, 160, 255), width=2)
    return im

SCOPE = (790 + 16, 990 + 16, 790 + 160, 990 + 130)
PLASMA = (400, CTOP - 40 - 52)


# ---------------- luz ----------------
_c = {}
def _lit_rgba(layer):
    a = np.array(layer, np.float32)
    a[..., :3] *= S.LIGHT[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')

def _beam():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dy = np.maximum(yy - S.LAMP_Y, 1)
    half = 60 + dy * 0.36
    beam = np.clip(1.0 - np.abs(xx - S.LAMP_X) / half, 0, 1) ** 1.5 * np.clip(1 - dy / 1600, 0, 1) * 18
    beam[yy < S.ROOM_T] = 0
    return beam[..., None] * np.array([1.0, 0.95, 0.8])

def layers():
    if not _c:
        raw = np.array(bare_raw(), np.float32) * S.LIGHT[..., None] + _beam()
        _c['bare'] = Image.fromarray(np.clip(raw, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
        _c['counter'] = _lit_rgba(counter_layer())
        _c['shelf'] = _lit_rgba(shelf_layer())
        _c['items'] = _lit_rgba(items_layer())
        full = _c['bare'].copy()
        for k in ('shelf', 'counter', 'items'):
            full.alpha_composite(_c[k])
        _c['full'] = full
        _c['full_np'] = np.array(full.convert('RGB'), np.float32)
    return _c


def draw_anim(cv, t, light=1.0):
    """partes vivas: onda del osciloscopio, bola de plasma, burbujas y LEDs"""
    if light < 0.05:
        return
    l = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(l)
    x0, y0, x1, y1 = SCOPE
    pts = []
    for k in range(60):
        u = k / 59
        x = x0 + 6 + (x1 - x0 - 12) * u
        y = (y0 + y1) / 2 + 34 * math.sin(u * 4 * math.pi + t * 5)
        pts.append((x, y))
    d.line(pts, fill=(90, 255, 140, int(235 * light)), width=4)
    # bola de plasma
    cx, cy = PLASMA
    d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=(70, 40, 120, int(110 * light)), outline=(200, 190, 255, int(200 * light)), width=3)
    rr = random.Random(int(t * 12))
    for k in range(5):
        a = rr.uniform(0, 2 * math.pi)
        p = [(cx, cy)]
        for j in range(1, 5):
            rad = 48 * j / 4
            a += rr.uniform(-0.4, 0.4)
            p.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
        d.line(p, fill=(230, 160, 255, int(220 * light)), width=3)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(255, 230, 255, int(255 * light)))
    # burbujas en los vasos
    for x, h, s in ((500, 90, 0), (575, 120, 1), (650, 80, 2)):
        for k in range(3):
            ph = (t * 0.7 + k / 3 + s * 0.13) % 1.0
            by = CTOP - 6 - ph * h * 0.5
            d.ellipse([x - 12 + 9 * k - 3, by - 3, x - 12 + 9 * k + 3, by + 3], fill=(255, 255, 255, int(170 * light * (1 - ph))))
    # LEDs del protoboard
    for k, col in enumerate([(255, 60, 60), (60, 255, 90), (255, 200, 40)]):
        on = (int(t * 3) + k) % 3 == 0
        c = col if on else tuple(v // 4 for v in col)
        d.ellipse([706 + k * 22, CTOP - 36, 718 + k * 22, CTOP - 24], fill=c + (int(255 * light),))
    cv.alpha_composite(l)


def transition(stone, t, t0, origin, light=1.0):
    """cambio de cuarto: los bloques se voltean en ola desde 'origin' y caen los muebles"""
    L = layers()
    out = stone.copy()
    bare = L['bare']
    ox, oy = origin
    for y in S.WALL_ROWS + [S.FLOOR_T]:
        for c in range(S.NCOL):
            x = S.X0 + c * BLK
            hgt = BLK if y != S.FLOOR_T else S.FLOOR_B - S.FLOOR_T
            dist = math.hypot(x + BLK / 2 - ox, y + BLK / 2 - oy)
            p = (t - t0 - dist / 1700) / 0.22
            if p <= 0:
                continue
            if p >= 1:
                out.paste(bare.crop((x, y, x + BLK, y + hgt)), (x, y))
                continue
            src = stone if p < 0.5 else bare
            k = abs(1 - 2 * p)
            tile = src.crop((x, y, x + BLK, y + hgt))
            wnew = max(1, int(BLK * k))
            tile = tile.resize((wnew, hgt))
            ImageDraw.Draw(out).rectangle([x, y, x + BLK - 1, y + hgt - 1], fill=(10, 12, 16))
            out.paste(tile, (x + (BLK - wnew) // 2, y))
    # muebles
    tf = t0 + 0.75
    for name, delay, dy0 in (('shelf', 0.0, -420), ('counter', 0.12, 300), ('items', 0.32, -160)):
        u = (t - tf - delay) / 0.45
        if u <= 0:
            continue
        if u >= 1:
            out.alpha_composite(L[name])
            continue
        v = S.bounce_out(u)
        dy = int(dy0 * (1 - v))
        lay = L[name]
        a = min(1.0, u * 3)
        if a < 1:
            arr = np.array(lay); arr[..., 3] = (arr[..., 3] * a).astype(np.uint8); lay = Image.fromarray(arr)
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        tmp.paste(lay, (0, dy))
        out.alpha_composite(tmp)
    return out

T_TRANS = 1.7     # duración total del cambio
