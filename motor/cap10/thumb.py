#!/usr/bin/env python3
# Portadas del capítulo 8 (el inductor) (el miniaturista hace varias versiones y se comparan).
import math
import random
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
import resistencia as R
import inductor as I
import rele as R
import trafo as T
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
        S.paste_center(img, T.transformer(110, 6, 6), x, y, angle=r.uniform(-0.6, 0.6))
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
    st = S.fancy_text('CAP. 10', 64, top=(150, 255, 210), bot=(30, 170, 120), outline=(5, 50, 30))
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


def neon_flash(img, x, y, sc=1.9):
    S.glow_fast(img, x, y - 30, 330, (255, 120, 40), 1.0)
    S.glow_fast(img, x, y - 30, 160, (255, 200, 120), 0.8)
    S.paste_center(img, I.neon(1.0, 200), x, y, scale=sc)


def big_coil(img, x, y, w=560, angle=-0.08, field=True):
    if field:
        fl = I.field_lines(0.3, 1.0, w, 120, n=4)
        S.paste_center(img, fl, x, y, angle=angle)
    S.glow_fast(img, x, y, 360, (255, 160, 70), 0.45)
    glow_paste(img, I.coil(w, int(w * 0.36), 16), x, y, angle=angle, times=1)


def zap(img, x, y, r=120, seed=2):
    l = D.L(W, H)
    rr = random.Random(seed)
    for j in range(9):
        a = rr.uniform(0, 2 * math.pi)
        pts = [(x, y)]
        for s in range(4):
            rad = r * (s + 1) / 4
            pts.append((x + rad * math.cos(a + rr.uniform(-0.4, 0.4)), y + rad * math.sin(a + rr.uniform(-0.4, 0.4))))
        l.line(pts, (220, 235, 255, 255), 7)
    img.alpha_composite(l.done())
    S.glow_fast(img, x, y, 200, (170, 210, 255), 0.9)


def big_relay(img, x, y, sc=2.4, angle=-0.06):
    S.glow_fast(img, x, y, 420, (90, 160, 255), 0.7)
    glow_paste(img, R.relay_box(300), x, y, scale=sc, angle=angle, times=1)


def clic(img, x, y, size=90, angle=-0.12):
    l = D.L(10, 10)
    f = S.font(size, True)
    w_, h_, b_ = S.text_size('¡CLIC!', f)
    R0 = max(w_, size) * 0.75 + 30
    l = D.L(int(R0 * 2 + 10), int(R0 * 2 + 10))
    c = (l.w / 2, l.h / 2)
    pts = []
    for k in range(24):
        r = R0 if k % 2 == 0 else R0 * 0.72
        a = k * math.pi / 12
        pts.append((c[0] + r * math.cos(a), c[1] + r * 0.62 * math.sin(a)))
    l.poly(pts, fill=(255, 255, 255, 240), outline=(30, 30, 36, 255), width=6)
    l.text(c, '¡CLIC!', size, fill=(225, 40, 40), black=True, stroke=3, stroke_fill=(60, 10, 10))
    S.paste_center(img, l.done(), x, y, angle=angle)


def title_A(img, word='TRANSFORMADOR?', style=None, size=98):
    style = style or ORANGE
    S.paste_center(img, S.fancy_text('¿CÓMO FUNCIONA UN', 82, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 420, angle=0.02)
    S.paste_center(img, S.fancy_text(word, size, **style), 540, 555, angle=-0.02)


def big_trafo(img, x, y, w=560, angle=-0.05, amp=0.9, glow2=1.0):
    S.glow_fast(img, x, y, 440, (255, 170, 80), 0.55)
    tr = T.transformer(w, 8, 12, glow2).copy()
    tr.alpha_composite(T.flux_overlay(w, 0.25, amp))
    glow_paste(img, tr, x, y, angle=angle, times=1)


def v_a():
    """estilo portada A: ¿CÓMO FUNCIONA UN TRANSFORMADOR? + transformador gigante brillando + personaje sorprendido"""
    img = base((255, 190, 110), 4)
    sparks(img, 540, 930, 360, 14)
    big_trafo(img, 540, 930, 560)
    title_A(img)
    stamp(img, 190, 1120)
    character(img, 'sorpresa')
    return img


def v_b():
    """¿NO SE TOCAN… Y PRENDE? + transformador con bombillo"""
    img = base((255, 225, 140), 7)
    big_trafo(img, 450, 950, 480, 0.03)
    S.glow_fast(img, 880, 830, 280, (255, 220, 120), 1.0)
    S.paste_center(img, I.bulb(1.0, 220), 880, 860, scale=1.4)
    S.paste_center(img, S.fancy_text('¿NO SE TOCAN...', 92, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 400, angle=-0.02)
    S.paste_center(img, S.fancy_text('Y PRENDE?', 130, **ORANGE), 540, 540, angle=0.02)
    S.paste_center(img, S.fancy_text('EL TRANSFORMADOR', 64, top=(170, 225, 255), bot=(40, 120, 230), outline=(8, 24, 70)), 540, 655)
    stamp(img, 880, 1130)
    character(img, 'sorpresa')
    return img


def v_c():
    """EL QUE ZUMBA EN TU POSTE"""
    img = base((150, 215, 255), 9)
    S.paste_center(img, S.fancy_text('¿QUÉ ZUMBA', 120, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 290, angle=-0.02)
    S.paste_center(img, S.fancy_text('EN EL POSTE?', 120, **BLUE), 540, 430, angle=0.02)
    S.glow_fast(img, 420, 900, 300, (255, 220, 140), 0.6)
    S.paste_center(img, T.pole(420, 1.0, 0.1), 600, 960, scale=1.35)
    stamp(img, 880, 1130)
    character(img, 'pensando')
    return img


def v_d():
    """¿CÓMO FUNCIONA UN TRANSFORMADOR? azul + 120 V"""
    img = base((140, 200, 255), 5)
    big_trafo(img, 540, 900, 560, 0.06)
    title_A(img, style=BLUE)
    S.paste_center(img, T.meter('120 V', 260), 860, 700, angle=0.08)
    stamp(img, 190, 1120)
    character(img, 'feliz')
    return img


VARIANTS = {'A': v_a, 'B': v_b, 'C': v_c, 'D': v_d}

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
