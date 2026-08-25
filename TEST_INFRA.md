# TEST INFRASTRUCTURE SPECIFICATION: Attack on Titan Media & Playback System

## 1. Executive Summary & Philosophy
This document establishes the test philosophy, architecture, 4-tier verification methodology, feature coverage mapping, and quality gates for the *Attack on Titan* media indexing, subtitle synchronization, playlist generation, and VLC smart intro-skipping controller ecosystem.

### Core Testing Principles
1. **Strict Opaque-Box Validation**: Test suites validate public interfaces, file schemas, network protocols, and executable behavior against specifications defined in `PROJECT.md` and `ORIGINAL_REQUEST.md`, without coupling to private implementation details.
2. **Deterministic & Self-Contained Tests**: Every test manages its own fixtures, avoids global side effects, and relies on deterministic mocks for external dependencies (network sockets, HTTP endpoints, subprocess execution).
3. **Progressive Testability**: Tests validate milestone deliverables progressively from static catalog schemas (Tier 1) and asset content integrity (Tier 2) to component contracts (Tier 3) and end-to-end user workflows (Tier 4).
4. **Authoritative Output Derivation**: Expected outputs for schema validation, AniSkip timecode math, SRT format parsing, M3U8 directives, and VLC RC command handling are derived directly from RFCs and project contracts.

---

## 2. 4-Tier Testing Methodology

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   Tier 4: End-to-End & Integration                       │
│    - Full CLI execution (play_aot.py) & argument parsing                 │
│    - Binge mode sequencing & progress.json state updates                 │
├──────────────────────────────────────────────────────────────────────────┤
│                   Tier 3: Component & Protocol Contracts                 │
│    - VLC RC Socket IPC & intro-skip state machine (vlc_controller.py)    │
│    - M3U8 compilation & EXTVLCOPT directives (playlist_generator.py)     │
│    - HTTP Range-request media probe (stream_verifier.py)                 │
├──────────────────────────────────────────────────────────────────────────┤
│                   Tier 2: Asset Integrity & Content Parsing              │
│    - Subtitle library validation (97 .srt files, UTF-8, regex timecodes) │
│    - AniSkip OP/ED timestamp ranges & duration boundary checks           │
├──────────────────────────────────────────────────────────────────────────┤
│                   Tier 1: Schema & Static Catalog Data                   │
│    - episodes.json 97-item catalog structure & field completeness        │
│    - Canonical chronological order (1–97) & unique identifier integrity  │
└──────────────────────────────────────────────────────────────────────────┘
```

### Tier 1: Schema & Static Catalog Verification
- **Target**: `episodes.json` and `indexed_episodes.json`.
- **Scope**:
  - Exactly 97 media items (75 main series TV episodes S1–S4P1, 12 Final Season Part 2 episodes, 2 Final Chapters Movie Specials, 8 Official OVAs).
  - Mandatory keys present on all items: `id`, `type`, `season_num`, `season_title`, `ep_num`, `absolute_num`, `chronological_order`, `title`, `filename`, `archive_path`, `size_mb`, `stream_url`, `subtitle_path`, `timestamps`, `quality`.
  - Uniqueness and domain validity: `id` format (`SxxExx`, `OVAxx`, `S04E29_Special_1`, etc.), `type` in `{'tv', 'movie', 'ova'}`, continuous sequence of `chronological_order` from 1 to 97.
  - Stream URLs match HTTPS protocol with valid domains and extensions (`.mp4`, `.mkv`).

### Tier 2: Asset Integrity & Content Validation
- **Target**: `subtitles/` directory (97 `.srt` files) and AniSkip `timestamps` objects.
- **Scope**:
  - Subtitle file existence: Every `subtitle_path` in `episodes.json` corresponds to a physical `.srt` file.
  - Minimum size threshold: Each `.srt` file must exceed 500 bytes to guarantee non-empty dialogue content.
  - Character encoding: Strict UTF-8 without BOM or decode errors.
  - Subtitle format syntax: Standard SRT format blocks containing numeric indices, regex-validated timecodes (`HH:MM:SS,mmm --> HH:MM:SS,mmm`), and dialogue lines.
  - Monotonicity: Within every `.srt` file, cue start times must be less than cue end times (`start < end`), and subsequent cues must not regress backwards in time (`start[n] >= start[n-1]`).
  - AniSkip timestamp sanity: `op_start < op_end`, `ed_start < ed_end` when present, positive float values, and timestamps within overall episode duration.

### Tier 3: Component & Contract Unit Testing
- **Target**: `stream_verifier.py`, `playlist_generator.py`, `vlc_controller.py`, `subtitle_manager.py`.
- **Scope**:
  - `stream_verifier.py`: Verifies HTTP Range requests (`Range: bytes=0-1024`), validates 206 Partial Content / 200 OK responses, handles timeouts, retries, and offline network error propagation.
  - `playlist_generator.py`: Verifies `#EXTM3U`, `#PLAYLIST:...`, `#EXTINF:-1,...`, and `#EXTVLCOPT:sub-file=...` formatting. Validates generation of chronological, full series release order, and per-season/OVA playlist files.
  - `vlc_controller.py`: Verifies TCP socket lifecycle (connect, retry, timeout, close), command formatting (`get_time\n`, `seek <time>\n`, `pause\n`), output parsing, auto-skip trigger when playback reaches `op_start`, and cold-open prologue protection (no skipping prior to `op_start`).

