cwlVersion: v1.2
class: CommandLineTool
label: CAPAS costurero workflow descriptor
doc: |
  Conceptual Workflow Run RO-Crate descriptor for the CAPAS costurero.
  The executable implementation lives in router.pipeline.run_with_trace.
  This descriptor exists so the crate has a recognized workflow entity while
  preserving Python as the implementation language in RO-Crate metadata.
baseCommand: capas-costurero-run
inputs:
  workload:
    type: File
    doc: Structured scientific workload routed by the CAPAS costurero.
outputs:
  result:
    type: File
    outputBinding:
      glob: runtrace.json
    doc: Structured RunTrace result, skipped state, or failure state.
requirements:
  InlineJavascriptRequirement: {}
