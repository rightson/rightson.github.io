#!/usr/bin/env python3
"""DS04 deterministic state model; not a network/cache implementation.

Run: python3 scripts/experiments/ds04_cache_refill_demo.py
Time is virtual seconds. Source reads are trusted, fresh authoritative reads.
Atomic methods below represent a per-key critical section, not real locking.
"""
from dataclasses import dataclass, replace
import unittest


@dataclass(frozen=True)
class Token:
    epoch: int
    incarnation: str
    key: str
    generation: int
    serial: int
    expires: float


@dataclass(frozen=True)
class SourceRead:
    version: int
    started: float
    payload: str


@dataclass(frozen=True)
class Value:
    version: int
    payload: str
    hard_deadline: float

    def usable(self, now):
        return now < self.hard_deadline


class Owner:
    def __init__(self, epoch=7, incarnation="boot-A"):
        self.epoch = epoch
        self.incarnation = incarnation
        self.serial = 0  # never reset within this incarnation
        self.state = {}

    def entry(self, key):
        return self.state.setdefault(key, {
            "generation": 0, "floor": 0, "token": None, "value": None
        })

    def acquire(self, key, now):
        e = self.entry(key)
        if e["token"] is not None and now < e["token"].expires:
            return None
        self.serial += 1
        token = Token(self.epoch, self.incarnation, key,
                      e["generation"], self.serial, now + 1.0)
        e["token"] = token
        return token

    def invalidate(self, key, version):
        e = self.entry(key)
        if version <= e["floor"]:
            return  # duplicate/older notification
        e["floor"] = version
        e["generation"] += 1
        e["token"] = None
        # Older payload may be served only under its original hard deadline.

    def fill(self, token, read, now):
        e = self.entry(token.key)
        hard = read.started + 29.8
        if (token.epoch != self.epoch
                or token.incarnation != self.incarnation
                or token != e["token"]
                or token.generation != e["generation"]
                or now >= token.expires
                or read.started > now
                or now - read.started > 1.0
                or read.version < e["floor"]
                or now >= hard):
            return False
        e["floor"] = max(e["floor"], read.version)
        e["value"] = Value(read.version, read.payload, hard)
        e["token"] = None  # single-use right
        return True

    def cutover(self, epoch):
        assert epoch > self.epoch
        self.epoch = epoch
        for e in self.state.values():
            e["generation"] += 1
            e["token"] = None

    def evict_metadata(self, key):
        # Real system: drain/cancel in-flight operations before forgetting floor.
        # The owner-wide serial prevents reuse even if generation starts at zero.
        self.state.pop(key, None)


class Tests(unittest.TestCase):
    def test_invalidation_rejects_late_v41(self):
        o = Owner(); t = o.acquire("tenantA:item1", 0)
        o.invalidate(t.key, 42)
        self.assertFalse(o.fill(t, SourceRead(41, 0, "old"), .2))
        n = o.acquire(t.key, .2)
        self.assertTrue(o.fill(n, SourceRead(42, .2, "new"), .3))

    def test_reordered_notifications_do_not_lower_floor(self):
        o = Owner(); o.invalidate("k", 42)
        t = o.acquire("k", .1)
        o.invalidate("k", 41); o.invalidate("k", 42)
        self.assertEqual(o.entry("k")["floor"], 42)
        self.assertTrue(o.fill(t, SourceRead(42, .1, "new"), .2))

    def test_expired_holder_cannot_overwrite_new_holder(self):
        o = Owner(); old = o.acquire("k", 0)
        self.assertIsNone(o.acquire("k", .5))
        new = o.acquire("k", 1.01)
        self.assertFalse(o.fill(old, SourceRead(41, 0, "old"), 1.1))
        self.assertTrue(o.fill(new, SourceRead(42, 1.01, "new"), 1.2))

    def test_restart_changes_incarnation(self):
        old_owner = Owner(); t = old_owner.acquire("k", 0)
        new_owner = Owner(incarnation="boot-B")
        new_owner.acquire("k", 0)
        self.assertFalse(new_owner.fill(t, SourceRead(41, 0, "old"), .1))

    def test_cutover_rejects_old_epoch(self):
        o = Owner(); old = o.acquire("k", 0)
        o.cutover(8); new = o.acquire("k", .1)
        self.assertFalse(o.fill(old, SourceRead(41, 0, "old"), .2))
        self.assertTrue(o.fill(new, SourceRead(42, .1, "new"), .2))

    def test_metadata_eviction_has_no_token_ABA(self):
        o = Owner(); old = o.acquire("k", 0)
        o.evict_metadata("k"); new = o.acquire("k", .1)
        self.assertEqual(old.generation, new.generation)
        self.assertNotEqual(old.serial, new.serial)
        self.assertFalse(o.fill(old, SourceRead(41, 0, "old"), .2))
        self.assertTrue(o.fill(new, SourceRead(42, .1, "new"), .2))

    def test_token_is_single_use(self):
        o = Owner(); t = o.acquire("k", 0)
        self.assertTrue(o.fill(t, SourceRead(42, 0, "new"), .1))
        self.assertFalse(o.fill(t, SourceRead(42, 0, "new"), .2))

    def test_floor_blocks_older_source_read(self):
        o = Owner(); o.invalidate("k", 42); t = o.acquire("k", 0)
        self.assertFalse(o.fill(t, SourceRead(41, 0, "lagged"), .1))

    def test_copy_inherits_original_deadline(self):
        o = Owner(); t = o.acquire("k", 0)
        self.assertTrue(o.fill(t, SourceRead(42, 0, "new"), .2))
        original = o.entry("k")["value"]
        copied = replace(original)  # receive at t=20; no new lifetime
        self.assertTrue(copied.usable(29.79))
        self.assertFalse(copied.usable(29.8))
        self.assertEqual(copied.hard_deadline, original.hard_deadline)

    def test_tenant_keys_have_separate_ownership(self):
        o = Owner(); a = o.acquire("tenantA:item1", 0)
        b = o.acquire("tenantB:item1", 0)
        o.invalidate(a.key, 42)
        self.assertFalse(o.fill(a, SourceRead(41, 0, "A"), .1))
        self.assertTrue(o.fill(b, SourceRead(1, 0, "B"), .1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
