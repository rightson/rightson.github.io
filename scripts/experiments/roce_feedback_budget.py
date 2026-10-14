#!/usr/bin/env python3
"""First-response fluid arithmetic, not a DCQCN/PFC packet simulator.

All rates are ideal data rates; decimal bytes/second and seconds internally.
No wire overhead, cell rounding, steady-state control, XON or transport retry.
The queue pressure line is abstract, not a real ingress PFC register.
Run from repository root to regenerate the adjacent JSON record.
"""
import json
import math
from pathlib import Path


def jain(rates):
    return sum(rates) ** 2 / (len(rates) * sum(r * r for r in rates))


def budget(rate_gbps=400, senders=4, cc_us=8, pause_us=2,
           mark_bytes=256_000, pressure_bytes=768_000, extra_bytes=9_000):
    link_Bps = rate_gbps * 1e9 / 8
    arrivals_Bps = senders * link_Bps
    excess_Bps = arrivals_Bps - link_Bps
    if excess_Bps <= 0:
        raise ValueError("This first-response example requires oversubscription.")
    mark_s = mark_bytes / excess_Bps
    pressure_s = pressure_bytes / excess_Bps
    cc_s = mark_s + cc_us * 1e-6
    pause_s = pressure_s + pause_us * 1e-6
    return {
        "rate_gbps": rate_gbps,
        "senders": senders,
        "link_Bps": link_Bps,
        "aggregate_arrival_Bps": arrivals_Bps,
        "excess_Bps": excess_Bps,
        "first_mark_us": mark_s * 1e6,
        "pressure_crossing_us": pressure_s * 1e6,
        "first_cc_effective_us": cc_s * 1e6,
        "first_pause_effective_us": pause_s * 1e6,
        "cc_feedback_excess_bytes": excess_Bps * cc_us * 1e-6,
        "ideal_cc_peak_bytes": excess_Bps * cc_s,
        "ideal_first_pause_peak_bytes": excess_Bps * pause_s,
        "pressure_to_mark_gap_us": (pressure_bytes - mark_bytes) / excess_Bps * 1e6,
        "raw_headroom_per_ingress_bytes": link_Bps * pause_us * 1e-6 + extra_bytes,
        "raw_concurrent_headroom_bytes": senders * (link_Bps * pause_us * 1e-6 + extra_bytes),
        "fair_share_GBps": link_Bps / senders / 1e9,
    }


def queue_at(t_us, result, mode):
    t = t_us * 1e-6
    excess = result["excess_Bps"]
    if mode == "ideal_cc":
        stop = result["first_cc_effective_us"] * 1e-6
        return excess * min(t, stop)  # total arrival becomes exactly service rate
    if mode == "first_pause":
        stop = result["first_pause_effective_us"] * 1e-6
        return excess * t if t <= stop else max(
            0.0, excess * stop - result["link_Bps"] * (t - stop))
    raise ValueError(mode)


def stepped_queue(result, mode, dt_us=0.001):
    """Independent discrete conservation check with quantized event timing."""
    event_us = result["first_cc_effective_us"] if mode == "ideal_cc" else result["first_pause_effective_us"]
    q, maximum = 0.0, 0.0
    for k in range(math.ceil(40 / dt_us)):
        t_us = k * dt_us
        arrivals = result["aggregate_arrival_Bps"] if t_us < event_us else (
            result["link_Bps"] if mode == "ideal_cc" else 0.0)
        q = max(0.0, q + (arrivals - result["link_Bps"]) * dt_us * 1e-6)
        maximum = max(maximum, q)
    return maximum


def main():
    r = budget()
    check = {}
    for mode, expected in [
        ("ideal_cc", r["ideal_cc_peak_bytes"]),
        ("first_pause", r["ideal_first_pause_peak_bytes"]),
    ]:
        measured = stepped_queue(r, mode)
        # quantized event must be within one integration interval of the analytic peak
        bound = r["aggregate_arrival_Bps"] * 0.001 * 1e-6
        assert abs(measured - expected) <= bound + 1e-6
        check[mode] = {"dt_us": 0.001, "stepped_peak_bytes": measured,
                       "analytic_peak_bytes": expected, "error_bound_bytes": bound}
    assert math.isclose(r["cc_feedback_excess_bytes"], 1_200_000)
    assert math.isclose(r["ideal_first_pause_peak_bytes"], 1_068_000)
    assert math.isclose(budget(800)["raw_headroom_per_ingress_bytes"], 209_000)
    # Independent mapping counterexample: all columns below ECN, one row above XOFF.
    columns = [48_000] * 4
    assert max(columns) < 80_000 and sum(columns) > 128_000
    # A source consumes 109kB, including its own dedicated 32kB, not 109kB from shared.
    shared_need = 4 * (r["raw_headroom_per_ingress_bytes"] - 32_000)
    assert math.isclose(shared_need - 200_000, 108_000)
    output = {
        "scope": "Executed hypothetical arithmetic and independent discrete conservation checks; no hardware measurements.",
        "assumptions": {"cc_feedback_us": 8, "pause_stop_us": 2,
                        "mark_bytes": 256_000, "abstract_pressure_bytes": 768_000,
                        "extra_per_ingress_bytes": 9_000,
                        "units": "decimal bytes, seconds, ideal data rate"},
        "base_case": r,
        "independent_checks": check,
        "queue_samples": [{"t_us": t, "ideal_cc_bytes": queue_at(t, r, "ideal_cc"),
                           "first_pause_bytes": queue_at(t, r, "first_pause")}
                          for t in sorted(set(list(range(41)) + [
                              r["first_mark_us"], r["pressure_crossing_us"],
                              r["first_cc_effective_us"], r["first_pause_effective_us"]]))],
        "rate_sensitivity": [budget(rate) for rate in [100, 200, 400, 800]],
        "headroom_delay_sensitivity_400G": [
            {"pause_us": t, "headroom_bytes": budget(pause_us=t)["raw_headroom_per_ingress_bytes"]}
            for t in [0.5, 1, 2, 4]],
        "mapping_counterexample": {"egress_columns_bytes": columns, "ingress_row_bytes": sum(columns),
                                   "ecn_bytes": 80_000, "xoff_bytes": 128_000},
        "shared_headroom": {"dedicated_per_ingress_bytes": 32_000, "shared_pool_bytes": 200_000,
                            "required_shared_bytes": shared_need, "shortfall_bytes": shared_need - 200_000},
        "jain": {"fair": jain([12.5] * 4), "unequal": jain([35, 5, 5, 5])},
        "completion_lower_bound_ms": 4 * 16e6 / r["link_Bps"] * 1e3,
        "short_message": {"bytes": 64_000, "serialization_us": 64_000 / r["link_Bps"] * 1e6,
                          "pause_us": 20, "pause_plus_serialization_us": 21.28},
    }
    path = Path(__file__).with_suffix(".results.json")
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"checks": "passed", "base_case": r,
                      "jain": output["jain"], "output": str(path)}, indent=2))


if __name__ == "__main__":
    main()

