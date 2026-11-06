#!/usr/bin/env python3
# Capítulo 9: El relé. Vertical 1080x1920, 30 fps.
# Gancho en el segundo 0: laboratorio en penumbra, título arriba, un botoncito de 5 V conectado a un relé azul
# y un REFLECTOR gigante. A los 0,4 s aprieta el botón: ¡CLIC! y el reflector prende el cuarto entero.
# Mejora nueva de este capítulo: PLANOS CERCANOS (la "cámara" hace zoom al relé por dentro, a los contactos
# en el ¡CLIC! y a la polilla de la Mark II).
# Regla: cada rótulo sale de VERIFICACION.md.
import math
import random
import numpy as np
from PIL import Image, ImageDraw
import scene as S
import diagrams as D
import inductor as I
import rele as R
import lab as LB
import char3d as C
from timeline import TL, PHRASES

W, H = S.W, S.H
FPS = S.FPS
CH = C.Character()
HOME_X = 230
INTRO_X = 290
LABEL_TXT = 'CAP. 9 · EL RELÉ'

P = lambda i: TL.s(i)
E = lambda i: TL.e(i)
KW = TL.kw

# ======================= tiempos clave =======================
T_PRESS = 0.4                       # aprieta el botoncito (¡CLIC! + reflector)
T_BONK = T_PRESS                    # (la música usa este nombre)
T_TITLE = T_PRESS                   # el groove arranca con el encendido
T_TITLE_FLY = P(1) + 0.15
T_WALK_HOME = P(1) + 0.2
T_H_SLAP = P(2) - 0.15              # se rompe el montaje del gancho
T_R_SLAP = E(5) + 0.2               # se rompe el relé en corte
T_N_SLAP = E(7) + 0.2               # se rompen los medidores
T_K_SLAP = E(8) + 0.2               # se rompe la gráfica del pico
T_C_SLAP = E(9) + 0.2               # se rompe el carro
T_M_SLAP = E(11) + 0.02             # se rompe la Mark II
T_END_SNAP = E(13) + 0.6
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
    (0.0, 'guino'), (T_PRESS + 0.02, 'sorpresa'), (KW(0, 'botoncito'), 'curioso'), (KW(0, 'GIGANTE'), 'sorpresa'),
    (KW(0, 'Cómo'), 'pensando'), (KW(0, 'RELÉ'), 'feliz'),
    (P(1), 'guino'), (KW(1, 'BICHO'), 'curioso'),
    (P(2), 'feliz'), (KW(2, 'IMÁN'), 'curioso'), (KW(2, 'BOBINA'), 'feliz'),
    (P(3), 'curioso'), (KW(3, 'IMÁN'), 'sorpresa'), (KW(3, 'jala'), 'feliz'),
    (P(4) - 0.1, 'sorpresa'), (KW(4, 'metal'), 'feliz'),
    (P(5), 'pensando'), (KW(5, 'RESORTE'), 'guino'),
    (P(6), 'guino'), (KW(6, '71'), 'curioso'), (KW(6, 'AMPERIOS', 1), 'sorpresa'),
    (P(7), 'feliz'), (KW(7, 'nunca'), 'pensando'),
    (P(8), 'sorpresa'), (KW(8, 'capítulo'), 'guino'), (KW(8, 'DIODO'), 'feliz'),
    (P(9), 'feliz'), (KW(9, 'PITO'), 'sorpresa'), (KW(9, 'corriente'), 'pensando'),
    (P(10), 'guino'), (KW(10, 'POLILLA'), 'sorpresa'), (KW(10, 'cuaderno'), 'feliz'),
    (P(11), 'pensando'), (KW(11, 'chiste'), 'feliz'),
    (P(12), 'corazon'),
    (P(13), 'feliz'), (KW(13, 'Reto'), 'guino'), (KW(13, 'COMÚN'), 'pensando'), (KW(13, 'Respóndeme'), 'feliz'),
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
        (P(7) + 0.1, 290, 0.6), (E(7) + 0.25, HOME_X, 0.6),
        (KW(13, 'Reto') - 0.1, 290, 0.7),
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
    # pícaro con el dedo en el botón; con la luz se echa para atrás y se tapa la luz con la mano
    if t < T_PRESS:
        p.lean += 0.08
        p.head = (p.head[0] - 0.12, p.head[1] + 0.4, p.head[2])
        p.look = (1.0, 0.3)
    elif t < P(0) + 0.8:
        u = t - T_PRESS
        j = S.jelly(u, 3.0, 4.0)
        p.lean += -0.22 * math.exp(-u * 3) + 0.04 * math.sin(u * 8)
        p.sx *= 1 + 0.07 * j; p.sy *= 1 - 0.07 * j
        p.head = (p.head[0] + 0.1 * math.exp(-u * 2), p.head[1] - 0.3 * math.exp(-u * 2), p.head[2])


def diagram_active(t):
    return (P(2) + 0.4 <= t < T_R_SLAP) or (P(6) + 0.3 <= t < T_N_SLAP) or (P(8) + 0.3 <= t < T_K_SLAP) \
        or (P(10) + 0.3 <= t < T_M_SLAP)


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


def light_at(t):
    if t > T_END_SNAP + 0.05:
        return 0.0
    if t < T_PRESS + 0.03:
        return 0.36                 # penumbra antes de apretar el botón
    return 0.36 + 0.64 * S.ease_out(S.seg(t, T_PRESS + 0.03, T_PRESS + 0.16))


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
        _tc['b'] = S.fancy_text('RELÉ?', 104, top=(170, 215, 255), bot=(40, 110, 230), outline=(8, 24, 70))
    return _tc

def setup_title():
    ev(KW(0, 'RELÉ') - 0.05, 'block', 0.5, 0.0, pitch=1.1)
    ev(T_TITLE_FLY, 'whoosh', 0.4, 0.0)

def draw_title(cv, t):
    TI = title_imgs()
    if t < T_TITLE_FLY + 0.5:
        fly = S.ease_in(S.seg(t, T_TITLE_FLY, T_TITLE_FLY + 0.45))
        bump = 1 + 0.12 * S.jelly(t - KW(0, 'RELÉ'), 3, 5) if t >= KW(0, 'RELÉ') else 1.0
        ya = 262 + (S.ROOM_T + 46 - 262) * fly; yb = 345 + (S.ROOM_T + 46 - 345) * fly
        sc = 1 - 0.75 * fly
        S.paste_center(cv, TI['a'], 540, ya, scale=sc, alpha=1 - fly * 0.9)
        S.paste_center(cv, TI['b'], 540, yb, scale=sc * bump, alpha=1 - fly * 0.9)


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


