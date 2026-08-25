# Project: Attack on Titan Media Indexer, Subtitle Sync, and VLC Smart Intro-Skip Controller

## Architecture
The system is an automated, high-fidelity media indexer, scraper, subtitle synchronization engine, and real-time VLC playback controller for the complete *Attack on Titan* franchise (97 media items total: Seasons 1–4 Part 1 [75 eps], Final Season Part 2 [12 eps], The Final Chapters Movie Specials [2 specials], and all 8 Official OVAs).

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           play_aot.py (CLI & UI)                          │
│   - Interactive terminal menu (Seasons 1-4, Final Chapters, OVAs, Binge) │
│   - Episode / Season / OVA / Special argument parser & resume tracker     │
└─────────────────────┬───────────────────────────────┬─────────────────────┘
                      │                               │
                      ▼                               ▼
      ┌──────────────────────────────┐ ┌───────────────────────────────────┐
      │     episodes.json (97 eps)   │ │       vlc_controller.py           │
      │ - Metadata & stream URLs     │ │ - TCP Socket IPC to VLC RC        │
      │ - Subtitle file bindings     │ │ - 250ms polling loop (get_time)   │
      │ - AniSkip OP/ED timestamps   │ │ - Intro-skip (op_start -> op_end) │
      │ - Chronological order index  │ │ - Console hotkeys (msvcrt)        │
      └──────────────┬───────────────┘ └─────────────────┬─────────────────┘
                     │                                   │
                     ├───────────────────┐               │
                     ▼                   ▼               ▼
      ┌────────────────────────┐ ┌──────────────┐ ┌────────────────────────┐
      │  playlist_generator.py │ │ subtitles/   │ │      VLC Player        │
      │ - #EXTVLCOPT:sub-file  │ │ (97 UTF-8    │ │ - Direct HTTPS stream  │
      │ - Chronological M3U8   │ │  .srt files) │ │ - Auto-attached subs   │
      │ - Season & OVA M3U8s   │ └──────────────┘ │ - Seamless intro skip  │
      └────────────────────────┘                  └────────────────────────┘
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | Extended Catalog Schema | Complete 97-item JSON catalog with metadata, types, stream URLs, subtitle paths, timestamps | M1 | Survey |
| F2 | S4 Part 2 Media Ingestion | Direct verified 1080p English Dub streaming URLs for S04E17–S04E28 | M1 | R1 |
| F3 | Final Chapters Specials Ingestion | Direct verified 1080p English Dub uncut movie specials (Special 1 & 2) | M1 | R1 |
| F4 | OVA Media Ingestion | Direct verified streaming URLs for all 8 Official OVAs | M1 | R1 |
| F5 | Media Stream URL Verifier | HTTP Range-request validation utility (`Range: bytes=0-1024`, status 200/206) | M1 | R1, Survey |
| F6 | 97-File UTF-8 Subtitle Library | Complete English Closed Captions (.srt) matching English dub audio for all 97 items | M2 | R2 |
| F7 | Subtitle Validation Engine | 5-level integrity validator (size, UTF-8, regex syntax, monotonic timestamps, non-empty dialogue) | M2 | R2, Survey |
| F8 | AniSkip OP/ED Timestamps Store | Pre-indexed and runtime-queryable OP/ED start and end timestamps for all 97 items | M3 | R3 |
| F9 | VLC Remote Control IPC Client | TCP socket connector to VLC `--extraintf rc --rc-host 127.0.0.1:<port>` | M3 | R3 |
| F10 | Smart Intro-Skip Engine | Non-blocking monitor that preserves cold opens/prologues and seeks past OP song at `op_start` | M3 | R3 |
| F11 | Interactive Console Hotkeys | Non-blocking hotkey listener (`msvcrt` on Windows) for Skip, Toggle Auto-Skip, Pause, Next, Quit | M3 | R3 |
| F12 | M3U8 Playlist Compiler | Generates M3U8 playlists with `#EXTVLCOPT:sub-file=...` for all seasons, specials, OVAs, and chronological | M4 | R4 |
| F13 | Complete Chronological Watch Order | Canon chronological sequence embedding OVAs and specials at their exact timeline positions | M4 | R4 |
| F14 | Enhanced CLI Player (`play_aot.py`) | Interactive menu, `--sub-file` VLC argument injection, `--ova`, `--special`, `--chronological`, `--no-skip` | M4 | R4 |
| F15 | Comprehensive Test Suite | Pytest test suite covering schema, streams, subtitles, playlists, VLC controller, and AniSkip (Tiers 1-5) | E2E / M5 | Criteria |

