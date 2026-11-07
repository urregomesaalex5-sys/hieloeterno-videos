#!/usr/bin/env python3
# Capítulo 10: El transformador. Vertical 1080x1920, 30 fps.
# Gancho en el segundo 0: laboratorio en penumbra, título arriba. Sobre el mesón: un tomacorriente, un
# transformador (dos bobinas en un marco de hierro) y un bombillo conectado SOLO a la segunda bobina.
# A los 0,45 s él mete el enchufe: ¡ZAS!, zumbido, el bombillo prende y el cuarto se ilumina.
# Mejora nueva de este capítulo: MODO ESQUINA. En los planos cercanos (el hierro por dentro y las
# láminas que zumban) el personaje se encoge y se corre a la esquina para no tapar nada
# (pedido del cap. 9). Y el video baja a ~75 s (antes 81 s).
# Regla: cada rótulo sale de VERIFICACION.md (códigos T#).
import math
import random
import numpy as np
from PIL import Image, ImageDraw
import scene as S
import diagrams as D
import inductor as I
import rele as R
import trafo as T
import lab as LB
import char3d as C
from timeline import TL, PHRASES

W, H = S.W, S.H
FPS = S.FPS
CH = C.Character()
HOME_X = 230
INTRO_X = 290
LABEL_TXT = 'CAP. 10 · EL TRANSFORMADOR'

P = lambda i: TL.s(i)
E = lambda i: TL.e(i)
KW = TL.kw

# ======================= tiempos clave =======================
T_PLUG = 0.45                       # mete el enchufe (¡ZAS! + bombillo)
T_BONK = T_PLUG                     # (la música usa este nombre)
T_TITLE = T_PLUG
T_TITLE_FLY = P(1) + 0.15
T_WALK_HOME = P(1) + 0.2
T_H_SLAP = P(2) - 0.15              # se rompe el montaje del gancho
T_R_SLAP = E(5) + 0.2               # se rompe el transformador grande
T_N_SLAP = E(8) + 0.2               # se rompen los voltímetros
T_B_SLAP = E(9) + 0.2               # se rompe la pila
T_P_SLAP = E(11) + 0.15             # se rompe el poste
T_END_SNAP = E(13) + 0.6
T_END = TL.END

# planos cercanos: el personaje se va a la esquina (mejora del cap. 10)
CORNER = [(KW(4, 'HIERRO') - 0.45, P(5) + 0.35), (KW(11, 'ZUMBIDO') - 0.45, E(11) + 0.1)]
def corner_k(t):
    k = 0.0
    for a, b in CORNER:
        k = max(k, S.ease_io(S.seg(t, a, a + 0.4)) * (1 - S.ease_io(S.seg(t, b, b + 0.4))))
    return k
# ======================= utilidades =======================
EVENTS = []
def ev(t, name, gain=1.0, pan=0.0, **kw):
    EVENTS.append((t, name, gain, pan, kw))

def panx(x):
    return max(-0.8, min(0.8, (x - W / 2) / (W / 2) * 0.8))

VOICE_ENV = None
def set_voice_env(env):
    global VOICE_ENV
    VOICE_ENV = env

def mouth_at(t):
    if VOICE_ENV is not None:
        i = int(t * 100)
        if 0 <= i < len(VOICE_ENV):
            return float(VOICE_ENV[i])
        return 0.0
    for i in range(len(PHRASES)):
        if P(i) <= t <= E(i):
            return 0.35 + 0.35 * abs(math.sin(t * 17)) * abs(math.sin(t * 5.3))
    return 0.0

def speaking(t):
    for i in range(len(PHRASES)):
        if P(i) - 0.05 <= t <= E(i) + 0.05:
            return i
    return None


def expr_at(t):
    e = 'normal'
    for tt, x in EXPR:
        if t >= tt:
            e = x
    return e

def blink_at(t):
    ph = (t + 0.7) % 3.3
    if ph < 0.12:
        return math.sin(ph / 0.12 * math.pi)
    return 0.0


JUMPS = []
SPINS = []
def spin_at(t):
    for t0, d in SPINS:
        if t0 <= t <= t0 + d:
            return 2 * math.pi * S.ease_io((t - t0) / d)
    return 0.0

def jump_at(t):
    for t0, d, h in JUMPS:
        if t0 <= t <= t0 + d:
            u = (t - t0) / d
            return 4 * h * u * (1 - u), u
    return 0.0, None


# ======================= gestos =======================
def aim(pose, side, shoulder, target, maxlen=2.6):
    dx = target[0] - shoulder[0]
    dyu = -(target[1] - shoulder[1])
    L = math.hypot(dx, dyu)
    if side == 'l':
        pz = math.atan2(dx, -dyu)
        pose.larm = (0.0, 0.0, pz); pose.lelbow = 0.0
        pose.larm_len = max(1.0, min(maxlen, L / (12 * S.SCALE)))
    else:
        pz = math.atan2(-dx, -dyu)
        pose.rarm = (0.0, 0.0, pz); pose.relbow = 0.0
        pose.rarm_len = max(1.0, min(maxlen, L / (12 * S.SCALE)))

def blend_arm(pose, side, target_pose, k):
    if side == 'l':
        pose.larm = tuple(a + (b - a) * k for a, b in zip(pose.larm, target_pose.larm))
        pose.lelbow += (target_pose.lelbow - pose.lelbow) * k
        pose.larm_len += (target_pose.larm_len - pose.larm_len) * k
    else:
        pose.rarm = tuple(a + (b - a) * k for a, b in zip(pose.rarm, target_pose.rarm))
        pose.relbow += (target_pose.relbow - pose.relbow) * k
        pose.rarm_len += (target_pose.rarm_len - pose.rarm_len) * k

def shoulder_screen(x, y_feet, side, sx=1.0, sy=1.0):
    sgn = -1 if side == 'r' else 1
    return (x + sgn * 6 * S.SCALE * sx, y_feet - 22 * S.SCALE * sy)

THROW_GESTURES = []
SLAPS = []
POINTS = []
REACT_ARMS = []
GEST = []

def arm_window(pose, t, x, yf):
    for t0, t1, side, target in POINTS:
        if t0 - 0.25 <= t <= t1 + 0.3:
            k = S.ease_out(S.seg(t, t0 - 0.25, t0)) * (1 - S.ease_io(S.seg(t, t1, t1 + 0.3)))
            if t0 <= 0.0:
                k = 1 - S.ease_io(S.seg(t, t1, t1 + 0.3))
            tp = pose.copy()
            tgt = target(t) if callable(target) else target
            aim(tp, side, shoulder_screen(x, yf, side, pose.sx, pose.sy), tgt, maxlen=2.6)
            if side == 'l':
                tp.larm = (tp.larm[0], tp.larm[1], tp.larm[2])
            blend_arm(pose, side, tp, k)
    for tr, side in THROW_GESTURES:
        if tr - 0.3 <= t <= tr + 0.3:
            if t < tr - 0.12:
                u = S.seg(t, tr - 0.3, tr - 0.12)
                tp = pose.copy(); a = (-0.9 * S.ease_out(u), 0, 0.3)
            elif t < tr + 0.05:
                u = S.seg(t, tr - 0.12, tr + 0.05)
                tp = pose.copy(); a = (-0.9 + 3.1 * S.ease_out(u), 0, 0.3 + 0.4 * u)
            else:
                u = S.seg(t, tr + 0.05, tr + 0.3)
                tp = pose.copy(); a = (2.2 * (1 - S.ease_io(u)), 0, 0.7 * (1 - u))
            if side == 'l':
                tp.larm = a; tp.lelbow = 0.2; tp.larm_len = 1.15
            else:
                tp.rarm = a; tp.relbow = 0.2; tp.rarm_len = 1.15
            k = S.seg(t, tr - 0.3, tr - 0.22) * (1 - S.seg(t, tr + 0.22, tr + 0.3))
            blend_arm(pose, side, tp, k)
            pose.lean += 0.12 * math.sin(S.seg(t, tr - 0.3, tr + 0.3) * math.pi)
    for ts, side in SLAPS:
        if ts - 0.25 <= t <= ts + 0.35:
            tp = pose.copy()
            if t < ts - 0.08:
                u = S.seg(t, ts - 0.25, ts - 0.08); a = (1.2 * u, 0, -0.3 * u)
            elif t < ts + 0.06:
                u = S.seg(t, ts - 0.08, ts + 0.06); a = (1.2 + 1.3 * u, 0, -0.3 + 2.2 * S.ease_out(u))
            else:
                u = S.seg(t, ts + 0.06, ts + 0.35); a = (2.5 * (1 - u), 0, 1.9 * (1 - S.ease_io(u)))
            if side == 'l':
                tp.larm = a; tp.lelbow = 0.1; tp.larm_len = 1.35
            else:
                tp.rarm = a; tp.relbow = 0.1; tp.rarm_len = 1.35
            k = S.seg(t, ts - 0.25, ts - 0.18) * (1 - S.seg(t, ts + 0.28, ts + 0.35))
            blend_arm(pose, side, tp, k)
            pose.yaw += 0.25 * math.sin(S.seg(t, ts - 0.25, ts + 0.35) * math.pi) * (1 if side == 'l' else -1)


