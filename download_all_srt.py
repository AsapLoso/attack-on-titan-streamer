import urllib.request
import urllib.parse
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SUBTITLES_DIR = BASE_DIR / "subtitles"

sub_folders_map = {
    "Season 1": (
        "season-1_subtitles",
        25,
        "Attack_on_Titan-E{}-1080p-English.asr.srt",
        "S01E{:02d}.en.srt"
    ),
    "Season 2": (
        "season-2_subtitles",
        12,
        "Attack_on_Titan_Season_2-E{}-1080p-English.asr.srt",
        "S02E{:02d}.en.srt"
    ),
    "Season 3 Part 1": (
        "season-3_subtitles",
        12,
        "Attack_on_Titan_Season_3-E{}-1080p-English.asr.srt",
        "S03E{:02d}.en.srt",
        1 # start index in season 3
    ),
    "Season 3 Part 2": (
        "season-3_subtitles",
        10,
        "Attack_on_Titan_Season_3-E{}-1080p-English.asr.srt",
        "S03E{:02d}.en.srt",
        13 # start index in season 3
    ),
    "Final Season Part 1": (
        "season-finale-pt-1_subtitles",
        16,
        "Attack_on_Titan_Final_Season,_Part_1-E{}-1080p-English.asr.srt",
        "S04E{:02d}.en.srt"
    )
}

def clean_srt(content):
    """Normalize line endings and ensure valid UTF-8 format."""
    lines = content.strip().splitlines()
    return "\r\n".join(line.rstrip() for line in lines) + "\r\n"

print("=== Downloading Subtitles for Seasons 1 to 4 Part 1 ===")

for s_name, config in sub_folders_map.items():
    s_dir = SUBTITLES_DIR / s_name
    s_dir.mkdir(parents=True, exist_ok=True)
    
    folder = config[0]
    count = config[1]
    archive_tmpl = config[2]
    out_tmpl = config[3]
    start_idx = config[4] if len(config) > 4 else 1
    
    print(f"\n--- {s_name} ({count} episodes) ---")
    for i in range(count):
        ep_num = start_idx + i
        archive_name = archive_tmpl.format(ep_num)
        out_name = out_tmpl.format(ep_num)
        target_path = s_dir / out_name
        
        encoded_path = f"{folder}/{urllib.parse.quote(archive_name)}"
        srt_url = f"https://archive.org/download/shingeki-no-kyojin_aot/{encoded_path}"
        
        try:
            req = urllib.request.Request(srt_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read().decode("utf-8", errors="ignore")
                if len(data.strip()) > 100:
                    cleaned = clean_srt(data)
                    with open(target_path, "w", encoding="utf-8") as out_f:
                        out_f.write(cleaned)
                    print(f"  [✓] {out_name} ({len(data.splitlines())} lines)")
                else:
                    print(f"  [!] Small/empty subtitle for {out_name}")
        except Exception as e:
            # Fallback to .vtt if .asr.srt is not found
            vtt_name = archive_name.replace("-English.asr.srt", ".vtt").replace(".asr.srt", ".vtt")
            vtt_url = f"https://archive.org/download/shingeki-no-kyojin_aot/{folder}/{urllib.parse.quote(vtt_name)}"
            try:
                req = urllib.request.Request(vtt_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    vtt_data = resp.read().decode("utf-8", errors="ignore")
                    with open(target_path, "w", encoding="utf-8") as out_f:
                        out_f.write(vtt_data)
                    print(f"  [✓ VTT Fallback] {out_name}")
            except Exception as e2:
                print(f"  [✗] Failed {out_name}: {e2}")

# Additional directories for S4P2, Final Chapters, and OVAs
(SUBTITLES_DIR / "Final Season Part 2").mkdir(parents=True, exist_ok=True)
(SUBTITLES_DIR / "Final Chapters").mkdir(parents=True, exist_ok=True)
(SUBTITLES_DIR / "OVAs").mkdir(parents=True, exist_ok=True)

print("\nSubtitles download completed!")
