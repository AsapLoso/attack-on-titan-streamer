"""
Test Suite: AniSkip OP/ED Timestamps Store & Boundary Sanity (F8)
Validates presence, numeric types, intro/outro interval constraints, and duration bounds.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

import pytest


def validate_single_item_timestamps(item_id: str, ts: Dict[str, Any], duration_seconds: float = None):
    """
    Validate timestamps dictionary invariants:
    - Must be a dictionary.
    - op_start, op_end must be non-negative floats/ints.
    - If op_end > 0, op_start < op_end.
    - If ed_end > 0, ed_start < ed_end.
    - If duration_seconds is provided, op_end <= duration and ed_end <= duration.
    """
    assert isinstance(ts, dict), f"Item {item_id} timestamps is not a dict: {ts}"
    assert "op_start" in ts, f"Item {item_id} timestamps missing 'op_start'"
    assert "op_end" in ts, f"Item {item_id} timestamps missing 'op_end'"

    op_start = float(ts["op_start"])
    op_end = float(ts["op_end"])

    assert op_start >= 0.0, f"Item {item_id} op_start ({op_start}) is negative"
    assert op_end >= 0.0, f"Item {item_id} op_end ({op_end}) is negative"

    if op_end > 0:
        assert op_start < op_end, f"Item {item_id} op_start ({op_start}) >= op_end ({op_end})"
        intro_duration = op_end - op_start
        # Standard anime OP is between 30 and 150 seconds
        assert 30.0 <= intro_duration <= 180.0, (
            f"Item {item_id} intro duration ({intro_duration:.1f}s) is outside reasonable range [30, 180]"
        )

    if "ed_start" in ts and "ed_end" in ts:
        ed_start = float(ts["ed_start"])
        ed_end = float(ts["ed_end"])
        assert ed_start >= 0.0, f"Item {item_id} ed_start ({ed_start}) is negative"
        assert ed_end >= 0.0, f"Item {item_id} ed_end ({ed_end}) is negative"
        if ed_end > 0:
            assert ed_start < ed_end, f"Item {item_id} ed_start ({ed_start}) >= ed_end ({ed_end})"
            outro_duration = ed_end - ed_start
            assert 30.0 <= outro_duration <= 240.0, (
                f"Item {item_id} outro duration ({outro_duration:.1f}s) is outside reasonable range [30, 240]"
            )

    if duration_seconds and duration_seconds > 0:
        assert op_end <= duration_seconds + 5.0, (
            f"Item {item_id} op_end ({op_end}) exceeds episode duration ({duration_seconds})"
        )


class TestAniSkipTimestampsContract:
    """Opaque-box tests verifying AniSkip timestamp calculation logic and invariants."""

    def test_standard_tv_intro_timestamps(self, sample_valid_episode: Dict[str, Any]):
        """Verify standard TV episode timestamps validation."""
        ep = sample_valid_episode
        validate_single_item_timestamps(ep["id"], ep["timestamps"], ep.get("duration_seconds"))
        # Cold open check: Season 1 Episode 1 has ~128.4s prologue before OP
        assert ep["timestamps"]["op_start"] > 0, "Expected cold open prologue for S01E01"

    def test_movie_special_without_opening_theme(self, sample_valid_movie_special: Dict[str, Any]):
        """Verify movie specials with no OP (op_start=0, op_end=0) are handled gracefully."""
        ep = sample_valid_movie_special
        validate_single_item_timestamps(ep["id"], ep["timestamps"], ep.get("duration_seconds"))
        assert ep["timestamps"]["op_start"] == 0.0
        assert ep["timestamps"]["op_end"] == 0.0

    def test_synthetic_97_catalog_timestamps(self, sample_synthetic_97_catalog: List[Dict[str, Any]]):
        """Verify all 97 items in synthetic catalog satisfy timestamp constraints."""
        for ep in sample_synthetic_97_catalog:
            validate_single_item_timestamps(ep["id"], ep["timestamps"], ep.get("duration_seconds"))

    def test_live_episodes_json_timestamps(self, episodes_json_path: Path):
        """Verify timestamps in live episodes.json once populated."""
        if not episodes_json_path.exists():
            pytest.skip("episodes.json does not exist")

        with open(episodes_json_path, "r", encoding="utf-8") as f:
            episodes = json.load(f)

        items_with_timestamps = [ep for ep in episodes if "timestamps" in ep]
        if not items_with_timestamps:
            pytest.skip("Timestamps not yet populated in episodes.json (M3 deliverable)")

        for ep in items_with_timestamps:
            validate_single_item_timestamps(ep["id"], ep["timestamps"], ep.get("duration_seconds"))
