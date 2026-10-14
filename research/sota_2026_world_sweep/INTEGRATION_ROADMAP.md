# Hoja de ruta de integración — CAPAS sobre hombros de gigantes (adoptada por el consejo, 2026-10-14)

Para Osvaldo. Lo largo está en `council/PLAN_v3.md` (en inglés, con quién pidió cada cosa), los créditos en
`GIANTS.md`, el camino institucional en `GFRN_HOW_TO_JOIN.md`, y la evidencia país por país en `wave_*.md`.

## Qué pasó
Ocho perspectivas (metrología alemana, metaciencia holandesa-brasileña-húngara, métodos formales israelí-suizos,
evaluación de IA británica-estadounidense, regulación farmacéutica, verificación por reglas china, benchmarking
cuántico y política científica mexicana) criticaron el plan de cinco acciones, cada una leyendo los informes del
barrido y el código real. Dos rondas. Resultado: ocho de ocho de acuerdo, cero en contra, con condiciones que se
integraron todas. Lo que se tomó de cada uno está marcado en el plan.

## Lo que me corrigieron, y acepto
1. **Nuestra métrica ciega tiene un hueco.** "Malos no aceptados / buenos no rechazados" la supera un motor que diga
   siempre HOLD. Desde ahora toda tasa va con la proporción de HOLD y la tasa informativa al lado.
2. **"El instrumento está prerregistrado" era media verdad.** El motor sí; el codificador no. Desde el siguiente lote,
   dos codificadores ciegos independientes, concordancia por campo publicada, desacuerdo en campo obligatorio → HOLD.
3. **El hash de auditoría no es un certificado todavía.** No lleva commit del motor ni traza de reglas, y el test que lo
   "re-deriva" importa el motor. Hasta que un verificador independiente re-ejecute los veredictos sellados sin el motor,
   ninguna página lo llama certificado.
4. **El "diff contra prerregistro" en prosa no es barato.** Nuestro propio repo lo midió: sensibilidad 0,89, valor
   predictivo 0,24. Se hace a nivel de campos, no de texto.
5. **El 37 % contra 94 % de PNAS mide reproducción, no juicio.** Se cita como contexto; no se usa como prior.
6. **Vocabulario:** sha256 es integridad, firma es autenticidad; nunca "firmado" por un hash. Chapultepec: "satisface
   mecánicamente la cláusula de investigación", nunca "cumple" ni "avalado por".

## Las siete acciones, en orden (90 días)
| Días | Acción | Qué la cierra |
|---|---|---|
| 0–30 | **Certificado re-verificable** (primero por unanimidad): el veredicto lleva tag y commit del motor, traza ordenada de reglas con id y versión, hashes de entradas, hash de la tabla de reglas. Un verificador aparte, `capas_check.py`, escrito por una sesión que no escribió el motor y sin importarlo, re-ejecuta los veredictos sellados en CI. | CI con trazas mutadas que el verificador debe rechazar todas; entrada de ledger cerrada antes de llamar "certificado" a nada |
| 0–30 | HOLD share, tasa informativa, conteo de exclusiones y regla de puntuación junto a cada tasa ciega (plantilla de la Iniciativa Brasileña) | `score_sealed.py` y las páginas los muestran; guardia de redacción |
| 30–45 | **Presupuesto de verificación por lote**: cuántos campos se leyeron de un archivo con hash, cuántos se declararon, cuántos se derivaron, por nivel de admisión; quién selló y quién corrió ("self-run" si fuimos nosotros) | sellado dentro del manifiesto antes de abrir desenlaces; el release falla sin la entrada |
| 45–60 | **Procedencia dentro del motor** (hash que no cuadra → HOLD en el veredicto, no solo en el runner); paquetes RO-Crate; procedencia del calibrador (humano, automático, modelo); campos de incertidumbre con banda de guarda, solo cuando la incertidumbre está declarada; campo obligatorio de **declaración de uso de IA** (herramienta, propósito, fase) | tests por adaptador; guardar la descarga cruda de IBM en el próximo job de Atlas |
| 60–75 | **Reglas de los gigantes**: DOI retractado como campo con hash y fecha → HOLD (nunca consulta en vivo; ausente → HOLD); adherencia al prerregistro por campos → REWRITE; recomputar p desde el estadístico declarado (statcheck); "qué lo habría tirado" en cada ACCEPT; reporte retroactivo de X1–X5 marcado dentro de muestra; protocolo de **dos codificadores** con la red | costo de cada regla medido en X1–X5 y declarado dentro de muestra |
| 75–90 | Adaptador de informe de validación farmacéutico (tipo Pinnacle 21: rechazo técnico antes de cualquier estadística); **prerregistro de CAPAS contra un LLM-juez** cofirmado por un modelo de otra empresa antes de sellar, con umbral de paso/fallo prefijado sobre la cota superior del falso-accept, brazos del juez con permutaciones y "llave maestra", hash del verificador sellado junto al tag | corre en el siguiente lote sellado (≥ 20 malos y 20 buenos; "grado piloto" si hay menos de 40) |
| > 90 | Certificados de calibración PTB (cuando alguien los emita), importación de prerregistros OSF, campos de física de VERaiPHY, normalizadores de equivalencia para REWRITE, propagación de retracciones en el ledger, CAPAS-Bench con el corpus de Atlas | — |

## Cómo integramos lo de afuera reconociéndolo
- Cada regla nueva nombra a su gigante en la guía de codificación y en la página "In depth" (`GIANTS.md` es la
  fuente). Nada se presenta como invención propia cuando es herencia.
- Lo que sí es propio, y se dice así: la composición con autoaplicación. Instrumento prerregistrado, tasa ciega con
  fuga declarada, ledger de números propios, contra-firma por otra familia, ingesta de máquina atada a un veredicto
  fail-closed. Nadie lo tiene junto; el barrido lo confirma país por país.

## Cómo nos volvemos referente (sin que la herramienta capture nada)
1. **Red Mexicana de Reproducibilidad**, fundada por investigadores de al menos tres instituciones (UNAM, CIMAT,
   Cinvestav, IPN; REMERI/CUDI como aliado), con los estatutos brasileños de plantilla. Tú entras como investigador
   fundador, no como proveedor. Primer paso: escribir a la UKRN preguntando quién ya trabaja en esto en México.
2. **La red corre el siguiente lote sellado, no Krenn·IQ.** "Independiente" se reserva para el primer lote que una
   institución miembro ejecute con el verificador por su cuenta. Hasta entonces, nuestras tasas dicen "self-run".
3. **Federación Global**: admite redes, por consenso, cuando cumplen la descripción de red y no hay riesgo de captura.
   CAPAS entra al catálogo de la red como herramienta abierta, igual que statcheck en Países Bajos.
4. **Taller NeurIPS 2026 "Verificación en la era de los científicos de IA"** (12 de diciembre): enviar el protocolo
   sellado con el verificador independiente.
5. **CAPAS-Bench**: el corpus sellado de Atlas y los lotes futuros, con puntuador sin dependencias, invitando a los
   autores del verificador-modelo chino a correrlo. El corpus Ginibre sigue privado hasta que el paper sea público.

## Decisiones tuyas
- Autorizar que el corpus sellado se abra bajo acuerdo a la institución que corra el lote independiente.
- Elegir qué institución y qué dos codificadores arrancan la red.
- Fecha para que una sesión distinta de la que escribió el motor escriba `capas_check.py` (regla constructor ≠ verificador).
