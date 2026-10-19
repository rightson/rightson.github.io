#!/usr/bin/env python3
"""Synthetic protocol test, not an RTL simulator or security sandbox.

Run: python3 scripts/experiments/agentic_artifact_grader.py
All fixtures are hand written; trusted producer isolation is assumed, not enforced.
"""
import copy
import hashlib
import json
from collections import deque


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def check_fifo(trace):
    q = deque()
    comparisons = 0
    failures = 0
    for event in trace:
        if event['op'] == 'reset':
            q.clear()
        elif event['op'] == 'write':
            q.append(event['value'])
        elif event['op'] == 'read':
            expected = q.popleft() if q else None
            comparisons += 1
            failures += event['value'] != expected
        else:
            raise ValueError('unknown event')
    return {'comparisons': comparisons, 'failures': failures}


TRACE = [{'op': 'reset'}, {'op': 'write', 'value': 7}, {'op': 'read', 'value': 7}]
LOCK = {'rtl': 'rtl-v1', 'test': 'test-v1', 'seed': 11, 'tool': 'sim-v1', 'checker': 'fifo-v1'}


def fixture(name, eligible):
    trace = copy.deepcopy(TRACE)
    report = {'identity': LOCK.copy(), 'execution': 'exec-1', 'complete': True,
              'coverage': 1.0, 'checks': check_fifo(trace), 'trace': trace}
    return {'name': name, 'eligible': eligible, 'report': report,
            'separate_failures': 0, 'sealed_digest': digest(report)}


def naive(case):
    # Deliberately weak baseline: separate scoreboard, missing interpreted as zero.
    return case['report']['coverage'] >= .98 and (case['separate_failures'] or 0) == 0


def strict(case):
    r = case['report']
    reasons = []
    if digest(r) != case['sealed_digest']:
        reasons.append('content_digest')
    if r['identity'] != LOCK:
        reasons.append('input_identity')
    if r['execution'] != 'exec-1':
        reasons.append('execution_identity')
    if not r['complete']:
        reasons.append('incomplete')
    checks = r['checks']
    if checks is None or checks['comparisons'] <= 0:
        reasons.append('missing_checker')
    elif checks != check_fifo(r['trace']) or checks['failures'] != 0:
        reasons.append('same_trace_check')
    if r['coverage'] < .98:
        reasons.append('coverage')
    return not reasons, reasons


def main():
    cases = [fixture('valid', True), fixture('valid-second-value', True),
             fixture('bad-generated-data', False), fixture('stale-rtl', False),
             fixture('different-stimulus', False), fixture('missing-checker', False),
             fixture('modified-after-seal', False), fixture('timeout-with-partial-report', False),
             fixture('coverage-gap', False), fixture('reported-failure', False)]
    cases[1]['report']['trace'][1]['value'] = 9
    cases[1]['report']['trace'][2]['value'] = 9
    cases[2]['report']['trace'][2]['value'] = 8
    cases[2]['report']['checks'] = check_fifo(cases[2]['report']['trace'])
    cases[3]['report']['identity']['rtl'] = 'rtl-v0'
    cases[4]['report']['identity']['test'] = 'test-v0'
    cases[4]['report']['execution'] = 'exec-other'
    cases[5]['report']['checks'] = None
    cases[5]['separate_failures'] = None
    cases[7]['report']['complete'] = False
    cases[8]['report']['coverage'] = .75
    cases[9]['report']['trace'][2]['value'] = 0
    cases[9]['report']['checks'] = check_fifo(cases[9]['report']['trace'])
    cases[9]['separate_failures'] = 1
    for i, case in enumerate(cases):
        if i != 6:
            case['sealed_digest'] = digest(case['report'])
    cases[6]['report']['trace'][1]['value'] = 8
    rows = []
    for case in cases:
        accepted, reasons = strict(case)
        assert accepted == case['eligible'], case['name']
        rows.append({'name': case['name'], 'eligible': case['eligible'],
                     'naive_accept': naive(case), 'strict_accept': accepted, 'reasons': reasons})
    f = [1, 1, 1, 1, 0, 0]
    g = [0, 0, 1, 1, 1, 1]
    score = sum(a*b*.8 for a, b in zip(f, g))/6
    wrong = (sum(f)/6)*(sum(g)/6)*.8
    assert abs(score-4/15) < 1e-12
    out = {'kind': 'synthetic-protocol-test', 'llm_executed': False,
           'eda_executed': False, 'producer_isolation_enforced': False,
           'fixtures_digest': digest(cases), 'cases': rows,
           'summary': {'naive_accept': sum(x['naive_accept'] for x in rows),
                       'naive_false_accept': sum(x['naive_accept'] and not x['eligible'] for x in rows),
                       'strict_accept': sum(x['strict_accept'] for x in rows),
                       'strict_false_accept': sum(x['strict_accept'] and not x['eligible'] for x in rows)},
           'joint_score': {'functional': f, 'physical': g, 'qualified_ppa': .8,
                           'joint': score, 'incorrect_marginal_product': wrong},
           'cost_example': {'attempts': 10, 'qualified': 2, 'total_core_hours': 160,
                            'core_hours_per_qualified': 80}}
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
