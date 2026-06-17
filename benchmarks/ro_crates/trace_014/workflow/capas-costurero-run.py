"""CAPAS costurero workflow descriptor.

This file is included so the RO-Crate has a concrete workflow file entity.
The executable implementation lives in router.pipeline.run_with_trace.
"""


def capas_costurero_workflow(workload):
    """Conceptual workflow stages recorded in the sealed RunTrace."""
    ingest(workload)
    record_runtime_context()
    estimate_cost_model()
    route_workload()
    execute_or_skip_backend()
    attach_physical_evidence()
