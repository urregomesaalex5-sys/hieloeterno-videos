#!/usr/bin/env python3
# Capítulo 8: El inductor (la bobina). Vertical 1080x1920, 30 fps.
# Gancho en el segundo 0: laboratorio YA prendido, título arriba y un circuito real: pila AA de 1,5 V,
# interruptor de cuchilla y una bobina grande con un neón en paralelo. Él abre el interruptor de un tirón:
# chispa en el contacto y el neón destella naranja (demo U. Maryland K2-11).
# Regla: cada rótulo sale de VERIFICACION.md.
import math
import numpy as np
from PIL import Image, ImageDraw
import scene as S
import diagrams as D
import inductor as I
import lab as LB
import char3d as C
from timeline import TL, PHRASES

W, H = S.W, S.H
FPS = S.FPS
CH = C.Character()
HOME_X = 230
INTRO_X = 290
LABEL_TXT = 'CAP. 8 · EL INDUCTOR'

P = lambda i: TL.s(i)
E = lambda i: TL.e(i)
KW = TL.kw

# ======================= tiempos clave =======================
T_GRAB = 0.0                        # ya tiene la mano en el mango
T_OPEN = 0.45                       # abre el interruptor (¡chispa + neón!)
T_BONK = T_OPEN                     # (la música usa este nombre)
T_TITLE = T_OPEN                    # el groove arranca con el destello
T_TITLE_FLY = P(1) + 0.15
T_WALK_HOME = P(1) + 0.2
T_I_SLAP = P(2) - 0.1               # se rompe el circuito del gancho
T_B_SLAP = E(4) + 0.2               # se rompe la bobina con la brújula
T_L_SLAP = P(6) - 0.15              # se rompen los bombillos
T_N_SLAP = E(6) + 0.2               # se rompe el circuito del neón (repetición)
T_A_SLAP = E(7) + 0.2               # se rompe la analogía
T_P_SLAP = E(8) + 0.2               # se rompe el celular
T_Q_SLAP = E(9) + 0.2               # se rompe la carga inalámbrica
T_F_SLAP = E(10) + 0.2              # se rompe el remate
T_END_SNAP = E(12) + 0.6
T_END = TL.END

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


# ======================= expresiones =======================
EXPR = [
    (0.0, 'guino'), (T_OPEN - 0.05, 'sorpresa'), (KW(0, 'pila'), 'sorpresa'), (KW(0, 'DECENAS'), 'curioso'),
    (KW(0, 'Cómo'), 'pensando'), (KW(0, 'INDUCTOR'), 'feliz'),
    (P(1), 'guino'), (KW(1, 'SIN CABLE'), 'feliz'),
    (P(2), 'curioso'), (KW(2, 'BOBINA'), 'feliz'), (KW(2, 'CAMPO'), 'pensando'), (KW(2, 'brújula'), 'sorpresa'),
    (P(3), 'feliz'), (KW(3, 'GUARDA'), 'corazon'),
    (P(4), 'guino'), (KW(4, 'CAMBIE'), 'sorpresa'),
    (P(5), 'curioso'), (KW(5, 'EN CONTRA'), 'pensando'), (KW(5, 'retraso'), 'feliz'),
    (P(6), 'guino'), (KW(6, 'golpe'), 'sorpresa'), (KW(6, 'MUCHO'), 'curioso'), (KW(6, 'neón'), 'feliz'),
    (P(7), 'pensando'), (KW(7, 'arrancarla'), 'curioso'), (KW(7, 'frenarla'), 'sorpresa'), (E(7), 'feliz'),
    (P(8), 'curioso'), (KW(8, '1,6'), 'sorpresa'), (KW(8, 'CELULARES'), 'feliz'),
    (P(9), 'guino'), (KW(9, 'campo'), 'curioso'), (KW(9, 'induce'), 'sorpresa'), (KW(9, 'induce') + 0.8, 'corazon'),
    (P(10), 'feliz'), (KW(10, 'CAMBIOS'), 'guino'),
    (P(11), 'feliz'), (KW(11, 'Gracias'), 'corazon'),
    (P(12), 'feliz'), (KW(12, 'Reto'), 'guino'), (KW(12, 'duplica'), 'pensando'), (KW(12, 'Respóndeme'), 'feliz'),
    (T_END_SNAP + 0.3, 'feliz'), (T_END_SNAP + 0.75, 'apagado'),
]
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


# ======================= caminatas =======================
WALKS = []
def setup_walks():
    plan = [
        (T_WALK_HOME, HOME_X, 0.6),
        (P(6) - 0.1, 300, 0.6), (E(6) + 0.4, HOME_X, 0.6),
        (P(9) + 0.1, 290, 0.7), (P(10) + 0.1, HOME_X, 0.7),
        (KW(12, 'Reto') - 0.1, 290, 0.7),
    ]
    x = INTRO_X
    for t0, x1, d in plan:
        WALKS.append((t0, t0 + d, x, x1))
        n = max(2, int(abs(x1 - x) / 70))
        for k in range(n):
            ev(t0 + 0.12 + k * (d - 0.24) / max(1, n - 1), 'step', 0.4, panx(x + (x1 - x) * k / max(1, n - 1)), heavy=0.75)
        x = x1

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


def intro_pose(p, t, x, yf):
    # pícaro con la mano en el mango; con el destello se echa para atrás
    if t < T_OPEN:
        p.lean += 0.06
        p.head = (p.head[0] - 0.1, p.head[1] + 0.35, p.head[2])
        p.look = (1.0, -0.2)
    elif t < P(0) + 0.6:
        u = t - T_OPEN
        j = S.jelly(u, 3.0, 4.0)
        p.lean += -0.26 * math.exp(-u * 3) + 0.05 * math.sin(u * 8)
        p.sx *= 1 + 0.08 * j; p.sy *= 1 - 0.08 * j
        p.head = (p.head[0] - 0.1 + 0.08 * math.sin(u * 9), p.head[1] + 0.3 * math.exp(-u * 2), p.head[2])


def diagram_active(t):
    return (P(2) + 0.4 <= t < T_B_SLAP) or (P(5) + 0.3 <= t < T_L_SLAP) or (P(8) + 0.3 <= t < T_P_SLAP) \
        or (P(9) + 0.3 <= t < T_Q_SLAP)


GEST = []

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


def light_at(t):
    if t > T_END_SNAP + 0.05:
        return 0.0
    return 1.0


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
def title_imgs():
    if not _tc:
        _tc['a'] = S.fancy_text('¿CÓMO FUNCIONA UN', 64)
        _tc['b'] = S.fancy_text('INDUCTOR?', 100, top=(190, 240, 255), bot=(60, 150, 255), outline=(10, 30, 70))
    return _tc

