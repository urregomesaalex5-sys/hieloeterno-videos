#!/usr/bin/env python3
# Portadas del capítulo 6 (la memoria del celular) (el miniaturista hace varias versiones y se comparan).
import math
import random
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
import memoria as M
import pcb as PCB
import char3d as C

W, H = 1080, 1920
os.makedirs('out', exist_ok=True)


def base(ray_col=(140, 255, 200), seed=4):
    img = PCB.layers()['full'].copy()
    img = Image.fromarray((np.array(img.convert('RGB'), np.float32) * 0.78).astype(np.uint8)).convert('RGBA')
    rays = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(rays)
    cx, cy = 540, 900
    for k in range(16):
        a0 = k * 2 * math.pi / 16; a1 = a0 + 0.12
        d.polygon([(cx, cy), (cx + 1600 * math.cos(a0), cy + 1600 * math.sin(a0)), (cx + 1600 * math.cos(a1), cy + 1600 * math.sin(a1))],
                  fill=ray_col + (42,))
    img.alpha_composite(rays.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, S.ROOM_T], fill=(10, 40, 26))
    d.rectangle([0, S.FLOOR_B, W, H], fill=(10, 40, 26))
    r = random.Random(seed)
    for k in range(7):
        x = r.choice([r.uniform(40, 170), r.uniform(910, 1040)]); y = r.uniform(560, 1300)
        S.paste_center(img, M.electron(26), x, y, scale=r.uniform(0.8, 1.3), angle=r.uniform(-0.8, 0.8))
    return img


def glow_paste(img, lay, x, y, scale=1.0, angle=0.0, col_blur=18, times=2):
    g = lay.filter(ImageFilter.GaussianBlur(col_blur))
    for _ in range(times):
        S.paste_center(img, g, x, y, scale=scale, angle=angle)
    S.paste_center(img, lay, x, y, scale=scale, angle=angle)


def character(img, expr='sorpresa', x=560, sx=1.0, sy=1.0, pose=None):
    ch = C.Character()
    p = pose or C.Pose(expr=expr, rarm=(2.4, 0, 0.5), relbow=0.6, larm=(0.4, 0, 0.5), lelbow=0.9, head=(0.1, -0.2, 0.08))
    p.expr = expr; p.sx = sx; p.sy = sy
    ch.render(img, p, dict(scale=32, ox=x, oy=H + 420, view_yaw=0.25), light=1.0, t=0.2)
    S.glow_fast(img, x, H + 420 - 28 * 32, 260, (60, 140, 255), 0.25)


def stamp(img, x=860, y=760):
    st = S.fancy_text('CAP. 6', 64, top=(150, 255, 210), bot=(30, 170, 120), outline=(5, 50, 30))
    S.paste_center(img, st, x, y, angle=-0.12)


def sparks(img, cx, cy, r=260, n=12, seed=1):
    l = D.L(W, H)
    rr = random.Random(seed)
    for k in range(n):
        a = k * 2 * math.pi / n + rr.uniform(-0.2, 0.2)
        r0 = r * rr.uniform(0.7, 0.9); r1 = r0 + rr.uniform(50, 90)
        l.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], (255, 235, 120, 255), 9)
    img.alpha_composite(l.done())


GREEN = dict(top=(150, 255, 210), bot=(30, 170, 120), outline=(5, 50, 30))
BLUE = dict(top=(150, 215, 255), bot=(40, 110, 240), outline=(5, 25, 70))


def v_a():
    """¿CÓMO FUNCIONA LA MEMORIA? + chip brillante con una foto"""
    img = base()
    S.paste_center(img, S.fancy_text('¿CÓMO FUNCIONA', 100, top=(255, 245, 120), bot=(255, 170, 20)), 540, 300, angle=0.02)
    S.paste_center(img, S.fancy_text('LA MEMORIA?', 124, **GREEN), 540, 445, angle=-0.02)
    S.glow_fast(img, 540, 820, 330, (120, 255, 190), 0.7)
    glow_paste(img, M.chip_grid(1.0), 540, 830, scale=1.0, angle=-0.06, times=1)
    S.paste_center(img, M.photo_card(False, 220), 800, 640, angle=0.15)
    stamp(img, 220, 1080)
    character(img, 'sorpresa')
    return img


