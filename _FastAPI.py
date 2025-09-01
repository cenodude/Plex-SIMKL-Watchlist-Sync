# _FastAPI.py
# Renders the full HTML for the web UI. Keep this file self‑contained 

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

  /* Ops card layout */
  #ops-card.card{ padding-block: 20px 38px; }

  /* Icon button + spinner animation */
  .iconbtn{
    display:inline-flex; align-items:center; justify-content:center;
    width:32px; height:32px; border-radius:10px;
    border:1px solid var(--border);
    background:linear-gradient(180deg,rgba(255,255,255,.02),transparent), #0b0b16;
    color:#dfe6ff; cursor:pointer;
    box-shadow:0 0 0 transparent;
    transition: box-shadow .25s ease, filter .2s ease, transform .05s ease, opacity .2s;
  }
  .iconbtn:hover{ box-shadow:0 0 14px #7c5cff66; filter: brightness(1.06); }
  .iconbtn:active{ transform: translateY(1px); }
  .iconbtn:disabled{ opacity:.55; cursor:not-allowed; box-shadow:none; }

  .iconbtn.loading svg{ animation: spin .8s linear infinite; }
  .iconbtn svg { transition: transform .3s ease; }
  .iconbtn.spin svg{ animation: pulseSpin 2s linear; }

  /* Shared rotation keyframe */
  @keyframes spin { to { transform: rotate(360deg); } }
  /* 2s "spin + slight scale" burst used on manual refresh */
  @keyframes pulseSpin {
    0%   { transform: rotate(0deg) scale(1); }
    50%  { transform: rotate(180deg) scale(1.2); }
    100% { transform: rotate(360deg) scale(1); }
  }

  /* Versioning pill */
  .hidden{ display:none }

  /* Sticky right meta card  */
  .det-right{
    position: sticky;
    top: 64px;  /* below header */
    align-self: start;
    margin-top: 20px;  /* extra initial offset in normal flow */
  }

  .meta-card{
    background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--panel);
    border:1px solid var(--border);
    border-radius:14px;
    padding:12px;
    box-shadow:0 0 40px #000 inset;
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

  .meta-value{ min-width: 0; }
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

  .truncate{ max-width:100%; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .mono{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; font-variant-numeric: tabular-nums; }

  .meta-actions{ display:flex; gap:8px; justify-content:flex-end; margin-top:12px; }

  /* Two-column details layout */
  .details-grid{
    display: grid;
    grid-template-columns: minmax(0,1fr) 320px;
    gap: 16px;
    align-items: stretch;
  }
  @media (max-width: 900px){
    .details-grid{ grid-template-columns: 1fr; }
    .det-right{ position: static; }
  }
  .det-left, .det-right{ display:flex; flex-direction:column; min-height:0; }

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
    animation: neonPulse 3.2s ease-in-out infinite;
  }
  .tab.active{color:var(--fg);border-color:#3d38ff;box-shadow:0 0 18px #3d38ff33}
  @keyframes neonPulse {
    0%   { box-shadow:0 0 10px #7c5cff33, inset 0 0 0 #0000 }
    50%  { box-shadow:0 0 18px #7c5cff66, inset 0 0 12px #7c5cff22 }
    100% { box-shadow:0 0 10px #7c5cff33, inset 0 0 0 #0000 }
  }
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

  .sync-icon{ width:15px; height:15px; border-radius:50%; flex-shrink:0; position: relative; top: -5px; }
  .sync-icon.sync-warn{ background:#ffc400; box-shadow:0 0 12px #ffc40088, 0 0 24px #ffc40044; animation: pulseWarn 1.6s infinite ease-in-out; }
  @keyframes pulseWarn { 0%,100% { transform:scale(1); opacity:1; } 50% { transform:scale(1.15); opacity:0.8; } }
  .sync-icon.sync-bad{ background:#ff4d4f; box-shadow:0 0 12px #ff4d4f88, 0 0 24px #ff4d4f44; animation: pulseBad 1.2s infinite ease-in-out; }
  @keyframes pulseBad { 0%,100% { transform:scale(1); } 50% { transform:scale(1.2); } }

  .sync-ok{background:var(--accent2)} .sync-warn{background:#ffc400} .sync-bad{background:#ff4d4f}
  .chiprow{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
  .chip{border:1px solid var(--border);background:#0a0a17;padding:6px 10px;border-radius:999px;color:#e7e9f4}

  .action-row{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:10px;margin-bottom:0}
  .action-buttons{display:flex;gap:8px;flex-wrap:wrap}
  .stepper{display:flex;gap:12px;align-items:center;margin:0}
  .step{display:flex;align-items:center;gap:6px;color:var(--muted);font-size:12px}
  .tl-dot{width:10px;height:10px;border-radius:50%;background:#333}.tl-dot.on{background:#7c5cff;box-shadow:0 0 10px var(--glow)}

  /* Sync output panel — match .card neon */
  .details{
    border:1px solid var(--border);
    border-radius:20px;
    padding:16px;
    margin-top:10px;
    background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--panel);
    box-shadow:0 0 40px #000 inset;
  }

  .log{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#05060b;border-radius:14px;border:1px solid var(--border);padding:12px;min-height:160px;max-height:50vh;overflow:auto;white-space:pre-wrap}

  .msg{border:1px solid transparent;border-radius:12px;padding:8px 12px;margin-top:8px;font-weight:650}
  .msg.ok{background:rgba(25,195,125,.12);border-color:rgba(25,195,125,.35);color:#c8ffe6}
  .msg.warn{background:rgba(255,196,0,.10);border-color:rgba(255,196,0,.35);color:#ffe28a}
  .muted{color:var(--muted)} code{padding:2px 6px;border:1px solid var(--border);border-radius:8px;background:#0a0a17}

  /* Footer buttons – consistent neon style */
  .footer{display:flex;gap:10px;align-items:center;margin-top:8px}
  .footer .btn{ padding:12px 16px; border-radius:14px; border:1px solid var(--border); background:#121224; color:#fff; font-weight:650; }
  .footer .btn:first-child{ background:linear-gradient(180deg,rgba(255,255,255,.02),transparent), var(--grad2); box-shadow:0 0 14px var(--glow2); }
  .footer .btn:nth-child(2){ background:linear-gradient(180deg,rgba(255,255,255,.02),transparent), var(--grad3); box-shadow:0 0 14px #ff7ae044; }
  .footer .btn:hover{filter:brightness(1.07);box-shadow:0 0 22px #7c5cff66}
  .footer .btn:active{transform:translateY(1px)}
  #save_msg{margin-left:8px}

  /* Log panel */
  #det-log{
    height: 25vh;          /* vast */
    min-height: 180px;
    max-height: 25vh;
    scrollbar-width: thin;                 /* Firefox */
    scrollbar-color: #6a67ff #0b0b16;      /* thumb / track */
  }
  #det-log::-webkit-scrollbar{ width:12px; }                    /* Chrome/Edge */
  #det-log::-webkit-scrollbar-track{
    background:#0b0b16;
    border-left:1px solid var(--border);
    border-radius:10px;
  }
  #det-log::-webkit-scrollbar-thumb{
    background:linear-gradient(180deg,#7c5cff66,#00b7eb66);
    border:1px solid #ffffff20;
    border-radius:10px;
  }
  #det-log::-webkit-scrollbar-thumb:hover{
    background:linear-gradient(180deg,#9f97ff88,#24c8ff88);
  }

  .log-scrub input[type="range"]{
    -webkit-appearance:none; appearance:none;
    width:100%; height:4px; border-radius:999px; outline:none;
    background:linear-gradient(90deg,#3d38ff33,#00b7eb33);
  }
  .log-scrub input[type="range"]::-webkit-slider-thumb{
    -webkit-appearance:none; appearance:none;
    width:16px; height:16px; border-radius:50%;
    background:#fff; border:1px solid #ffffff22; box-shadow:0 0 10px var(--glow);
  }
  .log-scrub input[type="range"]::-moz-range-thumb{
    width:16px; height:16px; border-radius:50%;
    background:#fff; border:1px solid #ffffff22; box-shadow:0 0 10px var(--glow);
  }


  /* Watchlist grid */
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
  .wl-del{ position:absolute; top:8px; left:8px; padding:4px 8px; border-radius:999px; font-size:11px; font-weight:800;
           background:rgba(0,0,0,.5); border:1px solid rgba(255,255,255,.12); backdrop-filter: blur(4px); cursor:pointer; }
  .wl-cap{ position:absolute; left:8px; right:8px; bottom:6px; font-size:12px; color:#dfe3ea; text-shadow:0 1px 2px #000 }
  .wl-hover{ position:absolute; inset:auto 0 0 0; height:62%;
             background: linear-gradient(180deg,rgba(0,0,0,.1),rgba(0,0,0,.60) 20%, rgba(0,0,0,.85));
             color:#eaf0ff; padding:10px; transform: translateY(100%); opacity:0; transition:.25s ease;
             border-top:1px solid #ffffff22; backdrop-filter: blur(8px); }
  .wl-poster:hover .wl-hover{ transform: translateY(0); opacity:1; }
  .wl-removing{ opacity:0; transform: scale(.98); filter: blur(1px); }

  /* Poster carousel */
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

  /* feedback for copy buttons */
  .btn.copied {
    box-shadow: 0 0 0 6px rgba(46, 204, 113, 0.15);
    position: relative;
  }

  .btn.copied::after {
    content: "Copied!";
    position: absolute;
    top: -28px;
    right: 0;
    background: #2ecc71;
    color: #111;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 12px;
    animation: pop-fade 900ms ease forwards;
  }

  @keyframes pop-fade {
    0%   { transform: translateY(6px) scale(0.9); opacity: 0; }
    20%  { transform: translateY(0)   scale(1);   opacity: 1; }
    70%  { opacity: 1; }
    100% { transform: translateY(-2px) scale(0.98); opacity: 0; }
  }

  /* Run button visual feedback */
  #run.btn.acc { position: relative; overflow: hidden; }
  #run.btn.acc::after{
    content:"";
    position:absolute; top:-120%; left:-30%;
    width:60%; height:300%;
    transform: rotate(25deg);
    opacity:0;
    background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.18) 50%, rgba(255,255,255,0) 100%);
  }
  #run.btn.acc.loading::after{ opacity:1; animation: shimmer 1.2s linear infinite; }
  @keyframes shimmer { 0%{ transform: translateX(-120%) rotate(25deg); } 100%{ transform: translateX(220%) rotate(25deg); } }

  #run{ --prog: 0; position: relative; overflow: hidden; }
  #run::before{
    content:""; position:absolute; inset:0;
    background: linear-gradient(90deg, #7c5cff33, #2da1ff33 50%, #19c37d33),
               linear-gradient(180deg, rgba(255,255,255,.04), transparent);
    transform: scaleX(calc(var(--prog) / 100)); transform-origin: left center;
    transition: transform .35s ease, opacity .2s ease;
    opacity:0; z-index:0;
  }
  #run.loading::before{ opacity:1; }
  #run.loading.indet::after{
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(120deg, transparent 0%, rgba(255,255,255,.12) 45%, rgba(255,255,255,.28) 50%, rgba(255,255,255,.12) 55%, transparent 100%);
    animation: run-sweep 1.1s linear infinite; z-index: 0;
  }
  #run .label, #run .spinner{ position: relative; z-index: 1; }
  @keyframes run-sweep { 0%{ transform: translateX(-100%);} 100%{ transform: translateX(100%);} }

  /* Footer button palette tweaks */
  .footer .btn{ transition: filter .15s ease, box-shadow .25s ease, transform .05s ease; }
  .footer .btn-save{ color:#d3ffe9; background:linear-gradient(180deg,#0a1411,#08110e)!important; border:1px solid #144233!important; box-shadow: inset 0 1px 0 #0f1f19; }
  .footer .btn-save:hover{ filter:brightness(1.05); box-shadow: inset 0 1px 0 #142a22, 0 0 14px rgba(25,195,125,.15); }
  .footer .btn-save:active{ transform: translateY(1px); }
  .footer .btn-exit{ color:#ffd7d7; background:linear-gradient(180deg,#150909,#100606)!important; border:1px solid #4a1417!important; box-shadow: inset 0 1px 0 #1a0c0d; }
  .footer .btn-exit:hover{ filter:brightness(1.05); box-shadow: inset 0 1px 0 #211013, 0 0 14px rgba(255,77,79,.15); }
  .footer .btn-exit:active{ transform: translateY(1px); }
  .footer .btn-ic{ margin-right:8px; opacity:.9; }

  /* Update banner */
  .hidden { display: none !important; }
  #update-banner { display: flex; gap: 0.25em; }

  /* Align far right inside a flex row (.chiprow must be display:flex) */
  #st-update { margin-left: auto; }

  /* Fancy attention without layout shifts */
  .badge.upd{
    position: relative;
    overflow: hidden;
    isolation: isolate;
    background: rgba(206,117,0,0.18);
    border: 1px solid rgba(206,117,0,0.45);
    color: #fff;
    font-weight: 700;
    /* size comes from your .badge */
    will-change: transform, box-shadow;
    transition: background .3s ease, border-color .3s ease, transform .2s ease, box-shadow .2s ease;
    animation: updPulse 2.4s ease-in-out infinite;
  }

  /* soft outer halo */
  .badge.upd::before{
    content: "";
    position: absolute;
    inset: -2px;
    border-radius: inherit;
    box-shadow: 0 0 0 0 rgba(206,117,0,0.0);
    animation: updHalo 2.4s ease-in-out infinite;
    z-index: -1;
    pointer-events: none;
  }

  /* FULL-WIDTH shimmer sweep (Fix B: animate 'left') */
  .badge.upd::after{
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    left: -40%;          /* start off the left edge */
    width: 40%;          /* stripe width */
    border-radius: inherit;
    background: linear-gradient(
      120deg,
      transparent 0%,
      rgba(255,255,255,.16) 35%,
      rgba(255,255,255,.18) 50%,
      transparent 65%
    );
    transform: skewX(-12deg);     /* keep diagonal look */
    animation: updShimmer 5.5s ease-in-out infinite;
    will-change: left;
    pointer-events: none;
  }

  /* Shimmer travels fully from left to right */
  @keyframes updShimmer{
    0%, 35%   { left: -40%; }
    55%, 100% { left: 100%; }
  }

  .badge.upd:hover{
    background: rgba(206,117,0,0.26);
    border-color: rgba(206,117,0,0.55);
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(206,117,0,.18);
  }

  /* one-time pop when it appears */
  .badge.upd.reveal{
    animation: updPop 650ms cubic-bezier(.2,.9,.2,1) 1, updPulse 2.4s ease-in-out 0s infinite;
  }

  /* link stays bold white */
  .badge.upd a{
    color: inherit;
    font-weight: 700;
    text-decoration: none;
  }
  .badge.upd a:hover{
    text-decoration: underline;
    text-underline-offset: 2px;
  }

  /* animations */
  @keyframes updPulse{
    0%,100% { box-shadow: 0 0 0 rgba(206,117,0,0); }
    50%     { box-shadow: 0 0 16px rgba(206,117,0,.25); }
  }
  @keyframes updHalo{
    0%   { box-shadow: 0 0 0 0 rgba(206,117,0,0.0); }
    50%  { box-shadow: 0 0 0 6px rgba(206,117,0,0.18); }
    100% { box-shadow: 0 0 0 0 rgba(206,117,0,0.0); }
  }
  @keyframes updPop{
    0%   { transform: scale(.92); filter: saturate(.9) brightness(.95); }
    60%  { transform: scale(1.06); }
    100% { transform: scale(1); filter: none; }
  }

  /* reduced motion */
  @media (prefers-reduced-motion: reduce){
    .badge.upd,
    .badge.upd::before,
    .badge.upd::after { animation: none !important; transition: none !important; }
  }

  /* Push the right meta card down in the details grid */
  .details-grid > .det-right {
    top: 28px !important;   /* optional sticky offset */
    display: flex;
    flex-direction: column;
  }

  .details-grid > .det-right .meta-card {
    margin-top: 28px;       /* keep the spacing */
    flex: 1;                /* let it grow to match left column height */
    display: flex;
    flex-direction: column;
    justify-content: space-between; /* buttons stick to bottom */
  }


  /* Hide the bottom title on the WATCHLIST PREVIEW (carousel) only */
  #placeholder-card .cap { display: none !important; }

  /* Hide titles in the WATCHLIST GRID page as well */
  #page-watchlist .wl-cap { display: none !important; }

  /* Icon-only button for Watchlist delete */
  .icon-btn{
    --fg: #fff;
    --bg: rgba(255,255,255,0.06);
    --bd: rgba(255,255,255,0.12);
    display:inline-flex; align-items:center; justify-content:center;
    width:36px; height:36px;
    border-radius:12px;
    background:var(--bg);
    border:1px solid var(--bd);
    color:var(--fg);
    cursor:pointer;
    transition: transform .12s ease, background .2s, border-color .2s, box-shadow .2s;
  }
  .icon-btn:hover{
    background:rgba(255,255,255,0.10);
    border-color:rgba(255,255,255,0.18);
    transform:translateY(-1px);
    box-shadow:0 6px 18px rgba(0,0,0,.25);
  }
  .icon-btn:active{ transform:translateY(0); }

  .icon-btn .ico{
    width:18px; height:18px;
    fill:none; stroke:currentColor; stroke-width:2;
    stroke-linecap:round; stroke-linejoin:round;
  }

  /* Trash-specific micro animation */
  .icon-btn.trash .lid{ transform-origin: 12px 6px; transition: transform .25s ease; }
  .icon-btn.trash:hover .lid{ transform: translateY(-1px) rotate(-12deg); }

  /* Async states */
  .icon-btn.working{ pointer-events:none; opacity:.85; }
  .icon-btn.working .ico{ animation: spin 900ms linear infinite; }

  .icon-btn.done{
    background: rgba(46,204,113,.18);
    border-color: rgba(46,204,113,.45);
  }
  .icon-btn.error{
    background: rgba(231,76,60,.18);
    border-color: rgba(231,76,60,.45);
  }

  @keyframes spin{ to{ transform: rotate(360deg); } }

  /* Fade the poster card away on success */
  .wl-poster.vanish{
    opacity:0; transform:scale(.96);
    filter:saturate(.7) brightness(.9);
    transition: opacity .28s ease, transform .28s ease, filter .28s ease;
    pointer-events:none;
  }

  /* Ensure delete icon is on top and clickable inside a poster */
  .wl-poster { position: relative; } /* already present, fine to duplicate */
  .wl-del.icon-btn{
    position: absolute;
    top: 8px;
    right: 8px;        /* move to top-right */
    z-index: 6;        /* above overlays */
    pointer-events: auto;
    padding: 0;        /* override old pill padding */
  }

  .wl-hover { pointer-events: none; } /* remove this line if you need clickable content inside the hover panel */

  /* About page  Modal */
  .modal-backdrop{ position:fixed; inset:0; z-index:9999; display:grid; place-items:center;
    background:rgba(0,0,0,.45); backdrop-filter:blur(6px); animation:fadeIn .18s ease; }
  .modal-backdrop.hidden{ display:none !important; }

  .modal-card{ width:min(560px,92vw); background:rgba(24,24,24,.9); border:1px solid rgba(255,255,255,.08);
    border-radius:16px; box-shadow:0 20px 60px rgba(0,0,0,.45); overflow:hidden; transform:scale(.98);
    animation:popIn .22s cubic-bezier(.2,.9,.2,1) forwards; }
  .modal-header,.modal-footer{ display:flex; align-items:center; justify-content:space-between;
    padding:14px 16px; background:linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,0)); }
  .modal-body{ padding:16px; }
  .title-wrap{ display:flex; gap:12px; align-items:center; }
  .app-logo{ font-size:22px; line-height:1; }
  .app-name{ font-weight:800; font-size:16px; }
  .app-sub{ color:var(--muted,#bbb); font-size:13px; }
  .btn-ghost{ background:transparent; border:1px solid rgba(255,255,255,.12); color:#fff; border-radius:10px;
    padding:6px 10px; cursor:pointer; transition:background .2s, border-color .2s, transform .12s; }
  .btn-ghost:hover{ background:rgba(255,255,255,.06); border-color:rgba(255,255,255,.2); transform:translateY(-1px); }
  .about-grid{ display:grid; grid-template-columns:1fr 2fr; gap:10px 14px; }
  .about-item .k{ color:var(--muted,#bbb); font-size:13px; }
  .about-item .v a{ color:#fff; text-decoration:none; border-bottom:1px dashed rgba(255,255,255,.35); }
  .about-item .v a:hover{ border-bottom-style:solid; }
  @media (max-width:480px){ .about-grid{ grid-template-columns:1fr; } .modal-header,.modal-footer{ flex-wrap:wrap; gap:8px; } }
  @keyframes popIn{ to{ transform:scale(1); } }
  @keyframes fadeIn{ from{ opacity:0 } to{ opacity:1 } }

/* Brand palette */
:root{
  --plex:  #e5a00d;   /* Plex */
  --simkl: #00b7eb;   /* SIMKL (cyan) */
  --tmdb:  #01d277;   /* TMDb */
}

/* Let section headers show right icon and colored left edge */
.section > .head{
  position: relative;
  padding-right: 44px;            /* space for the logo on the right */
}

/* Brand left edge + small indent */
#sec-plex  > .head{ border-left: 3px solid var(--plex);  padding-left: 10px; }
#sec-simkl > .head{ border-left: 3px solid var(--simkl); padding-left: 10px; }
#sec-tmdb  > .head{ border-left: 3px solid var(--tmdb);  padding-left: 10px; }


/* Per-brand accents */
.brand-ico.plex {  color: var(--plex);  background: rgba(229,160,13,.12);  border-color: rgba(229,160,13,.35); }
.brand-ico.simkl{  color: var(--simkl); background: rgba(0,183,235,.12);   border-color: rgba(0,183,235,.35); }
.brand-ico.tmdb {  color: var(--tmdb);  background: rgba(1,210,119,.12);   border-color: rgba(1,210,119,.35); }

/* TMDb wordmark badge */
.brand-ico.tmdb .tmdb-box{
  display:inline-block;
  padding: 0 4px;
  border-radius: 4px;
  line-height: 16px;
  font-size: 11px;
  font-weight: 800;
  color: #0a0;                      /* inner text color on bright bg */
  color: #0e3;                      /* tweak if needed */
  color: #0c4;                      /* final choice will inherit fine */
  color: #0;                         /* ensure contrast if your theme is very dark */
  color: var(--tmdb);
  border: 1px solid currentColor;
  background: rgba(1,210,119,.10);
}

/* Remove horizontal scrollbar in the details log */
#det-log{
  overflow-x: hidden;     /* hide horizontal bar */
  overflow-y: auto;       /* keep vertical scroll */
  white-space: pre-wrap;  /* wrap lines (already set on .log, keep it) */
  overflow-wrap: anywhere;/* break very long tokens/URLs */
  word-break: break-word; /* fallback for older browsers */
}

/* ANSI styles for the log */
.log .b { font-weight: 700; }
.log .u { text-decoration: underline; }

/* 8 basic + 8 bright foregrounds */
.log .c30{ color:#6e7681 } .log .c31{ color:#ff7b72 } .log .c32{ color:#3fb950 } .log .c33{ color:#d29922 }
.log .c34{ color:#58a6ff } .log .c35{ color:#bc8cff } .log .c36{ color:#76e3ea } .log .c37{ color:#f0f6fc }
.log .c90{ color:#8b949e } .log .c91{ color:#ff7b72 } .log .c92{ color:#3fb950 } .log .c93{ color:#d29922 }
.log .c94{ color:#58a6ff } .log .c95{ color:#bc8cff } .log .c96{ color:#76e3ea } .log .c97{ color:#ffffff }

.log .bg40{ background:rgba(110,118,129,.15) } .log .bg41{ background:rgba(255,123,114,.15) }
.log .bg42{ background:rgba(63,185,80,.15) }  .log .bg43{ background:rgba(210,153,34,.15) }
.log .bg44{ background:rgba(88,166,255,.15) } .log .bg45{ background:rgba(188,140,255,.15) }
.log .bg46{ background:rgba(118,227,234,.15) } .log .bg47{ background:rgba(240,246,252,.15) }
.log .bg100{ background:rgba(139,148,158,.20) } .log .bg101{ background:rgba(255,123,114,.22) }
.log .bg102{ background:rgba(63,185,80,.22) }  .log .bg103{ background:rgba(210,153,34,.22) }
.log .bg104{ background:rgba(88,166,255,.22) } .log .bg105{ background:rgba(188,140,255,.22) }
.log .bg106{ background:rgba(118,227,234,.22) } .log .bg107{ background:rgba(255,255,255,.22) }

/* Statistics  */

/* Layout */
.stats-modern{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:center}
@media (max-width:900px){ .stats-modern{grid-template-columns:1fr} }

/* Left: big */
.stats-modern .now .label{font-size:11px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase}
.stats-modern .value{font-variant-numeric:tabular-nums;font-weight:900;font-size:52px;line-height:1}
.stats-modern .chip.trend{
  margin-top:8px;display:inline-flex;align-items:center;gap:8px;
  padding:8px 12px;border-radius:999px;border:1px solid var(--border);
  background:#0b0b16;color:#dfe6ff;font-weight:700
}
.chip.trend.up{border-color:#2ecc71;color:#c8ffe6;box-shadow:0 0 12px rgba(46,204,113,.25)}
.chip.trend.down{border-color:#ff6b6b;color:#ffd7d7;box-shadow:0 0 12px rgba(255,77,79,.20)}
.chip.trend.flat{border-color:#2a2a3a;color:#aeb6c2}

/* Right: facts + meter */
.facts{display:grid;gap:8px;align-content:start}
.fact{display:flex;justify-content:space-between;gap:12px}
.fact .k{color:var(--muted);font-size:12px;letter-spacing:.02em}
.fact .v{font-weight:800}

/* Meter */
.stat-meter{
  position:relative;height:10px;border-radius:999px;overflow:hidden;
  border:1px solid var(--border);
  background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),#0a0a17;
}
.stat-meter::before{
  content:"";position:absolute;inset:-60% -40%;pointer-events:none;opacity:.35;
  background:
    radial-gradient(80% 40% at 0% 50%, #7c5cff33, transparent 60%),
    radial-gradient(80% 40% at 100% 50%, #2da1ff33, transparent 60%);
  filter:blur(10px);animation:meterGlow 10s ease-in-out infinite alternate;
}
@keyframes meterGlow{from{transform:translateX(-2%)}to{transform:translateX(2%)}}
#stat-fill{
  position:absolute;inset:0 auto 0 0;width:0%;
  background:linear-gradient(135deg,#7c5cff,#2da1ff);
  box-shadow:0 0 16px #7c5cff44 inset;
  transition:width .6s cubic-bezier(.2,.8,.2,1);
}

/* Celebration ping on positive change */
#stats-card.celebrate{animation:statPop .6s cubic-bezier(.2,.9,.2,1)}
@keyframes statPop{0%{transform:scale(.99)}50%{transform:scale(1.01)}100%{transform:scale(1)}}

/* Keep position next to Synchronization */
#stats-card{
  grid-column: 2;        /* right column */
  grid-row: 1;           /* same row as #ops-card */
  align-self: stretch;   /* fill the row height */
  height: 100%;
}

main.full #stats-card,
main.single #stats-card{
  grid-column: 1;
  grid-row: auto;
  align-self: start;
  height: auto;
}

/* chips row + alt style */
.chips{display:flex;gap:8px;margin-top:8px}

/* mini legend */
.mini-legend{display:grid;grid-template-columns:auto auto 1fr auto auto 1fr;gap:6px 10px;align-items:center;margin-top:6px}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.dot.add{background:#19c37d}
.dot.del{background:#ff6b6b}
.mini-legend .l{color:var(--muted);font-size:12px}
.mini-legend .n{font-weight:800}

/* Put the glow behind the entire card */
#stats-card{ position:relative; overflow:hidden; }
#stats-card .stats-modern.v2,
#stats-card .stat-tiles{ position:relative; z-index:2; }

/* Full-card aurora: spans entire stats card, not a single column */
#stats-card .aurora{
  position:absolute;
  inset:-24% -18% -18% -18%;   /* bleed beyond edges so it “breathes” */
  pointer-events:none;
  z-index:1;
  filter:blur(18px) saturate(118%);
  opacity:.55;
}

/* tiles */
.stat-tiles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}
.tile{padding:10px 12px;border-radius:14px;border:1px solid var(--border);
  background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),#0b0b16;
  display:flex;align-items:center;justify-content:space-between}
.tile .k{color:#cdd5e0;font-size:12px;letter-spacing:.03em}
.tile .n{font-weight:900;font-variant-numeric:tabular-nums}
.tile.g1{background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),#0b101e}
.tile.g2{background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),#0c1410}
.tile.g3{background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),#160e17}

/* Grid: default is single column; use 2-col only on desktop Main */
#layout{
  display:grid;
  gap:16px;
  align-items:stretch;
}

/* 2 columns only when NOT in .single/.full */
#layout:not(.single):not(.full){
  grid-template-columns:minmax(620px,1fr) minmax(360px,420px);
}

/* Explicit single-column states */
#layout.single,
#layout.full{
  grid-template-columns:1fr;
}


/* Place cards */
#ops-card{ grid-column:1; }
#stats-card{ grid-column:2; align-self:stretch; height:100%; }

/* Watchlist preview always full width, under both cards */
#placeholder-card{ grid-column:1 / -1; }

/* Mobile: single column */
@media (max-width:1100px){
  #layout{ grid-template-columns:1fr; }
  #ops-card,#stats-card,#placeholder-card{ grid-column:1; }
}

/* Align the action row (unchanged) */
@media (min-width:1101px){
  #ops-card .chiprow{  margin-bottom: 38px; }
  #ops-card .action-row{ margin-top: 20px !important; }
  #ops-card .stepper{ margin-top: 6px; }
}

/* Stats v2 – stacking & background */
#stats-card.card { overflow: hidden; }     /* clip inside rounded corners */
#stats-card { position: relative; }        /* stacking context */

#stats-card { position: relative; overflow: hidden; isolation: isolate; }

#stats-card::before{
  content:"";
  position:absolute; inset:-2px;                    /* fill the whole card */
  background: url("/assets/background.svg") no-repeat 50% 96% / cover;
  opacity:.14;                                      /* subtle */
  mix-blend-mode: screen;
  pointer-events:none;
}

/* content sits above the background */
#stats-card .stats-modern.v2,
#stats-card .stat-tiles { position: relative; z-index: 1; }

#stats-card .stat-tiles{
  display: grid;
  grid-template-columns: repeat(2, minmax(0,1fr));
  gap: 10px;
}
@media (max-width:560px){
  #stats-card .stat-tiles{ grid-template-columns: 1fr; }
}

/* Make "New" and "Removed" tiles more transparent */
#stats-card .tile.g3{
  background:
    linear-gradient(180deg, rgba(255,255,255,.02), transparent),
    rgba(11,11,22,0.32) !important;
  border-color: rgba(255,255,255,.12) !important;
  backdrop-filter: blur(2px) saturate(110%);
}
/* Keep labels strongly readable */
#stats-card .tile.g3 .k{ color:#dfe3ee; }
#stats-card .tile.g3 .n{ color:#fff; }

:root{
  --plex-rgb: 229,160,13;   /* Plex */
  --simkl-rgb: 0,194,255;   /* SIMKL */
}

/* Transparent tiles, like New/Removed */
.tile.plex,
.tile.simkl{
  background: transparent;
  /* very thin brand edge */
  border: 1px solid rgba(var(--plex-rgb), .35);
  box-shadow: 0 0 6px rgba(var(--plex-rgb), .18);
}
.tile.simkl{
  border-color: rgba(var(--simkl-rgb), .35);
  box-shadow: 0 0 6px rgba(var(--simkl-rgb), .18);
}

/* keep text readable; no heavy glow */
.tile.plex .k, .tile.plex .n,
.tile.simkl .k, .tile.simkl .n{
  color: var(--fg, #fff);
  text-shadow: none;
}

/* gentle value-change pop (re-usable for all tiles) */
.n.bump {
  animation: valuePop .35s ease-out;
}
@keyframes valuePop {
  0%   { transform: translateY(0) scale(1);   filter: none; opacity: .9; }
  40%  { transform: translateY(-1px) scale(1.08); filter: drop-shadow(0 0 6px rgba(255,255,255,.25)); }
  100% { transform: translateY(0) scale(1);   filter: none; opacity: 1; }
}

/* --- Insights styles --- */
.stat-block { margin-top: 14px; padding: 12px; border-radius: 16px; background: rgba(255,255,255,0.03); box-shadow: 0 0 0 1px rgba(255,255,255,0.04) inset; }
.stat-block-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }
.pill { padding:3px 8px; border-radius:999px; font-size:12px; letter-spacing:.2px; background: linear-gradient(90deg,var(--grad1,#7c5cff),var(--grad2,#2de2ff)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:700; }
.muted { opacity:.6; font-size:12px; }
.ghost { background:transparent; border:none; color:inherit; opacity:.6; cursor:pointer; }
.ghost:hover { opacity:1; }

/* Sparkline */
.sparkline { height: 64px; width: 100%; position: relative; }
.sparkline svg { width:100%; height:100%; display:block; }
.sparkline path.line { fill:none; stroke-width:2; filter: drop-shadow(0 0 6px rgba(124,92,255,.6)); stroke: url(#spark-grad); }
.sparkline .dot { r:2.5; opacity:.9; }
.sparkline .dot:hover { transform: scale(1.6); }

/* History list */
.history-list { display:grid; gap:8px; }
.history-item { display:flex; align-items:center; justify-content:space-between; padding:10px 12px; border-radius:12px; background: rgba(255,255,255,.02); border:1px solid rgba(255,255,255,.06); }
.history-meta { display:flex; gap:10px; align-items:center; font-size:12px; opacity:.9; }
.badge { padding:2px 8px; border-radius:999px; font-size:11px; border:1px solid rgba(255,255,255,.12); }
.badge.ok { border-color: rgba(46, 204, 113, .5); }
.badge.warn { border-color: rgba(231, 76, 60, .5); }

/* Watchtime */
.watchtime { display:flex; align-items:baseline; gap:10px; }
.watchtime .big { font-size:28px; font-weight:800; letter-spacing:.2px; background: linear-gradient(90deg,var(--grad1,#7c5cff),var(--grad2,#2de2ff)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.watchtime .units { font-size:12px; opacity:.8; }
.micro-note { margin-top:6px; font-size:11px; opacity:.6; }

/* Subtle appear */
.stat-block { animation: fadeUp .35s ease-out both; }
@keyframes fadeUp { from { opacity:0; transform: translateY(6px) } to { opacity:1; transform:none } }

/* collapse Insights when details are not open */
#stats-card.collapsed .stat-block { display: none; }
#stats-card { transition: filter .2s ease; }
#stats-card.expanded { filter: brightness(1.02); }

/* white text - Insight Modules*/
.pill.plain {
  background: none !important;
  -webkit-background-clip: unset !important;
  -webkit-text-fill-color: unset !important;
  color: #fff !important;
}

#plex_pin {
  font-size: 2rem;        /* make digits bigger */
  font-weight: 700;       /* bold */
  letter-spacing: 0.2em;  /* spaced digits */
  color: #fff;            /* white text */
  text-align: center;     /* center align */
  max-width: 7ch;   /* fits up to 5 characters + spacing */
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
    <div id="tab-about" class="tab" onclick="openAbout()">About</div>
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
        <div id="update-banner" class="hidden">
          <span id="update-text">A new version is available.</span>
          <a id="update-link" href="https://github.com/cenodude/plex-simkl-watchlist-sync/releases"
            target="_blank" rel="noopener noreferrer">Get update</a>
        </div>
        <button id="btn-status-refresh" class="iconbtn" title="Re-check Plex &amp; SIMKL status" aria-label="Refresh status" onclick="manualRefreshStatus()">
          <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
            <path d="M21 12a9 9 0 1 1-2.64-6.36" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M21 5v5h-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>

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
      <span id="st-update" class="badge upd hidden"></span>
    </div>

    <div class="sep"></div>
    <div class="action-row">
      <div class="action-buttons">
        <button id="run" class="btn acc" onclick="runSync()"><span class="label">Synchronize</span><span class="spinner" aria-hidden="true"></span></button>
        <button class="btn" onclick="toggleDetails()">View details</button>
        <button class="btn" onclick="copySummary(this)">Copy summary</button>
        <button class="btn" onclick="downloadSummary()">Download report</button>
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
        <div class="det-left">
          <div class="title" style="margin-bottom:6px;font-weight:700">Sync output</div>
          <pre id="det-log" class="log"></pre>
        </div>
        <div class="det-right">
          <div class="meta-card">
            <div class="meta-grid">
              <div class="meta-label">Module</div>
              <div class="meta-value"><span id="det-cmd" class="pillvalue truncate">–</span></div>
              <div class="meta-label">Version</div>
              <div class="meta-value"><span id="det-ver" class="pillvalue">–</span></div>
              <div class="meta-label">Started</div>
              <div class="meta-value"><span id="det-start" class="pillvalue mono">–</span></div>
              <div class="meta-label">Finished</div>
              <div class="meta-value"><span id="det-finish" class="pillvalue mono">–</span></div>
            </div>
            <div class="meta-actions">
              <button class="btn" onclick="copySummary(this)">Copy summary</button>
              <button class="btn" onclick="downloadSummary()">Download</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- MAIN: Statistics card -->
  <section id="stats-card" class="card collapsed">
    <div class="title">Statistics</div>

    <div class="stats-modern v2">
      <div class="now">
        <div class="label">Now</div>
        <div id="stat-now" class="value" data-v="0">0</div>
        <div class="chips">
          <span id="trend-week" class="chip trend flat">no change</span>
        </div>
      </div>

      <div class="facts">
        <div class="fact"><span class="k">Last Week</span><span id="stat-week" class="v" data-v="0">0</span></div>
        <div class="fact"><span class="k">Last Month</span><span id="stat-month" class="v" data-v="0">0</span></div>

        <div class="mini-legend">
          <span class="dot add"></span><span class="l">Added</span><span id="stat-added" class="n">0</span>
          <span class="dot del"></span><span class="l">Removed</span><span id="stat-removed" class="n">0</span>
        </div>

        <div class="stat-meter" aria-hidden="true"><span id="stat-fill"></span></div>
      </div>
    </div>

    <div class="stat-tiles">
      <div class="tile g3" id="tile-new" hidden>
        <div class="k">New</div><div class="n" id="stat-new">0</div>
      </div>
      <div class="tile g3" id="tile-del" hidden>
        <div class="k">Removed</div><div class="n" id="stat-del">0</div>
      </div>

      <div class="tile plex" id="tile-plex">
        <div class="k">Plex</div><div class="n" id="stat-plex">0</div>
      </div>
      <div class="tile simkl" id="tile-simkl">
        <div class="k">SIMKL</div><div class="n" id="stat-simkl">0</div>
      </div>
    </div>

    <!-- Insights: Recent syncs -->
    <div class="stat-block">
      <div class="stat-block-header">
        <span class="pill plain">Recent syncs</span>
        <button class="ghost refresh-insights" onclick="refreshInsights()" title="Refresh">⟲</button>
      </div>
      <div id="sync-history" class="history-list"></div>
    </div>

    <!-- Insights: Trend 
    <div class="stat-block">
      <div class="stat-block-header">
        <span class="pill plain">Trend</span>
        <span class="muted">Last 30 samples</span>
      </div>
      <div id="sparkline" class="sparkline"></div>
    </div>
    -->
	
    <!-- TMDB estimated watch time
    Insights: Estimated watch time 
    <div class="stat-block">
      <div class="stat-block-header"><span class="pill plain">Estimated watch time</span></div>
      <div id="watchtime" class="watchtime"></div>
      <div class="micro-note" id="watchtime-note"></div>
    </div>
    -->

  </section>

  <!-- MAIN: Watchlist Preview (carousel) -->
  <section id="placeholder-card" class="card hidden">
    <div class="title">Watchlist Preview</div>

    <div id="wall-msg" class="wall-msg">Loading…</div>

    <div class="wall-wrap">
      <!-- gradient edges -->
      <div id="edgeL" class="edge left"></div>
      <div id="edgeR" class="edge right"></div>

      <!-- posters row -->
      <div id="poster-row" class="row-scroll" aria-label="Watchlist preview"></div>

      <!-- nav buttons -->
      <button class="nav prev" type="button" onclick="scrollWall(-1)" aria-label="Scroll left">‹</button>
      <button class="nav next" type="button" onclick="scrollWall(1)"  aria-label="Scroll right">›</button>
    </div>
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

    <div class="section" id="sec-troubleshoot">
      <div class="head" onclick="toggleSection('sec-troubleshoot')"><span class="chev">▶</span><strong>Troubleshoot</strong></div>
      <div class="body">
        <div class="sub">Use these actions to reset application state. They are safe but cannot be undone.</div>
        <div><label>Debug</label><select id="debug"><option value="false">off</option><option value="true">on</option></select></div>
        <div class="chiprow">
          <button class="btn danger" onclick="clearState()">Clear State</button>
          <button class="btn danger" onclick="clearCache()">Clear Cache</button>
          <button class="btn danger" onclick="resetStats()">Reset Statistics</button>
        </div>
        <div id="tb_msg" class="msg ok hidden">Done ✓</div>
      </div>
    </div>

    <div class="section" id="sec-auth">
      <div class="head" onclick="toggleSection('sec-auth')">
        <span class="chev">▶</span><strong>Authentication</strong>
      </div>
      <div class="body">

        <!-- PLEX -->
        <div class="section" id="sec-plex">
          <div class="head" onclick="toggleSection('sec-plex')">
            <span class="chev"></span><strong>Plex</strong>
          </div>
          <div class="body">
            <div class="grid2">
              <div>
                <label>Current token</label>
                <div style="display:flex;gap:8px">
                  <input id="plex_token" placeholder="empty = not set">
                  <button id="btn-copy-plex-token" class="btn copy" onclick="copyInputValue('plex_token', this)">Copy</button>
                </div>
              </div>
              <div>
                <label>PIN</label>
                <div style="display:flex;gap:8px">
                  <input id="plex_pin" placeholder="" readonly>
                  <button id="btn-copy-plex-pin" class="btn copy" onclick="copyInputValue('plex_pin', this)">Copy</button>
                </div>
              </div>
            </div>
            <div style="display:flex;gap:8px">
              <button class="btn" onclick="requestPlexPin()">Request Token</button>
              <div style="align-self:center;color:var(--muted)">Opens plex.tv/link (PIN copied to clipboard)</div>
            </div>

            <div id="plex_msg" class="msg ok hidden">Successfully retrieved token</div>
            <div class="sep"></div>
          </div>
        </div>

        <!-- SIMKL -->
        <div class="section" id="sec-simkl">
          <div class="head" onclick="toggleSection('sec-simkl')">
            <span class="chev"></span><strong>SIMKL</strong>
          </div>
          <div class="body">
            <div class="grid2">
              <div>
                <label>Client ID</label>
                <input id="simkl_client_id" placeholder="Your SIMKL client id"
                      oninput="updateSimklButtonState(); updateSimklHint();">
              </div>
              <div>
                <label>Client Secret</label>
                <input id="simkl_client_secret" placeholder="Your SIMKL client secret"
                      oninput="updateSimklButtonState(); updateSimklHint();">
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
              <div>
                <label>Access token</label>
                <input id="simkl_access_token" readonly placeholder="empty = not set">
              </div>
            </div>

            <div id="simkl_msg" class="msg ok hidden">Successfully retrieved token</div>
            <div class="sep"></div>
          </div>
        </div>

        <!-- TMDb -->
        <div class="section" id="sec-tmdb">
          <div class="head" onclick="toggleSection('sec-tmdb')">
            <span class="chev"></span><strong>TMDb</strong>
          </div>
          <div class="body">
            <div class="grid2">
              <div style="grid-column:1 / -1">
                <label>API key</label>
                <input id="tmdb_api_key" placeholder="Your TMDb API key"
                      oninput="this.dataset.dirty='1'; updateTmdbHint()">
                <div id="tmdb_hint" class="msg warn hidden">
                  TMDb is optional but recommended to enrich posters & metadata in the preview.
                  Get an API key at
                  <a href="https://www.themoviedb.org/settings/api" target="_blank" rel="noopener">TMDb API settings</a>.
                </div>
                <div class="sub">This product uses the TMDb API but is not endorsed by TMDb.</div>
              </div>
            </div>
            <div class="sep"></div>
          </div>
        </div>


      </div>
    </div>

    <div class="footer">
      <button class="btn btn-save" onclick="saveSettings()"><span class="btn-ic">✔</span> Save</button>
      <button class="btn btn-exit" onclick="showTab('main')"><span class="btn-ic">↩</span> Exit</button>
      <span id="save_msg" class="msg ok hidden">Settings saved ✓</span>
    </div>
  </section>

<!-- Debug log -->
<aside id="log-panel" class="card hidden">
  <div class="title">Raw log (Debug)</div>
  <div id="log" class="log"></div>
</aside>

  <!-- About modal -->
  <div id="about-backdrop" class="modal-backdrop hidden" onclick="closeAbout(event)">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="about-title" onclick="event.stopPropagation()">
      <div class="modal-header">
        <div class="title-wrap">
          <div class="app-logo">🎬</div>
          <div>
            <div id="about-title" class="app-name">Plex ⇄ SIMKL Watchlist Sync</div>
            <div class="app-sub"><span id="about-version">Version …</span></div>
          </div>
        </div>
        <button class="btn-ghost" aria-label="Close" onclick="closeAbout()">✕</button>
      </div>

      <div class="modal-body">
        <div class="about-grid">
          <div class="about-item">
            <div class="k">Repository</div>
            <div class="v"><a id="about-repo" href="https://github.com/cenodude/plex-simkl-watchlist-sync" target="_blank" rel="noopener">GitHub</a></div>
          </div>
          <div class="about-item">
            <div class="k">Latest Release</div>
            <div class="v"><a id="about-latest" href="#" target="_blank" rel="noopener">—</a></div>
          </div>
          <div class="about-item">
            <div class="k">Update</div>
            <div class="v"><span id="about-update" class="badge upd hidden"></span></div>
          </div>
        </div>

        <div class="sep"></div>
        <div class="sub" role="note">
          <strong>Disclaimer:</strong> This is open-source software provided “as is,” without any warranties or guarantees. Use at your own risk.
          This project is not affiliated with, sponsored by, or endorsed by Plex, Inc., SIMKL, or The Movie Database (TMDb).
          All product names, logos, and brands are property of their respective owners.
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn" onclick="window.open(document.getElementById('about-latest').href,'_blank')">Open Releases</button>
        <button class="btn alt" onclick="closeAbout()">Close</button>
      </div>
    </div>
  </div>

</main>

<script>
  /* ====== Globals ====== */
  let lastStatusMs = 0;
  const STATUS_MIN_INTERVAL = 120000; // ms

  let busy=false, esDet=null, esSum=null, plexPoll=null, simklPoll=null, appDebug=false, currentSummary=null;
  let detStickBottom = true;  // auto-stick to bottom voor details-log
  let wallLoaded=false, _lastSyncEpoch=null, _wasRunning=false;
  window._ui = { status: null, summary: null };

  /* ====== Utilities ====== */
  function computeRedirectURI(){ return location.origin + '/callback'; }

  function flashCopy(btn, ok, msg){
    if (!btn) { if(!ok) alert(msg || 'Copy failed'); return; }
    const old = btn.textContent;
    btn.disabled = true;
    btn.textContent = ok ? 'Copied ✓' : (msg || 'Copy failed');
    setTimeout(()=>{ btn.textContent = old; btn.disabled = false; }, 1200);
  }

  function setRunProgress(pct){
    const btn = document.getElementById('run');
    if (!btn) return;
    const p = Math.max(0, Math.min(100, Math.floor(pct)));
    btn.style.setProperty('--prog', String(p));
  }

  function startRunVisuals(indeterminate = true){
    const btn = document.getElementById('run');
    if (!btn) return;
    btn.classList.add('loading');
    btn.classList.toggle('indet', !!indeterminate);
    if (indeterminate) setRunProgress(8);
  }

  function stopRunVisuals(){
    const btn = document.getElementById('run');
    if (!btn) return;
    setRunProgress(100);
    btn.classList.remove('indet');
    setTimeout(() => { btn.classList.remove('loading'); setRunProgress(0); }, 700);
  }

  function updateProgressFromTimeline(tl){
    const order = ['start','pre','post','done'];
    let done = 0;
    for (const k of order){ if (tl && tl[k]) done++; }
    let pct = (done / order.length) * 100;
    if (pct > 0 && pct < 15) pct = 15;
    setRunProgress(pct);
  }

  function recomputeRunDisabled() {
    const btn = document.getElementById('run');
    if (!btn) return;
    const busyNow = !!window.busy;
    const canRun = !(window._ui?.status) ? true : !!window._ui.status.can_run;
    const running = !!(window._ui?.summary && window._ui.summary.running);
    btn.disabled = busyNow || running || !canRun;
  }

  function setTimeline(tl){ ['start','pre','post','done'].forEach(k=>{ document.getElementById('tl-'+k).classList.toggle('on', !!(tl && tl[k])); }); }

  function setSyncHeader(status, msg){
    const icon = document.getElementById('sync-icon');
    icon.classList.remove('sync-ok','sync-warn','sync-bad'); icon.classList.add(status);
    document.getElementById('sync-status-text').textContent = msg;
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

  /* ====== About modal ====== */
  async function openAbout(){
    try{
      // Bust any cache so we don't show an old payload
      const r = await fetch('/api/version?cb=' + Date.now(), { cache: 'no-store' });
      const j = r.ok ? await r.json() : {};

      const cur    = (j.current ?? '0.0.0').toString().trim();
      const latest = (j.latest  ?? '').toString().trim() || null;
      const url    = j.html_url || 'https://github.com/cenodude/plex-simkl-watchlist-sync/releases';
      const upd    = !!j.update_available;

      // "Version x.y.z" — from CURRENT
      const verEl = document.getElementById('about-version');
      if (verEl){
        verEl.textContent = `Version ${cur}`;
        verEl.dataset.version = cur; // guard against later accidental overwrites
      }

      // If you also show a version elsewhere, keep it in sync (safe no-op if missing)
      const headerVer = document.getElementById('app-version');
      if (headerVer){
        headerVer.textContent = `Version ${cur}`;
        headerVer.dataset.version = cur;
      }

      // Latest release link/label (separate from current)
      const relEl = document.getElementById('about-latest');
      if (relEl){
        relEl.href = url;
        relEl.textContent = latest ? `v${latest}` : 'Releases';
        relEl.setAttribute('aria-label', latest ? `Latest release v${latest}` : 'Releases');
      }

      // Update badge
      const updEl = document.getElementById('about-update');
      if (updEl){
        updEl.classList.add('badge','upd');
        if (upd && latest){
          updEl.textContent = `Update ${latest} available`;
          updEl.classList.remove('hidden','reveal');
          void updEl.offsetWidth; // restart CSS animation
          updEl.classList.add('reveal');
        } else {
          updEl.textContent = '';
          updEl.classList.add('hidden');
          updEl.classList.remove('reveal');
        }
      }
    } catch(_) {}
    document.getElementById('about-backdrop')?.classList.remove('hidden');
  }

  function closeAbout(ev){
    if (ev && ev.type === 'click' && ev.currentTarget !== ev.target) return; // ignore clicks inside card
    document.getElementById('about-backdrop')?.classList.add('hidden');
  }

  document.addEventListener('keydown', (e)=>{ if (e.key === 'Escape') closeAbout(); });


  /* ====== Tabs ====== */
  async function showTab(n) {
    const pageSettings  = document.getElementById('page-settings');
    const pageWatchlist = document.getElementById('page-watchlist');
    const logPanel      = document.getElementById('log-panel');
    const layout        = document.getElementById('layout');
    const statsCard     = document.getElementById('stats-card');

    document.getElementById('tab-main')     ?.classList.toggle('active', n === 'main');
    document.getElementById('tab-watchlist')?.classList.toggle('active', n === 'watchlist');
    document.getElementById('tab-settings') ?.classList.toggle('active', n === 'settings');

    document.getElementById('ops-card')        ?.classList.toggle('hidden', n !== 'main');
    document.getElementById('placeholder-card')?.classList.toggle('hidden', n !== 'main');
    statsCard                                   ?.classList.toggle('hidden', n !== 'main');
    pageWatchlist?.classList.toggle('hidden', n !== 'watchlist');
    pageSettings ?.classList.toggle('hidden', n !== 'settings');

    const hasStats = !!(statsCard && !statsCard.classList.contains('hidden'));
    if (n === 'main') {
      layout.classList.remove('single');
      layout.classList.toggle('full', !appDebug && !hasStats);
      refreshStatus();
      if (!esSum) openSummaryStream();
      await updatePreviewVisibility();
      refreshSchedulingBanner();
      refreshStats(true);
    } else {
      layout.classList.add('single');
      layout.classList.remove('full');
      logPanel.classList.add('hidden');
      if (n === 'watchlist') { loadWatchlist(); }
      else { document.getElementById('sec-auth')?.classList.add('open'); await loadConfig();
            updateTmdbHint?.(); updateSimklHint?.(); updateSimklButtonState?.(); loadScheduling?.(); }
    }
  }



  function toggleSection(id){ document.getElementById(id).classList.toggle('open'); }

  /* ====== Run (synchronize) ====== */
  function setBusy(v){ busy = v; recomputeRunDisabled(); }

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
        await updateWatchlistPreview();
      }
    } catch (e) {
      setSyncHeader('sync-bad', 'Failed to reach server');
    } finally {
      setBusy(false);
      recomputeRunDisabled();
      refreshStatus();
    }
  }

  /* Version check + update notification */
  const UPDATE_CHECK_INTERVAL_MS = 12 * 60 * 60 * 1000;
  let _updInfo = null;

  function openUpdateModal(){
    if(!_updInfo) return;
    document.getElementById('upd-modal').classList.remove('hidden');
    document.getElementById('upd-title').textContent = `v${_updInfo.latest}`;
    document.getElementById('upd-notes').textContent = _updInfo.notes || '(No release notes)';
    document.getElementById('upd-link').href = _updInfo.url || '#';
  }
  function closeUpdateModal(){ document.getElementById('upd-modal').classList.add('hidden'); }
  function dismissUpdate(){
    if(_updInfo?.latest){ localStorage.setItem('dismissed_version', _updInfo.latest); }
    document.getElementById('upd-pill').classList.add('hidden');
    closeUpdateModal();
  }

  /* expanded insight Statistics */
  function setStatsExpanded(expanded){
    const sc = document.getElementById('stats-card');
    if(!sc) return;
    sc.classList.toggle('collapsed', !expanded);
    sc.classList.toggle('expanded', !!expanded);
    if (expanded) { try { refreshInsights(); } catch(e){} }
  }

  function isElementOpen(el){
    if (!el) return false;
    // consider "open"/"expanded"/"show" class OR visibility/height as open
    const c = el.classList || {};
    if (c.contains?.('open') || c.contains?.('expanded') || c.contains?.('show')) return true;
    const style = window.getComputedStyle(el);
    return !(style.display === 'none' || style.visibility === 'hidden' || el.offsetHeight === 0);
  }

  function findDetailsButton(){
    // try common IDs/classes first
    return document.getElementById('btn-details')
        || document.querySelector('[data-action="details"], .btn-details')
        || Array.from(document.querySelectorAll('button'))
            .find(b => (b.textContent || '').trim().toLowerCase() === 'view details');
  }

  function findDetailsPanel(){
    // adapt to your DOM: try several likely targets
    return document.getElementById('sync-output')
        || document.getElementById('details')
        || document.querySelector('#sync-log, .sync-output, [data-pane="details"]');
  }

  function wireDetailsToStats(){
    const btn = findDetailsButton();
    const panel = findDetailsPanel();

    // set initial state based on whether details are open at load
    setStatsExpanded(isElementOpen(panel));

    if (btn){
      btn.addEventListener('click', () => {
        // wait a tick for the panel to toggle
        setTimeout(() => setStatsExpanded(isElementOpen(panel)), 50);
      });
    }

    // optional: collapse stats when starting a new sync
    const syncBtn = document.getElementById('btn-sync') 
                || document.querySelector('[data-action="sync"], .btn-sync');
    if (syncBtn){
      syncBtn.addEventListener('click', () => setStatsExpanded(false));
    }
  }

  document.addEventListener('DOMContentLoaded', wireDetailsToStats);

  // BLOCK INSIGHT
  async function fetchJSON(u){ const r = await fetch(u, {cache: 'no-store'}); return r.ok ? r.json() : null; }
  

  async function refreshInsights(){
    const data = await fetchJSON('/api/insights?limit_samples=60&history=3');
    if(!data) return;

    // 1) Sparkline
    renderSparkline('sparkline', data.series || []);

    // 3) History
    const hist = data.history || [];
    const hEl = document.getElementById('sync-history');
    hEl.innerHTML = hist.map(row => {
      const dur = (row.duration_sec!=null) ? (row.duration_sec.toFixed ? row.duration_sec.toFixed(1) : row.duration_sec) : '—';
      const added = (row.added ?? '—');
      const removed = (row.removed ?? '—');
      const badgeClass = (String(row.result||'').toUpperCase()==='EQUAL') ? 'ok' : 'warn';
      const when = row.finished_at || row.started_at || '';
      return `
        <div class="history-item">
          <div class="history-meta">
            <span class="badge ${badgeClass}">${row.result || '—'}</span>
            <span>${when}</span>
            <span>⏱ ${dur}s</span>
          </div>
          <div class="history-meta">
            <span class="badge">+${added}</span>
            <span class="badge">-${removed}</span>
            <span class="badge">P:${row.plex_post ?? '—'}</span>
            <span class="badge">S:${row.simkl_post ?? '—'}</span>
          </div>
        </div>`;
    }).join('') || `<div class="history-item"><div class="history-meta">No history yet</div></div>`;

    // 6) Watchtime
    const wt = data.watchtime || {minutes:0, movies:0, shows:0, method:'fallback'};
    const wEl = document.getElementById('watchtime');
    const note = document.getElementById('watchtime-note');
    wEl.innerHTML = `
      <div class="big">≈ ${wt.hours}</div>
      <div class="units">hrs <span style="opacity:.6">(${wt.days} days)</span><br>
        <span style="opacity:.8">${wt.movies} movies • ${wt.shows} shows</span>
      </div>`;
    note.textContent = (wt.method==='tmdb') ? 'Based on TMDb runtimes' :
                      (wt.method==='mixed') ? 'TMDb + defaults (115/45 min)' :
                      'Defaults used (115/45 min)';
  }

  // lightweight SVG sparkline with neon gradient
  function renderSparkline(id, points){
    const el = document.getElementById(id);
    if(!el){ return; }
    if(!points.length){ el.innerHTML = `<div class="muted">No data yet</div>`; return; }

    const w = el.clientWidth || 260, h = el.clientHeight || 64, pad=4;
    const xs = points.map(p=>Number(p.ts)||0);
    const ys = points.map(p=>Number(p.count)||0);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const x = t => (maxX===minX)? pad : pad + (w-2*pad) * (t-minX)/(maxX-minX);
    const y = v => (maxY===minY)? (h/2) : (h-pad) - (h-2*pad) * (v-minY)/(maxY-minY);

    const d = points.map((p,i)=> (i? 'L':'M') + x(p.ts) + ',' + y(p.count)).join(' ');
    const dots = points.map(p=> `<circle class="dot" cx="${x(p.ts)}" cy="${y(p.count)}"></circle>`).join('');
    el.innerHTML = `
    <svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
      <defs>
        <linearGradient id="spark-grad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="var(--grad1,#7c5cff)"/>
          <stop offset="1" stop-color="var(--grad2,#2de2ff)"/>
        </linearGradient>
      </defs>
      <path class="line" d="${d}"></path>
      ${dots}
    </svg>`;
  }

  document.addEventListener('DOMContentLoaded', refreshInsights);


async function checkForUpdate() {
  try {
    const r = await fetch('/api/version', { cache: 'no-store' });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const j = await r.json();

    const cur     = j.current || '0.0.0';
    const latest  = j.latest  || null;
    const url     = j.html_url || 'https://github.com/cenodude/plex-simkl-watchlist-sync/releases';
    const hasUpdate = !!j.update_available;

    // Update the "Version x.y.z" label (if present)
    const vEl = document.getElementById('app-version');
    if (vEl) vEl.textContent = `Version ${cur}`;

    // Update badge (right side)
    const updEl = document.getElementById('st-update');
    if (!updEl) return;

    // Make sure it has the badge classes (harmless if already present)
    updEl.classList.add('badge','upd');

    if (hasUpdate && latest) {
      // Only re-animate if the version changed since last check
      const prev = updEl.dataset.lastLatest || '';
      const changed = (latest !== prev);

      updEl.innerHTML = `<a href="${url}" target="_blank" rel="noopener" title="Open release page">
                           Update ${latest} available
                         </a>`;
      updEl.setAttribute('aria-label', `Update ${latest} available`);
      updEl.classList.remove('hidden');

      if (changed) {
        // store for next time
        updEl.dataset.lastLatest = latest;
        // retrigger the one-time "reveal" animation
        updEl.classList.remove('reveal'); // reset
        void updEl.offsetWidth;           // reflow to restart CSS animation
        updEl.classList.add('reveal');    // CSS handles pop + pulse
      }
    } else {
      // No update -> hide and clear state
      updEl.classList.add('hidden');
      updEl.classList.remove('reveal');
      updEl.removeAttribute('aria-label');
      updEl.removeAttribute('data-last-latest');
      updEl.textContent = '';
    }
  } catch (err) {
    console.debug('Version check failed:', err);
  }
}

// Run once after DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  checkForUpdate();
  // Optional: re-check when the tab becomes visible again
  // document.addEventListener('visibilitychange', () => {
  //   if (!document.hidden) checkForUpdate();
  // });
});

  // tiny toast 
  function showToast(text, onClick){
    const toast = document.createElement('div');
    toast.className = 'msg ok';
    toast.textContent = text;
    toast.style.position = 'fixed';
    toast.style.right = '16px'; toast.style.bottom = '16px';
    toast.style.zIndex = 1000; toast.style.cursor = 'pointer';
    toast.onclick = () => { onClick && onClick(); toast.remove(); }
    document.body.appendChild(toast);
    setTimeout(()=>toast.classList.add('hidden'), 3000);
  }

  // call at boot, and on a timer
  checkForUpdate(true);
  setInterval(()=>checkForUpdate(false), UPDATE_CHECK_INTERVAL_MS);

  /* ====== Summary stream + details log ====== */
  function renderSummary(sum){
    currentSummary = sum;
    window._ui = window._ui || {};
    window._ui.summary = sum;

    const pp = sum.plex_post ?? sum.plex_pre;
    const sp = sum.simkl_post ?? sum.simkl_pre;
    document.getElementById('chip-plex').textContent  = (pp ?? '–');
    document.getElementById('chip-simkl').textContent = (sp ?? '–');
    document.getElementById('chip-dur').textContent   = sum.duration_sec != null ? (sum.duration_sec + 's') : '–';
    document.getElementById('chip-exit').textContent  = sum.exit_code  != null ? String(sum.exit_code)   : '–';

    if (sum.running){
      setSyncHeader('sync-warn', 'Running…');
    } else if (sum.exit_code === 0){
      setSyncHeader('sync-ok', (sum.result||'').toUpperCase()==='EQUAL' ? 'In sync ' : 'Synced ');
    } else if (sum.exit_code != null){
      setSyncHeader('sync-bad', 'Attention needed ⚠️');
    } else {
      setSyncHeader('sync-warn', 'Idle — run a sync to see results');
    }

    document.getElementById('det-cmd').textContent    = sum.cmd        || '–';
    document.getElementById('det-ver').textContent    = sum.version    || '–';
    document.getElementById('det-start').textContent  = sum.started_at || '–';
    document.getElementById('det-finish').textContent = sum.finished_at|| '–';

    const tl = sum.timeline || {};
    setTimeline(tl);
    updateProgressFromTimeline?.(tl);

    const btn = document.getElementById('run');
    if (btn){
      if (sum.running){
        btn.classList.add('glass','loading');
        if (tl.pre || tl.post || tl.done) btn.classList.remove('indet');
        else                               btn.classList.add('indet');
        if (!_wasRunning && !(tl.pre || tl.post || tl.done)) { setRunProgress?.(8); }
      } else {
        if (_wasRunning){
          setRunProgress?.(100);
          btn.classList.remove('indet');
          setTimeout(()=>{ btn.classList.remove('loading','glass'); setRunProgress?.(0); }, 700);
        } else {
          btn.classList.remove('loading','indet','glass');
          setRunProgress?.(0);
        }
      }
    }

    if (typeof recomputeRunDisabled === 'function') recomputeRunDisabled();

    if (_wasRunning && !sum.running) {
      window.wallLoaded = false;
      updatePreviewVisibility?.();
      loadWatchlist?.();
      refreshSchedulingBanner?.();
    }
    _wasRunning = !!sum.running;
  }

  function openSummaryStream(){
    esSum = new EventSource('/api/run/summary/stream');
    esSum.onmessage = (ev)=>{ try{ renderSummary(JSON.parse(ev.data)); }catch(_){} };
    fetch('/api/run/summary').then(r=>r.json()).then(renderSummary).catch(()=>{});
  }

    let _lastStatsFetch = 0;

    function _ease(t){ return t<.5 ? 2*t*t : -1+(4-2*t)*t; }
    function animateNumber(el,to){
      const from = parseInt(el.dataset.v||'0',10)||0;
      if(from===to){ el.textContent=String(to); el.dataset.v=String(to); return; }
      const dur=600, t0=performance.now();
      function step(now){
        const p=Math.min(1,(now-t0)/dur), v=Math.round(from+(to-from)*_ease(p));
        el.textContent=String(v);
        if(p<1) requestAnimationFrame(step); else el.dataset.v=String(to);
      }
      requestAnimationFrame(step);
    }

    function animateChart(now,week,month){
      const bars={
        now:document.querySelector('.bar.now'),
        week:document.querySelector('.bar.week'),
        month:document.querySelector('.bar.month'),
      };
      const max=Math.max(1,now,week,month);
      const h=v=>Math.max(.04,v/max);
      if(bars.week)  bars.week.style.transform  = `scaleY(${h(week)})`;
      if(bars.month) bars.month.style.transform = `scaleY(${h(month)})`;
      if(bars.now)   bars.now.style.transform   = `scaleY(${h(now)})`;
    }

    async function refreshStats(force=false){
      const nowT = Date.now();
      if (!force && nowT - _lastStatsFetch < 900) return;
      _lastStatsFetch = nowT;

      try{
        const j = await fetch('/api/stats', { cache:'no-store' }).then(r=>r.json());
        if (!j?.ok) return;

        const elNow = document.getElementById('stat-now');
        const elW   = document.getElementById('stat-week');
        const elM   = document.getElementById('stat-month');
        if (!elNow || !elW || !elM) return;

        const n = j.now|0, w = j.week|0, m = j.month|0;

        animateNumber(elNow, n);
        animateNumber(elW,   w);
        animateNumber(elM,   m);

        // meter
        const max = Math.max(1, n, w, m);
        const fill = document.getElementById('stat-fill');
        if (fill) fill.style.width = Math.round((n / max) * 100) + '%';

        // deltas
        const bumpOne = (delta, label) => {
          const t = document.getElementById('trend-week'); if (!t) return;
          const cls = delta>0 ? 'up' : (delta<0 ? 'down' : 'flat');
          t.className = 'chip trend ' + cls;
          t.textContent = delta === 0 ? 'no change' : `${delta>0?'+':''}${delta} vs ${label}`;
          if (cls === 'up'){ const c = document.getElementById('stats-card'); c?.classList.remove('celebrate'); void c?.offsetWidth; c?.classList.add('celebrate'); }
        };
        bumpOne(n - w, 'last week'); // or: bumpOne(n - m, 'last month')

        // optional API fields
        const by        = j.by_source || {};
        const totalAdd  = Number.isFinite(j.added)   ? j.added   : null; // all-time totals
        const totalRem  = Number.isFinite(j.removed) ? j.removed : null;
        const lastAdd   = Number.isFinite(j.new)     ? j.new     : null; // last run only
        const lastRem   = Number.isFinite(j.del)     ? j.del     : null;

        // legend numbers (all-time)
        const setTxt = (id, val) => {
          const el = document.getElementById(id);
          if (el) el.textContent = String(val ?? 0);
        };
        setTxt('stat-added',   totalAdd);
        setTxt('stat-removed', totalRem);

        // tiles (last run only, auto-hide when null)
        const setTile = (tileId, numId, val) => {
          const t = document.getElementById(tileId), nEl = document.getElementById(numId);
          if (!t || !nEl) return;
          if (val == null) { t.hidden = true; return; }
          nEl.textContent = String(val); t.hidden = false;
        };
        setTile('tile-new', 'stat-new', lastAdd);
        setTile('tile-del', 'stat-del', lastRem);

        // brand totals for Plex / SIMKL (transparent tiles + subtle edge glow)
        const plexVal  = Number.isFinite(by.plex_total)  ? by.plex_total  : ((by.plex  ?? 0) + (by.both ?? 0));
        const simklVal = Number.isFinite(by.simkl_total) ? by.simkl_total : ((by.simkl ?? 0) + (by.both ?? 0));

        const elP = document.getElementById('stat-plex');
        const elS = document.getElementById('stat-simkl');

        const curP = Number(elP?.textContent || 0);
        const curS = Number(elS?.textContent || 0);

        const pop = (el) => { if (!el) return; el.classList.remove('bump'); void el.offsetWidth; el.classList.add('bump'); };

        if (elP){
          if (plexVal !== curP){ animateNumber(elP, plexVal); pop(elP); }
          else { elP.textContent = String(plexVal); }
        }
        if (elS){
          if (simklVal !== curS){ animateNumber(elS, simklVal); pop(elS); }
          else { elS.textContent = String(simklVal); }
        }

        // ensure tiles are visible
        document.getElementById('tile-plex')?.removeAttribute('hidden');
        document.getElementById('tile-simkl')?.removeAttribute('hidden');

      }catch(_){}
    }

    function _setBarValues(n,w,m){
      const bw=document.querySelector('.bar.week');
      const bm=document.querySelector('.bar.month');
      const bn=document.querySelector('.bar.now');
      if(bw) bw.dataset.v = String(w);
      if(bm) bm.dataset.v = String(m);
      if(bn) bn.dataset.v = String(n);
    }

    function _initStatsTooltip(){
      const chart = document.getElementById('stats-chart');
      const tip   = document.getElementById('stats-tip');
      if(!chart || !tip) return;

      const map = [
        {el: document.querySelector('.bar.week'),  label: 'Last Week'},
        {el: document.querySelector('.bar.month'), label: 'Last Month'},
        {el: document.querySelector('.bar.now'),   label: 'Now'},
      ];

      function show(e, label, value){
        tip.textContent = `${label}: ${value} items`;
        tip.style.left = e.offsetX + 'px';
        tip.style.top  = e.offsetY + 'px';
        tip.classList.add('show'); tip.hidden = false;
      }
      function hide(){ tip.classList.remove('show'); tip.hidden = true; }

      map.forEach(({el,label})=>{
        if(!el) return;
        el.addEventListener('mousemove', (ev)=>{
          const rect = chart.getBoundingClientRect();
          const x = ev.clientX - rect.left, y = ev.clientY - rect.top;
          show({offsetX:x,offsetY:y}, label, el.dataset.v || '0');
        });
        el.addEventListener('mouseleave', hide);
        el.addEventListener('touchstart', (ev)=>{
          const t = ev.touches[0];
          const rect = chart.getBoundingClientRect();
          show({offsetX:t.clientX-rect.left, offsetY:t.clientY-rect.top}, label, el.dataset.v || '0');
        }, {passive:true});
        el.addEventListener('touchend', ()=>{ tip.classList.remove('show'); }, {passive:true});
      });
    }

    // Call once on boot
    document.addEventListener('DOMContentLoaded', _initStatsTooltip);

  // Call at boot
  document.addEventListener('DOMContentLoaded', () => { refreshStats(true); });

  // Nudge the stats whenever the summary updates or a run finishes
  const _origRenderSummary = (typeof renderSummary === 'function') ? renderSummary : null;
  window.renderSummary = function(sum){
    if (_origRenderSummary) _origRenderSummary(sum);
    refreshStats(false);
  };


  function openDetailsLog(){
    const el = document.getElementById('det-log');
    const slider = document.getElementById('det-scrub');
    if (!el) return;
    el.innerHTML = '';
    detStickBottom = true;
    if (esDet) { try{ esDet.close(); }catch(_){} esDet = null; }

    const updateSlider = () => {
      if (!slider) return;
      const max = el.scrollHeight - el.clientHeight;
      slider.value = max <= 0 ? 100 : Math.round((el.scrollTop / max) * 100);
    };
    const updateStick = () => {
      const pad = 6; // tolerantierandje
      detStickBottom = (el.scrollTop >= (el.scrollHeight - el.clientHeight - pad));

    };

    el.addEventListener('scroll', () => { updateSlider(); updateStick(); }, { passive:true });
    if (slider){
      slider.addEventListener('input', () => {
        const max = el.scrollHeight - el.clientHeight;
        el.scrollTop = Math.round((slider.value/100) * max);
        detStickBottom = (slider.value >= 99);
      });
    }

    esDet = new EventSource('/api/logs/stream?tag=SYNC');
    esDet.onmessage = (ev) => {
      if (!ev?.data) return;
      el.insertAdjacentHTML('beforeend', ev.data + '<br>');
      if (detStickBottom) el.scrollTop = el.scrollHeight;
      updateSlider();
    };

    esDet.onerror = () => { try { esDet?.close(); } catch(_){} esDet = null; };
    requestAnimationFrame(() => { el.scrollTop = el.scrollHeight; updateSlider(); });
  }

  function closeDetailsLog(){ try { esDet?.close(); } catch(_){ } esDet=null; }
  function toggleDetails(){
    const d = document.getElementById('details');
    d.classList.toggle('hidden');
    if (!d.classList.contains('hidden')) openDetailsLog(); else closeDetailsLog();
  }
  window.addEventListener('beforeunload', closeDetailsLog);

  /* ====== Summary copy / download ====== */
  async function copySummary(btn){
    if (!window.currentSummary) {
      try { window.currentSummary = await fetch('/api/run/summary').then(r=>r.json()); }
      catch { flashCopy(btn, false, 'No summary'); return; }
    }
    const s = window.currentSummary;
    if (!s) { flashCopy(btn, false, 'No summary'); return; }

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

    let ok = false;
    try { await navigator.clipboard.writeText(text); ok = true; } catch(e) { ok = false; }
    if (!ok){
      try{
        const ta = document.createElement('textarea');
        ta.value = text; ta.setAttribute('readonly','');
        ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta); ta.focus(); ta.select();
        ok = document.execCommand('copy'); document.body.removeChild(ta);
      }catch(e){ ok = false; }
    }
    flashCopy(btn, ok);
  }
  function downloadSummary(){ window.open('/api/run/summary/file', '_blank'); }

  /* ====== Status refresh (Plex & SIMKL) ====== */
  function setRefreshBusy(busy){
    const btn = document.getElementById('btn-status-refresh');
    if (!btn) return;
    btn.disabled = !!busy;
    btn.classList.toggle('loading', !!busy);
  }
  async function manualRefreshStatus(){
    const btn = document.getElementById('btn-status-refresh');
    try{
      setRefreshBusy(true);
      btn.classList.add('spin');
      setTimeout(()=> btn.classList.remove('spin'), 2000);
      await refreshStatus(true); // forces /api/status?fresh=1
    }catch(e){
      console?.warn('Manual status refresh failed', e);
    }finally{
      setRefreshBusy(false);
    }
  }
  async function refreshStatus(force = false){
    const now = Date.now();
    if (!force && now - lastStatusMs < STATUS_MIN_INTERVAL) return;
    lastStatusMs = now;

    const r = await fetch('/api/status' + (force ? '?fresh=1' : '')).then(r=>r.json());
    appDebug = !!r.debug;

    const pb = document.getElementById('badge-plex');
    const sb = document.getElementById('badge-simkl');
    pb.className = 'badge ' + (r.plex_connected ? 'ok' : 'no');
    pb.innerHTML = `<span class="dot ${r.plex_connected?'ok':'no'}"></span>Plex: ${r.plex_connected?'Connected':'Not connected'}`;
    sb.className = 'badge ' + (r.simkl_connected ? 'ok' : 'no');
    sb.innerHTML = `<span class="dot ${r.simkl_connected?'ok':'no'}"></span>SIMKL: ${r.simkl_connected?'Connected':'Not connected'}`;

    window._ui.status = { can_run: !!r.can_run, plex_connected: !!r.plex_connected, simkl_connected: !!r.simkl_connected };
    recomputeRunDisabled();

    const onMain = !document.getElementById('ops-card').classList.contains('hidden');
    const logPanel = document.getElementById('log-panel');
    const layout   = document.getElementById('layout');
    const stats    = document.getElementById('stats-card');
    const hasStatsVisible = !!(stats && !stats.classList.contains('hidden'));

    logPanel.classList.toggle('hidden', !(appDebug && onMain));
    layout.classList.toggle('full', onMain && !appDebug && !hasStatsVisible);
  }

  /* ====== Config & Settings ====== */
  async function loadConfig(){
    const cfg = await fetch('/api/config', {cache:'no-store'}).then(r=>r.json());

    // Sync Options
    document.getElementById('mode').value   = cfg.sync?.bidirectional?.mode || 'two-way';
    document.getElementById('source').value = cfg.sync?.bidirectional?.source_of_truth || 'plex';

    // Troubleshoot / Runtime
    document.getElementById('debug').value  = String(!!cfg.runtime?.debug);

    // Auth / Keys
    document.getElementById('plex_token').value           = cfg.plex?.account_token || '';
    document.getElementById('simkl_client_id').value      = cfg.simkl?.client_id || '';
    document.getElementById('simkl_client_secret').value  = cfg.simkl?.client_secret || '';
    document.getElementById('simkl_access_token').value   = cfg.simkl?.access_token || '';
    document.getElementById('tmdb_api_key').value         = cfg.tmdb?.api_key || '';

    // Scheduling (pull from /api/config so the same source drives the UI)
    const s = cfg.scheduling || {};
    document.getElementById('schEnabled').value = String(!!s.enabled);
    document.getElementById('schMode').value    = (typeof s.mode === 'string' && s.mode) ? s.mode : 'hourly';
    document.getElementById('schN').value       = Number.isFinite(s.every_n_hours) ? String(s.every_n_hours) : '2';
    document.getElementById('schTime').value    = (typeof s.daily_time === 'string' && s.daily_time) ? s.daily_time : '03:30';
    // Optional timezone field if you add an <input id="schTz">
    if (document.getElementById('schTz')) document.getElementById('schTz').value = s.timezone || '';

    // keep your existing hints
    updateSimklButtonState?.(); updateSimklHint?.(); updateTmdbHint?.();
  }

  // Save settings back to server
  async function saveSettings(){
    const toast = document.getElementById('save_msg');
    const showToast = (text, ok=true) => {
      if (!toast) return;
      toast.classList.remove('hidden','ok','warn');
      toast.classList.add(ok ? 'ok' : 'warn');
      toast.textContent = text;
      // keep it visible long enough to read
      setTimeout(() => toast.classList.add('hidden'), 2000);
    };

    try {
      // 1) Pull current server config and clone
      const serverResp = await fetch('/api/config');
      if (!serverResp.ok) throw new Error(`GET /api/config ${serverResp.status}`);
      const serverCfg = await serverResp.json();
      const cfg = (typeof structuredClone === 'function')
        ? structuredClone(serverCfg)
        : JSON.parse(JSON.stringify(serverCfg || {}));

      let changed = false;

      // --- SYNC ---
      const uiMode   = document.getElementById('mode').value;
      const uiSource = document.getElementById('source').value;
      const prevMode   = serverCfg?.sync?.bidirectional?.mode || 'two-way';
      const prevSource = serverCfg?.sync?.bidirectional?.source_of_truth || 'plex';
      if (uiMode !== prevMode) {
        cfg.sync = cfg.sync || {}; cfg.sync.bidirectional = cfg.sync.bidirectional || {};
        cfg.sync.bidirectional.mode = uiMode; changed = true;
      }
      if (uiSource !== prevSource) {
        cfg.sync = cfg.sync || {}; cfg.sync.bidirectional = cfg.sync.bidirectional || {};
        cfg.sync.bidirectional.source_of_truth = uiSource; changed = true;
      }

      // --- RUNTIME ---
      const uiDebug = (document.getElementById('debug').value === 'true');
      const prevDebug = !!serverCfg?.runtime?.debug;
      if (uiDebug !== prevDebug) {
        cfg.runtime = cfg.runtime || {};
        cfg.runtime.debug = uiDebug; changed = true;
      }

      // --- PLEX ---
      const uiPlexToken = (document.getElementById('plex_token').value || '').trim();
      const prevPlexTok = serverCfg?.plex?.account_token || '';
      if (uiPlexToken && uiPlexToken !== prevPlexTok) {
        cfg.plex = cfg.plex || {};
        cfg.plex.account_token = uiPlexToken; changed = true;
      }

      // --- SIMKL ---
      const uiCid = (document.getElementById('simkl_client_id').value || '').trim();
      const uiSec = (document.getElementById('simkl_client_secret').value || '').trim();
      const prevCid = serverCfg?.simkl?.client_id || '';
      const prevSec = serverCfg?.simkl?.client_secret || '';
      if (uiCid && uiCid !== prevCid) { cfg.simkl = cfg.simkl || {}; cfg.simkl.client_id = uiCid; changed = true; }
      if (uiSec && uiSec !== prevSec) { cfg.simkl = cfg.simkl || {}; cfg.simkl.client_secret = uiSec; changed = true; }

      // --- TMDb ---
      const uiTmdb = (document.getElementById('tmdb_api_key').value || '').trim();
      const prevTmdb = serverCfg?.tmdb?.api_key || '';
      if (uiTmdb && uiTmdb !== prevTmdb) { cfg.tmdb = cfg.tmdb || {}; cfg.tmdb.api_key = uiTmdb; changed = true; }

      // 2) Save updated config (only if changed)
      if (changed) {
        const postCfg = await fetch('/api/config', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify(cfg)
        });
        if (!postCfg.ok) throw new Error(`POST /api/config ${postCfg.status}`);
      }

      // 3) Save scheduling 
      try {
        const schPayload = {
          enabled: document.getElementById('schEnabled').value === 'true',
          mode: document.getElementById('schMode').value,
          every_n_hours: parseInt(document.getElementById('schN').value || '2', 10),
          daily_time: document.getElementById('schTime').value || '03:30',
          timezone: (document.getElementById('schTz')?.value || '').trim() || undefined
        };
        const postSch = await fetch('/api/scheduling', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify(schPayload)
        });
        if (!postSch.ok) throw new Error(`POST /api/scheduling ${postSch.status}`);
      } catch (e) {
        console.warn('saveSettings: scheduling failed', e);
      }

      // 4) Refresh UI pieces
      try { await refreshStatus(true); } catch {}
      try { updateTmdbHint?.(); } catch {}
      try { updateSimklState?.(); } catch {}
      try { await updateWatchlistTabVisibility?.(); } catch {}
      try { await loadScheduling?.(); } catch {}

      // 5) Success toast
      showToast('Settings saved ✓', true);

    } catch (err) {
      console.error('saveSettings failed', err);
      showToast('Save failed — see console', false);
    }
  }

  // ---- Scheduling UI ----
  async function loadScheduling(){
    try{
      const res = await fetch('/api/scheduling', { cache: 'no-store' });
      const s = await res.json();

      // Debug log so we can verify what the UI received
      console.debug('[UI] /api/scheduling ->', s);

      const en = document.getElementById('schEnabled');
      const mo = document.getElementById('schMode');
      const nh = document.getElementById('schN');
      const ti = document.getElementById('schTime');

      if (!en || !mo || !nh || !ti) {
        console.warn('[UI] scheduling controls not found in DOM');
        return;
      }

      // Map JSON -> controls (strings for <select> values)
      const valEnabled = s && s.enabled === true ? 'true' : 'false';
      const valMode    = (s && typeof s.mode === 'string' && s.mode) ? s.mode : 'hourly';
      const valN       = (s && Number.isFinite(s.every_n_hours)) ? String(s.every_n_hours) : '2';
      const valTime    = (s && typeof s.daily_time === 'string' && s.daily_time) ? s.daily_time : '03:30';

      // Update controls
      en.value = valEnabled;
      mo.value = valMode;
      nh.value = valN;
      ti.value = valTime;

      // nudge browser to update UI state
      en.dispatchEvent(new Event('change'));
      mo.dispatchEvent(new Event('change'));
      nh.dispatchEvent(new Event('change'));
      ti.dispatchEvent(new Event('change'));

    } catch (e) {
      console.warn('Failed to load scheduling config', e);
    }
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
          span.textContent = `—   Scheduler running (next ${nextRun})`;
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

  /* Troubleshooting actions */
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

  async function resetStats(){
    const btnText = "Reset Statistics";
    try{
      const r = await fetch('/api/troubleshoot/reset-stats', { method:'POST' });
      const j = await r.json();
      const m = document.getElementById('tb_msg');
      m.classList.remove('hidden');
      m.textContent = j.ok ? (btnText + ' – done ✓') : (btnText + ' – failed' + (j.error ? ` (${j.error})` : ''));
      setTimeout(()=>m.classList.add('hidden'), 2200);

      if (j.ok && typeof refreshStats === 'function') refreshStats(true);
    }catch(e){
      const m = document.getElementById('tb_msg');
      m.classList.remove('hidden');
      m.textContent = btnText + ' – failed (network)';
      setTimeout(()=>m.classList.add('hidden'), 2200);
    }
  }

  /* TMDb hint logic (Settings page only) */
  async function updateTmdbHint(){
    const hint  = document.getElementById('tmdb_hint');
    const input = document.getElementById('tmdb_api_key');
    if (!hint || !input) return;
    const settingsVisible = !document.getElementById('page-settings')?.classList.contains('hidden');
    if (!settingsVisible) return;
    const v = (input.value || '').trim();
    if (document.activeElement === input) input.dataset.dirty = '1';
    if (input.dataset.dirty === '1'){ hint.classList.toggle('hidden', !!v); return; }
    if (v){ hint.classList.add('hidden'); return; }
    try {
      const cfg = await fetch('/api/config', { cache: 'no-store' }).then(r => r.json());
      const has = !!((cfg.tmdb?.api_key || '').trim());
      hint.classList.toggle('hidden', has);
    } catch { hint.classList.remove('hidden'); }
  }

  /* Plex auth (PIN flow) */
  function setPlexSuccess(show){
    document.getElementById('plex_msg').classList.toggle('hidden', !show);
  }

  async function requestPlexPin(){
    setPlexSuccess(false);
    const r = await fetch('/api/plex/pin/new', {method:'POST'});
    const j = await r.json();
    if(!j.ok){ return; }

    document.getElementById('plex_pin').value = j.code;
    try{ await navigator.clipboard.writeText(j.code); }catch(_){}
    window.open('https://plex.tv/link', '_blank');

    if(plexPoll) { clearInterval(plexPoll); }
    let ticks = 0;

    plexPoll = setInterval(async ()=>{
      ticks++;
      const cfg = await fetch('/api/config', { cache: 'no-store' })
        .then(r=>r.json()).catch(()=>null);
      const tok = cfg?.plex?.account_token || '';

      const el = document.getElementById('plex_token');
      if (tok && el && el.value !== tok) {
        // Polling Current token until it changes
        el.value = tok;
        setPlexSuccess(true);
        await refreshStatus();
        clearInterval(plexPoll);
      }

      if(ticks > 360){ clearInterval(plexPoll); }
    }, 1000);
  }

  /* SIMKL auth */
  function setSimklSuccess(show){ document.getElementById('simkl_msg').classList.toggle('hidden', !show); }
  function isPlaceholder(v, ph){ return (v||'').trim().toUpperCase() === ph.toUpperCase(); }
  function updateSimklButtonState(){
    const cid = (document.getElementById('simkl_client_id').value || '').trim();
    const sec = (document.getElementById('simkl_client_secret').value || '').trim();
    const badCid = (!cid) || isPlaceholder(cid, 'YOUR_SIMKL_CLIENT_ID');
    const badSec = (!sec) || isPlaceholder(sec, 'YOUR_SIMKL_CLIENT_SECRET');
    const btn = document.getElementById('simkl_start_btn'); const hint = document.getElementById('simkl_hint');
    document.getElementById('redirect_uri_preview').textContent = computeRedirectURI();
    const ok = !(badCid || badSec); btn.disabled = !ok; hint.classList.toggle('hidden', ok);
  }
  async function copyRedirect(){ try{ await navigator.clipboard.writeText(computeRedirectURI()); }catch(_){} }
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
  // triggered by a real click only
  async function copyInputValue(inputId, btnEl) {
    const el = document.getElementById(inputId);
    const val = el?.value?.trim() || "";
    if (!val) return;

    try {
      // Modern, secure-context path (localhost/127.0.0.1 is ok in moderne browsers)
      await navigator.clipboard.writeText(val);
      flashBtnOK(btnEl);
    } catch (e) {
      // Fallback for older/locked-down contexts
      const ta = document.createElement('textarea');
      ta.value = val;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); flashBtnOK(btnEl); } catch(_) {}
      document.body.removeChild(ta);
    }
  }

  function flashBtnOK(btnEl){
    if (!btnEl) return;
    btnEl.disabled = true;
    btnEl.classList.add('copied');      // optional style hook
    setTimeout(() => { 
      btnEl.classList.remove('copied'); 
      btnEl.disabled = false; 
    }, 700);
  }

  // Wire up buttons once the DOM is ready (no layout changes)
  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btn-copy-plex-pin')
      ?.addEventListener('click', (e) => copyInputValue('plex_pin', e.currentTarget));
    document.getElementById('btn-copy-plex-token')
      ?.addEventListener('click', (e) => copyInputValue('plex_token', e.currentTarget));
  });

  /* ====== Poster carousel helpers ====== */
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

  /* ====== Watchlist (grid) ====== */
  function artUrl(item, size){
    const typ  = (item.type === 'tv' || item.type === 'show') ? 'tv' : 'movie';
    const tmdb = item.tmdb;
    if(!tmdb) return null;
    const cb = window._lastSyncEpoch || 0;
    return `/art/tmdb/${typ}/${tmdb}?size=${encodeURIComponent(size || 'w342')}&cb=${cb}`;
  }

  async function loadWall() {
    const card = document.getElementById('placeholder-card');
    const msg = document.getElementById('wall-msg');
    const row = document.getElementById('poster-row');
    msg.textContent = 'Loading…'; row.innerHTML = ''; row.classList.add('hidden'); card.classList.remove('hidden');

    const hidden = new Set((()=>{ try { return JSON.parse(localStorage.getItem('wl_hidden') || '[]'); } catch { return []; } })());
    const isDeleted = (k) => hidden.has(k) || (window._deletedKeys && window._deletedKeys.has(k));

    try {
      const data = await fetch('/api/state/wall').then(r => r.json());
      if (data.missing_tmdb_key) { card.classList.add('hidden'); return; }
      if (!data.ok) { msg.textContent = data.error || 'No state data found.'; return; }
      const items = data.items || [];
      _lastSyncEpoch = data.last_sync_epoch || null;
      if (items.length === 0) { msg.textContent = 'No items to show yet.'; return; }
      msg.classList.add('hidden'); row.classList.remove('hidden');

      for (const it of items) {
        if (!it.tmdb) continue;
        const a = document.createElement('a');
        a.className = 'poster';
        a.href = `https://www.themoviedb.org/${it.type}/${it.tmdb}`; a.target = '_blank'; a.rel = 'noopener';
        a.dataset.type = it.type; a.dataset.tmdb = String(it.tmdb); a.dataset.key = it.key || '';
        const uiStatus = isDeleted(it.key) ? 'deleted' : it.status; a.dataset.source = uiStatus;

        const img = document.createElement('img');
        img.loading = 'lazy'; img.alt = `${it.title || ''} (${it.year || ''})`; img.src = artUrl(it, 'w342'); a.appendChild(img);

        const ovr = document.createElement('div'); ovr.className = 'ovr';
        let pillText, pillClass;
        if (uiStatus === 'deleted')      { pillText = 'DELETED';  pillClass = 'p-del'; }
        else if (uiStatus === 'both')    { pillText = 'SYNCED';   pillClass = 'p-syn'; }
        else if (uiStatus === 'plex_only'){ pillText = 'PLEX';     pillClass = 'p-px'; }
        else                              { pillText = 'SIMKL';    pillClass = 'p-sk'; }
        const pill = document.createElement('div'); pill.className = 'pill ' + pillClass; pill.textContent = pillText; ovr.appendChild(pill); a.appendChild(ovr);

        const cap = document.createElement('div'); cap.className = 'cap'; cap.textContent = `${it.title || ''} ${it.year ? '· ' + it.year : ''}`; a.appendChild(cap);

        const hover = document.createElement('div'); hover.className = 'hover';
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
          } catch { descEl.textContent = '—'; descEl.dataset.loaded = '1'; }
        }, { passive: true });

        row.appendChild(a);
      }
      initWallInteractions();
    } catch { msg.textContent = 'Failed to load preview.'; }
  }

  async function loadWatchlist() {
    const grid = document.getElementById('wl-grid');
    const msg = document.getElementById('wl-msg');
    grid.innerHTML = ''; grid.classList.add('hidden'); msg.textContent = 'Loading…'; msg.classList.remove('hidden');
    try {
      const data = await fetch('/api/watchlist').then(r => r.json());
      if (data.missing_tmdb_key) { msg.textContent = 'Set a TMDb API key to see posters.'; return; }
      if (!data.ok) { msg.textContent = data.error || 'No state data found.'; return; }
      const items = data.items || [];
      if (items.length === 0) { msg.textContent = 'No items on your watchlist yet.'; return; }
      msg.classList.add('hidden'); grid.classList.remove('hidden');
      for (const it of items) {
        if (!it.tmdb) continue;
        const node = document.createElement('div');
        node.className = 'wl-poster poster';
        node.dataset.key = it.key;
        node.dataset.type = it.type === 'tv' || it.type === 'show' ? 'tv' : 'movie';
        node.dataset.tmdb = String(it.tmdb || '');
        node.dataset.status = it.status;
        const pillText = it.status === 'both' ? 'SYNCED' : (it.status === 'plex_only' ? 'PLEX' : 'SIMKL');
        const pillClass = it.status === 'both' ? 'p-syn' : (it.status === 'plex_only' ? 'p-px' : 'p-sk');
        
        node.innerHTML = `
          <img alt="" src="${artUrl(it, 'w342') || ''}" onerror="this.style.display='none'">
          <button class="wl-del icon-btn trash"
                  type="button"
                  title="Remove from Plex watchlist"
                  aria-label="Remove from Plex watchlist"
                  onclick="deletePoster(event, '${encodeURIComponent(it.key)}', this)">
            <svg class="ico" viewBox="0 0 24 24" aria-hidden="true">
              <path class="lid" d="M9 4h6l1 2H8l1-2z"/>
              <path d="M6 7h12l-1 13H7L6 7z"/>
              <path d="M10 11v6M14 11v6"/>
            </svg>
          </button>

          <div class="wl-ovr ovr"><span class="pill ${pillClass}">${pillText}</span></div>
          <div class="wl-cap cap">${(it.title || '').replace(/"/g, '&quot;')} ${it.year ? '· ' + it.year : ''}</div>
          <div class="wl-hover hover">
            <div class="titleline">${(it.title || '')}</div>
            <div class="meta">
              <div class="chip src">${it.status === 'both' ? 'Source: Synced' : (it.status === 'plex_only' ? 'Source: Plex' : 'Source: SIMKL')}</div>
              <div class="chip time">${relTimeFromEpoch(it.added_epoch)}</div>
            </div>
            <div class="desc" id="wldesc-${node.dataset.type}-${node.dataset.tmdb}">${it.tmdb ? 'Fetching description…' : '—'}</div>
          </div>`;


        const hidden = new Set(JSON.parse(localStorage.getItem('wl_hidden') || '[]'));
        if (hidden.has(it.key)) {
          const pill = node.querySelector('.pill'); pill.textContent = 'DELETED'; pill.classList.add('p-del');
        }

        node.addEventListener('mouseenter', async () => {
          const descEl = document.getElementById(`wldesc-${it.type}-${it.tmdb}`);
          if (!descEl || descEl.dataset.loaded) return;
          try {
            const cb = window._lastSyncEpoch || Date.now();
            const meta = await fetch(`/api/tmdb/meta/${it.type}/${it.tmdb}?cb=${cb}`).then(r => r.json());
            descEl.textContent = meta?.overview || '—';
            descEl.dataset.loaded = '1';
          } catch { descEl.textContent = '—'; descEl.dataset.loaded = '1'; }
        }, { passive: true });

        grid.appendChild(node);
      }
    } catch (error) {
      console.error('Error loading watchlist:', error);
      msg.textContent = 'Failed to load preview.';
    }
  }

  // Delete a watchlist item (from Plex)
  async function deletePoster(ev, encKey, btnEl) {
    ev?.stopPropagation?.();
    const key  = decodeURIComponent(encKey);
    const card = btnEl.closest('.wl-poster');

    // visual state
    btnEl.disabled = true;
    btnEl.classList.remove('done','error');
    btnEl.classList.add('working');

    try {
      const res = await fetch('/api/watchlist/' + encodeURIComponent(key), { method: 'DELETE' });
      if (!res.ok) throw new Error('HTTP ' + res.status);

      // fade out and remove
      if (card) {
        card.classList.add('wl-removing');
        setTimeout(() => { card.remove(); }, 350);
      }

      // persist hidden key (your existing behavior)
      const hidden = new Set(JSON.parse(localStorage.getItem('wl_hidden') || '[]'));
      hidden.add(key);
      localStorage.setItem('wl_hidden', JSON.stringify([...hidden]));
      window.dispatchEvent(new Event('storage'));

      btnEl.classList.remove('working');
      btnEl.classList.add('done');
    } catch (e) {
      console.warn('deletePoster error', e);
      btnEl.classList.remove('working');
      btnEl.classList.add('error');
      setTimeout(() => btnEl.classList.remove('error'), 1200);
    } finally {
      setTimeout(() => { btnEl.disabled = false; }, 600);
    }
  }

  /* ====== Watchlist preview visibility ====== */
  async function updateWatchlistPreview(){ await loadWatchlist(); }
  async function updateWatchlistTabVisibility(){
    try {
      const cfg = await fetch('/api/config').then(r=>r.json());
      const tmdbKey = (cfg.tmdb?.api_key || '').trim();
      document.getElementById('tab-watchlist').style.display = tmdbKey ? 'block' : 'none';
    } catch(e){ document.getElementById('tab-watchlist').style.display = 'none'; }
  }
  async function hasTmdbKey(){
    try{ const cfg = await fetch('/api/config').then(r=>r.json()); return !!(cfg.tmdb?.api_key || '').trim(); }catch(_){ return false; }
  }
  function isOnMain(){ return !document.getElementById('ops-card').classList.contains('hidden'); }
  async function updatePreviewVisibility(){
    const card = document.getElementById('placeholder-card');
    const row  = document.getElementById('poster-row');
    if (!isOnMain()) { card.classList.add('hidden'); return false; }
    const show = await hasTmdbKey();
    if(!show){
      card.classList.add('hidden');
      if(row){ row.innerHTML = ''; row.classList.add('hidden'); }
      window.wallLoaded = false; return false;
    } else {
      card.classList.remove('hidden');
      if(!window.wallLoaded){ await loadWall(); window.wallLoaded = true; }
      return true;
    }
  }

  /* ====== Boot ====== */
  showTab('main');
  updateWatchlistTabVisibility();
  window.addEventListener('storage', (event) => { if (event.key === 'wl_hidden') { loadWatchlist(); } });
</script>
</body></html>
"""
