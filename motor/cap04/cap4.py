#!/usr/bin/env python3
# Capítulo 4: El diodo. Vertical 1080x1920, 30 fps.
# Intro (gancho en el segundo 0): corre y atraviesa una puerta-diodo gigante; se devuelve y ¡BONK!
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
import diodo as DD
import char3d as C
from timeline import TL, PHRASES

W, H = S.W, S.H
FPS = S.FPS
CH = C.Character()
HOME_X = 230
LABEL_TXT = 'CAP. 4 · EL DIODO'

P = lambda i: TL.s(i)
E = lambda i: TL.e(i)
KW = TL.kw

# ======================= tiempos clave =======================
T_PASS = 0.62                     # atraviesa la puerta
T_ARR = 0.95                      # llega al otro lado y frena
T_RUN2 = E(0) - 0.05              # corre de vuelta
T_BONK = E(0) + 0.28              # ¡BONK!
T_PEEL = T_BONK + 0.55            # se despega
T_SIT = T_PEEL + 0.35             # queda sentado
T_UP = KW(1, 'Capítulo') - 0.45   # se levanta
T_TITLE = KW(1, 'Capítulo')       # título
T_TITLE_FLY = E(1) + 0.3
T_A_SLAP = None                   # el diodo no se rompe: se hace zoom
T_B_SLAP = E(8) + 0.4
T_C_SLAP = E(10) + 0.35
T_D_SLAP = KW(12, 'Pero') - 0.05
T_E_SLAP = E(17) + 0.3
T_END_SNAP = E(19) + 0.5
T_END = TL.END
T_SNAP = 0.0                      # (compatibilidad)
T_LIGHT = 0.0

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
    (0.0, 'feliz'), (T_ARR, 'guino'), (T_RUN2, 'feliz'), (T_BONK, 'sorpresa'), (T_PEEL + 0.2, 'mareado'),
    (P(1), 'feliz'), (T_TITLE, 'feliz'),
    (P(2), 'curioso'), (KW(2, 'solo sentido'), 'feliz'), (KW(2, 'bloquea'), 'sorpresa'), (E(2), 'guino'),
    (P(3), 'feliz'), (KW(3, 'rayita'), 'guino'),
    (P(4), 'pensando'), (P(5), 'curioso'), (KW(5, 'huecos'), 'feliz'), (KW(5, 'electrones de sobra'), 'feliz'),
    (P(6), 'pensando'), (KW(6, 'BARRERA'), 'sorpresa'),
    (P(7), 'curioso'), (KW(7, '0,7'), 'pensando'), (KW(7, 'cruzan'), 'feliz'), (E(7), 'corazon'),
    (P(8), 'curioso'), (KW(8, 'crece'), 'sorpresa'), (KW(8, 'no pasa'), 'pensando'),
    (P(9), 'feliz'), (KW(9, 'prende'), 'corazon'), (P(10), 'guino'), (KW(10, 'apaga'), 'sorpresa'), (E(10) + 0.2, 'feliz'),
    (P(11), 'curioso'), (KW(11, 'celular'), 'feliz'), (KW(11, 'directa'), 'corazon'),
    (P(12), 'feliz'), (KW(12, 'superpoderes'), 'sorpresa'),
    (P(13), 'feliz'), (KW(13, 'como luz'), 'sorpresa'), (KW(13, 'color'), 'corazon'),
    (P(14), 'pensando'), (KW(14, 'fijo'), 'guino'),
    (P(15), 'curioso'), (KW(15, 'rapidísimo'), 'sorpresa'),
    (P(16), 'pensando'), (KW(16, 'si le llega'), 'curioso'), (KW(16, 'deja pasar corriente'), 'feliz'), (KW(16, 'Así tu tele'), 'sorpresa'),
    (P(17), 'feliz'), (P(18), 'feliz'), (P(19), 'curioso'), (KW(19, 'Nos vemos'), 'guino'),
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


# ======================= puerta-diodo (intro) =======================
TRI_POS = (270, S.FLOOR_Y - DD.DOOR_H - 30)        # esquina sup-izq de la imagen del triángulo
FLAP_PIV = (270 + 30 + DD.TRI_W + 23, S.FLOOR_Y - DD.DOOR_H + 4)   # bisagra (pantalla)
FLAP_X = FLAP_PIV[0]
BONK_X = FLAP_X + 23 + 52                            # donde queda aplastado (lado derecho de la rayita)
RUN_X0, RUN_X1 = -140, 860
T_DOOR_OUT = T_TITLE - 0.15
DOOR_SYM_C = (540, 350)

def intro_x(t):
    if t < T_ARR:
        u = t / T_ARR
        return RUN_X0 + (RUN_X1 - RUN_X0) * (1 - (1 - u) ** 1.35)
    if t < T_RUN2:
        return RUN_X1
    if t < T_BONK:
        u = (t - T_RUN2) / (T_BONK - T_RUN2)
        return RUN_X1 + (BONK_X - RUN_X1) * u ** 1.25
    if t < T_PEEL:
        return BONK_X - 8
    if t < T_SIT:
        u = S.ease_out((t - T_PEEL) / (T_SIT - T_PEEL))
        return BONK_X + (790 - BONK_X) * u
    return 790

def flap_angle(t):
    """grados; negativo = la parte de abajo se va a la derecha (abre)"""
    if t < T_PASS - 0.12:
        return 0.0
    if t < T_PASS + 0.12:
        u = S.seg(t, T_PASS - 0.12, T_PASS + 0.12)
        return -78 * S.ease_out(u)
    v = t - T_PASS - 0.12
    a = -78 * math.exp(-v * 3.2) * abs(math.cos(v * 8))
    # el bonk la sacude contra el tope
    if t >= T_BONK:
        w = t - T_BONK
        a += 3 * math.sin(w * 40) * math.exp(-w * 8)
    return a

def door_out_k(t):
    return S.ease_in(S.seg(t, T_DOOR_OUT, T_DOOR_OUT + 0.45))

def draw_door(cv, t):
    k = door_out_k(t)
    if k >= 1:
        return
    sc = 1 - 0.8 * k
    # el conjunto se encoge hacia DOOR_SYM_C
    cx0, cy0 = 470, S.FLOOR_Y - DD.DOOR_H / 2
    cx = cx0 + (DOOR_SYM_C[0] - cx0) * k; cy = cy0 + (DOOR_SYM_C[1] - cy0) * k
    al = 1 - S.seg(k, 0.6, 1.0)
    tri = DD.door_triangle()
    tx = cx + (TRI_POS[0] + tri.size[0] / 2 - cx0) * sc
    ty = cy + (TRI_POS[1] + tri.size[1] / 2 - cy0) * sc
    pulse = 1 + 0.02 * math.sin(t * 6)
    S.paste_center(cv, tri, tx, ty, scale=sc * pulse, alpha=al)
    # cartel SOLO →
    sg = DD.one_way_sign()
    S.paste_center(cv, sg, cx + (450 - cx0) * sc, cy + (S.FLOOR_Y - DD.DOOR_H - 70 - cy0) * sc, scale=sc * 0.8, alpha=al,
                   angle=0.03 * math.sin(t * 2))
    # tope rojo
    stp = DD.stopper()
    S.paste_center(cv, stp, cx + (FLAP_X - 52 - cx0) * sc, cy + (S.FLOOR_Y - 34 - cy0) * sc, scale=sc, alpha=al)
    # puerta (rayita)
    fl = DD.door_flap()
    im, off = D.rotated_about(fl, (33, 18), flap_angle(t), sc)
    px = cx + (FLAP_PIV[0] - cx0) * sc; py = cy + (FLAP_PIV[1] - cy0) * sc
    if al < 0.999:
        im = S.with_alpha(im, al)
    S._paste(cv, im, int(px + off[0]), int(py + off[1]))