# ======================= escena H: gancho (frases 0–1) =======================
Hh = {}
BTN_C = (500, 1000)          # botoncito (en su tablerito)
BOARD = (380, 960, 760, 1060)
RBOX_C = (650, 1000); RBOX_W = 120
FLOOD_C = (880, 655); FLOOD_W = 320
BAT5 = (430, 1010)

def setup_H():
    POINTS.append((0.0, T_PRESS + 0.25, 'l', (BTN_C[0], BTN_C[1] - 20)))
    ev(T_PRESS, 'click', 0.5, panx(BTN_C[0]))
    ev(T_PRESS + 0.03, 'relay', 1.0, panx(RBOX_C[0]))
    ev(T_PRESS + 0.06, 'thud', 0.6, panx(FLOOD_C[0]))
    ev(T_PRESS + 0.06, 'hum', 0.06, panx(FLOOD_C[0]), dur=T_H_SLAP - T_PRESS, f=120)
    SHAKES.append((T_PRESS + 0.05, 0.22, 7))
    GEST.append((T_PRESS + 0.25, 0.9, 'shade'))
    Hh['l_btn'] = KW(0, 'botoncito') - 0.05
    Hh['l_flood'] = KW(0, 'GIGANTE') - 0.1
    Hh['l_rele'] = KW(0, 'RELÉ') - 0.05
    Hh['promise'] = KW(1, 'BICHO') - 0.15
    for k in ('l_btn', 'l_flood', 'l_rele'):
        ev(Hh[k], 'pop', 0.4, 0.3)
    ev(Hh['promise'], 'chime', 0.3, 0.2)
    add_slap(T_H_SLAP)

def moth_path(t, t0):
    """la polilla vuela en ochos alrededor de la luz (el bicho del final)"""
    u = t - t0
    x = FLOOD_C[0] - 30 + 120 * math.sin(u * 2.1) - 60 * (1 - S.ease_out(S.clamp(u / 0.6)))
    y = FLOOD_C[1] - 150 + 55 * math.sin(u * 4.2) + 300 * (1 - S.ease_out(S.clamp(u / 0.6)))
    return x, y

def draw_H(cv, t, at=None):
    if t > T_H_SLAP + 1.0:
        return
    if t >= T_H_SLAP and at is None:
        shattered(cv, draw_H, T_H_SLAP, t, 3, y0=230, y1=1090)
        return
    on = S.ease_out(S.seg(t, T_PRESS + 0.03, T_PRESS + 0.12))
    if on > 0.01:
        S.paste_center(cv, R.beam(round(on, 1), 640, 240, 760), FLOOD_C[0] - 200, FLOOD_C[1] + 300, angle=-0.55, alpha=0.9)
    l = D.L(W, 260)
    oy = 900
    l.rrect([BOARD[0], BOARD[1] - oy, BOARD[2], BOARD[3] - oy], 12, fill=(24, 96, 60, 255), outline=(12, 50, 30, 255), width=4)
    # cable delgado (control) botón → relé y cable grueso relé → reflector
    l.line([(BTN_C[0] + 50, BTN_C[1] - oy + 22), (RBOX_C[0] - 60, BTN_C[1] - oy + 22)], (255, 217, 61, 255), 4)
    l.line([(RBOX_C[0] + 70, RBOX_C[1] - oy + 10), (FLOOD_C[0] - 40, RBOX_C[1] - oy + 10), (FLOOD_C[0] - 40, 1090 - oy)], (40, 40, 46, 255), 16)
    l.line([(RBOX_C[0] + 70, RBOX_C[1] - oy + 10), (FLOOD_C[0] - 40, RBOX_C[1] - oy + 10), (FLOOD_C[0] - 40, 1090 - oy)], (230, 110, 40, 255), 10)
    cv.alpha_composite(l.done(), (0, oy))
    S.paste_center(cv, R.floodlight(round(on, 1), FLOOD_W), FLOOD_C[0], FLOOD_C[1])
    if on > 0.01:
        S.glow_fast(cv, FLOOD_C[0], FLOOD_C[1] - 125, 260, (255, 245, 200), 0.75 * on)
    pressed = 1.0 if T_PRESS - 0.03 <= t < T_PRESS + 0.35 else 0.0
    S.paste_center(cv, R.pushbutton(pressed, 96), BTN_C[0], BTN_C[1])
    rb = R.relay_box(RBOX_W)
    sq = 1 + 0.12 * S.jelly(t - T_PRESS, 4, 6) if t >= T_PRESS else 1.0
    if t >= Hh['l_rele']:
        S.glow_fast(cv, RBOX_C[0], RBOX_C[1], 120, (90, 160, 255), 0.5 * (0.7 + 0.3 * math.sin(t * 6)))
    S.paste_center(cv, rb, RBOX_C[0], RBOX_C[1], sx=2 - sq, sy=sq)
    S.paste_center(cv, R.small_led(1.0 if t >= T_PRESS else 0.0, 9), RBOX_C[0] + 20, BOARD[1] + 18)
    if t >= T_PRESS + 0.03 and t < T_PRESS + 0.6:
        S.paste_center(cv, burst('¡CLIC!', 46), RBOX_C[0] + 10, RBOX_C[1] - 120, scale=S.ease_back(S.seg(t, T_PRESS + 0.03, T_PRESS + 0.18)) * (1 - S.seg(t, T_PRESS + 0.45, T_PRESS + 0.6)))
    lbl(cv, 'BOTÓN · 5 V', BTN_C[0] + 70, BOARD[3] + 32, pop_in(t, Hh['l_btn']), (255, 230, 140))
    lbl(cv, 'REFLECTOR', FLOOD_C[0], FLOOD_C[1] + 330, pop_in(t, Hh['l_flood']), (255, 245, 200))
    lbl(cv, 'RELÉ', RBOX_C[0], RBOX_C[1] - 100, pop_in(t, Hh['l_rele']) * (1 - S.seg(t, T_PRESS + 0.03, T_PRESS + 0.05) if t < Hh['l_rele'] else 1), (150, 200, 255), 28)
    if t >= Hh['promise']:
        a = pop_in(t, Hh['promise']) * (1 - S.seg(t, T_H_SLAP - 0.3, T_H_SLAP))
        mx, my = moth_path(t, Hh['promise'])
        S.paste_center(cv, R.moth((t * 9) % 1.0, 120), mx, my, alpha=a)
        lbl(cv, 'AL FINAL: ¿QUÉ BICHO?', 470, 440, a, (255, 220, 120), 28)


