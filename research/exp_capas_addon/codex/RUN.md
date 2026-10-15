# Réplica OpenAI — registro de ejecución

**Listo para que Claude puntúe: CB1 es el intento 1 y conserva la línea 28 malformada.**

Actualizado: 2026-10-15T13:34:50-06:00. Este registro contiene ejecución y validación estructural; no contiene puntuaciones ni análisis de decisiones.

**Corrección de selección.** Antes de recibir la aclaración del usuario, el orquestador repitió CB1 por una fila inválida y presentó el intento 3 como vigente. La regla sellada indicada por el usuario exige conservar una fila ausente o malformada como peor caso (error y bloqueo), sin sustituir la muestra por otra corrida. Por ello se restituyó el intento 1 íntegro en `arm_B/decisions_CB1.jsonl`, junto con sus llamadas originales. La línea 28 permanece sin reparar: `Expecting ',' delimiter`, columna 96. Los intentos 2 y 3 se conservan fuera de la muestra. Esta corrección sustituye la selección y las afirmaciones de validez total de los reportes anteriores; los originales se preservan como historial. El puntuador lo ejecuta Claude, no el orquestador.

Selección explícita y regla de repetición en [SCORING_SELECTION.json](SCORING_SELECTION.json): solo repetir si falta la mayoría de los casos o falla el proceso; conservar e identificar todos los intentos. No se lanzó una nueva corrida tras esta instrucción.

Modelo por defecto confirmado en las cabeceras: `gpt-6-astra`, proveedor `openai`, razonamiento `xhigh`. El CLI no reporta un snapshot/versionado fechado del modelo. Versión del cliente: `codex-cli 0.162.1`. Cada intento usa un `codex exec` nuevo con el prompt original y `--sandbox workspace-write -C .`; no se usa resume ni fork. El supervisor añade `PYTHONDONTWRITEBYTECODE=1`.

## Corridas vigentes

Todas las horas llevan offset `-06:00` (America/Monterrey); wall es tiempo de proceso medido por el supervisor.

| Corrida | Intento | Inicio | Fin | Wall (s) | Tokens CLI | Herramientas / shell | Líneas JSON válidas |
|---|---:|---|---|---:|---:|---:|---:|
| CA1 | 2 | 2026-10-15T13:03:40-06:00 | 2026-10-15T13:07:49-06:00 | 248.872 | 82,731 | 13 / 12 | 50 |
| CA2 | 2 | 2026-10-15T13:03:40-06:00 | 2026-10-15T13:07:12-06:00 | 211.72 | 114,606 | 19 / 17 | 50 |
| CB1 | 1 | 2026-10-15T13:04:39-06:00 | 2026-10-15T13:13:40-06:00 | 541.059 | 135,290 | 33 / 101 | 49 |
| CB2 | 1 | 2026-10-15T13:04:39-06:00 | 2026-10-15T13:14:07-06:00 | 568.222 | 124,838 | 40 / 103 | 50 |

Herramientas = invocaciones superiores registradas en la traza de sesión; shell = comandos `exec` visibles en el log. Una invocación superior puede agrupar varias herramientas. `tokens CLI` reproduce el contador `tokens used`, sin confundirlo con el total acumulado que incluye entrada cacheada.

| Archivo | Líneas | JSON inválidos | Identificadores y orden exactos |
|---|---:|---:|---|
| [arm_A/decisions_CA1.jsonl](arm_A/decisions_CA1.jsonl) | 50 | 0 | C001–C050: PASS |
| [arm_A/decisions_CA2.jsonl](arm_A/decisions_CA2.jsonl) | 50 | 0 | C051–C100: PASS |
| [arm_B/decisions_CB1.jsonl](arm_B/decisions_CB1.jsonl) | 50 | 1 | C001–C050: 49 objetos parseados en su posición; línea 28 malformada, se conserva para el puntuador |
| [arm_B/decisions_CB2.jsonl](arm_B/decisions_CB2.jsonl) | 50 | 0 | C051–C100: PASS |

CB1 tiene 50 líneas físicas y 49 objetos JSON válidos. La comprobación estructural registra ese fallo; la muestra sigue lista para el puntuador bajo la regla declarada. No se afirma que los cuatro archivos sean íntegramente JSON válido.

## Arranques fallidos y repeticiones fuera de la muestra

| Corrida / intento | Inicio | Fin | Wall (s) | Tokens CLI | Herramientas / shell | Motivo |
|---|---|---|---:|---:|---:|---|
| CA1 / 1 | 2026-10-15T13:03:29-06:00 | 2026-10-15T13:03:30-06:00 | 1.011 | not reported | 0 / 0 | CLI no pudo inicializar app-server dentro del sandbox exterior; exit 1. |
| CA2 / 1 | 2026-10-15T13:03:29-06:00 | 2026-10-15T13:03:30-06:00 | 1.011 | not reported | 0 / 0 | CLI no pudo inicializar app-server dentro del sandbox exterior; exit 1. |
| CB1 / 2 | 2026-10-15T13:14:42-06:00 | 2026-10-15T13:17:23-06:00 | 160.644 | 28,027 | 8 / 2 | 0 casos: pidió aclarar uso de JavaScript solo para leer archivos y terminó. |
| CB1 / 3 | 2026-10-15T13:17:51-06:00 | 2026-10-15T13:28:40-06:00 | 648.54 | 144,763 | 57 / 101 | 50 líneas válidas; repetición del original por su fila malformada, excluida de la muestra. |

