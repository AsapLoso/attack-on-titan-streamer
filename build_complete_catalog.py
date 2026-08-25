import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Build the comprehensive 97-item catalog
episodes = []

# ==========================================
# 1. Season 1 (Episodes 1 to 25)
# ==========================================
s1_titles = [
    "To You, in 2000 Years: The Fall of Shiganshina, Part 1",
    "That Day: The Fall of Shiganshina, Part 2",
    "A Dim Light Amid Despair: Humanity's Comeback, Part 1",
    "Night of the Graduation Ceremony: Humanity's Comeback, Part 2",
    "First Battle: The Struggle for Trost, Part 1",
    "The World the Girl Saw: The Struggle for Trost, Part 2",
    "Small Blade: The Struggle for Trost, Part 3",
    "I Can Hear His Heartbeat: The Struggle for Trost, Part 4",
    "Whereabouts of His Left Arm: The Struggle for Trost, Part 5",
    "Response: The Struggle for Trost, Part 6",
    "Idol: The Struggle for Trost, Part 7",
    "Wound: The Struggle for Trost, Part 8",
    "Primal Desire: The Struggle for Trost, Part 9",
    "Can't Look into His Eyes Yet: Eve of the Counterattack, Part 1",
    "Special Operations Squad: Eve of the Counterattack, Part 2",
    "What Should Be Done: Eve of the Counterattack, Part 3",
    "Female Titan: The 57th Exterior Scouting Mission, Part 1",
    "Forest of Giant Trees: The 57th Exterior Scouting Mission, Part 2",
    "Bite: The 57th Exterior Scouting Mission, Part 3",
    "Erwin Smith: The 57th Exterior Scouting Mission, Part 4",
    "Crushing Blow: The 57th Exterior Scouting Mission, Part 5",
    "The Defeated: The 57th Exterior Scouting Mission, Part 6",
    "Smile: Raid on Stohess District, Part 1",
    "Mercy: Raid on Stohess District, Part 2",
    "Wall: Raid on Stohess District, Part 3"
]

for i, title in enumerate(s1_titles, 1):
    episodes.append({
        "id": f"S01E{i:02d}",
        "type": "tv",
        "season_num": 1,
        "season_title": "Season 1",
        "ep_num": i,
        "absolute_num": i,
        "title": title,
        "mal_id": 16498,
        "mal_ep_num": i,
        "filename": f"Attack_on_Titan-E{i}-1080p.mp4",
        "archive_path": f"season-1_DUB-1080p/Attack_on_Titan-E{i}-1080p.mp4",
        "stream_url": f"https://archive.org/download/shingeki-no-kyojin_aot/season-1_DUB-1080p/Attack_on_Titan-E{i}-1080p.mp4",
        "subtitle_path": f"subtitles/Season 1/S01E{i:02d}.en.srt",
        "timestamps": {
            "op_start": 128.4 if i != 1 else 128.4,
            "op_end": 218.4,
            "ed_start": 1342.8,
            "ed_end": 1430.6
        }
    })

# ==========================================
# 2. Season 2 (Episodes 1 to 12)
# ==========================================
s2_titles = [
    "Beast Titan", "I'm Home", "Southwestward", "Soldier", "Historia",
    "Warrior", "Close Combat", "The Hunters", "Opening", "Children",
    "Charge", "Scream"
]

for i, title in enumerate(s2_titles, 1):
    abs_num = 25 + i
    episodes.append({
        "id": f"S02E{i:02d}",
        "type": "tv",
        "season_num": 2,
        "season_title": "Season 2",
        "ep_num": i,
        "absolute_num": abs_num,
        "title": title,
        "mal_id": 25777,
        "mal_ep_num": i,
        "filename": f"Attack_on_Titan_Season_2-E{i}-1080p.mp4",
        "archive_path": f"season-2_DUB-1080p/Attack_on_Titan_Season_2-E{i}-1080p.mp4",
        "stream_url": f"https://archive.org/download/shingeki-no-kyojin_aot/season-2_DUB-1080p/Attack_on_Titan_Season_2-E{i}-1080p.mp4",
        "subtitle_path": f"subtitles/Season 2/S02E{i:02d}.en.srt",
        "timestamps": {
            "op_start": 167.7,
            "op_end": 257.7,
            "ed_start": 1329.0,
            "ed_end": 1434.0
        }
    })

