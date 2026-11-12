# Cap. 11 · El motor DC — verificación (regla de exactitud)

Cada frase del guion sale de un código M#. HECHO = respaldado por fuentes; ANALOGÍA = simplificación que no dice nada falso; PENDIENTE = no entra al video.

| Código | Afirmación | Estado | Respaldo |
|---|---|---|---|
| M1 | Un motor DC convierte energía eléctrica en movimiento. Por dentro (motor de juguete de imán permanente) tiene una bobina (rotor/armadura) entre imanes, más conmutador y escobillas. | HECHO | ScienceReady "Operation of a Simple DC Motor"; StudyPulse "Simple DC Motors" (componentes: alimentación DC + bobina + conmutador + campo + escobillas). |
| M2 | Un alambre con corriente dentro de un campo magnético recibe una fuerza (F = I·L × B), perpendicular a la corriente y al campo. | HECHO | iwant2study (MOE Singapur) "DC Motor 3D Virtual Lab": F = (I × B)L en cada lado activo; ScienceReady (motor effect). "Empujón" = fuerza (ANALOGÍA de palabra, sin error). |
| M3 | En la espira los dos lados llevan corriente en sentidos opuestos, así que las fuerzas van en sentidos opuestos (uno arriba, otro abajo con el campo horizontal) y forman un par que la hace girar. | HECHO | iwant2study: "the forces on the two vertical coil sides form a turning couple"; ScienceReady (torque τ = (w/2)·F por lado). |
| M4 | Sin conmutador (con anillos colectores) la bobina oscila y se queda quieta en la posición derecha (perpendicular al campo). El conmutador de anillo partido invierte la corriente en la bobina cada media vuelta, así el par siempre empuja hacia el mismo lado y el giro es continuo. | HECHO | HyperPhysics "Commutator and Brushes on DC Motor"; StudyPulse (slip rings → oscila y se para en la vertical); Wikipedia "Commutator (electric)" (apoyo). |
| M5 | Si se invierte solo la polaridad de la pila, el motor gira al revés. | HECHO | iwant2study: "Reverse only the supply polarity and the motor reverses." |
| M6 | (Reto) Si se invierten la pila Y los imanes, vuelve a girar en el sentido original. | HECHO | iwant2study: "Swap only the magnets and it reverses again. Reverse both and the original turning direction returns." Respuesta: gira hacia el MISMO lado que al principio. |
| M7 | Muchos controles de videojuego vibran con un motor DC con una masa descentrada (ERM): al girar, la masa desbalanceada sacude todo. No todos: algunos usan actuadores lineales; por eso se dice "en muchos". | HECHO | Makeability Lab (U. Washington) "Lesson 4: Vibromotors" (ERM en celulares y controles); patentes US 6693622 (motor DC con masa excéntrica en un gamepad) y US 6268671. |
| M8 | Si se gira un motor DC con la mano, funciona como generador y da voltaje (campo que cambia en la bobina → voltaje, cap. 8). El molino del cap. 2 usaba un motor DC como generador. | HECHO | Vedantu / Wikipedia "Commutator": el mismo conmutador hace de rectificador en el generador DC; cap. 2 del canal (molino eólico con motor DC). |

| M9 | (Dato extra del primer comentario) El 3 de septiembre de 1821 Faraday hizo girar un alambre con corriente alrededor de un imán, en un recipiente con mercurio ("rotaciones electromagnéticas"); la Royal Institution lo llama el primer motor eléctrico. | HECHO | Royal Institution "The birth of electric motion" y ficha del aparato de 1822 (rigb.org); Nature Physics editorial "Round and round it goes" (2021). |

## Lo que se dejó por fuera (PENDIENTE o innecesario)
- Fuerza contraelectromotriz y por qué el motor consume más al arrancar: cierto, pero no cabe bien en 75 s.
- Motores sin escobillas (brushless) de drones y ventiladores de PC: otro capítulo.
- "Velocidad proporcional al voltaje": solo aproximado y en vacío; no se dice.
