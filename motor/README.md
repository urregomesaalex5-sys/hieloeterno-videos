# Motor de la serie animada (HieloEterno)

Código para hacer los capítulos sin empezar de cero. Todo es Python (numpy, Pillow, scipy) + ffmpeg.

## Estructura
- `skin/skin.png` – skin de HieloEterno (mc-heads.net/skin/HieloEterno).
- `cap03/` – capítulo 3 completo, sirve de plantilla:
  - `char3d.py` – personaje 3D con la skin: codos, rodillas, estirar/aplastar, brazos de goma, cara de TV (expresiones: normal, feliz, sorpresa, curioso, pensando, guino, mareado, corazon, apagado) y boca de osciloscopio.
  - `scene.py` – cuarto de bloques, lámpara y luz, textos decorados, subtítulos, easing.
  - `sfx.py` – efectos ASMR sintetizados (pasos, bloques, clics, campanita, whoosh...).
  - `music.py` – música original suave de fondo (cambiar acordes/motivo en cada capítulo).
  - `diagrams.py` – diagramas del cap. 3 (reemplazar por los del nuevo tema).
  - `timeline.py` – guion: frases para ElevenLabs, subtítulos y pausas.
  - `cap3.py` – escenas, gestos, caminatas, saltos, eventos de sonido.
  - `segment.py` – corta la toma de voz por silencios → `voice_cuts.json`.
  - `render.py` – mezcla audio (voz + efectos + música con ducking) y renderiza 1080x1920 30 fps.
  - `thumb.py` – miniatura vertical. `sheet.py` – hoja de cuadros de prueba.

## Receta rápida
1. Copiar `cap03/` a `capNN/` y cambiar `timeline.py` (guion), `diagrams.py` y las escenas.
2. `python3 sheet.py prueba.png 5 20 40` para revisar cuadros.
3. Generar la voz (carlos, eleven_v4) con `tts_text()`; guardar la toma como `voice.wav` (48 kHz): `ffmpeg -i toma.mp3 -ac 1 -ar 48000 voice.wav`.
4. `python3 segment.py voice.wav` y revisar que haya un silencio largo por frase.
5. `python3 render.py 0.5 2` (borrador) y `python3 render.py 1.0 2` (final) → `out/`.
6. `python3 thumb.py` para la portada.
