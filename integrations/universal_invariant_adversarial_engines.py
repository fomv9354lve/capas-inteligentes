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


def _state_local_property_tests(state: np.ndarray) -> dict[str, bool]:
    norm = np.vdot(state, state).real
    return {
        "normalized": bool(np.isclose(norm, 1.0)),
        "finite_entries": bool(np.all(np.isfinite(state))),
        "valid_dimension_two_qubits": bool(state.shape == (4,)),
        "nonzero_state": bool(norm > 0.0),
    }


def _bell_entropy(state: np.ndarray) -> float:
    psi = state.reshape(2, 2)
    rho_a = psi @ psi.conj().T
    eigs = np.linalg.eigvalsh(rho_a)
    eigs = eigs[eigs > 1e-15]
    return float(-np.sum(eigs * np.log(eigs)))


def _matrix_adversarial_payload(
    *,
    observable: str,
    hamiltonian: np.ndarray,
    expected: float,
    universal_anchor: str,
    generator_error: str,
    physical_evidence_detail: str,
    pre_registered_success_criterion: str,
    claim_scope: str,
    coverage_case: str,
    local_oracle_caught: bool | None = None,
) -> dict:
    local_tests = _local_property_tests(hamiltonian)
    local_tests_pass = all(local_tests.values())
    caught_by_local = (not local_tests_pass) if local_oracle_caught is None else local_oracle_caught
    if local_tests["finite_entries"] and local_tests["hermitian"]:
        value = float(np.linalg.eigvalsh(hamiltonian)[0])
        abs_error = abs(value - expected)
        universal_anchor_pass: bool | str = bool(abs_error < 1e-12)
        invariant_caught: bool | str = bool(not universal_anchor_pass)
    else:
        value = "not_evaluated_local_oracle_failed"
        abs_error = "not_evaluated_local_oracle_failed"
        universal_anchor_pass = "not_evaluated_local_oracle_failed"
        invariant_caught = False

    return {
        "observable": observable,
        "value": value,
        "expected": expected,
        "abs_error": abs_error,
        "units": "energy",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": physical_evidence_detail,
        "benchmark_family": "Heisenberg",
        "reference_truth": "closed_form_antiferromagnetic_singlet_ground_energy",
        "verification_independence": "analytic_no_solver",
        "coverage_case": coverage_case,
        "local_property_tests": local_tests,
        "local_property_tests_pass": local_tests_pass,
        "local_oracle_caught": bool(caught_by_local),
        "universal_anchor": universal_anchor,
        "universal_anchor_pass": universal_anchor_pass,
        "invariant_caught": invariant_caught,
        "generator_error": generator_error,
        "structure_mapping": {
            "generator_output": "Hamiltonian implementation",
            "local_oracle_relation": "generic matrix validity properties",
            "universal_oracle_relation": "model-specific singlet/triplet spectrum invariant",
            "preserved_relation": "same generated object judged by local properties and independent physics",
        },
        "pre_registered_success_criterion": pre_registered_success_criterion,
        "claim_scope": claim_scope,
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


def heisenberg_nonhermitian_local_catches_anchor_not_needed(j_coupling: float = 1.0) -> dict:
    """Negative control: local matrix oracle catches the generated artifact first."""

    generated_hamiltonian = _heisenberg_dimer_hamiltonian(j_coupling, sign=1.0).copy()
    generated_hamiltonian[0, 1] += 0.2
    expected = float(-3.0 * j_coupling / 4.0)
    return _matrix_adversarial_payload(
        observable="Generated Heisenberg dimer Hamiltonian with non-Hermitian perturbation",
        hamiltonian=generated_hamiltonian,
        expected=expected,
        universal_anchor="E0_antiferromagnetic_heisenberg_dimer=-3J/4",
        generator_error="nonhermitian_matrix_entry",
        physical_evidence_detail=(
            "Negative control: the local matrix oracle catches non-Hermiticity before "
            "the analytic ground-state invariant is needed."
        ),
        pre_registered_success_criterion=(
            "local_property_tests_pass is false and universal_anchor_pass is not_evaluated_local_oracle_failed"
        ),
        claim_scope=(
            "negative control only; shows some generator errors are already caught by local properties "
            "and do not support a universal-anchor advantage claim"
        ),
        coverage_case="universal_invariant_local_catches_anchor_not_needed",
    )


def heisenberg_scaled_coupling_both_oracles_catch(j_coupling: float = 1.0) -> dict:
    """Redundant detection: local parameter oracle and analytic invariant both fail."""

    generated_coupling = 0.5 * j_coupling
    generated_hamiltonian = _heisenberg_dimer_hamiltonian(generated_coupling, sign=1.0)
    local_tests = _local_property_tests(generated_hamiltonian)
    local_tests["declared_coupling_matches_expected"] = bool(np.isclose(generated_coupling, j_coupling))
    local_tests_pass = all(local_tests.values())
    expected = float(-3.0 * j_coupling / 4.0)
    value = float(np.linalg.eigvalsh(generated_hamiltonian)[0])
    abs_error = abs(value - expected)
    universal_anchor_pass = bool(abs_error < 1e-12)
    return {
        "observable": "Generated Heisenberg dimer ground-state energy with scaled coupling",
        "value": value,
        "expected": expected,
        "abs_error": abs_error,
        "units": "energy",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": (
            "Redundant control: a wrong coupling parameter is caught by a local parameter "
            "check and by the analytic ground-state invariant."
        ),
        "benchmark_family": "Heisenberg",
        "reference_truth": "closed_form_antiferromagnetic_singlet_ground_energy",
        "verification_independence": "analytic_no_solver",
        "coverage_case": "universal_invariant_both_oracles_catch",
        "local_property_tests": local_tests,
        "local_property_tests_pass": local_tests_pass,
        "local_oracle_caught": bool(not local_tests_pass),
        "universal_anchor": "E0_antiferromagnetic_heisenberg_dimer=-3J/4",
        "universal_anchor_pass": universal_anchor_pass,
        "invariant_caught": bool(not universal_anchor_pass),
        "generator_error": "wrong_coupling_magnitude",
        "structure_mapping": {
            "generator_output": "Hamiltonian implementation with declared coupling",
            "local_oracle_relation": "declared parameter consistency plus generic matrix validity",
            "universal_oracle_relation": "model-specific singlet/triplet spectrum invariant",
            "preserved_relation": "same generated object judged by local parameter checks and independent physics",
        },
        "pre_registered_success_criterion": (
            "local_property_tests_pass is false and universal_anchor_pass is false"
        ),
        "claim_scope": (
            "redundant-control case only; shows the local oracle and universal anchor can overlap"
        ),
    }


