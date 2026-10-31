# Guion, tiempos de frases y utilidades de tiempo del capítulo 3.
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# (texto para ElevenLabs, subtítulo (con "/" para partir), pausa después en el video)
PHRASES = [
    ("[curious] ¿La gravedad... es un componente?", "¿La gravedad... es un componente?", 0.5),
    ("[laughs] Eso preguntó teo eme cero siete cuatro.", "Eso preguntó @teom074", 0.5),
    ("[mischievously] Pues primero... ¡encendamos la gravedad!", "Pues primero... ¡encendamos la gravedad!", 2.9),
    ("[curious] ¿Y qué es la gravedad?", "¿Y qué es la gravedad?", 0.45),
    ("Es la fuerza con la que todo lo que tiene masa atrae a lo demás.", "Es la fuerza con la que todo lo que tiene masa / atrae a lo demás", 0.5),
    ("La Tierra tiene tanta masa que nos jala a todos hacia su centro... [excited] ¡por eso las cosas caen!",
     "La Tierra tiene tanta masa / que nos jala a todos hacia su centro... / ¡por eso las cosas caen!", 0.9),
    ("[excited] Pero ojo: ¡la gravedad no es un componente! Aunque hay componentes que la sienten.",
     "Pero ojo: ¡la gravedad NO es un componente! / Aunque hay componentes que la sienten", 0.45),
    ("[happy] Hoy: el sensor de inclinación.", "Hoy: el sensor de inclinación", 1.0),
    ("Un tubito, una bolita metálica y dos patitas.", "Un tubito, una bolita metálica / y dos patitas", 0.5),
    ("Lo inclinas... y la gravedad hace rodar la bolita hasta las patitas.",
     "Lo inclinas... / y la gravedad hace rodar la bolita hasta las patitas", 0.1),
    ("¡Clic! Las une, y la corriente pasa.", "¡CLIC! Las une, / y la corriente pasa", 0.5),
    ("Lo enderezas... y la bolita se aleja. La corriente se corta.",
     "Lo enderezas... y la bolita se aleja. / La corriente se corta", 0.85),
    ("[excited] Ahora conéctalo a una pila y un LED.", "Ahora conéctalo a una pila y un LED", 0.5),
    ("¡Inclínalo... y el LED se prende!", "¡Inclínalo... y el LED se prende!", 0.45),
    ("¡Enderézalo... y se apaga!", "¡Enderézalo... y se apaga!", 0.45),
    ("[laughs] Un interruptor que obedece a la gravedad.", "Un interruptor que obedece a la gravedad", 0.85),
    ("Se usa en alarmas, juguetes, el tilt del pinbol, y calentadores que se apagan si se voltean.",
     "Se usa en alarmas, juguetes, / el TILT del pinball, / y calentadores que se apagan si se voltean", 1.0),
    ("[surprised] ¿Y tu celular? ¡Tiene un primo diminuto: el acelerómetro!",
     "¿Y tu celular? / ¡Tiene un primo diminuto: el acelerómetro!", 0.5),
    ("[whispers] Adentro hay una masa minúscula colgada de resortes.", "Adentro hay una masa minúscula / colgada de resortes", 0.5),
    ("La gravedad la jala, y el chip mide cuánto se mueve en tres direcciones.",
     "La gravedad la jala, / y el chip mide cuánto se mueve / en tres direcciones", 0.5),
    ("Así sabe dónde está el abajo... y gira tu pantalla.", "Así sabe dónde está el abajo... / y gira tu pantalla", 1.2),
    ("[warmly] Gracias, teo eme cero siete cuatro. ¡Buena pregunta!", "Gracias, @teom074. ¡Buena pregunta!", 0.45),
    ("[excited] ¡Dale me gusta, suscríbete y sígueme!", "¡Dale me gusta, suscríbete y sígueme!", 0.45),
    ("[happy] ¿Qué componente quieres en el capítulo cuatro? ¡Nos vemos!", "¿Qué componente quieres en el capítulo cuatro? / ¡Nos vemos!", 3.2),
]

START = 1.0


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
            t += d + gap
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
            return self.T[i]
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
                # repartir por caracteres (o por palabras reales si hay)
                tot = sum(len(p) for p in parts)
                acc = 0
                for j, p in enumerate(parts):
                    acc += len(p)
                    edge = a + (b - a) * self.char_to_frac(i, acc / tot)
                    if i in self.words:
                        first = parts[j + 1].split()[0].strip('¡¿,.!?').lower() if j + 1 < len(parts) else None
                        if first:
                            edge = self.kw(i, first) - 0.05
                    if t < edge or j == len(parts) - 1:
                        return p, i
        return None, None


TL = Timeline()
