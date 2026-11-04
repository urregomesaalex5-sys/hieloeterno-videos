#!/usr/bin/env python3
# Capítulo 7: La resistencia. Vertical 1080x1920, 30 fps.
# Intro (gancho en el segundo 0): laboratorio prendido, título arriba y un LED conectado DIRECTO a una
# fuente de 5 V. Él pulsa ON: el LED brilla de más, ¡pop!, chispa, hilo de humo y queda negro y agrietado.
# Regla: cada rótulo sale de VERIFICACION.md.
import math
import random
import numpy as np
from PIL import Image, ImageDraw
import scene as S
import diagrams as D
import resistencia as R
import lab as LB
import char3d as C
from timeline import TL, PHRASES

W, H = S.W, S.H
FPS = S.FPS
CH = C.Character()
HOME_X = 230
INTRO_X = 300
LABEL_TXT = 'CAP. 7 · LA RESISTENCIA'

P = lambda i: TL.s(i)
E = lambda i: TL.e(i)
KW = TL.kw

# ======================= tiempos clave =======================
T_PRESS = 0.12                      # pulsa ON
T_POP = max(0.5, P(0) - 0.25)       # ¡pop! (el LED se quema)
T_BONK = T_POP                      # (la música usa este nombre)
T_TITLE = T_POP                     # el groove arranca con el ¡pop! (el título ya está en pantalla)
T_SNAP = E(0) + 0.12              # chasquea: se construye el laboratorio
T_BUILD = T_SNAP + 0.08
T_LIT = T_BUILD + 1.2               # se prende la lámpara
T_TITLE_FLY = P(1) + 0.15
T_WALK_HOME = P(1) + 0.2
T_C_SLAP = E(5) + 0.25              # se rompe el circuito
T_J_SLAP = P(7) + 0.15              # se rompe la red de átomos
T_T_SLAP = E(7) + 0.2               # se rompe la tostadora
T_K_SLAP = E(9) + 0.25              # se rompe el código de colores
T_P_SLAP = E(10) + 0.2              # se rompe el celular
T_F_SLAP = P(12) - 0.1              # se rompe el circuito final
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
    (0.0, 'guino'), (T_PRESS + 0.1, 'feliz'), (T_POP - 0.15, 'curioso'), (T_POP, 'sorpresa'),
    (KW(0, 'Cómo'), 'pensando'), (KW(0, 'RESISTENCIA'), 'feliz'),
    (P(1), 'guino'), (KW(1, 'CÓDIGO'), 'feliz'),
    (P(2), 'curioso'), (KW(2, 'prende'), 'corazon'), (E(2), 'feliz'),
    (P(3), 'curioso'), (KW(3, 'LED'), 'pensando'), (KW(3, 'tocan'), 'feliz'),
    (P(4), 'pensando'), (KW(4, '3 ÷'), 'curioso'), (KW(4, '9 mili'), 'feliz'),
    (P(5), 'guino'), (KW(5, 'NO se'), 'sorpresa'), (KW(5, 'entra'), 'feliz'),
    (P(6), 'curioso'), (KW(6, 'vibran'), 'pensando'), (KW(6, 'calor'), 'sorpresa'), (KW(6, 'EFECTO'), 'feliz'),
    (P(7), 'guino'), (KW(7, 'TOSTADORA'), 'sorpresa'), (KW(7, 'rojo'), 'corazon'),
    (P(8), 'feliz'), (KW(8, 'multiplicador'), 'curioso'), (KW(8, 'tolerancia'), 'pensando'),
    (P(9), 'curioso'), (KW(9, '330'), 'sorpresa'), (KW(9, '330') + 0.5, 'feliz'),
    (P(10), 'curioso'), (KW(10, 'cientos'), 'sorpresa'), (KW(10, 'RESISTENCIAS'), 'feliz'),
    (P(11), 'feliz'), (KW(11, 'salvó'), 'corazon'),
    (P(12), 'feliz'), (KW(12, 'Reto'), 'guino'), (KW(12, 'Cuánto'), 'curioso'), (KW(12, 'Respóndeme'), 'feliz'),
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
            tp = pose.copy()
            tgt = target(t) if callable(target) else target
            aim(tp, side, shoulder_screen(x, yf, side, pose.sx, pose.sy), tgt, maxlen=2.6)
            wob = S.jelly(t - t0, 4, 5) * 0.12
            if side == 'l':
                tp.larm = (tp.larm[0], tp.larm[1], tp.larm[2] + wob)
            else:
                tp.rarm = (tp.rarm[0], tp.rarm[1], tp.rarm[2] + wob)
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
        (P(6) + 0.2, 310, 0.8), (P(7) + 0.5, HOME_X, 0.8),
        (P(10) + 0.2, 300, 0.8), (P(11) + 0.1, HOME_X, 0.8),
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
        # en reposo los brazos casi no se mueven: solo un vaivén suave al hablar
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
    # pícaro antes de pulsar; con el ¡pop! se va para atrás (sin taparse la cara)
    if t < T_POP:
        p.lean += 0.08 * S.ease_out(S.seg(t, 0.0, 0.3))
        p.head = (p.head[0] - 0.1, p.head[1] + 0.35, p.head[2])
        p.look = (1.0, -0.2)
    elif t < P(0) + 0.6:
        u = t - T_POP
        j = S.jelly(u, 3.0, 4.0)
        p.lean += -0.28 * math.exp(-u * 3) + 0.05 * math.sin(u * 8)
        p.sx *= 1 + 0.08 * j; p.sy *= 1 - 0.08 * j
        p.head = (p.head[0] - 0.1 + 0.08 * math.sin(u * 9), p.head[1] + 0.3 * math.exp(-u * 2), p.head[2])


