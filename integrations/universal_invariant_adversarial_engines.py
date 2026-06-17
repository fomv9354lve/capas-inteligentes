from __future__ import annotations

import numpy as np


PAULI_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
PAULI_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
PAULI_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)


def _swap_two_qubits() -> np.ndarray:
    swap = np.zeros((4, 4), dtype=complex)
    for a in range(2):
        for b in range(2):
            src = 2 * a + b
            dst = 2 * b + a
            swap[dst, src] = 1.0
    return swap


def _heisenberg_dimer_hamiltonian(j_coupling: float, *, sign: float) -> np.ndarray:
    return sign * j_coupling * (
        np.kron(PAULI_X, PAULI_X)
        + np.kron(PAULI_Y, PAULI_Y)
        + np.kron(PAULI_Z, PAULI_Z)
    ) / 4.0


def _local_property_tests(hamiltonian: np.ndarray) -> dict[str, bool]:
    swap = _swap_two_qubits()
    spectrum = np.linalg.eigvalsh(hamiltonian)
    return {
        "hermitian": bool(np.allclose(hamiltonian, hamiltonian.conj().T)),
        "trace_zero": bool(np.isclose(np.trace(hamiltonian), 0.0)),
        "real_spectrum": bool(np.allclose(spectrum.imag, 0.0)),
        "exchange_symmetric": bool(np.allclose(swap @ hamiltonian @ swap, hamiltonian)),
        "finite_entries": bool(np.all(np.isfinite(hamiltonian))),
    }


def heisenberg_wrong_sign_passes_local_properties(j_coupling: float = 1.0) -> dict:
    """Minimal adversarial case for universal-invariant verification.

    Intended system: antiferromagnetic spin-1/2 Heisenberg dimer,
    H = J S1.S2, with exact singlet ground energy -3J/4.

    Generator bug: wrong global sign, producing the ferromagnetic dimer. Generic
    local property tests still pass, but the analytic physical invariant fails.
    """

    generated_hamiltonian = _heisenberg_dimer_hamiltonian(j_coupling, sign=-1.0)
    local_tests = _local_property_tests(generated_hamiltonian)
    local_tests_pass = all(local_tests.values())

    value = float(np.linalg.eigvalsh(generated_hamiltonian)[0])
    expected = float(-3.0 * j_coupling / 4.0)
    abs_error = abs(value - expected)
    universal_anchor_pass = bool(abs_error < 1e-12)

    return {
        "observable": "Generated Heisenberg dimer ground-state energy with wrong coupling sign",
        "value": value,
        "expected": expected,
        "abs_error": abs_error,
        "units": "energy",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": (
            "Universal analytic invariant for antiferromagnetic H = J S1.S2 "
            "requires E0 = -3J/4; the generated Hamiltonian uses the wrong sign."
        ),
        "benchmark_family": "Heisenberg",
        "reference_truth": "closed_form_antiferromagnetic_singlet_ground_energy",
        "verification_independence": "analytic_no_solver",
        "coverage_case": "universal_invariant_adversarial_failure",
        "local_property_tests": local_tests,
        "local_property_tests_pass": local_tests_pass,
        "local_oracle_caught": False,
        "universal_anchor": "E0_antiferromagnetic_heisenberg_dimer=-3J/4",
        "universal_anchor_pass": universal_anchor_pass,
        "invariant_caught": bool(local_tests_pass and not universal_anchor_pass),
        "generator_error": "wrong_coupling_sign",
        "structure_mapping": {
            "generator_output": "Hamiltonian implementation",
            "local_oracle_relation": "generic matrix properties preserved by sign flip",
            "universal_oracle_relation": "model-specific singlet/triplet spectrum invariant",
            "preserved_relation": "same generated object judged by both local properties and independent physics",
        },
        "pre_registered_success_criterion": (
            "local_property_tests_pass is true and universal_anchor_pass is false"
        ),
        "claim_scope": (
            "minimal falsation case only; shows an analytic physical invariant can catch "
            "a generator error missed by local property tests"
        ),
    }
