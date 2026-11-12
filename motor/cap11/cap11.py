#!/usr/bin/env python3
# Capítulo 11: El motor DC. Vertical 1080x1920, 30 fps.
# Gancho en el segundo 0: laboratorio YA prendido, título arriba. Sobre el mesón: una pila AA y un
# motorcito de juguete con hélice. A los 0,45 s él toca la pila con el cable: ¡ZUUM!, la hélice arranca,
# sopla y unos papeles salen volando.
# Mejora nueva de este capítulo: CÁMARA LENTA CON CONTADOR. Cuando la bobina gira, un contador de
# "media vuelta" marca en pantalla el instante en que el conmutador cambia la corriente (flash en el
# anillo y en los alambres ⊙/⊗), para que se VEA la causa del giro continuo.
# Primer capítulo hecho 100 % en la nube (sin el PC de Edwin).
# Regla: cada rótulo sale de VERIFICACION.md (códigos M#).
import math
import random
import numpy as np
from PIL import Image, ImageDraw
import scene as S
import diagrams as D
import inductor as I
import motor as M
import lab as LB
import char3d as C
from timeline import TL, PHRASES

W, H = S.W, S.H
FPS = S.FPS
CH = C.Character()
HOME_X = 230
INTRO_X = 290
LABEL_TXT = 'CAP. 11 · EL MOTOR'

P = lambda i: TL.s(i)
E = lambda i: TL.e(i)
KW = TL.kw

# ======================= tiempos clave =======================
T_PLUG = 0.45                       # toca la pila con el cable: arranca la hélice
T_BONK = T_PLUG                     # (la música usa este nombre)
T_TITLE = T_PLUG
T_TITLE_FLY = P(1) + 0.15
T_WALK_HOME = P(1) + 0.2
T_H_SLAP = P(2) - 0.15              # se rompe el montaje del gancho
T_R_SLAP = E(5) + 0.15              # se rompe el motor por dentro (sin truco)
T_C_SLAP = E(8) + 0.2               # se rompe el conmutador
T_V_SLAP = E(9) + 0.15              # se rompe el control
T_G_SLAP = E(10) + 0.15             # se rompe la manivela
T_END_SNAP = E(12) + 0.6
T_END = TL.END

# planos cercanos: el personaje se va a la esquina
CORNER = [(KW(6, 'CONMUTADOR') - 0.45, P(7) + 0.2), (KW(9, 'PESA') - 0.5, E(9) + 0.05)]
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
    a = KW(12, 'Respóndeme') + 0.2
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
    (0.0, 'guino'), (T_PLUG + 0.02, 'sorpresa'), (KW(0, 'pila'), 'feliz'), (KW(0, 'alambre'), 'curioso'),
    (KW(0, 'GIRA'), 'sorpresa'), (KW(0, 'Cómo'), 'pensando'), (KW(0, 'MOTOR'), 'feliz'),
    (P(1), 'guino'), (KW(1, 'VIBRAR'), 'curioso'),
    (P(2), 'feliz'), (KW(2, 'IMANES'), 'curioso'),
    (P(3), 'feliz'), (KW(3, 'EMPUJÓN'), 'sorpresa'),
    (P(4), 'curioso'), (KW(4, 'GIRA'), 'feliz'),
    (P(5) - 0.1, 'pensando'), (KW(5, 'QUIETA'), 'sorpresa'),
    (P(6), 'guino'), (KW(6, 'CONMUTADOR'), 'feliz'),
    (P(7), 'curioso'), (KW(7, 'MISMO'), 'feliz'),
    (P(8), 'sorpresa'), (KW(8, 'REVÉS'), 'feliz'),
    (P(9), 'guino'), (KW(9, 'PESA'), 'curioso'), (KW(9, 'TIEMBLA'), 'sorpresa'),
    (P(10), 'curioso'), (KW(10, 'VOLTAJE'), 'sorpresa'), (KW(10, 'molino'), 'feliz'),
    (P(11), 'corazon'),
    (P(12), 'feliz'), (KW(12, 'Reto'), 'guino'), (KW(12, 'dónde'), 'pensando'), (KW(12, 'Respóndeme'), 'feliz'),
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
G_X = 400
def setup_walks():
    plan = [
        (T_WALK_HOME, HOME_X, 0.6),
        (P(10) - 0.35, G_X, 0.5), (T_G_SLAP + 0.1, HOME_X, 0.5),
        (KW(12, 'Reto') - 0.1, 290, 0.7),
    ]
    x = INTRO_X
    for t0, x1, d in plan:
        WALKS.append((t0, t0 + d, x, x1))
        n = max(2, int(abs(x1 - x) / 70))
        for k in range(n):
            ev(t0 + 0.12 + k * (d - 0.24) / max(1, n - 1), 'step', 0.4, panx(x + (x1 - x) * k / max(1, n - 1)), heavy=0.75)
        x = x1


def intro_pose(p, t, x, yf):
    # tiene el cable en la mano, toca la pila y se echa para atrás cuando arranca la hélice
    if t < T_PLUG:
        p.lean += 0.1
        p.head = (p.head[0] - 0.12, p.head[1] + 0.4, p.head[2])
        p.look = (1.0, 0.3)
    elif t < P(0) + 1.2:
        u = t - T_PLUG
        j = S.jelly(u, 3.0, 4.0)
        p.lean += -0.22 * math.exp(-u * 3) + 0.04 * math.sin(u * 8)
        p.sx *= 1 + 0.07 * j; p.sy *= 1 - 0.07 * j
        p.head = (p.head[0] + 0.1 * math.exp(-u * 2), p.head[1] - 0.3 * math.exp(-u * 2), p.head[2])


