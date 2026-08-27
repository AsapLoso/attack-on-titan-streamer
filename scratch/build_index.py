import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EPISODES_FILE = BASE_DIR / "episodes.json"

with open(EPISODES_FILE, "r", encoding="utf-8") as f:
    eps_data = json.load(f)

eps_json = json.dumps(eps_data)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Attack on Titan - Stream Hub</title>
  <meta name="theme-color" content="#121214">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

  <style>
    :root {{
      --bg: #0f0f12;
      --card-bg: #18181f;
      --card-hover: #22222b;
      --accent: #e50914;
      --accent-hover: #b80710;
      --cyan: #00adb5;
      --green: #4ade80;
      --yellow: #f59e0b;
      --text: #f4f4f5;
      --muted: #a1a1aa;
      --border: #27272e;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      padding-bottom: 70px;
    }}
    header {{
      background-color: #16161c;
      border-bottom: 1px solid var(--border);
      padding: 12px 20px;
      position: sticky;
      top: 0;
      z-index: 50;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .logo {{
      display: flex;
      align-items: center;
      gap: 10px;
      user-select: none;
    }}
    .logo h1 {{
      font-size: 1.25rem;
      font-weight: 800;
      letter-spacing: 0.5px;
      color: var(--accent);
      text-transform: uppercase;
    }}
    .logo span {{
      font-size: 0.75rem;
      color: var(--green);
      background: rgba(74, 222, 128, 0.1);
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
    }}
    .header-right {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex: 1;
      justify-content: flex-end;
    }}
    .search-box {{
      position: relative;
      max-width: 280px;
      min-width: 160px;
      width: 100%;
    }}
    .search-box input {{
      width: 100%;
      background: #23232b;
      border: 1px solid var(--border);
      color: #fff;
      padding: 8px 12px 8px 34px;
      border-radius: 20px;
      font-size: 0.88rem;
      outline: none;
    }}
    .search-box input:focus {{ border-color: var(--accent); }}
    .search-box i {{
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--muted);
      font-size: 0.85rem;
    }}
    .header-resume-btn {{
      background: rgba(229, 9, 20, 0.15);
      border: 1px solid rgba(229, 9, 20, 0.4);
      color: #fff;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      display: none;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
      transition: background 0.2s;
    }}
    .header-resume-btn:hover {{ background: var(--accent); }}

    /* Player Container */
    #player-section {{
      display: none;
      background: #000;
      position: relative;
      width: 100%;
      max-width: 1060px;
      margin: 0 auto 20px;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0,0,0,0.85);
    }}
    .video-wrapper {{
      position: relative;
      width: 100%;
      padding-top: 56.25%; /* 16:9 Aspect Ratio */
      background: #000;
    }}
    .video-wrapper:fullscreen {{
      padding-top: 0;
      width: 100vw;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    video#main-video {{
      position: absolute;
      top: 0; left: 0;
      width: 100%; height: 100%;
      background: #000;
      outline: none;
    }}
    video#main-video::cue {{
      background: rgba(0, 0, 0, 0.78);
      color: #ffffff;
      font-weight: 700;
      font-size: clamp(1rem, 2vw, 1.4rem);
      line-height: 1.35;
      text-shadow: 0 0 4px #000, 0 0 8px #000;
    }}
    .video-wrapper:fullscreen video#main-video {{
      width: 100%;
      height: 100%;
      object-fit: contain;
    }}

    /* Floating Skip & Jump Buttons */
    .skip-btn {{
      position: absolute;
      bottom: 65px;
      right: 20px;
      background: rgba(229, 9, 20, 0.95);
      color: #fff;
      border: 2px solid rgba(255, 255, 255, 0.4);
      padding: 10px 18px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.92rem;
      cursor: pointer;
      display: none;
      align-items: center;
      gap: 8px;
      z-index: 35;
      box-shadow: 0 4px 15px rgba(0,0,0,0.7);
      animation: pulse 1.5s infinite;
      backdrop-filter: blur(4px);
    }}
    .skip-btn.ending {{
      background: rgba(0, 173, 181, 0.95);
    }}
    .skip-btn.resume-jump {{
      background: rgba(245, 158, 11, 0.95);
      right: auto;
      left: 20px;
    }}
    @keyframes pulse {{
      0% {{ transform: scale(1); }}
      50% {{ transform: scale(1.04); }}
      100% {{ transform: scale(1); }}
    }}

    /* Player Header / Details */
    .player-details {{
      background: #18181f;
      padding: 12px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
      border-top: 1px solid var(--border);
    }}
    .player-title {{
      font-weight: 700;
      font-size: 1.05rem;
      color: #fff;
    }}
    .player-meta {{
      font-size: 0.8rem;
      color: var(--muted);
      margin-top: 2px;
    }}
    .quick-controls {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .btn-skip-jump {{
      background: #23232b;
      border: 1px solid var(--border);
      color: #fff;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: background 0.2s;
    }}
    .btn-skip-jump:hover {{ background: #2f2f3a; }}
    .btn-skip-jump.intro {{ color: #ffca28; }}
    .btn-skip-jump.outro {{ color: var(--cyan); }}
    .btn-skip-jump.cc-btn.active {{
      background: rgba(229, 9, 20, 0.25);
      border-color: var(--accent);
      color: #ff4d4d;
    }}

    /* Resume Toast Popup (Netflix Style) */
    .resume-toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: rgba(24, 24, 31, 0.96);
      border: 1px solid #3f3f4e;
      border-left: 4px solid var(--accent);
      border-radius: 10px;
      padding: 14px 18px;
      display: none;
      align-items: center;
      gap: 14px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.85);
      z-index: 100;
      backdrop-filter: blur(8px);
      max-width: 400px;
    }}
    .resume-toast-info {{ flex: 1; }}
    .resume-toast-title {{
      font-size: 0.88rem;
      font-weight: 700;
      color: #fff;
      line-height: 1.2;
    }}
    .resume-toast-meta {{
      font-size: 0.75rem;
      color: var(--muted);
      margin-top: 3px;
    }}
    .resume-toast-btn {{
      background: var(--accent);
      color: #fff;
      border: none;
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
      transition: background 0.2s;
    }}
    .resume-toast-btn:hover {{ background: var(--accent-hover); }}
    .resume-toast-close {{
      background: transparent;
      border: none;
      color: var(--muted);
      font-size: 1rem;
      cursor: pointer;
      padding: 4px;
    }}

    /* Category Nav Tabs */
    .tabs-nav {{
      display: flex;
      gap: 8px;
      padding: 12px 20px;
      overflow-x: auto;
      scrollbar-width: none;
      background: #121216;
      border-bottom: 1px solid var(--border);
    }}
    .tabs-nav::-webkit-scrollbar {{ display: none; }}
    .tab-btn {{
      background: #1c1c24;
      border: 1px solid var(--border);
      color: var(--muted);
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      white-space: nowrap;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .tab-btn.active, .tab-btn:hover {{
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }}

    /* Episode Grid */
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
      width: 100%;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 14px;
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s, background-color 0.2s, border-color 0.2s;
      cursor: pointer;
    }}
    .card:hover {{
      background: var(--card-hover);
      border-color: #3f3f4e;
      transform: translateY(-2px);
    }}
    .card.playing {{
      border-color: var(--accent);
      background: #201a1c;
    }}
    .card-top {{
      display: flex;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 8px;
    }}
    .badge {{
      background: #2a2a35;
      color: var(--cyan);
      font-weight: 700;
      font-size: 0.75rem;
      padding: 3px 6px;
      border-radius: 4px;
      white-space: nowrap;
    }}
    .badge.movie {{ color: #f59e0b; }}
    .badge.ova {{ color: #a855f7; }}
    .card-title {{
      font-size: 0.95rem;
      font-weight: 600;
      color: #fff;
      line-height: 1.3;
    }}
    .card-meta {{
      font-size: 0.75rem;
      color: var(--muted);
      margin-top: 6px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .card-actions {{
      margin-top: 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .play-action {{
      background: var(--accent);
      color: #fff;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: none;
      cursor: pointer;
    }}
    .watched-tag {{
      color: var(--green);
      font-size: 0.75rem;
      font-weight: 600;
      display: none;
      align-items: center;
      gap: 4px;
    }}
    .watched-tag.show {{ display: flex; }}

    @media (max-width: 600px) {{
      header {{ padding: 10px 14px; }}
      .grid {{ grid-template-columns: 1fr; }}
      .container {{ padding: 12px; }}
      .skip-btn {{ bottom: 50px; right: 12px; padding: 8px 14px; font-size: 0.85rem; }}
      .skip-btn.resume-jump {{ left: 12px; }}
      .resume-toast {{ bottom: 16px; left: 16px; right: 16px; max-width: none; }}
    }}
  </style>
</head>
<body>

  <header>
    <div class="logo">
      <i class="fa-solid fa-shield-halved" style="color: var(--accent); font-size: 1.4rem;"></i>
      <div>
        <h1>Attack on Titan</h1>
      </div>
      <span>1080p Dub</span>
    </div>
    <div class="header-right">
      <button id="header-resume-btn" class="header-resume-btn" onclick="resumeLastPlayed()">
        <i class="fa-solid fa-play"></i> <span id="header-resume-text">Resume S01E01</span>
      </button>
      <div class="search-box">
        <i class="fa-solid fa-magnifying-glass"></i>
        <input type="text" id="search" placeholder="Search 97 episodes...">
      </div>
    </div>
  </header>

  <!-- Video Player Section -->
  <div id="player-section">
    <div class="video-wrapper" id="video-wrapper">
      <video id="main-video" controls playsinline preload="auto">
        <track id="sub-track" kind="subtitles" srclang="en" label="English" default>
      </video>

      <!-- Floating Jump to Saved Time Button -->
      <button id="jump-resume-btn" class="skip-btn resume-jump" onclick="jumpToSavedTime()">
        <i class="fa-solid fa-forward"></i> <span id="jump-resume-text">Jump to 14:20</span>
      </button>

      <!-- Floating Skip Buttons -->
      <button id="skip-btn" class="skip-btn" onclick="skipIntro()">
        <i class="fa-solid fa-forward"></i> Skip Opening (Tab)
      </button>

      <button id="skip-outro-btn" class="skip-btn ending" onclick="skipOutro()">
        <i class="fa-solid fa-forward-step"></i> Skip Ending
      </button>
    </div>

    <!-- Episode Details & Quick Jump Buttons -->
    <div class="player-details">
      <div>
        <div id="current-title" class="player-title">Episode Title</div>
        <div id="current-meta" class="player-meta">Season 1 • 1080p English Dub</div>
      </div>
      <div class="quick-controls">
        <button class="btn-skip-jump intro" onclick="skipIntro()"><i class="fa-solid fa-forward"></i> Jump Intro</button>
        <button class="btn-skip-jump outro" onclick="skipOutro()"><i class="fa-solid fa-forward-step"></i> Jump Outro</button>
        <button id="cc-toggle-btn" class="btn-skip-jump cc-btn active" onclick="toggleSubtitles()"><i class="fa-solid fa-closed-captioning"></i> CC</button>
        <button class="btn-skip-jump" onclick="toggleFullscreen()"><i class="fa-solid fa-expand"></i> Fullscreen (F)</button>
        <button class="btn-skip-jump" onclick="playNextEpisode()"><i class="fa-solid fa-step-forward"></i> Next</button>
        <label style="font-size:0.75rem; color:var(--muted); display:flex; align-items:center; gap:4px; margin-left:8px; cursor:pointer;">
          <input type="checkbox" id="auto-skip-chk"> Auto-Skip OP
        </label>
      </div>
    </div>
  </div>

  <!-- Category Filter Tabs -->
  <div class="tabs-nav">
    <button class="tab-btn active" onclick="filterCategory('All')">All (97)</button>
    <button class="tab-btn" onclick="filterCategory('1')">Season 1 (25)</button>
    <button class="tab-btn" onclick="filterCategory('2')">Season 2 (12)</button>
    <button class="tab-btn" onclick="filterCategory('3')">Season 3 (22)</button>
    <button class="tab-btn" onclick="filterCategory('4')">The Final Season (30)</button>
    <button class="tab-btn" onclick="filterCategory('OVA')">Official OVAs (8)</button>
  </div>

  <!-- Main Episode Grid -->
  <div class="container">
    <div id="episodes-grid" class="grid"></div>
  </div>

  <!-- Resume Popup Toast (Netflix Style) -->
  <div id="resume-toast" class="resume-toast">
    <div class="resume-toast-info">
      <div class="resume-toast-title" id="toast-title">Continue Watching?</div>
      <div class="resume-toast-meta" id="toast-meta">Episode details...</div>
    </div>
    <button class="resume-toast-btn" onclick="resumeLastPlayed()"><i class="fa-solid fa-play"></i> Resume</button>
    <button class="resume-toast-close" onclick="closeResumeToast()"><i class="fa-solid fa-xmark"></i></button>
  </div>

  <script>
    // Embedded catalog fallback for offline / local file:// support
    const EMBEDDED_EPISODES = {eps_json};

    let allEpisodes = EMBEDDED_EPISODES;
    let currentCategory = 'All';
    let currentEpisodeIndex = -1;
    let watchedHistory = JSON.parse(localStorage.getItem('aot_watched') || '[]');
    let lastPlayed = JSON.parse(localStorage.getItem('aot_last_played') || 'null');
    let toastHideTimeout = null;
    let pendingResumeTime = 0;

    let ccEnabled = true;

    const video = document.getElementById('main-video');
    const subTrack = document.getElementById('sub-track');
    const ccToggleBtn = document.getElementById('cc-toggle-btn');

    const skipBtn = document.getElementById('skip-btn');
    const skipOutroBtn = document.getElementById('skip-outro-btn');
    const jumpResumeBtn = document.getElementById('jump-resume-btn');
    const jumpResumeText = document.getElementById('jump-resume-text');

    const playerSection = document.getElementById('player-section');
    const currentTitle = document.getElementById('current-title');
    const currentMeta = document.getElementById('current-meta');
    const autoSkipChk = document.getElementById('auto-skip-chk');

    const resumeToast = document.getElementById('resume-toast');
    const toastTitle = document.getElementById('toast-title');
    const toastMeta = document.getElementById('toast-meta');
    const headerResumeBtn = document.getElementById('header-resume-btn');
    const headerResumeText = document.getElementById('header-resume-text');

    function formatTime(sec) {{
      if (isNaN(sec) || sec < 0) return "00:00";
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60);
      return `${{m < 10 ? '0' : ''}}${{m}}:${{s < 10 ? '0' : ''}}${{s}}`;
    }}

    function toggleSubtitles() {{
      ccEnabled = !ccEnabled;
      ccToggleBtn.classList.toggle('active', ccEnabled);
      if (subTrack && subTrack.track) {{
        subTrack.track.mode = ccEnabled ? "showing" : "disabled";
      }}
    }}

    // Initial render from embedded data immediately
    renderEpisodes();
    checkAndShowResumePrompt();

    // Dynamically sync latest episodes.json if running on web server
    if (window.location.protocol.startsWith('http')) {{
      fetch('episodes.json?v=' + Date.now())
        .then(res => res.json())
        .then(data => {{
          if (Array.isArray(data) && data.length > 0) {{
            allEpisodes = data;
            renderEpisodes();
            checkAndShowResumePrompt();
          }}
        }})
        .catch(err => {{
          console.log('Using embedded catalog fallback');
        }});
    }}

    function checkAndShowResumePrompt() {{
      if (lastPlayed && lastPlayed.id) {{
        const ep = allEpisodes.find(e => e.id === lastPlayed.id);
        if (ep) {{
          const timeStr = lastPlayed.time ? formatTime(lastPlayed.time) : "00:00";
          headerResumeText.textContent = `Resume ${{ep.id}}`;
          headerResumeBtn.style.display = 'inline-flex';

          toastTitle.textContent = `${{ep.id}}: ${{ep.title || ep.filename}}`;
          toastMeta.textContent = `Resume from ${{timeStr}}`;
          resumeToast.style.display = 'flex';

          toastHideTimeout = setTimeout(() => {{
            closeResumeToast();
          }}, 10000);
        }}
      }}
    }}

    function closeResumeToast() {{
      clearTimeout(toastHideTimeout);
      resumeToast.style.display = 'none';
    }}

    function resumeLastPlayed() {{
      closeResumeToast();
      if (lastPlayed && lastPlayed.id) {{
        playEpisode(lastPlayed.id, lastPlayed.time || 0);
      }} else if (allEpisodes.length > 0) {{
        playEpisode(allEpisodes[0].id, 0);
      }}
    }}

    function filterCategory(cat) {{
      currentCategory = cat;
      document.querySelectorAll('.tab-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.textContent.startsWith(cat === '1' ? 'Season 1' : cat === '2' ? 'Season 2' : cat === '3' ? 'Season 3' : cat === '4' ? 'The Final' : cat === 'OVA' ? 'Official' : 'All'));
      }});
      renderEpisodes();
    }}

    document.getElementById('search').addEventListener('input', (e) => {{
      renderEpisodes(e.target.value.toLowerCase().trim());
    }});

    function renderEpisodes(query = '') {{
      const grid = document.getElementById('episodes-grid');
      grid.innerHTML = '';

      const filtered = allEpisodes.filter(ep => {{
        if (currentCategory === '1' && ep.season_num !== 1) return false;
        if (currentCategory === '2' && ep.season_num !== 2) return false;
        if (currentCategory === '3' && ep.season_num !== 3) return false;
        if (currentCategory === '4' && ep.season_num !== 4) return false;
        if (currentCategory === 'OVA' && ep.type !== 'ova' && ep.season_num !== 0) return false;

        if (query) {{
          const matchTitle = (ep.title || '').toLowerCase().includes(query);
          const matchId = (ep.id || '').toLowerCase().includes(query);
          if (!matchTitle && !matchId) return false;
        }}
        return true;
      }});

      filtered.forEach((ep) => {{
        const isWatched = watchedHistory.includes(ep.id);
        const isCurrent = (currentEpisodeIndex !== -1 && allEpisodes[currentEpisodeIndex].id === ep.id);
        const card = document.createElement('div');
        card.className = `card ${{isCurrent ? 'playing' : ''}}`;
        card.onclick = () => playEpisode(ep.id);

        const badgeClass = ep.type === 'movie' ? 'badge movie' : ep.type === 'ova' ? 'badge ova' : 'badge';

        card.innerHTML = `
          <div>
            <div class="card-top">
              <span class="${{badgeClass}}">${{ep.id}}</span>
              <div class="card-title">${{ep.title || ep.filename}}</div>
            </div>
            <div class="card-meta">
              <span>${{ep.season_title || ''}}</span>
              <span>•</span>
              <span>1080p Dub</span>
              ${{ep.size_mb ? `<span>• ${{ep.size_mb}} MB</span>` : ''}}
            </div>
          </div>
          <div class="card-actions">
            <button class="play-action"><i class="fa-solid fa-play"></i> ${{isCurrent ? 'Playing' : 'Play'}}</button>
            <div class="watched-tag ${{isWatched ? 'show' : ''}}"><i class="fa-solid fa-check"></i> Watched</div>
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    function playEpisode(epId, startTime = 0) {{
      closeResumeToast();
      pendingResumeTime = (startTime > 10) ? startTime : 0;

      const epIndex = allEpisodes.findIndex(e => e.id === epId);
      if (epIndex === -1) return;

      currentEpisodeIndex = epIndex;
      const ep = allEpisodes[epIndex];

      if (!watchedHistory.includes(ep.id)) {{
        watchedHistory.push(ep.id);
        localStorage.setItem('aot_watched', JSON.stringify(watchedHistory));
      }}

      lastPlayed = {{ id: ep.id, title: ep.title || ep.filename, time: startTime, timestamp: Date.now() }};
      localStorage.setItem('aot_last_played', JSON.stringify(lastPlayed));
      headerResumeText.textContent = `Resume ${{ep.id}}`;
      headerResumeBtn.style.display = 'inline-flex';

      renderEpisodes();

      playerSection.style.display = 'block';
      playerSection.scrollIntoView({{ behavior: 'smooth' }});

      currentTitle.textContent = `${{ep.id}}: ${{ep.title || ep.filename}}`;
      currentMeta.textContent = `${{ep.season_title || ''}} • 1080p English Dub`;

      if (pendingResumeTime > 0) {{
        jumpResumeText.textContent = `Jump to ${{formatTime(pendingResumeTime)}}`;
        jumpResumeBtn.style.display = 'flex';
      }} else {{
        jumpResumeBtn.style.display = 'none';
      }}

      // Load Native Browser Subtitles
      const subFile = ep.subtitle_path || ep.vtt_path;
      if (subFile) {{
        const encodedSubUrl = encodeURI(subFile);
        fetch(encodedSubUrl)
          .then(res => {{
            if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
            return res.text();
          }})
          .then(rawText => {{
            const vttText = "WEBVTT\\n\\n" + rawText.replace(/\\r/g, '').replace(/(\\d{{2}}:\\d{{2}}:\\d{{2}}),(\\d{{3}})/g, "$1.$2");
            const blob = new Blob([vttText], {{ type: 'text/vtt;charset=utf-8' }});
            subTrack.src = URL.createObjectURL(blob);
            if (subTrack.track) subTrack.track.mode = ccEnabled ? "showing" : "disabled";
          }})
          .catch(err => {{
            subTrack.src = '';
          }});
      }} else {{
        subTrack.src = '';
      }}

      video.src = ep.stream_url;
      video.play().catch(e => console.log("Play started"));
    }}

    function jumpToSavedTime() {{
      if (pendingResumeTime > 0) {{
        video.currentTime = pendingResumeTime;
        pendingResumeTime = 0;
        jumpResumeBtn.style.display = 'none';
      }}
    }}

    function toggleFullscreen() {{
      const wrapper = document.getElementById('video-wrapper');
      if (!document.fullscreenElement) {{
        if (wrapper.requestFullscreen) {{
          wrapper.requestFullscreen();
        }} else if (video.webkitEnterFullscreen) {{
          video.webkitEnterFullscreen();
        }}
      }} else {{
        if (document.exitFullscreen) {{
          document.exitFullscreen();
        }}
      }}
    }}

    let lastSaveTime = 0;
    video.addEventListener('timeupdate', () => {{
      if (currentEpisodeIndex === -1) return;
      const ep = allEpisodes[currentEpisodeIndex];
      const ts = ep.timestamps || {{}};
      const cur = video.currentTime;

      if (pendingResumeTime > 0 && cur >= 2) {{
        jumpToSavedTime();
      }}

      if (cur > 15 && jumpResumeBtn.style.display !== 'none') {{
        jumpResumeBtn.style.display = 'none';
      }}

      const now = Date.now();
      if (now - lastSaveTime > 4000 && cur > 5) {{
        lastSaveTime = now;
        lastPlayed = {{ id: ep.id, title: ep.title || ep.filename, time: cur, timestamp: now }};
        localStorage.setItem('aot_last_played', JSON.stringify(lastPlayed));
      }}

      if (ts.op_start && ts.op_end && cur >= ts.op_start && cur < ts.op_end) {{
        if (autoSkipChk.checked) {{
          video.currentTime = ts.op_end;
          skipBtn.style.display = 'none';
        }} else {{
          skipBtn.style.display = 'flex';
          skipBtn.innerHTML = `<i class="fa-solid fa-forward"></i> Skip Opening (${{Math.ceil(ts.op_end - cur)}}s)`;
        }}
      }} else {{
        skipBtn.style.display = 'none';
      }}

      if (ts.ed_start && ts.ed_end && cur >= ts.ed_start && cur < ts.ed_end) {{
        skipOutroBtn.style.display = 'flex';
      }} else {{
        skipOutroBtn.style.display = 'none';
      }}
    }});

    function skipIntro() {{
      if (currentEpisodeIndex === -1) return;
      const ep = allEpisodes[currentEpisodeIndex];
      const ts = ep.timestamps || {{}};
      if (ts.op_end) {{
        video.currentTime = ts.op_end;
        skipBtn.style.display = 'none';
      }} else {{
        video.currentTime += 85;
      }}
    }}

    function skipOutro() {{
      if (currentEpisodeIndex === -1) return;
      const ep = allEpisodes[currentEpisodeIndex];
      const ts = ep.timestamps || {{}};
      if (ts.ed_end) {{
        video.currentTime = ts.ed_end;
      }} else {{
        playNextEpisode();
      }}
      skipOutroBtn.style.display = 'none';
    }}

    function playNextEpisode() {{
      if (currentEpisodeIndex !== -1 && currentEpisodeIndex + 1 < allEpisodes.length) {{
        playEpisode(allEpisodes[currentEpisodeIndex + 1].id);
      }}
    }}

    video.addEventListener('ended', () => {{
      playNextEpisode();
    }});

    document.addEventListener('keydown', (e) => {{
      if (document.activeElement === document.getElementById('search')) return;
      const key = e.key.toLowerCase();
      if (key === 'f') {{
        e.preventDefault();
        toggleFullscreen();
      }} else if (key === 'c') {{
        e.preventDefault();
        toggleSubtitles();
      }} else if (key === 'tab' || key === 's') {{
        e.preventDefault();
        skipIntro();
      }} else if (key === 'n') {{
        e.preventDefault();
        playNextEpisode();
      }}
    }});
  </script>
</body>
</html>
"""

output_path = BASE_DIR / "index.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Generated index.html successfully at:", output_path)
