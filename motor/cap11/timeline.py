# Guion, tiempos de frases y utilidades de tiempo del capítulo 11 (el motor DC).
# Cada frase sale de VERIFICACION.md (códigos M#). Tema del backlog (sigue la familia del electromagnetismo).
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# (texto para ElevenLabs, subtítulo (con "/" para partir), pausa después en el video)
PHRASES = [
    # 0 · gancho: conecta la pila y la hélice del motor arranca (M1)
    ("[excited] ¡Una pila, un imán y alambre... y esto gira solo! ¿Cómo funciona un MOTOR?",
     "¡Una pila, un imán y alambre... / y esto GIRA solo! / ¿Cómo funciona un MOTOR?", 0.5),
    # 1 · promesa (se cumple en la frase 9) (M7)
    ("[mischievously] Al final, te muestro el que hace vibrar tu control.",
     "Al final, te muestro el que hace VIBRAR / tu control", 0.45),
    # 2 · qué es por dentro (M1)
    ("Por dentro: una bobina de alambre entre dos imanes.",
     "Por dentro: una BOBINA de alambre / entre dos IMANES", 0.4),
    # 3 · fuerza sobre un alambre con corriente (M2)
    ("[happy] Si pasa corriente por un alambre dentro del campo de un imán... ¡el alambre recibe un empujón!",
     "Si pasa CORRIENTE por un alambre / dentro del campo de un imán... / ¡el alambre recibe un EMPUJÓN!", 0.4),
    # 4 · par en la espira (M3)
    ("En la bobina, un lado empuja hacia arriba y el otro hacia abajo... ¡y gira!",
     "En la bobina, un lado empuja hacia ARRIBA / y el otro hacia ABAJO... ¡y GIRA!", 0.4),
    # 5 · sin conmutador se queda quieta (M4)
    ("[surprised] Pero al quedar derecha, el empujón la devolvería... y se quedaría quieta.",
     "Pero al quedar DERECHA, el empujón la devolvería... / y se quedaría QUIETA", 0.45),
    # 6 · el conmutador (M4)
    ("[mischievously] El truco es el conmutador: cada media vuelta, le da la vuelta a la corriente.",
     "El truco es el CONMUTADOR: / cada media vuelta, le da la vuelta a la CORRIENTE", 0.4),
    # 7 · siempre al mismo lado (M4)
    ("Así el empujón siempre la hace girar hacia el mismo lado.",
     "Así el empujón siempre la hace girar / hacia el MISMO LADO", 0.4),
    # 8 · polaridad (M5)
    ("[excited] ¡Y si volteas la pila, gira al revés!",
     "¡Y si VOLTEAS la pila, / gira AL REVÉS!", 0.5),
    # 9 · promesa cumplida: el vibrador (M7)
    ("[happy] ¿Y el de tu control? En muchos, es un motorcito con una pesa a un lado: al girar, todo tiembla.",
     "¿Y el de tu CONTROL? En muchos, es un motorcito / con una PESA a un lado: / al girar, todo TIEMBLA", 0.45),
    # 10 · el motor como generador, enlace al cap. 2 (M8)
    ("[surprised] Y si giras el motor con la mano, ¡da voltaje! Así funcionaba el molino del capítulo dos.",
     "Y si giras el motor con la mano, ¡da VOLTAJE! / Así funcionaba el molino del capítulo 2", 0.55),
    # 11 · remate (M1–M4)
    ("[warmly] Así que un motor es: corriente, imanes y un conmutador que no lo deja parar.",
     "Así que un motor es: corriente, imanes / y un CONMUTADOR que no lo deja parar", 0.55),
    # 12 · CTA + reto (M6)
    ("[excited] ¡Dale me gusta, suscríbete y sígueme! [mischievously] Reto: ¿y si volteas la pila y también los imanes? ¿Para dónde gira? ¡Respóndeme!",
     "¡Dale me gusta, suscríbete y sígueme! / Reto: ¿y si volteas la PILA / y también los IMANES? / ¿Para dónde gira? ¡Respóndeme!", 2.4),
]

START = 0.8


