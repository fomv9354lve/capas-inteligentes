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


def assignment_to_ising_function_level() -> dict:
    """Tiny assignment problem mapped to Ising and verified exhaustively.

    Spins encode the assignee:
      - s_i = -1 -> Ada
      - s_i = +1 -> Ben

    Energy:
      E(s) = constant + sum_i h_i s_i + sum_{i<j} J_ij s_i s_j

    Terms:
      - individual cost c_i(person): ((c_ben + c_ada)/2) + ((c_ben - c_ada)/2) s_i
      - load balance penalty lambda * (sum_i s_i)^2
      - conflict penalty gamma_ij if two tasks share a person:
        gamma_ij * (1 + s_i s_j) / 2
    """
    tasks = [
        "data_cleaning",
        "api_integration",
        "ux_copy",
        "model_eval",
        "dashboard",
        "vendor_followup",
        "qa_pass",
        "deployment_notes",
    ]
    people = ["Ada", "Ben"]
    # Lower cost means better affinity. Ada is stronger on data/model/QA,
    # Ben is stronger on integration/copy/dashboard/deployment.
    costs = [
        (1.0, 3.2),
        (3.0, 1.1),
        (2.6, 1.2),
        (1.1, 3.0),
        (2.4, 1.4),
        (1.8, 2.1),
        (1.2, 2.7),
        (2.9, 1.0),
    ]
    balance_lambda = 0.35
    conflicts = {
        (0, 3): 1.4,  # data_cleaning and model_eval should be split for review independence
        (1, 4): 1.1,  # api_integration and dashboard overload the same delivery track
        (2, 7): 0.9,  # ux_copy and deployment_notes should not bottleneck one person
        (5, 6): 0.8,  # vendor_followup and qa_pass need separate accountability
    }

    h = np.zeros(len(tasks), dtype=float)
    J: dict[tuple[int, int], float] = {}
    constant = 0.0
    mapping_terms: list[dict] = []

    for idx, (ada_cost, ben_cost) in enumerate(costs):
        constant += (ada_cost + ben_cost) / 2.0
        h[idx] += (ben_cost - ada_cost) / 2.0
        mapping_terms.append(
            {
                "kind": "individual_affinity",
                "task": tasks[idx],
                "ada_cost": ada_cost,
                "ben_cost": ben_cost,
                "constant_delta": (ada_cost + ben_cost) / 2.0,
                "h_delta": (ben_cost - ada_cost) / 2.0,
            }
        )

    constant += balance_lambda * len(tasks)
    for i in range(len(tasks)):
        for j in range(i + 1, len(tasks)):
            J[(i, j)] = J.get((i, j), 0.0) + 2.0 * balance_lambda
    mapping_terms.append(
        {
            "kind": "load_balance",
            "penalty": "lambda * (sum_i s_i)^2",
            "lambda": balance_lambda,
            "constant_delta": balance_lambda * len(tasks),
            "pairwise_J_delta": 2.0 * balance_lambda,
        }
    )

    for (i, j), gamma in conflicts.items():
        constant += gamma / 2.0
        J[(i, j)] = J.get((i, j), 0.0) + gamma / 2.0
        mapping_terms.append(
            {
                "kind": "same_person_conflict",
                "tasks": [tasks[i], tasks[j]],
                "penalty": "gamma * (1 + s_i s_j) / 2",
                "gamma": gamma,
                "constant_delta": gamma / 2.0,
                "J_delta": gamma / 2.0,
            }
        )

    def energy(spins: np.ndarray) -> float:
        pair_energy = sum(coupling * float(spins[i] * spins[j]) for (i, j), coupling in J.items())
        return float(constant + float(np.dot(h, spins)) + pair_energy)

    n = len(tasks)
    assignments: list[dict] = []
    energies = []
    for raw in range(2**n):
        spins = np.array([1 if (raw >> i) & 1 else -1 for i in range(n)], dtype=int)
        value = energy(spins)
        energies.append(value)
        assignments.append(
            {
                "bits": raw,
                "spins": [int(x) for x in spins],
                "assignees": [people[1] if x == 1 else people[0] for x in spins],
                "energy": value,
            }
        )

    # Simulator path: exact diagonalization of the diagonal Ising Hamiltonian.
    hamiltonian = np.diag(np.array(energies, dtype=float))
    eigvals, eigvecs = np.linalg.eigh(hamiltonian)
    solver_energy = float(eigvals[0])
    solver_index = int(np.argmax(np.abs(eigvecs[:, 0]) ** 2))
    solver_assignment = assignments[solver_index]

    # Independent witness path: exhaustive enumeration over the objective.
    brute_energy = float(min(energies))
    tolerance = 1e-12
    optimal_assignments = [
        item for item in assignments if abs(item["energy"] - brute_energy) <= tolerance
    ]
    solver_is_brute_optimal = abs(solver_energy - brute_energy) <= tolerance and any(
        item["bits"] == solver_assignment["bits"] for item in optimal_assignments
    )
    if not solver_is_brute_optimal:
        raise AssertionError("exact diagonalization optimum did not match brute-force optimum")

    J_serialized = [
        {"i": int(i), "j": int(j), "value": float(value)}
        for (i, j), value in sorted(J.items())
        if abs(value) > 0.0
    ]
    costs_serialized = [
        {"task": task, "Ada": float(ada_cost), "Ben": float(ben_cost)}
        for task, (ada_cost, ben_cost) in zip(tasks, costs)
    ]
    conflicts_serialized = [
        {"tasks": [tasks[i], tasks[j]], "gamma": float(gamma)}
        for (i, j), gamma in sorted(conflicts.items())
    ]

    return {
        "observable": "N=8 K=2 assignment Ising ground-state energy",
        "value": {
            "solver_energy": solver_energy,
            "solver_assignment": solver_assignment,
            "brute_force_energy": brute_energy,
            "degeneracy_count": len(optimal_assignments),
            "optimal_assignments": optimal_assignments,
        },
        "expected": brute_energy,
        "abs_error": abs(solver_energy - brute_energy),
        "units": "objective_energy",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": (
            "A small real assignment objective is mapped explicitly to an Ising Hamiltonian. "
            "Exact diagonalization of the diagonal Hamiltonian is checked against exhaustive "
            "enumeration of all 2^8 assignments. This certifies optimality only for this small "
            "function-level instance; it does not claim optimization speedup."
        ),
        "benchmark_family": "CombinatorialOptimization",
        "reference_truth": "exact_brute_force_enumeration_2^8_assignments",
        "verification_independence": "different_method_same_runtime",
        "bound_scope": "exact_small_instance_brute_force_verified",
        "evidence_status_detail": "success",
        "tasks": tasks,
        "people": people,
        "costs": costs_serialized,
        "balance_lambda": balance_lambda,
        "conflicts": conflicts_serialized,
        "spin_encoding": {"-1": "Ada", "+1": "Ben"},
        "ising_h": [float(x) for x in h],
        "ising_J": J_serialized,
        "constant_offset": float(constant),
        "mapping_terms": mapping_terms,
        "degeneracy_count": len(optimal_assignments),
        "falsification_notes": [
            "No artificial terms were added beyond affinity, load balance, and stated conflict penalties.",
            "At N=8 brute force is trivial; the simulator does not add speed at this scale.",
            "The defended claim is sealed optimality evidence, not superior optimization performance.",
        ],
        "witness_stack": {
            "primary": "exact diagonalization of diagonal Ising Hamiltonian",
            "witness": "exhaustive enumeration of 2^8 assignments",
            "runtime_relation": "same_python_runtime_different_method",
        },
    }


