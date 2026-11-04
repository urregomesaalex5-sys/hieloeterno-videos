#!/usr/bin/env python3
# Portadas del capítulo 7 (la resistencia) (el miniaturista hace varias versiones y se comparan).
import math
import random
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
import resistencia as R
import lab as LB
import char3d as C

W, H = 1080, 1920
os.makedirs('out', exist_ok=True)


def base(ray_col=(140, 255, 200), seed=4):
    img = LB.layers()['full'].copy()
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
    d.rectangle([0, 0, W, S.ROOM_T], fill=(30, 18, 8))
    d.rectangle([0, S.FLOOR_B, W, H], fill=(30, 18, 8))
    r = random.Random(seed)
    for k in range(6):
        x = r.choice([r.uniform(60, 170), r.uniform(910, 1020)]); y = r.uniform(600, 1300)
        S.paste_center(img, R.resistor(110, leads=False), x, y, angle=r.uniform(-0.8, 0.8))
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
    S.glow_fast(img, x, H + 420 - 28 * 32, 260, (255, 150, 60), 0.25)


def stamp(img, x=860, y=760):
    st = S.fancy_text('CAP. 7', 64, top=(150, 255, 210), bot=(30, 170, 120), outline=(5, 50, 30))
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


ORANGE = dict(top=(255, 236, 170), bot=(240, 120, 20), outline=(70, 30, 5))


def burnt_led(img, x, y, sc=1.6):
    S.glow_fast(img, x, y - 90, 220, (255, 200, 120), 0.6)
    S.paste_center(img, R.led(0.0, 1.0, 260), x, y, scale=sc)
    R.smoke(img, x, y - 140, 0.9, a=1.0)
    R.spark(img, x + 30, y - 130, 0.05)


def v_a():
    """¿CÓMO FUNCIONA UNA RESISTENCIA? + resistencia gigante brillante"""
    img = base((255, 200, 120), 4)
    S.paste_center(img, S.fancy_text('¿CÓMO FUNCIONA UNA', 78, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 300, angle=0.02)
    S.paste_center(img, S.fancy_text('RESISTENCIA?', 128, **ORANGE), 540, 430, angle=-0.02)
    S.glow_fast(img, 540, 800, 340, (255, 180, 80), 0.7)
    glow_paste(img, R.resistor(560), 540, 800, angle=-0.12, times=1)
    stamp(img, 860, 1080)
    character(img, 'sorpresa')
    return img


def v_b():
    """¿POR QUÉ SE QUEMÓ? + LED quemado con humo"""
    img = base((255, 140, 90), 7)
    S.paste_center(img, S.fancy_text('¿POR QUÉ', 120, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 295, angle=0.02)
    S.paste_center(img, S.fancy_text('SE QUEMÓ?', 140, top=(255, 200, 120), bot=(230, 50, 30), outline=(60, 10, 5)), 540, 445, angle=-0.03)
    burnt_led(img, 400, 920)
    S.paste_center(img, R.resistor(300), 760, 760, angle=0.5)
    stamp(img, 860, 1080)
    character(img, 'sorpresa')
    return img


def v_c():
    """¡ESTO SALVA TU LED! + LED prendido con resistencia"""
    img = base((255, 120, 110), 9)
    S.paste_center(img, S.fancy_text('¡ESTO SALVA', 120, **ORANGE), 540, 295, angle=-0.02)
    S.paste_center(img, S.fancy_text('TU LED!', 150, top=(255, 170, 160), bot=(230, 40, 40), outline=(60, 5, 5)), 540, 450, angle=0.02)
    S.glow_fast(img, 300, 760, 260, (255, 70, 60), 0.9)
    S.paste_center(img, R.led(1.0, 0.0, 260), 300, 830, scale=1.5)
    glow_paste(img, R.resistor(380), 730, 800, angle=-0.3, times=1)
    stamp(img, 860, 1080)
    character(img, 'corazon')
    return img


def v_d():
    """¿QUÉ SIGNIFICAN LOS COLORES? + resistencia con franjas resaltadas"""
    img = base((255, 230, 140), 3)
    S.paste_center(img, S.fancy_text('¿QUÉ SIGNIFICAN', 98, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 295, angle=0.02)
    S.paste_center(img, S.fancy_text('SUS COLORES?', 120, **ORANGE), 540, 430, angle=-0.02)
    glow_paste(img, R.resistor(600, hl=2), 540, 790, times=1)
    for k, (txt, x) in enumerate((('3', 330), ('3', 430), ('×10', 560), ('±5%', 820))):
        S.paste_center(img, S.fancy_text(txt, 70, **GREEN), x, 980 if k < 3 else 640)
    stamp(img, 860, 1120)
    character(img, 'pensando')
    return img


def v_e():
    """5V – 2V = 3V: ¡LEY DE OHM! + circuito"""
    img = base((150, 255, 200), 5)
    S.paste_center(img, S.fancy_text('¡NO SE COME', 116, **ORANGE), 540, 300, angle=-0.02)
    S.paste_center(img, S.fancy_text('LA CORRIENTE!', 110, **GREEN), 540, 440, angle=0.02)
    S.paste_center(img, R.meter('9 mA', 'A', 260), 300, 740, angle=-0.08)
    glow_paste(img, R.resistor(260), 540, 760, times=1)
    S.paste_center(img, R.meter('9 mA', 'A', 260), 780, 740, angle=0.08)
    stamp(img, 860, 1080)
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