def setup_title():
    ev(KW(0, 'INDUCTOR') - 0.05, 'block', 0.5, 0.0, pitch=1.1)
    ev(T_TITLE_FLY, 'whoosh', 0.4, 0.0)

def draw_title(cv, t):
    TI = title_imgs()
    if t < T_TITLE_FLY + 0.5:
        fly = S.ease_in(S.seg(t, T_TITLE_FLY, T_TITLE_FLY + 0.45))
        bump = 1 + 0.12 * S.jelly(t - KW(0, 'INDUCTOR'), 3, 5) if t >= KW(0, 'INDUCTOR') else 1.0
        ya = 268 + (S.ROOM_T + 46 - 268) * fly; yb = 345 + (S.ROOM_T + 46 - 345) * fly
        sc = 1 - 0.75 * fly
        S.paste_center(cv, TI['a'], 560, ya, scale=sc, alpha=1 - fly * 0.9)
        S.paste_center(cv, TI['b'], 560, yb, scale=sc * bump, alpha=1 - fly * 0.9)


# ======================= el circuito del neón (gancho y repetición) =======================
COIL_C = (650, 700); COIL_W, COIL_H = 380, 140
NEON_C = (650, 498); NEON_H = 180
SW_C = (612, 905); SW_W = 230
BAT_C = (995, 880); BAT_H = 190
_LE, _RE = I.coil_ends(COIL_C[0], COIL_C[1], COIL_W, COIL_H)
_post_c, _post_h = I.knife_posts(SW_W)
POST_C = (SW_C[0] + _post_c[0], SW_C[1] + _post_c[1])
POST_H = (SW_C[0] + _post_h[0], SW_C[1] + _post_h[1])
_cc = I.knife_contact(SW_W)
CONTACT = (SW_C[0] + _cc[0], SW_C[1] + _cc[1])
BAT_TOP = (BAT_C[0], BAT_C[1] - BAT_H / 2 - 4)
BAT_BOT = (BAT_C[0], BAT_C[1] + BAT_H / 2 + 6)
Y_LOW = 1010
NEON_LEADS = ((NEON_C[0] - 7, NEON_C[1] + NEON_H / 2 - 2), (NEON_C[0] + 7, NEON_C[1] + NEON_H / 2 - 2))
Y_NEON = NEON_C[1] + NEON_H / 2 + 14
LOOP_MAIN = [BAT_TOP, (BAT_TOP[0], _RE[1]), _RE, _LE, (_LE[0], Y_LOW), (POST_C[0], Y_LOW), POST_C,
             POST_H, (POST_H[0], Y_LOW), (BAT_BOT[0], Y_LOW), BAT_BOT]

def handle_pt(open_k):
    hx, hy = I.knife_handle(open_k, SW_W)
    return SW_C[0] + hx, SW_C[1] + hy

def draw_rig(cv, t, open_k, flow, field_k, neon_on, spark_u=None, alpha=1.0, labels=None):
    """circuito: pila AA → interruptor → bobina, con el neón en paralelo con la bobina"""
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    oy = 250
    l = D.L(W, 820)
    sh = lambda pts: [(x, y - oy) for x, y in pts]
    wire(l, sh([BAT_TOP, (BAT_TOP[0], _RE[1]), _RE]))
    wire(l, sh([_LE, (_LE[0], Y_LOW), (POST_C[0], Y_LOW), POST_C]))
    wire(l, sh([POST_H, (POST_H[0], Y_LOW), (BAT_BOT[0], Y_LOW), BAT_BOT]))
    # neón en paralelo con la bobina
    wire(l, sh([NEON_LEADS[0], (NEON_LEADS[0][0], Y_NEON), (_LE[0], Y_NEON), _LE]), w=5)
    wire(l, sh([NEON_LEADS[1], (NEON_LEADS[1][0], Y_NEON), (_RE[0], Y_NEON), _RE]), w=5)
    if flow > 0.01:
        curr_squares(l, LOOP_MAIN, t, 22, 0.16, flow, oy=oy, size=7)
    tmp.alpha_composite(l.done(), (0, oy))
    if field_k > 0.01:
        fl = I.field_lines(t, field_k, COIL_W, COIL_H * 0.62, n=3)
        if fl is not None:
            S.paste_center(tmp, fl, COIL_C[0], COIL_C[1], alpha=0.75)
    S.paste_center(tmp, I.coil(COIL_W, COIL_H, 14), COIL_C[0], COIL_C[1])
    if neon_on > 0.02:
        S.glow_fast(tmp, NEON_C[0], NEON_C[1] - 20, 150 + 60 * neon_on, (255, 120, 40), 0.85 * neon_on)
    S.paste_center(tmp, I.neon(round(min(1.0, neon_on), 2), NEON_H), NEON_C[0], NEON_C[1])
    S.paste_center(tmp, I.battery_aa(BAT_H), BAT_C[0], BAT_C[1])
    S.paste_center(tmp, I.knife_switch(round(open_k, 2), SW_W), SW_C[0], SW_C[1])
    if spark_u is not None and 0 <= spark_u < 0.45:
        k = 1 - spark_u / 0.45
        S.glow_fast(tmp, CONTACT[0], CONTACT[1] - 6, 120, (170, 210, 255), 0.95 * k)
        ll = D.L(240, 240)
        import random as _r
        rr = _r.Random(int(spark_u * 40))
        for j in range(7):
            a = rr.uniform(-math.pi, 0.2)
            pts = [(120, 120)]
            for s in range(4):
                r = 22 * (s + 1) * (0.6 + 0.6 * k)
                pts.append((120 + r * math.cos(a + rr.uniform(-0.4, 0.4)), 120 + r * math.sin(a + rr.uniform(-0.4, 0.4))))
            ll.line(pts, (220, 235, 255, int(255 * k)), 4)
        S.paste_center(tmp, ll.done(), CONTACT[0], CONTACT[1] - 10)
    if labels:
        for txt, x, y, a, col in labels:
            if a > 0:
                S.paste_center(tmp, D.label(txt, 24, fill=col), x, y, scale=a)
    cv.alpha_composite(tmp if alpha >= 0.999 else S.with_alpha(tmp, alpha))