def draw_door_symbol(cv, t):
    """el símbolo del diodo que queda tras encogerse la puerta; vuela con el título"""
    if t < T_DOOR_OUT + 0.3 or t > T_TITLE_FLY + 0.5:
        return
    k = S.ease_back(S.seg(t, T_DOOR_OUT + 0.3, T_DOOR_OUT + 0.6))
    fly = S.ease_in(S.seg(t, T_TITLE_FLY, T_TITLE_FLY + 0.45))
    y = DOOR_SYM_C[1] + (S.ROOM_T + 46 - DOOR_SYM_C[1]) * fly
    S.paste_center(cv, DD.symbol('normal', 100, (120, 255, 170)), DOOR_SYM_C[0], y, scale=k * (1 - 0.7 * fly), alpha=1 - fly)


# ======================= caminatas =======================
WALKS = []
def setup_walks():
    plan = [
        (E(1) + 0.1, HOME_X, 1.1),
        (P(5) + 0.3, 400, 1.1), (P(6) + 0.1, HOME_X, 1.0),
        (P(11) + 0.15, 400, 1.0), (KW(11, 'directa') + 0.2, HOME_X, 1.0),
        (P(14) + 0.2, 380, 0.9), (P(15) + 0.1, HOME_X, 0.9),
        (P(19) + 0.1, 300, 0.8),
    ]
    x = 790
    for t0, x1, d in plan:
        WALKS.append((t0, t0 + d, x, x1))
        n = max(2, int(abs(x1 - x) / 70))
        for k in range(n):
            ev(t0 + 0.12 + k * (d - 0.24) / max(1, n - 1), 'step', 0.4, panx(x + (x1 - x) * k / max(1, n - 1)), heavy=0.75)
        x = x1

def pos_x(t):
    if t < E(1) + 0.1:
        return intro_x(t), None
    x = 790
    for a, b, x0, x1 in WALKS:
        if t >= b:
            x = x1
        elif t >= a:
            u = S.ease_io((t - a) / (b - a))
            return x0 + (x1 - x0) * u, (a, b, x0, x1)
    return x, None


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
    if si is not None and walking is None and t > T_UP + 0.6:
        env = mouth_at(t)
        g1 = math.sin(t * 3.4 + si * 1.7); g2 = math.sin(t * 2.6 + si * 0.9 + 1.3)
        amp = 0.45 + 0.45 * env
        p.larm = (0.55 + 0.55 * g1 * amp, 0.15 * g2, 0.25 + 0.35 * max(0, g2) * amp); p.lelbow = 0.9 + 0.5 * g1
        p.rarm = (0.45 + 0.5 * g2 * amp, -0.15 * g1, 0.25 + 0.35 * max(0, g1) * amp); p.relbow = 0.9 + 0.5 * g2
        p.head = (p.head[0] + 0.14 * env * math.sin(t * 9), p.head[1] + 0.1 * g2, p.head[2] + 0.07 * g1)
        yf -= 3 * env
        p.sy *= 1 + 0.015 * env
        p.lean += 0.06 * g1
    # ---------- intro: corre, atraviesa, se devuelve, ¡BONK! ----------
    if t < T_UP + 0.6:
        intro_pose(p, t, x)
        if T_SIT - 0.05 <= t < T_UP + 0.25:
            yf += sit_drop(t)
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
    light = light_at(t)
    return p, x, yf, light, 0.0


SIT_DROP = 150
def sit_drop(t):
    if t < T_SIT:
        return SIT_DROP * S.ease_in(S.seg(t, T_SIT - 0.05, T_SIT))
    if t < T_UP:
        return SIT_DROP
    return SIT_DROP * (1 - S.ease_out(S.seg(t, T_UP, T_UP + 0.25)))


def run_pose(p, t, speed=1.0, d=1):
    ph = t * 3.4 * speed
    C.walk_pose(p, ph, 1.0)
    s = math.sin(ph * 2 * math.pi)
    p.rarm = (1.1 * s, 0, 0.15); p.larm = (-1.1 * s, 0, 0.15); p.relbow = 1.2; p.lelbow = 1.2
    p.rleg = (0.9 * s, 0, 0.0); p.lleg = (-0.9 * s, 0, 0.0)
    p.rknee = 0.6 + 0.6 * max(0, -s); p.lknee = 0.6 + 0.6 * max(0, s)
    p.lean += 0.22
    p.yaw = d * 0.95
    p.look = (d * 1.0, 0)


def intro_pose(p, t, x):
    if t < T_ARR:
        run_pose(p, t, 1.25, 1)
        if abs(x - FLAP_X) < 120:      # empuja la puerta con el pecho: se estira
            k = 1 - abs(x - FLAP_X) / 120
            p.sx *= 1 + 0.08 * k; p.sy *= 1 - 0.06 * k
        return
    if t < T_RUN2:
        # frena derrapando, se voltea y señala la puerta
        u = t - T_ARR
        j = S.jelly(u, 3.0, 5.0)
        p.lean += -0.35 * math.exp(-u * 6)
        p.sx *= 1 + 0.1 * j; p.sy *= 1 - 0.1 * j
        p.yaw = -0.7 * S.ease_io(S.seg(t, T_ARR + 0.15, T_ARR + 0.45))
        p.look = (-1.0, -0.2)
        return
    if t < T_BONK:
        run_pose(p, t, 1.4, -1)
        p.lean += 0.08
        return
    if t < T_PEEL:
        # aplastado como panqueque contra la rayita
        u = t - T_BONK
        j = S.jelly(u, 3.5, 6.0)
        p.sx *= 0.42 + 0.12 * j; p.sy *= 1.12 - 0.05 * j
        p.yaw = 0.0
        p.rarm = (0.0, 0, 1.55); p.larm = (0.0, 0, 1.55); p.relbow = 0.0; p.lelbow = 0.0
        p.rarm_len = 1.15; p.larm_len = 1.15
        p.rleg = (0, 0, 0.35); p.lleg = (0, 0, 0.35)
        p.look = (0, 0)
        return
    if t < T_SIT:
        # se despega y cae sentado hacia atrás
        u = S.seg(t, T_PEEL, T_SIT)
        p.sx *= 0.42 + 0.58 * S.ease_out(u); p.sy *= 1.12 - 0.12 * u
        p.lean += -0.5 * math.sin(u * math.pi)
        p.rarm = (0.3, 0, 2.2 * (1 - u) + 0.6); p.larm = (0.3, 0, 2.2 * (1 - u) + 0.6)
        p.rleg = (1.4 * u, 0, 0.1); p.lleg = (1.4 * u, 0, 0.1)
        p.yaw = -0.4 * u
        return
    # sentado riéndose
    v = t - T_SIT
    up = S.seg(t, T_UP, T_UP + 0.25)
    sit = 1 - up
    j = S.jelly(v, 3.0, 5.0)
    p.sy *= 1 - 0.12 * j * sit; p.sx *= 1 + 0.08 * j * sit
    sh = math.sin(t * 28) * 0.05 * sit
    p.head = (-0.22 * sit + sh, p.head[1], p.head[2])
    p.lean += (-0.12 + sh) * sit
    p.rleg = (1.45 * sit, 0, 0.12 * sit); p.lleg = (1.45 * sit, 0, 0.12 * sit)
    p.rknee = 0.3 * sit; p.lknee = 0.3 * sit
    p.rarm = (0.9 * sit, 0, 0.3); p.larm = (0.9 * sit, 0, 0.3); p.relbow = 1.4 * sit; p.lelbow = 1.4 * sit
    p.yaw = -0.4 * sit


def diagram_active(t):
    return (P(2) + 0.5 <= t < P(4)) or (P(5) + 0.4 <= t < T_B_SLAP) or (KW(9, 'pila') + 0.3 <= t < T_C_SLAP) \
        or (KW(11, '4 diodos') + 0.3 <= t < T_D_SLAP) or (P(13) + 0.4 <= t < T_E_SLAP)


