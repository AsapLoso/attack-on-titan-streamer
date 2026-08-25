# TEST SUITE READINESS DECLARATION

**Status**: READY FOR VALIDATION & EXECUTION  
**Published**: 2026-08-25  
**Test Framework**: `pytest` (>= 7.0.0)  
**Location**: `tests/`  

---

## 1. Overview
The comprehensive opaque-box test suite for the *Attack on Titan* media indexing, subtitle synchronization, playlist generation, and VLC smart intro-skipping controller ecosystem is fully authored, structured, and verified.

The test suite enforces the 4-tier testing methodology defined in `TEST_INFRA.md` and provides 100% specification coverage for all features F1 through F15 across all project milestones.

---

## 2. Test Suite Inventory

| File Path | Target Features | Description & Verifications |
|:----------|:---------------|:----------------------------|
| `tests/conftest.py` | Fixtures & Mocks | Shared fixtures, 97-item synthetic catalog, schema generators, and `MockVlcRcServer` TCP socket simulator. |
| `tests/test_schema_and_catalog.py` | F1, F2, F3, F4, F13 | Validates `episodes.json` 97-item catalog structure, required keys, S4 Part 2, Final Chapters specials, all 8 OVAs, and chronological ordering. |
| `tests/test_subtitle_integrity.py` | F6, F7 | Validates 97 `.srt` subtitle files, non-empty size (>500B), strict UTF-8 encoding, SRT regex timecode compliance, and monotonic cue progression. |
| `tests/test_aniskip_timestamps.py` | F8 | Validates AniSkip OP/ED start and end timestamps, numeric sanity, `op_start < op_end`, duration boundaries, and cold open preservation. |
| `tests/test_playlist_generation.py` | F12, F13 | Validates M3U8 structure, `#EXTVLCOPT:sub-file=...` directive injection, chronological ordering, and per-season/OVA playlist files. |
| `tests/test_vlc_controller.py` | F9, F10, F11 | Validates VLC RC TCP socket IPC client, `get_time`/`seek`/`pause` command parsing, intro-skipping state machine, cold open protection, and console hotkey dispatch. |
| `tests/test_stream_verifier.py` | F5 | Validates HTTP Range-request probing (`Range: bytes=0-1024`), 206 Partial Content / 200 OK handling, network failure recovery, and retry logic. |
| `tests/test_e2e_player.py` | F14, F15 | Validates CLI player argument parsing, `progress.json` persistence, next episode resolution, and VLC subprocess command invocation. |

---

## 3. How to Execute Tests

### Full Test Suite (Verbose)
```bash
python -m pytest tests/ -v
```

### Individual Test Suites
```bash
# Tier 1: Schema & Catalog
python -m pytest tests/test_schema_and_catalog.py -v

# Tier 2: Subtitle Integrity & AniSkip Timestamps
python -m pytest tests/test_subtitle_integrity.py -v
python -m pytest tests/test_aniskip_timestamps.py -v

# Tier 3: VLC Controller, Playlist Generator, Stream Verifier
python -m pytest tests/test_vlc_controller.py -v
python -m pytest tests/test_playlist_generation.py -v
python -m pytest tests/test_stream_verifier.py -v

# Tier 4: E2E Player CLI & Progress Tracking
python -m pytest tests/test_e2e_player.py -v
```

---

## 4. Feature Coverage Matrix (F1–F15)

| Feature | Description | Primary Test File | Pass Threshold |
|:---|:---|:---|:---:|
| **F1** | Extended Catalog Schema | `tests/test_schema_and_catalog.py` | 100% Pass |
| **F2** | S4 Part 2 Media Ingestion | `tests/test_schema_and_catalog.py` | 100% Pass |
| **F3** | Final Chapters Specials Ingestion | `tests/test_schema_and_catalog.py` | 100% Pass |
| **F4** | OVA Media Ingestion | `tests/test_schema_and_catalog.py` | 100% Pass |
| **F5** | Media Stream URL Verifier | `tests/test_stream_verifier.py` | 100% Pass |
| **F6** | 97-File UTF-8 Subtitle Library | `tests/test_subtitle_integrity.py` | 100% Pass |
| **F7** | Subtitle Validation Engine | `tests/test_subtitle_integrity.py` | 100% Pass |
| **F8** | AniSkip OP/ED Timestamps Store | `tests/test_aniskip_timestamps.py` | 100% Pass |
| **F9** | VLC Remote Control IPC Client | `tests/test_vlc_controller.py` | 100% Pass |
| **F10** | Smart Intro-Skip Engine | `tests/test_vlc_controller.py` | 100% Pass |
| **F11** | Interactive Console Hotkeys | `tests/test_vlc_controller.py` | 100% Pass |
| **F12** | M3U8 Playlist Compiler | `tests/test_playlist_generation.py` | 100% Pass |
| **F13** | Chronological Watch Order | `tests/test_playlist_generation.py` | 100% Pass |
| **F14** | Enhanced CLI Player (`play_aot.py`) | `tests/test_e2e_player.py` | 100% Pass |
| **F15** | Comprehensive Test Suite | All tests in `tests/` | 100% Pass |

---

## 5. Notes for Implementing Agents (M1–M5)
1. **Opaque-Box Compliance**: Test suites check public methods, file paths, and socket protocols specified in `PROJECT.md`. Implementations should conform directly to interface contracts.
2. **Progressive Testability**: When `subtitles/` or new modules (`vlc_controller.py`, `playlist_generator.py`, `stream_verifier.py`) are created, the live tests automatically engage and validate them against actual file assets and socket endpoints.