# ---------- escena I: gancho ----------
Ii = {}
def setup_I():
    POINTS.append((T_GRAB, T_OPEN + 0.25, 'l', lambda t: handle_pt(open_at_I(t))))
    ev(T_OPEN, 'click', 0.7, panx(SW_C[0])); ev(T_OPEN, 'zap', 0.9, panx(CONTACT[0]))
    ev(T_OPEN + 0.02, 'pop', 0.55, panx(NEON_C[0]), f0=900, f1=2200)
    ev(0.0, 'hum', 0.10, panx(COIL_C[0]), dur=T_OPEN, f=100)
    SHAKES.append((T_OPEN, 0.22, 7))
    Ii['lbl_bat'] = KW(0, 'pila') - 0.05
    Ii['lbl_neon'] = KW(0, 'neón') - 0.05
    Ii['lbl_dec'] = KW(0, 'DECENAS') - 0.05
    for k in ('lbl_bat', 'lbl_neon'):
        ev(Ii[k], 'pop', 0.4, 0.3)
    Ii['promise'] = KW(1, 'SIN CABLE') - 0.2
    ev(Ii['promise'], 'chime', 0.3, 0.2)
    add_slap(T_I_SLAP)

def open_at_I(t):
    return S.ease_out(S.seg(t, T_OPEN - 0.04, T_OPEN + 0.1))

def neon_flash(t, t0):
    if t < t0:
        return 0.0
    u = t - t0
    return max(0.0, 1.25 * math.exp(-u * 4.5) - 0.02) if u < 1.2 else 0.0

def draw_I(cv, t, at=None):
    if t > T_I_SLAP + 1.0:
        return
    if t >= T_I_SLAP and at is None:
        shattered(cv, draw_I, T_I_SLAP, t, 3)
        return
    ok = open_at_I(t)
    flow = 1.0 if t < T_OPEN else 0.0
    field = 1.0 if t < T_OPEN else max(0.0, 1 - (t - T_OPEN) / 0.25)
    labels = []
    if t >= Ii['lbl_bat']:
        labels.append(('PILA 1,5 V', BAT_C[0] - 10, BAT_C[1] - 150, pop_in(t, Ii['lbl_bat']), (255, 230, 140)))
    if t >= Ii['lbl_neon']:
        labels.append(('NEÓN: HASTA ~90 V', NEON_C[0] + 210, NEON_C[1] - 30, pop_in(t, Ii['lbl_neon']), (255, 170, 110)))
    if t >= Ii['promise']:
        a = pop_in(t, Ii['promise'])
        labels.append(('AL FINAL: CARGA SIN CABLE', 560, 420, a * (1 - S.seg(t, T_I_SLAP - 0.3, T_I_SLAP)), (150, 230, 255)))
    draw_rig(cv, t, ok, flow, field, neon_flash(t, T_OPEN), spark_u=t - T_OPEN if t >= T_OPEN else None, labels=labels)


# ======================= escena B: qué es, campo, energía (frases 2–4) =======================
Bb = {}
B_C = (640, 640); B_W, B_H = 400, 150
B_BAT = (640, 905)
def setup_B():
    Bb['wire'] = KW(2, 'alambre') - 0.25
    Bb['coil'] = KW(2, 'BOBINA') - 0.1
    Bb['curr'] = KW(2, 'corriente') - 0.1
    Bb['field'] = KW(2, 'CAMPO') - 0.1
    Bb['comp'] = KW(2, 'brújula') - 0.45
    Bb['energy'] = KW(3, 'GUARDA') - 0.1
    Bb['oppose'] = KW(4, 'CAMBIE') - 0.1
    ev(Bb['wire'], 'whoosh', 0.4, 0.1)
    for k in range(6):
        ev(Bb['wire'] + 0.15 + k * 0.12, 'roll', 0.12, -0.3 + 0.12 * k, dur=0.2)
    ev(Bb['coil'], 'block', 0.5, 0.0, pitch=1.15)
    ev(Bb['curr'], 'click', 0.5, panx(B_BAT[0])); ev(Bb['curr'] + 0.05, 'hum', 0.10, 0.0, dur=T_B_SLAP - Bb['curr'], f=100)
    ev(Bb['field'], 'whine', 0.12, 0.0, dur=0.7, f0=300, f1=700)
    ev(Bb['comp'], 'pop', 0.4, panx(860)); ev(Bb['comp'] + 0.35, 'tink', 0.35, panx(860), f=2600)
    ev(Bb['energy'], 'chime', 0.35, 0.0)
    ev(Bb['oppose'], 'thud', 0.7, 0.1); ev(Bb['oppose'], 'block', 0.5, 0.1, pitch=0.7)
    SHAKES.append((Bb['oppose'], 0.2, 6))
    GEST.extend([(KW(2, 'BOBINA'), 0.9, 'present'), (KW(2, 'CAMPO'), 0.9, 'open'), (KW(3, 'GUARDA'), 0.8, 'present'),
                 (KW(4, 'raro'), 0.8, 'chin'), (KW(4, 'CAMBIE') - 0.1, 1.0, 'stop')])
    add_slap(T_B_SLAP)

B_LE, B_RE = I.coil_ends(B_C[0], B_C[1], B_W, B_H)
B_LOOP = [(B_BAT[0] + 105, B_BAT[1]), (B_RE[0], B_BAT[1]), B_RE, B_LE, (B_LE[0], B_BAT[1]), (B_BAT[0] - 105, B_BAT[1])]

def compass_angle(t):
    if t < Bb['comp'] + 0.35:
        return 0.0
    u = t - Bb['comp'] - 0.35
    # gira hacia el campo (encima de la bobina el campo va al revés que adentro)
    return -math.pi / 2 * (1 - math.exp(-u * 4) * math.cos(u * 14))

