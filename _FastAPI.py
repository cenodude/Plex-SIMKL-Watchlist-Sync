# _FastAPI.py
# Exports the full HTML for the FastAPI index page.

def get_index_html() -> str:
    return r"""<!doctype html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plex ⇄ SIMKL Watchlist Sync</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="alternate icon" href="/favicon.ico">
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

  #ops-card.card{
    /* option A: more breathing room via padding */
    padding-block: 20px 38px;   /* top / bottom */

    /* option B (fixed floor): uncomment to enforce a minimum height */
    /* min-height: 260px; */
  }

  /* Right meta card */
  .det-right{ position: sticky; top: 8px; align-self: start; }

  .meta-card{
    background: #0a0a17;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px;
    box-shadow: 0 0 22px rgba(0,0,0,.25) inset;
  }

  .meta-grid{
    display: grid;
    grid-template-columns: auto 1fr;
    column-gap: 10px;
    row-gap: 8px;
    align-items: center;
  }

  .meta-label{
    font-size: 11px;
    letter-spacing: .08em;
    color: var(--muted);
    text-transform: uppercase;
    text-align: right;
    user-select: none;
  }

  .meta-value{ min-width: 0; }               /* allow truncation */
  .pillvalue{
    display: inline-flex;
    align-items: center;
    padding: 3px 8px;
    border-radius: 999px;
    background: #0b0b16aa;
    border: 1px solid #ffffff1a;
    font-weight: 700;
    font-size: 12px;
    line-height: 1.2;
  }

  .truncate{
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .mono{
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
    font-variant-numeric: tabular-nums;
  }

  .meta-actions{
    display: flex;
    gap: 8px;
    justify-content: flex-end;
    margin-top: 12px;
  }

  /* keep two-column details layout */
  .details-grid{
    display: grid;
    grid-template-columns: minmax(0,1fr) 320px;  /* left grows, right fixed */
    gap: 16px;
    align-items: stretch;                        /* <-- equal heights */
  }
  @media (max-width: 900px){
    .details-grid{ grid-template-columns: 1fr; }
    .det-right{ position: static; }
  }

  /* Columns as vertical flex stacks */
  .det-left,
  .det-right{
    display: flex;
    flex-direction: column;
    min-height: 0;                               /* avoid overflow in flex */
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
  #ops-card .chiprow{ margin-bottom: 20px; }     /* was ~8px */
  #ops-card .sep{ margin: 6px 0 16px; }          /* pushes the buttons down a bit */
  #ops-card .action-row{ margin-top: 0; }        /* ensure no extra collapse */

  /* Hide the title captions under posters */
  .cap, .wl-cap { display: none !important; }

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

  .sync-icon{
    width:15px;
    height:15px;
    border-radius:50%;
    flex-shrink:0;
    position: relative;
    top: -5px;
  }

  .sync-status{
  display:flex;
  align-items:center;
  gap:8px;
}

  .sync-icon.sync-warn{
    background:#ffc400;
    box-shadow:0 0 12px #ffc40088, 0 0 24px #ffc40044;
    animation: pulseWarn 1.6s infinite ease-in-out;
  }
  @keyframes pulseWarn {
    0%,100% { transform:scale(1); opacity:1; }
    50% { transform:scale(1.15); opacity:0.8; }
  }

  .sync-icon.sync-bad{
    background:#ff4d4f;
    box-shadow:0 0 12px #ff4d4f88, 0 0 24px #ff4d4f44;
    animation: pulseBad 1.2s infinite ease-in-out;
  }
  @keyframes pulseBad {
    0%,100% { transform:scale(1); }
    50% { transform:scale(1.2); }
  }

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

  .details-grid{
    display:grid;
    grid-template-columns:minmax(0,1fr) 300px;
    gap:14px;
  }
  #det-log{
    min-height:220px;
    max-height:55vh;
  }
  @media (max-width: 900px){
    .details-grid{ grid-template-columns: 1fr; }
  }

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

  .wl-del{ 
    position:absolute; top:8px; left:8px; z-index:5; 
  }
  .pill.p-del{
    color:#ffd8d8;
    border-color: rgba(255,77,79,.45);
    box-shadow: 0 0 14px rgba(255,77,79,.45);
  }

.pill.p-del:hover{ filter:brightness(1.06); box-shadow:0 0 18px rgba(255,77,79,.60); }
.pill.p-del:active{ transform:translateY(1px); }
  
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
    <!-- <div id="schedBanner" class="msg ok" style="display:none; width:auto; max-width:100%;">Scheduler is <b>running</b> • next run: <b id="schedNext">—</b></div> -->

    <div class="sync-status">
      <div id="sync-icon" class="sync-icon sync-warn"></div>
      <div id="sync-status-text" class="sub">Idle — run a sync to see results</div>
      <span id="sched-inline" class="sub muted" style="margin-left:8px; white-space:nowrap; display:none"></span>
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
        <div class="details-grid">
          <!-- LEFT: live output from plex_simkl_watchlist_sync.py -->
          <div class="det-left">
            <div class="title" style="margin-bottom:6px;font-weight:700">Sync output</div>
            <pre id="det-log" class="log"></pre>
          </div>

        <!-- RIGHT: run metadata -->
        <div class="det-right">
          <div class="meta-card">
            <div class="meta-grid">
              <div class="meta-label">Command</div>
              <div class="meta-value"><span id="det-cmd" class="pillvalue truncate">–</span></div>

              <div class="meta-label">Version</div>
              <div class="meta-value"><span id="det-ver" class="pillvalue">–</span></div>

              <div class="meta-label">Started</div>
              <div class="meta-value"><span id="det-start" class="pillvalue mono">–</span></div>

              <div class="meta-label">Finished</div>
              <div class="meta-value"><span id="det-finish" class="pillvalue mono">–</span></div>
            </div>

            <div class="meta-actions">
              <button class="btn" onclick="copySummary()">Copy summary</button>
              <button class="btn" onclick="downloadSummary()">Download</button>
            </div>
          </div>
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

  <!-- WATCHLIST (grid) -->
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
      </div>
    </div>

    <!-- TROUBLESHOOT -->
    <div class="section" id="sec-troubleshoot">
      <div class="head" onclick="toggleSection('sec-troubleshoot')"><span class="chev">▶</span><strong>Troubleshoot</strong></div>
      <div class="body">
        <div class="sub">Use these actions to fix common issues. They are safe but cannot be undone.</div>
        <div><label>Debug</label><select id="debug"><option value="false">off</option><option value="true">on</option></select></div>
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
                <div style="display:flex;gap:8px">
                  <input id="plex_token" placeholder="empty = not set">
                  <button class="btn" onclick="copyField('plex_token', this)">Copy</button>
                </div>

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
              <div>
                <label>Client ID</label>
                <input id="simkl_client_id" placeholder="Your SIMKL client id" oninput="updateSimklButtonState(); updateSimklHint();">
              </div>
              <div>
                <label>Client Secret</label>
                <input id="simkl_client_secret" placeholder="Your SIMKL client secret" oninput="updateSimklButtonState(); updateSimklHint();">
              </div>
            </div>

            <div id="simkl_hint" class="msg warn hidden">
              You need a SIMKL API key. Create one at
              <a href="https://simkl.com/settings/developer/" target="_blank" rel="noopener">SIMKL Developer</a>.
              Set the Redirect URL to <code id="redirect_uri_preview"></code>.
              <button class="btn" style="margin-left:8px" onclick="copyRedirect()">Copy Redirect URL</button>
            </div>

            <div style="display:flex;gap:8px;margin-top:8px">
              <button id="simkl_start_btn" class="btn" onclick="startSimkl()" disabled>Start SIMKL Auth</button>
              <div style="align-self:center;color:var(--muted)">Opens SIMKL authorize, callback to this webapp</div>
            </div>

            <div class="grid2" style="margin-top:8px">
              <div><label>Access token</label><input id="simkl_access_token" readonly placeholder="empty = not set"></div>
            </div>
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

  // Compute the correct redirect URL for this webapp
  function computeRedirectURI(){ return location.origin + '/callback'; }

  function updateSimklButtonState(){
    const id  = (document.getElementById('simkl_client_id')?.value || '').trim();
    const sec = (document.getElementById('simkl_client_secret')?.value || '').trim();
    const btn = document.getElementById('simkl_start_btn');
    if (btn) btn.disabled = !(id && sec);
  }

  // Hide SIMKL hint if client/secret exist locally OR in saved config.
  // Also keeps the Redirect URL preview in sync.
  function updateSimklHint(){
    const hint = document.getElementById('simkl_hint');
    if (!hint) return;

    const prev = document.getElementById('redirect_uri_preview');
    if (prev) prev.textContent = computeRedirectURI();

    const idVal  = (document.getElementById('simkl_client_id')?.value  || '').trim();
    const secVal = (document.getElementById('simkl_client_secret')?.value || '').trim();

    // local-first: no fetch; no flicker
    const bothFilled = !!idVal && !!secVal;
    hint.classList.toggle('hidden', bothFilled);
  }

  // Function to update the watchlist preview
  async function updateWatchlistPreview() {
    // Call the loadWatchlist function to reload the updated posters
    await loadWatchlist();
  }

  // Listen for changes in localStorage (other browsers)
  window.addEventListener('storage', (event) => {
    if (event.key === 'wl_hidden') {
      // Reload the watchlist when there's a change in the deleted items
      loadWatchlist();  // This will reload the watchlist and reflect the "DELETED" overlay
    }
  });

  let busy=false, esLog=null, esSum=null, plexPoll=null, simklPoll=null, appDebug=false, currentSummary=null;
  let wallLoaded=false, _lastSyncEpoch=null, _wasRunning=false;

  async function showTab(n) {
    const pageSettings = document.getElementById('page-settings');
    const pageWatchlist = document.getElementById('page-watchlist');
    const logPanel = document.getElementById('log-panel');
    const layout = document.getElementById('layout');

    // Tabs active state
    document.getElementById('tab-main').classList.toggle('active', n === 'main');
    document.getElementById('tab-watchlist').classList.toggle('active', n === 'watchlist');
    document.getElementById('tab-settings').classList.toggle('active', n === 'settings');

    // Sections visibility
    document.getElementById('ops-card').classList.toggle('hidden', n !== 'main');
    document.getElementById('placeholder-card').classList.toggle('hidden', n !== 'main');
    pageWatchlist.classList.toggle('hidden', n !== 'watchlist');
    pageSettings.classList.toggle('hidden', n !== 'settings');

    if (n === 'main') {
      layout.classList.remove('single');
      refreshStatus();
      layout.classList.toggle('full', !appDebug);
      if (!esSum) { openSummaryStream(); }
      await updatePreviewVisibility();    // Load posters for Main
      refreshSchedulingBanner();
    } else if (n === 'watchlist') {
      layout.classList.add('single');
      layout.classList.remove('full');
      logPanel.classList.add('hidden');
      loadWatchlist();                    // Rebuild watchlist grid
    } else { // n === 'settings'
      layout.classList.add('single');
      layout.classList.remove('full');
      logPanel.classList.add('hidden');

      // Open sections so inputs are visible
      document.getElementById('sec-auth')?.classList.add('open');
      document.getElementById('sec-plex')?.classList.add('close');
      document.getElementById('sec-simkl')?.classList.add('close');
      document.getElementById('sec-tmdb')?.classList.add('close');

      // Load config first so fields are populated, then compute UI state
      await loadConfig();
      updateTmdbHint?.();
      updateSimklHint?.();
      updateSimklButtonState?.();
      loadScheduling?.();
    }
  }
  
  function toggleSection(id) { 
    document.getElementById(id).classList.toggle('open'); 
  }

  function setBusy(v) {
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
  async function runSync() {
      if (busy) return;

      const btn = document.getElementById('run');
      setBusy(true);
      try { btn?.classList.add('glass'); } catch(_){}

      try {
          const resp = await fetch('/api/run', { method: 'POST' });
          const j = await resp.json();

          if (!resp.ok || !j || j.ok !== true) {
              setSyncHeader('sync-bad', `Failed to start${j?.error ? ` – ${j.error}` : ''}`);
          } else {
              // After sync completes, update the watchlist
              updateWatchlistPreview();  // This will trigger the refresh of the Watchlist Preview
          }
      } catch (e) {
          setSyncHeader('sync-bad', 'Failed to reach server');
      } finally {
          setBusy(false);
          recomputeRunDisabled();
          refreshStatus();
      }
  }


function logHTML(t){ const el=document.getElementById('log'); el.innerHTML += t + "<br>"; el.scrollTop = el.scrollHeight; }

  function setPlexSuccess(show){ document.getElementById('plex_msg').classList.toggle('hidden', !show); }
  function setSimklSuccess(show){ document.getElementById('simkl_msg').classList.toggle('hidden', !show); }

  async function copyField(id, btn){
    const el = document.getElementById(id);
    const text = el ? (('value' in el) ? el.value : (el.textContent || '')) : '';
    if (!text) { flashCopy(btn, false, 'Empty'); return; }

    let ok = false;
    try {                       // modern API
      await navigator.clipboard.writeText(text);
      ok = true;
    } catch {
      try {                     // fallback for non-HTTPS
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly','');
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.focus(); ta.select();
        ok = document.execCommand('copy');
        document.body.removeChild(ta);
      } catch { ok = false; }
    }
    flashCopy(btn, ok);
  }

  function flashCopy(btn, ok, msg){
    if (!btn) { if(!ok) alert(msg || 'Copy failed'); return; }
    const old = btn.textContent;
    btn.disabled = true;
    btn.textContent = ok ? 'Copied ✓' : (msg || 'Copy failed');
    setTimeout(()=>{ btn.textContent = old; btn.disabled = false; }, 1000);
  }

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
    setSyncHeader('sync-ok', (sum.result||'').toUpperCase()==='EQUAL' ? 'In sync ' : 'Synced ');
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

  const btn = document.getElementById('run');
  if (btn){
    if (sum.running) btn.classList.add('glass');
    else btn.classList.remove('glass');
  }
  // disabled-toestand op 1 plek bepalen
  if (typeof recomputeRunDisabled === 'function') recomputeRunDisabled();

  // When we transition from running -> not running, refresh posters
  if (_wasRunning && !sum.running) {
    // force the main preview to rebuild (resets wallLoaded and loads fresh)
    window.wallLoaded = false;
    updatePreviewVisibility?.();  // triggers loadWall() on Main if TMDb key is set

    // refresh the watchlist grid too
    loadWatchlist?.();

    // keep the inline scheduler text fresh
    refreshSchedulingBanner?.();
  }
  _wasRunning = !!sum.running;

}


  function openSummaryStream(){
    esSum = new EventSource('/api/run/summary/stream');
    esSum.onmessage = (ev)=>{ try{ renderSummary(JSON.parse(ev.data)); }catch(_){} };
    fetch('/api/run/summary').then(r=>r.json()).then(renderSummary).catch(()=>{});
  }

  let esDet = null;

  function openDetailsLog(){
    const el = document.getElementById('det-log');
    if (!el) return;
    el.innerHTML = '';                 // start fresh
    if (esDet) { esDet.close(); esDet = null; }
    esDet = new EventSource('/api/logs/stream?tag=SYNC');  // <- backend route below

    esDet.onmessage = (ev) => {
      if (!ev?.data) return;
      el.insertAdjacentHTML('beforeend', ev.data + '<br>');  // lines are HTML-escaped
      el.scrollTop = el.scrollHeight;
    };
    esDet.onerror = () => { try { esDet?.close(); } catch(_){} esDet = null; };
  }

  function closeDetailsLog(){
    try { esDet?.close(); } catch(_){}
    esDet = null;
  }

  function toggleDetails(){
    const d = document.getElementById('details');
    d.classList.toggle('hidden');
    if (!d.classList.contains('hidden')) openDetailsLog(); else closeDetailsLog();
  }

  window.addEventListener('beforeunload', closeDetailsLog);

  async function copySummary(btn){
    // Ensure we have a summary
    if (!window.currentSummary) {
      try { window.currentSummary = await fetch('/api/run/summary').then(r=>r.json()); }
      catch { flashCopy(btn, false, 'No summary'); return; }
    }
    const s = window.currentSummary;
    if (!s) { flashCopy(btn, false, 'No summary'); return; }

    // Build text
    const lines = [];
    lines.push(`Plex ⇄ SIMKL Watchlist Sync ${s.version || ''}`.trim());
    if (s.started_at)   lines.push(`Start:   ${s.started_at}`);
    if (s.finished_at)  lines.push(`Finish:  ${s.finished_at}`);
    if (s.cmd)          lines.push(`Cmd:     ${s.cmd}`);
    if (s.plex_pre != null && s.simkl_pre != null)   lines.push(`Pre:     Plex=${s.plex_pre} vs SIMKL=${s.simkl_pre}`);
    if (s.plex_post != null && s.simkl_post != null) lines.push(`Post:    Plex=${s.plex_post} vs SIMKL=${s.simkl_post} -> ${s.result || 'UNKNOWN'}`);
    if (s.duration_sec != null) lines.push(`Duration: ${s.duration_sec}s`);
    if (s.exit_code != null)    lines.push(`Exit:     ${s.exit_code}`);
    const text = lines.join('\n');

    // Try modern clipboard, then fallback
    let ok = false;
    try {
      await navigator.clipboard.writeText(text);
      ok = true;
    } catch {
      try {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly','');
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.focus(); ta.select();
        ok = document.execCommand('copy');
        document.body.removeChild(ta);
      } catch { ok = false; }
    }

    flashCopy(btn, ok);
  }

  function flashCopy(btn, ok, msg){
    if (!btn) { if(!ok) alert(msg || 'Copy failed'); return; }
    const old = btn.textContent;
    btn.disabled = true;
    btn.textContent = ok ? 'Copied ✓' : (msg || 'Copy failed');
    setTimeout(()=>{ btn.textContent = old; btn.disabled = false; }, 1200);
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

    // --- SYNC / runtime ---
    document.getElementById('mode').value   = cfg.sync?.bidirectional?.mode || 'two-way';
    document.getElementById('source').value = cfg.sync?.bidirectional?.source_of_truth || 'plex';
    document.getElementById('debug').value  = String(cfg.runtime?.debug || false);

    // --- PLEX ---
    document.getElementById('plex_token').value = cfg.plex?.account_token || '';

    // --- SIMKL (the missing bit) ---
    document.getElementById('simkl_client_id').value     = cfg.simkl?.client_id || '';
    document.getElementById('simkl_client_secret').value = cfg.simkl?.client_secret || '';
    document.getElementById('simkl_access_token').value  = cfg.simkl?.access_token || '';

    // --- TMDb ---
    document.getElementById('tmdb_api_key').value = cfg.tmdb?.api_key || '';

    // refresh UI state after fields are filled
    updateSimklButtonState?.();
    updateSimklHint?.();
    updateTmdbHint?.();
  }

  // SAVE SETTINGS
  async function saveSettings(){
    // 1) Read server config + deep clone
    const serverCfg = await fetch('/api/config').then(r=>r.json()).catch(()=>({}));
    const cfg = (typeof structuredClone === 'function')
      ? structuredClone(serverCfg)
      : JSON.parse(JSON.stringify(serverCfg || {}));

    // --- SYNC ---
    cfg.sync = cfg.sync || {};
    cfg.sync.bidirectional = cfg.sync.bidirectional || {};
    const uiMode   = document.getElementById('mode').value;
    const uiSource = document.getElementById('source').value;
    cfg.sync.bidirectional.mode = uiMode;
    cfg.sync.bidirectional.source_of_truth = uiSource;

    // --- RUNTIME ---
    cfg.runtime = cfg.runtime || {};
    cfg.runtime.debug = (document.getElementById('debug').value === 'true');

    // --- PLEX ---
    cfg.plex = cfg.plex || {};
    const uiPlexToken = (document.getElementById('plex_token').value || '').trim();
    if (uiPlexToken) cfg.plex.account_token = uiPlexToken;

    // --- SIMKL ---
    cfg.simkl = cfg.simkl || {};
    const uiCid = (document.getElementById('simkl_client_id').value || '').trim();
    const uiSec = (document.getElementById('simkl_client_secret').value || '').trim();
    if (uiCid) cfg.simkl.client_id = uiCid;
    if (uiSec) cfg.simkl.client_secret = uiSec;
    // (access_token not modified here)

    // --- TMDb ---
    cfg.tmdb = cfg.tmdb || {};
    const uiTmdb = (document.getElementById('tmdb_api_key').value || '').trim();
    if (uiTmdb) cfg.tmdb.api_key = uiTmdb;

    // 2) Save general config
    await fetch('/api/config', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(cfg)
    });

    // 2b) Save Scheduling with the same Save button
    try {
      const schPayload = {
        enabled: document.getElementById('schEnabled').value === 'true',
        mode: document.getElementById('schMode').value,
        every_n_hours: parseInt(document.getElementById('schN').value || '2', 10),
        daily_time: document.getElementById('schTime').value || '03:30'
      };
      await fetch('/api/scheduling', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(schPayload)
      });
    } catch (e) {
      console.warn('Failed to save scheduling', e);
    }

    // 3) UI refreshes
    updateSimklButtonState?.();
    updateTmdbHint?.();
    await refreshStatus();
    refreshSchedulingBanner?.();
    await updateWatchlistTabVisibility?.();

    // 4) Only manage the preview on Main
    const onMain = !document.getElementById('ops-card').classList.contains('hidden');
    if (onMain) {
      await updatePreviewVisibility();
    } else {
      document.getElementById('placeholder-card')?.classList.add('hidden');
    }

    // 5) Save toast
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
    fetch('/api/scheduling/status')
      .then(r => r.json())
      .then(j => {
        const span = document.getElementById('sched-inline');
        if (!span) return;
        if (j && j.config && j.config.enabled) {
          const nextRun = j.next_run_at ? new Date(j.next_run_at*1000).toLocaleString() : '—';
          span.textContent = `-   Scheduler running (next ${nextRun})`;
          span.style.display = 'inline';
        } else {
          span.textContent = '';
          span.style.display = 'none';
        }
      })
      .catch(() => {
        const span = document.getElementById('sched-inline');
        if (span){ span.textContent = ''; span.style.display = 'none'; }
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
    const hint  = document.getElementById('tmdb_hint');
    const input = document.getElementById('tmdb_api_key');
    if (!hint || !input) return;

    const v = (input.value || '').trim();
    if (v){                         // user already typed / field filled
      hint.classList.add('hidden');
      return;
    }

    // Field is empty — double-check saved config on the server
    try {
      const cfg = await fetch('/api/config', { cache: 'no-store' }).then(r => r.json());
      const has = !!((cfg.tmdb?.api_key || '').trim());
      hint.classList.toggle('hidden', has);
    } catch {
      // If we can’t reach the server, err on the side of showing the hint
      hint.classList.remove('hidden');
    }
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
  async function loadWall() {
    const card = document.getElementById('placeholder-card');
    const msg = document.getElementById('wall-msg');
    const row = document.getElementById('poster-row');
    msg.textContent = 'Loading…'; 
    row.innerHTML = ''; 
    row.classList.add('hidden'); 
    card.classList.remove('hidden');

    // Read client-side hidden set (successfully deleted keys)
    const hidden = new Set((()=>{
      try { return JSON.parse(localStorage.getItem('wl_hidden') || '[]'); }
      catch { return []; }
    })());

    // Add to hidden keys when deleting an item
    const isDeleted = (k) => hidden.has(k) || (window._deletedKeys && window._deletedKeys.has(k));

    try {
      const data = await fetch('/api/state/wall').then(r => r.json());
      if (data.missing_tmdb_key) {
        card.classList.add('hidden');
        return;
      }
      if (!data.ok) {
        msg.textContent = data.error || 'No state data found.';
        return;
      }
      const items = data.items || [];
      _lastSyncEpoch = data.last_sync_epoch || null;
      if (items.length === 0) {
        msg.textContent = 'No items to show yet.';
        return;
      }
      msg.classList.add('hidden');
      row.classList.remove('hidden');

      // Loop through each item and check its status
      for (const it of items) {
        if (!it.tmdb) continue;

        const a = document.createElement('a');
        a.className = 'poster';
        a.href = `https://www.themoviedb.org/${it.type}/${it.tmdb}`; 
        a.target = '_blank'; 
        a.rel = 'noopener';
        a.dataset.type = it.type; 
        a.dataset.tmdb = String(it.tmdb); 
        a.dataset.key = it.key || '';

        // Decide UI status (override to 'deleted' if key is hidden)
        const uiStatus = isDeleted(it.key) ? 'deleted' : it.status;
        a.dataset.source = uiStatus;

        const img = document.createElement('img');
        img.loading = 'lazy'; 
        img.alt = `${it.title || ''} (${it.year || ''})`;
        img.src = artUrl(it, 'w342');
        a.appendChild(img);

        const ovr = document.createElement('div'); 
        ovr.className = 'ovr';
        let pillText, pillClass;
        if (uiStatus === 'deleted') {
          pillText = 'DELETED'; 
          pillClass = 'p-del'; // requires .pill.p-del CSS
        } else if (uiStatus === 'both') {
          pillText = 'SYNCED';  
          pillClass = 'p-syn';
        } else if (uiStatus === 'plex_only') {
          pillText = 'PLEX';    
          pillClass = 'p-px';
        } else {
          pillText = 'SIMKL';   
          pillClass = 'p-sk';
        }
        const pill = document.createElement('div');
        pill.className = 'pill ' + pillClass;
        pill.textContent = pillText;
        ovr.appendChild(pill); 
        a.appendChild(ovr);

        const cap = document.createElement('div'); 
        cap.className = 'cap';
        cap.textContent = `${it.title || ''} ${it.year ? '· ' + it.year : ''}`;
        a.appendChild(cap);

        const hover = document.createElement('div'); 
        hover.className = 'hover';
        hover.innerHTML = `
          <div class="titleline">${it.title || ''}</div>
          <div class="meta">
            <div class="chip src">${uiStatus === 'deleted' ? 'Status: Deleted' : (uiStatus === 'both' ? 'Source: Synced' : (uiStatus === 'plex_only' ? 'Source: Plex' : 'Source: SIMKL'))}</div>
            <div class="chip time" id="time-${it.type}-${it.tmdb}">${_lastSyncEpoch ? ('updated ' + relTimeFromEpoch(_lastSyncEpoch)) : ''}</div>
          </div>
          <div class="desc" id="desc-${it.type}-${it.tmdb}">Fetching description…</div>
        `;
        a.appendChild(hover);

        a.addEventListener('mouseenter', async () => {
          const descEl = document.getElementById(`desc-${it.type}-${it.tmdb}`);
          if (!descEl || descEl.dataset.loaded) return;
          try {
            const cb = window._lastSyncEpoch || 0;
            const meta = await fetch(`/api/tmdb/meta/${it.type}/${it.tmdb}?cb=${cb}`).then(r => r.json());
            descEl.textContent = meta?.overview || '—';
            descEl.dataset.loaded = '1';
          } catch {
            descEl.textContent = '—';
            descEl.dataset.loaded = '1';
          }
        }, { passive: true });

        row.appendChild(a);
      }
      initWallInteractions();
    } catch {
      msg.textContent = 'Failed to load preview.';
    }
  }

  // ---- Watchlist helpers ----
  function artUrl(item, size){
    const typ  = (item.type === 'tv' || item.type === 'show') ? 'tv' : 'movie';
    const tmdb = item.tmdb;
    if(!tmdb) return null;
    const cb = window._lastSyncEpoch || 0;          // changes after each sync
    return `/art/tmdb/${typ}/${tmdb}?size=${encodeURIComponent(size || 'w342')}&cb=${cb}`;
  }

  function relTimeFromEpoch(epoch){
    if(!epoch) return '';
    const secs = Math.max(1, Math.floor(Date.now()/1000 - epoch));
    const units = [["y",31536000],["mo",2592000],["d",86400],["h",3600],["m",60],["s",1]];
    for(const [label,span] of units){ if(secs >= span) return Math.floor(secs/span) + label + " ago"; }
    return "just now";
  }

  async function loadWatchlist() {
      const grid = document.getElementById('wl-grid');
      const msg = document.getElementById('wl-msg');

      // Reset grid and show loading message
      grid.innerHTML = ''; 
      grid.classList.add('hidden'); 
      msg.textContent = 'Loading…'; 
      msg.classList.remove('hidden');

      try {
          // Fetch the watchlist data from the API
          const data = await fetch('/api/watchlist').then(r => r.json());

          // Debugging: Log fetched data
          console.log("Fetched Watchlist Data:", data);

          if (data.missing_tmdb_key) {
              msg.textContent = 'Set a TMDb API key to see posters.';
              return;
          }

          if (!data.ok) {
              msg.textContent = data.error || 'No state data found.';
              return;
          }

          const items = data.items || [];
          if (items.length === 0) {
              msg.textContent = 'No items on your watchlist yet.';
              return;
          }

          // Hide loading message and show grid
          msg.classList.add('hidden'); 
          grid.classList.remove('hidden');

          // Loop through each item and create the DOM elements
          for (const it of items) {
              console.log("Item:", it);  // Log each item for verification

              if (!it.tmdb) continue;

              // Create poster container
              const node = document.createElement('div');
              node.className = 'wl-poster poster';
              node.dataset.key = it.key;
              node.dataset.type = it.type === 'tv' || it.type === 'show' ? 'tv' : 'movie';
              node.dataset.tmdb = String(it.tmdb || '');
              node.dataset.status = it.status;

              // Check if the item is marked as deleted
              const isDeleted = (key) => {
                  const hidden = new Set(JSON.parse(localStorage.getItem('wl_hidden') || '[]'));
                  return hidden.has(key);
              };

              // Set the pill text based on the item status
              const pillText = it.status === 'both' ? 'SYNCED' : (it.status === 'plex_only' ? 'PLEX' : 'SIMKL');
              const pillClass = it.status === 'both' ? 'p-syn' : (it.status === 'plex_only' ? 'p-px' : 'p-sk');

              // Build the inner HTML for the poster
              node.innerHTML = `
                  <img alt="" src="${artUrl(it, 'w342') || ''}" onerror="this.style.display='none'">
                  <div class="wl-del pill p-del" role="button" tabindex="0"
                      title="Delete from Plex"
                      onclick="deletePoster(event, '${encodeURIComponent(it.key)}', this)">
                      Delete
                  </div>

                  <div class="wl-ovr ovr">
                      <span class="pill ${pillClass}">${pillText}</span>
                  </div>

                  <div class="wl-cap cap">${(it.title || '').replace(/"/g, '&quot;')} ${it.year ? '· ' + it.year : ''}</div>

                  <div class="wl-hover hover">
                      <div class="titleline">${(it.title || '')}</div>
                      <div class="meta">
                          <div class="chip src">${it.status === 'both' ? 'Source: Synced' : (it.status === 'plex_only' ? 'Source: Plex' : 'Source: SIMKL')}</div>
                          <div class="chip time">${relTimeFromEpoch(it.added_epoch)}</div>
                      </div>
                      <div class="desc" id="wldesc-${node.dataset.type}-${node.dataset.tmdb}">${it.tmdb ? 'Fetching description…' : '—'}</div>
                  </div>
              `;

              // If the item is deleted, update the pill to show 'DELETED'
              if (isDeleted(it.key)) {
                  const pill = node.querySelector('.pill');
                  pill.textContent = 'DELETED';  // Change pill to 'DELETED'
                  pill.classList.add('p-del');   // Apply 'DELETED' styling
              }

              // Description lazy loading for hover
              node.addEventListener('mouseenter', async () => {
                  const descEl = document.getElementById(`wldesc-${it.type}-${it.tmdb}`);
                  if (!descEl || descEl.dataset.loaded) return;
                  try {
                      const cb = window._lastSyncEpoch || Date.now();
                      const meta = await fetch(`/api/tmdb/meta/${it.type}/${it.tmdb}?cb=${cb}`).then(r => r.json());
                      descEl.textContent = meta?.overview || '—';
                      descEl.dataset.loaded = '1';
                  } catch {
                      descEl.textContent = '—';
                      descEl.dataset.loaded = '1';
                  }
              }, { passive: true });

              // Append the item to the grid
              grid.appendChild(node);
          }
      } catch (error) {
          console.error('Error loading watchlist:', error);
          msg.textContent = 'Failed to load preview.';
      }
  }

  async function deletePoster(ev, encKey, btnEl) {
    ev?.stopPropagation?.();
    const key = decodeURIComponent(encKey);
    const card = btnEl.closest('.wl-poster');
    btnEl.disabled = true;

    try {
      const res = await fetch('/api/watchlist/' + encodeURIComponent(key), { method: 'DELETE' });

      if (res.ok) {
        card.classList.add('wl-removing');
        setTimeout(() => { card.remove(); }, 350);

        // Update the localStorage to reflect deleted status
        const hidden = new Set(JSON.parse(localStorage.getItem('wl_hidden') || '[]'));
        hidden.add(key);  // Add deleted item key to hidden
        localStorage.setItem('wl_hidden', JSON.stringify([...hidden]));

        // Notify other browsers of the change by triggering the 'storage' event
        window.dispatchEvent(new Event('storage'));  // This will trigger the storage event in other browsers
        return;
      }

      btnEl.disabled = false;
      btnEl.textContent = 'Failed';
      setTimeout(() => { btnEl.textContent = 'Delete'; }, 1200);
    } catch (e) {
      console.warn('deletePoster error', e);
      btnEl.disabled = false;
      btnEl.textContent = 'Error';
      setTimeout(() => { btnEl.textContent = 'Delete'; }, 1200);
    }
  }

  async function updateWatchlistTabVisibility(){
  try {
    const cfg = await fetch('/api/config').then(r=>r.json());
    const tmdbKey = (cfg.tmdb?.api_key || '').trim();
     // CENODUDE WATCHLIST DISABLE document.getElementById('tab-watchlist').style.display = tmdbKey ? 'block' : 'none';
     document.getElementById('tab-watchlist').style.display = 'none';
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