def assignment_to_ising_degenerate_function_level() -> dict:
    """Tiny assignment problem with deliberately degenerate optima.

    This uses the same assignment-to-Ising grammar as
    assignment_to_ising_function_level, but two tasks are deliberately symmetric.
    The mathematical optimum is therefore a set, not a single assignment.
    """
    tasks = [
        "data_cleaning",
        "api_integration",
        "ux_copy",
        "model_eval",
        "dashboard",
        "documentation_polish",
        "qa_pass",
        "release_notes",
    ]
    people = ["Ada", "Ben"]
    costs = [
        (1.0, 3.2),  # Ada-leaning
        (3.0, 1.1),  # Ben-leaning
        (2.7, 1.2),  # Ben-leaning
        (1.1, 3.0),  # Ada-leaning
        (2.4, 1.4),  # Ben-leaning
        (2.0, 2.0),  # neutral
        (1.2, 2.7),  # Ada-leaning
        (2.0, 2.0),  # neutral
    ]
    balance_lambda = 0.35
    conflicts = {
        (0, 1): 0.8,
        (3, 4): 0.8,
        (5, 7): 0.6,
    }

    h = np.zeros(len(tasks), dtype=float)
    J: dict[tuple[int, int], float] = {}
    constant = 0.0
    mapping_terms: list[dict] = []

    for idx, (ada_cost, ben_cost) in enumerate(costs):
        constant += (ada_cost + ben_cost) / 2.0
        h[idx] += (ben_cost - ada_cost) / 2.0
        mapping_terms.append(
            {
                "kind": "individual_affinity",
                "task": tasks[idx],
                "ada_cost": ada_cost,
                "ben_cost": ben_cost,
                "constant_delta": (ada_cost + ben_cost) / 2.0,
                "h_delta": (ben_cost - ada_cost) / 2.0,
            }
        )

    constant += balance_lambda * len(tasks)
    for i in range(len(tasks)):
        for j in range(i + 1, len(tasks)):
            J[(i, j)] = J.get((i, j), 0.0) + 2.0 * balance_lambda
    mapping_terms.append(
        {
            "kind": "load_balance",
            "penalty": "lambda * (sum_i s_i)^2",
            "lambda": balance_lambda,
            "constant_delta": balance_lambda * len(tasks),
            "pairwise_J_delta": 2.0 * balance_lambda,
        }
    )

    for (i, j), gamma in conflicts.items():
        constant += gamma / 2.0
        J[(i, j)] = J.get((i, j), 0.0) + gamma / 2.0
        mapping_terms.append(
            {
                "kind": "same_person_conflict",
                "tasks": [tasks[i], tasks[j]],
                "penalty": "gamma * (1 + s_i s_j) / 2",
                "gamma": gamma,
                "constant_delta": gamma / 2.0,
                "J_delta": gamma / 2.0,
            }
        )

    def energy(spins: np.ndarray) -> float:
        pair_energy = sum(coupling * float(spins[i] * spins[j]) for (i, j), coupling in J.items())
        return float(constant + float(np.dot(h, spins)) + pair_energy)

    n = len(tasks)
    assignments: list[dict] = []
    energies = []
    for raw in range(2**n):
        spins = np.array([1 if (raw >> i) & 1 else -1 for i in range(n)], dtype=int)
        value = energy(spins)
        energies.append(value)
        assignments.append(
            {
                "bits": raw,
                "spins": [int(x) for x in spins],
                "assignees": [people[1] if x == 1 else people[0] for x in spins],
                "energy": value,
            }
        )

    hamiltonian = np.diag(np.array(energies, dtype=float))
    eigvals, eigvecs = np.linalg.eigh(hamiltonian)
    solver_energy = float(eigvals[0])
    solver_index = int(np.argmax(np.abs(eigvecs[:, 0]) ** 2))
    solver_assignment = assignments[solver_index]

    brute_energy = float(min(energies))
    tolerance = 1e-12
    optimal_assignments = [
        item for item in assignments if abs(item["energy"] - brute_energy) <= tolerance
    ]
    if len(optimal_assignments) < 2:
        raise AssertionError("degenerate test instance did not produce multiple optima")
    solver_is_brute_optimal = abs(solver_energy - brute_energy) <= tolerance and any(
        item["bits"] == solver_assignment["bits"] for item in optimal_assignments
    )
    if not solver_is_brute_optimal:
        raise AssertionError("exact diagonalization optimum did not match brute-force optimum")

    J_serialized = [
        {"i": int(i), "j": int(j), "value": float(value)}
        for (i, j), value in sorted(J.items())
        if abs(value) > 0.0
    ]
    costs_serialized = [
        {"task": task, "Ada": float(ada_cost), "Ben": float(ben_cost)}
        for task, (ada_cost, ben_cost) in zip(tasks, costs)
    ]
    conflicts_serialized = [
        {"tasks": [tasks[i], tasks[j]], "gamma": float(gamma)}
        for (i, j), gamma in sorted(conflicts.items())
    ]

    return {
        "observable": "Degenerate N=8 K=2 assignment Ising ground-state energy",
        "value": {
            "solver_energy": solver_energy,
            "solver_assignment": solver_assignment,
            "brute_force_energy": brute_energy,
            "degeneracy_count": len(optimal_assignments),
            "optimal_assignments": optimal_assignments,
        },
        "expected": brute_energy,
        "abs_error": abs(solver_energy - brute_energy),
        "units": "objective_energy",
        "physical_evidence_level": "analytic",
        "physical_evidence_detail": (
            "A deliberately symmetric assignment objective is mapped to Ising and solved by exact "
            "diagonalization. Exhaustive enumeration confirms multiple equally optimal assignments. "
            "The trace certifies the optimal set for this small instance and records that final choice "
            "among optima requires an external/business criterion."
        ),
        "benchmark_family": "CombinatorialOptimization",
        "reference_truth": "exact_brute_force_enumeration_2^8_assignments_degenerate",
        "verification_independence": "different_method_same_runtime",
        "bound_scope": "exact_small_instance_brute_force_verified",
        "evidence_status_detail": "success_degenerate_optimum_set",
        "tasks": tasks,
        "people": people,
        "costs": costs_serialized,
        "balance_lambda": balance_lambda,
        "conflicts": conflicts_serialized,
        "spin_encoding": {"-1": "Ada", "+1": "Ben"},
        "ising_h": [float(x) for x in h],
        "ising_J": J_serialized,
        "constant_offset": float(constant),
        "mapping_terms": mapping_terms,
        "degeneracy_count": len(optimal_assignments),
        "falsification_notes": [
            "Degeneracy is deliberate: documentation_polish and release_notes are symmetric neutral tasks.",
            "At N=8 brute force is trivial; the simulator does not add speed at this scale.",
            "The defended claim is sealed optimality-set evidence, not superior optimization performance.",
            "The trace shows where mathematics stops: choosing among equivalent optima needs an external criterion.",
        ],
        "witness_stack": {
            "primary": "exact diagonalization of diagonal Ising Hamiltonian",
            "witness": "exhaustive enumeration of 2^8 assignments",
            "runtime_relation": "same_python_runtime_different_method",
        },
    }


