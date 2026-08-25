"""
Test Suite: End-to-End CLI Player and Progress Tracker Integration (F14, F15)
Validates CLI invocation, episode sequencing, progress tracking, and VLC argument construction.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock

import pytest
import play_aot


class TestProgressTracker:
    """Validate user playback tracking in progress.json."""

    def test_load_and_save_progress(self, tmp_path: Path, monkeypatch):
        """Verify saving and loading progress updates last_played_id and history."""
        fake_progress_file = tmp_path / "progress.json"
        monkeypatch.setattr(play_aot, "PROGRESS_FILE", fake_progress_file)

        initial = play_aot.load_progress()
        assert initial["last_played_id"] is None
        assert initial["history"] == []

        ep = {"id": "S01E01", "season_title": "Season 1", "ep_num": 1}
        play_aot.save_progress(ep)

        loaded = play_aot.load_progress()
        assert loaded["last_played_id"] == "S01E01"
        assert "S01E01" in loaded["history"]

        # Save next episode
        ep2 = {"id": "S01E02", "season_title": "Season 1", "ep_num": 2}
        play_aot.save_progress(ep2)

        loaded2 = play_aot.load_progress()
        assert loaded2["last_played_id"] == "S01E02"
        assert loaded2["history"] == ["S01E01", "S01E02"]


class TestEpisodeSequencing:
    """Validate next episode resolution in standard and chronological order."""

    def test_get_next_episode_sequential(self, sample_synthetic_97_catalog: List[Dict[str, Any]]):
        """Verify get_next_episode retrieves the immediately following episode."""
        episodes = sample_synthetic_97_catalog
        next_ep = play_aot.get_next_episode(episodes, "S01E01")
        assert next_ep is not None
        assert next_ep["id"] == "S01E02"

    def test_get_next_episode_at_end_returns_none(self, sample_synthetic_97_catalog: List[Dict[str, Any]]):
        """Verify get_next_episode returns None when at the end of catalog."""
        episodes = sample_synthetic_97_catalog
        last_id = episodes[-1]["id"]
        next_ep = play_aot.get_next_episode(episodes, last_id)
        assert next_ep is None


class TestVlcCommandConstruction:
    """Verify construction of VLC launch commands with subtitle and metadata flags."""

    @patch("subprocess.run")
    def test_stream_episode_command_arguments(self, mock_subproc_run, sample_valid_episode: Dict[str, Any], monkeypatch, tmp_path: Path):
        """Verify stream_episode passes stream URL, meta-title, and play-and-exit."""
        fake_progress_file = tmp_path / "progress.json"
        monkeypatch.setattr(play_aot, "PROGRESS_FILE", fake_progress_file)
        mock_subproc_run.return_value = MagicMock(returncode=0)

        ep = sample_valid_episode
        result = play_aot.stream_episode(ep, vlc_path="vlc.exe", wait_finish=True)
        assert result is True

        mock_subproc_run.assert_called_once()
        args = mock_subproc_run.call_args[0][0]
        assert args[0] == "vlc.exe"
        assert ep["stream_url"] in args
        assert any("--meta-title=" in a for a in args)
        assert "--play-and-exit" in args