def draw_B(cv, t, at=None):
    if t < P(2) - 0.1 or t > T_B_SLAP + 1.0:
        return
    if t >= T_B_SLAP and at is None:
        shattered(cv, draw_B, T_B_SLAP, t, 5)
        return
    # el alambre recto vuela y se enrolla
    if t < Bb['coil'] + 0.25:
        if t >= Bb['wire']:
            k = S.ease_io(S.seg(t, Bb['wire'] + 0.2, Bb['coil']))
            a_in = S.seg(t, Bb['wire'], Bb['wire'] + 0.2)
            a_out = 1 - S.seg(t, Bb['coil'], Bb['coil'] + 0.25)
            S.paste_center(cv, I.winding(k, B_W, B_H), B_C[0] - 200 * (1 - a_in), B_C[1], alpha=a_in * a_out)
    on = t >= Bb['curr']
    if t >= Bb['coil']:
        l = D.L(W, 720)
        oy = 250
        sh = lambda pts: [(x, y - oy) for x, y in pts]
        if t >= Bb['curr'] - 0.3:
            a = S.seg(t, Bb['curr'] - 0.3, Bb['curr'])
            wire(l, sh([(B_BAT[0] + 105, B_BAT[1]), (B_RE[0], B_BAT[1]), B_RE]), col=(232, 232, 232))
            wire(l, sh([B_LE, (B_LE[0], B_BAT[1]), (B_BAT[0] - 105, B_BAT[1])]), col=(232, 232, 232))
            if on:
                curr_squares(l, B_LOOP, t, 16, 0.14, S.seg(t, Bb['curr'], Bb['curr'] + 0.3), oy=oy, size=7)
        cv.alpha_composite(l.done(), (0, oy))
        # campo magnético
        if t >= Bb['field']:
            fk = S.ease_out(S.seg(t, Bb['field'], Bb['field'] + 0.8))
            boost = 0.0
            if t >= Bb['energy']:
                boost = 0.5 + 0.5 * math.sin((t - Bb['energy']) * 6)
            fl = I.field_lines(t, fk, B_W, 95, n=4, col=(90 + int(100 * boost), 200 + int(40 * boost), 255))
            if fl is not None:
                S.paste_center(cv, fl, B_C[0], B_C[1])
            if t >= Bb['energy']:
                S.glow_fast(cv, B_C[0], B_C[1], 330, (80, 170, 255), 0.25 + 0.12 * boost)
        k = S.ease_back(S.seg(t, Bb['coil'], Bb['coil'] + 0.3))
        sq = 1 + 0.1 * S.jelly(t - Bb['oppose'], 4, 5) if t >= Bb['oppose'] else 1.0
        S.paste_center(cv, I.coil(B_W, B_H, 15), B_C[0], B_C[1], scale=k, sx=sq, sy=2 - sq)
        if t >= Bb['curr'] - 0.3:
            S.paste_center(cv, I.battery_aa(170), B_BAT[0], B_BAT[1], angle=-math.pi / 2,
                           alpha=S.seg(t, Bb['curr'] - 0.3, Bb['curr']))
        if t >= Bb['coil']:
            S.paste_center(cv, D.label('BOBINA', 26, fill=(255, 200, 140)), B_C[0], B_C[1] + 128, scale=pop_in(t, Bb['coil'] + 0.1))
    if t >= Bb['field'] + 0.2:
        S.paste_center(cv, D.label('CAMPO MAGNÉTICO', 24, fill=(150, 225, 255)), 905, 870, scale=pop_in(t, Bb['field'] + 0.2))
    if t >= Bb['comp']:
        u = S.seg(t, Bb['comp'], Bb['comp'] + 0.35)
        y = 380 - 300 * (1 - S.bounce_out(u))
        S.paste_center(cv, I.compass(round(compass_angle(t), 2), 150), 920, y)
    if t >= Bb['energy']:
        a = pop_in(t, Bb['energy'], 0.35)
        S.paste_center(cv, S.fancy_text('GUARDA ENERGÍA', 52, top=(190, 240, 255), bot=(60, 150, 255), outline=(10, 30, 70)),
                       560, 300, scale=a * (1 - S.seg(t, Bb['oppose'] - 0.2, Bb['oppose'])))
        S.paste_center(cv, D.label('U = ½ · L · I²', 26, fill=(220, 235, 255)), 560, 372,
                       scale=a * (1 - S.seg(t, Bb['oppose'] - 0.2, Bb['oppose'])))
    if t >= Bb['oppose']:
        u = S.seg(t, Bb['oppose'], Bb['oppose'] + 0.15)
        sc = 2.2 - 1.2 * S.ease_in(u)
        stp = stamp_img('SE OPONE AL CAMBIO', 44)
        S.paste_center(cv, stp, 640, 330, scale=sc, angle=-0.1, alpha=min(1, u * 2))


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


# ======================= escena L: dos bombillos (frase 5) =======================
Ll = {}
LBX, RBX = 330, 760
ROW_T = 480
LC_C = (470, 690); LC_W, LC_H = 200, 80
_lle, _lre = I.coil_ends(LC_C[0], LC_C[1], LC_W, LC_H)
ROW_B = _lle[1]
BULB_H = 150
BULB_A = (560, ROW_T - BULB_H / 2 + 10)
BULB_B = (680, ROW_B - BULB_H / 2 + 10)
LSW_C = (450, 873); ROW_P = LSW_C[1] + I.knife_contact(SW_W)[1]
LBAT_C = (672, ROW_P)
GRAPH_C = (880, 345)

def l_open_k(t):
    # empieza abierto; lo cierra en "sube"
    return 1 - S.ease_out(S.seg(t, Ll['close'] - 0.08, Ll['close'] + 0.08))

def l_handle(t):
    hx, hy = I.knife_handle(l_open_k(t), SW_W)
    return LSW_C[0] + hx, LSW_C[1] + hy

def bulbB_level(t):
    if t < Ll['close']:
        return 0.0
    u = t - Ll['close']
    return 1 - math.exp(-u * 1.6)

def setup_L():
    Ll['in'] = P(5) - 0.15
    Ll['close'] = KW(5, 'sube') - 0.05
    Ll['contra'] = KW(5, 'EN CONTRA') - 0.15
    Ll['delay'] = KW(5, 'retraso') - 0.1
    ev(Ll['in'], 'block', 0.5, 0.0, pitch=1.05); ev(Ll['in'] + 0.12, 'block', 0.45, 0.3, pitch=0.9)
    POINTS.append((Ll['close'] - 0.35, Ll['close'] + 0.25, 'l', l_handle))
    ev(Ll['close'], 'click', 0.7, panx(LSW_C[0])); ev(Ll['close'] + 0.02, 'switch', 0.4, panx(LSW_C[0]))
    ev(Ll['close'] + 0.03, 'zap', 0.25, panx(BULB_A[0]))
    ev(Ll['close'] + 0.05, 'whine', 0.12, panx(BULB_B[0]), dur=1.6, f0=200, f1=500)
    ev(Ll['contra'], 'thud', 0.5, panx(LC_C[0]))
    ev(Ll['delay'], 'chime', 0.3, panx(BULB_B[0]))
    GEST.extend([(KW(5, 'EN CONTRA'), 0.9, 'stop'), (KW(5, 'retraso'), 0.9, 'present')])
    add_slap(T_L_SLAP)

