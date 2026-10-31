#!/usr/bin/env python3
# Capítulo 3: ¿La gravedad es un componente? -> El sensor de inclinación
# Vertical 1080x1920, 30 fps. El personaje HieloEterno construye todo.
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
import char3d as C
from timeline import TL, PHRASES

W, H = S.W, S.H
FPS = S.FPS
CH = C.Character()
HOME_X = 230          # posición habitual del personaje (pantalla)
LABEL_TXT = 'CAP. 3 · SENSOR DE INCLINACIÓN'

# ======================= tiempos clave =======================
t_ = TL
P = lambda i: TL.s(i)
E = lambda i: TL.e(i)
KW = TL.kw

T_SNAP = E(2) + 0.45
T_LIGHT = T_SNAP + 1.35          # la lámpara termina de prender
WALK1 = (P(3) - 0.1, P(3) + 1.0)  # camina del centro a la izquierda
T_PLANET_SLAP = E(5) + 0.35
T_TITLE_FLY = E(7) + 0.25
T_A_SLAP = E(11) + 0.3
T_B_SLAP = E(15) + 0.3
T_C_SLAP = E(16) + 0.55
T_D_SLAP = E(20) + 0.55
T_END_SNAP = E(23) + 0.5
T_END = TL.END

# ======================= utilidades =======================
def sfx_events():
    return EVENTS

EVENTS = []   # (t, nombre, gain, pan, kwargs)
def ev(t, name, gain=1.0, pan=0.0, **kw):
    EVENTS.append((t, name, gain, pan, kw))

def panx(x):
    return max(-0.8, min(0.8, (x - W / 2) / (W / 2) * 0.8))


# ======================= voz (envolvente para la boca) =======================
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
    (0.0, 'curioso'), (P(1), 'feliz'), (P(2), 'guino'), (T_SNAP, 'sorpresa'), (T_SNAP + 0.75, 'feliz'),
    (P(3), 'curioso'), (P(4), 'pensando'), (KW(4, 'masa'), 'sorpresa'), (KW(4, 'atrae'), 'feliz'),
    (P(5), 'curioso'), (KW(5, 'jala'), 'sorpresa'), (KW(5, 'por eso'), 'feliz'), (E(5), 'guino'),
    (P(6), 'pensando'), (KW(6, 'aunque'), 'feliz'), (P(7), 'feliz'),
    (P(8), 'feliz'), (KW(8, 'bolita'), 'curioso'), (KW(8, 'patitas'), 'feliz'), (P(9), 'curioso'), (P(10), 'sorpresa'), (P(10) + 0.5, 'feliz'), (P(11), 'pensando'), (KW(11, 'corta'), 'sorpresa'), (E(11), 'guino'),
    (P(12), 'feliz'), (P(13), 'curioso'), (KW(13, 'prende'), 'feliz'), (P(14), 'guino'), (P(15), 'feliz'),
    (P(16), 'feliz'), (KW(16, 'tilt'), 'sorpresa'), (KW(16, 'calentadores'), 'feliz'), (P(17), 'sorpresa'), (KW(17, 'primo'), 'feliz'), (P(18), 'curioso'), (P(19), 'pensando'), (KW(19, 'tres'), 'feliz'),
    (P(20), 'curioso'), (KW(20, 'gira'), 'corazon'), (P(21), 'corazon'), (P(22), 'feliz'), (P(23), 'feliz'),
    (KW(23, 'nos vemos'), 'guino'), (T_END_SNAP + 0.3, 'feliz'), (T_END_SNAP + 0.75, 'apagado'),
]

def expr_at(t):
    e = 'normal'
    for tt, x in EXPR:
        if t >= tt:
            e = x
    return e

def blink_at(t):
    # parpadeo cada ~3.3 s
    ph = (t + 0.7) % 3.3
    if ph < 0.12:
        return math.sin(ph / 0.12 * math.pi)
    return 0.0


# ======================= posición y caminatas =======================
WALKS = [(WALK1[0], WALK1[1], 540, HOME_X)]
FAR_X = 500
WALK_PLAN = []   # (t_inicio, x_destino, duración) se llena en setup_walks()

def setup_walks():
    plan = [
        (P(4) + 0.1, FAR_X, 1.3), (P(5) + 0.2, HOME_X, 1.3),
        (P(8) - 0.2, 330, 0.9), (P(9) - 0.1, HOME_X, 0.9),
        (P(11) + 0.1, FAR_X, 1.2), (P(12) - 0.1, HOME_X, 1.1),
        (P(16) + 0.1, FAR_X, 1.4), (P(17) + 0.2, HOME_X, 1.2),
        (P(18) + 0.1, 340, 1.5), (P(19) + 0.3, HOME_X, 1.3),
        (P(21) + 0.1, 300, 1.0),
    ]
    x = HOME_X
    for t0, x1, d in plan:
        WALKS.append((t0, t0 + d, x, x1))
        n = max(2, int(abs(x1 - x) / 70))
        for k in range(n):
            ev(t0 + 0.12 + k * (d - 0.24) / max(1, n - 1), 'step', 0.4, panx(x + (x1 - x) * k / max(1, n - 1)), heavy=0.75)
        x = x1

def pos_x(t):
    x = 540
    for a, b, x0, x1 in WALKS:
        if t >= b:
            x = x1
        elif t >= a:
            u = S.ease_io((t - a) / (b - a))
            x = x0 + (x1 - x0) * u
            return x, (a, b, x0, x1)
    return x, None


# ======================= saltos =======================
JUMPS = []   # (t0, dur, alto px)

SPINS = []   # (t0, dur)

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
    """mezcla el brazo actual con el de target_pose (k 0..1)"""
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


# Lanzamientos: (t0, lado) -> gesto de lanzar
THROW_GESTURES = []   # (t_release, side)
SLAPS = []            # (t, side)
POINTS = []           # (t0, t1, side, target)

def arm_window(pose, t, x, yf):
    """aplica gestos de brazos programados"""
    # señalar / alcanzar objetivos
    for t0, t1, side, target in POINTS:
        if t0 - 0.25 <= t <= t1 + 0.3:
            k = S.ease_out(S.seg(t, t0 - 0.25, t0)) * (1 - S.ease_io(S.seg(t, t1, t1 + 0.3)))
            tp = pose.copy()
            tgt = target(t) if callable(target) else target
            aim(tp, side, shoulder_screen(x, yf, side, pose.sx, pose.sy), tgt)
            # temblor de goma al estirarse
            wob = S.jelly(t - t0, 4, 5) * 0.12
            if side == 'l':
                tp.larm = (tp.larm[0], tp.larm[1], tp.larm[2] + wob)
            else:
                tp.rarm = (tp.rarm[0], tp.rarm[1], tp.rarm[2] + wob)
            blend_arm(pose, side, tp, k)
    for tr, side in THROW_GESTURES:
        if tr - 0.3 <= t <= tr + 0.3:
            if t < tr - 0.12:          # anticipación: brazo atrás
                u = S.seg(t, tr - 0.3, tr - 0.12)
                tp = pose.copy(); a = (-0.9 * S.ease_out(u), 0, 0.3)
            elif t < tr + 0.05:        # golpe hacia adelante-arriba
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