# ======================= escena R: el relé por dentro (frases 2–5) =======================
Rr = {}
R_C = (640, 600)
def setup_R():
    Rr['in'] = P(2) - 0.05
    Rr['lid'] = KW(2, 'BOBINA') - 0.35
    Rr['curr'] = KW(3, 'corriente') - 0.1
    Rr['field'] = KW(3, 'IMÁN') - 0.05
    Rr['pull'] = KW(3, 'jala') + 0.05
    Rr['cont'] = KW(3, 'CONTACTOS') - 0.1
    Rr['zoom'] = P(4) - 0.35
    Rr['off1'] = KW(4, 'CLIC') - 0.4
    Rr['on2'] = KW(4, 'CLIC') - 0.05
    Rr['metal'] = KW(4, 'metal') - 0.05
    Rr['unzoom'] = E(4) + 0.05
    Rr['release'] = KW(5, 'corriente') + 0.1
    Rr['spring'] = KW(5, 'RESORTE') - 0.1
    add_throw(Rr['in'] - 0.45, R_C, lambda t: R.relay_box(360), side='l', dur=0.45, land_sfx='block')
    ev(Rr['lid'], 'pop', 0.5, 0.0, f0=300, f1=900); ev(Rr['lid'] + 0.05, 'whoosh', 0.4, 0.2)
    ev(Rr['curr'], 'switch', 0.4, -0.2)
    ev(Rr['field'], 'hum', 0.07, 0.0, dur=Rr['release'] - Rr['field'], f=100)
    for tt in (Rr['pull'], Rr['on2']):
        ev(tt, 'relay', 1.0, panx(R_C[0] + 150))
        SHAKES.append((tt, 0.16, 6))
    ev(Rr['off1'], 'relay', 0.7, panx(R_C[0] + 150), off=True)
    ev(Rr['release'], 'relay', 0.75, panx(R_C[0] + 150), off=True)
    ev(Rr['release'] + 0.05, 'boing', 0.35, 0.1, f0=500, f1=900)
    ev(Rr['spring'], 'pop', 0.35, 0.0)
    for k in ('cont', 'metal'):
        ev(Rr[k], 'pop', 0.35, 0.2)
    GEST.extend([(KW(2, 'INTERRUPTOR'), 0.9, 'present'), (KW(2, 'BOBINA'), 0.8, 'open'),
                 (KW(3, 'jala') - 0.1, 0.8, 'present'), (Rr['on2'] - 0.25, 1.2, 'ears'), (KW(5, 'RESORTE'), 0.9, 'present')])
    add_slap(T_R_SLAP)

def r_k(t):
    """posición de la armadura (0 suelta, 1 pegada) con rebote gelatinoso"""
    def pull(t0):
        u = t - t0
        if u < 0:
            return 0.0
        return min(1.0, S.ease_in(S.clamp(u / 0.06))) if u < 0.06 else 1.0
    def rel(t0):
        u = t - t0
        if u < 0:
            return 1.0
        return max(0.0, math.exp(-u * 9) * math.cos(u * 30)) if u > 0 else 1.0
    if t < Rr['pull']:
        return 0.0
    if t < Rr['off1']:
        return pull(Rr['pull'])
    if t < Rr['on2']:
        return max(0.0, rel(Rr['off1']))
    if t < Rr['release']:
        return pull(Rr['on2'])
    return max(0.0, rel(Rr['release']))

def r_zoom(t):
    """plano cercano: de 1 a 1.75 sobre los contactos en el ¡CLIC!"""
    zin = S.ease_io(S.seg(t, Rr['zoom'], Rr['zoom'] + 0.45))
    zout = S.ease_io(S.seg(t, Rr['unzoom'], Rr['unzoom'] + 0.45))
    return zin * (1 - zout)