def pos_x(t):
    x = INTRO_X
    for a, b, x0, x1 in WALKS:
        if t >= b:
            x = x1
        elif t >= a:
            u = S.ease_io((t - a) / (b - a))
            return x0 + (x1 - x0) * u, (a, b, x0, x1)
    return x, None


# ======================= estado del personaje =======================
def char_state(t):
    p = C.Pose()
    p.expr = expr_at(t)
    p.blink = blink_at(t) if p.expr in ('normal', 'curioso', 'hablando') else 0.0
    p.mouth = mouth_at(t)
    x, walking = pos_x(t)
    yf = S.FLOOR_Y
    br = math.sin(t * 2.2)
    p.sy *= 1 + 0.008 * br; p.sx *= 1 - 0.004 * br
    p.head = (0.04 * math.sin(t * 1.3), 0.08 * math.sin(t * 0.7), 0.03 * math.sin(t * 1.1))
    p.rarm = (0.05, 0, 0.08 + 0.03 * br); p.larm = (0.05, 0, 0.08 + 0.03 * br)
    p.relbow = 0.15; p.lelbow = 0.15
    if diagram_active(t):
        ph = (t * 0.45) % 1.0
        k = S.ease_io(S.clamp((ph / 0.08) if ph < 0.3 else (0.6 - ph) / 0.08 if ph < 0.6 else 0))
        p.head = (p.head[0] - 0.12 * k, p.head[1] + 0.45 * k, p.head[2])
        p.look = (1.0 * k, -0.6 * k)
        p.lean += 0.08 * k
    si = speaking(t)
    if si is not None and walking is None and t > T_WALK_HOME + 0.8:
        # en reposo los brazos casi no se mueven (pedido de Edwin)
        env = mouth_at(t)
        g1 = math.sin(t * 1.5 + si * 1.7); g2 = math.sin(t * 1.2 + si * 0.9 + 1.3)
        p.larm = (0.14 + 0.05 * g1 * env, 0, 0.13 + 0.03 * env); p.lelbow = 0.3 + 0.08 * g1
        p.rarm = (0.14 + 0.05 * g2 * env, 0, 0.13 + 0.03 * env); p.relbow = 0.3 + 0.08 * g2
        p.head = (p.head[0] + 0.1 * env * math.sin(t * 8), p.head[1] + 0.08 * g2, p.head[2] + 0.05 * g1)
        yf -= 2 * env
        p.sy *= 1 + 0.01 * env
        p.lean += 0.03 * g1
    if t < T_WALK_HOME:
        intro_pose(p, t, x, yf)
    if walking is not None:
        a, b, x0, x1 = walking
        dist = abs(x - x0)
        phase = dist / 210.0
        amt = S.clamp(min((t - a) / 0.15, (b - t) / 0.15))
        C.walk_pose(p, phase, amt)
        d = -1 if x1 < x0 else 1
        p.yaw = d * 0.85 * S.clamp(min((t - a) / 0.2, (b - t) / 0.2))
        p.look = (d * 1.0, 0)
    jy, ju = jump_at(t)
    if ju is not None:
        yf -= jy
        if ju < 0.12:
            p.sy *= 0.9; p.sx *= 1.06
        else:
            p.sy *= 1.06; p.sx *= 0.96
        p.rknee = 0.5 * math.sin(ju * math.pi); p.lknee = 0.5 * math.sin(ju * math.pi)
    p.yaw += spin_at(t)
    scene_gestures(p, t, x, yf)
    arm_window(p, t, x, yf)
    return p, x, yf, light_at(t), 0.0


def scene_gestures(p, t, x, yf):
    for t0, d, kind in REACT_ARMS:
        if t0 - 0.1 <= t <= t0 + d + 0.15:
            k = S.seg(t, t0 - 0.1, t0 + 0.05) * (1 - S.seg(t, t0 + d, t0 + d + 0.15))
            tp = p.copy()
            if kind in ('up', 'spin'):
                tp.larm = (0.2, 0, 2.6); tp.rarm = (0.2, 0, 2.6); tp.lelbow = 0.2; tp.relbow = 0.2
                tp.larm_len = 1.15; tp.rarm_len = 1.15
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
            elif kind == 'thumbs':
                tp.larm = (1.4, 0, 0.6); tp.lelbow = 1.6; tp.rarm = (1.4, 0, 0.6); tp.relbow = 1.6
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
    for t0, d, kind in GEST:
        if t0 - 0.2 <= t <= t0 + d + 0.25:
            k = S.ease_out(S.seg(t, t0 - 0.2, t0)) * (1 - S.ease_io(S.seg(t, t0 + d, t0 + d + 0.25)))
            tp = p.copy()
            if kind == 'present':
                tp.larm = (0.85, 0, 0.95); tp.lelbow = 0.35
                blend_arm(p, 'l', tp, k)
                p.head = (p.head[0], p.head[1] + 0.35 * k, p.head[2])
            elif kind == 'open':
                tp.larm = (0.6, 0, 0.85); tp.lelbow = 0.3; tp.rarm = (0.6, 0, 0.85); tp.relbow = 0.3
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
            elif kind == 'count':
                tp.rarm = (1.25, 0, 0.25); tp.relbow = 1.5
                blend_arm(p, 'r', tp, k)
            elif kind == 'chin':
                tp.rarm = (1.9, 0, -0.2); tp.relbow = 2.0
                blend_arm(p, 'r', tp, k)
                p.head = (p.head[0] - 0.08 * k, p.head[1] + 0.2 * k, p.head[2] + 0.1 * k)
            elif kind == 'stop':       # mano de "alto" hacia el diagrama
                tp.larm = (1.45, 0, 1.0); tp.lelbow = 0.9
                blend_arm(p, 'l', tp, k)
                p.lean -= 0.06 * k
            elif kind == 'shade':      # mano de visera (¡qué luz!)
                tp.rarm = (2.3, 0, -0.55); tp.relbow = 1.6
                blend_arm(p, 'r', tp, k)
                p.head = (p.head[0] + 0.12 * k, p.head[1], p.head[2])
            elif kind == 'ears':       # se tapa los oídos (¡CLIC!)
                tp.larm = (1.2, 0, 1.3); tp.lelbow = 2.2; tp.rarm = (1.2, 0, 1.3); tp.relbow = 2.2
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
                p.sy *= 1 - 0.04 * k
            elif kind == 'laugh':      # se agarra la barriga de la risa
                tp.larm = (0.9, 0, -0.5); tp.lelbow = 1.5; tp.rarm = (0.9, 0, -0.5); tp.relbow = 1.5
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
                p.lean += 0.05 * k * math.sin(t * 22)
                p.head = (p.head[0] - 0.15 * k, p.head[1], p.head[2] + 0.06 * k * math.sin(t * 18))
            elif kind == 'chest':      # manos al pecho (gracias)
                tp.larm = (1.6, 0, -0.35); tp.lelbow = 1.9; tp.rarm = (1.6, 0, -0.35); tp.relbow = 1.9
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
    # despedida
    a = KW(13, 'Respóndeme') + 0.2
    if a <= t < T_END_SNAP - 0.35:
        k = S.seg(t, a, a + 0.2)
        tp = p.copy(); tp.larm = (0.1, 0, 2.5 + 0.35 * math.sin((t - a) * 13)); tp.lelbow = 0.4; tp.larm_len = 1.2
        blend_arm(p, 'l', tp, k)
    if T_END_SNAP - 0.35 <= t < T_END_SNAP + 0.6:
        u = S.ease_out(S.seg(t, T_END_SNAP - 0.35, T_END_SNAP - 0.05)) * (1 - S.seg(t, T_END_SNAP + 0.3, T_END_SNAP + 0.6))
        tp = p.copy(); tp.rarm = (0.3, 0, 2.6); tp.relbow = 0.5
        blend_arm(p, 'r', tp, u)


SHAKES = []
def shake_at(t):
    dx = dy = 0.0
    for t0, d, amp in SHAKES:
        if t0 <= t < t0 + d:
            u = (t - t0) / d
            a = amp * (1 - u)
            dx += a * math.sin(t * 91); dy += a * math.cos(t * 77)
    return int(dx), int(dy)


# ======================= lanzamientos y manotazos =======================
THROWS = []
def add_throw(t0, target, img_fn, side='l', dur=0.45, arc=180, spin=1.0, land_sfx='block', pitch=1.0):
    THROWS.append(dict(t0=t0, dur=dur, target=target, img_fn=img_fn, side=side, arc=arc, spin=spin))
    THROW_GESTURES.append((t0, side))
    ev(t0, 'whoosh', 0.35, panx(target[0]))
    if land_sfx == 'block':
        ev(t0 + dur, 'block', 0.55, panx(target[0]), pitch=pitch)
    elif land_sfx == 'pop':
        ev(t0 + dur, 'pop', 0.5, panx(target[0]))
    return THROWS[-1]

_hand_cache = {}
def hand_pos(t, side):
    key = (round(t, 3), side)
    if key in _hand_cache:
        return _hand_cache[key]
    p, x, yf, _, _ = char_state(t)
    CH.build(p, None)
    pt = CH.points[side + 'hand']
    res = (x + pt[0] * S.SCALE, yf - pt[1] * S.SCALE)
    _hand_cache[key] = res
    return res