def draw_L(cv, t, at=None):
    if t < Ll['in'] or t > T_L_SLAP + 1.0:
        return
    if t >= T_L_SLAP and at is None:
        shattered(cv, draw_L, T_L_SLAP, t, 7)
        return
    k = pop_in(t, Ll['in'], 0.35)
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    l = D.L(W, 720); oy = 250
    sh = lambda pts: [(x, y - oy) for x, y in pts]
    wire(l, sh([(LBX, ROW_T), (RBX, ROW_T)]))
    wire(l, sh([(LBX, ROW_B), _lle])); wire(l, sh([_lre, (RBX, ROW_B)]))
    wire(l, sh([(LBX, ROW_T), (LBX, ROW_P), (LSW_C[0] + I.knife_contact(SW_W)[0], ROW_P)]))
    wire(l, sh([(LSW_C[0] + I.knife_posts(SW_W)[1][0], ROW_P), (RBX, ROW_P), (RBX, ROW_T)]))
    on = t >= Ll['close']
    if on:
        a = S.seg(t, Ll['close'], Ll['close'] + 0.15)
        top = [(LBX, ROW_P), (LBX, ROW_T), (RBX, ROW_T), (RBX, ROW_P)]
        curr_squares(l, top, t, 12, 0.22, a, oy=oy, size=6)
        bot = [(LBX, ROW_P), (LBX, ROW_B), (RBX, ROW_B), (RBX, ROW_P)]
        curr_squares(l, bot, t, 12, 0.22, a * bulbB_level(t), oy=oy, size=6)
    tmp.alpha_composite(l.done(), (0, oy))
    S.paste_center(tmp, I.coil(LC_W, LC_H, 10), LC_C[0], LC_C[1])
    la = 1.0 if on else 0.0
    lb = bulbB_level(t)
    if la > 0:
        S.glow_fast(tmp, BULB_A[0], BULB_A[1] - 30, 190, (255, 210, 110), 1.0 * la)
    if lb > 0.05:
        S.glow_fast(tmp, BULB_B[0], BULB_B[1] - 30, 190, (255, 210, 110), 1.0 * lb)
    S.paste_center(tmp, I.bulb(round(la, 1), BULB_H), BULB_A[0], BULB_A[1])
    S.paste_center(tmp, I.bulb(round(lb, 1), BULB_H), BULB_B[0], BULB_B[1])
    S.paste_center(tmp, I.knife_switch(round(l_open_k(t), 2), SW_W), LSW_C[0], LSW_C[1])
    S.paste_center(tmp, I.battery_aa(150), LBAT_C[0], LBAT_C[1], angle=-math.pi / 2)
    S.paste_center(tmp, D.label('SIN BOBINA', 22, fill=(220, 225, 235)), BULB_A[0] - 130, ROW_T - 60)
    S.paste_center(tmp, D.label('CON BOBINA', 22, fill=(255, 190, 120)), LC_C[0], ROW_B + 52)
    # gráfica corriente vs tiempo
    gk = S.seg(t, Ll['close'] - 0.25, Ll['close'] + 1.8)
    S.paste_center(tmp, I.graph_rise(gk, 330, 200), GRAPH_C[0], GRAPH_C[1])
    if t >= Ll['close'] + 0.6:
        S.paste_center(tmp, D.label('sin bobina', 18, fill=(190, 196, 210)), GRAPH_C[0] + 60, GRAPH_C[1] - 112)
        S.paste_center(tmp, D.label('con bobina', 18, fill=(255, 170, 80)), GRAPH_C[0] + 70, GRAPH_C[1] + 125,
                       scale=pop_in(t, Ll['close'] + 0.6))
    # voltaje en contra
    if t >= Ll['contra']:
        a = pop_in(t, Ll['contra'])
        ll = D.L(320, 70)
        D.arrow(ll, (300, 35), (30, 35), (255, 80, 80, 255), 10, 26)
        S.paste_center(tmp, ll.done(), LC_C[0], LC_C[1] - 75, scale=a * (1 + 0.06 * math.sin(t * 9)))
        S.paste_center(tmp, D.label('VOLTAJE INDUCIDO (EN CONTRA)', 22, fill=(255, 140, 140)), LC_C[0] + 40, LC_C[1] - 128, scale=a)
    if t >= Ll['delay']:
        a = pop_in(t, Ll['delay'])
        S.paste_center(tmp, D.label('PRENDE CON RETRASO', 24, fill=(255, 220, 120)), BULB_B[0] + 120, BULB_B[1] - 110, scale=a)
    cv.alpha_composite(S.with_alpha(tmp, min(1.0, k)) if k < 0.999 else tmp)


# ======================= escena N: repetición del neón (frase 6) =======================
Nn = {}
def setup_N():
    Nn['in'] = P(6) - 0.05
    Nn['open'] = KW(6, 'golpe') - 0.05
    Nn['fall'] = KW(6, 'cae') - 0.1
    Nn['bars'] = KW(6, 'MUCHO') - 0.1
    Nn['eso'] = KW(6, 'neón') - 0.25
    ev(Nn['in'], 'block', 0.5, 0.0, pitch=1.1); ev(Nn['in'] + 0.1, 'hum', 0.10, panx(COIL_C[0]), dur=Nn['open'] - Nn['in'], f=100)
    POINTS.append((Nn['open'] - 0.4, Nn['open'] + 0.3, 'l', lambda t: handle_pt(n_open(t))))
    ev(Nn['open'], 'click', 0.7, panx(SW_C[0])); ev(Nn['open'], 'zap', 0.9, panx(CONTACT[0]))
    ev(Nn['open'] + 0.02, 'pop', 0.5, panx(NEON_C[0]), f0=900, f1=2200)
    SHAKES.append((Nn['open'], 0.2, 6))
    ev(Nn['bars'], 'whine', 0.15, 0.3, dur=0.5, f0=400, f1=2400)
    ev(Nn['eso'], 'chime', 0.35, panx(NEON_C[0]))
    GEST.extend([(KW(6, 'MUCHO'), 0.9, 'open'), (KW(6, 'neón'), 0.8, 'present')])
    add_slap(T_N_SLAP)

def n_open(t):
    return S.ease_out(S.seg(t, Nn['open'] - 0.04, Nn['open'] + 0.1))

def volt_bars(k_bat, k_peak):
    l = D.L(300, 330)
    l.rrect([4, 4, 296, 326], 16, fill=(18, 20, 26, 225), outline=(200, 205, 215, 255), width=3)
    y1 = 250
    hb = 14 * k_bat
    hp = 200 * k_peak
    l.rect([45, y1 - hb, 125, y1], fill=(255, 210, 80, 255))
    l.rect([175, y1 - hp, 255, y1], fill=(255, 110, 50, 255))
    l.line([(30, y1), (270, y1)], (200, 205, 215, 255), 3)
    l.text((85, 280), 'PILA', 20, fill=(255, 230, 140)); l.text((85, 304), '1,5 V', 20, fill=(255, 230, 140))
    l.text((215, 280), 'PICO', 20, fill=(255, 170, 110)); l.text((215, 304), 'DECENAS V', 18, fill=(255, 170, 110))
    return l.done()

