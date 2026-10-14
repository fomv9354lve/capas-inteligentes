# Ronda 2 — México / redes latinoamericanas

**Verdicto: AGREE WITH CONDITIONS.**

## (a) Líneas rojas

Ninguna cruzada. Las tres entraron: la fórmula "satisface mecánicamente la cláusula de investigación de P3" (vocabulario, primer bloque), la red fundada por personas e instituciones con CAPAS como una entrada del catálogo (Posicionamiento), y "detector de fraude" prohibido. El 37 %/94 % queda SCOPED (A4).

## (b) El cambio que sigo exigiendo

"La red, no Krenn·IQ, corre el siguiente lote sellado" está en la sección *sin ingeniería* y por tanto sin test. Una red que no existe el día 90 no corre nada; mientras tanto A7 publicará lotes corridos por la misma casa que escribió el motor y el replayer (A1 lo exige "de otra sesión", pero de la misma empresa: §6 intramuros). Pido que pase a ledger: cada reporte de lote (A7) y cada `verification_budget` (A2) llevan `sealed_by` y `run_by` con institución; cuando ambos son Krenn·IQ la página dice *self-run* al lado de la tasa, y la palabra *independiente* se reserva al primer lote cuyo `run_by` sea una institución miembro (CIMAT o UNAM, con `capas_check.py` ejecutado allá y su hash en la entrada). Es la versión mecánica de los comités de validación ciegos de BRI. Corolario: si CAPAS-Bench quiere que la red corra el lote, el corpus sellado no puede quedar privado para la red; privado para el público hasta el paper, abierto bajo acuerdo para la institución que corre.

## (c) Dónde me equivoqué

Mantuve la diferencia paper-vs-prerregistro como regla "barata" diciendo que era "justo lo que invalidó 53 réplicas en BRI". El metacientífico tiene razón: esas 53 las invalidaron comités humanos leyendo protocolos, y el propio repo (Phase 0, `research/registration_adherence`) midió el diff de texto en sensibilidad 0,89 / PPV 0,24. Confundí la invalidación humana con una regla mecánica. La versión correcta es la de A5: diff a nivel de campo entre el esqueleto del `prereg` y el payload de resultados; la prosa es territorio asesor de metacheck, no de CAPAS. También acepto la corrección del evaluador: cité "1/1 malo no-ACCEPT" sin su cuota de HOLD; con `hold_share` al lado, como ahora manda el plan.
