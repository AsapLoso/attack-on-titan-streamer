import urllib.request
import urllib.parse
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SUBTITLES_DIR = BASE_DIR / "subtitles"
SUBTITLES_DIR.mkdir(exist_ok=True)

# Seasons folders in the archive
season_folders = [
    ("season-1_subtitles", "Season 1", 25, "Attack_on_Titan-E{}-1080p.vtt", "S01E{:02d}.en.srt"),
    ("season-2_subtitles", "Season 2", 12, "Attack_on_Titan_Season_2-E{}-1080p.vtt", "S02E{:02d}.en.srt"),
    ("season-3_subtitles", "Season 3", 22, "Attack_on_Titan_Season_3-E{}-1080p.vtt", "S03E{:02d}.en.srt"),
    ("season-finale-pt-1_subtitles", "Final Season Part 1", 16, "Attack_on_Titan_Final_Season,_Part_1-E{}-1080p.vtt", "S04E{:02d}.en.srt")
]

def vtt_to_srt(vtt_text):
    """Convert WebVTT subtitle text to valid SRT format."""
    lines = vtt_text.strip().splitlines()
    srt_lines = []
    cue_idx = 1
    i = 0
    
    # Skip WEBVTT header
    while i < len(lines) and (lines[i].startswith("WEBVTT") or lines[i].startswith("NOTE") or not lines[i].strip()):
        i += 1
        
    while i < len(lines):
        line = lines[i].strip()
        if "-->" in line:
            # Timestamp line (e.g. 00:01:23.456 --> 00:01:25.789)
            # Replace period with comma for milliseconds
            parts = line.split("-->")
            start = parts[0].strip().replace(".", ",")
            end = parts[1].strip().split()[0].replace(".", ",") # remove position tags like line:90%
            
            # Ensure hh:mm:ss format
            if len(start.split(":")[0]) == 2 and start.count(":") == 1:
                start = "00:" + start
            if len(end.split(":")[0]) == 2 and end.count(":") == 1:
                end = "00:" + end
                
            srt_lines.append(str(cue_idx))
            srt_lines.append(f"{start} --> {end}")
            cue_idx += 1
            i += 1
            # Read dialogue lines
            dialogue = []
            while i < len(lines) and lines[i].strip():
                # clean vtt tags <v ...> or <c ...>
                clean_text = re.sub(r'<[^>]+>', '', lines[i].strip())
                if clean_text:
                    dialogue.append(clean_text)
                i += 1
            srt_lines.extend(dialogue)
            srt_lines.append("") # empty line after cue
        else:
            i += 1
            
    return "\n".join(srt_lines)

print("=== Downloading and Converting Subtitles for Seasons 1-4 Part 1 ===")

for folder, s_title, ep_count, vtt_template, srt_template in season_folders:
    s_dir = SUBTITLES_DIR / s_title
    s_dir.mkdir(exist_ok=True)
    print(f"\nProcessing {s_title} ({ep_count} episodes)...")
    
    for ep in range(1, ep_count + 1):
        vtt_name = vtt_template.format(ep)
        srt_name = srt_template.format(ep)
        target_srt = s_dir / srt_name
        
        if target_srt.exists() and target_srt.stat().st_size > 500:
            print(f"  [Exists] {srt_name}")
            continue
            
        encoded_vtt = urllib.parse.quote(vtt_name)
        vtt_url = f"https://archive.org/download/shingeki-no-kyojin_aot/{folder}/{encoded_vtt}"
        
        try:
            req = urllib.request.Request(vtt_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                vtt_data = resp.read().decode("utf-8", errors="ignore")
                srt_content = vtt_to_srt(vtt_data)
                with open(target_srt, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                print(f"  [✓ Downloaded] {srt_name} ({len(srt_content.splitlines())} lines)")
        except Exception as e:
            print(f"  [!] Error fetching {vtt_url}: {e}")

print("\nSubtitles processing finished!")