def diagram_active(t):
    return (P(2) + 0.4 <= t < T_C_SLAP) or (P(6) + 0.4 <= t < T_J_SLAP) or (P(8) + 0.3 <= t < T_K_SLAP) \
        or (P(10) + 0.4 <= t < T_P_SLAP)


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
    # gestos para explicar: solo en momentos clave, y vuelven al reposo
    for t0, d, kind in GEST:
        if t0 - 0.2 <= t <= t0 + d + 0.25:
            k = S.ease_out(S.seg(t, t0 - 0.2, t0)) * (1 - S.ease_io(S.seg(t, t0 + d, t0 + d + 0.25)))
            tp = p.copy()
            if kind == 'present':      # mano abierta hacia el diagrama
                tp.larm = (0.85, 0, 0.95); tp.lelbow = 0.35
                blend_arm(p, 'l', tp, k)
                p.head = (p.head[0], p.head[1] + 0.35 * k, p.head[2])
            elif kind == 'open':       # los dos brazos abiertos
                tp.larm = (0.6, 0, 0.85); tp.lelbow = 0.3; tp.rarm = (0.6, 0, 0.85); tp.relbow = 0.3
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
            elif kind == 'count':      # mano frente al pecho, como quien cuenta
                tp.rarm = (1.25, 0, 0.25); tp.relbow = 1.5
                blend_arm(p, 'r', tp, k)
            elif kind == 'chin':       # mano en la barbilla
                tp.rarm = (1.9, 0, -0.2); tp.relbow = 2.0
                blend_arm(p, 'r', tp, k)
                p.head = (p.head[0] - 0.08 * k, p.head[1] + 0.2 * k, p.head[2] + 0.1 * k)
    # muestra la resistencia (mano izquierda arriba) en "te enseño a salvarlo"
    a, b = SHOW_T0, SHOW_T1
    if a - 0.2 <= t < b + 0.2:
        k = S.seg(t, a - 0.2, a) * (1 - S.seg(t, b, b + 0.2))
        tp = p.copy(); tp.larm = (1.2, 0, 1.4); tp.lelbow = 1.1; tp.larm_len = 1.1
        blend_arm(p, 'l', tp, k)
        p.head = (p.head[0] - 0.05 * k, p.head[1] + 0.25 * k, p.head[2])
    # "NO se come la corriente": niega con el dedo (mano derecha arriba) y con la cabeza
    a, b = KW(5, 'NO se') - 0.15, KW(5, 'entra')
    if a <= t < b + 0.2:
        k = S.seg(t, a, a + 0.15) * (1 - S.seg(t, b, b + 0.2))
        tp = p.copy(); tp.rarm = (1.3, 0, 0.9 + 0.35 * math.sin((t - a) * 16)); tp.relbow = 1.2
        blend_arm(p, 'r', tp, k)
        p.head = (p.head[0], p.head[1] + 0.25 * k * math.sin((t - a) * 12), p.head[2])
    # se calienta las manos frente a la tostadora
    a, b = KW(7, 'rojo') - 0.2, T_T_SLAP - 0.3
    if a <= t < b:
        k = S.seg(t, a, a + 0.25) * (1 - S.seg(t, b - 0.25, b))
        rub = 0.12 * math.sin((t - a) * 18)
        tp = p.copy(); tp.larm = (1.5 + rub, 0, 0.35); tp.lelbow = 0.5; tp.rarm = (1.5 - rub, 0, 0.35); tp.relbow = 0.5
        blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
        p.lean += 0.1 * k
    # chasquido que construye el laboratorio
    if T_SNAP - 0.3 <= t < T_SNAP + 0.6:
        u = S.ease_out(S.seg(t, T_SNAP - 0.3, T_SNAP - 0.05)) * (1 - S.seg(t, T_SNAP + 0.3, T_SNAP + 0.6))
        tp = p.copy(); tp.rarm = (0.3, 0, 2.6); tp.relbow = 0.5
        blend_arm(p, 'r', tp, u)
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
    if t < T_LIT or t > T_END_SNAP + 0.05:
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

# ======================= lanzamientos =======================
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


def curr_squares(l, pts, t, n, speed, on, oy=0, col=None, size=9):
    col = col or D.CURR
    for k in range(n):
        p = D.along(pts, (t * speed + k / n) % 1.0)
        l.rect([p[0] - size, p[1] - oy - size, p[0] + size, p[1] - oy + size], fill=col + (int(255 * on),))


def capture(fn, t, y0, y1):
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fn(tmp, t, at=True)
    return tmp.crop((0, y0, W, y1))

_cap_cache = {}
def shattered(cv, fn, ts, t, seed, y0=250, y1=960):
    """dibuja la escena 'fn' rota en bloquecitos tras el manotazo en ts"""
    key = (fn, ts)
    if key not in _cap_cache:
        _cap_cache[key] = capture(fn, ts - 0.01, y0, y1)
    D.shatter(cv, _cap_cache[key], 0, y0, t - ts, seed=seed, tile=64, push=(300, -100))

def add_slap(ts):
    SLAPS.append((ts, 'l'))
    ev(ts, 'whoosh', 0.5, 0.2); ev(ts + 0.05, 'crumble', 0.7, 0.2)


# ======================= título (en pantalla desde el cuadro 0) =======================
_tc = {}
def title_imgs():
    if not _tc:
        _tc['a'] = S.fancy_text('¿CÓMO FUNCIONA UNA', 70)
        _tc['b'] = S.fancy_text('RESISTENCIA?', 104, top=(255, 236, 170), bot=(240, 130, 30), outline=(70, 30, 5))
    return _tc

def setup_title():
    ev(KW(0, 'RESISTENCIA') - 0.05, 'block', 0.5, 0.0, pitch=1.1)
    ev(T_TITLE_FLY, 'whoosh', 0.4, 0.0)

def draw_title(cv, t):
    TI = title_imgs()
    if t < T_TITLE_FLY + 0.5:
        fly = S.ease_in(S.seg(t, T_TITLE_FLY, T_TITLE_FLY + 0.45))
        ka = 1.0 if t < 0.02 else S.ease_back(S.seg(t, 0.0, 0.25)) * 0.15 + 0.85
        bump = 1 + 0.12 * S.jelly(t - KW(0, 'RESISTENCIA'), 3, 5) if t >= KW(0, 'RESISTENCIA') else 1.0
        ya = 288 + (S.ROOM_T + 46 - 288) * fly; yb = 372 + (S.ROOM_T + 46 - 372) * fly
        sc = 1 - 0.75 * fly
        S.paste_center(cv, TI['a'], 600, ya, scale=ka * sc, alpha=1 - fly * 0.9)
        S.paste_center(cv, TI['b'], 600, yb, scale=ka * sc * bump, alpha=1 - fly * 0.9)


# ======================= escena C: el circuito (frases 0–5 y 11) =======================
Cc = {}
SUP = (700, 890)
SUP_SC = 1.2
TERM_M = (SUP[0] + (90 - R.SUP_W / 2) * SUP_SC, SUP[1] + (10 - (R.SUP_H + 30) / 2) * SUP_SC)    # terminal −
TERM_P = (SUP[0] + (190 - R.SUP_W / 2) * SUP_SC, SUP[1] + (10 - (R.SUP_H + 30) / 2) * SUP_SC)   # terminal +
BTN_ON = (SUP[0] + (80 - R.SUP_W / 2) * SUP_SC, SUP[1] + (167 - (R.SUP_H + 30) / 2) * SUP_SC)
XL, XR, YT, YB = 470, 920, 450, 745
LED_H = 250
LED_C = (XL, 575)
RES_C = (695, YT)
RES_W = 200
LOOP = [TERM_P, (TERM_P[0], YB), (XR, YB), (XR, YT), (XL, YT), (XL, YB), (TERM_M[0], YB), TERM_M]
BAR_C = (1010, 610)
SHELF_LED = (330, 392)

