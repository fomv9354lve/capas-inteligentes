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


def _scaling_local_property_tests(system_sizes: np.ndarray, gaps: np.ndarray) -> dict[str, bool]:
    return {
        "finite_sizes_strictly_increasing": bool(np.all(np.diff(system_sizes) > 0)),
        "gaps_positive": bool(np.all(gaps > 0.0)),
        "gaps_finite": bool(np.all(np.isfinite(gaps))),
        "gaps_strictly_decreasing": bool(np.all(np.diff(gaps) < 0.0)),
    }


def _fit_gap_exponent(system_sizes: np.ndarray, gaps: np.ndarray) -> tuple[float, float]:
    x = np.log(system_sizes)
    y = np.log(gaps)
    slope, intercept = np.polyfit(x, y, 1)
    predicted = slope * x + intercept
    residual = y - predicted
    total = y - np.mean(y)
    r_squared = 1.0 - float(np.sum(residual**2) / np.sum(total**2))
    return float(-slope), r_squared


def _scaling_points_from_agent_table(agent_table: list[dict[str, float]]) -> tuple[np.ndarray, np.ndarray]:
    sizes = np.array([row["system_size"] for row in agent_table], dtype=float)
    gaps = np.array([row["gap"] for row in agent_table], dtype=float)
    return sizes, gaps


def _ising_scaling_payload(
    *,
    observable: str,
    gaps: np.ndarray,
    generator_error: str,
    coverage_case: str,
    physical_evidence_detail: str,
    pre_registered_success_criterion: str,
    claim_scope: str,
    system_sizes: np.ndarray | None = None,
    finite_size_notes: str | None = None,
) -> dict:
    sizes = np.array([8, 12, 16, 24, 32, 48], dtype=float) if system_sizes is None else system_sizes
    expected_exponent = 1.0
    exponent_tolerance = 0.10
    local_tests = _scaling_local_property_tests(sizes, gaps)
    local_tests_pass = all(local_tests.values())
    if local_tests_pass:
        fitted_exponent, r_squared = _fit_gap_exponent(sizes, gaps)
        abs_error: float | str = abs(fitted_exponent - expected_exponent)
        universal_anchor_pass: bool | str = bool(abs_error <= exponent_tolerance)
        invariant_caught: bool | str = bool(not universal_anchor_pass)
        value: float | str = fitted_exponent
    else:
        fitted_exponent = "not_evaluated_local_oracle_failed"
        r_squared = "not_evaluated_local_oracle_failed"
        abs_error = "not_evaluated_local_oracle_failed"
        universal_anchor_pass = "not_evaluated_local_oracle_failed"
        invariant_caught = False
        value = "not_evaluated_local_oracle_failed"

    return {
        "observable": observable,
        "value": value,
        "expected": expected_exponent,
        "abs_error": abs_error,
        "units": "dynamic_exponent_z",
        "physical_evidence_level": "scaling_law_anchor",
        "physical_evidence_detail": physical_evidence_detail,
        "benchmark_family": "CriticalIsingFiniteSizeScaling",
        "reference_truth": "critical_ising_gap_dynamic_exponent_z_equals_1",
        "verification_independence": "theory_scaling_law_no_solver",
        "coverage_case": coverage_case,
        "local_property_tests": local_tests,
        "local_property_tests_pass": local_tests_pass,
        "local_oracle_caught": bool(not local_tests_pass),
        "universal_anchor": "critical_ising_gap_delta_L_scales_as_L^-1",
        "universal_anchor_pass": universal_anchor_pass,
        "invariant_caught": invariant_caught,
        "generator_error": generator_error,
        "anchor_kind": "absolute_scaling_law",
        "anchor_mode": "absolute_anchor",
        "scaling_points": [
            {"system_size": int(size), "gap": float(gap)}
            for size, gap in zip(sizes, gaps, strict=True)
        ],
        "fitted_exponent": fitted_exponent,
        "expected_exponent": expected_exponent,
        "exponent_tolerance": exponent_tolerance,
        "fit_r_squared": r_squared,
        "finite_size_notes": finite_size_notes or (
            "Synthetic finite-size scaling trace. The preregistered decision is based "
            "on the fitted exponent z within +/-0.10 of the Ising critical value z=1."
        ),
        "structure_mapping": {
            "generator_output": "finite-size gap sequence",
            "local_oracle_relation": "positive finite gaps decrease with increasing system size",
            "universal_oracle_relation": "critical Ising dynamic exponent z=1",
            "preserved_relation": "same gap sequence judged by local monotonicity and universal scaling exponent",
        },
        "pre_registered_success_criterion": pre_registered_success_criterion,
        "claim_scope": claim_scope,
    }


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
        "anchor_mode": "absolute_anchor",
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
        "anchor_mode": "absolute_anchor",
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
        "anchor_mode": "absolute_anchor",
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
        "anchor_mode": "absolute_anchor",
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
        "anchor_mode": "none",
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


