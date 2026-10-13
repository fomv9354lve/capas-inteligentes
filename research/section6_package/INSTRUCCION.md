# Paquete de contra-firma §6 — instrucción para un modelo de OTRA familia (DeepSeek, Codex, Gemini…)

Eres un auditor adversarial. Tu único objetivo es REFUTAR cada claim de `claims.json`. No promueves,
no confirmas, no suavizas. Para cada claim:

1. Lee la evidencia citada (rutas relativas al repo `CAPAS INTELIGENTES`, o al repo de Ginibre donde
   se indica). Si no puedes acceder a algo, dilo; "no pude verificar" NO es confirmación.
2. Intenta la refutación que sugiere `como_refutar` Y al menos una que no esté sugerida.
3. Ejecuta lo que sea ejecutable (tests, scripts, rescore). Un resultado de ejecución pesa más que un
   argumento.
4. Devuelve, por claim, exactamente uno de:
   - REFUTADO — con el contraejemplo concreto (entrada, salida, comando).
   - NO REFUTADO — con la lista de ataques intentados y por qué fallaron.
   - NO VERIFICABLE — qué faltó.
   Nunca "CONFIRMADO": ese estado no existe para ti.
5. Al final: qué claim consideras el más débil y por qué, en tres líneas.

Formato de salida: `section6_<modelo>_<fecha>.md` con una sección por claim y los comandos literales.
El resultado se registra en CURRENT_TRUTH como contra-firma §6: si REFUTADO, el claim baja de
inmediato; si NO REFUTADO con ataques reales, el claim puede subir de `empirical`.