def draw_N(cv, t, at=None):
    if t < Nn['in'] or t > T_N_SLAP + 1.0:
        return
    if t >= T_N_SLAP and at is None:
        shattered(cv, draw_N, T_N_SLAP, t, 9)
        return
    k = pop_in(t, Nn['in'], 0.35)
    ok = n_open(t)
    closed = t < Nn['open']
    flow = S.seg(t, Nn['in'] + 0.2, Nn['in'] + 0.5) if closed else 0.0
    if closed:
        field = S.seg(t, Nn['in'] + 0.2, Nn['in'] + 0.9)
    else:
        # el campo "se cae": se encoge rápido
        field = max(0.0, 1 - (t - Nn['open']) / 0.35)
    labels = [('PILA 1,5 V', BAT_C[0] - 10, BAT_C[1] - 150, 1.0, (255, 230, 140))]
    if not closed and field > 0:
        labels.append(('EL CAMPO SE CAE', COIL_C[0], COIL_C[1] - 120, 1.0, (150, 225, 255)))
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_rig(tmp, t, ok, flow, field, neon_flash(t, Nn['open']), spark_u=(t - Nn['open']) if not closed else None, labels=labels)
    if t >= Nn['bars']:
        a = pop_in(t, Nn['bars'])
        S.paste_center(tmp, volt_bars(1.0, S.ease_out(S.seg(t, Nn['bars'], Nn['bars'] + 0.5))), 880, 420, scale=0.9 * a)
    if t >= Nn['eso']:
        a = pop_in(t, Nn['eso'])
        ring = D.L(220, 260)
        ring.circle((110, 130), 100, outline=(255, 200, 80, 255), width=8)
        S.paste_center(tmp, ring.done(), NEON_C[0], NEON_C[1] - 10, scale=a * (1 + 0.05 * math.sin(t * 8)))
        S.paste_center(tmp, D.label('¡POR ESO PRENDIÓ!', 24, fill=(255, 200, 120)), NEON_C[0] - 210, NEON_C[1] - 60, scale=a)
    S.paste_center(cv, tmp, W / 2, H / 2, scale=1.0, alpha=min(1.0, k * 1.2))


# ======================= escena A: analogía de la inercia (frase 7) =======================
Aa = {}
RAIL_Y = 760
CART_X0, CART_X1 = 470, 880
def setup_A():
    Aa['in'] = P(7) - 0.05
    Aa['go'] = KW(7, 'arrancarla') - 0.15
    Aa['brake'] = KW(7, 'frenarla') - 0.15
    Aa['stop'] = E(7) + 0.15
    ev(Aa['in'], 'block', 0.5, 0.2, pitch=0.8)
    POINTS.append((Aa['go'] - 0.1, Aa['go'] + 0.6, 'l', lambda t: (cart_x(t) - 140, RAIL_Y - 60)))
    ev(Aa['go'], 'roll', 0.3, panx(CART_X0), dur=Aa['brake'] - Aa['go'])
    ev(Aa['brake'], 'roll', 0.25, panx(CART_X1), dur=Aa['stop'] - Aa['brake'])
    ev(Aa['brake'] + 0.05, 'whine', 0.08, panx(CART_X1), dur=0.8, f0=1800, f1=1500)
    GEST.extend([(KW(7, 'INERCIA'), 0.9, 'present'), (KW(7, 'frenarla'), 1.0, 'stop')])
    add_slap(T_A_SLAP)

def cart_x(t):
    """arranca despacio (acelera de a poco) y frena despacio"""
    a, b, c = Aa['go'], Aa['brake'], Aa['stop']
    if t <= a:
        return CART_X0
    vmax = None
    T1 = b - a; T2 = max(0.3, c - b)
    # aceleración constante hasta b, luego desaceleración constante hasta c
    d_total = CART_X1 - CART_X0
    vm = 2 * d_total / (T1 + T2)
    if t <= b:
        return CART_X0 + 0.5 * (vm / T1) * (t - a) ** 2
    if t <= c:
        u = t - b
        return CART_X0 + 0.5 * vm * T1 + vm * u - 0.5 * (vm / T2) * u ** 2
    return CART_X1

def draw_A(cv, t, at=None):
    if t < Aa['in'] or t > T_A_SLAP + 1.0:
        return
    if t >= T_A_SLAP and at is None:
        shattered(cv, draw_A, T_A_SLAP, t, 11)
        return
    k = pop_in(t, Aa['in'], 0.35)
    S.paste_center(cv, S.fancy_text('ANALOGÍA', 60), 640, 310, scale=k)
    S.paste_center(cv, D.label('inductancia ↔ masa  ·  corriente ↔ velocidad', 22, fill=(220, 225, 235)), 640, 380, scale=k)
    S.paste_center(cv, I.rails(760), 680, RAIL_Y + 52, scale=k)
    x = cart_x(t)
    wob = 0.0
    if t >= Aa['brake']:
        wob = 0.03 * math.sin((t - Aa['brake']) * 9) * math.exp(-(t - Aa['brake']) * 1.5)
    S.paste_center(cv, I.cart(300), x, RAIL_Y - 30, scale=k, angle=wob)
    if Aa['go'] <= t < Aa['stop']:
        sp = (cart_x(t + 0.03) - cart_x(t)) / 0.03
        if sp > 150:
            S.speed_lines(cv, x - 170, RAIL_Y - 60, x - 170 - sp * 0.25, RAIL_Y - 60, n=3, color=(255, 255, 255, 110), width=4, seed=3)
    if t >= Aa['go'] + 0.1:
        S.paste_center(cv, D.label('CUESTA ARRANCAR', 26, fill=(255, 220, 120)), 520, 480, scale=pop_in(t, Aa['go'] + 0.1))
    if t >= Aa['brake'] + 0.1:
        S.paste_center(cv, D.label('CUESTA FRENAR', 26, fill=(255, 150, 120)), 820, 540, scale=pop_in(t, Aa['brake'] + 0.1))


# ======================= escena P: inductores de chip (frase 8) =======================
Pc = {}
PCB_C = (620, 600)
MAG_C = (800, 480)
def setup_P():
    Pc['in'] = P(8) - 0.05
    Pc['mag'] = KW(8, '1,6') - 0.3
    Pc['cut'] = Pc['mag'] + 0.45
    Pc['cel'] = KW(8, 'CELULARES') - 0.1
    ev(Pc['in'], 'block', 0.5, 0.2, pitch=1.1); ev(Pc['in'] + 0.2, 'zap', 0.25, 0.2)
    ev(Pc['mag'], 'whoosh', 0.4, 0.4); ev(Pc['mag'] + 0.3, 'tink', 0.35, 0.4, f=3000)
    ev(Pc['cut'], 'pop', 0.35, 0.4)
    ev(Pc['cel'], 'pop', 0.4, 0.2)
    GEST.extend([(KW(8, '1,6'), 0.9, 'present'), (KW(8, 'CELULARES'), 0.8, 'open')])
    add_slap(T_P_SLAP)

