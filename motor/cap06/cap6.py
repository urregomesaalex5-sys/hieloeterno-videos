#!/usr/bin/env python3
# Capítulo 6: La memoria del celular. Vertical 1080x1920, 30 fps.
# Intro (gancho en el segundo 0): prende un celular gigante que alumbra el cuarto, saca una foto y la voltea:
# ¿dónde viven? Luego el comentario de @Liguitoo_oficial y se mete por el puerto de carga (por dentro: placa).
# Regla: cada rótulo sale de VERIFICACION.md.
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import scene as S
import diagrams as D
import memoria as M
import pcb as PCB
import char3d as C
from timeline import TL, PHRASES

W, H = S.W, S.H
FPS = S.FPS
CH = C.Character()
HOME_X = 230
INTRO_X = 300
IN_X = 470
LABEL_TXT = 'CAP. 6 · LA MEMORIA DEL CELULAR'

P = lambda i: TL.s(i)
E = lambda i: TL.e(i)
KW = TL.kw

# ======================= tiempos clave =======================
T_ON = 0.12                          # se prende el celular (luz)
T_BONK = T_ON                        # (la música usa este nombre)
T_PHOTO = KW(0, 'fotos') - 0.1       # saca una foto de la pantalla
T_FLIP = KW(0, 'dónde') - 0.05       # la voltea: detrás no hay nada
T_COM = P(1) - 0.15                  # comentarios del seguidor
T_X2 = KW(1, 'dos') - 0.05
T_COM_OUT = E(1) + 0.15
T_GO = E(1) + 0.2                    # camina al puerto de carga
T_DIVE = KW(2, 'meternos', after=True) + 0.05
T_IN = T_DIVE + 0.45                 # ya está adentro (placa)
T_TITLE = max(KW(2, 'Capítulo'), T_IN + 0.35)
T_TITLE_FLY = E(2) + 0.3
T_WALK_HOME = E(2) + 0.1
T_D_SLAP = P(4) - 0.05
T_CELL_SLAP = E(9) + 0.25
T_G_SLAP = E(10) + 0.25
T_X_SLAP = E(11) + 0.25
T_R_SLAP = E(14) + 0.25
T_END_SNAP = E(17) + 0.5
T_END = TL.END
PH_X = 790
PH_Y = S.FLOOR_Y - M.PH_H / 2 - 6
PORT = (PH_X, S.FLOOR_Y - 14)
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




# ======================= expresiones =======================
EXPR = [
    (0.0, 'curioso'), (T_ON + 0.1, 'sorpresa'), (T_ON + 0.5, 'feliz'), (T_PHOTO + 0.3, 'curioso'),
    (T_FLIP + 0.1, 'pensando'),
    (T_COM, 'feliz'), (T_X2, 'corazon'), (E(1), 'guino'),
    (P(2), 'feliz'), (T_DIVE - 0.2, 'guino'), (T_IN, 'mareado'), (T_IN + 0.5, 'feliz'), (T_TITLE, 'feliz'),
    (P(3), 'curioso'), (KW(3, 'RAM'), 'feliz'), (KW(3, 'ALMACENAMIENTO'), 'guino'),
    (P(4), 'curioso'), (KW(4, 'miles'), 'sorpresa'),
    (P(5), 'pensando'), (KW(5, 'AISLANTES'), 'feliz'),
    (P(6), 'curioso'), (KW(6, 'TÚNEL'), 'sorpresa'),
    (P(7), 'sorpresa'), (KW(7, 'cuántica'), 'pensando'), (KW(7, 'pasar'), 'feliz'),
    (P(8), 'curioso'), (KW(8, 'ATRAPADOS'), 'guino'), (KW(8, 'Por eso'), 'feliz'),
    (P(9), 'pensando'), (KW(9, 'sin electrones'), 'curioso'), (KW(9, 'con electrones'), 'feliz'),
    (P(10), 'sorpresa'), (KW(10, '8'), 'corazon'),
    (P(11), 'pensando'), (KW(11, 'BLOQUES'), 'sorpresa'), (KW(11, 'gasta'), 'curioso'),
    (P(12), 'feliz'), (KW(12, 'capítulo'), 'guino'),
    (P(13), 'curioso'), (KW(13, '64'), 'sorpresa'),
    (P(14), 'pensando'), (KW(14, 'MIL'), 'sorpresa'), (KW(14, 'apps'), 'feliz'),
    (P(15), 'feliz'), (KW(15, 'bolsillo'), 'corazon'),
    (P(16), 'feliz'), (KW(16, 'Gracias'), 'corazon'),
    (P(17), 'feliz'), (KW(17, 'Qué'), 'curioso'), (KW(17, 'Nos vemos'), 'guino'),
    (T_END_SNAP + 0.3, 'feliz'), (T_END_SNAP + 0.75, 'apagado'),
]


# ======================= caminatas =======================
WALKS = []
def setup_walks():
    plan = [
        (T_GO, PORT[0] - 150, max(0.5, T_DIVE - 0.35 - T_GO), True),
        (T_IN - 0.01, IN_X, 0.005, False),                         # aparece adentro (cae del techo)
        (T_WALK_HOME, HOME_X, 1.0, True),
        (P(6) + 0.3, 330, 0.9, True), (P(7) + 0.1, HOME_X, 0.9, True),
        (P(11) + 0.2, 330, 0.9, True), (P(12) + 0.1, HOME_X, 0.9, True),
        (P(15) + 0.2, 320, 0.9, True), (P(16) + 0.1, HOME_X, 0.9, True),
        (P(17) + 0.1, 300, 0.8, True),
    ]
    x = INTRO_X
    for t0, x1, d, steps in plan:
        WALKS.append((t0, t0 + d, x, x1))
        if steps:
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
            if b - a < 0.05:
                return x1, None
            u = S.ease_io((t - a) / (b - a))
            return x0 + (x1 - x0) * u, (a, b, x0, x1)
    return x, None


# ======================= tamaño del personaje (se encoge para entrar) =======================
def char_scale(t):
    if T_DIVE - 0.45 <= t < T_IN:
        u = S.ease_in(S.seg(t, T_DIVE - 0.45, T_DIVE))
        return 1 - 0.8 * u
    return 1.0

def char_visible(t):
    return not (T_DIVE + 0.02 <= t < T_IN)

