#!/usr/bin/env bash
# Publish CAPAS to PyPI. Run:  TWINE_PASSWORD=<your-pypi-token> ./publish.sh
set -euo pipefail
python3 -m build --no-isolation --outdir dist
python3 -m twine check dist/capas_claim_gate-0.4.0*
TWINE_USERNAME=__token__ python3 -m twine upload dist/capas_claim_gate-0.4.0*
echo "Published. Verify:  pip install capas-claim-gate"