_mag = {}
def mag_content(cut):
    key = round(cut, 1)
    if key not in _mag:
        l = D.L(380, 380)
        l.rect([0, 0, 380, 380], fill=(18, 92, 58, 255))
        l.line([(0, 190), (380, 190)], (196, 132, 58, 255), 26)
        l.rect([40, 140, 100, 240], fill=(232, 192, 70, 255)); l.rect([280, 140, 340, 240], fill=(232, 192, 70, 255))
        c = l.done()
        S.paste_center(c, I.smd_inductor(250, cut), 190, 190)
        _mag[key] = c
    return _mag[key]

def draw_P(cv, t, at=None):
    if t < Pc['in'] or t > T_P_SLAP + 1.0:
        return
    if t >= T_P_SLAP and at is None:
        shattered(cv, draw_P, T_P_SLAP, t, 13)
        return
    k = pop_in(t, Pc['in'], 0.35)
    S.paste_center(cv, I.pcb_panel_L(), PCB_C[0], PCB_C[1], scale=0.85 * k)
    l = D.L(W, 720)
    for j in range(3):
        x = PCB_C[0] - 240 + ((t * 260 + j * 170) % 480)
        y = PCB_C[1] - 120 + j * 110
        l.rect([x - 10, y - 250 - 3, x + 10, y - 250 + 3], fill=(120, 240, 255, int(170 * k)))
    cv.alpha_composite(l.done(), (0, 250))
    if t >= Pc['mag']:
        u = S.ease_back(S.seg(t, Pc['mag'], Pc['mag'] + 0.4))
        cut = S.seg(t, Pc['cut'], Pc['cut'] + 0.4)
        x = MAG_C[0] + 200 * (1 - u); y = MAG_C[1] + 160 * (1 - u)
        S.paste_center(cv, D.magnifier(mag_content(cut), r=150), x, y, scale=u)
        if cut > 0.5:
            S.paste_center(cv, D.label('por dentro: alambre enrollado', 20, fill=(255, 200, 150)), MAG_C[0] - 20, MAG_C[1] + 178,
                           alpha=S.seg(t, Pc['cut'] + 0.2, Pc['cut'] + 0.5))
        S.paste_center(cv, D.label('EXISTEN DE 1,6 × 0,8 mm', 28, fill=(255, 230, 140)), PCB_C[0], 870, scale=pop_in(t, Pc['mag'] + 0.3))
    if t >= Pc['cel']:
        S.paste_center(cv, D.label('INDUCTORES DE POTENCIA PARA CELULARES', 24, fill=(170, 255, 200)), PCB_C[0], 300, scale=pop_in(t, Pc['cel']))


# ======================= escena Q: carga inalámbrica (frase 9) =======================
Qq = {}
QI_C = (650, 610)
def setup_Q():
    Qq['in'] = P(9) - 0.05
    Qq['base'] = KW(9, 'base') - 0.15
    Qq['field'] = KW(9, 'campo') - 0.1
    Qq['phone'] = KW(9, 'induce') - 0.35
    Qq['charge'] = KW(9, 'induce') + 0.1
    ev(Qq['in'], 'block', 0.5, 0.2, pitch=0.9)
    ev(Qq['base'], 'click', 0.5, panx(QI_C[0])); ev(Qq['field'], 'hum', 0.10, 0.0, dur=T_Q_SLAP - Qq['field'], f=120)
    ev(Qq['phone'], 'whoosh', 0.35, 0.2); ev(Qq['phone'] + 0.35, 'block', 0.45, 0.2, pitch=1.3)
    ev(Qq['charge'], 'chime', 0.4, 0.2)
    GEST.extend([(KW(9, 'base'), 0.8, 'present'), (KW(9, 'induce'), 1.0, 'open')])
    add_slap(T_Q_SLAP)

def draw_Q(cv, t, at=None):
    if t < Qq['in'] or t > T_Q_SLAP + 1.0:
        return
    if t >= T_Q_SLAP and at is None:
        shattered(cv, draw_Q, T_Q_SLAP, t, 15)
        return
    k = pop_in(t, Qq['in'], 0.35)
    on = S.seg(t, Qq['field'], Qq['field'] + 0.4)
    kp = S.bounce_out(S.seg(t, Qq['phone'], Qq['phone'] + 0.45)) if t >= Qq['phone'] else 0.0
    ch = 0.15 + 0.65 * S.seg(t, Qq['charge'], T_Q_SLAP - 0.2) if t >= Qq['charge'] else 0.15
    S.paste_center(cv, I.qi_scene(t, on, kp, ch), QI_C[0], QI_C[1], scale=k)
    if t >= Qq['base']:
        S.paste_center(cv, D.label('BOBINA DE LA BASE', 24, fill=(255, 200, 140)), QI_C[0], QI_C[1] + 285, scale=pop_in(t, Qq['base']))
    if t >= Qq['field'] + 0.2:
        S.paste_center(cv, D.label('CAMPO QUE CAMBIA', 22, fill=(150, 225, 255)), QI_C[0] + 250, QI_C[1] - 30,
                       scale=pop_in(t, Qq['field'] + 0.2))
    if t >= Qq['charge']:
        a = pop_in(t, Qq['charge'])
        S.paste_center(cv, D.label('BOBINA DEL CELULAR', 24, fill=(255, 220, 140)), QI_C[0], 400, scale=a)
        S.paste_center(cv, D.label('(si tiene carga inalámbrica)', 18, fill=(200, 205, 215)), QI_C[0], 442, scale=a)


# ======================= escena F: remate (frase 10) =======================
Fn = {}
F_C = (640, 620)
def setup_F():
    Fn['in'] = P(10) - 0.05
    Fn['energy'] = KW(10, 'energía') - 0.1
    Fn['change'] = KW(10, 'CAMBIOS') - 0.1
    ev(Fn['in'], 'block', 0.5, 0.0, pitch=1.15)
    ev(Fn['energy'], 'chime', 0.3, 0.0); ev(Fn['change'], 'thud', 0.5, 0.0)
    GEST.extend([(KW(10, 'energía'), 0.9, 'present'), (KW(10, 'CAMBIOS'), 0.9, 'stop')])
    add_slap(T_F_SLAP)