def dive_offset(t):
    """mientras se encoge, se va hacia el puerto de carga"""
    if T_DIVE - 0.45 <= t < T_DIVE + 0.02:
        u = S.ease_in(S.seg(t, T_DIVE - 0.45, T_DIVE))
        x, _ = pos_x(t)
        return (PORT[0] - x) * u, 0
    return 0, 0

def fall_at(t):
    """cae del techo al aparecer adentro"""
    if T_IN <= t < T_IN + 0.38:
        u = S.ease_in(S.seg(t, T_IN, T_IN + 0.32))
        return 900 * (1 - u), u
    return 0.0, None


# ======================= estado del personaje =======================
def light_at(t):
    if t < T_ON:
        return 0.0
    if t > T_END_SNAP + 0.05:
        return 0.0
    return S.ease_out(S.seg(t, T_ON, T_ON + 0.35))

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
    fy, fu = fall_at(t)
    if fu is not None:
        yf -= fy
        p.larm = (0.2, 0, 2.6); p.rarm = (0.2, 0, 2.6)
        if fu >= 0.99:
            j = S.jelly(t - T_IN - 0.32, 3, 6)
            p.sy *= 1 - 0.25 * j; p.sx *= 1 + 0.2 * j
    elif T_IN + 0.38 <= t < T_IN + 0.8:
        j = S.jelly(t - T_IN - 0.32, 3, 6)
        p.sy *= 1 - 0.25 * j; p.sx *= 1 + 0.2 * j
    p.yaw += spin_at(t)
    intro_pose(p, t, x, yf)
    scene_gestures(p, t, x, yf)
    arm_window(p, t, x, yf)
    dx, dy = dive_offset(t)
    return p, x + dx, yf + dy, light_at(t), 0.0


def photo_hold(t):
    x, _ = pos_x(t)
    return (x + 175, S.FLOOR_Y - 30 * S.SCALE)

def intro_pose(p, t, x, yf):
    # toca la pantalla para prenderla
    if t < T_ON + 0.35:
        k = S.ease_out(S.seg(t, 0.0, 0.08)) * (1 - S.ease_io(S.seg(t, T_ON + 0.15, T_ON + 0.35)))
        tp = p.copy()
        aim(tp, 'l', shoulder_screen(x, yf, 'l', p.sx, p.sy), (PH_X - 150, PH_Y + 40), maxlen=3.0)
        blend_arm(p, 'l', tp, k)
    # sostiene la foto
    if T_PHOTO + 0.3 <= t < T_COM + 0.1:
        k = S.seg(t, T_PHOTO + 0.3, T_PHOTO + 0.45) * (1 - S.seg(t, T_COM - 0.1, T_COM + 0.1))
        tp = p.copy()
        h = photo_hold(t)
        aim(tp, 'l', shoulder_screen(x, yf, 'l', p.sx, p.sy), (h[0] - 50, h[1] + 30), maxlen=2.8)
        blend_arm(p, 'l', tp, k)
    # se rasca la cabeza al ver que detrás no hay nada
    if T_FLIP + 0.2 <= t < E(0) + 0.3:
        k = S.seg(t, T_FLIP + 0.2, T_FLIP + 0.35) * (1 - S.seg(t, E(0) + 0.1, E(0) + 0.3))
        tp = p.copy(); tp.rarm = (0.6, 0, 2.9 + 0.15 * math.sin(t * 22)); tp.relbow = 2.2
        blend_arm(p, 'r', tp, k)
        p.head = (p.head[0], p.head[1], p.head[2] + 0.15 * k)


def diagram_active(t):
    return (P(3) + 0.5 <= t < E(14))


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
            elif kind == 'heart':        # manos al pecho
                tp.larm = (1.3, 0, -0.5); tp.lelbow = 1.8; tp.rarm = (1.3, 0, -0.5); tp.relbow = 1.8
                blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
    # "con una pared delgadísima": mano en la barbilla
    a, b = KW(7, 'cuántica') - 0.2, KW(7, 'pasar') - 0.1
    if a <= t < b:
        k = S.seg(t, a, a + 0.2) * (1 - S.seg(t, b - 0.2, b))
        tp = p.copy(); tp.rarm = (1.9, 0, -0.2); tp.relbow = 2.0
        blend_arm(p, 'r', tp, k)
        p.head = (p.head[0] - 0.1 * k, p.head[1] + 0.3 * k, p.head[2] + 0.15 * k)
    # "Sin energía, se pierde todo": se encoge de hombros
    a = KW(14, 'Sin energía') - 0.1
    if a <= t < a + 0.9:
        k = S.seg(t, a, a + 0.15) * (1 - S.seg(t, a + 0.7, a + 0.9))
        tp = p.copy(); tp.larm = (0.4, 0, 1.0); tp.lelbow = 1.9; tp.rarm = (0.4, 0, 1.0); tp.relbow = 1.9
        blend_arm(p, 'l', tp, k); blend_arm(p, 'r', tp, k)
    # despedida
    a = KW(17, 'Nos vemos') - 0.2
    if a <= t < T_END_SNAP - 0.35:
        k = S.seg(t, a, a + 0.2)
        tp = p.copy(); tp.larm = (0.1, 0, 2.5 + 0.35 * math.sin((t - a) * 13)); tp.lelbow = 0.4; tp.larm_len = 1.2
        blend_arm(p, 'l', tp, k)
    if T_END_SNAP - 0.35 <= t < T_END_SNAP + 0.6:
        u = S.ease_out(S.seg(t, T_END_SNAP - 0.35, T_END_SNAP - 0.05)) * (1 - S.seg(t, T_END_SNAP + 0.3, T_END_SNAP + 0.6))
        tp = p.copy(); tp.rarm = (0.3, 0, 2.6); tp.relbow = 0.5
        blend_arm(p, 'r', tp, u)


# ======================= título =======================
_tc = {}
def title_imgs():
    if not _tc:
        _tc['a'] = S.fancy_text('CAPÍTULO 6', 92)
        _tc['b'] = S.fancy_text('LA MEMORIA', 96, top=(150, 255, 210), bot=(30, 170, 120), outline=(5, 50, 30))
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


# ======================= intro: celular gigante, foto y comentario =======================
def phone_state(t):
    """(escala, alfa) del celular gigante; al meterse, se agranda hacia el puerto"""
    if t >= T_IN:
        return None
    if t < T_DIVE:
        return 1.0, 1.0
    u = S.ease_in(S.seg(t, T_DIVE, T_IN))
    return 1 + 3.5 * u, 1 - S.seg(u, 0.7, 1.0)