def draw_R(cv, t, at=None):
    if t < Rr['in'] or t > T_R_SLAP + 1.0:
        return
    if t >= T_R_SLAP and at is None:
        shattered(cv, draw_R, T_R_SLAP, t, 5, y0=230, y1=1060)
        return
    th = THROWS[[i for i, x in enumerate(THROWS) if abs(x['t0'] - (Rr['in'] - 0.45)) < 1e-6][0]]
    if t < Rr['lid'] + 0.05:
        st = throw_state(th, t)
        if st is not None and st[0] == 'fly':
            S.paste_center(cv, R.relay_box(360), st[1], st[2], scale=st[4], angle=st[3])
            return
        if st is not None:
            S.paste_center(cv, R.relay_box(360), R_C[0], R_C[1], sx=st[1], sy=st[2])
        lbl(cv, 'RELÉ DE 5 V', R_C[0], R_C[1] + 250, pop_in(t, Rr['in'] + 0.4), (150, 200, 255))
        return
    # corte por dentro
    k = r_k(t)
    on = t >= Rr['curr'] and t < Rr['release']
    flow = S.seg(t, Rr['curr'], Rr['curr'] + 0.2) if on else 0.0
    field = S.seg(t, Rr['field'], Rr['field'] + 0.25) * (1 - S.seg(t, Rr['release'], Rr['release'] + 0.15)) if t >= Rr['field'] else 0.0
    gc = 0.0
    for tt in (Rr['pull'], Rr['on2']):
        if tt <= t < tt + 0.5:
            gc = max(gc, 1 - (t - tt) / 0.5)
    img = R.relay_inside(k, flow, t, field, gc)
    z = r_zoom(t)
    base = 0.95
    sc = base * (1 + 0.5 * z)
    # el foco se mueve hacia los contactos
    fx, fy = R.CONT_X, R.rivet_pt(1)[1]
    cx0 = R_C[0] + (720 - R_C[0]) * z - (fx - R.RW / 2) * sc * z
    cy0 = R_C[1] - (fy - R.RH / 2) * sc * z
    a_in = S.seg(t, Rr['lid'], Rr['lid'] + 0.25)
    paste_clipped(cv, img, cx0, cy0, scale=sc * (0.9 + 0.1 * a_in), alpha=a_in)
    def to_scr(px, py):
        return cx0 + (px - R.RW / 2) * sc, cy0 + (py - R.RH / 2) * sc
    # tapa volando
    if t < Rr['lid'] + 0.7:
        u = S.seg(t, Rr['lid'], Rr['lid'] + 0.6)
        S.paste_center(cv, R.relay_lid(360), R_C[0] + 220 * u, R_C[1] - 420 * S.ease_out(u), angle=0.9 * u, alpha=1 - u)
    # rótulos
    LBS = R.inside_labels()
    def L_(name, t0, t1=None, col=(255, 255, 255), size=24):
        if t >= t0 and (t1 is None or t < t1):
            a = pop_in(t, t0) * (1 - (S.seg(t, t1 - 0.2, t1) if t1 else 0))
            x, y = to_scr(*LBS[name])
            lbl(cv, name, x, y, a, col, size)
    if z < 0.05:
        L_('BOBINA', KW(2, 'BOBINA') - 0.05, None, (255, 200, 140))
        L_('NÚCLEO', KW(3, 'IMÁN') - 0.05, None, (200, 210, 225))
        L_('ARMADURA', KW(3, 'hierro') - 0.05, None, (200, 210, 225))
        L_('RESORTE', Rr['spring'], None, (180, 240, 200), 28)
        L_('NC', Rr['cont'], None, (255, 200, 140))
        L_('NA', Rr['cont'] + 0.1, None, (150, 225, 255))
        L_('COM', Rr['cont'] + 0.2, None, (255, 230, 140))
    if t >= Rr['field'] and t < Rr['release'] and z < 0.05:
        lbl(cv, '¡IMÁN!', to_scr(395, 330)[0], to_scr(395, 330)[1], pop_in(t, Rr['field']), (150, 225, 255), 30)
    if t >= Rr['curr'] and t < Rr['release'] and z < 0.05:
        x, y = to_scr(R.PINS['b1'] - 70, R.PIN_Y + 40)
        lbl(cv, 'CORRIENTE', x, y, pop_in(t, Rr['curr']), (255, 217, 61), 22)
    # ¡CLIC! gigante en el plano cercano
    for tt in (Rr['pull'], Rr['on2']):
        if tt <= t < tt + 0.7:
            x, y = to_scr(R.CONT_X - 120, R.rivet_pt(1)[1] - 140)
            a = S.ease_back(S.seg(t, tt, tt + 0.15)) * (1 - S.seg(t, tt + 0.5, tt + 0.7))
            S.paste_center(cv, burst('¡CLIC!', 60 if tt == Rr['on2'] else 44), max(330, min(900, x)), max(300, y), scale=a, angle=-0.12)
    if t >= Rr['metal'] and t < Rr['unzoom'] + 0.2:
        a = pop_in(t, Rr['metal']) * (1 - S.seg(t, Rr['unzoom'], Rr['unzoom'] + 0.2))
        lbl(cv, 'METAL CONTRA METAL', 640, 930, a, (255, 230, 140), 30)
    if Rr['release'] <= t < Rr['release'] + 0.8:
        x, y = to_scr(205, 140)
        S.glow_fast(cv, x, y, 90, (180, 255, 200), 0.6 * (1 - (t - Rr['release']) / 0.8))


# ======================= escena N: corriente chica manda a corriente grande (frases 6–7) =======================
Nn = {}
G_L = (440, 430); G_R = (830, 430)
N_RB = (640, 760)
N_BULB = (900, 800)
def setup_N():
    Nn['in'] = P(6) - 0.1
    Nn['ma'] = KW(6, '71') - 0.15
    Nn['amp'] = KW(6, 'AMPERIOS', 1) - 0.3
    Nn['grande'] = KW(7, 'GRANDE') - 0.15
    Nn['nunca'] = KW(7, 'nunca') - 0.5
    add_throw(Nn['in'] - 0.4, G_L, lambda t: R.gauge('71 mA', 0.0, sub='BOBINA'), side='l', dur=0.4)
    add_throw(Nn['in'] - 0.15, G_R, lambda t: R.gauge('10 A', 0.0, sub='CONTACTOS'), side='l', dur=0.45, pitch=0.9)
    ev(Nn['in'] + 0.3, 'block', 0.45, panx(N_RB[0]), pitch=1.1)
    ev(Nn['ma'] + 0.1, 'tink', 0.3, panx(G_L[0]), f=2400)
    ev(Nn['amp'], 'relay', 0.9, panx(N_RB[0])); ev(Nn['amp'] + 0.05, 'zap', 0.4, panx(N_BULB[0]))
    SHAKES.append((Nn['amp'] + 0.05, 0.25, 8))
    ev(Nn['grande'], 'pop', 0.4, 0.2)
    ev(Nn['nunca'], 'marker', 0.4, 0.1, dur=0.5)
    GEST.extend([(KW(6, 'genial'), 0.8, 'chin'), (KW(6, 'AMPERIOS', 1), 0.9, 'open'), (KW(7, 'GRANDE'), 0.8, 'present')])
    add_slap(T_N_SLAP)

