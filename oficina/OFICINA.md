# La oficina de HieloEterno

Basada en el video de @martivegara ("Le pedí un canal de YouTube y me montó una oficina entera dentro del portátil").
Cada capítulo lo hace un **equipo de 7 puestos**. Cada puesto tiene una sola tarea, deja su resultado en un archivo,
y el siguiente puesto parte de ahí. Edwin es el jefe: **solo aprueba en 2 botones** (guion y publicación).

> Regla fija: todo capítulo nuevo se hace así, en este orden. Antes de empezar se lee `motor/RECETA.md`
> y `oficina/notas_para_guionista.md`.

```
 🔎 Explorador ──► ✍️ Guionista ──[BOTÓN 1: Edwin aprueba]──► 🎙️ Voz ──► 🎬 Animador ──► 🖼️ Miniaturista ──► 📤 Publicador ──[BOTÓN 2]──► publicado
       ▲                ▲                                                                                                      │
       │                └──────────────── 📊 Analista ("la gente se fue en el segundo 3") ◄────────── datos 24–48 h ◄────────┘
       └───────────────────────────────── 📊 Analista ("este video hizo 10x la media") 
```

---

## 🔎 1. Explorador de tendencias — "busca qué está petando en tu nicho"
- **Revisa:** las vistas de cada video propio en Metricool (TikTok `TKPO07`, Instagram `IGRE23`, YouTube `YTVP06`), los comentarios con pedidos y lo que sale en el nicho (electrónica en Shorts/Reels/TikTok).
- **Alarma 10x:** si un video hace **10 veces la media** de los demás (propio o de la competencia), lo marca como 🚨 y dice qué tiene de distinto (tema, título, gancho, hora).
- **Entrega:** `oficina/backlog.md` con los próximos temas ordenados (siempre debe haber al menos 3 listos, para no fallar ni un día).
- **Prioridad de temas:** 1) lo que pidió alguien en los comentarios (con crédito), 2) el formato que dio la alarma 10x, 3) un componente básico que falte en la serie.

## ✍️ 2. Guionista — "escribe guiones con el gancho en el primer segundo"
- **Lee primero:** `oficina/notas_para_guionista.md` (lo que dijo el analista) y la RECETA.
- **Gancho en el segundo 0–1:** la primera frase arranca con el personaje ya en movimiento y una pregunta o una acción rara. Nada de pantalla vacía ni frases de relleno al empezar.
- **Cada 3–5 s pasa algo nuevo** (pieza que llega, cambio de cara, golpe, sonido), porque en Shorts la gente decide en el segundo 3.
- Duración de 85–100 s y frases cortas. El personaje nunca dice su nombre. La exactitud técnica se verifica.
- **Entrega:** `capNN/timeline.py` (frases para ElevenLabs + subtítulos) y `capNN/GUION.md` (guion + plan de escenas).
- 🔴 **BOTÓN 1:** se le muestra el guion a Edwin y se espera su OK antes de gastar créditos de voz.

## 🎙️ 3. Voz — "pone la voz"
- ElevenLabs, voz **carlos** (`zSPJ694fdnzmEKl5n9wI`), modelo **eleven_v4**, todo el guion en un texto con `[long pause]`.
- Primero `estimate_only` y luego **una sola toma**. Edwin descarga el mp3 (desde el entorno de Claude está bloqueado) y lo adjunta.
- `segment.py` corta las frases. Se revisa que haya una frase por silencio largo y que la velocidad sea pareja.

## 🎬 4. Animador — "anima cada escena, sin repetir ni una"
- Copia el motor del capítulo anterior (`motor/capNN-1/` → `motor/capNN/`) y cambia solo el guion, los diagramas y las escenas.
- **Antes de animar lee `oficina/escenas_usadas.md`** y no repite intro, chiste visual ni demo. Al terminar, agrega las suyas a la lista.
- Hoja de cuadros (`sheet.py`), luego borrador al 50 % para Edwin y luego el render final.

## 🖼️ 5. Miniaturista — "hace varias versiones y se queda la que más saca"
- Hace **4–6 versiones** de la portada (cambia el título, la cara, el color y el encuadre) y las pone en una sola hoja de comparación.
- Las califica: se lee en chiquito (al 20 %), hay contraste, la cara se ve sorprendida y aparece el componente.
- Se usan **las 2 mejores**: la A en Instagram y la B en TikTok (YouTube no deja poner portada en Shorts mientras el canal no esté verificado). El analista anota cuál sacó más y esa línea gana en el siguiente capítulo.

## 📤 6. Publicador — "lo sube con título, descripción, a la hora que tu audiencia está conectada"
- Sube el .mp4 y las portadas a `capNN-tema/` en GitHub y usa el enlace raw como media en Metricool (marca 7725500, America/Bogota).
- Programa **un post por red a su mejor hora** (`getBestTimeToPostByNetwork`), 5 minutos antes del pico.
- Títulos con el formato ganador: **"¿Cómo funciona un [COMPONENTE]? ⚡ | Cap. N"**. El comentario que pide ideas cambia en cada video.
- 🔴 **BOTÓN 2:** se le muestra el resumen a Edwin y se espera su OK antes de programar.

## 📊 7. Analista — "mira los datos; si la gente se va en el segundo 3, avisa al guionista"
- A las 24–48 h de cada publicación saca por video: vistas, tiempo promedio visto, % que lo vio completo (TikTok `TKPO13`, `TKPO15`), la tasa de vistas de más de 3 s en Reels (`IGRE28`), la retención (`IGRE27`), los likes y los comentarios.
- Si el tiempo promedio es menor que el 30 % del video o el *view rate* (más de 3 s) es menor que el 60 %, **el gancho falló**. Lo anota para el guionista con el segundo exacto y qué pasaba en pantalla en ese momento.
- La curva de retención segundo a segundo solo está en **YouTube Studio / TikTok Studio**. Si hace falta, Edwin la mira o se abre con el navegador.
- **Entrega:** un informe en `oficina/informes/AAAA-MM-DD-analista.md` y 3 a 5 reglas cortas en `oficina/notas_para_guionista.md`. Avisa al explorador si hubo alarma 10x.

---

## 👔 El jefe (Edwin) — "lo más importante: pulsar el botón"
1. **Botón 1:** "OK al guion" (antes de gastar la voz).
2. **Botón 2:** "OK a publicar" (antes de programar).
Todo lo demás lo hace la oficina. La meta es **1 capítulo al día sin fallar**.

## Cómo se ejecuta
- **En el chat:** Claude hace los puestos en orden, en la misma conversación (así gasta menos cupo). El explorador y el analista pueden ir como agentes Sonnet en paralelo porque solo leen datos.
- **En Claude Code** (abriendo este repo): los puestos están en `.claude/agents/` y se llaman por nombre (`explorador`, `guionista`, `analista`…).
- **Turno de noche (opcional):** una tarea programada diaria hace al explorador y al analista y deja el informe en Notion, para que el guionista amanezca con las notas listas.
- Se anota todo en Notion: una página por capítulo y el informe del analista.