def setup_C():
    Cc['press'] = T_PRESS + 0.1
    ev(Cc['press'], 'click', 0.7, panx(BTN_ON[0])); ev(Cc['press'] + 0.02, 'switch', 0.4, panx(BTN_ON[0]))
    ev(Cc['press'] + 0.05, 'buzz', 0.35, panx(LED_C[0]))
    ev(T_POP, 'pop', 0.9, panx(LED_C[0]), f0=300, f1=1800); ev(T_POP, 'zap', 0.6, panx(LED_C[0]))
    ev(T_POP + 0.05, 'hiss', 0.25, panx(LED_C[0]), dur=0.9)
    SHAKES.append((T_POP, 0.25, 8))
    POINTS.append((Cc['press'] - 0.02, Cc['press'] + 0.12, 'l', BTN_ON))
    # frase 1: muestra una resistencia
    Cc['show'] = SHOW_T0
    ev(SHOW_T0 + 0.05, 'tink', 0.35, panx(HOME_X), f=3200)
    Cc['code_lbl'] = KW(1, 'CÓDIGO') - 0.1
    ev(Cc['code_lbl'], 'pop', 0.4, 0.2)
    # frase 2: el LED quemado sale volando al estante; LED nuevo; resistencia en su lugar; prende
    Cc['eject'] = P(2) - 0.1
    ev(Cc['eject'], 'boing', 0.4, panx(LED_C[0]), f0=300, f1=700)
    ev(Cc['eject'] + 0.65, 'block', 0.4, panx(SHELF_LED[0]), pitch=1.4)
    Cc['th_led'] = add_throw(P(2) + 0.2, LED_C, lambda t: R.led(0.0, 0.0, LED_H), 'l', dur=0.4, arc=160, spin=0.4, land_sfx='pop')
    Cc['th_res'] = add_throw(KW(2, 'LIMITA') - 0.3, RES_C, lambda t: R.resistor(RES_W), 'l', dur=0.45, arc=170, spin=0.6)
    Cc['on'] = KW(2, 'prende') - 0.1
    ev(Cc['on'], 'zap', 0.35, panx(LED_C[0])); ev(Cc['on'], 'hum', 0.12, panx(LED_C[0]), dur=T_C_SLAP - Cc['on'], f=110)
    Cc['bar'] = KW(2, 'prende') + 0.1
    ev(Cc['bar'], 'whine', 0.15, panx(BAR_C[0]), dur=0.6, f0=500, f1=900)
    # frase 3: voltajes
    Cc['sup_hl'] = KW(3, 'Fuente') - 0.05
    Cc['vm_led'] = KW(3, 'LED') - 0.05
    Cc['vm_res'] = KW(3, 'resistencia') - 0.05
    Cc['stack'] = KW(3, 'tocan')
    for k in ('sup_hl', 'vm_led', 'vm_res'):
        ev(Cc[k], 'pop', 0.4, 0.3)
    ev(Cc['stack'], 'chime', 0.35, panx(BAR_C[0]))
    # frase 4: ley de Ohm
    Cc['ohm'] = P(4) + 0.05
    Cc['nums'] = KW(4, '3 ÷') - 0.1
    Cc['ma'] = KW(4, '9 mili') - 0.1
    ev(Cc['ohm'], 'block', 0.45, 0.2, pitch=1.2); ev(Cc['nums'], 'marker', 0.4, 0.2, dur=0.4)
    ev(Cc['ma'], 'chime', 0.35, panx(BAR_C[0]))
    # frase 5: no se consume
    Cc['amm'] = P(5) + 0.05
    Cc['strike'] = KW(5, 'come') - 0.05
    Cc['stamp'] = KW(5, 'entra') - 0.1
    ev(Cc['amm'], 'pop', 0.4, 0.0); ev(Cc['amm'] + 0.12, 'pop', 0.4, 0.4)
    ev(Cc['stamp'], 'thud', 0.7, 0.2); ev(Cc['stamp'], 'block', 0.5, 0.2, pitch=0.7)
    SHAKES.append((Cc['stamp'], 0.2, 6))
    add_slap(T_C_SLAP)

SHOW_T0 = P(1) + 0.1
SHOW_T1 = P(2) + 0.1

def led_state(t):
    """(on, burnt) del LED del circuito en la escena C"""
    if t < Cc['press']:
        return 0.0, 0.0
    if t < T_POP:
        u = S.seg(t, Cc['press'], T_POP)
        return 1.0 + 1.2 * u ** 1.5, 0.0
    return 0.0, 1.0

def draw_wires(cv, t, with_res, oy=250):
    l = D.L(W, 720)
    pts = [(x, y - oy) for x, y in LOOP]
    l.line(pts, D.WIRE + (255,), 8)
    cv.alpha_composite(l.done(), (0, oy))

def flow_layer(cv, t, on, speed=0.22, n=16):
    if on <= 0.01:
        return
    l = D.L(W, 720)
    curr_squares(l, LOOP, t, n, speed, on, oy=250, size=8)
    cv.alpha_composite(l.done(), (0, 250))

