#!/usr/bin/env python3
# Render completo del capítulo 3: audio (voz + efectos ASMR) y video 1080x1920 30 fps.
import os
import sys
import json
import math
import subprocess
import numpy as np
from multiprocessing import Process

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)
SR = 48000


def load_voice():
    """voz original (mono float, 48k) si existe"""
    p = os.path.join(HERE, 'voice.wav')
    if not os.path.exists(p):
        return None
    import wave
    w = wave.open(p)
    n = w.getnframes(); ch = w.getnchannels(); sr = w.getframerate()
    raw = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    if ch > 1:
        raw = raw.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        raise SystemExit('voice.wav debe estar a 48 kHz')
    return raw


def build_audio(V, TL):
    import sfx as X
    dur = V.T_END + 0.5
    mix = X.Mixer(dur)
    voice = load_voice()
    vtrack = np.zeros(mix.n)
    if voice is not None and TL.cuts:
        for i, c in enumerate(TL.cuts):
            a, b = int(c['a'] * SR), int(c['b'] * SR)
            seg = voice[a:b].copy()
            f = min(len(seg) // 4, int(0.012 * SR))
            if f > 0:
                seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
            s0 = int(TL.T[i] * SR)
            m = min(len(seg), mix.n - s0)
            vtrack[s0:s0 + m] += seg[:m]
        pk = np.max(np.abs(vtrack)) + 1e-9
        vtrack = vtrack / pk * 0.85
    # envolvente de la boca (100 Hz)
    hop = SR // 100
    nwin = len(vtrack) // hop
    env = np.sqrt(np.mean(vtrack[:nwin * hop].reshape(nwin, hop) ** 2, axis=1))
    if env.max() > 0:
        env = np.clip(env / (np.percentile(env[env > 0.01], 90) + 1e-9), 0, 1.2)
    sm = np.zeros_like(env); acc = 0
    for k in range(len(env)):
        acc = acc * 0.55 + env[k] * 0.45; sm[k] = acc
    np.save(os.path.join(OUT, 'mouth_env.npy'), sm)

    # ---------- efectos ----------
    seeds = iter(range(1000, 100000))
    for (t, name, gain, pan, kw) in V.EVENTS:
        sd = next(seeds)
        if name == 'drone':
            snd = X.float_drone(kw.get('dur', 3.0))
        elif name == 'pop':
            snd = X.pop(kw.get('f0', 500), kw.get('f1', 1200))
        elif name == 'snap':
            snd = X.snap(sd)
        elif name == 'thud':
            snd = X.thud(sd)
        elif name == 'block':
            snd = X.block_place(sd, kw.get('pitch', 1.0))
        elif name == 'step':
            snd = X.step_wood(sd, kw.get('heavy', 1.0))
        elif name == 'tink':
            snd = X.tink(kw.get('f', 3800), 0.35, sd)
        elif name == 'switch':
            snd = X.switch(sd)
        elif name == 'zap':
            snd = X.zap_on()
        elif name == 'whoosh':
            snd = X.whoosh(0.4, 500, 2200, sd)
        elif name == 'crumble':
            snd = X.crumble(sd)
        elif name == 'boing':
            snd = X.boing(kw.get('f0', 180), kw.get('f1', 420))
        elif name == 'marker':
            snd = X.marker(kw.get('dur', 0.4), sd)
        elif name == 'roll':
            snd = X.roll(max(0.2, kw.get('dur', 0.5)), sd)
        elif name == 'click':
            snd = X.click(sd)
        elif name == 'beep':
            tt = np.arange(int(SR * 0.12)) / SR
            snd = np.sin(2 * np.pi * 1800 * tt) * np.minimum(1, (0.12 - tt) * 60) * 0.4
        elif name == 'squeak':
            snd = X.boing(700, 1300, 0.22)
        elif name == 'buzz':
            tt = np.arange(int(SR * 0.4)) / SR
            snd = np.sign(np.sin(2 * np.pi * 110 * tt)) * 0.25 * np.minimum(1, (0.4 - tt) * 20)
            snd = X.lp_fast(snd, 2000)
        elif name == 'bell':
            snd = X.bell()
        elif name == 'thump2':
            a = X.thud(sd, 60) * 0.6
            snd = np.zeros(int(SR * 0.6)); snd[:len(a)] += a
            i2 = int(0.22 * SR); snd[i2:i2 + len(a)] += a[:len(snd) - i2] * 0.8
        elif name == 'tvoff':
            snd = X.tv_off()
        else:
            print('sonido desconocido', name); continue
        mix.add(t, snd, gain * 0.55, pan)
    st = mix.stereo()
    # música original de fondo, bajita y con "ducking" cuando habla
    import music as M
    mu = M.build(V.T_END + 0.5, V.T_SNAP, V.T_LIGHT + 0.2, V.T_END_SNAP)
    m = min(len(mu), st.shape[0])
    rms = np.sqrt(np.mean(mu[:m] ** 2)) + 1e-9
    mu = mu / rms * 0.032
    duck_env = np.repeat(sm, hop)[:m] if len(sm) else np.zeros(m)
    if len(duck_env) < m:
        duck_env = np.pad(duck_env, (0, m - len(duck_env)))
    duck = 1 - 0.45 * np.clip(duck_env * 1.5, 0, 1)
    duck = X.lp_fast(duck, 4)
    st[:m] += mu[:m] * duck[:, None]
    st[:, 0] += vtrack; st[:, 1] += vtrack
    pk = np.max(np.abs(st)) + 1e-9
    if pk > 0.97:
        st = st / pk * 0.97
    n = int((V.T_END + 0.2) * SR)
    st = st[:n]
    import wave
    w = wave.open(os.path.join(OUT, 'audio.wav'), 'wb')
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
    w.close()
    return sm


def worker(idx, f0, f1, scale):
    sys.path.insert(0, HERE)
    import cap3 as V
    env = np.load(os.path.join(OUT, 'mouth_env.npy')) if os.path.exists(os.path.join(OUT, 'mouth_env.npy')) else None
    if env is not None and V.TL.cuts:
        V.set_voice_env(env)
    w, h = int(1080 * scale), int(1920 * scale)
    w -= w % 2; h -= h % 2
    out = os.path.join(OUT, f'part{idx}.mp4')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', '30', '-i', '-',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18' if scale >= 1 else '26', '-pix_fmt', 'yuv420p', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        im = V.render_frame(f / 30.0)
        if scale != 1:
            im = im.resize((w, h))
        p.stdin.write(im.tobytes())
        if (f - f0) % 300 == 0:
            print(f'[{idx}] {f - f0}/{f1 - f0}', flush=True)
    p.stdin.close(); p.wait()


def main():
    scale = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    nproc = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    sys.path.insert(0, HERE)
    import cap3 as V
    from timeline import TL
    build_audio(V, TL)
    nf = int(V.T_END * 30)
    print('frames', nf, 'duración', round(V.T_END, 2))
    bounds = [int(nf * k / nproc) for k in range(nproc + 1)]
    ps = [Process(target=worker, args=(i, bounds[i], bounds[i + 1], scale)) for i in range(nproc)]
    for p in ps:
        p.start()
    for p in ps:
        p.join()
    lst = os.path.join(OUT, 'parts.txt')
    with open(lst, 'w') as f:
        for i in range(nproc):
            f.write(f"file 'part{i}.mp4'\n")
    final = os.path.join(OUT, 'cap03_sensor_inclinacion.mp4' if scale >= 1 else 'preview.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', os.path.join(OUT, 'audio.wav'),
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final], check=True)
    print('listo', final)


if __name__ == '__main__':
    main()