def diagram_active(t):
    return (P(2) + 0.4 <= t < T_R_SLAP) or (P(11) + 0.3 <= t < P(12) - 0.2)


def light_at(t):
    if t > T_END_SNAP + 0.05:
        return 0.0
    return 1.0


# ======================= título =======================
_tc = {}
def title_imgs():
    if not _tc:
        _tc['a'] = S.fancy_text('¿CÓMO FUNCIONA UN', 64)
        _tc['b'] = S.fancy_text('MOTOR?', 110, top=(255, 214, 150), bot=(214, 110, 40), outline=(70, 30, 6))
    return _tc

def setup_title():
    ev(KW(0, 'MOTOR') - 0.05, 'block', 0.5, 0.0, pitch=1.1)
    ev(T_TITLE_FLY, 'whoosh', 0.4, 0.0)

def draw_title(cv, t):
    TI = title_imgs()
    if t < T_TITLE_FLY + 0.5:
        fly = S.ease_in(S.seg(t, T_TITLE_FLY, T_TITLE_FLY + 0.45))
        k0 = KW(0, 'MOTOR')
        bump = 1 + 0.12 * S.jelly(t - k0, 3, 5) if t >= k0 else 1.0
        ya = 262 + (S.ROOM_T + 46 - 262) * fly; yb = 355 + (S.ROOM_T + 46 - 355) * fly
        sc = 1 - 0.75 * fly
        S.paste_center(cv, TI['a'], 540, ya, scale=sc, alpha=1 - fly * 0.9)
        S.paste_center(cv, TI['b'], 540, yb, scale=sc * bump, alpha=1 - fly * 0.9)


# ======================= giro (tabla de ángulos integrada) =======================
DT = 1 / 240.0
class Spin:
    """ángulo = integral de una velocidad angular w(t) (rad/s), precalculada"""
    def __init__(self, wfn, t0, t1, a0=0.0):
        self.t0 = t0
        n = int((t1 - t0) / DT) + 2
        ts = t0 + np.arange(n) * DT
        w = np.array([wfn(x) for x in ts])
        self.a = a0 + np.concatenate([[0], np.cumsum((w[1:] + w[:-1]) / 2 * DT)])
        self.w = w
    def __call__(self, t):
        i = (t - self.t0) / DT
        if i <= 0:
            return float(self.a[0])
        if i >= len(self.a) - 1:
            return float(self.a[-1])
        k = int(i); f = i - k
        return float(self.a[k] * (1 - f) + self.a[k + 1] * f)
    def omega(self, t):
        i = int(max(0, min(len(self.w) - 1, (t - self.t0) / DT)))
        return float(self.w[i])


# ======================= escena H: gancho (frases 0–1) =======================
Hh = {}
BAT_C = (500, 1060)
MOT_C = (810, 1010)
MOT_W = 190
PROP_Y = MOT_C[1] - 170
PAPERS = [(-150, 0.0), (-60, 0.35), (120, 0.15), (190, 0.5)]
def w_hook(t):
    if t < T_PLUG:
        return 0.0
    return 32.0 * (1 - math.exp(-(t - T_PLUG) / 0.3))
SPIN_H = Spin(w_hook, 0.0, P(2) + 1.2)

def setup_H():
    POINTS.append((0.0, T_PLUG + 0.25, 'l', (BAT_C[0], BAT_C[1] - 135)))
    ev(T_PLUG, 'click', 0.6, panx(BAT_C[0]))
    ev(T_PLUG + 0.02, 'zap', 0.45, panx(BAT_C[0]))
    ev(T_PLUG + 0.05, 'hum', 0.1, panx(MOT_C[0]), dur=T_H_SLAP - T_PLUG, f=180)
    ev(T_PLUG + 0.1, 'whoosh', 0.5, panx(MOT_C[0]))
    SHAKES.append((T_PLUG + 0.05, 0.2, 5))
    GEST.append((T_PLUG + 0.35, 0.8, 'shade'))
    Hh['l_pila'] = KW(0, 'pila') - 0.05
    Hh['l_iman'] = KW(0, 'imán') - 0.05
    Hh['l_alambre'] = KW(0, 'alambre') - 0.05
    Hh['gira'] = KW(0, 'GIRA') - 0.05
    Hh['promise'] = KW(1, 'VIBRAR') - 0.2
    for k in ('l_pila', 'l_iman', 'l_alambre'):
        ev(Hh[k], 'pop', 0.4, 0.3)
    ev(Hh['promise'], 'chime', 0.3, 0.3)
    add_slap(T_H_SLAP)

def draw_motor_rig(cv, t, ang, speed, cx=MOT_C[0], cy=MOT_C[1]):
    S.paste_center(cv, M.toy_motor(MOT_W), cx, cy)
    S.paste_center(cv, M.propeller(ang, speed, 360), cx, cy - 172)
    if speed > 6:
        a = min(1.0, (speed - 6) / 16)
        S.speed_lines(cv, cx - 120, cy - 170, cx - 150, cy - 420, n=3, color=(255, 255, 255, int(110 * a)), width=4, seed=int(t * 12))
        S.speed_lines(cv, cx + 120, cy - 170, cx + 150, cy - 420, n=3, color=(255, 255, 255, int(110 * a)), width=4, seed=int(t * 12) + 7)

