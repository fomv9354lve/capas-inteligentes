# Reintentos CB1: solo sensibilidad

El primario es el intento 1: `../decisions_CB1.jsonl`, con la línea 28 malformada intacta. Estos archivos no lo sustituyen ni reparan.

- Intento 2 real: `decisions_CB1_try2.jsonl` y `calls.jsonl`, ambos vacíos. Terminó con 0 casos y 0 llamadas --case; no emitió un archivo de decisiones. Los archivos vacíos son una representación explícita de esa ausencia de salida, creada al empaquetar. Metadatos: `metadata_CB1_attempt2.json`.
- Intento 3 real: `try3/decisions_CB1_try3.jsonl` (50 líneas) y `try3/calls.jsonl` (50 llamadas propias), copiados byte por byte del archivo preservado. Se mantiene el número 3 para no confundirlo con el intento 2. Metadatos: `try3/metadata_CB1_attempt3.json`.

Índice y hashes: `ATTEMPTS.json`. Las trazas completas originales siguen en `../../run_CB1_attempt2.log` y `../../run_CB1_attempt3.log`. No se han ejecutado nuevas corridas ni puntuaciones para este empaquetado.