def tts_text():
    return ' [long pause] '.join(p[0] for p in PHRASES)


def _est(sub):
    words = len(re.sub(r'[^\w@ ]', ' ', sub).split())
    pauses = sub.count('...')
    return words / 2.7 + 0.3 * pauses + 0.25


def load_cuts():
    p = os.path.join(HERE, 'voice_cuts.json')
    if os.path.exists(p):
        return json.load(open(p))
    return None


class Timeline:
    def __init__(self):
        cuts = load_cuts()
        self.cuts = cuts
        self.T = []; self.D = []
        t = START
        for i, (tts, sub, gap) in enumerate(PHRASES):
            if cuts:
                d = cuts[i]['b'] - cuts[i]['a']
            else:
                d = _est(sub)
            self.T.append(t); self.D.append(d)
            t += d + (gap * 0.7 if i < len(PHRASES) - 1 else gap)
        self.END = t
        self.words = {}
        if cuts:
            for i, c in enumerate(cuts):
                if 'words' in c:
                    self.words[i] = c['words']

    def s(self, i):
        return self.T[i]

    def e(self, i):
        return self.T[i] + self.D[i]

    def kw(self, i, word, occ=0, after=False):
        """tiempo (en el video) en que empieza 'word' dentro de la frase i"""
        if i in self.words:
            ws = self.words[i]
            n = 0
            for w in ws:
                if word.lower() in w['w'].lower():
                    if n == occ:
                        base = self.cuts[i]['a']
                        return self.T[i] + (w['e'] if after else w['s']) - base
                    n += 1
        sub = PHRASES[i][1].replace(' / ', ' ').lower()
        k = -1
        for _ in range(occ + 1):
            k = sub.find(word.lower(), k + 1)
        if k < 0:
            raise KeyError(f'palabra {word!r} no está en la frase {i}')
        if after:
            k += len(word)
        return self.T[i] + self.D[i] * self.char_to_frac(i, k / max(1, len(sub)))

    def char_to_frac(self, i, c):
        # mapeo por tramos usando las pausas internas reales de la voz
        pts = [(0.0, 0.0)]
        if self.cuts and self.cuts[i].get('anchors'):
            for cf, g0, g1 in self.cuts[i]['anchors']:
                pts.append((cf, g0)); pts.append((cf + 1e-4, g1))
        pts.append((1.0, 1.0))
        for (c0, t0), (c1, t1) in zip(pts, pts[1:]):
            if c <= c1:
                return t0 + (t1 - t0) * (c - c0) / max(1e-6, c1 - c0)
        return 1.0

    def subtitle_at(self, t):
        for i, (tts, sub, gap) in enumerate(PHRASES):
            a, b = self.T[i], self.T[i] + self.D[i]
            if a - 0.05 <= t <= b + 0.25:
                parts = [p.strip() for p in sub.split(' / ')]
                if len(parts) == 1:
                    return parts[0], i
                tot = sum(len(p) for p in parts)
                acc = 0
                for j, p in enumerate(parts):
                    acc += len(p)
                    edge = a + (b - a) * self.char_to_frac(i, acc / tot)
                    if i in self.words:
                        first = parts[j + 1].split()[0].strip('¡¿,.!?').lower() if j + 1 < len(parts) else None
                        if first:
                            try:
                                edge = self.kw(i, first) - 0.05
                            except KeyError:
                                pass
                    if t < edge or j == len(parts) - 1:
                        return p, i
        return None, None


TL = Timeline()

if __name__ == '__main__':
    txt = tts_text()
    open(os.path.join(HERE, 'tts.txt'), 'w').write(txt + '\n')
    words = sum(len(re.sub(r'\[[^\]]*\]', '', p[0]).split()) for p in PHRASES)
    chars = len(re.sub(r'\[[^\]]*\]', '', txt).replace('  ', ' '))
    print('frases', len(PHRASES), 'palabras', words, 'caracteres', len(txt), 'sin etiquetas', chars)
    print('duración estimada', round(TL.END, 1), 's')
    for i in range(len(PHRASES)):
        print(i, round(TL.s(i), 1), round(TL.e(i), 1))