# ======================= estado del personaje =======================
def char_state(t):
    """devuelve (pose, x_pantalla, y_pies, luz, glow)"""
    p = C.Pose()
    p.expr = expr_at(t)
    p.blink = blink_at(t) if p.expr in ('normal', 'curioso', 'hablando') else 0.0
    p.mouth = mouth_at(t)
    x, walking = pos_x(t)
    yf = S.FLOOR_Y
    # respiración
    br = math.sin(t * 2.2)
    p.sy *= 1 + 0.008 * br; p.sx *= 1 - 0.004 * br
    p.head = (0.04 * math.sin(t * 1.3), 0.08 * math.sin(t * 0.7), 0.03 * math.sin(t * 1.1))
    p.rarm = (0.05, 0, 0.08 + 0.03 * br); p.larm = (0.05, 0, 0.08 + 0.03 * br)
    p.relbow = 0.15; p.lelbow = 0.15
    # mirar los diagramas mientras explica
    look_diag = diagram_active(t)
    if look_diag and t > T_LIGHT:
        ph = (t * 0.45) % 1.0
        k = 1.0 if ph < 0.6 else 0.0
        k = S.ease_io(S.clamp((ph / 0.08) if ph < 0.3 else (0.6 - ph) / 0.08 if ph < 0.6 else 0))
        p.head = (p.head[0] - 0.12 * k, p.head[1] + 0.45 * k, p.head[2])
        p.look = (1.0 * k, -0.6 * k)
        p.lean += 0.08 * k
    # hablando: gestos grandes con los dos brazos, la cabeza asiente con las sílabas
    si = speaking(t)
    if si is not None and walking is None:
        env = mouth_at(t)
        g1 = math.sin(t * 3.4 + si * 1.7); g2 = math.sin(t * 2.6 + si * 0.9 + 1.3)
        amp = 0.45 + 0.45 * env
        p.larm = (0.55 + 0.55 * g1 * amp, 0.15 * g2, 0.25 + 0.35 * max(0, g2) * amp); p.lelbow = 0.9 + 0.5 * g1
        p.rarm = (0.45 + 0.5 * g2 * amp, -0.15 * g1, 0.25 + 0.35 * max(0, g1) * amp); p.relbow = 0.9 + 0.5 * g2
        p.head = (p.head[0] + 0.14 * env * math.sin(t * 9), p.head[1] + 0.1 * g2, p.head[2] + 0.07 * g1)
        yf -= 3 * env
        p.sy *= 1 + 0.015 * env
        p.lean += 0.06 * g1
    # ---------- intro: flotando sin gravedad ----------
    if t < T_SNAP + 0.05:
        float_y = 200 + 18 * math.sin(t * 1.4)
        yf = S.FLOOR_Y - float_y
        p.body_roll = 0.18 * math.sin(t * 0.9)
        p.body_pitch = 0.1 * math.sin(t * 0.7)
        ph = t * 1.6
        p.rknee = 0.6 + 0.5 * math.sin(ph * 2 * math.pi); p.lknee = 0.6 - 0.5 * math.sin(ph * 2 * math.pi)
        p.rleg = (0.3 + 0.3 * math.sin(ph * 2 * math.pi), 0, 0.05); p.lleg = (0.3 - 0.3 * math.sin(ph * 2 * math.pi), 0, 0.05)
        p.rarm = (0.2, 0, 0.9 + 0.35 * math.sin(t * 3)); p.larm = (0.2, 0, 0.9 + 0.35 * math.sin(t * 3 + 1))
        p.relbow = 0.4; p.lelbow = 0.4
        p.look = (0.0, -1.0)
        if P(1) <= t < P(2):    # se ríe
            sh = math.sin(t * 30) * 0.05
            p.head = (-0.25 + sh, 0, 0.1); p.lean = -0.1 + sh
            p.rarm = (0.9, 0, 0.2); p.larm = (0.9, 0, 0.2); p.relbow = 1.4; p.lelbow = 1.4
        if P(2) <= t < T_SNAP - 0.35:    # se frota las manos
            u = math.sin(t * 22)
            p.rarm = (1.0, 0.25 * u, 0.35); p.larm = (1.0, -0.25 * u, 0.35)
            p.relbow = 1.3; p.lelbow = 1.3
            p.sy *= 0.96; p.sx *= 1.03
        if T_SNAP - 0.35 <= t:             # brazo arriba y chasquido
            u = S.ease_out(S.seg(t, T_SNAP - 0.35, T_SNAP - 0.05))
            p.larm = (0.0, 0, 0.9 + 1.9 * u); p.lelbow = 0.6 * (1 - u); p.larm_len = 1 + 0.25 * u
            p.look = (0.5, -1)
    # ---------- caída y aterrizaje ----------
    elif t < T_SNAP + 1.2:
        tf = t - T_SNAP
        h0 = 200 + 18 * math.sin(T_SNAP * 1.4)
        tfall = math.sqrt(2 * h0 / 4200)
        if tf < tfall:
            yf = S.FLOOR_Y - (h0 - 0.5 * 4200 * tf * tf)
            p.rarm = (0.3, 0, 2.6); p.larm = (0.3, 0, 2.6); p.relbow = 0.2; p.lelbow = 0.2
            p.rarm_len = 1.2; p.larm_len = 1.2
            p.rleg = (0.4, 0, 0.1); p.lleg = (-0.2, 0, 0.1); p.rknee = 0.8; p.lknee = 0.5
            p.sy *= 1.12; p.sx *= 0.92
            p.body_roll = 0.18 * math.sin(T_SNAP * 0.9) * (1 - tf / tfall)
        else:
            tl = tf - tfall
            j = S.jelly(tl, 3.5, 5.0)
            p.sy *= 1 - 0.22 * j; p.sx *= 1 + 0.16 * j
            if tl < 0.18:
                p.rknee = 0.9; p.lknee = 0.9; p.rleg = (0.45, 0, 0.1); p.lleg = (0.45, 0, 0.1)
                yf = S.FLOOR_Y + 0
            p.rarm = (0.2, 0, 0.9 * math.exp(-tl * 4)); p.larm = (0.2, 0, 0.9 * math.exp(-tl * 4))
    # ---------- caminata ----------
    if walking is not None:
        a, b, x0, x1 = walking
        dist = abs(x - x0)
        phase = dist / 210.0
        amt = S.clamp(min((t - a) / 0.15, (b - t) / 0.15))
        C.walk_pose(p, phase, amt)
        d = -1 if x1 < x0 else 1
        p.yaw = d * 0.85 * S.clamp(min((t - a) / 0.2, (b - t) / 0.2))
        p.look = (d * 1.0, 0)
    # salto
    jy, ju = jump_at(t)
    if ju is not None:
        yf -= jy
        if ju < 0.12:
            p.sy *= 0.9; p.sx *= 1.06
        else:
            p.sy *= 1.06; p.sx *= 0.96
        p.rknee = 0.5 * math.sin(ju * math.pi); p.lknee = 0.5 * math.sin(ju * math.pi)
    p.yaw += spin_at(t)
    # gestos especiales por escena
    scene_gestures(p, t, x, yf)
    arm_window(p, t, x, yf)
    light = light_at(t)
    glow = 1.0 - light if light < 0.95 else 0.0
    if t >= T_END_SNAP + 0.75:
        glow = 0.0
    return p, x, yf, light, glow


def diagram_active(t):
    if 'click' not in A:
        return False
    return (KW(4, 'fuerza') <= t < T_PLANET_SLAP) or (A['t_tube'] + 0.4 <= t < T_A_SLAP) or (B['t_sens'] + 0.4 <= t < T_B_SLAP) \
        or (KW(16, 'alarmas') <= t < T_C_SLAP) or (PC['t_phone'] + 0.4 <= t < T_D_SLAP)


def scene_gestures(p, t, x, yf):
    for t0, d, kind in REACT_ARMS:
        if t0 - 0.1 <= t <= t0 + d + 0.15:
            k = S.seg(t, t0 - 0.1, t0 + 0.05) * (1 - S.seg(t, t0 + d, t0 + d + 0.15))
            tp = p.copy()
            if kind in ('up', 'spin'):
                tp.larm = (0.2, 0, 2.6); tp.rarm = (0.2, 0, 2.6); tp.lelbow = 0.2; tp.relbow = 0.2
                tp.larm_len = 1.15; tp.rarm_len = 1.15
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
            elif kind == 'fist':
                tp.rarm = (0.3, 0, 2.7); tp.relbow = 0.3; tp.rarm_len = 1.2
                blend_arm(p, 'r', tp, k)
            elif kind == 'thumb':
                tp.larm = (1.4, 0, 0.6); tp.lelbow = 1.6
                blend_arm(p, 'l', tp, k)
    # "?" sobre la cabeza y mano en la barbilla: ¿Y qué es la gravedad?
    if WALK1[1] <= t < E(3) + 0.2:
        k = S.seg(t, WALK1[1], WALK1[1] + 0.2) * (1 - S.seg(t, E(3), E(3) + 0.2))
        tp = p.copy(); tp.rarm = (1.9, 0, -0.2); tp.relbow = 2.0
        blend_arm(p, 'r', tp, k)
        p.head = (p.head[0] - 0.1 * k, p.head[1], p.head[2] + 0.15 * k)
    # "¡la gravedad NO es un componente!": dedo que dice que no
    a, b = P(6), KW(6, 'aunque')
    if a <= t < b:
        k = S.seg(t, a, a + 0.2) * (1 - S.seg(t, b - 0.15, b))
        tp = p.copy(); tp.larm = (1.6, 0, 0.35 * math.sin((t - a) * 14)); tp.lelbow = 1.6
        blend_arm(p, 'l', tp, k)
    # "Aunque hay componentes que la sienten": brazos arriba
    a = KW(6, 'aunque')
    if a <= t < E(6) + 0.2:
        k = S.seg(t, a, a + 0.15) * (1 - S.seg(t, E(6), E(6) + 0.2))
        tp = p.copy(); tp.larm = (0.2, 0, 2.5); tp.rarm = (0.2, 0, 2.5); tp.lelbow = 0.2; tp.relbow = 0.2
        blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
    # mímica de inclinar el sensor (circuito): manos al frente y el cuerpo se inclina igual
    if 'tilt0' in B and B['tilt0'] - 0.3 <= t < B['rock1'] + 0.3:
        k = S.seg(t, B['tilt0'] - 0.3, B['tilt0'] - 0.05) * (1 - S.seg(t, B['rock1'], B['rock1'] + 0.3))
        if B['untilt0'] + 0.5 < t < B['rock0'] - 0.25:
            k *= 0.0 if t > B['untilt0'] + 0.8 else 1 - S.seg(t, B['untilt0'] + 0.5, B['untilt0'] + 0.8)
        if B['rock0'] - 0.25 <= t < B['rock0']:
            k = S.seg(t, B['rock0'] - 0.25, B['rock0'])
        a = math.radians(sens_angle(t))
        tp = p.copy()
        tp.larm = (1.5, 0, 0.25); tp.rarm = (1.5, 0, 0.25); tp.lelbow = 0.5; tp.relbow = 0.5
        blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
        p.roll += -a * 0.45 * k
        p.head = (p.head[0], p.head[1], p.head[2] - a * 0.5 * k)
    # risa con el LED de disco
    if P(15) <= t < E(15):
        sh = math.sin(t * 30) * 0.04
        p.head = (-0.2 + sh, p.head[1], p.head[2]); p.lean = -0.06 + sh
    # susurro: inclinado, mano a la boca
    if P(18) <= t < E(18) + 0.1:
        k = S.seg(t, P(18), P(18) + 0.2) * (1 - S.seg(t, E(18) - 0.1, E(18) + 0.1))
        tp = p.copy(); tp.rarm = (1.6, 0, -0.35); tp.relbow = 2.1
        blend_arm(p, 'r', tp, k)
        p.lean += 0.12 * k; p.head = (p.head[0] + 0.1 * k, p.head[1] + 0.3 * k, p.head[2])
    # despedida: agita la mano
    a = KW(23, 'nos vemos') - 0.2
    if a <= t < T_END_SNAP - 0.35:
        k = S.seg(t, a, a + 0.2)
        tp = p.copy(); tp.larm = (0.1, 0, 2.5 + 0.35 * math.sin((t - a) * 13)); tp.lelbow = 0.4; tp.larm_len = 1.2
        blend_arm(p, 'l', tp, k)
    # chasquido final
    if T_END_SNAP - 0.35 <= t < T_END_SNAP + 0.6:
        u = S.ease_out(S.seg(t, T_END_SNAP - 0.35, T_END_SNAP - 0.05)) * (1 - S.seg(t, T_END_SNAP + 0.3, T_END_SNAP + 0.6))
        tp = p.copy(); tp.rarm = (0.3, 0, 2.6); tp.relbow = 0.5
        blend_arm(p, 'r', tp, u)


