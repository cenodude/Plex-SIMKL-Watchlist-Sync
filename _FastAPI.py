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

  /* Sticky right meta card — push it down a bit */
  .det-right{
    position: sticky;
    top: 100px;
    align-self: start;
    margin-top: 8px;  /* extra initial offset in normal flow */
  }

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

  /* Page layout */
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
  #ops-card .chiprow{ margin-bottom: 20px; }
  #ops-card .sep{ margin: 6px 0 16px; }
  #ops-card .action-row{ margin-top: 0; }

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
  .details{border:1px dashed #2a2a3a;border-radius:12px;padding:10px;margin-top:10px;background:#0a0a17}
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
    top: 28px !important;   /* increase sticky offset */
  }

  /* Extra spacing inside the right column (optional) */
  .details-grid > .det-right .meta-card {
    margin-top: 12px;       /* bump the whole card downward */
  }

  /* Hide the bottom title on the WATCHLIST PREVIEW (carousel) only */
  #placeholder-card .cap { display: none !important; }

  /* Hide titles in the WATCHLIST GRID page as well */
  #page-watchlist .wl-cap { display: none !important; }

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
              <button class="btn" onclick="copySummary(this)">Copy summary</button>
              <button class="btn" onclick="downloadSummary()">Download</button>
            </div>
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
            <span class="chev">▶</span><strong>Plex</strong>
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
                  <input id="plex_pin" placeholder="request to fill" readonly>
                  <button id="btn-copy-plex-pin"   class="btn copy" onclick="copyInputValue('plex_pin', this)">Copy</button>
                </div>
              </div>
            </div>
            <div style="display:flex;gap:8px">
              <button class="btn" onclick="requestPlexPin()">Request Token</button>
              <div style="align-self:center;color:var(--muted)">
                Opens plex.tv/link (PIN copied to clipboard)
              </div>
            </div>
            <div id="plex_msg" class="msg ok hidden">Successfully retrieved token</div>
            <div class="sep"></div>
          </div>
        </div>
      </div>
    </div>


        <!-- SIMKL -->
        <div class="section" id="sec-simkl">
          <div class="head" onclick="toggleSection('sec-simkl')"><span class="chev">▶</span><strong>SIMKL</strong></div>
          <div class="body">
            <div class="grid2">
              <div><label>Client ID</label><input id="simkl_client_id" placeholder="Your SIMKL client id" oninput="updateSimklButtonState(); updateSimklHint();"></div>
              <div><label>Client Secret</label><input id="simkl_client_secret" placeholder="Your SIMKL client secret" oninput="updateSimklButtonState(); updateSimklHint();"></div>
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
                <input id="tmdb_api_key" placeholder="Your TMDb API key" oninput="this.dataset.dirty='1'; updateTmdbHint()">
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
      <button class="btn btn-save" onclick="saveSettings()"><span class="btn-ic">✔</span> Save</button>
      <button class="btn btn-exit" onclick="showTab('main')"><span class="btn-ic">↩</span> Exit</button>
      <span id="save_msg" class="msg ok hidden">Settings saved ✓</span>
    </div>
  </section>

  <aside id="log-panel" class="card hidden">
    <div class="title">Raw log (Debug)</div>
    <div id="log" class="log"></div>
  </aside>

</main>

<script>
  /* ====== Globals ====== */
  let lastStatusMs = 0;
  const STATUS_MIN_INTERVAL = 120000; // ms

  let busy=false, esDet=null, esSum=null, plexPoll=null, simklPoll=null, appDebug=false, currentSummary=null;
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

  /* ====== Tabs ====== */
  async function showTab(n) {
    const pageSettings = document.getElementById('page-settings');
    const pageWatchlist = document.getElementById('page-watchlist');
    const logPanel = document.getElementById('log-panel');
    const layout = document.getElementById('layout');

    document.getElementById('tab-main').classList.toggle('active', n === 'main');
    document.getElementById('tab-watchlist').classList.toggle('active', n === 'watchlist');
    document.getElementById('tab-settings').classList.toggle('active', n === 'settings');

    document.getElementById('ops-card').classList.toggle('hidden', n !== 'main');
    document.getElementById('placeholder-card').classList.toggle('hidden', n !== 'main');
    pageWatchlist.classList.toggle('hidden', n !== 'watchlist');
    pageSettings.classList.toggle('hidden', n !== 'settings');

    if (n === 'main') {
      layout.classList.remove('single');
      refreshStatus();
      layout.classList.toggle('full', !appDebug);
      if (!esSum) { openSummaryStream(); }
      await updatePreviewVisibility();
      refreshSchedulingBanner();
    } else if (n === 'watchlist') {
      layout.classList.add('single');
      layout.classList.remove('full');
      logPanel.classList.add('hidden');
      loadWatchlist();
    } else { // settings
      layout.classList.add('single');
      layout.classList.remove('full');
      logPanel.classList.add('hidden');
      document.getElementById('sec-auth')?.classList.add('open');
      await loadConfig();
      updateTmdbHint?.(); updateSimklHint?.(); updateSimklButtonState?.(); loadScheduling?.();
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

  // tiny toast you already have styling for messages; here's a quick helper
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

  function openDetailsLog(){
    const el = document.getElementById('det-log');
    if (!el) return;
    el.innerHTML = '';
    if (esDet) { esDet.close(); esDet = null; }
    esDet = new EventSource('/api/logs/stream?tag=SYNC');
    esDet.onmessage = (ev) => {
      if (!ev?.data) return;
      el.insertAdjacentHTML('beforeend', ev.data + '<br>');
      el.scrollTop = el.scrollHeight;
    };
    esDet.onerror = () => { try { esDet?.close(); } catch(_){} esDet = null; };
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
    try { await navigator.clipboard.writeText(text); ok = True; } catch(e) { ok = false; }
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
    const layout = document.getElementById('layout');
    logPanel.classList.toggle('hidden', !(appDebug && onMain));
    layout.classList.toggle('full', onMain && !appDebug);
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
          <div class="wl-del pill p-del" role="button" tabindex="0" title="Delete from Plex" onclick="deletePoster(event, '${encodeURIComponent(it.key)}', this)">Delete</div>
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
        const hidden = new Set(JSON.parse(localStorage.getItem('wl_hidden') || '[]'));
        hidden.add(key);
        localStorage.setItem('wl_hidden', JSON.stringify([...hidden]));
        window.dispatchEvent(new Event('storage'));
        return;
      }
      btnEl.disabled = false; btnEl.textContent = 'Failed'; setTimeout(() => { btnEl.textContent = 'Delete'; }, 1200);
    } catch (e) {
      console.warn('deletePoster error', e);
      btnEl.disabled = false; btnEl.textContent = 'Error'; setTimeout(() => { btnEl.textContent = 'Delete'; }, 1200);
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
