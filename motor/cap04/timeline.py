# Guion, tiempos de frases y utilidades de tiempo del capítulo 4 (el diodo).
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# (texto para ElevenLabs, subtítulo (con "/" para partir), pausa después en el video)
PHRASES = [
    # 0 · gancho (segundo 0): ya corre y atraviesa la puerta-diodo
    ("[excited] ¡Esta puerta solo abre para un lado!", "¡Esta puerta solo abre para un lado!", 0.35),
    # 1 · intenta volver: ¡BONK! · luces · título
    ("[laughs] En electrónica hay una igual. ¡Capítulo cuatro: el diodo!", "En electrónica hay una igual. / ¡Capítulo 4: el DIODO!", 0.9),
    # 2 · qué es
    ("Un diodo deja pasar la corriente en un solo sentido... y la bloquea en el otro.",
     "Un diodo deja pasar la corriente en un solo sentido... / y la bloquea en el otro", 0.45),
    # 3 · patitas
    ("Tiene dos patitas: el ánodo... y el cátodo, el de la rayita.", "Tiene dos patitas: el ÁNODO... / y el CÁTODO, el de la rayita", 0.5),
    # 4 · pregunta
    ("[excited] ¿Y cómo lo hace?", "¿Y cómo lo hace?", 0.35),
    # 5 · por dentro: P y N
    ("Por dentro es un cristal de silicio con dos zonas: la P tiene huecos donde faltan electrones... y la N tiene electrones de sobra.",
     "Por dentro es un cristal de silicio con dos zonas: / la P tiene huecos donde faltan electrones... / y la N tiene electrones de sobra", 0.35),
    # 6 · barrera
    ("Donde se juntan, se forma una barrera.", "Donde se juntan, se forma una BARRERA", 0.45),
    # 7 · directa
    ("[excited] Si pones el positivo en el lado P, y le das unos cero coma siete voltios... ¡las cargas cruzan la barrera y la corriente pasa!",
     "Si pones el positivo en el lado P / y le das unos 0,7 voltios... / ¡las cargas cruzan la barrera y la corriente pasa!", 0.5),
    # 8 · inversa
    ("Si lo volteas, la barrera crece... y la corriente no pasa.", "Si lo volteas, la barrera crece... / y la corriente no pasa", 0.6),
    # 9 · demo
    ("[excited] Pruébalo: una pila, un diodo y un bombillo... ¡prende!", "Pruébalo: una pila, un diodo y un bombillo... / ¡prende!", 0.4),
    # 10
    ("Volteas la pila... [surprised] ¡y se apaga!", "Volteas la pila... / ¡y se apaga!", 0.55),
    # 11 · vida diaria
    ("Con cuatro diodos, el cargador de tu celular convierte la corriente alterna del enchufe... en directa.",
     "Con 4 diodos, el cargador de tu celular / convierte la corriente alterna del enchufe... / en directa", 0.6),
    # 12 · transición a tipos
    ("[happy] Ese es el rectificador. Pero tiene hermanos con superpoderes.",
     "Ese es el RECTIFICADOR. / Pero tiene hermanos con superpoderes", 0.5),
    # 13 · LED
    ("El LED: cuando los electrones cruzan la barrera, sueltan energía... [excited] ¡como luz! Su color depende del material.",
     "El LED: cuando los electrones cruzan la barrera, / sueltan energía... ¡como luz! / Su color depende del material", 0.5),
    # 14 · Zener
    ("El Zener se conecta al revés: bloquea hasta un voltaje exacto... y ahí lo mantiene fijo.",
     "El ZENER se conecta al revés: / bloquea hasta un voltaje exacto... / y ahí lo mantiene fijo", 0.5),
    # 15 · Schottky
    ("El Schottky pega metal al silicio: enciende con menos voltaje... y es rapidísimo.",
     "El SCHOTTKY pega metal al silicio: / enciende con menos voltaje... / y es rapidísimo", 0.5),
    # 16 · fotodiodo
    ("Y el fotodiodo también se conecta al revés: a oscuras no deja pasar nada... pero si le llega luz, ¡deja pasar corriente! [surprised] Así tu tele escucha al control.",
     "Y el FOTODIODO también se conecta al revés: / a oscuras no deja pasar nada... / pero si le llega luz, ¡deja pasar corriente! / Así tu tele escucha al control", 0.7),
    # 17 · remate
    ("[laughs] Mismo truco... distinto superpoder.", "Mismo truco... / distinto superpoder", 0.9),
    # 18 · CTA
    ("[excited] ¡Dale me gusta, suscríbete y sígueme!", "¡Dale me gusta, suscríbete y sígueme!", 0.4),
    # 19 · pregunta próximo cap (distinta a caps 1-3)
    ("[happy] ¿Qué componente cruzamos en el capítulo cinco? ¡Nos vemos!",
     "¿Qué componente cruzamos en el capítulo cinco? / ¡Nos vemos!", 3.2),
]

START = 0.25


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
