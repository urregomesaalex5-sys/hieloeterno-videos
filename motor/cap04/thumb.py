#!/usr/bin/env python3
# Portadas del capítulo 4 (el miniaturista hace varias versiones y se comparan).
import math
import random
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
import diodo as DD
import char3d as C

W, H = 1080, 1920
os.makedirs('out', exist_ok=True)


def base(ray_col=(255, 220, 140), seed=4):
    img = S.lit_room().convert('RGBA')
    for y0 in range(0, S.ROOM_T, S.BLK):
        for c in range(S.NCOL):
            t = S.STONES[(c + y0) % len(S.STONES)].point(lambda v: int(v * 0.45))
            img.paste(t, (S.X0 + c * S.BLK, y0 - (S.BLK - S.ROOM_T % S.BLK)))
    for y0 in range(S.FLOOR_B, H, S.BLK):
        for c in range(S.NCOL):
            t = S.WOODS[(c + y0) % len(S.WOODS)].point(lambda v: int(v * 0.4))
            img.paste(t, (S.X0 + c * S.BLK, y0))
    rays = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(rays)
    cx, cy = 540, 980
    for k in range(16):
        a0 = k * 2 * math.pi / 16; a1 = a0 + 0.12
        d.polygon([(cx, cy), (cx + 1600 * math.cos(a0), cy + 1600 * math.sin(a0)), (cx + 1600 * math.cos(a1), cy + 1600 * math.sin(a1))],
                  fill=ray_col + (38,))
    img.alpha_composite(rays.filter(ImageFilter.GaussianBlur(6)))
    r = random.Random(seed)
    for k in range(10):
        b = S.WOODS[k % len(S.WOODS)] if k % 2 else S.STONES[k % len(S.STONES)]
        x = r.choice([r.uniform(40, 200), r.uniform(880, 1040)]); y = r.uniform(500, 1450)
        S.paste_center(img, b.convert('RGBA'), x, y, scale=r.uniform(0.6, 1.0), angle=r.uniform(-0.8, 0.8))
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
    S.glow_fast(img, x, H + 420 - 28 * 32, 260, (40, 160, 90), 0.25)


def stamp(img, x=860, y=760):
    st = S.fancy_text('CAP. 4', 64, top=(140, 255, 190), bot=(30, 170, 100), outline=(5, 50, 25))
    S.paste_center(img, st, x, y, angle=-0.12)


def v_a():
    """¿CÓMO FUNCIONA UN DIODO? + diodo brillante con corriente"""
    img = base()
    S.paste_center(img, S.fancy_text('¿CÓMO FUNCIONA', 104, top=(255, 245, 120), bot=(255, 170, 20)), 540, 300, angle=0.02)
    S.paste_center(img, S.fancy_text('UN DIODO?', 150, top=(140, 255, 190), bot=(30, 170, 100), outline=(5, 50, 25)), 540, 450, angle=-0.02)
    part = DD.diode_part(1.0, 1.0)
    glow_paste(img, part, 540, 830, scale=1.25, angle=-0.12)
    l = D.L(W, 300)
    for k in range(7):
        x = 120 + k * 130
        l.rect([x - 14, 136, x + 14, 164], fill=D.CURR + (255,))
    S.paste_center(img, l.done(), 540, 830, angle=-0.12)
    S.paste_center(img, D.label('SOLO PASA →', 44, fill=DD.GREEN), 540, 1010)
    stamp(img, 870, 640)
    character(img, 'sorpresa')
    return img


def v_b():
    """¡SOLO PASA PARA UN LADO! + la puerta-diodo y ¡BONK!"""
    img = base((150, 255, 190), 7)
    S.paste_center(img, S.fancy_text('¡SOLO DEJA', 120, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 290, angle=0.02)
    S.paste_center(img, S.fancy_text('PASAR POR UN LADO!', 92, top=(255, 245, 120), bot=(255, 150, 20)), 540, 420, angle=-0.02)
    tri = DD.door_triangle(); fl = DD.door_flap()
    S.paste_center(img, tri, 430, 860, scale=0.9)
    S.paste_center(img, fl, 580, 860, scale=0.9)
    S.paste_center(img, DD.stopper(), 545, 1080, scale=0.9)
    S.paste_center(img, DD.bonk_text(), 780, 640, scale=1.3, angle=-0.15)
    S.paste_center(img, DD.symbol('normal', 90, (120, 255, 170)), 820, 900, angle=0.1)
    stamp(img, 220, 640)
    character(img, 'mareado', x=620, sx=0.8, sy=1.05)
    return img


def v_c():
    """5 TIPOS DE DIODOS + tarjetas"""
    img = base((255, 200, 120), 9)
    S.paste_center(img, S.fancy_text('¡5 TIPOS', 130, top=(255, 245, 120), bot=(255, 170, 20)), 540, 280, angle=0.02)
    S.paste_center(img, S.fancy_text('DE DIODOS!', 120, top=(140, 255, 190), bot=(30, 170, 100), outline=(5, 50, 25)), 540, 420, angle=-0.02)
    t = 1.0
    cards = [DD.card_led(t, 0.0, 1.0), DD.card_zener(t, 1.0), DD.card_schottky(t, 1.0, 1.0), DD.card_foto(1.0, 1, 1, 1, 0)]
    pos = [(305, 640), (775, 640), (305, 910), (775, 910)]
    for c, p in zip(cards, pos):
        S.paste_center(img, c, p[0], p[1], scale=1.0, angle=random.Random(p[0] + p[1]).uniform(-0.06, 0.06))
    stamp(img, 540, 1110)
    character(img, 'feliz')
    return img


def v_d():
    """¿QUÉ HAY DENTRO DE UN DIODO? + unión P-N"""
    img = base((180, 160, 255), 3)
    S.paste_center(img, S.fancy_text('¿QUÉ HAY DENTRO', 100, top=(255, 255, 255), bot=(200, 210, 230), outline=(30, 30, 40)), 540, 290)
    S.paste_center(img, S.fancy_text('DE UN DIODO?', 130, top=(255, 245, 120), bot=(255, 170, 20)), 540, 430, angle=-0.02)
    fr = DD.pn_frame(1.0, 1.0)
    S.paste_center(img, fr, 540, 800, scale=1.05)
    oy = 800 - (DD.PN_Y0 + DD.PN_Y1) / 2
    S.paste_center(img, DD.barrier_img(80), 540, 800, scale=1.05)
    for c in DD.HOLES:
        if abs(c['x'] - DD.PN_MID) > 50:
            S.paste_center(img, DD.hole_img(), 540 + (c['x'] - 540) * 1.05, c['y'] + oy)
    for c in DD.ELECS:
        if abs(c['x'] - DD.PN_MID) > 50:
            S.paste_center(img, DD.elec_img(), 540 + (c['x'] - 540) * 1.05, c['y'] + oy)
    stamp(img, 870, 1040)
    character(img, 'curioso')
    return img


def v_e():
    """EL DIODO + bombillo encendido y símbolo gigante"""
    img = base((255, 230, 120), 5)
    S.paste_center(img, S.fancy_text('EL DIODO', 170, top=(140, 255, 190), bot=(30, 170, 100), outline=(5, 50, 25)), 540, 330, angle=-0.03)
    S.paste_center(img, S.fancy_text('explicado con bloques', 64, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40)), 540, 470)
    glow_paste(img, DD.symbol('normal', 200, (120, 255, 170)), 400, 800, times=3)
    glow_paste(img, DD.bulb_img(1.0), 860, 780, scale=1.2, times=1)
    stamp(img, 200, 1040)
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
