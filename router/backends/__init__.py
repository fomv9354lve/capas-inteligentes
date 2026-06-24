# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Execution adapters for already-routed workloads.

Backends do not decide routes. They only execute a `RouteDecision` produced by
`router.route`.
"""

from .dense_backend import execute_dense_circuit
from .external_engine_backend import execute_external_engine
from .stim_backend import execute_stim_circuit
from .tensor_backend import execute_tensor_contract

__all__ = [
    "execute_dense_circuit",
    "execute_external_engine",
    "execute_stim_circuit",
    "execute_tensor_contract",
]
