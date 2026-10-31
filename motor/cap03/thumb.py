#!/usr/bin/env python3
# Miniatura vertical del capítulo 3
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
import char3d as C

W, H = 1080, 1920
img = S.lit_room().convert('RGBA')
# rellenar arriba y abajo con bloques oscuros
for y0 in range(0, S.ROOM_T, S.BLK):
    for c in range(S.NCOL):
        t = S.STONES[(c + y0) % len(S.STONES)].point(lambda v: int(v * 0.45))
        img.paste(t, (S.X0 + c * S.BLK, y0 - (S.BLK - S.ROOM_T % S.BLK)))
for y0 in range(S.FLOOR_B, H, S.BLK):
    for c in range(S.NCOL):
        t = S.WOODS[(c + y0) % len(S.WOODS)].point(lambda v: int(v * 0.4))
        img.paste(t, (S.X0 + c * S.BLK, y0))
# rayos de luz
rays = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(rays)
cx, cy = 540, 980
for k in range(16):
    a0 = k * 2 * math.pi / 16
    a1 = a0 + 0.12
    d.polygon([(cx, cy), (cx + 1600 * math.cos(a0), cy + 1600 * math.sin(a0)), (cx + 1600 * math.cos(a1), cy + 1600 * math.sin(a1))],
              fill=(255, 220, 140, 38))
rays = rays.filter(ImageFilter.GaussianBlur(6))
img.alpha_composite(rays)
# bloques flotando
r = random.Random(4)
for k in range(12):
    b = S.WOODS[k % len(S.WOODS)] if k % 2 else S.STONES[k % len(S.STONES)]
    x = r.choice([r.uniform(40, 220), r.uniform(860, 1040)]); y = r.uniform(450, 1500)
    S.paste_center(img, b.convert('RGBA'), x, y, scale=r.uniform(0.6, 1.0), angle=r.uniform(-0.8, 0.8))
# título
t1 = S.fancy_text('¿LA GRAVEDAD', 120, top=(255, 245, 120), bot=(255, 170, 20))
t2 = S.fancy_text('ES UN', 96, top=(255, 255, 255), bot=(210, 215, 230), outline=(30, 30, 40))
t3 = S.fancy_text('COMPONENTE?', 120, top=(255, 255, 255), bot=(200, 210, 230), outline=(30, 30, 40))
S.paste_center(img, t1, 540, 300, angle=0.03)
S.paste_center(img, t2, 540, 430)
S.paste_center(img, t3, 540, 545, angle=-0.02)
# diagrama del sensor inclinado y brillante
lay = D.tube_layer(D.BALL_TOUCH[0], D.BALL_TOUCH[1], 1.0, closed=1.0, flash=1.0)
glow_l = lay.filter(ImageFilter.GaussianBlur(18))
im, off = D.rotated_about(lay, (D.TCX, D.TCY), 28, 1.0)
gl, _ = D.rotated_about(glow_l, (D.TCX, D.TCY), 28, 1.0)
img.alpha_composite(gl, (int(560 + off[0]), int(900 + off[1])))
img.alpha_composite(gl, (int(560 + off[0]), int(900 + off[1])))
img.alpha_composite(im, (int(560 + off[0]), int(900 + off[1])))
S.paste_center(img, D.gravity_arrow(260, 1.0), 130, 900)
# personaje en primer plano, sorprendido
ch = C.Character()
p = C.Pose(expr='sorpresa', rarm=(2.4, 0, 0.5), relbow=0.6, larm=(0.4, 0, 0.5), lelbow=0.9, head=(0.1, -0.2, 0.08))
ch.render(img, p, dict(scale=32, ox=560, oy=H + 420, view_yaw=0.25), light=1.0, t=0.2)
S.glow_fast(img, 560, H + 420 - 28 * 32, 260, (40, 160, 90), 0.25)
# sello CAP. 3
st = S.fancy_text('CAP. 3', 64, top=(140, 230, 255), bot=(40, 120, 255), outline=(10, 30, 70))
S.paste_center(img, st, 860, 700, angle=-0.12)
img.convert('RGB').save('out/portada_cap03.jpg', quality=92)
print('ok')
