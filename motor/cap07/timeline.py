# Guion, tiempos de frases y utilidades de tiempo del capítulo 7 (la resistencia).
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# (texto para ElevenLabs, subtítulo (con "/" para partir), pausa después en el video)
PHRASES = [
    # 0 · gancho (segundo 0): LED directo a la fuente, se quema; título en pantalla (H2, H3)
    ("[surprised] ¡Se quemó el LED! [excited] ¿Cómo funciona una RESISTENCIA?",
     "¡Se quemó el LED! / ¿Cómo funciona una RESISTENCIA?", 0.6),
    # 1 · promesa (se cumple en la frase 8-9: código de colores; y la 11: salvó al LED)
    ("[mischievously] Te enseño a salvarlo... y a leer su código de colores.",
     "Te enseño a salvarlo... / y a leer su CÓDIGO DE COLORES", 0.6),
    # 2 · qué es (H1, H2)
    ("Una resistencia limita la corriente. [happy] ¡Y el LED prende bien!",
     "Una resistencia LIMITA la corriente. / ¡Y el LED prende bien!", 0.45),
    # 3 · ejemplo, voltajes (H3, H4)
    ("Fuente de cinco voltios; el LED se queda en unos dos. [excited] ¡A la resistencia le tocan tres!",
     "Fuente de 5 voltios; el LED se queda en unos 2. / ¡A la resistencia le tocan 3!", 0.45),
    # 4 · ley de Ohm + corriente (H5, H6, H7)
    ("Ley de Ohm: la corriente es voltaje entre resistencia. Tres entre trescientos treinta: unos nueve miliamperios.",
     "LEY DE OHM: corriente = voltaje ÷ resistencia. / 3 ÷ 330 = unos 9 miliamperios", 0.5),
    # 5 · mini gancho 1 · mito (H8)
    ("[surprised] Ojo: no se come la corriente. ¡La que entra es la misma que sale!",
     "Ojo: NO se come la corriente. / ¡La que entra es la MISMA que sale!", 0.5),
    # 6 · por dentro (MODELO SIMPLIFICADO) + Joule (H9, H10)
    ("Los electrones chocan con átomos que vibran y les pasan energía: ¡calor! Es el efecto Joule.",
     "Los electrones chocan con átomos que vibran / y les pasan energía: ¡calor! / Es el EFECTO JOULE", 0.5),
    # 7 · mini gancho 2 · calor a propósito (H11)
    ("[mischievously] ¿Y si quieres ese calor? ¡En una tostadora, el alambre se pone al rojo a propósito!",
     "¿Y si quieres ese calor? / ¡En una TOSTADORA, el alambre / se pone al rojo a propósito!", 0.55),
    # 8 · código de colores (H12)
    ("[excited] El código de colores: dos dígitos, un multiplicador y la tolerancia.",
     "El código de colores: / 2 dígitos, un multiplicador / y la tolerancia", 0.4),
    # 9 · ejemplo del código (H5, H12, H13, H14)
    ("Naranja, naranja, marrón, dorado: tres, tres, por diez... ¡trescientos treinta ohmios, más o menos cinco por ciento!",
     "Naranja, naranja, marrón, dorado: / 3, 3, por 10... / ¡330 OHMIOS, más o menos 5 %!", 0.55),
    # 10 · celular (H15, H16)
    ("[happy] Tu celular tiene cientos de componentes pasivos, y entre ellos hay resistencias.",
     "Tu celular tiene cientos de componentes pasivos, / y entre ellos hay RESISTENCIAS", 0.7),
    # 11 · remate (H7, H8)
    ("[warmly] Así que una resistencia limita cuánta corriente pasa... ¡y por eso salvó a mi LED!",
     "Una resistencia LIMITA cuánta corriente pasa... / ¡y por eso salvó a mi LED!", 0.7),
    # 12 · CTA + reto del comentario (H17) + cierre
    ("[excited] ¡Dale me gusta, suscríbete y sígueme! [mischievously] Reto: marrón, negro, rojo, dorado. ¿Cuánto vale? ¡Respóndeme!",
     "¡Dale me gusta, suscríbete y sígueme! / Reto: marrón, negro, rojo, dorado. / ¿Cuánto vale? ¡Respóndeme!", 3.2),
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
