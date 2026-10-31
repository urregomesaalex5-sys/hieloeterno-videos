# Personaje HieloEterno en 3D por software (proyección ortográfica, caras texturizadas con la skin).
# Unidades: píxeles de la skin. El personaje mide 32 de alto (pies en y=0).
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SKIN_PATH = __file__.rsplit('/', 1)[0] + '/../skin/skin.png'
SKIN = Image.open(SKIN_PATH).convert('RGBA')

# ---------- UV de Minecraft (formato 64x64, brazos de 4) ----------
def box_uv(u, v, w, h, d):
    """Rectángulos (x0,y0,x1,y1) de las 6 caras para una caja con origen UV (u,v)."""
    return {
        'top':    (u + d, v, u + d + w, v + d),
        'bottom': (u + d + w, v, u + d + 2 * w, v + d),
        'right':  (u, v + d, u + d, v + d + h),          # lado -x (derecha del personaje)
        'front':  (u + d, v + d, u + d + w, v + d + h),
        'left':   (u + d + w, v + d, u + 2 * d + w, v + d + h),  # lado +x
        'back':   (u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h),
    }

UV = {
    'head': (box_uv(0, 0, 8, 8, 8), box_uv(32, 0, 8, 8, 8)),
    'body': (box_uv(16, 16, 8, 12, 4), box_uv(16, 32, 8, 12, 4)),
    'rarm': (box_uv(40, 16, 4, 12, 4), box_uv(40, 32, 4, 12, 4)),
    'larm': (box_uv(32, 48, 4, 12, 4), box_uv(48, 48, 4, 12, 4)),
    'rleg': (box_uv(0, 16, 4, 12, 4), box_uv(0, 32, 4, 12, 4)),
    'lleg': (box_uv(16, 48, 4, 12, 4), box_uv(0, 48, 4, 12, 4)),
}

_tex_cache = {}
def crop_tex(rect, part=None):
    """part: None (completo), 'upper' (filas 0-6) o 'lower' (filas 6-12) para caras laterales de extremidades."""
    key = (rect, part)
    if key in _tex_cache:
        return _tex_cache[key]
    x0, y0, x1, y1 = rect
    if part == 'upper':
        y1 = y0 + (y1 - y0) // 2
    elif part == 'lower':
        y0 = y0 + (y1 - y0) // 2
    t = np.array(SKIN.crop((x0, y0, x1, y1)), dtype=np.float32)
    _tex_cache[key] = t
    return t

# ---------- Pantalla de TV (cara) ----------
SCR = 16  # resolución por píxel de skin para la cara
YEL = (248, 250, 36)
GRN = (80, 255, 140)
PINK = (255, 90, 160)