def draw_C(cv, t, at=None):
    if t > T_C_SLAP + 1.0:
        return
    if t >= T_C_SLAP and at is None:
        shattered(cv, draw_C, T_C_SLAP, t, 3)
        return
    res_in = throw_state(Cc['th_res'], t)
    res_landed = res_in is not None and res_in[0] == 'land'
    # cables (el tramo de arriba queda tapado por la resistencia cuando llega)
    draw_wires(cv, t, res_landed)
    # corriente: de sobra en la intro (rápida y roja), luego normalita
    if Cc['press'] <= t < T_POP:
        flow_layer_col(cv, t, 1.0, (255, 90, 60), speed=0.9, n=26)
    elif t >= Cc['on']:
        flow_layer(cv, t, S.seg(t, Cc['on'], Cc['on'] + 0.3))
    # fuente
    pressed = 1.0 if Cc['press'] <= t < Cc['press'] + 0.15 else 0.0
    amps = '0.00'
    if Cc['press'] <= t < T_POP:
        amps = '1.50'
    elif t >= Cc['on']:
        amps = '0.01'
    S.paste_center(cv, R.supply('5,00', amps, pressed), SUP[0], SUP[1], scale=SUP_SC)
    if Cc['sup_hl'] <= t < Cc['sup_hl'] + 1.2:
        u = (t - Cc['sup_hl']) / 1.2
        S.glow_fast(cv, SUP[0] - 30, SUP[1] - 20, 170, (120, 255, 140), 0.45 * math.sin(u * math.pi))
    # LED: el de la intro (se quema) y sale volando; luego el nuevo
    on, burnt = led_state(t)
    if t < Cc['eject']:
        jit = 3 * math.sin(t * 90) if Cc['press'] <= t < T_POP else 0
        if on > 0.05:
            S.glow_fast(cv, LED_C[0], LED_C[1] - 60, 120 + 80 * min(1, on - 1), (255, 120 if on < 1.5 else 230, 90), min(1.0, 0.6 * on))
        S.paste_center(cv, R.led(round(on, 1), burnt, LED_H), LED_C[0] + jit, LED_C[1])
    else:
        # LED nuevo
        lv = S.seg(t, Cc['on'], Cc['on'] + 0.15)
        def placeLED(c, sx, sy):
            if lv > 0.02:
                S.glow_fast(c, LED_C[0], LED_C[1] - 60, 150, (255, 70, 60), 0.6 * lv)
            S.paste_center(c, R.led(round(lv, 1), 0.0, LED_H), LED_C[0], LED_C[1], sx=sx, sy=sy)
        draw_thrown(cv, Cc['th_led'], t, placeLED)
    if T_POP <= t < Cc['eject']:
        R.spark(cv, LED_C[0], LED_C[1] - 70, t - T_POP)
        R.smoke(cv, LED_C[0], LED_C[1] - 80, t - T_POP, a=1 - S.seg(t, Cc['eject'] - 0.4, Cc['eject']))
    # resistencia
    def placeR(c, sx, sy):
        S.paste_center(c, R.resistor(RES_W), RES_C[0], RES_C[1], sx=sx, sy=sy)
    draw_thrown(cv, Cc['th_res'], t, placeR)
    # rótulo de la promesa (frase 1)
    if Cc['code_lbl'] <= t < P(2) + 0.6:
        a = S.ease_back(S.seg(t, Cc['code_lbl'], Cc['code_lbl'] + 0.3)) * (1 - S.seg(t, P(2) + 0.3, P(2) + 0.6))
        S.paste_center(cv, D.label('AL FINAL: CÓDIGO DE COLORES', 32, fill=(255, 220, 120)), 690, 340, scale=a)
    # barra de corriente (frases 2, 4, 5)
    vis_bar = (Cc['bar'] <= t < Cc['stack'] - 0.2) or (t >= Cc['ohm'])
    if vis_bar:
        a0 = Cc['bar'] if t < Cc['stack'] else Cc['ohm']
        k = S.ease_back(S.seg(t, a0, a0 + 0.3))
        ma = 9.0 * S.ease_out(S.seg(t, a0, a0 + 0.8)) if t < Cc['stack'] else (9.0 if t >= Cc['ma'] else 9.0 * S.seg(t, Cc['ohm'], Cc['ma']))
        S.paste_center(cv, R.current_bar(round(ma)), BAR_C[0], BAR_C[1], scale=0.85 * k)
        S.paste_center(cv, D.label('LED: MÁX. TÍPICO 20 mA', 20, fill=(255, 140, 130)), 940, 395, scale=k)
    # voltajes (frase 3)
    if Cc['vm_led'] <= t < Cc['ohm']:
        out = S.seg(t, Cc['ohm'] - 0.3, Cc['ohm'])
        a = S.ease_back(S.seg(t, Cc['vm_led'], Cc['vm_led'] + 0.3)) * (1 - out)
        S.paste_center(cv, R.meter('≈2 V', 'V', 160), XL, 340, scale=a)
        S.paste_center(cv, D.label('LED ROJO', 22, fill=(255, 150, 140)), XL + 110, 560, scale=a)
        if t >= Cc['vm_res']:
            a2 = S.ease_back(S.seg(t, Cc['vm_res'], Cc['vm_res'] + 0.3)) * (1 - out)
            S.paste_center(cv, R.meter('3 V', 'V', 160), RES_C[0] + 60, 340, scale=a2)
        if t >= Cc['stack'] - 0.2:
            a3 = S.ease_back(S.seg(t, Cc['stack'] - 0.2, Cc['stack'] + 0.1)) * (1 - out)
            S.paste_center(cv, R.volt_stack(S.seg(t, Cc['stack'] - 0.2, Cc['stack']), S.seg(t, Cc['stack'], Cc['stack'] + 0.3)),
                           BAR_C[0], BAR_C[1], scale=0.85 * a3)
    # ley de Ohm (frase 4)
    if Cc['ohm'] <= t < Cc['amm']:
        out = S.seg(t, Cc['amm'] - 0.25, Cc['amm'])
        a = S.ease_back(S.seg(t, Cc['ohm'], Cc['ohm'] + 0.35)) * (1 - out)
        if t < Cc['nums']:
            S.paste_center(cv, S.fancy_text('I = V ÷ R', 76), 695, 330, scale=a)
        else:
            txt = '3 V ÷ 330 Ω' if t < Cc['ma'] else '3 V ÷ 330 Ω ≈ 9 mA'
            S.paste_center(cv, S.fancy_text(txt, 56 if t >= Cc['ma'] else 64), 695, 330, scale=a * (1 + 0.1 * S.jelly(t - Cc['nums'], 3, 6)))
        a2 = S.seg(t, Cc['nums'] + 0.3, Cc['nums'] + 0.6) * (1 - out)
        if a2 > 0:
            S.paste_center(cv, D.label('Ohm se aplica a la resistencia,', 22, fill=(200, 210, 230)), 695, 575, alpha=a2)
            S.paste_center(cv, D.label('no al LED', 22, fill=(200, 210, 230)), 695, 620, alpha=a2)
    # no se consume (frase 5)
    if t >= Cc['amm']:
        a = S.ease_back(S.seg(t, Cc['amm'], Cc['amm'] + 0.3))
        a2 = S.ease_back(S.seg(t, Cc['amm'] + 0.12, Cc['amm'] + 0.42))
        S.paste_center(cv, R.meter('9 mA', 'A', 150), 565, 345, scale=a)
        S.paste_center(cv, R.meter('9 mA', 'A', 150), 835, 345, scale=a2)
        if t >= Cc['strike']:
            a3 = S.seg(t, Cc['strike'], Cc['strike'] + 0.2)
            S.paste_center(cv, R.strike('"se gasta la corriente"', 26), 695, 555, alpha=a3)
        if t >= Cc['stamp']:
            u = S.seg(t, Cc['stamp'] - 0.0, Cc['stamp'] + 0.15)
            sc = 2.2 - 1.2 * S.ease_in(u)
            S.paste_center(cv, R.stamp('NO SE CONSUME', 40), 695, 645, scale=sc, angle=-0.12, alpha=min(1, u * 2))


def flow_layer_col(cv, t, on, col, speed=0.5, n=20):
    l = D.L(W, 720)
    curr_squares(l, LOOP, t, n, speed, on, oy=250, col=col, size=8)
    cv.alpha_composite(l.done(), (0, 250))


# LED quemado: sale volando al estante y se queda ahí (R.I.P. al final)
def shelf_led_pos(t):
    a = Cc['eject']
    if t < a:
        return None
    u = S.seg(t, a, a + 0.65)
    if u < 1:
        x = LED_C[0] + (SHELF_LED[0] - LED_C[0]) * u
        y = LED_C[1] + (SHELF_LED[1] - LED_C[1]) * u - 260 * math.sin(math.pi * u)
        return x, y, 1 - 0.55 * u, u * 4
    return SHELF_LED[0], SHELF_LED[1], 0.45, 0.0

