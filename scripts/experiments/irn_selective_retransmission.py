#!/usr/bin/env python3
"""Deterministic teaching model for IRN selective retransmission and BDP-FC.

This is not an IRN simulator. It checks packet accounting, bitmap completion
conditions, and BDP-cap scaling for the assumptions used in the companion post.
"""
from __future__ import annotations

import json
import math


def bdp_case(link_gbps: int, rtt_us: int, mtu_bytes: int = 1024) -> dict:
    bdp_bytes = link_gbps * 1_000_000_000 / 8 * rtt_us / 1_000_000
    packets = math.ceil(bdp_bytes / mtu_bytes)
    return {
        "link_gbps": link_gbps,
        "rtt_us": rtt_us,
        "mtu_bytes": mtu_bytes,
        "bdp_bytes": int(bdp_bytes),
        "bdp_packets": packets,
        "five_bitmap_bits_per_qp": packets * 5,
        "five_bitmap_bytes_per_qp": math.ceil(packets * 5 / 8),
    }


def retransmission_case(window_packets: int, lost_psns: list[int]) -> dict:
    first_loss = min(lost_psns)
    go_back_n_retransmissions = window_packets - first_loss
    selective_retransmissions = len(lost_psns)
    return {
        "window_packets": window_packets,
        "lost_psns": lost_psns,
        "go_back_n": {
            "initial_transmissions": window_packets,
            "retransmissions": go_back_n_retransmissions,
            "total_transmissions": window_packets + go_back_n_retransmissions,
            "redundant_retransmissions": go_back_n_retransmissions - len(lost_psns),
        },
        "selective": {
            "initial_transmissions": window_packets,
            "retransmissions": selective_retransmissions,
            "total_transmissions": window_packets + selective_retransmissions,
            "redundant_retransmissions": 0,
        },
    }


def completion_trace(packet_count: int, first_arrivals: list[int], repairs: list[int]) -> dict:
    arrived = [False] * packet_count
    trace = []

    def contiguous_prefix() -> int:
        prefix = 0
        while prefix < packet_count and arrived[prefix]:
            prefix += 1
        return prefix

    for phase, sequence in (("first_arrival", first_arrivals), ("repair", repairs)):
        for psn in sequence:
            arrived[psn] = True
            prefix = contiguous_prefix()
            trace.append({
                "phase": phase,
                "psn": psn,
                "contiguous_prefix_packets": prefix,
                "last_packet_present": arrived[-1],
                "completion_visible": prefix == packet_count and arrived[-1],
            })

    return {
        "packet_count": packet_count,
        "arrival_order": first_arrivals + repairs,
        "trace": trace,
        "completion_event_index": next(
            i for i, event in enumerate(trace) if event["completion_visible"]
        ),
    }


def main() -> None:
    results = {
        "model": "deterministic packet-accounting example; not a network simulation",
        "bdp_cases": [
            bdp_case(40, 24),
            bdp_case(100, 24),
            bdp_case(200, 12),
            bdp_case(400, 12),
            bdp_case(800, 12),
        ],
        "loss_case": retransmission_case(64, [7, 29]),
        "completion_case": completion_trace(
            packet_count=12,
            first_arrivals=[0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            repairs=[2],
        ),
    }
    print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

