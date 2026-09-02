#!/usr/bin/env pythonw
"""
Attack on Titan (AOT) - Desktop Stream Hub (Tkinter Native UI)
Author: Antigravity
Native dark-mode desktop interface with Always-On Binge Mode for MPV & VLC.
"""

import sys
import os
import json
import subprocess
import shutil
import threading
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

BASE_DIR = Path(__file__).resolve().parent
EPISODES_FILE = BASE_DIR / "episodes.json"
PROGRESS_FILE = BASE_DIR / "progress.json"
PLAYLISTS_DIR = BASE_DIR / "playlists"
SUBTITLES_DIR = BASE_DIR / "subtitles"
MPV_EXE = BASE_DIR / "mpv" / "mpvnet.exe"

VLC_POSSIBLE_PATHS = [
    r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
    os.environ.get("VLC_PATH", ""),
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\VLC\vlc.exe"),
]

def find_vlc():
    """Locate VLC executable on system."""
    for path in VLC_POSSIBLE_PATHS:
        if path and os.path.exists(path):
            return path
    vlc_in_path = shutil.which("vlc")
    if vlc_in_path:
        return vlc_in_path
    return None

def find_mpv():
    """Locate MPV executable."""
    if MPV_EXE.exists():
        return str(MPV_EXE.resolve())
    mpv_in_path = shutil.which("mpv") or shutil.which("mpvnet")
    if mpv_in_path:
        return mpv_in_path
    return None

def find_ffmpeg():
    """Locate FFmpeg executable on system or conda environment."""
    which_path = shutil.which("ffmpeg")
    if which_path:
        return which_path
    conda_path = Path(sys.prefix) / "Library" / "bin" / "ffmpeg.exe"
    if conda_path.exists():
        return str(conda_path)
    return None

def get_time_between_endings(ep):
    """Calculate episode story content duration (from post-intro up to ed_start)."""
    ts = ep.get("timestamps", {})
    op_end = ts.get("op_end", 0) if (ts and ts.get("op_end") is not None) else 0
    if ts and ts.get("ed_start") is not None:
        ed_start = ts["ed_start"]
    elif ep.get("id") == "S04E29":
        ed_start = 59 * 60
    elif ep.get("id") == "S04E30":
        ed_start = 83 * 60
    elif ep.get("type") == "ova":
        ed_start = 25 * 60
    elif ep.get("type") == "movie":
        ed_start = 115 * 60
    else:
        ed_start = 22.5 * 60

    return max(60, round(ed_start - op_end))

def format_net_duration(sec):
    """Format seconds into readable min / h m."""
    mins = round(sec / 60)
    if mins < 60:
        return f"{mins} min"
    h = mins // 60
    m = mins % 60
    return f"{h}h" if m == 0 else f"{h}h {m}m"

def load_episodes():
    """Load episodes list from episodes.json."""
    if not EPISODES_FILE.exists():
        return []
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
    return {"last_played_id": None, "history": [], "player": "MPV"}

