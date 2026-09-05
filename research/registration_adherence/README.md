# Registration adherence — Fase 0 (2026-09-04)

Prueba de viabilidad de un gate determinista sobre adherencia registro↔publicación.
**Veredicto: HOLD.** El sustrato es mejor de lo que dice la literatura; la validación
contra juicio humano no es concluyente, y sé exactamente por qué.

## Lo que funciona

`/api/int/studies/{NCT}/history` devuelve, estructurado y en una llamada:
`originalData.primaryOutcomes` (los outcomes primarios tal como se registraron),
`lastUpdateVersions` y los `moduleLabels` de cada versión.

Esto importa: el paper de `cthist` y la documentación pública sostienen que el
historial **solo se obtiene raspando la web**. No es así. Sobre n=500 ensayos
completados con resultados, **93,4%** son recuperables de forma completamente
determinista; el único fallo son 33 ensayos con outcomes no estructurados.

## Lo que no funciona

Comparar títulos de outcome por igualdad marca el **78,6%** de los ensayos. La
literatura sitúa el switching real en ~31,7%. La diferencia es ruido: el título se
reescribe de forma rutinaria al publicar resultados —"KOOS4" pasa a "Change in KOOS4
from baseline"— sin que cambie nada sustantivo.

Contra el ground truth de COMPare (68 ensayos evaluados a mano en NEJM, JAMA, Lancet,
BMJ y Annals; 51 cruzables por NCT, 41 decidibles):

| variante | sensibilidad | VPP |
|---|---|---|
| solo determinista | 0,89 | 0,24 |
| + umbral de solapamiento léxico | 0,33 | 0,43 |
| + mapeo semántico (LLM propone, motor dispone) | 0,33 | 0,43 |

**El mapeo semántico cuidadoso no superó al heurístico léxico crudo.** Mismo punto de
la curva.

## Por qué, y por qué invalida la comparación

Los falsos negativos lo dicen: COMPare etiqueta **2/4**, **1/2**, **1/3** outcomes
primarios correctamente reportados. Su medida es *cuántos outcomes registrados
aparecen bien reportados en el paper*. Un ensayo con el registro intacto falla igual
si el paper omite un outcome o lo reporta sin el análisis preespecificado.

Este pipeline solo observa mutación del registro. **Nunca lee el paper.** Son
fenómenos solapados —8 de 9 positivos humanos sí tocaron el registro— pero no el
mismo. Las cifras de arriba no son una validación del método: son la medida de un
proxy contra otro objetivo.

## Qué se puede afirmar y qué no

**Se puede:** "la definición de los outcomes primarios en el registro cambió tras el
inicio del estudio en N% de los ensayos", con N derivado deterministamente y
re-ejecutable. Requiere antes una definición que excluya la reformulación al publicar
resultados — no hecha.

**No se puede:** ninguna afirmación sobre tasa de outcome switching, ni sobre fidelidad
del reporte. Eso exige el texto del paper, que este pipeline no toca.

## Reproducir

```bash
python3 research/registration_adherence/phase0.py 500 out.json   # barrido
python3 research/registration_adherence/validate.py val.json     # vs COMPare
```

`data/compare_gt.csv` procede de la hoja pública que alimenta compare-trials.org
(clave `1EgNcKJ_p4v7P0JNq5GSElKGvDX88z8QZN52n8C-yQAc`).

## Siguiente paso si esto continúa

El cuello de botella no es el mapeo semántico, es el **acceso al texto del paper**.
Sin él no hay adherencia que gatear, solo cambios de registro. Antes de escribir más
código: decidir si ese texto es obtenible a escala y de forma legal.