## Code Layout
```
AOT/
├── episodes.json              # Primary unified database (97 items)
├── indexed_episodes.json      # Synchronized backward-compatible export
├── progress.json              # User playback tracking & resume state
├── play.bat                   # Windows batch CLI wrapper
├── play_aot.py                # Main CLI controller and interactive UI
├── vlc_controller.py          # Real-time VLC RC TCP IPC, intro-skipping, and hotkeys
├── subtitle_manager.py        # Subtitle validator, format converter, and path resolver
├── playlist_generator.py      # M3U8 playlist compiler with EXTVLCOPT subtitle directives
├── stream_verifier.py         # HTTP Range-request media URL health probe
├── subtitles/                 # Complete UTF-8 English Closed Captions library (97 files)
│   ├── Season 1/              # S01E01.en.srt ... S01E25.en.srt
│   ├── Season 2/              # S02E01.en.srt ... S02E12.en.srt
│   ├── Season 3 Part 1/       # S03E01.en.srt ... S03E12.en.srt
│   ├── Season 3 Part 2/       # S03E13.en.srt ... S03E22.en.srt
│   ├── Final Season Part 1/   # S04E01.en.srt ... S04E16.en.srt
│   ├── Final Season Part 2/   # S04E17.en.srt ... S04E28.en.srt
│   ├── Final Chapters/        # S04E29_Special_1.en.srt, S04E30_Special_2.en.srt
│   └── OVAs/                  # OVA01.en.srt ... OVA08.en.srt
├── playlists/                 # Enhanced M3U8 playlists with #EXTVLCOPT
│   ├── Attack_on_Titan_Chronological_Complete.m3u8
│   ├── Attack_on_Titan_Full_Series_Release_Order.m3u8
│   ├── Attack_on_Titan_Season_1.m3u8
│   ├── Attack_on_Titan_Season_2.m3u8
│   ├── Attack_on_Titan_Season_3.m3u8
│   ├── Attack_on_Titan_Final_Season_Part_1.m3u8
│   ├── Attack_on_Titan_Final_Season_Part_2.m3u8
│   ├── Attack_on_Titan_The_Final_Chapters.m3u8
│   └── Attack_on_Titan_OVAs.m3u8
├── scripts/                   # Verification and maintenance utilities
│   ├── verify_subtitles.py
│   └── verify_streams.py
└── tests/                     # Opaque-box and unit pytest suite
    ├── __init__.py
    ├── test_schema_and_catalog.py
    ├── test_subtitle_integrity.py
    ├── test_aniskip_timestamps.py
    ├── test_vlc_controller.py
    ├── test_playlist_generation.py
    └── test_e2e_player.py
```

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Media Discovery & Catalog Expansion | Ingest S4P2, Final Chapters 1 & 2, all 8 OVAs into `episodes.json` (97 items) and build `stream_verifier.py` | none | PLANNED |
| M2 | Subtitle Library & Validator | Create 97 clean UTF-8 `.srt` files matching English dub in `subtitles/` and `subtitle_manager.py` | M1 | PLANNED |
| M3 | AniSkip Database & VLC Smart Intro-Skip Controller | Populate timestamps for all 97 items, build `vlc_controller.py` with RC socket IPC, auto-skip, and hotkeys | M1 | PLANNED |
| M4 | Player CLI & Playlist Integration | Build `playlist_generator.py` with `#EXTVLCOPT:sub-file=...`, update `play_aot.py` with `--sub-file`, new menus, and full CLI flags | M1, M2, M3 | PLANNED |
| M5 | Final Milestone: Full E2E & Adversarial Verification | Pass 100% E2E test suite (Tiers 1-4) and execute Tier 5 adversarial hardening | M1, M2, M3, M4, TEST_READY | PLANNED |

## Interface Contracts

### 1. `episodes.json` Item Schema Contract
```json
{
  "id": "S01E01",
  "type": "tv" | "movie" | "ova",
  "season_num": 1,
  "season_title": "Season 1",
  "ep_num": 1,
  "absolute_num": 1,
  "chronological_order": 4,
  "title": "To You, in 2000 Years: The Fall of Shiganshina, Part 1",
  "filename": "Attack_on_Titan-E1-1080p.mp4",
  "archive_path": "season-1_DUB-1080p/Attack_on_Titan-E1-1080p.mp4",
  "size_mb": 431.6,
  "duration_seconds": 1440.0,
  "stream_url": "https://archive.org/download/shingeki-no-kyojin_aot/season-1_DUB-1080p/Attack_on_Titan-E1-1080p.mp4",
  "subtitle_path": "subtitles/Season 1/S01E01.en.srt",
  "timestamps": {
    "op_start": 128.4,
    "op_end": 218.4,
    "ed_start": 1342.8,
    "ed_end": 1430.6
  },
  "mal_id": 16498,
  "mal_ep_num": 1,
  "quality": "1080p Blu-ray DUB"
}
```

### 2. `vlc_controller.py` Module Contract
- Class `VlcRcController`:
  - `__init__(self, vlc_path: str, port: int = 4212, poll_interval: float = 0.25, auto_skip: bool = True)`
  - `play_episode(self, episode_dict: dict, no_skip: bool = False) -> subprocess.Popen`
  - `start_monitoring(self, op_start: float, op_end: float, ed_start: float = None) -> None`
  - `send_command(self, cmd: str) -> str`
  - `stop(self) -> None`

### 3. `subtitle_manager.py` Module Contract
- Function `verify_subtitles_directory(subtitles_dir: Path) -> Tuple[bool, List[str]]`
- Function `get_subtitle_path_for_episode(episode_id: str) -> Optional[Path]`
- Function `convert_vtt_to_srt(vtt_content: str) -> str`

### 4. `playlist_generator.py` Module Contract
- Function `generate_all_playlists(episodes: List[dict], output_dir: Path) -> List[Path]`
- Function `format_m3u8_entry(ep: dict, base_dir: Path) -> str` (includes `#EXTVLCOPT:sub-file=...`)
