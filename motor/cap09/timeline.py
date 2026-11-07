# Guion, tiempos de frases y utilidades de tiempo del capítulo 9 (el relé).
# Cada frase sale de VERIFICACION.md (códigos I#). Tema del backlog (sigue al inductor del cap. 8).
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# (texto para ElevenLabs, subtítulo (con "/" para partir), pausa después en el video)
PHRASES = [
    # 0 · gancho: aprieta un botoncito y ¡CLIC! se prende un reflector gigante (R1, R5)
    ("[excited] ¡Un botoncito de cinco voltios prendió este reflector gigante! ¿Cómo funciona un RELÉ?",
     "¡Un botoncito de 5 voltios / prendió este reflector GIGANTE! / ¿Cómo funciona un RELÉ?", 0.55),
    # 1 · promesa (se cumple en la frase 10) (R20)
    ("[mischievously] Al final, te cuento qué bicho encontraron dentro de un relé.",
     "Al final, te cuento qué BICHO / encontraron dentro de un relé", 0.5),
    # 2 · qué es (R1)
    ("Un relé es un interruptor que se mueve con un imán: adentro hay una bobina.",
     "Un relé es un INTERRUPTOR que se mueve con un IMÁN: / adentro hay una BOBINA", 0.45),
    # 3 · cómo funciona (R1)
    ("[happy] Con corriente, se vuelve imán... y jala una pieza de hierro que cierra los contactos.",
     "Con corriente, se vuelve IMÁN... / y jala una pieza de hierro / que cierra los CONTACTOS", 0.45),
    # 4 · el clic (R2)
    ("[excited] ¡Ese clic que oyes es metal golpeando metal!",
     "¡Ese CLIC que oyes / es metal golpeando metal!", 0.4),
    # 5 · resorte (R8)
    ("Sin corriente, un resorte la devuelve.",
     "Sin corriente, / un RESORTE la devuelve", 0.4),
    # 6 · mini gancho: números (R3, R4)
    ("[mischievously] Pero lo genial: pide unos setenta y un miliamperios... y maneja hasta diez amperios.",
     "Pero lo genial: pide unos 71 miliamperios... / ¡y maneja hasta 10 AMPERIOS!", 0.45),
    # 7 · chiquito manda a grande, aislados (R5, R6)
    ("Un circuito chiquito manda sobre uno grande... y nunca se tocan.",
     "Un circuito chiquito manda sobre uno GRANDE... / y nunca se tocan", 0.45),
    # 8 · pico + diodo (R9)
    ("[surprised] Ojo: al apagarlo, la bobina lanza un pico de voltaje, como en el capítulo pasado. Por eso se le pone un diodo.",
     "Ojo: al apagarlo, la bobina lanza un PICO de voltaje, / como en el capítulo pasado. / Por eso se le pone un DIODO", 0.5),
    # 9 · carro (R13)
    ("[happy] En el carro, las luces y el pito usan relés: así la corriente fuerte no pasa por el botón.",
     "En el carro, las LUCES y el PITO usan relés: / así la corriente fuerte / no pasa por el botón", 0.5),
    # 10 · promesa cumplida (R19, R20)
    ("[excited] Y el bicho: en mil novecientos cuarenta y siete, encontraron una polilla atrapada en el relé setenta de la computadora Mark dos... ¡y la pegaron en el cuaderno como primer bug real!",
     "Y el bicho: en 1947 encontraron una POLILLA / atrapada en el relé 70 de la computadora MARK II... / ¡y la pegaron en el cuaderno / como primer \"bug\" real!", 0.45),
    # 11 · la palabra ya existía (R21)
    ("[laughs] La palabra bug ya existía: ¡fue un chiste!",
     "La palabra \"bug\" ya existía: / ¡fue un chiste!", 0.55),
    # 12 · remate (R1)
    ("[warmly] Así que un relé es un interruptor con imán.",
     "Un relé es un interruptor con IMÁN", 0.55),
    # 13 · CTA + reto (R7)
    ("[excited] ¡Dale me gusta, suscríbete y sígueme! [mischievously] Reto: con el relé apagado, ¿al común se conecta la N A o la N C? ¡Respóndeme!",
     "¡Dale me gusta, suscríbete y sígueme! / Reto: con el relé APAGADO, / ¿al COMÚN se conecta la NA o la NC? / ¡Respóndeme!", 3.2),
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
