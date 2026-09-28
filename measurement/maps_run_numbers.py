"""Reproduces the article's Google Maps stage to get its run numbers.

Same inputs the workflow uses: the query pattern `{leads_query} {location}`,
the article's example GPS anchor, pagination by result offset in steps of 20
until Maps stops returning rows. Duplicates are counted on the workflow's own
dedup key (title + kgmid). Two queries run: the dense city one from the
screenshots, and a narrow small-town one, so the article can say what happens in
both cases instead of generalizing from one.

Writes maps_run_numbers.json next to this script.
"""
import json
import os
import pathlib
import sys
import time

import requests as rq

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = pathlib.Path(__file__).resolve().parent
KEY = os.environ["HASDATA_API_KEY"]
URL = "https://api.hasdata.com/scrape/google-maps/search"

RUNS = [
    {"name": "dense city", "q": "emergency plumbing services New York",
     "ll": "@40.7455096,-74.0083012,14z", "max_pages": 12},
    {"name": "narrow small town", "q": "emergency plumbing services Ely Nevada",
     "ll": "@39.2472,-114.8888,14z", "max_pages": 12},
]


def measure(run):
    pages, seen, dups = [], {}, 0
    for page in range(run["max_pages"]):
        params = {"q": run["q"], "ll": run["ll"], "start": page * 20}
        for _ in range(4):
            r = rq.get(URL, params=params, headers={"x-api-key": KEY}, timeout=120)
            if r.status_code != 429:
                break
            time.sleep(10)
        j = r.json()
        rows = j.get("localResults") or j.get("results") or []
        pages.append({"page": page + 1, "status": r.status_code, "rows": len(rows)})
        for item in rows:
            # the workflow's Remove Duplicates node compares title + kgmid
            key = (item.get("title"), item.get("kgmid") or item.get("placeId"))
            if key in seen:
                dups += 1
            else:
                seen[key] = {"phone": bool(item.get("phone")),
                             "website": bool(item.get("website")),
                             "address": bool(item.get("address"))}
        print(json.dumps({"run": run["name"], **pages[-1]}))
        if not rows:
            break
        time.sleep(1.2)
    uniq, total = len(seen), sum(p["rows"] for p in pages)
    cov = {f: sum(1 for v in seen.values() if v[f]) for f in ("phone", "website", "address")}
    return {
        "name": run["name"], "query": run["q"], "ll": run["ll"],
        "pages_fetched": len(pages),
        "last_nonempty_page": max((p["page"] for p in pages if p["rows"]), default=0),
        "hit_empty_page": any(p["rows"] == 0 for p in pages),
        "total_rows": total, "unique_places": uniq, "duplicates": dups,
        "dup_share": round(dups / total, 3) if total else None,
        "dedup_key": "title + kgmid (as in the workflow's Remove Duplicates node)",
        "coverage": {f: {"n": cov[f], "share": round(cov[f] / uniq, 4)} for f in cov} if uniq else {},
        "credits_per_request": 5,
        "credits_spent": len(pages) * 5,
        "pages": pages,
    }


out = {"runs": [measure(r) for r in RUNS]}
(HERE / "maps_run_numbers.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
for r in out["runs"]:
    print(json.dumps({k: r[k] for k in r if k != "pages"}, ensure_ascii=False, indent=1))