def throw_state(th, t):
    if t < th['t0']:
        return None
    u = (t - th['t0']) / th['dur']
    if u < 1:
        st = hand_pos(th['t0'], th['side'])
        tg = th['target']
        k = S.ease_out(u) * 0.6 + u * 0.4
        x = st[0] + (tg[0] - st[0]) * k
        y = st[1] + (tg[1] - st[1]) * k - th['arc'] * math.sin(math.pi * u)
        ang = (1 - k) * th['spin'] * 2 * math.pi
        sc = 0.35 + 0.65 * S.ease_out(u)
        return ('fly', x, y, ang, sc)
    v = t - th['t0'] - th['dur']
    j = S.jelly(v, 3.0, 6.0)
    return ('land', 1 + 0.18 * j, 1 - 0.18 * j)

def draw_thrown(canvas, th, t, place_fn, img_now=None):
    st = throw_state(th, t)
    if st is None:
        return None
    if st[0] == 'fly':
        img = img_now if img_now is not None else th['img_fn'](t)
        S.paste_center(canvas, img, st[1], st[2], scale=st[4], angle=st[3])
        S.speed_lines(canvas, st[1] - 30, st[2] + 20, st[1] - 120, st[2] + 60, n=3, color=(255, 255, 255, 90), width=3, seed=int(th['t0'] * 10))
    else:
        place_fn(canvas, st[1], st[2])
    return st


def curr_squares(l, pts, t, n, speed, on, oy=0, col=None, size=8):
    col = col or D.CURR
    for k in range(n):
        p = D.along(pts, (t * speed + k / n) % 1.0)
        l.rect([p[0] - size, p[1] - oy - size, p[0] + size, p[1] - oy + size], fill=col + (int(255 * on),))


def capture(fn, t, y0, y1):
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fn(tmp, t, at=True)
    return tmp.crop((0, y0, W, y1))

_cap_cache = {}
def shattered(cv, fn, ts, t, seed, y0=230, y1=1030):
    key = (fn, ts)
    if key not in _cap_cache:
        _cap_cache[key] = capture(fn, ts - 0.01, y0, y1)
    D.shatter(cv, _cap_cache[key], 0, y0, t - ts, seed=seed, tile=64, push=(300, -100))

def add_slap(ts):
    SLAPS.append((ts, 'l'))
    ev(ts, 'whoosh', 0.5, 0.2); ev(ts + 0.05, 'crumble', 0.7, 0.2)

def pop_in(t, t0, d=0.3):
    return S.ease_back(S.seg(t, t0, t0 + d))

def wire(l, pts, col=I.WIRE, w=7):
    l.line(pts, col + (255,), w)


# ======================= título (en pantalla desde el cuadro 0) =======================
_tc = {}
_stc = {}
def stamp_img(txt, size=40, col=(230, 60, 60)):
    key = (txt, size, col)
    if key not in _stc:
        f = S.font(size)
        w, h, b = S.text_size(txt, f)
        l = D.L(w + 60, size + 50)
        l.rrect([8, 8, w + 52, size + 42], 10, fill=(255, 255, 255, 50), outline=col + (255,), width=6)
        l.text(((w + 60) / 2, (size + 50) / 2), txt, size, fill=col)
        _stc[key] = l.done()
    return _stc[key]


def burst(txt, size=70, col=(255, 230, 90)):
    """rótulo de cómic (¡CLIC!) con estrella detrás"""
    key = ('burst', txt, size, col)
    if key not in _stc:
        f = S.font(size, True)
        w, h, b = S.text_size(txt, f)
        R0 = max(w, size) * 0.75 + 30
        l = D.L(int(R0 * 2 + 10), int(R0 * 2 + 10))
        c = (l.w / 2, l.h / 2)
        pts = []
        for k in range(24):
            r = R0 if k % 2 == 0 else R0 * 0.72
            a = k * math.pi / 12
            pts.append((c[0] + r * math.cos(a), c[1] + r * 0.62 * math.sin(a)))
        l.poly(pts, fill=(255, 255, 255, 235), outline=(30, 30, 36, 255), width=6)
        l.text(c, txt, size, fill=(225, 40, 40), black=True, stroke=3, stroke_fill=(60, 10, 10))
        _stc[key] = l.done()
    return _stc[key]


CLIP = (0, 228, 1080, 1075)
def paste_clipped(cv, img, x, y, box=CLIP, **kw):
    """pega una imagen recortada a la ventana del laboratorio (para los planos cercanos)"""
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    S.paste_center(tmp, img, x, y, **kw)
    cv.alpha_composite(tmp.crop(box), (box[0], box[1]))


def lbl(cv, txt, x, y, a, col=(255, 255, 255), size=24):
    if a > 0.01:
        S.paste_center(cv, D.label(txt, size, fill=col), x, y, scale=a)



# ======================= expresiones =======================
EXPR = [
    (0.0, 'guino'), (T_PLUG + 0.02, 'sorpresa'), (KW(0, 'bobinas'), 'curioso'), (KW(0, 'NO'), 'pensando'),
    (KW(0, 'bombillo'), 'sorpresa'), (KW(0, 'Cómo'), 'pensando'), (KW(0, 'TRANSFORMADOR'), 'feliz'),
    (P(1), 'guino'), (KW(1, 'ZUMBA'), 'curioso'),
    (P(2), 'feliz'), (KW(2, 'NÚCLEO'), 'curioso'),
    (P(3), 'feliz'), (KW(3, '60'), 'sorpresa'),
    (P(4), 'curioso'), (KW(4, 'HIERRO'), 'feliz'),
    (P(5) - 0.1, 'sorpresa'), (KW(5, 'capítulo'), 'guino'),
    (P(6), 'guino'), (KW(6, 'VUELTAS'), 'curioso'),
    (P(7), 'feliz'), (KW(7, 'MITAD'), 'curioso'),
    (P(8), 'pensando'), (KW(8, 'SUBE'), 'feliz'), (KW(8, 'BAJA'), 'sorpresa'),
    (P(9), 'sorpresa'), (KW(9, 'PULSITO'), 'pensando'),
    (P(10), 'guino'), (KW(10, 'MILES'), 'sorpresa'), (KW(10, 'enchufe'), 'feliz'),
    (P(11), 'curioso'), (KW(11, 'estira'), 'feliz'),
    (P(12), 'corazon'),
    (P(13), 'feliz'), (KW(13, 'Reto'), 'guino'), (KW(13, 'Cuánto'), 'pensando'), (KW(13, 'Respóndeme'), 'feliz'),
    (T_END_SNAP + 0.3, 'feliz'), (T_END_SNAP + 0.75, 'apagado'),
]
def expr_at(t):
    e = 'normal'
    for tt, x in EXPR:
        if t >= tt:
            e = x
    return e


# ======================= caminatas =======================
WALKS = []
def setup_walks():
    plan = [
        (T_WALK_HOME, HOME_X, 0.6),
        (P(7) + 0.1, 270, 0.5), (E(7) + 0.2, HOME_X, 0.5),
        (KW(13, 'Reto') - 0.1, 290, 0.7),
    ]
    x = INTRO_X
    for t0, x1, d in plan:
        WALKS.append((t0, t0 + d, x, x1))
        n = max(2, int(abs(x1 - x) / 70))
        for k in range(n):
            ev(t0 + 0.12 + k * (d - 0.24) / max(1, n - 1), 'step', 0.4, panx(x + (x1 - x) * k / max(1, n - 1)), heavy=0.75)
        x = x1


def intro_pose(p, t, x, yf):
    # tiene el enchufe en la mano, lo mete y se echa para atrás cuando prende el bombillo
    if t < T_PLUG:
        p.lean += 0.1
        p.head = (p.head[0] - 0.12, p.head[1] + 0.4, p.head[2])
        p.look = (1.0, 0.3)
    elif t < P(0) + 0.9:
        u = t - T_PLUG
        j = S.jelly(u, 3.0, 4.0)
        p.lean += -0.2 * math.exp(-u * 3) + 0.04 * math.sin(u * 8)
        p.sx *= 1 + 0.07 * j; p.sy *= 1 - 0.07 * j
        p.head = (p.head[0] + 0.1 * math.exp(-u * 2), p.head[1] - 0.3 * math.exp(-u * 2), p.head[2])


def diagram_active(t):
    return (P(2) + 0.4 <= t < T_R_SLAP) or (P(6) + 0.3 <= t < T_N_SLAP) or (P(10) + 0.3 <= t < T_P_SLAP)


def light_at(t):
    if t > T_END_SNAP + 0.05:
        return 0.0
    if t < T_PLUG + 0.05:
        return 0.34
    return 0.34 + 0.66 * S.ease_out(S.seg(t, T_PLUG + 0.05, T_PLUG + 0.35))


# ======================= título =======================
_tc = {}
def title_imgs():
    if not _tc:
        _tc['a'] = S.fancy_text('¿CÓMO FUNCIONA UN', 64)
        _tc['b'] = S.fancy_text('TRANSFORMADOR?', 88, top=(255, 214, 150), bot=(214, 110, 40), outline=(70, 30, 6))
    return _tc

def setup_title():
    ev(KW(0, 'TRANSFORMADOR') - 0.05, 'block', 0.5, 0.0, pitch=1.1)
    ev(T_TITLE_FLY, 'whoosh', 0.4, 0.0)

