# Verificación técnica · Cap. 9 · ¿Cómo funciona un RELÉ?

Regla: cero información falsa. Cada frase del guion sale de esta tabla (códigos R#).
Tipos: **HECHO** (verificado en fuente), **ANALOGÍA** (se dice como analogía y se anota su límite), **PENDIENTE** (no entra al guion).
Investigación del 6 nov 2026 (páginas abiertas y leídas).

## A. Afirmaciones del guion
| # | Afirmación | Tipo | Fuente | Límite (qué NO decir) |
|---|---|---|---|---|
| R1 | Un relé electromecánico es un interruptor movido por un electroimán: la corriente en la bobina magnetiza el núcleo de hierro, este atrae una pieza móvil (armadura) que gira sobre un punto de apoyo y abre o cierra los contactos | HECHO | Omron, "Principles of relays" https://www.ia.omron.com/support/guide/36/principles.html | Existen relés de estado sólido (sin piezas móviles, no hacen clic): decir "un relé **electromecánico**" o "un relé clásico". |
| R2 | El "clic" viene de golpes mecánicos: la armadura choca contra el núcleo al atraerse, y los contactos chocan entre sí (al soltar, la armadura golpea el lado NC) | HECHO | Patente US6798322 "Low noise relay" https://patents.google.com/patent/US6798322 · Patente JPH05190071A https://patents.google.com/patent/JPH05190071A/en · SparkFun SIK exp. 13 (se oye un clic al activar) https://learn.sparkfun.com/tutorials/sik-experiment-guide-for-arduino---v33/experiment-13-using-relays | No decir que es "la electricidad" la que suena. Es metal golpeando metal. |
| R3 | Songle SRD-05VDC-SL-C ("L" = bobina de 0,36 W): bobina de 5 V, **70 Ω, 71,4 mA** (≈0,36 W). La versión "D" (0,45 W) es 55 Ω, 89,3 mA | HECHO | Hoja de datos Songle SRD (código de pedido SRD-XXVDC-S-L-C: S = sellado, L = 0,36 W, C = 1 forma C) https://w.electrodragon.com/w/images/3/3e/SRD_songle_relay_specification.pdf · LCSC C35449 (70 Ω, 360 mW) https://lcsc.com/product-detail/Power-Relays_Ningbo-Songle-Relay-SRD-05VDC-SL-C_C35449.html | El rango "70–90 mA" mezcla dos versiones. Para el SL-C: **~71 mA**. |
| R4 | Contactos del SRD (carga resistiva): **10 A 250 VAC, 10 A 125 VAC, 10 A 30 VDC**. Con carga inductiva (motores) baja a 3–5 A. TÜV: 10 A/250 VAC, 30 VDC; UL: 10 A/125 VAC, 28 VDC | HECHO | Misma hoja de datos Songle SRD (tabla de contactos y aprobaciones) | Decir "hasta 10 A" (es máximo, carga resistiva). LCSC dice "15 A" en su tabla: **no usar**, no está en la hoja. No decir que el **módulo** de Arduino aguanta 10 A (ver PENDIENTE). |
| R5 | Con ~71 mA a 5 V (≈0,36 W) en la bobina se conmutan hasta 10 A a 250 V (≈2.500 VA en carga resistiva) | HECHO (cálculo con R3–R4) | Hoja Songle SRD · Omron (los relés se usan para encender fuentes de carga) | El relé no "amplifica" energía: solo deja pasar o corta la corriente de otro circuito. La hoja limita la potencia máxima de la forma C (no decir una cifra de VA distinta). |
| R6 | La bobina y los contactos son circuitos separados: el aislamiento soporta **1.500 VAC durante 1 minuto** entre bobina y contacto (resistencia de aislamiento ≥100 MΩ a 500 VDC) | HECHO | Hoja Songle SRD (rigidez dieléctrica) · LCSC (FAQ: 1500 VAC bobina–contactos) | "Aislados eléctricamente" sí; no decir que eso hace "seguro" tocar el lado de 220 V. |
| R7 | Terminales: **COM** (común), **NA/NO** (normalmente abierto: se conecta a COM solo cuando la bobina tiene corriente) y **NC** (normalmente cerrado: conectado a COM cuando la bobina está apagada). SL-C = 1 forma C (conmutado), 5 pines | HECHO | SparkFun SIK exp. 13 · Omron principles (NO = "make", NC) · hoja Songle (1C) | En el SL-C los 5 pines son: 2 de bobina + COM + NO + NC (por la forma 1C; el orden físico de pines no se verificó → no dibujarlo con números de pin). |
| R8 | Al quitar la corriente, el resorte de retorno devuelve la armadura a su posición | HECHO | Omron principles ("the force of the release spring returns the armature") | — |
| R9 | Al apagar la bobina, el campo magnético colapsa y aparece un pico de voltaje: un relé de 12 V puede generar **1.000–1.500 V** al apagarse. Por eso se pone un diodo en inverso **en paralelo con la bobina** (diodo de rueda libre / flyback) | HECHO | TE Connectivity, "Relay coil suppression – DC relays" https://www.te.com/en/products/relays-and-contactors/electromechanical-relays/intersection/relay-coil-suppression-dc-relays.html · Omron FAQ (vía DigiKey) https://forum.digikey.com/t/what-are-surge-countermeasures-in-coil-relays/33842 | La cifra 1.000–1.500 V es para 12 V **sin protección** (dato de TE). Efecto secundario: el diodo hace que el relé suelte más lento (TE, Omron). Enlaza con el cap. 8 (autoinducción). |
| R10 | Tiempos del SRD: operación **10 ms máx.**, liberación **5 ms máx.** | HECHO | Hoja Songle SRD · LCSC (10 ms) | Son **máximos**, no típicos. Decir "en menos de 10 milésimas de segundo". |
| R11 | Encendido/apagado del SRD-05: se activa con a lo más 75 % del voltaje (≤3,75 V) y suelta por debajo de ~10 % (0,5 V) | HECHO | Hoja Songle SRD (pull-in 75 % máx., drop-out 10 % mín.) | Opcional; no es necesario en el guion. |
| R12 | Un pin de Arduino Uno (ATmega328P) tiene máximo absoluto de **40 mA** (especificado a 20 mA): no alcanza para los ~71 mA de la bobina; por eso se usa un transistor (y el diodo) | HECHO | Arduino Playground "Pin current limitations" https://www.arduino.cc/playground/Main/ArduinoPinCurrentLimitations/ · SparkFun SIK exp. 13 (transistor maneja el relé) | Los "módulos de relé" traen ya el transistor y el diodo en muchos modelos, pero no todos: decir "por eso los módulos suelen traer un transistor". |
| R13 | En los carros: relés para luces y bocina (pito); así la corriente fuerte va corta, de la batería al faro por el relé, y el interruptor del tablero solo lleva una corriente de control pequeña (<150 mA en el ejemplo de HELLA) | HECHO | Catálogo HELLA Relays/Horns/Switches 2012, p. 7 https://konpart.de/wp-content/uploads/2024/11/HELLA-Relays-Horns-Switches-Catalog-2012.pdf | "Relé de arranque": no verificado con fuente buena → PENDIENTE. |
| R14 | El "tic-tac" de la direccional: en carros viejos venía de un intermitente térmico (lámina bimetálica) o de un relé; en carros modernos a veces hay un relé real y **a veces el sonido es simulado por parlantes** | HECHO (fuente de prensa) | Jalopnik "Here's why your turn signals make that clicking noise" https://jalopnik.com/heres-why-your-turn-signals-make-that-clicking-noise-1793380845 | No decir "siempre es un relé" ni "siempre es falso". Decir "en algunos carros nuevos el sonido es simulado" (la fuente dice "a veces"). No nombrar marcas. |
| R15 | 1835: Joseph Henry, en el College of New Jersey (hoy Princeton), usó un electroimán pequeño para controlar otro grande que sostenía pesas; al cortar el circuito pequeño, las pesas caían. Mostró que se podía controlar algo a distancia, base del telégrafo | HECHO | Smithsonian Institution Archives, "Joseph Henry Demonstrates Primitive 'Relay' Telegraph" https://siarchives.si.edu/collections/siris_sic_12484 · SIA "Joseph Henry: Inventor of the Telegraph?" https://siarchives.si.edu/collections/siris_sic_12604 | No decir "Henry inventó el telégrafo" (es disputado con Morse). Decir "un relé primitivo". |
| R16 | En las líneas largas de telégrafo la señal llegaba débil; se ponía un relé y una batería local en cada estación: la corriente débil movía el relé y este cerraba un circuito local fuerte | HECHO | Avery (1895), citado en ClipArt ETC, Univ. South Florida https://etc.usf.edu/clipart/36000/36094/tele_relay_36094.htm | Así dicho ("repetía/reforzaba la señal") está bien; no dar fechas ni nombres de inventor de esto. |
| R17 | Zuse Z3: presentado el **12 de mayo de 1941** en Berlín; **más de 2.000 relés** (Horst Zuse da ~2.600: ~600 aritmética + ~2.000 memoria; Zuse Institute Berlin da 2.000); reloj ~5,3 Hz; el original se destruyó en un bombardeo en 1943; hay réplica en el Deutsches Museum | HECHO | Zuse Institute Berlin https://zuse.zib.de/z3 · Horst Zuse https://horst-zuse.hier-im-netz.de/Konrad_Zuse_index_english_html/rechner_z3.html | Las fuentes no coinciden en el número exacto → decir "**más de 2.000 relés**". No decir "la primera computadora" a secas (es un debate). |
| R18 | Harvard Mark I (1944, IBM + Howard Aiken): electromecánica, ~16 m de largo, **3.500 relés** con 35.000 contactos, además de contadores e interruptores | HECHO | IEEE Milestone proposal (ETHW) https://ethw.org/Milestone-Proposal:Harvard_Mark_1_Computer,_1944_-_1959 | No decir que era "toda de relés" (usaba también contadores giratorios). |
| R19 | Harvard Mark II: construida con relés electromagnéticos rápidos, para la Marina de EE. UU. (Dahlgren); terminada y depurada en sept. 1947 | HECHO (apoyo) | Wikipedia "Harvard Mark II" (cita a Rife 2006, GPO, y Annals of the Computation Lab, 1949) https://en.wikipedia.org/wiki/Harvard_Mark_II | Número de relés del Mark II (~13.000): solo fuentes débiles → PENDIENTE. |
| R20 | El 9 de septiembre de 1947, operadores del Mark II encontraron una polilla atrapada entre los contactos del **relé n.º 70, panel F**, y la pegaron en el cuaderno con la nota "First actual case of bug being found" ("primer caso real de bug encontrado") | HECHO | Smithsonian NMAH, "Log Book With Computer Bug" (1994.0191.01) https://www.si.edu/object/log-book-computer-bug:nmah_334663 · Naval History and Heritage Command, foto NH 96566-KN (relé #70, panel F) https://ibiblio.org/hyperwar/OnlineLibrary/photos/images/h96000/h96566kc.htm · Computer History Museum https://www.computerhistory.org/tdih/september/9/ | La leyenda vieja de la foto del NHHC dice "1945": es un error conocido; Smithsonian, CHM y JSTOR dan 1947. Usar **1947**. No dar la hora (15:45) — no la confirmó una fuente buena. |
| R21 | La palabra "bug" (falla en una máquina) **ya existía**: Edison la usaba en 1878 y salió en prensa en 1889. La polilla fue un chiste sobre una palabra ya conocida, **no el origen** | HECHO | Smithsonian NMAH (Edison hablaba de bugs en circuitos en los 1870) · JSTOR Daily "The bug in the computer bug story" https://daily.jstor.org/the-bug-in-the-computer-bug-story/ · CHM | Prohibido: "así nació la palabra bug". |
| R22 | Quién la encontró: **el equipo/operadores** del Mark II, no se sabe el nombre. Grace Hopper trabajaba en ese equipo y después **hizo famosa la historia** en sus charlas. Smithsonian: el cuaderno "probablemente no era de Hopper" | HECHO | Smithsonian NMAH · Computer History Museum · JSTOR Daily | Prohibido: "Grace Hopper encontró la polilla" o "Hopper escribió la nota". |

## B. Dato extra (comentario fijado)
| # | Afirmación | Tipo | Fuente | Límite |
|---|---|---|---|---|
| D1 | El SRD de Songle está garantizado para al menos **10 millones** de operaciones sin carga, pero solo **100.000** con carga eléctrica: lo que más lo gasta son las chispas en los contactos, no el movimiento | HECHO (la primera parte) | Hoja Songle SRD (vida mecánica 10⁷, eléctrica 10⁵) | "Lo que más lo gasta son las chispas": es la explicación usual, **no** la dice la hoja → para el comentario usar solo: "10 millones de clics sin carga, 100.000 con carga". |
| D2 | Joseph Henry imaginaba con su demo de 1835 hacer sonar campanas de iglesia a distancia | HECHO (según recuerdos de alumnos) | Smithsonian Institution Archives siris_sic_12484 | Decir "según recordaban sus alumnos". |

## C. Analogías
| Analogía | Límite que hay que rotular |
|---|---|
| El relé es "un dedo magnético" que aprieta un interruptor | "ANALOGÍA": no hay dedo; es la armadura de hierro atraída por el imán. |
| "Un circuito chiquito le da órdenes a uno grande" | Bien como imagen; el relé no amplifica energía, solo conecta o corta (R5). |

## D. PENDIENTE / no usar
- "Relé de arranque / motor de arranque": no hay fuente buena leída (solo anuncios). El solenoide del motor de arranque es otra pieza; no se menciona.
- Número de relés del Harvard Mark II (~13.000): solo fuentes débiles.
- Hora de la polilla (15:45): no confirmada en fuente primaria leída.
- Que los **módulos** de relé para Arduino aguanten 10 A: el 10 A es del relé; las pistas y bornes del módulo dependen del fabricante.
- Orden físico de los 5 pines del SRD: no verificado.
- "15 A 125 VAC" para el SRD-05VDC-SL-C: aparece en tiendas, no en la hoja de datos leída.
- Electrodomésticos concretos (lavadora, aire acondicionado…) que usan relés: sin fuente específica leída. Se puede decir "aparatos de casa" solo en general, mejor evitar.

## E. Para el animador
- Relé azul tipo Songle SRD-05VDC-SL-C, bobina con núcleo, armadura, resorte, contactos COM / NO / NC.
- Rótulos permitidos: "BOBINA 5 V · ~71 mA", "CONTACTOS: HASTA 10 A · 250 V~", "COM", "NA (NO)", "NC", "RESORTE", "ARMADURA", "AISLADO: 1.500 V", "DIODO EN PARALELO", "< 10 ms", "RELÉ #70 · PANEL F · 9 SEP 1947", "MÁS DE 2.000 RELÉS (Z3)".
- Si se muestra 220 V: rótulo de PELIGRO; no mostrar a nadie tocando bornes.

## Frases seguras para el guion
1. "Un relé es un interruptor que se mueve con un imán." (R1)
2. "Adentro hay una bobina: cuando le pasa corriente, se vuelve imán y jala una pieza de hierro." (R1)
3. "Ese clic que oyes es metal golpeando metal: la pieza contra el imán y los contactos chocando." (R2)
4. "Este relé de 5 voltios pide unos 71 miliamperios… y puede manejar hasta 10 amperios a 250 voltios." (R3, R4)
5. "Un circuito chiquito le da órdenes a uno grande, y nunca se tocan: los separa un aislamiento que aguanta 1.500 voltios." (R5, R6)
6. "Tiene tres patas de salida: común, normalmente abierto y normalmente cerrado." (R7)
7. "Cuando cortas la corriente, un resorte lo devuelve a su lugar." (R8)
8. "Y al apagarlo, la bobina lanza un pico de voltaje, el mismo efecto del capítulo pasado. Por eso se le pone un diodo al revés, en paralelo." (R9)
9. "Todo eso pasa en menos de 10 milésimas de segundo." (R10)
10. "Un pin de Arduino no da tanta corriente; por eso los módulos de relé suelen traer un transistor." (R12)
11. "En el carro, las luces y el pito usan relés para que la corriente fuerte no pase por el botón." (R13)
12. "¿Y el tic-tac de las direccionales? En algunos carros nuevos ya no es un relé: es un sonido que sale por el parlante." (R14)
13. "Ya en 1835, Joseph Henry usó un electroimán pequeño para controlar uno grande. Esa idea ayudó a nacer el telégrafo." (R15, R16)
14. "En 1947, en la computadora Mark II, encontraron una polilla atrapada en el relé 70, la pegaron en el cuaderno y escribieron: 'primer caso real de bug encontrado'. Ojo: la palabra 'bug' ya existía; fue un chiste." (R20, R21, R22)

## Lo que NO se puede decir
- "Grace Hopper encontró la polilla" / "Hopper inventó la palabra bug". (R22, R21)
- "Así nació la palabra bug". (R21)
- "El primer bug fue en 1945" (error de la leyenda vieja de la foto). (R20)
- "El Z3 tenía exactamente 2.600 relés" o "fue la primera computadora" a secas. (R17)
- "Joseph Henry inventó el telégrafo". (R15)
- "Todos los relés hacen clic" (los de estado sólido no). (R1)
- "La bobina consume 70–90 mA" para el SL-C (mezcla versiones) / "aguanta 15 A". (R3, R4)
- "El relé amplifica la corriente/energía". (R5)
- "El tic-tac de las direccionales siempre es falso" o "siempre es un relé". (R14)
- "El módulo de Arduino aguanta 10 A". (D)
- "Relé de arranque" o el número de relés del Mark II. (D)
- "Tarda 10 ms" como típico (es el máximo). (R10)

## Decisión del control de calidad (6 nov 2026)
- En las frases 2 y 12 la voz dice "Un relé es un interruptor…" sin "electromecánico". Se deja así porque el video entero muestra un relé electromecánico (con bobina y armadura), la frase segura n.º 1 usa la forma corta, y el comentario fijado aclara que también existen relés de estado sólido sin piezas móviles que no hacen clic (R1).