def draw_H(cv, t, at=None):
    if t > T_H_SLAP + 1.0:
        return
    if t >= T_H_SLAP and at is None:
        shattered(cv, draw_H, T_H_SLAP, t, 3, y0=230, y1=1150)
        return
    ang = SPIN_H(t); w = SPIN_H.omega(t)
    on = 1.0 if t >= T_PLUG else 0.0
    bat = I.battery_aa(220)
    t1, t2 = M.toy_motor_terms(*MOT_C, MOT_W)
    l = D.L(W, 1000); oy = 500
    # cable negro: del − de la pila (abajo) a la terminal izquierda del motor, por el mesón
    for wcol, ww in (((20, 20, 24), 11), ((60, 64, 72), 6)):
        l.line([(BAT_C[0], 1146 - oy), (t1[0], 1146 - oy), (t1[0], t1[1] - 4 - oy)], wcol + (255,), ww)
    # cable rojo: de la terminal derecha, por detrás del motor y por arriba, hasta la mano (o al + de la pila)
    if t < T_PLUG:
        hx, hy = hand_pos(t, 'l')
        pp = (hx + 8, hy)
    else:
        pp = (BAT_C[0], BAT_C[1] - 122)
    xr_ = MOT_C[0] + 150
    for wcol, ww in (((150, 30, 30), 11), ((220, 60, 60), 6)):
        l.line([(t2[0], t2[1] - 4 - oy), (xr_, t2[1] - 4 - oy), (xr_, 740 - oy), (BAT_C[0] + 60, 740 - oy), (BAT_C[0] + 60, pp[1] - 50 - oy), (pp[0], pp[1] - oy)], wcol + (255,), ww)
    cv.alpha_composite(l.done(), (0, oy))
    S.paste_center(cv, bat, BAT_C[0], BAT_C[1])
    # papeles que salen volando con el viento
    for k, (dx, d0) in enumerate(PAPERS):
        x0, y0 = MOT_C[0] + dx, 1142
        if t < T_PLUG + 0.15 + d0 * 0.4:
            pos = (x0, y0); rot = 0.0; sc = 1.0
        else:
            u = t - (T_PLUG + 0.15 + d0 * 0.4)
            pos = (x0 + (dx * 0.8) * u + 30 * math.sin(u * 4 + k), y0 - 520 * u + 90 * u * u)
            rot = u * (3 + k); sc = 1.0
            if pos[1] > y0:
                pos = (pos[0], y0)
        pl = D.L(70, 50)
        pl.poly([(4, 10), (64, 4), (66, 44), (6, 46)], fill=(248, 246, 236, 255), outline=(170, 168, 160, 255), width=2)
        for j in range(3):
            pl.line([(14, 16 + j * 9), (56, 14 + j * 9)], (150, 160, 190, 200), 2)
        S.paste_center(cv, pl.done(), pos[0], pos[1] - 18, angle=rot, sx=1.0, sy=0.35 + 0.65 * abs(math.cos(rot * 0.7)))
    draw_motor_rig(cv, t, ang, w)
    if T_PLUG <= t < T_PLUG + 0.6:
        a = S.ease_back(S.seg(t, T_PLUG, T_PLUG + 0.15)) * (1 - S.seg(t, T_PLUG + 0.45, T_PLUG + 0.6))
        S.paste_center(cv, burst('¡ZUUM!', 42), MOT_C[0] + 60, MOT_C[1] - 330, scale=a, angle=0.1)
        S.glow_fast(cv, BAT_C[0], BAT_C[1] - 120, 70, (255, 240, 180), 0.8 * (1 - S.seg(t, T_PLUG, T_PLUG + 0.3)))
    lbl(cv, 'PILA', BAT_C[0], BAT_C[1] - 190, pop_in(t, Hh['l_pila']), (255, 230, 150), 26)
    lbl(cv, 'IMÁN + ALAMBRE (ADENTRO)', 640, 690, pop_in(t, Hh['l_iman']), (150, 220, 255), 22)
    if t >= Hh['promise']:
        a = pop_in(t, Hh['promise']) * (1 - S.seg(t, T_H_SLAP - 0.3, T_H_SLAP))
        jit = 4 * math.sin(t * 60) if t >= Hh['promise'] + 0.3 else 0
        S.paste_center(cv, M.gamepad(230), 330 + jit, 560, scale=a, angle=0.08)
        lbl(cv, 'AL FINAL: EL DEL CONTROL', 560, 440, a, (255, 220, 120), 34)


# ======================= escena R: por dentro (frases 2–5) =======================
Rr = {}
R_C = (610, 600)
def setup_R():
    Rr['in'] = P(2) - 0.05
    Rr['l_b'] = KW(2, 'BOBINA') - 0.05
    Rr['l_m'] = KW(2, 'IMANES') - 0.05
    Rr['one'] = P(3) - 0.1
    Rr['cur'] = KW(3, 'CORRIENTE') - 0.1
    Rr['campo'] = KW(3, 'campo') - 0.1
    Rr['push'] = KW(3, 'EMPUJÓN') - 0.15
    Rr['both'] = P(4) - 0.05
    Rr['up'] = KW(4, 'ARRIBA') - 0.1
    Rr['down'] = KW(4, 'ABAJO') - 0.1
    Rr['gira'] = KW(4, 'GIRA') - 0.15
    Rr['derecha'] = KW(5, 'DERECHA') - 0.1
    Rr['quieta'] = KW(5, 'QUIETA') - 0.1
    add_throw(Rr['in'] - 0.45, R_C, lambda t: M.motor_inside(0.0, show_cur=0.0, field=0.0), side='l', dur=0.45, land_sfx='block')
    ev(Rr['l_b'], 'pop', 0.4, 0.0); ev(Rr['l_m'], 'pop', 0.4, -0.4); ev(Rr['l_m'] + 0.12, 'pop', 0.4, 0.4)
    ev(Rr['cur'], 'zap', 0.35, 0.3); ev(Rr['campo'], 'tink', 0.3, 0.0, f=2000)
    ev(Rr['push'], 'boing', 0.4, 0.3, f0=250, f1=700); SHAKES.append((Rr['push'], 0.15, 4))
    ev(Rr['up'], 'pop', 0.4, 0.3, f0=400, f1=1100); ev(Rr['down'], 'pop', 0.4, -0.3, f0=900, f1=350)
    ev(Rr['gira'], 'whoosh', 0.4, 0.0)
    ev(Rr['derecha'], 'thud', 0.45, 0.0); ev(Rr['quieta'], 'marker', 0.35, 0.0, dur=0.4)
    GEST.extend([(KW(2, 'BOBINA'), 0.9, 'present'), (KW(3, 'EMPUJÓN'), 0.8, 'open'), (KW(4, 'GIRA'), 0.8, 'present'),
                 (KW(5, 'QUIETA'), 0.9, 'chin')])
    add_slap(T_R_SLAP)