# ======================= luz =======================
def light_at(t):
    if t < T_SNAP + 0.55:
        return 0.0
    if t < T_LIGHT:
        u = t - (T_SNAP + 0.55)
        # parpadeo dos veces y prende
        seq = [(0.0, 0.0), (0.12, 0.7), (0.2, 0.05), (0.38, 0.85), (0.46, 0.1), (0.62, 0.6), (0.8, 1.0)]
        v = 0.0
        for tt, lv in seq:
            if u >= tt:
                v = lv
        return v
    if t > T_END_SNAP + 0.05:
        return 0.0
    return 1.0


# ======================= objetos de la intro =======================
RNG = random.Random(9)
INTRO_BLOCKS = []
def _init_blocks():
    # piso de madera (todas las columnas) + columnas de piedra a los lados
    for c in range(S.NCOL):
        tx, ty = S.X0 + c * S.BLK, S.FLOOR_T
        INTRO_BLOCKS.append(dict(img=S.FLOOR[c][0], tx=tx, ty=ty, kind='wood'))
    for c in (0, S.NCOL - 1):
        for r in range(1, 4):
            ty = S.FLOOR_T - r * S.BLK
            ri = S.WALL_ROWS.index(ty) if ty in S.WALL_ROWS else None
            if ri is None:
                continue
            idx = ri * S.NCOL + c
            INTRO_BLOCKS.append(dict(img=S.WALL[idx][0], tx=S.WALL[idx][1], ty=S.WALL[idx][2], kind='stone'))
    for b in INTRO_BLOCKS:
        # posición flotando: en la mitad de arriba del cuarto, sin tapar al personaje ni las burbujas
        while True:
            fx = RNG.uniform(60, W - 130); fy = RNG.uniform(330, 1250)
            if not (330 < fx < 760 and 330 < fy < 1300):
                break
        b['fx'] = fx; b['fy'] = fy
        b['ax'] = RNG.uniform(10, 26); b['ay'] = RNG.uniform(10, 26)
        b['w'] = RNG.uniform(0.6, 1.3); b['ph'] = RNG.uniform(0, 6.28)
        b['rot0'] = RNG.uniform(-0.6, 0.6); b['spin'] = RNG.uniform(-0.5, 0.5)
        b['delay'] = RNG.uniform(0.0, 0.45)
        b['scale'] = RNG.uniform(0.75, 1.0)
_init_blocks()

def block_state(b, t):
    """(x, y, ang, scale, landed) en esquina sup-izq del bloque"""
    if t < T_SNAP:
        x = b['fx'] + b['ax'] * math.sin(t * b['w'] + b['ph'])
        y = b['fy'] + b['ay'] * math.cos(t * b['w'] * 0.8 + b['ph'])
        return x, y, b['rot0'] + b['spin'] * t, b['scale'], False
    t0 = T_SNAP + b['delay']
    x0 = b['fx'] + b['ax'] * math.sin(T_SNAP * b['w'] + b['ph'])
    y0 = b['fy'] + b['ay'] * math.cos(T_SNAP * b['w'] * 0.8 + b['ph'])
    a0 = b['rot0'] + b['spin'] * T_SNAP
    if t < t0:
        tt = t - T_SNAP
        return x0, y0 - 6 * math.sin(tt * 20), a0, b['scale'], False
    g = 4200.0
    dy = b['ty'] - y0
    if dy <= 0:
        dy = 1
    tfall = math.sqrt(2 * dy / g)
    u = t - t0
    if u < tfall:
        k = u / tfall
        x = x0 + (b['tx'] - x0) * S.ease_io(k)
        y = y0 + 0.5 * g * u * u
        return x, y, a0 * (1 - k), b['scale'] + (1 - b['scale']) * k, False
    v = u - tfall
    bump = 14 * math.exp(-v * 9) * abs(math.sin(v * 22))
    return b['tx'], b['ty'] - bump, 0.0, 1.0, True

def block_land_time(b):
    x0 = b['fx'] + b['ax'] * math.sin(T_SNAP * b['w'] + b['ph'])
    y0 = b['fy'] + b['ay'] * math.cos(T_SNAP * b['w'] * 0.8 + b['ph'])
    dy = max(1, b['ty'] - y0)
    return T_SNAP + b['delay'] + math.sqrt(2 * dy / 4200.0)

# lámpara: flota y luego cae a su sitio colgando
LAMP_FLOAT = (820, 420)
def lamp_state(t):
    """(x, y_bombillo, on) – y_off relativo a la posición colgada"""
    if t < T_SNAP + 0.1:
        return LAMP_FLOAT[0] + 20 * math.sin(t * 0.8), LAMP_FLOAT[1] + 15 * math.cos(t * 1.1), 0.2 * math.sin(t * 0.6), False
    u = t - (T_SNAP + 0.1)
    # se desliza a su sitio (como si el cable la recogiera) y rebota
    k = S.ease_in(S.clamp(u / 0.35))
    x = LAMP_FLOAT[0] + (S.LAMP_X - LAMP_FLOAT[0]) * k
    y = LAMP_FLOAT[1] + (S.LAMP_Y - LAMP_FLOAT[1]) * k
    sw = 0.0
    if u > 0.35:
        v = u - 0.35
        y = S.LAMP_Y + 26 * S.jelly(v, 2.5, 4.0)
        sw = 0.12 * S.jelly(v, 0.9, 1.6)
    return x, y, sw, u > 0.35


# ======================= capas de diagramas por escena =======================
TUBE_C = (560, 590)    # pivote del tubo (centro) en pantalla

def tube_place(layer_img, ang, scale=1.0, piv=(D.TCX, D.TCY), center=TUBE_C):
    im, off = D.rotated_about(layer_img, piv, ang, scale)
    return im, (int(center[0] + off[0]), int(center[1] + off[1]))


THROWS = []   # dict(t0, dur, target, img_fn, side, arc, spin)

def add_throw(t0, target, img_fn, side='l', dur=0.45, arc=180, spin=1.0, land_sfx='block', pitch=1.0):
    THROWS.append(dict(t0=t0, dur=dur, target=target, img_fn=img_fn, side=side, arc=arc, spin=spin))
    THROW_GESTURES.append((t0, side))
    ev(t0, 'whoosh', 0.35, panx(target[0]))
    if land_sfx == 'block':
        ev(t0 + dur, 'block', 0.55, panx(target[0]), pitch=pitch)
    elif land_sfx == 'pop':
        ev(t0 + dur, 'pop', 0.5, panx(target[0]))

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
    """None si no ha salido; ('fly', x, y, ang, sc) en vuelo; ('land', sx, sy) aterrizado"""
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

def draw_thrown(canvas, th, t, place_fn):
    """place_fn(canvas, sx, sy) dibuja el objeto ya aterrizado con aplaste."""
    st = throw_state(th, t)
    if st is None:
        return
    if st[0] == 'fly':
        img = th['img_fn'](t)
        S.paste_center(canvas, img, st[1], st[2], scale=st[4], angle=st[3])
        # estela
        S.speed_lines(canvas, st[1] - 30, st[2] + 20, st[1] - 120, st[2] + 60, n=3, color=(255, 255, 255, 90), width=3, seed=int(th['t0'] * 10))
    else:
        place_fn(canvas, st[1], st[2])


# --------- burbujas de comentario ---------
BUB1 = (520, 330); BUB2 = (560, 490)
_bub_cache = {}
def bubble(i):
    if i not in _bub_cache:
        _bub_cache[i] = D.comment_bubble('La gravedad?' if i == 1 else 'No sé si es un componente', width=560 if i == 1 else 640)
    return _bub_cache[i]


# ======================= sonidos por eventos de la intro =======================
def schedule_intro_sfx():
    ev(0.0, 'drone', 0.9, 0.0, dur=T_SNAP + 0.3)
    ev(P(0) + 0.1, 'pop', 0.5, 0.0)
    ev(P(1) + 0.2, 'pop', 0.5, 0.05)
    ev(T_SNAP, 'snap', 1.0, 0.25)
    ev(T_SNAP + 0.02, 'thud', 0.5, 0.0)
    for b in INTRO_BLOCKS:
        tl = block_land_time(b)
        ev(tl, 'block', 0.35 if b['kind'] == 'wood' else 0.4, panx(b['tx'] + 36), pitch=0.8 if b['kind'] == 'wood' else 1.1)
    h0 = 200 + 18 * math.sin(T_SNAP * 1.4)
    ev(T_SNAP + math.sqrt(2 * h0 / 4200), 'step', 1.0, 0.0, heavy=1.4)
    ev(T_SNAP + 0.45, 'tink', 0.35, 0.0, f=2400)    # la lámpara llega
    for tt in (0.12, 0.38, 0.62):
        ev(T_SNAP + 0.55 + tt, 'switch', 0.35, 0.0)
    ev(T_SNAP + 0.55 + 0.8, 'zap', 0.4, 0.0)
    ev(T_SNAP + 0.1, 'pop', 0.3, -0.2)
    ev(T_SNAP + 0.15, 'pop', 0.3, 0.2)


# ======================= escena: gravedad =======================
PLANET_C = (600, 560)
ATTR_C = (600, 560)

def setup_gravity():
    # pasos de la caminata
    a, b = WALK1
    n = 5
    for k in range(n):
        ev(a + 0.1 + k * (b - a - 0.2) / (n - 1), 'step', 0.5, panx(540 - (540 - HOME_X) * k / (n - 1)), heavy=0.8)
    ev(WALK1[1] + 0.05, 'boing', 0.3, panx(HOME_X))   # aparece "?"
    # dos bloques que se atraen
    add_throw(KW(4, 'fuerza'), (ATTR_C[0] - 300, ATTR_C[1]), lambda t: D.stone_cube(170, (140, 150, 170)), 'l')
    add_throw(KW(4, 'masa'), (ATTR_C[0] + 300, ATTR_C[1]), lambda t: D.stone_cube(130, (190, 130, 90)), 'l')
    ev(KW(4, 'atrae'), 'whoosh', 0.25, 0.0)
    ev(E(4) + 0.05, 'block', 0.5, 0.0, pitch=1.3)
    # el planeta reemplaza a los bloques
    add_throw(P(5) + 0.05, PLANET_C, lambda t: D.planet_img(195), 'l', dur=0.5, arc=220, land_sfx='block', pitch=0.6)
    for i in range(4):
        ev(KW(5, 'nos jala') + i * 0.12, 'pop', 0.3, (i - 1.5) * 0.3)
    # suelta un bloque que cae
    ev(KW(5, 'cosas') + 0.35, 'thud', 0.8, panx(HOME_X + 120))
    SLAPS.append((T_PLANET_SLAP, 'l'))
    ev(T_PLANET_SLAP, 'whoosh', 0.5, 0.2); ev(T_PLANET_SLAP + 0.05, 'crumble', 0.6, 0.2)