# ==========================================
# 3. Season 3 (Episodes 1 to 22)
# ==========================================
s3_titles = [
    "Smoke Signal", "Pain", "Old Story", "Trust", "Reply", "Sin", "Wish",
    "Outside the Gates of Orvud District", "Ruler of the Walls", "Friends",
    "Bystander", "Night of the Battle to Retake the Wall",
    "The Town Where Everything Began", "Thunder Spears", "Descent",
    "Perfect Game", "Hero", "Midnight Sun", "The Basement", "That Day",
    "Attack Titan", "The Other Side of the Wall"
]

for i, title in enumerate(s3_titles, 1):
    abs_num = 37 + i
    is_part2 = i > 12
    s3_folder = "Season 3 Part 2" if is_part2 else "Season 3 Part 1"
    mal_id = 38524 if is_part2 else 35760
    mal_ep = i - 12 if is_part2 else i
    
    episodes.append({
        "id": f"S03E{i:02d}",
        "type": "tv",
        "season_num": 3,
        "season_title": "Season 3",
        "ep_num": i,
        "absolute_num": abs_num,
        "title": title,
        "mal_id": mal_id,
        "mal_ep_num": mal_ep,
        "filename": f"Attack_on_Titan_Season_3-E{i}-1080p.mp4",
        "archive_path": f"season-3_DUB-1080p/Attack_on_Titan_Season_3-E{i}-1080p.mp4",
        "stream_url": f"https://archive.org/download/shingeki-no-kyojin_aot/season-3_DUB-1080p/Attack_on_Titan_Season_3-E{i}-1080p.mp4",
        "subtitle_path": f"subtitles/{s3_folder}/S03E{i:02d}.en.srt",
        "timestamps": {
            "op_start": 111.2 if is_part2 else 2.15,
            "op_end": 204.8 if is_part2 else 92.15,
            "ed_start": 1330.2,
            "ed_end": 1420.2
        }
    })

# ==========================================
# 4. Final Season Part 1 (Episodes 1 to 16)
# ==========================================
s4_p1_titles = [
    "The Other Side of the Sea", "Midnight Train", "The Door of Hope",
    "From One Hand to Another", "Declaration of War", "The War Hammer Titan",
    "Assault", "Assassin's Bullet", "Brave Volunteers", "A Sound Argument",
    "Deceiver", "Guides", "Children of the Forest", "Savagery", "Sole Salvation",
    "Above and Below"
]

for i, title in enumerate(s4_p1_titles, 1):
    abs_num = 59 + i
    episodes.append({
        "id": f"S04E{i:02d}",
        "type": "tv",
        "season_num": 4,
        "season_title": "The Final Season Part 1",
        "ep_num": i,
        "absolute_num": abs_num,
        "title": title,
        "mal_id": 40028,
        "mal_ep_num": i,
        "filename": f"Attack_on_Titan_Final_Season,_Part_1-E{i}-1080p.mp4",
        "archive_path": f"season-finale-pt-1_DUB-1080p/Attack_on_Titan_Final_Season,_Part_1-E{i}-1080p.mp4",
        "stream_url": f"https://archive.org/download/shingeki-no-kyojin_aot/season-finale-pt-1_DUB-1080p/Attack_on_Titan_Final_Season%2C_Part_1-E{i}-1080p.mp4",
        "subtitle_path": f"subtitles/Final Season Part 1/S04E{i:02d}.en.srt",
        "timestamps": {
            "op_start": 208.0,
            "op_end": 298.5,
            "ed_start": 1377.0,
            "ed_end": 1420.2
        }
    })

# ==========================================
# 5. Final Season Part 2 (Episodes 17 to 28)
# ==========================================
s4_p2_titles = [
    "Judgment", "Sneak Attack", "Two Brothers", "Memories of the Future",
    "From You, 2,000 Years Ago", "Thaw", "Sunset", "Pride", "Night of the End",
    "Traitor", "Retrospective", "The Dawn of Humanity"
]

for idx, title in enumerate(s4_p2_titles, 17):
    ep_p2 = idx - 16
    abs_num = 75 + ep_p2
    episodes.append({
        "id": f"S04E{idx:02d}",
        "type": "tv",
        "season_num": 4,
        "season_title": "The Final Season Part 2",
        "ep_num": idx,
        "absolute_num": abs_num,
        "title": title,
        "mal_id": 48583,
        "mal_ep_num": ep_p2,
        "filename": f"Attack_on_Titan_Final_Season_Part_2-E{ep_p2}-1080p.mp4",
        "archive_path": f"attack-on-titan-chronology-final-season-pt2-uncut/Attack_on_Titan_Final_Season_Part_2-E{ep_p2}-1080p.mp4",
        "stream_url": f"https://archive.org/download/attack-on-titan-chronology-final-season-pt2-uncut/Attack_on_Titan_Final_Season_Part_2-E{ep_p2}-1080p.mp4",
        "subtitle_path": f"subtitles/Final Season Part 2/S04E{idx:02d}.en.srt",
        "timestamps": {
            "op_start": 220.0,
            "op_end": 310.0,
            "ed_start": 1329.9,
            "ed_end": 1420.0
        }
    })