def theta_R(t):
    """sin conmutador: arranca acostada, gira y oscila hasta quedar derecha"""
    if t < Rr['gira']:
        return 0.0
    u = t - Rr['gira']
    return math.pi / 2 - (math.pi / 2) * math.exp(-0.55 * u) * math.cos(2.3 * u)

def draw_R(cv, t, at=None):
    if t < Rr['in'] - 0.5 or t > T_R_SLAP + 1.0:
        return
    if t >= T_R_SLAP and at is None:
        shattered(cv, draw_R, T_R_SLAP, t, 5, y0=230, y1=1060)
        return
    st = throw_state(R_THROW[0], t)
    if st is None:
        return
    if st[0] == 'fly':
        S.paste_center(cv, M.motor_inside(0.0, show_cur=0.0, field=0.0), st[1], st[2], scale=st[4], angle=st[3])
        return
    th = theta_R(t)
    one = Rr['one'] <= t < Rr['both']
    show_cur = S.seg(t, Rr['cur'], Rr['cur'] + 0.2)
    field = S.seg(t, Rr['campo'], Rr['campo'] + 0.3)
    if t < Rr['both']:
        push = S.ease_out(S.seg(t, Rr['push'], Rr['push'] + 0.3))
    else:
        push = 1.0 if t < Rr['gira'] else 1.0
    if Rr['both'] <= t < Rr['up']:
        push = 0.0
    img = M.motor_inside(th, cur=1, show_cur=show_cur, push=push, field=field, t=t, highlight_one=one)
    if Rr['both'] <= t < Rr['down'] and t >= Rr['up']:
        # solo el empujón de arriba (lado derecho) mientras dice "arriba"
        img = M.motor_inside(th, cur=1, show_cur=show_cur, push=0.0, field=field, t=t)
        l = D.L(img.width, img.height)
        ex, ey = M.coil_end_pos(th, 0)
        px, py = img.width / 2 + ex, img.height / 2 + ey
        D.arrow(l, (px, py - 38), (px, py - 38 - 95 * S.ease_out(S.seg(t, Rr['up'], Rr['up'] + 0.3))), M.PUSH + (255,), width=10, head=24)
        img = img.copy(); img.alpha_composite(l.done())
    if st[0] == 'land' and t < Rr['l_b']:
        S.paste_center(cv, img, R_C[0], R_C[1], sx=st[1], sy=st[2])
    else:
        bump = 0
        if one and t >= Rr['push']:
            bump = -16 * S.jelly(t - Rr['push'], 3, 4)
        S.paste_center(cv, img, R_C[0], R_C[1] + bump * 0)
    # rótulos
    a_l = 1 - S.seg(t, Rr['one'] - 0.2, Rr['one'])
    if a_l > 0.01:
        lbl(cv, 'BOBINA (VISTA DE PUNTA)', R_C[0], R_C[1] + 270, pop_in(t, Rr['l_b']) * a_l, (255, 200, 140), 28)
        lbl(cv, 'IMÁN', R_C[0] - 250, R_C[1] - 205, pop_in(t, Rr['l_m']) * a_l, (255, 150, 140), 28)
        lbl(cv, 'IMÁN', R_C[0] + 250, R_C[1] - 205, pop_in(t, Rr['l_m'] + 0.12) * a_l, (150, 190, 255), 28)
    if one:
        lbl(cv, '⊙ CORRIENTE SALE HACIA TI', R_C[0], R_C[1] + 270, pop_in(t, Rr['cur']), (255, 230, 140), 26)
        lbl(cv, 'CAMPO DEL IMÁN →', R_C[0], R_C[1] - 205, pop_in(t, Rr['campo']), (120, 210, 255), 26)
        if t >= Rr['push']:
            S.paste_center(cv, burst('¡EMPUJÓN!', 34), R_C[0] - 140, R_C[1] - 120, scale=S.ease_back(S.seg(t, Rr['push'], Rr['push'] + 0.2)), angle=0.08)
    if Rr['both'] <= t < Rr['derecha']:
        lbl(cv, 'UN LADO ↑   EL OTRO ↓', R_C[0], R_C[1] + 270, pop_in(t, Rr['up']), (255, 230, 140), 28)
        if t >= Rr['gira']:
            S.paste_center(cv, burst('¡GIRA!', 40), R_C[0], R_C[1] - 250, scale=S.ease_back(S.seg(t, Rr['gira'], Rr['gira'] + 0.2)))
    if t >= Rr['derecha']:
        lbl(cv, 'SIN TRUCO: DERECHA = SIN GIRO', R_C[0], R_C[1] + 270, pop_in(t, Rr['derecha']), (255, 170, 150), 26)
        if t >= Rr['quieta']:
            S.paste_center(cv, stamp_img('SE QUEDA QUIETA', 40), R_C[0], R_C[1] - 250, scale=pop_in(t, Rr['quieta']), angle=-0.06)