def draw_N(cv, t, at=None):
    if t < Nn['in'] - 0.45 or t > T_N_SLAP + 1.0:
        return
    if t >= T_N_SLAP and at is None:
        shattered(cv, draw_N, T_N_SLAP, t, 7, y0=230, y1=1060)
        return
    fl = S.ease_out(S.seg(t, Nn['ma'], Nn['ma'] + 0.4)) * 0.071 / 0.1 * 0.35   # aguja chiquita
    fr = S.ease_out(S.seg(t, Nn['amp'], Nn['amp'] + 0.35)) * 0.95
    if t >= Nn['amp'] + 0.35:
        fr += 0.02 * math.sin((t - Nn['amp']) * 9) * math.exp(-(t - Nn['amp']))
    on = t >= Nn['amp']
    big = S.ease_io(S.seg(t, Nn['grande'], Nn['grande'] + 0.4))
    sL = 1 - 0.25 * big; sR = 1 + 0.2 * big
    # circuitos (cable delgado a la izquierda, grueso a la derecha)
    if t >= Nn['in'] + 0.2:
        a = S.seg(t, Nn['in'] + 0.2, Nn['in'] + 0.5)
        l = D.L(W, 500); oy = 560
        l.line([(G_L[0], 520 - oy + 40), (G_L[0], N_RB[1] - oy), (N_RB[0] - 70, N_RB[1] - oy)], (255, 217, 61, int(255 * a)), 5)
        for w_, c_ in ((20, (40, 40, 46)), (12, (230, 110, 40))):
            l.line([(N_RB[0] + 70, N_RB[1] - oy), (N_BULB[0], N_RB[1] - oy), (N_BULB[0], 1010 - oy)], c_ + (int(255 * a),), w_)
            l.line([(G_R[0], 520 - oy + 40), (G_R[0], N_RB[1] - oy - 40), (N_RB[0] + 40, N_RB[1] - oy - 40)], c_ + (int(255 * a),), w_)
        if on:
            curr_squares(l, [(N_RB[0] + 70, N_RB[1] - oy), (N_BULB[0], N_RB[1] - oy)], t, 6, 0.5, a, size=9, col=(255, 190, 60))
        cv.alpha_composite(l.done(), (0, oy))
        if on:
            S.glow_fast(cv, N_BULB[0], N_BULB[1] - 30, 220, (255, 220, 120), 0.7)
        S.paste_center(cv, I.bulb(1.0 if on else 0.0, 170), N_BULB[0], N_BULB[1], alpha=a)
        S.paste_center(cv, R.relay_box(170), N_RB[0], N_RB[1], alpha=a,
                       sx=1 + 0.1 * S.jelly(t - Nn['amp'], 4, 6) if on else 1, sy=1 - 0.1 * S.jelly(t - Nn['amp'], 4, 6) if on else 1)
    for idx, (gx, gy), txt, frac, sub, sc_ in ((0, G_L, '71 mA', fl, 'BOBINA', sL), (1, G_R, '10 A', fr, 'CONTACTOS', sR)):
        th = N_THROWS[idx]
        st = throw_state(th, t)
        if st is None:
            continue
        img = R.gauge(txt, round(frac, 3), sub=sub)
        if st[0] == 'fly':
            S.paste_center(cv, img, st[1], st[2], scale=st[4], angle=st[3])
        else:
            S.paste_center(cv, img, gx, gy, scale=sc_, sx=st[1], sy=st[2])
    lbl(cv, 'HASTA 10 A · 250 V~', G_R[0], G_R[1] + 140 * sR, pop_in(t, Nn['amp'] + 0.3), (255, 190, 120), 22)
    lbl(cv, 'CHIQUITO', G_L[0], G_L[1] - 120 * sL, pop_in(t, Nn['grande'] - 0.4), (255, 230, 140), 24)
    lbl(cv, 'GRANDE', G_R[0], G_R[1] - 130 * sR, pop_in(t, Nn['grande']), (255, 160, 100), 30)
    if t >= Nn['nunca']:
        u = S.seg(t, Nn['nunca'], Nn['nunca'] + 0.45)
        l = D.L(40, 420)
        n = int(10 * u)
        for k in range(n):
            l.rect([14, k * 42, 26, k * 42 + 26], fill=(255, 80, 80, 255))
        S.paste_center(cv, l.done(), N_RB[0], 640)
        lbl(cv, 'AISLADOS · 1.500 V', N_RB[0], 890, pop_in(t, Nn['nunca'] + 0.3), (255, 120, 120), 26)

N_THROWS = []


# ======================= escena K: el pico y el diodo (frase 8) =======================
Kk = {}
K_G = (640, 430)
K_COIL = (640, 790)
def setup_K():
    Kk['in'] = P(8) - 0.05
    Kk['draw'] = KW(8, 'apagarlo') - 0.05
    Kk['pico'] = KW(8, 'PICO') - 0.05
    Kk['cap'] = KW(8, 'capítulo') - 0.5
    Kk['diode'] = KW(8, 'Por eso') - 0.15
    ev(Kk['in'], 'block', 0.5, 0.0, pitch=1.05)
    ev(Kk['draw'], 'relay', 0.6, 0.1, off=True)
    ev(Kk['pico'], 'zap', 0.9, 0.2); ev(Kk['pico'], 'thud', 0.5, 0.2)
    SHAKES.append((Kk['pico'], 0.25, 9))
    ev(Kk['cap'], 'pop', 0.4, 0.4)
    ev(Kk['diode'], 'whoosh', 0.4, 0.0); ev(Kk['diode'] + 0.35, 'block', 0.55, 0.0, pitch=1.2)
    ev(Kk['diode'] + 0.6, 'chime', 0.3, 0.0)
    GEST.extend([(KW(8, 'PICO'), 0.8, 'stop'), (KW(8, 'DIODO'), 0.9, 'present')])
    JUMPS.append((Kk['pico'] + 0.02, 0.4, 55))
    add_slap(T_K_SLAP)

def draw_K(cv, t, at=None):
    if t < Kk['in'] or t > T_K_SLAP + 1.0:
        return
    if t >= T_K_SLAP and at is None:
        shattered(cv, draw_K, T_K_SLAP, t, 9, y0=230, y1=1060)
        return
    k = 0.42 * S.seg(t, Kk['in'], Kk['draw']) + 0.58 * S.ease_out(S.seg(t, Kk['draw'], Kk['pico'] + 0.4))
    dk = S.seg(t, Kk['diode'] + 0.4, Kk['diode'] + 0.9)
    a = pop_in(t, Kk['in'], 0.35)
    S.paste_center(cv, R.spike_graph(round(k, 2), round(dk, 2), 520, 320), K_G[0], K_G[1], scale=a)
    if Kk['pico'] <= t < Kk['pico'] + 0.4:
        S.glow_fast(cv, K_G[0] - 20, K_G[1] - 120, 140, (255, 90, 90), 0.8 * (1 - (t - Kk['pico']) / 0.4))
    # bobina del relé con el diodo en paralelo
    S.paste_center(cv, I.coil(300, 100, 12), K_COIL[0], K_COIL[1], scale=a)
    le, re_ = I.coil_ends(K_COIL[0], K_COIL[1], 300, 100)
    lbl(cv, 'BOBINA DEL RELÉ', K_COIL[0], K_COIL[1] + 95, a * pop_in(t, Kk['in'] + 0.2), (255, 200, 140), 22)
    if t >= Kk['diode']:
        u = S.seg(t, Kk['diode'], Kk['diode'] + 0.35)
        y_d = K_COIL[1] - 120
        l = D.L(W, 200); oy = y_d - 40
        aa = int(255 * S.seg(t, Kk['diode'] + 0.3, Kk['diode'] + 0.4))
        l.line([(le[0], le[1] - oy), (le[0], y_d - oy), (K_COIL[0] - 90, y_d - oy)], (232, 232, 232, aa), 5)
        l.line([(re_[0], re_[1] - oy), (re_[0], y_d - oy), (K_COIL[0] + 90, y_d - oy)], (232, 232, 232, aa), 5)
        cv.alpha_composite(l.done(), (0, oy))
        S.paste_center(cv, R.diode_part(190), K_COIL[0], y_d - 300 * (1 - S.bounce_out(u)), angle=math.pi)
        lbl(cv, 'DIODO EN PARALELO', K_COIL[0], y_d - 60, pop_in(t, Kk['diode'] + 0.5), (120, 240, 150), 26)
    if t >= Kk['cap']:
        aa = pop_in(t, Kk['cap']) * (1 - S.seg(t, Kk['diode'] + 0.6, Kk['diode'] + 0.8))
        S.paste_center(cv, I.neon(1.0, 120), 930, 660, scale=aa)
        lbl(cv, 'CAP. 8', 930, 740, aa, (255, 170, 110), 24)


