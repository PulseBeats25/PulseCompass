# 🚀 How to Start PulseCompass

## Quick Start Guide

### Prerequisites
- Docker Desktop running
- Python 3.11+ installed
- Node.js 18+ installed

---

## Step 1: Start Redis

Check if Redis is running:
```powershell
docker ps | findstr pulsecompass-redis
```

**If nothing shows up, start Redis:**
```powershell
docker run -d --name pulsecompass-redis -p 6380:6379 -v pulsecompass_redis:/data redis:7-alpine --appendonly yes
```

**If container exists but is stopped:**
```powershell
docker start pulsecompass-redis
```

---

## Step 2: Install Dependencies (First Time Only)

### Backend Dependencies
```powershell
cd "E:\PROJECTS  APP\stocks analyzer\PulseCompass\backend"
pip install -r requirements.txt
```

### Frontend Dependencies
```powershell
cd "E:\PROJECTS  APP\stocks analyzer\PulseCompass"
npm install
```

---

## Step 3: Start Services (3 Terminals)

### Terminal 1: Backend API
```powershell
cd "E:\PROJECTS  APP\stocks analyzer\PulseCompass\backend"
uvicorn main:app --reload
```

**Wait for:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

---

### Terminal 2: Worker
```powershell
cd "E:\PROJECTS  APP\stocks analyzer\PulseCompass\backend"
python worker.py
```

**Wait for:**
```
*** Listening on default...
Worker started with PID
```

---

### Terminal 3: Frontend
```powershell
cd "E:\PROJECTS  APP\stocks analyzer\PulseCompass"
npm run dev
```

**Wait for:**
```
▲ Next.js 14.2.32
- Local:        http://localhost:3000
✓ Ready in 3s
```

---

## Step 4: Verify Everything Works

### Test API Health
```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health/redis
```

**Expected output:**
```
ok
--
True
```

### Test Queue Metrics
```powershell
Invoke-RestMethod http://localhost:8000/api/v1/metrics/queues
```

### Open Frontend
```powershell
start http://localhost:3000
```

Or visit: http://localhost:3000

---

## What Should Be Running

| Service | Port | Terminal | Status Check |
|---------|------|----------|--------------|
| **Redis** | 6380 | Docker | `docker ps \| findstr redis` |
| **Backend API** | 8000 | Terminal 1 | http://localhost:8000/docs |
| **Worker** | - | Terminal 2 | Check terminal output |
| **Frontend** | 3000 | Terminal 3 | http://localhost:3000 |

---

## Troubleshooting

### Redis won't start
```powershell
# Remove old container
docker rm -f pulsecompass-redis

# Start fresh
docker run -d --name pulsecompass-redis -p 6380:6379 -v pulsecompass_redis:/data redis:7-alpine --appendonly yes
```

### Backend errors
```powershell
# Check .env file exists
cd backend
Get-Content .env

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Worker not processing jobs
```powershell
# Verify Redis connection
cd backend
python -c "from core.redis import get_redis; print(get_redis().ping())"

# Should print: True
```

### Frontend won't start
```powershell
# Clear cache and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item -Recurse -Force .next
npm install
npm run dev
```

---

## Stop All Services

### Stop Terminals
Press `CTRL+C` in each terminal window

### Stop Redis
```powershell
docker stop pulsecompass-redis
```

### Stop Everything (including Redis)
```powershell
docker stop pulsecompass-redis
# Then close all terminal windows
```

---

## Alternative: Docker Compose (All-in-One)

Start everything with one command:

```powershell
cd "E:\PROJECTS  APP\stocks analyzer\PulseCompass"
docker-compose up -d
```

**View logs:**
```powershell
docker-compose logs -f
```

**Stop everything:**
```powershell
docker-compose down
```

---

## Access Points

- **Frontend UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc
- **API Health**: http://localhost:8000/api/v1/health/redis
- **Queue Metrics**: http://localhost:8000/api/v1/metrics/queues
- **Worker Metrics**: http://localhost:8000/api/v1/metrics/workers

---

## Environment Files

Make sure these files exist with correct values:

### `backend/.env`
```env
REDIS_URL=redis://localhost:6380/0
SUPABASE_JWT_SECRET=AcUB98gzYeXkYcTCVpRnWE7FuZU1LmSJFSnUQqFVFei3sa0LmcWu2h651P0rlDLc9OUGklGOgqYwitNfHvq5lQ==
SUPABASE_URL=https://otgeplfjbxildbzgwnxt.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90Z2VwbGZqYnhpbGRiemd3bnh0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1MjY3MjgsImV4cCI6MjA3MzEwMjcyOH0.2cblM9Z7CamjJ05bP85TjA8jqinydAGdtTQSxvbwE1w
```

### `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://otgeplfjbxildbzgwnxt.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90Z2VwbGZqYnhpbGRiemd3bnh0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1MjY3MjgsImV4cCI6MjA3MzEwMjcyOH0.2cblM9Z7CamjJ05bP85TjA8jqinydAGdtTQSxvbwE1w
```

---

## Summary

**Minimum to run the app:**
1. ✅ Redis container (Docker)
2. ✅ Backend API (Terminal 1)
3. ✅ Worker (Terminal 2)
4. ✅ Frontend (Terminal 3)

**That's it! Your app is running at http://localhost:3000** 🎉
