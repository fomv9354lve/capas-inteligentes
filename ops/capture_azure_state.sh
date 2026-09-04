#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
#
# Vuelca el estado completo de un resource group antes de recrear nada.
# Los secretos de Container Apps son de solo escritura: esto captura sus NOMBRES,
# no sus valores. Reponer los valores es trabajo manual — ver §7 del spec.
set -euo pipefail

RG="${1:-capas-rg}"
ENV_NAME="${2:-capas-env}"
OUT="$(cd "$(dirname "$0")" && pwd)/azure_state"
mkdir -p "$OUT"

echo "capturando $RG -> $OUT"

az containerapp list -g "$RG" --query "[].name" -o tsv > "$OUT/apps.txt"

while read -r a; do
  [ -z "$a" ] && continue
  echo "  app: $a"
  az containerapp show -n "$a" -g "$RG" -o json          > "$OUT/app-$a.json"
  python3 "$(dirname "$0")/redact_capture.py" "$OUT/app-$a.json"
  az containerapp secret list -n "$a" -g "$RG" -o json    > "$OUT/secrets-$a.json"
  # `az containerapp secret list` imprime stdout VACÍO (no `[]`) cuando la app no tiene
  # secretos. Un fichero de 0 bytes es indistinguible de una escritura fallida, que es
  # justo lo que el validador debe atrapar. Normalizamos aquí, en la captura, para no
  # tener que ablandar el validador.
  [ -s "$OUT/secrets-$a.json" ] || echo "[]" > "$OUT/secrets-$a.json"
  pid=$(az containerapp show -n "$a" -g "$RG" --query "identity.principalId" -o tsv)
  if [ -n "$pid" ] && [ "$pid" != "None" ]; then
    az role assignment list --assignee "$pid" --all -o json > "$OUT/roles-$a.json"
  else
    echo "[]" > "$OUT/roles-$a.json"
  fi
done < "$OUT/apps.txt"

az containerapp env show -n "$ENV_NAME" -g "$RG" -o json             > "$OUT/env-$ENV_NAME.json"
az containerapp env certificate list -n "$ENV_NAME" -g "$RG" -o json > "$OUT/certs-$ENV_NAME.json"
az resource list -g "$RG" -o json                                    > "$OUT/resources.json"

echo "listo. valida con: python3 ops/verify_capture.py"
