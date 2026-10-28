#!/usr/bin/env python3
"""Deterministic byte accounting for the Eunomia article's hypothetical examples."""
from __future__ import annotations

import json
import math
from pathlib import Path


STATIC_BITMAP_BYTES = 32
STATIC_METADATA_BYTES = 9
DBA_BYTES_PER_QP = 4
HD_METADATA_BYTES_PER_REORDERED_QP = 48
BLOCK_BITS = 16
BLOCK_BYTES = BLOCK_BITS // 8


def dynamic_bytes_per_reordered_qp(reordering_span_packets: int) -> int:
    blocks = math.ceil(reordering_span_packets / BLOCK_BITS)
    return HD_METADATA_BYTES_PER_REORDERED_QP + blocks * BLOCK_BYTES


def fleet_bytes(qps: int, reordered_fraction: float, span_packets: int) -> dict:
    reordered_qps = round(qps * reordered_fraction)
    static = qps * (STATIC_BITMAP_BYTES + STATIC_METADATA_BYTES)
    dynamic = (
        qps * DBA_BYTES_PER_QP
        + reordered_qps * dynamic_bytes_per_reordered_qp(span_packets)
    )
    return {
        "qps": qps,
        "reordered_fraction": reordered_fraction,
        "span_packets": span_packets,
        "reordered_qps": reordered_qps,
        "static_bytes": static,
        "dynamic_bytes": dynamic,
        "static_MB_decimal": round(static / 1_000_000, 3),
        "dynamic_MB_decimal": round(dynamic / 1_000_000, 3),
        "saving_percent": round((1 - dynamic / static) * 100, 2),
    }


def break_even_fraction(span_packets: int) -> float:
    static_per_qp = STATIC_BITMAP_BYTES + STATIC_METADATA_BYTES
    extra_dynamic = dynamic_bytes_per_reordered_qp(span_packets)
    return (static_per_qp - DBA_BYTES_PER_QP) / extra_dynamic


def header_overhead(payload_bytes: int) -> dict:
    extra_bits = 33
    return {
        "payload_bytes": payload_bytes,
        "extra_header_bits": extra_bits,
        "extra_header_bytes_equivalent": extra_bits / 8,
        "payload_ratio_percent": round(extra_bits / (payload_bytes * 8) * 100, 4),
    }


def main() -> None:
    qps = 1_000_000
    scenarios = [
        fleet_bytes(qps, fraction, span)
        for span in (16, 64, 256)
        for fraction in (0.01, 0.05, 0.20, 0.60, 1.00)
    ]
    out = {
        "model": {
            "static_bitmap_bytes_per_qp": STATIC_BITMAP_BYTES,
            "static_metadata_bytes_per_qp": STATIC_METADATA_BYTES,
            "dynamic_base_DBA_bytes_per_qp": DBA_BYTES_PER_QP,
            "dynamic_metadata_bytes_per_reordered_qp": HD_METADATA_BYTES_PER_REORDERED_QP,
            "block_bits": BLOCK_BITS,
            "block_bytes": BLOCK_BYTES,
            "note": "Hypothetical accounting derived from the paper's 256-bit/16-bit-block example; excludes allocator alignment, packet buffers, timers, and all RNIC state outside Eunomia.",
        },
        "break_even_reordered_fraction": {
            str(span): round(break_even_fraction(span), 6)
            for span in (16, 64, 256)
        },
        "header_overhead": [header_overhead(x) for x in (256, 1024, 4096)],
        "scenarios": scenarios,
    }
    target = Path(__file__).with_suffix(".results.json")
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
