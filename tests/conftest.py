"""
Pytest configuration and shared fixtures for Attack on Titan test suite.
"""

import json
import os
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

import pytest

# Ensure repository root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def episodes_json_path(project_root: Path) -> Path:
    """Return path to episodes.json."""
    return project_root / "episodes.json"


@pytest.fixture
def subtitles_dir_path(project_root: Path) -> Path:
    """Return path to subtitles directory."""
    return project_root / "subtitles"


@pytest.fixture
def playlists_dir_path(project_root: Path) -> Path:
    """Return path to playlists directory."""
    return project_root / "playlists"


@pytest.fixture
def sample_valid_episode() -> Dict[str, Any]:
    """Return a single schema-compliant TV episode dict."""
    return {
        "id": "S01E01",
        "type": "tv",
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


@pytest.fixture
def sample_valid_movie_special() -> Dict[str, Any]:
    """Return a schema-compliant movie special episode dict."""
    return {
        "id": "S04E29_Special_1",
        "type": "movie",
        "season_num": 4,
        "season_title": "The Final Chapters",
        "ep_num": 29,
        "absolute_num": 88,
        "chronological_order": 96,
        "title": "The Final Chapters: Special 1",
        "filename": "Attack_on_Titan_The_Final_Chapters_Special_1_1080p.mp4",
        "archive_path": "the-final-chapters_DUB-1080p/Special_1_1080p.mp4",
        "size_mb": 1420.0,
        "duration_seconds": 3660.0,
        "stream_url": "https://archive.org/download/aot-final-chapters-dub/Special_1_1080p.mp4",
        "subtitle_path": "subtitles/Final Chapters/S04E29_Special_1.en.srt",
        "timestamps": {
            "op_start": 0.0,
            "op_end": 0.0,
            "ed_start": 3520.0,
            "ed_end": 3640.0
        },
        "mal_id": 51535,
        "mal_ep_num": 1,
        "quality": "1080p Blu-ray DUB"
    }


@pytest.fixture
def sample_valid_ova() -> Dict[str, Any]:
    """Return a schema-compliant OVA episode dict."""
    return {
        "id": "OVA01",
        "type": "ova",
        "season_num": 0,
        "season_title": "OVAs",
        "ep_num": 1,
        "absolute_num": 1,
        "chronological_order": 1,
        "title": "Ilse's Notebook: Memoirs of a Scout Regiment Member",
        "filename": "Attack_on_Titan_OVA_01_Ilses_Notebook_1080p.mp4",
        "archive_path": "aot-ovas-1080p-dub/OVA_01_Ilses_Notebook.mp4",
        "size_mb": 512.4,
        "duration_seconds": 1500.0,
        "stream_url": "https://archive.org/download/aot-ovas-1080p-dub/OVA_01_Ilses_Notebook.mp4",
        "subtitle_path": "subtitles/OVAs/OVA01.en.srt",
        "timestamps": {
            "op_start": 95.0,
            "op_end": 185.0,
            "ed_start": 1390.0,
            "ed_end": 1480.0
        },
        "mal_id": 18397,
        "mal_ep_num": 1,
        "quality": "1080p Blu-ray DUB"
    }


@pytest.fixture
def sample_synthetic_97_catalog() -> List[Dict[str, Any]]:
    """Generate a synthetic 97-item catalog adhering strictly to F1-F4, F8, F13 contracts."""
    catalog = []
    
    # 1. Seasons 1-4 Part 1: 75 episodes (IDs S01E01-S01E25, S02E01-S02E12, S03E01-S03E22, S04E01-S04E16)
    tv_seasons = [
        (1, "Season 1", 25),
        (2, "Season 2", 12),
        (3, "Season 3", 22),
        (4, "Final Season Part 1", 16)
    ]
    abs_counter = 1
    chron_counter = 1
    
    # 8 OVAs (chronological order interleaved)
    ova_titles = [
        "Ilse's Notebook: Memoirs of a Scout Regiment Member",
        "The Sudden Visitor: The Torturous Curse of Youth",
        "Distress",
        "No Regrets: Part 1",
        "No Regrets: Part 2",
        "Lost Girls: Wall Sina, Goodbye - Part 1",
        "Lost Girls: Wall Sina, Goodbye - Part 2",
        "Lost Girls: Lost in the Cruel World"
    ]
    
    for s_num, s_title, count in tv_seasons:
        for ep in range(1, count + 1):
            ep_id = f"S{s_num:02d}E{ep:02d}"
            catalog.append({
                "id": ep_id,
                "type": "tv",
                "season_num": s_num,
                "season_title": s_title,
                "ep_num": ep,
                "absolute_num": abs_counter,
                "chronological_order": chron_counter,
                "title": f"Episode {ep_id}",
                "filename": f"Attack_on_Titan_{ep_id}_1080p.mp4",
                "archive_path": f"{s_title.lower().replace(' ', '-')}/{ep_id}.mp4",
                "size_mb": 400.0,
                "duration_seconds": 1440.0,
                "stream_url": f"https://archive.org/download/shingeki-no-kyojin_aot/{ep_id}.mp4",
                "subtitle_path": f"subtitles/{s_title}/{ep_id}.en.srt",
                "timestamps": {
                    "op_start": 90.0,
                    "op_end": 180.0,
                    "ed_start": 1320.0,
                    "ed_end": 1410.0
                },
                "mal_id": 16498,
                "mal_ep_num": ep,
                "quality": "1080p Blu-ray DUB"
            })
            abs_counter += 1
            chron_counter += 1

    # Final Season Part 2: 12 episodes (S04E17 - S04E28 / #76-87)
    for ep in range(17, 29):
        ep_id = f"S04E{ep:02d}"
        catalog.append({
            "id": ep_id,
            "type": "tv",
            "season_num": 4,
            "season_title": "Final Season Part 2",
            "ep_num": ep,
            "absolute_num": abs_counter,
            "chronological_order": chron_counter,
            "title": f"Episode {ep_id}",
            "filename": f"Attack_on_Titan_{ep_id}_1080p.mp4",
            "archive_path": f"final-season-part-2/{ep_id}.mp4",
            "size_mb": 450.0,
            "duration_seconds": 1440.0,
            "stream_url": f"https://archive.org/download/aot-final-season-part-2-dub/{ep_id}.mp4",
            "subtitle_path": f"subtitles/Final Season Part 2/{ep_id}.en.srt",
            "timestamps": {
                "op_start": 95.0,
                "op_end": 185.0,
                "ed_start": 1330.0,
                "ed_end": 1420.0
            },
            "mal_id": 48583,
            "mal_ep_num": ep - 16,
            "quality": "1080p Blu-ray DUB"
        })
        abs_counter += 1
        chron_counter += 1

    # The Final Chapters: 2 Movie Specials
    specials = [
        ("S04E29_Special_1", 29, "The Final Chapters: Special 1", 3660.0),
        ("S04E30_Special_2", 30, "The Final Chapters: Special 2", 5100.0),
    ]
    for ep_id, ep_num, title, duration in specials:
        catalog.append({
            "id": ep_id,
            "type": "movie",
            "season_num": 4,
            "season_title": "The Final Chapters",
            "ep_num": ep_num,
            "absolute_num": abs_counter,
            "chronological_order": chron_counter,
            "title": title,
            "filename": f"Attack_on_Titan_{ep_id}_1080p.mp4",
            "archive_path": f"the-final-chapters/{ep_id}.mp4",
            "size_mb": 1400.0,
            "duration_seconds": duration,
            "stream_url": f"https://archive.org/download/aot-final-chapters/{ep_id}.mp4",
            "subtitle_path": f"subtitles/Final Chapters/{ep_id}.en.srt",
            "timestamps": {
                "op_start": 0.0,
                "op_end": 0.0,
                "ed_start": duration - 120.0,
                "ed_end": duration - 10.0
            },
            "mal_id": 51535,
            "mal_ep_num": ep_num - 28,
            "quality": "1080p Blu-ray DUB"
        })
        abs_counter += 1
        chron_counter += 1

    # 8 OVAs
    for idx, ova_title in enumerate(ova_titles, start=1):
        ova_id = f"OVA{idx:02d}"
        catalog.append({
            "id": ova_id,
            "type": "ova",
            "season_num": 0,
            "season_title": "OVAs",
            "ep_num": idx,
            "absolute_num": idx,
            "chronological_order": chron_counter,
            "title": ova_title,
            "filename": f"Attack_on_Titan_{ova_id}_1080p.mp4",
            "archive_path": f"ovas/{ova_id}.mp4",
            "size_mb": 420.0,
            "duration_seconds": 1500.0,
            "stream_url": f"https://archive.org/download/aot-ovas-dub/{ova_id}.mp4",
            "subtitle_path": f"subtitles/OVAs/{ova_id}.en.srt",
            "timestamps": {
                "op_start": 80.0,
                "op_end": 170.0,
                "ed_start": 1380.0,
                "ed_end": 1470.0
            },
            "mal_id": 18397,
            "mal_ep_num": idx,
            "quality": "1080p Blu-ray DUB"
        })
        chron_counter += 1

    return catalog


@pytest.fixture
def sample_valid_srt_string() -> str:
    """Return a standard multi-cue valid SRT string."""
    return """1
00:01:05,200 --> 00:01:08,450
That day, the human race remembered...

2
00:01:09,100 --> 00:01:13,800
the terror of being ruled by them...

3
00:01:14,200 --> 00:01:18,500
and the humiliation of being kept in a cage.
"""


class MockVlcRcServer:
    """Simulated VLC RC TCP socket server for deterministic testing of vlc_controller."""

    def __init__(self, host: str = "127.0.0.1", port: int = 0):
        self.host = host
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, port))
        self.port = self.server_sock.getsockname()[1]
        self.server_sock.listen(1)
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.client_sock: Optional[socket.socket] = None
        self.received_commands: List[str] = []
        self.current_time = 0.0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        # Small sleep to ensure listen loop started
        time.sleep(0.05)

    def _run(self):
        self.server_sock.settimeout(2.0)
        try:
            self.client_sock, _ = self.server_sock.accept()
            self.client_sock.settimeout(2.0)
            self.client_sock.sendall(b"> \r\n")
            buffer = ""
            while self.running:
                try:
                    data = self.client_sock.recv(1024)
                    if not data:
                        break
                    buffer += data.decode("utf-8", errors="ignore")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if line:
                            self.received_commands.append(line)
                            response = self._handle_command(line)
                            if response:
                                self.client_sock.sendall(response.encode("utf-8"))
                except socket.timeout:
                    continue
                except Exception:
                    break
        except Exception:
            pass

    def _handle_command(self, cmd: str) -> str:
        parts = cmd.split()
        if not parts:
            return "> \r\n"
        action = parts[0].lower()
        if action == "get_time":
            return f"{int(self.current_time)}\r\n> "
        elif action == "seek":
            if len(parts) > 1:
                try:
                    self.current_time = float(parts[1])
                except ValueError:
                    pass
            return "> \r\n"
        elif action == "pause":
            return "> \r\n"
        elif action in ("quit", "shutdown", "stop"):
            self.running = False
            return "> \r\n"
        elif action == "status":
            return "status: playing\r\n> "
        return "> \r\n"

    def stop(self):
        self.running = False
        if self.client_sock:
            try:
                self.client_sock.close()
            except Exception:
                pass
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)


@pytest.fixture
def mock_vlc_server():
    """Fixture providing a managed MockVlcRcServer instance."""
    server = MockVlcRcServer()
    server.start()
    yield server
    server.stop()