def draw_shelf_led(cv, t):
    st = shelf_led_pos(t)
    if st is None or t > T_END_SNAP + 0.3:
        return
    x, y, sc, ang = st
    S.paste_center(cv, R.led(0.0, 1.0), x, y, scale=sc, angle=ang)
    if t >= Fn['rip']:
        a = S.ease_back(S.seg(t, Fn['rip'], Fn['rip'] + 0.35)) * (1 - S.seg(t, T_F_SLAP - 0.2, T_F_SLAP))
        if a > 0:
            S.paste_center(cv, D.label('R.I.P.', 26, fill=(220, 220, 230)), x, y - 85, scale=a)
            if t < T_F_SLAP:
                R.smoke(cv, x, y - 30, 0.8 + (t - Fn['rip']), a=0.35 * a)


# la resistencia que muestra en la frase 1 (en la mano)
def draw_show_res(cv, t):
    if not (SHOW_T0 <= t < Cc['th_res']['t0']):
        return
    hx, hy = hand_pos(t, 'l')
    k = S.ease_back(S.seg(t, SHOW_T0, SHOW_T0 + 0.3))
    S.paste_center(cv, R.resistor(RES_W), hx + 10, hy - 40, scale=0.9 * k, angle=0.15 * math.sin(t * 3))
    if t < SHOW_T0 + 0.6:
        S.glow_fast(cv, hx + 10, hy - 40, 90, (255, 240, 160), 0.6 * (1 - S.seg(t, SHOW_T0, SHOW_T0 + 0.6)))


# ======================= escena J: por dentro (efecto Joule) =======================
Jj = {}
LAT_C = (700, 565)
LAT_SC = 0.85
TH_C = (1005, 590)
def setup_J():
    Jj['in'] = P(6) - 0.05
    Jj['zoom'] = Jj['in'] + 0.45
    Jj['heat0'] = KW(6, 'vibran') - 0.2
    Jj['heat1'] = KW(6, 'calor') + 0.1
    Jj['joule'] = KW(6, 'EFECTO') - 0.1
    Jj['th'] = add_throw(Jj['in'], LAT_C, lambda t: R.resistor(260), 'l', dur=0.4, arc=150, spin=0.5)
    ev(Jj['zoom'], 'whoosh', 0.5, 0.2)
    for k in range(6):
        ev(KW(6, 'chocan') + k * 0.28, 'tink', 0.18, panx(LAT_C[0]) + 0.1 * (k % 3), f=2600 + 300 * (k % 3))
    ev(Jj['heat1'], 'hiss', 0.2, panx(LAT_C[0]), dur=1.0)
    ev(Jj['joule'], 'block', 0.5, 0.0, pitch=1.15); ev(Jj['joule'] + 0.25, 'block', 0.5, 0.0, pitch=0.95)
    add_slap(T_J_SLAP)

def draw_J(cv, t, at=None):
    if t < Jj['in'] or t > T_J_SLAP + 1.0:
        return
    if t >= T_J_SLAP and at is None:
        shattered(cv, draw_J, T_J_SLAP, t, 5)
        return
    if t < Jj['zoom'] + 0.3:
        z = S.ease_in(S.seg(t, Jj['zoom'], Jj['zoom'] + 0.3))
        def place(c, sx, sy):
            S.paste_center(c, R.resistor(260), LAT_C[0], LAT_C[1], sx=sx * (1 + 3 * z), sy=sy * (1 + 3 * z), alpha=1 - z)
        draw_thrown(cv, Jj['th'], t, place)
    if t >= Jj['zoom']:
        k = S.ease_back(S.seg(t, Jj['zoom'] + 0.1, Jj['zoom'] + 0.45))
        heat = S.ease_io(S.seg(t, Jj['heat0'], Jj['heat1']))
        S.paste_center(cv, R.lattice(t, heat), LAT_C[0], LAT_C[1], scale=LAT_SC * k)
        S.paste_center(cv, R.thermometer(0.15 + 0.75 * heat), TH_C[0], TH_C[1], scale=0.8 * k)
        if heat > 0.05:
            S.glow_fast(cv, LAT_C[0], LAT_C[1], 280, (255, 140, 40), 0.25 * heat * k)
        a = S.seg(t, Jj['zoom'] + 0.5, Jj['zoom'] + 0.8)
        S.paste_center(cv, D.label('MODELO SIMPLIFICADO', 22, fill=(200, 210, 230)), LAT_C[0], 790, alpha=a)
        S.paste_center(cv, D.label('iones de la red (+)  ·  electrones (−)', 20, fill=(200, 210, 230)), LAT_C[0], 835, alpha=a)
    if t >= Jj['joule']:
        k = S.ease_back(S.seg(t, Jj['joule'], Jj['joule'] + 0.35))
        S.paste_center(cv, S.fancy_text('¡EFECTO JOULE!', 74, top=(255, 230, 140), bot=(255, 110, 30)), LAT_C[0], 300, scale=k)


# ======================= escena T: tostadora =======================
Tt = {}
TOA_C = (720, 610)
def setup_T():
    Tt['drop'] = KW(7, 'TOSTADORA') - 0.4
    Tt['land'] = Tt['drop'] + 0.35
    Tt['glow0'] = KW(7, 'alambre') - 0.1
    Tt['glow1'] = KW(7, 'rojo') + 0.1
    Tt['lbl'] = KW(7, 'propósito') - 0.1
    ev(Tt['drop'], 'whoosh', 0.45, 0.2)
    ev(Tt['land'], 'thud', 0.8, panx(TOA_C[0])); ev(Tt['land'], 'block', 0.6, panx(TOA_C[0]), pitch=0.8)
    SHAKES.append((Tt['land'], 0.25, 9))
    ev(Tt['glow0'], 'hum', 0.2, panx(TOA_C[0]), dur=T_T_SLAP - Tt['glow0'], f=60)
    ev(Tt['glow1'], 'hiss', 0.15, panx(TOA_C[0]), dur=1.2)
    ev(Tt['lbl'], 'pop', 0.4, 0.2)
    add_slap(T_T_SLAP)

def draw_T(cv, t, at=None):
    if t < Tt['drop'] or t > T_T_SLAP + 1.0:
        return
    if t >= T_T_SLAP and at is None:
        shattered(cv, draw_T, T_T_SLAP, t, 7)
        return
    u = S.seg(t, Tt['drop'], Tt['land'])
    y = -300 + (TOA_C[1] + 300) * S.ease_in(u)
    j = S.jelly(t - Tt['land'], 3, 6) if t >= Tt['land'] else 0
    glow = S.ease_io(S.seg(t, Tt['glow0'], Tt['glow1']))
    toast = S.seg(t, Tt['glow1'], Tt['glow1'] + 2.0)
    if glow > 0.05:
        S.glow_fast(cv, TOA_C[0], TOA_C[1] + 40, 260, (255, 110, 30), 0.4 * glow)
    S.paste_center(cv, R.toaster(round(glow, 1), round(toast, 1)), TOA_C[0], y, sx=1 + 0.15 * j, sy=1 - 0.15 * j)
    if glow > 0.6:
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1.0
            S.paste_center(cv, D.label('~', 30, fill=(255, 190, 120), bg=(0, 0, 0, 0)), TOA_C[0] - 70 + 70 * k, TOA_C[1] - 200 - 80 * ph, alpha=(1 - ph) * glow)
    if t >= Tt['lbl']:
        a = S.ease_back(S.seg(t, Tt['lbl'], Tt['lbl'] + 0.3))
        S.paste_center(cv, D.label('CALOR A PROPÓSITO', 34, fill=(255, 190, 120)), TOA_C[0], 330, scale=a)