R_THROW = []


# ======================= escena C: el conmutador (frases 6–8) =======================
Cc = {}
C_MI = (650, 530); C_MI_S = 0.8
C_CO = (650, 900)
C_BAT = (880, 1072)
W_SLOW = 1.7          # rad/s en cámara lenta
def setup_C():
    Cc['in'] = P(6) - 0.05
    Cc['conm'] = KW(6, 'CONMUTADOR') - 0.1
    Cc['spin'] = KW(6, 'CONMUTADOR') + 0.35
    Cc['mismo'] = KW(7, 'MISMO') - 0.1
    Cc['flip'] = KW(8, 'VOLTEAS') - 0.05
    Cc['reves'] = KW(8, 'REVÉS') - 0.1
    add_throw(Cc['in'] - 0.45, C_CO, lambda t: M.commutator(math.pi / 2, w=460), side='l', dur=0.45, land_sfx='block')
    ev(Cc['conm'], 'pop', 0.4, 0.0); ev(Cc['conm'] + 0.1, 'chime', 0.3, 0.0)
    ev(Cc['spin'], 'hum', 0.06, 0.0, dur=T_C_SLAP - Cc['spin'], f=150)
    ev(Cc['mismo'], 'pop', 0.4, 0.3)
    ev(Cc['flip'], 'whoosh', 0.45, 0.0); ev(Cc['flip'] + 0.35, 'block', 0.5, 0.0, pitch=1.2)
    ev(Cc['reves'], 'boing', 0.4, 0.0, f0=600, f1=250)
    GEST.extend([(KW(6, 'CONMUTADOR'), 0.8, 'present'), (KW(7, 'MISMO'), 0.8, 'open'), (KW(8, 'VOLTEAS'), 0.6, 'count')])
    add_slap(T_C_SLAP)
    # instantes en que cambia la corriente (bobina derecha: theta = pi/2 + k pi)
    Cc['flips'] = []
    tt = Cc['spin']; prev = SPIN_C(tt)
    while tt < T_C_SLAP:
        tt += 1 / 120
        a = SPIN_C(tt)
        if math.floor((prev - math.pi / 2) / math.pi) != math.floor((a - math.pi / 2) / math.pi):
            Cc['flips'].append(tt)
            ev(tt, 'tink', 0.32, 0.0, f=2400)
        prev = a

def w_C(t):
    if t < Cc_spin_t():
        return 0.0
    w = W_SLOW * S.ease_io(S.seg(t, Cc_spin_t(), Cc_spin_t() + 0.4))
    f = Cc_flip_t()
    if t >= f:
        w = W_SLOW * (1 - 2 * S.ease_io(S.seg(t, f + 0.15, f + 0.75)))
    return w

def Cc_spin_t():
    return KW(6, 'CONMUTADOR') + 0.35
def Cc_flip_t():
    return KW(8, 'VOLTEAS') - 0.05
SPIN_C = Spin(w_C, P(6) - 1.0, T_C_SLAP + 1.2, a0=0.0)

def cur_C(t, th):
    """el conmutador hace que el alambre del lado derecho siempre tenga ⊙ (o ⊗ con la pila volteada)"""
    s = 1 if math.cos(th) >= 0 else -1
    flipped = t >= Cc_flip_t() + 0.35
    return -s if flipped else s

