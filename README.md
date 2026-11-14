# BruteKit Web — Render Deploy Guide

## Render pe deploy kaise kare

### Step 1 — GitHub account banao (agar nahi hai)
https://github.com

### Step 2 — New repository banao
1. GitHub pe jao → New Repository
2. Name: `brutekit` (private rakhna)
3. Create repository

### Step 3 — Files upload karo
GitHub repo mein ye sab files upload karo:
- app.py
- requirements.txt
- render.yaml
- Procfile
- username.txt
- password.txt

### Step 4 — Render pe deploy
1. https://render.com pe jao → Sign up (free)
2. New → Web Service
3. GitHub repo connect karo
4. Settings:
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --timeout 0 --workers 1 --threads 8 --bind 0.0.0.0:$PORT`
5. Deploy karo

### Step 5 — Use karo
Render ek URL dega jaise:
`https://brutekit.onrender.com`

Wahan jao → URL daalo → mode choose karo → START

---

## Username.txt / Password.txt edit karna
GitHub pe directly edit kar sakte ho — Render automatically redeploy karega.