def _kron_all(operators: list[np.ndarray]) -> np.ndarray:
    result = np.array([[1.0]], dtype=complex)
    for operator in operators:
        result = np.kron(result, operator)
    return result


def _single_site_operator(operator: np.ndarray, site: int, n_sites: int) -> np.ndarray:
    identity = np.eye(2, dtype=complex)
    return _kron_all([operator if index == site else identity for index in range(n_sites)])


def _two_site_operator(
    first_operator: np.ndarray,
    first_site: int,
    second_operator: np.ndarray,
    second_site: int,
    n_sites: int,
) -> np.ndarray:
    identity = np.eye(2, dtype=complex)
    operators = []
    for index in range(n_sites):
        if index == first_site:
            operators.append(first_operator)
        elif index == second_site:
            operators.append(second_operator)
        else:
            operators.append(identity)
    return _kron_all(operators)


def _critical_tfim_open_chain_gap(n_sites: int) -> float:
    hamiltonian = np.zeros((2**n_sites, 2**n_sites), dtype=complex)
    for site in range(n_sites - 1):
        hamiltonian -= _two_site_operator(PAULI_Z, site, PAULI_Z, site + 1, n_sites)
    for site in range(n_sites):
        hamiltonian -= _single_site_operator(PAULI_X, site, n_sites)
    spectrum = np.linalg.eigvalsh(hamiltonian)
    return float(np.real(spectrum[1] - spectrum[0]))


def _critical_tfim_open_chain_gap_sequence(system_sizes: np.ndarray) -> np.ndarray:
    return np.array([_critical_tfim_open_chain_gap(int(size)) for size in system_sizes], dtype=float)


def _randomized_wrong_exponent_variants(
    *,
    seed: int,
    variant_count: int,
    system_sizes: np.ndarray,
) -> list[dict]:
    rng = np.random.default_rng(seed)
    variants = []
    for index in range(variant_count):
        target_exponent = float(rng.uniform(0.35, 0.72))
        amplitude = float(rng.uniform(1.2, 2.8))
        jitter = rng.uniform(-0.015, 0.015, size=len(system_sizes))
        gaps = amplitude * np.power(system_sizes, -target_exponent) * (1.0 + jitter)
        # Enforce the local monotonicity oracle without changing the exponent
        # class: sorted positive points still fit far from z=1.
        gaps = np.minimum.accumulate(gaps)
        gaps = gaps - np.linspace(0.0, 1e-6, len(gaps))
        local_tests = _scaling_local_property_tests(system_sizes, gaps)
        fitted_exponent, r_squared = _fit_gap_exponent(system_sizes, gaps)
        abs_error = abs(fitted_exponent - 1.0)
        variants.append({
            "variant_index": index,
            "target_exponent": target_exponent,
            "fitted_exponent": fitted_exponent,
            "abs_error": abs_error,
            "fit_r_squared": r_squared,
            "local_property_tests": local_tests,
            "local_property_tests_pass": all(local_tests.values()),
            "universal_anchor_pass": bool(abs_error <= 0.10),
            "scaling_points": [
                {"system_size": int(size), "gap": float(gap)}
                for size, gap in zip(system_sizes, gaps, strict=True)
            ],
        })
    return variants