# ======================= escena K: código de colores =======================
Kk = {}
KR_C = (735, 560)
KR_W = 420
def setup_K():
    Kk['in'] = P(8) - 0.05
    Kk['th'] = add_throw(Kk['in'], KR_C, lambda t: R.resistor(KR_W), 'l', dur=0.45, arc=170, spin=0.4)
    Kk['l01'] = KW(8, '2 dígitos') - 0.05
    Kk['l2'] = KW(8, 'multiplicador') - 0.05
    Kk['l3'] = KW(8, 'tolerancia') - 0.05
    Kk['n'] = [KW(9, 'naranja', 0) - 0.05, KW(9, 'naranja', 1) - 0.05, KW(9, 'marrón') - 0.05, KW(9, 'dorado') - 0.05]
    Kk['res'] = KW(9, '330') - 0.1
    Kk['range'] = Kk['res'] + 0.9
    for k in ('l01', 'l2', 'l3'):
        ev(Kk[k], 'pop', 0.4, 0.3)
    for k, tn in enumerate(Kk['n']):
        ev(tn, 'tink', 0.35, panx(KR_C[0] + R.band_x(KR_W, k)), f=2400 + 300 * k)
    ev(Kk['res'], 'chime', 0.5, 0.0)
    add_slap(T_K_SLAP)

def band_hl(t):
    if Kk['n'][0] <= t < Kk['res']:
        h = None
        for k, tn in enumerate(Kk['n']):
            if t >= tn:
                h = k
        return h
    if Kk['l01'] <= t < Kk['l2']:
        return 0 if (t - Kk['l01']) % 0.6 < 0.3 else 1
    if Kk['l2'] <= t < Kk['l3']:
        return 2
    if Kk['l3'] <= t < Kk['l3'] + 0.9:
        return 3
    return None

def draw_K(cv, t, at=None):
    if t < Kk['in'] or t > T_K_SLAP + 1.0:
        return
    if t >= T_K_SLAP and at is None:
        shattered(cv, draw_K, T_K_SLAP, t, 9)
        return
    hl = band_hl(t)
    def place(c, sx, sy):
        S.paste_center(c, R.resistor(KR_W, hl=hl), KR_C[0], KR_C[1], sx=sx, sy=sy)
    draw_thrown(cv, Kk['th'], t, place)
    bx = [KR_C[0] + R.band_x(KR_W, k) for k in range(4)]
    labels_out = S.seg(t, P(9) - 0.2, P(9) + 0.1)
    l = D.L(W, 700)
    oy = 250
    specs = [('1.ª CIFRA', bx[0] - 60, 430, Kk['l01']), ('2.ª CIFRA', bx[1] - 40, 690, Kk['l01'] + 0.15),
             ('MULTIPLICADOR', bx[2] + 30, 370, Kk['l2']), ('TOLERANCIA', bx[3] + 30, 690, Kk['l3'])]
    for k, (txt, x, y, t0) in enumerate(specs):
        if t >= t0 and labels_out < 1:
            a = S.ease_back(S.seg(t, t0, t0 + 0.3)) * (1 - labels_out)
            yb = KR_C[1] - 45 if y < KR_C[1] else KR_C[1] + 45
            l.line([(bx[k], yb - oy), (x, y - oy + (22 if y < KR_C[1] else -22))], (255, 240, 160, int(220 * a)), 4)
            S.paste_center(cv, D.label(txt, 26, fill=(255, 230, 140)), x, y, scale=a)
    cv.alpha_composite(l.done(), (0, oy))
    # números (frase 9)
    nums = ['3', '3', '× 10', '± 5 %']
    nx = [560, 650, 770, 925]
    for k in range(4):
        tn = Kk['n'][k]
        if t >= tn:
            a = S.ease_back(S.seg(t, tn, tn + 0.3))
            # vuela desde la franja a su lugar
            u = S.ease_out(S.seg(t, tn, tn + 0.3))
            x = bx[k] + (nx[k] - bx[k]) * u
            y = KR_C[1] + (720 - KR_C[1]) * u
            S.paste_center(cv, S.fancy_text(nums[k], 64 if k < 2 else 50), x, y, scale=a)
    if t >= Kk['res']:
        a = S.ease_back(S.seg(t, Kk['res'], Kk['res'] + 0.35))
        S.paste_center(cv, S.fancy_text('= 330 Ω  ± 5 %', 76, top=(170, 255, 190), bot=(40, 190, 90), outline=(5, 50, 20)), KR_C[0], 360, scale=a)
    if t >= Kk['range']:
        a = S.seg(t, Kk['range'], Kk['range'] + 0.3)
        S.paste_center(cv, D.label('valor real: entre 313,5 y 346,5 Ω', 24, fill=(200, 230, 210)), KR_C[0], 830, alpha=a)


# ======================= escena Pc: el celular por dentro =======================
Pc = {}
PCB_C = (715, 560)
MAG_C = (850, 560)
def setup_P():
    Pc['in'] = P(10) - 0.05
    Pc['many'] = KW(10, 'cientos') - 0.05
    Pc['mag'] = KW(10, 'RESISTENCIAS') - 0.2
    Pc['size'] = Pc['mag'] + 0.6
    ev(Pc['in'], 'block', 0.5, 0.2, pitch=1.1); ev(Pc['in'] + 0.2, 'zap', 0.25, 0.2)
    ev(Pc['many'], 'pop', 0.4, 0.2)
    ev(Pc['mag'], 'whoosh', 0.4, 0.4); ev(Pc['mag'] + 0.3, 'tink', 0.35, 0.4, f=3000)
    ev(Pc['size'], 'pop', 0.35, 0.2)
    add_slap(T_P_SLAP)

_mag = {}
def mag_content():
    if 'c' not in _mag:
        l = D.L(380, 380)
        l.rect([0, 0, 380, 380], fill=(18, 92, 58, 255))
        l.line([(0, 190), (380, 190)], (196, 132, 58, 255), 26)
        l.rect([60, 160, 110, 220], fill=(232, 192, 70, 255)); l.rect([270, 160, 320, 220], fill=(232, 192, 70, 255))
        c = l.done()
        S.paste_center(c, R.smd_resistor(220), 190, 190)
        _mag['c'] = c
    return _mag['c']