### Tier 4: End-to-End Integration & CLI Flow Testing
- **Target**: `play_aot.py` and combined workflow.
- **Scope**:
  - CLI invocation with various arguments: `--episode S01E01`, `--season 2`, `--ova 1`, `--special 1`, `--chronological`, `--no-skip`, `--sub-file`.
  - Progress persistence: Reading and updating `progress.json` (`last_played_id`, `history`).
  - Binge mode sequencing: Querying next sequential or chronological episode upon simulated VLC exit.
  - Graceful degradation when VLC binary is missing or stream returns an error.

---

## 3. Feature Inventory Coverage Matrix

| Feature ID | Feature Name | Test Suite | Specific Test Methods | Tier |
|:-----------|:-------------|:-----------|:----------------------|:----:|
| **F1** | Extended Catalog Schema | `test_schema_and_catalog.py` | `test_catalog_total_count`, `test_catalog_required_keys`, `test_catalog_types_distribution`, `test_catalog_unique_ids` | Tier 1 |
| **F2** | S4 Part 2 Media Ingestion | `test_schema_and_catalog.py` | `test_s4_part2_presence_and_metadata`, `test_s4_part2_stream_urls` | Tier 1 |
| **F3** | Final Chapters Specials Ingestion | `test_schema_and_catalog.py` | `test_final_chapters_presence_and_metadata`, `test_final_chapters_movie_special_attributes` | Tier 1 |
| **F4** | OVA Media Ingestion | `test_schema_and_catalog.py` | `test_all_8_ovas_presence_and_metadata`, `test_ova_id_conventions` | Tier 1 |
| **F5** | Media Stream URL Verifier | `test_stream_verifier.py` | `test_range_request_headers`, `test_verify_stream_success_206`, `test_verify_stream_fallback_200`, `test_verify_stream_network_failure`, `test_batch_verify_streams` | Tier 3 |
| **F6** | 97-File UTF-8 Subtitle Library | `test_subtitle_integrity.py` | `test_all_97_subtitle_files_exist`, `test_subtitle_file_sizes`, `test_subtitle_utf8_encoding` | Tier 2 |
| **F7** | Subtitle Validation Engine | `test_subtitle_integrity.py` | `test_srt_regex_timecodes`, `test_srt_monotonic_timecodes`, `test_srt_non_empty_dialogue`, `test_subtitle_manager_contract` | Tier 2/3 |
| **F8** | AniSkip OP/ED Timestamps Store | `test_aniskip_timestamps.py` | `test_all_items_have_timestamps_dict`, `test_op_timestamps_valid_range`, `test_ed_timestamps_valid_range`, `test_timestamps_within_duration` | Tier 2 |
| **F9** | VLC Remote Control IPC Client | `test_vlc_controller.py` | `test_vlc_rc_socket_connection`, `test_vlc_rc_send_command`, `test_vlc_rc_get_time_parsing`, `test_vlc_rc_connection_retry` | Tier 3 |
| **F10** | Smart Intro-Skip Engine | `test_vlc_controller.py` | `test_auto_skip_triggers_at_op_start`, `test_cold_open_prologue_preserved`, `test_no_skip_flag_respected`, `test_ed_skip_or_notification` | Tier 3 |
| **F11** | Interactive Console Hotkeys | `test_vlc_controller.py` | `test_hotkey_parser_s_skips`, `test_hotkey_parser_a_toggles_autoskip`, `test_hotkey_parser_space_pauses` | Tier 3 |
| **F12** | M3U8 Playlist Compiler | `test_playlist_generation.py` | `test_generate_all_playlists_creates_files`, `test_m3u8_extvlcopt_subfile_injection`, `test_season_playlists_match_episodes`, `test_full_series_playlist` | Tier 3 |
| **F13** | Chronological Watch Order | `test_playlist_generation.py`, `test_schema_and_catalog.py` | `test_chronological_order_sequence_1_to_97`, `test_chronological_m3u8_ordering`, `test_ova_interleaving_positions` | Tier 1/3 |
| **F14** | Enhanced CLI Player (`play_aot.py`) | `test_e2e_player.py` (or `test_playlist_generation.py`) | `test_cli_argument_dispatch`, `test_progress_tracking_and_resume`, `test_binge_mode_iteration` | Tier 4 |
| **F15** | Comprehensive Test Suite | `tests/` (All) | Full test execution across all test files with 100% pass threshold | E2E |