def draw_C(cv, t, at=None):
    if t < Cc['in'] - 0.5 or t > T_C_SLAP + 1.0:
        return
    if t >= T_C_SLAP and at is None:
        shattered(cv, draw_C, T_C_SLAP, t, 7, y0=230, y1=1150)
        return
    st = throw_state(C_THROW[0], t)
    if st is None:
        return
    th = SPIN_C(t)
    flipped = t >= Cc['flip'] + 0.35
    co = M.commutator(th + math.pi / 2, w=460, plus_left=not flipped)
    if st[0] == 'fly':
        S.paste_center(cv, co, st[1], st[2], scale=st[4], angle=st[3])
        return
    a = S.seg(t, Cc['in'] + 0.1, Cc['in'] + 0.4)
    cur = cur_C(t, th)
    mi = M.motor_inside(th, cur=cur, show_cur=1.0, push=1.0 if t >= Cc['spin'] else 0.0, field=1.0, t=t)
    S.paste_center(cv, mi, C_MI[0], C_MI[1], scale=C_MI_S * pop_in(t, Cc['in'] + 0.1, 0.35))
    # flash en cada cambio de corriente + contador de medias vueltas (mejora del cap. 11)
    last = [f for f in Cc['flips'] if f <= t]
    if last:
        u = t - last[-1]
        if u < 0.35:
            S.glow_fast(cv, C_CO[0], C_CO[1], 170, (255, 230, 140), 0.9 * (1 - u / 0.35))
            S.glow_fast(cv, C_MI[0], C_MI[1], 240, (255, 230, 140), 0.35 * (1 - u / 0.35))
    sx = sy = None
    if st[0] == 'land':
        sx, sy = st[1], st[2]
    S.paste_center(cv, co, C_CO[0], C_CO[1], sx=sx, sy=sy)
    # pila (se voltea)
    if t >= Cc['in'] + 0.2:
        rot = math.pi * S.ease_io(S.seg(t, Cc['flip'], Cc['flip'] + 0.35))
        hop = 120 * math.sin(math.pi * S.seg(t, Cc['flip'], Cc['flip'] + 0.35))
        S.paste_center(cv, M.battery_h(230), C_BAT[0], C_BAT[1] - hop, angle=rot, scale=pop_in(t, Cc['in'] + 0.2))
        if t >= Cc['flip'] + 0.35:
            lbl(cv, 'PILA VOLTEADA', C_BAT[0], C_BAT[1] - 75, pop_in(t, Cc['flip'] + 0.35), (255, 230, 150), 22)
    lbl(cv, 'CONMUTADOR', C_CO[0], C_CO[1] - 175, pop_in(t, Cc['conm']) * (1 - S.seg(t, Cc['mismo'] - 0.3, Cc['mismo'] - 0.1)), (255, 210, 120), 30)
    lbl(cv, 'ESCOBILLA', C_CO[0] - 250, C_CO[1] + 75, pop_in(t, Cc['conm'] + 0.15) * (1 - S.seg(t, Cc['spin'] + 1.5, Cc['spin'] + 1.8)), (210, 210, 220), 22)
    lbl(cv, 'ESCOBILLA', C_CO[0] + 250, C_CO[1] + 75, pop_in(t, Cc['conm'] + 0.25) * (1 - S.seg(t, Cc['spin'] + 1.5, Cc['spin'] + 1.8)), (210, 210, 220), 22)
    if t >= Cc['spin']:
        n = len(last)
        if n > 0:
            u = t - last[-1]
            k = S.ease_back(S.seg(u, 0, 0.2))
            S.paste_center(cv, D.label(f'MEDIA VUELTA #{n}: ¡CAMBIA LA CORRIENTE!', 26, fill=(255, 235, 150)), C_MI[0], 330, scale=0.85 + 0.15 * k)
        lbl(cv, 'CÁMARA LENTA', 930, 640, 1.0 if t < Cc['flip'] else 1 - S.seg(t, Cc['flip'], Cc['flip'] + 0.2), (200, 200, 210), 20)
    if Cc['mismo'] <= t < Cc['flip']:
        S.paste_center(cv, S.fancy_text('SIEMPRE AL MISMO LADO', 46, top=(170, 255, 200), bot=(30, 170, 110), outline=(5, 50, 30)), 640, 690, scale=pop_in(t, Cc['mismo']))
    if t >= Cc['reves']:
        S.paste_center(cv, S.fancy_text('¡AL REVÉS!', 64, top=(255, 200, 170), bot=(230, 80, 50), outline=(70, 15, 5)), 640, 690, scale=pop_in(t, Cc['reves']))

C_THROW = []


# ======================= escena V: el control que vibra (frase 9) =======================
Vv = {}
V_C = (640, 600)
V_W = 600
def setup_V():
    Vv['in'] = P(9) - 0.1
    Vv['muchos'] = KW(9, 'muchos') - 0.1
    Vv['open'] = KW(9, 'motorcito') - 0.2
    Vv['pesa'] = KW(9, 'PESA') - 0.1
    Vv['girar'] = KW(9, 'girar') - 0.15
    Vv['tiembla'] = KW(9, 'TIEMBLA') - 0.1
    add_throw(Vv['in'] - 0.45, V_C, lambda t: M.gamepad(V_W), side='l', dur=0.45, land_sfx='block')
    ev(Vv['muchos'], 'pop', 0.35, 0.0); ev(Vv['open'], 'whoosh', 0.35, -0.3); ev(Vv['pesa'], 'pop', 0.4, -0.3)
    ev(Vv['girar'], 'buzz', 0.35, -0.3)
    ev(Vv['girar'] + 0.35, 'buzz', 0.35, -0.3)
    ev(Vv['tiembla'], 'buzz', 0.45, 0.0)
    GEST.extend([(KW(9, 'CONTROL'), 0.8, 'present'), (KW(9, 'TIEMBLA'), 0.9, 'laugh')])
    add_slap(T_V_SLAP)

def draw_V(cv, t, at=None):
    if t < Vv['in'] - 0.5 or t > T_V_SLAP + 1.0:
        return
    if t >= T_V_SLAP and at is None:
        shattered(cv, draw_V, T_V_SLAP, t, 9, y0=230, y1=1060)
        return
    st = throw_state(V_THROW[0], t)
    if st is None:
        return
    spinning = t >= Vv['girar']
    ang = 0.6 + (19.0 * (t - Vv['girar']) if spinning else 0.0)
    inside = S.ease_io(S.seg(t, Vv['open'], Vv['open'] + 0.35))
    img = M.gamepad(V_W, inside, ang if inside > 0.02 else 0.0)
    if st[0] == 'fly':
        S.paste_center(cv, M.gamepad(V_W), st[1], st[2], scale=st[4], angle=st[3])
        return
    dx = dy = 0.0
    if spinning:
        amp = 9 * S.seg(t, Vv['girar'], Vv['girar'] + 0.3)
        dx = amp * math.cos(ang); dy = -amp * math.sin(ang)
    sx = sy = None
    if st[0] == 'land':
        sx, sy = st[1], st[2]
    S.paste_center(cv, img, V_C[0] + dx, V_C[1] + dy, sx=sx, sy=sy)
    if spinning:
        for sgn in (-1, 1):
            x0 = V_C[0] + sgn * 330
            S.speed_lines(cv, x0, V_C[1] - 60, x0 + sgn * 70, V_C[1] - 90, n=3, color=(255, 230, 140, 170), width=5, seed=int(t * 20) + sgn)
    lbl(cv, 'EN MUCHOS CONTROLES', V_C[0], V_C[1] - 290, pop_in(t, Vv['muchos']), (255, 255, 255), 28)
    if t >= Vv['pesa']:
        gx = V_C[0] - V_W * 0.3 + dx; gy = V_C[1] + V_W * 0.62 * 0.12 + dy
        lbl(cv, 'PESA A UN LADO', gx + 40, gy + 205, pop_in(t, Vv['pesa']), (255, 230, 140), 28)
    if t >= Vv['tiembla']:
        S.paste_center(cv, burst('¡TIEMBLA!', 40), V_C[0] + 250, V_C[1] + 230, scale=S.ease_back(S.seg(t, Vv['tiembla'], Vv['tiembla'] + 0.2)), angle=0.1)

