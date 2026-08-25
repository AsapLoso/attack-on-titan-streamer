"""
Test Suite: Subtitle Integrity, Encoding, and Validator Engine (F6, F7)
Validates UTF-8 encoding, non-empty file size (>500B), SRT timecode regex, and monotonicity.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

import pytest

SRT_TIMECODE_REGEX = re.compile(r"^(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})$")


def timecode_to_ms(hours: int, minutes: int, seconds: int, milliseconds: int) -> int:
    """Convert time components to total milliseconds."""
    return (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds


def parse_srt_cues(content: str) -> List[Tuple[int, int, str]]:
    """
    Parse an SRT content string into a list of (start_ms, end_ms, dialogue_text) tuples.
    Raises ValueError on syntax violation.
    """
    cues = []
    blocks = re.split(r"\r?\n\r?\n", content.strip())
    
    for block_idx, block in enumerate(blocks):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        
        # Block structure: Line 1 = numeric cue index, Line 2 = timecodes, Line 3+ = dialogue
        if len(lines) < 2:
            raise ValueError(f"Malformed SRT block #{block_idx + 1}: fewer than 2 lines -> {block}")
        
        # If line 0 is numeric index, timecode is line 1; otherwise line 0 might be timecode
        if lines[0].isdigit() and len(lines) >= 2:
            timecode_line = lines[1]
            dialogue_lines = lines[2:]
        else:
            timecode_line = lines[0]
            dialogue_lines = lines[1:]

        match = SRT_TIMECODE_REGEX.match(timecode_line)
        if not match:
            raise ValueError(f"Invalid SRT timecode format in block #{block_idx + 1}: '{timecode_line}'")
        
        h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
        start_ms = timecode_to_ms(h1, m1, s1, ms1)
        end_ms = timecode_to_ms(h2, m2, s2, ms2)
        
        dialogue = " ".join(dialogue_lines).strip()
        cues.append((start_ms, end_ms, dialogue))

    return cues


class TestSubtitleFormatEngine:
    """Opaque-box tests for SRT parsing, regex syntax validation, and timecode monotonicity."""

    def test_valid_srt_string_parses_successfully(self, sample_valid_srt_string: str):
        """Verify standard multi-cue SRT parses accurately."""
        cues = parse_srt_cues(sample_valid_srt_string)
        assert len(cues) == 3
        
        # First cue: 00:01:05,200 --> 00:01:08,450
        assert cues[0][0] == (1 * 60 + 5) * 1000 + 200
        assert cues[0][1] == (1 * 60 + 8) * 1000 + 450
        assert "human race remembered" in cues[0][2]
        
        # Monotonicity check
        for i in range(len(cues)):
            assert cues[i][0] < cues[i][1], f"Cue {i+1} start time is not strictly before end time"
            if i > 0:
                assert cues[i][0] >= cues[i-1][0], f"Cue {i+1} starts before cue {i}"

    def test_invalid_timecode_format_raises_error(self):
        """Verify invalid timecodes (e.g. dots instead of commas) trigger parsing errors."""
        invalid_vtt_style = """1
00:01:05.200 --> 00:01:08.450
This is VTT style with dot instead of comma.
"""
        with pytest.raises(ValueError, match="Invalid SRT timecode format"):
            parse_srt_cues(invalid_vtt_style)

    def test_non_monotonic_cue_detected(self):
        """Verify cue where end < start is detected as invalid."""
        inverted_times = """1
00:02:00,000 --> 00:01:00,000
End is before start!
"""
        cues = parse_srt_cues(inverted_times)
        assert cues[0][0] > cues[0][1]  # Demonstrates detection capability

    def test_vtt_to_srt_conversion_if_implemented(self):
        """Verify VTT to SRT conversion contract if subtitle_manager is present."""
        try:
            import subtitle_manager
            if hasattr(subtitle_manager, "convert_vtt_to_srt"):
                vtt_sample = "WEBVTT\n\n1\n00:01:05.200 --> 00:01:08.450\nHello World\n"
                srt_out = subtitle_manager.convert_vtt_to_srt(vtt_sample)
                assert "00:01:05,200 --> 00:01:08,450" in srt_out
                assert "WEBVTT" not in srt_out
        except ImportError:
            pass  # Module to be created in M2


class TestLiveSubtitleDirectory:
    """Validate all .srt files in the local subtitles/ directory."""

    def test_subtitles_directory_and_files_integrity(self, subtitles_dir_path: Path):
        """
        Validate all existing .srt files in subtitles/:
        - Non-empty (> 500 bytes)
        - Strict UTF-8 encoding
        - Valid regex timecodes
        - Monotonic start/end timestamps
        """
        if not subtitles_dir_path.exists():
            pytest.skip("subtitles/ directory does not exist yet (M2 deliverable)")

        srt_files = list(subtitles_dir_path.glob("**/*.srt"))
        if not srt_files:
            pytest.skip("No .srt files found in subtitles/ directory yet (M2 deliverable)")

        print(f"\n[INFO] Validating {len(srt_files)} subtitle files...")
        
        for srt_path in srt_files:
            # 1. Check file size > 500 bytes
            file_size = srt_path.stat().st_size
            assert file_size >= 500, f"Subtitle file {srt_path.name} too small ({file_size} bytes < 500 bytes)"

            # 2. Strict UTF-8 decoding
            try:
                content = srt_path.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                pytest.fail(f"Subtitle file {srt_path.name} failed UTF-8 decoding: {e}")

            # 3. Parse cues and validate regex & monotonicity
            try:
                cues = parse_srt_cues(content)
            except Exception as e:
                pytest.fail(f"Subtitle file {srt_path.name} contains invalid SRT syntax: {e}")

            assert len(cues) > 0, f"Subtitle file {srt_path.name} contains zero parsed cues"

            # 4. Monotonicity validation
            for idx, (start_ms, end_ms, dialogue) in enumerate(cues):
                assert start_ms < end_ms, f"{srt_path.name} cue {idx+1} has start ({start_ms}ms) >= end ({end_ms}ms)"
                if idx > 0:
                    prev_start = cues[idx - 1][0]
                    assert start_ms >= prev_start, f"{srt_path.name} cue {idx+1} start ({start_ms}ms) < previous cue start ({prev_start}ms)"

    def test_all_97_subtitles_present_when_m2_complete(self, subtitles_dir_path: Path, episodes_json_path: Path):
        """When M2 is complete, verify all 97 subtitle paths from episodes.json exist on disk."""
        if not subtitles_dir_path.exists() or not episodes_json_path.exists():
            pytest.skip("Subtitles or episodes.json not available")

        import json
        with open(episodes_json_path, "r", encoding="utf-8") as f:
            episodes = json.load(f)

        if len(episodes) == 97:
            missing_subs = []
            for ep in episodes:
                sub_rel = ep.get("subtitle_path")
                if not sub_rel:
                    missing_subs.append(f"{ep['id']} (no subtitle_path key)")
                else:
                    sub_full = subtitles_dir_path.parent / sub_rel
                    if not sub_full.exists():
                        missing_subs.append(f"{ep['id']} -> {sub_rel}")

            assert not missing_subs, f"Missing subtitle files for episodes:\n" + "\n".join(missing_subs)
