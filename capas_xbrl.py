# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — XBRL extraction loop (Arelle) for financial-ratio re-derivation.

Closes the loop the SOTA review flagged: instead of a human hand-typing the line
items of a ratio, CAPAS reads them straight from a filed XBRL instance via Arelle
and feeds them to rederive_accounting(). The producer no longer chooses the
numbers that go into the re-derivation — they come from the filing itself, by
standard US-GAAP concept, for the latest reporting period.

Optional dependency: if `arelle` is not installed the module imports fine and the
xbrl evidence path is simply unavailable (capas_verify degrades gracefully).
Arelle is the mature library the review named; CAPAS consumes it, not reinvents.
"""
from __future__ import annotations

from typing import Any

# Each ratio's component -> candidate concept localNames a filer may use, across
# BOTH taxonomies: US-GAAP (us-gaap:) and IFRS (ifrs-full:, used in EU ESEF and
# most non-US filings). First match wins, so the same extractor serves either.
# rederive_accounting consumes the left-hand component keys.
_CONCEPTS: dict[str, list[str]] = {
    # component: [US-GAAP ..., IFRS ...]
    "current_assets": ["AssetsCurrent", "CurrentAssets"],
    "current_liabilities": ["LiabilitiesCurrent", "CurrentLiabilities"],
    "total_assets": ["Assets"],  # both taxonomies use "Assets"
    "total_equity": ["StockholdersEquity",
                     "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
                     "Equity", "EquityAttributableToOwnersOfParent"],
    "total_debt": ["Liabilities", "LongTermDebtNoncurrent", "DebtLongtermAndShorttermCombinedAmount",
                   "Borrowings", "NoncurrentLiabilities"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],  # ProfitLoss is the IFRS concept
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                "Revenue", "RevenueFromContractsWithCustomers"],
    "inventory": ["InventoryNet", "Inventories"],
    "cogs": ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold", "CostOfSales"],
    "shares_outstanding": ["WeightedAverageNumberOfSharesOutstandingBasic",
                           "WeightedAverageNumberOfDilutedSharesOutstanding",
                           "EntityCommonStockSharesOutstanding",
                           "WeightedAverageShares", "NumberOfSharesOutstanding",
                           "WeightedAverageNumberOfOrdinarySharesOutstanding"],
    "preferred_dividends": ["PreferredStockDividendsAndOtherAdjustments",
                            "DividendsRecognisedAsDistributionsToOwnersOfParentRelatingToPreferenceShares"],
}
# Components each ratio needs (mirrors rederive_accounting's _RATIOS).
RATIO_COMPONENTS: dict[str, list[str]] = {
    "current_ratio": ["current_assets", "current_liabilities"],
    "quick_ratio": ["current_assets", "inventory", "current_liabilities"],
    "debt_to_equity": ["total_debt", "total_equity"],
    "return_on_equity": ["net_income", "total_equity"], "roe": ["net_income", "total_equity"],
    "return_on_assets": ["net_income", "total_assets"], "roa": ["net_income", "total_assets"],
    "gross_margin": ["revenue", "cogs"],
    "net_margin": ["net_income", "revenue"],
    "eps": ["net_income", "preferred_dividends", "shares_outstanding"],
    "earnings_per_share": ["net_income", "preferred_dividends", "shares_outstanding"],
}


def _latest_facts(model_xbrl: Any) -> dict[str, float]:
    """Map concept localName -> value, taking the NON-dimensioned fact with the
    latest period end (the consolidated, most-recent figure)."""
    best: dict[str, tuple[Any, float]] = {}
    for fact in model_xbrl.facts:
        ctx = fact.context
        if ctx is None or ctx.qnameDims:  # skip segment/dimensioned breakdowns
            continue
        try:
            val = float(fact.xValue)
        except (TypeError, ValueError):
            continue
        name = fact.qname.localName
        end = ctx.instantDatetime or ctx.endDatetime
        if name not in best or (end is not None and best[name][0] is not None and end > best[name][0]):
            best[name] = (end, val)
    return {k: v for k, (_, v) in best.items()}


def extract_components(instance_path: str, ratio: str) -> dict[str, Any]:
    """Load an XBRL instance with Arelle and return the component values needed to
    re-derive `ratio`, plus which concept each came from. Missing components are
    reported (so the caller routes to ATTEST rather than guessing)."""
    from arelle import Cntlr

    rname = ratio.lower().replace("-", "_").replace(" ", "_")
    need = RATIO_COMPONENTS.get(rname)
    if need is None:
        return {"status": "UNKNOWN_RATIO", "ratio": rname}

    cntlr = Cntlr.Cntlr(logFileName=None)
    try:
        model = cntlr.modelManager.load(instance_path)
        if model is None or not getattr(model, "facts", None):
            return {"status": "NO_FACTS", "ratio": rname}
        facts = _latest_facts(model)
    finally:
        cntlr.close()

    out: dict[str, Any] = {"ratio": rname, "sources": {}}
    missing = []
    for comp in need:
        concept = next((c for c in _CONCEPTS.get(comp, []) if c in facts), None)
        if concept is None:
            # preferred_dividends legitimately absent -> default 0 (no preferred stock)
            if comp == "preferred_dividends":
                out[comp] = 0.0
                out["sources"][comp] = "(absent -> 0)"
                continue
            missing.append(comp)
            continue
        out[comp] = facts[concept]
        out["sources"][comp] = concept
    if missing:
        return {"status": "MISSING_COMPONENTS", "ratio": rname, "missing": missing, "sources": out["sources"]}
    out["status"] = "OK"
    return out


def build_accounting_evidence(instance_path: str, ratio: str, reported: float,
                              tolerance: float | None = None) -> dict[str, Any]:
    """Produce the `accounting` evidence dict (identity=financial_ratio) that
    rederive_accounting() consumes, with components pulled from the filing."""
    comp = extract_components(instance_path, ratio)
    if comp.get("status") != "OK":
        return {"identity": "financial_ratio", "ratio": comp.get("ratio", ratio),
                "status": comp.get("status"), "xbrl_extraction": comp}
    acc = {"identity": "financial_ratio", "ratio": comp["ratio"], "reported": float(reported),
           "xbrl_sources": comp["sources"]}
    if tolerance is not None:
        acc["tolerance"] = tolerance
    for k, v in comp.items():
        if k not in ("status", "ratio", "sources"):
            acc[k] = v
    return acc