# ==========================================
# 6. The Final Chapters Movie Specials (1 & 2)
# ==========================================
episodes.append({
    "id": "S04E29",
    "type": "movie",
    "season_num": 4,
    "season_title": "The Final Chapters (Specials)",
    "ep_num": 29,
    "absolute_num": 88,
    "title": "The Final Chapters: Special 1 (The Rumbling / Sinners)",
    "mal_id": 51535,
    "mal_ep_num": 1,
    "filename": "EP.1.TVRip.1080p.mp4",
    "archive_path": "attack-on-titan-the-final-chapters-ep.-1.-tvrip.-1080p/EP.1.TVRip.1080p.mp4",
    "stream_url": "https://archive.org/download/attack-on-titan-the-final-chapters-ep.-1.-tvrip.-1080p/EP.1.TVRip.1080p.mp4",
    "subtitle_path": "subtitles/Final Chapters/S04E29_Special_1.en.srt",
    "timestamps": {
        "op_start": None,
        "op_end": None,
        "ed_start": 3500.0,
        "ed_end": 3664.0
    }
})

episodes.append({
    "id": "S04E30",
    "type": "movie",
    "season_num": 4,
    "season_title": "The Final Chapters (Specials)",
    "ep_num": 30,
    "absolute_num": 89,
    "title": "The Final Chapters: Special 2 (The Battle of Heaven and Earth / Toward the Tree on That Hill)",
    "mal_id": 54492,
    "mal_ep_num": 1,
    "filename": "EP.2.TVRip.1080p.mp4",
    "archive_path": "attack-on-titan-the-final-chapters-ep.-2.-tvrip.-1080p/EP.2.TVRip.1080p.mp4",
    "stream_url": "https://archive.org/download/attack-on-titan-the-final-chapters-ep.-2.-tvrip.-1080p/EP.2.TVRip.1080p.mp4",
    "subtitle_path": "subtitles/Final Chapters/S04E30_Special_2.en.srt",
    "timestamps": {
        "op_start": None,
        "op_end": None,
        "ed_start": 4900.0,
        "ed_end": 5106.0
    }
})

