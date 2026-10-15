# Réplica OpenAI — registro de ejecución

**Completo: listo para que Claude puntúe.**

Actualizado: 2026-10-15T13:28:57-06:00. Este registro contiene ejecución y validación estructural; no contiene puntuaciones ni análisis de decisiones.

Modelo por defecto confirmado en las cabeceras: `gpt-6-astra`, proveedor `openai`, razonamiento `xhigh`. El CLI no reporta un snapshot/versionado fechado del modelo. Versión del cliente: `codex-cli 0.162.1`. Cada intento usa un `codex exec` nuevo con el prompt original y `--sandbox workspace-write -C .`; no se usa resume ni fork. El supervisor añade `PYTHONDONTWRITEBYTECODE=1`.

## Corridas vigentes

Todas las horas llevan offset `-06:00` (America/Monterrey); wall es tiempo de proceso medido por el supervisor.

| Corrida | Intento | Inicio | Fin | Wall (s) | Tokens CLI | Herramientas / shell | Líneas JSON válidas |
|---|---:|---|---|---:|---:|---:|---:|
| CA1 | 2 | 2026-10-15T13:03:40-06:00 | 2026-10-15T13:07:49-06:00 | 248.872 | 82,731 | 13 / 12 | 50 |
| CA2 | 2 | 2026-10-15T13:03:40-06:00 | 2026-10-15T13:07:12-06:00 | 211.72 | 114,606 | 19 / 17 | 50 |
| CB1 | 3 | 2026-10-15T13:17:51-06:00 | 2026-10-15T13:28:40-06:00 | 648.54 | 144,763 | 57 / 101 | 50 |
| CB2 | 1 | 2026-10-15T13:04:39-06:00 | 2026-10-15T13:14:07-06:00 | 568.222 | 124,838 | 40 / 103 | 50 |

Herramientas = invocaciones superiores registradas en la traza de sesión; shell = comandos `exec` visibles en el log. Una invocación superior puede agrupar varias herramientas. `tokens CLI` reproduce el contador `tokens used`, sin confundirlo con el total acumulado que incluye entrada cacheada.

| Archivo | Líneas | JSON inválidos | Identificadores y orden exactos |
|---|---:|---:|---|
| [arm_A/decisions_CA1.jsonl](arm_A/decisions_CA1.jsonl) | 50 | 0 | C001–C050: PASS |
| [arm_A/decisions_CA2.jsonl](arm_A/decisions_CA2.jsonl) | 50 | 0 | C051–C100: PASS |
| [arm_B/decisions_CB1.jsonl](arm_B/decisions_CB1.jsonl) | 50 | 0 | C001–C050: PASS |
| [arm_B/decisions_CB2.jsonl](arm_B/decisions_CB2.jsonl) | 50 | 0 | C051–C100: PASS |

## Intentos descartados y reinicios

| Corrida / intento | Inicio | Fin | Wall (s) | Tokens CLI | Herramientas / shell | Motivo |
|---|---|---|---:|---:|---:|---|
| CA1 / 1 | 2026-10-15T13:03:29-06:00 | 2026-10-15T13:03:30-06:00 | 1.011 | not reported | 0 / 0 | CLI no pudo inicializar app-server dentro del sandbox exterior; exit 1. |
| CA2 / 1 | 2026-10-15T13:03:29-06:00 | 2026-10-15T13:03:30-06:00 | 1.011 | not reported | 0 / 0 | CLI no pudo inicializar app-server dentro del sandbox exterior; exit 1. |
| CB1 / 1 | 2026-10-15T13:04:39-06:00 | 2026-10-15T13:13:40-06:00 | 541.059 | 135,290 | 33 / 101 | 50 líneas; línea 28 JSON inválido. Original conservado sin reparar. |
| CB1 / 2 | 2026-10-15T13:14:42-06:00 | 2026-10-15T13:17:23-06:00 | 160.644 | 28,027 | 8 / 2 | 0 casos: pidió aclarar uso de JavaScript solo para leer archivos y terminó. |

CA1/CA2 se reiniciaron solo después del fallo de arranque. El entorno aprobó iniciar el CLI fuera del sandbox exterior; cada proceso hijo mantuvo su sandbox `workspace-write`. CB1 se repitió con contexto nuevo y el mismo prompt por los fallos descritos; no hubo correcciones manuales de sus decisiones. Los intentos y sus métricas están preservados en [rejected_attempts/CB1_attempt1/](rejected_attempts/CB1_attempt1/) y [rejected_attempts/CB1_attempt2/](rejected_attempts/CB1_attempt2/).

## Llamadas CAPAS e incidencias

- CB1 vigente: 50 llamadas `--case`, 50 casos únicos; repeticiones: {}; casos faltantes: 0; casos fuera de rango: 0.
- CB2 vigente: 51 llamadas `--case`, 50 casos únicos; repeticiones: {"C054": 2}; casos faltantes: 0; casos fuera de rango: 0.
- CB1 descartado, intento 1: 50 llamadas de 50 casos; intento 2: 0 llamadas `--case`. Las 50 llamadas descartadas y una copia íntegra del log compartido anterior al reinicio están archivadas. El log activo [arm_B/calls.jsonl](arm_B/calls.jsonl) conserva CB2 y el intento vigente de CB1; la partición preservó los bytes de cada línea.
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
| CB1 vigente | 4,431,181 | 4,316,416 | 29,998 | 4,461,179 |
| CB2 vigente | 2,756,271 | 2,659,840 | 28,407 | 2,784,678 |
| CB1_attempt1 | 2,260,219 | 2,152,576 | 27,647 | 2,287,866 |
| CB1_attempt2 | 319,578 | 292,992 | 1,441 | 321,019 |

## Evidencia y alcance

Métricas, identificadores de sesión, hashes de decisiones y comprobación de integridad de prompts/protocolo/motor: [run_summary.json](run_summary.json). Tiempos y códigos de salida: `metadata_*_attempt*.json`. Logs originales: `run_*.log`; las corridas reiniciadas usan sufijos `_attempt2` / `_attempt3`.

La [validación estructural](validation.json) comprueba 50 objetos JSON estrictos por archivo, campos/tipos requeridos y los case_id exactos en orden. No comprueba aciertos, citas, audit_hash ni efectos de CAPAS: eso queda para Claude. Las coincidencias de fuentes excluidas en las llamadas de herramientas están registradas para revisión; no constituyen una prueba absoluta de ausencia de acceso. No se leyó el oráculo ni la corrida de Claude. No hubo commit, push ni deploy.
