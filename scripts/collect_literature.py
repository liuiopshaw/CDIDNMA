#!/usr/bin/env python3
"""Collect literature (title + DOI) from OpenAlex for the CDI antimicrobial
electrode agent project, organized into three layers:
  cdi_core                  - CDI disinfection/antibacterial (core data)
  electrocatalysis_prior    - electrocatalytic ROS / electrochemical disinfection
  photocatalysis_inspiration- photocatalytic ROS / disinfection (inspiration only)

Output: one CSV per layer + a combined CSV, columns: title, doi
"""
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.openalex.org/works"
OUT = Path(__file__).resolve().parent.parent / "data"
PER_PAGE = 200          # max allowed by OpenAlex
PAGES_PER_QUERY = 1     # top-200 by relevance per query
MAILTO = "cdi-agent@example.com"   # polite pool; replace with a real address

QUERIES = {
    "cdi_core": [
        "capacitive deionization disinfection",
        "capacitive deionization antibacterial electrode",
        "capacitive deionization bacteria inactivation",
        "capacitive deionization sterilization water",
        "flow electrode capacitive deionization disinfection",
        "capacitive deionization nanoparticle electrode",
        "capacitive deionization single atom catalyst",
    ],
    "electrocatalysis_prior": [
        "electrochemical disinfection reactive oxygen species electrode",
        "two-electron oxygen reduction hydrogen peroxide carbon cathode",
        "electro-Fenton cathode H2O2 production carbon",
        "electrocatalytic antibacterial water treatment",
        "single-atom catalyst oxygen reduction hydrogen peroxide",
        "atomically dispersed metal nitrogen carbon two-electron ORR",
        "metal nanocluster electrocatalyst reactive oxygen species",
        "single atom catalyst electrochemical disinfection",
        "metal nanocluster antibacterial reactive oxygen species",
        "supported metal nanoparticle electrocatalyst support interaction",
    ],
    "photocatalysis_inspiration": [
        "photocatalytic disinfection reactive oxygen species",
        "photocatalytic antibacterial mechanism ROS",
    ],
}

# Queries added in the v2 expansion (nanomaterial electrodes). Records first
# seen via these queries are also written to an increment file.
V2_QUERIES = {
    "capacitive deionization nanoparticle electrode",
    "capacitive deionization single atom catalyst",
    "single-atom catalyst oxygen reduction hydrogen peroxide",
    "atomically dispersed metal nitrogen carbon two-electron ORR",
    "metal nanocluster electrocatalyst reactive oxygen species",
    "single atom catalyst electrochemical disinfection",
    "metal nanocluster antibacterial reactive oxygen species",
    "supported metal nanoparticle electrocatalyst support interaction",
}

# Local relevance filters applied to the (lowercased) title
LAYER_FILTERS = {
    "cdi_core": r"capacitive deionization|electrosorption",
    "electrocatalysis_prior": (
        r"disinfect|antibacter|antimicrobial|bacteri|inactivat|steriliz|"
        r"hydrogen peroxide|h2o2|oxygen reduction|electro-?fenton|reactive oxygen"
    ),
    "photocatalysis_inspiration": (
        r"photocataly|antibacter|antimicrobial|disinfect|inactivat|reactive oxygen"
    ),
}


def fetch(query: str) -> list[dict]:
    params = {
        "search": query,
        "per-page": PER_PAGE,
        "select": "id,doi,title,publication_year,type",
        "mailto": MAILTO,
    }
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "cdi-agent/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)["results"]


def main() -> None:
    seen: set[str] = set()
    layers: dict[str, list[tuple[str, str]]] = {k: [] for k in QUERIES}
    increment: list[tuple[str, str, str, str]] = []

    for layer, queries in QUERIES.items():
        pattern = re.compile(LAYER_FILTERS[layer])
        for q in queries:
            try:
                works = fetch(q)
            except Exception as exc:  # noqa: BLE001
                print(f"[WARN] query failed: {q!r}: {exc}")
                continue
            kept = 0
            for w in works:
                doi = (w.get("doi") or "").replace("https://doi.org/", "").strip()
                title = (w.get("title") or "").strip()
                if not doi or not title or doi in seen:
                    continue
                if w.get("type") not in ("article", "review"):
                    continue
                if not pattern.search(title.lower()):
                    continue
                seen.add(doi)
                layers[layer].append((title, doi))
                if q in V2_QUERIES:
                    increment.append((layer, q, title, doi))
                kept += 1
            print(f"{layer:28s} | {q:55s} | fetched {len(works):3d} kept {kept:3d}")
            time.sleep(0.4)

    for layer, rows in layers.items():
        path = OUT / layer / "titles_dois.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["title", "doi"])
            w.writerows(rows)

    combined = OUT / "all_titles_dois.csv"
    with combined.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["layer", "title", "doi"])
        for layer, rows in layers.items():
            for title, doi in rows:
                w.writerow([layer, title, doi])

    inc_path = OUT / "increment_v2_titles_dois.csv"
    with inc_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["layer", "query", "title", "doi"])
        w.writerows(increment)

    total = sum(len(v) for v in layers.values())
    print("\n=== summary ===")
    for layer, rows in layers.items():
        print(f"{layer:28s}: {len(rows)}")
    print(f"{'TOTAL (deduped)':28s}: {total}")
    print(f"{'increment (v2 queries)':28s}: {len(increment)}")
    print(f"written to {OUT}")


if __name__ == "__main__":
    main()
