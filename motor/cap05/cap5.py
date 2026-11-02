#!/usr/bin/env python3
# Capítulo 5: El condensador. Vertical 1080x1920, 30 fps.
# Intro (gancho en el segundo 0): a oscuras, el pitido del flash cargándose... ¡FLASH! y se prende el cuarto.
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
import condensador as K
import lab as LB
import char3d as C
from timeline import TL, PHRASES

W, H = S.W, S.H
FPS = S.FPS
CH = C.Character()
HOME_X = 230
INTRO_X = 470
LABEL_TXT = 'CAP. 5 · EL CONDENSADOR'

P = lambda i: TL.s(i)
E = lambda i: TL.e(i)
KW = TL.kw

# ======================= tiempos clave =======================
T_FLASH = KW(0, 'FLASH')          # ¡FLASH!
T_BONK = T_FLASH                  # (la música usa este nombre)
T_PRESENT = KW(1, 'aquí') - 0.2   # muestra la cámara con rayos X
T_TITLE = KW(1, 'Capítulo')
T_TITLE_FLY = E(1) + 0.3
T_WALK_HOME = E(2) + 0.1
T_LOOK = P(2)
T_SNAP_LAB = KW(2, 'Mejor') - 0.15
T_FLIP0 = T_SNAP_LAB + 0.08
T_LAB_DONE = T_FLIP0 + LB.T_TRANS
T_A_SLAP = E(3) + 0.15
T_R_SLAP = E(4) + 0.3
T_B_SLAP = E(9) + 0.35
T_F_SLAP = E(10) + 0.25
T_T_SLAP = E(13) + 0.2
T_S_SLAP = E(14) + 0.3
T_M_SLAP = E(15) + 0.3
T_K_SLAP = E(17) + 0.3
T_END_SNAP = E(20) + 0.5
T_END = TL.END
T_POOF = KW(13, 'PUM') - 0.05
T_FLASH2 = KW(16, 'soltarlos')
T_SUPER = P(14) + 0.1
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


