# ⚔️ Attack on Titan - Stream Hub & Subtitle Suite

A lightweight, native desktop & mobile streaming hub and episode indexer for **Attack on Titan (Shingeki no Kyojin)** in **1080p English Dub**. Streams directly from open archives in **MPV, VLC, or Web Browser** with automatic English Closed Captions (CC) and smart AniSkip intro-skipping support.

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
* **📱 Mobile Web App (GitHub Pages)**: Live, zero-backend mobile streaming hub at [https://asaploso.github.io/attack-on-titan-streamer/](https://asaploso.github.io/attack-on-titan-streamer/).
* **🖥️ Native Desktop GUI**: Sleek dark-themed Tkinter interface (`app_gui.py`) with season tabs, search filtering, and 1-click playback.
* **⏩ Smart Intro-Skipping**: Built-in AniSkip on-screen Skip Opening (`[Tab]` / `S`) button and auto-skip.
* **💬 Automatic English CC Subtitles**: Pre-indexed and synchronized local & cloud `.srt` subtitle library for every episode.
* **🍿 Always-On Binge Mode**: Automatically queues and auto-plays subsequent episodes continuously.

---

## 🚀 Quick Start

### 1. Mobile & Web Browser
Open the live web app on any device:
👉 **[https://asaploso.github.io/attack-on-titan-streamer/](https://asaploso.github.io/attack-on-titan-streamer/)**

### 2. Windows Desktop GUI
Double-click **`Attack on Titan.lnk`** on your Desktop or run:
```powershell
pythonw app_gui.py
```

### 3. CLI Streamer
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

---

## 📁 Repository Structure

```text
├── index.html               # Mobile-first web app (GitHub Pages)
├── app_gui.py               # Native Tkinter desktop streaming app
├── play_aot.py              # CLI player & playlist generator
├── Attack_on_Titan.bat      # Windowless quick launcher
├── episodes.json            # 97-item master metadata & stream index
├── playlists/               # M3U8 streaming playlists for MPV & VLC
├── subtitles/               # Offline English CC subtitle library (.srt)
└── tests/                   # Automated E2E test suite
```

---

## 📜 Disclaimer
This project is an open-source educational indexer and player wrapper. Media streams and metadata are indexed from public archives on the Internet Archive. Attack on Titan is the intellectual property of Hajime Isayama, Kodansha, Wit Studio, and MAPPA.