def make_screen(expr='normal', mouth=0.0, t=0.0, blink=0.0, look=(0.0, 0.0)):
    """Textura del frente de la cabeza (8x8 skin) a 16x con la pantalla dibujada.
    expr: normal, feliz, sorpresa, curioso, mareado, corazon, guino, pensando, asustado, apagado
    mouth: 0..1 amplitud de la voz. look: desplazamiento de ojos (-1..1)."""
    base = SKIN.crop((8, 8, 16, 16)).resize((8 * SCR, 8 * SCR), Image.NEAREST)
    im = base.copy()
    d = ImageDraw.Draw(im)
    # zona de pantalla: columnas 1..7, filas 3..6 (el marco gris del sombrero cubre col 0,7 y fila 6)
    sx0, sy0, sx1, sy1 = 1 * SCR, 3 * SCR, 7 * SCR, 6 * SCR
    if expr == 'apagado':
        d.rectangle([sx0, sy0, sx1, sy1], fill=(18, 20, 24, 255))
        return im
    d.rectangle([sx0, sy0, sx1, sy1], fill=(22, 30, 34, 255))
    # líneas de escaneo sutiles
    for yy in range(sy0, sy1, 4):
        d.line([sx0, yy, sx1, yy], fill=(28, 40, 44, 255))
    lx, ly = look
    ex = int(lx * 6); ey = int(ly * 4)
    e1 = (sx0 + 12 + ex, sy0 + 8 + ey)       # ojo izquierdo (en pantalla)
    e2 = (sx1 - 12 - 16 + ex, sy0 + 8 + ey)  # ojo derecho
    es = 16
    def eye_sq(p, s=es, h=None, col=YEL):
        h = s if h is None else h
        d.rectangle([p[0], p[1], p[0] + s - 1, p[1] + h - 1], fill=col + (255,))
    blinkh = max(2, int(es * (1 - blink)))
    if expr in ('normal', 'hablando'):
        eye_sq(e1, h=blinkh); eye_sq(e2, h=blinkh)
    elif expr == 'feliz':
        for p in (e1, e2):
            d.line([p[0], p[1] + 12, p[0] + 8, p[1] + 2, p[0] + 16, p[1] + 12], fill=YEL + (255,), width=5)
    elif expr == 'sorpresa' or expr == 'asustado':
        for p in (e1, e2):
            d.rectangle([p[0] - 3, p[1] - 4, p[0] + 19, p[1] + 18], fill=YEL + (255,))
            d.rectangle([p[0] + 4, p[1] + 3, p[0] + 12, p[1] + 11], fill=(22, 30, 34, 255))
    elif expr == 'curioso':
        eye_sq(e1, s=12, h=max(2, int(10 * (1 - blink))))
        d.rectangle([e2[0] - 3, e2[1] - 4, e2[0] + 19, e2[1] + 18], fill=YEL + (255,))
    elif expr == 'mareado':
        for p in (e1, e2):
            c = (p[0] + 8, p[1] + 7)
            for k in range(3):
                r = 3 + k * 4
                a0 = (t * 600 + k * 90) % 360
                d.arc([c[0] - r, c[1] - r, c[0] + r, c[1] + r], a0, a0 + 250, fill=YEL + (255,), width=3)
    elif expr == 'corazon':
        for p in (e1, e2):
            cx, cy = p[0] + 8, p[1] + 8
            pul = 1.0 + 0.15 * math.sin(t * 12)
            r = 5 * pul
            d.ellipse([cx - 2 * r, cy - 1.6 * r, cx, cy + 0.4 * r], fill=PINK + (255,))
            d.ellipse([cx, cy - 1.6 * r, cx + 2 * r, cy + 0.4 * r], fill=PINK + (255,))
            d.polygon([(cx - 2 * r, cy - 0.4 * r), (cx + 2 * r, cy - 0.4 * r), (cx, cy + 2.2 * r)], fill=PINK + (255,))
    elif expr == 'guino':
        eye_sq(e1)
        d.line([e2[0], e2[1] + 10, e2[0] + 16, e2[1] + 10], fill=YEL + (255,), width=5)
    elif expr == 'pensando':
        eye_sq((e1[0] + 4, e1[1] - 2), s=12, h=8); eye_sq((e2[0] + 4, e2[1] - 2), s=12, h=8)
    # boca de osciloscopio
    my = sy1 - 13
    mx0, mx1 = sx0 + 14, sx1 - 14
    pts = []
    n = 40
    amp = 1.2 + 9.0 * mouth
    if expr == 'sorpresa':
        d.ellipse([(mx0 + mx1) / 2 - 7, my - 8, (mx0 + mx1) / 2 + 7, my + 6], outline=GRN + (255,), width=3)
    else:
        for i in range(n + 1):
            x = mx0 + (mx1 - mx0) * i / n
            ph = i / n
            env = math.sin(math.pi * ph)
            y = my + amp * env * math.sin(ph * 6 * math.pi + t * 25) * (0.6 + 0.4 * math.sin(ph * 17 + t * 9))
            if expr == 'feliz' or expr == 'corazon':
                y += -5 * math.sin(math.pi * ph) * 0.0 + 4 * (2 * (ph - 0.5)) ** 2 * 1.5 - 3
            pts.append((x, y))
        d.line(pts, fill=GRN + (255,), width=3)
    return im


# ---------- Matemática ----------
def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

def rot(px=0.0, py=0.0, pz=0.0):
    return rot_y(py) @ rot_x(px) @ rot_z(pz)