def bell_product_state_passes_local_properties_but_fails_entropy() -> dict:
    """Transfer case: valid two-qubit state fails the Bell entanglement invariant."""

    generated_state = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    local_tests = _state_local_property_tests(generated_state)
    local_tests_pass = all(local_tests.values())
    value = _bell_entropy(generated_state)
    expected = float(np.log(2.0))
    abs_error = abs(value - expected)
    universal_anchor_pass = bool(abs_error < 1e-12)
    return {
        "observable": "Generated two-qubit Bell-state entropy from plausible product state",
        "value": value,
        "expected": expected,
        "abs_error": abs_error,
        "units": "nats",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": (
            "Transfer case: the generated state is normalized and dimensionally valid, "
            "but the Bell-state invariant requires single-qubit entropy ln2."
        ),
        "benchmark_family": "Bell",
        "reference_truth": "closed_form_bell_entropy_ln2",
        "verification_independence": "analytic_no_solver",
        "coverage_case": "universal_invariant_non_heisenberg_adversarial_failure",
        "local_property_tests": local_tests,
        "local_property_tests_pass": local_tests_pass,
        "local_oracle_caught": False,
        "universal_anchor": "S_Bell_reduced_state=ln2",
        "universal_anchor_pass": universal_anchor_pass,
        "invariant_caught": bool(local_tests_pass and not universal_anchor_pass),
        "generator_error": "plausible_product_state_instead_of_bell_state",
        "structure_mapping": {
            "generator_output": "two-qubit state vector",
            "local_oracle_relation": "generic state validity properties preserved by product state",
            "universal_oracle_relation": "Bell entanglement entropy invariant",
            "preserved_relation": "same generated state judged by local validity and independent entanglement invariant",
        },
        "pre_registered_success_criterion": (
            "local_property_tests_pass is true and universal_anchor_pass is false"
        ),
        "claim_scope": (
            "transfer seed only; shows the local-miss/universal-catch pattern for an entropy invariant, "
            "not just a Heisenberg energy invariant"
        ),
    }


def normalized_random_state_without_universal_anchor(seed: int = 32) -> dict:
    """No-anchor control: valid generated state with no claimed universal invariant."""

    rng = np.random.default_rng(seed)
    generated_state = rng.normal(size=4) + 1j * rng.normal(size=4)
    generated_state = generated_state / np.linalg.norm(generated_state)
    local_tests = _state_local_property_tests(generated_state)
    local_tests_pass = all(local_tests.values())
    value = _bell_entropy(generated_state)
    return {
        "observable": "Generated normalized two-qubit state entropy without a universal target",
        "value": value,
        "expected": "not_applicable_no_universal_anchor",
        "abs_error": "not_applicable_no_universal_anchor",
        "units": "nats",
        "physical_evidence_level": "no_universal_anchor_control",
        "physical_evidence_detail": (
            "No-anchor control: the state is locally valid, but no universal reference is claimed "
            "for this arbitrary generated state."
        ),
        "benchmark_family": "NoUniversalAnchorControl",
        "reference_truth": "none",
        "verification_independence": "none",
        "coverage_case": "universal_invariant_no_anchor_control",
        "local_property_tests": local_tests,
        "local_property_tests_pass": local_tests_pass,
        "local_oracle_caught": bool(not local_tests_pass),
        "universal_anchor": "not_applicable_no_universal_anchor",
        "universal_anchor_pass": "not_applicable_no_universal_anchor",
        "invariant_caught": False,
        "generator_error": "none_declared",
        "structure_mapping": {
            "generator_output": "arbitrary normalized two-qubit state",
            "local_oracle_relation": "generic state validity properties",
            "universal_oracle_relation": "none claimed",
            "preserved_relation": "CAPAS records absence of an anchor instead of inventing evidence",
        },
        "pre_registered_success_criterion": (
            "local_property_tests_pass is true and universal_anchor_pass is not_applicable_no_universal_anchor"
        ),
        "claim_scope": (
            "no-anchor control only; shows CAPAS can seal local validity while refusing a universal-invariant claim"
        ),
    }