def scene_gestures(p, t, x, yf):
    for t0, d, kind in REACT_ARMS:
        if t0 - 0.1 <= t <= t0 + d + 0.15:
            k = S.seg(t, t0 - 0.1, t0 + 0.05) * (1 - S.seg(t, t0 + d, t0 + d + 0.15))
            tp = p.copy()
            if kind in ('up', 'spin'):
                tp.larm = (0.2, 0, 2.6); tp.rarm = (0.2, 0, 2.6); tp.lelbow = 0.2; tp.relbow = 0.2
                tp.larm_len = 1.15; tp.rarm_len = 1.15
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
            elif kind == 'thumbs':        # dos pulgares arriba
                tp.larm = (1.4, 0, 0.6); tp.lelbow = 1.6; tp.rarm = (1.4, 0, 0.6); tp.relbow = 1.6
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
            elif kind == 'shrug':         # ¿qué pasó?
                tp.larm = (0.3, 0, 1.2); tp.rarm = (0.3, 0, 1.2); tp.lelbow = 1.5; tp.relbow = 1.5
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
                p.head = (p.head[0], p.head[1], p.head[2] + 0.2 * k * math.sin((t - t0) * 6))
    # "¿Y cómo lo hace?": mano en la barbilla y se inclina hacia el diodo
    a, b = P(4) - 0.1, P(5) + 0.5
    if a <= t < b:
        k = S.seg(t, a, a + 0.2) * (1 - S.seg(t, b - 0.2, b))
        tp = p.copy(); tp.rarm = (1.9, 0, -0.2); tp.relbow = 2.0
        blend_arm(p, 'r', tp, k)
        p.head = (p.head[0] - 0.1 * k, p.head[1] + 0.3 * k, p.head[2] + 0.15 * k)
        p.lean += 0.1 * k
    # "y la bloquea en el otro": mano de "alto"
    a = KW(2, 'bloquea') - 0.1
    if a <= t < E(2) + 0.1:
        k = S.seg(t, a, a + 0.15) * (1 - S.seg(t, E(2) - 0.1, E(2) + 0.1))
        tp = p.copy(); tp.larm = (1.55, 0, 0.1); tp.lelbow = 0.1; tp.larm_len = 1.2
        blend_arm(p, 'l', tp, k)
    # "y la corriente no pasa": niega con la cabeza
    a = KW(8, 'no pasa') - 0.2
    if a <= t < E(8) + 0.2:
        k = S.seg(t, a, a + 0.15) * (1 - S.seg(t, E(8), E(8) + 0.2))
        p.head = (p.head[0], p.head[1] + 0.35 * k * math.sin((t - a) * 14), p.head[2])
    # risa en "mismo truco"
    if P(17) <= t < E(17):
        sh = math.sin(t * 30) * 0.04
        p.head = (-0.2 + sh, p.head[1], p.head[2]); p.lean = -0.06 + sh
    # despedida
    a = KW(19, 'Nos vemos') - 0.2
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


# ======================= título =======================
_tc = {}
def title_imgs():
    if not _tc:
        _tc['a'] = S.fancy_text('CAPÍTULO 4', 92)
        _tc['b'] = S.fancy_text('EL DIODO', 96, top=(140, 255, 190), bot=(30, 170, 100), outline=(5, 50, 25))
    return _tc

def setup_title():
    ev(T_DOOR_OUT, 'whoosh', 0.45, 0.0)
    ev(T_DOOR_OUT + 0.35, 'pop', 0.5, 0.0)
    ev(T_TITLE + 0.05, 'block', 0.6, -0.1, pitch=1.2)
    ev(T_TITLE + 0.4, 'block', 0.6, 0.1, pitch=1.0)
    ev(T_TITLE_FLY, 'whoosh', 0.4, 0.0)

def draw_title(cv, t):
    TI = title_imgs()
    b0 = T_TITLE
    if b0 <= t < T_TITLE_FLY + 0.5:
        fly = S.ease_in(S.seg(t, T_TITLE_FLY, T_TITLE_FLY + 0.45))
        ka = S.ease_back(S.seg(t, b0, b0 + 0.35)); kb = S.ease_back(S.seg(t, b0 + 0.3, b0 + 0.65))
        ya = 500 + (S.ROOM_T + 46 - 500) * fly; yb = 620 + (S.ROOM_T + 46 - 620) * fly
        sc = 1 - 0.75 * fly
        S.paste_center(cv, TI['a'], 540, ya, scale=ka * sc, alpha=1 - fly * 0.9)
        S.paste_center(cv, TI['b'], 540, yb, scale=kb * sc, alpha=1 - fly * 0.9)


# ======================= escena A: el componente =======================
A = {}
PART_C = (600, 630)
PART_OX = PART_C[0] - DD.PART_W / 2
STRIPE_X = PART_OX + (DD.STRIPE[0] + DD.STRIPE[1]) / 2

def setup_A():
    A['t_part'] = P(2) + 0.05
    A['th'] = add_throw(A['t_part'], PART_C, lambda t: DD.diode_part(), 'l', dur=0.45, arc=170, spin=0.5)
    A['flow'] = KW(2, 'solo sentido') - 0.3
    A['block'] = KW(2, 'bloquea') - 0.1
    A['anodo'] = KW(3, 'ÁNODO') - 0.1
    A['catodo'] = KW(3, 'CÁTODO') - 0.1
    A['rayita'] = KW(3, 'rayita') - 0.1
    A['sym'] = P(3) + 0.1
    A['zoom0'] = P(4) + 0.1
    A['zoom1'] = P(5) + 0.35
    ev(A['flow'], 'zap', 0.3, 0.0)
    ev(A['block'] + 0.45, 'thud', 0.5, panx(STRIPE_X)); ev(A['block'] + 0.47, 'boing', 0.3, panx(STRIPE_X), f0=260, f1=140)
    ev(A['sym'], 'pop', 0.45, 0.0)
    ev(A['anodo'], 'pop', 0.4, panx(250)); ev(A['catodo'], 'pop', 0.4, panx(930))
    ev(A['rayita'], 'tink', 0.45, panx(STRIPE_X), f=3000)
    POINTS.append((A['anodo'], A['catodo'] - 0.1, 'l', (PART_OX + 60, PART_C[1])))
    POINTS.append((A['catodo'], A['rayita'] + 0.6, 'l', (STRIPE_X, PART_C[1] + 30)))
    ev(A['zoom0'], 'whoosh', 0.5, 0.0)