def draw_gravity(cv, t):
    if t < P(4) - 0.3 or t > T_PLANET_SLAP + 1.2:
        return
    # -- dos bloques que se atraen (frase 4) --
    t_att0 = KW(4, 'atrae')
    if t < P(5) + 0.2:
        out_k = S.seg(t, P(5) - 0.05, P(5) + 0.2)
        if out_k < 1:
            th1, th2 = THROWS_G['b1'], THROWS_G['b2']
            gap_k = S.ease_in(S.seg(t, t_att0, E(4) + 0.05))
            x1 = ATTR_C[0] - 300 + 145 * gap_k
            x2 = ATTR_C[0] + 300 - 140 * gap_k
            def place1(c, sx, sy, x1=x1):
                S.paste_center(c, D.stone_cube(170, (140, 150, 170)), x1, ATTR_C[1], sx=sx, sy=sy, alpha=1 - out_k)
            def place2(c, sx, sy, x2=x2):
                S.paste_center(c, D.stone_cube(130, (190, 130, 90)), x2, ATTR_C[1], sx=sx, sy=sy, alpha=1 - out_k)
            draw_thrown(cv, th1, t, place1)
            draw_thrown(cv, th2, t, place2)
            if t >= t_att0 and t < E(4) + 0.05:
                a = S.ease_out(S.seg(t, t_att0, t_att0 + 0.3))
                l = D.L(W, 300)
                D.arrow(l, (x1 + 100, 150), (x1 + 100 + 80 * a, 150), D.GRAV + (255,), 10, 22)
                D.arrow(l, (x2 - 85, 150), (x2 - 85 - 80 * a, 150), D.GRAV + (255,), 10, 22)
                cv.alpha_composite(l.done(), (0, ATTR_C[1] - 150))
            if t >= t_att0 - 0.1:
                a = S.seg(t, t_att0 - 0.1, t_att0 + 0.2) * (1 - out_k)
                lb = D.label('todo lo que tiene MASA se atrae', 36, fill=(255, 220, 120))
                S.paste_center(cv, lb, ATTR_C[0], ATTR_C[1] - 150, alpha=a)
    # -- planeta (frase 5) --
    thp = THROWS_G['planet']
    if t >= thp['t0']:
        if t < T_PLANET_SLAP:
            st = throw_state(thp, t)
            if st[0] == 'fly':
                S.paste_center(cv, D.planet_img(195), st[1], st[2], scale=st[4], angle=st[3])
            else:
                guys = S.seg(t, KW(5, 'nos jala') - 0.1, KW(5, 'nos jala') + 0.5)
                arrows = S.seg(t, KW(5, 'hacia') - 0.1, KW(5, 'hacia') + 0.6)
                lay = D.gravity_planet(t, 1.0, arrows, guys, r=195)
                S.paste_center(cv, lay, PLANET_C[0], PLANET_C[1], sx=st[1], sy=st[2])
                if t > KW(5, 'masa') - 0.1:
                    a = S.seg(t, KW(5, 'masa') - 0.1, KW(5, 'masa') + 0.2)
                    S.paste_center(cv, D.label('TIERRA: muchísima masa', 30, fill=(150, 220, 255)), PLANET_C[0], 250, alpha=a)
        else:
            lay = D.gravity_planet(T_PLANET_SLAP, 1.0, 1.0, 1.0, r=195)
            D.shatter(cv, lay, int(PLANET_C[0] - lay.size[0] / 2), int(PLANET_C[1] - lay.size[1] / 2), t - T_PLANET_SLAP, seed=3, tile=64, push=(400, 0))
    # -- bloque que cae de la mano (por eso las cosas caen) --
    td = KW(5, 'cosas') - 0.05
    if td - 0.4 <= t < td + 1.6:
        hx = HOME_X + 160
        y_top = 960
        if t < td:
            k = S.ease_back(S.seg(t, td - 0.4, td - 0.15))
            S.paste_center(cv, D.stone_cube(70, (120, 200, 120)), hx, y_top, scale=k)
        else:
            u = t - td
            yb = y_top + 0.5 * 4200 * u * u
            ymax = S.FLOOR_Y - 40
            sq = 1.0
            if yb >= ymax:
                v = u - math.sqrt(2 * (ymax - y_top) / 4200)
                yb = ymax - 30 * math.exp(-v * 8) * abs(math.sin(v * 18))
                sq = 1 + 0.2 * S.jelly(v, 3, 6)
            al = 1 - S.seg(t, td + 1.2, td + 1.6)
            S.paste_center(cv, D.stone_cube(70, (120, 200, 120)), hx, yb, sx=sq, sy=2 - sq, alpha=al)
            ga = S.seg(t, td, td + 0.2) * al
            S.paste_center(cv, D.gravity_arrow(140, 1.0, False), hx + 90, 1080, alpha=ga)


THROWS_G = {}

# ======================= escena: título =======================
_title_cache = {}
def title_imgs():
    if not _title_cache:
        _title_cache['a'] = S.fancy_text('CAPÍTULO 3', 92)
        _title_cache['b'] = S.fancy_text('SENSOR DE INCLINACIÓN', 70, top=(140, 230, 255), bot=(40, 120, 255), outline=(10, 30, 70))
        _title_cache['no'] = S.fancy_text('¿COMPONENTE?', 84, top=(255, 255, 255), bot=(200, 200, 210), outline=(40, 40, 50))
        _title_cache['grav'] = S.fancy_text('¡GRAVEDAD ACTIVADA!', 76)
        _title_cache['clic'] = S.fancy_text('¡CLIC!', 80, top=(255, 255, 120), bot=(255, 180, 0))
    return _title_cache

def setup_title():
    ev(P(6) + 0.1, 'pop', 0.5, 0.0)
    ev(KW(6, 'no es') , 'block', 0.6, 0.0, pitch=0.7)  # sello X
    ev(P(7) + 0.05, 'block', 0.5, -0.1, pitch=1.2)
    ev(P(7) + 0.35, 'block', 0.5, 0.1, pitch=1.0)
    ev(T_TITLE_FLY, 'whoosh', 0.4, 0.0)


def draw_title(cv, t):
    TI = title_imgs()
    # ¿COMPONENTE? con X roja (frase 6)
    a0, a1 = P(6), KW(6, 'aunque') + 0.3
    if a0 <= t < a1 + 0.3:
        k = S.ease_back(S.seg(t, a0, a0 + 0.35))
        out = S.seg(t, a1, a1 + 0.3)
        S.paste_center(cv, TI['no'], 600, 520, scale=k * (1 - 0.3 * out), alpha=1 - out)
        tx = KW(6, 'no es')
        if t >= tx:
            u = S.seg(t, tx, tx + 0.2)
            sc = 2.2 - 1.2 * S.ease_out(u)
            l = D.L(300, 300)
            l.line([(40, 40), (260, 260)], (255, 50, 70, 255), 36); l.line([(260, 40), (40, 260)], (255, 50, 70, 255), 36)
            S.paste_center(cv, l.done(), 600, 520, scale=sc * 0.9, alpha=(1 - out) * min(1, u * 3))
    # sensación: "hay componentes que la sienten" -> chispas
    # título
    b0 = P(7) - 0.05
    if b0 <= t < T_TITLE_FLY + 0.5:
        fly = S.ease_in(S.seg(t, T_TITLE_FLY, T_TITLE_FLY + 0.45))
        ka = S.ease_back(S.seg(t, b0, b0 + 0.35)); kb = S.ease_back(S.seg(t, b0 + 0.3, b0 + 0.65))
        ya = 470 + (S.ROOM_T + 46 - 470) * fly; yb = 590 + (S.ROOM_T + 46 - 590) * fly
        sc = 1 - 0.75 * fly
        S.paste_center(cv, TI['a'], 540, ya, scale=ka * sc, alpha=1 - fly * 0.9)
        S.paste_center(cv, TI['b'], 540, yb, scale=kb * sc, alpha=1 - fly * 0.9)


# ======================= escena A: el sensor por dentro =======================
A = {}
def setup_A():
    A['t_tube'] = KW(8, 'tubito') - 0.1
    A['t_ball'] = KW(8, 'bolita') - 0.1
    A['t_cap'] = KW(8, 'patitas') - 0.15
    A['tilt0'] = KW(9, 'inclinas') - 0.25
    A['tilt1'] = A['tilt0'] + 0.6
    A['roll0'] = KW(9, 'hace rodar') - 0.1
    A['click'] = P(10) + 0.02
    A['untilt0'] = KW(11, 'enderezas') - 0.2
    A['untilt1'] = A['untilt0'] + 0.55
    A['roll_back0'] = A['untilt0'] + 0.25
    A['grav'] = KW(9, 'gravedad') - 0.15
    add_throw(A['t_tube'], TUBE_C, lambda t: D.tube_layer(parts=('tube',)), 'l', dur=0.45, arc=150, spin=0.5)
    add_throw(A['t_ball'], (TUBE_C[0] - D.TCX + D.BALL_REST[0], TUBE_C[1] - 220), lambda t: _ball_img(), 'l', dur=0.4, arc=160, land_sfx=None)
    add_throw(A['t_cap'], (TUBE_C[0] - D.TCX + 760, TUBE_C[1]), lambda t: D.tube_layer(parts=('cap',)).crop((520, 40, 900, 240)), 'l', dur=0.45, arc=140, spin=0.5, pitch=1.2)
    # la bolita cae dentro del tubo y rebota
    tb = A['t_ball'] + 0.4
    ev(tb + 0.12, 'tink', 0.45, panx(260), f=3600); ev(tb + 0.3, 'tink', 0.3, panx(260), f=3400)
    ev(A['t_cap'] + 0.6, 'marker', 0.4, 0.2)
    POINTS.append((A['tilt0'], A['untilt1'] - 0.05, 'l', lambda t: _tube_end_screen(t)))
    ev(A['tilt0'], 'whoosh', 0.25, -0.2)
    ev(A['grav'] + 0.25, 'thud', 0.5, panx(120))
    ev(A['roll0'], 'roll', 0.7, 0.0, dur=A['click'] - A['roll0'])
    ev(A['click'], 'click', 0.9, 0.3); ev(A['click'] + 0.03, 'tink', 0.5, 0.3, f=4200)
    ev(A['click'] + 0.4, 'zap', 0.25, 0.3)
    ev(A['roll_back0'], 'roll', 0.5, 0.0, dur=0.8)
    ev(A['roll_back0'] + 0.85, 'block', 0.3, -0.3, pitch=1.6)
    SLAPS.append((T_A_SLAP, 'l'))
    ev(T_A_SLAP, 'whoosh', 0.5, 0.2); ev(T_A_SLAP + 0.05, 'crumble', 0.7, 0.2)