def ising_gap_wrong_exponent_passes_local_monotonicity() -> dict:
    """Scaling-law adversarial case: plausible monotone gaps with wrong exponent."""

    sizes = np.array([8, 12, 16, 24, 32, 48], dtype=float)
    gaps = 2.0 / np.sqrt(sizes)
    return _ising_scaling_payload(
        observable="Generated Ising critical finite-size gap exponent with wrong scaling",
        gaps=gaps,
        generator_error="wrong_dynamic_exponent_half_instead_of_one",
        coverage_case="universal_invariant_scaling_law_adversarial_failure",
        physical_evidence_detail=(
            "Scaling-law adversarial case: gaps are positive and strictly decreasing, "
            "but fit z≈0.5 instead of the critical Ising value z=1."
        ),
        pre_registered_success_criterion=(
            "local_property_tests_pass is true and abs(fitted_exponent - 1.0) > 0.10"
        ),
        claim_scope=(
            "scaling-law seed only; shows a universal exponent anchor can catch a "
            "plausible monotone finite-size sequence missed by local checks"
        ),
    )


def ising_gap_correct_exponent_noisy_passes_scaling_anchor() -> dict:
    """Positive scaling-law control: noisy but correct exponent within tolerance."""

    sizes = np.array([8, 12, 16, 24, 32, 48], dtype=float)
    noise = np.array([1.012, 0.993, 1.007, 0.996, 1.004, 0.998], dtype=float)
    gaps = np.pi * noise / sizes
    return _ising_scaling_payload(
        observable="Generated Ising critical finite-size gap exponent with small noise",
        gaps=gaps,
        generator_error="none_declared_noisy_scaling_control",
        coverage_case="universal_invariant_scaling_law_positive_control",
        physical_evidence_detail=(
            "Positive scaling-law control: finite-size gaps include small deterministic "
            "noise but fit the critical Ising exponent z=1 within the preregistered tolerance."
        ),
        pre_registered_success_criterion=(
            "local_property_tests_pass is true and abs(fitted_exponent - 1.0) <= 0.10"
        ),
        claim_scope=(
            "positive scaling-law control only; shows CAPAS can seal a noisy sequence "
            "that satisfies the preregistered universal exponent tolerance"
        ),
    )


def ising_gap_constant_sequence_local_catches_before_scaling() -> dict:
    """Generator-trivial negative control: local monotonicity rejects first."""

    gaps = np.full(6, 0.25, dtype=float)
    return _ising_scaling_payload(
        observable="Generated Ising critical finite-size gap exponent from constant sequence",
        gaps=gaps,
        generator_error="constant_gap_sequence",
        coverage_case="universal_invariant_scaling_law_local_catches",
        physical_evidence_detail=(
            "Generator-trivial negative control: constant gaps are positive and finite "
            "but fail the local decreasing-gap oracle before exponent fitting is credited."
        ),
        pre_registered_success_criterion=(
            "local_property_tests_pass is false and universal_anchor_pass is not_evaluated_local_oracle_failed"
        ),
        claim_scope=(
            "negative scaling-law control only; local monotonicity is sufficient and "
            "the universal exponent anchor is not credited"
        ),
    )