def save_progress(ep_id, player="MPV"):
    """Save progress."""
    data = load_progress()
    data["last_played_id"] = ep_id
    data["player"] = player
    if ep_id not in data.get("history", []):
        data.setdefault("history", []).append(ep_id)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class AOTStreamHub(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("⚔️ Attack on Titan - Stream Hub (Binge Mode)")
        self.geometry("1150x750")
        self.minsize(900, 580)
        self.configure(bg="#121214")
        
        self.vlc_path = find_vlc()
        self.mpv_path = find_mpv()
        self.episodes = load_episodes()
        self.progress = load_progress()
        self.current_category = "All"
        self.search_query = ""
        self.player_var = tk.StringVar(value="MPV (On-Screen Skip [Tab])" if self.mpv_path else "VLC Media Player")
        self.skip_intro_var = tk.BooleanVar(value=False)
        self.enable_subs_var = tk.BooleanVar(value=True)
        
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        self._build_header()
        self._build_body()
        self._refresh_episode_list()
        
    def _build_header(self):
        header_frame = tk.Frame(self, bg="#1a1a1f", height=85, padx=20, pady=12)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Left title & resume
        title_box = tk.Frame(header_frame, bg="#1a1a1f")
        title_box.pack(side=tk.LEFT, fill=tk.Y)
        
        title_lbl = tk.Label(
            title_box, 
            text="⚔️ ATTACK ON TITAN", 
            font=("Segoe UI", 16, "bold"), 
            fg="#e50914", 
            bg="#1a1a1f"
        )
        title_lbl.pack(anchor="w")
        
        sub_title = tk.Label(
            title_box, 
            text="1080p English Dub • Auto-Next Binge Mode Active", 
            font=("Segoe UI", 9), 
            fg="#4ade80", 
            bg="#1a1a1f"
        )
        sub_title.pack(anchor="w")
        
        # Right controls
        ctrl_box = tk.Frame(header_frame, bg="#1a1a1f")
        ctrl_box.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Player selector dropdown
        player_box = tk.Frame(ctrl_box, bg="#1a1a1f")
        player_box.pack(side=tk.LEFT, padx=(0, 10))
        
        pl_lbl = tk.Label(player_box, text="Player:", font=("Segoe UI", 8, "bold"), fg="#71717a", bg="#1a1a1f")
        pl_lbl.pack(anchor="w")
        
        player_menu = ttk.Combobox(
            player_box,
            textvariable=self.player_var,
            values=["MPV (On-Screen Skip [Tab])", "VLC Media Player"],
            state="readonly",
            width=22,
            font=("Segoe UI", 9)
        )
        player_menu.pack()
        if self.mpv_path:
            player_menu.current(0)
        else:
            player_menu.current(1)
            
        # Search input
        search_box = tk.Frame(ctrl_box, bg="#27272e", padx=8, pady=4)
        search_box.pack(side=tk.LEFT, padx=8)
        
        search_icon = tk.Label(search_box, text="🔍", bg="#27272e", fg="#ffffff")
        search_icon.pack(side=tk.LEFT)
        
        self.search_entry = tk.Entry(
            search_box, 
            font=("Segoe UI", 10), 
            bg="#27272e", 
            fg="#ffffff", 
            insertbackground="#ffffff", 
            bd=0, 
            width=18
        )
        self.search_entry.pack(side=tk.LEFT, padx=4)
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # Toggles
        toggles_box = tk.Frame(ctrl_box, bg="#1a1a1f")
        toggles_box.pack(side=tk.LEFT, padx=6)
        
        sub_cb = tk.Checkbutton(
            toggles_box,
            text="💬 English CC",
            variable=self.enable_subs_var,
            bg="#1a1a1f",
            fg="#e0e0e0",
            selectcolor="#27272e",
            activebackground="#1a1a1f",
            activeforeground="#ffffff",
            font=("Segoe UI", 9)
        )
        sub_cb.pack(anchor="w")
        
        skip_cb = tk.Checkbutton(
            toggles_box,
            text="⏩ Auto-Skip OP",
            variable=self.skip_intro_var,
            bg="#1a1a1f",
            fg="#e0e0e0",
            selectcolor="#27272e",
            activebackground="#1a1a1f",
            activeforeground="#ffffff",
            font=("Segoe UI", 9)
        )
        skip_cb.pack(anchor="w")
        
        # Resume button
        last_id = self.progress.get("last_played_id", "S01E01")
        self.resume_btn = tk.Button(
            ctrl_box,
            text=f"▶ Binge: {last_id or 'S01E01'}",
            font=("Segoe UI", 10, "bold"),
            bg="#e50914",
            fg="#ffffff",
            activebackground="#b80710",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._play_resume
        )
        self.resume_btn.pack(side=tk.LEFT, padx=6)

    def _build_body(self):
        body_frame = tk.Frame(self, bg="#121214")
        body_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Left Sidebar (Categories)
        sidebar = tk.Frame(body_frame, bg="#18181c", width=210, padx=10, pady=15)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        cat_lbl = tk.Label(sidebar, text="SEASONS & ARCS", font=("Segoe UI", 9, "bold"), fg="#71717a", bg="#18181c")
        cat_lbl.pack(anchor="w", pady=(0, 10), padx=8)
        
        self.categories = [
            ("All Episodes", "All", 97),
            ("Season 1", "1", 25),
            ("Season 2", "2", 12),
            ("Season 3", "3", 22),
            ("The Final Season", "4", 30),
            ("Official OVAs", "OVA", 8),
        ]
        
        self.cat_buttons = {}
        for label, cat_id, count in self.categories:
            btn = tk.Button(
                sidebar,
                text=f"{label}  ({count})",
                font=("Segoe UI", 10),
                bg="#222228" if cat_id == "All" else "#18181c",
                fg="#ffffff" if cat_id == "All" else "#a1a1aa",
                activebackground="#27272e",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                anchor="w",
                padx=12,
                pady=8,
                cursor="hand2",
                command=lambda c=cat_id: self._select_category(c)
            )
            btn.pack(fill=tk.X, pady=2)
            self.cat_buttons[cat_id] = btn

        # Playlist Action
        pl_sep = tk.Frame(sidebar, height=1, bg="#27272e")
        pl_sep.pack(fill=tk.X, pady=15)
        
        pl_btn = tk.Button(
            sidebar,
            text="🎵 Open Full Playlist",
            font=("Segoe UI", 9, "bold"),
            bg="#27272e",
            fg="#00adb5",
            activebackground="#33333d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=8,
            pady=8,
            cursor="hand2",
            command=self._open_full_playlist
        )
        pl_btn.pack(fill=tk.X, pady=4)

        # Right Content (Scrollable Canvas)
        content_container = tk.Frame(body_frame, bg="#121214")
        content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.canvas = tk.Canvas(content_container, bg="#121214", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(content_container, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.scroll_content = tk.Frame(self.canvas, bg="#121214")
        self.scroll_content.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.bind(
            "<Configure>", 
            lambda event: self.canvas.itemconfig(self.canvas_window, width=event.width)
        )
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _select_category(self, cat_id):
        self.current_category = cat_id
        for c, btn in self.cat_buttons.items():
            if c == cat_id:
                btn.configure(bg="#27272e", fg="#ffffff", font=("Segoe UI", 10, "bold"))
            else:
                btn.configure(bg="#18181c", fg="#a1a1aa", font=("Segoe UI", 10))
        self._refresh_episode_list()

    def _on_search(self, event):
        self.search_query = self.search_entry.get().strip().lower()
        self._refresh_episode_list()

    def _refresh_episode_list(self):
        for widget in self.scroll_content.winfo_children():
            widget.destroy()
            
        filtered = []
        for ep in self.episodes:
            if self.current_category == "1" and ep.get("season_num") != 1:
                continue
            elif self.current_category == "2" and ep.get("season_num") != 2:
                continue
            elif self.current_category == "3" and ep.get("season_num") != 3:
                continue
            elif self.current_category == "4" and ep.get("season_num") != 4:
                continue
            elif self.current_category == "OVA" and (ep.get("type") != "ova" and ep.get("season_num") != 0):
                continue
                
            if self.search_query:
                title_str = ep.get("title", "").lower()
                id_str = ep.get("id", "").lower()
                fn_str = ep.get("filename", "").lower()
                if self.search_query not in title_str and self.search_query not in id_str and self.search_query not in fn_str:
                    continue
                    
            filtered.append(ep)

        count_lbl = tk.Label(
            self.scroll_content,
            text=f"Showing {len(filtered)} episodes (Click ▶ to Binge from any episode)",
            font=("Segoe UI", 10, "bold"),
            fg="#71717a",
            bg="#121214"
        )
        count_lbl.pack(anchor="w", padx=4, pady=(0, 10))

        history = self.progress.get("history", [])
        for ep in filtered:
            self._render_episode_card(ep, is_watched=(ep["id"] in history))

    def _render_episode_card(self, ep, is_watched):
        card = tk.Frame(self.scroll_content, bg="#1a1a1f", pady=10, padx=15, relief=tk.FLAT)
        card.pack(fill=tk.X, pady=4, padx=2)

        info_frame = tk.Frame(card, bg="#1a1a1f")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        top_row = tk.Frame(info_frame, bg="#1a1a1f")
        top_row.pack(anchor="w")

        badge_bg = "#27272e"
        badge_fg = "#00adb5"
        if ep.get("type") == "movie":
            badge_fg = "#f39c12"
        elif ep.get("type") == "ova":
            badge_fg = "#9b59b6"

        id_badge = tk.Label(
            top_row,
            text=f" {ep['id']} ",
            font=("Segoe UI", 9, "bold"),
            bg=badge_bg,
            fg=badge_fg,
            padx=4,
            pady=1
        )
        id_badge.pack(side=tk.LEFT, padx=(0, 10))

        title_lbl = tk.Label(
            top_row,
            text=ep.get("title", ep.get("filename", "")),
            font=("Segoe UI", 11, "bold"),
            fg="#ffffff" if not is_watched else "#a1a1aa",
            bg="#1a1a1f"
        )
        title_lbl.pack(side=tk.LEFT)

        bot_row = tk.Frame(info_frame, bg="#1a1a1f")
        bot_row.pack(anchor="w", pady=(4, 0))

        meta_text = f"{ep.get('season_title', '')} • 1080p English Dub"
        if ep.get("size_mb"):
            meta_text += f" • {ep['size_mb']} MB"
        
        meta_lbl = tk.Label(bot_row, text=meta_text, font=("Segoe UI", 8), fg="#71717a", bg="#1a1a1f")
        meta_lbl.pack(side=tk.LEFT, padx=(0, 12))

        sub_path = BASE_DIR / ep.get("subtitle_path", "")
        if sub_path.exists():
            sub_badge = tk.Label(bot_row, text="CC English", font=("Segoe UI", 7, "bold"), bg="#1e3a2b", fg="#4ade80", padx=4)
            sub_badge.pack(side=tk.LEFT, padx=(0, 8))

        if is_watched:
            watched_badge = tk.Label(bot_row, text="✓ Watched", font=("Segoe UI", 8), fg="#4ade80", bg="#1a1a1f")
            watched_badge.pack(side=tk.LEFT)

        # Download Button
        dl_btn = tk.Button(
            card,
            text="⬇ Download",
            font=("Segoe UI", 9, "bold"),
            bg="#162e2e",
            fg="#00adb5",
            activebackground="#00adb5",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            cursor="hand2",
            command=lambda e=ep: self._open_download_dialog(e)
        )
        dl_btn.pack(side=tk.RIGHT, padx=4)

        # Binge Play Button
        play_btn = tk.Button(
            card,
            text="▶ Binge from here",
            font=("Segoe UI", 9, "bold"),
            bg="#27272e",
            fg="#ffffff",
            activebackground="#e50914",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=lambda e=ep: self._play_episode(e)
        )
        play_btn.pack(side=tk.RIGHT, padx=5)

    def _open_download_dialog(self, episode):
        """Open batch download popup with counting net duration dropdown."""
        start_idx = 0
        for i, ep in enumerate(self.episodes):
            if ep["id"] == episode["id"]:
                start_idx = i
                break

        max_available = min(6, len(self.episodes) - start_idx)
        combo_values = []
        option_map = {}
        cumulative_sec = 0

        for count in range(1, max_available + 1):
            ep_item = self.episodes[start_idx + count - 1]
            cumulative_sec += get_time_between_endings(ep_item)
            time_str = format_net_duration(cumulative_sec)

            if count == 1:
                label = f"1 ep ({time_str} • {episode['id']})"
            else:
                label = f"{count} eps ({time_str} • {episode['id']} - {ep_item['id']})"

            combo_values.append(label)
            option_map[label] = count

        # Create Modal Window
        win = tk.Toplevel(self)
        win.title(f"⬇ Download Video & Subtitles - {episode['id']}")
        win.geometry("560x420")
        win.minsize(500, 380)
        win.configure(bg="#18181f")
        win.transient(self)
        win.grab_set()

        # Header in Modal
        header = tk.Frame(win, bg="#18181f", padx=20, pady=15)
        header.pack(fill=tk.X)

        title_lbl = tk.Label(
            header,
            text=f"⬇ Download: {episode['id']} - {episode.get('title', episode.get('filename', ''))}",
            font=("Segoe UI", 12, "bold"),
            fg="#00adb5",
            bg="#18181f"
        )
        title_lbl.pack(anchor="w")

        info_lbl = tk.Label(
            header,
            text=f"{episode.get('season_title', '')} • 1080p English Dub + CC Subtitles",
            font=("Segoe UI", 9),
            fg="#a1a1aa",
            bg="#18181f"
        )
        info_lbl.pack(anchor="w", pady=(2, 0))

        body = tk.Frame(win, bg="#18181f", padx=20)
        body.pack(fill=tk.BOTH, expand=True)

        # Batch Selector Dropdown
        sel_lbl = tk.Label(body, text="Select Episode Batch (Duration excluding Intro & Outro):", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#18181f")
        sel_lbl.pack(anchor="w", pady=(10, 4))

        batch_var = tk.StringVar(value=combo_values[0] if combo_values else "")
        batch_combo = ttk.Combobox(body, textvariable=batch_var, values=combo_values, state="readonly", font=("Segoe UI", 9))
        batch_combo.pack(fill=tk.X, pady=(0, 15))

        # Subtitle Embedding Checkbox (FFmpeg detection)
        ffmpeg_bin = find_ffmpeg()
        embed_var = tk.BooleanVar(value=bool(ffmpeg_bin))
        embed_cb = tk.Checkbutton(
            body,
            text="🎬 Embed Subtitles into MP4 container (FFmpeg fast-mux)" if ffmpeg_bin else "☐ Embed Subtitles (FFmpeg not found - saving side-by-side)",
            variable=embed_var,
            state=tk.NORMAL if ffmpeg_bin else tk.DISABLED,
            bg="#18181f",
            fg="#4ade80" if ffmpeg_bin else "#71717a",
            selectcolor="#27272e",
            activebackground="#18181f",
            activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold" if ffmpeg_bin else "normal")
        )
        embed_cb.pack(anchor="w", pady=(0, 15))

        # Save Directory Selector
        dest_lbl = tk.Label(body, text="Save To Folder:", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#18181f")
        dest_lbl.pack(anchor="w", pady=(0, 4))

        default_dir = str((BASE_DIR / "downloads").resolve())
        dir_var = tk.StringVar(value=default_dir)

        dir_frame = tk.Frame(body, bg="#18181f")
        dir_frame.pack(fill=tk.X, pady=(0, 15))

        dir_entry = tk.Entry(dir_frame, textvariable=dir_var, font=("Segoe UI", 9), bg="#27272e", fg="#ffffff", insertbackground="#ffffff", bd=0)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 6))

        def browse_dir():
            chosen = filedialog.askdirectory(initialdir=dir_var.get(), parent=win)
            if chosen:
                dir_var.set(chosen)

        browse_btn = tk.Button(dir_frame, text="Browse...", font=("Segoe UI", 9), bg="#33333f", fg="#ffffff", relief=tk.FLAT, padx=10, command=browse_dir)
        browse_btn.pack(side=tk.RIGHT)

        # Progress elements
        progress_bar = ttk.Progressbar(body, mode="determinate")
        progress_bar.pack(fill=tk.X, pady=(10, 4))

        status_lbl = tk.Label(body, text="Ready to download.", font=("Segoe UI", 8), fg="#4ade80", bg="#18181f")
        status_lbl.pack(anchor="w", pady=(0, 10))

        # Action Buttons
        btn_frame = tk.Frame(win, bg="#18181f", padx=20, pady=15)
        btn_frame.pack(fill=tk.X)

        cancel_flag = {"cancelled": False}

        def on_close():
            cancel_flag["cancelled"] = True
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        def start_download():
            selected_label = batch_var.get()
            count = option_map.get(selected_label, 1)
            target_folder = Path(dir_var.get())
            target_folder.mkdir(parents=True, exist_ok=True)

            items_to_download = self.episodes[start_idx : start_idx + count]
            dl_action_btn.configure(state=tk.DISABLED, text="Downloading...")
            batch_combo.configure(state=tk.DISABLED)
            embed_cb.configure(state=tk.DISABLED)

            def worker():
                total_items = len(items_to_download)
                completed_count = 0

                for idx, ep_item in enumerate(items_to_download):
                    if cancel_flag["cancelled"]:
                        break

                    ep_id = ep_item["id"]
                    fn = ep_item.get("filename") or f"{ep_id}.mp4"
                    final_mp4 = target_folder / f"{ep_id}_{fn}"
                    tmp_mp4 = target_folder / f".tmp_{ep_id}_{fn}"
                    target_sub = target_folder / f"{ep_id}_English.srt"

                    # 1. Download Video with Retries
                    download_ok = False
                    for attempt in range(1, 4):
                        if cancel_flag["cancelled"]:
                            break
                        try:
                            win.after(0, lambda t=f"Downloading ({idx+1}/{total_items}): {ep_id} (Attempt {attempt})...": status_lbl.configure(text=t))
                            req = urllib.request.Request(ep_item["stream_url"], headers={"User-Agent": "Mozilla/5.0"})
                            with urllib.request.urlopen(req, timeout=35) as response, open(tmp_mp4, "wb") as out_file:
                                total_size = int(response.headers.get("content-length", 0))
                                downloaded = 0
                                chunk_size = 1024 * 512
                                while not cancel_flag["cancelled"]:
                                    chunk = response.read(chunk_size)
                                    if not chunk:
                                        break
                                    out_file.write(chunk)
                                    downloaded += len(chunk)
                                    if total_size > 0:
                                        percent = (downloaded / total_size) * 100
                                        mb_cur = downloaded / (1024 * 1024)
                                        mb_tot = total_size / (1024 * 1024)
                                        overall_pct = ((idx + (downloaded / total_size)) / total_items) * 100
                                        win.after(0, lambda p=overall_pct, txt=f"[{idx+1}/{total_items}] {ep_id}: {mb_cur:.1f}/{mb_tot:.1f} MB ({percent:.0f}%)": (
                                            progress_bar.configure(value=p),
                                            status_lbl.configure(text=txt)
                                        ))
                                if not cancel_flag["cancelled"]:
                                    download_ok = True
                                    break
                        except Exception as e:
                            print(f"Download retry {attempt} failed on {ep_id}: {e}")
                            if attempt < 3:
                                import time
                                time.sleep(1.5)

                    if cancel_flag["cancelled"]:
                        if tmp_mp4.exists():
                            tmp_mp4.unlink()
                        break

                    if not download_ok:
                        continue

                    # 2. Prepare Subtitle File
                    sub_file = ep_item.get("subtitle_path")
                    has_sub = False
                    if sub_file:
                        local_sub = BASE_DIR / sub_file
                        if local_sub.exists():
                            shutil.copy2(local_sub, target_sub)
                            has_sub = True
                        else:
                            try:
                                sub_url = f"https://asaploso.github.io/attack-on-titan-streamer/{sub_file}"
                                req_sub = urllib.request.Request(sub_url, headers={"User-Agent": "Mozilla/5.0"})
                                with urllib.request.urlopen(req_sub, timeout=12) as s_resp, open(target_sub, "wb") as s_out:
                                    s_out.write(s_resp.read())
                                has_sub = True
                            except Exception:
                                pass

                    # 3. Robust FFmpeg Muxing (Embed Subtitles into MP4)
                    if embed_var.get() and ffmpeg_bin and has_sub and target_sub.exists() and target_sub.stat().st_size > 50:
                        win.after(0, lambda: status_lbl.configure(text=f"[{idx+1}/{total_items}] {ep_id}: Embedding subtitles via FFmpeg..."))
                        muxed_tmp = target_folder / f".mux_{ep_id}_{fn}"
                        cmd = [
                            ffmpeg_bin, "-y",
                            "-i", str(tmp_mp4.resolve()),
                            "-i", str(target_sub.resolve()),
                            "-c:v", "copy",
                            "-c:a", "copy",
                            "-c:s", "mov_text",
                            "-metadata:s:s:0", "language=eng",
                            "-metadata:s:s:0", "title=English CC",
                            "-movflags", "+faststart",
                            str(muxed_tmp.resolve())
                        ]
                        try:
                            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)
                            if res.returncode == 0 and muxed_tmp.exists() and muxed_tmp.stat().st_size > 1024 * 1024:
                                if final_mp4.exists():
                                    final_mp4.unlink()
                                muxed_tmp.rename(final_mp4)
                                if tmp_mp4.exists():
                                    tmp_mp4.unlink()
                            else:
                                if final_mp4.exists():
                                    final_mp4.unlink()
                                tmp_mp4.rename(final_mp4)
                        except Exception as mux_err:
                            print(f"Mux fallback on {ep_id}: {mux_err}")
                            if final_mp4.exists():
                                final_mp4.unlink()
                            tmp_mp4.rename(final_mp4)
                    else:
                        if final_mp4.exists():
                            final_mp4.unlink()
                        tmp_mp4.rename(final_mp4)

                    completed_count += 1

                if not cancel_flag["cancelled"]:
                    win.after(0, lambda: (
                        progress_bar.configure(value=100),
                        status_lbl.configure(text=f"✓ Complete! Saved {completed_count} episode(s) to: {target_folder}"),
                        dl_action_btn.configure(text="📂 Open Folder", state=tk.NORMAL, bg="#4ade80", fg="#000000", command=lambda: os.startfile(target_folder))
                    ))

            t = threading.Thread(target=worker, daemon=True)
            t.start()

        dl_action_btn = tk.Button(
            btn_frame,
            text="⬇ Start Download",
            font=("Segoe UI", 10, "bold"),
            bg="#00adb5",
            fg="#ffffff",
            activebackground="#007c82",
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=start_download
        )
        dl_action_btn.pack(side=tk.RIGHT, padx=6)

        cancel_btn = tk.Button(
            btn_frame,
            text="Close",
            font=("Segoe UI", 9),
            bg="#27272e",
            fg="#a1a1aa",
            relief=tk.FLAT,
            padx=12,
            pady=8,
            cursor="hand2",
            command=on_close
        )
        cancel_btn.pack(side=tk.RIGHT)

    def _play_episode(self, episode):
        use_mpv = "MPV" in self.player_var.get()
        target_player = "MPV" if use_mpv else "VLC"
        
        save_progress(episode["id"], target_player)
        self.progress = load_progress()
        self.resume_btn.configure(text=f"▶ Binge: {episode['id']}")

        # Direct stream execution with subtitles
        sub_path = BASE_DIR / episode.get("subtitle_path", "")
        has_sub = sub_path.exists() and self.enable_subs_var.get()
        ts = episode.get("timestamps", {})

        if use_mpv and self.mpv_path:
            cmd = [
                self.mpv_path,
                episode["stream_url"],
                f"--title=Attack on Titan - {episode['id']}: {episode.get('title', '')}",
                "--keep-open=yes"
            ]
            if has_sub:
                cmd.append(f"--sub-file={str(sub_path.resolve())}")
            if self.skip_intro_var.get() and ts and ts.get("op_end"):
                cmd.append(f"--start={int(ts['op_end'])}")
            subprocess.Popen(cmd)
        else:
            if not self.vlc_path:
                messagebox.showerror("Player Not Found", "Neither MPV nor VLC was located on your system.")
                return
            cmd = [
                self.vlc_path,
                episode["stream_url"],
                f"--meta-title=Attack on Titan - {episode['id']}: {episode.get('title', '')}"
            ]
            if has_sub:
                cmd.append(f"--sub-file={str(sub_path.resolve())}")
            if self.skip_intro_var.get() and ts and ts.get("op_end"):
                cmd.append(f"--start-time={int(ts['op_end'])}")
            subprocess.Popen(cmd)

        self._refresh_episode_list()

    def _play_resume(self):
        last_id = self.progress.get("last_played_id")
        target_ep = None
        if last_id:
            for idx, ep in enumerate(self.episodes):
                if ep["id"] == last_id:
                    if idx + 1 < len(self.episodes):
                        target_ep = self.episodes[idx + 1]
                    break
        if not target_ep:
            target_ep = self.episodes[0]
        self._play_episode(target_ep)

    def _open_full_playlist(self):
        pl_path = PLAYLISTS_DIR / "Attack_on_Titan_Full_Series.m3u8"
        if not pl_path.exists():
            messagebox.showerror("Error", "Playlist file not found.")
            return
        if "MPV" in self.player_var.get() and self.mpv_path:
            subprocess.Popen([self.mpv_path, str(pl_path.resolve())])
        elif self.vlc_path:
            subprocess.Popen([self.vlc_path, str(pl_path.resolve())])

def main():
    app = AOTStreamHub()
    app.mainloop()

if __name__ == "__main__":
    main()