def draw_A(cv, t):
    if t < A['t_part'] or t > A['zoom1'] + 0.1:
        return
    zoom = S.ease_in(S.seg(t, A['zoom0'], A['zoom1']))
    hl = 0.0
    if t >= A['rayita']:
        hl = 0.5 + 0.5 * math.sin((t - A['rayita']) * 10) if t < A['zoom0'] else 0.0
    glow = 0.0
    def place(c, sx, sy):
        img = DD.diode_part(glow, round(hl * 4) / 4)
        if zoom > 0:
            # zoom hacia el cuerpo del diodo
            bc = PART_OX + (DD.BODY[0] + DD.BODY[2]) / 2
            sc = 1 + 3.2 * zoom
            S.paste_center(c, img, PART_C[0] + (PART_C[0] - bc) * (sc - 1), PART_C[1], scale=sc, alpha=1 - S.seg(zoom, 0.5, 1.0))
        else:
            S.paste_center(c, img, PART_C[0], PART_C[1], sx=sx, sy=sy)
    draw_thrown(cv, A['th'], t, place)
    if zoom > 0:
        return
    # corriente que pasa (izq -> der)
    if A['flow'] <= t < A['zoom0']:
        on = S.seg(t, A['flow'], A['flow'] + 0.2) * (1 - S.seg(t, A['zoom0'] - 0.3, A['zoom0']))
        l = D.L(W, 120)
        pts = [(PART_OX + 10, 60), (PART_OX + DD.PART_W - 10, 60)]
        curr_squares(l, pts, t, 7, 0.55, on * 0.9, size=10, col=DD.GREEN if t < A['block'] else D.CURR)
        cv.alpha_composite(l.done(), (0, int(PART_C[1] - 60)))
        if t < A['anodo']:
            a = S.seg(t, A['flow'], A['flow'] + 0.25) * (1 - S.seg(t, A['anodo'] - 0.3, A['anodo']))
            S.paste_center(cv, D.label('SÍ PASA →', 32, fill=DD.GREEN), 400, PART_C[1] - 110, alpha=a, scale=S.ease_back(min(1, a * 1.3)))
    # corriente que choca contra la rayita (der -> izq) y rebota
    if A['block'] <= t < A['anodo']:
        u = t - A['block']
        l = D.L(W, 120)
        for k in range(3):
            v = u - k * 0.18
            if v < 0:
                continue
            x0 = PART_OX + DD.PART_W - 10
            xs = STRIPE_X + 40
            dur_in = 0.45
            if v < dur_in:
                x = x0 + (xs - x0) * (v / dur_in)
            else:
                w = v - dur_in
                x = xs + 260 * (1 - math.exp(-w * 4))
            al = 1 - S.seg(v, 1.0, 1.4)
            l.rect([x - 10, 50, x + 10, 70], fill=DD.RED + (int(255 * al),))
        cv.alpha_composite(l.done(), (0, int(PART_C[1] - 60)))
        if u > 0.45:
            k = S.ease_back(S.seg(u, 0.45, 0.65)) * (1 - S.seg(t, A['anodo'] - 0.3, A['anodo']))
            ll = D.L(140, 140)
            ll.line([(20, 20), (120, 120)], DD.RED + (255,), 22); ll.line([(120, 20), (20, 120)], DD.RED + (255,), 22)
            S.paste_center(cv, ll.done(), STRIPE_X + 75, PART_C[1], scale=k * 0.7)
            S.paste_center(cv, D.label('← NO PASA', 32, fill=DD.RED), 840, PART_C[1] - 110, alpha=k)
    # símbolo arriba y rótulos de las patitas
    if t >= A['sym']:
        k = S.ease_back(S.seg(t, A['sym'], A['sym'] + 0.35))
        sym = DD.symbol('normal', 90, (255, 255, 255))
        S.paste_center(cv, sym, 600, 380, scale=k)
        if t >= A['rayita']:
            a = S.seg(t, A['rayita'], A['rayita'] + 0.3)
            l = D.L(W, 260)
            for yy in range(0, 140, 22):
                l.line([(600 + 45, 30 + yy), (600 + 45 + (STRIPE_X - 645) * yy / 140, 30 + yy + 12)], (255, 230, 140, int(220 * a)), 5)
            cv.alpha_composite(l.done(), (0, 410))
    if t >= A['anodo']:
        a = S.ease_back(S.seg(t, A['anodo'], A['anodo'] + 0.3))
        S.paste_center(cv, D.label('ÁNODO  +', 32, fill=(255, 190, 190)), PART_OX + 120, PART_C[1] - 100, scale=a)
    if t >= A['catodo']:
        a = S.ease_back(S.seg(t, A['catodo'], A['catodo'] + 0.3))
        S.paste_center(cv, D.label('CÁTODO  −', 32, fill=(190, 215, 255)), PART_OX + DD.PART_W - 140, PART_C[1] - 100, scale=a)
    if t >= A['rayita']:
        a = S.ease_back(S.seg(t, A['rayita'], A['rayita'] + 0.3))
        l = D.L(160, 200)
        l.circle((80, 100), 70, outline=(255, 230, 120, 255), width=7)
        S.paste_center(cv, l.done(), STRIPE_X, PART_C[1], scale=a * (1 + 0.05 * math.sin(t * 9)))


# ======================= escena B: la unión P-N =======================
B = {}
BAT_C = (540, 790)
WIRE_L = [(DD.PN_X0, 480), (100, 480), (100, BAT_C[1]), (BAT_C[0] - 125, BAT_C[1])]
WIRE_R = [(DD.PN_X1, 480), (985, 480), (985, BAT_C[1]), (BAT_C[0] + 125, BAT_C[1])]
LOOP = [(BAT_C[0] - 125, BAT_C[1]), (100, BAT_C[1]), (100, 480), (DD.PN_X0, 480), (DD.PN_X1, 480), (985, 480), (985, BAT_C[1]), (BAT_C[0] + 125, BAT_C[1])]

def setup_B():
    B['frame'] = P(5) + 0.1
    B['p'] = KW(5, 'la P') - 0.15
    B['holes'] = KW(5, 'huecos') - 0.1
    B['n'] = KW(5, 'la N') - 0.15
    B['elec'] = KW(5, 'electrones de sobra') - 0.1
    B['bar0'] = KW(6, 'juntan') - 0.1
    B['bar1'] = KW(6, 'BARRERA') + 0.2
    B['bat'] = P(7) + 0.05
    B['wire0'] = KW(7, 'positivo') - 0.1
    B['wire1'] = B['wire0'] + 0.6
    B['v0'] = KW(7, '0,7') - 0.2
    B['v1'] = B['v0'] + 0.9
    B['cross'] = KW(7, 'cruzan') - 0.1
    B['flip0'] = KW(8, 'volteas') - 0.1
    B['flip1'] = B['flip0'] + 0.5
    B['grow0'] = KW(8, 'crece') - 0.2
    B['grow1'] = B['grow0'] + 0.8
    B['nopasa'] = KW(8, 'no pasa') - 0.05
    B['th_bat'] = add_throw(B['bat'], BAT_C, lambda t: DD.battery_rot(90), 'l', dur=0.45, arc=150, spin=0.5)
    ev(B['p'], 'pop', 0.4, panx(300)); ev(B['n'], 'pop', 0.4, panx(780))
    for k in range(6):
        ev(B['holes'] + k * 0.07, 'pop', 0.2, panx(200 + 50 * k), f0=700, f1=1300)
        ev(B['elec'] + k * 0.07, 'tink', 0.18, panx(600 + 50 * k), f=3200 + 100 * k)
    ev(B['bar0'] + 0.2, 'block', 0.5, 0.0, pitch=0.7)
    ev(B['wire0'], 'marker', 0.45, 0.0, dur=0.6)
    ev(B['v0'], 'roll', 0.3, 0.0, dur=0.9)
    ev(B['cross'], 'zap', 0.5, 0.0)
    ev(B['cross'] + 0.1, 'hum', 0.25, 0.0, dur=B['flip0'] - B['cross'], f=110)
    ev(B['flip0'], 'whoosh', 0.45, 0.0); ev(B['flip1'], 'click', 0.6, 0.0)
    ev(B['grow0'], 'boing', 0.3, 0.0, f0=140, f1=90)
    ev(B['nopasa'], 'thud', 0.5, 0.0)
    POINTS.append((B['flip0'] - 0.1, B['flip1'] + 0.05, 'l', (BAT_C[0] - 60, BAT_C[1] - 30)))
    SLAPS.append((T_B_SLAP, 'l'))
    ev(T_B_SLAP, 'whoosh', 0.5, 0.2); ev(T_B_SLAP + 0.05, 'crumble', 0.7, 0.2)

def volts(t):
    if t < B['v0']:
        return 0.0
    if t < B['flip0']:
        return 0.7 * S.ease_out(S.seg(t, B['v0'], B['v1']))
    return -0.7 * S.ease_io(S.seg(t, B['flip0'], B['flip1'])) + 0.7 * (1 - S.ease_io(S.seg(t, B['flip0'], B['flip1'])))

def barrier_w(t):
    if t < B['bar0']:
        return 0.0
    base = 90 * S.ease_out(S.seg(t, B['bar0'], B['bar0'] + 0.5))
    if t < B['flip0']:
        v = max(0.0, volts(t))
        return base - 72 * (v / 0.7)
    shrink = 18
    grow = S.ease_back(S.seg(t, B['grow0'], B['grow1']), 1.2)
    back = S.seg(t, B['flip0'], B['flip1'])
    w0 = shrink + (90 - shrink) * back
    return w0 + (250 - 90) * grow

def fwd(t):
    """1 mientras la corriente pasa"""
    if t < B['cross']:
        return 0.0
    return S.seg(t, B['cross'], B['cross'] + 0.25) * (1 - S.seg(t, B['flip0'], B['flip0'] + 0.15))