def draw_title(cv, t):
    TI = title_imgs()
    if t < T_TITLE_FLY + 0.5:
        fly = S.ease_in(S.seg(t, T_TITLE_FLY, T_TITLE_FLY + 0.45))
        k0 = KW(0, 'TRANSFORMADOR')
        bump = 1 + 0.12 * S.jelly(t - k0, 3, 5) if t >= k0 else 1.0
        ya = 262 + (S.ROOM_T + 46 - 262) * fly; yb = 345 + (S.ROOM_T + 46 - 345) * fly
        sc = 1 - 0.75 * fly
        S.paste_center(cv, TI['a'], 540, ya, scale=sc, alpha=1 - fly * 0.9)
        S.paste_center(cv, TI['b'], 540, yb, scale=sc * bump, alpha=1 - fly * 0.9)


def trafo_at(cv, w, cx, cy, n1, n2, t, amp=0.0, glow2=0.0, scale=1.0, alpha=1.0, sx=None, sy=None, flux_a=1.0):
    """pega el transformador y (si hay flujo) las flechitas que dan la vuelta por el hierro"""
    img = T.transformer(w, n1, n2, round(glow2, 1))
    if abs(amp) > 0.04 and flux_a > 0.02:
        img = img.copy()
        img.alpha_composite(T.flux_overlay(w, t, amp, alpha=flux_a))
    S.paste_center(cv, img, cx, cy, scale=scale, alpha=alpha, sx=sx, sy=sy)

def trafo_pt(w, cx, cy, p, scale=1.0):
    g = T.geom(w)
    return cx + (p[0] - g['W'] / 2) * scale, cy + (p[1] - g['H'] / 2) * scale


def ac(t, f=0.9):
    """corriente alterna en cámara lenta (f vueltas por segundo en pantalla)"""
    return math.sin(2 * math.pi * f * t)


# ======================= escena H: gancho (frases 0–1) =======================
Hh = {}
OUT_C = (420, 1000)       # tomacorriente en la pared
TH_C = (722, 996)         # transformador del gancho
TH_W = 360
BULB_C = (1006, 1058)

def setup_H():
    POINTS.append((0.0, T_PLUG + 0.2, 'l', (OUT_C[0], OUT_C[1] + 10)))
    ev(T_PLUG, 'click', 0.6, panx(OUT_C[0]))
    ev(T_PLUG + 0.02, 'zap', 0.5, panx(OUT_C[0]))
    ev(T_PLUG + 0.04, 'thud', 0.5, panx(TH_C[0]))
    ev(T_PLUG + 0.05, 'hum', 0.08, panx(TH_C[0]), dur=T_H_SLAP - T_PLUG, f=120)
    SHAKES.append((T_PLUG + 0.05, 0.2, 6))
    GEST.append((T_PLUG + 0.3, 0.8, 'shade'))
    Hh['l_coils'] = KW(0, 'bobinas') - 0.05
    Hh['no'] = KW(0, 'NO') - 0.1
    Hh['l_bulb'] = KW(0, 'bombillo') - 0.05
    Hh['promise'] = KW(1, 'ZUMBA') - 0.2
    for k in ('l_coils', 'l_bulb'):
        ev(Hh[k], 'pop', 0.4, 0.3)
    ev(Hh['no'], 'marker', 0.4, 0.1, dur=0.45)
    ev(Hh['promise'], 'chime', 0.3, 0.3)
    add_slap(T_H_SLAP)

def draw_H(cv, t, at=None):
    if t > T_H_SLAP + 1.0:
        return
    if t >= T_H_SLAP and at is None:
        shattered(cv, draw_H, T_H_SLAP, t, 3, y0=230, y1=1150)
        return
    on = S.ease_out(S.seg(t, T_PLUG + 0.04, T_PLUG + 0.14))
    g = T.geom(TH_W)
    la, lb, ra, rb = T.lead_points(TH_W)
    pla = trafo_pt(TH_W, *TH_C, la); plb = trafo_pt(TH_W, *TH_C, lb)
    pra = trafo_pt(TH_W, *TH_C, ra); prb = trafo_pt(TH_W, *TH_C, rb)
    # tomacorriente
    S.paste_center(cv, T.outlet(110), OUT_C[0], OUT_C[1])
    # cable del enchufe: de la mano (o del tomacorriente) a la bobina 1
    if t < T_PLUG:
        hx, hy = hand_pos(t, 'l')
        pp = (hx + 10, hy)
    else:
        pp = (OUT_C[0], OUT_C[1] + 12)
    l = D.L(W, 500); oy = 800
    for wcol, ww in (((20, 20, 24), 12), ((50, 52, 58), 7)):
        l.line([(pp[0], pp[1] + 20 - oy), (pp[0] + 6, 1140 - oy), (pla[0] - 30, 1140 - oy), (pla[0] - 30, plb[1] - oy), (pla[0], plb[1] - oy)], wcol + (255,), ww)
        l.line([(pla[0] - 30, plb[1] - oy), (pla[0] - 30, pla[1] - oy), (pla[0], pla[1] - oy)], wcol + (255,), ww)
    # bobina 2 → bombillo (en su sócket)
    for wcol, ww in (((150, 80, 30), 9), ((222, 140, 70), 5)):
        l.line([(pra[0], pra[1] - oy), (BULB_C[0] - 14, pra[1] - oy), (BULB_C[0] - 14, BULB_C[1] + 60 - oy)], wcol + (255,), ww)
        l.line([(prb[0], prb[1] - oy), (BULB_C[0] + 14, prb[1] - oy), (BULB_C[0] + 14, BULB_C[1] + 60 - oy)], wcol + (255,), ww)
    l.rrect([BULB_C[0] - 34, BULB_C[1] + 58 - oy, BULB_C[0] + 34, 1150 - oy], 6, fill=(60, 62, 70, 255), outline=(30, 30, 36, 255), width=3)
    cv.alpha_composite(l.done(), (0, oy))
    amp = ac(t) * on
    trafo_at(cv, TH_W, TH_C[0], TH_C[1], 7, 7, t, amp=amp, glow2=on * 0.8)
    if on > 0.01:
        S.glow_fast(cv, BULB_C[0], BULB_C[1] - 25, 260, (255, 225, 140), 0.8 * on)
    S.paste_center(cv, I.bulb(round(on, 1), 150), BULB_C[0], BULB_C[1])
    # enchufe (en la mano o metido)
    if t < T_PLUG:
        S.paste_center(cv, T.plug_front(64), pp[0], pp[1], angle=-0.2)
    else:
        sq = 1 + 0.15 * S.jelly(t - T_PLUG, 4, 6)
        S.paste_center(cv, T.plug_front(64), OUT_C[0], OUT_C[1] + 8, sx=sq, sy=2 - sq)
    if T_PLUG <= t < T_PLUG + 0.6:
        a = S.ease_back(S.seg(t, T_PLUG, T_PLUG + 0.15)) * (1 - S.seg(t, T_PLUG + 0.45, T_PLUG + 0.6))
        S.paste_center(cv, burst('¡ZAS!', 42), OUT_C[0] + 20, OUT_C[1] - 120, scale=a, angle=-0.1)
        S.glow_fast(cv, OUT_C[0], OUT_C[1], 90, (180, 220, 255), 0.8 * (1 - S.seg(t, T_PLUG, T_PLUG + 0.3)))
    # rótulos
    lbl(cv, 'BOBINA 1', trafo_pt(TH_W, *TH_C, g['lc'])[0], TH_C[1] - 190, pop_in(t, Hh['l_coils']), (255, 200, 140), 24)
    lbl(cv, 'BOBINA 2', trafo_pt(TH_W, *TH_C, g['rc'])[0], TH_C[1] - 190, pop_in(t, Hh['l_coils'] + 0.12), (150, 220, 255), 24)
    if t >= Hh['no']:
        u = S.seg(t, Hh['no'], Hh['no'] + 0.35)
        a = 1.0
        x = TH_C[0]
        l = D.L(30, 200)
        for k in range(int(6 * u) + 1):
            l.rect([10, k * 34, 20, k * 34 + 20], fill=(255, 80, 80, 255))
        S.paste_center(cv, l.done(), x, TH_C[1])
        lbl(cv, '✗ NO SE TOCAN', x, TH_C[1] - 250, pop_in(t, Hh['no'] + 0.15), (255, 130, 130), 30)
    lbl(cv, 'BOMBILLO', BULB_C[0] - 20, BULB_C[1] - 135, pop_in(t, Hh['l_bulb']), (255, 235, 160), 22)
    if t >= Hh['promise']:
        a = pop_in(t, Hh['promise']) * (1 - S.seg(t, T_H_SLAP - 0.3, T_H_SLAP))
        S.paste_center(cv, T.pole(150, 1.0, t), 880, 560, scale=a)
        lbl(cv, 'AL FINAL: EL DEL POSTE', 640, 440, a, (255, 220, 120), 34)