def ising_gap_exact_diagonalization_scaling_anchor() -> dict:
    """Simulation-generated scaling-law control from exact diagonalization."""

    sizes = np.array([4, 5, 6, 7, 8, 9], dtype=float)
    gaps = _critical_tfim_open_chain_gap_sequence(sizes)
    return _ising_scaling_payload(
        observable="Exact-diagonalization critical Ising open-chain gap exponent",
        gaps=gaps,
        system_sizes=sizes,
        generator_error="none_declared_exact_diagonalization_scaling_control",
        coverage_case="universal_invariant_scaling_law_simulation_generated",
        physical_evidence_detail=(
            "Simulation-generated scaling-law control: finite-size gaps are computed "
            "by exact diagonalization of the critical transverse-field Ising open chain. "
            "The fitted exponent is judged against the universal z=1 anchor with the "
            "same preregistered +/-0.10 tolerance."
        ),
        pre_registered_success_criterion=(
            "local_property_tests_pass is true and abs(fitted_exponent - 1.0) <= 0.10"
        ),
        claim_scope=(
            "non-synthetic scaling-law seed only; shows CAPAS can seal a sequence "
            "generated by an explicit finite-size Hamiltonian simulation, not just "
            "hand-authored scaling points"
        ),
        finite_size_notes=(
            "Exact diagonalization of open-chain critical TFIM for L=4..9. The sizes "
            "are intentionally small enough for dense diagonalization in the local test "
            "environment; the fitted exponent is a finite-size seed, not a precision "
            "critical-phenomena benchmark."
        ),
    )


def ising_gap_randomized_wrong_exponent_family() -> dict:
    """Randomized adversarial scaling family with preregistered thresholds."""

    sizes = np.array([8, 12, 16, 24, 32, 48], dtype=float)
    random_seed = 20260617
    variant_count = 8
    exponent_tolerance = 0.10
    variants = _randomized_wrong_exponent_variants(
        seed=random_seed,
        variant_count=variant_count,
        system_sizes=sizes,
    )
    local_pass_count = sum(variant["local_property_tests_pass"] for variant in variants)
    anchor_fail_count = sum(not variant["universal_anchor_pass"] for variant in variants)
    min_abs_error = min(variant["abs_error"] for variant in variants)
    max_abs_error = max(variant["abs_error"] for variant in variants)
    fitted_exponents = [variant["fitted_exponent"] for variant in variants]
    all_local_pass = local_pass_count == variant_count
    all_anchor_fail = anchor_fail_count == variant_count

    return {
        "observable": "Randomized generated Ising finite-size gap exponents with wrong scaling",
        "value": {
            "variant_count": variant_count,
            "local_pass_count": local_pass_count,
            "anchor_fail_count": anchor_fail_count,
            "fitted_exponents": fitted_exponents,
        },
        "expected": "all randomized variants violate z=1 by more than preregistered tolerance",
        "abs_error": min_abs_error,
        "units": "dynamic_exponent_z_min_abs_error",
        "physical_evidence_level": "scaling_law_anchor",
        "physical_evidence_detail": (
            "Randomized adversarial scaling family: all generated finite-size gap "
            "sequences are positive, finite, and decreasing, but every fitted exponent "
            "falls outside the preregistered z=1 +/-0.10 tolerance."
        ),
        "benchmark_family": "CriticalIsingFiniteSizeScaling",
        "reference_truth": "critical_ising_gap_dynamic_exponent_z_equals_1",
        "verification_independence": "theory_scaling_law_no_solver",
        "coverage_case": "universal_invariant_scaling_law_randomized_adversarial",
        "local_property_tests": {
            "all_variants_local_pass": all_local_pass,
            "variant_count": variant_count,
            "local_pass_count": local_pass_count,
        },
        "local_property_tests_pass": all_local_pass,
        "local_oracle_caught": False,
        "universal_anchor": "critical_ising_gap_delta_L_scales_as_L^-1",
        "universal_anchor_pass": bool(not all_anchor_fail),
        "invariant_caught": bool(all_local_pass and all_anchor_fail),
        "generator_error": "randomized_wrong_dynamic_exponents",
        "anchor_kind": "absolute_scaling_law",
        "anchor_mode": "absolute_anchor",
        "scaling_points": variants[0]["scaling_points"],
        "fitted_exponent": float(np.mean(fitted_exponents)),
        "expected_exponent": 1.0,
        "exponent_tolerance": exponent_tolerance,
        "fit_r_squared": min(variant["fit_r_squared"] for variant in variants),
        "finite_size_notes": (
            "Deterministic randomized adversarial family generated with seed 20260617. "
            "Each variant samples an exponent in [0.35, 0.72], then applies small "
            "jitter while preserving positive decreasing gaps. The preregistered "
            "criterion requires all variants to pass local monotonicity and fail the "
            "z=1 +/-0.10 universal anchor."
        ),
        "random_seed": random_seed,
        "variant_count": variant_count,
        "randomized_variants": variants,
        "min_abs_error": min_abs_error,
        "max_abs_error": max_abs_error,
        "structure_mapping": {
            "generator_output": "randomized family of finite-size gap sequences",
            "local_oracle_relation": "each variant has positive finite gaps decreasing with system size",
            "universal_oracle_relation": "critical Ising dynamic exponent z=1",
            "preserved_relation": "each generated sequence is judged by local monotonicity and universal scaling exponent",
        },
        "pre_registered_success_criterion": (
            "variant_count is 8, every variant has local_property_tests_pass true, "
            "and every variant has abs(fitted_exponent - 1.0) > 0.10"
        ),
        "claim_scope": (
            "randomized adversarial seed only; shows the scaling-law anchor is not a "
            "single hand-picked example, but it still is not an agent-generated corpus"
        ),
    }


