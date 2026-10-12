#!/usr/bin/env python3
"""Synthetic diagnosis-routing/skill-release experiment; no LLM, EDA or PDK.

Run: python3 scripts/experiments/agentic_diagnostic_skill_demo.py
All fixtures are authored protocol tests, NOT a held-out empirical benchmark.
Candidate v1 uses positive cases; v2 adds development-set contraindications.
The frozen test group is evaluated only after both candidates are constructed.
"""
import hashlib
import json
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Case:
    id: str
    design_family: str
    signature: str
    parser: str
    tool: str
    failed_stage: str
    support: bool
    expected: str


POSITIVES = (
    Case('train-l', 'train-a', 'checkout-error', 'p1', 't1', 'launch', True, 'inspect-license'),
    Case('train-b', 'train-b', 'cell-error', 'p1', 't1', 'elaborate', True, 'inspect-library'),
    Case('train-c', 'train-c', 'revision-error', 'p1', 't1', 'configure', True, 'inspect-inputs'),
)
DEVELOPMENT = tuple(
    Case('dev-' + c.id, 'dev-' + c.design_family, c.signature, c.parser,
         c.tool, c.failed_stage, False, 'inspect-upstream')
    for c in POSITIVES
)


def test_cases():
    cases = []
    for c in POSITIVES:
        for i in range(2):
            cases.append(Case(f'test-pos-{c.id}-{i}', f'test-family-{i}', c.signature,
                              'p1', 't1', c.failed_stage, True, c.expected))
        cases.append(Case(f'test-neg-{c.id}', 'test-negative', c.signature,
                          'p1', 't1', c.failed_stage, False, 'inspect-upstream'))
        cases.append(Case(f'test-schema-{c.id}', 'test-future', c.signature,
                          'p2', 't1', c.failed_stage, True, 'unsupported'))
    return tuple(cases)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def construct_skills():
    v1 = {c.signature: {'action': c.expected, 'parser': c.parser,
                       'tool': c.tool, 'stage': c.failed_stage} for c in POSITIVES}
    v2 = json.loads(json.dumps(v1))
    for c in DEVELOPMENT:
        assert c.signature in v2 and c.support is False
        v2[c.signature]['negative_action'] = c.expected
    return v1, v2


def route(case, rules, mode):
    rule = rules.get(case.signature)
    if rule is None:
        return None
    if mode == 'unscoped':
        return rule['action']
    if (case.parser, case.tool, case.failed_stage) != (rule['parser'], rule['tool'], rule['stage']):
        return None
    if not case.support:
        return rule.get('negative_action')
    return rule['action']


def evaluate(cases, rules, mode):
    rows = []
    for c in cases:
        action = route(c, rules, mode)
        rows.append({'id': c.id, 'expected': c.expected, 'action': action,
                     'status': 'abstain' if action is None else 'correct' if action == c.expected else 'wrong'})
    counts = {s: sum(r['status'] == s for r in rows) for s in ('correct', 'wrong', 'abstain')}
    answered = counts['correct'] + counts['wrong']
    return {**counts, 'total': len(cases), 'coverage': answered / len(cases),
            'precision_when_answered': counts['correct'] / answered if answered else None,
            'correct_over_all': counts['correct'] / len(cases), 'cases': rows}


class Registry:
    """In-process reference model of version-checked release decisions.

    Does not model a real transactional storage backend or distributed atomicity.
    """
    def __init__(self, bundles):
        self.bundles = bundles
        self.current = 'v1'
        self.history = []
        self.revoked = set()

    def release(self, version, expected, report):
        if expected != self.current:
            return 'conflict'
        if version in self.revoked:
            return 'revoked'
        if report['bundle_digest'] != digest(self.bundles[version]):
            return 'digest-mismatch'
        if report['wrong'] > 0 or report['coverage'] < 0.5:
            return 'rejected'
        self.history.append({'from': self.current, 'to': version, 'reason': 'evaluation'})
        self.current = version
        return 'released'

    def revoke(self, version):
        self.revoked.add(version)
        if self.current == version:
            self.history.append({'from': version, 'to': 'v1', 'reason': 'revocation'})
            self.current = 'v1'


def run():
    v1, v2 = construct_skills()
    # Freeze all artifacts before evaluating the authored test group.
    bundles = {'v1': v1, 'v2': v2}
    tests = test_cases()
    assert set(c.design_family for c in POSITIVES + DEVELOPMENT).isdisjoint(c.design_family for c in tests)
    evaluated = {
        'unscoped_v1': evaluate(tests, v1, 'unscoped'),
        'scoped_v1': evaluate(tests, v1, 'scoped'),
        'scoped_v2': evaluate(tests, v2, 'scoped'),
    }
    assert [evaluated[k][s] for k in evaluated for s in ('correct', 'wrong', 'abstain')] == [6, 6, 0, 6, 0, 6, 9, 0, 3]
    registry = Registry(bundles)
    report = {**evaluated['scoped_v2'], 'bundle_digest': digest(v2)}
    bad_report = {**report, 'bundle_digest': digest(v1)}
    checks = {
        'mismatched_report': registry.release('v2', 'v1', bad_report),
        'promotion': registry.release('v2', 'v1', report),
        'stale_promotion': registry.release('v2', 'v1', report),
    }
    assert checks == {'mismatched_report': 'digest-mismatch', 'promotion': 'released', 'stale_promotion': 'conflict'}
    registry.revoke('v2')
    checks['current_after_revocation'] = registry.current
    checks['reuse_revoked'] = registry.release('v2', 'v1', report)
    assert registry.current == 'v1' and checks['reuse_revoked'] == 'revoked'
    return {
        'fixture_kind': 'authored_synthetic_protocol_cases_not_empirical_generalization',
        'model_calls': 0, 'eda_calls': 0,
        'counts': {'positive_training': 3, 'negative_development': 3, 'test_cases': 12},
        'bundle_digests': {k: digest(v) for k, v in bundles.items()},
        'test_fixture_digest': digest([asdict(c) for c in tests]),
        'evaluations': evaluated, 'release_checks': checks,
        'history': registry.history,
        'limits': ['No language generation, LLM evaluation, simulator or tool execution',
                   'Small authored fixtures share rule structure; no statistical independence',
                   'In-process release model; no distributed storage, crash durability or race test'],
    }


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, ensure_ascii=False))
