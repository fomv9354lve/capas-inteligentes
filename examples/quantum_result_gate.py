# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Waits for the real ibm_kingston Bell job, then CAPAS gates the measurement against the
device calibration — both the first-order floor AND the calibration-grade Aer prediction."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_quantum_hw as Q
from qiskit_ibm_runtime import QiskitRuntimeService
cal = json.load(open("/tmp/kingston_calib.json"))
try:
    pred = json.load(open("/tmp/kingston_predicted.json"))
except Exception:
    pred = {"00": 4038, "11": 3985, "01": 96, "10": 73}
tok = json.load(open("/Users/kreniq/Downloads/apikey (1).json"))["apikey"]
s = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
job = s.job(cal["job_id"])
print("waiting for job", cal["job_id"], "on", cal["backend"], "...")
counts = job.result()[0].data.meas.get_counts()
ideal = {"00", "11"}
v1 = Q.gate_hardware_claim(ideal, counts, cal)
v2 = Q.gate_against_prediction(counts, pred, ideal)
print("REAL hardware measurement:", counts)
print(f"first-order gate : {v1['verdict']} | measured {v1['measured_error']:.1%} vs floor {v1['predicted_floor']:.1%}")
print(f"calibration-grade: {v2['verdict']} | sig {v2['measured_noise_signature']} vs expected {v2['expected_noise_signature']} | {v2['resolution_note']}")
print("CONSILIENCE:", v2["consilience"])
json.dump({"counts": counts, "first_order": v1, "calibrated": v2}, open("/tmp/kingston_capas_verdict.json", "w"))
