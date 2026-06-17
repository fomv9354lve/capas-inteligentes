from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


PHYSICS_LAB_ROOT = Path(
    "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/physics_quantum/physics-magnitude-lab"
)
SRC = PHYSICS_LAB_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from physics_magnitude_lab import quantum_engine as qe  # noqa: E402


def hadamard_square_returns_zero() -> dict:
    psi = qe.H_GATE @ (qe.H_GATE @ qe.basis_state(2, 0))
    value = float(abs(psi[0]) ** 2)
    return {
        "observable": "P(|0>) after H H |0>",
        "value": value,
        "expected": 1.0,
        "abs_error": abs(value - 1.0),
        "units": "probability",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": "H^2 = I, so H H |0> = |0>",
    }


def bell_entropy_ln2() -> dict:
    value = qe.entanglement_entropy(qe.bell_state(), dims=[2, 2], keep=[0])
    expected = float(np.log(2))
    return {
        "observable": "Bell pair entanglement entropy",
        "value": float(value),
        "expected": expected,
        "abs_error": abs(float(value) - expected),
        "units": "nats",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": "Reduced density matrix of Bell pair is I/2, entropy = ln 2",
    }


def product_entropy_zero() -> dict:
    product = np.kron(qe.basis_state(2, 0), qe.basis_state(2, 1))
    value = qe.entanglement_entropy(product, dims=[2, 2], keep=[0])
    return {
        "observable": "Product state entanglement entropy",
        "value": float(value),
        "expected": 0.0,
        "abs_error": abs(float(value)),
        "units": "nats",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": "Product states have rank-1 reduced density matrix, entropy = 0",
    }


def ghz_entropy_ln2(n_qubits: int = 3) -> dict:
    value = qe.entanglement_entropy(qe.ghz_state(n_qubits), dims=[2] * n_qubits, keep=[0])
    expected = float(np.log(2))
    return {
        "observable": f"GHZ({n_qubits}) one-qubit bipartition entropy",
        "value": float(value),
        "expected": expected,
        "abs_error": abs(float(value) - expected),
        "units": "nats",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": "Single-qubit reduction of GHZ state is I/2, entropy = ln 2",
    }


def born_rule_plus_state() -> dict:
    psi = qe.H_GATE @ qe.basis_state(2, 0)
    projectors = [g[1] for g in qe.spectral_projectors(qe.PAULI_Z)]
    probs = qe.born_probabilities(psi, projectors)
    expected = [0.5, 0.5]
    return {
        "observable": "Born probabilities for |+> in Z basis",
        "value": [float(p) for p in probs],
        "expected": expected,
        "abs_error": max(abs(float(p) - e) for p, e in zip(probs, expected)),
        "units": "probability",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": "|+> measured in Z basis gives 50/50 probabilities",
    }


def heisenberg_dimer_ground_state(J: float = 1.0) -> dict:
    H = J * (
        np.kron(qe.PAULI_X, qe.PAULI_X)
        + np.kron(qe.PAULI_Y, qe.PAULI_Y)
        + np.kron(qe.PAULI_Z, qe.PAULI_Z)
    ) / 4.0
    value = float(np.linalg.eigvalsh(H)[0])
    expected = float(-3.0 * J / 4.0)
    return {
        "observable": "Spin-1/2 Heisenberg dimer ground-state energy",
        "value": value,
        "expected": expected,
        "abs_error": abs(value - expected),
        "units": "energy",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": "For H = J S1.S2, the singlet ground state has E0 = -3J/4",
        "benchmark_family": "Heisenberg",
        "reference_truth": "closed_form_singlet_triplet_spectrum",
        "verification_independence": "analytic_no_solver",
    }


def transverse_field_ising_two_spin_ground_state(J: float = 1.0, h: float = 0.7) -> dict:
    H = -J * np.kron(qe.PAULI_Z, qe.PAULI_Z) - h * (
        np.kron(qe.PAULI_X, np.eye(2)) + np.kron(np.eye(2), qe.PAULI_X)
    )
    value = float(np.linalg.eigvalsh(H)[0])
    expected = float(-np.sqrt(J * J + 4.0 * h * h))
    return {
        "observable": "Two-spin transverse-field Ising ground-state energy",
        "value": value,
        "expected": expected,
        "abs_error": abs(value - expected),
        "units": "energy",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": "N=2 TFIM even block eigenvalues are +/-sqrt(J^2 + 4h^2); ground E0 = -sqrt(J^2 + 4h^2)",
        "benchmark_family": "Ising",
        "reference_truth": "closed_form_two_spin_TFIM_spectrum",
        "verification_independence": "analytic_no_solver",
    }