class Pose:
    """Todos los ángulos en radianes. Brazos: px>0 levanta hacia adelante, pz abre hacia afuera."""
    def __init__(self, **kw):
        self.x = 0.0; self.y = 0.0; self.z = 0.0   # posición del personaje (pies)
        self.yaw = 0.0                               # giro del cuerpo
        self.lean = 0.0; self.roll = 0.0             # inclinación del torso
        self.body_roll = 0.0                         # rotación de todo el cuerpo (caídas, flotar)
        self.body_pitch = 0.0
        self.sx = 1.0; self.sy = 1.0                 # estirar y aplastar
        self.head = (0.0, 0.0, 0.0)                  # pitch, yaw, roll
        self.rarm = (0.0, 0.0, 0.0); self.larm = (0.0, 0.0, 0.0)   # hombro pitch, yaw, roll
        self.relbow = 0.0; self.lelbow = 0.0
        self.rleg = (0.0, 0.0, 0.0); self.lleg = (0.0, 0.0, 0.0)
        self.rknee = 0.0; self.lknee = 0.0
        self.rarm_len = 1.0; self.larm_len = 1.0     # brazos de goma
        self.expr = 'normal'; self.mouth = 0.0; self.blink = 0.0; self.look = (0.0, 0.0)
        self.hat_bounce = 0.0
        for k, v in kw.items():
            setattr(self, k, v)

    def copy(self):
        p = Pose()
        p.__dict__.update(self.__dict__)
        return p


def _faces_for_box(name, mn, mx, uvs, M, origin, inflate, seg=None, screen=None, overlay=False):
    """Genera caras (puntos 3D en mundo, textura, normal) de una caja."""
    x0, y0, z0 = mn; x1, y1, z1 = mx
    x0 -= inflate; y0 -= inflate; z0 -= inflate
    x1 += inflate; y1 += inflate; z1 += inflate
    # esquinas en orden (arriba-izq, arriba-der, abajo-der, abajo-izq) vistas desde fuera
    F = {
        'front':  [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
        'back':   [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)],
        'right':  [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)],
        'left':   [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)],
        'top':    [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
        'bottom': [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)],
    }
    out = []
    for fname, pts in F.items():
        if seg == 'upper' and fname == 'bottom':
            continue
        if seg == 'lower' and fname == 'top':
            continue
        rect = uvs[fname]
        part = None
        if seg and fname not in ('top', 'bottom'):
            part = seg
        if screen is not None and fname == 'front' and not overlay:
            tex = screen
        else:
            tex = crop_tex(rect, part)
        P = np.array(pts, dtype=np.float64) @ M.T + origin
        out.append((name + '.' + fname + ('.o' if overlay else ''), P, tex, fname, screen is not None and fname == 'front' and not overlay))
    return out


