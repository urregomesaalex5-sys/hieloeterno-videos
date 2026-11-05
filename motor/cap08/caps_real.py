# Condensadores con aspecto realista (cilindros con sombreado, forro impreso, tapa con cruz).
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S

SS = 2
_cache = {}
def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]

def _shade_cols(w, spec=0.28):
    u = (np.arange(w) + 0.5) / w
    s = 0.38 + 0.72 * np.sin(np.pi * u) ** 0.55
    s += 0.55 * np.exp(-((u - spec) / 0.045) ** 2) + 0.15 * np.exp(-((u - 0.82) / 0.03) ** 2)
    return s

def _cyl(w, h, rgb, spec=0.28):
    """cuadro w x h (RGB float) con el sombreado de un cilindro"""
    s = _shade_cols(w, spec)
    arr = np.ones((h, w, 3), np.float32) * np.array(rgb, np.float32)
    return arr * s[None, :, None]

def _ellipse_mask(size, box):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).ellipse(box, fill=255)
    return m

def _text_img(txt, size, col):
    f = S.font(size, True)
    l, t, r, b = f.getbbox(txt)
    im = Image.new('RGBA', (r - l + 8, b - t + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - l, 4 - t), txt, font=f, fill=col)
    return im

def elec_cap(h=300, swell=0.0, stripe_hl=0.0, top_off=0.0, q=False,
             sleeve=(28, 52, 120), stripe=(170, 200, 240), label=('1000µF', '16V')):
    key = ('elec', h, round(swell, 2), round(stripe_hl, 1), round(top_off, 2), q, sleeve)
    def mk():
        H0 = h * SS
        bw = int(0.25 * H0)                 # radio del cuerpo
        bh = int(0.70 * H0)                 # alto del cuerpo
        ry = max(4, int(bw * 0.30))         # elipse de la tapa
        cw = int(2 * bw * 1.35 + 240 * SS / 2)
        chh = int(H0 + 160 * SS)
        cx = cw // 2
        top = int(60 * SS + ry * (1 + 1.2 * swell))
        bot = top + bh
        im = Image.new('RGBA', (cw, chh), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        # patas (la + es más larga)
        lc = (196, 200, 210, 255)
        lw = max(3, int(5 * SS))
        d.line([(cx - bw * 0.42, bot), (cx - bw * 0.42, chh - 6 * SS)], fill=lc, width=lw)
        d.line([(cx + bw * 0.42, bot), (cx + bw * 0.42, chh - 50 * SS)], fill=lc, width=lw)
        d.line([(cx - bw * 0.42 + lw * 0.3, bot), (cx - bw * 0.42 + lw * 0.3, chh - 6 * SS)], fill=(240, 242, 248, 255), width=max(1, lw // 3))
        # tapón de goma abajo
        d.ellipse([cx - bw * 0.86, bot - ry * 0.7, cx + bw * 0.86, bot + ry * 0.9], fill=(38, 38, 42, 255))
        # cuerpo (se infla arriba)
        body_w = 2 * bw
        body = _cyl(body_w, bh + ry, sleeve)
        # franja del negativo
        u = (np.arange(body_w) + 0.5) / body_w
        smask = (u > 0.66) & (u < 0.86)
        sc = np.array(stripe if stripe_hl < 0.5 else (255, 236, 120), np.float32)
        body[:, smask] = sc * _shade_cols(body_w)[smask][None, :, None] / 1.0
        bimg = Image.fromarray(np.clip(body, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
        # forma: rectángulo + elipse abajo, con la parte de arriba inflada
        mask = Image.new('L', (body_w, bh + ry), 0)
        md = ImageDraw.Draw(mask)
        md.rectangle([0, 0, body_w, bh], fill=255)
        md.ellipse([0, bh - ry, body_w, bh + ry], fill=255)
        bimg.putalpha(mask)
        if swell > 0:
            # abombar la parte de arriba
            arr = np.array(bimg)
            out = np.zeros_like(arr)
            hh = arr.shape[0]
            for y in range(hh):
                v = 1 - y / hh
                k = 1 + 0.22 * swell * max(0.0, math.sin(min(1.0, v * 1.7) * math.pi / 2))
                row = Image.fromarray(arr[y:y + 1]).resize((int(body_w * k), 1))
                ra = np.array(row)
                x0 = (body_w - ra.shape[1]) // 2
                if x0 >= 0:
                    out[y, x0:x0 + ra.shape[1]] = ra
                else:
                    out[y] = ra[:, -x0:-x0 + body_w]
            big = Image.new('RGBA', (int(body_w * 1.3), hh), (0, 0, 0, 0))
            big.paste(Image.fromarray(out), ((big.size[0] - body_w) // 2, 0))
            bimg = Image.fromarray(np.array(big)) 
            im.alpha_composite(bimg, (int(cx - big.size[0] / 2), top))
        else:
            im.alpha_composite(bimg, (cx - bw, top))
        # signos − en la franja
        for k in range(4):
            yy = top + bh * (0.18 + 0.2 * k)
            xs = cx - bw + body_w * 0.76
            d.line([(xs - 9 * SS, yy), (xs + 9 * SS, yy)], fill=(20, 30, 70, 255), width=int(4 * SS))
        # texto del forro (vertical)
        if not q:
            t1 = _text_img(label[0], int(bw * 0.42), (235, 240, 255, 235)).rotate(90, expand=True)
            t2 = _text_img(label[1], int(bw * 0.32), (235, 240, 255, 220)).rotate(90, expand=True)
            im.alpha_composite(t1, (int(cx - bw * 0.45 - t1.size[0] / 2), int(top + bh * 0.5 - t1.size[1] / 2)))
            im.alpha_composite(t2, (int(cx - bw * 0.02 - t2.size[0] / 2), int(top + bh * 0.5 - t2.size[1] / 2)))
        # anillo del forro doblado arriba
        dome = 1 + 2.2 * swell
        if top_off < 0.01:
            d.ellipse([cx - bw * (1 + 0.2 * swell), top - ry * dome, cx + bw * (1 + 0.2 * swell), top + ry], fill=sleeve + (255,))
            # tapa de aluminio (gradiente)
            tw = int(2 * bw * 0.86 * (1 + 0.2 * swell)); th = int(2 * ry * 0.8 * dome)
            cap = _cyl(tw, th, (205, 210, 220), spec=0.35)
            yy = np.linspace(-1, 1, th)[:, None]
            cap *= (1.05 - 0.25 * yy)[..., None]
            ci = Image.fromarray(np.clip(cap, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
            ci.putalpha(_ellipse_mask((tw, th), [0, 0, tw - 1, th - 1]))
            im.alpha_composite(ci, (int(cx - tw / 2), int(top - ry * 0.8 * dome)))
            # cruz (válvula) en perspectiva
            ccx, ccy = cx, top - ry * 0.8 * dome + th / 2
            vc = (120, 126, 138, 255)
            d.line([(ccx - tw * 0.32, ccy), (ccx + tw * 0.32, ccy)], fill=vc, width=int(4 * SS))
            d.line([(ccx, ccy - th * 0.32), (ccx, ccy + th * 0.32)], fill=vc, width=int(4 * SS))
            if swell > 0.5:
                # la cruz se abre
                d.line([(ccx - tw * 0.2, ccy - 2), (ccx + tw * 0.2, ccy - 2)], fill=(60, 40, 30, 255), width=int(5 * SS * swell))
        else:
            # sin tapa: hueco oscuro y tapa volando
            d.ellipse([cx - bw, top - ry, cx + bw, top + ry], fill=(40, 34, 30, 255))
            off = top_off * 180 * SS
            a = int(255 * max(0, 1 - top_off * 1.3))
            d.ellipse([cx - bw * 0.86 + off * 0.3, top - ry - off, cx + bw * 0.86 + off * 0.3, top + ry * 0.6 - off], fill=(205, 210, 220, a))
        if q:
            qt = _text_img('?', int(bh * 0.55), (255, 255, 255, 255))
            stroke = qt.filter(ImageFilter.MaxFilter(9))
            arr = np.array(stroke); arr[..., :3] = (15, 25, 60); stroke = Image.fromarray(arr)
            im.alpha_composite(stroke, (int(cx - qt.size[0] / 2), int(top + bh * 0.45 - qt.size[1] / 2)))
            im.alpha_composite(qt, (int(cx - qt.size[0] / 2), int(top + bh * 0.45 - qt.size[1] / 2)))
        return im.resize((cw // SS, chh // SS), Image.LANCZOS)
    return cached(key, mk)


def ceramic_cap(size=220, flip=False):
    def mk():
        sz = size * SS
        cw, chh = sz + 40 * SS, int(sz * 1.55)
        cx, cy = cw / 2, sz * 0.5 + 10 * SS
        r = sz * 0.42
        im = Image.new('RGBA', (cw, chh), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        lc = (196, 200, 210, 255)
        for sx in (-0.35, 0.35):
            d.line([(cx + r * sx, cy + r * 0.5), (cx + r * sx * 1.1, cy + r * 0.95), (cx + r * sx * 1.1, chh - 6 * SS)], fill=lc, width=int(5 * SS))
        # gota de recubrimiento hacia las patas
        d.polygon([(cx - r * 0.45, cy + r * 0.5), (cx + r * 0.45, cy + r * 0.5), (cx + r * 0.3, cy + r * 1.08), (cx - r * 0.3, cy + r * 1.08)], fill=(200, 110, 40, 255))
        # disco con sombreado radial
        w2, h2 = int(2 * r), int(2 * r * 0.92)
        yy, xx = np.mgrid[0:h2, 0:w2].astype(np.float32)
        nx = (xx - w2 * 0.38) / (w2 / 2); ny = (yy - h2 * 0.32) / (h2 / 2)
        s = np.clip(1.25 - 0.55 * np.sqrt(nx ** 2 + ny ** 2), 0.45, 1.25)
        disc = np.ones((h2, w2, 3), np.float32) * np.array((214, 112, 36), np.float32) * s[..., None]
        di = Image.fromarray(np.clip(disc, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
        di.putalpha(_ellipse_mask((w2, h2), [0, 0, w2 - 1, h2 - 1]))
        im.alpha_composite(di, (int(cx - r), int(cy - r * 0.92)))
        d.ellipse([cx - r * 0.55, cy - r * 0.62, cx - r * 0.18, cy - r * 0.35], fill=(255, 210, 160, 90))
        f = S.font(int(size * 0.17 * SS), True)
        d.text((cx, cy + 6 * SS), '104', font=f, fill=(90, 40, 8, 255), anchor='mm')
        return im.resize((cw // SS, chh // SS), Image.LANCZOS)
    return cached(('cer', size, flip), mk)


def supercap(h=430):
    def mk():
        H0 = h * SS
        bw = int(0.36 * H0); bh = int(0.8 * H0); ry = int(bw * 0.28)
        cw, chh = int(2 * bw + 60 * SS), int(H0 + 80 * SS)
        cx = cw // 2; top = int(70 * SS); bot = top + bh
        im = Image.new('RGBA', (cw, chh), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        body = _cyl(2 * bw, bh + ry, (34, 36, 44))
        u = (np.arange(2 * bw) + 0.5) / (2 * bw)
        band = np.zeros((bh + ry,), bool); band[int(bh * 0.3):int(bh * 0.72)] = True
        body[band] = np.array((40, 120, 235), np.float32) * _shade_cols(2 * bw)[None, :, None]
        bi = Image.fromarray(np.clip(body, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
        m = Image.new('L', (2 * bw, bh + ry), 0); md = ImageDraw.Draw(m)
        md.rectangle([0, 0, 2 * bw, bh], fill=255); md.ellipse([0, bh - ry, 2 * bw, bh + ry], fill=255)
        bi.putalpha(m)
        im.alpha_composite(bi, (cx - bw, top))
        d.ellipse([cx - bw, top - ry, cx + bw, top + ry], fill=(150, 156, 166, 255))
        d.ellipse([cx - bw * 0.9, top - ry * 0.85, cx + bw * 0.9, top + ry * 0.85], fill=(185, 190, 200, 255))
        # bornes
        for sx, col in ((-0.4, (230, 190, 70)), (0.4, (200, 204, 214))):
            d.rounded_rectangle([cx + bw * sx - 18 * SS, top - ry * 0.3 - 48 * SS, cx + bw * sx + 18 * SS, top - ry * 0.3], 6 * SS, fill=col + (255,))
        f1 = S.font(int(bw * 0.3), True); f2 = S.font(int(bw * 0.2), True)
        d.text((cx - bw * 0.12, top + bh * 0.45), 'SUPER', font=f1, fill=(255, 255, 255, 255), anchor='mm')
        d.text((cx - bw * 0.12, top + bh * 0.6), '3000 F · 2,7 V', font=f2, fill=(220, 236, 255, 255), anchor='mm')
        return im.resize((cw // SS, chh // SS), Image.LANCZOS)
    return cached(('super', h), mk)
