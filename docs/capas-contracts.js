/* GENERATED from capas.py by scripts/gen_gate_contracts.py — do not edit by hand.
   Single source of truth for the browser gate's evidence contracts.
   Regenerate after changing CLAIM_TYPE_REGISTRY / ANCHOR_MODE_CONTRACTS. */
window.CAPAS_CONTRACTS = {
  "anchor_mode_contracts": {
    "absolute_anchor": {
      "license": "universal-anchor claim boundary",
      "optional": [
        "physical_evidence_level",
        "verification_independence"
      ],
      "required": [
        "anchor_mode",
        "local_property_tests_pass",
        "universal_anchor_pass"
      ]
    },
    "benchmark_anchor": {
      "license": "benchmark-limited claim boundary",
      "optional": [
        "physical_evidence_level",
        "verification_independence"
      ],
      "required": [
        "anchor_mode",
        "local_property_tests_pass",
        "benchmark_name",
        "benchmark_metric",
        "benchmark_pass"
      ]
    },
    "empirical_anchor": {
      "license": "bounded empirical-agreement claim boundary",
      "optional": [
        "physical_evidence_level",
        "verification_independence"
      ],
      "required": [
        "anchor_mode",
        "local_property_tests_pass",
        "empirical_reference_present",
        "empirical_tolerance",
        "empirical_anchor_pass"
      ]
    },
    "relative_anchor": {
      "license": "comparison-only claim boundary",
      "optional": [
        "physical_evidence_level",
        "verification_independence"
      ],
      "required": [
        "anchor_mode",
        "local_property_tests_pass",
        "relative_anchor_reference",
        "relative_anchor_comparison_pass"
      ]
    }
  },
  "descriptions": {
    "causal_mechanism_claim": "Causal-mechanism claims requiring design, temporal, confounder, and mechanism evidence.",
    "claim_transition": "Claims that upgrade a weaker licensed statement to a stronger one.",
    "evidence_conflict_claim": "Claims that resolve disclosed supporting and contradicting evidence.",
    "exact_model_solution": "Exact or bounded-error model solution claims.",
    "financial_metric_claim": "Financial metric claims against a reference value and period.",
    "multimodal_evidence_claim": "Claims supported by declared multimodal evidence and extraction method.",
    "physical_accuracy": "Direct physical or chemical-accuracy claims.",
    "programming_language_behavior_claim": "Executable programming-language behavior claims requiring snippet, runtime, and observed output evidence.",
    "reproducibility_check": "Artifact availability and independent reproduction claims.",
    "statistical_confidence": "Statistical threshold and effect-direction claims.",
    "systematic_review_claim": "Systematic-review claims requiring protocol, inclusion, bias, and consistency evidence.",
    "universal_anchor_claim": "Claims that require an explicit anchor-mode evidence contract."
  },
  "generated_from": "capas.py CLAIM_TYPE_REGISTRY + ANCHOR_MODE_CONTRACTS",
  "optional": {
    "causal_mechanism_claim": [
      "verification_independence"
    ],
    "claim_transition": [
      "current_claim"
    ],
    "evidence_conflict_claim": [],
    "exact_model_solution": [
      "bound_scope",
      "physical_evidence_level",
      "verification_independence"
    ],
    "financial_metric_claim": [
      "metric_name",
      "audit_trail"
    ],
    "multimodal_evidence_claim": [],
    "physical_accuracy": [
      "physical_evidence_level",
      "reference_truth"
    ],
    "programming_language_behavior_claim": [
      "docs_reference"
    ],
    "reproducibility_check": [],
    "statistical_confidence": [],
    "systematic_review_claim": [],
    "universal_anchor_claim": [
      "benchmark_metric",
      "benchmark_name",
      "benchmark_pass",
      "empirical_anchor_pass",
      "empirical_reference_present",
      "empirical_tolerance",
      "physical_evidence_level",
      "relative_anchor_comparison_pass",
      "relative_anchor_reference",
      "verification_independence"
    ]
  },
  "required": {
    "causal_mechanism_claim": [
      "intervention_or_natural_experiment",
      "temporal_order_established",
      "confounders_controlled",
      "mechanism_evidence_present"
    ],
    "claim_transition": [
      "upgrade_evidence_present"
    ],
    "evidence_conflict_claim": [
      "supporting_sources",
      "contradicting_sources",
      "conflict_resolution_method",
      "resolution_pre_registered"
    ],
    "exact_model_solution": [
      "abs_error",
      "tolerance"
    ],
    "financial_metric_claim": [
      "reported_value",
      "reference_value",
      "tolerance",
      "metric_period_match"
    ],
    "multimodal_evidence_claim": [
      "modality",
      "source_hashes_verified",
      "cross_modal_alignment",
      "extraction_method_declared"
    ],
    "physical_accuracy": [
      "within_chemical_accuracy"
    ],
    "programming_language_behavior_claim": [
      "language",
      "language_version",
      "claim_api",
      "code_snippet",
      "expected_output",
      "observed_output",
      "execution_observed",
      "runtime_environment_declared"
    ],
    "reproducibility_check": [
      "artifact_available",
      "independent_reproduction_pass"
    ],
    "statistical_confidence": [
      "p_value",
      "alpha",
      "effect_direction_confirmed"
    ],
    "systematic_review_claim": [
      "protocol_registered",
      "inclusion_criteria_declared",
      "risk_of_bias_assessed",
      "effect_consistency"
    ],
    "universal_anchor_claim": [
      "anchor_mode",
      "local_property_tests_pass",
      "universal_anchor_pass"
    ]
  },
  "schema_version": "capas-claim-payload-v3"
};