def draw_phone(cv, t):
    st = phone_state(t)
    if st is None:
        return
    sc, al = st
    on = S.ease_out(S.seg(t, T_ON, T_ON + 0.3))
    img = M.phone_big(round(on * 4) / 4)
    # escalar alrededor del puerto de carga
    cx = PORT[0] + (PH_X - PORT[0]) * sc
    cy = PORT[1] + (PH_Y - PORT[1]) * sc
    if on > 0:
        S.glow_fast(cv, PH_X, PH_Y - 60, 420, (150, 190, 255), 0.35 * on * al)
    S.paste_center(cv, img, cx, cy, scale=sc, alpha=al)

def photo_pos(t):
    src = (PH_X, PH_Y - 120)
    if t < T_PHOTO:
        return None
    u = S.ease_out(S.seg(t, T_PHOTO, T_PHOTO + 0.4))
    h = photo_hold(t)
    dst = (h[0], h[1] - 120)
    return (src[0] + (dst[0] - src[0]) * u, src[1] + (dst[1] - src[1]) * u - 120 * math.sin(math.pi * u)), u

def draw_photo(cv, t):
    if t < T_PHOTO or t >= T_COM + 0.25:
        return
    pp = photo_pos(t)
    (x, y), u = pp
    out = S.ease_in(S.seg(t, T_COM - 0.1, T_COM + 0.25))
    fl = S.seg(t, T_FLIP, T_FLIP + 0.3)
    sxx = abs(math.cos(fl * math.pi))
    back = fl >= 0.5
    S.paste_center(cv, M.photo_card(back), x, y, scale=(0.4 + 0.6 * u) * (1 - out), sx=max(0.05, sxx), alpha=1 - out)

COM_Y = (330, 565)
def draw_comments(cv, t):
    if t < T_COM or t > T_COM_OUT + 0.35:
        return
    out = S.ease_in(S.seg(t, T_COM_OUT, T_COM_OUT + 0.35))
    for k, path in enumerate(('assets/comentario1.png', 'assets/comentario2.png')):
        a = S.ease_back(S.seg(t, T_COM + 0.25 * k, T_COM + 0.25 * k + 0.35))
        S.paste_center(cv, M.comment_shot(path, 900), 540, COM_Y[k], scale=a * (1 - 0.6 * out), alpha=1 - out)
    if t >= T_X2:
        a = S.ease_back(S.seg(t, T_X2, T_X2 + 0.3)) * (1 - out)
        S.paste_center(cv, D.label('×2', 56, fill=(255, 230, 120), bg=(200, 40, 70, 235)), 960, 600, scale=a,
                       angle=-0.15 + 0.05 * math.sin(t * 9))

def schedule_intro_sfx():
    ev(0.02, 'click', 0.5, panx(PH_X))
    ev(T_ON, 'chime', 0.45, panx(PH_X))
    ev(T_ON + 0.02, 'switch', 0.35, 0.0)
    ev(T_PHOTO, 'whoosh', 0.4, 0.2); ev(T_PHOTO + 0.4, 'pop', 0.4, 0.0)
    ev(T_FLIP, 'whoosh', 0.25, -0.1)
    ev(T_FLIP + 0.3, 'boing', 0.3, -0.1)
    ev(T_COM, 'pop', 0.45, 0.0); ev(T_COM + 0.25, 'pop', 0.45, 0.0)
    ev(T_X2, 'tink', 0.4, 0.6, f=2600)
    ev(T_DIVE - 0.45, 'whine', 0.3, panx(PORT[0]), dur=0.45, f0=1600, f1=400)
    ev(T_DIVE, 'whoosh', 0.7, panx(PORT[0]))
    ev(T_DIVE + 0.2, 'zap', 0.35, 0.0)
    ev(T_IN + 0.32, 'thud', 0.7, panx(IN_X)); ev(T_IN + 0.32, 'step', 0.6, panx(IN_X), heavy=1.0)
    SHAKES.append((T_IN + 0.32, 0.3, 10))

def draw_dive_flash(cv, t):
    a = 0.0
    if T_IN - 0.15 <= t < T_IN + 0.35:
        u = S.seg(t, T_IN - 0.15, T_IN + 0.35)
        a = math.sin(u * math.pi)
    if a > 0.01:
        cv.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * a))))


# ======================= escena Dk: dos memorias (escritorio y archivero) =======================
Dk = {}
DESK_C = (560, 610)
CAB_C = (880, 590)

def setup_Dk():
    Dk['desk'] = add_throw(KW(3, 'RAM') - 0.35, DESK_C, lambda t: M.desk_img(1.0), 'l', dur=0.42, arc=160, spin=0.4)
    Dk['cab'] = add_throw(KW(3, 'ALMACENAMIENTO') - 0.35, CAB_C, lambda t: M.cabinet_img(), 'l', dur=0.45, arc=160, spin=0.3)
    Dk['lram'] = KW(3, 'RAM')
    Dk['lalm'] = KW(3, 'ALMACENAMIENTO')
    ev(Dk['lram'] + 0.1, 'pop', 0.35, panx(DESK_C[0])); ev(Dk['lalm'] + 0.1, 'pop', 0.35, panx(CAB_C[0]))
    # el escritorio se va de un manotazo; el archivero se vuelve chip
    SLAPS.append((T_D_SLAP, 'l'))
    ev(T_D_SLAP, 'whoosh', 0.5, 0.2)

