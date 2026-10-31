# Receta de la serie HieloEterno · Electrónica animada

Esta receta junta lo mejor de los capítulos 1 (transistor), 2 (molino eólico) y 3 (sensor de inclinación), además de todo lo que Edwin pidió en el camino. Hay que leerla antes de empezar cada capítulo nuevo.

---

## 1. Tema e idea
- El tema sale de los **comentarios de la gente** siempre que se pueda. En el cap. 3, @teom074 preguntó "¿La gravedad?". Hay que darle crédito en el video y en la descripción.
- Busca un **gancho** que responda la duda con humor. Ejemplo: "La gravedad NO es un componente… ¡pero hay componentes que la sienten!".
- Si el tema no es un componente (la gravedad, el viento), primero se **explica el concepto en 2 o 3 frases** y luego se conecta con un componente real.
- Cada video debe tener al menos una **demo práctica**: algo que se arma, se prende o se mueve (el LED del molino, el LED del sensor).
- Cierra con algo que la gente use todos los días, como "tu celular tiene uno". Eso ayuda a que lo compartan.
- La exactitud técnica se verifica siempre. Si hay que simplificar, que no quede algo falso.
- Para planear se puede usar un **agente de Sonnet**, que hace el guion, el escena por escena y la publicación. Opus hace el video.

## 2. Guion
- Debe durar **85–100 s**, con frases cortas.
- Estructura:
  1. Intro especial (5–12 s)
  2. Gancho y título
  3. Qué es
  4. Cómo funciona por dentro
  5. Demo
  6. Dónde se usa
  7. Remate
  8. Gracias / crédito
  9. Pedir like, suscripción y follow
  10. Pregunta para el próximo capítulo
  11. "¡Nos vemos!"
- El personaje **nunca se presenta por nombre**.
- **Se le muestra el guion a Edwin y se espera su OK** antes de gastar créditos de voz.

## 3. Intro especial (distinta en cada capítulo)
Las intros que ya se usaron, para no repetirlas:
- **Cap. 1:** a oscuras, se asoma curioso desde abajo con un primer plano de la cabeza: "¿Desean aprender electrónica?". Empuja la cámara y aparecen las letras "¡Están en el lugar correcto!". Aplaude para prender la lámpara y construye el piso y las paredes.
- **Cap. 2:** baja colgando de cabeza desde arriba, dice "¡Holaaa!", se resbala, cae mareado y luego dice "¡Bienvenidos al capítulo dos!".
- **Cap. 3:** todo flota a oscuras sin gravedad, con el comentario del suscriptor en burbujas. Chasquea los dedos y todo cae en su lugar: bloques, lámpara que parpadea y se prende, y el letrero "¡GRAVEDAD ACTIVADA!".

Reglas para la intro:
- Debe ser **corta** y tener relación con el tema del capítulo.
- El mundo **lo construye o lo activa él**. Nada de tablero, teatro ni nieve.

## 4. Personaje y animación
- Usa la skin real de HieloEterno (`motor/skin/skin.png`, de mc-heads.net). Tiene cabeza de TV, codos y rodillas.
- **Estilo caricaturesco, tipo Alan Becker:**
  - estirar y aplastar
  - brazos de goma
  - anticipación
  - rebote gelatinoso
  - estelas y líneas de velocidad
- **Cara de TV expresiva** que cambia según lo que dice: curioso, feliz, sorpresa, pensando, guiño, corazón, mareado y apagado. La boca de osciloscopio va sincronizada con la voz.
- **Al explicar, camina de un lado a otro** con zancada real, sin patinar. Los gestos de manos son naturales y mira hacia el diagrama y luego a la cámara.
- ⚠️ **No debe moverse ni rebotar todo el tiempo.** Edwin dijo que parecía que "tuviera ganas de orinar". La energía va en **momentos clave**:
  - saltar al aterrizar
  - brazos arriba
  - un giro con el título
  - celebrar el "¡CLIC!"
  - chocar el puño cuando algo se prende
  - brincar de sorpresa
- Interactúa con todo: **lanza las piezas** del diagrama (llegan con un "clac") y **lo rompe de un manotazo** al cambiar de tema. También inclina o empuja cosas con el brazo de goma, o con mímica.
- Al final, **la pantalla de su cara se apaga** cuando se apaga la luz.

## 5. Escenario y gráficos
- Cuarto de bloques de piedra con piso de madera y una lámpara colgante con cono de luz. La franja negra de arriba lleva el cable de la lámpara.
- La etiqueta "CAP. N · TEMA" va arriba, en naranja.
- Los diagramas van **arriba del personaje**, entre y = 250 y 860, sin taparle la cabeza ni salirse de los bordes.
- Usa rótulos cortos con fondo oscuro (BOLITA, CERRADO ✓, ABIERTO ✗…). La flecha roja de GRAVEDAD se usa cuando aplica.
- Los títulos van en letras decoradas con degradado, contorno y sombra, y entran con rebote.