def v_b():
    """¿DÓNDE VIVEN TUS FOTOS? + foto con ? y electrones"""
    img = base((150, 210, 255), 7)
    S.paste_center(img, S.fancy_text('¿DÓNDE VIVEN', 112, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 295, angle=0.02)
    S.paste_center(img, S.fancy_text('TUS FOTOS?', 140, top=(255, 245, 120), bot=(255, 170, 20)), 540, 445, angle=-0.03)
    S.glow_fast(img, 540, 820, 320, (120, 180, 255), 0.7)
    glow_paste(img, M.photo_card(False, 300), 450, 820, angle=-0.1, times=1)
    S.paste_center(img, M.photo_card(True, 220), 760, 760, angle=0.18)
    for k in range(9):
        a = k * 2 * math.pi / 9
        S.paste_center(img, M.electron(18), 540 + 300 * math.cos(a), 820 + 230 * math.sin(a))
    stamp(img, 860, 1080)
    character(img, 'sorpresa')
    return img


def v_c():
    """RAM vs ALMACENAMIENTO + escritorio contra archivero"""
    img = base((255, 220, 140), 9)
    S.paste_center(img, S.fancy_text('RAM vs', 140, **BLUE), 540, 290, angle=-0.02)
    S.paste_center(img, S.fancy_text('ALMACENAMIENTO', 84, top=(255, 245, 120), bot=(255, 170, 20)), 540, 430, angle=0.02)
    S.paste_center(img, M.desk_img(1.0), 300, 760, scale=1.3)
    S.paste_center(img, M.cabinet_img(), 800, 760, scale=1.25)
    stamp(img, 540, 1080)
    character(img, 'pensando')
    return img


def v_d():
    """¡ELECTRONES ATRAPADOS! + celda en corte con electrones"""
    img = base((150, 210, 255), 3)
    S.paste_center(img, S.fancy_text('¡ELECTRONES', 120, **BLUE), 540, 295, angle=0.02)
    S.paste_center(img, S.fancy_text('ATRAPADOS!', 130, top=(255, 245, 120), bot=(255, 170, 20)), 540, 440, angle=-0.02)
    cell = M.cell_layer(1.0, True)
    cell = cell.copy()
    for k in range(7):
        S.paste_center(cell, M.electron(), M.CELL_X0 + 150 + k * 50, 185)
    S.glow_fast(img, 540, 800, 330, (120, 180, 255), 0.6)
    glow_paste(img, cell, 540, 820, scale=1.5, times=1)
    stamp(img, 870, 1090)
    character(img, 'corazon')
    return img


def v_e():
    """¡3 BITS EN UNA CELDA! + vaso de 8 niveles"""
    img = base((255, 230, 140), 5)
    S.paste_center(img, S.fancy_text('¡3 BITS EN', 130, top=(255, 245, 120), bot=(255, 170, 20)), 540, 300, angle=-0.02)
    S.paste_center(img, S.fancy_text('UNA CELDA!', 124, **GREEN), 540, 445, angle=0.02)
    glow_paste(img, M.glass(5), 520, 840, scale=1.25, times=1)
    stamp(img, 860, 680)
    character(img, 'sorpresa')
    return img


VARIANTS = {'A': v_a, 'B': v_b, 'C': v_c, 'D': v_d, 'E': v_e}

if __name__ == '__main__':
    ims = {}
    for k, fn in VARIANTS.items():
        im = fn().convert('RGB')
        im.save(f'out/portada_{k}.jpg', quality=92)
        ims[k] = im
    # hoja de comparación (y prueba de lectura en chiquito: 20 %)
    sw, shh = 360, 640
    sheet = Image.new('RGB', (sw * len(ims), shh + 70 + 384), (20, 20, 24))
    d = ImageDraw.Draw(sheet)
    for i, (k, im) in enumerate(ims.items()):
        sheet.paste(im.resize((sw, shh)), (i * sw, 0))
        d.text((i * sw + sw // 2, shh + 35), k, font=S.font(40), fill=(255, 255, 255), anchor='mm')
        sheet.paste(im.resize((216, 384)), (i * sw + 72, shh + 70))
    sheet.save('out/portadas_comparacion.jpg', quality=90)
    print('ok')