def draw_Dk(cv, t):
    if t < Dk['desk']['t0'] or t > P(5) + 0.4:
        return
    # escritorio
    if t < T_D_SLAP + 0.6:
        def place(c, sx, sy):
            if t < T_D_SLAP:
                S.paste_center(c, M.desk_img(1.0), DESK_C[0], DESK_C[1], sx=sx, sy=sy)
            else:
                u = S.seg(t, T_D_SLAP, T_D_SLAP + 0.6)
                S.paste_center(c, M.desk_img(1.0), DESK_C[0] - 900 * S.ease_in(u), DESK_C[1] - 300 * math.sin(u * math.pi),
                               angle=4 * u, alpha=1 - u)
        draw_thrown(cv, Dk['desk'], t, place)
    if Dk['lram'] <= t < T_D_SLAP:
        k = S.ease_back(S.seg(t, Dk['lram'], Dk['lram'] + 0.3))
        S.paste_center(cv, D.label('RAM', 36, fill=(140, 230, 255)), DESK_C[0], 420, scale=k)
    # archivero → chip
    tz = KW(4, 'FLASH') - 0.3
    def place2(c, sx, sy):
        if t < P(4):
            S.paste_center(c, M.cabinet_img(), CAB_C[0], CAB_C[1], sx=sx, sy=sy)
        else:
            u = S.ease_io(S.seg(t, P(4), tz))
            x = CAB_C[0] + (700 - CAB_C[0]) * u; y = CAB_C[1] + (560 - CAB_C[1]) * u
            S.paste_center(c, M.cabinet_img(), x, y, scale=1 + 0.3 * u, alpha=1 - S.seg(t, tz, tz + 0.25))
    if t < tz + 0.3:
        draw_thrown(cv, Dk['cab'], t, place2)
    if Dk['lalm'] <= t < P(4):
        k = S.ease_back(S.seg(t, Dk['lalm'], Dk['lalm'] + 0.3))
        S.paste_center(cv, D.label('ALMACENAMIENTO', 30, fill=(255, 220, 140)), CAB_C[0] - 40, 375, scale=k)
    if KW(3, 'escritorio') <= t < T_D_SLAP:
        k = S.ease_back(S.seg(t, KW(3, 'escritorio'), KW(3, 'escritorio') + 0.3))
        S.paste_center(cv, D.label('ANALOGÍA', 22, fill=(200, 200, 210), bg=(20, 22, 28, 170)), 720, 835, scale=k)
    # chip con miles de millones de celdas
    if t >= tz:
        a = S.ease_back(S.seg(t, tz, tz + 0.35))
        zoom = S.ease_in(S.seg(t, P(5) - 0.05, P(5) + 0.35))
        hi = S.seg(t, P(5) - 0.4, P(5) - 0.1)
        S.paste_center(cv, M.chip_grid(round(hi * 4) / 4), 700, 560, scale=0.92 * a * (1 + 2.5 * zoom), alpha=1 - zoom)
        if t < P(5):
            S.paste_center(cv, D.label('MEMORIA FLASH', 32, fill=(160, 255, 200)), 700, 300, scale=a)
        kl = KW(4, 'miles')
        if kl <= t < P(5):
            k = S.ease_back(S.seg(t, kl, kl + 0.3))
            S.paste_center(cv, D.label('MILES DE MILLONES DE CELDAS', 26, fill=(255, 240, 160)), 700, 840, scale=k)


