# _FastAPI.py
# Exports the full HTML for the FastAPI index page.


def get_index_html() -> str:
    return r"""<!doctype html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plex ⇄ SIMKL Watchlist Sync</title>
<style>
  :root{
    --bg:#000; --panel:#0b0b0f; --panel2:#0e0e15; --muted:#9aa4b2; --fg:#f2f4f8;
    --accent:#7c5cff; --accent2:#19c37d; --danger:#ff4d4f; --border:#1a1a24; --glow:#7c5cff66; --glow2:#19c37d66;
    --grad1:linear-gradient(135deg,#7c5cff,#2da1ff);
    --grad2:linear-gradient(135deg,#19c37d,#36e0b7);
    --grad3:linear-gradient(135deg,#ff7ae0,#ffb86c);
    --brand-grad: linear-gradient(135deg,#2de2ff,#7c5cff,#ff7ae0);
  }
  *{box-sizing:border-box}
  body{
    margin:0;
    background:radial-gradient(1200px 600px at 20% -10%, #15152544, transparent), var(--bg);
    color:var(--fg);
    font:14px/1.5 ui-sans-serif,system-ui,Segoe UI,Roboto;
  }

  /* Header */
  header{
    position:sticky;top:0;z-index:10;
    background:linear-gradient(180deg,rgba(10,10,14,.85),rgba(10,10,14,.6),transparent);
    backdrop-filter:blur(6px);
    padding:14px 18px;border-bottom:1px solid var(--border);
    display:flex;gap:16px;align-items:center
  }
  .tabs{display:flex;gap:10px;margin-left:auto}
  .tab{
    position:relative;
    padding:10px 16px;border:1px solid var(--border);border-radius:12px;cursor:pointer;
    color:var(--muted);transition:.2s; background:#0b0b16;
    box-shadow:0 0 0px transparent;
    overflow:hidden;
  }
  .tab.active{color:var(--fg);border-color:#3d38ff;box-shadow:0 0 18px #3d38ff33}
  @keyframes neonPulse {
    0%   { box-shadow:0 0 10px #7c5cff33, inset 0 0 0 #0000 }
    50%  { box-shadow:0 0 18px #7c5cff66, inset 0 0 12px #7c5cff22 }
    100% { box-shadow:0 0 10px #7c5cff33, inset 0 0 0 #0000 }
  }
  .tab{ animation: neonPulse 3.2s ease-in-out infinite; }
  .tab:hover{ box-shadow:0 0 22px #7c5cff88 }
  .tab.active:hover{ box-shadow:0 0 28px #7c5cffaa }

  /* Branding */
  .brand{display:flex;align-items:center;gap:10px}
  .brand .logo{width:28px;height:28px;display:inline-block}
  .brand .name{
    font-size:18px;font-weight:800;letter-spacing:.2px;
    background: var(--brand-grad);
    -webkit-background-clip:text;background-clip:text;color:transparent;
    filter: drop-shadow(0 1px 6px rgba(124,92,255,.25));
    user-select:none
  }

  /* Layout */
  main{
    display:grid;
    grid-template-columns:1fr 440px;
    gap:16px;
    padding:16px;
    min-height:calc(100vh - 60px);
    align-items:start;
    align-content:start;
  }
  main.full{grid-template-columns:1fr}
  main.single{grid-template-columns:1fr}
  #ops-card{grid-column:1} #placeholder-card{grid-column:1} #log-panel{grid-column:2; align-self:start}

  /* Reuse carousel visuals on the Watchlist grid items */
  .wl-poster.poster { /* combineert grid en poster styles */ }
  .wl-poster .wl-ovr.ovr { /* alias: zelfde pill-styling als carrousel */ }
  .wl-poster .wl-cap.cap { /* alias: zelfde caption styling */ }
  .wl-poster .wl-hover.hover { /* alias: zelfde hover-overlay styling */ }

  /* Zorg dat Delete altijd klikbaar blijft */
  .wl-del { z-index: 5; position: absolute; }
   
  /* Cards */
  .card{
    background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--panel);
    border:1px solid var(--border);border-radius:20px;padding:16px;box-shadow:0 0 40px #000 inset
  }
  .title{font-size:12px;letter-spacing:.12em;color:var(--muted);text-transform:uppercase;margin-bottom:10px}
  .sub{color:var(--muted);margin-bottom:10px}
  .hidden{display:none}
  .btn{
    padding:11px 14px;border-radius:14px;border:1px solid var(--border);
    background:#121224;color:#fff;cursor:pointer;font-weight:650;
    transition:transform .05s ease, box-shadow .25s ease, background .25s ease, filter .25s ease;
  }
  .btn:hover{box-shadow:0 0 14px var(--glow)}
  .btn:active{transform:translateY(1px)}
  .btn.acc{background:var(--grad1)}
  .btn.danger{
    background:linear-gradient(135deg,#ff4d4f,#ff7a7a);
    border-color:#ff9a9a55;
    box-shadow:0 0 14px #ff4d4f55;
  }
  .btn:disabled{opacity:.55;cursor:not-allowed;box-shadow:none}
  .badges{display:flex;gap:8px;margin:0;flex-wrap:wrap}
  .badge{padding:6px 10px;border-radius:999px;font-weight:650;display:inline-flex;align-items:center;gap:8px;border:1px solid transparent}
  .ok{background:rgba(25,195,125,.12);color:#c8ffe6;border-color:rgba(25,195,125,.35);box-shadow:0 0 12px var(--glow2)}
  .no{background:rgba(255,77,79,.10);color:#ffd2d2;border-color:rgba(255,77,79,.35)}
  .dot{width:10px;height:10px;border-radius:50%}.dot.ok{background:var(--accent2)}.dot.no{background:var(--danger)}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  label{font-weight:650;color:var(--muted);font-size:12px}
  input,select{width:100%;padding:10px 12px;border-radius:12px;border:1px solid var(--border);background:#0a0a17;color:#e7e9f4}
  .sep{height:1px;background:linear-gradient(90deg,transparent,#30304a,transparent);margin:12px 0}

  .section{border:1px solid var(--border);border-radius:16px;background:var(--panel2);overflow:hidden;margin-bottom:12px}
  .section>.head{display:flex;align-items:center;gap:10px;padding:12px 14px;cursor:pointer}
  .section>.head:hover{background:#11111a}
  .chev{transition:transform .25s ease}.section.open .chev{transform:rotate(90deg)}
  .section>.body{display:grid;gap:12px;padding:0 14px;max-height:0;overflow:hidden;transition:max-height .35s ease, padding .35s ease}
  .section.open>.body{padding:12px 14px;max-height:650px}

  .ops-header{display:flex;align-items:center;gap:12px}
  .ops-header .badges{margin-left:auto}
  .sync-status{display:flex;align-items:center;gap:10px;margin:8px 0 4px}
  .sync-icon{width:14px;height:14px;border-radius:50%;box-shadow:0 0 12px #000 inset}
  .sync-ok{background:var(--accent2)} .sync-warn{background:#ffc400} .sync-bad{background:#ff4d4f}
  .chiprow{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
  .chip{border:1px solid var(--border);background:#0a0a17;padding:6px 10px;border-radius:999px;color:#e7e9f4}

  .action-row{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:10px;margin-bottom:0}
  .action-buttons{display:flex;gap:8px;flex-wrap:wrap}
  .stepper{display:flex;gap:12px;align-items:center;margin:0}
  .step{display:flex;align-items:center;gap:6px;color:var(--muted);font-size:12px}
  .tl-dot{width:10px;height:10px;border-radius:50%;background:#333}.tl-dot.on{background:#7c5cff;box-shadow:0 0 10px var(--glow)}
  .details{border:1px dashed #2a2a3a;border-radius:12px;padding:10px;margin-top:10px;background:#0a0a17}
  .log{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#05060b;border-radius:14px;border:1px solid var(--border);padding:12px;min-height:160px;max-height:50vh;overflow:auto;white-space:pre-wrap}

  .msg{border:1px solid transparent;border-radius:12px;padding:8px 12px;margin-top:8px;font-weight:650}
  .msg.ok{background:rgba(25,195,125,.12);border-color:rgba(25,195,125,.35);color:#c8ffe6}
  .msg.warn{background:rgba(255,196,0,.10);border-color:rgba(255,196,0,.35);color:#ffe28a}
  .muted{color:var(--muted)} code{padding:2px 6px;border:1px solid var(--border);border-radius:8px;background:#0a0a17}

  /* Footer buttons – consistent neon style */
  .footer{display:flex;gap:10px;align-items:center;margin-top:8px}
  .footer .btn{
    padding:12px 16px;
    border-radius:14px;
    border:1px solid var(--border);
    background:#121224;
    color:#fff;
    font-weight:650;
  }
  .footer .btn:first-child{
    background:linear-gradient(180deg,rgba(255,255,255,.02),transparent), var(--grad2);
    box-shadow:0 0 14px var(--glow2);
  }
  .footer .btn:nth-child(2){
    background:linear-gradient(180deg,rgba(255,255,255,.02),transparent), var(--grad3);
    box-shadow:0 0 14px #ff7ae044;
  }
  .footer .btn:hover{filter:brightness(1.07);box-shadow:0 0 22px #7c5cff66}
  .footer .btn:active{transform:translateY(1px)}
  #save_msg{margin-left:8px}

  
  /* ---- Watchlist grid (not a carousel) ---- */
  .wl-grid{
    --gap: 12px;
    display:grid;
    grid-template-columns: repeat(auto-fill, minmax(148px, 1fr));
    gap: var(--gap);
  }
  .wl-poster{
    position:relative;
    aspect-ratio: 2/3;
    border-radius:14px; overflow:hidden;
    background:#0a0a17; border:1px solid var(--border);
    transition: transform .15s ease, box-shadow .2s ease, opacity .35s ease, filter .35s ease;
  }
  .wl-poster:hover{ transform: translateY(-2px) scale(1.01); box-shadow:0 0 24px #7c5cff44; }
  .wl-poster img{ width:100%; height:100%; object-fit:cover; display:block }
  .wl-ovr{ position:absolute; top:8px; right:8px; display:flex; gap:6px }
  .wl-del{
    position:absolute; top:8px; left:8px;
    padding:4px 8px; border-radius:999px; font-size:11px; font-weight:800;
    background:rgba(0,0,0,.5); border:1px solid rgba(255,255,255,.12); backdrop-filter: blur(4px);
    cursor:pointer;
  }
  .wl-cap{ position:absolute; left:8px; right:8px; bottom:6px; font-size:12px; color:#dfe3ea; text-shadow:0 1px 2px #000 }
  .wl-hover{
    position:absolute; inset:auto 0 0 0; height:62%;
    background: linear-gradient(180deg,rgba(0,0,0,.1),rgba(0,0,0,.60) 20%, rgba(0,0,0,.85));
    color:#eaf0ff; padding:10px; transform: translateY(100%); opacity:0; transition:.25s ease;
    border-top:1px solid #ffffff22; backdrop-filter: blur(8px);
  }
  .wl-poster:hover .wl-hover{ transform: translateY(0); opacity:1; }
  .wl-removing{ opacity:0; transform: scale(.98); filter: blur(1px); }

  /* ---------- Poster carousel ---------- */
  .wall-msg{color:var(--muted);margin-bottom:10px}
  .wall-wrap{position:relative; overflow:hidden;}
  .row-scroll{
    --poster-gap: 12px;
    --poster-visible: 7;
    display:grid;
    grid-auto-flow: column;
    grid-auto-columns: calc((100% - (var(--poster-gap) * (var(--poster-visible) - 1))) / var(--poster-visible));
    gap: var(--poster-gap);
    overflow-x:auto; overflow-y:hidden;
    padding:6px 40px 6px 40px;
    scroll-snap-type: x mandatory;
    width:100%; max-width:100%;
  }
  @media (max-width:1400px){ .row-scroll{ --poster-visible:6; } }
  @media (max-width:1100px){ .row-scroll{ --poster-visible:5; } }
  @media (max-width:900px){  .row-scroll{ --poster-visible:4; } }
  @media (max-width:700px){  .row-scroll{ --poster-visible:3; } }
  @media (max-width:520px){  .row-scroll{ --poster-visible:2; } }

  .row-scroll::-webkit-scrollbar{height:10px}
  .row-scroll::-webkit-scrollbar-thumb{background:#2a2a3a;border-radius:8px}

  .poster{
    position:relative;
    aspect-ratio: 2 / 3;
    border-radius:14px; overflow:hidden; background:#0a0a17; border:1px solid var(--border);
    scroll-snap-align:start;
    box-shadow:0 0 0 transparent; transition:transform .15s ease, box-shadow .2s;
  }
  .poster:hover{ transform: translateY(-2px) scale(1.01); box-shadow:0 0 24px #7c5cff44; }
  .poster img{width:100%; height:100%; object-fit:cover; display:block}

  .ovr{position:absolute; top:8px; right:8px; display:flex; gap:6px}
  .pill{padding:4px 8px; border-radius:999px; font-size:11px; font-weight:700;
    background:rgba(0,0,0,.45); border:1px solid rgba(255,255,255,.08); backdrop-filter: blur(4px)}
  .p-syn{color:#c8ffe6; border-color:rgba(25,195,125,.35)} .p-px{color:#cfe2ff} .p-sk{color:#d0d9ff}

  .cap{position:absolute; left:8px; right:8px; bottom:6px; font-size:12px; color:#dfe3ea; text-shadow:0 1px 2px #000}

  .hover{
    position:absolute; inset:auto 0 0 0; height:62%;
    background:
      radial-gradient(800px 220px at 20% -40%, #7c5cff33, transparent 60%),
      radial-gradient(800px 220px at 80% -40%, #19c37d33, transparent 60%),
      linear-gradient(180deg,rgba(0,0,0,.1),rgba(0,0,0,.60) 20%, rgba(0,0,0,.85));
    color:#eaf0ff;
    padding:10px 10px 12px 10px;
    transform: translateY(100%); opacity:0; transition:.25s ease;
    border-top:1px solid #ffffff22; backdrop-filter: blur(8px);
  }
  .poster:hover .hover{ transform: translateY(0); opacity:1; }
  .hover .titleline{font-weight:800; font-size:12px; letter-spacing:.02em}
  .hover .meta{display:flex;gap:8px;margin:6px 0 8px 0;flex-wrap:wrap}
  .hover .chip{font-size:11px;font-weight:800;padding:3px 7px;border-radius:999px;background:#0b0b16aa;border:1px solid #ffffff2b}
  .chip.src{background:#0b1420aa;border-color:#4aa8ff66}
  .chip.time{background:#0e1b13aa;border-color:#19c37d66}
  .hover .desc{font-size:12px;line-height:1.35;color:#e9ecffcc;max-height:60px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical}

  .nav{position:absolute; top:50%; transform:translateY(-50%); width:36px; height:64px; border-radius:12px;
    border:1px solid var(--border); background:rgba(10,10,23,.6); color:#fff; font-size:24px; line-height:60px;
    text-align:center; cursor:pointer; user-select:none; display:flex; align-items:center; justify-content:center}
  .nav:hover{box-shadow:0 0 14px var(--glow)}
  .nav.prev{left:8px} .nav.next{right:8px}

  .edge{position:absolute; top:0; bottom:0; width:36px; pointer-events:none}
  .edge.left{left:0; background:linear-gradient(90deg,var(--panel) 0%, transparent 100%)}
  .edge.right{right:0; background:linear-gradient(270deg,var(--panel) 0%, transparent 100%)}
  .edge.hide{opacity:0}
  
  #ops-card { position: relative; }
  #conn-badges {
    position: absolute;
    top: 16px;
    right: 16px;
    display: flex;
    gap: 8px;
    margin: 0 !important;
    flex-wrap: wrap;
  }

  /* --- subtle glass shimmer on the main Sync button --- */
  #run.btn.acc { position: relative; overflow: hidden; }
  #run.btn.acc::after {
    content: "";
    position: absolute;
    top: -120%;
    left: -30%;
    width: 60%;
    height: 300%;
    transform: rotate(25deg);
    opacity: 0;
    background: linear-gradient( to right, rgba(255,255,255,0) 0%,
                                          rgba(255,255,255,0.18) 50%,
                                          rgba(255,255,255,0) 100% );
    transition: opacity .2s ease;
  }
  #run.btn.acc.glass::after { animation: shimmer 2.8s linear infinite; opacity: 1; }
  @keyframes shimmer { 0% { transform: translateX(-120%) rotate(25deg); } 100% { transform: translateX(220%) rotate(25deg); } }


  /* snellere shimmer wanneer loading */
  #run.btn.acc.glass::after { animation: shimmer 2.8s linear infinite; opacity: 1; }
  #run.btn.acc.loading.glass::after { animation-duration: 1.2s; }

  /* spinner in de knop */
  #run .spinner{
    display: none;
    width: 14px; height: 14px;
    margin-left: 10px;
    border: 2px solid rgba(255,255,255,.35);
    border-top-color: rgba(255,255,255,1);
    border-radius: 50%;
    animation: cw-spin 0.9s linear infinite;
  }
  #run.loading .spinner{ display:inline-block; }

  /* visuele cues bij loading */
  #run.loading{
    cursor: progress;
    filter: brightness(1.02);
  }
  #run.loading .label::after{
    content: "…";
    font-weight: 800;
  }

  @keyframes cw-spin{ to { transform: rotate(360deg); } }

  /* --- Watchlist: Delete pill in neon red --- */
  .wl-del{ 
    position:absolute; top:8px; left:8px; z-index:5; 
  }

  /* Hergebruik basis .pill styling en kleur 'm rood */
  .pill.p-del{
    color:#ffd8d8;
    border-color: rgba(255,77,79,.45);
    box-shadow: 0 0 14px rgba(255,77,79,.45);
  }

  /* Hover/active feedback zoals de rest van de UI */
  .pill.p-del:hover{
    filter: brightness(1.06);
    box-shadow: 0 0 18px rgba(255,77,79,.60);
  }
  .pill.p-del:active{
    transform: translateY(1px);
  }

  
</style>
</head><body>
<header>
  <div class="brand">
    <svg class="logo" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Plex ⇄ SIMKL Watchlist Sync">
      <defs><linearGradient id="cw-g" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#2de2ff"/><stop offset="0.5" stop-color="#7c5cff"/><stop offset="1" stop-color="#ff7ae0"/>
      </linearGradient></defs>
      <rect x="3" y="4" width="18" height="12" rx="2" ry="2" stroke="url(#cw-g)" stroke-width="1.7"/>
      <rect x="8" y="18" width="8" height="1.6" rx="0.8" fill="url(#cw-g)"/>
      <circle cx="8" cy="9" r="1" fill="url(#cw-g)"/>
      <circle cx="12" cy="11" r="1" fill="url(#cw-g)"/>
      <circle cx="16" cy="8" r="1" fill="url(#cw-g)"/>
      <path d="M8 9 L12 11 L16 8" stroke="url(#cw-g)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <span class="name">Plex ⇄ SIMKL Watchlist Sync</span>
  </div>

  <div class="tabs">
    <div id="tab-main" class="tab active" onclick="showTab('main')">Main</div>
    <div id="tab-watchlist" class="tab" onclick="showTab('watchlist')">Watchlist</div>
    <div id="tab-settings" class="tab" onclick="showTab('settings')">Settings</div>
  </div>
</header>

<main id="layout">
  <!-- MAIN: Synchronization -->
  <section id="ops-card" class="card">
    <div class="title">Synchronization</div>
    <div class="ops-header">
      <div class="badges" id="conn-badges" style="margin-left:auto">
        <span id="badge-plex" class="badge no"><span class="dot no"></span>Plex: Not connected</span>
        <span id="badge-simkl" class="badge no"><span class="dot no"></span>SIMKL: Not connected</span>
      </div>
    </div>

    <!-- Scheduler banner (compact, only visible when enabled) -->
    <div id="schedBanner" class="msg ok" style="display:none; width:auto; max-width:100%;">Scheduler is <b>running</b> • next run: <b id="schedNext">—</b></div>

    <div id="sync-card">
      <div class="sync-status">
        <div id="sync-icon" class="sync-icon sync-warn"></div>
        <div id="sync-status-text" class="sub">Idle — run a sync to see results</div>
      </div>

      <div class="chiprow">
        <div class="chip">Plex: <span id="chip-plex">–</span></div>
        <div class="chip">SIMKL: <span id="chip-simkl">–</span></div>
        <div class="chip">Duration: <span id="chip-dur">–</span></div>
        <div class="chip">Exit: <span id="chip-exit">–</span></div>
      </div>

      <div class="sep"></div>
      <div class="action-row">
        <div class="action-buttons">
          <button id="run" class="btn acc glass" onclick="runSync()"><span class="label">Synchronize</span><span class="spinner" aria-hidden="true"></span></button>
          <button class="btn" onclick="toggleDetails()">View details</button>
          <button class="btn" onclick="copySummary()">Copy summary</button>
          <button class="btn" onclick="downloadSummary()">Download report (JSON)</button>
        </div>
        <div class="stepper" aria-label="Sync progress">
          <div class="step"><div class="tl-dot" id="tl-start"></div><div class="muted">Start</div></div>
          <div class="step"><div class="tl-dot" id="tl-pre"></div><div class="muted">Pre-counts</div></div>
          <div class="step"><div class="tl-dot" id="tl-post"></div><div class="muted">Post</div></div>
          <div class="step"><div class="tl-dot" id="tl-done"></div><div class="muted">Done</div></div>
        </div>
      </div>

      <div id="details" class="details hidden">
        <div><b>Command:</b> <code id="det-cmd">–</code></div>
        <div><b>Version:</b> <code id="det-ver">–</code></div>
        <div><b>Started:</b> <span id="det-start">–</span></div>
        <div><b>Finished:</b> <span id="det-finish">–</span></div>
      </div>
    </div>
  </section>

  <!-- MAIN: Poster carousel -->
  <section id="placeholder-card" class="card hidden">
    <div class="title">Watchlist preview</div>
    <div class="wall-wrap">
      <div class="nav prev" onclick="scrollWall(-1)" aria-label="Previous">‹</div>
      <div class="nav next" onclick="scrollWall(1)" aria-label="Next">›</div>
      <div class="edge left" id="edgeL"></div>
      <div class="edge right" id="edgeR"></div>
      <div id="poster-row" class="row-scroll hidden"></div>
    </div>
    <div id="wall-msg" class="wall-msg">Loading…</div>
  </section>
  <!-- WATCHLIST (grid, not carousel) -->
  <section id="page-watchlist" class="card hidden">
    <div class="title">Watchlist</div>
    <div id="wl-msg" class="wall-msg">Loading…</div>
    <div id="wl-grid" class="wl-grid hidden"></div>
  </section>


  <!-- SETTINGS -->
  <section id="page-settings" class="card hidden">
    <div class="title">Settings</div>

    <div class="section" id="sec-sync">
      <div class="head" onclick="toggleSection('sec-sync')"><span class="chev">▶</span><strong>Sync Options</strong></div>
      <div class="body">
        <div class="grid2">
          <div><label>Mode</label><select id="mode"><option value="two-way">two-way</option><option value="mirror">mirror</option></select></div>
          <div><label>Source of truth (mirror only)</label><select id="source"><option value="plex">plex</option><option value="simkl">simkl</option></select></div>
          <div><label>Debug</label><select id="debug"><option value="false">off</option><option value="true">on</option></select></div>
        </div>
      </div>
    </div>

    <!-- SCHEDULING -->
    <div class="section" id="sec-scheduling">
      <div class="head" onclick="toggleSection('sec-scheduling')"><span class="chev">▶</span><strong>Scheduling</strong></div>
      <div class="body">
        <div class="grid2">
          <div><label>Enable</label>
            <select id="schEnabled"><option value="false">Disabled</option><option value="true">Enabled</option></select>
          </div>
          <div><label>Frequency</label>
            <select id="schMode">
              <option value="hourly">Every hour</option>
              <option value="every_n_hours">Every N hours</option>
              <option value="daily_time">Daily at…</option>
            </select>
          </div>
          <div><label>Every N hours</label><input id="schN" type="number" min="1" max="24" value="2"></div>
          <div><label>Time</label><input id="schTime" type="time" value="03:30"></div>
        </div>
        <div class="footer" style="margin-top:0">
          <button class="btn" onclick="saveScheduling()">Save scheduling</button>
          <span id="schStatus" class="msg ok hidden">Saved ✓</span>
        </div>
      </div>
    </div>

    <!-- TROUBLESHOOT -->
    <div class="section" id="sec-troubleshoot">
      <div class="head" onclick="toggleSection('sec-troubleshoot')"><span class="chev">▶</span><strong>Troubleshoot</strong></div>
      <div class="body">
        <div class="sub">Use these actions to fix common issues. They are safe but cannot be undone.</div>
        <div class="chiprow">
          <button class="btn danger" onclick="clearState()">Clear State</button>
          <button class="btn danger" onclick="clearCache()">Clear Cache</button>
        </div>
        <div id="tb_msg" class="msg ok hidden">Done ✓</div>
      </div>
    </div>

    <div class="section" id="sec-auth">
      <div class="head" onclick="toggleSection('sec-auth')"><span class="chev">▶</span><strong>Authentication</strong></div>
      <div class="body">
        <!-- PLEX -->
        <div class="section" id="sec-plex">
          <div class="head" onclick="toggleSection('sec-plex')"><span class="chev">▶</span><strong>Plex</strong></div>
          <div class="body">
            <div class="grid2">
              <div>
                <label>Current token</label>
                <div style="display:flex;gap:8px"><input id="plex_token" placeholder="empty = not set"><button class="btn" onclick="copyField('plex_token')">Copy</button></div>
              </div>
              <div>
                <label>PIN</label>
                <div style="display:flex;gap:8px"><input id="plex_pin" placeholder="request to fill" readonly><button class="btn" onclick="copyField('plex_pin')">Copy</button></div>
              </div>
            </div>
            <div style="display:flex;gap:8px"><button class="btn" onclick="requestPlexPin()">Request Token</button><div style="align-self:center;color:var(--muted)">Opens plex.tv/link (PIN copied to clipboard)</div></div>
            <div id="plex_msg" class="msg ok hidden">Successfully retrieved token</div>
            <div class="sep"></div>
          </div>
        </div>

        <!-- SIMKL -->
        <div class="section" id="sec-simkl">
          <div class="head" onclick="toggleSection('sec-simkl')"><span class="chev">▶</span><strong>SIMKL</strong></div>
          <div class="body">
            <div class="grid2">
              <div><label>Client ID</label><input id="simkl_client_id" placeholder="Your SIMKL client id" oninput="updateSimklButtonState()"></div>
              <div><label>Client Secret</label><input id="simkl_client_secret" placeholder="Your SIMKL client secret" oninput="updateSimklButtonState()"></div>
            </div>
            <div id="simkl_hint" class="msg warn hidden">
              You need a SIMKL API key. Create one at
              <a href="https://simkl.com/settings/developer/" target="_blank" rel="noopener">SIMKL Developer</a>.
              Set the Redirect URL to <code id="redirect_uri_preview"></code>.
              <button class="btn" style="margin-left:8px" onclick="copyRedirect()">Copy Redirect URL</button>
            </div>
            <div style="display:flex;gap:8px;margin-top:8px"><button id="simkl_start_btn" class="btn" onclick="startSimkl()" disabled>Start SIMKL Auth</button><div style="align-self:center;color:var(--muted)">Opens SIMKL authorize, callback to this webapp</div></div>
            <div class="grid2" style="margin-top:8px"><div><label>Access token</label><input id="simkl_access_token" readonly placeholder="empty = not set"></div></div>
            <div id="simkl_msg" class="msg ok hidden">Successfully retrieved token</div>
            <div class="sep"></div>
          </div>
        </div>

        <!-- TMDb -->
        <div class="section" id="sec-tmdb">
          <div class="head" onclick="toggleSection('sec-tmdb')"><span class="chev">▶</span><strong>TMDb</strong></div>
          <div class="body">
            <div class="grid2">
              <div style="grid-column:1 / -1">
                <label>API key</label>
                <input id="tmdb_api_key" placeholder="Your TMDb API key" oninput="updateTmdbHint()">
                <div id="tmdb_hint" class="msg warn hidden">
                  TMDb is optional but recommended to enrich posters & metadata in the preview.
                  Get an API key at
                  <a href="https://www.themoviedb.org/settings/api" target="_blank" rel="noopener">TMDb API settings</a>.
                </div>
                <div class="sub">This product uses the TMDb API but is not endorsed by TMDb.</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <div class="footer">
      <button class="btn" onclick="saveSettings()">Save</button>
      <button class="btn" onclick="showTab('main')">Exit</button>
      <span id="save_msg" class="msg ok hidden">Settings saved ✓</span>
    </div>
  </section>

  <aside id="log-panel" class="card hidden">
    <div class="title">Raw log (Debug)</div>
    <div id="log" class="log"></div>
  </aside>
</main>

<script>
  let busy=false, esLog=null, esSum=null, plexPoll=null, simklPoll=null, appDebug=false, currentSummary=null;
  let wallLoaded=false, _lastSyncEpoch=null;

  async function showTab(n){
    const pageSettings = document.getElementById('page-settings');
    const pageWatchlist = document.getElementById('page-watchlist');
    const logPanel = document.getElementById('log-panel');
    const layout = document.getElementById('layout');

    document.getElementById('tab-main').classList.toggle('active', n==='main');
    document.getElementById('tab-watchlist').classList.toggle('active', n==='watchlist');
    document.getElementById('tab-settings').classList.toggle('active', n==='settings');

    document.getElementById('ops-card').classList.toggle('hidden', n!=='main');
    document.getElementById('placeholder-card').classList.toggle('hidden', n!=='main');
    pageWatchlist.classList.toggle('hidden', n!=='watchlist');
    pageSettings.classList.toggle('hidden', n!=='settings');

    if(n==='main'){
      layout.classList.remove('single');
      refreshStatus();
      layout.classList.toggle('full', !appDebug);
      if(!esSum){ openSummaryStream(); }
      await updatePreviewVisibility();   // i.p.v. loadWall()
      refreshSchedulingBanner();
    } else if(n==='watchlist'){
      layout.classList.add('single'); layout.classList.remove('full');
      logPanel.classList.add('hidden');
      loadWatchlist();
    } else {
      layout.classList.add('single'); layout.classList.remove('full');
      logPanel.classList.add('hidden');
      loadConfig(); updateSimklButtonState(); loadScheduling(); updateTmdbHint();
    }
  }

  function toggleSection(id){ document.getElementById(id).classList.toggle('open'); }
  function setBusy(v){
  busy = v;
  recomputeRunDisabled();
}


// Global UI snapshot
window._ui = { status: null, summary: null };

// The only place that decides whether the Run button is disabled
function recomputeRunDisabled() {
  const btn = document.getElementById('run');
  if (!btn) return;

  const busyNow = !!window.busy;
  const canRun = !(window._ui?.status) ? true : !!window._ui.status.can_run;
  const running = !!(window._ui?.summary && window._ui.summary.running);

  btn.disabled = busyNow || running || !canRun;
}
  
//FIX ... I HOPE THIS WORKS
  async function runSync(){
  if (busy) return;

  const btn = document.getElementById('run');
  setBusy(true);
  try { btn?.classList.add('glass'); } catch(_){}

  try{
    // Belangrijk: géén saveSettings() hier — sync moet los staan van UI-settings
    const resp = await fetch('/api/run', { method:'POST' });
    const j = await resp.json().catch(()=>null);

    if (!resp.ok || !j || j.ok !== true){
      // UI laten zien dat starten niet lukte
      setSyncHeader('sync-bad', `Failed to start${j?.error ? ` – ${j.error}` : ''}`);
    } else {
      // Zorg dat we running/finished via SSE oppikken
      if (!esSum) { openSummaryStream(); }
    }
  } catch (e){
    setSyncHeader('sync-bad', 'Failed to reach server');
  } finally {
    // Busy direct vrijgeven; disabled state wordt door SSE/summary geregeld
    setBusy(false);
    if (typeof recomputeRunDisabled === 'function') recomputeRunDisabled();
    // Status even verversen (kan can_run wijzigen)
    refreshStatus();
  }
}

function logHTML(t){ const el=document.getElementById('log'); el.innerHTML += t + "<br>"; el.scrollTop = el.scrollHeight; }

  function setPlexSuccess(show){ document.getElementById('plex_msg').classList.toggle('hidden', !show); }
  function setSimklSuccess(show){ document.getElementById('simkl_msg').classList.toggle('hidden', !show); }
  async function copyField(id){ try{ await navigator.clipboard.writeText(document.getElementById(id).value||''); }catch(_){} }
  function computeRedirectURI(){ return window.location.origin + '/callback'; }
  async function copyRedirect(){ try{ await navigator.clipboard.writeText(computeRedirectURI()); }catch(_){} }
  function isPlaceholder(v, ph){ return (v||'').trim().toUpperCase() === ph.toUpperCase(); }

  function setTimeline(tl){ ['start','pre','post','done'].forEach(k=>{ document.getElementById('tl-'+k).classList.toggle('on', !!(tl && tl[k])); }); }

  function setSyncHeader(status, msg){
    const icon = document.getElementById('sync-icon');
    icon.classList.remove('sync-ok','sync-warn','sync-bad'); icon.classList.add(status);
    document.getElementById('sync-status-text').textContent = msg;
  }

  function renderSummary(sum){
  currentSummary = sum;

  // <-- NIEUW: snapshot voor centrale disabled-logica
  window._ui = window._ui || {};
  window._ui.summary = sum;

  const pp = sum.plex_post ?? sum.plex_pre;
  const sp = sum.simkl_post ?? sum.simkl_pre;
  document.getElementById('chip-plex').textContent = (pp ?? '–');
  document.getElementById('chip-simkl').textContent = (sp ?? '–');
  document.getElementById('chip-dur').textContent = sum.duration_sec != null ? (sum.duration_sec + 's') : '–';
  document.getElementById('chip-exit').textContent = sum.exit_code != null ? String(sum.exit_code) : '–';

  if (sum.running){
    setSyncHeader('sync-warn', 'Running…');
  } else if (sum.exit_code === 0){
    setSyncHeader('sync-ok', (sum.result||'').toUpperCase()==='EQUAL' ? 'In sync ✅' : 'Synced ✅');
  } else if (sum.exit_code != null){
    setSyncHeader('sync-bad', 'Attention needed ⚠️');
  } else {
    setSyncHeader('sync-warn', 'Idle — run a sync to see results');
  }

  document.getElementById('det-cmd').textContent = sum.cmd || '–';
  document.getElementById('det-ver').textContent = sum.version || '–';
  document.getElementById('det-start').textContent = sum.started_at || '–';
  document.getElementById('det-finish').textContent = sum.finished_at || '–';
  setTimeline(sum.timeline || {});

  // <-- NIEUW: knop-UI consistent houden
  const btn = document.getElementById('run');
  if (btn){
    if (sum.running) btn.classList.add('glass');
    else btn.classList.remove('glass');
  }
  // disabled-toestand op 1 plek bepalen
  if (typeof recomputeRunDisabled === 'function') recomputeRunDisabled();
}


  function openSummaryStream(){
    esSum = new EventSource('/api/run/summary/stream');
    esSum.onmessage = (ev)=>{ try{ renderSummary(JSON.parse(ev.data)); }catch(_){} };
    fetch('/api/run/summary').then(r=>r.json()).then(renderSummary).catch(()=>{});
  }

  function toggleDetails(){ document.getElementById('details').classList.toggle('hidden'); }

  async function copySummary(){
    if(!currentSummary) return;
    const s = currentSummary; const lines = [];
    lines.push(`Plex ⇄ SIMKL Watchlist Sync ${s.version || ''}`.trim());
    if(s.started_at) lines.push(`Start:   ${s.started_at}`);
    if(s.finished_at) lines.push(`Finish:  ${s.finished_at}`);
    if(s.cmd) lines.push(`Cmd:     ${s.cmd}`);
    if(s.plex_pre != null && s.simkl_pre != null) lines.push(`Pre:     Plex=${s.plex_pre} vs SIMKL=${s.simkl_pre}`);
    if(s.plex_post != null && s.simkl_post != null) lines.push(`Post:    Plex=${s.plex_post} vs SIMKL=${s.simkl_post} -> ${s.result || 'UNKNOWN'}`);
    if(s.duration_sec != null) lines.push(`Duration: ${s.duration_sec}s`);
    if(s.exit_code != null) lines.push(`Exit:     ${s.exit_code}`);
    try{ await navigator.clipboard.writeText(lines.join('\n')); }catch(_){}
  }
  function downloadSummary(){ window.open('/api/run/summary/file', '_blank'); }

  async function refreshStatus(){
    const r = await fetch('/api/status').then(r=>r.json());
    appDebug = !!r.debug;
    const pb = document.getElementById('badge-plex'); const sb = document.getElementById('badge-simkl');
    pb.className = 'badge ' + (r.plex_connected?'ok':'no');
    pb.innerHTML = `<span class="dot ${r.plex_connected?'ok':'no'}"></span>Plex: ${r.plex_connected?'Connected':'Not connected'}`;
    sb.className = 'badge ' + (r.simkl_connected?'ok':'no');
    sb.innerHTML = `<span class="dot ${r.simkl_connected?'ok':'no'}"></span>SIMKL: ${r.simkl_connected?'Connected':'Not connected'}`;
    window._ui.status = {can_run: !!r.can_run,plex_connected: !!r.plex_connected,simkl_connected: !!r.simkl_connected};

    recomputeRunDisabled();

    const onMain = !document.getElementById('ops-card').classList.contains('hidden');
    const logPanel = document.getElementById('log-panel'); const layout = document.getElementById('layout');
    logPanel.classList.toggle('hidden', !(appDebug && onMain)); layout.classList.toggle('full', onMain && !appDebug);
  }

  async function loadConfig(){
    const cfg = await fetch('/api/config').then(r=>r.json());
    document.getElementById('mode').value = cfg.sync?.bidirectional?.mode || 'two-way';
    document.getElementById('source').value = cfg.sync?.bidirectional?.source_of_truth || 'plex';
    document.getElementById('debug').value = String(cfg.runtime?.debug || false);
    document.getElementById('plex_token').value = cfg.plex?.account_token || '';
    document.getElementById('simkl_client_id').value = cfg.simkl?.client_id || '';
    document.getElementById('simkl_client_secret').value = cfg.simkl?.client_secret || '';
    document.getElementById('simkl_access_token').value = cfg.simkl?.access_token || '';
    document.getElementById('tmdb_api_key').value = cfg.tmdb?.api_key || '';
  }

  async function saveSettings(){
  // 1) Serverconfig ophalen + deep clone
  const serverCfg = await fetch('/api/config').then(r=>r.json()).catch(()=>({}));
  const cfg = (typeof structuredClone === 'function')
    ? structuredClone(serverCfg)
    : JSON.parse(JSON.stringify(serverCfg || {}));

  // --- SYNC ---
  cfg.sync = cfg.sync || {};
  cfg.sync.bidirectional = cfg.sync.bidirectional || {};

  // Alleen UI-velden zetten
  const uiMode   = document.getElementById('mode').value;
  const uiSource = document.getElementById('source').value;
  cfg.sync.bidirectional.mode = uiMode;
  cfg.sync.bidirectional.source_of_truth = uiSource;
  // Laat overige flags ongemoeid (enable_add/remove/verify_after_write/bidirectional.enabled)

  // --- RUNTIME ---
  cfg.runtime = cfg.runtime || {};
  cfg.runtime.debug = (document.getElementById('debug').value === 'true');

  // --- PLEX ---
  cfg.plex = cfg.plex || {};
  const uiPlexToken = (document.getElementById('plex_token').value || '').trim();
  if (uiPlexToken) cfg.plex.account_token = uiPlexToken;  // alleen overschrijven als niet leeg

  // --- SIMKL ---
  cfg.simkl = cfg.simkl || {};
  const uiCid = (document.getElementById('simkl_client_id').value || '').trim();
  const uiSec = (document.getElementById('simkl_client_secret').value || '').trim();
  if (uiCid) cfg.simkl.client_id = uiCid;
  if (uiSec) cfg.simkl.client_secret = uiSec;
  // Access token niet hier aanpassen

  // --- TMDb ---
  cfg.tmdb = cfg.tmdb || {};
  const uiTmdb = (document.getElementById('tmdb_api_key').value || '').trim();
  if (uiTmdb) cfg.tmdb.api_key = uiTmdb;   // alleen als ingevuld (leeg = niet wissen)

  // 2) Wegschrijven
  await fetch('/api/config', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(cfg)
  });

  // 3) UI refreshes
  updateSimklButtonState();
  updateTmdbHint();
  await refreshStatus();
  await updateWatchlistTabVisibility?.();  // tab tonen/verbergen o.b.v. TMDb key

  // 4) Alleen op Main de preview beheren/laden
  const onMain = !document.getElementById('ops-card').classList.contains('hidden');
  if (onMain) {
    await updatePreviewVisibility();       // laat deze zelf beslissen of 'ie moet laden
  } else {
    // Zit je op Settings? Zorg dat de preview verborgen blijft.
    document.getElementById('placeholder-card')?.classList.add('hidden');
    // (en laat wallLoaded zoals 'ie staat; updatePreviewVisibility() doet de juiste reset)
  }

  // 5) Save-melding
  const m = document.getElementById('save_msg');
  m.classList.remove('hidden');
  setTimeout(()=>m.classList.add('hidden'), 1600);
}

  // ---- Scheduling UI ----
  async function loadScheduling(){
    try{
      const s = await fetch('/api/scheduling').then(r=>r.json());
      document.getElementById('schEnabled').value = String(!!s.enabled);
      document.getElementById('schMode').value = s.mode || 'hourly';
      document.getElementById('schN').value = (s.every_n_hours != null ? s.every_n_hours : 2);
      document.getElementById('schTime').value = s.daily_time || '03:30';
    }catch(_){}
    refreshSchedulingBanner();
  }

  async function saveScheduling(){
    const payload = {
      enabled: document.getElementById('schEnabled').value === 'true',
      mode: document.getElementById('schMode').value,
      every_n_hours: parseInt(document.getElementById('schN').value || '2', 10),
      daily_time: document.getElementById('schTime').value || '03:30'
    };
    const r = await fetch('/api/scheduling', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    const j = await r.json().catch(()=>({}));
    const m = document.getElementById('schStatus'); m.classList.remove('hidden'); m.textContent = j.ok ? 'Saved ✓' : 'Error';
    setTimeout(()=>m.classList.add('hidden'), 1500);
    refreshSchedulingBanner();
  }

  function refreshSchedulingBanner(){
    fetch('/api/scheduling/status').then(r=>r.json()).then(j=>{
      const b = document.getElementById('schedBanner');
      if(!b) return;
      if(j && j.config && j.config.enabled){
        b.style.display = 'inline-block';
        const nextRun = (j.next_run_at ? new Date(j.next_run_at*1000).toLocaleString() : '—');
        b.querySelector('#schedNext')?.replaceWith((()=>{ const x=document.createElement('b'); x.id='schedNext'; x.textContent=nextRun; return x; })());
      }else{
        b.style.display = 'none';
      }
    }).catch(()=>{
      const b = document.getElementById('schedBanner');
      if(b) b.style.display = 'none';
    });
  }

  // ---- Troubleshoot actions ----
  async function clearState(){
    const btnText = "Clear State";
    try{
      const r = await fetch('/api/troubleshoot/reset-state', {method:'POST'});
      const j = await r.json();
      const m = document.getElementById('tb_msg');
      m.classList.remove('hidden'); m.textContent = j.ok ? (btnText + ' – started ✓') : (btnText + ' – failed');
      setTimeout(()=>m.classList.add('hidden'), 1600);
    }catch(_){}
  }
  async function clearCache(){
    const btnText = "Clear Cache";
    try{
      const r = await fetch('/api/troubleshoot/clear-cache', {method:'POST'});
      const j = await r.json();
      const m = document.getElementById('tb_msg');
      m.classList.remove('hidden'); m.textContent = j.ok ? (btnText + ' – done ✓') : (btnText + ' – failed');
      setTimeout(()=>m.classList.add('hidden'), 1600);
    }catch(_){}
  }

  // ---- Hints / Validation ----
  async function updateTmdbHint(){
    const v = (document.getElementById('tmdb_api_key').value || '').trim();
    const hint = document.getElementById('tmdb_hint');
    hint.classList.toggle('hidden', !!v);
  }

  // PLEX
  async function requestPlexPin(){
    setPlexSuccess(false);
    const r = await fetch('/api/plex/pin/new', {method:'POST'}); const j = await r.json();
    if(!j.ok){ return; }
    document.getElementById('plex_pin').value = j.code;
    try{ await navigator.clipboard.writeText(j.code); }catch(_){}
    window.open('https://plex.tv/link', '_blank');
    if(plexPoll) { clearInterval(plexPoll); }
    let ticks = 0;
    plexPoll = setInterval(async ()=>{
      ticks++;
      const cfg = await fetch('/api/config').then(r=>r.json()).catch(()=>null);
      const tok = cfg?.plex?.account_token || '';
      if(tok){
        document.getElementById('plex_token').value = tok; setPlexSuccess(true); await refreshStatus(); clearInterval(plexPoll);
      }
      if(ticks > 360){ clearInterval(plexPoll); }
    }, 1000);
  }

  // SIMKL
  async function updateSimklButtonState(){
    const cid = (document.getElementById('simkl_client_id').value || '').trim();
    const sec = (document.getElementById('simkl_client_secret').value || '').trim();
    const badCid = (!cid) || isPlaceholder(cid, 'YOUR_SIMKL_CLIENT_ID');
    const badSec = (!sec) || isPlaceholder(sec, 'YOUR_SIMKL_CLIENT_SECRET');
    const btn = document.getElementById('simkl_start_btn'); const hint = document.getElementById('simkl_hint');
    document.getElementById('redirect_uri_preview').textContent = computeRedirectURI();
    const ok = !(badCid || badSec); btn.disabled = !ok; hint.classList.toggle('hidden', ok);
  }

  async function startSimkl(){
    setSimklSuccess(false); await saveSettings();
    const origin = window.location.origin;
    const r = await fetch('/api/simkl/authorize', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({origin})});
    const j = await r.json(); if(!j.ok){ return; }
    window.open(j.authorize_url, '_blank');
    if(simklPoll) { clearInterval(simklPoll); }
    let ticks = 0;
    simklPoll = setInterval(async ()=>{
      ticks++;
      const cfg = await fetch('/api/config').then(r=>r.json()).catch(()=>null);
      const tok = cfg?.simkl?.access_token || '';
      if(tok){
        document.getElementById('simkl_access_token').value = tok; setSimklSuccess(true); await refreshStatus(); clearInterval(simklPoll);
      }
      if(ticks > 600){ clearInterval(simklPoll); }
    }, 1000);
  }

  // ---- Carousel helpers ----
  function updateEdges(){
    const row = document.getElementById('poster-row');
    const L = document.getElementById('edgeL'), R = document.getElementById('edgeR');
    const max = row.scrollWidth - row.clientWidth - 1;
    L.classList.toggle('hide', row.scrollLeft <= 0);
    R.classList.toggle('hide', row.scrollLeft >= max);
  }
  function scrollWall(dir){
    const row = document.getElementById('poster-row');
    const step = row.clientWidth;
    row.scrollBy({ left: dir * step, behavior: 'smooth' });
    setTimeout(updateEdges, 350);
  }
  function initWallInteractions(){
    const row = document.getElementById('poster-row');
    row.addEventListener('scroll', updateEdges);
    row.addEventListener('wheel', (e)=>{
      if(Math.abs(e.deltaY) > Math.abs(e.deltaX)){
        e.preventDefault(); row.scrollBy({left:e.deltaY, behavior:'auto'});
      }
    }, {passive:false});
    updateEdges();
  }

  function relTimeFromEpoch(epoch){
    if(!epoch) return '';
    const secs = Math.max(1, Math.floor(Date.now()/1000 - epoch));
    const units = [["y",31536000],["mo",2592000],["d",86400],["h",3600],["m",60],["s",1]];
    for(const [label,span] of units){
      if(secs >= span) return Math.floor(secs/span) + label + " ago";
    }
    return "just now";
  }

  // Poster wall (build)
  async function loadWall(){
    const card = document.getElementById('placeholder-card');
    const msg = document.getElementById('wall-msg');
    const row = document.getElementById('poster-row');
    msg.textContent = 'Loading…'; row.innerHTML = ''; row.classList.add('hidden'); card.classList.remove('hidden');

    try{
      const data = await fetch('/api/state/wall').then(r=>r.json());
      if(data.missing_tmdb_key){ card.classList.add('hidden'); return; }
      if(!data.ok){ msg.textContent = data.error || 'No state data found.'; return; }
      const items = data.items || [];
      _lastSyncEpoch = data.last_sync_epoch || null;
      if(items.length === 0){ msg.textContent = 'No items to show yet.'; return; }
      msg.classList.add('hidden'); row.classList.remove('hidden');

      for(const it of items){
        if(!it.tmdb) continue;

        const a = document.createElement('a'); a.className = 'poster';
        a.href = `https://www.themoviedb.org/${it.type}/${it.tmdb}`; a.target = '_blank'; a.rel='noopener';
        a.dataset.type = it.type; a.dataset.tmdb = String(it.tmdb); a.dataset.source = it.status;

        const img = document.createElement('img');
        img.loading='lazy'; img.alt = `${it.title||''} (${it.year||''})`;
        img.src = `/art/tmdb/${it.type}/${it.tmdb}?size=w342`;
        a.appendChild(img);

        const ovr = document.createElement('div'); ovr.className='ovr';
        const pill = document.createElement('div'); pill.className = 'pill ' + (it.status==='both'?'p-syn':(it.status==='plex_only'?'p-px':'p-sk'));
        pill.textContent = (it.status==='both'?'SYNCED':(it.status==='plex_only'?'PLEX':'SIMKL'));
        ovr.appendChild(pill); a.appendChild(ovr);

        const cap = document.createElement('div'); cap.className='cap';
        cap.textContent = `${it.title||''} ${it.year?'· '+it.year:''}`;
        a.appendChild(cap);

        const hover = document.createElement('div'); hover.className='hover';
        hover.innerHTML = `
          <div class="titleline">${it.title || ''}</div>
          <div class="meta">
            <div class="chip src">${it.status==='both'?'Source: Synced':(it.status==='plex_only'?'Source: Plex':'Source: SIMKL')}</div>
            <div class="chip time" id="time-${it.type}-${it.tmdb}">${_lastSyncEpoch?('updated ' + relTimeFromEpoch(_lastSyncEpoch)) : ''}</div>
          </div>
          <div class="desc" id="desc-${it.type}-${it.tmdb}">Fetching description…</div>
        `;
        a.appendChild(hover);

        a.addEventListener('mouseenter', async ()=>{
          const descEl = document.getElementById(`desc-${it.type}-${it.tmdb}`);
          if(!descEl || descEl.dataset.loaded) return;
          try{
            const meta = await fetch(`/api/tmdb/meta/${it.type}/${it.tmdb}`).then(r=>r.json());
            descEl.textContent = meta?.overview || '—';
            descEl.dataset.loaded = '1';
          }catch(_){
            descEl.textContent = '—';
            descEl.dataset.loaded = '1';
          }
        }, {passive:true});

        row.appendChild(a);
      }
      initWallInteractions();
    }catch(e){
      msg.textContent = 'Failed to load preview.';
    }
  }

  // ---- Watchlist helpers ----
  function artUrl(item, size){
    const typ = (item.type === 'tv' || item.type === 'show') ? 'tv' : 'movie';
    const tmdb = item.tmdb;
    if(!tmdb) return null;
    return `/art/tmdb/${typ}/${tmdb}?size=${encodeURIComponent(size || 'w342')}`;
  }

  function relTimeFromEpoch(epoch){
    if(!epoch) return '';
    const secs = Math.max(1, Math.floor(Date.now()/1000 - epoch));
    const units = [["y",31536000],["mo",2592000],["d",86400],["h",3600],["m",60],["s",1]];
    for(const [label,span] of units){ if(secs >= span) return Math.floor(secs/span) + label + " ago"; }
    return "just now";
  }

  async function loadWatchlist(){
    const grid = document.getElementById('wl-grid');
    const msg  = document.getElementById('wl-msg');
    grid.innerHTML = ''; grid.classList.add('hidden'); msg.textContent = 'Loading…'; msg.classList.remove('hidden');

    try{
      const data = await fetch('/api/watchlist').then(r=>r.json());
      if(data.missing_tmdb_key){ msg.textContent = 'Set a TMDb API key to see posters.'; return; }
      if(!data.ok){ msg.textContent = data.error || 'No state data found.'; return; }
      const items = data.items || [];
      if(items.length === 0){ msg.textContent = 'No items on your watchlist yet.'; return; }

      msg.classList.add('hidden'); grid.classList.remove('hidden');

      for(const it of items){
        const url = artUrl(it, 'w342');

        // container krijgt zowel wl- als poster-classes => hergebruik carrousel CSS
        const node = document.createElement('div');
        node.className = 'wl-poster poster';
        node.dataset.key = it.key;
        node.dataset.type = it.type === 'tv' || it.type === 'show' ? 'tv' : 'movie';
        node.dataset.tmdb = String(it.tmdb || '');
        node.dataset.status = it.status;

        // status pill tekst
        const pillText = it.status === 'both' ? 'SYNCED' : (it.status === 'plex_only' ? 'PLEX' : 'SIMKL');
        const pillClass = it.status === 'both' ? 'p-syn' : (it.status === 'plex_only' ? 'p-px' : 'p-sk');

        // markup spiegelt de carrousel (ovr + cap + hover), én houdt Delete
        node.innerHTML = `
          <img alt="" src="${url || ''}" onerror="this.style.display='none'">
         <div class="wl-del pill p-del" role="button" tabindex="0"
              title="Delete from Plex"
              onclick="deletePoster(event, '${encodeURIComponent(it.key)}', this)">
          Delete
        </div>

          <div class="wl-ovr ovr">
            <span class="pill ${pillClass}">${pillText}</span>
          </div>

          <div class="wl-cap cap">${(it.title || '').replace(/"/g,'&quot;')} ${it.year ? '· ' + it.year : ''}</div>

          <div class="wl-hover hover">
            <div class="titleline">${(it.title || '')}</div>
            <div class="meta">
              <div class="chip src">${it.status==='both' ? 'Source: Synced' : (it.status==='plex_only' ? 'Source: Plex' : 'Source: SIMKL')}</div>
              <div class="chip time">${relTimeFromEpoch(it.added_epoch)}</div>
            </div>
            <div class="desc" id="wldesc-${node.dataset.type}-${node.dataset.tmdb}">${it.tmdb ? 'Fetching description…' : '—'}</div>
          </div>
        `;

        // Beschrijving lazy laden bij hover (zoals in de carrousel)
        node.addEventListener('mouseenter', async ()=>{
          const typ = node.dataset.type;
          const tmdb = node.dataset.tmdb;
          if (!tmdb) return;
          const descEl = document.getElementById(`wldesc-${typ}-${tmdb}`);
          if (!descEl || descEl.dataset.loaded) return;
          try{
            const meta = await fetch(`/api/tmdb/meta/${typ}/${tmdb}`).then(r=>r.json());
            descEl.textContent = meta?.overview || '—';
            descEl.dataset.loaded = '1';
          }catch(_){
            descEl.textContent = '—';
            descEl.dataset.loaded = '1';
          }
        }, {passive:true});

        grid.appendChild(node);
      }
    }catch(_){
      msg.textContent = 'Failed to load.';
    }
  }


  async function deletePoster(ev, encKey, btnEl){
  ev?.stopPropagation?.();
  const key = decodeURIComponent(encKey);
  const card = btnEl.closest('.wl-poster');
  btnEl.disabled = true;
  try{
    const res = await fetch('/api/watchlist/' + encodeURIComponent(key), { method:'DELETE' });

    // probeer JSON; zo niet, pak tekst
    let payload = null;
    let text = null;
    try { payload = await res.json(); } catch { text = await res.text(); }

    console.debug('DELETE /api/watchlist', key, {status: res.status, payload, text});

    // 1) primaire pad: backend geeft {ok:true}
    if (payload && payload.ok === true) {
      card.classList.add('wl-removing');
      setTimeout(()=>{ card.remove(); }, 350);
      return;
    }

    // 2) fallback: als HTTP 2xx is, maar geen JSON -> optimistic UI
    if (res.ok && !payload) {
      card.classList.add('wl-removing');
      setTimeout(()=>{ card.remove(); }, 350);
      return;
    }

    // anders: fout tonen
    btnEl.disabled = false;
    btnEl.textContent = 'Failed';
    setTimeout(()=>{ btnEl.textContent = 'Delete'; }, 1200);

  }catch(e){
    console.warn('deletePoster error', e);
    btnEl.disabled = false;
    btnEl.textContent = 'Error';
    setTimeout(()=>{ btnEl.textContent = 'Delete'; }, 1200);
  }
}


  async function updateWatchlistTabVisibility(){
  try {
    const cfg = await fetch('/api/config').then(r=>r.json());
    const tmdbKey = (cfg.tmdb?.api_key || '').trim();
    document.getElementById('tab-watchlist').style.display = tmdbKey ? 'block' : 'none';
  } catch(e){
    // bij error: tab verbergen
    document.getElementById('tab-watchlist').style.display = 'none';
  }
}
async function hasTmdbKey(){
  try{
    const cfg = await fetch('/api/config').then(r=>r.json());
    return !!(cfg.tmdb?.api_key || '').trim();
  }catch(_){ return false; }
}


function isOnMain(){
  return !document.getElementById('ops-card').classList.contains('hidden');
}

async function updatePreviewVisibility(){
  const card = document.getElementById('placeholder-card');
  const row  = document.getElementById('poster-row');

  if (!isOnMain()) {
    card.classList.add('hidden');
    return false;
  }

  const show = await hasTmdbKey();

  if(!show){
    card.classList.add('hidden');
    if(row){ row.innerHTML = ''; row.classList.add('hidden'); }
    window.wallLoaded = false;
    return false;
  } else {
    card.classList.remove('hidden');
    // Alleen laden als we 'm nog niet hebben
    if(!window.wallLoaded){
      await loadWall();
      window.wallLoaded = true;
    }
    return true;
  }
}

  // Boot
  showTab('main');
  updateWatchlistTabVisibility();
</script>
</body></html>
"""
