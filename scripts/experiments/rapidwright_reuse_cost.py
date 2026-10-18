#!/usr/bin/env python3
"""Synthetic cost model, not an FPGA implementation or timing experiment.

Run: python3 scripts/experiments/rapidwright_reuse_cost.py
All hours are summed implementation-job hours, not CPU-hours or elapsed time.
"""
import json
import math


def cost(versions, refresh_every=None, *, prep=45.0, flat=6.0, warm=2.0):
    libraries = 1 if refresh_every is None else math.ceil(versions / refresh_every)
    baseline = versions * flat
    reuse = libraries * prep + versions * warm
    return {"versions": versions, "libraries": libraries,
            "flat_job_hours": baseline, "reuse_job_hours": reuse,
            "saved_job_hours": baseline - reuse}


def first_saving(prep, flat, warm):
    return None if warm >= flat else math.floor(prep / (flat - warm)) + 1


def main():
    assumptions = {"exploration_jobs": 180, "hours_per_exploration_job": 0.25,
                   "initial_library_job_hours": 45, "flat_per_version_job_hours": 6,
                   "warm_per_version_job_hours": 2,
                   "excludes": ["CPU core count", "license token weights", "queue wait",
                                "engineering time", "timing failures", "FPGA PPA"]}
    stable = [cost(n) for n in (1, 5, 12, 20)]
    # An independent summation checks the periodic model at the refresh boundary.
    periodic = cost(20, refresh_every=10)
    explicit = sum(2 + (45 if i in (1, 11) else 0) for i in range(1, 21))
    assert periodic["reuse_job_hours"] == explicit == 130
    assert cost(11)["saved_job_hours"] < 0 < cost(12)["saved_job_hours"]
    assert first_saving(45, 6, 6) is None
    assert first_saving(45, 6, 7) is None
    print(json.dumps({"kind": "synthetic_cost_model", "assumptions": assumptions,
                      "stable_library": stable,
                      "refresh_every_10_versions": periodic,
                      "first_strictly_profitable_version": first_saving(45, 6, 2),
                      "no_break_even_if_warm_ge_flat": True}, indent=2))


if __name__ == "__main__":
    main()