_ball_cache = {}
def _ball_img():
    if 'b' not in _ball_cache:
        l = D.L(100, 100)
        c = (50, 50); R = D.BALL_R
        l.circle(c, R, fill=(150, 156, 164, 255), outline=(90, 95, 100, 255), width=3)
        l.circle((c[0] - 4, c[1] - 4), R - 9, fill=D.SILVER + (255,))
        l.circle((c[0] - 15, c[1] - 16), 9, fill=(255, 255, 255, 255))
        _ball_cache['b'] = l.done()
    return _ball_cache['b']

def tube_angle(t):
    """ángulo en grados (positivo = horario: el lado de las patitas baja)"""
    if t < A['tilt0']:
        return 0.0
    if t < A['untilt0']:
        u = S.seg(t, A['tilt0'], A['tilt1'])
        # anticipación hacia atrás, luego sobreimpulso
        if u < 0.25:
            return -5 * S.ease_out(u / 0.25)
        v = (u - 0.25) / 0.75
        return -5 + 37 * S.ease_back(v, 2.2)
    u = S.seg(t, A['untilt0'], A['untilt1'])
    return 32 * (1 - S.ease_back(u, 1.5))

def ball_local(t):
    """posición y giro de la bolita en coords de la capa del tubo"""
    x0, y0 = D.BALL_REST; x1, y1 = D.BALL_TOUCH
    if t < A['roll0']:
        return x0, y0, 0.0, 0.0
    if t < A['roll_back0']:
        tr = A['click'] - A['roll0']
        u = S.clamp((t - A['roll0']) / tr)
        k = u * u
        x = x0 + (x1 - x0) * k
        y = y0 + (y1 - y0) * S.ease_io(S.seg(k, 0.75, 1.0))
        if t > A['click']:
            v = t - A['click']
            x = x1 - 10 * math.exp(-v * 10) * abs(math.sin(v * 25))
        return x, y, (x - x0) / D.BALL_R, 1.0 if t >= A['click'] else 0.0
    u = S.clamp((t - A['roll_back0']) / 0.85)
    k = 1 - (1 - u) ** 2
    x = x1 + (x0 - x1) * k
    y = y1 + (y0 - y1) * S.ease_io(S.seg(k, 0.0, 0.2))
    if u >= 1:
        v = t - A['roll_back0'] - 0.85
        x = x0 + 6 * math.exp(-v * 9) * abs(math.sin(v * 20))
    return x, y, (x - x0) / D.BALL_R, 0.0

def _tube_end_screen(t):
    ang = math.radians(tube_angle(t))
    p = D.rotate_pt((D.T_X0 + 60, D.TCY - 70), (D.TCX, D.TCY), ang)
    return (TUBE_C[0] - D.TCX + p[0], TUBE_C[1] - D.TCY + p[1])

def tube_composite(t, closed, flash, with_current):
    bx, by, br, _ = ball_local(t)
    lay = D.tube_layer(bx, by, br, closed=closed, flash=flash)
    if with_current > 0:
        l = D.L(D.TUBE_W, D.TUBE_H)
        pts = D.tube_path_points()
        for k in range(6):
            u = (t * 0.55 + k / 6) % 1.0
            p = D.along(pts, u)
            l.rect([p[0] - 8, p[1] - 8, p[0] + 8, p[1] + 8], fill=D.CURR + (int(255 * with_current),))
        lay.alpha_composite(l.done())
    return lay

def draw_A(cv, t):
    if t < A['t_tube'] or t > T_A_SLAP + 1.0:
        return
    closed = S.seg(t, A['click'], A['click'] + 0.15) * (1 - S.seg(t, A['roll_back0'] + 0.15, A['roll_back0'] + 0.3))
    flash = max(0.0, 1 - (t - A['click']) / 0.35) if t >= A['click'] else 0.0
    cur = closed if t < A['roll_back0'] + 0.3 else 0.0
    # gravedad
    if t >= A['grav']:
        gk = S.ease_out(S.seg(t, A['grav'], A['grav'] + 0.3))
        ga = 1 - S.seg(t, T_A_SLAP, T_A_SLAP + 0.15)
        S.paste_center(cv, D.gravity_arrow(220, gk), 120, 470 - (1 - gk) * 120, alpha=ga)
    if t >= T_A_SLAP:
        lay = tube_composite(T_A_SLAP, 0, 0, 0)
        im, off = tube_place(lay, tube_angle(T_A_SLAP))
        D.shatter(cv, im, off[0], off[1], t - T_A_SLAP, seed=5, tile=60, push=(500, -100))
        return
    # piezas
    th_tube, th_ball, th_cap = A['th']
    st_tube = throw_state(th_tube, t); st_cap = throw_state(th_cap, t)
    ang = tube_angle(t)
    landed_all = st_cap is not None and st_cap[0] == 'land'
    if landed_all:
        lay = tube_composite(t, closed, flash, cur)
        sq = st_cap[1]
        im, off = tube_place(lay, ang)
        cv.alpha_composite(im, off) if off[0] >= 0 and off[1] >= 0 else S._paste(cv, im, off[0], off[1])
    else:
        # tubo
        if st_tube is not None:
            if st_tube[0] == 'fly':
                S.paste_center(cv, D.tube_layer(parts=('tube',)), st_tube[1], st_tube[2], scale=st_tube[4], angle=st_tube[3])
            else:
                lay = D.tube_layer(parts=('tube',))
                S.paste_center(cv, lay, TUBE_C[0] - D.TCX + D.TUBE_W / 2, TUBE_C[1] - D.TCY + D.TUBE_H / 2, sx=st_tube[1], sy=st_tube[2])
        # bolita
        stb = throw_state(th_ball, t)
        if stb is not None:
            if stb[0] == 'fly':
                S.paste_center(cv, _ball_img(), stb[1], stb[2], scale=stb[4], angle=stb[3])
            else:
                v = t - th_ball['t0'] - th_ball['dur']
                y_top = TUBE_C[1] - 220; y_bot = TUBE_C[1] - D.TCY + D.BALL_REST[1]
                tfall = math.sqrt(2 * (y_bot - y_top) / 4200)
                if v < tfall:
                    y = y_top + 0.5 * 4200 * v * v
                else:
                    w = v - tfall
                    y = y_bot - 40 * math.exp(-w * 7) * abs(math.sin(w * 16))
                S.paste_center(cv, _ball_img(), TUBE_C[0] - D.TCX + D.BALL_REST[0], y)
        if st_cap is not None and st_cap[0] == 'fly':
            S.paste_center(cv, th_cap['img_fn'](t), st_cap[1], st_cap[2], scale=st_cap[4], angle=st_cap[3])
    # rótulos
    if t >= A['t_cap'] + 0.55:
        a = S.seg(t, A['t_cap'] + 0.55, A['t_cap'] + 0.8) * (1 - S.seg(t, A['tilt0'] - 0.2, A['tilt0']))
        if a > 0:
            bx = TUBE_C[0] - D.TCX + D.BALL_REST[0]
            S.paste_center(cv, D.label('BOLITA', 28), bx, TUBE_C[1] + 120, alpha=a)
            S.paste_center(cv, D.label('CONTACTOS', 28), TUBE_C[0] - D.TCX + 600, TUBE_C[1] - 120, alpha=a)
            S.paste_center(cv, D.label('PATITAS', 28), TUBE_C[0] - D.TCX + 790, TUBE_C[1] + 105, alpha=a)
    # estado
    if t >= A['click']:
        if t < A['roll_back0'] + 0.25:
            a = S.seg(t, A['click'], A['click'] + 0.15)
            S.paste_center(cv, D.label('CERRADO ✓', 34, fill=D.GREEN), 760, 850, scale=S.ease_back(a))
        else:
            a = S.seg(t, A['roll_back0'] + 0.25, A['roll_back0'] + 0.4) * (1 - S.seg(t, T_A_SLAP, T_A_SLAP + 0.1))
            S.paste_center(cv, D.label('ABIERTO ✗', 34, fill=(255, 90, 90)), 760, 850, scale=S.ease_back(a), alpha=a)
    # ¡CLIC!
    if A['click'] <= t < A['click'] + 0.7:
        u = S.seg(t, A['click'], A['click'] + 0.7)
        pt = D.rotate_pt((D.BALL_TOUCH[0] + 40, D.TCY - 90), (D.TCX, D.TCY), math.radians(tube_angle(t)))
        S.paste_center(cv, title_imgs()['clic'], TUBE_C[0] - D.TCX + pt[0], TUBE_C[1] - D.TCY + pt[1] - 40 * u,
                       scale=0.6 + 0.5 * S.ease_back(min(1, u * 4)), angle=-0.15, alpha=1 - S.seg(u, 0.7, 1.0))


# ======================= escena B: circuito =======================
B = {}
BAT = (390, 690); LED = (960, 690); RES = (675, 860)
WIRE_Y0, WIRE_Y1 = 540, 860
SENS_PIV = (720, WIRE_Y0)        # base de las patitas (pivote) en pantalla
SENS_SCALE = 0.5
SENS_TILT = 27
BX0, BX1 = BAT[0], LED[0]

