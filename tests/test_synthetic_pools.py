"""Tests for sampling pools and stratification."""

from __future__ import annotations

import random
from collections import Counter

import pytest

from src.synthetic.pools import LEANING_CATEGORIES, build_stratified_leanings


def test_stratification_counts():
    counts = Counter(build_stratified_leanings(20, rng=random.Random(0)))
    assert set(counts) == set(LEANING_CATEGORIES)
    assert set(counts.values()) == {2, 3}  # 2 full cycles + 4 remainder.
    assert sum(counts.values()) == 20


def test_remainder_has_no_duplicates():
    leanings = build_stratified_leanings(10, rng=random.Random(0))
    assert len(leanings) == 10
    assert len(set(leanings)) == 8


def test_zero_returns_empty():
    assert build_stratified_leanings(0, rng=random.Random(0)) == []


def test_negative_rejected():
    with pytest.raises(ValueError, match="must not be negative"):
        build_stratified_leanings(-5)