def ising_gap_scripted_agent_wrong_exponent() -> dict:
    """Scripted-agent scaling adversarial case.

    This is intentionally not labeled as an LLM run. The generator is a minimal
    auditable agent transcript that answers a physics prompt with a plausible
    but wrong mean-field-style finite-size gap law, Delta(L) ~ L^-1/2.
    """

    agent_prompt = (
        "Produce finite-size critical transverse-field Ising gaps for "
        "L = 8, 12, 16, 24, 32, 48. Return a smooth positive decreasing "
        "sequence suitable for a quick scaling sanity check."
    )
    agent_response = {
        "agent": "scripted_scaling_agent_v1",
        "response_text": (
            "Use a smooth finite-size correction Delta(L)=1.7/sqrt(L). "
            "The gaps are positive, finite, and decrease with L, so the "
            "sequence should be acceptable for the scaling sanity check."
        ),
        "generated_table": [
            {"system_size": 8, "gap": 0.6010407640085654},
            {"system_size": 12, "gap": 0.4907477288111819},
            {"system_size": 16, "gap": 0.425},
            {"system_size": 24, "gap": 0.3470112407912327},
            {"system_size": 32, "gap": 0.3005203820042827},
            {"system_size": 48, "gap": 0.24537386440559094},
        ],
    }
    sizes, gaps = _scaling_points_from_agent_table(agent_response["generated_table"])
    payload = _ising_scaling_payload(
        observable="Scripted-agent generated Ising finite-size gap exponent with wrong scaling",
        gaps=gaps,
        system_sizes=sizes,
        generator_error="scripted_agent_mean_field_square_root_gap_law",
        coverage_case="universal_invariant_scaling_law_agent_generated_adversarial",
        physical_evidence_detail=(
            "Scripted-agent adversarial scaling case: the generated gap table is "
            "positive, finite, and decreasing, but it follows a plausible "
            "mean-field-style L^-1/2 law instead of the critical Ising z=1 law."
        ),
        pre_registered_success_criterion=(
            "agent_kind is scripted_agent, local_property_tests_pass is true, "
            "and abs(fitted_exponent - 1.0) > 0.10"
        ),
        claim_scope=(
            "agent-generated seed only; the generator is a deterministic scripted "
            "agent transcript, not an LLM corpus. This closes the plumbing and "
            "evidence grammar for agent-generated scaling outputs without claiming "
            "benchmark-level LLM utility."
        ),
        finite_size_notes=(
            "The sequence is produced by an embedded deterministic scripted-agent "
            "transcript and then checked by CAPAS. It is not sampled by the "
            "randomized adversarial generator and is not an LLM output."
        ),
    )
    payload.update({
        "agent_kind": "scripted_agent",
        "agent_id": agent_response["agent"],
        "agent_prompt": agent_prompt,
        "agent_response": agent_response,
    })
    return payload