def wire_path():
    la = SENS_PIV[0] - 26; lb = SENS_PIV[0] + 26
    return [(BX0, BAT[1] - 110), (BX0, WIRE_Y0), (la, WIRE_Y0), (lb, WIRE_Y0), (BX1, WIRE_Y0), (BX1, LED[1] - 55),
            (BX1, LED[1] + 55), (BX1, WIRE_Y1), (RES[0] + 75, WIRE_Y1), (RES[0] - 75, WIRE_Y1), (BX0, WIRE_Y1), (BX0, BAT[1] + 110)]

def setup_B():
    B['t_sens'] = P(12) + 0.05
    B['t_bat'] = KW(12, 'pila') - 0.15
    B['t_led'] = KW(12, 'led') - 0.15
    B['t_res'] = B['t_led'] + 0.35
    B['wire0'] = B['t_res'] + 0.45
    B['wire1'] = B['wire0'] + 0.7
    B['tilt0'] = KW(13, 'inclínalo') - 0.1
    B['on'] = KW(13, 'prende') - 0.1
    B['untilt0'] = KW(14, 'enderézalo') - 0.1
    B['off'] = KW(14, 'apaga') - 0.15
    B['rock0'] = P(15) + 0.1
    B['rock1'] = E(15) - 0.1
    B['th'] = []
    for key, tgt, fn in (('t_sens', (SENS_PIV[0], SENS_PIV[1] - 60), lambda t: _sensor_img(0, 0)[0]),
                         ('t_bat', BAT, lambda t: D.battery_img()), ('t_led', LED, lambda t: D.led_img(0)),
                         ('t_res', RES, lambda t: D.resistor_img())):
        add_throw(B[key], tgt, fn, 'l', dur=0.4, arc=150, spin=0.6)
        B['th'].append(THROWS[-1])
    ev(B['wire0'], 'marker', 0.5, 0.0, dur=0.7)

    ev(B['tilt0'] + 0.2, 'roll', 0.5, 0.0, dur=0.45)
    ev(B['on'], 'click', 0.7, 0.2); ev(B['on'] + 0.02, 'zap', 0.5, panx(LED[0]))
    ev(B['untilt0'] + 0.15, 'roll', 0.4, 0.0, dur=0.4)
    ev(B['off'], 'click', 0.5, 0.0); ev(B['off'] + 0.02, 'pop', 0.3, panx(LED[0]), f0=700, f1=300)

    k = B['rock0'] + 0.15
    while k < B['rock1']:
        ev(k, 'click', 0.35, 0.0); ev(k + 0.02, 'zap', 0.2, panx(LED[0]))
        k += 0.42
    SLAPS.append((T_B_SLAP, 'l'))
    ev(T_B_SLAP, 'whoosh', 0.5, 0.2); ev(T_B_SLAP + 0.05, 'crumble', 0.7, 0.2)

def sens_angle(t):
    if t < B['tilt0']:
        return 0.0
    if t < B['untilt0']:
        return SENS_TILT * S.ease_back(S.seg(t, B['tilt0'], B['tilt0'] + 0.35), 2.0)
    if t < B['rock0']:
        return SENS_TILT * (1 - S.ease_back(S.seg(t, B['untilt0'], B['untilt0'] + 0.35), 1.5))
    if t < B['rock1']:
        u = t - B['rock0']
        return SENS_TILT * max(0.0, math.sin(u * 2 * math.pi / 0.84)) * S.seg(t, B['rock0'], B['rock0'] + 0.15)
    return 0.0

def led_on(t):
    if B['on'] <= t < B['off']:
        return S.seg(t, B['on'], B['on'] + 0.08)
    if B['rock0'] <= t < B['rock1']:
        return 1.0 if sens_angle(t) > 17 else 0.0
    return 0.0

def _sens_ball(t):
    """fracción 0 (atrás) .. 1 (en contactos)"""
    on = led_on(t)
    if B['rock0'] <= t < B['rock1']:
        return S.clamp(sens_angle(t) / 22)
    if t < B['tilt0']:
        return 0.0
    if t < B['untilt0']:
        return S.clamp((t - B['tilt0'] - 0.15) / (B['on'] - B['tilt0'] - 0.15)) ** 2
    return 1 - S.clamp((t - B['untilt0'] - 0.1) / max(0.1, (B['off'] - B['untilt0'] - 0.1)))

def _sensor_img(ang, ballk, on=0.0):
    x0, y0 = D.BALL_REST; x1, y1 = D.BALL_TOUCH
    bx = x0 + (x1 - x0) * ballk; by = y0 + (y1 - y0) * S.ease_io(S.seg(ballk, 0.75, 1))
    lay = D.tube_layer(bx, by, (bx - x0) / D.BALL_R, closed=on, legs_down=True)
    piv = (D.T_X1 + 55, D.TCY + 130)
    return lay, piv

def draw_B(cv, t):
    if t < B['t_sens'] or t > T_B_SLAP + 1.0:
        return
    layer = Image.new('RGBA', (W, 700), (0, 0, 0, 0))    # y 260..960
    OY = 260
    on = led_on(t)
    # cables
    if t >= B['wire0']:
        u = S.seg(t, B['wire0'], B['wire1'])
        pts = wire_path()
        l = D.L(W, 700)
        tot = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        acc = 0; drawn = [pts[0]]
        for i in range(len(pts) - 1):
            d = math.dist(pts[i], pts[i + 1])
            if acc + d <= u * tot:
                drawn.append(pts[i + 1])
            else:
                k = (u * tot - acc) / d
                drawn.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k))
                break
            acc += d
        col = tuple(int(D.WIRE[i] * (1 - 0.25 * on) + (255, 200, 120)[i] * 0.25 * on) for i in range(3))
        # el tramo bajo el sensor no se dibuja (lo cierran las patitas)
        segs = []
        cur = [drawn[0]]
        for j in range(1, len(drawn)):
            a, b = drawn[j - 1], drawn[j]
            if j == 3 and len(drawn) > 3 and abs(a[1] - WIRE_Y0) < 1 and abs(b[1] - WIRE_Y0) < 1:
                segs.append(cur); cur = [b]; continue
            cur.append(b)
        segs.append(cur)
        for sgm in segs:
            if len(sgm) > 1:
                l.line([(x, y - OY) for x, y in sgm], col + (255,), 10)
        if on > 0:
            for k in range(14):
                p = D.along(pts, (t * 0.22 + k / 14) % 1.0)
                l.rect([p[0] - 9, p[1] - OY - 9, p[0] + 9, p[1] - OY + 9], fill=D.CURR + (int(255 * on),))
        layer.alpha_composite(l.done())
    cv.alpha_composite(layer, (0, OY))
    # componentes
    def placer(img_fn, pos):
        def f(c, sx, sy):
            S.paste_center(c, img_fn(), pos[0], pos[1], sx=sx, sy=sy)
        return f
    th_s, th_b, th_l, th_r = B['th']
    draw_thrown(cv, th_b, t, placer(D.battery_img, BAT))
    draw_thrown(cv, th_r, t, placer(D.resistor_img, RES))
    draw_thrown(cv, th_l, t, placer(lambda: D.led_img(on), LED))
    st = throw_state(th_s, t)
    if st is not None:
        ang = sens_angle(t)
        lay, piv = _sensor_img(ang, _sens_ball(t), on)
        if st[0] == 'fly':
            S.paste_center(cv, lay.resize((int(lay.size[0] * SENS_SCALE), int(lay.size[1] * SENS_SCALE))), st[1], st[2], scale=st[4], angle=st[3])
        else:
            im, off = D.rotated_about(lay, piv, ang, SENS_SCALE)
            S._paste(cv, im, int(SENS_PIV[0] + off[0]), int(SENS_PIV[1] + off[1]))
    # rótulos
    if t >= B['wire1']:
        a = S.seg(t, B['wire1'], B['wire1'] + 0.2)
        S.paste_center(cv, D.label('PILA', 26), BAT[0], BAT[1] + 160, alpha=a)
        S.paste_center(cv, D.label('LED', 26), LED[0] - 10, LED[1] + 110, alpha=a)
        S.paste_center(cv, D.label('SENSOR', 26), SENS_PIV[0] - 190, SENS_PIV[1] - 150, alpha=a * (1 - S.seg(t, B['tilt0'] - 0.2, B['tilt0'])))
        S.paste_center(cv, D.label('RESISTENCIA', 24), RES[0], RES[1] + 60, alpha=a)
    if t >= B['on'] - 0.05 and t < B['rock0']:
        if t < B['off']:
            S.paste_center(cv, D.label('CERRADO ✓', 32, fill=D.GREEN), 675, 700, scale=S.ease_back(S.seg(t, B['on'], B['on'] + 0.15)))
        else:
            a = 1 - S.seg(t, B['rock0'] - 0.2, B['rock0'])
            S.paste_center(cv, D.label('ABIERTO ✗', 32, fill=(255, 90, 90)), 675, 700, scale=S.ease_back(S.seg(t, B['off'], B['off'] + 0.15)), alpha=a)
    if t >= B['rock0'] + 0.3:
        a = S.seg(t, B['rock0'] + 0.3, B['rock0'] + 0.5) * (1 - S.seg(t, T_B_SLAP, T_B_SLAP + 0.1))
        S.paste_center(cv, D.label('obedece a la GRAVEDAD', 30, fill=D.GRAV), 675, 700, alpha=a)
    if t >= T_B_SLAP:
        pass


def capture_B_layer(t):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_B(lay, t)
    return lay.crop((0, 230, W, 960))


# ======================= escena: usos =======================
U = {}
CARDS = [('alarmas', D.card_alarm, (305, 445)), ('juguetes', D.card_toy, (775, 445)),
         ('tilt', D.card_pinball, (305, 715)), ('calentadores', D.card_heater, (775, 715))]