def particle_in_box_energy(n: int = 1, mass: float = 1.0, length: float = 1.0, hbar: float = 1.0) -> dict:
    value = float((n * n * np.pi * np.pi * hbar * hbar) / (2.0 * mass * length * length))
    expected = value
    return {
        "observable": f"1D infinite square well energy E_{n}",
        "value": value,
        "expected": expected,
        "abs_error": 0.0,
        "units": "energy",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": "Infinite square well eigenvalues are E_n = n^2*pi^2*hbar^2/(2mL^2)",
        "benchmark_family": "Schrodinger",
        "reference_truth": "closed_form_infinite_square_well",
        "verification_independence": "analytic_no_solver",
    }


def harmonic_oscillator_energy(n: int = 0, omega: float = 1.0, hbar: float = 1.0) -> dict:
    value = float(hbar * omega * (n + 0.5))
    expected = value
    return {
        "observable": f"Quantum harmonic oscillator energy E_{n}",
        "value": value,
        "expected": expected,
        "abs_error": 0.0,
        "units": "energy",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": "Harmonic oscillator eigenvalues are E_n = hbar*omega*(n + 1/2)",
        "benchmark_family": "Schrodinger",
        "reference_truth": "closed_form_harmonic_oscillator",
        "verification_independence": "analytic_no_solver",
    }


def pauli_z_ground_energy(field: float = 1.25) -> dict:
    H = -field * qe.PAULI_Z
    value = float(np.linalg.eigvalsh(H)[0])
    expected = float(-abs(field))
    return {
        "observable": "Single-spin Pauli-Z Hamiltonian ground-state energy",
        "value": value,
        "expected": expected,
        "abs_error": abs(value - expected),
        "units": "energy",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": "Eigenvalues of -h Z are {-h, +h}; ground energy is -|h|",
        "benchmark_family": "Pauli",
        "reference_truth": "closed_form_pauli_z_spectrum",
        "verification_independence": "analytic_no_solver",
    }


def bell_entropy_cross_sim() -> dict:
    bell = qe.bell_state()
    value = float(qe.entanglement_entropy(bell, dims=[2, 2], keep=[0]))
    rho = np.array([[0.5, 0.0], [0.0, 0.5]], dtype=float)
    evals = np.linalg.eigvalsh(rho)
    witness = float(-sum(float(x) * np.log(float(x)) for x in evals if x > 0))
    return {
        "observable": "Bell pair entanglement entropy cross-sim witness",
        "value": value,
        "expected": witness,
        "abs_error": abs(value - witness),
        "units": "nats",
        "physical_evidence_level": "cross_sim",
        "physical_evidence_detail": "quantum_engine entropy checked against independent reduced-density eigenvalue calculation",
        "benchmark_family": "Entanglement",
        "reference_truth": "independent_reduced_density_eigenspectrum",
        "verification_independence": "different_algorithm_same_runtime",
    }


def unverified_variational_energy() -> dict:
    rng = np.random.default_rng(1234)
    value = float(rng.normal(loc=-1.0, scale=0.05))
    return {
        "observable": "Toy variational energy without external witness",
        "value": value,
        "expected": None,
        "abs_error": None,
        "units": "energy",
        "physical_evidence_level": "none",
        "physical_evidence_detail": "No analytic solution or independent witness attached to this trace",
        "benchmark_family": "UnverifiedToy",
        "reference_truth": "none",
        "verification_independence": "none",
    }


def deliberately_failing_engine() -> dict:
    raise RuntimeError("intentional failure for failed-trace coverage")


def quimb_mps_estimated_bound(n: int = 60, depth: int = 6, max_bond: int = 8, seed: int = 1) -> dict:
    from physics_magnitude_lab.approx_hard_core import rcs_1d
    from physics_magnitude_lab.quimb_sim import quimb_truncated

    result = quimb_truncated(n, rcs_1d(n, depth, seed=seed), max_bond=max_bond)
    fidelity_lower_bound = float(result["fidelity_estimate"])
    trace_distance_upper_bound = float(np.sqrt(max(0.0, 1.0 - fidelity_lower_bound)))
    return {
        "observable": "Truncated MPS fidelity/trace-distance estimate for 1D random circuit",
        "value": {
            "fidelity_lower_bound": fidelity_lower_bound,
            "trace_distance_upper_bound": trace_distance_upper_bound,
            "bond_used": result["bond_used"],
        },
        "expected": "no dense reference at this scale",
        "abs_error": None,
        "units": "dimensionless",
        "physical_evidence_level": "estimated_bound",
        "physical_evidence_detail": (
            "Derived from quimb CircuitMPS fidelity_estimate(), which quimb documents as an estimate based on "
            "the norm of the truncated state and an approximation to the ideal overlap. Trace distance uses "
            "D<=sqrt(1-F_est). This is not a formal truncation certificate."
        ),
        "benchmark_family": "TensorNetwork",
        "reference_truth": "quimb_circuitmps_truncation_error_tracker",
        "verification_independence": "algorithmic_error_certificate_same_runtime",
        "certification_status": "estimated_not_formal_certificate",
        "formal_bound_status": "not_established_from_quimb_circuitmps_api",
        "n": n,
        "depth": depth,
        "max_bond": max_bond,
        "source_label": result["label"],
    }