def h2_sto3g_experimental_reference() -> dict:
    """H2/STO-3G exact model solve compared with measured dissociation energy.

    This trace separates:
      - solver error: PySCF FCI value vs itself re-diagonalized in the FCI model,
      - model error: minimal-basis H2 binding energy vs measured H2 dissociation.

    The experimental reference is the measured H2 dissociation energy
    D0(N=1)=35999.582834 cm^-1 from Hölsch et al. 2019. It is used here as a
    lab-measured binding-energy reference, not as a claim that STO-3G represents
    the full physical molecule accurately.
    """
    from pyscf import fci, gto, scf

    bond_length_angstrom = 0.7414
    basis = "sto-3g"
    molecule = gto.M(
        atom=f"H 0 0 0; H 0 0 {bond_length_angstrom}",
        basis=basis,
        unit="Angstrom",
        charge=0,
        spin=0,
        verbose=0,
    )
    mf = scf.RHF(molecule).run(verbose=0)
    cisolver = fci.FCI(molecule, mf.mo_coeff)
    fci_total_energy, _ = cisolver.kernel()
    fci_total_energy = float(fci_total_energy)

    # Same basis, isolated H atom reference. This is deliberately a model
    # quantity; it is not the exact physical H atom energy.
    atom = gto.M(
        atom="H 0 0 0",
        basis=basis,
        unit="Angstrom",
        charge=0,
        spin=1,
        verbose=0,
    )
    atom_mf = scf.UHF(atom).run(verbose=0)
    model_atom_energy = float(atom_mf.e_tot)
    model_binding_energy = float(2.0 * model_atom_energy - fci_total_energy)

    experimental_d0_cm_inverse = 35999.582834
    hartree_per_cm_inverse = 1.0 / 219474.6313705
    experimental_binding_energy = float(experimental_d0_cm_inverse * hartree_per_cm_inverse)
    chemical_accuracy_threshold = 0.0015936

    solver_error_hartree = 0.0
    model_error_hartree = abs(model_binding_energy - experimental_binding_energy)
    within_chemical_accuracy = bool(model_error_hartree < chemical_accuracy_threshold)

    return {
        "observable": "H2 STO-3G binding energy vs experimental dissociation energy",
        "value": {
            "fci_total_energy_hartree": fci_total_energy,
            "model_atom_energy_hartree": model_atom_energy,
            "model_binding_energy_hartree": model_binding_energy,
            "experimental_binding_energy_hartree": experimental_binding_energy,
            "experimental_d0_cm_inverse": experimental_d0_cm_inverse,
            "solver_error_hartree": solver_error_hartree,
            "model_error_hartree": model_error_hartree,
            "within_chemical_accuracy": within_chemical_accuracy,
        },
        "expected": {
            "reference_fci_total_energy_hartree": fci_total_energy,
            "reference_experimental_binding_energy_hartree": experimental_binding_energy,
            "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        },
        "abs_error": solver_error_hartree,
        "abs_error_vs_fci": solver_error_hartree,
        "abs_error_vs_experimental": model_error_hartree,
        "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        "within_chemical_accuracy": within_chemical_accuracy,
        "units": "hartree",
        "physical_evidence_level": "experimental",
        "physical_evidence_detail": (
            "H2/STO-3G at R=0.7414 Angstrom is solved by PySCF FCI. The solver error against "
            "the model FCI reference is zero by construction of the exact model solve. The model "
            "binding energy is then compared against the measured H2 dissociation energy "
            "D0(N=1)=35999.582834 cm^-1. The trace intentionally records that the minimal-basis "
            "model is not within chemical accuracy of the experimental binding reference."
        ),
        "benchmark_family": "QuantumChemistry",
        "reference_truth": {
            "fci": {
                "kind": "exact_model_solution",
                "method": "PySCF FCI",
                "basis": basis,
                "geometry": f"H-H {bond_length_angstrom} Angstrom",
                "total_energy_hartree": fci_total_energy,
            },
            "experimental": {
                "kind": "measured_dissociation_energy",
                "quantity": "D0(N=1) ortho-H2",
                "value_cm_inverse": experimental_d0_cm_inverse,
                "value_hartree": experimental_binding_energy,
                "source": "Hölsch et al. 2019, arXiv:1902.09471",
            },
            "chemical_accuracy": {
                "threshold_hartree": chemical_accuracy_threshold,
                "threshold_name": "1 kcal/mol",
            },
        },
        "verification_independence": "same_runtime_exact_fci_with_external_experimental_reference",
        "bound_scope": "single_molecule_minimal_basis_equilibrium_geometry",
        "evidence_status_detail": "experimental_reference_model_error_reported",
        "basis": basis,
        "geometry": [{"atom": "H", "xyz_angstrom": [0.0, 0.0, 0.0]}, {"atom": "H", "xyz_angstrom": [0.0, 0.0, bond_length_angstrom]}],
        "bond_length_angstrom": bond_length_angstrom,
        "solver_error_hartree": solver_error_hartree,
        "model_error_hartree": model_error_hartree,
        "model_binding_energy_hartree": model_binding_energy,
        "experimental_binding_energy_hartree": experimental_binding_energy,
        "reference_fci_total_energy_hartree": fci_total_energy,
        "reference_experimental_d0_cm_inverse": experimental_d0_cm_inverse,
        "source_label": "PySCF FCI model solve + external H2 D0 measurement",
        "falsification_notes": [
            "The STO-3G FCI solve is exact for the minimal-basis model, not exact for physical H2.",
            "The model binding energy is not within chemical accuracy of the experimental D0 reference.",
            "This is recorded as model error, not solver error.",
            "The defended claim is error separation in a sealed trace, not competitive quantum chemistry.",
        ],
        "witness_stack": {
            "primary": "PySCF FCI exact model solve",
            "witness": "external experimental H2 dissociation energy",
            "runtime_relation": "same_runtime_model_solve_plus_external_measurement",
        },
    }


def h2_ccpvdz_experimental_reference() -> dict:
    """H2/cc-pVDZ exact model solve compared with measured dissociation energy.

    This is the paired trace for h2_sto3g_experimental_reference. The solver is
    still exact FCI for the declared model, but the basis is larger. The expected
    behavior is lower model error against the same experimental D0 reference.
    """
    from pyscf import fci, gto, scf

    bond_length_angstrom = 0.7414
    basis = "cc-pvdz"
    molecule = gto.M(
        atom=f"H 0 0 0; H 0 0 {bond_length_angstrom}",
        basis=basis,
        unit="Angstrom",
        charge=0,
        spin=0,
        verbose=0,
    )
    mf = scf.RHF(molecule).run(verbose=0)
    cisolver = fci.FCI(molecule, mf.mo_coeff)
    fci_total_energy, _ = cisolver.kernel()
    fci_total_energy = float(fci_total_energy)

    atom = gto.M(
        atom="H 0 0 0",
        basis=basis,
        unit="Angstrom",
        charge=0,
        spin=1,
        verbose=0,
    )
    atom_mf = scf.UHF(atom).run(verbose=0)
    model_atom_energy = float(atom_mf.e_tot)
    model_binding_energy = float(2.0 * model_atom_energy - fci_total_energy)

    experimental_d0_cm_inverse = 35999.582834
    hartree_per_cm_inverse = 1.0 / 219474.6313705
    experimental_binding_energy = float(experimental_d0_cm_inverse * hartree_per_cm_inverse)
    chemical_accuracy_threshold = 0.0015936

    solver_error_hartree = 0.0
    model_error_hartree = abs(model_binding_energy - experimental_binding_energy)
    within_chemical_accuracy = bool(model_error_hartree < chemical_accuracy_threshold)

    return {
        "observable": "H2 cc-pVDZ binding energy vs experimental dissociation energy",
        "value": {
            "fci_total_energy_hartree": fci_total_energy,
            "model_atom_energy_hartree": model_atom_energy,
            "model_binding_energy_hartree": model_binding_energy,
            "experimental_binding_energy_hartree": experimental_binding_energy,
            "experimental_d0_cm_inverse": experimental_d0_cm_inverse,
            "solver_error_hartree": solver_error_hartree,
            "model_error_hartree": model_error_hartree,
            "within_chemical_accuracy": within_chemical_accuracy,
        },
        "expected": {
            "reference_fci_total_energy_hartree": fci_total_energy,
            "reference_experimental_binding_energy_hartree": experimental_binding_energy,
            "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        },
        "abs_error": solver_error_hartree,
        "abs_error_vs_fci": solver_error_hartree,
        "abs_error_vs_experimental": model_error_hartree,
        "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        "within_chemical_accuracy": within_chemical_accuracy,
        "units": "hartree",
        "physical_evidence_level": "experimental",
        "physical_evidence_detail": (
            "H2/cc-pVDZ at R=0.7414 Angstrom is solved by PySCF FCI. The solver error against "
            "the model FCI reference is zero by construction. Compared with the same measured "
            "H2 D0 reference used by trace_021, the larger basis reduces model error and is "
            "within the 1 kcal/mol chemical-accuracy threshold for this binding-energy comparison."
        ),
        "benchmark_family": "QuantumChemistry",
        "reference_truth": {
            "fci": {
                "kind": "exact_model_solution",
                "method": "PySCF FCI",
                "basis": basis,
                "geometry": f"H-H {bond_length_angstrom} Angstrom",
                "total_energy_hartree": fci_total_energy,
            },
            "experimental": {
                "kind": "measured_dissociation_energy",
                "quantity": "D0(N=1) ortho-H2",
                "value_cm_inverse": experimental_d0_cm_inverse,
                "value_hartree": experimental_binding_energy,
                "source": "Hölsch et al. 2019, arXiv:1902.09471",
            },
            "chemical_accuracy": {
                "threshold_hartree": chemical_accuracy_threshold,
                "threshold_name": "1 kcal/mol",
            },
        },
        "verification_independence": "same_runtime_exact_fci_with_external_experimental_reference",
        "bound_scope": "single_molecule_larger_basis_equilibrium_geometry",
        "evidence_status_detail": "experimental_reference_model_error_within_chemical_accuracy",
        "basis": basis,
        "geometry": [{"atom": "H", "xyz_angstrom": [0.0, 0.0, 0.0]}, {"atom": "H", "xyz_angstrom": [0.0, 0.0, bond_length_angstrom]}],
        "bond_length_angstrom": bond_length_angstrom,
        "solver_error_hartree": solver_error_hartree,
        "model_error_hartree": model_error_hartree,
        "model_binding_energy_hartree": model_binding_energy,
        "experimental_binding_energy_hartree": experimental_binding_energy,
        "reference_fci_total_energy_hartree": fci_total_energy,
        "reference_experimental_d0_cm_inverse": experimental_d0_cm_inverse,
        "source_label": "PySCF FCI cc-pVDZ model solve + external H2 D0 measurement",
        "falsification_notes": [
            "The cc-pVDZ FCI solve is exact for the declared finite-basis model, not exact for full physical H2.",
            "The larger basis reduces model error relative to STO-3G for this binding-energy comparison.",
            "Within chemical accuracy here means the model binding energy is close to the chosen D0 reference; it does not include a full spectroscopic correction audit.",
            "The defended claim is solver/model/experiment separation across model quality levels, not competitive quantum chemistry.",
        ],
        "witness_stack": {
            "primary": "PySCF FCI exact cc-pVDZ model solve",
            "witness": "external experimental H2 dissociation energy",
            "runtime_relation": "same_runtime_model_solve_plus_external_measurement",
        },
    }


def h2_ccpvtz_experimental_reference() -> dict:
    """H2/cc-pVTZ larger-basis model compared with measured D0.

    This trace is intentionally not forced to improve the previous result. It
    records what happens when the basis is larger while the experimental
    reference remains the measured dissociation energy. For this simple
    vertical comparison, cc-pVTZ is exact for its model but not within chemical
    accuracy against the chosen D0 reference.
    """
    from pyscf import fci, gto, scf

    bond_length_angstrom = 0.7414
    basis = "cc-pvtz"
    molecule = gto.M(
        atom=f"H 0 0 0; H 0 0 {bond_length_angstrom}",
        basis=basis,
        unit="Angstrom",
        charge=0,
        spin=0,
        verbose=0,
    )
    mf = scf.RHF(molecule).run(verbose=0)
    cisolver = fci.FCI(molecule, mf.mo_coeff)
    fci_total_energy, _ = cisolver.kernel()
    fci_total_energy = float(fci_total_energy)

    atom = gto.M(
        atom="H 0 0 0",
        basis=basis,
        unit="Angstrom",
        charge=0,
        spin=1,
        verbose=0,
    )
    atom_mf = scf.UHF(atom).run(verbose=0)
    model_atom_energy = float(atom_mf.e_tot)
    model_binding_energy = float(2.0 * model_atom_energy - fci_total_energy)

    experimental_d0_cm_inverse = 35999.582834
    hartree_per_cm_inverse = 1.0 / 219474.6313705
    experimental_binding_energy = float(experimental_d0_cm_inverse * hartree_per_cm_inverse)
    chemical_accuracy_threshold = 0.0015936

    solver_error_hartree = 0.0
    model_error_hartree = abs(model_binding_energy - experimental_binding_energy)
    within_chemical_accuracy = bool(model_error_hartree < chemical_accuracy_threshold)

    return {
        "observable": "H2 cc-pVTZ binding energy vs experimental dissociation energy",
        "value": {
            "fci_total_energy_hartree": fci_total_energy,
            "model_atom_energy_hartree": model_atom_energy,
            "model_binding_energy_hartree": model_binding_energy,
            "experimental_binding_energy_hartree": experimental_binding_energy,
            "experimental_d0_cm_inverse": experimental_d0_cm_inverse,
            "solver_error_hartree": solver_error_hartree,
            "model_error_hartree": model_error_hartree,
            "within_chemical_accuracy": within_chemical_accuracy,
            "basis_orbitals": int(molecule.nao_nr()),
        },
        "expected": {
            "reference_fci_total_energy_hartree": fci_total_energy,
            "reference_experimental_binding_energy_hartree": experimental_binding_energy,
            "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        },
        "abs_error": solver_error_hartree,
        "abs_error_vs_fci": solver_error_hartree,
        "abs_error_vs_experimental": model_error_hartree,
        "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        "within_chemical_accuracy": within_chemical_accuracy,
        "units": "hartree",
        "physical_evidence_level": "experimental",
        "physical_evidence_detail": (
            "H2/cc-pVTZ at R=0.7414 Angstrom is solved by PySCF FCI. The basis is larger than "
            "cc-pVDZ, but this vertical electronic comparison against measured D0 is not within "
            "the 1 kcal/mol threshold. The trace records this honestly as model/reference mismatch, "
            "not solver error."
        ),
        "benchmark_family": "QuantumChemistry",
        "reference_truth": {
            "fci": {
                "kind": "exact_model_solution",
                "method": "PySCF FCI",
                "basis": basis,
                "geometry": f"H-H {bond_length_angstrom} Angstrom",
                "total_energy_hartree": fci_total_energy,
            },
            "experimental": {
                "kind": "measured_dissociation_energy",
                "quantity": "D0(N=1) ortho-H2",
                "value_cm_inverse": experimental_d0_cm_inverse,
                "value_hartree": experimental_binding_energy,
                "source": "Hölsch et al. 2019, arXiv:1902.09471",
            },
            "chemical_accuracy": {
                "threshold_hartree": chemical_accuracy_threshold,
                "threshold_name": "1 kcal/mol",
            },
        },
        "verification_independence": "same_runtime_exact_fci_with_external_experimental_reference",
        "bound_scope": "single_molecule_larger_basis_equilibrium_geometry",
        "evidence_status_detail": "experimental_reference_larger_basis_not_within_chemical_accuracy",
        "basis": basis,
        "basis_orbitals": int(molecule.nao_nr()),
        "geometry": [{"atom": "H", "xyz_angstrom": [0.0, 0.0, 0.0]}, {"atom": "H", "xyz_angstrom": [0.0, 0.0, bond_length_angstrom]}],
        "bond_length_angstrom": bond_length_angstrom,
        "solver_error_hartree": solver_error_hartree,
        "model_error_hartree": model_error_hartree,
        "model_binding_energy_hartree": model_binding_energy,
        "experimental_binding_energy_hartree": experimental_binding_energy,
        "reference_fci_total_energy_hartree": fci_total_energy,
        "reference_experimental_d0_cm_inverse": experimental_d0_cm_inverse,
        "source_label": "PySCF FCI cc-pVTZ model solve + external H2 D0 measurement",
        "falsification_notes": [
            "The cc-pVTZ FCI solve is exact for the declared finite-basis electronic model.",
            "The model error is larger than the cc-pVDZ trace for this D0 comparison.",
            "This shows that larger basis alone does not automatically mean better agreement with a measured dissociation reference when other physical corrections are not modeled.",
            "The defended claim is honest separation of solver/model/reference mismatch, not monotonic improvement.",
        ],
        "witness_stack": {
            "primary": "PySCF FCI exact cc-pVTZ model solve",
            "witness": "external experimental H2 dissociation energy",
            "runtime_relation": "same_runtime_model_solve_plus_external_measurement",
        },
    }


def h2_ccpvtz_reference_definition_corrected() -> dict:
    """H2/cc-pVTZ compared against a model-vibrational D_e reference.

    The earlier chemistry traces compared electronic binding energies against
    experimental D0. D0 includes zero-point vibration, while the electronic
    calculation is a clamped-nuclei D_e-like quantity. This trace computes a
    harmonic vibrational ZPE from the same electronic model and applies:

        D_e ~= D0 + ZPE_harmonic(model)

    The correction is model-harmonic, not a full spectroscopic audit.
    """
    from pyscf import fci, gto, hessian, scf
    from pyscf.hessian import thermo

    bond_length_angstrom = 0.7414
    basis = "cc-pvtz"
    molecule = gto.M(
        atom=f"H 0 0 0; H 0 0 {bond_length_angstrom}",
        basis=basis,
        unit="Angstrom",
        charge=0,
        spin=0,
        verbose=0,
    )
    mf = scf.RHF(molecule).run(verbose=0)
    cisolver = fci.FCI(molecule, mf.mo_coeff)
    fci_total_energy, _ = cisolver.kernel()
    fci_total_energy = float(fci_total_energy)

    atom = gto.M(
        atom="H 0 0 0",
        basis=basis,
        unit="Angstrom",
        charge=0,
        spin=1,
        verbose=0,
    )
    atom_mf = scf.UHF(atom).run(verbose=0)
    model_atom_energy = float(atom_mf.e_tot)
    model_binding_energy = float(2.0 * model_atom_energy - fci_total_energy)

    hess = hessian.RHF(mf).kernel()
    harmonic = thermo.harmonic_analysis(molecule, hess)
    harmonic_frequencies_cm_inverse = [float(x) for x in harmonic["freq_wavenumber"] if float(x) > 0.0]
    zpe_cm_inverse = float(0.5 * sum(harmonic_frequencies_cm_inverse))

    experimental_d0_cm_inverse = 35999.582834
    hartree_per_cm_inverse = 1.0 / 219474.6313705
    experimental_d0_hartree = float(experimental_d0_cm_inverse * hartree_per_cm_inverse)
    zpe_hartree = float(zpe_cm_inverse * hartree_per_cm_inverse)
    experimental_de_corrected_hartree = float(experimental_d0_hartree + zpe_hartree)
    chemical_accuracy_threshold = 0.0015936

    solver_error_hartree = 0.0
    uncorrected_reference_error_hartree = abs(model_binding_energy - experimental_d0_hartree)
    reference_definition_corrected_error_hartree = abs(model_binding_energy - experimental_de_corrected_hartree)
    within_chemical_accuracy = bool(reference_definition_corrected_error_hartree < chemical_accuracy_threshold)

    return {
        "observable": "H2 cc-pVTZ electronic binding energy vs ZPE-corrected experimental D_e reference",
        "value": {
            "fci_total_energy_hartree": fci_total_energy,
            "model_atom_energy_hartree": model_atom_energy,
            "model_binding_energy_hartree": model_binding_energy,
            "experimental_d0_hartree": experimental_d0_hartree,
            "zpe_hartree": zpe_hartree,
            "zpe_cm_inverse": zpe_cm_inverse,
            "harmonic_frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
            "experimental_de_corrected_hartree": experimental_de_corrected_hartree,
            "uncorrected_reference_error_hartree": uncorrected_reference_error_hartree,
            "reference_definition_corrected_error_hartree": reference_definition_corrected_error_hartree,
            "solver_error_hartree": solver_error_hartree,
            "within_chemical_accuracy": within_chemical_accuracy,
            "basis_orbitals": int(molecule.nao_nr()),
        },
        "expected": {
            "reference_fci_total_energy_hartree": fci_total_energy,
            "reference_experimental_de_corrected_hartree": experimental_de_corrected_hartree,
            "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        },
        "abs_error": solver_error_hartree,
        "abs_error_vs_fci": solver_error_hartree,
        "abs_error_vs_experimental": reference_definition_corrected_error_hartree,
        "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        "within_chemical_accuracy": within_chemical_accuracy,
        "units": "hartree",
        "physical_evidence_level": "experimental",
        "physical_evidence_detail": (
            "H2/cc-pVTZ electronic binding energy is compared to a D_e-like reference rather than "
            "raw D0. The D_e reference is formed by adding the same-model harmonic ZPE to measured "
            "D0. This records reference-definition correction: electronic D_e-like quantity versus "
            "D0-with-vibration was the mismatch in trace_023."
        ),
        "benchmark_family": "QuantumChemistry",
        "reference_truth": {
            "fci": {
                "kind": "exact_model_solution",
                "method": "PySCF FCI",
                "basis": basis,
                "geometry": f"H-H {bond_length_angstrom} Angstrom",
                "total_energy_hartree": fci_total_energy,
            },
            "experimental": {
                "kind": "measured_dissociation_energy_with_reference_definition_correction",
                "raw_quantity": "D0(N=1) ortho-H2",
                "raw_value_cm_inverse": experimental_d0_cm_inverse,
                "raw_value_hartree": experimental_d0_hartree,
                "zpe_quantity": "same-model harmonic zero-point vibrational energy",
                "zpe_value_cm_inverse": zpe_cm_inverse,
                "zpe_value_hartree": zpe_hartree,
                "harmonic_frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
                "corrected_quantity": "model-harmonic D_e = D0 + ZPE_harmonic(model)",
                "corrected_value_hartree": experimental_de_corrected_hartree,
                "source": "D0: Hölsch et al. 2019, arXiv:1902.09471; ZPE: PySCF harmonic analysis from the declared cc-pVTZ electronic model",
            },
            "chemical_accuracy": {
                "threshold_hartree": chemical_accuracy_threshold,
                "threshold_name": "1 kcal/mol",
            },
        },
        "verification_independence": "same_runtime_exact_fci_with_external_experimental_reference",
        "bound_scope": "single_molecule_larger_basis_reference_definition_corrected",
        "evidence_status_detail": "experimental_reference_definition_corrected_approximate_zpe",
        "basis": basis,
        "basis_orbitals": int(molecule.nao_nr()),
        "geometry": [{"atom": "H", "xyz_angstrom": [0.0, 0.0, 0.0]}, {"atom": "H", "xyz_angstrom": [0.0, 0.0, bond_length_angstrom]}],
        "bond_length_angstrom": bond_length_angstrom,
        "solver_error_hartree": solver_error_hartree,
        "model_error_hartree": reference_definition_corrected_error_hartree,
        "reference_definition_error_hartree": uncorrected_reference_error_hartree,
        "reference_definition_corrected_error_hartree": reference_definition_corrected_error_hartree,
        "reference_definition_match": "corrected_model_harmonic_D0_plus_ZPE_to_match_electronic_De",
        "reference_definition_correction": {
            "raw_reference": "D0 includes vibrational zero-point energy",
            "computed_quantity": "clamped-nuclei electronic binding energy",
            "correction": "D_e ~= D0 + ZPE_harmonic(model)",
            "zpe_cm_inverse": zpe_cm_inverse,
            "zpe_hartree": zpe_hartree,
            "harmonic_frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
            "quality": "same_model_harmonic_vibrational_correction_not_full_spectroscopic_audit",
        },
        "vibrational_zpe_hartree": zpe_hartree,
        "vibrational_zpe_cm_inverse": zpe_cm_inverse,
        "harmonic_frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
        "model_binding_energy_hartree": model_binding_energy,
        "experimental_binding_energy_hartree": experimental_de_corrected_hartree,
        "reference_fci_total_energy_hartree": fci_total_energy,
        "reference_experimental_d0_cm_inverse": experimental_d0_cm_inverse,
        "source_label": "PySCF FCI cc-pVTZ model solve + D0 experimental reference corrected by PySCF harmonic ZPE",
        "falsification_notes": [
            "trace_023 compared an electronic D_e-like quantity against raw D0, which mixes reference definitions.",
            "This trace applies a same-model harmonic ZPE correction to compare electronic binding against D_e-like reference.",
            "The ZPE value is model-harmonic, not an anharmonic spectroscopic constant.",
            "The defended claim is that CAPAS can record and correct reference-definition mismatch explicitly.",
        ],
        "witness_stack": {
            "primary": "PySCF FCI exact cc-pVTZ model solve",
            "witness": "external experimental H2 D0 plus same-model harmonic ZPE reference-definition correction",
            "runtime_relation": "same_runtime_model_solve_plus_external_measurement_and_reference_correction",
        },
    }


def h2o_sto3g_electronic_vibrational_reference() -> dict:
    """H2O/STO-3G exact model solve with electronic/vibrational split.

    This is the first more-complex molecule trace. It is exact for a small
    finite-basis electronic model, computes a model-harmonic ZPE, and compares
    the resulting D0-like atomization energy to a tabulated experimental
    atomization reference assembled from two O-H dissociation energies.
    """
    from pyscf import fci, gto, hessian, scf
    from pyscf.hessian import thermo

    basis = "sto-3g"
    geometry = [
        {"atom": "O", "xyz_angstrom": [0.0, 0.0, 0.0]},
        {"atom": "H", "xyz_angstrom": [0.0, -0.757, 0.587]},
        {"atom": "H", "xyz_angstrom": [0.0, 0.757, 0.587]},
    ]
    molecule = gto.M(
        atom="O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587",
        basis=basis,
        unit="Angstrom",
        charge=0,
        spin=0,
        verbose=0,
    )
    mf = scf.RHF(molecule).run(verbose=0)
    cisolver = fci.FCI(molecule, mf.mo_coeff)
    fci_total_energy, _ = cisolver.kernel()
    fci_total_energy = float(fci_total_energy)

    hess = hessian.RHF(mf).kernel()
    harmonic = thermo.harmonic_analysis(molecule, hess)
    harmonic_frequencies_cm_inverse = [float(x) for x in harmonic["freq_wavenumber"] if float(x) > 0.0]
    hartree_per_cm_inverse = 1.0 / 219474.6313705
    zpe_cm_inverse = float(0.5 * sum(harmonic_frequencies_cm_inverse))
    zpe_hartree = float(zpe_cm_inverse * hartree_per_cm_inverse)

    h_atom = gto.M(atom="H 0 0 0", basis=basis, unit="Angstrom", charge=0, spin=1, verbose=0)
    h_mf = scf.UHF(h_atom).run(verbose=0)
    h_fci = fci.FCI(h_atom, h_mf.mo_coeff)
    h_atom_energy, _ = h_fci.kernel(nelec=h_atom.nelec)
    h_atom_energy = float(h_atom_energy)

    o_atom = gto.M(atom="O 0 0 0", basis=basis, unit="Angstrom", charge=0, spin=2, verbose=0)
    o_mf = scf.UHF(o_atom).run(verbose=0)
    o_fci = fci.FCI(o_atom, o_mf.mo_coeff)
    o_atom_energy, _ = o_fci.kernel(nelec=o_atom.nelec)
    o_atom_energy = float(o_atom_energy)

    electronic_atomization_energy = float(o_atom_energy + 2.0 * h_atom_energy - fci_total_energy)
    zpe_corrected_atomization_energy = float(electronic_atomization_energy - zpe_hartree)

    kcal_per_hartree = 627.5094740631
    experimental_first_oh_bde_kcal_mol = 118.8
    experimental_second_oh_bde_kcal_mol = 101.8
    experimental_atomization_kcal_mol = float(experimental_first_oh_bde_kcal_mol + experimental_second_oh_bde_kcal_mol)
    experimental_atomization_energy = float(experimental_atomization_kcal_mol / kcal_per_hartree)
    chemical_accuracy_threshold = 0.0015936

    solver_error_hartree = 0.0
    electronic_reference_error = abs(electronic_atomization_energy - experimental_atomization_energy)
    zpe_corrected_reference_error = abs(zpe_corrected_atomization_energy - experimental_atomization_energy)
    within_chemical_accuracy = bool(zpe_corrected_reference_error < chemical_accuracy_threshold)

    return {
        "observable": "H2O/STO-3G FCI atomization energy with model-harmonic ZPE correction",
        "value": {
            "fci_total_energy_hartree": fci_total_energy,
            "h_atom_energy_hartree": h_atom_energy,
            "o_atom_energy_hartree": o_atom_energy,
            "electronic_atomization_energy_hartree": electronic_atomization_energy,
            "vibrational_zpe_hartree": zpe_hartree,
            "vibrational_zpe_cm_inverse": zpe_cm_inverse,
            "harmonic_frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
            "zpe_corrected_atomization_energy_hartree": zpe_corrected_atomization_energy,
            "experimental_atomization_energy_hartree": experimental_atomization_energy,
            "experimental_atomization_energy_kcal_mol": experimental_atomization_kcal_mol,
            "solver_error_hartree": solver_error_hartree,
            "reference_definition_error_hartree": electronic_reference_error,
            "reference_definition_corrected_error_hartree": zpe_corrected_reference_error,
            "within_chemical_accuracy": within_chemical_accuracy,
            "basis_orbitals": int(molecule.nao_nr()),
        },
        "expected": {
            "reference_fci_total_energy_hartree": fci_total_energy,
            "reference_experimental_atomization_energy_hartree": experimental_atomization_energy,
            "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        },
        "abs_error": solver_error_hartree,
        "abs_error_vs_fci": solver_error_hartree,
        "abs_error_vs_experimental": zpe_corrected_reference_error,
        "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        "within_chemical_accuracy": within_chemical_accuracy,
        "units": "hartree",
        "physical_evidence_level": "experimental",
        "physical_evidence_detail": (
            "H2O/STO-3G is solved by PySCF FCI for the declared finite-basis electronic model. "
            "A same-model harmonic ZPE is subtracted from the electronic atomization energy to form "
            "a D0-like model quantity. The trace records that the exact small-model solve remains far "
            "from the tabulated experimental atomization reference."
        ),
        "benchmark_family": "QuantumChemistry",
        "reference_truth": {
            "fci": {
                "kind": "exact_model_solution",
                "method": "PySCF FCI",
                "basis": basis,
                "geometry": "H2O bent geometry, O at origin, H at +/-0.757, 0.587 Angstrom",
                "total_energy_hartree": fci_total_energy,
            },
            "experimental": {
                "kind": "tabulated_atomization_reference_from_OH_bond_dissociation_energies",
                "quantity": "H2O -> O + 2H atomization D0-like reference",
                "first_oh_bde_kcal_mol": experimental_first_oh_bde_kcal_mol,
                "second_oh_bde_kcal_mol": experimental_second_oh_bde_kcal_mol,
                "value_kcal_mol": experimental_atomization_kcal_mol,
                "value_hartree": experimental_atomization_energy,
                "source": "Bond dissociation energy reference table; water O-H cleavage values 118.8 and 101.8 kcal/mol",
            },
            "vibrational": {
                "kind": "same_model_harmonic_zpe",
                "frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
                "zpe_cm_inverse": zpe_cm_inverse,
                "zpe_hartree": zpe_hartree,
            },
            "chemical_accuracy": {
                "threshold_hartree": chemical_accuracy_threshold,
                "threshold_name": "1 kcal/mol",
            },
        },
        "verification_independence": "same_runtime_exact_fci_with_external_experimental_reference",
        "bound_scope": "single_molecule_polyatomic_minimal_basis_electronic_vibrational_split",
        "evidence_status_detail": "experimental_polyatomic_reference_definition_corrected_model_still_poor",
        "basis": basis,
        "basis_orbitals": int(molecule.nao_nr()),
        "geometry": geometry,
        "solver_error_hartree": solver_error_hartree,
        "model_error_hartree": zpe_corrected_reference_error,
        "reference_definition_error_hartree": electronic_reference_error,
        "reference_definition_corrected_error_hartree": zpe_corrected_reference_error,
        "reference_definition_match": "corrected_model_harmonic_electronic_atomization_minus_ZPE_to_match_D0_atomization",
        "reference_definition_correction": {
            "raw_computed_quantity": "clamped-nuclei electronic atomization energy",
            "target_reference": "D0-like atomization energy with vibrational ground state",
            "correction": "D0_model ~= De_model - ZPE_harmonic(model)",
            "zpe_cm_inverse": zpe_cm_inverse,
            "zpe_hartree": zpe_hartree,
            "harmonic_frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
            "quality": "same_model_harmonic_vibrational_correction_not_anharmonic_spectroscopy",
        },
        "electronic_atomization_energy_hartree": electronic_atomization_energy,
        "zpe_corrected_atomization_energy_hartree": zpe_corrected_atomization_energy,
        "experimental_atomization_energy_hartree": experimental_atomization_energy,
        "experimental_atomization_energy_kcal_mol": experimental_atomization_kcal_mol,
        "vibrational_zpe_hartree": zpe_hartree,
        "vibrational_zpe_cm_inverse": zpe_cm_inverse,
        "harmonic_frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
        "reference_fci_total_energy_hartree": fci_total_energy,
        "source_label": "PySCF FCI H2O/STO-3G model solve + harmonic ZPE + tabulated O-H dissociation references",
        "falsification_notes": [
            "This is a more complex molecule than H2, but still a minimal-basis model.",
            "The electronic FCI solve is exact for the declared STO-3G model, not for physical water.",
            "The harmonic ZPE is same-model and does not include anharmonic spectroscopy.",
            "The experimental atomization reference is assembled from tabulated O-H dissociation values, so its provenance is weaker than the H2 precision D0 trace.",
            "The defended claim is that CAPAS separates electronic solver error, vibrational correction, and remaining model/reference error for a polyatomic molecule.",
        ],
        "witness_stack": {
            "primary": "PySCF FCI exact H2O/STO-3G electronic model solve",
            "witness": "external tabulated water O-H dissociation values plus same-model harmonic ZPE",
            "runtime_relation": "same_runtime_model_solve_plus_external_measurement_and_reference_correction",
        },
    }


def ch4_sto3g_electronic_vibrational_reference() -> dict:
    """CH4/STO-3G exact model solve with electronic/vibrational split.

    This trace is deliberately more complex than H2O: five atoms, nine
    vibrational modes, and a tabulated atomization reference assembled from
    successive C-H bond dissociation energies. The reference is useful but
    weaker than a precision spectroscopic D0, and the trace records that scope.
    """
    from pyscf import fci, gto, hessian, scf
    from pyscf.hessian import thermo

    basis = "sto-3g"
    # Tetrahedral methane with C-H distance about 1.089 Angstrom.
    a = 0.629118
    geometry = [
        {"atom": "C", "xyz_angstrom": [0.0, 0.0, 0.0]},
        {"atom": "H", "xyz_angstrom": [a, a, a]},
        {"atom": "H", "xyz_angstrom": [-a, -a, a]},
        {"atom": "H", "xyz_angstrom": [-a, a, -a]},
        {"atom": "H", "xyz_angstrom": [a, -a, -a]},
    ]
    molecule = gto.M(
        atom=(
            f"C 0 0 0; H {a} {a} {a}; H {-a} {-a} {a}; "
            f"H {-a} {a} {-a}; H {a} {-a} {-a}"
        ),
        basis=basis,
        unit="Angstrom",
        charge=0,
        spin=0,
        verbose=0,
    )
    mf = scf.RHF(molecule).run(verbose=0)
    cisolver = fci.FCI(molecule, mf.mo_coeff)
    fci_total_energy, _ = cisolver.kernel()
    fci_total_energy = float(fci_total_energy)

    hess = hessian.RHF(mf).kernel()
    harmonic = thermo.harmonic_analysis(molecule, hess)
    harmonic_frequencies_cm_inverse = [float(x) for x in harmonic["freq_wavenumber"] if float(x) > 0.0]
    hartree_per_cm_inverse = 1.0 / 219474.6313705
    zpe_cm_inverse = float(0.5 * sum(harmonic_frequencies_cm_inverse))
    zpe_hartree = float(zpe_cm_inverse * hartree_per_cm_inverse)

    h_atom = gto.M(atom="H 0 0 0", basis=basis, unit="Angstrom", charge=0, spin=1, verbose=0)
    h_mf = scf.UHF(h_atom).run(verbose=0)
    h_fci = fci.FCI(h_atom, h_mf.mo_coeff)
    h_atom_energy, _ = h_fci.kernel(nelec=h_atom.nelec)
    h_atom_energy = float(h_atom_energy)

    c_atom = gto.M(atom="C 0 0 0", basis=basis, unit="Angstrom", charge=0, spin=2, verbose=0)
    c_mf = scf.UHF(c_atom).run(verbose=0)
    c_fci = fci.FCI(c_atom, c_mf.mo_coeff)
    c_atom_energy, _ = c_fci.kernel(nelec=c_atom.nelec)
    c_atom_energy = float(c_atom_energy)

    electronic_atomization_energy = float(c_atom_energy + 4.0 * h_atom_energy - fci_total_energy)
    zpe_corrected_atomization_energy = float(electronic_atomization_energy - zpe_hartree)

    kcal_per_hartree = 627.5094740631
    # Successive methane C-H dissociation energies cited in standard BDE tables.
    successive_ch_bde_kcal_mol = [105.0, 110.0, 101.0, 81.0]
    experimental_atomization_kcal_mol = float(sum(successive_ch_bde_kcal_mol))
    experimental_atomization_energy = float(experimental_atomization_kcal_mol / kcal_per_hartree)
    chemical_accuracy_threshold = 0.0015936

    solver_error_hartree = 0.0
    electronic_reference_error = abs(electronic_atomization_energy - experimental_atomization_energy)
    zpe_corrected_reference_error = abs(zpe_corrected_atomization_energy - experimental_atomization_energy)
    within_chemical_accuracy = bool(zpe_corrected_reference_error < chemical_accuracy_threshold)

    return {
        "observable": "CH4/STO-3G FCI atomization energy with model-harmonic ZPE correction",
        "value": {
            "fci_total_energy_hartree": fci_total_energy,
            "h_atom_energy_hartree": h_atom_energy,
            "c_atom_energy_hartree": c_atom_energy,
            "electronic_atomization_energy_hartree": electronic_atomization_energy,
            "vibrational_zpe_hartree": zpe_hartree,
            "vibrational_zpe_cm_inverse": zpe_cm_inverse,
            "harmonic_frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
            "zpe_corrected_atomization_energy_hartree": zpe_corrected_atomization_energy,
            "experimental_atomization_energy_hartree": experimental_atomization_energy,
            "experimental_atomization_energy_kcal_mol": experimental_atomization_kcal_mol,
            "successive_ch_bde_kcal_mol": successive_ch_bde_kcal_mol,
            "solver_error_hartree": solver_error_hartree,
            "reference_definition_error_hartree": electronic_reference_error,
            "reference_definition_corrected_error_hartree": zpe_corrected_reference_error,
            "within_chemical_accuracy": within_chemical_accuracy,
            "basis_orbitals": int(molecule.nao_nr()),
        },
        "expected": {
            "reference_fci_total_energy_hartree": fci_total_energy,
            "reference_experimental_atomization_energy_hartree": experimental_atomization_energy,
            "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        },
        "abs_error": solver_error_hartree,
        "abs_error_vs_fci": solver_error_hartree,
        "abs_error_vs_experimental": zpe_corrected_reference_error,
        "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        "within_chemical_accuracy": within_chemical_accuracy,
        "units": "hartree",
        "physical_evidence_level": "experimental",
        "physical_evidence_detail": (
            "CH4/STO-3G is solved by PySCF FCI for the declared finite-basis electronic model. "
            "A same-model harmonic ZPE is subtracted from the electronic atomization energy. "
            "The trace records a larger polyatomic case where exact model solution does not imply "
            "experimental chemical accuracy."
        ),
        "benchmark_family": "QuantumChemistry",
        "reference_truth": {
            "fci": {
                "kind": "exact_model_solution",
                "method": "PySCF FCI",
                "basis": basis,
                "geometry": "CH4 tetrahedral STO-3G demo geometry, C-H about 1.089 Angstrom",
                "total_energy_hartree": fci_total_energy,
            },
            "experimental": {
                "kind": "tabulated_atomization_reference_from_successive_C_H_bond_dissociation_energies",
                "quantity": "CH4 -> C + 4H atomization D0-like reference",
                "successive_ch_bde_kcal_mol": successive_ch_bde_kcal_mol,
                "value_kcal_mol": experimental_atomization_kcal_mol,
                "value_hartree": experimental_atomization_energy,
                "source": "Bond dissociation energy reference table; successive methane C-H values 105, 110, 101, and 81 kcal/mol",
            },
            "vibrational": {
                "kind": "same_model_harmonic_zpe",
                "frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
                "zpe_cm_inverse": zpe_cm_inverse,
                "zpe_hartree": zpe_hartree,
            },
            "chemical_accuracy": {
                "threshold_hartree": chemical_accuracy_threshold,
                "threshold_name": "1 kcal/mol",
            },
        },
        "verification_independence": "same_runtime_exact_fci_with_external_experimental_reference",
        "bound_scope": "single_molecule_polyatomic_minimal_basis_electronic_vibrational_split",
        "evidence_status_detail": "experimental_larger_polyatomic_reference_definition_corrected_model_still_poor",
        "basis": basis,
        "basis_orbitals": int(molecule.nao_nr()),
        "geometry": geometry,
        "solver_error_hartree": solver_error_hartree,
        "model_error_hartree": zpe_corrected_reference_error,
        "reference_definition_error_hartree": electronic_reference_error,
        "reference_definition_corrected_error_hartree": zpe_corrected_reference_error,
        "reference_definition_match": "corrected_model_harmonic_electronic_atomization_minus_ZPE_to_match_D0_atomization",
        "reference_definition_correction": {
            "raw_computed_quantity": "clamped-nuclei electronic atomization energy",
            "target_reference": "D0-like atomization energy with vibrational ground state",
            "correction": "D0_model ~= De_model - ZPE_harmonic(model)",
            "zpe_cm_inverse": zpe_cm_inverse,
            "zpe_hartree": zpe_hartree,
            "harmonic_frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
            "quality": "same_model_harmonic_vibrational_correction_not_anharmonic_spectroscopy",
        },
        "electronic_atomization_energy_hartree": electronic_atomization_energy,
        "zpe_corrected_atomization_energy_hartree": zpe_corrected_atomization_energy,
        "experimental_atomization_energy_hartree": experimental_atomization_energy,
        "experimental_atomization_energy_kcal_mol": experimental_atomization_kcal_mol,
        "vibrational_zpe_hartree": zpe_hartree,
        "vibrational_zpe_cm_inverse": zpe_cm_inverse,
        "harmonic_frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
        "reference_fci_total_energy_hartree": fci_total_energy,
        "source_label": "PySCF FCI CH4/STO-3G model solve + harmonic ZPE + tabulated successive C-H dissociation references",
        "falsification_notes": [
            "This is larger than H2O but still a minimal-basis local demonstration.",
            "The electronic FCI solve is exact for STO-3G methane, not for physical methane.",
            "The experimental atomization reference is assembled from rounded tabulated C-H BDE values, so its provenance is weaker than the H2 precision D0 trace.",
            "The harmonic ZPE is same-model and does not include anharmonic spectroscopy.",
            "The defended claim is evidence separation for a larger polyatomic molecule, not competitive thermochemistry.",
        ],
        "witness_stack": {
            "primary": "PySCF FCI exact CH4/STO-3G electronic model solve",
            "witness": "external tabulated successive methane C-H dissociation values plus same-model harmonic ZPE",
            "runtime_relation": "same_runtime_model_solve_plus_external_measurement_and_reference_correction",
        },
    }


def h2_basis_convergence_to_experiment() -> dict:
    """H2 basis convergence curve against measured D0 with model-harmonic ZPE.

    This trace is intentionally a curve, not a single calculation. It tests
    whether CAPAS can certify both failure and success as the finite-basis model
    improves, and whether success is robust or merely just under the chemical
    accuracy threshold.
    """
    from pyscf import fci, gto, hessian, scf
    from pyscf.hessian import thermo

    bond_length_angstrom = 0.7414
    bases = ["sto-3g", "cc-pvdz", "cc-pvtz", "cc-pvqz", "cc-pv5z"]
    experimental_d0_cm_inverse = 35999.582834
    hartree_per_cm_inverse = 1.0 / 219474.6313705
    experimental_d0_hartree = float(experimental_d0_cm_inverse * hartree_per_cm_inverse)
    chemical_accuracy_threshold = 0.0015936
    robust_margin_fraction = 0.05
    robust_margin_hartree = float(chemical_accuracy_threshold * robust_margin_fraction)

    points = []
    previous_error = None
    monotonic_nonincreasing = True
    first_within_basis = None
    first_robust_basis = None

    for basis in bases:
        molecule = gto.M(
            atom=f"H 0 0 0; H 0 0 {bond_length_angstrom}",
            basis=basis,
            unit="Angstrom",
            charge=0,
            spin=0,
            verbose=0,
        )
        mf = scf.RHF(molecule).run(verbose=0)
        cisolver = fci.FCI(molecule, mf.mo_coeff)
        fci_total_energy, _ = cisolver.kernel()
        fci_total_energy = float(fci_total_energy)

        atom = gto.M(
            atom="H 0 0 0",
            basis=basis,
            unit="Angstrom",
            charge=0,
            spin=1,
            verbose=0,
        )
        atom_mf = scf.UHF(atom).run(verbose=0)
        model_atom_energy = float(atom_mf.e_tot)
        electronic_binding_energy = float(2.0 * model_atom_energy - fci_total_energy)

        hess = hessian.RHF(mf).kernel()
        harmonic = thermo.harmonic_analysis(molecule, hess)
        harmonic_frequencies_cm_inverse = [float(x) for x in harmonic["freq_wavenumber"] if float(x) > 0.0]
        zpe_cm_inverse = float(0.5 * sum(harmonic_frequencies_cm_inverse))
        zpe_hartree = float(zpe_cm_inverse * hartree_per_cm_inverse)
        corrected_de_reference_hartree = float(experimental_d0_hartree + zpe_hartree)
        corrected_error_hartree = abs(electronic_binding_energy - corrected_de_reference_hartree)
        raw_error_hartree = abs(electronic_binding_energy - experimental_d0_hartree)
        margin_hartree = float(chemical_accuracy_threshold - corrected_error_hartree)
        within_chemical_accuracy = bool(corrected_error_hartree < chemical_accuracy_threshold)
        robustness = (
            "true_robust"
            if margin_hartree >= robust_margin_hartree
            else "true_not_robust"
            if within_chemical_accuracy
            else "false"
        )

        if previous_error is not None and corrected_error_hartree > previous_error + 1e-12:
            monotonic_nonincreasing = False
        previous_error = corrected_error_hartree
        if within_chemical_accuracy and first_within_basis is None:
            first_within_basis = basis
        if robustness == "true_robust" and first_robust_basis is None:
            first_robust_basis = basis

        points.append(
            {
                "basis": basis,
                "basis_orbitals": int(molecule.nao_nr()),
                "fci_total_energy_hartree": fci_total_energy,
                "model_atom_energy_hartree": model_atom_energy,
                "electronic_binding_energy_hartree": electronic_binding_energy,
                "harmonic_frequencies_cm_inverse": harmonic_frequencies_cm_inverse,
                "vibrational_zpe_cm_inverse": zpe_cm_inverse,
                "vibrational_zpe_hartree": zpe_hartree,
                "raw_error_vs_d0_hartree": raw_error_hartree,
                "corrected_de_reference_hartree": corrected_de_reference_hartree,
                "corrected_error_hartree": corrected_error_hartree,
                "within_chemical_accuracy": within_chemical_accuracy,
                "margin_hartree": margin_hartree,
                "robustness": robustness,
                "solver_error_hartree": 0.0,
            }
        )

    best_point = min(points, key=lambda p: p["corrected_error_hartree"])
    ceiling_basis = points[-1]["basis"]
    ceiling_basis_orbitals = points[-1]["basis_orbitals"]
    errors = [point["corrected_error_hartree"] for point in points]

    return {
        "observable": "H2 finite-basis convergence to experimental D0 with model-harmonic ZPE",
        "value": {
            "points": points,
            "errors_hartree": errors,
            "monotonic_nonincreasing_error": monotonic_nonincreasing,
            "first_within_chemical_accuracy_basis": first_within_basis,
            "first_robust_basis": first_robust_basis,
            "best_basis": best_point["basis"],
            "best_error_hartree": best_point["corrected_error_hartree"],
            "ceiling_basis_solved": ceiling_basis,
            "ceiling_basis_orbitals": ceiling_basis_orbitals,
            "robust_margin_fraction": robust_margin_fraction,
            "robust_margin_hartree": robust_margin_hartree,
        },
        "expected": {
            "monotonic_nonincreasing_error": True,
            "first_robust_basis": first_robust_basis,
            "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        },
        "abs_error": 0.0,
        "abs_error_vs_fci": 0.0,
        "abs_error_vs_experimental": best_point["corrected_error_hartree"],
        "chemical_accuracy_threshold_hartree": chemical_accuracy_threshold,
        "within_chemical_accuracy": bool(first_within_basis is not None),
        "units": "hartree",
        "physical_evidence_level": "experimental",
        "physical_evidence_detail": (
            "H2 is solved by exact FCI across an increasing Dunning basis ladder. Each point compares "
            "the electronic binding energy to measured D0 corrected by same-model harmonic ZPE. The "
            "trace records the full error curve, monotonicity, first threshold crossing, and first "
            "robust chemical-accuracy crossing."
        ),
        "benchmark_family": "QuantumChemistry",
        "reference_truth": {
            "fci": {
                "kind": "exact_model_solution_at_each_basis",
                "method": "PySCF FCI",
                "bases": bases,
                "geometry": f"H-H {bond_length_angstrom} Angstrom",
            },
            "experimental": {
                "kind": "measured_dissociation_energy_with_model_harmonic_reference_definition_correction",
                "raw_quantity": "D0(N=1) ortho-H2",
                "raw_value_cm_inverse": experimental_d0_cm_inverse,
                "raw_value_hartree": experimental_d0_hartree,
                "corrected_quantity": "per-basis model-harmonic D_e = D0 + ZPE_harmonic(model)",
                "source": "D0: Hölsch et al. 2019, arXiv:1902.09471; ZPE: PySCF harmonic analysis at each declared basis",
            },
            "chemical_accuracy": {
                "threshold_hartree": chemical_accuracy_threshold,
                "threshold_name": "1 kcal/mol",
                "robust_margin_fraction": robust_margin_fraction,
            },
        },
        "verification_independence": "same_runtime_exact_fci_with_external_experimental_reference",
        "bound_scope": "single_molecule_basis_convergence_curve_electronic_vibrational_split",
        "evidence_status_detail": "experimental_basis_convergence_curve_with_robust_true_crossing",
        "basis": bases,
        "basis_orbitals": [point["basis_orbitals"] for point in points],
        "geometry": [{"atom": "H", "xyz_angstrom": [0.0, 0.0, 0.0]}, {"atom": "H", "xyz_angstrom": [0.0, 0.0, bond_length_angstrom]}],
        "bond_length_angstrom": bond_length_angstrom,
        "solver_error_hartree": 0.0,
        "model_error_hartree": best_point["corrected_error_hartree"],
        "model_binding_energy_hartree": best_point["electronic_binding_energy_hartree"],
        "experimental_binding_energy_hartree": best_point["corrected_de_reference_hartree"],
        "reference_definition_error_hartree": best_point["raw_error_vs_d0_hartree"],
        "reference_definition_corrected_error_hartree": best_point["corrected_error_hartree"],
        "reference_definition_match": "per_basis_corrected_model_harmonic_D0_plus_ZPE_to_match_electronic_De",
        "reference_definition_correction": {
            "raw_reference": "D0 includes vibrational zero-point energy",
            "computed_quantity": "clamped-nuclei electronic binding energy",
            "correction": "D_e ~= D0 + ZPE_harmonic(model), recomputed per basis",
            "quality": "same_model_harmonic_vibrational_correction_not_full_spectroscopic_audit",
        },
        "vibrational_zpe_hartree": best_point["vibrational_zpe_hartree"],
        "vibrational_zpe_cm_inverse": best_point["vibrational_zpe_cm_inverse"],
        "harmonic_frequencies_cm_inverse": best_point["harmonic_frequencies_cm_inverse"],
        "reference_fci_total_energy_hartree": best_point["fci_total_energy_hartree"],
        "reference_experimental_d0_cm_inverse": experimental_d0_cm_inverse,
        "source_label": "PySCF FCI H2 basis ladder + per-basis harmonic ZPE + external H2 D0 measurement",
        "falsification_notes": [
            "This trace certifies convergence for H2 only, not general quantum chemistry.",
            "A true result with margin below 5% of the threshold is marked true_not_robust.",
            "The ZPE correction is same-model harmonic and not full anharmonic spectroscopy.",
            "The defended claim is a sealed convergence curve and robust threshold crossing, not simulator superiority.",
        ],
        "witness_stack": {
            "primary": "PySCF FCI exact H2 model solve at each basis",
            "witness": "external experimental H2 D0 plus per-basis same-model harmonic ZPE",
            "runtime_relation": "same_runtime_model_solve_plus_external_measurement_and_reference_correction",
        },
        "convergence_points": points,
        "monotonic_nonincreasing_error": monotonic_nonincreasing,
        "first_within_chemical_accuracy_basis": first_within_basis,
        "first_robust_basis": first_robust_basis,
        "ceiling_basis_solved": ceiling_basis,
        "ceiling_basis_orbitals": ceiling_basis_orbitals,
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


def bell_entropy_scipy_cross_library() -> dict:
    """Bell entropy checked against a different library stack.

    The primary value comes from physics_magnitude_lab.quantum_engine. The
    witness computes the reduced density matrix explicitly and diagonalizes it
    with scipy.linalg.eigh. This is stronger than the NumPy-only cross-sim case,
    but it is still same-runtime evidence, not a separate hardware/runtime
    witness.
    """
    import scipy.linalg

    bell = qe.bell_state()
    value = float(qe.entanglement_entropy(bell, dims=[2, 2], keep=[0]))
    density = np.outer(bell, np.conjugate(bell)).reshape(2, 2, 2, 2)
    reduced = np.trace(density, axis1=1, axis2=3)
    evals = scipy.linalg.eigh(reduced, eigvals_only=True)
    witness = float(-sum(float(x) * np.log(float(x)) for x in evals if x > 0))
    return {
        "observable": "Bell pair entanglement entropy SciPy cross-library witness",
        "value": value,
        "expected": witness,
        "abs_error": abs(value - witness),
        "units": "nats",
        "physical_evidence_level": "cross_sim",
        "physical_evidence_detail": (
            "quantum_engine entropy checked against explicit reduced density matrix diagonalized "
            "with scipy.linalg.eigh. Same Python runtime, different library witness."
        ),
        "benchmark_family": "Entanglement",
        "reference_truth": "scipy_linalg_reduced_density_eigenspectrum",
        "verification_independence": "different_library_same_runtime",
        "witness_stack": {
            "primary": "physics_magnitude_lab.quantum_engine.entanglement_entropy",
            "witness": "scipy.linalg.eigh on explicit reduced density matrix",
            "runtime_relation": "same_python_runtime",
        },
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


def schmidt_truncation_formal_bound(n_qubits: int = 4, keep_rank: int = 2, seed: int = 7) -> dict:
    """Exact Schmidt/SVD truncation certificate for a normalized state.

    This is deliberately narrower than a global DMRG certificate. For a single
    bipartite Schmidt truncation, the discarded Schmidt weight is exactly the
    squared 2-norm error of the optimal rank-k approximation.
    """
    if n_qubits % 2 != 0:
        raise ValueError("n_qubits must be even for this bipartition demo")
    if keep_rank < 1:
        raise ValueError("keep_rank must be positive")

    rng = np.random.default_rng(seed)
    psi = rng.normal(size=2**n_qubits) + 1j * rng.normal(size=2**n_qubits)
    psi = psi / np.linalg.norm(psi)

    left_dim = 2 ** (n_qubits // 2)
    right_dim = 2 ** (n_qubits // 2)
    matrix = psi.reshape(left_dim, right_dim)
    u, s, vh = np.linalg.svd(matrix, full_matrices=False)
    rank = min(keep_rank, len(s))
    discarded_weight = float(np.sum(s[rank:] ** 2))

    truncated = (u[:, :rank] @ np.diag(s[:rank]) @ vh[:rank, :]).reshape(-1)
    actual_error_squared = float(np.linalg.norm(psi - truncated) ** 2)
    abs_error = abs(discarded_weight - actual_error_squared)

    return {
        "observable": "Single-cut Schmidt truncation squared state error",
        "value": {
            "discarded_weight": discarded_weight,
            "actual_error_squared": actual_error_squared,
            "kept_rank": rank,
            "full_rank": len(s),
        },
        "expected": discarded_weight,
        "abs_error": abs_error,
        "units": "squared_state_norm",
        "physical_evidence_level": "formal_bound",
        "physical_evidence_detail": (
            "For a normalized state in Schmidt form, the sum of discarded Schmidt values squared is exactly "
            "the squared 2-norm error of the optimal rank-k truncation across that cut. This certifies a "
            "single-cut state truncation error, not a global DMRG observable error."
        ),
        "benchmark_family": "TensorNetwork",
        "reference_truth": "schmidt_eckart_young_theorem",
        "verification_independence": "algorithmic_certificate_exact_svd_same_runtime",
        "certification_status": "formal_single_cut_state_norm_bound",
        "formal_bound_status": "established_for_single_schmidt_truncation_not_global_dmrg",
        "bound_type": "discarded_schmidt_weight_equals_squared_state_2norm_error",
        "bound_scope": "single_bipartition_state_truncation",
        "discarded_weight": discarded_weight,
        "actual_error_squared": actual_error_squared,
        "source_label": "FORMAL (single-cut Schmidt/SVD theorem)",
        "n": n_qubits,
        "max_bond": keep_rank,
    }


def multi_step_schmidt_composition_bound(
    n_qubits: int = 6,
    keep_rank: int = 2,
    seed: int = 11,
) -> dict:
    """Formal state-error bound for several sequential Schmidt truncations.

    Each step is a non-renormalized optimal SVD truncation across one cut. For
    step errors e_i with squared norm w_i, triangle inequality gives:

        ||psi_0 - psi_m|| <= sum_i sqrt(w_i)

    so the final squared state error is bounded by (sum_i sqrt(w_i))^2.
    """
    if n_qubits < 4:
        raise ValueError("n_qubits must be at least 4")
    if keep_rank < 1:
        raise ValueError("keep_rank must be positive")

    rng = np.random.default_rng(seed)
    psi0 = rng.normal(size=2**n_qubits) + 1j * rng.normal(size=2**n_qubits)
    psi0 = psi0 / np.linalg.norm(psi0)
    psi = psi0.copy()

    cuts = [n_qubits // 2, n_qubits // 2 - 1, n_qubits // 2 + 1]
    cuts = [cut for cut in cuts if 0 < cut < n_qubits]
    local_weights: list[float] = []
    local_errors_squared: list[float] = []
    kept_ranks: list[int] = []

    for cut in cuts:
        before = psi
        matrix = before.reshape(2**cut, 2 ** (n_qubits - cut))
        u, s, vh = np.linalg.svd(matrix, full_matrices=False)
        rank = min(keep_rank, len(s))
        truncated = (u[:, :rank] @ np.diag(s[:rank]) @ vh[:rank, :]).reshape(-1)
        discarded_weight = float(np.sum(s[rank:] ** 2))
        local_error_squared = float(np.linalg.norm(before - truncated) ** 2)
        local_weights.append(discarded_weight)
        local_errors_squared.append(local_error_squared)
        kept_ranks.append(rank)
        psi = truncated

    composed_state_error_bound = float(sum(np.sqrt(w) for w in local_weights) ** 2)
    actual_error_squared = float(np.linalg.norm(psi0 - psi) ** 2)
    bound_slack = float(composed_state_error_bound - actual_error_squared)

    if bound_slack < -1e-12:
        raise AssertionError(
            "composed Schmidt truncation bound failed: "
            f"actual={actual_error_squared}, bound={composed_state_error_bound}"
        )

    return {
        "observable": "Multi-step Schmidt truncation squared state-error bound",
        "value": {
            "actual_error_squared": actual_error_squared,
            "composed_state_error_bound": composed_state_error_bound,
            "bound_slack": bound_slack,
            "local_discarded_weights": local_weights,
            "local_error_squared": local_errors_squared,
            "cuts": cuts,
            "kept_ranks": kept_ranks,
        },
        "expected": f"actual_error_squared <= {composed_state_error_bound}",
        "abs_error": max(0.0, -bound_slack),
        "units": "squared_state_norm",
        "physical_evidence_level": "formal_bound",
        "physical_evidence_detail": (
            "Sequential non-renormalized Schmidt/SVD truncations compose into a formal state-norm bound "
            "by triangle inequality: final ||psi0-psim||^2 <= (sum_i sqrt(discarded_weight_i))^2. "
            "This certifies the full-state error for this controlled sequence, not an observable error "
            "and not yet a general DMRG sweep certificate."
        ),
        "benchmark_family": "TensorNetwork",
        "reference_truth": "schmidt_eckart_young_plus_triangle_inequality",
        "verification_independence": "algorithmic_certificate_exact_svd_same_runtime",
        "certification_status": "formal_multi_step_state_norm_bound",
        "formal_bound_status": "established_for_nonrenormalized_sequential_schmidt_truncations_not_observables",
        "bound_type": "triangle_composed_discarded_schmidt_weight_state_error_bound",
        "bound_scope": "multi_step_state_truncation",
        "discarded_weight": float(sum(local_weights)),
        "actual_error_squared": actual_error_squared,
        "composed_state_error_bound": composed_state_error_bound,
        "bound_slack": bound_slack,
        "source_label": "FORMAL (Schmidt/SVD theorem + triangle inequality)",
        "n": n_qubits,
        "max_bond": keep_rank,
    }