## 6. Sonido y música
- **Voz al frente.**
- **Efectos estilo ASMR en estéreo:**
  - pasos de madera
  - bloques que encajan
  - whoosh al lanzar
  - marcador
  - clics
  - campanita en suscribir
  - apagado de TV
- 🎵 **Música de fondo original, suave y bajita, distinta en cada capítulo y acorde al tema** (se pidió desde el cap. 3):
  - En el cap. 3: intro flotante sin ritmo, un sonido de "caer" en el chasquido y luego un lo-fi a 92 BPM con acordes que bajan y una marimba que rebota como la bolita.
  - Baja (ducking) cuando habla el personaje y se apaga con el chasquido final.
  - Se cambian los acordes y el motivo según el tema, en `music.py`.

## 7. Voz (ElevenLabs)
- Voz **"carlos"** (voice_id zSPJ694fdnzmEKl5n9wI), modelo **eleven_v4**.
- Todo el guion va en **un solo texto**, con `[long pause]` entre frases y etiquetas de emoción: [curious], [excited], [laughs], [whispers], [surprised], [mischievously], [warmly], [happy].
- Los usuarios se escriben como se pronuncian: "teo eme cero siete cuatro". En los subtítulos se escriben normal (@teom074).
- Antes de generar, se usa `estimate_only` para saber cuántos créditos cuesta. **Una sola toma** (~1.700 créditos) para ahorrar.
- La descarga desde el entorno de Claude está bloqueada. Edwin descarga el mp3 y lo adjunta al chat. A Edwin se le pasan los enlaces de ElevenLabs completos, con `&mode=switchWorkspace&oobCode=…`.
- `segment.py` corta las frases por silencios largos (los de `[long pause]`) y ancla los tiempos en las pausas internas ("...", ".", "?", ":"). Hay que revisar que la cantidad de frases coincida y que la velocidad sea pareja (13–18 caracteres por segundo).

## 8. Formato y render
- Vertical **1080×1920 a 30 fps**.
- Subtítulos grandes y blancos con contorno, en la franja negra de abajo (y ≈ 1560), dentro de la zona segura de Reels.
- Pasos de trabajo:
  1. Hoja de cuadros de prueba (`sheet.py`) para revisar cada escena.
  2. Borrador en baja resolución (`render.py 0.5`), que se le manda a Edwin para que lo vea.
  3. Render final (`render.py 1.0`).
- Si el video no le abre a Edwin, se le manda también una **versión liviana** (crf 25, ~11 MB).

## 9. Miniatura vertical
- Fondo de bloques con rayos de luz y bloques flotando.
- Título decorado tipo gancho: "¿CÓMO FUNCIONA…?" o la pregunta del suscriptor.
- Diagrama brillante en el centro.
- Personaje sorprendido en primer plano abajo.
- Sello "CAP. N".

## 10. Publicación
1. Subir el video (.mp4) y la portada (.jpg) a `hieloeterno-videos/capNN-tema/`.
2. En Metricool (marca 7725500, America/Bogota), crear **un post por red**, **cada uno en su mejor hora** según `getBestTimeToPostByNetwork` (a Edwin le parece bien que salgan a horas distintas).
   - En el sábado del cap. 3 salió así: Instagram y TikTok a las 10 am, YouTube a las 4 pm. Se programa 5 minutos antes del pico.
3. Datos de cada red:
   - **YouTube Short:**
     - título con emoji y "| Cap. N"
     - categoría Educación, no es para niños, público
     - sin portada (el canal no está verificado)
     - **mencionar con @ al suscriptor** en la descripción y en el primer comentario, para que vea que se le respondió
   - **Instagram Reel:**
     - con portada, se muestra en el perfil, isAiGenerated = true
     - el usuario de YouTube se escribe sin arroba: "teom074 (de YouTube)"
   - **TikTok:**
     - con portada, público, isAigc = true
     - TikTok no deja programar el primer comentario, así que la pregunta va en la descripción
4. El **comentario que pide ideas cambia en cada video**, nunca el mismo. Ejemplos del cap. 3:
   - "@teom074 ¡tu pregunta se volvió capítulo! 🙌 Y tú, ¿qué componente te da curiosidad? La mejor idea de los comentarios puede ser el capítulo 4"
   - "Este capítulo salió de un comentario 💬 ¿El siguiente sale del tuyo?"
5. En la descripción va "🔊 Voz generada con ElevenLabs (elevenlabs.io)". El plan gratis no permite uso comercial: si se monetiza, hay que pagar el plan.
6. **Se le muestra el resumen a Edwin y se espera su OK antes de programar.**
7. Se anota todo en Notion: una página por capítulo con la idea, las decisiones y los pendientes.

## 11. Para ahorrar tiempo y tokens
- Copiar `motor/cap03/` como base para el capítulo nuevo. Se cambian solo `timeline.py` (guion), `diagrams.py` y las escenas de `cap3.py`.
- No rehacer el personaje, el cuarto, el sonido ni el render: ya funcionan.
- Al terminar un capítulo, guardar su código en `motor/capNN/`.
