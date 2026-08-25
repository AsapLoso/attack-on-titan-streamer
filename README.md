# ⚔️ Attack on Titan - VLC 4.0 Stream Hub & Subtitle Suite

A lightweight, native desktop streaming hub and episode indexer for **Attack on Titan (Shingeki no Kyojin)** in **1080p English Dub**. Streams directly from open archives in **VLC Media Player** with automatic English Closed Captions (CC) and smart intro-skipping support.

---

## 🌟 Features

* **Complete 97-Item Franchise Coverage**:
  * **Season 1** (25 Episodes)
  * **Season 2** (12 Episodes)
  * **Season 3** (22 Episodes, Parts 1 & 2)
  * **The Final Season Part 1** (16 Episodes)
  * **The Final Season Part 2** (12 Episodes)
  * **The Final Chapters** (2 Uncut Movie-Length Specials: Special 1 & Special 2)
  * **All 8 Official OVAs** (*No Regrets Parts 1 & 2*, *Lost Girls Parts 1–3*, *Ilse's Notebook*, *The Sudden Visitor*, *Distress*)
* **Native Desktop GUI**: Sleek dark-themed Tkinter interface (`app_gui.py`) with season tabs, search filtering, and 1-click playback.
* **Automatic English CC Subtitles**: Pre-indexed and synchronized local `.srt` subtitle library for every episode.
* **AniSkip Integration**: Accurate Opening (OP) and Ending (ED) timestamps for intro skipping.
* **VLC Integration**: Designed for VLC 4.0 / 3.0+ with automatic `--sub-file` loading and `.m3u8` playlist exports.
* **Progress Tracking**: Automatically remembers your last watched episode (`progress.json`).

---

## 🚀 Quick Start (Windows)

### Prerequisites
* [Python 3.8+](https://www.python.org/downloads/)
* [VLC Media Player](https://www.videolan.org/vlc/)

### 1. Launch Desktop GUI (Recommended)
Double-click **`Attack_on_Titan.bat`** or run:
```powershell
pythonw app_gui.py
```

### 2. CLI Streamer
```powershell
# Interactive Menu
python play_aot.py

# Play specific episode (e.g. Season 4 Episode 17)
python play_aot.py -p S04E17

# Play Movie Special
python play_aot.py -p S04E29

# Auto-skip intro
python play_aot.py -p S01E05 --skip-intro

# Resume next episode
python play_aot.py --resume
```

### 3. VLC Playlists
Open any `.m3u8` playlist in the `playlists/` folder directly in VLC:
* `Attack_on_Titan_Full_Series.m3u8` (All 97 items)
* `Attack_on_Titan_Season_1.m3u8`
* `Attack_on_Titan_Season_2.m3u8`
* `Attack_on_Titan_Season_3.m3u8`
* `Attack_on_Titan_Final_Season.m3u8`
* `Attack_on_Titan_OVAs.m3u8`

---

## 📁 Repository Structure

```text
├── app_gui.py               # Native Tkinter desktop streaming app
├── play_aot.py              # CLI player & playlist generator
├── Attack_on_Titan.bat      # Windowless quick launcher
├── episodes.json            # 97-item master metadata & stream index
├── playlists/               # M3U8 streaming playlists for VLC
├── subtitles/               # Offline English CC subtitle library (.srt)
└── tests/                   # Automated E2E test suite
```

---

## 📜 Disclaimer
This project is an open-source educational indexer and player wrapper. Media streams and metadata are indexed from public archives on the Internet Archive. Attack on Titan is the intellectual property of Hajime Isayama, Kodansha, Wit Studio, and MAPPA.
