# Verificación técnica · Cap. 6 · Memoria del celular (almacenamiento + RAM)

Regla: no se pierde la física ni la química y nada falso. Cada afirmación del guion sale de esta tabla.
Tipos: **HECHO** (verificado en fuente), **ANALOGÍA** (se dice como analogía), **PENDIENTE** (no usar hasta verificar).
Actualizada el 2 nov 2026 con el informe de investigación (papers, patentes, JEDEC y fabricantes).

## ⚠️ Correcciones a lo que se había dicho
1. **Compuerta flotante vs. trampa de carga.** El modelo clásico es la compuerta flotante (polisilicio, conductor). En la 3D NAND actual casi todos usan **trampa de carga**: una capa de nitruro de silicio (aislante). → El guion dice "una capa encerrada entre aislantes", que es cierto para los dos.
2. **Micron ya no usa compuerta flotante** en su NAND nueva: pasó a trampa de carga en 2020, con la NAND de 176 capas (comunicado de Micron, 9-nov-2020). Su NAND de 96 capas sí era de compuerta flotante. La versión anterior de esta tabla decía lo contrario.
3. **Borrado en trampa de carga:** no "salen los electrones por túnel" como en la compuerta flotante; se **inyectan huecos** que neutralizan la carga atrapada (Goda, Micron, *Electronics* 2021). → El guion no explica cómo se borra por dentro.
4. **Transistor del cap. 1:** era bipolar (colector/base/emisor). La celda flash es un MOSFET. → El guion no dice "como el del capítulo uno".

## A. Almacenamiento (flash NAND)
| # | Afirmación | Tipo | Fuente |
|---|---|---|---|
| A1 | El almacenamiento del celular es memoria flash NAND con un controlador (eMMC o UFS); tiene miles de millones de celdas | HECHO | Micron UFS product brief; Micron FMS 2016 |
| A2 | Cada celda es un transistor MOSFET con una capa aislada (entre la compuerta de control y el silicio) que guarda carga | HECHO | Hyperstone "What is NAND Flash"; Cai et al. arXiv 1706.08642 |
| A3 | La mayoría de la 3D NAND actual usa trampa de carga (nitruro de silicio, aislante); la compuerta flotante es el modelo clásico | HECHO | TechTarget; AnandTech "3D NAND: How It Works"; Goda 2021 |
| A4 | Al programar, los electrones entran a la capa por efecto túnel (Fowler–Nordheim) a través del óxido túnel; en trampa de carga es un FN "modificado" | HECHO | Cai et al. 1706.08642 sec. 3.4; patente US 5999452; Goda 2021 |
| A5 | El óxido túnel es muy delgado para que haya campos eléctricos suficientes sin voltajes excesivos | HECHO | Patente US 6266275 |
| A6 | Programar = meter electrones (bit 0 en la forma simple, SLC). Borrado = todo en 1 (0xFF). Se lee y escribe por **páginas** (~16 KB) y se borra por **bloques** (de varios MB a decenas de MB) | HECHO | Hyperstone; Cai et al. 2017 (Proc. IEEE); SanDisk "Flash 101"; hoja de datos Frontgrade UT81NDQ512G8T (bloque ≈ 36 MB) |
| A7 | Voltajes: la programación usa pulsos que empiezan en ~16 V y suben hasta más de 20 V; el borrado usa ~20 V. Los generan bombas de carga dentro del chip a partir de ~2,5–3,3 V | HECHO (orden de magnitud) | Patentes US 7952929, US 8000152, US 11521988, US 12348132; Ishida/Takeuchi ISSCC 2009; JEDEC JESD230D |
| A8 | Para leer, se mide a qué voltaje empieza a conducir el transistor (voltaje umbral); la carga atrapada lo cambia | HECHO | Cai et al. 1706.08642 |
| A9 | SLC/MLC/TLC/QLC = 1/2/3/4 bits por celda = 2/4/8/16 niveles | HECHO | Rossmann Group; Dell QLC (una fuente dice 14 para QLC: error, 2⁴ = 16) |
| A10 | Se programa con pulsos que suben un poco el voltaje y se verifica tras cada pulso (ISPP) | HECHO | Cai et al. 1706.08642; patente US 7952929 |
| A11 | Más bits por celda = márgenes más estrechos, escritura más lenta y menos durabilidad | HECHO | Rossmann; AnandTech "Understanding TLC NAND" |
| A12 | Cada ciclo de programar/borrar daña un poco el óxido túnel; por eso la celda tiene vida limitada | HECHO | Cai et al.; patente US 9164836; IEEE TechNav |
| A13 | La carga se fuga muy despacio (túnel asistido por trampas); empeora con calor y desgaste | HECHO | Cai et al. 1711.11427; Oldham NASA NEPP |
| A14 | El controlador reparte las escrituras (wear leveling) y corrige errores (ECC) | HECHO | Rossmann; IEEE TechNav; Micron |
| A15 | Es no volátil: la carga queda rodeada de aislante y no necesita energía para quedarse | HECHO | Hyperstone; patente US 6266275 |
| A16 | Una página no se puede reescribir directo: el dato nuevo va a otra página, la vieja se marca inválida y el bloque se borra después (recolección de basura) | HECHO | Cai et al. 2017; SanDisk "Flash 101" |
| A17 | La NAND actual apila alrededor de 300 capas (Samsung 286, SK hynix 321, Kioxia 332 en muestras); Samsung ya produce más de 400 | HECHO (cifras cambian; poner "a 2026") | SK hynix newsroom (nov-2024); Samsung (2024 y blog técnico 2026); TrendForce. *No usado en el guion.* |
| A18 | En trampa de carga, el borrado se hace sobre todo inyectando huecos que neutralizan los electrones | HECHO | Goda (Micron), *Electronics* 2021, 10, 3156. *No usado en el guion.* |
| A19 | JEDEC JESD218 (SSD de consumo) exige ≥1 año de retención sin energía a 30 °C **al final de la vida útil**; una celda casi nueva retiene mucho más (Kioxia estima ~10 años con <100 ciclos) | HECHO, con matiz: es norma de SSD, no de celular | JEDEC JESD218B; nota de fiabilidad Kioxia. *No usado en el guion.* |

