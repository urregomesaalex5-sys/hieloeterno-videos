# Cap. 9 · El relé — 5/6 nov 2026 (turno de noche, hecho solo por la oficina)

**Tema:** el relé. Salió del backlog (prioridad 2, formato ganador "¿Cómo funciona un [X]?"); sigue natural al inductor del cap. 8 (usa la bobina y el pico de voltaje). No hubo pedido nuevo de seguidores que se pudiera leer (Metricool no trae los comentarios).
**Título:** "¿Cómo funciona un RELÉ? 🧲 | Cap. 9"
**Duración:** 81,4 s · 14 frases · 206 palabras · voz de 86,7 s con los silencios largos; en el video las pausas entre frases se recortan al 70 % (carlos, eleven_v4, 1 toma, 1.433 créditos).
**Regla de exactitud:** cada frase sale de `VERIFICACION.md` (códigos R#).
**Mejora nueva de este capítulo:** PLANOS CERCANOS. La "cámara" entra al relé (la tapa sale volando y se ve el corte), hace zoom a los contactos en el ¡CLIC! y hace zoom al relé #70 de la Mark II donde quedó la polilla (pedido del cap. 8: "más planos cercanos del componente"). Además, el sonido del clic de relé es un efecto nuevo hecho a mano (golpe de armadura + tic de contactos con rebote) y la música lo usa como hi-hat.

## Intro nueva (gancho en el segundo 0,4, no repetida)
Laboratorio en penumbra con el título ya en pantalla. Sobre el mesón hay un tablerito verde con un botoncito rojo, un relé azul y un cable grueso hasta un REFLECTOR gigante en trípode. Él tiene el dedo en el botón y a los 0,4 s lo aprieta: ¡CLIC! (burbuja de cómic), el reflector prende con destello blanco y un cono de luz, el cuarto se ilumina y él se echa para atrás haciendo visera con la mano. En la promesa, una polilla vuela alrededor del reflector (anticipa el "bicho" del final).
No repite: asomarse (1), colgar (2), gravedad (3), puerta-diodo (4), flash a oscuras (5), celular gigante (6), LED quemado (7), interruptor de cuchilla + neón (8).

## Guion y escenas
| # | Voz | En pantalla | Respaldo |
|---|---|---|---|
| 0 | ¡Un botoncito de cinco voltios prendió este reflector gigante! ¿Cómo funciona un RELÉ? | Botón → ¡CLIC! → reflector. Rótulos "BOTÓN · 5 V", "REFLECTOR", "RELÉ". | R1, R5 |
| 1 | Al final, te cuento qué bicho encontraron dentro de un relé. | Título vuela a la etiqueta. Polilla volando junto a la luz. "AL FINAL: ¿QUÉ BICHO?". | promesa → 10 |
| 2 | Un relé es un interruptor que se mueve con un imán: adentro hay una bobina. | Manotazo. Lanza el relé azul (SRD-05VDC-SL-C, 10 A 250 VAC…); la tapa sale volando y queda el CORTE: bobina, núcleo, yugo, armadura, resorte, contactos. | R1 |
| 3 | Con corriente, se vuelve imán... y jala una pieza de hierro que cierra los contactos. | Cuadritos de corriente por la bobina, "¡IMÁN!" y brillo azul; la armadura baja, ¡CLIC!, el remache pasa de NC a NA. Rótulos NÚCLEO, ARMADURA, NC, NA, COM. | R1, R7 |
| 4 | ¡Ese clic que oyes es metal golpeando metal! | PLANO CERCANO a los contactos: suelta y vuelve a cerrar, ¡CLIC! grande, "METAL CONTRA METAL". Él se tapa los oídos. | R2 |
| 5 | Sin corriente, un resorte la devuelve. | Se corta la corriente, la armadura sube con rebote, brilla el resorte, "RESORTE". | R8 |
| 6 | Pero lo genial: pide unos setenta y un miliamperios... y maneja hasta diez amperios. | Manotazo. Medidores "71 mA · BOBINA" y "10 A · CONTACTOS"; el relé conmuta un bombillo grande; "HASTA 10 A · 250 V~". | R3, R4 |
| 7 | Un circuito chiquito manda sobre uno grande... y nunca se tocan. | El medidor chico se encoge y el grande crece ("CHIQUITO" / "GRANDE"); línea roja punteada "AISLADOS · 1.500 V". | R5, R6 |
| 8 | Ojo: al apagarlo, la bobina lanza un pico de voltaje, como en el capítulo pasado. Por eso se le pone un diodo. | Gráfica voltaje–tiempo con el PICO rojo; neón "CAP. 8"; cae un diodo en paralelo con la bobina y la traza verde "CON DIODO" queda sin pico. | R9 |
| 9 | En el carro, las luces y el pito usan relés: así la corriente fuerte no pasa por el botón. | Frente de carro: prenden las farolas, ¡PIII!; esquema botón (cable delgado) → relé → cable grueso de la batería a las luces. | R13 |
| 10 | Y el bicho: en 1947 encontraron una polilla atrapada en el relé 70 de la computadora Mark II... ¡y la pegaron en el cuaderno como primer bug real! | Panel "MARK II · PANEL F", la polilla entra volando y queda en el relé #70 (zoom); el cuaderno "9/9/47 · Relay #70 Panel F", la polilla pegada con cinta y "First actual case of bug being found." + traducción. | R19, R20 |
| 11 | La palabra bug ya existía: ¡fue un chiste! | Sello "LA PALABRA YA EXISTÍA" y "¡CHISTE!"; él se ríe agarrándose la barriga. | R21 |
| 12 | Así que un relé es un interruptor con imán. | Símbolo del relé que conmuta (clic-clic) + "IMÁN + INTERRUPTOR". | R1 |
| 13 | ¡Dale me gusta, suscríbete y sígueme! Reto: con el relé apagado, ¿al común se conecta la N A o la N C? ¡Respóndeme! | Botones; tarjeta del reto con el símbolo tapado con "?", "¿COM → NA o NC?". Chasquido, luz y pantalla de TV apagadas. | R7 |

**Respuesta al reto:** la **NC** (normalmente cerrado): con la bobina sin corriente, el resorte deja el común tocando el contacto NC (R7, R8).

## Música
Clic de relé + acorde grande de "encendido" (Mi menor) cuando prende el reflector; luego groove a 108 BPM (Em9–Cmaj7–G6–D6sus) con hi-hat hecho de clics de relé y un pad CONMUTADO todo-o-nada (ON-ON-OFF-ON…), y marimba que salta entre dos notas (NA / NC).