def setup_U():
    U['th'] = []
    for word, fn, pos in CARDS:
        t0 = KW(16, word) - 0.2
        add_throw(t0, pos, (lambda fn: (lambda t: fn(0)))(fn), 'l', dur=0.4, arc=140, spin=0.4)
        U['th'].append((THROWS[-1], fn, pos))
    tt = KW(16, 'alarmas') + 0.3
    ev(tt, 'beep', 0.25, panx(305)); ev(tt + 0.25, 'beep', 0.25, panx(305))
    ev(KW(16, 'juguetes') + 0.45, 'squeak', 0.3, panx(775))
    ev(KW(16, 'tilt') + 0.4, 'buzz', 0.25, panx(305))
    ev(KW(16, 'calentadores') + 0.7, 'thud', 0.4, panx(775))
    SLAPS.append((T_C_SLAP, 'l'))
    ev(T_C_SLAP, 'whoosh', 0.5, 0.2); ev(T_C_SLAP + 0.05, 'crumble', 0.7, 0.2)

def draw_U(cv, t, at=None):
    if t < KW(16, 'alarmas') - 0.25 or t > T_C_SLAP + 1.0:
        return
    if t >= T_C_SLAP and at is None:
        lay = Image.new('RGBA', (W, 700), (0, 0, 0, 0))
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw_U(tmp, T_C_SLAP - 0.01, at=True)
        lay = tmp.crop((0, 280, W, 880))
        D.shatter(cv, lay, 0, 280, t - T_C_SLAP, seed=8, tile=64, push=(300, -100))
        return
    for th, fn, pos in U['th']:
        st = throw_state(th, t)
        if st is None:
            continue
        lt = t - th['t0'] - th['dur']
        if st[0] == 'fly':
            S.paste_center(cv, fn(0), st[1], st[2], scale=st[4], angle=st[3])
        else:
            S.paste_center(cv, fn(max(0, lt)), pos[0], pos[1], sx=st[1], sy=st[2])


# ======================= escena C: celular y acelerómetro =======================
PC = {}
PHONE_C = (370, 560); PHONE_S = 0.8
LENS_C = (800, 500)

def setup_PC():
    PC['t_phone'] = KW(17, 'celular') - 0.2
    PC['t_chip'] = KW(17, 'acelerómetro') - 0.1
    PC['t_lens'] = PC['t_chip'] + 0.25
    PC['t_grav'] = KW(19, 'jala') - 0.25
    PC['t_bars'] = KW(19, 'tres') - 0.15
    PC['rot0'] = KW(20, 'gira') - 0.2
    PC['rot1'] = PC['rot0'] + 0.55
    PC['lens_out'] = KW(20, 'gira') - 0.4
    add_throw(PC['t_phone'], PHONE_C, lambda t: D.phone_img()[0].resize((int(380 * PHONE_S), int(670 * PHONE_S))), 'l', dur=0.45, arc=160, spin=0.5)
    PC['th'] = THROWS[-1]
    ev(PC['t_chip'], 'zap', 0.35, panx(PHONE_C[0]))
    ev(PC['t_lens'], 'pop', 0.5, panx(LENS_C[0]))
    ev(P(18) + 0.3, 'boing', 0.25, panx(LENS_C[0]))
    ev(PC['t_grav'] + 0.2, 'thud', 0.4, panx(LENS_C[0]))
    ev(PC['t_grav'] + 0.3, 'boing', 0.35, panx(LENS_C[0]), f0=260, f1=150)
    ev(PC['t_bars'], 'marker', 0.35, panx(LENS_C[0]))
    ev(PC['rot0'], 'whoosh', 0.45, panx(PHONE_C[0]))
    ev(PC['rot1'] + 0.3, 'click', 0.5, panx(PHONE_C[0]))
    POINTS.append((PC['rot0'] - 0.15, PC['rot1'] + 0.1, 'l', lambda t: (PHONE_C[0] + 60, PHONE_C[1] + 200)))
    SLAPS.append((T_D_SLAP, 'l'))
    ev(T_D_SLAP, 'whoosh', 0.5, 0.2); ev(T_D_SLAP + 0.05, 'crumble', 0.7, 0.2)

def phone_angle(t):
    if t < PC['rot0']:
        return 0.0
    u = S.seg(t, PC['rot0'], PC['rot1'])
    if u < 0.2:
        return -8 * S.ease_out(u / 0.2)
    return -8 + 98 * S.ease_back((u - 0.2) / 0.8, 1.8)

def content_rot(t):
    if t < PC['rot1'] + 0.2:
        return 0.0
    return -math.pi / 2 * S.ease_back(S.seg(t, PC['rot1'] + 0.2, PC['rot1'] + 0.55), 1.4)

def mass_shift(t):
    if t < PC['t_grav']:
        return (0.0, 0.0)
    v = t - PC['t_grav'] - 0.2
    if v < 0:
        return (0.0, 0.0)
    y = 28 * (1 - S.jelly(v, 2.2, 3.5))
    return (0.0, y)

def draw_PC(cv, t, at=None):
    if t < PC['t_phone'] or t > T_D_SLAP + 1.0:
        return
    if t >= T_D_SLAP and at is None:
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw_PC(tmp, T_D_SLAP - 0.01, at=True)
        D.shatter(cv, tmp.crop((0, 230, W, 900)), 0, 230, t - T_D_SLAP, seed=12, tile=64, push=(300, -100))
        return
    chip = S.seg(t, PC['t_chip'], PC['t_chip'] + 0.2)
    # lupa (detrás del celular)
    if PC['t_lens'] <= t < PC['lens_out'] + 0.4:
        k = S.ease_back(S.seg(t, PC['t_lens'], PC['t_lens'] + 0.35)) * (1 - S.ease_in(S.seg(t, PC['lens_out'], PC['lens_out'] + 0.35)))
        if k > 0.01:
            # líneas de zoom del chip a la lupa
            ph_img, chip_off = D.phone_img(0, chip)
            cx = PHONE_C[0] + (chip_off[0] + 40 - ph_img.size[0] / 2) * PHONE_S
            cy = PHONE_C[1] + (chip_off[1] + 40 - ph_img.size[1] / 2) * PHONE_S
            l = D.L(W, H)
            for dy in (-1, 1):
                l.line([(cx + 18, cy + dy * 18), (LENS_C[0] - 120, LENS_C[1] + dy * 140)], (255, 230, 140, int(150 * k)), 4)
            cv.alpha_composite(l.done())
            hl = S.seg(t, PC['t_bars'] - 0.2, PC['t_bars'] + 0.2)
            mag = D.magnifier(D.mems_img(mass_shift(t), hl), r=170)
            S.paste_center(cv, mag, LENS_C[0] + 50, LENS_C[1] + 50, scale=k)
            if t >= P(18) + 0.4:
                a = S.seg(t, P(18) + 0.4, P(18) + 0.6) * k
                S.paste_center(cv, D.label('RESORTES', 26), LENS_C[0] - 150, LENS_C[1] + 175, alpha=a)
            if t >= PC['t_grav']:
                gk = S.ease_out(S.seg(t, PC['t_grav'], PC['t_grav'] + 0.3))
                S.paste_center(cv, D.gravity_arrow(150, gk), 580, LENS_C[1] - 70, alpha=k, scale=0.8)
            if t >= PC['t_bars']:
                bk = S.ease_back(S.seg(t, PC['t_bars'], PC['t_bars'] + 0.3)) * k
                ms = mass_shift(t)
                vals = (0.15 * math.sin(t * 7), -ms[1] / 28 * 0.9 - 0.05 * math.sin(t * 5), 0.1 * math.sin(t * 9 + 1))
                S.paste_center(cv, D.axis_bars(vals), 935, 800, scale=bk * 0.8)
    # celular
    st = throw_state(PC['th'], t)
    if st is not None:
        ph_img, _ = D.phone_img(content_rot(t), chip)
        ph_img = ph_img.resize((int(ph_img.size[0] * PHONE_S), int(ph_img.size[1] * PHONE_S)), Image.LANCZOS)
        if st[0] == 'fly':
            S.paste_center(cv, ph_img, st[1], st[2], scale=st[4], angle=st[3])
        else:
            S.paste_center(cv, ph_img, PHONE_C[0], PHONE_C[1], sx=st[1], sy=st[2], angle=-math.radians(phone_angle(t)))
        if t >= PC['t_chip'] and t < PC['rot0']:
            a = S.seg(t, PC['t_chip'], PC['t_chip'] + 0.2)
            S.paste_center(cv, D.label('ACELERÓMETRO', 28, fill=(255, 220, 120)), 640, 860, alpha=a)


# ======================= escena final =======================
F = {}
BTN = {'like': (770, 600), 'sub': (770, 735), 'follow': (770, 870)}

def setup_F():
    F['bub'] = P(21) - 0.05
    F['heart'] = KW(21, 'gracias') + 0.3
    F['bub_out'] = E(21) + 0.3
    F['btn_in'] = P(22) - 0.6
    F['hit'] = {'like': KW(22, 'me gusta'), 'sub': KW(22, 'suscríbete'), 'follow': KW(22, 'sígueme')}
    ev(F['bub'], 'pop', 0.5, 0.0)
    ev(F['heart'], 'pop', 0.5, 0.2, f0=400, f1=900)
    ev(F['heart'] + 0.1, 'thump2', 0.5, 0.2)
    for i, k in enumerate(('like', 'sub', 'follow')):
        ev(F['btn_in'] + i * 0.1, 'pop', 0.35, 0.4)
        th = F['hit'][k]
        JUMPS.append((th - 0.3, 0.55, 70))
        POINTS.append((th - 0.12, th + 0.08, 'l', (lambda kk: (lambda t: (BTN[kk][0] - 180, BTN[kk][1])))(k)))
        ev(th, 'click', 0.6, 0.5); ev(th + 0.02, 'pop', 0.4, 0.5, f0=600, f1=1400)
        if k == 'sub':
            ev(th + 0.05, 'bell', 0.6, 0.5)
        ev(th - 0.3 + 0.55, 'step', 0.5, panx(300))
    ev(T_END_SNAP, 'snap', 0.9, -0.2)
    ev(T_END_SNAP + 0.05, 'switch', 0.5, 0.0)
    ev(T_END_SNAP + 1.35, 'tvoff', 0.8, 0.0)