class Character:
    def __init__(self):
        self.screen_cache = {}

    def build(self, pose, screen_img):
        """Devuelve lista de caras en coordenadas de mundo (unidades skin)."""
        faces = []
        self.points = {}
        S = np.diag([pose.sx, pose.sy, pose.sx])
        Rbody = rot(pose.body_pitch, pose.yaw, pose.body_roll)
        base_M = Rbody @ S
        base_o = np.array([pose.x, pose.y, pose.z])
        # cadera
        hip_o = base_o + base_M @ np.array([0, 12.0, 0])
        Mt = base_M @ rot(pose.lean, 0, pose.roll)
        # torso
        faces += _faces_for_box('body', (-4, 0, -2), (4, 12, 2), UV['body'][0], Mt, hip_o, 0.0)
        faces += _faces_for_box('body', (-4, 0, -2), (4, 12, 2), UV['body'][1], Mt, hip_o, 0.25, overlay=True)
        # cabeza
        neck_o = hip_o + Mt @ np.array([0, 12.0, 0])
        Mh = Mt @ rot(*pose.head)
        self.points['head'] = neck_o + Mh @ np.array([0, 4.0, 4.0])
        faces += _faces_for_box('head', (-4, 0, -4), (4, 8, 4), UV['head'][0], Mh, neck_o, 0.0, screen=screen_img)
        hb = np.array([0, pose.hat_bounce, 0])
        faces += _faces_for_box('head', (-4, 0, -4), (4, 8, 4), UV['head'][1], Mh, neck_o + Mh @ hb, 0.5, overlay=True, screen=screen_img)
        # brazos: derecho (lado -x), izquierdo (+x)
        for side, sgn, ang, elbow, ln in (('rarm', -1, pose.rarm, pose.relbow, pose.rarm_len),
                                          ('larm', 1, pose.larm, pose.lelbow, pose.larm_len)):
            px_, py_, pz_ = ang
            sh_o = hip_o + Mt @ np.array([sgn * 6.0, 10.0, 0])
            Ma = Mt @ rot(-px_, py_, sgn * pz_) @ np.diag([1, ln, 1])
            uvb, uvo = UV[side]
            faces += _faces_for_box(side + 'U', (-2, -4.2, -2), (2, 2, 2), uvb, Ma, sh_o, 0.0, seg='upper')
            faces += _faces_for_box(side + 'U', (-2, -4.2, -2), (2, 2, 2), uvo, Ma, sh_o, 0.25, seg='upper', overlay=True)
            el_o = sh_o + Ma @ np.array([0, -4.0, 0])
            Mf = Ma @ rot(-elbow, 0, 0)
            faces += _faces_for_box(side + 'L', (-2, -6, -2), (2, 0.2, 2), uvb, Mf, el_o, 0.0, seg='lower')
            faces += _faces_for_box(side + 'L', (-2, -6, -2), (2, 0.2, 2), uvo, Mf, el_o, 0.25, seg='lower', overlay=True)
            self.points[side[0] + 'hand'] = el_o + Mf @ np.array([0, -5.5, 0])
        for side, sgn, ang, knee in (('rleg', -1, pose.rleg, pose.rknee), ('lleg', 1, pose.lleg, pose.lknee)):
            px_, py_, pz_ = ang
            hp_o = hip_o + Mt @ np.array([sgn * 2.0, 0.0, 0]) if False else hip_o + base_M @ np.array([sgn * 2.0, 0.0, 0])
            Ml = base_M @ rot(-px_, py_, sgn * pz_)
            uvb, uvo = UV[side]
            faces += _faces_for_box(side + 'U', (-2, -6.2, -2), (2, 0, 2), uvb, Ml, hp_o, 0.0, seg='upper')
            faces += _faces_for_box(side + 'U', (-2, -6.2, -2), (2, 0, 2), uvo, Ml, hp_o, 0.25, seg='upper', overlay=True)
            kn_o = hp_o + Ml @ np.array([0, -6.0, 0])
            Mk = Ml @ rot(knee, 0, 0)
            faces += _faces_for_box(side + 'L', (-2, -6, -2), (2, 0.2, 2), uvb, Mk, kn_o, 0.0, seg='lower')
            faces += _faces_for_box(side + 'L', (-2, -6, -2), (2, 0.2, 2), uvo, Mk, kn_o, 0.25, seg='lower', overlay=True)
        return faces

    def render(self, canvas, pose, cam, light=1.0, glow=0.0, t=0.0, tint=None):
        """canvas: Image RGBA. cam: dict(scale, ox, oy, view_yaw, view_pitch).
        light: multiplicador de iluminación. glow: brillo verde de la pantalla (0..1)."""
        screen = make_screen(pose.expr, pose.mouth, t, pose.blink, pose.look)
        sarr = np.array(screen, dtype=np.float32)
        faces = self.build(pose, sarr)
        V = rot(cam.get('view_pitch', 0.0), cam.get('view_yaw', 0.0), 0)
        sc = cam['scale']; ox = cam['ox']; oy = cam['oy']
        L = np.array([0.35, 0.8, 0.5]); L = L / np.linalg.norm(L)
        draw_list = []
        for name, P, tex, fname, emissive in faces:
            Pv = P @ V.T
            q = np.stack([ox + Pv[:, 0] * sc, oy - Pv[:, 1] * sc], axis=1)
            # backface culling por orientación 2D
            a = (q[1, 0] - q[0, 0]) * (q[3, 1] - q[0, 1]) - (q[1, 1] - q[0, 1]) * (q[3, 0] - q[0, 0])
            if a <= 0.5:
                continue
            n = np.cross(Pv[1] - Pv[0], Pv[3] - Pv[0]); nn = np.linalg.norm(n)
            if nn > 0:
                n = n / nn
            shade = 0.55 + 0.45 * max(0.0, float(n @ L))
            if fname == 'top':
                shade = min(1.0, shade + 0.08)
            depth = Pv[:, 2].mean() + (0.01 if name.endswith('.o') else 0)
            draw_list.append((depth, q, tex, shade, emissive))
        draw_list.sort(key=lambda r: r[0])
        self.screen_pts = {}
        for k, P in self.points.items():
            Pv = V @ P
            self.screen_pts[k] = (ox + Pv[0] * sc, oy - Pv[1] * sc)
        for depth, q, tex, shade, emissive in draw_list:
            th, tw = tex.shape[0], tex.shape[1]
            t2 = tex.copy()
            k = shade * light
            if emissive:
                # la pantalla brilla: no se oscurece tanto
                scr_k = max(k, 0.92)
                t2[..., :3] *= k
                # restaurar zona de pantalla (filas 3..6, columnas 1..7 en 16x)
                y0, y1, x0, x1 = 3 * SCR, 6 * SCR, 1 * SCR, 7 * SCR
                t2[y0:y1, x0:x1, :3] = tex[y0:y1, x0:x1, :3] * scr_k
            else:
                t2[..., :3] *= k
            if tint is not None:
                t2[..., :3] = t2[..., :3] * (1 - tint[3]) + np.array(tint[:3]) * tint[3]
            timg = Image.fromarray(np.clip(t2, 0, 255).astype(np.uint8), 'RGBA')
            _draw_quad(canvas, q, timg)
        return faces


