# Guion, tiempos de frases y utilidades de tiempo del capítulo 5 (el condensador).
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# (texto para ElevenLabs, subtítulo (con "/" para partir), pausa después en el video)
PHRASES = [
    # 0 · gancho (segundo 0): a oscuras, pitido de carga subiendo... ¡FLASH!
    ("[excited] ¿Escuchas ese pitido? ... ¡Flash!", "¿Escuchas ese pitido?... / ¡FLASH!", 0.35),
    # 1 · rayos X a la cámara · título
    ("[laughs] El secreto está aquí adentro. ¡Capítulo cinco: el condensador!",
     "El secreto está aquí adentro. / ¡Capítulo 5: el CONDENSADOR!", 0.9),
    # 2 · qué es
    ("También le dicen capacitor. Guarda energía eléctrica... y la suelta de golpe.",
     "También le dicen CAPACITOR. / Guarda energía eléctrica... / y la suelta de golpe", 0.45),
    # 3 · pila vs condensador
    ("Parece una pila, pero no: la pila es maratonista... [excited] ¡el condensador es velocista!",
     "Parece una pila, pero no: / la pila es maratonista... / ¡el condensador es velocista!", 0.5),
    # 4 · pregunta
    ("[excited] ¿Y qué tiene por dentro?", "¿Y qué tiene por dentro?", 0.35),
    # 5 · placas + aislante
    ("Dos placas de metal muy cerquita... separadas por un aislante.",
     "Dos placas de metal muy cerquita... / separadas por un AISLANTE", 0.45),
    # 6 · carga
    ("Conectas una pila: los electrones se amontonan en una placa... y se van de la otra.",
     "Conectas una pila: / los electrones se amontonan en una placa... / y se van de la otra", 0.4),
    # 7 · cargado
    ("No pueden cruzar el aislante... así que esperan. [happy] ¡Ya está cargado!",
     "No pueden cruzar el aislante... así que esperan. / ¡Ya está CARGADO!", 0.5),
    # 8 · demo LED
    ("[excited] Quitas la pila, le pones un LED... ¡prende! ... y se apaga poquito a poquito.",
     "Quitas la pila, le pones un LED... ¡prende! / ...y se apaga poquito a poquito", 0.55),
    # 9 · faradios
    ("Se mide en faradios... pero uno es muchísimo, por eso verás microfaradios.",
     "Se mide en FARADIOS... pero uno es muchísimo, / por eso verás microfaradios (µF)", 0.55),
    # 10 · cerámico
    ("El cerámico: chiquito como una lenteja... y se pone por cualquier lado.",
     "El CERÁMICO: chiquito como una lenteja... / y se pone por cualquier lado", 0.45),
    # 11 · electrolítico
    ("El electrolítico: una latica que guarda mucho más... pero tiene lado: la franja marca el negativo.",
     "El ELECTROLÍTICO: una latica que guarda mucho más... / pero tiene lado: / la franja marca el NEGATIVO", 0.4),
    # 12 · al revés: PUM
    ("Al revés, se infla y... [surprised] ¡pum! Por eso trae una cruz arriba: es su válvula de seguridad.",
     "Al revés, se infla y... ¡PUM! / Por eso trae una cruz arriba: / es su válvula de seguridad", 0.55),
    # 13 · supercondensador
    ("Y el supercondensador... [excited] ¡puede tener miles de faradios!",
     "Y el SUPERCONDENSADOR... / ¡puede tener miles de faradios!", 0.55),
    # 14 · el más común
    ("¿El más común del mundo? El cerámico mini: tu celular tiene cientos... [surprised] ¡algunos del tamaño de un grano de arena!",
     "¿El más común del mundo? El cerámico mini: / tu celular tiene cientos... / ¡algunos del tamaño de un grano de arena!", 0.6),
    # 15 · vuelta al flash
    ("¿Y el pitido del flash? Es su condensador cargándose a unos trescientos voltios... para soltarlos en una milésima de segundo.",
     "¿Y el pitido del flash? Es su condensador / cargándose a unos 300 voltios... / para soltarlos en una milésima de segundo", 0.5),
    # 16 · advertencia
    ("Ojo: aunque la cámara esté apagada, puede seguir cargado. ¡No la abras!",
     "Ojo: aunque la cámara esté apagada, / puede seguir cargado. ¡No la abras!", 0.5),
    # 17 · remate
    ("[laughs] Pequeñito... pero con mucha chispa.", "Pequeñito... / pero con mucha chispa", 0.9),
    # 18 · CTA
    ("[excited] ¡Dale me gusta, suscríbete y sígueme!", "¡Dale me gusta, suscríbete y sígueme!", 0.4),
    # 19 · pregunta próximo cap
    ("[happy] ¿Qué componente cargamos en el capítulo seis? ¡Nos vemos!",
     "¿Qué componente cargamos en el capítulo seis? / ¡Nos vemos!", 3.2),
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