def draw_F(cv, t):
    if F['bub'] <= t < F['bub_out'] + 0.3:
        k = S.ease_back(S.seg(t, F['bub'], F['bub'] + 0.3)) * (1 - S.ease_in(S.seg(t, F['bub_out'], F['bub_out'] + 0.3)))
        heart = S.ease_back(S.seg(t, F['heart'], F['heart'] + 0.3))
        b = D.comment_bubble('La gravedad?', width=560, heart=heart, t=t)
        S.paste_center(cv, b, 560, 470, scale=k)
    if t >= F['btn_in'] and t < T_END_SNAP + 0.4:
        for i, k in enumerate(('like', 'sub', 'follow')):
            s = S.ease_back(S.seg(t, F['btn_in'] + i * 0.1, F['btn_in'] + i * 0.1 + 0.35)) * (1 - S.ease_in(S.seg(t, T_END_SNAP + 0.05, T_END_SNAP + 0.35)))
            th = F['hit'][k]
            pressed = 1.0 if t >= th else 0.0
            sq = 1 - 0.25 * S.jelly(t - th, 3, 6) if t >= th else 1.0
            S.paste_center(cv, D.end_button(k, pressed), BTN[k][0], BTN[k][1], scale=s, sx=2 - sq, sy=sq)
    # al final un bloque flota hacia arriba (se apagó la gravedad)
    if t >= T_END_SNAP + 0.3:
        u = t - T_END_SNAP - 0.3
        S.paste_center(cv, D.stone_cube(56, (120, 200, 120)), 880, S.FLOOR_Y - 40 - 70 * u * u - 30 * u, angle=0.4 * u, alpha=min(1, u * 4))


# ======================= montaje de todo =======================
def setup_all():
    setup_walks()
    schedule_intro_sfx()
    setup_gravity()
    THROWS_G['b1'], THROWS_G['b2'], THROWS_G['planet'] = THROWS[0], THROWS[1], THROWS[2]
    setup_title()
    setup_A()
    A['th'] = THROWS[-3:]
    setup_B()
    setup_U()
    setup_PC()
    setup_F()
    # reacciones con saltos, giros y brazos arriba
    react = [
        (T_SNAP + 0.9, 0.45, 60, None),                 # salta feliz tras aterrizar
        (KW(6, 'aunque') - 0.05, 0.5, 90, 'up'),          # hay componentes que la sienten
        (P(7) + 0.1, 0.7, 110, 'spin'),                   # título
        (A['click'] + 0.05, 0.4, 55, 'up'),               # ¡clic!
        (B['on'] + 0.05, 0.45, 70, 'fist'),               # LED prende
        (P(15) + 0.2, 0.35, 40, None), (P(15) + 0.6, 0.35, 40, None), (P(15) + 1.0, 0.35, 40, None),
        (P(17) - 0.05, 0.45, 70, 'up'),                   # ¿y tu celular?
        (KW(20, 'gira') + 0.6, 0.45, 60, 'up'),
        (KW(21, 'buena') - 0.1, 0.45, 60, 'thumb'),
    ]
    for t0, d, h, kind in react:
        JUMPS.append((t0, d, h))
        ev(t0 + d, 'step', 0.45, 0.0, heavy=0.9)
        if kind == 'spin':
            SPINS.append((t0, d)); ev(t0, 'whoosh', 0.3, 0.0)
        if kind:
            REACT_ARMS.append((t0, d, kind))

REACT_ARMS = []
setup_all()

_bg = {}
def bg_img(light):
    if 'lit' not in _bg:
        _bg['lit'] = S.lit_room()
        _bg['lit_np'] = np.array(_bg['lit'], np.float32)
    if light >= 0.999:
        return _bg['lit'].convert('RGBA')
    if light <= 0.001:
        return Image.new('RGBA', (W, H), (0, 0, 0, 255))
    a = (_bg['lit_np'] * light).astype(np.uint8)
    return Image.fromarray(a, 'RGB').convert('RGBA')


def render_frame(t):
    pose, x, yf, light, glow = char_state(t)
    cv = bg_img(light)
    # ----- intro: bloques flotando / cayendo -----
    if t < T_LIGHT + 0.6:
        for b in INTRO_BLOCKS:
            bx, by, ang, sc, landed = block_state(b, t)
            if landed and light >= 0.999:
                continue
            img = b['img'].convert('RGBA')
            dim = 0.5 if t < T_SNAP else max(0.5, light)
            if dim < 0.999:
                arr = np.array(img, np.float32); arr[..., :3] *= dim
                img = Image.fromarray(arr.astype(np.uint8), 'RGBA')
            S.paste_center(cv, img, bx + S.BLK / 2, by + S.BLK / 2, scale=sc, angle=ang)
        # el piso queda dibujado si no hay luz completa
    # ----- lámpara -----
    lx, ly, sw, hanging = lamp_state(t) if t < T_LIGHT + 1.0 else (S.LAMP_X, S.LAMP_Y, 0.0, True)
    if t >= T_END_SNAP:
        sw = 0.04 * math.sin((t - T_END_SNAP) * 5) * math.exp(-(t - T_END_SNAP))
    lamp_on = light
    if not hanging:
        # flotando: sin cable, girando
        d = ImageDraw.Draw(cv)
        tmp = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
        S.draw_lamp(tmp, on=0.0, swing=0, y_off=0, cord=False, x=60) if False else None
        lamp = Image.new('RGBA', (140, 140), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lamp)
        dd.line([(70, 0), (70, 40)], fill=(70, 70, 70), width=3)
        dd.polygon([(54, 40), (86, 40), (96, 58), (44, 58)], fill=(80, 80, 85))
        dd.ellipse([61, 55, 79, 69], fill=(110, 108, 100))
        S.paste_center(cv, lamp, lx, ly, angle=sw * 3)
    else:
        S.draw_lamp(cv, on=lamp_on, swing=sw, y_off=ly - S.LAMP_Y)
        if lamp_on > 0.05:
            S.glow_fast(cv, S.LAMP_X + math.sin(sw) * S.LAMP_Y, math.cos(sw) * ly + 22, 90, (255, 230, 150), 0.6 * lamp_on)
    # ----- etiqueta -----
    if t >= T_TITLE_FLY + 0.4 and t < T_END_SNAP + 0.1:
        S.draw_label(cv, LABEL_TXT, alpha=S.seg(t, T_TITLE_FLY + 0.4, T_TITLE_FLY + 0.6) * light)
    # ----- diagramas -----
    draw_gravity(cv, t)
    draw_title(cv, t)
    draw_A(cv, t)
    if t >= T_B_SLAP:
        if t < T_B_SLAP + 1.0:
            lay = capture_B_layer(T_B_SLAP - 0.01)
            D.shatter(cv, lay, 0, 230, t - T_B_SLAP, seed=7, tile=64, push=(300, -100))
    else:
        draw_B(cv, t)
    draw_U(cv, t)
    draw_PC(cv, t)
    # ----- sombra del personaje -----
    if light > 0.05:
        h = S.FLOOR_Y - yf
        sh_w = 150 * max(0.4, 1 - h / 600)
        d = ImageDraw.Draw(cv, 'RGBA')
        d.ellipse([x - sh_w, S.FLOOR_Y - 14, x + sh_w, S.FLOOR_Y + 12], fill=(0, 0, 0, int(110 * light * max(0.3, 1 - h / 500))))
    # ----- personaje -----
    if glow > 0.02:
        S.glow_fast(cv, x, yf - 28 * S.SCALE, 210, (40, 160, 90), 0.35 * glow)
    char_light = 0.32 + 0.68 * light if t < T_END_SNAP + 1.3 else 0.32
    CH.render(cv, pose, dict(scale=S.SCALE, ox=x, oy=yf, view_yaw=0.12 * math.sin(t * 0.2)), light=char_light, t=t)
    # ----- "?" de la pregunta -----
    if WALK1[1] <= t < E(3) + 0.3:
        k = S.ease_back(S.seg(t, WALK1[1], WALK1[1] + 0.3)) * (1 - S.seg(t, E(3), E(3) + 0.3))
        q = S.fancy_text('?', 110, top=(255, 255, 255), bot=(200, 220, 255), outline=(30, 40, 80)) if 'q' not in _bg else _bg['q']
        _bg['q'] = q
        S.paste_center(cv, q, x + 120, yf - 36 * S.SCALE + 8 * math.sin(t * 6), scale=k)
    # ----- burbujas de la intro -----
    if t < T_SNAP + 1.0:
        for i, (ts, pos) in enumerate(((P(0) + 0.1, BUB1), (P(1) + 0.2, BUB2))):
            if t < ts:
                continue
            k = S.ease_back(S.seg(t, ts, ts + 0.3))
            if t < T_SNAP:
                S.paste_center(cv, bubble(i + 1), pos[0], pos[1] + 8 * math.sin(t * 1.7 + i), scale=k, angle=0.03 * math.sin(t + i))
            else:
                u = t - T_SNAP - 0.05 * i
                y = pos[1] + 0.5 * 4200 * max(0, u) ** 2
                S.paste_center(cv, bubble(i + 1), pos[0], y, angle=0.4 * max(0, u) * (1 if i else -1), alpha=1 - S.seg(u, 0.15, 0.35))
    # ----- chasquido: onda y texto -----
    if T_SNAP <= t < T_SNAP + 1.9:
        u = t - T_SNAP
        hp = hand_pos(T_SNAP, 'l')
        if u < 0.5:
            r = 30 + 900 * S.ease_out(u / 0.5)
            l = D.L(W, H)
            l.circle(hp, r, outline=(255, 255, 255, int(200 * (1 - u / 0.5))), width=8)
            cv.alpha_composite(l.done())
        k = S.ease_back(S.seg(u, 0.15, 0.45))
        S.paste_center(cv, title_imgs()['grav'], 540, 560 + 10 * math.sin(u * 8), scale=k, alpha=1 - S.seg(u, 1.4, 1.9))
    draw_F(cv, t)
    # ----- subtítulos -----
    sub, si = TL.subtitle_at(t)
    if sub and t < T_END_SNAP + 0.2:
        S.draw_subtitle(cv, sub)
    # ----- apagado de TV viejo -----
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
    import sys
    print('duración', round(T_END, 2))
    for i in range(len(PHRASES)):
        print(i, round(P(i), 2), round(E(i), 2), PHRASES[i][1][:50])