# ======================= escena R: por dentro (frases 2–5) =======================
Rr = {}
R_W = 520
R_C = (620, 560)
R_C2 = (640, 770); R_S2 = 0.74
G_C = (640, 405)
def setup_R():
    Rr['in'] = P(2) - 0.05
    Rr['l_b'] = KW(2, 'BOBINAS') - 0.05
    Rr['l_n'] = KW(2, 'NÚCLEO') - 0.05
    Rr['ac'] = KW(3, 'corriente') - 0.15
    Rr['60'] = KW(3, '60') - 0.1
    Rr['campo'] = KW(4, 'CAMPO') - 0.1
    Rr['zoom'] = KW(4, 'HIERRO') - 0.35
    Rr['unzoom'] = P(5) - 0.05
    Rr['volt'] = KW(5, 'VOLTAJE') - 0.1
    Rr['cap'] = KW(5, 'capítulo') - 0.2
    add_throw(Rr['in'] - 0.45, R_C, lambda t: T.transformer(R_W, 8, 8), side='l', dur=0.45, land_sfx='block')
    ev(Rr['l_b'], 'pop', 0.4, -0.2); ev(Rr['l_b'] + 0.12, 'pop', 0.4, 0.3); ev(Rr['l_n'], 'pop', 0.4, 0.0)
    ev(Rr['ac'], 'whoosh', 0.35, 0.0); ev(Rr['ac'] + 0.3, 'block', 0.45, 0.0, pitch=1.1)
    ev(Rr['60'], 'tink', 0.3, 0.0, f=2000)
    ev(Rr['campo'], 'hum', 0.07, 0.0, dur=E(5) - Rr['campo'], f=120)
    ev(Rr['zoom'], 'whoosh', 0.35, 0.3); ev(Rr['unzoom'], 'whoosh', 0.3, -0.2)
    ev(Rr['volt'], 'zap', 0.45, 0.4); ev(Rr['volt'] + 0.02, 'chime', 0.3, 0.4)
    SHAKES.append((Rr['volt'], 0.18, 6))
    ev(Rr['cap'], 'pop', 0.4, -0.4)
    GEST.extend([(KW(2, 'BOBINAS'), 0.9, 'present'), (KW(3, '60'), 0.8, 'count'), (KW(4, 'CAMPO'), 0.9, 'open'),
                 (KW(5, 'VOLTAJE'), 0.8, 'present')])
    add_slap(T_R_SLAP)

def r_place(t):
    """dónde está el transformador grande: centro (frase 2) → abajo y más chico (frases 3–5) + zoom al hierro"""
    k = S.ease_io(S.seg(t, Rr['ac'], Rr['ac'] + 0.45))
    cx = R_C[0] + (R_C2[0] - R_C[0]) * k
    cy = R_C[1] + (R_C2[1] - R_C[1]) * k
    sc = 1 + (R_S2 - 1) * k
    z = S.ease_io(S.seg(t, Rr['zoom'], Rr['zoom'] + 0.45)) * (1 - S.ease_io(S.seg(t, Rr['unzoom'], Rr['unzoom'] + 0.45)))
    return cx, cy, sc, z

def draw_R(cv, t, at=None):
    if t < Rr['in'] - 0.5 or t > T_R_SLAP + 1.0:
        return
    if t >= T_R_SLAP and at is None:
        shattered(cv, draw_R, T_R_SLAP, t, 5, y0=230, y1=1060)
        return
    th = R_THROW[0]
    st = throw_state(th, t)
    if st is None:
        return
    if st[0] == 'fly':
        S.paste_center(cv, T.transformer(R_W, 8, 8), st[1], st[2], scale=st[4], angle=st[3])
        return
    cx, cy, sc, z = r_place(t)
    g = T.geom(R_W)
    on = t >= Rr['ac']
    amp_on = S.seg(t, Rr['campo'], Rr['campo'] + 0.3)
    v = ac(t)
    glow2 = S.seg(t, Rr['volt'], Rr['volt'] + 0.2) * (0.6 + 0.4 * abs(v))
    # plano cercano: zoom a la esquina de arriba a la derecha (el flujo entra a la bobina 2)
    focus = (g['x0'] + g['w'] - g['th'] * 0.5, g['y0'] + g['th'] * 0.5)
    scz = sc * (1 + 0.85 * z)
    fx = cx + (focus[0] - g['W'] / 2) * sc
    fy = cy + (focus[1] - g['H'] / 2) * sc
    tx, ty = 700, 520
    ccx = cx + (tx - fx) * z - (focus[0] - g['W'] / 2) * (scz - sc) * (1 - z) * 0
    ccy = cy + (ty - fy) * z
    # cuando hay zoom, el centro se corre para que el foco quede en (tx, ty)
    ccx = (1 - z) * cx + z * (tx - (focus[0] - g['W'] / 2) * scz)
    ccy = (1 - z) * cy + z * (ty - (focus[1] - g['H'] / 2) * scz)
    img = T.transformer(R_W, 8, 8, round(glow2, 1))
    if amp_on > 0.02:
        img = img.copy(); img.alpha_composite(T.flux_overlay(R_W, t, v * amp_on))
    if on:
        # corriente (cuadritos) en la bobina 1, sube o baja según el signo
        img = img.copy()
        l = D.L(g['W'], g['H'])
        x = g['lc'][0]
        for k in range(5):
            u = ((t * 0.9 * (1 if v > 0 else -1)) + k / 5) % 1.0
            y = g['lc'][1] - g['ch'] * 0.45 + g['ch'] * 0.9 * u
            l.rect([x - g['cw'] * 0.55 - 7, y - 7, x - g['cw'] * 0.55 + 7, y + 7], fill=(255, 217, 61, int(255 * min(1, abs(v) * 2))))
        img.alpha_composite(l.done())
    if st[0] == 'land' and t < Rr['ac']:
        S.paste_center(cv, img, cx, cy, sx=st[1], sy=st[2])
    else:
        paste_clipped(cv, img, ccx, ccy, scale=scz)
    def scr(p):
        return ccx + (p[0] - g['W'] / 2) * scz, ccy + (p[1] - g['H'] / 2) * scz
    if z < 0.05:
        a_l = 1 - S.seg(t, Rr['ac'] - 0.2, Rr['ac'])
        if a_l > 0.01:
            x1, y1 = scr((g['lc'][0], g['y0']))
            x2, y2 = scr((g['rc'][0], g['y0']))
            lbl(cv, 'BOBINA 1', x1, y1 - 40, pop_in(t, Rr['l_b']) * a_l, (255, 200, 140), 28)
            lbl(cv, 'BOBINA 2', x2, y2 - 40, pop_in(t, Rr['l_b'] + 0.12) * a_l, (150, 220, 255), 28)
            xn, yn = scr((g['W'] / 2, g['y0'] + g['h']))
            lbl(cv, 'NÚCLEO DE HIERRO', xn, yn + 40, pop_in(t, Rr['l_n']) * a_l, (210, 215, 225), 28)
    # gráfica de la corriente alterna
    if on and t < Rr['zoom'] + 0.2:
        a = pop_in(t, Rr['ac'] + 0.1, 0.35) * (1 - S.seg(t, Rr['zoom'] - 0.1, Rr['zoom'] + 0.2))
        cur = ((t - Rr['ac']) * 0.9 / 3) % 1.0
        S.paste_center(cv, T.ac_graph(1.0, round(cur, 3), 540, 250), G_C[0], G_C[1], scale=a)
        lbl(cv, '60 CICLOS POR SEGUNDO · COLOMBIA', G_C[0], 560, pop_in(t, Rr['60']) * a, (255, 230, 140), 24)
        if t >= Rr['campo']:
            lbl(cv, 'CAMPO MAGNÉTICO', 900, 640, pop_in(t, Rr['campo']) * a, (120, 210, 255), 22)
    if t >= Rr['campo'] and z < 0.05:
        lbl(cv, 'EN CÁMARA LENTA', 900, 600 if t < Rr['zoom'] else 600, 0.0, (200, 200, 210), 18)
    if z > 0.3:
        a = S.seg(z, 0.3, 0.8)
        lbl(cv, 'EL HIERRO LLEVA EL CAMPO', 640, 300, a, (120, 210, 255), 30)
        lbl(cv, '→ A LA BOBINA 2', 760, 880, a, (150, 220, 255), 28)
    # voltaje en la bobina 2
    if t >= Rr['volt']:
        x2, y2 = scr(g['rc'])
        S.paste_center(cv, burst('¡VOLTAJE!', 36), min(880, x2 + 30), max(330, y2 - 220), scale=S.ease_back(S.seg(t, Rr['volt'], Rr['volt'] + 0.2)), angle=0.08)
    if t >= Rr['cap']:
        a = pop_in(t, Rr['cap'])
        S.paste_center(cv, I.coil(150, 56, 9), 250, 420, scale=a)
        lbl(cv, 'CAP. 8 · INDUCTOR', 250, 490, a, (255, 170, 110), 28)

R_THROW = []