def carrier_pos(c, t, kind):
    x0, y0 = c['x'], c['y']
    jx = 6 * math.sin(t * c['w'] + c['ph']); jy = 6 * math.cos(t * c['w'] * 1.3 + c['ph'])
    bw = barrier_w(t)
    f = fwd(t)
    x = x0
    if f > 0:
        span = DD.PN_X1 - DD.PN_X0 - 60
        d = (t - B['cross']) * 230 * (1 if kind == 'h' else -1)
        x = DD.PN_X0 + 30 + ((x0 - DD.PN_X0 - 30 + d) % span)
        x = x0 + (x - x0) * f
    elif t >= B['flip0']:
        # se alejan de la barrera
        g = S.ease_out(S.seg(t, B['grow0'], B['grow1']))
        if kind == 'h':
            lim = DD.PN_MID - bw / 2 - 26
            x = min(x0, DD.PN_X0 + 40 + (x0 - DD.PN_X0 - 40) * (1 - 0.35 * g))
            x = min(x, lim)
        else:
            lim = DD.PN_MID + bw / 2 + 26
            x = max(x0, DD.PN_X1 - 40 - (DD.PN_X1 - 40 - x0) * (1 - 0.35 * g))
            x = max(x, lim)
    return x + jx, y0 + jy

def carrier_alpha(c, t, kind, x):
    t_in = (B['holes'] if kind == 'h' else B['elec']) + c['pop']
    a = S.seg(t, t_in, t_in + 0.15)
    bw = barrier_w(t)
    if fwd(t) <= 0.01 and bw > 10 and abs(x - DD.PN_MID) < bw / 2 + 8:
        a *= 0.0
    return a

def draw_B(cv, t, at=None):
    if t < B['frame'] or t > T_B_SLAP + 1.0:
        return
    if t >= T_B_SLAP and at is None:
        lay = capture(draw_B, T_B_SLAP - 0.01, 270, 860)
        D.shatter(cv, lay, 0, 270, t - T_B_SLAP, seed=7, tile=64, push=(300, -100))
        return
    zin = S.ease_out(S.seg(t, B['frame'], B['frame'] + 0.35))
    pa = S.seg(t, B['p'], B['p'] + 0.25); na = S.seg(t, B['n'], B['n'] + 0.25)
    frame = DD.pn_frame(max(0.25, pa) if zin > 0 else 0, max(0.25, na))
    S.paste_center(cv, frame, (DD.PN_X0 + DD.PN_X1) / 2, (DD.PN_Y0 + DD.PN_Y1) / 2, scale=0.6 + 0.4 * zin, alpha=zin)
    if zin < 1:
        return
    # barrera
    bw = barrier_w(t)
    if bw > 4:
        S.paste_center(cv, DD.barrier_img(bw), DD.PN_MID, (DD.PN_Y0 + DD.PN_Y1) / 2)
    # portadores
    hi = DD.hole_img(); ei = DD.elec_img()
    for c in DD.HOLES:
        x, y = carrier_pos(c, t, 'h')
        a = carrier_alpha(c, t, 'h', x)
        if a > 0.02:
            S.paste_center(cv, hi, x, y, scale=0.5 + 0.5 * S.ease_back(a), alpha=a)
    for c in DD.ELECS:
        x, y = carrier_pos(c, t, 'e')
        a = carrier_alpha(c, t, 'e', x)
        if a > 0.02:
            S.paste_center(cv, ei, x, y, scale=0.5 + 0.5 * S.ease_back(a), alpha=a)
    # rótulos
    if t >= B['holes'] and t < P(7):
        a = S.seg(t, B['holes'], B['holes'] + 0.25) * (1 - S.seg(t, P(7) - 0.3, P(7)))
        S.paste_center(cv, D.label('HUECOS: faltan electrones', 26, fill=(255, 200, 200)), 340, 670, alpha=a)
    if t >= B['elec'] and t < P(7):
        a = S.seg(t, B['elec'], B['elec'] + 0.25) * (1 - S.seg(t, P(7) - 0.3, P(7)))
        S.paste_center(cv, D.label('ELECTRONES de sobra', 26, fill=(190, 220, 255)), 760, 740, alpha=a)
    if B['bar0'] + 0.3 <= t < B['cross']:
        a = S.ease_back(S.seg(t, B['bar0'] + 0.3, B['bar0'] + 0.6))
        S.paste_center(cv, D.label('BARRERA', 32, fill=(225, 210, 255)), DD.PN_MID, 312, scale=a)
    # pila y cables
    th = B['th_bat']
    st = throw_state(th, t)
    if st is not None:
        ang = 90 + 180 * S.ease_back(S.seg(t, B['flip0'], B['flip1']), 1.4) if t >= B['flip0'] else 90
        hop = 70 * math.sin(math.pi * S.seg(t, B['flip0'], B['flip1'])) if t >= B['flip0'] else 0
        if t >= B['wire0']:
            u = S.seg(t, B['wire0'], B['wire1'])
            l = D.L(W, H)
            wire_partial(l, WIRE_L, u, D.WIRE, 10)
            wire_partial(l, WIRE_R, u, D.WIRE, 10)
            f = fwd(t)
            if f > 0:
                pts = LOOP if True else LOOP
                curr_squares(l, pts, t, 16, 0.18, f)
            cv.alpha_composite(l.done())
        if st[0] == 'fly':
            S.paste_center(cv, DD.battery_rot(90), st[1], st[2], scale=st[4], angle=st[3])
        else:
            S.paste_center(cv, DD.battery_rot(int(ang) % 360), BAT_C[0], BAT_C[1] - hop, sx=st[1], sy=st[2])
    # voltímetro
    if t >= B['v0']:
        v = volts(t)
        a = S.ease_back(S.seg(t, B['v0'], B['v0'] + 0.3))
        txt = ('%.1f V' % abs(v)).replace('.', ',')
        col = (255, 230, 120) if t < B['flip0'] else (255, 150, 150)
        S.paste_center(cv, D.label(txt, 40, fill=col), BAT_C[0], BAT_C[1] - 120, scale=a)
    # estado
    if t >= B['cross'] and t < B['flip0']:
        a = S.ease_back(S.seg(t, B['cross'], B['cross'] + 0.3))
        S.paste_center(cv, D.label('✓ LA CORRIENTE PASA', 32, fill=DD.GREEN), DD.PN_MID, 312, scale=a)
    if t >= B['grow0']:
        a = S.ease_back(S.seg(t, B['grow0'], B['grow0'] + 0.3))
        S.paste_center(cv, D.label('LA BARRERA CRECE', 30, fill=(225, 210, 255)), DD.PN_MID, 312, scale=a)
    if t >= B['nopasa']:
        k = S.ease_back(S.seg(t, B['nopasa'], B['nopasa'] + 0.25))
        ll = D.L(160, 160)
        ll.line([(24, 24), (136, 136)], DD.RED + (255,), 24); ll.line([(136, 24), (24, 136)], DD.RED + (255,), 24)
        S.paste_center(cv, ll.done(), DD.PN_MID, (DD.PN_Y0 + DD.PN_Y1) / 2, scale=k)


# ======================= escena C: pila, diodo y bombillo =======================
Cc = {}
BAT2 = (300, 600); DIO2 = (600, 380); BULB = (880, 570)
DIO2_S = 0.5
WY_TOP, WY_BOT = 380, 790
C_LOOP = [(BAT2[0], BAT2[1] - 125), (BAT2[0], WY_TOP), (DIO2[0] - 190, WY_TOP), (DIO2[0] + 190, WY_TOP), (BULB[0], WY_TOP),
          (BULB[0], BULB[1] - 110), (BULB[0], BULB[1] + 110), (BULB[0], WY_BOT), (BAT2[0], WY_BOT), (BAT2[0], BAT2[1] + 125)]