def _draw_quad(canvas, q, timg):
    # expandir un poco para tapar rendijas
    c = q.mean(axis=0)
    qq = c + (q - c) * 1.0
    d = qq - c
    ln = np.linalg.norm(d, axis=1, keepdims=True) + 1e-6
    qq = qq + d / ln * 0.7
    x0 = int(math.floor(qq[:, 0].min())); x1 = int(math.ceil(qq[:, 0].max()))
    y0 = int(math.floor(qq[:, 1].min())); y1 = int(math.ceil(qq[:, 1].max()))
    W, H = canvas.size
    if x1 < 0 or y1 < 0 or x0 > W or y0 > H or x1 - x0 < 1 or y1 - y0 < 1:
        return
    tw, th = timg.size
    # afín: punto destino (x,y) -> origen (u,v); usar esquinas 0 (u0,v0), 1 (u1,v0), 3 (u0,v1)
    p0 = qq[0] - (x0, y0); p1 = qq[1] - (x0, y0); p3 = qq[3] - (x0, y0)
    A = np.array([[p1[0] - p0[0], p3[0] - p0[0]], [p1[1] - p0[1], p3[1] - p0[1]]])
    det = np.linalg.det(A)
    if abs(det) < 1e-6:
        return
    Ai = np.linalg.inv(A)  # (x,y)-p0 -> (s,t) en 0..1
    a, b = Ai[0] * tw; c_, d_ = Ai[1] * th
    coeffs = (a, b, -(a * p0[0] + b * p0[1]), c_, d_, -(c_ * p0[0] + d_ * p0[1]))
    out = timg.transform((x1 - x0, y1 - y0), Image.AFFINE, coeffs, resample=Image.NEAREST)
    canvas.alpha_composite(out, (x0, y0)) if x0 >= 0 and y0 >= 0 and x1 <= W and y1 <= H else _safe_paste(canvas, out, x0, y0)


def _safe_paste(canvas, img, x, y):
    W, H = canvas.size
    cx0 = max(0, -x); cy0 = max(0, -y)
    cx1 = min(img.size[0], W - x); cy1 = min(img.size[1], H - y)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    canvas.alpha_composite(img.crop((cx0, cy0, cx1, cy1)), (x + cx0, y + cy0))


# ---------- Poses de ayuda ----------
def lerp(a, b, t):
    return a + (b - a) * t

def walk_pose(p, phase, amt=1.0):
    """Ciclo de caminata con zancada real. phase en ciclos."""
    s = math.sin(phase * 2 * math.pi)
    c = math.cos(phase * 2 * math.pi)
    sw = 0.55 * amt
    p.rleg = (s * sw, 0, 0); p.lleg = (-s * sw, 0, 0)
    p.rknee = max(0, -c) * 0.7 * amt if s > 0 else max(0, c) * 0.25 * amt
    p.lknee = max(0, c) * 0.7 * amt if s < 0 else max(0, -c) * 0.25 * amt
    p.rarm = (-s * 0.45 * amt, 0, 0.06); p.larm = (s * 0.45 * amt, 0, 0.06)
    p.relbow = 0.25 * amt; p.lelbow = 0.25 * amt
    # rebote vertical (dos veces por ciclo) y aplastar al pisar
    b = abs(math.sin(phase * 2 * math.pi))
    p.y += 0.6 * b * amt
    p.sy *= 1.0 - 0.03 * (1 - b) * amt
    p.sx *= 1.0 + 0.02 * (1 - b) * amt
    return p