V_THROW = []


# ======================= escena G: el motor como generador (frase 10) =======================
Gg = {}
GM_C = (690, 1035)
LED_C = (960, 1080)
def setup_G():
    Gg['in'] = P(10) - 0.15
    Gg['crank'] = KW(10, 'giras') - 0.1
    Gg['volt'] = KW(10, 'VOLTAJE') - 0.1
    Gg['molino'] = KW(10, 'molino') - 0.2
    ev(Gg['in'], 'pop', 0.4, 0.3); ev(Gg['in'] + 0.12, 'pop', 0.35, 0.6)
    ev(Gg['crank'], 'roll', 0.3, 0.3, dur=T_G_SLAP - Gg['crank'])
    ev(Gg['volt'], 'zap', 0.4, 0.6); ev(Gg['volt'] + 0.02, 'chime', 0.3, 0.6)
    ev(Gg['molino'], 'pop', 0.4, -0.4)
    POINTS.append((Gg['crank'], T_G_SLAP - 0.25, 'l', lambda t: crank_handle(t)))
    add_slap(T_G_SLAP)

def crank_ang(t):
    if t < Gg['crank']:
        return 0.3
    u = t - Gg['crank']
    return 0.3 + 7.0 * (u - 0.3 * (1 - math.exp(-u / 0.3)))

CR_C = (GM_C[0], GM_C[1] - 175)
def crank_handle(t):
    a = crank_ang(t)
    r = 200 * 0.36
    return (CR_C[0] + r * math.cos(a), CR_C[1] - r * math.sin(a) * 0.45)

def draw_G(cv, t, at=None):
    if t < Gg['in'] or t > T_G_SLAP + 1.0:
        return
    if t >= T_G_SLAP and at is None:
        shattered(cv, draw_G, T_G_SLAP, t, 11, y0=230, y1=1150)
        return
    a = pop_in(t, Gg['in'], 0.35)
    t1, t2 = M.toy_motor_terms(*GM_C, MOT_W)
    l = D.L(W, 500); oy = 800
    for p0, col in ((t1, (60, 64, 72)), (t2, (220, 60, 60))):
        l.line([(p0[0], p0[1] - oy), (p0[0], 1146 - oy), (LED_C[0] + (-14 if p0 is t1 else 14), 1146 - oy), (LED_C[0] + (-14 if p0 is t1 else 14), LED_C[1] + 20 - oy)], col + (int(255 * a),), 6)
    cv.alpha_composite(l.done(), (0, oy))
    S.paste_center(cv, M.toy_motor(MOT_W), GM_C[0], GM_C[1], scale=a)
    ca = crank_ang(t)
    S.paste_center(cv, M.crank(ca, 200), CR_C[0], CR_C[1], scale=a, sy=0.45 * a)
    speed = 7.0 if t >= Gg['crank'] + 0.3 else 0.0
    on = S.seg(t, Gg['crank'] + 0.3, Gg['crank'] + 0.6) * (0.85 + 0.15 * math.sin(t * 30)) if t >= Gg['crank'] else 0.0
    if on > 0.02:
        S.glow_fast(cv, LED_C[0], LED_C[1] - 20, 130, (255, 80, 70), 0.8 * on)
    S.paste_center(cv, D.led_img(on), LED_C[0], LED_C[1], scale=a)
    lbl(cv, 'LED', LED_C[0], LED_C[1] - 120, a, (255, 170, 160), 24)
    lbl(cv, 'TÚ LO GIRAS', CR_C[0], CR_C[1] - 110, pop_in(t, Gg['crank']), (255, 230, 140), 26)
    if t >= Gg['volt']:
        S.paste_center(cv, burst('¡VOLTAJE!', 38), LED_C[0] - 60, LED_C[1] - 260, scale=S.ease_back(S.seg(t, Gg['volt'], Gg['volt'] + 0.2)), angle=0.08)
        lbl(cv, 'GIRADO A MANO = GENERADOR', 640, 330, pop_in(t, Gg['volt'] + 0.2), (150, 230, 255), 28)
    if t >= Gg['molino']:
        aa = pop_in(t, Gg['molino'])
        S.paste_center(cv, M.windmill(170, t * 3), 760, 470, scale=aa)
        lbl(cv, 'CAP. 2 · EL MOLINO', 760, 610, aa, (255, 210, 120), 28)


# ======================= escena F: remate (frase 11) =======================
Ff = {}
F_C = (640, 650)
def setup_F():
    Ff['in'] = P(11) + 0.2
    Ff['t1'] = KW(11, 'corriente') - 0.1
    Ff['t2'] = KW(11, 'CONMUTADOR') - 0.2
    ev(Ff['in'], 'pop', 0.45, 0.0); ev(Ff['t1'], 'pop', 0.4, 0.0); ev(Ff['t2'], 'chime', 0.35, 0.0)
    ev(Ff['in'], 'hum', 0.05, 0.0, dur=P(12) - Ff['in'], f=150)
    GEST.append((KW(11, 'motor'), 1.0, 'open'))
SPIN_F = Spin(lambda t: 3.2, P(11) - 0.5, P(12) + 0.5)