def setup_C():
    Cc['th_bat'] = add_throw(KW(9, 'pila') - 0.15, BAT2, lambda t: D.battery_img(), 'l', dur=0.4, arc=150, spin=0.6)
    Cc['th_dio'] = add_throw(KW(9, 'diodo') - 0.15, DIO2, lambda t: DD.diode_part().resize((int(DD.PART_W * DIO2_S), int(DD.PART_H * DIO2_S))), 'l', dur=0.4, arc=150, spin=0.6)
    Cc['th_bulb'] = add_throw(KW(9, 'bombillo') - 0.15, BULB, lambda t: DD.bulb_img(0), 'l', dur=0.4, arc=150, spin=0.6)
    Cc['wire0'] = KW(9, 'bombillo') + 0.3
    Cc['wire1'] = Cc['wire0'] + 0.55
    Cc['on'] = KW(9, 'prende') - 0.05
    Cc['flip0'] = P(10) + 0.15
    Cc['flip1'] = Cc['flip0'] + 0.55
    Cc['off'] = KW(10, 'apaga') - 0.1
    ev(Cc['wire0'], 'marker', 0.45, 0.0, dur=0.55)
    ev(Cc['on'], 'switch', 0.5, panx(BULB[0])); ev(Cc['on'] + 0.02, 'zap', 0.5, panx(BULB[0]))
    ev(Cc['on'] + 0.05, 'tink', 0.35, panx(BULB[0]), f=2600)
    ev(Cc['flip0'], 'whoosh', 0.45, panx(BAT2[0])); ev(Cc['flip1'], 'click', 0.6, panx(BAT2[0]))
    ev(Cc['off'], 'pop', 0.4, panx(BULB[0]), f0=700, f1=250)
    ev(Cc['off'] + 0.05, 'thud', 0.4, panx(DIO2[0]))
    POINTS.append((Cc['flip0'] - 0.05, Cc['flip1'] + 0.05, 'l', (BAT2[0] - 20, BAT2[1] - 40)))
    SLAPS.append((T_C_SLAP, 'l'))
    ev(T_C_SLAP, 'whoosh', 0.5, 0.2); ev(T_C_SLAP + 0.05, 'crumble', 0.7, 0.2)

def bulb_on(t):
    if Cc['on'] <= t < Cc['flip0'] + 0.35:
        return S.seg(t, Cc['on'], Cc['on'] + 0.08)
    return 0.0

def draw_C(cv, t, at=None):
    if t < Cc['th_bat']['t0'] or t > T_C_SLAP + 1.0:
        return
    if t >= T_C_SLAP and at is None:
        lay = capture(draw_C, T_C_SLAP - 0.01, 270, 880)
        D.shatter(cv, lay, 0, 270, t - T_C_SLAP, seed=9, tile=64, push=(300, -100))
        return
    on = bulb_on(t)
    if t >= Cc['wire0']:
        l = D.L(W, H)
        col = tuple(int(D.WIRE[i] * (1 - 0.25 * on) + (255, 200, 120)[i] * 0.25 * on) for i in range(3))
        wire_partial(l, C_LOOP, S.seg(t, Cc['wire0'], Cc['wire1']), col, 10)
        if on > 0:
            curr_squares(l, C_LOOP, t, 14, 0.22, on)
        cv.alpha_composite(l.done())
    def placer(img_fn, pos):
        def f(c, sx, sy):
            S.paste_center(c, img_fn(), pos[0], pos[1], sx=sx, sy=sy)
        return f
    draw_thrown(cv, Cc['th_dio'], t, placer(lambda: DD.diode_part().resize((int(DD.PART_W * DIO2_S), int(DD.PART_H * DIO2_S)), Image.LANCZOS), DIO2))
    draw_thrown(cv, Cc['th_bulb'], t, placer(lambda: DD.bulb_img(on), BULB))
    # pila (se voltea)
    st = throw_state(Cc['th_bat'], t)
    if st is not None:
        if st[0] == 'fly':
            S.paste_center(cv, D.battery_img(), st[1], st[2], scale=st[4], angle=st[3])
        else:
            u = S.seg(t, Cc['flip0'], Cc['flip1'])
            ang = math.pi * S.ease_back(u, 1.4) if t >= Cc['flip0'] else 0.0
            hop = 90 * math.sin(math.pi * u) if t >= Cc['flip0'] else 0.0
            S.paste_center(cv, D.battery_img(), BAT2[0], BAT2[1] - hop, sx=st[1], sy=st[2], angle=ang)
    # rótulos
    if t >= Cc['wire1']:
        a = S.seg(t, Cc['wire1'], Cc['wire1'] + 0.2) * (1 - S.seg(t, T_C_SLAP - 0.1, T_C_SLAP))
        S.paste_center(cv, D.label('PILA', 26), BAT2[0] - 135, BAT2[1], alpha=a)
        S.paste_center(cv, D.label('DIODO', 26), DIO2[0], DIO2[1] - 70, alpha=a)
        S.paste_center(cv, D.label('BOMBILLO', 26), BULB[0], BULB[1] + 175, alpha=a)
    if Cc['on'] <= t < Cc['flip0']:
        S.paste_center(cv, D.label('✓ PASA', 32, fill=DD.GREEN), DIO2[0], 520, scale=S.ease_back(S.seg(t, Cc['on'], Cc['on'] + 0.15)))
    if t >= Cc['off']:
        k = S.ease_back(S.seg(t, Cc['off'], Cc['off'] + 0.2))
        ll = D.L(120, 120)
        ll.line([(18, 18), (102, 102)], DD.RED + (255,), 20); ll.line([(102, 18), (18, 102)], DD.RED + (255,), 20)
        S.paste_center(cv, ll.done(), DIO2[0], DIO2[1], scale=k)
        S.paste_center(cv, D.label('✗ BLOQUEADO', 32, fill=DD.RED), DIO2[0], 520, scale=k)


# ======================= escena D: el cargador =======================
Dd = {}
OUT_C = (125, 610); AC_C = (325, 610); BR_C = (560, 610); DC_C = (790, 610); PH_C = (968, 610)

def setup_D():
    Dd['th_br'] = add_throw(KW(11, '4 diodos') - 0.15, BR_C, lambda t: DD.bridge_img(), 'l', dur=0.45, arc=160, spin=0.5)
    Dd['th_ph'] = add_throw(KW(11, 'celular') - 0.15, PH_C, lambda t: DD.phone_img(0.2), 'l', dur=0.45, arc=170, spin=0.5)
    Dd['th_out'] = add_throw(KW(11, 'alterna') - 0.2, OUT_C, lambda t: DD.outlet_img(), 'l', dur=0.4, arc=150, spin=0.5)
    Dd['ac'] = KW(11, 'alterna') + 0.15
    Dd['dc'] = KW(11, 'directa') - 0.15
    Dd['rect'] = KW(12, 'RECTIFICADOR') - 0.1
    ev(Dd['ac'], 'hum', 0.35, panx(AC_C[0]), dur=T_D_SLAP - Dd['ac'], f=60)
    ev(Dd['dc'], 'zap', 0.45, panx(PH_C[0]))
    ev(Dd['dc'] + 0.4, 'bell', 0.25, panx(PH_C[0]))
    ev(Dd['rect'], 'block', 0.6, panx(BR_C[0]), pitch=0.8)
    SLAPS.append((T_D_SLAP, 'l'))
    ev(T_D_SLAP, 'whoosh', 0.5, 0.2); ev(T_D_SLAP + 0.05, 'crumble', 0.7, 0.2)

