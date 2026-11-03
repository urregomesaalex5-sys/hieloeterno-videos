# Escenario del cap. 6: POR DENTRO DEL CELULAR.
# Pared = placa de circuito (verde) en bloques estilo Minecraft, con pistas de cobre, pads dorados
# y chips negros. Piso = la superficie de un chip (negro) con patitas plateadas.
import math
import random
import numpy as np
from PIL import Image, ImageDraw
import scene as S

W, H, BLK = S.W, S.H, S.BLK
_c = {}


def _board_tile(rng, kind):
    px = BLK // 8
    im = Image.new('RGB', (BLK, BLK))
    d = ImageDraw.Draw(im)
    base = (18, 92, 58)
    for i in range(8):
        for j in range(8):
            v = rng.randint(-10, 10)
            d.rectangle([i * px, j * px, i * px + px - 1, j * px + px - 1],
                        fill=(base[0] + v // 2, base[1] + v, base[2] + v // 2))
    cu = (196, 132, 58)
    if kind == 'h':
        y = rng.choice([2, 3, 4, 5]) * px
        d.rectangle([0, y, BLK, y + px - 2], fill=cu)
    elif kind == 'v':
        x = rng.choice([2, 3, 4, 5]) * px
        d.rectangle([x, 0, x + px - 2, BLK], fill=cu)
    elif kind == 'corner':
        x = 4 * px; y = 4 * px
        d.rectangle([0, y, x + px - 2, y + px - 2], fill=cu)
        d.rectangle([x, y, x + px - 2, BLK], fill=cu)
    elif kind == 'pad':
        c = BLK // 2
        d.rectangle([c - 2 * px, c - 2 * px, c + 2 * px - 1, c + 2 * px - 1], fill=(232, 192, 70))
        d.rectangle([c - px, c - px, c + px - 1, c + px - 1], fill=(30, 40, 34))
    elif kind == 'via':
        for _ in range(2):
            x = rng.randint(1, 6) * px; y = rng.randint(1, 6) * px
            d.ellipse([x - px, y - px, x + px, y + px], fill=(220, 180, 70))
            d.ellipse([x - px // 2, y - px // 2, x + px // 2, y + px // 2], fill=(20, 30, 25))
    # borde de bloque
    d.rectangle([0, 0, BLK - 1, BLK - 1], outline=(12, 64, 40), width=2)
    return im


def _chip(w, h, label=''):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pin = 9
    for x in range(14, w - 14, 22):
        d.rectangle([x, 0, x + pin, 12], fill=(200, 205, 212))
        d.rectangle([x, h - 12, x + pin, h], fill=(200, 205, 212))
    d.rectangle([0, 10, w, h - 10], fill=(26, 26, 30), outline=(60, 60, 66), width=3)
    d.ellipse([12, 20, 26, 34], fill=(60, 60, 66))
    if label:
        d.text((w / 2, h / 2), label, font=S.font(22), fill=(150, 150, 160), anchor='mm')
    return im


def raw():
    rng = random.Random(61)
    im = Image.new('RGB', (W, H), (0, 0, 0))
    kinds = ['plain'] * 6 + ['h', 'h', 'v', 'v', 'corner', 'pad', 'via']
    for y in S.WALL_ROWS:
        for c in range(S.NCOL):
            im.paste(_board_tile(rng, rng.choice(kinds)), (S.X0 + c * BLK, y))
    # chips en la placa (lejos de donde van los diagramas, más que nada en los bordes)
    for (x, y, w, h, lab) in [(40, 300, 150, 110, 'SoC'), (880, 980, 170, 120, 'UFS'),
                              (70, 1030, 150, 100, 'LPDDR'), (900, 330, 140, 90, '')]:
        ch = _chip(w, h, lab)
        im.paste(ch, (x, y), ch)
    # piso: superficie de un chip con patitas
    d = ImageDraw.Draw(im)
    d.rectangle([0, S.FLOOR_T, W, S.FLOOR_B], fill=(28, 28, 32))
    for x in range(0, W, 36):
        d.rectangle([x + 6, S.FLOOR_T, x + 24, S.FLOOR_T + 10], fill=(205, 210, 218))
    for x in range(0, W, 9):
        v = rng.randint(-6, 6)
        d.line([(x, S.FLOOR_T + 14), (x, S.FLOOR_B)], fill=(32 + v, 32 + v, 37 + v))
    d.rectangle([0, 0, W, S.ROOM_T - 1], fill=(0, 0, 0))
    d.rectangle([0, S.FLOOR_B, W, H], fill=(0, 0, 0))
    return im


def layers():
    if not _c:
        arr = np.array(raw(), np.float32) * S.LIGHT[..., None]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dy = np.maximum(yy - S.LAMP_Y, 1)
        half = 60 + dy * 0.36
        beam = np.clip(1.0 - np.abs(xx - S.LAMP_X) / half, 0, 1) ** 1.5 * np.clip(1 - dy / 1600, 0, 1) * 18
        beam[yy < S.ROOM_T] = 0
        arr += beam[..., None] * np.array([1.0, 0.95, 0.8])
        full = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
        _c['full'] = full
        _c['full_np'] = np.array(full.convert('RGB'), np.float32)
    return _c


def draw_anim(cv, t, light=1.0):
    """pulsos de datos que corren por algunas pistas (puntitos cian)"""
    if light < 0.05:
        return
    d = ImageDraw.Draw(cv, 'RGBA')
    rows = [S.WALL_ROWS[2] + 3 * BLK // 8, S.WALL_ROWS[11] + 4 * BLK // 8, S.WALL_ROWS[15] + 3 * BLK // 8]
    for k, y in enumerate(rows):
        for j in range(3):
            x = ((t * (260 + 70 * k) + j * 380 + k * 150) % (W + 200)) - 100
            d.rectangle([x - 10, y, x + 10, y + 6], fill=(120, 240, 255, int(170 * light)))