# ======================= escena N: las vueltas (frases 6–8) =======================
Nn = {}
N_W = 440
N_C = (640, 560)
M_IN = (450, 880); M_OUT = (830, 880)
def setup_N():
    Nn['in'] = P(6) - 0.05
    Nn['vueltas'] = KW(6, 'VUELTAS') - 0.1
    Nn['doble'] = KW(7, 'DOBLE') - 0.1
    Nn['mitad'] = KW(7, 'MITAD') - 0.1
    Nn['back'] = P(8) - 0.1
    Nn['magia'] = KW(8, 'magia') - 0.1
    Nn['sube'] = KW(8, 'SUBE') - 0.05
    Nn['baja'] = KW(8, 'BAJA') - 0.05
    add_throw(Nn['in'] - 0.45, N_C, lambda t: T.transformer(N_W, 8, 8), side='l', dur=0.45)
    ev(Nn['in'] + 0.2, 'block', 0.45, panx(M_IN[0]), pitch=1.15); ev(Nn['in'] + 0.3, 'block', 0.45, panx(M_OUT[0]), pitch=1.2)
    ev(Nn['vueltas'], 'pop', 0.4, -0.2); ev(Nn['vueltas'] + 0.1, 'pop', 0.4, 0.3)
    for k in ('doble', 'mitad', 'back'):
        ev(Nn[k], 'boing', 0.35, 0.3, f0=400 if k == 'mitad' else 300, f1=300 if k == 'mitad' else 700)
        ev(Nn[k] + 0.25, 'tink', 0.3, panx(M_OUT[0]), f=2600 if k != 'mitad' else 1600)
    ev(Nn['magia'], 'thud', 0.5, 0.0); SHAKES.append((Nn['magia'], 0.15, 5))
    ev(Nn['sube'], 'pop', 0.4, 0.3); ev(Nn['baja'], 'pop', 0.4, 0.3, f0=900, f1=300)
    GEST.extend([(KW(6, 'truco'), 0.8, 'chin'), (KW(7, 'DOBLE'), 0.8, 'open'), (KW(7, 'MITAD'), 0.7, 'count'),
                 (KW(8, 'magia'), 0.8, 'chin')])
    add_slap(T_N_SLAP)

def n_turns(t):
    if t < Nn['doble'] + 0.15:
        return 8
    if t < Nn['mitad'] + 0.15:
        return 16
    if t < Nn['back'] + 0.15:
        return 4
    return 16

def draw_N(cv, t, at=None):
    if t < Nn['in'] - 0.5 or t > T_N_SLAP + 1.0:
        return
    if t >= T_N_SLAP and at is None:
        shattered(cv, draw_N, T_N_SLAP, t, 7, y0=230, y1=1060)
        return
    st = throw_state(N_THROW[0], t)
    if st is None:
        return
    n2 = n_turns(t)
    if st[0] == 'fly':
        S.paste_center(cv, T.transformer(N_W, 8, 8), st[1], st[2], scale=st[4], angle=st[3])
        return
    g = T.geom(N_W)
    la, lb, ra, rb = [trafo_pt(N_W, *N_C, p) for p in T.lead_points(N_W)]
    a = S.seg(t, Nn['in'] + 0.1, Nn['in'] + 0.35)
    l = D.L(W, 600); oy = 500
    for p, q in ((la, (M_IN[0] - 40, M_IN[1] - 60)), (lb, (M_IN[0] + 40, M_IN[1] - 60))):
        l.line([(p[0], p[1] - oy), (p[0] - 30, p[1] - oy), (p[0] - 30, q[1] - 30 - oy), (q[0], q[1] - 30 - oy), (q[0], q[1] - oy)], (232, 232, 232, int(255 * a)), 5)
    for p, q in ((ra, (M_OUT[0] - 40, M_OUT[1] - 60)), (rb, (M_OUT[0] + 40, M_OUT[1] - 60))):
        l.line([(p[0], p[1] - oy), (p[0] + 30, p[1] - oy), (p[0] + 30, q[1] - 30 - oy), (q[0], q[1] - 30 - oy), (q[0], q[1] - oy)], (232, 232, 232, int(255 * a)), 5)
    cv.alpha_composite(l.done(), (0, oy))
    jig = 1.0
    for k in ('doble', 'mitad', 'back'):
        if Nn[k] + 0.15 <= t:
            jig = 1 + 0.08 * S.jelly(t - Nn[k] - 0.15, 4, 6)
    trafo_at(cv, N_W, N_C[0], N_C[1], 8, n2, t, amp=ac(t) * 0.9, sx=st[1] if t < Nn['in'] + 0.6 else None, sy=st[2] if t < Nn['in'] + 0.6 else None)
    vin = '6 V~'
    vout = {8: '6 V~', 16: '12 V~', 4: '3 V~'}[n2]
    S.paste_center(cv, T.meter(vin, 190), M_IN[0], M_IN[1], scale=a)
    S.paste_center(cv, T.meter(vout, 190, col=(120, 240, 150) if n2 >= 8 else (255, 190, 90)), M_OUT[0], M_OUT[1], scale=a * jig)
    lbl(cv, 'ENTRA', M_IN[0], M_IN[1] + 90, a, (220, 220, 230), 20)
    lbl(cv, 'SALE', M_OUT[0], M_OUT[1] + 90, a, (220, 220, 230), 20)
    xl = trafo_pt(N_W, *N_C, g['lc'])[0]; xr = trafo_pt(N_W, *N_C, g['rc'])[0]
    if t >= Nn['vueltas']:
        lbl(cv, '8 VUELTAS', xl, 330, pop_in(t, Nn['vueltas']), (255, 200, 140), 26)
        lbl(cv, f'{n2} VUELTAS', xr, 330, pop_in(t, Nn['vueltas'] + 0.1) * jig, (150, 220, 255), 26)
    if Nn['doble'] + 0.15 <= t < Nn['mitad']:
        S.paste_center(cv, burst('DOBLE', 40), 960, 700, scale=S.ease_back(S.seg(t, Nn['doble'] + 0.2, Nn['doble'] + 0.4)) * (1 - S.seg(t, Nn['mitad'] - 0.2, Nn['mitad'])))
    if Nn['mitad'] + 0.15 <= t < Nn['back']:
        S.paste_center(cv, burst('MITAD', 40), 960, 700, scale=S.ease_back(S.seg(t, Nn['mitad'] + 0.2, Nn['mitad'] + 0.4)) * (1 - S.seg(t, Nn['back'] - 0.2, Nn['back'])))
    if t >= Nn['magia']:
        u = S.seg(t, Nn['magia'], Nn['magia'] + 0.15)
        S.paste_center(cv, stamp_img('NO ES MAGIA', 40), 640, 560, scale=(2.2 - 1.2 * S.ease_in(u)) * (1 - S.seg(t, Nn['sube'] - 0.15, Nn['sube'])), angle=-0.12, alpha=min(1, u * 2))
    if t >= Nn['sube']:
        lbl(cv, 'VOLTAJE ↑ (EL DOBLE)', 640, 1025, pop_in(t, Nn['sube']), (120, 240, 150), 28)
    if t >= Nn['baja']:
        lbl(cv, 'CORRIENTE ↓ (LA MITAD)', 640, 1075, pop_in(t, Nn['baja']), (255, 130, 130), 28)

N_THROW = []


# ======================= escena B: con una pila no funciona (frase 9) =======================
Bb = {}
B_BAT = (420, 610)
B_W = 340
B_C = (735, 610)
B_G = (660, 900)
def setup_B():
    Bb['in'] = P(9) - 0.1
    Bb['conn'] = KW(9, 'PULSITO') - 0.25
    Bb['no'] = KW(9, 'PILA') + 0.35
    add_throw(Bb['in'] - 0.4, B_BAT, lambda t: T.battery_d(190), side='l', dur=0.4)
    ev(Bb['in'] + 0.15, 'block', 0.45, panx(B_C[0]), pitch=1.1)
    ev(Bb['conn'], 'click', 0.5, panx(B_BAT[0])); ev(Bb['conn'] + 0.03, 'zap', 0.35, panx(B_C[0]))
    ev(Bb['no'], 'thud', 0.4, 0.0)
    GEST.extend([(KW(9, 'PILA'), 0.7, 'stop'), (KW(9, 'conectarla'), 0.9, 'open')])
    add_slap(T_B_SLAP)

def draw_B(cv, t, at=None):
    if t < Bb['in'] - 0.45 or t > T_B_SLAP + 1.0:
        return
    if t >= T_B_SLAP and at is None:
        shattered(cv, draw_B, T_B_SLAP, t, 9, y0=230, y1=1060)
        return
    st = throw_state(B_THROW[0], t)
    a = S.seg(t, Bb['in'], Bb['in'] + 0.3)
    la, lb, ra, rb = [trafo_pt(B_W, *B_C, p) for p in T.lead_points(B_W)]
    conn = t >= Bb['conn']
    l = D.L(W, 400); oy = 400
    l.line([(B_BAT[0], B_BAT[1] - 115 - oy), (B_BAT[0], 440 - oy), (la[0] - 20, 440 - oy), (la[0] - 20, la[1] - oy), (la[0], la[1] - oy)], (232, 232, 232, int(255 * a)), 5)
    end = (B_BAT[0] + 70, lb[1]) if conn else (B_BAT[0] + 40, lb[1] + 60)
    l.line([(la[0], lb[1] - oy), (end[0], end[1] - oy)], (232, 232, 232, int(255 * a)), 5)
    cv.alpha_composite(l.done(), (0, oy))
    pulse = math.exp(-max(0.0, t - Bb['conn']) * 6) if conn else 0.0
    trafo_at(cv, B_W, B_C[0], B_C[1], 7, 7, t, amp=0.9 * pulse, glow2=pulse, scale=a)
    if st is not None:
        if st[0] == 'fly':
            S.paste_center(cv, T.battery_d(190), st[1], st[2], scale=st[4], angle=st[3])
        else:
            S.paste_center(cv, T.battery_d(190), B_BAT[0], B_BAT[1], sx=st[1], sy=st[2])
    if conn and t < Bb['conn'] + 0.3:
        S.glow_fast(cv, end[0], end[1], 80, (180, 220, 255), 0.9 * (1 - (t - Bb['conn']) / 0.3))
    k = S.seg(t, Bb['conn'] - 0.4, Bb['conn'] + 1.6)
    S.paste_center(cv, T.pulse_graph(round(k, 2), 500, 250), B_G[0], B_G[1], scale=pop_in(t, Bb['in'] + 0.2, 0.35))
    if t >= Bb['no']:
        S.paste_center(cv, D.label('✗ NO FUNCIONA', 40, fill=(255, 110, 110), outline=(255, 80, 80)), 735, 395, scale=2.0 - S.ease_in(S.seg(t, Bb['no'], Bb['no'] + 0.15)), angle=-0.06,
                       alpha=min(1, S.seg(t, Bb['no'], Bb['no'] + 0.15) * 2))