# ======================= escena Ce: la celda flash =======================
Ce = {}
CELL_C = (700, 560)
CELL_O = (CELL_C[0] - M.CW // 2, CELL_C[1] - M.CH_ // 2)
NE = 7
_er = random.Random(11)
E_X = [CELL_O[0] + 150 + k * 50 + _er.uniform(-6, 6) for k in range(NE)]

def setup_Ce():
    Ce['b0'] = P(5) + 0.05
    Ce['b1'] = KW(5, 'AISLANTES')
    Ce['v0'] = KW(6, '20') - 0.3
    Ce['e0'] = KW(6, 'electrones') - 0.1
    Ce['tun'] = KW(6, 'TÚNEL') - 0.1
    Ce['cmp0'] = P(7) + 0.05
    Ce['cmp1'] = E(7) + 0.2
    Ce['off'] = KW(8, 'quitar') - 0.05
    Ce['trap'] = KW(8, 'ATRAPADOS') - 0.1
    Ce['nob'] = KW(8, 'Por eso') - 0.05
    Ce['rd'] = P(9) - 0.05
    Ce['b_1'] = KW(9, 'sin electrones') - 0.05
    Ce['b_0'] = KW(9, 'con electrones') - 0.05
    for k in range(5):
        ev(Ce['b0'] + k * (Ce['b1'] - Ce['b0']) / 5, 'block', 0.35, panx(CELL_C[0]), pitch=0.9 + 0.08 * k)
    ev(Ce['v0'], 'whine', 0.3, panx(880), dur=0.8, f0=300, f1=1400)
    for k in range(NE):
        ev(Ce['e0'] + k * 0.17 + 0.35, 'tink', 0.18, panx(E_X[k]), f=2200 + 120 * k)
    ev(Ce['tun'], 'zap', 0.3, panx(CELL_C[0]))
    ev(Ce['cmp0'], 'pop', 0.4, -0.2); ev(Ce['cmp0'] + 0.15, 'pop', 0.4, 0.3)
    ev(Ce['off'], 'switch', 0.5, panx(880))
    ev(Ce['trap'], 'pop', 0.4, panx(CELL_C[0]))
    ev(Ce['rd'], 'pop', 0.4, -0.2); ev(Ce['rd'] + 0.12, 'pop', 0.4, 0.3)
    ev(Ce['b_1'], 'tink', 0.35, -0.2, f=1800); ev(Ce['b_0'], 'tink', 0.35, 0.3, f=2400)
    add_slap(T_CELL_SLAP)

def volts(t):
    if t < Ce['v0']:
        return 3
    if t < Ce['off']:
        return 3 + 17 * S.ease_io(S.seg(t, Ce['v0'], Ce['v0'] + 0.8))
    return 20 * (1 - S.ease_out(S.seg(t, Ce['off'], Ce['off'] + 0.3)))

def e_pos(k, t):
    t0 = Ce['e0'] + k * 0.17
    y_si = CELL_O[1] + 300 - (k % 3) * 18
    y_tr = CELL_O[1] + 185
    if t < t0:
        return E_X[k], y_si, 0.0
    u = S.ease_io(S.seg(t, t0, t0 + 0.45))
    return E_X[k], y_si + (y_tr - y_si) * u, u

def cmp_vis(t):
    return S.seg(t, Ce['cmp0'] - 0.1, Ce['cmp0'] + 0.2) * (1 - S.seg(t, Ce['cmp1'] - 0.2, Ce['cmp1']))

def draw_Ce(cv, t, at=None):
    if t < Ce['b0'] or t > T_CELL_SLAP + 1.0:
        return
    if t >= T_CELL_SLAP and at is None:
        shattered(cv, draw_Ce, T_CELL_SLAP, t, 6)
        return
    rd = S.seg(t, Ce['rd'], Ce['rd'] + 0.3)
    cvis = (1 - cmp_vis(t)) * (1 - rd)
    if cvis > 0.01:
        build = S.seg(t, Ce['b0'], Ce['b1'] + 0.1)
        S.paste_center(cv, M.cell_layer(round(build * 10) / 10), CELL_C[0], CELL_C[1], alpha=cvis)
        if t >= Ce['b1'] - 0.2 and t < Ce['v0']:
            a = S.seg(t, Ce['b1'] - 0.2, Ce['b1'] + 0.1)
            S.paste_center(cv, D.label('ÓXIDO TÚNEL (delgadísimo)', 22, fill=(170, 225, 255)), CELL_C[0], CELL_O[1] + 375, alpha=a * cvis)
        # voltímetro
        if t >= Ce['v0'] - 0.3:
            a = S.ease_back(S.seg(t, Ce['v0'] - 0.3, Ce['v0'])) * cvis
            S.paste_center(cv, M.volt_meter(volts(t)), 935, 322, scale=0.8 * a)
        # brillo del óxido túnel mientras cruzan
        if Ce['e0'] <= t < Ce['e0'] + NE * 0.17 + 0.6:
            S.glow_fast(cv, CELL_C[0], CELL_O[1] + 218, 220, (150, 220, 255), 0.35 * cvis)
        if t >= Ce['e0']:
            for k in range(NE):
                x, y, u = e_pos(k, t)
                S.paste_center(cv, M.electron(), x, y, scale=0.9, alpha=cvis)
        if Ce['tun'] <= t < Ce['cmp0']:
            a = S.ease_back(S.seg(t, Ce['tun'], Ce['tun'] + 0.3)) * cvis
            S.paste_center(cv, D.label('¡EFECTO TÚNEL!', 32, fill=(140, 220, 255)), 560, 300, scale=a)
        if t >= Ce['trap']:
            a = S.ease_back(S.seg(t, Ce['trap'], Ce['trap'] + 0.3)) * cvis
            S.paste_center(cv, D.label('ATRAPADOS', 30, fill=(255, 230, 120)), CELL_C[0], CELL_O[1] - 10, scale=a)
        if t >= Ce['nob']:
            a = S.ease_back(S.seg(t, Ce['nob'], Ce['nob'] + 0.3)) * cvis
            S.paste_center(cv, D.label('SIN ENERGÍA: SIGUEN AHÍ', 26, fill=(160, 255, 190)), CELL_C[0], CELL_O[1] + 375, scale=a)
    # comparación: saltar ✗ / atravesar ✓
    cmv = cmp_vis(t)
    if cmv > 0.01:
        u = ((t - Ce['cmp0']) % 1.6) / 1.6
        S.paste_center(cv, M.tunnel_panel(False, u), 545, 560, scale=0.95 * cmv)
        S.paste_center(cv, M.tunnel_panel(True, u), 865, 560, scale=0.95 * cmv)
        S.paste_center(cv, D.label('FÍSICA CUÁNTICA', 30, fill=(200, 170, 255)), 705, 330, scale=cmv)
    # lectura: voltaje umbral
    if rd > 0.01:
        a = S.ease_back(rd)
        S.paste_center(cv, M.mini_cell(False, S.seg(t, Ce['b_1'], Ce['b_1'] + 0.2)), 545, 520, scale=1.3 * a)
        S.paste_center(cv, M.mini_cell(True, S.seg(t, Ce['b_0'], Ce['b_0'] + 0.2)), 875, 520, scale=1.3 * a)
        v = 0.25 if t < Ce['b_0'] else 0.25 + 0.5 * S.ease_io(S.seg(t, Ce['b_0'], Ce['b_0'] + 0.4))
        S.paste_center(cv, M.gauge(v), 710, 815, scale=1.15 * a)
        S.paste_center(cv, D.label('¿A QUÉ VOLTAJE CONDUCE?', 26, fill=(255, 230, 140)), 710, 310, scale=a)


# ======================= escena Gl: ocho niveles =======================
Gl = {}
GL_C = (680, 560)

def setup_Gl():
    Gl['th'] = add_throw(P(10) - 0.2, GL_C, lambda t: M.glass(0), 'l', dur=0.45, arc=170, spin=0.4)
    Gl['s0'] = KW(10, 'midiendo')
    Gl['s1'] = KW(10, '3 bits') - 0.1
    Gl['lbl'] = KW(10, '8') - 0.1
    for k in range(7):
        ev(Gl['s0'] + (k + 1) * (Gl['s1'] - Gl['s0']) / 7, 'tink', 0.25, panx(GL_C[0]), f=900 + 180 * k)
    ev(Gl['lbl'], 'pop', 0.45, panx(GL_C[0]))
    add_slap(T_G_SLAP)

def glass_level(t):
    if t < Gl['s0']:
        return 0
    step = (Gl['s1'] - Gl['s0']) / 7
    n = int(min(7, (t - Gl['s0']) / step))
    frac = S.ease_out(S.seg((t - Gl['s0']) - n * step, 0, 0.15))
    return min(7, n + frac) if n < 7 else 7

def draw_Gl(cv, t, at=None):
    if t < Gl['th']['t0'] or t > T_G_SLAP + 1.0:
        return
    if t >= T_G_SLAP and at is None:
        shattered(cv, draw_Gl, T_G_SLAP, t, 8)
        return
    lv = glass_level(t)
    def place(c, sx, sy):
        S.paste_center(c, M.glass(round(lv * 4) / 4), GL_C[0], GL_C[1], sx=sx, sy=sy)
    draw_thrown(cv, Gl['th'], t, place, img_now=M.glass(0))
    if Gl['s0'] <= t < Gl['s1'] + 0.2:
        ph = ((t - Gl['s0']) / ((Gl['s1'] - Gl['s0']) / 7)) % 1.0
        S.paste_center(cv, D.label('PULSO → MIDE', 22, fill=(170, 225, 255)), 930, 360, alpha=1.0 if ph < 0.5 else 0.55)
    if t >= Gl['lbl']:
        a = S.ease_back(S.seg(t, Gl['lbl'], Gl['lbl'] + 0.3))
        S.paste_center(cv, D.label('8 NIVELES = 3 BITS (TLC)', 30, fill=(255, 230, 120)), 680, 840, scale=a)


# ======================= escena Bk: se borra por bloques y se gasta =======================
Bk = {}
BK_C = (700, 560)

def setup_Bk():
    Bk['in'] = P(11) - 0.1
    Bk['try'] = KW(11, 'borra') - 0.15
    Bk['sw0'] = KW(11, 'BLOQUES') - 0.1
    Bk['sw1'] = Bk['sw0'] + 0.7
    Bk['wear'] = KW(11, 'ciclo') - 0.1
    ev(Bk['in'], 'pop', 0.4, panx(BK_C[0]))
    ev(Bk['try'] + 0.25, 'boing', 0.4, panx(BK_C[0]))
    ev(Bk['sw0'], 'roll', 0.5, panx(BK_C[0]), dur=0.7)
    ev(Bk['wear'] + 0.3, 'crumble', 0.3, panx(BK_C[0]))
    add_slap(T_X_SLAP)

def draw_Bk(cv, t, at=None):
    if t < Bk['in'] or t > T_X_SLAP + 1.0:
        return
    if t >= T_X_SLAP and at is None:
        shattered(cv, draw_Bk, T_X_SLAP, t, 9)
        return
    a = S.ease_back(S.seg(t, Bk['in'], Bk['in'] + 0.35))
    wv = S.seg(t, Bk['wear'], Bk['wear'] + 0.3)
    sw = None if t < Bk['sw0'] else S.ease_io(S.seg(t, Bk['sw0'], Bk['sw1']))
    if wv < 1:
        S.paste_center(cv, M.block_grid(0, None if sw is None else round(sw * 8) / 8), BK_C[0], BK_C[1], scale=0.95 * a, alpha=1 - wv)
    # borrador chico: intenta borrar UNA celda y rebota
    if Bk['try'] <= t < Bk['sw0']:
        u = S.seg(t, Bk['try'], Bk['try'] + 0.5)
        x = 640 + 30 * math.sin(u * math.pi * 3) * (1 - u); y = 500
        S.paste_center(cv, M.eraser(0.6), x, y, angle=0.3 * math.sin(u * 12) * (1 - u))
        if t >= Bk['try'] + 0.25:
            S.paste_center(cv, D.label('✗ UNA SOLA, NO', 26, fill=(255, 130, 130)), 700, 300, scale=S.ease_back(S.seg(t, Bk['try'] + 0.25, Bk['try'] + 0.5)))
    # borrador gigante barre el bloque completo
    if sw is not None and wv < 1:
        x = BK_C[0] - 200 + 400 * sw
        S.paste_center(cv, M.eraser(2.2), x, BK_C[1] - 60, angle=-0.2, alpha=1 - S.seg(t, Bk['sw1'], Bk['sw1'] + 0.2))
        S.paste_center(cv, D.label('SE BORRA EL BLOQUE ENTERO', 26, fill=(255, 220, 140)), 700, 300, scale=S.ease_back(S.seg(t, Bk['sw0'], Bk['sw0'] + 0.3)), alpha=1 - wv)
    # desgaste del aislante
    if wv > 0:
        crack = S.seg(t, Bk['wear'] + 0.2, E(11))
        S.paste_center(cv, M.cell_layer(1.0, True, round(crack * 5) / 5), CELL_C[0], CELL_C[1], alpha=wv)
        S.paste_center(cv, D.label('CADA CICLO GASTA UN POQUITO EL AISLANTE', 22, fill=(255, 190, 150)), 700, 300, alpha=wv)


# ======================= escena Rm: la RAM =======================
Rm = {}
DC_C = (720, 560)
GRID_O = (470, 400)
NR, NCc = 4, 6
CC = 78

def setup_Rm():
    Rm['th'] = add_throw(P(12) - 0.1, DC_C, lambda t: M.dram_cell(1.0), 'l', dur=0.45, arc=170, spin=0.3)
    Rm['lbl'] = KW(12, 'CONDENSADOR') - 0.1
    Rm['g0'] = P(13) - 0.05
    Rm['ms'] = KW(13, '64') - 0.1
    Rm['off'] = KW(14, 'Sin energía') - 0.05
    Rm['race'] = KW(14, 'responde') - 0.1
    Rm['k1000'] = KW(14, 'MIL') - 0.05
    Rm['apps'] = KW(14, 'apps') - 0.1
    ev(Rm['lbl'], 'pop', 0.4, panx(DC_C[0]))
    ev(Rm['g0'], 'pop', 0.4, panx(DC_C[0]))
    t = Rm['g0'] + 0.9
    while t < Rm['off']:
        ev(t, 'tink', 0.12, panx(DC_C[0]), f=3000)
        t += 1.1
    ev(Rm['off'], 'switch', 0.6, panx(DC_C[0])); ev(Rm['off'] + 0.05, 'tvoff', 0.3, panx(DC_C[0]))
    ev(Rm['race'], 'whoosh', 0.6, 0.4)
    ev(Rm['k1000'], 'pop', 0.45, 0.2)
    ev(Rm['apps'], 'tink', 0.3, 0.2, f=2400)
    add_slap(T_R_SLAP)

def ram_q(t, r, c):
    """nivel de carga de cada celda: se va descargando y la recarga pasa fila por fila (cámara lenta)"""
    if t >= Rm['off']:
        return max(0.0, 1 - S.seg(t, Rm['off'], Rm['off'] + 0.5)) * ram_q(Rm['off'] - 0.001, r, c)
    if (r * 7 + c * 3) % 5 == 0:
        return 0.0      # algunas celdas guardan un 0
    period = 1.1
    tt = t - Rm['g0'] - r * period / NR
    since = tt % period
    return max(0.35, 1 - since / period * 0.6)

def draw_Rm(cv, t, at=None):
    if t < Rm['th']['t0'] or t > T_R_SLAP + 1.0:
        return
    if t >= T_R_SLAP and at is None:
        shattered(cv, draw_Rm, T_R_SLAP, t, 10)
        return
    gv = S.seg(t, Rm['g0'], Rm['g0'] + 0.3)
    rv = S.seg(t, Rm['race'] - 0.2, Rm['race'] + 0.1)
    # celda DRAM
    if gv < 1:
        def place(c, sx, sy):
            S.paste_center(c, M.dram_cell(1.0), DC_C[0], DC_C[1], scale=1.25, sx=sx, sy=sy, alpha=1 - gv)
        draw_thrown(cv, Rm['th'], t, place)
        if t >= Rm['lbl']:
            S.paste_center(cv, D.label('RAM: TRANSISTOR + CONDENSADOR', 26, fill=(140, 230, 255)), DC_C[0], 330,
                           scale=S.ease_back(S.seg(t, Rm['lbl'], Rm['lbl'] + 0.3)), alpha=1 - gv)
    # cuadrícula que se descarga y se recarga
    if gv > 0 and rv < 1:
        al = gv * (1 - rv)
        for r in range(NR):
            for c in range(NCc):
                q = ram_q(t, r, c)
                S.paste_center(cv, M.cap_cell(round(q * 10) / 10, 62), GRID_O[0] + c * CC, GRID_O[1] + r * (CC + 8), alpha=al)
        if t < Rm['off']:
            period = 1.1
            rr = int(((t - Rm['g0']) % period) / (period / NR))
            y = GRID_O[1] + rr * (CC + 8)
            d = ImageDraw.Draw(cv, 'RGBA')
            d.rounded_rectangle([GRID_O[0] - 44, y - 40, GRID_O[0] + (NCc - 1) * CC + 44, y + 44], 12, outline=(255, 230, 120, int(220 * al)), width=5)
            S.paste_center(cv, D.label('RECARGA ↻', 22, fill=(255, 230, 120)), GRID_O[0] + (NCc - 1) * CC + 40, y - 52, alpha=al)
        if t >= Rm['ms']:
            S.paste_center(cv, D.label('CADA 64 ms O MENOS', 30, fill=(255, 230, 120)), 680, 760, scale=S.ease_back(S.seg(t, Rm['ms'], Rm['ms'] + 0.3)) * (1 - rv))
            S.paste_center(cv, D.label('(aquí en cámara lenta)', 20, fill=(200, 200, 210), bg=(20, 22, 28, 170)), 680, 825, alpha=al)
        if t >= Rm['off']:
            S.paste_center(cv, D.label('SIN ENERGÍA: SE PIERDE', 28, fill=(255, 140, 140)), 680, 300, scale=S.ease_back(S.seg(t, Rm['off'], Rm['off'] + 0.3)) * (1 - rv))
    # carrera: tiempo de respuesta
    if rv > 0:
        u = t - Rm['race']
        fr_ram = S.ease_out(S.seg(u, 0.05, 0.3))
        fr_fl = S.seg(u, 0.05, 6.0) * 0.12
        S.paste_center(cv, M.race_bar('RAM', fr_ram, (80, 220, 140), 'decenas de ns'), 700, 430, alpha=rv)
        S.paste_center(cv, M.race_bar('FLASH', fr_fl, (255, 170, 80), 'decenas de µs'), 700, 570, alpha=rv)
        if t >= Rm['k1000']:
            S.paste_center(cv, D.label('~1000× MÁS RÁPIDA EN RESPONDER', 28, fill=(160, 255, 190)), 700, 310, scale=S.ease_back(S.seg(t, Rm['k1000'], Rm['k1000'] + 0.3)))
        if t >= Rm['apps']:
            S.paste_center(cv, D.label('APPS ABIERTAS → RAM', 30, fill=(140, 230, 255)), 700, 720, scale=S.ease_back(S.seg(t, Rm['apps'], Rm['apps'] + 0.3)))


# ======================= remate: foto = electrones atrapados =======================
Rt = {}
def setup_Rt():
    Rt['in'] = P(15) + 0.05
    Rt['lbl'] = KW(15, 'atrapados') - 0.1
    Rt['out'] = P(16) - 0.1
    ev(Rt['in'], 'pop', 0.45, 0.3)
    ev(Rt['lbl'], 'chime', 0.35, 0.3)

def draw_Rt(cv, t):
    if t < Rt['in'] or t > Rt['out'] + 0.3:
        return
    a = S.ease_back(S.seg(t, Rt['in'], Rt['in'] + 0.35)) * (1 - S.ease_in(S.seg(t, Rt['out'], Rt['out'] + 0.3)))
    S.glow_fast(cv, 700, 540, 220, (120, 180, 255), 0.35 * a)
    S.paste_center(cv, M.photo_card(False, 260), 700, 540, scale=a, angle=0.06 * math.sin(t * 2))
    if t >= Rt['lbl']:
        for k in range(10):
            ang = t * 2.2 + k * 2 * math.pi / 10
            S.paste_center(cv, M.electron(12), 700 + 210 * math.cos(ang), 540 + 160 * math.sin(ang), alpha=a * S.seg(t, Rt['lbl'], Rt['lbl'] + 0.3))
        S.paste_center(cv, D.label('ELECTRONES ATRAPADOS', 30, fill=(140, 220, 255)), 700, 790, scale=a * S.ease_back(S.seg(t, Rt['lbl'], Rt['lbl'] + 0.3)))


# ======================= gracias: el comentario otra vez =======================
Gr = {}
def setup_Gr():
    Gr['in'] = P(16) - 0.05
    Gr['heart'] = KW(16, 'Gracias') - 0.1
    Gr['out'] = P(17) - 0.2
    ev(Gr['in'], 'pop', 0.45, 0.0)
    ev(Gr['heart'], 'chime', 0.4, 0.3)

def draw_Gr(cv, t):
    if t < Gr['in'] or t > Gr['out'] + 0.3:
        return
    a = S.ease_back(S.seg(t, Gr['in'], Gr['in'] + 0.35)) * (1 - S.ease_in(S.seg(t, Gr['out'], Gr['out'] + 0.3)))
    S.paste_center(cv, M.comment_shot('assets/comentario2.png', 900), 540, 470, scale=a)
    if t >= Gr['heart']:
        k = S.ease_back(S.seg(t, Gr['heart'], Gr['heart'] + 0.3)) * a
        S.paste_center(cv, D.label('♥ ¡GRACIAS!', 40, fill=(255, 255, 255), bg=(220, 40, 80, 240)), 760, 640,
                       scale=k * (1 + 0.06 * math.sin(t * 10)))


# ======================= cierre: botones y pregunta =======================
Fin = {}
BTN = {'like': (770, 600), 'sub': (770, 735), 'follow': (770, 870)}

def setup_Fin():
    Fin['btn_in'] = P(17) - 0.15
    Fin['hit'] = {'like': KW(17, 'me gusta'), 'sub': KW(17, 'suscríbete'), 'follow': KW(17, 'sígueme')}
    Fin['q'] = KW(17, 'Qué') - 0.1
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
    if t >= Fin['btn_in'] and t < Fin['q'] + 0.3:
        for i, k in enumerate(('like', 'sub', 'follow')):
            s = S.ease_back(S.seg(t, Fin['btn_in'] + i * 0.1, Fin['btn_in'] + i * 0.1 + 0.35)) * (1 - S.ease_in(S.seg(t, Fin['q'] - 0.05, Fin['q'] + 0.3)))
            th = Fin['hit'][k]
            pressed = 1.0 if t >= th else 0.0
            sq = 1 - 0.25 * S.jelly(t - th, 3, 6) if t >= th else 1.0
            S.paste_center(cv, D.end_button(k, pressed), BTN[k][0], BTN[k][1], scale=s, sx=2 - sq, sy=sq)
    if Fin['q'] <= t < T_END_SNAP + 0.4:
        k = S.ease_back(S.seg(t, Fin['q'], Fin['q'] + 0.35)) * (1 - S.ease_in(S.seg(t, T_END_SNAP + 0.05, T_END_SNAP + 0.35)))
        S.glow_fast(cv, 700, 520, 170, (200, 170, 255), 0.4 * k)
        S.paste_center(cv, M.mystery_box(), 700, 520, scale=0.95 * k, angle=0.05 * math.sin((t - Fin['q']) * 6))
        S.paste_center(cv, D.label('CAP. 7', 30, fill=(255, 220, 120)), 700, 700, alpha=S.seg(t, Fin['q'] + 0.2, Fin['q'] + 0.4) * k)


def setup_all():
    setup_walks()
    schedule_intro_sfx()
    setup_title()
    setup_Dk()
    setup_Ce()
    setup_Gl()
    setup_Bk()
    setup_Rm()
    setup_Rt()
    setup_Gr()
    setup_Fin()
    react = [
        (T_ON + 0.05, 0.4, 50, None),                         # ¡se prendió!
        (T_X2 + 0.05, 0.45, 60, 'up'),                        # ¡dos veces!
        (T_TITLE - 0.05, 0.7, 110, 'spin'),                   # título
        (Ce['tun'] + 0.05, 0.45, 60, 'up'),                   # ¡efecto túnel!
        (Gl['lbl'] + 0.05, 0.45, 70, 'up'),                   # ¡3 bits!
        (Bk['sw0'] + 0.1, 0.4, 40, None),                     # ¡el bloque entero!
        (Rm['k1000'] + 0.05, 0.45, 60, 'up'),                 # ¡mil veces!
        (Gr['heart'] + 0.02, 0.6, 0, 'heart'),                # gracias
    ]
    for t0, d, h, kind in react:
        if h > 0:
            JUMPS.append((t0, d, h))
            ev(t0 + d, 'step', 0.45, 0.0, heavy=0.9)
        if kind == 'spin':
            SPINS.append((t0, d)); ev(t0, 'whoosh', 0.3, 0.0)
        if kind:
            REACT_ARMS.append((t0, d, kind))
    # señala los diagramas en momentos clave
    POINTS.append((KW(6, 'electrones') - 0.1, KW(6, 'TÚNEL') + 0.3, 'l', lambda t: (CELL_C[0] - 120, CELL_O[1] + 218)))
    POINTS.append((KW(15, 'foto') - 0.1, KW(15, 'bolsillo') + 0.3, 'l', lambda t: (560, 560)))

setup_all()


_bg = {}
def bg_at(t, light):
    if 'stone' not in _bg:
        _bg['stone'] = S.lit_room().convert('RGBA')
        _bg['stone_np'] = np.array(_bg['stone'].convert('RGB'), np.float32)
    if t < T_IN:
        base, arr = _bg['stone'], _bg['stone_np']
    else:
        L_ = PCB.layers(); base, arr = L_['full'], L_['full_np']
    if light >= 0.999:
        return base.copy()
    if light <= 0.001:
        return Image.new('RGBA', (W, H), (0, 0, 0, 255))
    return Image.fromarray((arr * light).astype(np.uint8), 'RGB').convert('RGBA')


def render_frame(t):
    pose, x, yf, light, glow = char_state(t)
    cv = bg_at(t, light)
    if t >= T_IN:
        PCB.draw_anim(cv, t, light)
    sw = 0.0
    if t >= T_END_SNAP:
        sw = 0.04 * math.sin((t - T_END_SNAP) * 5) * math.exp(-(t - T_END_SNAP))
    for t0 in (T_IN + 0.32,):
        if t0 <= t < t0 + 1.4:
            sw += 0.06 * math.sin((t - t0) * 7) * math.exp(-(t - t0) * 2.5)
    S.draw_lamp(cv, on=light, swing=sw)
    if light > 0.05:
        S.glow_fast(cv, S.LAMP_X + math.sin(sw) * S.LAMP_Y, math.cos(sw) * S.LAMP_Y + 22, 90, (255, 230, 150), 0.6 * light)
    if t >= T_TITLE_FLY + 0.4 and t < T_END_SNAP + 0.1:
        S.draw_label(cv, LABEL_TXT, alpha=S.seg(t, T_TITLE_FLY + 0.4, T_TITLE_FLY + 0.6) * light)
    draw_phone(cv, t)
    draw_title(cv, t)
    # ----- escenas -----
    draw_Dk(cv, t)
    draw_Ce(cv, t)
    draw_Gl(cv, t)
    draw_Bk(cv, t)
    draw_Rm(cv, t)
    draw_Rt(cv, t)
    # ----- sombra -----
    cs = char_scale(t)
    if light > 0.05 and char_visible(t):
        h = S.FLOOR_Y - yf
        sh_w = 150 * cs * max(0.4, 1 - h / 600)
        d = ImageDraw.Draw(cv, 'RGBA')
        d.ellipse([x - sh_w, S.FLOOR_Y - 14, x + sh_w, S.FLOOR_Y + 12], fill=(0, 0, 0, int(110 * light * max(0.3, 1 - h / 500))))
    # ----- personaje -----
    char_light = 0.32 + 0.68 * light if t < T_END_SNAP + 1.3 else 0.32
    if t < T_ON:
        char_light = 0.42
    if char_visible(t):
        CH.render(cv, pose, dict(scale=S.SCALE * cs, ox=x, oy=yf, view_yaw=0.12 * math.sin(t * 0.2)), light=char_light, t=t)
    draw_photo(cv, t)
    draw_comments(cv, t)
    draw_Gr(cv, t)
    draw_Fin(cv, t)
    draw_dive_flash(cv, t)
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