# ==========================================
# 7. Official OVAs (8 Episodes)
# ==========================================
ova_list = [
    {
        "id": "OVA01",
        "ep_num": 1,
        "canonical_code": "3.5",
        "title": "Ilse's Notebook: Memoirs of a Scout Regiment Member",
        "mal_id": 18397,
        "mal_ep_num": 1,
        "stream_url": "https://archive.org/download/newb-subs-shingeki-no-kyojin-oad-05-0.5-b-2015-576p-dvd-x-265-aac-c-42-c-88-eb/%5BNewbSubs%5D%20Shingeki%20no%20Kyojin%20OAD%2001%203.5%202013%20%28576p%20DVD%20x265%20AAC%29%5B9ABDB92C%5D.mp4",
        "subtitle_path": "subtitles/OVAs/OVA01_Ilses_Notebook.en.srt"
    },
    {
        "id": "OVA02",
        "ep_num": 2,
        "canonical_code": "3.25",
        "title": "The Sudden Visitor: The Torturous Curse of Youth",
        "mal_id": 18397,
        "mal_ep_num": 2,
        "stream_url": "https://archive.org/download/newb-subs-shingeki-no-kyojin-oad-05-0.5-b-2015-576p-dvd-x-265-aac-c-42-c-88-eb/%5BNewbSubs%5D%20Shingeki%20no%20Kyojin%20OAD%2002%203.25%202014%20%28576p%20DVD%20x265%20AAC%29%5B74B064E9%5D.mp4",
        "subtitle_path": "subtitles/OVAs/OVA02_The_Sudden_Visitor.en.srt"
    },
    {
        "id": "OVA03",
        "ep_num": 3,
        "canonical_code": "3.75",
        "title": "Distress",
        "mal_id": 18397,
        "mal_ep_num": 3,
        "stream_url": "https://archive.org/download/newb-subs-shingeki-no-kyojin-oad-05-0.5-b-2015-576p-dvd-x-265-aac-c-42-c-88-eb/%5BNewbSubs%5D%20Shingeki%20no%20Kyojin%20OAD%2003%203.75%202014%20%28576p%20DVD%20x265%20AAC%29%5B21719207%5D.mp4",
        "subtitle_path": "subtitles/OVAs/OVA03_Distress.en.srt"
    },
    {
        "id": "OVA04",
        "ep_num": 4,
        "canonical_code": "0.5A",
        "title": "No Regrets: Part 1",
        "mal_id": 23755,
        "mal_ep_num": 1,
        "stream_url": "https://archive.org/download/2.-attack-on-titan-no-regrets-part-2_202511/No%20Regrets/1.%20Attack%20On%20Titan%20No%20Regrets%20Part%201.mp4",
        "subtitle_path": "subtitles/OVAs/OVA04_No_Regrets_Part_1.en.srt"
    },
    {
        "id": "OVA05",
        "ep_num": 5,
        "canonical_code": "0.5B",
        "title": "No Regrets: Part 2",
        "mal_id": 23755,
        "mal_ep_num": 2,
        "stream_url": "https://archive.org/download/2.-attack-on-titan-no-regrets-part-2_202511/No%20Regrets/2.%20Attack%20On%20Titan%20No%20Regrets%20Part%202.mp4",
        "subtitle_path": "subtitles/OVAs/OVA05_No_Regrets_Part_2.en.srt"
    },
    {
        "id": "OVA06",
        "ep_num": 6,
        "canonical_code": "16.5A",
        "title": "Lost Girls: Wall Sina, Goodbye - Part 1",
        "mal_id": 36106,
        "mal_ep_num": 1,
        "stream_url": "https://archive.org/download/newb-subs-shingeki-no-kyojin-oad-05-0.5-b-2015-576p-dvd-x-265-aac-c-42-c-88-eb/%5BNewbSubs%5D%20Shingeki%20no%20Kyojin%20OAD%2006%2016.5A%202017%20%28576p%20DVD%20x265%20AAC%29%5BC6301971%5D.mp4",
        "subtitle_path": "subtitles/OVAs/OVA06_Lost_Girls_Wall_Sina_Part_1.en.srt"
    },
    {
        "id": "OVA07",
        "ep_num": 7,
        "canonical_code": "16.5B",
        "title": "Lost Girls: Wall Sina, Goodbye - Part 2",
        "mal_id": 36106,
        "mal_ep_num": 2,
        "stream_url": "https://archive.org/download/newb-subs-shingeki-no-kyojin-oad-05-0.5-b-2015-576p-dvd-x-265-aac-c-42-c-88-eb/%5BNewbSubs%5D%20Shingeki%20no%20Kyojin%20OAD%2007%2016.5B%202018%20%28576p%20DVD%20x265%20AAC%29%5BB8351CAE%5D.mp4",
        "subtitle_path": "subtitles/OVAs/OVA07_Lost_Girls_Wall_Sina_Part_2.en.srt"
    },
    {
        "id": "OVA08",
        "ep_num": 8,
        "canonical_code": "16.5C",
        "title": "Lost Girls: Lost in the Cruel World",
        "mal_id": 36106,
        "mal_ep_num": 3,
        "stream_url": "https://archive.org/download/newb-subs-shingeki-no-kyojin-oad-05-0.5-b-2015-576p-dvd-x-265-aac-c-42-c-88-eb/%5BNewbSubs%5D%20Shingeki%20no%20Kyojin%20OAD%2008%202018%20%28576p%20DVD%20x265%20AAC%29%5BDC10E9A3%5D.mp4",
        "subtitle_path": "subtitles/OVAs/OVA08_Lost_Girls_Lost_in_the_Cruel_World.en.srt"
    }
]

for ova in ova_list:
    episodes.append({
        "id": ova["id"],
        "type": "ova",
        "season_num": 0,
        "season_title": "Official OVAs",
        "ep_num": ova["ep_num"],
        "canonical_code": ova["canonical_code"],
        "title": ova["title"],
        "mal_id": ova["mal_id"],
        "mal_ep_num": ova["mal_ep_num"],
        "filename": ova["stream_url"].split("/")[-1],
        "archive_path": ova["stream_url"],
        "stream_url": ova["stream_url"],
        "subtitle_path": ova["subtitle_path"],
        "timestamps": {
            "op_start": None,
            "op_end": None,
            "ed_start": 1307.0,
            "ed_end": 1400.0
        }
    })

# Save updated episodes.json
target_json = BASE_DIR / "episodes.json"
with open(target_json, "w", encoding="utf-8") as f:
    json.dump(episodes, f, indent=2)

print(f"Successfully assembled full catalog: {len(episodes)} total items in {target_json}")
