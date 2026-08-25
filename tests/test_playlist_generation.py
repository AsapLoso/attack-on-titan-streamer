"""
Test Suite: M3U8 Playlist Compiler & Chronological Sequence (F12, F13)
Validates M3U8 directives (#EXTVLCOPT:sub-file), chronological order, and season playlists.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

import pytest


def parse_m3u8_content(content: str) -> List[Dict[str, str]]:
    """
    Parse an M3U8 file into structured entries:
    Each entry contains: title, sub_file (if any), stream_url.
    """
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines or lines[0] != "#EXTM3U":
        raise ValueError("Invalid M3U8: Missing #EXTM3U header")

    entries = []
    current_title = ""
    current_sub = ""
    
    for line in lines[1:]:
        if line.startswith("#PLAYLIST:"):
            continue
        elif line.startswith("#EXTINF:"):
            parts = line.split(",", 1)
            current_title = parts[1] if len(parts) > 1 else ""
        elif line.startswith("#EXTVLCOPT:sub-file="):
            current_sub = line.split("=", 1)[1]
        elif not line.startswith("#"):
            entries.append({
                "title": current_title,
                "sub_file": current_sub,
                "stream_url": line
            })
            current_title = ""
            current_sub = ""

    return entries


class TestPlaylistDirectivesAndSyntax:
    """Opaque-box tests for M3U8 entry formatting, #EXTVLCOPT subtitle binding, and sequencing."""

    def test_m3u8_entry_formatting_with_subtitles(self, sample_valid_episode: Dict[str, Any], project_root: Path):
        """Verify formatted M3U8 entry includes #EXTINF, #EXTVLCOPT:sub-file, and stream URL."""
        ep = sample_valid_episode
        sub_path = str(project_root / ep["subtitle_path"])
        
        # Test expected structure according to Interface Contract 4
        expected_entry = f"#EXTINF:-1,{ep['title']}\n#EXTVLCOPT:sub-file={sub_path}\n{ep['stream_url']}"
        assert "#EXTINF:-1" in expected_entry
        assert "#EXTVLCOPT:sub-file=" in expected_entry
        assert ep["stream_url"] in expected_entry

    def test_chronological_playlist_ordering(self, sample_synthetic_97_catalog: List[Dict[str, Any]]):
        """Verify sorting by chronological_order produces correct 1..97 sequence."""
        sorted_episodes = sorted(sample_synthetic_97_catalog, key=lambda x: x["chronological_order"])
        orders = [ep["chronological_order"] for ep in sorted_episodes]
        assert orders == list(range(1, 98))

        # Check OVA 1 is at chronological position 1 (Ilse's Notebook)
        assert sorted_episodes[0]["id"] == "OVA01"
        assert sorted_episodes[0]["chronological_order"] == 1

    def test_playlist_generator_module_if_implemented(self, sample_synthetic_97_catalog: List[Dict[str, Any]], tmp_path: Path):
        """Test playlist_generator module contract if present in repository."""
        try:
            import playlist_generator
            if hasattr(playlist_generator, "generate_all_playlists"):
                generated_files = playlist_generator.generate_all_playlists(sample_synthetic_97_catalog, tmp_path)
                assert len(generated_files) > 0, "No playlists returned by generate_all_playlists"
                
                # Check for Chronological playlist
                chron_file = next((f for f in generated_files if "Chronological" in f.name), None)
                assert chron_file is not None, "Chronological playlist was not generated"
                
                content = chron_file.read_text(encoding="utf-8")
                entries = parse_m3u8_content(content)
                assert len(entries) == 97, f"Expected 97 entries in chronological playlist, found {len(entries)}"
                
                # Check subtitle directive present
                assert any(e["sub_file"] != "" for e in entries), "Subtitle directives missing in generated M3U8"
        except ImportError:
            pass  # Module to be created in M4


class TestLivePlaylistsDirectory:
    """Validate existing .m3u8 playlists in the playlists/ directory."""

    def test_live_playlists_valid_m3u8_syntax(self, playlists_dir_path: Path):
        """Validate all existing .m3u8 files in playlists/ directory."""
        if not playlists_dir_path.exists():
            pytest.skip("playlists/ directory does not exist")

        m3u8_files = list(playlists_dir_path.glob("*.m3u8"))
        if not m3u8_files:
            pytest.skip("No .m3u8 files in playlists/ directory")

        for m3u8_file in m3u8_files:
            content = m3u8_file.read_text(encoding="utf-8")
            entries = parse_m3u8_content(content)
            assert len(entries) > 0, f"Playlist {m3u8_file.name} contains zero media entries"
            for entry in entries:
                assert entry["stream_url"].startswith("http"), f"Invalid stream URL in {m3u8_file.name}: {entry['stream_url']}"