def draw_F(cv, t, at=None):
    if t < Ff['in'] or t > P(12) + 0.1:
        return
    a = pop_in(t, Ff['in'], 0.35) * (1 - S.ease_in(S.seg(t, P(12) - 0.25, P(12) + 0.1)))
    th = SPIN_F(t)
    S.glow_fast(cv, F_C[0], F_C[1], 300, (255, 190, 110), 0.22 * a)
    s = 1 if math.cos(th) >= 0 else -1
    S.paste_center(cv, M.motor_inside(th, cur=s, show_cur=1.0, push=1.0, field=1.0, t=t), F_C[0], F_C[1], scale=0.85 * a)
    if t >= Ff['t1']:
        aa = pop_in(t, Ff['t1'], 0.35) * a
        S.paste_center(cv, S.fancy_text('CORRIENTE + IMANES', 56), 620, 345, scale=aa)
    if t >= Ff['t2']:
        aa = pop_in(t, Ff['t2'], 0.35) * a
        S.paste_center(cv, S.fancy_text('+ UN CONMUTADOR', 54, top=(170, 225, 255), bot=(40, 120, 230), outline=(8, 24, 70)), 640, 925, scale=aa)


# ======================= cierre: botones y reto =======================
Fin = {}
BTN = {'like': (810, 620), 'sub': (810, 755), 'follow': (810, 890)}
Q_C = (330, 520)

def setup_Fin():
    Fin['btn_in'] = P(12) - 0.4
    Fin['hit'] = {'like': KW(12, 'me gusta'), 'sub': KW(12, 'suscríbete'), 'follow': KW(12, 'sígueme')}
    Fin['q'] = KW(12, 'Reto') - 0.1
    Fin['q2'] = KW(12, 'IMANES') - 0.1
    Fin['q3'] = KW(12, 'dónde') - 0.1
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
    GEST.append((KW(12, 'dónde'), 0.9, 'chin'))
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
        S.paste_center(cv, M.reto_card(400), x, Q_C[1], scale=kk)
        S.paste_center(cv, D.label('RETO', 30, fill=(255, 220, 120)), Q_C[0], Q_C[1] - 230,
                       scale=S.ease_back(S.seg(t, Fin['q'] + 0.2, Fin['q'] + 0.5)) * kk)
        if t >= Fin['q2']:
            a = S.ease_back(S.seg(t, Fin['q2'], Fin['q2'] + 0.3)) * kk
            S.paste_center(cv, D.label('PILA VOLTEADA + IMANES VOLTEADOS', 23, fill=(150, 220, 255)), Q_C[0] + 30, Q_C[1] + 225, scale=a)
        if t >= Fin['q3']:
            a = S.ease_back(S.seg(t, Fin['q3'], Fin['q3'] + 0.3)) * kk
            S.paste_center(cv, D.label('¿PARA DÓNDE GIRA? ↺ o ↻', 30, fill=(255, 255, 255)), Q_C[0] + 30, Q_C[1] + 282, scale=a)


def setup_all():
    setup_walks()
    setup_title()
    setup_H()
    setup_R()
    R_THROW.append(THROWS[-1])
    setup_C()
    C_THROW.append(THROWS[-1])
    setup_V()
    V_THROW.append(THROWS[-1])
    setup_G()
    setup_F()
    setup_Fin()
    react = [
        (T_PLUG + 0.06, 0.4, 50, None),                    # ¡arrancó!
        (Rr['push'] + 0.05, 0.4, 45, None),                # ¡empujón!
        (Cc['mismo'] + 0.1, 0.4, 45, 'thumbs'),
        (Gg['volt'] + 0.05, 0.4, 45, None),
        (KW(11, 'CONMUTADOR') + 0.1, 0.45, 65, 'up'),      # remate
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
    if T_PLUG <= t < T_PLUG + 1.6:
        sw += 0.07 * math.sin((t - T_PLUG) * 6) * math.exp(-(t - T_PLUG) * 2.0)   # el viento de la hélice mece la lámpara
    S.draw_lamp(cv, on=light, swing=sw)
    if light > 0.05:
        S.glow_fast(cv, S.LAMP_X + math.sin(sw) * S.LAMP_Y, math.cos(sw) * S.LAMP_Y + 22, 90, (255, 230, 150), 0.6 * light)
    if t >= T_TITLE_FLY + 0.4 and t < T_END_SNAP + 0.1:
        S.draw_label(cv, LABEL_TXT, alpha=S.seg(t, T_TITLE_FLY + 0.4, T_TITLE_FLY + 0.6) * light)
    # ----- escenas -----
    draw_H(cv, t)
    draw_R(cv, t)
    draw_C(cv, t)
    draw_V(cv, t)
    draw_G(cv, t)
    draw_F(cv, t)
    draw_title(cv, t)
    # ----- modo esquina (planos cercanos) -----
    ck = corner_k(t)
    xr = x + (150 - x) * ck
    scl = S.SCALE * (1 - 0.3 * ck)
    # ----- sombra -----
    if light > 0.05:
        h = S.FLOOR_Y - yf
        sh_w = 150 * max(0.4, 1 - h / 600) * (1 - 0.3 * ck)
        d = ImageDraw.Draw(cv, 'RGBA')
        d.ellipse([xr - sh_w, S.FLOOR_Y - 14, xr + sh_w, S.FLOOR_Y + 12], fill=(0, 0, 0, int(110 * light * max(0.3, 1 - h / 500))))
    # ----- personaje -----
    char_light = 0.32 + 0.68 * light if t < T_END_SNAP + 1.3 else 0.32
    CH.render(cv, pose, dict(scale=scl, ox=xr, oy=yf, view_yaw=0.12 * math.sin(t * 0.2)), light=char_light, t=t)
    draw_Fin(cv, t)
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
