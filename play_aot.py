#!/usr/bin/env python3
"""
Attack on Titan (AOT) - Archive.org VLC 4.0 Streaming Wrapper
Author: Antigravity
Streams 1080p DUB episodes, Specials, and OVAs with automatic English CC subtitles and AniSkip support.
"""

import sys
import os
import json
import subprocess
import shutil
import urllib.parse
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EPISODES_FILE = BASE_DIR / "episodes.json"
PROGRESS_FILE = BASE_DIR / "progress.json"
PLAYLISTS_DIR = BASE_DIR / "playlists"
SUBTITLES_DIR = BASE_DIR / "subtitles"

VLC_POSSIBLE_PATHS = [
    r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
    os.environ.get("VLC_PATH", ""),
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\VLC\vlc.exe"),
]

def find_vlc():
    """Locate VLC executable on system (prioritizing installed VLC 4.0)."""
    for path in VLC_POSSIBLE_PATHS:
        if path and os.path.exists(path):
            return path
    vlc_in_path = shutil.which("vlc")
    if vlc_in_path:
        return vlc_in_path
    return None

def load_episodes():
    """Load episodes list from episodes.json."""
    if not EPISODES_FILE.exists():
        print(f"[!] Error: {EPISODES_FILE} not found.")
        sys.exit(1)
    with open(EPISODES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_progress():
    """Load playback progress."""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_played_id": None, "history": []}

def save_progress(episode):
    """Save the currently played episode to progress history."""
    data = load_progress()
    data["last_played_id"] = episode["id"]
    if episode["id"] not in data.get("history", []):
        data.setdefault("history", []).append(episode["id"])
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_playlists(episodes):
    """Generate M3U8 playlists for full series, seasons, and OVAs."""
    PLAYLISTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Full series playlist (Release Order)
    full_playlist_path = PLAYLISTS_DIR / "Attack_on_Titan_Full_Series.m3u8"
    with open(full_playlist_path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("#PLAYLIST:Attack on Titan (Complete Series 1080p Dub)\n\n")
        for ep in episodes:
            title = f"Attack on Titan - {ep['id']}: {ep.get('title', ep['filename'])}"
            f.write(f"#EXTINF:-1,{title}\n")
            sub_path = BASE_DIR / ep.get("subtitle_path", "")
            if sub_path.exists():
                f.write(f"#EXTVLCOPT:sub-file={sub_path.resolve().as_posix()}\n")
            f.write(f"{ep['stream_url']}\n\n")

    # 2. Per-season & OVA playlists
    categories = {
        "Season 1": [e for e in episodes if e.get("season_num") == 1],
        "Season 2": [e for e in episodes if e.get("season_num") == 2],
        "Season 3": [e for e in episodes if e.get("season_num") == 3],
        "Final Season": [e for e in episodes if e.get("season_num") == 4],
        "OVAs": [e for e in episodes if e.get("type") == "ova" or e.get("season_num") == 0]
    }
    
    category_files = {}
    for cat_name, cat_eps in categories.items():
        if not cat_eps:
            continue
        fname = f"Attack_on_Titan_{cat_name.replace(' ', '_')}.m3u8"
        pl_path = PLAYLISTS_DIR / fname
        with open(pl_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write(f"#PLAYLIST:Attack on Titan - {cat_name}\n\n")
            for ep in cat_eps:
                title = f"Attack on Titan - {ep['id']}: {ep.get('title', ep['filename'])}"
                f.write(f"#EXTINF:-1,{title}\n")
                sub_path = BASE_DIR / ep.get("subtitle_path", "")
                if sub_path.exists():
                    f.write(f"#EXTVLCOPT:sub-file={sub_path.resolve().as_posix()}\n")
                f.write(f"{ep['stream_url']}\n\n")
        category_files[cat_name] = pl_path

    return full_playlist_path, category_files

def stream_episode(episode, vlc_path, wait_finish=True, skip_intro=False):
    """Launch VLC 4.0 to stream the episode with automatic subtitles."""
    title = f"Attack on Titan - {episode['id']}: {episode.get('title', episode['filename'])}"
    sub_path = BASE_DIR / episode.get("subtitle_path", "")
    has_sub = sub_path.exists()
    
    print(f"\n========================================================")
    print(f"▶ Now Streaming: {title}")
    if has_sub:
        print(f"💬 English Subtitles: {sub_path.name}")
    ts = episode.get("timestamps", {})
    if ts and ts.get("op_start"):
        print(f"⏩ Intro Theme: {ts['op_start']}s -> {ts['op_end']}s")
    print(f"🔗 Stream URL: {episode['stream_url']}")
    print(f"========================================================\n")
    
    save_progress(episode)
    
    cmd = [
        vlc_path,
        episode["stream_url"],
        f"--meta-title={title}",
    ]
    
    if has_sub:
        cmd.append(f"--sub-file={str(sub_path.resolve())}")
        
    if skip_intro and ts and ts.get("op_end"):
        # Auto start right after intro if skip_intro requested
        cmd.append(f"--start-time={int(ts['op_end'])}")
        print(f"[⏩ Auto-Skip] Starting after intro at second {int(ts['op_end'])}...")
        
    if wait_finish:
        cmd.append("--play-and-exit")
        proc = subprocess.run(cmd)
        return proc.returncode == 0
    else:
        subprocess.Popen(cmd)
        return True

def play_playlist(playlist_path, vlc_path):
    """Launch VLC with an M3U8 playlist."""
    print(f"\n▶ Opening playlist in VLC: {playlist_path.name}")
    subprocess.Popen([vlc_path, str(playlist_path.resolve())])

def get_next_episode(episodes, current_id):
    """Get the next episode in order."""
    for idx, ep in enumerate(episodes):
        if ep["id"] == current_id:
            if idx + 1 < len(episodes):
                return episodes[idx + 1]
            return None
    return None

def start_binge_mode(episodes, start_ep, vlc_path, skip_intro=False):
    """Continuous playback mode: plays next episode automatically when VLC exits."""
    current = start_ep
    while current:
        print(f"\n[Binge Mode] Streaming episode {current['id']}...")
        success = stream_episode(current, vlc_path, wait_finish=True, skip_intro=skip_intro)
        
        next_ep = get_next_episode(episodes, current["id"])
        if not next_ep:
            print("\n🎉 Congratulations! You have reached the end of the series!")
            break
            
        print(f"\nFinished {current['id']}.")
        choice = input(f"Press Enter to play next ({next_ep['id']}), or 'q' to stop: ").strip().lower()
        if choice == 'q':
            break
        current = next_ep

def interactive_cli(episodes, vlc_path):
    """Interactive command-line UI."""
    generate_playlists(episodes)
    
    while True:
        progress = load_progress()
        last_id = progress.get("last_played_id")
        
        print("\n" + "=" * 55)
        print("    ⚔️  ATTACK ON TITAN - VLC 4.0 STREAMER  ⚔️")
        print("=" * 55)
        if last_id:
            print(f" [★] Last Watched: {last_id}")
        print(" 1. Resume / Play Next Unwatched Episode")
        print(" 2. Browse by Season & Episodes (Seasons 1–4, Specials, OVAs)")
        print(" 3. Binge Mode (Continuous Auto-Play)")
        print(" 4. Open Playlists in VLC (Full Series, Seasons, OVAs)")
        print(" 5. Regenerate M3U8 Playlists")
        print(" 6. Exit")
        print("=" * 55)
        
        choice = input("Select an option (1-6): ").strip()
        
        if choice == "1":
            if not last_id:
                ep = episodes[0]
            else:
                next_ep = get_next_episode(episodes, last_id)
                ep = next_ep if next_ep else episodes[0]
            stream_episode(ep, vlc_path, wait_finish=False)
            
        elif choice == "2":
            groups = [
                ("Season 1 (25 Episodes)", [e for e in episodes if e.get("season_num") == 1]),
                ("Season 2 (12 Episodes)", [e for e in episodes if e.get("season_num") == 2]),
                ("Season 3 (22 Episodes)", [e for e in episodes if e.get("season_num") == 3]),
                ("The Final Season (Part 1 & 2 + Specials - 30 Episodes)", [e for e in episodes if e.get("season_num") == 4]),
                ("Official OVAs (8 Episodes)", [e for e in episodes if e.get("type") == "ova" or e.get("season_num") == 0])
            ]
            print("\n--- Select Category ---")
            for idx, (label, _) in enumerate(groups, 1):
                print(f" {idx}. {label}")
            print(" 0. Back")
            g_choice = input(f"Choose (0-{len(groups)}): ").strip()
            if g_choice.isdigit() and 1 <= int(g_choice) <= len(groups):
                chosen_label, chosen_eps = groups[int(g_choice) - 1]
                print(f"\n--- {chosen_label} ---")
                for idx, ep in enumerate(chosen_eps, 1):
                    watched = "✓" if ep["id"] in progress.get("history", []) else " "
                    print(f" [{watched}] {idx:2d}. {ep['id']}: {ep.get('title', ep['filename'])}")
                print("  0. Back")
                ep_choice = input(f"Choose Episode (1-{len(chosen_eps)}): ").strip()
                if ep_choice.isdigit() and 1 <= int(ep_choice) <= len(chosen_eps):
                    target_ep = chosen_eps[int(ep_choice) - 1]
                    stream_episode(target_ep, vlc_path, wait_finish=False)
                    
        elif choice == "3":
            print("\nStart Binge Mode from:")
            print(" 1. Last Watched / Next Episode")
            print(" 2. Season 1 Episode 1")
            print(" 3. Choose Custom Episode ID (e.g. S04E17, OVA04)")
            b_choice = input("Select (1-3): ").strip()
            if b_choice == "1":
                start_ep = get_next_episode(episodes, last_id) if last_id else episodes[0]
                start_binge_mode(episodes, start_ep or episodes[0], vlc_path)
            elif b_choice == "2":
                start_binge_mode(episodes, episodes[0], vlc_path)
            elif b_choice == "3":
                ep_id = input("Enter Episode ID (e.g. S01E05, S04E17, OVA01): ").strip().upper()
                match = next((ep for ep in episodes if ep["id"] == ep_id), None)
                if match:
                    start_binge_mode(episodes, match, vlc_path)
                else:
                    print(f"[!] Episode '{ep_id}' not found.")
                    
        elif choice == "4":
            full_pl, cat_pls = generate_playlists(episodes)
            print("\n--- Playlists ---")
            print(" 1. Full Series (All 97 Episodes, Specials & OVAs)")
            pl_keys = list(cat_pls.keys())
            for idx, key in enumerate(pl_keys, 2):
                print(f" {idx}. {key} Playlist ({cat_pls[key].name})")
            print(" 0. Back")
            pl_choice = input(f"Select playlist (0-{len(pl_keys)+1}): ").strip()
            if pl_choice == "1":
                play_playlist(full_pl, vlc_path)
            elif pl_choice.isdigit() and 2 <= int(pl_choice) <= len(pl_keys) + 1:
                chosen_key = pl_keys[int(pl_choice) - 2]
                play_playlist(cat_pls[chosen_key], vlc_path)
                
        elif choice == "5":
            full_pl, cat_pls = generate_playlists(episodes)
            print(f"\n[✓] Generated all playlists in: {PLAYLISTS_DIR}")
            print(f" - {full_pl.name}")
            for p in cat_pls.values():
                print(f" - {p.name}")
                
        elif choice == "6":
            print("Goodbye! ⚔️")
            break

def main():
    parser = argparse.ArgumentParser(description="Attack on Titan Archive.org VLC 4.0 Streaming Wrapper")
    parser.add_argument("-p", "--play", help="Play specific episode ID (e.g. S01E01, S04E17, OVA04)")
    parser.add_argument("-s", "--season", type=int, help="Season number (1-4, 0 for OVAs)")
    parser.add_argument("-e", "--episode", type=int, help="Episode number")
    parser.add_argument("-r", "--resume", action="store_true", help="Resume playing next unwatched episode")
    parser.add_argument("-b", "--binge", action="store_true", help="Enable binge mode (auto-advance)")
    parser.add_argument("--skip-intro", action="store_true", help="Skip intro opening theme automatically")
    parser.add_argument("--playlist", help="Open playlist in VLC ('all', '1', '2', '3', '4', 'ova')")
    parser.add_argument("--export", action="store_true", help="Export M3U8 playlists")
    parser.add_argument("--list", action="store_true", help="List all 97 indexed episodes")
    
    args = parser.parse_args()
    episodes = load_episodes()
    vlc_path = find_vlc()
    
    if not vlc_path and not args.export and not args.list:
        print("[!] Error: VLC Media Player was not found.")
        sys.exit(1)

    if args.export:
        full_pl, cat_pls = generate_playlists(episodes)
        print(f"[✓] Successfully generated playlists in {PLAYLISTS_DIR}")
        return

    if args.list:
        for ep in episodes:
            sub = " [CC]" if (BASE_DIR / ep.get("subtitle_path", "")).exists() else ""
            print(f"{ep['id']}: {ep.get('title', ep['filename'])}{sub} -> {ep['stream_url']}")
        return

    if args.playlist:
        full_pl, cat_pls = generate_playlists(episodes)
        if args.playlist == "all":
            play_playlist(full_pl, vlc_path)
        elif args.playlist in ("1", "2", "3"):
            key = f"Season {args.playlist}"
            if key in cat_pls:
                play_playlist(cat_pls[key], vlc_path)
        elif args.playlist in ("4", "final"):
            if "Final Season" in cat_pls:
                play_playlist(cat_pls["Final Season"], vlc_path)
        elif args.playlist in ("0", "ova", "ovas"):
            if "OVAs" in cat_pls:
                play_playlist(cat_pls["OVAs"], vlc_path)
        return

    if args.resume:
        progress = load_progress()
        last_id = progress.get("last_played_id")
        target_ep = get_next_episode(episodes, last_id) if last_id else episodes[0]
        if not target_ep:
            target_ep = episodes[0]
        if args.binge:
            start_binge_mode(episodes, target_ep, vlc_path, skip_intro=args.skip_intro)
        else:
            stream_episode(target_ep, vlc_path, wait_finish=False, skip_intro=args.skip_intro)
        return

    if args.season is not None and args.episode is not None:
        if args.season == 0:
            ep_id = f"OVA{args.episode:02d}"
        else:
            ep_id = f"S{args.season:02d}E{args.episode:02d}"
        target_ep = next((ep for ep in episodes if ep["id"] == ep_id), None)
        if not target_ep:
            print(f"[!] Episode {ep_id} not found.")
            return
        if args.binge:
            start_binge_mode(episodes, target_ep, vlc_path, skip_intro=args.skip_intro)
        else:
            stream_episode(target_ep, vlc_path, wait_finish=False, skip_intro=args.skip_intro)
        return

    if args.play:
        target_id = args.play.upper()
        target_ep = next((ep for ep in episodes if ep["id"] == target_id), None)
        if not target_ep:
            print(f"[!] Episode {target_id} not found.")
            return
        if args.binge:
            start_binge_mode(episodes, target_ep, vlc_path, skip_intro=args.skip_intro)
        else:
            stream_episode(target_ep, vlc_path, wait_finish=False, skip_intro=args.skip_intro)
        return

    # Default interactive UI
    interactive_cli(episodes, vlc_path)

if __name__ == "__main__":
    main()