## B. RAM (DRAM)
| # | Afirmación | Tipo | Fuente |
|---|---|---|---|
| B16 | La RAM del celular es DRAM de bajo consumo (LPDDR) | HECHO | Micron FMS 2016; hojas de datos Micron LPDDR5 |
| B17 | Cada celda DRAM = 1 transistor + 1 condensador; el bit es la carga del condensador | HECHO | halbleiter.org "DRAM cell"; Wikipedia DRAM |
| B18 | El condensador es diminuto (unos pocos femtofaradios) | HECHO | halbleiter.org |
| B19 | La carga se fuga; JEDEC pide refrescar cada fila cada 64 ms o menos | HECHO | Wikipedia DRAM; halbleiter.org; patente US 6940773 |
| B20 | Es volátil: sin energía se pierden los datos en poco tiempo | HECHO | Wikipedia DRAM |
| B21 | SRAM usa ~6 transistores por bit; más rápida pero ocupa más | HECHO | halbleiter.org |
| B22 | La RAM responde en decenas de nanosegundos (LPDDR5 tRCD = 18 ns); leer una página NAND tarda decenas de microsegundos → unas **mil veces** más | HECHO | JEDEC Mobile Forum 2024; Park et al. arXiv 2104.09611; Samsung V-NAND 6.ª gen.; VLDB (Suzuki) |
| B23 | Android deja las apps abiertas en la RAM ("la RAM libre es RAM desperdiciada") y solo las cierra si falta memoria; cerrarlas obliga a un arranque en frío | HECHO | Android Developers "Memory overview" y "Memory management"; blog Android Developers 2026 |

## C. Analogías (decirlas como analogía)
| # | Analogía | Límite que hay que aclarar |
|---|---|---|
| C22 | Celda flash ≈ condensador | No es un condensador de placas: es la compuerta de un transistor. **No usada en el guion** |
| C23 | DRAM ≈ cubeta que gotea | Sí hay un condensador real; es la más fiel |
| C24 | Efecto túnel ≈ pasar a través de una pared | No la rompe ni salta por encima; es mecánica cuántica con óxido muy delgado y campo fuerte. **El guion lo aclara** |
| C25 | RAM = escritorio; almacenamiento = archivero | La diferencia de velocidad es de unas mil veces, y el escritorio se vacía al apagar. **El guion lo dice** |
| C26 | Bomba de carga = escalera que sube el voltaje | No crea energía: sube el voltaje a costa de corriente, en pulsos cortos |
| C27 | Programar niveles = llenar un vaso hasta una marca, por escalones | Se llena con electrones por túnel, no con un flujo continuo; con el tiempo baja un poco |

## D. PENDIENTE (no usar)
- Norma JEDEC de retención propia de UFS/eMMC de celular: no encontrada.
- Valores numéricos de JESD47: no se pudo leer la norma.
- Latencia total de lectura aleatoria de UFS 4.x medida en un teléfono: solo hay blogs.
- Qué NAND, cuántas capas o qué tipo de celda tiene un celular concreto: depende del modelo.

## Crédito
Tema pedido por @Liguitoo_oficial (cap. 4 y cap. 5). Mencionar con @ en la descripción y el primer comentario.
