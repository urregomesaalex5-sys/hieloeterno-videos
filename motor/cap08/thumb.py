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
        S.paste_center(img, I.coil(120, 44, 8, core=True, leads=False), x, y, angle=r.uniform(-0.8, 0.8))
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
    st = S.fancy_text('CAP. 8', 64, top=(150, 255, 210), bot=(30, 170, 120), outline=(5, 50, 30))
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


def v_a():
    """¿CÓMO FUNCIONA UN INDUCTOR? + bobina gigante con campo + neón prendido"""
    img = base((120, 200, 255), 4)
    S.paste_center(img, S.fancy_text('¿CÓMO FUNCIONA UN', 82, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 300, angle=0.02)
    S.paste_center(img, S.fancy_text('INDUCTOR?', 150, **BLUE), 540, 440, angle=-0.02)
    big_coil(img, 540, 820)
    neon_flash(img, 860, 640, 1.5)
    stamp(img, 200, 1060)
    character(img, 'sorpresa')
    return img


def v_b():
    """¿1,5 V PRENDIÓ ESTO? + neón gigante prendido + pila"""
    img = base((255, 150, 80), 7)
    S.paste_center(img, S.fancy_text('¿UNA PILA DE 1,5 V', 84, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 295, angle=0.02)
    S.paste_center(img, S.fancy_text('PRENDIÓ ESTO?', 120, **ORANGE), 540, 430, angle=-0.03)
    neon_flash(img, 620, 820, 2.6)
    S.paste_center(img, I.battery_aa(230), 300, 860, scale=1.4, angle=0.25)
    zap(img, 780, 1060)
    stamp(img, 870, 1100)
    character(img, 'sorpresa')
    return img


def v_c():
    """¿CÓMO CARGA SIN CABLE? + base y celular con campo"""
    img = base((150, 230, 255), 9)
    S.paste_center(img, S.fancy_text('¿CÓMO CARGA', 120, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 295, angle=-0.02)
    S.paste_center(img, S.fancy_text('SIN CABLE?', 140, **BLUE), 540, 450, angle=0.02)
    S.paste_center(img, I.qi_scene(0.1, 1.0, 1.0, 0.8), 540, 820, scale=1.35)
    stamp(img, 870, 1100)
    character(img, 'corazon')
    return img


def v_d():
    """LA BOBINA QUE ODIA LOS CAMBIOS + bobina con sello"""
    img = base((255, 200, 120), 3)
    S.paste_center(img, S.fancy_text('SE OPONE', 130, **ORANGE), 540, 295, angle=0.02)
    S.paste_center(img, S.fancy_text('AL CAMBIO', 130, **BLUE), 540, 440, angle=-0.02)
    big_coil(img, 540, 800, angle=0.06)
    S.paste_center(img, S.fancy_text('¿INDUCTOR?', 80, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 1050, angle=-0.05)
    stamp(img, 880, 620)
    character(img, 'pensando')
    return img


def v_e():
    """INDUCTOR + chispa en el interruptor"""
    img = base((170, 210, 255), 5)
    S.paste_center(img, S.fancy_text('¿CÓMO FUNCIONA UN', 82, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 300, angle=0.02)
    S.paste_center(img, S.fancy_text('INDUCTOR?', 150, **ORANGE), 540, 440, angle=-0.02)
    S.paste_center(img, I.knife_switch(0.6, 230), 380, 880, scale=2.0)
    zap(img, 330, 900, 160)
    neon_flash(img, 820, 800, 2.0)
    stamp(img, 860, 1100)
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
