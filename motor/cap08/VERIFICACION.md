# Verificación técnica · Cap. 8 · El inductor (la bobina)

Regla: cero información falsa. Cada frase del guion sale de esta tabla (códigos I#).
Tipos: **HECHO** (verificado en fuente), **ANALOGÍA** (se dice como analogía y se anota su límite), **PENDIENTE** (no entra al guion).
Investigación del 4 nov 2026 (páginas abiertas y leídas). Tema pedido por **@vpalep** en Instagram (comentario del cap. 1: "Inductores :D").

## A. Afirmaciones del guion
| # | Afirmación | Tipo | Fuente | Límite (qué NO decir) |
|---|---|---|---|---|
| I1 | Un inductor es un elemento de circuito que da autoinductancia; normalmente un alambre aislado enrollado en bobina, a veces con núcleo de hierro o ferrita | HECHO | OpenStax Univ. Physics 2, 14.2 https://openstax.org/books/university-physics-volume-2/pages/14-2-self-inductance-and-inductors · apoyo: Wikipedia "Inductor" | No decir que "siempre" lleva núcleo (hay bobinas de aire). |
| I2 | Una corriente crea un campo magnético alrededor del alambre; una brújula cercana se desvía (Oersted, 1820) | HECHO | Linda Hall Library, "Hans Christian Oersted" https://www.lindahall.org/about/news/scientist-of-the-day/hans-christian-oersted/ | La fecha exacta (21 abr) es "tradición"; no se dice. |
| I3 | El inductor guarda energía en su campo magnético: U = ½·L·I² | HECHO | OpenStax 14.3 https://openstax.org/books/university-physics-volume-2/pages/14-3-energy-in-a-magnetic-field · Murata app note MPAN-01 | Guarda, no "produce", energía; la devuelve cuando baja la corriente. |
| I4 | Se opone a los CAMBIOS de corriente (no a la corriente constante): un cambio de corriente cambia el flujo e induce una fem que se opone al cambio (Faraday + Lenz), ε = −L·dI/dt | HECHO | OpenStax 14.2 (la fem siempre se opone al cambio; con corriente constante no hay fem) · Coilcraft "What is an inductor" | No decir "frena la corriente". Con corriente constante, una bobina ideal es solo un alambre. |
| I5 | Bombillo con bobina grande en serie: la corriente sube poco a poco (τ = L/R); en la demo de dos ramas, el bombillo de la bobina prende con retraso | HECHO | OpenStax 14.4 https://openstax.org/books/university-physics-volume-2/pages/14-4-rl-circuits · U. Maryland Lecture Demos K7-03 https://lecdem.physics.umd.edu/k/k7/k7-03.html | El retraso va de milisegundos a segundos según L y R; no "se queda apagado". |
| I6 | Al abrir el interruptor de golpe, dI/dt es enorme y aparece un voltaje mucho mayor que el de la pila; con una bobina grande y una pila de **1,5 V** se prende brevemente un neón en paralelo | HECHO | U. Maryland Lecture Demos K2-11 https://lecdem.physics.umd.edu/k/k2/k2-11.html (pila de 1,5 V; fem inversa de "unos 90 V" que enciende el neón) | La cifra de 90 V es de esa bobina concreta. No decir que la bobina "multiplica" el voltaje como un transformador: es energía guardada que se descarga rápido. **9 V no verificado → se usa 1,5 V.** |
| I7 | Una lámpara de neón pequeña (NE-2) necesita decenas de voltios para encender: máx. de encendido 65 V (AC) / 90 V (DC) | HECHO | Hoja de datos NE-2 (A1A, RS) https://assets.rs-online.com/v1698855769/Datasheets/33c338a3395bf8a48766cf8b62fb2d18.pdf | Son valores máximos de encendido; el guion dice "decenas de voltios", el rótulo "hasta ~90 V". |
| I8 | En una analogía común (fuerza ↔ voltaje), la inductancia equivale a la masa y la corriente a la velocidad: cuesta arrancar y cuesta frenar | ANALOGÍA | Wikibooks "Engineering Acoustics/Electro-Mechanical Analogies" · Stocco (UBC), analogía de movilidad (la otra) | Hay DOS analogías; en la otra el inductor es un resorte → se dice "una analogía común". La "inercia" es del campo magnético, no de los electrones. Rótulo "ANALOGÍA". |
| I10 | Solenoide largo: L = μ·N²·A/ℓ; con el doble de vueltas en el mismo largo y área, L se multiplica por 4 | HECHO (con condiciones) | OpenStax 14.2 (L = μ0N²A/ℓ, solenoide largo, sin efectos de borde) | Respuesta del reto, NO se dice en el video. Aproximado; con núcleo magnético puede saturar. |
| I12 | Existen inductores de potencia de chip de 1,6 × 0,8 mm cuya aplicación principal son las fuentes de dispositivos como smartphones | HECHO | TDK, serie MLP1608 https://www.tdk.com/en/news_center/press/aah38500.htm · Murata 0603/1608 · Coilcraft XFL2010 | No se dice "tu celular tiene N inductores" ni qué modelo usa cuál. Se dice "existen… pensados para celulares". |
| I13 | Carga inalámbrica Qi: la corriente alterna de la bobina de la base crea un campo que cambia e **induce un voltaje** en la bobina del teléfono (luego se rectifica a DC); Qi v1.3 trabaja típicamente entre 87 y 205 kHz | HECHO | WPC "How Qi works" https://www.wirelesspowerconsortium.com/knowledge-base/magnetic-induction/how-qi-works/ · WPC Qi v1.3 Introduction (PDF) · Würth ANP014 | Se dice "induce un voltaje" (como WPC). Solo aplica a celulares con carga inalámbrica: el guion dice "y sin cable". |

## B. Dato extra (comentario fijado)
| # | Afirmación | Tipo | Fuente | Límite |
|---|---|---|---|---|
| D1 | La bobina de encendido de un carro parte de 12 V y entrega miles de voltios a la bujía (típico 5.000–25.000 V; hasta ~40–45 kV en carros modernos) cortando de golpe la corriente del primario: el campo colapsa e induce alto voltaje en un secundario de muchas más vueltas | HECHO | Delphi "Ignition coils – design and mode of operation" · aa1car "Ignition coils" | Dar rango, no una sola cifra. Tiene dos bobinas (no es solo autoinducción). |

## C. Analogías
| Analogía | Límite que hay que rotular |
|---|---|
| Inductor ≈ inercia (carrito pesado) | "ANALOGÍA": es una de dos analogías posibles; la inercia es del campo, no de los electrones. |

## D. PENDIENTE / no usar
- "Una pila de 9 V prende un neón": no verificado (se usa 1,5 V).
- "El inductor convierte/baja el voltaje" en un convertidor: FALSO así dicho; lo fija el ciclo de trabajo del interruptor, el inductor guarda y suaviza.
- "Tu celular lleva N inductores / en el PMIC": sin fuente.
- El chispazo al desenchufar aparatos: sin fuente buena.
- Henrio / Joseph Henry: solo Wikipedia; no se usa.
- NFC a 13,56 MHz en "tu celular": la fuente es de etiquetas ST25; no se usa.

## E. Para el animador
- Pila **AA 1,5 V**, interruptor de cuchilla, bobina grande con núcleo de hierro, neón NE-2 en paralelo con la bobina.
- Rótulos permitidos: "PILA 1,5 V", "NEÓN: HASTA ~90 V", "SE OPONE AL CAMBIO", "VOLTAJE INDUCIDO (EN CONTRA)", "ANALOGÍA", "EXISTEN DE 1,6 × 0,8 mm", "BOBINA DE LA BASE / BOBINA DEL CELULAR", "U = ½·L·I²".