B_THROW = []


# ======================= escena P: el poste (frases 10–11) =======================
Pp = {}
POLE_W = 360
POLE_C = (560, 610)
HOUSE_C = (930, 900)
MAG_C = (700, 560)
def setup_P():
    Pp['in'] = P(10) - 0.1
    Pp['miles'] = KW(10, 'MILES') - 0.1
    Pp['120'] = KW(10, '120') - 0.1
    Pp['zoom'] = KW(11, 'ZUMBIDO') - 0.35
    Pp['mag'] = KW(11, 'HIERRO') - 0.2
    Pp['120b'] = KW(11, '120') - 0.1
    add_throw(Pp['in'] - 0.45, POLE_C, lambda t: T.pole(POLE_W), side='l', dur=0.45, arc=140, spin=0.0)
    ev(Pp['miles'], 'zap', 0.4, 0.0); ev(Pp['miles'] + 0.05, 'pop', 0.35, 0.2)
    ev(Pp['120'], 'pop', 0.4, panx(HOUSE_C[0])); ev(Pp['120'] + 0.1, 'switch', 0.4, panx(HOUSE_C[0]))
    ev(Pp['zoom'], 'whoosh', 0.35, 0.0)
    ev(Pp['zoom'] + 0.1, 'hum', 0.16, 0.0, dur=E(11) - Pp['zoom'] + 0.1, f=120)
    ev(Pp['mag'], 'pop', 0.4, 0.2); ev(Pp['120b'], 'tink', 0.3, 0.2, f=2400)
    GEST.extend([(KW(10, 'POSTE'), 0.8, 'present'), (KW(10, 'enchufe'), 0.8, 'open')])
    add_slap(T_P_SLAP)

def draw_P(cv, t, at=None):
    if t < Pp['in'] - 0.5 or t > T_P_SLAP + 1.0:
        return
    if t >= T_P_SLAP and at is None:
        shattered(cv, draw_P, T_P_SLAP, t, 11, y0=230, y1=1080)
        return
    st = throw_state(P_THROW[0], t)
    if st is None:
        return
    hum = 1.0 if t >= Pp['zoom'] else 0.0
    if st[0] == 'fly':
        S.paste_center(cv, T.pole(POLE_W), st[1], st[2], scale=st[4], angle=st[3])
        return
    z = S.ease_io(S.seg(t, Pp['zoom'], Pp['zoom'] + 0.45)) * (1 - S.ease_io(S.seg(t, T_P_SLAP - 0.35, T_P_SLAP)))
    img = T.pole(POLE_W, hum, t)
    pw, ph = img.size
    focus = (pw * 0.24, ph * 0.425)       # el tanque del transformador
    scz = 1 + 0.7 * z
    tx, ty = 330, 620
    cx = (1 - z) * POLE_C[0] + z * (tx - (focus[0] - pw / 2) * scz)
    cy = (1 - z) * POLE_C[1] + z * (ty - (focus[1] - ph / 2) * scz)
    if z < 0.02 and st[0] == 'land':
        S.paste_center(cv, img, POLE_C[0], POLE_C[1], sx=st[1], sy=st[2])
    else:
        paste_clipped(cv, img, cx, cy, scale=scz, box=(0, 292, 1080, 1075))
    # casa (sale de cuadro con el zoom)
    a_h = pop_in(t, Pp['120'] - 0.3) * (1 - S.seg(z, 0.0, 0.4))
    if a_h > 0.01:
        S.paste_center(cv, T.house(190, 1.0 if t >= Pp['120'] + 0.1 else 0.0), HOUSE_C[0], HOUSE_C[1], scale=a_h)
        lbl(cv, '120 V · CASAS EN COLOMBIA', HOUSE_C[0] - 60, HOUSE_C[1] - 135, pop_in(t, Pp['120']) * a_h, (150, 240, 160), 24)
    if t >= Pp['miles'] and z < 0.4:
        a = pop_in(t, Pp['miles']) * (1 - S.seg(z, 0.0, 0.4))
        lbl(cv, 'MILES DE VOLTIOS', 790, 330, a, (255, 140, 120), 28)
        # chispitas en los cables de arriba
        for k in range(4):
            x = 400 + ((t * 260 + k * 90) % 420)
            S.glow_fast(cv, x, POLE_C[1] - 306 + 0.11 * 612 + 8, 18, (255, 220, 120), 0.6 * a)
        lbl(cv, '↓ BAJA', 300, 470, a * pop_in(t, Pp['120'] - 0.2), (255, 230, 140), 36)
    if z > 0.3:
        a = S.seg(z, 0.3, 0.8)
        # ondas de zumbido
        for k in range(3):
            r = 60 + k * 45 + 40 * ((t * 2.2) % 1.0)
            l = D.L(int(2 * r + 20), int(2 * r + 20))
            l.d.arc([10 * SS_, 10 * SS_, (2 * r + 10) * SS_, (2 * r + 10) * SS_], -40, 40, fill=(255, 230, 140, int(200 * a * (1 - k * 0.25))), width=6 * SS_)
            S.paste_center(cv, l.done(), 330 + 60, 620)
        lbl(cv, 'MMMMMM...', 330, 420, a, (255, 230, 140), 30)
    if t >= Pp['mag']:
        a = pop_in(t, Pp['mag'], 0.35)
        kk = math.sin(2 * math.pi * 1.6 * t)
        content = T.lamination(kk, 520, 220)
        S.paste_center(cv, D.magnifier(content, 190), MAG_C[0] + 70, MAG_C[1] + 40, scale=a)
        lbl(cv, 'LÁMINAS DE HIERRO', MAG_C[0], MAG_C[1] - 230, a, (210, 215, 225), 26)
        lbl(cv, 'SE ESTIRAN Y SE ENCOGEN', MAG_C[0], 850, a, (255, 230, 140), 26)
        if t >= Pp['120b']:
            lbl(cv, '120 VECES POR SEGUNDO', MAG_C[0], 905, pop_in(t, Pp['120b']), (255, 255, 255), 28)

P_THROW = []
SS_ = D.SS


# ======================= escena F: remate (frase 12) =======================
Ff = {}
F_C = (640, 640)
def setup_F():
    Ff['in'] = P(12) + 0.2
    Ff['t1'] = KW(12, 'bobinas') - 0.1
    Ff['t2'] = KW(12, 'CAMBIA') - 0.2
    ev(Ff['in'], 'pop', 0.45, 0.0); ev(Ff['t1'], 'pop', 0.4, 0.0); ev(Ff['t2'], 'chime', 0.35, 0.0)
    ev(Ff['in'], 'hum', 0.05, 0.0, dur=P(13) - Ff['in'], f=120)
    GEST.append((KW(12, 'transformador'), 1.0, 'open'))

def draw_F(cv, t, at=None):
    if t < Ff['in'] or t > P(13) + 0.1:
        return
    a = pop_in(t, Ff['in'], 0.35) * (1 - S.ease_in(S.seg(t, P(13) - 0.25, P(13) + 0.1)))
    S.glow_fast(cv, F_C[0], F_C[1], 300, (255, 190, 110), 0.22 * a)
    trafo_at(cv, 440, F_C[0], F_C[1], 8, 8, t, amp=ac(t) * 0.9, glow2=0.5 + 0.5 * abs(ac(t)), scale=a)
    if t >= Ff['t1']:
        aa = pop_in(t, Ff['t1'], 0.35) * a
        S.paste_center(cv, S.fancy_text('2 BOBINAS + HIERRO', 56), 600, 335, scale=aa)
    if t >= Ff['t2']:
        aa = pop_in(t, Ff['t2'], 0.35) * a
        S.paste_center(cv, S.fancy_text('+ UN CAMPO QUE CAMBIA', 52, top=(170, 225, 255), bot=(40, 120, 230), outline=(8, 24, 70)), 640, 418, scale=aa)


# ======================= cierre: botones y reto =======================
Fin = {}
BTN = {'like': (810, 620), 'sub': (810, 755), 'follow': (810, 890)}
Q_C = (330, 500)

