from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "outputs" / "sota_watch"
DEFAULT_DOC = ROOT / "docs" / "SOTA_DAILY_WATCH.md"

DEFAULT_QUERIES = [
    "scientific claim verification provenance",
    "training data provenance fine-tuning governance",
    "claim level auditability research agents",
    "RO-Crate provenance AI training data",
    "scientific fact checking evidence alignment",
    "AI Act training data provenance audit trail",
    "dataset curation claim verification machine learning",
]


def today_utc() -> str:
    return dt.datetime.now(dt.UTC).date().isoformat()


def ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # type: ignore

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def fetch_json(url: str, *, timeout: float) -> dict[str, Any]:
    headers = {
        "User-Agent": "CAPAS-SOTA-Watch/1.0 (+https://fomv9354lve.github.io/capas-inteligentes/)"
    }
    s2_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY") or os.environ.get("S2_API_KEY")
    if "api.semanticscholar.org" in url and s2_key:
        headers["x-api-key"] = s2_key
    req = urllib.request.Request(
        url,
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_text(url: str, *, timeout: float) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "CAPAS-SOTA-Watch/1.0 (+https://fomv9354lve.github.io/capas-inteligentes/)"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
        return resp.read().decode("utf-8", errors="replace")


def semantic_scholar_search(query: str, *, limit: int, timeout: float) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {
            "query": query,
            "limit": str(limit),
            "fields": "title,year,authors,url,venue,abstract,citationCount,publicationDate,externalIds",
        }
    )
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
    data = fetch_json(url, timeout=timeout)
    rows: list[dict[str, Any]] = []
    for paper in data.get("data", []) or []:
        rows.append(
            {
                "source": "semantic_scholar",
                "query": query,
                "title": paper.get("title") or "",
                "year": paper.get("year"),
                "publication_date": paper.get("publicationDate"),
                "venue": paper.get("venue") or "",
                "url": paper.get("url") or "",
                "doi": (paper.get("externalIds") or {}).get("DOI", ""),
                "citation_count": paper.get("citationCount"),
                "authors": [a.get("name", "") for a in paper.get("authors", [])[:6]],
                "abstract": paper.get("abstract") or "",
            }
        )
    return rows


def arxiv_search(query: str, *, limit: int, timeout: float) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {
            "search_query": f"all:{query}",
            "start": "0",
            "max_results": str(limit),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    url = f"https://export.arxiv.org/api/query?{params}"
    text = fetch_text(url, timeout=timeout)
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    rows: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns):
        title = " ".join((entry.findtext("atom:title", default="", namespaces=ns) or "").split())
        summary = " ".join((entry.findtext("atom:summary", default="", namespaces=ns) or "").split())
        published = entry.findtext("atom:published", default="", namespaces=ns) or ""
        link = ""
        for link_el in entry.findall("atom:link", ns):
            if link_el.attrib.get("rel") == "alternate":
                link = link_el.attrib.get("href", "")
                break
        rows.append(
            {
                "source": "arxiv",
                "query": query,
                "title": title,
                "year": int(published[:4]) if published[:4].isdigit() else None,
                "publication_date": published[:10],
                "venue": "arXiv",
                "url": link,
                "doi": "",
                "citation_count": None,
                "authors": [
                    a.findtext("atom:name", default="", namespaces=ns) or ""
                    for a in entry.findall("atom:author", ns)[:6]
                ],
                "abstract": summary,
            }
        )
    return rows


def normalize_key(row: dict[str, Any]) -> str:
    doi = str(row.get("doi") or "").lower().strip()
    if doi:
        return f"doi:{doi}"
    url = str(row.get("url") or "").lower().strip()
    if url:
        return f"url:{url}"
    return "title:" + " ".join(str(row.get("title") or "").lower().split())


def score_row(row: dict[str, Any]) -> int:
    text = f"{row.get('title', '')} {row.get('abstract', '')}".lower()
    weighted_terms = {
        "provenance": 4,
        "training data": 4,
        "fine-tuning": 4,
        "claim": 3,
        "evidence": 1,
        "audit": 3,
        "fact checking": 2,
        "scientific": 2,
        "ro-crate": 3,
        "ai act": 3,
        "governance": 3,
        "verification": 2,
    }
    score = 0
    for term, weight in weighted_terms.items():
        if term in text:
            score += weight
    if row.get("source") == "semantic_scholar" and row.get("citation_count"):
        score += min(int(row["citation_count"]), 50) // 10
    return score


def has_capas_anchor(row: dict[str, Any]) -> bool:
    text = f"{row.get('title', '')} {row.get('abstract', '')}".lower()
    anchors = (
        "claim",
        "provenance",
        "training data",
        "fine-tuning",
        "fine tuning",
        "fact-check",
        "fact checking",
        "ro-crate",
        "audit",
        "governance",
        "dataset curation",
        "evidence alignment",
        "scientific verification",
    )
    return any(anchor in text for anchor in anchors)


def dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = normalize_key(row)
        if not has_capas_anchor(row):
            continue
        row = dict(row)
        row["capas_relevance_score"] = score_row(row)
        if row["capas_relevance_score"] < 4:
            continue
        if key not in by_key or row["capas_relevance_score"] > by_key[key]["capas_relevance_score"]:
            by_key[key] = row
    return sorted(
        by_key.values(),
        key=lambda r: (r.get("capas_relevance_score", 0), str(r.get("publication_date") or "")),
        reverse=True,
    )


def render_markdown(report: dict[str, Any]) -> str:
    rows = report.get("top_results", [])
    lines = [
        "# CAPAS Daily SotA Watch",
        "",
        f"Last updated: `{report['run_date']}`",
        "",
        "This file is generated by `scripts/update_sota_watch.py`. It is a watchlist, not a claim that CAPAS has verified every paper.",
        "",
        "## Operating Commitment",
        "",
        "- We will keep the literature and state-of-the-art positioning fresh through a daily local watch run.",
        "- We will treat new sources as candidates until a human reviews and promotes them into CAPAS documentation.",
        "- We will not claim novelty from a watch result alone; claims require explicit source-backed review.",
        "",
        "## Run Status",
        "",
        f"- Status: `{report['status']}`",
        f"- Queries: `{len(report['queries'])}`",
        f"- Results retained: `{len(rows)}`",
        f"- Artifact: `{report['artifact_path']}`",
        "",
        "## Top Candidates",
        "",
    ]
    if not rows:
        lines += [
            "No candidates were retained in this run. If status is `network_error`, rerun when network access is available.",
            "",
        ]
        return "\n".join(lines)

    lines.append("| Score | Source | Year | Title | Link | Why it matters |")
    lines.append("|---:|---|---:|---|---|---|")
    for row in rows[:25]:
        title = html.escape(str(row.get("title") or "Untitled"))
        url = str(row.get("url") or "")
        link = f"[link]({url})" if url else ""
        why = " ".join(str(row.get("abstract") or "").split())[:180]
        if len(str(row.get("abstract") or "")) > 180:
            why += "..."
        lines.append(
            "| {score} | {source} | {year} | {title} | {link} | {why} |".format(
                score=row.get("capas_relevance_score", 0),
                source=row.get("source", ""),
                year=row.get("year") or "",
                title=title.replace("|", "\\|"),
                link=link,
                why=html.escape(why).replace("|", "\\|"),
            )
        )
    lines += [
        "",
        "## Promotion Rule",
        "",
        "A result should be promoted into `docs/SOTA_POSITIONING.md` or `docs/GLOBAL_SOTA_MARKET_AUDIT.md` only after a reviewer records:",
        "",
        "1. what the source occupies,",
        "2. what CAPAS must not claim because of it,",
        "3. what defensible CAPAS gap remains,",
        "4. source URL/DOI and retrieval date.",
        "",
    ]
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict[str, Any]:
    queries = args.query or DEFAULT_QUERIES
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    if not args.offline:
        for query in queries:
            for source_name, search_fn in (
                ("semantic_scholar", semantic_scholar_search),
                ("arxiv", arxiv_search),
            ):
                try:
                    rows.extend(search_fn(query, limit=args.limit, timeout=args.timeout))
                except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ET.ParseError, json.JSONDecodeError) as exc:
                    errors.append({"source": source_name, "query": query, "error": str(exc)})
                time.sleep(args.pause)

    retained = dedupe(rows)[: args.retain]
    status = "ok"
    if args.offline:
        status = "offline"
    elif errors and not retained:
        status = "network_error"
    elif errors:
        status = "partial"

    run_date = args.date or today_utc()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = out_dir / f"{run_date}.json"
    report: dict[str, Any] = {
        "run_date": run_date,
        "status": status,
        "queries": queries,
        "errors": errors,
        "top_results": retained,
        "artifact_path": str(artifact.relative_to(ROOT) if artifact.is_relative_to(ROOT) else artifact),
        "non_claim": "This is a literature watchlist, not a CAPAS verification decision or novelty claim.",
    }
    artifact.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report["artifact_path"] = str(artifact.relative_to(ROOT) if artifact.is_relative_to(ROOT) else artifact)
    Path(args.doc).write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Update CAPAS daily literature and SotA watch artifacts.")
    parser.add_argument("--query", action="append", help="query to run; can be repeated")
    parser.add_argument("--limit", type=int, default=5, help="results per query/source")
    parser.add_argument("--retain", type=int, default=30, help="deduped candidates to retain")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--pause", type=float, default=2.0, help="seconds between source requests")
    parser.add_argument("--date", help="override run date, YYYY-MM-DD")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--doc", default=str(DEFAULT_DOC))
    parser.add_argument("--offline", action="store_true", help="write an offline status artifact without network calls")
    args = parser.parse_args()
    report = run(args)
    print(json.dumps({"status": report["status"], "artifact": report["artifact_path"], "results": len(report["top_results"])}, indent=2))
    return 0 if report["status"] in {"ok", "partial", "offline"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
