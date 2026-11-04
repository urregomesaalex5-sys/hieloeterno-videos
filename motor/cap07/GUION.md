# Cap. 7 · La resistencia (borrador, 4 nov 2026)

**Estado:** guion aprobado (BOTÓN 1) y publicación aprobada (BOTÓN 2) por Edwin el 4 nov 2026. Portadas elegidas: A (Instagram) y C (TikTok).
**Estado anterior:** borrador del ✍️ guionista, a la espera del BOTÓN 1 (OK de Edwin). No se ha generado voz ni publicado nada.
**Tema:** propuesto por el 🔎 explorador (backlog, línea 6). **No salió de un comentario de un seguidor: no hay crédito a nadie.**
**Título (en pantalla y primera frase):** "¿Cómo funciona una RESISTENCIA?"
**Duración estimada:** ≈ 75 s en total (≈ 72 s de voz + 3 s de cierre con el reto en pantalla; margen real 72–78 s). 13 frases · 177 palabras · 1.347 caracteres de voz (≈ 1.350 créditos, menos que el cap. 6).
**Regla de exactitud:** cada frase sale de `VERIFICACION.md` (códigos H#). Nada PENDIENTE entra al guion.

## Intro nueva (gancho en el segundo 0, no repetida)
Laboratorio ya encendido (sin oscuridad, para no repetir el ¡FLASH! del cap. 5). Frame 0: el título "¿CÓMO FUNCIONA UNA RESISTENCIA?" arriba y un LED conectado **directo** a una fuente de laboratorio con pantalla "5,00 V". Él ya está pulsando el botón de la fuente (el mundo lo activa él): el LED brilla fortísimo, ¡pop! con una chispita y un hilo finito de humo, y queda negro y agrietado. Cara de sorpresa, **sin taparse la cara**. Es el "¡wow!" en el segundo 0 y la promesa va enseguida.
No repite: asomarse desde abajo (1), colgar de cabeza (2), gravedad (3), puerta-diodo (4), flash a oscuras (5), celular gigante (6). Tampoco el ¡PUM! con humo y tapa volando del electrolítico (cap. 5): aquí es un LED pequeño, un chasquido y un hilo de humo.

## Guion y escenas
Tiempos estimados con el estimador de `timeline.py` (se corrigen con la voz real).
| # | t (s) | Voz | Qué pasa en pantalla | Respaldo |
|---|---|---|---|---|
| 0 | 0,2 | ¡Se quemó el LED! ¿Cómo funciona una RESISTENCIA? | Frame 0: título grande + LED directo a la fuente "5,00 V". Él pulsa el botón: destello, ¡pop!, hilo de humo, LED negro y agrietado. Cara de sorpresa. Rótulo naranja "CAP. 7 · RESISTENCIA". | H2, H3 |
| 1 | 3,7 | Te enseño a salvarlo... y a leer su código de colores. | Con guiño toma con los dedos una resistencia diminuta (franjas naranja, naranja, marrón, dorado) y la muestra a cámara. Rótulo "AL FINAL: CÓDIGO DE COLORES" con 4 franjas. | — |
| 2 | 8,8 | Una resistencia limita la corriente. ¡Y el LED prende bien! | Cambia el LED, pone la resistencia en el camino, cierra el circuito: prende parejo. Pose "¡ta-dá!". Barra de corriente: sin resistencia sube y pasa la línea roja "MÁX. TÍPICO DE UN LED: 20 mA"; con resistencia se queda abajo. | H1, H2, H3 |
| 3 | 13,0 | Fuente de cinco voltios; el LED se queda en unos dos. ¡A la resistencia le tocan tres! | Lanza el esquema (clac): fuente → resistencia → LED. LED ROJO (los azules/blancos piden ≈3 V). Dos voltímetros: LED "≈ 2 V", resistencia "3 V". Barra apilada 5 V = 2 V + 3 V. | H3, H4 |
| 4 | 19,9 | Ley de Ohm: la corriente es voltaje entre resistencia. Tres entre trescientos treinta: unos nueve miliamperios. | Ecuación grande "I = V ÷ R"; entran los números: 3 V ÷ 330 Ω y el contador sube hasta ≈ 9 mA (por debajo de la línea de 20 mA). Rótulo pequeño: "La ley de Ohm es de la resistencia, no del LED". | H5, H6, H7 |
| 5 | 24,6 | Ojo: no se come la corriente. ¡La que entra es la misma que sale! | **Mini gancho 1.** Dos amperímetros, antes y después de la resistencia: los dos marcan 9 mA. Sello rojo "NO SE CONSUME" sobre "consume corriente". Él mueve el dedo en negación. | H8 |
| 6 | 30,3 | Los electrones chocan con átomos que vibran y les pasan energía: ¡calor! Es el efecto Joule. | Zoom dentro de la resistencia: red de átomos, electrones que chocan y los átomos vibran más y se ponen naranja; termómetro sube. Rótulo "MODELO SIMPLIFICADO". Título "EFECTO JOULE" con rebote. | H9, H10 |
| 7 | 36,9 | ¿Y si quieres ese calor? ¡En una tostadora, el alambre se pone al rojo a propósito! | **Mini gancho 2.** Manotazo al diagrama. Cae una tostadora (clac) con corte lateral: alambre que se pone rojo-naranja y tuesta el pan; él se calienta las manos. Rótulo "CALOR A PROPÓSITO". | H11 |
| 8 | 43,4 | El código de colores: dos dígitos, un multiplicador y la tolerancia. | La resistencia se agranda: 4 franjas con rótulos "1.ª cifra · 2.ª cifra · multiplicador · tolerancia". | H12 |
| 9 | 48,0 | Naranja, naranja, marrón, dorado: tres, tres, por diez... ¡trescientos treinta ohmios, más o menos cinco por ciento! | Decodifica paso a paso con números que vuelan: 3 · 3 · ×10 · ±5 % → "330 Ω ±5 %". Es la **misma resistencia** del LED. Rótulo breve: "valor real entre 313,5 y 346,5 Ω". Cierra la promesa del código. | H5, H12, H13, H14 |
| 10 | 54,2 | Tu celular tiene cientos de componentes pasivos, y entre ellos hay resistencias. | **Mini gancho 3.** Corte a la placa por dentro del celular (`pcb.py`): lupa sobre las resistencias diminutas, rótulo "EXISTEN DE 0,4 × 0,2 mm (tamaño 01005)". Sin cifra de "resistencias por celular". | H15, H16, H18 |
| 11 | 59,3 | Así que una resistencia limita cuánta corriente pasa... ¡y por eso salvó a mi LED! | De vuelta en el laboratorio: el LED nuevo prende y el LED quemado queda en el estante con una crucecita "R.I.P.". Palmadita a la resistencia. Rótulo "LIMITA LA CORRIENTE". Cierra la promesa del segundo 3. | H7, H8 |
| 12 | 65,2 | ¡Dale me gusta, suscríbete y sígueme! Reto: marrón, negro, rojo, dorado. ¿Cuánto vale? ¡Respóndeme! | Botones Me gusta / Suscríbete / Sígueme + campanita. Sale una resistencia misteriosa con las franjas marrón-negro-rojo-dorado y "¿CUÁNTO VALE?" + "RESPÓNDEME EN LOS COMENTARIOS". Chasquido, luz apagada y la TV de su cara se apaga (firma). | H17 |

**Mini ganchos:** segundo 0 (el LED que se quema), ~10 s (el LED prende bien), ~25 s ("no se come la corriente"), ~37 s (tostadora), ~54 s (celular) y ~65 s (reto). Algo nuevo en pantalla cada 3–5 s (cada frase tiene 2 o 3 eventos visuales).

## Lo que se dejó fuera a propósito (para no decir nada a medias)
- **Divisor de voltaje**: es el segundo gran uso de la resistencia, pero explicarlo bien necesita otro ejemplo y alargaría el video. Va para un posible capítulo corto.
- **Potencia (P = V·I, vatios) y por qué las resistencias vienen de ¼ W, ½ W…**: da para un capítulo propio.
- **Por qué un LED "se queda en 2 V"**: es física de semiconductores y se ve en el cap. 4 (diodo). Aquí se dice "unos dos" y el rótulo aclara que la ley de Ohm no aplica al LED.
- **Resistencias de 5 bandas, SMD con números (331) y potenciómetros.**
- **Ducha eléctrica y secador**: sin fuente propia para este guion; se usa solo la tostadora (nicromo, respaldada).
- **La velocidad de los electrones** (lentísima): se deja como dato extra del comentario fijado en lugar de apurar una explicación en 3 segundos.
- **"Tu celular usa X resistencias"**: depende del modelo; solo se dice "cientos de componentes pasivos, y entre ellos hay resistencias".
- **Analogía del tubo de agua**: se descartó para no arrastrar sus límites (ver VERIFICACION.md, sección C).

## Voz (ElevenLabs)
- Voz carlos (`zSPJ694fdnzmEKl5n9wI`), eleven_v4, todo en un texto con `[long pause]`.
- Etiquetas usadas: [surprised], [excited], [mischievously], [happy], [warmly]. Sin [whispers] ni [curious] ni partes bajitas.
- El personaje nunca dice su nombre.
- "LED" se lee "led" (si suena raro, escribir "ele-e-de" solo en el texto de voz). "Ohm" y "miliamperios" se dejan como están; revisar la pronunciación en la toma.
- Los números van en palabras ("trescientos treinta") para que no se lea "tres cientos".
- Primero `estimate_only` (≈ 1.350 créditos), luego una sola toma. Después de grabar: revisar que la velocidad sea pareja (13–18 caracteres/s).
- La frase 12 es la más larga del cierre; si la voz la apura, partir "Reto…" en su propia frase y pegarla con `insert_phrase.py`.

## Cómo este guion aplica las notas del analista
1. **Título/primera frase con la fórmula ganadora**: "¿Cómo funciona una RESISTENCIA?" (componente clásico, muy buscado, como el transistor del cap. 1 que hizo ~50x). Nada de preguntas raras.
2. **El "¡wow!" en el segundo 0**: el LED se quema antes de hablar de nada; sin saludo ni intro lenta. La luz del lab ya está encendida (el gancho del cap. 4 dio 69 % de view rate con la luz ya prendida).
3. **Promesa al inicio, cumplida dos veces**: "te enseño a salvarlo" (frases 2 y 11, el LED vive) y "a leer su código de colores" (frases 8 y 9).
4. **Mini gancho cada 10–15 s** (lista arriba) y evento nuevo cada 3–5 s.
5. **Duración ≈ 75 s en vez de 100 s**: 177 palabras (el cap. 6 tuvo 251). Para eso se dejaron fuera divisor de voltaje, potencia y la analogía del agua.
6. **Retención:** lo más fuerte (quemar y salvar el LED) está pegado al inicio, y el reto cierra con curiosidad abierta.
7. **Comentarios**: en lugar de la pregunta de siempre ("¿qué componente quieres ver?"), el video cierra con un **reto con respuesta concreta** (marrón-negro-rojo-dorado: ¿cuánto vale?). Pide una acción fácil, que se puede acertar y que da pie a contestar. El comentario fijado agrega un dato extra y una segunda invitación madura (decir los colores de una resistencia propia para que se la lean). Hay que responder los comentarios en las primeras horas.
8. **Seguidores**: CTA corto (una sola frase) y el reto aparece justo después, para que "sígueme" no sea lo último que se oiga.
9. **Sin crédito inventado**: el tema lo propuso el explorador; no se menciona a nadie.

## Publicación (borrador para el BOTÓN 2)
- **Comentario fijado (dato extra verificado + invitación madura, distinto a los de los caps. 3–6):**
  > Dato extra: los electrones de un cable avanzan LENTÍSIMO. En un alambre de cobre de 2 mm de diámetro con 1 amperio, van a unos 23 micrómetros por segundo, o sea unos 8 centímetros por HORA. Entonces, ¿por qué la luz prende al instante? Porque la señal viaja como onda electromagnética guiada por el cable, a entre el 50 % y el 99 % de la velocidad de la luz, según el cable. 🤯 Y el reto sigue en pie: marrón, negro, rojo, dorado, ¿cuánto vale? Si tienes una resistencia a la mano, escribe sus colores y te ayudo a leerla.
  (Respaldo D1, D2, D3, H17. Los datos de "ese alambre y esa corriente" van en el comentario para que nadie crea que es una cifra universal.)
- **Respuesta al reto (para contestar a quien acierte):** 10 × 100 = 1.000 Ω = 1 kΩ, con ±5 %.
- **Opciones de título:**
  1. ¿Cómo funciona una RESISTENCIA? 🔥 | Cap. 7 (la fórmula ganadora; recomendada)
  2. ¿Por qué un LED necesita una resistencia? ⚡ | Cap. 7
  3. Esta pieza diminuta salva a tu LED 💡 ¿Cómo funciona una resistencia? | Cap. 7
- **Descripción (borrador):** ¿Por qué se quema un LED y qué lo salva? 🔥 En este capítulo ves qué hace una resistencia: limita la corriente, cómo se calcula con la ley de Ohm, por qué se calienta (efecto Joule), por qué las tostadoras la usan a propósito y cómo leer su código de colores. 🧩 Reto: marrón, negro, rojo, dorado, ¿cuánto vale? Respóndeme en los comentarios. 👍 Dale me gusta, suscríbete y sígueme. 🔊 Voz generada con ElevenLabs (elevenlabs.io)
- **Portada sugerida (para el 🖼️ miniaturista):** A: "¿CÓMO FUNCIONA UNA RESISTENCIA?" con el LED humeando y la resistencia a rayas al lado. B: "¿POR QUÉ SE QUEMÓ MI LED?".
- Etiquetas: resistencia, código de colores, ley de Ohm, led, electronica, aprende electronica, fisica, minecraft, animacion, shorts.
- El diseño de las franjas de color debe ser exacto (naranja, naranja, marrón, dorado y marrón, negro, rojo, dorado) porque son la prueba de lo que se dice.

## Dudas y puntos débiles
- La duración queda en el borde alto del objetivo (≈ 72 s de voz + 3 s de cierre). Si la voz sale lenta, recortar la frase 10 (celular) o la 8.
- La frase 6 usa el modelo clásico "los electrones chocan con átomos que vibran". Es la forma estándar de enseñarlo, pero es un modelo simplificado: el rótulo en pantalla es obligatorio.
- La norma IEC 60062 no se pudo leer (es de pago); el código se respalda en Wikipedia, que la cita, y en prácticas de fabricantes. Si Edwin quiere la fuente primaria, falta ese paso.
- Pocas hojas de datos de fabricante en las fuentes (Vishay CRCW, SparkFun). Varias son Wikipedia, Make y Raspberry Pi Magazine, aceptables como apoyo pero no como libro de texto; conviene reforzar con Vishay/Yageo si hay tiempo.
- "Cientos de componentes pasivos" sale de un solo artículo (Electronic Design); el artículo no desglosa cuántas son resistencias, por eso el guion no da ese número.
- El reto del final depende de que alguien responda: si no hay respuestas en 24 h, el 📊 analista debe revisar si conviene comentar la solución.