def draw_F(cv, t, at=None):
    if t < Fn['in'] or t > T_F_SLAP + 1.0:
        return
    if t >= T_F_SLAP and at is None:
        shattered(cv, draw_F, T_F_SLAP, t, 17)
        return
    k = pop_in(t, Fn['in'], 0.35)
    fl = I.field_lines(t, S.seg(t, Fn['in'] + 0.1, Fn['in'] + 0.8), B_W, 95, n=4)
    if fl is not None:
        S.paste_center(cv, fl, F_C[0], F_C[1])
    S.paste_center(cv, I.coil(B_W, B_H, 15), F_C[0], F_C[1], scale=k)
    if t >= Fn['energy']:
        S.paste_center(cv, D.label('GUARDA ENERGÍA EN SU CAMPO', 26, fill=(150, 225, 255)), F_C[0], 320, scale=pop_in(t, Fn['energy']))
    if t >= Fn['change']:
        u = S.seg(t, Fn['change'], Fn['change'] + 0.15)
        S.paste_center(cv, stamp_img('SE OPONE A LOS CAMBIOS', 34), 690, 890, scale=2.2 - 1.2 * S.ease_in(u), angle=-0.06, alpha=min(1, u * 2))


# ======================= crédito (frase 11) =======================
Cr = {}
def setup_Cr():
    Cr['in'] = P(11) - 0.05
    Cr['heart'] = KW(11, 'Gracias') - 0.1
    ev(Cr['in'], 'pop', 0.45, 0.2); ev(Cr['heart'], 'chime', 0.35, 0.2)
    GEST.append((KW(11, 'Gracias'), 1.0, 'chest'))

def draw_Cr(cv, t):
    if t < Cr['in'] or t > P(12) + 0.1:
        return
    a = pop_in(t, Cr['in'], 0.35) * (1 - S.ease_in(S.seg(t, P(12) - 0.25, P(12) + 0.1)))
    heart = S.seg(t, Cr['heart'], Cr['heart'] + 0.3)
    S.paste_center(cv, D.comment_bubble('Inductores :D', user='@vpalep · Instagram', width=560, heart=heart, t=t), 620, 520, scale=1.25 * a)
    S.paste_center(cv, D.label('¡TU IDEA SE VOLVIÓ CAPÍTULO!', 26, fill=(255, 220, 120)), 620, 730, scale=a * pop_in(t, Cr['heart']))


# ======================= cierre: botones y reto =======================
Fin = {}
BTN = {'like': (810, 620), 'sub': (810, 755), 'follow': (810, 890)}
Q_C = (325, 540)

def setup_Fin():
    Fin['btn_in'] = P(12) - 0.4
    Fin['hit'] = {'like': KW(12, 'me gusta'), 'sub': KW(12, 'suscríbete'), 'follow': KW(12, 'sígueme')}
    Fin['q'] = KW(12, 'Reto') - 0.1
    Fin['q2'] = KW(12, 'duplica') - 0.1
    Fin['q3'] = KW(12, 'Respóndeme') - 0.1
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
    GEST.append((KW(12, 'duplica'), 0.9, 'chin'))
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
        S.paste_center(cv, I.reto_pair(), x, Q_C[1], scale=0.85 * kk)
        S.paste_center(cv, D.label('RETO · mismo tamaño', 26, fill=(255, 220, 120)), Q_C[0], Q_C[1] - 185,
                       scale=S.ease_back(S.seg(t, Fin['q'] + 0.2, Fin['q'] + 0.5)) * kk)
        if t >= Fin['q3']:
            a = S.ease_back(S.seg(t, Fin['q3'], Fin['q3'] + 0.3)) * kk
            S.paste_center(cv, D.label('RESPÓNDEME', 26, fill=(255, 255, 255)), Q_C[0], Q_C[1] + 175, scale=a)
            S.paste_center(cv, D.label('EN LOS COMENTARIOS', 22, fill=(255, 255, 255)), Q_C[0], Q_C[1] + 222, scale=a)


def setup_all():
    setup_walks()
    setup_title()
    setup_I()
    setup_B()
    setup_L()
    setup_N()
    setup_A()
    setup_P()
    setup_Q()
    setup_F()
    setup_Cr()
    setup_Fin()
    react = [
        (T_OPEN + 0.02, 0.4, 55, None),                    # ¡destello!
        (Bb['coil'] + 0.05, 0.4, 45, None),                # ¡bobina!
        (Bb['comp'] + 0.4, 0.4, 50, None),                 # la brújula gira
        (Ll['close'] + 0.9, 0.45, 55, 'thumbs'),           # prende el segundo bombillo
        (Nn['open'] + 0.02, 0.4, 55, None),                # ¡chispa!
        (Nn['eso'] + 0.1, 0.45, 70, 'up'),                 # ¡eso prendió el neón!
        (Qq['charge'] + 0.05, 0.45, 70, 'up'),             # ¡carga!
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
    for t0 in (T_OPEN, Nn['open']):
        if t0 <= t < t0 + 1.4:
            sw += 0.05 * math.sin((t - t0) * 7) * math.exp(-(t - t0) * 2.5)
    S.draw_lamp(cv, on=light, swing=sw)
    if light > 0.05:
        S.glow_fast(cv, S.LAMP_X + math.sin(sw) * S.LAMP_Y, math.cos(sw) * S.LAMP_Y + 22, 90, (255, 230, 150), 0.6 * light)
    if t >= T_TITLE_FLY + 0.4 and t < T_END_SNAP + 0.1:
        S.draw_label(cv, LABEL_TXT, alpha=S.seg(t, T_TITLE_FLY + 0.4, T_TITLE_FLY + 0.6) * light)
    # ----- escenas -----
    draw_I(cv, t)
    draw_B(cv, t)
    draw_L(cv, t)
    draw_N(cv, t)
    draw_A(cv, t)
    draw_P(cv, t)
    draw_Q(cv, t)
    draw_F(cv, t)
    draw_Cr(cv, t)
    draw_title(cv, t)
    # ----- sombra -----
    if light > 0.05:
        h = S.FLOOR_Y - yf
        sh_w = 150 * max(0.4, 1 - h / 600)
        d = ImageDraw.Draw(cv, 'RGBA')
        d.ellipse([x - sh_w, S.FLOOR_Y - 14, x + sh_w, S.FLOOR_Y + 12], fill=(0, 0, 0, int(110 * light * max(0.3, 1 - h / 500))))
    # ----- personaje -----
    char_light = 0.32 + 0.68 * light if t < T_END_SNAP + 1.3 else 0.32
    for t0 in (T_OPEN, Nn['open']):
        if t0 <= t < t0 + 0.35:
            char_light = min(1.25, char_light + 0.3 * (1 - (t - t0) / 0.35))
    CH.render(cv, pose, dict(scale=S.SCALE, ox=x, oy=yf, view_yaw=0.12 * math.sin(t * 0.2)), light=char_light, t=t)
    draw_Fin(cv, t)
    # destello del neón (naranja) en el gancho y en la repetición
    for t0 in (T_OPEN, Nn['open']):
        if t0 <= t < t0 + 0.3:
            u = (t - t0) / 0.3
            S.glow_fast(cv, NEON_C[0], NEON_C[1], 460, (255, 150, 70), 0.55 * (1 - u) ** 2)
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