def draw_P(cv, t, at=None):
    if t < Pc['in'] or t > T_P_SLAP + 1.0:
        return
    if t >= T_P_SLAP and at is None:
        shattered(cv, draw_P, T_P_SLAP, t, 11)
        return
    k = S.ease_back(S.seg(t, Pc['in'], Pc['in'] + 0.35))
    S.paste_center(cv, R.pcb_panel(t), PCB_C[0], PCB_C[1], scale=0.85 * k)
    # pulsos sobre la placa
    l = D.L(W, 600)
    for j in range(3):
        x = PCB_C[0] - 240 + ((t * 260 + j * 170) % 480)
        y = PCB_C[1] - 120 + j * 110
        l.rect([x - 10, y - 250 - 3, x + 10, y - 250 + 3], fill=(120, 240, 255, int(170 * k)))
    cv.alpha_composite(l.done(), (0, 250))
    if t >= Pc['many']:
        a = S.ease_back(S.seg(t, Pc['many'], Pc['many'] + 0.3))
        S.paste_center(cv, D.label('CIENTOS DE COMPONENTES PASIVOS', 28, fill=(170, 255, 200)), PCB_C[0], 310, scale=a)
    if t >= Pc['mag']:
        u = S.ease_back(S.seg(t, Pc['mag'], Pc['mag'] + 0.4))
        x = MAG_C[0] + 200 * (1 - u); y = MAG_C[1] + 160 * (1 - u)
        S.paste_center(cv, D.magnifier(mag_content(), r=150), x, y, scale=u)
        a2 = S.seg(t, Pc['mag'] + 0.3, Pc['mag'] + 0.6)
        S.paste_center(cv, D.label('resistencia de chip', 22, fill=(220, 230, 240)), MAG_C[0] - 20, MAG_C[1] + 175, alpha=a2)
    if t >= Pc['size']:
        a = S.ease_back(S.seg(t, Pc['size'], Pc['size'] + 0.3))
        S.paste_center(cv, D.label('existen de 0,4 × 0,2 mm (tamaño 01005)', 24, fill=(255, 230, 140)), PCB_C[0], 835, scale=a)


# ======================= escena F: remate (circuito que funciona) =======================
Fn = {}
def setup_F():
    Fn['in'] = P(11) - 0.05
    Fn['pat'] = KW(11, 'LIMITA') - 0.1
    Fn['rip'] = KW(11, 'salvó') - 0.1
    ev(Fn['in'], 'block', 0.5, 0.2); ev(Fn['in'] + 0.25, 'zap', 0.3, panx(LED_C[0]))
    for k in range(2):
        ev(Fn['pat'] + 0.12 + k * 0.22, 'tink', 0.3, panx(RES_C[0]), f=2000)
    ev(Fn['rip'], 'pop', 0.4, panx(SHELF_LED[0]))
    add_slap(T_F_SLAP)

def draw_F(cv, t, at=None):
    if t < Fn['in'] or t > T_F_SLAP + 1.0:
        return
    if t >= T_F_SLAP and at is None:
        shattered(cv, draw_F, T_F_SLAP, t, 13)
        return
    k = S.ease_back(S.seg(t, Fn['in'], Fn['in'] + 0.35))
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_wires(tmp, t, True)
    flow_layer(tmp, t, S.seg(t, Fn['in'] + 0.25, Fn['in'] + 0.5))
    S.paste_center(tmp, R.supply('5,00', '0.01'), SUP[0], SUP[1], scale=SUP_SC)
    lv = S.seg(t, Fn['in'] + 0.25, Fn['in'] + 0.35)
    if lv > 0:
        S.glow_fast(tmp, LED_C[0], LED_C[1] - 60, 150, (255, 70, 60), 0.6 * lv)
    S.paste_center(tmp, R.led(round(lv, 1), 0.0, LED_H), LED_C[0], LED_C[1])
    sq = 1 + 0.12 * S.jelly(t - Fn['pat'] - 0.15, 4, 5) if t >= Fn['pat'] + 0.15 else 1.0
    S.paste_center(tmp, R.resistor(RES_W), RES_C[0], RES_C[1], sx=sq, sy=2 - sq)
    if t >= Fn['pat']:
        a = S.ease_back(S.seg(t, Fn['pat'], Fn['pat'] + 0.3))
        S.paste_center(tmp, D.label('LIMITA LA CORRIENTE', 34, fill=(170, 255, 190)), 695, 340, scale=a)
    S.paste_center(cv, tmp, W / 2, H / 2, scale=1.0, alpha=min(1.0, k * 1.2))


# ======================= cierre: botones y reto =======================
Fin = {}
BTN = {'like': (810, 620), 'sub': (810, 755), 'follow': (810, 890)}
Q_C = (380, 430)

def setup_Fin():
    Fin['btn_in'] = P(12) - 0.4
    Fin['hit'] = {'like': KW(12, 'me gusta'), 'sub': KW(12, 'suscríbete'), 'follow': KW(12, 'sígueme')}
    Fin['q'] = KW(12, 'Reto') - 0.1
    Fin['q2'] = KW(12, 'Cuánto') - 0.1
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
    # el reto: resistencia marrón-negro-rojo-dorado
    if Fin['q'] <= t < T_END_SNAP + 0.4:
        out = S.ease_in(S.seg(t, T_END_SNAP + 0.05, T_END_SNAP + 0.35))
        u = S.seg(t, Fin['q'], Fin['q'] + 0.35)
        x = Q_C[0] - 500 * (1 - S.ease_out(u))
        k = (1 - out)
        S.paste_center(cv, R.resistor(200, R.B1K), x, Q_C[1], scale=k, angle=-0.6 * (1 - u) + 0.04 * math.sin((t - Fin['q']) * 5))
        S.paste_center(cv, D.label('RETO', 28, fill=(255, 220, 120)), Q_C[0], Q_C[1] - 75, scale=S.ease_back(S.seg(t, Fin['q'] + 0.2, Fin['q'] + 0.5)) * k)
        if t >= Fin['q2']:
            a = S.ease_back(S.seg(t, Fin['q2'], Fin['q2'] + 0.3)) * k
            S.paste_center(cv, S.fancy_text('¿CUÁNTO VALE?', 52), Q_C[0], Q_C[1] + 95, scale=a * (1 + 0.04 * math.sin(t * 6)))
        if t >= Fin['q3']:
            a = S.ease_back(S.seg(t, Fin['q3'], Fin['q3'] + 0.3)) * k
            S.paste_center(cv, D.label('RESPÓNDEME', 26, fill=(255, 255, 255)), Q_C[0], Q_C[1] + 165, scale=a)
            S.paste_center(cv, D.label('EN LOS COMENTARIOS', 22, fill=(255, 255, 255)), Q_C[0], Q_C[1] + 212, scale=a)


GEST = [
    (KW(2, 'LIMITA') + 0.3, 0.9, 'present'),
    (KW(3, 'Fuente'), 1.0, 'present'),
    (P(4) + 0.1, 1.1, 'count'),
    (KW(6, 'chocan'), 1.1, 'present'),
    (KW(6, 'calor'), 0.7, 'open'),
    (P(8) + 0.1, 1.0, 'present'),
    (KW(8, 'tolerancia'), 0.8, 'count'),
    (P(9) + 0.05, 1.6, 'present'),
    (KW(10, 'celular'), 0.9, 'open'),
    (KW(10, 'RESISTENCIAS'), 0.8, 'present'),
    (KW(11, 'LIMITA'), 1.0, 'present'),
    (KW(12, 'Cuánto'), 0.8, 'chin'),
]


