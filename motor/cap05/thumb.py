#!/usr/bin/env python3
# Portadas del capítulo 5 (el miniaturista hace varias versiones y se comparan).
import math
import random
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
import condensador as K
import lab as LB
import char3d as C

W, H = 1080, 1920
os.makedirs('out', exist_ok=True)


def base(ray_col=(255, 220, 140), seed=4):
    img = LB.layers()['full'].copy()
    LB.draw_anim(img, 0.4, 1.0)
    img = Image.fromarray((np.array(img.convert('RGB'), np.float32) * 0.8).astype(np.uint8)).convert('RGBA')
    for y0 in range(0, S.ROOM_T, S.BLK):
        for c in range(S.NCOL):
            t = LB.TILES[(c + y0) % len(LB.TILES)].point(lambda v: int(v * 0.5))
            img.paste(t, (S.X0 + c * S.BLK, y0 - (S.BLK - S.ROOM_T % S.BLK)))
    for y0 in range(S.FLOOR_B, H, S.BLK):
        for c in range(S.NCOL):
            t = (LB.FLOOR_W if (c + y0 // S.BLK) % 2 else LB.FLOOR_B).point(lambda v: int(v * 0.45))
            img.paste(t, (S.X0 + c * S.BLK, y0))
    rays = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(rays)
    cx, cy = 540, 900
    for k in range(16):
        a0 = k * 2 * math.pi / 16; a1 = a0 + 0.12
        d.polygon([(cx, cy), (cx + 1600 * math.cos(a0), cy + 1600 * math.sin(a0)), (cx + 1600 * math.cos(a1), cy + 1600 * math.sin(a1))],
                  fill=ray_col + (42,))
    img.alpha_composite(rays.filter(ImageFilter.GaussianBlur(6)))
    r = random.Random(seed)
    for k in range(8):
        b = LB.TILES[k % len(LB.TILES)] if k % 2 else S.STONES[k % len(S.STONES)]
        x = r.choice([r.uniform(40, 170), r.uniform(910, 1040)]); y = r.uniform(560, 1300)
        S.paste_center(img, b.convert('RGBA'), x, y, scale=r.uniform(0.55, 0.9), angle=r.uniform(-0.8, 0.8))
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
    st = S.fancy_text('CAP. 5', 64, top=(150, 215, 255), bot=(40, 110, 240), outline=(5, 25, 70))
    S.paste_center(img, st, x, y, angle=-0.12)


def sparks(img, cx, cy, r=260, n=12, seed=1):
    l = D.L(W, H)
    rr = random.Random(seed)
    for k in range(n):
        a = k * 2 * math.pi / n + rr.uniform(-0.2, 0.2)
        r0 = r * rr.uniform(0.7, 0.9); r1 = r0 + rr.uniform(50, 90)
        l.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], (255, 235, 120, 255), 9)
    img.alpha_composite(l.done())


def v_a():
    """¿CÓMO FUNCIONA UN CONDENSADOR? + condensador brillante"""
    img = base()
    S.paste_center(img, S.fancy_text('¿CÓMO FUNCIONA', 100, top=(255, 245, 120), bot=(255, 170, 20)), 540, 300, angle=0.02)
    S.paste_center(img, S.fancy_text('UN CONDENSADOR?', 90, top=(150, 215, 255), bot=(40, 110, 240), outline=(5, 25, 70)), 540, 440, angle=-0.02)
    S.glow_fast(img, 540, 800, 330, (255, 220, 90), 0.8)
    glow_paste(img, K.elec_cap(380), 540, 850, scale=1.15, angle=-0.1, times=1)
    sparks(img, 540, 760, 250)
    stamp(img, 870, 1080)
    character(img, 'sorpresa')
    return img


def v_b():
    """¡¿EXPLOTA?! + electrolítico inflado con ¡PUM!"""
    img = base((255, 160, 90), 7)
    S.paste_center(img, S.fancy_text('¡NO LO CONECTES', 100, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 290, angle=0.02)
    S.paste_center(img, S.fancy_text('AL REVÉS!', 150, top=(255, 230, 120), bot=(255, 80, 30), outline=(80, 20, 0)), 540, 440, angle=-0.03)
    S.paste_center(img, K.smoke(0.8, 3), 560, 640, scale=1.6, alpha=0.8)
    glow_paste(img, K.elec_cap(380, 0.9), 540, 860, scale=1.1, angle=0.08, times=1)
    S.paste_center(img, K.pum_text(), 800, 640, scale=1.2, angle=-0.15)
    stamp(img, 220, 1080)
    character(img, 'sorpresa', x=600)
    return img


def v_c():
    """3 TIPOS DE CONDENSADORES + fila de tipos"""
    img = base((150, 210, 255), 9)
    S.paste_center(img, S.fancy_text('¡3 TIPOS DE', 120, top=(255, 245, 120), bot=(255, 170, 20)), 540, 280, angle=0.02)
    S.paste_center(img, S.fancy_text('CONDENSADORES!', 104, top=(150, 215, 255), bot=(40, 110, 240), outline=(5, 25, 70)), 540, 420, angle=-0.02)
    S.paste_center(img, K.ceramic_cap(240), 210, 860, angle=-0.12)
    glow_paste(img, K.elec_cap(330), 520, 820, times=1)
    S.paste_center(img, K.supercap(400), 840, 830, scale=0.95, angle=0.08)
    stamp(img, 540, 1110)
    character(img, 'feliz')
    return img


def v_d():
    """¿POR QUÉ PITA EL FLASH? + cámara con destello y 300 V"""
    img = base((255, 255, 220), 3)
    S.paste_center(img, S.fancy_text('¿POR QUÉ PITA', 112, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 290)
    S.paste_center(img, S.fancy_text('EL FLASH?', 150, top=(255, 245, 120), bot=(255, 170, 20)), 540, 440, angle=-0.02)
    S.paste_center(img, K.camera_img(1.0, 1.0, 1.0, 1.0), 540, 820, scale=2.0)
    S.paste_center(img, K.flash_star(), 540 - 90, 820 - 165, scale=1.2)
    S.paste_center(img, K.volt_meter(300), 820, 1060, scale=1.0, angle=0.08)
    stamp(img, 220, 1060)
    character(img, 'sorpresa')
    return img


def v_e():
    """TU CELULAR TIENE CIENTOS + placa con lupa"""
    img = base((255, 230, 140), 5)
    S.paste_center(img, S.fancy_text('TU CELULAR', 130, top=(255, 245, 120), bot=(255, 170, 20)), 540, 300, angle=-0.02)
    S.paste_center(img, S.fancy_text('TIENE CIENTOS', 104, top=(150, 215, 255), bot=(40, 110, 240), outline=(5, 25, 70)), 540, 440, angle=0.02)
    S.paste_center(img, K.phone_board(0.3), 420, 860, scale=1.05, angle=-0.08)
    S.paste_center(img, D.magnifier(K.sand_vs_mlcc(), r=170), 720, 960, scale=1.0)
    stamp(img, 870, 640)
    character(img, 'corazon')
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
