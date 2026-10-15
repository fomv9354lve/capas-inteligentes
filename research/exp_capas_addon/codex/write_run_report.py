"""Render process metrics only; does not inspect case content or score outcomes."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def n(value):
    return f"{value:,}" if isinstance(value, int) else "not reported" if value is None else str(value)


def main():
    summary = json.loads((HERE / "run_summary.json").read_text())
    records = summary["runs"]
    archived = []
    for directory in sorted((HERE / "rejected_attempts").glob("CB1_attempt*")):
        snapshot = json.loads((directory / "run_summary_before_retry.json").read_text())
        archived.append((directory.name, snapshot["runs"]["CB1"]))
    done = summary["all_complete"]
    out = ["# Réplica OpenAI — registro de ejecución", "",
           "**Completo: listo para que Claude puntúe.**" if done else "**En curso: todavía no está listo para puntuar.**", "",
           f"Actualizado: {summary['generated_at']}. Este registro contiene ejecución y validación estructural; no contiene puntuaciones ni análisis de decisiones.", "",
           "Modelo por defecto confirmado en las cabeceras: `gpt-6-astra`, proveedor `openai`, razonamiento `xhigh`. "
           "El CLI no reporta un snapshot/versionado fechado del modelo. Versión del cliente: `codex-cli 0.162.1`. "
           "Cada intento usa un `codex exec` nuevo con el prompt original y `--sandbox workspace-write -C .`; no se usa resume ni fork. "
           "El supervisor añade `PYTHONDONTWRITEBYTECODE=1`.", "",
           "## Corridas vigentes", "",
           "Todas las horas llevan offset `-06:00` (America/Monterrey); wall es tiempo de proceso medido por el supervisor.", "",
           "| Corrida | Intento | Inicio | Fin | Wall (s) | Tokens CLI | Herramientas / shell | Líneas JSON válidas |",
           "|---|---:|---|---|---:|---:|---:|---:|"]
    for arm, record in records.items():
        attempt = record["attempts"][-1]
        valid = record["validation"]["lines"] - len(record["validation"]["invalid_json_lines"])
        out.append(f"| {arm} | {attempt['attempt']} | {attempt['start']} | {attempt['end'] or 'en curso'} | "
                   f"{attempt['wall_seconds'] if attempt['wall_seconds'] is not None else 'en curso'} | {n(record['cli_tokens_used'])} | "
                   f"{sum(record['top_level_tool_calls'].values())} / {record['shell_exec_calls']} | {valid} |")
    out += ["", "Herramientas = invocaciones superiores registradas en la traza de sesión; shell = comandos `exec` visibles en el log. "
            "Una invocación superior puede agrupar varias herramientas. `tokens CLI` reproduce el contador `tokens used`, "
            "sin confundirlo con el total acumulado que incluye entrada cacheada.", "",
            "| Archivo | Líneas | JSON inválidos | Identificadores y orden exactos |",
            "|---|---:|---:|---|"]
    for arm, record in records.items():
        valid = record["validation"]
        span = "C001–C050" if arm.endswith("1") else "C051–C100"
        out.append(f"| [{valid['path']}]({valid['path']}) | {valid['lines']} | {len(valid['invalid_json_lines'])} | "
                   f"{span}: {'PASS' if valid['case_ids_exact_order'] else 'pendiente/FAIL'} |")
    out += ["", "## Intentos descartados y reinicios", "",
            "| Corrida / intento | Inicio | Fin | Wall (s) | Tokens CLI | Herramientas / shell | Motivo |",
            "|---|---|---|---:|---:|---:|---|"]
    for arm in ("CA1", "CA2"):
        attempt = records[arm]["attempts"][0]
        out.append(f"| {arm} / 1 | {attempt['start']} | {attempt['end']} | {attempt['wall_seconds']} | not reported | 0 / 0 | "
                   "CLI no pudo inicializar app-server dentro del sandbox exterior; exit 1. |")
    for name, record in archived:
        attempt = record["attempts"][-1]
        reason = ("50 líneas; línea 28 JSON inválido. Original conservado sin reparar."
                  if attempt["attempt"] == 1 else "0 casos: pidió aclarar uso de JavaScript solo para leer archivos y terminó.")
        out.append(f"| CB1 / {attempt['attempt']} | {attempt['start']} | {attempt['end']} | {attempt['wall_seconds']} | "
                   f"{n(record['cli_tokens_used'])} | {sum(record['top_level_tool_calls'].values())} / {record['shell_exec_calls']} | {reason} |")
    out += ["", "CA1/CA2 se reiniciaron solo después del fallo de arranque. El entorno aprobó iniciar el CLI fuera del sandbox exterior; "
            "cada proceso hijo mantuvo su sandbox `workspace-write`. CB1 se repitió con contexto nuevo y el mismo prompt por los fallos descritos; "
            "no hubo correcciones manuales de sus decisiones. Los intentos y sus métricas están preservados en "
            "[rejected_attempts/CB1_attempt1/](rejected_attempts/CB1_attempt1/) y [rejected_attempts/CB1_attempt2/](rejected_attempts/CB1_attempt2/).", "",
            "## Llamadas CAPAS e incidencias", ""]
    for arm in ("CB1", "CB2"):
        calls = records[arm]["capas_calls"]
        out.append(f"- {arm} vigente: {calls['total']} llamadas `--case`, {calls['unique_cases']} casos únicos; "
                   f"repeticiones: {json.dumps(calls['repeated_ids'], ensure_ascii=False)}; "
                   f"casos faltantes: {len(calls['missing_expected_ids'])}; casos fuera de rango: {len(calls['extra_ids'])}.")
    out += ["- CB1 descartado, intento 1: 50 llamadas de 50 casos; intento 2: 0 llamadas `--case`. "
            "Las 50 llamadas descartadas y una copia íntegra del log compartido anterior al reinicio están archivadas. "
            "El log activo [arm_B/calls.jsonl](arm_B/calls.jsonl) conserva CB2 y el intento vigente de CB1; la partición preservó los bytes de cada línea.",
            "- Antes de B, se detectó que `capas_call.py` escribía fuera del carril Codex. Claude corrigió únicamente el destino "
            "para agentes con prefijo `C`, a `codex/arm_B/calls.jsonl`; se verificó la corrección antes de lanzar B. "
            "CAPAS y la forma de respuesta del helper no se editaron por esta sesión.",
            "- Los rechazos iniciales fueron del sandbox exterior (`Operation not permitted` al inicializar app-server). "
            "No se observan estados shell no cero ni fallos MCP en las corridas de modelo registradas. "
            "Un veredicto de CAPAS no se clasifica aquí como fallo de ejecución.",
            "- Hubo salidas truncadas al descubrir herramientas. Los avisos por corrida quedan en `run_summary.json` y en los snapshots archivados. "
            "No se cambiaron los prompts para corregirlos.",
            "- En las llamadas revisadas no se detectaron lecturas explícitas de fuentes excluidas ni lecturas de archivos de los agentes fuera de `cases/`. "
            "Los comandos shell de B fueron exclusivamente los dos tipos de llamada CAPAS permitidos. "
            "El helper accede al motor y a los payloads temporales como establece el protocolo. "
            "Los hashes de `capas.py`, el protocolo y los cuatro prompts coinciden entre preflight y cierre.", "",
            "## Contadores acumulados de las trazas", "",
            "Estos son los contadores brutos reportados por Codex; la entrada cacheada está incluida en entrada y total, no se suma otra vez.", "",
            "| Corrida | Entrada | Entrada cacheada | Salida | Total acumulado |",
            "|---|---:|---:|---:|---:|"]
    all_records = [(arm+" vigente", record) for arm,record in records.items()] + archived
    for label, record in all_records:
        usage = record["cumulative_token_usage"] or {}
        out.append(f"| {label} | {n(usage.get('input_tokens'))} | {n(usage.get('cached_input_tokens'))} | "
                   f"{n(usage.get('output_tokens'))} | {n(usage.get('total_tokens'))} |")
    out += ["", "## Evidencia y alcance", "",
            "Métricas, identificadores de sesión, hashes de decisiones y comprobación de integridad de prompts/protocolo/motor: "
            "[run_summary.json](run_summary.json). Tiempos y códigos de salida: `metadata_*_attempt*.json`. "
            "Logs originales: `run_*.log`; las corridas reiniciadas usan sufijos `_attempt2` / `_attempt3`.", "",
            "La [validación estructural](validation.json) comprueba 50 objetos JSON estrictos por archivo, campos/tipos requeridos y los case_id exactos en orden. "
            "No comprueba aciertos, citas, audit_hash ni efectos de CAPAS: eso queda para Claude. "
            "Las coincidencias de fuentes excluidas en las llamadas de herramientas están registradas para revisión; "
            "no constituyen una prueba absoluta de ausencia de acceso. No se leyó el oráculo ni la corrida de Claude. "
            "No hubo commit, push ni deploy.", ""]
    (HERE / "RUN.md").write_text("\n".join(out))
    print("RUN.md actualizado; completo:", done)


if __name__ == "__main__":
    main()