def setup_all():
    setup_walks()
    schedule_build_sfx()
    setup_title()
    setup_C()
    setup_J()
    setup_T()
    setup_K()
    setup_P()
    setup_F()
    setup_Fin()
    react = [
        (T_POP + 0.02, 0.4, 55, None),                     # ¡pop!
        (KW(0, 'RESISTENCIA') - 0.05, 0.7, 100, 'spin'),   # título
        (Cc['on'] + 0.05, 0.45, 70, 'thumbs'),             # ¡prende!
        (Cc['stack'] + 0.05, 0.4, 50, 'up'),               # ¡le tocan tres!
        (Cc['ma'] + 0.05, 0.4, 45, None),                  # 9 mA
        (Jj['joule'] + 0.05, 0.45, 60, 'up'),              # efecto Joule
        (Tt['land'] + 0.02, 0.4, 60, None),                # cae la tostadora
        (Kk['res'] + 0.05, 0.45, 70, 'up'),                # ¡330!
        (Pc['many'] + 0.05, 0.35, 40, None),               # cientos
        (Fn['rip'] + 0.05, 0.45, 60, 'thumbs'),            # ¡lo salvó!
    ]
    for t0, d, h, kind in react:
        if h > 0:
            JUMPS.append((t0, d, h))
            ev(t0 + d, 'step', 0.45, 0.0, heavy=0.9)
        if kind == 'spin':
            SPINS.append((t0, d)); ev(t0, 'whoosh', 0.3, 0.0)
        if kind:
            REACT_ARMS.append((t0, d, kind))


def build_bg(t):
    """construcción del laboratorio: piso primero, luego las paredes fila por fila de abajo hacia arriba,
    y al final caen los muebles"""
    L = LB.layers()
    bare = L['bare']
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    rows = [S.FLOOR_T] + S.WALL_ROWS[::-1]
    for ri, y in enumerate(rows):
        hgt = S.BLK if y != S.FLOOR_T else S.FLOOR_B - S.FLOOR_T
        for c in range(S.NCOL):
            x = S.X0 + c * S.BLK
            ta = T_BUILD + ri * 0.05 + abs(x + S.BLK / 2 - INTRO_X) / 3500
            p = (t - ta) / 0.14
            if p <= 0:
                continue
            tile = bare.crop((x, y, x + S.BLK, y + hgt))
            if p >= 1:
                out.paste(tile, (x, y))
                continue
            sc = max(0.05, S.ease_back(p))
            tw, th = max(1, int(S.BLK * sc)), max(1, int(hgt * sc))
            out.paste(tile.resize((tw, th)), (x + (S.BLK - tw) // 2, y + (hgt - th) // 2 - int(30 * (1 - p))))
    tf = T_BUILD + 0.85
    for name, delay, dy0 in (('shelf', 0.0, -420), ('counter', 0.08, 300), ('items', 0.18, -160)):
        u = (t - tf - delay) / 0.3
        if u <= 0:
            continue
        lay = L[name]
        if u >= 1:
            out.alpha_composite(lay)
            continue
        v = S.bounce_out(u)
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        tmp.paste(lay, (0, int(dy0 * (1 - v))))
        out.alpha_composite(tmp)
    return out


def schedule_build_sfx():
    ev(T_SNAP, 'snap', 0.9, panx(INTRO_X))
    ev(T_BUILD, 'whoosh', 0.45, 0.0)
    for ri in range(1 + len(S.WALL_ROWS)):
        ev(T_BUILD + ri * 0.05 + 0.08, 'block', 0.26, -0.6 + 1.2 * ((ri * 7) % 10) / 10, pitch=0.85 + 0.03 * ri)
    tf = T_BUILD + 0.85
    ev(tf + 0.3, 'thud', 0.6, -0.5); ev(tf + 0.38, 'thud', 0.6, 0.1); ev(tf + 0.48, 'block', 0.4, 0.3, pitch=1.2)
    ev(T_LIT, 'switch', 0.55, 0.0); ev(T_LIT + 0.05, 'chime', 0.4, 0.0)


_bg = {}
def bg_at(t, light):
    if t < T_LIT:
        if t < T_BUILD:
            return Image.new('RGBA', (W, H), (0, 0, 0, 255))
        return build_bg(t)
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
    if t < T_BUILD:
        # a oscuras: solo se ve lo que alumbra la pantalla de la fuente (y el LED)
        S.glow_fast(cv, SUP[0], SUP[1], 260, (60, 160, 90), 0.35)
    if t >= T_LIT:
        LB.draw_anim(cv, t, light)
    sw = 0.0
    if t >= T_END_SNAP:
        sw = 0.04 * math.sin((t - T_END_SNAP) * 5) * math.exp(-(t - T_END_SNAP))
    for t0 in (T_LIT, Tt['land']):
        if t0 <= t < t0 + 1.4:
            sw += 0.06 * math.sin((t - t0) * 7) * math.exp(-(t - t0) * 2.5)
    S.draw_lamp(cv, on=light, swing=sw)
    if light > 0.05:
        S.glow_fast(cv, S.LAMP_X + math.sin(sw) * S.LAMP_Y, math.cos(sw) * S.LAMP_Y + 22, 90, (255, 230, 150), 0.6 * light)
    if t >= T_TITLE_FLY + 0.4 and t < T_END_SNAP + 0.1:
        S.draw_label(cv, LABEL_TXT, alpha=S.seg(t, T_TITLE_FLY + 0.4, T_TITLE_FLY + 0.6) * light)
    draw_shelf_led(cv, t)
    # ----- escenas -----
    draw_C(cv, t)
    draw_J(cv, t)
    draw_T(cv, t)
    draw_K(cv, t)
    draw_P(cv, t)
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
    if t < T_LIT:
        char_light = 0.5 if t < T_BUILD else 0.5 + 0.4 * S.seg(t, T_BUILD, T_LIT)
        if T_POP <= t < T_POP + 0.4:
            char_light = max(char_light, 1.0 - (t - T_POP) / 0.4 * 0.5)
    CH.render(cv, pose, dict(scale=S.SCALE, ox=x, oy=yf, view_yaw=0.12 * math.sin(t * 0.2)), light=char_light, t=t)
    draw_show_res(cv, t)
    draw_Fin(cv, t)
    # destello del ¡pop!
    if T_POP <= t < T_POP + 0.35:
        u = (t - T_POP) / 0.35
        S.glow_fast(cv, LED_C[0], LED_C[1] - 70, 520, (255, 235, 200), 0.9 * (1 - u) ** 2)
    sub, si = TL.subtitle_at(t)
    if sub and t < T_END_SNAP + 0.2:
        S.draw_subtitle(cv, sub)
    # ----- temblor -----
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
