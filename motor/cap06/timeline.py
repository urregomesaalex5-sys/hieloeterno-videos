# Guion, tiempos de frases y utilidades de tiempo del capítulo 6 (la memoria del celular).
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# (texto para ElevenLabs, subtítulo (con "/" para partir), pausa después en el video)
PHRASES = [
    # 0 · gancho (segundo 0): prende el celular gigante, saca una foto y la voltea
    ("[excited] Miles de fotos en tu celular... ¿pero dónde viven?",
     "Miles de fotos en tu celular... / ¿pero dónde VIVEN?", 0.35),
    # 1 · el comentario del seguidor (sus 2 comentarios en pantalla)
    ("[warmly] ¡Eso me preguntó Liguito oficial... [excited] dos veces!",
     "¡Eso me preguntó @Liguitoo_oficial... / dos veces!", 0.45),
    # 2 · entra por el puerto de carga · título
    ("[mischievously] ¡Vamos a meternos! [excited] Capítulo seis: ¡la memoria del celular!",
     "¡Vamos a meternos! / ¡Capítulo 6: la MEMORIA del celular!", 0.8),
    # 3 · dos memorias (ANALOGÍA C25)
    ("Tu celular tiene dos memorias: la RAM, que es el escritorio... y el almacenamiento, que es el archivero.",
     "Tu celular tiene DOS memorias: / la RAM, que es el escritorio... / y el ALMACENAMIENTO, que es el archivero", 0.45),
    # 4 · flash (A1)
    ("El archivero es memoria flash: miles de millones de celdas.",
     "El archivero es memoria FLASH: / miles de millones de celdas", 0.4),
    # 5 · celda (A2, A3)
    ("Cada una es un transistor especial, con una capa encerrada entre aislantes.",
     "Cada una es un transistor especial, / con una capa encerrada entre AISLANTES", 0.4),
    # 6 · túnel (A4, A7)
    ("Con unos veinte voltios, los electrones cruzan el aislante por efecto túnel.",
     "Con unos 20 voltios, los electrones / cruzan el aislante por EFECTO TÚNEL", 0.35),
    # 7 · cuántica (A4, A5, C24)
    ("[surprised] ¡No lo rompen! Es física cuántica: con una pared delgadísima, el electrón puede pasar al otro lado.",
     "¡No lo rompen! Es física cuántica: / con una pared delgadísima, / el electrón puede pasar al otro lado", 0.45),
    # 8 · no volátil (A15)
    ("Al quitar el voltaje, se quedan atrapados. Por eso tus fotos no se borran sin batería.",
     "Al quitar el voltaje, se quedan ATRAPADOS. / Por eso tus fotos no se borran sin batería", 0.45),
    # 9 · lectura (A6, A8)
    ("Para leer, el chip mide a qué voltaje conduce el transistor: sin electrones, un uno; con electrones, un cero.",
     "Para leer, el chip mide a qué voltaje / conduce el transistor: / sin electrones, un 1; con electrones, un 0", 0.45),
    # 10 · niveles (A9, A10, C27)
    ("[excited] ¡Y midiendo muy fino, una celda puede guardar ocho niveles: tres bits!",
     "¡Y midiendo muy fino, una celda puede / guardar 8 NIVELES: 3 bits!", 0.5),
    # 11 · costo (A6, A12, A16)
    ("El costo: se borra por bloques enteros, y cada ciclo de escribir y borrar gasta un poquito el aislante.",
     "El costo: se borra por BLOQUES enteros, / y cada ciclo de escribir y borrar / gasta un poquito el aislante", 0.5),
    # 12 · DRAM (B16, B17)
    ("Ahora, el escritorio: cada celda de RAM es un transistor y un condensador... [excited] ¡como el del capítulo cinco!",
     "Ahora, el escritorio: cada celda de RAM es / un transistor y un CONDENSADOR... / ¡como el del capítulo 5!", 0.45),
    # 13 · refresco (B19)
    ("El condensador se va descargando, así que el celular lo recarga cada sesenta y cuatro milisegundos o menos.",
     "El condensador se va descargando, / así que el celular lo recarga / cada 64 milisegundos o menos", 0.45),
    # 14 · volátil y rápida (B20, B22, B23)
    ("Sin energía, se pierde todo. Pero responde unas mil veces más rápido: por eso ahí viven tus apps abiertas.",
     "Sin energía, se pierde todo. / Pero responde unas MIL veces más rápido: / por eso ahí viven tus apps abiertas", 0.5),
    # 15 · remate (A15)
    ("[happy] Así que cada foto que tomas... son electrones atrapados, dentro de tu bolsillo.",
     "Así que cada foto que tomas... / son electrones atrapados, / dentro de tu bolsillo", 0.8),
    # 16 · gracias
    ("[warmly] Este capítulo fue idea de Liguito oficial. ¡Gracias!",
     "Este capítulo fue idea de @Liguitoo_oficial. / ¡Gracias!", 0.5),
    # 17 · CTA + pregunta + cierre
    ("[excited] ¡Dale me gusta, suscríbete y sígueme! [happy] ¿Qué componente abrimos en el capítulo siete? ¡Nos vemos!",
     "¡Dale me gusta, suscríbete y sígueme! / ¿Qué componente abrimos en el capítulo 7? / ¡Nos vemos!", 3.2),
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