# ======================= escena C: el carro (frase 9) =======================
Cc = {}
CAR_C = (640, 470)
def setup_C():
    Cc['in'] = P(9) - 0.05
    Cc['luces'] = KW(9, 'LUCES') - 0.05
    Cc['pito'] = KW(9, 'PITO') - 0.05
    Cc['fuerte'] = KW(9, 'fuerte') - 0.2
    Cc['boton'] = KW(9, 'botón') - 0.15
    add_throw(Cc['in'] - 0.45, CAR_C, lambda t: R.car_front(0.0, 520), side='l', dur=0.45, arc=120, spin=0.0)
    ev(Cc['luces'], 'relay', 0.8, 0.0); ev(Cc['luces'] + 0.03, 'zap', 0.3, 0.0)
    ev(Cc['pito'], 'relay', 0.8, 0.1); ev(Cc['pito'] + 0.02, 'buzz', 0.9, 0.0)
    ev(Cc['fuerte'], 'pop', 0.4, 0.3); ev(Cc['boton'], 'pop', 0.4, -0.2)
    GEST.extend([(KW(9, 'LUCES'), 0.8, 'present'), (KW(9, 'PITO') - 0.1, 0.7, 'ears')])
    add_slap(T_C_SLAP)

def draw_C(cv, t, at=None):
    if t < Cc['in'] - 0.5 or t > T_C_SLAP + 1.0:
        return
    if t >= T_C_SLAP and at is None:
        shattered(cv, draw_C, T_C_SLAP, t, 11, y0=230, y1=1060)
        return
    th = C_THROW[0]
    st = throw_state(th, t)
    lights = S.seg(t, Cc['luces'], Cc['luces'] + 0.08)
    if st is None:
        return
    if st[0] == 'fly':
        S.paste_center(cv, R.car_front(0.0, 520), st[1], st[2], scale=st[4])
        return
    honk = Cc['pito'] <= t < Cc['pito'] + 0.45
    dy = 4 * math.sin(t * 90) if honk else 0
    if lights > 0.01:
        for x in (CAR_C[0] - 520 * 0.33, CAR_C[0] + 520 * 0.33):
            S.glow_fast(cv, x, CAR_C[1] + 30, 170, (255, 250, 200), 0.8 * lights)
    S.paste_center(cv, R.car_front(round(lights, 1), 520), CAR_C[0], CAR_C[1] + dy, sx=st[1], sy=st[2])
    if honk or (Cc['pito'] + 0.45 <= t < Cc['pito'] + 0.8):
        a = 1 - S.seg(t, Cc['pito'] + 0.45, Cc['pito'] + 0.8)
        S.paste_center(cv, burst('¡PIII!', 42), CAR_C[0] + 300, CAR_C[1] - 150, scale=S.ease_back(S.seg(t, Cc['pito'], Cc['pito'] + 0.15)) * a, angle=0.1)
    # esquema abajo: botón (cable delgado) → relé; batería → relé → luces (cable grueso)
    if t >= Cc['luces'] - 0.3:
        a = S.seg(t, Cc['luces'] - 0.3, Cc['luces'])
        l = D.L(W, 420); oy = 640
        l.line([(560, 900 - oy), (650, 900 - oy)], (255, 217, 61, int(255 * a)), 4)
        thick = [[(830, 900 - oy), (930, 900 - oy), (930, 600 - oy), (CAR_C[0] + 175, 600 - oy)],
                 [(760, 850 - oy), (760, 800 - oy), (980, 800 - oy)]]
        for w_, c_ in ((20, (40, 40, 46)), (12, (230, 110, 40))):
            for pts in thick:
                l.line(pts, c_ + (int(255 * a),), w_)
        if lights > 0:
            curr_squares(l, [(980, 800 - oy), (760, 800 - oy), (760, 850 - oy)], t, 4, 0.6, a, size=8, col=(255, 190, 60))
            curr_squares(l, thick[0], t, 6, 0.6, a, size=8, col=(255, 190, 60))
        cv.alpha_composite(l.done(), (0, oy))
        S.paste_center(cv, R.pushbutton(1.0 if lights > 0 else 0.0, 80), 520, 900, alpha=a)
        S.paste_center(cv, R.relay_box(130), 740, 910, alpha=a)
        lbl(cv, 'BATERÍA', 990, 760, a, (255, 230, 140), 22)
    lbl(cv, 'BOTÓN · CABLE DELGADO', 560, 985, pop_in(t, Cc['boton']), (255, 230, 140), 20)
    lbl(cv, 'A LAS LUCES · CABLE GRUESO', 830, 700, pop_in(t, Cc['fuerte']), (255, 170, 100), 20)


C_THROW = []


