"""
Test Suite: Catalog Schema and Metadata Ingestion (F1, F2, F3, F4, F13)
Validates the unified 97-item catalog structure, required keys, stream URLs, and types.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

import pytest

REQUIRED_SCHEMA_KEYS = {
    "id",
    "type",
    "season_num",
    "season_title",
    "ep_num",
    "absolute_num",
    "chronological_order",
    "title",
    "filename",
    "archive_path",
    "size_mb",
    "stream_url",
    "subtitle_path",
    "timestamps",
    "quality"
}

ALLOWED_TYPES = {"tv", "movie", "ova"}

OVA_TITLES_EXPECTED = [
    "Ilse's Notebook",
    "The Sudden Visitor",
    "Distress",
    "No Regrets: Part 1",
    "No Regrets: Part 2",
    "Wall Sina, Goodbye - Part 1",
    "Wall Sina, Goodbye - Part 2",
    "Lost in the Cruel World"
]


class TestEpisodeSchemaContract:
    """Validate individual episode dictionary contracts against PROJECT.md § Interface Contracts."""

    def test_single_tv_episode_schema(self, sample_valid_episode: Dict[str, Any]):
        """Verify TV episode contains all required keys and correct types."""
        ep = sample_valid_episode
        missing_keys = REQUIRED_SCHEMA_KEYS - set(ep.keys())
        assert not missing_keys, f"TV episode missing required keys: {missing_keys}"
        assert ep["type"] in ALLOWED_TYPES
        assert isinstance(ep["season_num"], int)
        assert isinstance(ep["ep_num"], (int, float, str))
        assert isinstance(ep["chronological_order"], int)
        assert isinstance(ep["size_mb"], (int, float))
        assert isinstance(ep["timestamps"], dict)
        assert ep["stream_url"].startswith("https://")
        assert ep["subtitle_path"].endswith(".srt")

    def test_single_movie_special_schema(self, sample_valid_movie_special: Dict[str, Any]):
        """Verify movie special contains all required keys and valid movie type."""
        ep = sample_valid_movie_special
        missing_keys = REQUIRED_SCHEMA_KEYS - set(ep.keys())
        assert not missing_keys, f"Movie special missing required keys: {missing_keys}"
        assert ep["type"] == "movie"
        assert "Special" in ep["title"] or "Final Chapters" in ep["title"]
        assert ep["duration_seconds"] >= 3000.0  # Movie length check

    def test_single_ova_schema(self, sample_valid_ova: Dict[str, Any]):
        """Verify OVA contains all required keys and valid ova type."""
        ep = sample_valid_ova
        missing_keys = REQUIRED_SCHEMA_KEYS - set(ep.keys())
        assert not missing_keys, f"OVA missing required keys: {missing_keys}"
        assert ep["type"] == "ova"
        assert ep["id"].startswith("OVA") or "OVA" in ep["id"]


class TestSynthetic97CatalogInvariants:
    """Validate the mathematical invariants and constraints of a full 97-item catalog."""

    def test_synthetic_catalog_total_count(self, sample_synthetic_97_catalog: List[Dict[str, Any]]):
        """Ensure full catalog consists of exactly 97 items."""
        assert len(sample_synthetic_97_catalog) == 97

    def test_synthetic_catalog_unique_ids(self, sample_synthetic_97_catalog: List[Dict[str, Any]]):
        """Ensure all episode IDs are strictly unique."""
        ids = [ep["id"] for ep in sample_synthetic_97_catalog]
        assert len(ids) == len(set(ids)), "Duplicate episode IDs detected in catalog"

    def test_synthetic_catalog_chronological_ordering(self, sample_synthetic_97_catalog: List[Dict[str, Any]]):
        """Ensure chronological_order forms a continuous sequence from 1 to 97."""
        chron_orders = sorted([ep["chronological_order"] for ep in sample_synthetic_97_catalog])
        assert chron_orders == list(range(1, 98)), "Chronological order sequence is not a continuous 1..97 range"

    def test_synthetic_catalog_types_breakdown(self, sample_synthetic_97_catalog: List[Dict[str, Any]]):
        """Ensure accurate distribution: 87 TV (75 S1-S4P1 + 12 S4P2), 2 Movies, 8 OVAs."""
        type_counts = {}
        for ep in sample_synthetic_97_catalog:
            t = ep["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        assert type_counts.get("tv", 0) == 87
        assert type_counts.get("movie", 0) == 2
        assert type_counts.get("ova", 0) == 8


class TestLiveEpisodesJson:
    """Validate the actual episodes.json file present in the project workspace."""

    def test_episodes_json_readable_and_non_empty(self, episodes_json_path: Path):
        """Verify episodes.json exists and is valid JSON."""
        assert episodes_json_path.exists(), f"episodes.json not found at {episodes_json_path}"
        with open(episodes_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) > 0, "episodes.json is empty"

    def test_episodes_json_all_entries_valid_schema(self, episodes_json_path: Path):
        """Verify every entry in episodes.json satisfies schema contract."""
        with open(episodes_json_path, "r", encoding="utf-8") as f:
            episodes = json.load(f)

        ids_seen = set()
        for idx, ep in enumerate(episodes):
            assert "id" in ep, f"Entry at index {idx} missing 'id'"
            assert ep["id"] not in ids_seen, f"Duplicate ID '{ep['id']}' at index {idx}"
            ids_seen.add(ep["id"])

            # Check core keys present in current and future versions
            assert "season_num" in ep, f"Entry {ep['id']} missing 'season_num'"
            assert "ep_num" in ep, f"Entry {ep['id']} missing 'ep_num'"
            assert "stream_url" in ep, f"Entry {ep['id']} missing 'stream_url'"
            assert ep["stream_url"].startswith("http"), f"Entry {ep['id']} invalid stream_url: {ep['stream_url']}"

            # If extended keys are populated, validate them strictly
            if "type" in ep:
                assert ep["type"] in ALLOWED_TYPES, f"Entry {ep['id']} has invalid type {ep['type']}"
            if "timestamps" in ep:
                assert isinstance(ep["timestamps"], dict), f"Entry {ep['id']} timestamps must be a dict"
                assert "op_start" in ep["timestamps"], f"Entry {ep['id']} timestamps missing 'op_start'"
                assert "op_end" in ep["timestamps"], f"Entry {ep['id']} timestamps missing 'op_end'"

    def test_episodes_json_target_97_items_when_extended(self, episodes_json_path: Path):
        """Verify that when the extended catalog is ingested (M1), exactly 97 items are present."""
        with open(episodes_json_path, "r", encoding="utf-8") as f:
            episodes = json.load(f)

        # In M1+ this must be 97 items.
        if len(episodes) == 97:
            # Full catalog checks:
            ids = [ep["id"] for ep in episodes]
            # 1. Check Final Season Part 2 episodes (S04E17 - S04E28)
            s4p2_ids = [f"S04E{i:02d}" for i in range(17, 29)]
            for s4_id in s4p2_ids:
                assert s4_id in ids, f"Final Season Part 2 episode {s4_id} missing from 97-item catalog"

            # 2. Check Final Chapters Specials (Special 1 and Special 2)
            specials_found = [ep for ep in episodes if ep.get("type") == "movie" or "Special" in ep["id"]]
            assert len(specials_found) >= 2, "The Final Chapters Specials (2 items) missing from catalog"

            # 3. Check 8 OVAs
            ovas_found = [ep for ep in episodes if ep.get("type") == "ova" or ep["id"].startswith("OVA")]
            assert len(ovas_found) == 8, f"Expected 8 OVAs in catalog, found {len(ovas_found)}"

            # 4. Check chronological order continuity
            chron_orders = [ep.get("chronological_order") for ep in episodes if "chronological_order" in ep]
            if len(chron_orders) == 97:
                assert sorted(chron_orders) == list(range(1, 98))
        else:
            # Baseline catalog (75 episodes) before M1 extension
            assert len(episodes) in (75, 97), f"Catalog has unexpected length {len(episodes)} (expected 75 or 97)"
