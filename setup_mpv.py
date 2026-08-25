import urllib.request
import zipfile
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MPV_DIR = BASE_DIR / "mpv"
SCRIPTS_DIR = MPV_DIR / "portable_config" / "scripts"

MPV_ZIP_URL = "https://github.com/mpvnet-player/mpv.net/releases/download/v7.1.2.0/mpv.net-v7.1.2.0-portable-x64.zip"
ANISKIP_URL = "https://raw.githubusercontent.com/po5/mpv-aniskip/master/aniskip.lua"
THUMBFAST_URL = "https://raw.githubusercontent.com/po5/thumbfast/master/thumbfast.lua"

print("=== Setting up MPV Portable with AniSkip & Thumbfast ===")

if not (MPV_DIR / "mpvnet.exe").exists() and not (MPV_DIR / "mpv.exe").exists():
    print(f"Downloading MPV Portable from {MPV_ZIP_URL}...")
    zip_path = BASE_DIR / "mpv_portable.zip"
    
    req = urllib.request.Request(MPV_ZIP_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp, open(zip_path, "wb") as out:
        shutil.copyfileobj(resp, out)
        
    print("Extracting MPV...")
    MPV_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(MPV_DIR)
        
    if zip_path.exists():
        zip_path.unlink()
    print(f"[✓] MPV installed in {MPV_DIR}")
else:
    print("[✓] MPV already present.")

# Create scripts directory
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

# 1. Download aniskip.lua
aniskip_path = SCRIPTS_DIR / "aniskip.lua"
if not aniskip_path.exists():
    print("Downloading aniskip.lua...")
    req = urllib.request.Request(ANISKIP_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        aniskip_path.write_bytes(resp.read())
    print("[✓] Installed aniskip.lua (Auto 'Skip Intro [Tab]' button)")

# 2. Download thumbfast.lua
thumbfast_path = SCRIPTS_DIR / "thumbfast.lua"
if not thumbfast_path.exists():
    print("Downloading thumbfast.lua...")
    req = urllib.request.Request(THUMBFAST_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        thumbfast_path.write_bytes(resp.read())
    print("[✓] Installed thumbfast.lua (Hover seekbar thumbnails)")

# 3. Create mpv.conf for optimum streaming & subtitle defaults
conf_path = MPV_DIR / "portable_config" / "mpv.conf"
conf_content = """# MPV Configuration for Attack on Titan Streamer
sub-auto=fuzzy
sub-font-size=45
sub-color="#FFFFFFFF"
sub-border-color="#FF000000"
sub-border-size=2.5
sub-shadow-offset=1
osd-font-size=30
volume=100
keep-open=yes
ytdl=yes
"""
conf_path.write_text(conf_content, encoding="utf-8")
print("[✓] Created mpv.conf")

print("\n🎉 MPV Setup Complete!")
