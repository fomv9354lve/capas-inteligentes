"""CAPAS — the verified knowledge braid: grounding by position, not self-assertion.

The topological/relational horizon. A claim's certification is stored NOT in a
node's own self-assertion (the Löbian trap — no node certifies itself) but in its
POSITION in a growing braid of verified claims linked by reciprocity. Two grounded
claims that re-derive the SAME target by DIFFERENT methods CORRESPOND (ayni /
perichoretic mutual support); two that disagree on the same target are a braid
FAULT — caught by the whole even when each is locally grounded.

The braid carries a non-local compressed invariant (a Merkle root over all node
invariants — the "Jones polynomial" of the knowledge structure): tampering any one
node's content changes the global root, so a forged claim cannot sit in the braid
without breaking it. This is "closed locally (each node is a hard deterministic
receipt), open globally (the braid grows; the root never self-certifies, only
re-roots forward)". Grounding by the whole, not the node.

Built on capas_rcc (only GROUNDED claims enter the braid). Local truth is the
node's receipt; braid coherence is reciprocity across methods — and the second
catches what the first cannot.
"""
from __future__ import annotations

import hashlib
from typing import Any

import capas_rcc


def _h(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def _merkle(leaves: list[str]) -> str:
    if not leaves:
        return _h("empty")
    layer = [_h(x) for x in leaves]
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [_h(layer[i], layer[i + 1]) for i in range(0, len(layer), 2)]
    return layer[0]


class Braid:
    def __init__(self, tol: float = 1e-6) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}     # claim_id -> node
        self.edges: list[dict[str, Any]] = []          # {a, b, type: corresponds|contradicts}
        self.tol = tol

    def _invariant(self, target: str, value: float, method: str, receipt_id: str) -> str:
        return "node:" + _h(str(target), repr(float(value)), str(method), str(receipt_id))

    def root(self) -> str:
        """The non-local compressed invariant over the whole braid."""
        return "braidroot:" + _merkle(sorted(n["invariant"] for n in self.nodes.values()))

    def add(self, payload: dict[str, Any], target: str, value: float, method: str) -> dict[str, Any]:
        """Add a claim to the braid iff it is GROUNDED locally; then relate it to
        existing same-target nodes (reciprocity) and surface any braid fault."""
        cert = capas_rcc.rcc(payload)
        if not str(cert.get("headline", "")).startswith("GROUNDED"):
            return {"added": False, "reason": "not locally grounded", "headline": cert.get("headline")}
        cid = (payload.get("claim") or {}).get("id") or _h(str(target), method)
        inv = self._invariant(target, value, method, cert.get("certificate_id", ""))
        corresponds, contradicts = [], []
        for oid, n in self.nodes.items():
            if n["target"] != target:
                continue
            if abs(n["value"] - value) <= self.tol:
                self.edges.append({"a": cid, "b": oid, "type": "corresponds"})
                corresponds.append(oid)
            else:
                self.edges.append({"a": cid, "b": oid, "type": "contradicts"})
                contradicts.append(oid)
        self.nodes[cid] = {"invariant": inv, "target": target, "value": float(value),
                           "method": method, "receipt_id": cert.get("certificate_id")}
        return {"added": True, "claim_id": cid, "corresponds": corresponds,
                "contradicts": contradicts, "braid_fault": bool(contradicts), "root": self.root()}

    def reciprocal_support(self, cid: str) -> int:
        return sum(1 for e in self.edges if e["type"] == "corresponds" and cid in (e["a"], e["b"]))

    def faults(self) -> list[dict[str, Any]]:
        """Same-target disagreements: locally grounded yet braid-incoherent."""
        seen, out = set(), []
        for e in self.edges:
            if e["type"] == "contradicts":
                k = frozenset((e["a"], e["b"]))
                if k not in seen:
                    seen.add(k)
                    a, b = self.nodes.get(e["a"], {}), self.nodes.get(e["b"], {})
                    out.append({"between": [e["a"], e["b"]], "target": a.get("target"),
                                "values": [a.get("value"), b.get("value")],
                                "methods": [a.get("method"), b.get("method")]})
        return out

    def position_certificate(self, cid: str) -> dict[str, Any]:
        """A claim's certification AS POSITION: its local invariant + the braid root
        it sits in + reciprocal support + any contradictions. Validity is a property
        of the whole, robust to local error (re-rooting on tamper)."""
        n = self.nodes.get(cid)
        if n is None:
            return {"in_braid": False}
        corr = sorted({(e["b"] if e["a"] == cid else e["a"]) for e in self.edges
                       if e["type"] == "corresponds" and cid in (e["a"], e["b"])})
        contra = sorted({(e["b"] if e["a"] == cid else e["a"]) for e in self.edges
                         if e["type"] == "contradicts" and cid in (e["a"], e["b"])})
        return {"in_braid": True, "claim_id": cid, "node_invariant": n["invariant"],
                "braid_root": self.root(), "reciprocal_support": len(corr),
                "corresponds_with": corr, "contradicts": contra,
                "braid_coherent": not contra,
                "grounding": "by position in the verified braid (the whole), not node self-assertion"}

    def tamper(self, cid: str, new_value: float) -> dict[str, Any]:
        """Mutate a node's value — to show the global invariant catches it: the root
        changes and any prior position certificate no longer matches."""
        old_root = self.root()
        n = self.nodes[cid]
        n["value"] = float(new_value)
        n["invariant"] = self._invariant(n["target"], new_value, n["method"], n["receipt_id"])
        return {"old_root": old_root, "new_root": self.root(), "root_changed": old_root != self.root()}
