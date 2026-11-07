# Guion, tiempos de frases y utilidades de tiempo del capítulo 10 (el transformador).
# Cada frase sale de VERIFICACION.md (códigos T#). Tema del backlog (sigue al inductor y al relé).
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# (texto para ElevenLabs, subtítulo (con "/" para partir), pausa después en el video)
PHRASES = [
    # 0 · gancho: enchufa la bobina 1 y el bombillo de la bobina 2 prende sin tocarse (T1)
    ("[excited] ¡Estas dos bobinas no se tocan... y el bombillo prendió! ¿Cómo funciona un TRANSFORMADOR?",
     "¡Estas dos bobinas NO se tocan... / y el bombillo prendió! / ¿Cómo funciona un TRANSFORMADOR?", 0.5),
    # 1 · promesa (se cumple en las frases 10 y 11) (T7, T8)
    ("[mischievously] Al final, te muestro el que zumba en el poste de tu calle.",
     "Al final, te muestro el que ZUMBA / en el poste de tu calle", 0.45),
    # 2 · qué es (T1)
    ("Por dentro: dos bobinas en el mismo núcleo de hierro.",
     "Por dentro: dos BOBINAS / en el mismo NÚCLEO de hierro", 0.4),
    # 3 · corriente alterna (T4)
    ("[happy] La corriente de tu casa va y vuelve sesenta veces por segundo.",
     "La corriente de tu casa / va y vuelve 60 VECES por segundo", 0.4),
    # 4 · campo que cambia, el hierro lo lleva (T2)
    ("Eso hace un campo magnético que cambia sin parar... y el hierro lo lleva a la otra bobina.",
     "Eso hace un CAMPO magnético que cambia sin parar... / y el HIERRO lo lleva a la otra bobina", 0.4),
    # 5 · Faraday, enlace al cap. 8 (T2)
    ("[surprised] ¡Y un campo que cambia crea voltaje, como en el capítulo del inductor!",
     "¡Y un campo que CAMBIA crea VOLTAJE, / como en el capítulo del inductor!", 0.45),
    # 6 · mini gancho (T5)
    ("[mischievously] Ahora el truco: el voltaje depende de las vueltas.",
     "Ahora el truco: / el voltaje depende de las VUELTAS", 0.4),
    # 7 · relación de vueltas (T5)
    ("El doble de vueltas, el doble de voltaje. La mitad, la mitad.",
     "El DOBLE de vueltas, el doble de voltaje. / La MITAD, la mitad", 0.4),
    # 8 · potencia (T6)
    ("Pero no es magia: si sube el voltaje, baja la corriente.",
     "Pero no es magia: / si SUBE el voltaje, BAJA la corriente", 0.45),
    # 9 · con pila no funciona (T3)
    ("[surprised] Ojo: con una pila no funciona: solo da un pulsito al conectarla.",
     "Ojo: con una PILA no funciona: / solo da un PULSITO al conectarla", 0.5),
    # 10 · promesa cumplida: el poste (T7)
    ("[excited] ¿Y el del poste? Baja miles de voltios a los ciento veinte de tu enchufe.",
     "¿Y el del POSTE? / Baja MILES de voltios / a los 120 de tu enchufe", 0.4),
    # 11 · el zumbido (T8)
    ("[happy] Su zumbido sale sobre todo del hierro, que se estira y se encoge ciento veinte veces por segundo.",
     "Su ZUMBIDO sale sobre todo del HIERRO, / que se estira y se encoge / 120 veces por segundo", 0.55),
    # 12 · remate (T1, T2)
    ("[warmly] Así que un transformador es: dos bobinas, hierro y un campo que cambia.",
     "Así que un transformador es: / dos bobinas, hierro / y un campo que CAMBIA", 0.55),
    # 13 · CTA + reto (T5)
    ("[excited] ¡Dale me gusta, suscríbete y sígueme! [mischievously] Reto: entran ciento veinte voltios y la otra bobina tiene la mitad de vueltas. ¿Cuánto sale? ¡Respóndeme!",
     "¡Dale me gusta, suscríbete y sígueme! / Reto: entran 120 VOLTIOS / y la otra bobina tiene la MITAD de vueltas. / ¿Cuánto sale? ¡Respóndeme!", 2.4),
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