def setup_Fin():
    Fin['btn_in'] = P(13) - 0.4
    Fin['hit'] = {'like': KW(13, 'me gusta'), 'sub': KW(13, 'suscríbete'), 'follow': KW(13, 'sígueme')}
    Fin['q'] = KW(13, 'Reto') - 0.1
    Fin['q2'] = KW(13, 'MITAD') - 0.1
    Fin['q3'] = KW(13, 'Cuánto') - 0.1
    for i, k in enumerate(('like', 'sub', 'follow')):
        ev(Fin['btn_in'] + i * 0.1, 'pop', 0.35, 0.4)
        th = Fin['hit'][k]
        JUMPS.append((th - 0.3, 0.55, 70))
        POINTS.append((th - 0.12, th + 0.08, 'l', (lambda kk: (lambda t: (BTN[kk][0] - 180, BTN[kk][1])))(k)))
        ev(th, 'click', 0.6, 0.5); ev(th + 0.02, 'pop', 0.4, 0.5, f0=600, f1=1400)
        if k == 'sub':
            ev(th + 0.05, 'bell', 0.6, 0.5)
        ev(th - 0.3 + 0.55, 'step', 0.5, panx(300))
    ev(Fin['q'], 'whoosh', 0.4, panx(Q_C[0])); ev(Fin['q'] + 0.3, 'block', 0.5, panx(Q_C[0]))
    ev(Fin['q2'], 'pop', 0.4, panx(Q_C[0])); ev(Fin['q3'], 'pop', 0.4, panx(Q_C[0]))
    GEST.append((KW(13, 'Cuánto'), 0.9, 'chin'))
    ev(T_END_SNAP, 'snap', 0.9, -0.2)
    ev(T_END_SNAP + 0.05, 'switch', 0.5, 0.0)
    ev(T_END_SNAP + 1.35, 'tvoff', 0.8, 0.0)

def draw_Fin(cv, t):
    if t >= Fin['btn_in'] and t < T_END_SNAP + 0.4:
        for i, k in enumerate(('like', 'sub', 'follow')):
            s = S.ease_back(S.seg(t, Fin['btn_in'] + i * 0.1, Fin['btn_in'] + i * 0.1 + 0.35)) * (1 - S.ease_in(S.seg(t, T_END_SNAP + 0.05, T_END_SNAP + 0.35)))
            th = Fin['hit'][k]
            pressed = 1.0 if t >= th else 0.0
            sq = 1 - 0.25 * S.jelly(t - th, 3, 6) if t >= th else 1.0
            S.paste_center(cv, D.end_button(k, pressed), BTN[k][0], BTN[k][1], scale=s, sx=2 - sq, sy=sq)
    if Fin['q'] <= t < T_END_SNAP + 0.4:
        out = S.ease_in(S.seg(t, T_END_SNAP + 0.05, T_END_SNAP + 0.35))
        u = S.seg(t, Fin['q'], Fin['q'] + 0.35)
        x = Q_C[0] - 500 * (1 - S.ease_out(u))
        kk = (1 - out)
        hide = t >= Fin['q2']
        S.paste_center(cv, T.trafo_symbol(440, None, hide, '120 V', '?' if hide else ''), x, Q_C[1], scale=0.9 * kk)
        S.paste_center(cv, D.label('RETO', 30, fill=(255, 220, 120)), Q_C[0], Q_C[1] - 190,
                       scale=S.ease_back(S.seg(t, Fin['q'] + 0.2, Fin['q'] + 0.5)) * kk)
        if t >= Fin['q2']:
            a = S.ease_back(S.seg(t, Fin['q2'], Fin['q2'] + 0.3)) * kk
            S.paste_center(cv, D.label('OTRA BOBINA: MITAD DE VUELTAS', 25, fill=(150, 220, 255)), Q_C[0] + 20, Q_C[1] + 205, scale=a)
        if t >= Fin['q3']:
            a = S.ease_back(S.seg(t, Fin['q3'], Fin['q3'] + 0.3)) * kk
            S.paste_center(cv, D.label('¿CUÁNTOS VOLTIOS SALEN?', 30, fill=(255, 255, 255)), Q_C[0] + 20, Q_C[1] + 262, scale=a)


def setup_all():
    setup_walks()
    setup_title()
    setup_H()
    setup_R()
    R_THROW.append(THROWS[-1])
    setup_N()
    N_THROW.append(THROWS[-1])
    setup_B()
    B_THROW.append(THROWS[-1])
    setup_P()
    P_THROW.append(THROWS[-1])
    setup_F()
    setup_Fin()
    react = [
        (T_PLUG + 0.06, 0.4, 50, None),                    # ¡prendió!
        (Rr['volt'] + 0.05, 0.4, 45, None),                # ¡voltaje!
        (Nn['doble'] + 0.2, 0.4, 45, 'thumbs'),            # el doble
        (Pp['miles'] + 0.05, 0.4, 45, None),
        (KW(12, 'CAMBIA') + 0.1, 0.45, 65, 'up'),          # remate
    ]
    for t0, d, h, kind in react:
        if h > 0:
            JUMPS.append((t0, d, h))
            ev(t0 + d, 'step', 0.45, 0.0, heavy=0.9)
        if kind:
            REACT_ARMS.append((t0, d, kind))


def bg_at(t, light):
    L = LB.layers()
    base, arr = L['full'], L['full_np']
    if light >= 0.999:
        return base.copy()
    if light <= 0.001:
        return Image.new('RGBA', (W, H), (0, 0, 0, 255))
    return Image.fromarray((arr * light).astype(np.uint8), 'RGB').convert('RGBA')


setup_all()


def render_frame(t):
    pose, x, yf, light, glow = char_state(t)
    cv = bg_at(t, light)
    LB.draw_anim(cv, t, light)
    sw = 0.0
    if t >= T_END_SNAP:
        sw = 0.04 * math.sin((t - T_END_SNAP) * 5) * math.exp(-(t - T_END_SNAP))
    if T_PLUG <= t < T_PLUG + 1.4:
        sw += 0.05 * math.sin((t - T_PLUG) * 7) * math.exp(-(t - T_PLUG) * 2.5)
    S.draw_lamp(cv, on=light, swing=sw)
    if light > 0.05:
        S.glow_fast(cv, S.LAMP_X + math.sin(sw) * S.LAMP_Y, math.cos(sw) * S.LAMP_Y + 22, 90, (255, 230, 150), 0.6 * light)
    if t >= T_TITLE_FLY + 0.4 and t < T_END_SNAP + 0.1:
        S.draw_label(cv, LABEL_TXT, alpha=S.seg(t, T_TITLE_FLY + 0.4, T_TITLE_FLY + 0.6) * light)
    # ----- escenas -----
    draw_H(cv, t)
    draw_R(cv, t)
    draw_N(cv, t)
    draw_B(cv, t)
    draw_P(cv, t)
    draw_F(cv, t)
    draw_title(cv, t)
    # ----- modo esquina (planos cercanos) -----
    ck = corner_k(t)
    xr = x + (165 - x) * ck
    scl = S.SCALE * (1 - 0.3 * ck)
    # ----- sombra -----
    if light > 0.05:
        h = S.FLOOR_Y - yf
        sh_w = 150 * max(0.4, 1 - h / 600) * (1 - 0.3 * ck)
        d = ImageDraw.Draw(cv, 'RGBA')
        d.ellipse([xr - sh_w, S.FLOOR_Y - 14, xr + sh_w, S.FLOOR_Y + 12], fill=(0, 0, 0, int(110 * light * max(0.3, 1 - h / 500))))
    # ----- personaje -----
    char_light = 0.32 + 0.68 * light if t < T_END_SNAP + 1.3 else 0.32
    if T_PLUG <= t < T_PLUG + 0.5:
        char_light = min(1.3, char_light + 0.3 * (1 - (t - T_PLUG) / 0.5))
    CH.render(cv, pose, dict(scale=scl, ox=xr, oy=yf, view_yaw=0.12 * math.sin(t * 0.2)), light=char_light, t=t)
    draw_Fin(cv, t)
    if T_PLUG + 0.04 <= t < T_PLUG + 0.35:
        u = (t - T_PLUG - 0.04) / 0.31
        S.glow_fast(cv, BULB_C[0], BULB_C[1] - 25, 600, (255, 240, 200), 0.5 * (1 - u) ** 2)
    sub, si = TL.subtitle_at(t)
    if sub and t < T_END_SNAP + 0.2:
        S.draw_subtitle(cv, sub)
    dx, dy = shake_at(t)
    if dx or dy:
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        sh.paste(cv, (dx, dy))
        cv = sh
    t_off = T_END_SNAP + 1.35
    if t >= t_off:
        u = t - t_off
        out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        if u < 0.25:
            k = 1 - S.ease_in(u / 0.25)
            hgt = max(4, int(H * k))
            sq = cv.resize((W, hgt))
            arr = np.array(sq, np.float32); arr[..., :3] = arr[..., :3] * k + 255 * (1 - k); sq = Image.fromarray(arr.astype(np.uint8))
            out.paste(sq, (0, (H - hgt) // 2))
        elif u < 0.5:
            k = 1 - S.ease_in((u - 0.25) / 0.25)
            wd = max(6, int(W * k))
            d = ImageDraw.Draw(out)
            d.rectangle([(W - wd) // 2, H // 2 - 3, (W + wd) // 2, H // 2 + 3], fill=(255, 255, 255))
        elif u < 0.8:
            d = ImageDraw.Draw(out)
            r = 8 * (1 - (u - 0.5) / 0.3)
            d.ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=(255, 255, 255))
        cv = out
    return cv.convert('RGB')


if __name__ == '__main__':
    print('duración', round(T_END, 2))
    for i in range(len(PHRASES)):
        print(i, round(P(i), 2), round(E(i), 2), PHRASES[i][1][:50])