# ======================= expresiones =======================
EXPR = [
    (0.0, 'feliz'), (0.5, 'guino'), (T_FLASH - 0.25, 'feliz'), (T_FLASH, 'sorpresa'), (T_FLASH + 0.25, 'mareado'),
    (P(1) + 0.35, 'feliz'), (T_PRESENT + 0.3, 'curioso'), (T_TITLE, 'feliz'),
    (T_LOOK, 'feliz'), (KW(2, 'cuarto'), 'pensando'), (KW(2, 'Mejor') - 0.1, 'guino'), (KW(2, 'LABORATORIO'), 'feliz'), (T_LAB_DONE - 0.2, 'corazon'),
    (P(3), 'feliz'), (KW(3, 'Guarda'), 'curioso'), (KW(3, 'golpe'), 'sorpresa'), (E(3), 'feliz'),
    (P(4), 'pensando'), (KW(4, 'maratonista'), 'feliz'), (KW(4, 'velocista'), 'sorpresa'), (E(4) + 0.2, 'feliz'),
    (P(5), 'pensando'), (P(6), 'curioso'), (KW(6, 'AISLANTE'), 'feliz'),
    (P(7), 'curioso'), (KW(7, 'amontonan'), 'feliz'), (KW(7, 'se van'), 'curioso'),
    (P(8), 'pensando'), (KW(8, 'esperan'), 'guino'), (KW(8, 'CARGADO'), 'feliz'),
    (P(9), 'curioso'), (KW(9, 'prende'), 'corazon'), (KW(9, 'apaga'), 'curioso'), (E(9), 'feliz'),
    (P(10), 'curioso'), (KW(10, 'muchísimo'), 'sorpresa'), (KW(10, 'microfaradios'), 'guino'),
    (P(11), 'feliz'), (KW(11, 'cualquier'), 'guino'),
    (P(12), 'curioso'), (KW(12, 'tiene lado'), 'pensando'), (KW(12, 'NEGATIVO'), 'feliz'),
    (P(13), 'pensando'), (KW(13, 'infla'), 'sorpresa'), (T_POOF, 'mareado'), (KW(13, 'cruz'), 'feliz'),
    (P(14), 'curioso'), (T_SUPER + 0.45, 'sorpresa'), (KW(14, 'miles'), 'corazon'),
    (P(15), 'curioso'), (KW(15, 'celular'), 'feliz'), (KW(15, 'grano'), 'sorpresa'),
    (P(16), 'pensando'), (KW(16, '300'), 'curioso'), (T_FLASH2, 'sorpresa'), (T_FLASH2 + 0.5, 'feliz'),
    (P(17), 'pensando'), (KW(17, 'No la abras'), 'sorpresa'),
    (P(18), 'guino'), (KW(18, 'chispa'), 'feliz'),
    (P(19), 'feliz'), (P(20), 'curioso'), (KW(20, 'Nos vemos'), 'guino'),
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
            aim(tp, side, shoulder_screen(x, yf, side, pose.sx, pose.sy), tgt)
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
        (T_WALK_HOME, HOME_X, 1.0),
        (P(6) + 0.3, 330, 0.9), (P(7) + 0.1, HOME_X, 0.9),
        (P(11) + 0.2, 330, 0.9), (P(12) + 0.1, HOME_X, 0.9),
        (P(15) + 0.2, 320, 0.9), (P(16) + 0.1, HOME_X, 0.9),
        (P(20) + 0.1, 300, 0.8),
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


# ======================= cámara de la intro =======================
def cam_hold_pt(t):
    """donde está la cámara (centro) mientras la sostiene"""
    x, _ = pos_x(t)
    return (x + 175, S.FLOOR_Y - 30 * S.SCALE)

CAM_SHOW = (735, 560)

def cam_state(t):
    """(cx, cy, escala, alfa, rayosX) o None"""
    if t >= T_TITLE + 0.05:
        return None
    hold = cam_hold_pt(t)
    if t < T_PRESENT:
        up = S.ease_out(S.seg(t, 0.0, 0.3))
        return (hold[0], hold[1] + 120 * (1 - up), 0.62 + 0.08 * up, 1.0, 0.0)
    u = S.ease_back(S.seg(t, T_PRESENT, T_PRESENT + 0.45))
    x = hold[0] + (CAM_SHOW[0] - hold[0]) * u
    y = hold[1] + (CAM_SHOW[1] - hold[1]) * u
    sc = 0.7 + 0.75 * u
    xr = S.ease_io(S.seg(t, KW(1, 'adentro') - 0.15, KW(1, 'adentro') + 0.25))
    out = S.ease_in(S.seg(t, T_TITLE - 0.25, T_TITLE + 0.05))
    return (x, y, sc * (1 - 0.9 * out), 1 - out, xr)

def cam_ready(t):
    if t >= T_FLASH - 0.35:
        return 1.0
    return 1.0 if int(t / 0.16) % 2 == 0 else 0.0


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
    if si is not None and walking is None and t > T_WALK_HOME + 1.0:
        env = mouth_at(t)
        g1 = math.sin(t * 3.4 + si * 1.7); g2 = math.sin(t * 2.6 + si * 0.9 + 1.3)
        amp = 0.45 + 0.45 * env
        p.larm = (0.55 + 0.55 * g1 * amp, 0.15 * g2, 0.25 + 0.35 * max(0, g2) * amp); p.lelbow = 0.9 + 0.5 * g1
        p.rarm = (0.45 + 0.5 * g2 * amp, -0.15 * g1, 0.25 + 0.35 * max(0, g1) * amp); p.relbow = 0.9 + 0.5 * g2
        p.head = (p.head[0] + 0.14 * env * math.sin(t * 9), p.head[1] + 0.1 * g2, p.head[2] + 0.07 * g1)
        yf -= 3 * env
        p.sy *= 1 + 0.015 * env
        p.lean += 0.06 * g1
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
    # sostiene la cámara con el brazo (de goma) hacia su izquierda, mirando a la cámara
    if t < T_PRESENT + 0.45:
        k = S.ease_out(S.seg(t, 0.0, 0.3)) * (1 - S.ease_io(S.seg(t, T_PRESENT + 0.25, T_PRESENT + 0.45)))
        st = cam_state(t)
        if st:
            tp = p.copy()
            aim(tp, 'l', shoulder_screen(x, yf, 'l', p.sx, p.sy), (st[0] - 40 * st[2], st[1] + 30 * st[2]), maxlen=2.8)
            blend_arm(p, 'l', tp, k)
    if t < T_FLASH:
        # se agacha un poquito, como fotógrafo, y se ríe pícaro
        crouch = S.ease_out(S.seg(t, 0.05, 0.5))
        p.rknee = 0.35 * crouch; p.lknee = 0.35 * crouch
        p.lean += 0.06 * crouch + 0.03 * math.sin(t * 9)
        p.head = (p.head[0] + 0.05 * math.sin(t * 7), p.head[1] - 0.15, p.head[2])
        p.rarm = (0.5, 0, 0.5); p.relbow = 1.3     # mano en la rodilla
    elif t < P(1) + 0.3:
        # el flash lo encandila: se va hacia atrás y se tambalea
        u = t - T_FLASH
        j = S.jelly(u, 3.0, 4.0)
        p.lean += -0.3 * math.exp(-u * 3) + 0.06 * math.sin(u * 8)
        p.sx *= 1 + 0.08 * j; p.sy *= 1 - 0.08 * j
        p.rarm = (0.9, 0, 0.6); p.relbow = 2.0          # se tapa los ojos
        p.head = (p.head[0] + 0.1 * math.sin(u * 9), p.head[1], p.head[2] + 0.12 * math.sin(u * 6))


def diagram_active(t):
    return (P(3) + 0.5 <= t < T_R_SLAP) or (P(6) + 0.4 <= t < T_B_SLAP) or (P(10) + 0.3 <= t < T_F_SLAP) \
        or (P(11) + 0.3 <= t < T_S_SLAP) or (P(15) + 0.4 <= t < T_M_SLAP) or (P(16) + 0.3 <= t < T_K_SLAP)


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
            elif kind == 'cover':        # se cubre la cara (¡PUM!)
                tp.larm = (1.5, 0, -0.3); tp.lelbow = 1.9; tp.rarm = (1.5, 0, -0.3); tp.relbow = 1.9
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
                p.lean += -0.15 * k
    # mira el cuarto de piedra: "necesita un cambio" (mano en la barbilla, mira a los lados)
    a, b = KW(2, 'cuarto') - 0.3, T_SNAP_LAB - 0.1
    if a <= t < b:
        k = S.seg(t, a, a + 0.2) * (1 - S.seg(t, b - 0.15, b))
        tp = p.copy(); tp.rarm = (1.9, 0, -0.2); tp.relbow = 2.0
        blend_arm(p, 'r', tp, k)
        sw = math.sin((t - a) * 3.2)
        p.head = (p.head[0] - 0.12 * k, p.head[1] + 0.7 * k * sw, p.head[2])
        p.look = (sw * k, -0.3 * k)
    # chasquido para cambiar el cuarto
    if T_SNAP_LAB - 0.3 <= t < T_SNAP_LAB + 0.6:
        u = S.ease_out(S.seg(t, T_SNAP_LAB - 0.3, T_SNAP_LAB - 0.05)) * (1 - S.seg(t, T_SNAP_LAB + 0.3, T_SNAP_LAB + 0.6))
        tp = p.copy(); tp.rarm = (0.3, 0, 2.6); tp.relbow = 0.5
        blend_arm(p, 'r', tp, u)
    # "¿Y qué tiene por dentro?": mano en la barbilla
    a, b = P(5) - 0.1, P(6) + 0.3
    if a <= t < b:
        k = S.seg(t, a, a + 0.2) * (1 - S.seg(t, b - 0.2, b))
        tp = p.copy(); tp.rarm = (1.9, 0, -0.2); tp.relbow = 2.0
        blend_arm(p, 'r', tp, k)
        p.head = (p.head[0] - 0.1 * k, p.head[1] + 0.3 * k, p.head[2] + 0.15 * k)
        p.lean += 0.1 * k
    # "así que esperan": brazos cruzados, tamborilea el pie
    a, b = KW(8, 'esperan') - 0.1, KW(8, 'CARGADO') - 0.1
    if a <= t < b:
        k = S.seg(t, a, a + 0.15) * (1 - S.seg(t, b - 0.15, b))
        tp = p.copy(); tp.larm = (1.2, 0, -0.6); tp.lelbow = 1.7; tp.rarm = (1.2, 0, -0.6); tp.relbow = 1.7
        blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
        p.rleg = (0.25 * k * max(0, math.sin((t - a) * 14)), 0, 0)
    # "¡No la abras!": mano de "alto" y niega con la cabeza
    a = KW(17, 'No la abras') - 0.15
    if a <= t < E(17) + 0.25:
        k = S.seg(t, a, a + 0.15) * (1 - S.seg(t, E(17), E(17) + 0.25))
        tp = p.copy(); tp.larm = (1.55, 0, 0.1); tp.lelbow = 0.1; tp.larm_len = 1.2
        blend_arm(p, 'l', tp, k)
        p.head = (p.head[0], p.head[1] + 0.35 * k * math.sin((t - a) * 14), p.head[2])
    # risa en "con mucha chispa"
    if P(18) <= t < E(18):
        sh = math.sin(t * 30) * 0.03
        p.head = (-0.15 + sh, p.head[1], p.head[2])
    # despedida
    a = KW(20, 'Nos vemos') - 0.2
    if a <= t < T_END_SNAP - 0.35:
        k = S.seg(t, a, a + 0.2)
        tp = p.copy(); tp.larm = (0.1, 0, 2.5 + 0.35 * math.sin((t - a) * 13)); tp.lelbow = 0.4; tp.larm_len = 1.2
        blend_arm(p, 'l', tp, k)
    if T_END_SNAP - 0.35 <= t < T_END_SNAP + 0.6:
        u = S.ease_out(S.seg(t, T_END_SNAP - 0.35, T_END_SNAP - 0.05)) * (1 - S.seg(t, T_END_SNAP + 0.3, T_END_SNAP + 0.6))
        tp = p.copy(); tp.rarm = (0.3, 0, 2.6); tp.relbow = 0.5
        blend_arm(p, 'r', tp, u)


def light_at(t):
    if t < T_FLASH + 0.03:
        return 0.0
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


def wire_partial(l, pts, u, col, width=10, oy=0):
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
    if len(drawn) > 1:
        l.line([(x, y - oy) for x, y in drawn], col + (255,), width)


def capture(fn, t, y0, y1):
    tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fn(tmp, t, at=True)
    return tmp.crop((0, y0, W, y1))



_cap_cache = {}
def shattered(cv, fn, ts, t, seed, y0=250, y1=880):
    """dibuja la escena 'fn' rota en bloquecitos tras el manotazo en ts"""
    if fn not in _cap_cache:
        _cap_cache[fn] = capture(fn, ts - 0.01, y0, y1)
    D.shatter(cv, _cap_cache[fn], 0, y0, t - ts, seed=seed, tile=64, push=(300, -100))

def add_slap(ts):
    SLAPS.append((ts, 'l'))
    ev(ts, 'whoosh', 0.5, 0.2); ev(ts + 0.05, 'crumble', 0.7, 0.2)


# ======================= título =======================
_tc = {}
def title_imgs():
    if not _tc:
        _tc['a'] = S.fancy_text('CAPÍTULO 5', 92)
        _tc['b'] = S.fancy_text('EL CONDENSADOR', 90, top=(150, 215, 255), bot=(40, 110, 240), outline=(5, 25, 70))
    return _tc

def setup_title():
    ev(T_TITLE + 0.05, 'block', 0.6, -0.1, pitch=1.2)
    ev(T_TITLE + 0.4, 'block', 0.6, 0.1, pitch=1.0)
    ev(T_TITLE_FLY, 'whoosh', 0.4, 0.0)

def draw_title(cv, t):
    TI = title_imgs()
    b0 = T_TITLE
    if b0 <= t < T_TITLE_FLY + 0.5:
        fly = S.ease_in(S.seg(t, T_TITLE_FLY, T_TITLE_FLY + 0.45))
        ka = S.ease_back(S.seg(t, b0, b0 + 0.35)); kb = S.ease_back(S.seg(t, b0 + 0.3, b0 + 0.65))
        ya = 470 + (S.ROOM_T + 46 - 470) * fly; yb = 590 + (S.ROOM_T + 46 - 590) * fly
        sc = 1 - 0.75 * fly
        S.paste_center(cv, TI['a'], 540, ya, scale=ka * sc, alpha=1 - fly * 0.9)
        S.paste_center(cv, TI['b'], 540, yb, scale=kb * sc, alpha=1 - fly * 0.9)


# ======================= intro: cámara y flash =======================
def draw_camera(cv, t):
    st = cam_state(t)
    if st is None:
        return
    cx, cy, sc, al, xr = st
    fl = 1.0 if T_FLASH <= t < T_FLASH + 0.15 else 0.0
    img = K.camera_img(cam_ready(t), round(xr * 4) / 4, 1.0, fl)
    if t < T_FLASH:
        # en la oscuridad: la luz de "listo" ilumina un poquito
        S.glow_fast(cv, cx - 96 * sc, cy - 0 * sc, 50, (60, 255, 120), 0.5 * cam_ready(t))
    if xr > 0:
        S.glow_fast(cv, cx - 68 * sc, cy + 40 * sc, 120, (255, 220, 90), 0.5 * xr)
    S.paste_center(cv, img, cx, cy, scale=sc, alpha=al)

def flash_pos(t):
    st = cam_state(t)
    if st is None:
        return (CAM_SHOW[0], CAM_SHOW[1])
    return (st[0] + (85 - K.CAM_W / 2) * st[2], st[1] + (38 - K.CAM_H / 2) * st[2])

def draw_flash_overlay(cv, t, tf, strength=1.0, dur=0.8, pos=None):
    if not (tf <= t < tf + dur):
        return
    u = (t - tf) / dur
    a = (1.0 if u < 0.08 else 1 - S.ease_out((u - 0.08) / 0.92)) * strength
    if pos is not None and u < 0.5:
        S.paste_center(cv, K.flash_star(), pos[0], pos[1], scale=0.6 + 1.2 * u, alpha=min(1, 1.6 * (1 - u / 0.5)), angle=u * 0.6)
    if a > 0.01:
        wh = Image.new('RGBA', (W, H), (255, 255, 250, int(255 * a)))
        cv.alpha_composite(wh)


# ======================= escena A: qué es =======================
A = {}
CAPA_C = (700, 575)
BAR_C = (935, 570)

def setup_A():
    A['t'] = P(3) + 0.05
    A['th'] = add_throw(A['t'], CAPA_C, lambda t: K.elec_cap(300), 'l', dur=0.45, arc=170, spin=0.6)
    A['lbl'] = KW(3, 'CAPACITOR') - 0.1
    A['fill'] = KW(3, 'Guarda') - 0.05
    A['dump'] = KW(3, 'golpe') - 0.05
    ev(A['lbl'], 'pop', 0.45, panx(CAPA_C[0]))
    ev(A['fill'], 'whine', 0.18, panx(BAR_C[0]), dur=0.9, f0=500, f1=1500)
    ev(A['dump'], 'zap', 0.5, panx(CAPA_C[0])); ev(A['dump'] + 0.02, 'flash', 0.35, panx(CAPA_C[0]))
    add_slap(T_A_SLAP)

def bar_level_A(t):
    if t < A['fill']:
        return 0.0
    if t < A['dump']:
        return S.ease_io(S.seg(t, A['fill'], A['fill'] + 1.0))
    return 1 - S.ease_out(S.seg(t, A['dump'], A['dump'] + 0.15))

def draw_A(cv, t, at=None):
    if t < A['t'] or t > T_A_SLAP + 1.0:
        return
    if t >= T_A_SLAP and at is None:
        shattered(cv, draw_A, T_A_SLAP, t, 3)
        return
    def place(c, sx, sy):
        S.paste_center(c, K.elec_cap(300), CAPA_C[0], CAPA_C[1], sx=sx, sy=sy)
    draw_thrown(cv, A['th'], t, place)
    if t >= A['lbl']:
        k = S.ease_back(S.seg(t, A['lbl'], A['lbl'] + 0.3))
        S.paste_center(cv, D.label('= CAPACITOR', 34, fill=(170, 220, 255)), CAPA_C[0], 322, scale=k)
    if t >= A['fill'] - 0.3:
        k = S.ease_back(S.seg(t, A['fill'] - 0.3, A['fill']))
        lv = bar_level_A(t)
        S.paste_center(cv, K.energy_bar(round(lv * 20) / 20, 340), BAR_C[0], BAR_C[1], scale=k)
        if A['fill'] <= t < A['dump']:
            S.glow_fast(cv, CAPA_C[0], CAPA_C[1], 130, (255, 220, 80), 0.35 * lv)
    if A['dump'] <= t < A['dump'] + 0.6:
        u = (t - A['dump']) / 0.6
        S.glow_fast(cv, CAPA_C[0], CAPA_C[1], 240, (255, 240, 150), 1.0 - u)
        l = D.L(W, 700)
        rnd = random.Random(4)
        for j in range(14):
            a = rnd.uniform(0, 2 * math.pi); r0 = 60 + 420 * S.ease_out(u); r1 = r0 + 60
            l.line([(CAPA_C[0] + r0 * math.cos(a), 350 + r0 * math.sin(a)), (CAPA_C[0] + r1 * math.cos(a), 350 + r1 * math.sin(a))],
                   (255, 235, 120, int(255 * (1 - u))), 7)
        cv.alpha_composite(l.done(), (0, CAPA_C[1] - 350))


# ======================= escena R: la carrera =======================
R = {}
LANE1, LANE2 = 470, 745
R_X0, R_FIN = 440, 1000

def setup_R():
    R['t'] = P(4) + 0.05
    R['bat_lbl'] = KW(4, 'maratonista') - 0.1
    R['go'] = KW(4, 'velocista') - 0.25
    ev(R['t'], 'pop', 0.4, panx(R_X0)); ev(R['t'] + 0.12, 'pop', 0.4, panx(R_X0))
    ev(R['bat_lbl'], 'tink', 0.3, panx(600), f=2600)
    ev(R['go'], 'whoosh', 0.7, 0.4)
    ev(R['go'] + 0.25, 'zap', 0.35, 0.6)
    add_slap(T_R_SLAP)

def draw_R(cv, t, at=None):
    if t < R['t'] or t > T_R_SLAP + 1.0:
        return
    if t >= T_R_SLAP and at is None:
        shattered(cv, draw_R, T_R_SLAP, t, 5)
        return
    k = S.ease_back(S.seg(t, R['t'], R['t'] + 0.35))
    # pistas y meta
    l = D.L(W, 520)
    for y in (LANE1 + 150, LANE2 + 130):
        l.line([(R_X0 - 60, y - 300), (1040, y - 300)], (255, 255, 255, int(110 * k)), 4)
    for j in range(16):
        col = (255, 255, 255, int(230 * k)) if j % 2 == 0 else (20, 20, 20, int(230 * k))
        l.rect([R_FIN - 8, 40 + j * 28, R_FIN + 8, 40 + j * 28 + 28], fill=col)
    cv.alpha_composite(l.done(), (0, 300))
    # pila maratonista: trota despacito
    bx = R_X0 + 160 * S.seg(t, R['t'], T_R_SLAP)
    bob = abs(math.sin(t * 6)) * 10
    S.paste_center(cv, K.runner_battery(t * 1.6), bx, LANE1 - bob, scale=1.0 * k)
    if t >= R['bat_lbl']:
        a = S.ease_back(S.seg(t, R['bat_lbl'], R['bat_lbl'] + 0.3))
        S.paste_center(cv, D.label('PILA: MARATONISTA', 30, fill=(255, 210, 150)), 810, LANE1 + 10, scale=a)
    # condensador velocista: ¡zuum!
    if t < R['go']:
        cx = R_X0
        S.paste_center(cv, K.elec_cap(200), cx, LANE2, scale=k, angle=0.05 * math.sin(t * 20))
    else:
        u = S.seg(t, R['go'], R['go'] + 0.3)
        cx = R_X0 + (R_FIN + 10 - R_X0) * S.ease_in(u)
        if u < 1:
            S.speed_lines(cv, cx - 60, LANE2 - 40, cx - 340, LANE2 + 40, n=5, color=(255, 230, 120, 200), width=6, seed=3)
        j = S.jelly(t - R['go'] - 0.3, 3, 6) if u >= 1 else 0
        S.paste_center(cv, K.elec_cap(200), cx, LANE2, sx=1 + 0.25 * j, sy=1 - 0.2 * j, angle=-0.25 * (1 - u) if u < 1 else 0)
        if u >= 1:
            a = S.ease_back(S.seg(t, R['go'] + 0.3, R['go'] + 0.6))
            S.paste_center(cv, D.label('¡VELOCISTA!', 34, fill=(255, 240, 120)), 800, LANE2 + 150, scale=a)


# ======================= escena Z: ¿qué tiene por dentro? =======================
Z = {}
def setup_Z():
    Z['t'] = P(5) - 0.05
    Z['zoom0'] = P(6) - 0.35
    Z['zoom1'] = P(6) + 0.1
    ev(Z['t'], 'pop', 0.45, panx(CAPA_C[0]))
    ev(Z['zoom0'], 'whoosh', 0.5, 0.0)

def draw_Z(cv, t):
    if t < Z['t'] or t > Z['zoom1']:
        return
    k = S.ease_back(S.seg(t, Z['t'], Z['t'] + 0.3))
    zoom = S.ease_in(S.seg(t, Z['zoom0'], Z['zoom1']))
    S.paste_center(cv, K.elec_cap(300), CAPA_C[0], CAPA_C[1] - 40 * zoom, scale=k * (1 + 3.0 * zoom), alpha=1 - S.seg(zoom, 0.5, 1.0))
    if zoom == 0:
        a = S.seg(t, Z['t'] + 0.2, Z['t'] + 0.4)
        S.paste_center(cv, D.label('?', 60, fill=(255, 230, 120)), CAPA_C[0] + 140, 360, alpha=a, scale=1 + 0.08 * math.sin(t * 8))


# ======================= escena B: placas, carga y LED =======================
B = {}
PLX_L, PLX_R = 600, 800
PL_Y0, PL_Y1 = 335, 640
BAT_B = (700, 812)
PATH = [(PLX_L, 600), (PLX_L, 700), (470, 700), (470, BAT_B[1]), (575, BAT_B[1]), (825, BAT_B[1]),
        (930, BAT_B[1]), (930, 700), (PLX_R, 700), (PLX_R, 600)]
WIRE_L = [(PLX_L, PL_Y1), (PLX_L, 700), (470, 700), (470, BAT_B[1]), (575, BAT_B[1])]
WIRE_R = [(PLX_R, PL_Y1), (PLX_R, 700), (930, 700), (930, BAT_B[1]), (825, BAT_B[1])]
NMOVE = 6

def plate_img():
    def mk():
        l = D.L(60, PL_Y1 - PL_Y0 + 20)
        l.rrect([8, 4, 52, PL_Y1 - PL_Y0 + 14], 10, fill=K.METAL + (255,), outline=(120, 126, 138, 255), width=4)
        l.rect([16, 14, 24, PL_Y1 - PL_Y0], fill=(255, 255, 255, 90))
        return l.done()
    return K.cached('plate', mk)

def setup_B():
    B['plL'] = KW(6, 'placas') - 0.2
    B['plR'] = B['plL'] + 0.18
    B['ins'] = KW(6, 'AISLANTE') - 0.1
    B['bat'] = P(7) + 0.0
    B['wire0'] = B['bat'] + 0.5
    B['wire1'] = B['wire0'] + 0.5
    B['flow0'] = KW(7, 'amontonan') - 0.25
    B['bounce'] = KW(8, 'cruzar') - 0.05
    B['charged'] = KW(8, 'CARGADO') - 0.1
    B['remove'] = KW(9, 'Quitas') - 0.05
    B['led'] = KW(9, 'LED') - 0.35
    B['on'] = KW(9, 'prende') - 0.05
    B['dim1'] = E(9) + 0.1
    B['thL'] = add_throw(B['plL'], (PLX_L, (PL_Y0 + PL_Y1) / 2), lambda t: plate_img(), 'l', dur=0.4, arc=150, spin=0.3)
    B['thR'] = add_throw(B['plR'], (PLX_R, (PL_Y0 + PL_Y1) / 2), lambda t: plate_img(), 'l', dur=0.4, arc=150, spin=0.3, pitch=1.15)
    B['thB'] = add_throw(B['bat'], BAT_B, lambda t: K.battery_rot(90), 'l', dur=0.45, arc=150, spin=0.5)
    B['thLED'] = add_throw(B['led'], BAT_B, lambda t: D.led_img(0.0), 'l', dur=0.4, arc=150, spin=0.5, land_sfx='pop')
    ev(B['ins'], 'pop', 0.45, panx(700)); ev(B['ins'] + 0.05, 'tink', 0.3, panx(700), f=2200)
    ev(B['wire0'], 'marker', 0.45, 0.0, dur=0.5)
    for k in range(NMOVE):
        ev(B['flow0'] + k * 0.22 + 1.05, 'tink', 0.22, panx(PLX_R), f=3000 + 150 * k)
    for k in range(3):
        ev(B['bounce'] + k * 0.3 + 0.12, 'boing', 0.28, panx(720), f0=240, f1=150)
    ev(B['charged'], 'chime', 0.5, 0.0)
    POINTS.append((B['remove'], B['remove'] + 0.3, 'l', BAT_B))
    ev(B['remove'] + 0.3, 'whoosh', 0.45, -0.3)
    ev(B['on'], 'zap', 0.4, panx(BAT_B[0]))
    ev(B['on'], 'hum', 0.18, panx(BAT_B[0]), dur=B['dim1'] - B['on'], f=110)
    add_slap(T_B_SLAP)

def led_level(t):
    if t < B['on']:
        return 0.0
    u = t - B['on']
    if u < 0.35:
        return 1.0
    return max(0.0, math.exp(-(u - 0.35) * 2.2 / max(0.5, (B['dim1'] - B['on'] - 0.35) / 2.0)) - 0.03)

def electron_layer(t):
    """electrones (azules) y cargas + en las placas"""
    l = D.L(W, 640)
    oy = 280
    rnd = random.Random(2)
    ys = [PL_Y0 + 30 + j * (PL_Y1 - PL_Y0 - 60) / 5 for j in range(6)]
    dur = 1.1
    # cuántos han llegado / vuelto
    def moved(k):
        a = B['flow0'] + k * 0.22
        if t < a:
            return 0.0, None
        u = (t - a) / dur
        if u < 1:
            return u, 'go'
        return 1.0, None
    def returned(k):
        if t < B['on']:
            return 0.0, None
        lv0 = 1 - k / NMOVE           # vuelven en orden mientras el LED se apaga
        a = B['on'] + 0.05 + (B['dim1'] - B['on'] - 0.6) * (k / NMOVE) ** 1.3
        u = (t - a) / 0.8
        if u < 0:
            return 0.0, None
        if u < 1:
            return u, 'back'
        return 1.0, None
    jig = 0.0
    if B['bounce'] <= t < B['bounce'] + 1.0:
        v = (t - B['bounce']) % 0.3
        jig = -18 * math.sin(v / 0.3 * math.pi)
    # electrones fijos (los que no se mueven)
    for j in range(6):
        l.circle((PLX_L - 34, ys[j] - oy), 13, fill=K.ELEC + (255,), outline=(220, 235, 255, 255), width=2)
        l.text((PLX_L - 34, ys[j] - oy - 1), '−', 22, fill=(255, 255, 255))
        l.circle((PLX_R + 34 + jig * 0.5, ys[j] - oy), 13, fill=K.ELEC + (255,), outline=(220, 235, 255, 255), width=2)
        l.text((PLX_R + 34 + jig * 0.5, ys[j] - oy - 1), '−', 22, fill=(255, 255, 255))
    for k in range(NMOVE):
        m, st = moved(k)
        r, st2 = returned(k)
        y_slot = ys[k]
        if st2 == 'back':
            p = D.along(PATH[::-1], r)
            x, y = p
        elif r >= 1:
            x, y = PLX_L + 34, y_slot
        elif st == 'go':
            p = D.along(PATH, m)
            x, y = p
        elif m >= 1:
            x, y = PLX_R - 34 + jig, y_slot
        else:
            x, y = PLX_L + 34, y_slot
        # hueco +: aparece donde se fue el electrón
        if m > 0.15 and not (r >= 1):
            a = min(1.0, (m - 0.15) / 0.3) if r == 0 else max(0.0, 1 - r * 3)
            l.circle((PLX_L + 34, y_slot - oy), 13, fill=K.PLUS + (int(255 * a),))
            l.text((PLX_L + 34, y_slot - oy - 1), '+', 24, fill=(255, 255, 255, int(255 * a)))
        if not (m > 0.15 and (x, y) == (PLX_L + 34, y_slot)):
            l.circle((x, y - oy), 13, fill=K.ELEC + (255,), outline=(220, 235, 255, 255), width=2)
            l.text((x, y - oy - 1), '−', 22, fill=(255, 255, 255))
    return l.done(), oy

def draw_B(cv, t, at=None):
    if t < B['plL'] or t > T_B_SLAP + 1.0:
        return
    if t >= T_B_SLAP and at is None:
        shattered(cv, draw_B, T_B_SLAP, t, 7)
        return
    # aislante
    if t >= B['ins']:
        k = S.ease_back(S.seg(t, B['ins'], B['ins'] + 0.35))
        l = D.L(160, PL_Y1 - PL_Y0)
        l.rrect([0, 0, 160 * k, PL_Y1 - PL_Y0], 10, fill=K.INSUL + (95,), outline=K.INSUL + (200,), width=3)
        for yy in range(10, PL_Y1 - PL_Y0, 28):
            l.line([(10, yy), (min(150, 150 * k), yy + 14)], K.INSUL + (90,), 3)
        cv.alpha_composite(l.done(), (int(700 - 80 * k), PL_Y0))
        a = S.seg(t, B['ins'] + 0.1, B['ins'] + 0.4) * (1 - S.seg(t, B['charged'] - 0.2, B['charged']))
        if a > 0:
            S.paste_center(cv, D.label('AISLANTE', 32, fill=K.INSUL), 700, 322, alpha=a, scale=S.ease_back(min(1, a * 1.2)))
    # campo (energía guardada) entre las placas
    charge = S.seg(t, B['flow0'] + 0.6, B['flow0'] + 0.6 + NMOVE * 0.22)
    if t >= B['on']:
        charge *= led_level(t) * 0.9 + 0.1 * (1 - S.seg(t, B['on'], B['dim1']))
    if charge > 0.02:
        l = D.L(W, PL_Y1 - PL_Y0)
        for j in range(7):
            y = 20 + j * (PL_Y1 - PL_Y0 - 40) / 6
            off = (t * 120) % 30
            for xx in range(int(PLX_R - 60), int(PLX_L + 50), -30):
                x = xx - off
                if PLX_L + 50 < x < PLX_R - 50:
                    l.line([(x, y), (x - 14, y)], K.CURR + (int(200 * charge),), 4)
        cv.alpha_composite(l.done(), (0, PL_Y0))
        S.glow_fast(cv, 700, (PL_Y0 + PL_Y1) / 2, 140, (255, 220, 90), 0.35 * charge)
    # placas
    def placeL(c, sx, sy):
        S.paste_center(c, plate_img(), PLX_L, (PL_Y0 + PL_Y1) / 2, sx=sx, sy=sy)
    def placeR(c, sx, sy):
        S.paste_center(c, plate_img(), PLX_R, (PL_Y0 + PL_Y1) / 2, sx=sx, sy=sy)
    draw_thrown(cv, B['thL'], t, placeL)
    draw_thrown(cv, B['thR'], t, placeR)
    # cables
    if t >= B['wire0']:
        u = S.seg(t, B['wire0'], B['wire1'])
        l = D.L(W, 700)
        wire_partial(l, WIRE_L, u, D.WIRE, 9, oy=250)
        wire_partial(l, WIRE_R, u, D.WIRE, 9, oy=250)
        cv.alpha_composite(l.done(), (0, 250))
    # pila (luego se la quitan) o LED
    if t < B['remove'] + 0.3:
        def placeB(c, sx, sy):
            S.paste_center(c, K.battery_rot(90), BAT_B[0], BAT_B[1], sx=sx, sy=sy)
        draw_thrown(cv, B['thB'], t, placeB)
    elif t < B['remove'] + 0.9:
        u = S.seg(t, B['remove'] + 0.3, B['remove'] + 0.9)
        x = BAT_B[0] + (-200 - BAT_B[0]) * S.ease_in(u)
        y = BAT_B[1] - 500 * math.sin(u * math.pi * 0.8)
        S.paste_center(cv, K.battery_rot(90), x, y, angle=u * 5)
    lv = led_level(t)
    def placeLED(c, sx, sy):
        S.paste_center(c, D.led_img(round(lv * 20) / 20), BAT_B[0], BAT_B[1] - 20, sx=sx * 0.62, sy=sy * 0.62)
        if lv > 0.02:
            S.glow_fast(c, BAT_B[0], BAT_B[1] - 20, 200, (255, 80, 80), 0.6 * lv)
    draw_thrown(cv, B['thLED'], t, placeLED)
    # electrones
    if t >= B['plR'] + 0.4:
        a = S.seg(t, B['plR'] + 0.4, B['plR'] + 0.7)
        lay, oy = electron_layer(t)
        S.paste_center(cv, lay, W / 2, oy + lay.size[1] / 2, alpha=a)
    if t >= B['charged']:
        a = S.ease_back(S.seg(t, B['charged'], B['charged'] + 0.3)) * (1 - S.seg(t, B['remove'] - 0.2, B['remove']))
        if a > 0:
            S.paste_center(cv, D.label('CARGADO ✓', 36, fill=K.GREEN), 700, 322, scale=a)
    if B['flow0'] <= t < B['charged']:
        a = S.seg(t, B['flow0'], B['flow0'] + 0.3) * (1 - S.seg(t, B['charged'] - 0.3, B['charged']))
        S.paste_center(cv, D.label('−  −  −', 30, fill=(170, 210, 255)), PLX_R + 120, 322, alpha=a)
        S.paste_center(cv, D.label('+  +  +', 30, fill=(255, 180, 180)), PLX_L - 120, 322, alpha=a)


# ======================= escena F: faradios =======================
Fd = {}
FAR_C = (700, 520)
def setup_F():
    Fd['drop'] = KW(10, 'FARADIOS') - 0.35
    Fd['land'] = Fd['drop'] + 0.35
    Fd['big'] = KW(10, 'muchísimo') - 0.1
    Fd['micro'] = KW(10, 'microfaradios') - 0.2
    ev(Fd['drop'], 'whoosh', 0.45, 0.2)
    ev(Fd['land'], 'thud', 0.9, panx(FAR_C[0])); ev(Fd['land'] + 0.02, 'block', 0.6, panx(FAR_C[0]), pitch=0.6)
    SHAKES.append((Fd['land'], 0.35, 14))
    ev(Fd['big'], 'boing', 0.35, 0.2, f0=160, f1=90)
    ev(Fd['micro'], 'squeak', 0.4, 0.2); ev(Fd['micro'] + 0.25, 'pop', 0.5, 0.2)
    add_slap(T_F_SLAP)

def draw_F(cv, t, at=None):
    if t < Fd['drop'] or t > T_F_SLAP + 1.0:
        return
    if t >= T_F_SLAP and at is None:
        shattered(cv, draw_F, T_F_SLAP, t, 8)
        return
    if t < Fd['micro'] + 0.25:
        if t < Fd['land']:
            u = S.ease_in(S.seg(t, Fd['drop'], Fd['land']))
            y = -150 + (FAR_C[1] + 150) * u
            S.paste_center(cv, K.big_farad(), FAR_C[0], y, sx=0.9, sy=1.1)
        else:
            j = S.jelly(t - Fd['land'], 3, 5)
            pulse = 1 + 0.12 * S.jelly(t - Fd['big'], 2.5, 3) if t >= Fd['big'] else 1.0
            shrink = 1 - S.ease_in(S.seg(t, Fd['micro'], Fd['micro'] + 0.25))
            S.paste_center(cv, K.big_farad(), FAR_C[0], FAR_C[1] + 30 * j * shrink, sx=(1 + 0.2 * j) * pulse * max(0.01, shrink),
                           sy=(1 - 0.2 * j) * pulse * max(0.01, shrink))
    if t >= Fd['micro'] + 0.2:
        k = S.ease_back(S.seg(t, Fd['micro'] + 0.2, Fd['micro'] + 0.5))
        S.paste_center(cv, K.micro_f(), FAR_C[0], FAR_C[1], scale=k)
        a = S.seg(t, Fd['micro'] + 0.5, Fd['micro'] + 0.8)
        S.paste_center(cv, D.label('1 µF = 0,000001 F', 34, fill=(200, 230, 255)), FAR_C[0], FAR_C[1] + 140, alpha=a)


# ======================= escena T: tipos =======================
T = {}
TYPE_C = (720, 610)
SHELF = (450, 430)

def setup_T():
    T['cer'] = KW(11, 'CERÁMICO') - 0.3
    T['flip'] = KW(11, 'cualquier') - 0.1
    T['elec'] = KW(12, 'ELECTROLÍTICO') - 0.3
    T['shelf'] = T['elec'] - 0.15
    T['lado'] = KW(12, 'tiene lado') - 0.05
    T['neg'] = KW(12, 'franja') - 0.1
    T['rev'] = KW(13, 'revés') - 0.15
    T['infla'] = KW(13, 'infla') - 0.1
    T['cruz'] = KW(13, 'cruz') - 0.15
    T['thC'] = add_throw(T['cer'], TYPE_C, lambda t: K.ceramic_cap(240), 'l', dur=0.4, arc=160, spin=0.8)
    T['thE'] = add_throw(T['elec'], TYPE_C, lambda t: K.elec_cap(320), 'l', dur=0.45, arc=160, spin=0.6)
    ev(T['flip'], 'whoosh', 0.3, panx(TYPE_C[0])); ev(T['flip'] + 0.45, 'chime', 0.35, panx(TYPE_C[0]))
    ev(T['shelf'], 'whoosh', 0.3, -0.2); ev(T['shelf'] + 0.3, 'block', 0.4, panx(SHELF[0]), pitch=1.4)
    ev(T['lado'], 'pop', 0.4, panx(640)); ev(T['neg'], 'tink', 0.45, panx(800), f=2800)
    ev(T['rev'], 'buzz', 0.35, panx(TYPE_C[0]))
    ev(T['infla'], 'hiss', 0.45, panx(TYPE_C[0]), dur=T_POOF - T['infla'])
    ev(T_POOF, 'poof', 1.0, panx(TYPE_C[0]))
    SHAKES.append((T_POOF, 0.45, 18))
    ev(T['cruz'], 'pop', 0.45, panx(TYPE_C[0]))
    add_slap(T_T_SLAP)

def swell_at(t):
    if t < T['infla']:
        return 0.0
    return S.ease_in(S.seg(t, T['infla'], T_POOF))

def draw_T(cv, t, at=None):
    if t < T['cer'] or t > T_T_SLAP + 1.0:
        return
    if t >= T_T_SLAP and at is None:
        shattered(cv, draw_T, T_T_SLAP, t, 9)
        return
    # ---- cerámico ----
    if t < T['shelf']:
        ang = math.pi * S.ease_io(S.seg(t, T['flip'], T['flip'] + 0.45))
        def place(c, sx, sy):
            S.paste_center(c, K.ceramic_cap(240), TYPE_C[0], TYPE_C[1], sx=sx, sy=sy, angle=ang)
        draw_thrown(cv, T['thC'], t, place)
        if t >= T['cer'] + 0.45:
            a = S.ease_back(S.seg(t, T['cer'] + 0.45, T['cer'] + 0.75))
            S.paste_center(cv, D.label('CERÁMICO', 34, fill=(255, 190, 130)), TYPE_C[0], 322, scale=a)
        if t >= T['flip'] + 0.45:
            a = S.ease_back(S.seg(t, T['flip'] + 0.45, T['flip'] + 0.75))
            S.paste_center(cv, D.label('SIN LADO ✓', 32, fill=K.GREEN), TYPE_C[0], 790, scale=a)
    else:
        u = S.ease_io(S.seg(t, T['shelf'], T['shelf'] + 0.3))
        x = TYPE_C[0] + (SHELF[0] - TYPE_C[0]) * u; y = TYPE_C[1] + (SHELF[1] - TYPE_C[1]) * u
        S.paste_center(cv, K.ceramic_cap(240), x, y, scale=1 - 0.6 * u, angle=math.pi)
    # ---- electrolítico ----
    if t >= T['elec'] and t < T['cruz']:
        sw = swell_at(t)
        tr = 6 * sw * math.sin(t * 70)
        rev = S.ease_io(S.seg(t, T['rev'], T['rev'] + 0.3))
        if t < T_POOF:
            def place(c, sx, sy):
                S.paste_center(c, K.elec_cap(320, round(sw * 10) / 10, 1.0 if (t >= T['neg'] and int(t * 6) % 2 == 0 and t < T['rev']) else 0.0),
                               TYPE_C[0] + tr, TYPE_C[1], sx=sx, sy=sy)
            draw_thrown(cv, T['thE'], t, place)
        else:
            # ¡PUM!: la tapa sale volando y queda el humo
            u = t - T_POOF
            S.paste_center(cv, K.elec_cap(320, 1.0, 0.0, min(1.0, u * 1.5)), TYPE_C[0], TYPE_C[1], alpha=1 - S.seg(u, 0.5, 0.8))
            S.paste_center(cv, K.smoke(min(1.0, u * 1.6)), TYPE_C[0], TYPE_C[1] - 160 - 80 * u, scale=1.2, alpha=1 - S.seg(u, 0.6, 1.1))
            if u < 0.8:
                k = S.ease_back(S.seg(u, 0.0, 0.15), 2.5) * (1 - S.seg(u, 0.55, 0.8))
                S.paste_center(cv, K.pum_text(), TYPE_C[0] + 60, 400, scale=k, angle=-0.1)
            if u < 0.3:
                S.glow_fast(cv, TYPE_C[0], TYPE_C[1] - 120, 260, (255, 200, 120), 1 - u / 0.3)
        if T['elec'] + 0.5 <= t < T['rev']:
            a = S.ease_back(S.seg(t, T['elec'] + 0.5, T['elec'] + 0.8))
            S.paste_center(cv, D.label('ELECTROLÍTICO', 34, fill=(160, 200, 255)), TYPE_C[0], 322, scale=a)
        if T['lado'] <= t < T['rev']:
            a = S.ease_back(S.seg(t, T['lado'], T['lado'] + 0.3))
            S.paste_center(cv, D.label('+ pata larga', 28, fill=(255, 190, 190)), TYPE_C[0] - 170, 760, scale=a)
        if T['neg'] <= t < T['rev']:
            a = S.ease_back(S.seg(t, T['neg'], T['neg'] + 0.3))
            S.paste_center(cv, D.label('− NEGATIVO', 30, fill=(190, 215, 255)), TYPE_C[0] + 190, 470, scale=a)
        if T['rev'] <= t < T_POOF:
            S.paste_center(cv, D.label('¡AL REVÉS!', 34, fill=K.RED), TYPE_C[0], 322, scale=S.ease_back(S.seg(t, T['rev'], T['rev'] + 0.3)))
            S.paste_center(cv, K.battery_rot(-90), TYPE_C[0], 820, scale=0.7 * rev, angle=0.04 * math.sin(t * 30) * sw)
    # ---- la cruz de seguridad (vista de arriba) ----
    if t >= T['cruz']:
        k = S.ease_back(S.seg(t, T['cruz'], T['cruz'] + 0.35))
        hl = 1.0 if int((t - T['cruz']) * 4) % 2 == 0 else 0.0
        S.paste_center(cv, K.elec_top(hl), TYPE_C[0], TYPE_C[1], scale=k)
        a = S.ease_back(S.seg(t, T['cruz'] + 0.3, T['cruz'] + 0.6))
        S.paste_center(cv, D.label('VÁLVULA DE SEGURIDAD', 32, fill=(255, 220, 120)), TYPE_C[0], 760, scale=a)


# ======================= escena S: supercondensador =======================
Sp = {}
def setup_S():
    Sp['land'] = T_SUPER + 0.4
    Sp['count'] = KW(14, 'miles') - 0.1
    ev(T_SUPER, 'whoosh', 0.5, 0.2)
    ev(Sp['land'], 'thud', 1.0, panx(TYPE_C[0])); ev(Sp['land'] + 0.03, 'thump2', 0.8, panx(TYPE_C[0]))
    SHAKES.append((Sp['land'], 0.5, 22))
    for k in range(8):
        ev(Sp['count'] + k * 0.1, 'tink', 0.2, 0.3, f=2000 + 220 * k)
    ev(Sp['count'] + 0.85, 'chime', 0.45, 0.3)
    add_slap(T_S_SLAP)

def draw_S(cv, t, at=None):
    if t < T_SUPER or t > T_S_SLAP + 1.0:
        return
    if t >= T_S_SLAP and at is None:
        shattered(cv, draw_S, T_S_SLAP, t, 10)
        return
    if t < Sp['land']:
        u = S.ease_in(S.seg(t, T_SUPER, Sp['land']))
        S.paste_center(cv, K.supercap(), TYPE_C[0], -300 + (TYPE_C[1] + 300) * u, sx=0.92, sy=1.08)
    else:
        j = S.jelly(t - Sp['land'], 3, 6)
        S.paste_center(cv, K.supercap(), TYPE_C[0], TYPE_C[1] + 20 * j, sx=1 + 0.12 * j, sy=1 - 0.12 * j)
        if t - Sp['land'] < 0.4:
            u = (t - Sp['land']) / 0.4
            S.paste_center(cv, K.smoke(0.3 + u, 7), TYPE_C[0] - 200, S.FLOOR_Y - 600, alpha=0.6 * (1 - u), scale=0.6)
    if t >= Sp['count']:
        u = S.ease_out(S.seg(t, Sp['count'], Sp['count'] + 0.85))
        n = int(1 + 2999 * u)
        n = n - n % 10 if n > 20 else n
        txt = f'{n:,}'.replace(',', '.') + ' F'
        a = S.ease_back(S.seg(t, Sp['count'], Sp['count'] + 0.3))
        S.paste_center(cv, D.label(txt, 54, fill=(255, 235, 120)), TYPE_C[0], 900, scale=a * (1 + 0.1 * S.jelly(t - Sp['count'] - 0.85, 3, 5) if u >= 1 else a))


# ======================= escena M: el más común (celular) =======================
M = {}
PH_C = (720, 625)
def setup_M():
    M['q'] = P(15) + 0.05
    M['phone'] = KW(15, 'celular') - 0.25
    M['many'] = KW(15, 'cientos') - 0.05
    M['sand'] = KW(15, 'grano') - 0.3
    ev(M['q'], 'pop', 0.4, panx(700))
    M['th'] = add_throw(M['phone'], PH_C, lambda t: K.phone_board(0.0), 'l', dur=0.45, arc=160, spin=0.4)
    for k in range(10):
        ev(M['many'] + k * 0.06, 'tink', 0.13, -0.4 + 0.1 * k, f=3200 + 120 * k)
    ev(M['sand'], 'whoosh', 0.35, 0.3); ev(M['sand'] + 0.3, 'pop', 0.45, 0.3)
    add_slap(T_M_SLAP)

def draw_M(cv, t, at=None):
    if t < M['q'] or t > T_M_SLAP + 1.0:
        return
    if t >= T_M_SLAP and at is None:
        shattered(cv, draw_M, T_M_SLAP, t, 12)
        return
    a = S.ease_back(S.seg(t, M['q'], M['q'] + 0.3))
    S.paste_center(cv, D.label('EL MÁS COMÚN', 34, fill=(255, 220, 120)), 700, 322, scale=a)
    if t < M['phone']:
        S.paste_center(cv, K.ceramic_cap(200), PH_C[0], PH_C[1], scale=a * (1 + 0.05 * math.sin(t * 6)))
    tw = (t * 0.8) if t >= M['many'] else 0.0
    def place(c, sx, sy):
        S.paste_center(c, K.phone_board(round(tw % 1.0, 1)), PH_C[0], PH_C[1], sx=sx * 0.84, sy=sy * 0.84)
    draw_thrown(cv, M['th'], t, place)
    if t >= M['many']:
        k = S.ease_back(S.seg(t, M['many'], M['many'] + 0.3))
        S.paste_center(cv, D.label('CIENTOS', 30, fill=(255, 235, 190)), PH_C[0] - 210, 450, scale=k)
    if t >= M['sand']:
        k = S.ease_back(S.seg(t, M['sand'] + 0.15, M['sand'] + 0.5))
        S.paste_center(cv, D.magnifier(K.sand_vs_mlcc(), r=150), PH_C[0] + 150, PH_C[1] + 110, scale=k)


# ======================= escena Kc: el flash y el ¡ojo! =======================
Kc = {}
CAM2 = (700, 450)
VM_C = (700, 740)
def setup_K():
    Kc['cam'] = P(16) + 0.0
    Kc['ch0'] = KW(16, 'cargándose') - 0.1
    Kc['ch1'] = T_FLASH2 - 0.15
    Kc['warn'] = P(17) + 0.05
    Kc['th'] = add_throw(Kc['cam'], CAM2, lambda t: K.camera_img(0.0, 1.0, 1.0), 'l', dur=0.45, arc=160, spin=0.4)
    ev(Kc['ch0'], 'whine', 0.45, panx(CAM2[0]), dur=Kc['ch1'] - Kc['ch0'] + 0.1)
    ev(T_FLASH2, 'flash', 1.0, panx(CAM2[0]))
    ev(Kc['warn'], 'buzz', 0.4, 0.2); ev(Kc['warn'] + 0.05, 'pop', 0.4, 0.2)
    add_slap(T_K_SLAP)

def volts_K(t):
    if t < Kc['ch0']:
        return 0.0
    if t < T_FLASH2:
        return 300 * S.ease_out(S.seg(t, Kc['ch0'], Kc['ch1']))
    if t < Kc['warn']:
        return 300 * (1 - S.ease_out(S.seg(t, T_FLASH2, T_FLASH2 + 0.12)))
    return 280.0       # puede seguir cargado

def draw_K(cv, t, at=None):
    if t < Kc['cam'] or t > T_K_SLAP + 1.0:
        return
    if t >= T_K_SLAP and at is None:
        shattered(cv, draw_K, T_K_SLAP, t, 13)
        return
    v = volts_K(t)
    ready = 1.0 if (v >= 299 or t >= Kc['warn']) else 0.0
    fl = 1.0 if T_FLASH2 <= t < T_FLASH2 + 0.15 else 0.0
    def place(c, sx, sy):
        S.paste_center(c, K.camera_img(ready, 1.0, round(v / 300, 1), fl), CAM2[0], CAM2[1], sx=sx * 1.2, sy=sy * 1.2)
        S.glow_fast(c, CAM2[0] - 82, CAM2[1] + 22, 110, (255, 220, 80), 0.5 * v / 300)
    draw_thrown(cv, Kc['th'], t, place)
    if t >= Kc['ch0'] - 0.3:
        k = S.ease_back(S.seg(t, Kc['ch0'] - 0.3, Kc['ch0']))
        S.paste_center(cv, K.volt_meter(round(v / 10) * 10), VM_C[0], VM_C[1], scale=k)
    if T_FLASH2 <= t < T_FLASH2 + 0.5 and at is None:
        u = (t - T_FLASH2) / 0.5
        S.paste_center(cv, K.flash_star(), CAM2[0] - 130, CAM2[1] - 100, scale=0.5 + 1.0 * u, alpha=1 - u)
        S.paste_center(cv, D.label('0,001 s', 34, fill=(255, 255, 200)), CAM2[0] + 170, CAM2[1] - 170, alpha=1 - S.seg(u, 0.7, 1.0))
    if t >= Kc['warn']:
        k = S.ease_back(S.seg(t, Kc['warn'], Kc['warn'] + 0.35))
        S.paste_center(cv, K.warning_sign(), 930, 600, scale=0.55 * k, angle=0.06 * math.sin(t * 5))
        a = S.ease_back(S.seg(t, Kc['warn'] + 0.3, Kc['warn'] + 0.6))
        S.paste_center(cv, D.label('¡PELIGRO!', 32, fill=(255, 210, 60)), 700, 322, scale=a)


# ======================= chispa del remate =======================
def draw_spark(cv, t):
    a, b = KW(18, 'chispa') - 0.2, E(18) + 0.4
    if not (a <= t < b):
        return
    hx, hy = hand_pos(t, 'l')
    k = S.ease_back(S.seg(t, a, a + 0.25)) * (1 - S.seg(t, b - 0.2, b))
    S.glow_fast(cv, hx, hy - 40, 90, (255, 230, 120), 0.7 * k)
    S.paste_center(cv, K.spark(46), hx, hy - 40, scale=k * (1 + 0.15 * math.sin(t * 20)), angle=t * 3)


# ======================= cierre: botones y pregunta =======================
Fin = {}
BTN = {'like': (770, 600), 'sub': (770, 735), 'follow': (770, 870)}

def setup_Fin():
    Fin['btn_in'] = P(19) - 0.6
    Fin['hit'] = {'like': KW(19, 'me gusta'), 'sub': KW(19, 'suscríbete'), 'follow': KW(19, 'sígueme')}
    Fin['q'] = P(20) + 0.1
    for i, k in enumerate(('like', 'sub', 'follow')):
        ev(Fin['btn_in'] + i * 0.1, 'pop', 0.35, 0.4)
        th = Fin['hit'][k]
        JUMPS.append((th - 0.3, 0.55, 70))
        POINTS.append((th - 0.12, th + 0.08, 'l', (lambda kk: (lambda t: (BTN[kk][0] - 180, BTN[kk][1])))(k)))
        ev(th, 'click', 0.6, 0.5); ev(th + 0.02, 'pop', 0.4, 0.5, f0=600, f1=1400)
        if k == 'sub':
            ev(th + 0.05, 'bell', 0.6, 0.5)
        ev(th - 0.3 + 0.55, 'step', 0.5, panx(300))
    ev(Fin['q'], 'whine', 0.25, panx(420), dur=1.2, f0=600, f1=1800)
    ev(Fin['q'] + 0.05, 'block', 0.4, panx(420))
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
    # condensador misterioso que se va cargando: el capítulo 6
    if Fin['q'] <= t < T_END_SNAP + 0.4:
        k = S.ease_back(S.seg(t, Fin['q'], Fin['q'] + 0.35)) * (1 - S.ease_in(S.seg(t, T_END_SNAP + 0.05, T_END_SNAP + 0.35)))
        lv = S.seg(t, Fin['q'], Fin['q'] + 1.2)
        S.glow_fast(cv, 420, 480, 150, (255, 220, 90), 0.4 * lv * k)
        S.paste_center(cv, K.elec_cap(260, q=True), 420, 480, scale=0.85 * k, angle=0.05 * math.sin((t - Fin['q']) * 6))
        S.paste_center(cv, D.label('CAP. 6', 26, fill=(255, 220, 120)), 420, 680, alpha=S.seg(t, Fin['q'] + 0.2, Fin['q'] + 0.4) * k)


# ======================= intro: sonidos =======================
def schedule_intro_sfx():
    ev(0.0, 'whine', 0.55, panx(cam_hold_pt(0)[0]), dur=T_FLASH + 0.02, f0=900, f1=5200)
    for k in range(int(T_FLASH / 0.32)):
        ev(0.05 + k * 0.32, 'beep', 0.08, 0.3)
    ev(T_FLASH, 'flash', 1.0, panx(cam_hold_pt(0)[0]))
    ev(T_FLASH + 0.04, 'switch', 0.45, 0.0)
    JUMPS.append((T_FLASH + 0.02, 0.4, 45))
    ev(T_FLASH + 0.42, 'step', 0.5, panx(INTRO_X), heavy=1.0)
    ev(T_PRESENT, 'whoosh', 0.4, 0.3)
    ev(KW(1, 'adentro') - 0.15, 'zap', 0.3, 0.3)
    ev(T_TITLE - 0.2, 'pop', 0.45, 0.3)
    # cambio a laboratorio
    ev(T_SNAP_LAB, 'snap', 0.9, panx(INTRO_X))
    ev(T_FLIP0, 'whoosh', 0.5, 0.0)
    for k in range(14):
        ev(T_FLIP0 + 0.04 + k * 0.055, 'block', 0.22, -0.8 + 0.12 * k, pitch=0.9 + 0.04 * k)
    ev(T_FLIP0 + 0.75 + 0.45, 'thud', 0.6, -0.5); ev(T_FLIP0 + 0.75 + 0.45, 'block', 0.5, -0.5, pitch=0.8)
    ev(T_FLIP0 + 0.87 + 0.45, 'thud', 0.6, 0.0)
    for k in range(4):
        ev(T_FLIP0 + 1.07 + 0.35 + k * 0.07, 'pop', 0.3, -0.2 + 0.2 * k, f0=500 + 150 * k, f1=1300)
    ev(T_LAB_DONE, 'chime', 0.45, 0.0)


def setup_all():
    setup_walks()
    schedule_intro_sfx()
    setup_title()
    setup_A()
    setup_R()
    setup_Z()
    setup_B()
    setup_F()
    setup_T()
    setup_S()
    setup_M()
    setup_K()
    setup_Fin()
    react = [
        (T_TITLE - 0.05, 0.7, 110, 'spin'),               # título
        (KW(2, 'LABORATORIO') - 0.05, 0.5, 80, 'up'),     # ¡laboratorio!
        (A['dump'] + 0.05, 0.4, 50, 'up'),                # ¡de golpe!
        (R['go'] + 0.3, 0.45, 60, 'up'),                  # ¡velocista!
        (B['charged'] + 0.05, 0.45, 60, 'up'),            # ¡cargado!
        (B['on'] + 0.05, 0.45, 70, 'thumbs'),             # ¡prende!
        (Fd['big'] + 0.05, 0.4, 0, None),
        (T_POOF + 0.02, 0.7, 40, 'cover'),                # ¡PUM!
        (Sp['land'] + 0.02, 0.4, 70, None),               # el súper cae
        (Sp['count'] + 0.9, 0.45, 60, 'up'),              # ¡miles!
        (M['sand'] + 0.3, 0.4, 50, None),                 # grano de arena
        (T_FLASH2 + 0.02, 0.4, 50, 'cover'),              # flash
    ]
    for t0, d, h, kind in react:
        if h > 0:
            JUMPS.append((t0, d, h))
            ev(t0 + d, 'step', 0.45, 0.0, heavy=0.9)
        if kind == 'spin':
            SPINS.append((t0, d)); ev(t0, 'whoosh', 0.3, 0.0)
        if kind:
            REACT_ARMS.append((t0, d, kind))
    POINTS.append((KW(18, 'chispa') - 0.2, E(18) + 0.3, 'l', lambda t: (HOME_X + 170, 760)))

setup_all()

_bg = {}
def bg_at(t, light):
    if 'stone' not in _bg:
        _bg['stone'] = S.lit_room().convert('RGBA')
        _bg['stone_np'] = np.array(_bg['stone'].convert('RGB'), np.float32)
    if t < T_FLIP0:
        base, arr = _bg['stone'], _bg['stone_np']
    elif t < T_LAB_DONE:
        return LB.transition(_bg['stone'], t, T_FLIP0, (INTRO_X, 760))
    else:
        L = LB.layers(); base, arr = L['full'], L['full_np']
    if light >= 0.999:
        return base.copy()
    if light <= 0.001:
        return Image.new('RGBA', (W, H), (0, 0, 0, 255))
    return Image.fromarray((arr * light).astype(np.uint8), 'RGB').convert('RGBA')


def render_frame(t):
    pose, x, yf, light, glow = char_state(t)
    cv = bg_at(t, light)
    if t >= T_LAB_DONE:
        LB.draw_anim(cv, t, light)
    sw = 0.0
    if t >= T_END_SNAP:
        sw = 0.04 * math.sin((t - T_END_SNAP) * 5) * math.exp(-(t - T_END_SNAP))
    for t0 in (T_FLASH, T_POOF, Sp['land'], Fd['land']):
        if t0 <= t < t0 + 1.4:
            sw += 0.06 * math.sin((t - t0) * 7) * math.exp(-(t - t0) * 2.5)
    S.draw_lamp(cv, on=light, swing=sw)
    if light > 0.05:
        S.glow_fast(cv, S.LAMP_X + math.sin(sw) * S.LAMP_Y, math.cos(sw) * S.LAMP_Y + 22, 90, (255, 230, 150), 0.6 * light)
    if t >= T_TITLE_FLY + 0.4 and t < T_END_SNAP + 0.1:
        S.draw_label(cv, LABEL_TXT, alpha=S.seg(t, T_TITLE_FLY + 0.4, T_TITLE_FLY + 0.6) * light)
    draw_title(cv, t)
    # ----- escenas -----
    draw_A(cv, t)
    draw_R(cv, t)
    draw_Z(cv, t)
    draw_B(cv, t)
    draw_F(cv, t)
    draw_T(cv, t)
    draw_S(cv, t)
    draw_M(cv, t)
    draw_K(cv, t)
    # ----- sombra -----
    if light > 0.05:
        h = S.FLOOR_Y - yf
        sh_w = 150 * max(0.4, 1 - h / 600)
        d = ImageDraw.Draw(cv, 'RGBA')
        d.ellipse([x - sh_w, S.FLOOR_Y - 14, x + sh_w, S.FLOOR_Y + 12], fill=(0, 0, 0, int(110 * light * max(0.3, 1 - h / 500))))
    # ----- personaje -----
    char_light = 0.32 + 0.68 * light if t < T_END_SNAP + 1.3 else 0.32
    if t < T_FLASH:
        char_light = 0.42
    CH.render(cv, pose, dict(scale=S.SCALE, ox=x, oy=yf, view_yaw=0.12 * math.sin(t * 0.2)), light=char_light, t=t)
    draw_camera(cv, t)
    draw_spark(cv, t)
    draw_Fin(cv, t)
    # ----- flashes -----
    draw_flash_overlay(cv, t, T_FLASH, 1.0, 0.9, flash_pos(T_FLASH))
    draw_flash_overlay(cv, t, T_FLASH2, 0.75, 0.45)
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
