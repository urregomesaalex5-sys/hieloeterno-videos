# Guion, tiempos de frases y utilidades de tiempo del capítulo 8 (el inductor).
# Cada frase sale de VERIFICACION.md (códigos I#). Tema pedido por @vpalep en Instagram.
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# (texto para ElevenLabs, subtítulo (con "/" para partir), pausa después en el video)
PHRASES = [
    # 0 · gancho: abre el interruptor, chispa y el neón se prende (I6, I7)
    ("[surprised] ¡Una pila de uno coma cinco voltios prendió un neón que pide decenas de voltios! [excited] ¿Cómo funciona un INDUCTOR?",
     "¡Una pila de 1,5 voltios prendió un neón / que pide DECENAS de voltios! / ¿Cómo funciona un INDUCTOR?", 0.55),
    # 1 · promesa (se cumple en la frase 9)
    ("[mischievously] Al final, te muestro cómo carga un celular... sin cable.",
     "Al final, te muestro cómo carga un celular... / ¡SIN CABLE!", 0.5),
    # 2 · qué es + campo (I1, I2)
    ("Un inductor es un alambre enrollado: una bobina. [happy] Cuando pasa corriente, crea un campo magnético... ¡mira la brújula!",
     "Un inductor es un alambre enrollado: una BOBINA. / Cuando pasa corriente, crea un CAMPO MAGNÉTICO... / ¡mira la brújula!", 0.45),
    # 3 · energía (I3)
    ("Y en ese campo guarda energía.",
     "Y en ese campo GUARDA ENERGÍA", 0.45),
    # 4 · mini gancho 1 (I4)
    ("[mischievously] Pero lo raro es esto: se opone a que la corriente CAMBIE.",
     "Pero lo raro es esto: / se opone a que la corriente CAMBIE", 0.45),
    # 5 · subida con retraso (I4, I5)
    ("Si la corriente sube, el campo que cambia induce un voltaje en contra: por eso este bombillo prende con retraso.",
     "Si la corriente sube, el campo que cambia / induce un voltaje EN CONTRA: / por eso este bombillo prende con retraso", 0.45),
    # 6 · corte de golpe = el neón del gancho (I4, I6)
    ("[excited] Y si la cortas de golpe, el campo se cae y aparece un voltaje mucho mayor que el de la pila. ¡Eso prendió el neón!",
     "Y si la cortas de golpe, el campo se cae / y aparece un voltaje MUCHO MAYOR que el de la pila. / ¡Eso prendió el neón!", 0.5),
    # 7 · analogía (I8)
    ("En una analogía común, es como la inercia: cuesta arrancarla... y cuesta frenarla.",
     "En una analogía común, es como la INERCIA: / cuesta arrancarla... / y cuesta frenarla", 0.5),
    # 8 · celular (I12)
    ("[happy] Existen inductores de solo uno coma seis milímetros, pensados para celulares.",
     "Existen inductores de solo 1,6 milímetros, / pensados para CELULARES", 0.5),
    # 9 · promesa cumplida: carga inalámbrica (I13)
    ("[excited] Y sin cable: la bobina de la base crea un campo que cambia... ¡e induce un voltaje en la bobina del celular!",
     "Y sin cable: la bobina de la base / crea un campo que cambia... / ¡e induce un voltaje en la bobina del celular!", 0.6),
    # 10 · remate (I3, I4)
    ("[warmly] Así que un inductor guarda energía en su campo magnético... y se opone a los cambios de corriente.",
     "Un inductor guarda energía en su campo magnético... / y se opone a los CAMBIOS de corriente", 0.6),
    # 11 · crédito
    ("[happy] Este capítulo lo pidió ve palep en Instagram. ¡Gracias!",
     "Este capítulo lo pidió @vpalep en Instagram. / ¡Gracias!", 0.5),
    # 12 · CTA + reto (I10)
    ("[excited] ¡Dale me gusta, suscríbete y sígueme! [mischievously] Reto: doble de vueltas, mismo tamaño. ¿La inductancia se duplica... o se cuadruplica? ¡Respóndeme!",
     "¡Dale me gusta, suscríbete y sígueme! / Reto: doble de vueltas, mismo tamaño. / ¿La inductancia se duplica... o se cuadruplica? / ¡Respóndeme!", 3.2),
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