def draw_D(cv, t, at=None):
    if t < Dd['th_br']['t0'] or t > T_D_SLAP + 1.0:
        return
    if t >= T_D_SLAP and at is None:
        lay = capture(draw_D, T_D_SLAP - 0.01, 270, 860)
        D.shatter(cv, lay, 0, 270, t - T_D_SLAP, seed=11, tile=64, push=(300, -100))
        return
    glow = S.seg(t, Dd['rect'], Dd['rect'] + 0.2)
    def placer(img_fn, pos):
        def f(c, sx, sy):
            S.paste_center(c, img_fn(), pos[0], pos[1], sx=sx, sy=sy)
        return f
    level = 0.2 + 0.75 * S.seg(t, Dd['dc'] + 0.2, Dd['dc'] + 2.0)
    chg = (0.6 + 0.4 * math.sin(t * 8)) if t >= Dd['dc'] else 0.0
    draw_thrown(cv, Dd['th_out'], t, placer(DD.outlet_img, OUT_C))
    draw_thrown(cv, Dd['th_br'], t, placer(lambda: DD.bridge_img(round(glow * 4) / 4), BR_C))
    draw_thrown(cv, Dd['th_ph'], t, placer(lambda: DD.phone_img(round(level * 20) / 20, round(chg, 1)), PH_C))
    if t >= Dd['ac']:
        u = S.seg(t, Dd['ac'], Dd['ac'] + 0.5)
        S.paste_center(cv, DD.wave_img('ac', t * 7, draw=u), AC_C[0], AC_C[1])
        a = S.seg(t, Dd['ac'], Dd['ac'] + 0.3)
        S.paste_center(cv, D.label('ALTERNA: va y viene', 24, fill=(255, 230, 140)), AC_C[0] - 10, AC_C[1] + 115, alpha=a)
    if t >= Dd['dc']:
        u = S.seg(t, Dd['dc'], Dd['dc'] + 0.5)
        S.paste_center(cv, DD.wave_img('dc', t * 7, draw=u, col=DD.GREEN), DC_C[0], DC_C[1])
        a = S.seg(t, Dd['dc'], Dd['dc'] + 0.3)
        S.paste_center(cv, D.label('DIRECTA: un solo sentido', 24, fill=DD.GREEN), DC_C[0] + 20, DC_C[1] + 115, alpha=a)
    if t >= Dd['th_br']['t0'] + 0.5:
        a = S.seg(t, Dd['th_br']['t0'] + 0.5, Dd['th_br']['t0'] + 0.7)
        S.paste_center(cv, D.label('4 DIODOS', 26), BR_C[0], BR_C[1] - 150, alpha=a)
    if t >= Dd['rect']:
        k = S.ease_back(S.seg(t, Dd['rect'], Dd['rect'] + 0.3))
        S.paste_center(cv, S.fancy_text('RECTIFICADOR', 66, top=(140, 255, 190), bot=(30, 170, 100), outline=(5, 50, 25)) if 'rf' not in _tc else _tc['rf'],
                       BR_C[0], 380, scale=k, angle=-0.04)
        _tc.setdefault('rf', S.fancy_text('RECTIFICADOR', 66, top=(140, 255, 190), bot=(30, 170, 100), outline=(5, 50, 25)))


# ======================= escena E: los hermanos con superpoderes =======================
Ee = {}
CARD_POS = {'led': (305, 430), 'zener': (775, 430), 'schottky': (305, 700), 'foto': (775, 700)}

def setup_E():
    Ee['sp'] = KW(12, 'superpoderes') - 0.15
    ev(Ee['sp'], 'pop', 0.5, 0.0); ev(Ee['sp'] + 0.05, 'bell', 0.25, 0.0)
    Ee['th'] = {}
    for key, i in (('led', 13), ('zener', 14), ('schottky', 15), ('foto', 16)):
        Ee['th'][key] = add_throw(P(i) + 0.05, CARD_POS[key], (lambda kk: (lambda t: card_img(kk, P(16) - 5)))(key), 'l', dur=0.45, arc=150, spin=0.4)
        POINTS.append((P(i) + 0.6, P(i) + 1.4, 'l', (CARD_POS[key][0] - 100, CARD_POS[key][1] + 60)))
    Ee['luz'] = KW(13, 'como luz') - 0.1
    Ee['color'] = KW(13, 'color') - 0.1
    Ee['z0'] = KW(14, 'bloquea') - 0.1
    Ee['z1'] = KW(14, 'fijo') + 0.2
    Ee['s0'] = KW(15, 'enciende') - 0.1
    Ee['s1'] = KW(15, 'rapidísimo') + 0.1
    Ee['fast'] = KW(15, 'rapidísimo') - 0.1
    Ee['dark'] = KW(16, 'a oscuras') - 0.1
    Ee['light'] = KW(16, 'si le llega') - 0.05
    Ee['curr'] = KW(16, 'deja pasar corriente') - 0.05
    Ee['tv'] = KW(16, 'Así tu tele') + 0.1
    ev(Ee['luz'], 'zap', 0.45, panx(305)); ev(Ee['luz'] + 0.05, 'tink', 0.4, panx(305), f=3400)
    for k in range(4):
        ev(Ee['color'] + k * 0.45, 'tink', 0.2, panx(305), f=2400 + 400 * k)
    ev(Ee['z0'], 'roll', 0.25, panx(775), dur=1.2)
    ev(KW(14, 'fijo') - 0.1, 'block', 0.4, panx(775), pitch=1.4)
    ev(Ee['s0'], 'roll', 0.25, panx(305), dur=1.0)
    ev(Ee['s0'] + 0.6, 'zap', 0.3, panx(305))
    ev(Ee['fast'], 'whoosh', 0.5, panx(305))
    ev(Ee['light'], 'beep', 0.25, panx(775)); ev(Ee['light'] + 0.2, 'beep', 0.25, panx(775))
    ev(Ee['curr'], 'zap', 0.3, panx(775))
    ev(Ee['tv'], 'switch', 0.5, panx(775)); ev(Ee['tv'] + 0.03, 'pop', 0.4, panx(775))
    SLAPS.append((T_E_SLAP, 'l'))
    ev(T_E_SLAP, 'whoosh', 0.5, 0.2); ev(T_E_SLAP + 0.05, 'crumble', 0.7, 0.2)

def card_img(key, t):
    if key == 'led':
        light = 0.15 + 0.85 * S.seg(t, Ee['luz'], Ee['luz'] + 0.15)
        ck = max(0.0, (t - Ee['color']) * 1.6) if t >= Ee['color'] else 0.0
        return DD.card_led(t, ck, light)
    if key == 'zener':
        return DD.card_zener(t, S.seg(t, Ee['z0'], Ee['z1']))
    if key == 'schottky':
        return DD.card_schottky(t, S.seg(t, Ee['s0'], Ee['s1']), S.seg(t, Ee['fast'], Ee['fast'] + 0.2))
    light = S.seg(t, Ee['light'], Ee['light'] + 0.2)
    return DD.card_foto(t, light, S.seg(t, Ee['curr'], Ee['curr'] + 0.2) * light, S.seg(t, Ee['tv'], Ee['tv'] + 0.2),
                        1.0 if Ee['dark'] <= t < Ee['light'] else 0.0)

def draw_E(cv, t, at=None):
    # ¡SUPERPODERES!
    if Ee['sp'] <= t < P(13) + 0.4:
        k = S.ease_back(S.seg(t, Ee['sp'], Ee['sp'] + 0.35)) * (1 - S.ease_in(S.seg(t, P(13), P(13) + 0.4)))
        S.paste_center(cv, DD.superpoderes(), 540, 560 + 8 * math.sin(t * 7), scale=k, angle=0.04 * math.sin(t * 5))
    if t < P(13) or t > T_E_SLAP + 1.0:
        return
    if t >= T_E_SLAP and at is None:
        lay = capture(draw_E, T_E_SLAP - 0.01, 280, 860)
        D.shatter(cv, lay, 0, 280, t - T_E_SLAP, seed=13, tile=64, push=(300, -100))
        return
    pulse = 0.0
    if P(17) <= t:
        pulse = S.seg(t, P(17), P(17) + 0.3)
    for i, key in enumerate(('led', 'zener', 'schottky', 'foto')):
        th = Ee['th'][key]
        st = throw_state(th, t)
        if st is None:
            continue
        img = card_img(key, t)
        if st[0] == 'fly':
            S.paste_center(cv, img, st[1], st[2], scale=st[4], angle=st[3])
        else:
            pos = CARD_POS[key]
            sc = 1 + 0.05 * pulse * math.sin(t * 9 + i * 1.5)
            if pulse > 0:
                S.glow_fast(cv, pos[0], pos[1], 170, (255, 210, 90), 0.35 * pulse)
            S.paste_center(cv, img, pos[0], pos[1], sx=st[1] * sc, sy=st[2] * sc)


# ======================= escena final =======================
F = {}
BTN = {'like': (770, 600), 'sub': (770, 735), 'follow': (770, 870)}

