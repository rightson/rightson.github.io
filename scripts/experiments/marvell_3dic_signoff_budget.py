#!/usr/bin/env python3
"""Reproduce the resource-accounting example used by the Marvell 3DIC article.

The runtimes and core counts are transcribed from Marvell's WISH 2025
presentation.  The five-iteration strategies are explicit what-if calculations,
not a measurement of Marvell's project schedule.
"""

from __future__ import annotations

import json
from pathlib import Path


JOBS = {
    "tier2": {
        "TOPO": {"hours": 1.5, "cores": 48},
        "LDL": {"hours": 1.6, "cores": 48},
        "CD": {"hours": 1.8, "cores": 48},
        "P2P": {"hours": 41.0, "cores": 240},
    },
    "tier1_kgs": {
        "TOPO": {"hours": 2.9, "cores": 48},
        "LDL": {"hours": 2.5, "cores": 48},
        "CD": {"hours": 6.2, "cores": 16},
        "P2P": {"hours": 6.5, "cores": 240},
    },
}


def summarize(jobs: dict[str, dict[str, float]]) -> dict[str, object]:
    rows = {}
    total = 0.0
    for name, values in jobs.items():
        core_hours = values["hours"] * values["cores"]
        rows[name] = {**values, "core_hours": round(core_hours, 1)}
        total += core_hours
    p2p_share = rows["P2P"]["core_hours"] / total
    return {
        "jobs": rows,
        "critical_path_hours_if_serial": round(sum(v["hours"] for v in jobs.values()), 1),
        "total_core_hours": round(total, 1),
        "p2p_core_hour_share": round(p2p_share, 4),
    }


def main() -> None:
    summaries = {name: summarize(jobs) for name, jobs in JOBS.items()}
    full = summaries["tier1_kgs"]["total_core_hours"]
    lightweight = sum(
        summaries["tier1_kgs"]["jobs"][name]["core_hours"] for name in ("TOPO", "LDL")
    )
    iterations = 5
    all_full = full * iterations
    staged = lightweight * (iterations - 1) + full
    output = {
        "source": "Marvell WISH 2025 public runtime table",
        "reported_job_accounting": summaries,
        "what_if": {
            "iterations": iterations,
            "all_iterations_full_core_hours": round(all_full, 1),
            "four_lightweight_plus_one_full_core_hours": round(staged, 1),
            "core_hours_reduced": round(all_full - staged, 1),
            "reduction_fraction": round((all_full - staged) / all_full, 4),
            "assumption": (
                "Early iterations run TOPO and LDL only; the final iteration runs "
                "TOPO, LDL, CD, and P2P. This is a scheduling illustration and "
                "does not replace signoff requirements."
            ),
        },
    }
    destination = Path(__file__).with_suffix(".results.json")
    destination.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