---

## 4. Test Directory Layout

```
tests/
├── __init__.py
├── conftest.py                   # Shared pytest fixtures, sample mock data, socket helpers
├── test_schema_and_catalog.py     # F1, F2, F3, F4, F13: Schema, keys, types, 97-item catalog
├── test_subtitle_integrity.py     # F6, F7: UTF-8 encoding, SRT regex timecodes, monotonicity
├── test_aniskip_timestamps.py     # F8: AniSkip OP/ED timestamp ranges & duration bounds
├── test_playlist_generation.py    # F12, F13: M3U8 syntax, #EXTVLCOPT:sub-file, chronological order
├── test_vlc_controller.py         # F9, F10, F11: VLC RC socket IPC, auto-skip, hotkeys
├── test_stream_verifier.py        # F5: HTTP Range requests, 200/206 status codes, retry logic
└── test_e2e_player.py             # F14, F15: CLI argument parsing, progress tracker, binge mode
```

---

## 5. Test Execution & Automation Guide

### Prerequisites
- Python 3.9+
- `pytest` (>= 7.0.0)

### Running Test Suites

1. **Run Full Test Suite (Verbose Mode)**:
   ```bash
   python -m pytest tests/ -v
   ```

2. **Run Individual Test Suites**:
   ```bash
   python -m pytest tests/test_schema_and_catalog.py -v
   python -m pytest tests/test_subtitle_integrity.py -v
   python -m pytest tests/test_aniskip_timestamps.py -v
   python -m pytest tests/test_playlist_generation.py -v
   python -m pytest tests/test_vlc_controller.py -v
   python -m pytest tests/test_stream_verifier.py -v
   ```

3. **Run with Coverage Report**:
   ```bash
   python -m pytest tests/ --cov=. --cov-report=term-missing
   ```

---

## 6. Quality Gates & Pass/Fail Thresholds

| Metric | Target / Gate | Enforcement Action |
|:-------|:--------------|:-------------------|
| **Unit & Contract Test Pass Rate** | **100%** | Zero test failures permitted for Tier 1-3 contract & mock tests. |
| **Catalog Count** | **97 items** | Build failure if total catalog items != 97 once M1 is applied. |
| **Subtitle File Count** | **97 files** | Build failure if subtitle files count != 97 once M2 is applied. |
| **Subtitle Regex Validation** | **100% compliance** | Zero timecode parsing errors allowed. |
| **Timestamp Monotonicity** | **100% compliance** | Subtitle cues must be strictly chronological. |
| **AniSkip Op Start < Op End** | **100% compliance** | All non-zero OP timestamps must satisfy `op_start < op_end`. |
| **Code Style & Linting** | **Zero critical lints** | Flake8 / Ruff / Pylint clean. |

---

## 7. Adversarial & Edge Case Verification

The test suite includes dedicated adversarial test cases:
1. **Network Faults & Partial Responses**: Tests stream verifier under HTTP 403, 404, 500, socket timeouts, and truncated payload deliveries.
2. **Socket Latency & Buffer Fragmentation**: Tests VLC RC controller socket handling when response strings are fragmented across multiple TCP packets (`"12"`, `"8.4\n"`).
3. **Mismatched Subtitle Encodings & Corrupted Timecodes**: Verifies subtitle validator rejects non-UTF8 encodings, overlapping start/end times, and non-SRT formats (e.g. malformed VTT).
4. **Extreme / Missing Intro Scenarios**: Tests episodes with no opening theme (`op_start: 0.0, op_end: 0.0`), opening at 0 seconds (no cold open), or opening at the very end.