def setup_F():
    F['btn_in'] = P(18) - 0.6
    F['hit'] = {'like': KW(18, 'me gusta'), 'sub': KW(18, 'suscríbete'), 'follow': KW(18, 'sígueme')}
    F['door'] = P(19) + 0.1
    for i, k in enumerate(('like', 'sub', 'follow')):
        ev(F['btn_in'] + i * 0.1, 'pop', 0.35, 0.4)
        th = F['hit'][k]
        JUMPS.append((th - 0.3, 0.55, 70))
        POINTS.append((th - 0.12, th + 0.08, 'l', (lambda kk: (lambda t: (BTN[kk][0] - 180, BTN[kk][1])))(k)))
        ev(th, 'click', 0.6, 0.5); ev(th + 0.02, 'pop', 0.4, 0.5, f0=600, f1=1400)
        if k == 'sub':
            ev(th + 0.05, 'bell', 0.6, 0.5)
        ev(th - 0.3 + 0.55, 'step', 0.5, panx(300))
    ev(F['door'], 'squeak', 0.35, panx(420)); ev(F['door'] + 0.05, 'block', 0.4, panx(420))
    ev(T_END_SNAP, 'snap', 0.9, -0.2)
    ev(T_END_SNAP + 0.05, 'switch', 0.5, 0.0)
    ev(T_END_SNAP + 1.35, 'tvoff', 0.8, 0.0)

def draw_F(cv, t):
    if t >= F['btn_in'] and t < T_END_SNAP + 0.4:
        for i, k in enumerate(('like', 'sub', 'follow')):
            s = S.ease_back(S.seg(t, F['btn_in'] + i * 0.1, F['btn_in'] + i * 0.1 + 0.35)) * (1 - S.ease_in(S.seg(t, T_END_SNAP + 0.05, T_END_SNAP + 0.35)))
            th = F['hit'][k]
            pressed = 1.0 if t >= th else 0.0
            sq = 1 - 0.25 * S.jelly(t - th, 3, 6) if t >= th else 1.0
            S.paste_center(cv, D.end_button(k, pressed), BTN[k][0], BTN[k][1], scale=s, sx=2 - sq, sy=sq)
    # puerta misteriosa del capítulo 5
    if F['door'] <= t < T_END_SNAP + 0.4:
        k = S.ease_back(S.seg(t, F['door'], F['door'] + 0.35)) * (1 - S.ease_in(S.seg(t, T_END_SNAP + 0.05, T_END_SNAP + 0.35)))
        wob = 0.05 * math.sin((t - F['door']) * 6)
        S.paste_center(cv, DD.mystery_door(), 400, 410, scale=0.85 * k, angle=wob)
        S.paste_center(cv, D.label('CAP. 5', 26, fill=(255, 220, 120)), 400, 590, alpha=S.seg(t, F['door'] + 0.2, F['door'] + 0.4) * k)


# ======================= intro: sonidos =======================
def schedule_intro_sfx():
    ev(0.0, 'whoosh', 0.45, -0.6)
    for k in range(6):
        tt = 0.06 + k * 0.14
        ev(tt, 'step', 0.45, panx(intro_x(tt)), heavy=0.7)
    ev(T_PASS - 0.05, 'squeak', 0.45, panx(FLAP_X))
    ev(T_PASS + 0.35, 'tink', 0.25, panx(FLAP_X), f=1800)
    ev(T_ARR, 'roll', 0.35, panx(RUN_X1), dur=0.3)
    for k in range(3):
        tt = T_RUN2 + 0.05 + k * 0.1
        ev(tt, 'step', 0.45, panx(intro_x(tt)), heavy=0.7)
    ev(T_BONK, 'bonk', 1.0, panx(BONK_X))
    ev(T_BONK + 0.02, 'block', 0.5, panx(BONK_X), pitch=0.6)
    ev(T_SIT, 'thud', 0.7, panx(790))
    ev(T_UP + 0.25, 'step', 0.5, panx(790), heavy=1.0)


def setup_all():
    setup_walks()
    schedule_intro_sfx()
    setup_title()
    setup_A()
    setup_B()
    setup_C()
    setup_D()
    setup_E()
    setup_F()
    react = [
        (T_TITLE - 0.05, 0.7, 110, 'spin'),               # título
        (B['cross'] + 0.05, 0.45, 60, 'up'),              # ¡la cruzan!
        (Cc['on'] + 0.05, 0.45, 70, 'thumbs'),            # ¡prende!
        (Cc['off'] + 0.1, 0.5, 0, 'shrug'),               # ¡se apaga!
        (Dd['dc'] + 0.1, 0.45, 55, 'up'),                 # ¡directa!
        (Ee['sp'] + 0.05, 0.6, 90, 'up'),                 # ¡superpoderes!
        (Ee['luz'] + 0.05, 0.4, 50, None),                # LED
        (Ee['fast'] + 0.05, 0.4, 50, None),               # rapidísimo
        (Ee['tv'] + 0.05, 0.45, 60, 'thumbs'),            # la tele prende
    ]
    for t0, d, h, kind in react:
        if h > 0:
            JUMPS.append((t0, d, h))
            ev(t0 + d, 'step', 0.45, 0.0, heavy=0.9)
        if kind == 'spin':
            SPINS.append((t0, d)); ev(t0, 'whoosh', 0.3, 0.0)
        if kind:
            REACT_ARMS.append((t0, d, kind))

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
    sw = 0.0
    if t >= T_END_SNAP:
        sw = 0.04 * math.sin((t - T_END_SNAP) * 5) * math.exp(-(t - T_END_SNAP))
    if T_BONK <= t < T_BONK + 1.2:       # el golpe sacude la lámpara
        sw = 0.07 * math.sin((t - T_BONK) * 7) * math.exp(-(t - T_BONK) * 2.5)
    S.draw_lamp(cv, on=light, swing=sw)
    if light > 0.05:
        S.glow_fast(cv, S.LAMP_X + math.sin(sw) * S.LAMP_Y, math.cos(sw) * S.LAMP_Y + 22, 90, (255, 230, 150), 0.6 * light)
    if t >= T_TITLE_FLY + 0.4 and t < T_END_SNAP + 0.1:
        S.draw_label(cv, LABEL_TXT, alpha=S.seg(t, T_TITLE_FLY + 0.4, T_TITLE_FLY + 0.6) * light)
    # ----- intro -----
    if t < T_DOOR_OUT + 0.5:
        draw_door(cv, t)
    draw_door_symbol(cv, t)
    draw_title(cv, t)
    # ----- escenas -----
    draw_A(cv, t)
    draw_B(cv, t)
    draw_C(cv, t)
    draw_D(cv, t)
    draw_E(cv, t)
    # ----- sombra -----
    if light > 0.05:
        h = S.FLOOR_Y - yf
        sh_w = 150 * max(0.4, 1 - h / 600) * (0.6 if T_BONK <= t < T_PEEL else 1.0)
        d = ImageDraw.Draw(cv, 'RGBA')
        d.ellipse([x - sh_w, S.FLOOR_Y - 14, x + sh_w, S.FLOOR_Y + 12], fill=(0, 0, 0, int(110 * light * max(0.3, 1 - h / 500))))
    # ----- personaje -----
    char_light = 0.32 + 0.68 * light if t < T_END_SNAP + 1.3 else 0.32
    CH.render(cv, pose, dict(scale=S.SCALE, ox=x, oy=yf, view_yaw=0.12 * math.sin(t * 0.2)), light=char_light, t=t)
    # ----- ¡BONK! -----
    if T_BONK <= t < T_BONK + 1.1:
        u = t - T_BONK
        k = S.ease_back(S.seg(u, 0.0, 0.18), 2.5) * (1 - S.seg(u, 0.8, 1.1))
        S.paste_center(cv, DD.bonk_text(), BONK_X + 60, S.FLOOR_Y - 640 - 30 * u, scale=k, angle=-0.12)
        if u < 0.35:
            l = D.L(W, H)
            for j in range(8):
                a = j * math.pi / 4
                r0 = 60 + 300 * u; r1 = r0 + 70
                cx, cy = FLAP_X + 20, S.FLOOR_Y - 330
                l.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
                       (255, 255, 200, int(255 * (1 - u / 0.35))), 8)
            cv.alpha_composite(l.done())
    draw_F(cv, t)
    sub, si = TL.subtitle_at(t)
    if sub and t < T_END_SNAP + 0.2:
        S.draw_subtitle(cv, sub)
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