# ======================= escena M: la polilla de la Mark II (frases 10–11) =======================
Mm = {}
PAN_C = (640, 590); PAN_W = 520
CELL70 = (3, 4)
LOG_C = (640, 560)
def setup_M():
    Mm['in'] = P(10) - 0.05
    Mm['year'] = KW(10, '1947') - 0.1
    Mm['moth'] = KW(10, 'POLILLA') - 0.5
    Mm['stuck'] = KW(10, 'POLILLA') + 0.35
    Mm['r70'] = KW(10, 'relé') - 0.1
    Mm['zoom'] = KW(10, 'relé') + 0.1
    Mm['log'] = KW(10, 'cuaderno') - 0.4
    Mm['tape'] = KW(10, 'pegaron') + 0.15
    Mm['text'] = KW(10, 'bug') - 0.6
    Mm['exist'] = KW(11, 'existía') - 0.2
    Mm['joke'] = KW(11, 'chiste') - 0.4
    ev(Mm['in'], 'block', 0.5, 0.0, pitch=0.9); ev(Mm['in'] + 0.1, 'block', 0.45, 0.2, pitch=1.0)
    for k in range(6):
        ev(Mm['in'] + 0.3 + k * 0.11, 'relay', 0.35, -0.4 + 0.16 * k, off=bool(k % 2))
    ev(Mm['year'], 'pop', 0.4, 0.2)
    ev(Mm['moth'], 'whoosh', 0.25, 0.4)
    ev(Mm['stuck'], 'relay', 0.8, 0.0); ev(Mm['stuck'] + 0.05, 'boing', 0.35, 0.0, f0=300, f1=200)
    ev(Mm['r70'], 'pop', 0.4, 0.0)
    ev(Mm['log'], 'whoosh', 0.4, 0.0); ev(Mm['log'] + 0.35, 'block', 0.45, 0.0, pitch=1.2)
    ev(Mm['tape'], 'thud', 0.5, 0.0); ev(Mm['tape'] + 0.02, 'block', 0.4, 0.0, pitch=1.4)
    ev(Mm['text'], 'marker', 0.45, 0.0, dur=1.0)
    ev(Mm['exist'], 'thud', 0.7, 0.1); ev(Mm['exist'], 'block', 0.5, 0.1, pitch=0.7)
    SHAKES.append((Mm['exist'], 0.2, 6))
    ev(Mm['joke'], 'chime', 0.35, 0.0)
    GEST.extend([(KW(10, 'POLILLA'), 0.9, 'open'), (KW(10, 'cuaderno'), 0.8, 'present'), (KW(11, 'chiste') - 0.45, 1.4, 'laugh')])
    add_slap(T_M_SLAP)

def m_zoom(t):
    return S.ease_io(S.seg(t, Mm['zoom'], Mm['zoom'] + 0.5)) * (1 - S.ease_io(S.seg(t, Mm['log'] - 0.2, Mm['log'] + 0.2)))

def draw_M(cv, t, at=None):
    if t < Mm['in'] or t > T_M_SLAP + 0.55:
        return
    if t >= T_M_SLAP and at is None:
        shattered(cv, draw_M, T_M_SLAP, t, 13, y0=230, y1=1060)
        return
    a_pan = pop_in(t, Mm['in'], 0.35) * (1 - S.seg(t, Mm['log'] - 0.1, Mm['log'] + 0.2))
    z = m_zoom(t)
    cell = R.panel_cell_center(PAN_W, CELL70)
    sc = 1 + 1.0 * z
    pcx = PAN_C[0] - cell[0] * 1.0 * z
    pcy = PAN_C[1] - cell[1] * 1.0 * z
    c70 = (pcx + cell[0] * sc, pcy + cell[1] * sc)
    if a_pan > 0.01:
        hi = CELL70 if t >= Mm['r70'] else None
        paste_clipped(cv, R.relay_panel(PAN_W, hi), pcx, pcy, scale=sc * a_pan, alpha=min(1, a_pan * 1.5))
        if t >= Mm['r70']:
            lbl(cv, 'RELÉ #70', c70[0], c70[1] - 60 * sc * 0.6 - 30, pop_in(t, Mm['r70']) * a_pan, (255, 120, 120), 26)
    if t >= Mm['year']:
        a = pop_in(t, Mm['year'])
        lbl(cv, '9 SEP 1947 · HARVARD MARK II', 640, 905, a, (255, 230, 140), 26)
    # polilla: entra volando, queda atrapada en el relé 70, luego vuela al cuaderno y queda pegada
    if t >= Mm['moth']:
        if t < Mm['stuck']:
            u = S.seg(t, Mm['moth'], Mm['stuck'])
            x = 1000 + (c70[0] - 1000) * S.ease_io(u) + 40 * math.sin(u * 12)
            y = 300 + (c70[1] - 300) * S.ease_io(u) + 50 * math.sin(u * 9)
            S.paste_center(cv, R.moth((t * 9) % 1.0, 90), x, y)
        elif t < Mm['log'] + 0.3:
            wig = 0.08 * math.sin(t * 40)
            S.paste_center(cv, R.moth((t * 14) % 1.0, int(70 * sc)), c70[0], c70[1], angle=wig, alpha=max(0.0, 1 - S.seg(t, Mm['log'] + 0.1, Mm['log'] + 0.3)))
    if t >= Mm['log']:
        u = S.seg(t, Mm['log'], Mm['log'] + 0.4)
        x = LOG_C[0] + 700 * (1 - S.ease_out(u))
        tk = S.seg(t, Mm['text'], Mm['text'] + 1.0)
        S.paste_center(cv, R.logbook(text_k=round(tk, 2), w=600), x, LOG_C[1], angle=-0.04)
        mx, my = x - 20, LOG_C[1] - 20
        if t >= Mm['log'] + 0.2:
            if t < Mm['tape']:
                uu = S.seg(t, Mm['log'] + 0.2, Mm['tape'])
                S.paste_center(cv, R.moth((t * 9) % 1.0, 150), mx + 200 * (1 - uu), my - 200 * (1 - uu) + 40 * math.sin(uu * 8))
            else:
                S.paste_center(cv, R.moth(0.0, 150, flat=True), mx, my, angle=-0.04)
                tu = S.seg(t, Mm['tape'], Mm['tape'] + 0.12)
                S.paste_center(cv, R.tape_strip(260), mx, my - 10 - 60 * (1 - tu), angle=-0.12, scale=1.2 - 0.2 * tu)
        if t >= Mm['text'] + 1.0:
            lbl(cv, '"Primer caso real de bug encontrado"', 640, 960, pop_in(t, Mm['text'] + 1.0), (255, 255, 255), 24)
    if t >= Mm['exist']:
        u = S.seg(t, Mm['exist'], Mm['exist'] + 0.15)
        S.paste_center(cv, stamp_img('LA PALABRA YA EXISTÍA', 40), 640, 700, scale=2.2 - 1.2 * S.ease_in(u), angle=-0.15, alpha=min(1, u * 2))
    if t >= Mm['joke']:
        S.paste_center(cv, burst('¡CHISTE!', 40), 900, 960, scale=S.ease_back(S.seg(t, Mm['joke'], Mm['joke'] + 0.3)), angle=0.1)