CA1/CA2 se reiniciaron solo después del fallo de arranque. El entorno aprobó iniciar el CLI fuera del sandbox exterior; cada proceso hijo mantuvo su sandbox `workspace-write`. Las dos repeticiones de CB1 ya habían ocurrido antes de recibir la aclaración del usuario. No hubo correcciones manuales de decisiones. El intento 2 está en [rejected_attempts/CB1_attempt2/](rejected_attempts/CB1_attempt2/) y el intento 3 en [excluded_attempts/CB1_attempt3/](excluded_attempts/CB1_attempt3/). El nombre histórico `rejected_attempts/CB1_attempt1/` se conserva, pero su contenido es el original ahora seleccionado, idéntico byte por byte al archivo activo; CURRENT_ROLE.md aclara ese cambio de estado.

## Paquetes para sensibilidad, sin sustituir el primario

Por instrucción posterior de Claude, los reintentos quedan disponibles en [arm_B/retry/](arm_B/retry/), con índice y hashes en [ATTEMPTS.json](arm_B/retry/ATTEMPTS.json). Ninguno reemplaza el intento 1 ni repara la línea 28.

- Intento 2 real: [decisions_CB1_try2.jsonl](arm_B/retry/decisions_CB1_try2.jsonl) y su propio [calls.jsonl](arm_B/retry/calls.jsonl), ambos vacíos: terminó sin casos y sin llamadas `--case`. El agente no emitió archivo de decisiones; estos archivos vacíos se crearon al empaquetar para representar explícitamente esa ausencia de salida.
- Intento 3 real: [decisions_CB1_try3.jsonl](arm_B/retry/try3/decisions_CB1_try3.jsonl), 50 líneas, y [calls.jsonl propio](arm_B/retry/try3/calls.jsonl), 50 llamadas. Copias byte por byte del intento preservado, identificado como tercero para evitar atribuírselo al segundo.

## Llamadas CAPAS e incidencias

- CB1 vigente: 50 llamadas `--case`, 50 casos únicos; repeticiones: {}; casos faltantes: 0; casos fuera de rango: 0.
- CB2 vigente: 51 llamadas `--case`, 50 casos únicos; repeticiones: {"C054": 2}; casos faltantes: 0; casos fuera de rango: 0.
- CB1 fuera de la muestra: intento 2, 0 llamadas `--case`; intento 3, 50 llamadas de 50 casos, archivadas junto con sus decisiones. El log activo [arm_B/calls.jsonl](arm_B/calls.jsonl) se restauró byte por byte desde el log anterior a la primera repetición: incluye las 50 llamadas del intento 1 de CB1 y las 51 de CB2. El log sustituido también está preservado.
- Antes de B, se detectó que `capas_call.py` escribía fuera del carril Codex. Claude corrigió únicamente el destino para agentes con prefijo `C`, a `codex/arm_B/calls.jsonl`; se verificó la corrección antes de lanzar B. CAPAS y la forma de respuesta del helper no se editaron por esta sesión.
- Los rechazos iniciales fueron del sandbox exterior (`Operation not permitted` al inicializar app-server). No se observan estados shell no cero ni fallos MCP en las corridas de modelo registradas. Un veredicto de CAPAS no se clasifica aquí como fallo de ejecución.
- Hubo salidas truncadas al descubrir herramientas. Los avisos por corrida quedan en `run_summary.json` y en los snapshots archivados. No se cambiaron los prompts para corregirlos.
- En las llamadas revisadas no se detectaron lecturas explícitas de fuentes excluidas ni lecturas de archivos de los agentes fuera de `cases/`. Los comandos shell de B fueron exclusivamente los dos tipos de llamada CAPAS permitidos. El helper accede al motor y a los payloads temporales como establece el protocolo. Los hashes de `capas.py`, el protocolo y los cuatro prompts coinciden entre preflight y cierre.

## Contadores acumulados de las trazas

Estos son los contadores brutos reportados por Codex; la entrada cacheada está incluida en entrada y total, no se suma otra vez.

| Corrida | Entrada | Entrada cacheada | Salida | Total acumulado |
|---|---:|---:|---:|---:|
| CA1 vigente | 552,282 | 481,408 | 11,857 | 564,139 |
| CA2 vigente | 950,804 | 848,128 | 11,930 | 962,734 |
| CB1 vigente | 2,260,219 | 2,152,576 | 27,647 | 2,287,866 |
| CB2 vigente | 2,756,271 | 2,659,840 | 28,407 | 2,784,678 |
| CB1_attempt2 | 319,578 | 292,992 | 1,441 | 321,019 |
| CB1_attempt3 | 4,431,181 | 4,316,416 | 29,998 | 4,461,179 |

## Evidencia y alcance

Métricas, identificadores de sesión, hashes de decisiones y comprobación de integridad de prompts/protocolo/motor: [run_summary.json](run_summary.json), que distingue intento seleccionado, procesos terminados, validez estructural y disponibilidad para puntuación. Tiempos y códigos de salida: `metadata_*_attempt*.json`. Logs originales: `run_*.log`; las corridas reiniciadas usan sufijos `_attempt2` / `_attempt3`.

La [validación estructural](validation.json) registra 50 líneas por archivo, errores JSON, campos/tipos de filas parseables y posiciones de case_id. CB1 falla JSON estricto en la línea 28; las otras tres corridas pasan. No comprueba aciertos, citas, audit_hash ni efectos de CAPAS: eso queda para Claude. Las coincidencias de fuentes excluidas en las llamadas de herramientas están registradas para revisión; no constituyen una prueba absoluta de ausencia de acceso. No se leyó el oráculo ni la corrida de Claude. No hubo commit, push ni deploy.