# ======================= escena F: remate (frase 12) =======================
Ff = {}
F_C = (640, 640)
def setup_F():
    Ff['in'] = P(12) + 0.25
    Ff['iman'] = P(12) + 0.5
    ev(Ff['in'], 'pop', 0.45, 0.0)
    for k in range(4):
        ev(Ff['in'] + 0.5 + k * 0.5, 'relay', 0.55, 0.2, off=bool(k % 2))
    ev(Ff['iman'], 'chime', 0.35, 0.0)
    GEST.append((KW(12, 'interruptor'), 1.0, 'open'))

def draw_F(cv, t, at=None):
    if t < Ff['in'] or t > P(13) + 0.1:
        return
    a = pop_in(t, Ff['in'], 0.35) * (1 - S.ease_in(S.seg(t, P(13) - 0.25, P(13) + 0.1)))
    n = int(max(0, t - Ff['in'] - 0.5) / 0.5)
    stt = 1.0 if (n % 2 == 0 and t >= Ff['in'] + 0.5) else 0.0
    if n >= 4:
        stt = 1.0
    S.glow_fast(cv, F_C[0], F_C[1], 300, (90, 160, 255), 0.25 * a)
    S.paste_center(cv, R.relay_symbol(stt, w=430), F_C[0], F_C[1], scale=a)
    if t >= Ff['iman']:
        aa = pop_in(t, Ff['iman'], 0.35) * a
        S.paste_center(cv, S.fancy_text('IMÁN + INTERRUPTOR', 54, top=(170, 215, 255), bot=(40, 110, 230), outline=(8, 24, 70)), 560, 330, scale=aa)


# ======================= cierre: botones y reto =======================
Fin = {}
BTN = {'like': (810, 620), 'sub': (810, 755), 'follow': (810, 890)}
Q_C = (330, 560)

def setup_Fin():
    Fin['btn_in'] = P(13) - 0.4
    Fin['hit'] = {'like': KW(13, 'me gusta'), 'sub': KW(13, 'suscríbete'), 'follow': KW(13, 'sígueme')}
    Fin['q'] = KW(13, 'Reto') - 0.1
    Fin['q2'] = KW(13, 'COMÚN') - 0.1
    Fin['q3'] = KW(13, 'Respóndeme') - 0.1
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
    GEST.append((KW(13, 'COMÚN'), 0.9, 'chin'))
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
        S.paste_center(cv, R.relay_symbol(0.0, hide=True, w=360), x, Q_C[1], scale=0.85 * kk)
        S.paste_center(cv, D.label('RETO · RELÉ APAGADO', 26, fill=(255, 220, 120)), Q_C[0], Q_C[1] - 185,
                       scale=S.ease_back(S.seg(t, Fin['q'] + 0.2, Fin['q'] + 0.5)) * kk)
        if t >= Fin['q2']:
            a = S.ease_back(S.seg(t, Fin['q2'], Fin['q2'] + 0.3)) * kk
            S.paste_center(cv, D.label('¿COM → NA o NC?', 30, fill=(255, 255, 255)), Q_C[0], Q_C[1] + 175, scale=a)
        if t >= Fin['q3']:
            a = S.ease_back(S.seg(t, Fin['q3'], Fin['q3'] + 0.3)) * kk
            S.paste_center(cv, D.label('RESPÓNDEME EN LOS COMENTARIOS', 22, fill=(255, 255, 255)), Q_C[0] + 30, Q_C[1] + 228, scale=a)


def setup_all():
    setup_walks()
    setup_title()
    setup_H()
    setup_R()
    setup_N()
    N_THROWS.extend(THROWS[-2:])
    setup_K()
    setup_C()
    C_THROW.append(THROWS[-1])
    setup_M()
    setup_F()
    setup_Fin()
    react = [
        (T_PRESS + 0.04, 0.4, 50, None),                   # ¡luz!
        (Rr['pull'] + 0.03, 0.4, 45, None),                # ¡clic!
        (Nn['amp'] + 0.1, 0.45, 60, 'thumbs'),             # prende el bombillo grande
        (Cc['luces'] + 0.05, 0.4, 45, None),
        (Mm['stuck'] + 0.05, 0.4, 50, None),               # ¡atrapada!
        (KW(12, 'IMÁN') + 0.1, 0.45, 65, 'up'),            # remate
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
    if T_PRESS <= t < T_PRESS + 1.4:
        sw += 0.05 * math.sin((t - T_PRESS) * 7) * math.exp(-(t - T_PRESS) * 2.5)
    S.draw_lamp(cv, on=light, swing=sw)
    if light > 0.05:
        S.glow_fast(cv, S.LAMP_X + math.sin(sw) * S.LAMP_Y, math.cos(sw) * S.LAMP_Y + 22, 90, (255, 230, 150), 0.6 * light)
    if t >= T_TITLE_FLY + 0.4 and t < T_END_SNAP + 0.1:
        S.draw_label(cv, LABEL_TXT, alpha=S.seg(t, T_TITLE_FLY + 0.4, T_TITLE_FLY + 0.6) * light)
    # ----- escenas -----
    draw_H(cv, t)
    draw_R(cv, t)
    draw_N(cv, t)
    draw_K(cv, t)
    draw_C(cv, t)
    draw_M(cv, t)
    draw_F(cv, t)
    draw_title(cv, t)
    # ----- sombra -----
    if light > 0.05:
        h = S.FLOOR_Y - yf
        sh_w = 150 * max(0.4, 1 - h / 600)
        d = ImageDraw.Draw(cv, 'RGBA')
        d.ellipse([x - sh_w, S.FLOOR_Y - 14, x + sh_w, S.FLOOR_Y + 12], fill=(0, 0, 0, int(110 * light * max(0.3, 1 - h / 500))))
    # ----- personaje -----
    char_light = 0.32 + 0.68 * light if t < T_END_SNAP + 1.3 else 0.32
    if T_PRESS <= t < T_PRESS + 0.5:
        char_light = min(1.3, char_light + 0.35 * (1 - (t - T_PRESS) / 0.5))
    CH.render(cv, pose, dict(scale=S.SCALE, ox=x, oy=yf, view_yaw=0.12 * math.sin(t * 0.2)), light=char_light, t=t)
    draw_Fin(cv, t)
    # destello blanco del reflector al prender
    if T_PRESS + 0.03 <= t < T_PRESS + 0.35:
        u = (t - T_PRESS - 0.03) / 0.32
        S.glow_fast(cv, FLOOD_C[0], FLOOD_C[1] - 125, 700, (255, 250, 225), 0.6 * (1 - u) ** 2)
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
